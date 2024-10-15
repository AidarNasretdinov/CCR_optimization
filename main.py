import re
import requests
import json
import os
from dotenv import load_dotenv
import uuid

# load variables from .env file
load_dotenv()

def generate_unique_id():
    return str(uuid.uuid4())

# Load a JSON file
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"File {file_path} loaded successfully.")
            # Print JSON for verification
            # print(f"Contents of {file_path}: {json.dumps(data, indent=4, ensure_ascii=False)}")
            return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"JSON decoding error in file {file_path}.")
        return None

# Save changes to a JSON file
def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Changes saved to {file_path}.")
    return data

# Create a Slider widget based on type
def create_slider_widget(widget_type):
    return {
        "id": generate_unique_id(),
        "type": widget_type,
        "props": {
            'slides': [],
            "hideMobileText": False
        },
        "widget": "Slider",
        "isVisible": True
    }

# Find home page by path and type
def find_home_page(lobby_settings):
    # Search in settings.pages
    pages = lobby_settings.get("settings", {}).get("pages", [])
    for page in pages:
        # Check if path="/" and type="home"
        if page.get("path") == "/" and page.get("type") == "home":
            return page
    return None

# Add widget to home page
def add_slider_to_home(lobby_settings, slider_widget):
    home_page = find_home_page(lobby_settings)

    if home_page:
        # Check if "widgets" exists
        if "widgets" in home_page.get("content", {}):
            home_page["content"]["widgets"] = [slider_widget]
        else:
            home_page["content"]["widgets"] = [slider_widget]
        print("Widget added to 'home' page.")
    else:
        print("Home page not found in lobby_settings.json")

def main():
    # Load files
    output_json = load_json('output.json')  # Input file
    lobby_settings = load_json('lobby_settings.json')  # Lobby settings file

    # If files loaded
    if output_json and lobby_settings:
        # Check for elements in output_json
        if "elements" in output_json:
            for element in output_json["elements"]:
                # Check if element is Slider and get its type
                if element.lower().startswith("slider"):
                    # Extract slider type (e.g., "E" from "slider E")
                    widget_type = element.split()[-1]

                    # Create Slider widget with correct type
                    slider_widget = create_slider_widget(widget_type)

                    # Add it to home page
                    add_slider_to_home(lobby_settings, slider_widget)
                    print(f"Added Slider widget of type {widget_type} to 'home' page.")
        else:
            print("Elements not found in output.json.")

        # Save changes to lobby_settings.json
        save_json('lobby_settings.json', lobby_settings)
        return lobby_settings
    else:
        print("Failed to load necessary files.")
        return lobby_settings

def extract_figma_ids(figma_url):
    file_pattern = r"https://www.figma.com/design/([a-zA-Z0-9]+)"
    node_pattern = r"node-id=([0-9\-:]+)"

    # Find file_id
    file_match = re.search(file_pattern, figma_url)
    file_id = file_match.group(1) if file_match else None

    # Find node_id and replace '-' with ':' for correct format
    node_match = re.search(node_pattern, figma_url)
    node_id = node_match.group(1).replace('-', ':') if node_match else None

    return file_id, node_id

# Clean element names, remove extra spaces and slashes
def clean_element_name(name):
    return ' '.join(name.replace('/', ' ').split())

# Main function to request data from Figma API
def figma_json(figma_url):
    FILE_ID, NODE_ID = extract_figma_ids(figma_url)

    if not FILE_ID or not NODE_ID:
        print("Invalid Figma URL. Please provide a valid URL.")
        return

    # Get Figma token from .env
    FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

    # Construct API request URL
    base_url = f'https://api.figma.com/v1/files/{FILE_ID}/nodes?ids={NODE_ID}'

    # API request headers
    headers = {
        'X-Figma-Token': FIGMA_TOKEN
    }

    # Request frame data from Figma API
    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        figma_data = response.json()
        frame_node = figma_data['nodes'][NODE_ID]['document']

        # Find 'body' element
        body_element = next((child for child in frame_node.get('children', []) if child['name'] == 'body'), None)

        if body_element:
            print(f"Element 'body' found!")

            # Find 'content' inside 'body'
            content_element = next((child for child in body_element.get('children', []) if child['name'] == 'content'), None)

            if not content_element:
                print(f"Element with name 'content' not found.")
            else:
                print(f"Element 'content' found!")

                content_children = content_element.get('children', [])
                extracted_elements = []

                # Loop through all elements in 'content'
                for element in content_children:
                    if element.get('visible', True):
                        element_name = element.get('name', 'Without name')

                        # Skip elements containing 'footer'
                        if 'footer' in element_name.lower():
                            print(f"Element '{element_name}' contains 'footer' and was skipped.")
                            continue

                        # Clean element name
                        cleaned_name = clean_element_name(element_name)
                        print(f"Element found: {cleaned_name}")

                        # Add element to list
                        extracted_elements.append(cleaned_name)
                    else:
                        print(f"Element '{element.get('name', 'Without name')}' hidden and skipped.")

                # Create JSON data
                json_data = {
                    "content_element": "content",
                    "elements": extracted_elements
                }

                # Save JSON to output.json
                with open('output.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

                print("JSON has been created!")
        else:
            print(f"Element with name 'body' not found.")
    else:
        print(f"Error when requesting from Figma: {response.status_code}")
        print(response.text)

def make_request(url, headers, payload=None, method='GET'):
    # Send a request to the given URL
    try:
        if method == 'POST':
            response = requests.post(url, json=payload, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        response.raise_for_status()  # for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during {method} request: {e}")
        return None


def authenticate(username, password):
    # log in the user and return the token
    url = "https://mbo.slotegrator.tech/api/sso/login/admin"
    payload = {
        "EmailOrLogin": username,
        "password": password,
    }
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

    result = make_request(url, headers, payload, method='POST')
    if result and 'token' in result:
        print("Authentication successful, token obtained.")
        return result['token']
    print("Authentication failed.")
    return None


def fetch_lobby_settings(uuid, token, x_node_id):
    # Fetch lobby settings using the provided UUID
    url = f'https://mbo.slotegrator.tech/api/ccr/api/lobbies/{uuid}'
    headers = {
        'accept': 'application/json',
        'token': token,
        'x-node-id': x_node_id,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    }
    lobbyVersionId = ''
    data = make_request(url, headers)
    if data:
        lobbyVersionId = data["id"]
        data["id"] = uuid
        with open('lobby_settings.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return lobbyVersionId, headers
        print("Data successfully written to lobby_settings.json.")
    else:
        print("Failed to fetch lobby settings.")
    return lobbyVersionId, headers


# main
if __name__ == "__main__":
    # username & password from .env file
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    # check for creds
    if not username or not password:
        print("Username or password is missing. Please set them in the .env file.")
    else:
        # log in and get token
        token = authenticate(username, password)
        if token:
            # user input hall uuid and lobby uuid
            # x_node_id = input("Enter the HALL UUID (x-node-id): ")  # ("Enter the HALL UUID (x-node-id):
            # uuid_to_fetch = input("Enter the LOBBY UUID: ")  # input("Enter the LOBBY UUID: ")
            #
            # figma_url = input("Please enter the Figma URL: ")
            x_node_id = 'fcf5ab1b-d7b7-43b6-9dd7-ce6d62d4b5e7'  # ("Enter the HALL UUID (x-node-id):
            uuid_to_fetch = 'fc691848-9e2f-4c82-a939-5d5bcf388651'  # input("Enter the LOBBY UUID: ")

            figma_url = 'https://www.figma.com/design/tKZJbHcDHh5VJB6KIdYTQp/FLICK?node-id=3409-536213&node-type=frame&t=cNfvW1tmIZgjHJpl-0'
            # Pass the URL to the main function
            figma_json(figma_url)
            # FILE_ID = input("Enter the FILE_ID: ")
            # NODE_ID = input("Enter the NODE_ID: ")
            # figma_json(FILE_ID, NODE_ID)

            lobbyVersionId, headers = fetch_lobby_settings(uuid_to_fetch, token, x_node_id)  # fetch lobby settings

            response = requests.patch(
                'https://mbo.slotegrator.tech/api/ccr/api/lobbies/' + lobbyVersionId,
                headers=headers,
                json=main(),
            )
            print(response.status_code, response.text)
