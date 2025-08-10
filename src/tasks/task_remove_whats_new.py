from steam.steam_remove_whats_new import remove_whats_new


def execute(context, config):
    if not config.get('remove_whats_new', False):
        return
    
    remove_whats_new()