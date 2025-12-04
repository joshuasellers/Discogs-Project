import tokens
import discogs_client  # https://github.com/joalla/discogs_client
import imageUrl
import requests
import json
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

    me = d.identity()

    file_path = Path(output_file)

    if file_path.is_file():
        print(f"The file {file_path} exists.")
        with open(file_path, "a") as file:
            file.write(f"\nGoogle Result: {title} for URL: {url} */* Discogs Result: {first_result}")
    else:
        print(f"The file {file_path} does not exist")
        with open(file_path, "w") as file:
            file.write(f"Google Result: {title} for URL: {url} */* Discogs Result: {first_result}")

    confirm_additions(output_file)
    """ Commenting this out for now
    if first_result.id not in [item.id for item in me.collection_folders[0].releases]:
        me.collection_folders[0].add_release(first_result.id)
        print("added to collection")
    """
    print("Collection:")
    for item in me.collection_folders[0].releases:
        print(item)


def confirm_additions(file):
    # TODO - test new function
    d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)
    final_lines = []

    with open(file, 'r') as f:
        for line in f:
            content = line.split("*/*")
            print(f"For the input {content[0]}, this script got this result from Discogs: {content[1]}")
            new_discog_input = input("Edit the Discog result (blank for no change): ")
            results = d.search(new_discog_input, type='release')
            first_result = results[0]
            check_input = input(f"Does this match what you want: {first_result}? Y/N")
            if check_input == "Y":
                content[1] = first_result
                final_lines.append(content)

    with open(file, 'w') as f:
        for line in final_lines:
            f.write(line[0] + " */* " + line[1] + "\n")


def main():
    urls = imageUrl.get_raw_album_urls()
    for url in urls:
        title = google_search(url)
        discogs_collection_update(title, url)


if __name__ == '__main__':
    main()
