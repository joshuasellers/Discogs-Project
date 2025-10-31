import tokens
import discogs_client

d = discogs_client.Client('ExampleApplication/0.1', user_token=tokens.token)

results = d.search('Stockholm By Night', type='release')
print(results.pages)
