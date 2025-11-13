import tokens
import discogs_client  # https://github.com/joalla/discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search
import imageUrl
import requests


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

    response = requests.get(url, params=params)
    print(response.text)
    #results = GoogleSearch(params).get_dict()
    #ex = results['related_content'][0]['query']
    title = "Born To Run"
    return title


def discogs_collection_update(title):
    d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)

    results = d.search(title, type='release')
    first_result = results[0]
    print(first_result)

    me = d.identity()

    if first_result.id not in [item.id for item in me.collection_folders[0].releases]:
        me.collection_folders[0].add_release(first_result.id)
        print("added to collection")

    for item in me.collection_folders[0].releases:
        print(item)


def main():
    urls = imageUrl.get_raw_album_urls()
    for url in urls:
        title = google_search(url)
        discogs_collection_update(title)


if __name__ == '__main__':
    main()
