import sys
import argparse

from steam_remove_whats_new import remove_whats_new
from launch_steam import launch_steam


parser = argparse.ArgumentParser(description='Check for Steam games without 600x900 grid images.')
parser.add_argument('--launch', type=bool, help='Launch Steam', default=False)
parser.add_argument('--bigpicture', type=bool, help='Start Steam in BicPicture mode', default=False)
parser.add_argument('--steam_api_key', type=str, help='Steam API Key for fetching grid images')
parser.add_argument('--steamgriddb_api_key', type=str, help='SteamGridDb API Key for fetching grid images')
parser.add_argument('--steam_id', type=int, help='User\'s SteamID64')
args = parser.parse_args()

remove_whats_new()
if args.launch or args.bigpicture:
    launch_steam(args.bigpicture)