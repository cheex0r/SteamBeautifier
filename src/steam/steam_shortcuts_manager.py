import os
import vdf
import zlib

from steam.constants import SHORTCUTS_VDF_PATH

def _generate_non_steam_game_appid(exe_path, app_name):
    combined_string = f"{exe_path}{app_name}"
    crc32_value = zlib.crc32(combined_string.encode('utf-8')) & 0xFFFFFFFF
    
    intBytes = [
        (crc32_value >> 24) & 0xFF,
        (crc32_value >> 16) & 0xFF,
        (crc32_value >> 8) & 0xFF,
        crc32_value & 0xFF
    ]
    
    # Reassemble the appid from the bytes
    appid = (
        (intBytes[0] << 24) |
        (intBytes[1] << 16) |
        (intBytes[2] << 8) |
        intBytes[3]
    )
    
    appid = (((appid | 0x80000000) << 32) | 0x02000000) >> 32
    appid_old = (((crc32_value | 0x80000000) << 32) | 0x02000000)
    
    return str(appid), str(appid_old)


def get_shortcuts_vdf_path_from_steamid(steam_dir, steam_id):
    return os.path.join(steam_dir, SHORTCUTS_VDF_PATH.format(user_id=steam_id))


def parse_shortcuts_vdf(steam_dir, user_id):
    file_path = get_shortcuts_vdf_path_from_steamid(steam_dir, user_id)
    apps_info = {}
    
    with open(file_path, 'rb') as f:
        data = vdf.binary_load(f)
        
    shortcuts = data.get('shortcuts', {})
    
    for app_id, app_data in shortcuts.items():
        app_name = app_data.get('appname', 'Unknown')
        exe_path = app_data.get('exe', 'Unknown')   
        grid_image_id = _generate_non_steam_game_appid(exe_path, app_name)[0]
        app_info = {
            'AppName': app_name,
            'Exe': exe_path,
            'StartDir': app_data.get('StartDir', 'Unknown'),
            'LaunchOptions': app_data.get('LaunchOptions', ''),
            'ShortcutPath': app_data.get('ShortcutPath', ''),
            'Icon': app_data.get('icon', ''),
            'Tags': app_data.get('tags', []),
            'AppId': str(app_id)
        }
        apps_info[grid_image_id] = app_info
    
    return apps_info
