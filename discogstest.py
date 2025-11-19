import tokens
import discogs_client  # https://github.com/joalla/discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search
import imageUrl
import requests
import json
from pathlib import Path


def google_search(imageurl):
    # commenting out to save API calls
    params = {
        'api_key': tokens.serpapi_key,  # your serpapi api
        "engine": "google_lens",
        "search_type": "products",
        "q": "Discogs",
        'url': imageurl
    }
    url = "https://www.searchapi.io/api/v1/search"
    print("Getting google result")
    response = requests.get(url, params=params)
    print(response)
    response_json = json.loads(response.text)
    print(response_json)
    # title = "Born To Run"
    return response_json["visual_matches"][0]["title"]


def discogs_collection_update(title):
    d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)

    results = d.search(title, type='release')
    first_result = results[0]
    print(first_result)

    me = d.identity()

    file_path = Path("discog_output.txt")

    if file_path.is_file():
        print(f"The file {file_path} exists.")
        with open(file_path, "a") as file:
            file.write(f"\n{title} | {first_result}")
    else:
        print(f"The file {file_path} does not exist")
        with open(file_path, "w") as file:
            file.write(f"{title} | {first_result}")

    """ Commenting this out for now
    if first_result.id not in [item.id for item in me.collection_folders[0].releases]:
        me.collection_folders[0].add_release(first_result.id)
        print("added to collection")
    """
    print("Collection:")
    for item in me.collection_folders[0].releases:
        print(item)


def main():
    urls = imageUrl.get_raw_album_urls()
    for url in urls:
        title = google_search(url)
        discogs_collection_update(title)


if __name__ == '__main__':
    main()
