import requests
from bs4 import BeautifulSoup
import json
import urllib


def iterate_nested_json(obj):
    """
    helper function to print the contents of a nested JSON
    :param obj:
    :return: none
    """
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


def get_album_links():
    """
    returns all of the links to the album images in this project
    as hosted on github.
    :return: list of album art urls
    """
    url = "https://github.com/joshuasellers/Discogs-Project/blob/main/albums/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    a = soup.find_all('script')
    albums = list(filter(lambda x: "name" in str(x) and "path" in str(x), a))[0]
    json_albums = json.loads(albums.string)
    album_links = []
    if json_albums.get('payload').get('tree').get('items'):
        for item in json_albums.get('payload').get('tree').get('items'):
            album_links.append(url + urllib.parse.quote(item['name']))
    print(album_links)
    return album_links


def get_raw_album_urls():
    """
    returns the raw urls for the hosted images
    to be used for google image search
    :return: list of raw urls
    """
    urls = get_album_links()
    raw_urls = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')
        image_tag = list(filter(lambda x: "displayUrl" in str(x), scripts))[0]
        json_image = json.loads(image_tag.string)
        if json_image.get('payload').get('blob'):
            raw_urls.append(json_image.get('payload').get('blob')['displayUrl'])
    print(raw_urls)
    return raw_urls
