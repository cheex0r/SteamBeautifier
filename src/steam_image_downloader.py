import argparse
import os
import time

from image_downloader import save_image
from steam_api_proxy import get_games_without_600x900_grid_image
from steam_directory_finder import get_steam_path
from steam_ids import steamid64_to_steamid
from steamgriddb_api_proxy import get_gameid_from_steam_appid, get_grid_url_from_gameid, get_hero_url_from_gameid, get_logo_url_from_gameid

def download_missing_images(steam_api_key, steamgriddb_api_key, steam_id64):
    steam_path = get_steam_path()
    steamid = steamid64_to_steamid(steam_id64)
    grid_path = ['userdata', str(steamid), 'config', 'grid']

    appids_with_missing_graphics = get_games_without_600x900_grid_image(steam_api_key, steam_id64)
    for appid in appids_with_missing_graphics:
        print("Getting images for appid: " + str(appid))
        try:
            game_id = get_gameid_from_steam_appid(steamgriddb_api_key, appid)
            get_horizontal_image(steamgriddb_api_key, game_id, steam_path, grid_path, appid)
            get_vertical_image(steamgriddb_api_key, game_id, steam_path, grid_path, appid)
            get_hero_image(steamgriddb_api_key, game_id, steam_path, grid_path, appid)
            get_logo_image(steamgriddb_api_key, game_id, steam_path, grid_path, appid)
            time.sleep(0.1)
        except Exception as e:
            print(f"An exception occurred: {e}")

def get_logo_image(steamgriddb_api_key, gameid, steam_path, grid_path, appid):
    url = get_logo_url_from_gameid(steamgriddb_api_key, gameid)
    filename = str(appid) + "_logo.png"
    download_image(url, steam_path, grid_path, filename)

def get_hero_image(steamgriddb_api_key, gameid, steam_path, grid_path, appid):
    url = get_hero_url_from_gameid(steamgriddb_api_key, gameid)
    filename = str(appid) + "_hero.png"
    download_image(url, steam_path, grid_path, filename)

def get_horizontal_image(steamgriddb_api_key, gameid, steam_path, grid_path, appid):
    url = get_grid_url_from_gameid(steamgriddb_api_key, gameid, dimensions='920x430,460x215')
    filename = str(appid) + ".png"
    download_image(url, steam_path, grid_path, filename)

def get_vertical_image(steamgriddb_api_key, gameid, steam_path, grid_path, appid):
    url = get_grid_url_from_gameid(steamgriddb_api_key, gameid)
    filename = str(appid) + "p.png"
    download_image(url, steam_path, grid_path, filename)

def download_image(url, steam_path, grid_path, image_name):
    full_filepath = os.path.join(url, steam_path, *grid_path, image_name)
    save_image(url, full_filepath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download ')
    parser.add_argument('--steam_api_key', type=str)
    parser.add_argument('--steamgriddb_api_key', type=str)
    parser.add_argument('--steam_id64', type=int)

    args = parser.parse_args()

    download_missing_images(args.steam_api_key, args.steamgriddb_api_key, args.steam_id64)