import requests
from bs4 import BeautifulSoup
import json

"""
def iterate_nested_json(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"Key: {key}, Value: {value}")
            iterate_nested_json(value)  # Recurse for nested dictionaries
    elif isinstance(obj, list):
        for item in obj:
            iterate_nested_json(item)  # Recurse for items in lists
    else:
        # Handle primitive types (strings, numbers, booleans)
        pass
"""


url = "https://github.com/joshuasellers/Discogs-Project/blob/main/albums/sgt.%20pepper's.jpeg"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the image tag (adjust selector based on the website's HTML)
scripts = soup.find_all('script')
image_tag = list(filter(lambda x: "displayUrl" in str(x), scripts))[0]
json_data = json.loads(image_tag.string)
if json_data.get('payload').get('blob'):
    print(f"Image URL found: {json_data.get('payload').get('blob')['displayUrl']}")
else:
    print("Image not found on the page.")