import tokens
import albumUrls
import discogs_client  # https://github.com/joalla/discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search

client = serpapi.Client(api_key=tokens.serpapi_key)
results = client.search(engine="google_reverse_image", image_url=albumUrls.sgt)
title = results['image_results'][0]['title']

d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)

results = d.search(title, type='release')
print(results[0].artists[0])
