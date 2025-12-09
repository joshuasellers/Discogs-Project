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
    print("Getting link")
    if json_albums.get('payload').get('tree').get('items'):
        for item in json_albums.get('payload').get('tree').get('items'):
            album_links.append(url + urllib.parse.quote(item['name']))
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
        print("URL " + url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')
        image_tag = list(filter(lambda x: "displayUrl" in str(x), scripts))[0]
        json_image = json.loads(image_tag.string)
        if json_image.get('payload').get('blob'):
            raw_urls.append(json_image.get('payload').get('blob')['displayUrl'])
    return raw_urls


def multiple_choice(options):
    """
    Gets user input for a list of options
    :param options: list to chose from
    :return: the selected list item
    """
    # Display options with numbers starting from 1
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")

    while True:
        # Get user input as a string and attempt to convert to an integer
        choice_str = input("Enter the number of your choice: ")
        try:
            choice_int = int(choice_str)
            # Check if the chosen number is within the valid range
            if 1 <= choice_int <= len(options):
                selected_option = options[choice_int - 1]
                print(f"You selected: {selected_option}")
                return selected_option  # Exit the loop once a valid choice is made
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            # Handle cases where the user enters non-integer input
            print("Invalid input. Please enter a valid number.")
