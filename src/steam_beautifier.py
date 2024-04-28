import sys

from steam_remove_whats_new import remove_whats_new
from launch_steam import launch_steam

is_bigpicture = "--bigpicture" in sys.argv
is_launch_steam = "--launch" in sys.argv or is_bigpicture

remove_whats_new()
if is_launch_steam:
    launch_steam(is_bigpicture)