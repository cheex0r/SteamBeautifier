from steam.steam_image_downloader import download_missing_images


def execute(context, config):
    if not config.get('download-images', False):
        return
    
    steam_id = context.get('steam_id')
    
    download_missing_images(
        config['steam_api_key'],
        config['steamgriddb_api_key'],
        steam_id)