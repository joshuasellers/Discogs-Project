import tokens
import discogs_client  # https://github.com/joalla/discogs_client
import imageUrl
import json
import os
from pathlib import Path
from serpapi import GoogleSearch  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search

output_file = "discog_output.txt"


def google_search(imageurl):
    # commenting out to save API calls
    params = {
        "api_key": tokens.serpapi_key,  # your serpapi api
        "engine": "google_lens",
        "search_type": "products",
        "q": "Discogs",
        "url": imageurl
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    print(results)
    response = results['visual_matches']
    print(response)
    # title = "Born To Run"
    return response[0]["title"]


def discogs_collection_update(title, url):
    d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)

    results = d.search(title, type='release')
    first_result = results[0]
    print(first_result)

    file_path = Path(output_file)

    if file_path.is_file():
        print(f"The file {file_path} exists - opening it")
        with open(file_path, "a") as file:
            file.write(f"\nGoogle Result: {title} for URL: {url} */* Discogs Result: {first_result}")
    else:
        print(f"The file {file_path} does not exist - creating it")
        with open(file_path, "w") as file:
            file.write(f"Google Result: {title} for URL: {url} */* Discogs Result: {first_result}")


def confirm_additions(file):
    d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)
    final_lines = []

    with open(file, 'r') as f:
        for line in f:
            content = line.split("*/*")
            c0 = content[0].replace("Google Result: ", "")
            c1 = content[1].replace(" Discogs Result: ", "")
            print(f"For the input {c0}, this script got this result from Discogs: {c1}")
            new_discog_input = input("Edit the Discog result (blank for no change): ")
            if new_discog_input != "":
                results = d.search(new_discog_input, type='release')
                first_result = results[0]
                check_input = input(f"Does this match what you want: {first_result}? Y/N: ")
                if check_input == "Y":
                    final_lines.append(f"{content[0]} */* {first_result}")
            else:
                final_lines.append(line)

    with open(file, 'w') as f:
        for line in final_lines:
            f.write(line + "\n")


def update_collection(file):
    # TODO: test function
    d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)
    me = d.identity()

    with open(file, 'r') as f:
        for line in f:
            content = line.split("*/*")
            c0 = content[0].replace("Google Result: ", "")
            c1 = content[1].replace(" Discogs Result: ", "")
            result = c1.strip().replace("<", "").replace(">", "").split(" ")
            if result[1] not in [item.id for item in me.collection_folders[0].releases]:
                me.collection_folders[0].add_release(result[1])
                print(f"{c1} added to collection from Google result: {c0}")

    print("Collection:")
    for item in me.collection_folders[0].releases:
        print(item)


def main():
    # Cleaning up file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"File '{output_file}' has been deleted.")
    else:
        print(f"File '{output_file}' does not exist.")
    # main logic
    urls = imageUrl.get_raw_album_urls()
    for url in urls:
        title = google_search(url)
        discogs_collection_update(title, url)
    confirm_additions(output_file)
    update_collection(output_file)


if __name__ == '__main__':
    main()
