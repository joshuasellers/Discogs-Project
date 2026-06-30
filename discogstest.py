import argparse
import re

import discogs_client
import inquirer
import tokens
from serpapi import GoogleSearch

import helper

USER_AGENT = "VinylImageReadingProject/0.1"


def get_client():
    return discogs_client.Client(USER_AGENT, user_token=tokens.discogs_token)


def google_search(imageurl):
    params = {
        "api_key": tokens.serpapi_key,
        "engine": "google_lens",
        "search_type": "products",
        "q": "Discogs",
        "url": imageurl,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    response = results.get("visual_matches", [])
    filtered_response = filter(
        lambda r: r.get("source") == "Discogs" and "Vinyl" in r.get("title", ""),
        response,
    )
    titles = [r["title"] for r in filtered_response]
    print(titles)
    print("************************************************")
    return titles


def match_release(client, titles):
    album_options = []
    for title in titles:
        ids = re.findall(r"\[r[0-9]+]", title)
        for release_ref in ids:
            results = client.search(
                release_ref.replace("[", "").replace("]", ""), type="release"
            )
            if results:
                album_options.append((results[0], title))

    if len(album_options) > 1:
        print("Please choose the correct album:")
        release, google_title = helper.multiple_choice(album_options)
        return release, google_title
    if len(album_options) == 1:
        return album_options[0]
    return None, None


def new_manifest_item(image_url, google_title, release, defaults):
    return {
        "image_url": image_url,
        "google_title": google_title,
        "release_id": release.id,
        "release_title": helper.release_title(release),
        "media_condition": defaults["media_condition"],
        "sleeve_condition": defaults["sleeve_condition"],
        "notes": "",
        "status": "pending",
    }


def cmd_match():
    client = get_client()
    manifest = helper.default_manifest()
    urls = helper.get_raw_album_urls()

    for url in urls:
        titles = google_search(url)
        release, google_title = match_release(client, titles)
        if release is None:
            print(f"No Discogs match found for {url}")
            continue
        item = new_manifest_item(url, google_title, release, manifest["defaults"])
        manifest["items"].append(item)
        print(f"Matched: {item['release_title']} (release {item['release_id']})")

    helper.save_manifest(manifest)
    print(f"Wrote {len(manifest['items'])} item(s) to {helper.MANIFEST_FILE}")


def search_release(client, query):
    query = query.strip()
    if query.isdigit():
        results = client.search(query, type="release")
    else:
        results = client.search(query, type="release")
    if not results:
        print("No releases found.")
        return None
    if len(results) == 1:
        return results[0]
    options = [(r, helper.release_title(r)) for r in results[:10]]
    print("Multiple releases found:")
    for index, (_, title) in enumerate(options, 1):
        print(f"{index}. {title}")
    choice = helper.multiple_choice(options)
    return choice[0]


def review_item(client, item, defaults):
    print("\n" + "=" * 60)
    print(f"Google match: {item.get('google_title', '')}")
    print(f"Discogs: {item.get('release_title', '')} (release {item.get('release_id')})")
    print(f"Media: {item.get('media_condition')} | Sleeve: {item.get('sleeve_condition')}")
    if item.get("notes"):
        print(f"Notes: {item['notes']}")

    action = inquirer.list_input(
        "Action",
        choices=[
            ("Confirm", "confirm"),
            ("Skip", "skip"),
            ("Change release", "change"),
            ("Edit conditions", "conditions"),
        ],
    )

    if action == "skip":
        item["status"] = "skipped"
        return item

    if action == "change":
        query = input("Search by release ID or text: ")
        release = search_release(client, query)
        if release is None:
            print("Keeping previous release.")
        else:
            confirm = input(f"Use {helper.release_title(release)} (release {release.id})? [Y/n]: ")
            if confirm.strip() == "" or helper.is_yes(confirm):
                item["release_id"] = release.id
                item["release_title"] = helper.release_title(release)
        return review_item(client, item, defaults)

    if action == "conditions":
        media = inquirer.list_input(
            "Media condition",
            choices=helper.MEDIA_CONDITIONS,
            default=item.get("media_condition", defaults["media_condition"]),
        )
        sleeve = inquirer.list_input(
            "Sleeve condition",
            choices=helper.SLEEVE_CONDITIONS,
            default=item.get("sleeve_condition", defaults["sleeve_condition"]),
        )
        notes = input(f"Notes [{item.get('notes', '')}]: ").strip()
        item["media_condition"] = media
        item["sleeve_condition"] = sleeve
        if notes:
            item["notes"] = notes
        return review_item(client, item, defaults)

    item["status"] = "confirmed"
    item["media_condition"] = helper.normalize_media_condition(
        item.get("media_condition"), defaults["media_condition"]
    )
    item["sleeve_condition"] = helper.normalize_sleeve_condition(
        item.get("sleeve_condition"), defaults["sleeve_condition"]
    )
    return item


def cmd_review():
    client = get_client()
    manifest = helper.load_manifest()
    defaults = manifest["defaults"]
    pending = [item for item in manifest["items"] if item.get("status") == "pending"]

    if not pending:
        print("No pending items to review.")
        return

    for item in manifest["items"]:
        if item.get("status") != "pending":
            continue
        review_item(client, item, defaults)

    helper.save_manifest(manifest)
    confirmed = sum(1 for item in manifest["items"] if item.get("status") == "confirmed")
    skipped = sum(1 for item in manifest["items"] if item.get("status") == "skipped")
    print(f"Review complete: {confirmed} confirmed, {skipped} skipped")


def release_in_folder(folder, release_id):
    return any(item.id == release_id for item in folder.releases)


def apply_collection_fields(client, username, folder_id, release_id, instance_id, item, field_ids):
    media = item.get("media_condition")
    sleeve = item.get("sleeve_condition")
    notes = item.get("notes", "")

    if media and "Media" in field_ids:
        helper.set_collection_field(
            client, username, folder_id, release_id, instance_id,
            field_ids["Media"], media,
        )
    if sleeve and "Sleeve" in field_ids:
        helper.set_collection_field(
            client, username, folder_id, release_id, instance_id,
            field_ids["Sleeve"], sleeve,
        )
    if notes and "Notes" in field_ids:
        helper.set_collection_field(
            client, username, folder_id, release_id, instance_id,
            field_ids["Notes"], notes,
        )


def cmd_upload():
    client = get_client()
    me = client.identity()
    username = me.username
    manifest = helper.load_manifest()
    defaults = manifest["defaults"]
    folder_id = defaults.get("folder_id", 1)
    folder = helper.get_folder(client, me, folder_id)
    field_ids = helper.get_collection_field_ids(client, username)

    to_upload = [
        item for item in manifest["items"]
        if item.get("status") == "confirmed"
    ]

    if not to_upload:
        print("No confirmed items to upload. Run `review` first or set status to confirmed in the manifest.")
        return

    for item in to_upload:
        release_id = item["release_id"]
        title = item.get("release_title", release_id)

        if release_in_folder(folder, release_id):
            print(f"{title} already in folder {folder_id}")
            item["status"] = "uploaded"
            continue

        try:
            response = helper.add_release_to_folder(client, folder, release_id)
            instance_id = response["instance_id"]
            apply_collection_fields(
                client, username, folder_id, release_id, instance_id, item, field_ids
            )
            item["status"] = "uploaded"
            print(f"Added {title} (release {release_id}) with media={item.get('media_condition')}")
        except Exception as exc:
            print(f"Failed to upload {title}: {exc}")

    helper.save_manifest(manifest)
    print(f"Upload complete. Folder {folder_id} ({folder.name}) now has {folder.count} item(s).")


def cmd_run():
    cmd_match()
    cmd_review()
    cmd_upload()


def main():
    parser = argparse.ArgumentParser(
        description="Match album art to Discogs releases and add them to your collection."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("match", help="Image search and match releases into collection_draft.json")
    subparsers.add_parser("review", help="Interactively review and confirm pending manifest items")
    subparsers.add_parser("upload", help="Upload confirmed items to your Discogs collection")
    subparsers.add_parser("run", help="Run match, review, and upload in sequence")

    args = parser.parse_args()
    commands = {
        "match": cmd_match,
        "review": cmd_review,
        "upload": cmd_upload,
        "run": cmd_run,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
