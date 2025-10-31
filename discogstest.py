import tokens
import discogs_client
import serpapi  # potential free alternative: https://github.com/RMNCLDYO/Google-Reverse-Image-Search

client = serpapi.Client(api_key=tokens.serpapi_key)
results = client.search(engine="google_reverse_image", image_url="https://example.com/image.jpg")
print(results)

d = discogs_client.Client('VinylImageReadingProject/0.1', user_token=tokens.discogs_token)

results = d.search('Stockholm By Night', type='release')
print(results.pages)
