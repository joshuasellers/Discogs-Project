import tokens
import albumUrls
import discogs_client  # https://github.com/joalla/discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search

# commenting out to preserve free api calls
""" 
client = serpapi.Client(api_key=tokens.serpapi_key)
results = client.search(engine="google_reverse_image", image_url=albumUrls.sgt)
title = results['image_results'][0]['title']
"""
title = "Born To Run"

d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)

results = d.search(title, type='release')
first_result = results[0]
print(first_result)
print(first_result.id)

me = d.identity()
print(me)
print(me.collection_folders)

me.collection_folders[0].add_release(first_result.id)

for item in me.collection_folders[0].releases:
    print(item)
