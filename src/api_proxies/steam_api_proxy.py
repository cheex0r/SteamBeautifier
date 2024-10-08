import argparse
import pprint
import requests
from steam.steam_id import SteamId

def get_owned_games(api_key, steam_id: SteamId):
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id.get_steamid64()}&include_appinfo=true"
    owned_games = requests.get(url)
    response_data = owned_games.json().get('response', {})
    if 'games' in response_data:
        return response_data['games']
    else:
        print(f"No games found or an error for user {steam_id.get_steamid64()}.")
        return []

def has_600x900_grid_image(app_id):
    # Steam API endpoint for getting app details
    url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/library_600x900.jpg"

    try:
        # Send a GET request to the Steam API
        response = requests.get(url)

        # Check if the request was successful and the app data is available
        if response.status_code == 200:
             return True
              
    except Exception as e:
        print(f"An error occurred fetching steam library image from steamcdn-a: {e}")
        return False
    return False

def get_games_without_600x900_grid_image(api_key, steam_id: SteamId):
    owned_games_json = get_owned_games(api_key, steam_id)
    games_without_600x900_image = set()

    for game in owned_games_json:
        has_grid_image = has_600x900_grid_image(game['appid'])
        if not has_grid_image:
            games_without_600x900_image.add(game['appid'])
    
    return games_without_600x900_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for Steam games without 600x900 grid images.')
    parser.add_argument('--api_key', type=str, help='Your Steam API key')
    parser.add_argument('--steam_id', type=str, help='Your Steam ID')

    args = parser.parse_args()

    steam_id = SteamId(steamid64=args.steam_id)
    games = get_games_without_600x900_grid_image(args.api_key, steam_id)

    print("Games without a 600x900 grid image:")
    for game in games:
        pprint(game.json())
