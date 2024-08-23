import argparse
import os
import time
from tqdm import tqdm

from api_proxies.steam_api_proxy import get_owned_games, has_600x900_grid_image
from api_proxies.steamgriddb_api_proxy import (
    get_gameid_from_steam_appid,
    get_grid_url_from_gameid,
    get_hero_url_from_gameid, get_logo_url_from_gameid
)
from data.app_data import AppData
from downloader.image_downloader import save_image_as_png
from steam.steam_directory_finder import (
    get_steam_path,
    get_grid_path
)
from steam.steam_id import SteamId


CACHE_FILE_NAME = 'games_with_vertical_grids.json'

def download_missing_images(steam_api_key, steamgriddb_api_key, steam_id: SteamId, skip_if_exists=True):
    owned_games = get_owned_games(steam_api_key, steam_id.get_steamid64())
    steam_path = get_steam_path()
    grid_path = get_grid_path(steam_id.get_steamid64())
    steam_grid_path = os.path.join(steam_path, grid_path)
    existing_grid_images = get_appids_with_custom_images(steam_grid_path)
    steam_games_with_vertical_grid_images = get_steam_games_with_vertical_grids()
    for game in tqdm(owned_games, desc="Downloading images from SteamGridDB"):
        appid = str(game['appid'])
        download_missing_images_for_game(steamgriddb_api_key,
                                         appid,
                                         steam_grid_path,
                                         existing_grid_images,
                                         steam_games_with_vertical_grid_images,
                                         skip_if_exists)
    save_steam_games_with_vertical_grids(steam_games_with_vertical_grid_images)


def get_appids_with_custom_images(path):
    existing_grid_images = set()
    with os.scandir(path) as it:
        for entry in it:
            # Vertical grid filenames end in p
            if 'p.' in entry.name: 
                entry_name = entry.name.split('p')[0]
                existing_grid_images.add(entry_name)
    return existing_grid_images


def get_steam_games_with_vertical_grids():
    return AppData.read_json_from_file(CACHE_FILE_NAME, set)


def save_steam_games_with_vertical_grids(games):
    AppData.save_json_to_file(CACHE_FILE_NAME, games, list)


def download_missing_images_for_game(steamgriddb_api_key,
                                     appid, steam_grid_path,
                                     existing_grid_images,
                                     steam_games_with_vertical_grid_images,
                                     skip_if_exists=True):
    # TODO: ivestigate why VRX_Player_Steam_Edition causes issues appid: 844880
    if appid == '844880':
        return
    try:
        if skip_if_exists and appid in existing_grid_images:
            return
        if appid in steam_games_with_vertical_grid_images or has_600x900_grid_image(appid):
            steam_games_with_vertical_grid_images.add(appid)
            return
        time.sleep(0.1)
        game_id = get_gameid_from_steam_appid(steamgriddb_api_key, appid)
        get_vertical_image(steamgriddb_api_key, game_id, steam_grid_path, appid)
        get_horizontal_image(steamgriddb_api_key, game_id, steam_grid_path, appid)
        get_hero_image(steamgriddb_api_key, game_id, steam_grid_path, appid)
        get_logo_image(steamgriddb_api_key, game_id, steam_grid_path, appid)
    except Exception as e:
        print(f"An exception occurred getting images for Steam AppId {appid}: {e}")


def get_logo_image(steamgriddb_api_key, gameid, steam_grid_path, appid):
    url = get_logo_url_from_gameid(steamgriddb_api_key, gameid)
    filename = str(appid) + "_logo.png"
    download_image(url, steam_grid_path, filename)


def get_hero_image(steamgriddb_api_key, gameid, steam_grid_path, appid):
    url = get_hero_url_from_gameid(steamgriddb_api_key, gameid)
    filename = str(appid) + "_hero.png"
    download_image(url, steam_grid_path, filename)


def get_horizontal_image(steamgriddb_api_key, gameid, steam_grid_path, appid):
    url = get_grid_url_from_gameid(steamgriddb_api_key, gameid, dimensions='920x430,460x215')
    filename = str(appid) + ".png"
    download_image(url, steam_grid_path, filename)


def get_vertical_image(steamgriddb_api_key, gameid, steam_grid_path, appid):
    url = get_grid_url_from_gameid(steamgriddb_api_key, gameid)
    filename = str(appid) + "p.png"
    download_image(url, steam_grid_path, filename)


def download_image(url, steam_grid_path, image_name):
    full_filepath = os.path.join(steam_grid_path, image_name)
    save_image_as_png(url, full_filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download ')
    parser.add_argument('--steam_api_key', type=str, default=None)
    parser.add_argument('--steamgriddb_api_key', type=str)
    parser.add_argument('--steam_id64', type=int)
    parser.add_argument('--steam_app_id', type=int, default=None)
    parser.add_argument('--skip_if_exists', type=bool, default=True)

    args = parser.parse_args()

    steam_id = SteamId(steamid64=args.steam_id64)

    skip_if_exists=False
    if args.skip_if_exists is not None:
        skip_if_exists=True
    if args.steam_api_key is not None:
        download_missing_images(args.steam_api_key, args.steamgriddb_api_key, steam_id, args.skip_if_exists)
    if args.steam_app_id is not None:
        download_missing_images_for_game(args.steamgriddb_api_key, steam_id, args.steam_app_id, args.skip_if_exists)
