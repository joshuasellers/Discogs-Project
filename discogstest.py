import requests

response = requests.get('https://example.com')
print(response.text)

# For a POST request with data
# https://api.discogs.com/releases/249504 --user-agent "FooBarApp/3.0"

data = {'user-agent': 'FooBarApp/3.0'}
response = requests.post('https://api.discogs.com/releases/249504', data=data)
print(response.json())
