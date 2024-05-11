import argparse
import requests

def get_gameid_from_steam_appid(api_key, steam_app_id):
    url = f"https://www.steamgriddb.com/api/v2/games/steam/{steam_app_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()  # Parse JSON response
        if data.get('success', False):  # Check if 'success' key is present in the response
            game_id = data.get('data', {}).get('id', None)  # Access game ID safely
            if game_id is not None:
                print(f"SteamID {steam_app_id} maps to GameID {game_id}")
                return game_id
            else:
                print(f"No game ID found for Steam app ID {steam_app_id}")
        else:
            print(f"Failed to fetch images from SteamGridDB for app ID {steam_app_id}.")
    else:
        print(f"Failed to fetch images from SteamGridDB for app ID {steam_app_id}. Status code: {response.status_code}")
    return None
    
def get_grid_url_from_gameid(api_key, game_id, dimensions='600x900'):
    url = f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}?dimensions={dimensions}"
    return get_url_from_data(api_key, url, game_id)

def get_hero_url_from_gameid(api_key, game_id):
    url = f"https://www.steamgriddb.com/api/v2/heroes/game/{game_id}"
    return get_url_from_data(api_key, url, game_id)

def get_logo_url_from_gameid(api_key, game_id):
    url = f"https://www.steamgriddb.com/api/v2/logos/game/{game_id}"
    return get_url_from_data(api_key, url, game_id)

def get_url_from_data(api_key, url, game_id):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    print ("Fetching streamgriddb grids from: " + url)
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()  # Parse JSON response
        if data.get('success', False):  # Check if 'success' key is present in the response
            try:
                response_url = data.get('data', [])[0].get('url', None)  # Access grid URL safely
            except:
                print(f"No images found {game_id}")
                return None
            if response_url is not None:
                return response_url
            else:
                print(f"No grid URL found for game ID {game_id}")
        else:
            print(f"Failed to fetch images from SteamGridDB for app ID {game_id}.")
    else:
        print(f"Failed to fetch images from SteamGridDB for app ID {game_id}. Status code: {response.status_code}")
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get images from steamgriddb.')
    parser.add_argument('--api_key', type=str, help='Your steamgriddb key')
    parser.add_argument('--app_id', type=str, help='App Id')
    args = parser.parse_args()

    images = get_gameid_from_steam_appid(args.api_key, args.app_id)
