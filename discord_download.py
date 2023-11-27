import os
import yaml
import requests
from tqdm import tqdm
from pathvalidate import sanitize_filename
from json_handling import save_to_kemono_favorites

CONFIG_PATH = "Config"
SETTINGS_FILE = os.path.join(CONFIG_PATH, "user_settings.yaml")
BASE_URL = "https://kemono.su"  # Updated base URL

def read_stash_path_from_yaml():
    """Read stash_path from the YAML settings file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = yaml.safe_load(f)
            return settings.get('stash_path', '')
    return ''


def clear_console(artist_name_or_id, channel_name=None):
    """Clear the console and display the header."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{'='*80}")
    if channel_name:
        print(f"Downloading posts from: {artist_name_or_id} in channel: {channel_name}")
    else:
        print(f"Downloading posts from: {artist_name_or_id}")
    print(f"{'='*80}\n")



def get_artist_name_from_id(artist_id, combined_data):
    """
    Given an artist ID and a combined list of creators, return the artist's name.
    """
    for creator in combined_data:
        if creator['id'] == artist_id:
            return creator['name']
    return None


def get_or_set_download_preference():
    """Get the user's download preference or prompt them to set it."""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = yaml.safe_load(f)
            preference = settings.get('download_preference', 0)
            if preference != 0:
                return str(preference)

    # Prompt the user for their preference
    choice = ''
    while choice not in ['1', '2']:
        print("\nWith Discord users the files can get a little messy, so you have 2 options to choose from:")
        print("You can change this later in settings.\n")
        print("1. Save each post in a separate folder.")
        print("2. Save all files in the channel folder.")
        choice = input("\nEnter your choice (1/2): ")
        os.system('cls' if os.name == 'nt' else 'clear')
    choice = int(choice)

    # Update the download_preference in the settings dictionary
    settings['download_preference'] = choice

    # Save the updated settings back to the YAML file
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)
    with open(SETTINGS_FILE, 'w') as f:
        yaml.dump(settings, f)

    return choice


def sanitize_attachment_name(name):
    # Remove any URL components
    name = name.replace("https://", "").replace("http://", "")
    # Further sanitize the name to remove invalid characters
    return sanitize_filename(name)


def fetch_discord_channels(server_id):
    """Fetch the list of channels for a given server."""
    url = f"{BASE_URL}/api/v1/discord/channel/lookup/{server_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for URL: {url}")
        print(response.text)
        return []

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON from URL: {url}")
        print(response.text)
        return []


def get_post_folder_name(post):
    """Generate a folder name for a given post."""
    if date := post.get('published') or post.get('added'):
        return sanitize_filename(date)
    else:
        return sanitize_filename(post.get('id', 'Unknown'))


def fetch_discord_posts(channel_id, skip_value):
    """Fetch posts for a given channel."""
    response = requests.get(f"{BASE_URL}/api/v1/discord/channel/{channel_id}?skip={skip_value}")
    if response.status_code == 200:
        return response.json()
    return []


def scrape_discord_server(server_id):
    from download import download_file, save_content_to_txt
    stash_path = read_stash_path_from_yaml()
    creators_list = requests.get("https://kemono.su/api/v1/creators.txt").json()
    artist_name = sanitize_filename(get_artist_name_from_id(server_id, creators_list))

    # If artist name is not found, default to server_id
    artist_name_or_id = artist_name if artist_name else server_id

    # Use stash_path from YAML file as the base directory
    base_path = os.path.join(stash_path, "Creators", "Kemono", artist_name_or_id)

    download_preference = get_or_set_download_preference()

    channels = fetch_discord_channels(server_id)
    for channel in channels:
        print(f"Fetching posts from channel: {channel['name']}...\n")
        channel_path = os.path.join(base_path, channel['name'])

        skip_value = 0
        last_post_id = None
        while True:
            posts = fetch_discord_posts(channel['id'], skip_value)
            if not posts:
                break

            current_last_post_id = posts[-1]['id']

            if last_post_id == current_last_post_id:
                break  # Break the loop if the last post ID starts repeating

            last_post_id = current_last_post_id  # Update the last_post_id for the next iteration
            skip_value += 10  # Increment skip value for the next batch

            for post in posts:
                post_folder_name = get_post_folder_name(post)
                post_folder_path = os.path.join(channel_path, post_folder_name)

                # If preference is to save all in the channel folder, adjust paths
                if download_preference == '2':
                    post_folder_path = channel_path
                    post_date_prefix = f"{post_folder_name}_"
                else:
                    post_date_prefix = ""

                if not os.path.exists(post_folder_path):
                    os.makedirs(post_folder_path)

                for attachment in post.get('attachments', []):
                    attachment_url = BASE_URL + attachment.get('path', '')
                    attachment_name = sanitize_attachment_name(post_date_prefix + attachment.get('name', ''))
                    if attachment_url and attachment_name:
                        download_file(attachment_url, post_folder_path, attachment_name, BASE_URL, artist_name_or_id, channel['name'])

                save_content_to_txt(post_folder_path, post.get('content', ''), post.get('embed', {}), post)

        print(f"Finished fetching posts from channel: {channel['name']}\n")

    print(f"\n{'='*40}")
    print("Download complete!")
    print(f"{'='*40}\n")

    # Call save_to_kemono_favorites to save the data of the Discord server
    creators_list = fetch_creator_data()
    artist_data = next((item for item in creators_list if item['id'] == server_id), None)
    if artist_data:
        save_to_kemono_favorites(artist_data)
    else:
        print(f"Failed to find data for artist with server ID: {server_id}")