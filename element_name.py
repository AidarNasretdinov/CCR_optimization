import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# figma token and id's
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")  # create .env file and add personal figma token
FILE_ID = '9EUMkqC8y8RcB55XTWOzew'  # ID file
NODE_ID = '39046:942108'  # Node ID frame

# API url
base_url = f'https://api.figma.com/v1/files/{FILE_ID}/nodes?ids={NODE_ID}'

# headers request for token
headers = {
    'X-Figma-Token': FIGMA_TOKEN
}

# request to figma API for exact frame info
response = requests.get(base_url, headers=headers)

if response.status_code == 200:
    figma_data = response.json()
    frame_node = figma_data['nodes'][NODE_ID]['document']

    # searching for 'body' element
    body_element = next((child for child in frame_node.get('children', []) if child['name'] == 'body'), None)

    if body_element:
        print(f"Element 'body' found!")

        # searching for name 'content' inside 'body'
        content_element = next((child for child in body_element.get('children', []) if child['name'] == 'content'),
                               None)
        if not content_element:
            print(f"Element with name 'content' not found.")
        else:
            print(f"Element 'content' found!")

            # extracting all elements from 'content'
            content_children = content_element.get('children', [])

            extracted_elements = []

            # go through all the elements inside 'content'
            for element in content_children:
                # checking element visible or not
                if element.get('visible', True):
                    element_name = element.get('name', 'Without name')

                    """
                     Skip element containing 'footer' in name.
                     Temporary solution, in the next ver. footer will be an individual element inside 'body' frame.
                     !!! For now 'footer' is an element of 'content' frame !!!
                    """

                    if 'footer' in element_name.lower():
                        print(f"Element '{element_name}' contains 'footer' and was skipped.")
                        continue

                    print(f"Element found: {element_name}")
                    # adding element inside list
                    extracted_elements.append(element_name)
                else:
                    print(f"Element '{element.get('name', 'Without name')}' hidden and skipped.")

            json_data = {
                "content_element": "content",
                "elements": extracted_elements
            }

            with open('output.json', 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)

            print("JSON has been created!")
    else:
        print(f"Element with name 'body' not found.")
else:
    print(f"Error when requesting from Figma: {response.status_code}")
    print(response.text)