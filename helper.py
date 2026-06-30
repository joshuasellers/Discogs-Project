import json
import requests
import urllib
from bs4 import BeautifulSoup

MANIFEST_FILE = "collection_draft.json"

MEDIA_CONDITIONS = [
    "Mint (M)",
    "Near Mint (NM or M-)",
    "Very Good Plus (VG+)",
    "Very Good (VG)",
    "Good Plus (G+)",
    "Good (G)",
    "Fair (F)",
    "Poor (P)",
]

SLEEVE_CONDITIONS = MEDIA_CONDITIONS + ["Generic", "Not Graded", "No Cover"]

CONDITION_ALIASES = {
    "mint": "Mint (M)",
    "m": "Mint (M)",
    "near mint": "Near Mint (NM or M-)",
    "nm": "Near Mint (NM or M-)",
    "near mint (nm or m-)": "Near Mint (NM or M-)",
    "very good plus": "Very Good Plus (VG+)",
    "vg+": "Very Good Plus (VG+)",
    "very good": "Very Good (VG)",
    "vg": "Very Good (VG)",
    "good plus": "Good Plus (G+)",
    "g+": "Good Plus (G+)",
    "good": "Good (G)",
    "g": "Good (G)",
    "fair": "Fair (F)",
    "f": "Fair (F)",
    "poor": "Poor (P)",
    "p": "Poor (P)",
    "generic": "Generic",
    "not graded": "Not Graded",
    "no cover": "No Cover",
}

DEFAULT_MANIFEST = {
    "defaults": {
        "media_condition": "Near Mint (NM or M-)",
        "sleeve_condition": "Near Mint (NM or M-)",
        "folder_id": 1,
    },
    "items": [],
}


def default_manifest():
    return json.loads(json.dumps(DEFAULT_MANIFEST))


def load_manifest(path=MANIFEST_FILE):
    try:
        with open(path, "r") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        manifest = default_manifest()
    manifest.setdefault("defaults", default_manifest()["defaults"])
    manifest.setdefault("items", [])
    return manifest


def save_manifest(manifest, path=MANIFEST_FILE):
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def normalize_media_condition(value, default=None):
    return _normalize_condition(value, MEDIA_CONDITIONS, default)


def normalize_sleeve_condition(value, default=None):
    return _normalize_condition(value, SLEEVE_CONDITIONS, default)


def _normalize_condition(value, valid_values, default):
    if not value:
        return default
    stripped = value.strip()
    if stripped in valid_values:
        return stripped
    alias = CONDITION_ALIASES.get(stripped.lower())
    if alias and alias in valid_values:
        return alias
    for valid in valid_values:
        if valid.lower() == stripped.lower():
            return valid
    return default


def is_yes(value):
    return value.strip().lower() in ("y", "yes")


def release_title(release):
    if release.artists:
        return f"{release.artists[0].name} - {release.title}"
    return release.title


def get_collection_field_ids(client, username):
    data = client._get(f"{client._base_url}/users/{username}/collection/fields")
    return {field["name"]: field["id"] for field in data.get("fields", [])}


def set_collection_field(client, username, folder_id, release_id, instance_id, field_id, value):
    encoded = urllib.parse.quote(value)
    url = (
        f"{client._base_url}/users/{username}/collection/folders/{folder_id}"
        f"/releases/{release_id}/instances/{instance_id}/fields/{field_id}?value={encoded}"
    )
    client._post(url, None)


def add_release_to_folder(client, folder, release_id):
    resource_url = folder.fetch("resource_url")
    return client._post(f"{resource_url}/releases/{release_id}", None)


def get_folder(client, me, folder_id):
    for folder in me.collection_folders:
        if folder.id == folder_id:
            return folder
    raise ValueError(f"Collection folder {folder_id} not found")


def get_album_links():
    """
    returns all of the links to the album images in this project
    as hosted on github.
    :return: list of album art urls
    """
    url = "https://github.com/joshuasellers/Discogs-Project/blob/main/albums/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    a = soup.find_all("script")
    albums = list(filter(lambda x: "name" in str(x) and "path" in str(x), a))[0]
    json_albums = json.loads(albums.string)
    album_links = []
    print("Getting link")
    if json_albums.get("payload").get("tree").get("items"):
        for item in json_albums.get("payload").get("tree").get("items"):
            album_links.append(url + urllib.parse.quote(item["name"]))
    return album_links


def get_raw_album_urls():
    """
    returns the raw urls for the hosted images
    to be used for google image search
    :return: list of raw urls
    """
    urls = get_album_links()
    raw_urls = []
    for url in urls:
        print("URL " + url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        scripts = soup.find_all("script")
        image_tag = list(filter(lambda x: "displayUrl" in str(x), scripts))[0]
        json_image = json.loads(image_tag.string)
        if json_image.get("payload").get("blob"):
            raw_urls.append(json_image.get("payload").get("blob")["displayUrl"])
    return raw_urls


def multiple_choice(options):
    """
    Gets user input for a list of options
    :param options: list to chose from
    :return: the selected list item
    """
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")

    while True:
        choice_str = input("Enter the number of your choice: ")
        try:
            choice_int = int(choice_str)
            if 1 <= choice_int <= len(options):
                selected_option = options[choice_int - 1]
                print(f"You selected: {selected_option}")
                return selected_option
            print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
