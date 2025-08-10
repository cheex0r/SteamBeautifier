from steam.launch_steam import launch_steam


def execute(context, config):
    if config['launch'] or config['bigpicture']:
        launch_steam(config['bigpicture'])