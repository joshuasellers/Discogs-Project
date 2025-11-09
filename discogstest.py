import tokens
import albumUrls
import discogs_client  # https://github.com/joalla/discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect


def dropboxCall(app, secret):
    """
    https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html#dropbox.dropbox_client.Dropbox
    """
    auth_flow = DropboxOAuth2FlowNoRedirect(app, secret)

    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print('Error: %s' % (e,))
        exit(1)

    with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
        print(dbx.users_get_current_account())
        print(dbx.sharing_list_folders())
        print("Successfully set up client!")


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
    dropboxCall(tokens.dropbox_app,tokens.dropbox_secret)


if __name__ == '__main__':
    main()
