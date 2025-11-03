import tokens
import albumUrls
import discogs_client  # https://github.com/joalla/discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search


def google_search(imageurl):
    # commenting out to save API calls
    # client = serpapi.Client(api_key=tokens.serpapi_key)
    # results = client.search(engine="google_reverse_image", image_url=imageurl)
    # title = results['image_results'][0]['title']
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
    title = google_search(albumUrls.sgt)
    discogs_collection_update(title)


if __name__ == '__main__':
    main()
