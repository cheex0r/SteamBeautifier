from cloud.dropbox_manager import DropboxManager
from filemanagers.config_file_manager import ConfigFileManager
from config.start_on_boot_manager import start_on_boot
from steam.launch_steam import launch_steam
from steam.steam_directory_finder import get_grid_path, get_steam_ids
from steam.steam_image_downloader import download_missing_images
from steam.steam_remove_whats_new import remove_whats_new
from steam.steam_shortcuts_manager import parse_shortcuts_vdf
from steam.steam_id import SteamId
from steam.steam_directory_finder import get_steam_path
from filemanagers.dropbox_manifest_file_manager import DropboxManifestFileManager

from api_proxies.nextcloud_api_proxy import NextcloudApiProxy
from cloud.nextcloud_manager import NextcloudManager
from cloud.steam_grid_sync_manager import SteamGridSyncManager

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text

HEADER = r"""
 ____    __                                                             
/\  _`\ /\ \__                                                          
\ \,\L\_\ \ ,_\    __     __      ___ ___                               
 \/_\__ \\ \ \/  /'__`\ /'__`\  /' __` __`\                             
   /\ \L\ \ \ \_/\  __//\ \L\.\_/\ \/\ \/\ \                            
   \ `\____\ \__\ \____\ \__/.\_\ \_\ \_\ \_\                           
    \/_____/\/__/\/____/\/__/\/_/\/_/\/_/\/_/                           
                                                                        
                                                                        
 ____                              __           ___                     
/\  _`\                           /\ \__  __  /'___\ __                 
\ \ \L\ \     __     __     __  __\ \ ,_\/\_\/\ \__//\_\     __   _ __  
 \ \  _ <'  /'__`\ /'__`\  /\ \/\ \\ \ \/\/\ \ \ ,__\/\ \  /'__`\/\`'__\
  \ \ \L\ \/\  __//\ \L\.\_\ \ \_\ \\ \ \_\ \ \ \ \_/\ \ \/\  __/\ \ \/ 
   \ \____/\ \____\ \__/.\_\\ \____/ \ \__\\ \_\ \_\  \ \_\ \____\\ \_\ 
    \/___/  \/____/\/__/\/_/ \/___/   \/__/ \/_/\/_/   \/_/\/____/ \/_/                                                        
"""

console = Console()

def main():
    console.print(Panel(Text(HEADER, justify="left", style="bold cyan"), title="Welcome", subtitle="v0.1.0"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
        setup_task = progress.add_task("[green]Loading configuration...", total=None)
        
        config_file_manager = ConfigFileManager()
        config = config_file_manager.load_or_create_preferences()

        start_on_boot(config.get('start_on_boot', False))
        
        if config['remove_whats_new']:
            progress.update(setup_task, description="[green]Removing 'What's New' section...")
            remove_whats_new()
        
        progress.update(setup_task, completed=100, visible=False)

        steam_path = get_steam_path()
        steam_id64s = config.get('steam_id', '*')
        if steam_id64s.strip() == '*':
            steam_ids = get_steam_ids()
        else:
            steam_ids = [SteamId(steamid64=steam_id64.strip()) for steam_id64 in steam_id64s.split(',')]

        for steam_id in steam_ids: 
            user_task = progress.add_task(f"[bold blue]Processing User: {steam_id.get_steamid()}", total=None)
            _run_task_for_user(config, steam_path, steam_id, progress)
            progress.update(user_task, completed=100) # Keep visible so we know which user was processed

        if config['launch'] or config['bigpicture']:
            launch_task = progress.add_task("[yellow]Launching Steam...", total=None)
            launch_steam(config['bigpicture'])
            progress.update(launch_task, completed=100)

    console.print("[bold green]All tasks completed successfully![/bold green]")


def _run_task_for_user(config, steam_path, steam_id: SteamId, progress):
    local_grid_file_path = get_grid_path(steam_id)
    non_steam_games = parse_shortcuts_vdf(steam_path, steam_id)
    sync_manager = None

    if config.get('nextcloud_url', False):
        # cloud_task = progress.add_task(f"Setting up Nextcloud for {steam_id.get_steamid()}", total=None)
        # console.print(f"Nextcloud URL: {config['nextcloud_url']}")
        cloud_folder = f"{config.get('nextcloud_base_folder', 'SteamBeautifier')}/{steam_id.get_steamid()}"
        api_proxy = NextcloudApiProxy(config['nextcloud_url'], config['nextcloud_user'], config['nextcloud_password'])
        nextcloud_manager = NextcloudManager(api_proxy, cloud_folder)
        sync_manager = SteamGridSyncManager(nextcloud_manager, non_steam_games)
        # progress.update(cloud_task, completed=100)

    dropbox_manager = None
    if config['dropbox_sync']:
        db_setup_task = progress.add_task("Initializing Dropbox connection...", total=None)
        dropbox_manifest_file_manager = DropboxManifestFileManager(steam_id)
        dropbox_manifest = dropbox_manifest_file_manager.load_or_create_manifest()
        dropbox_manager = _get_dropbox_manager(config, steam_id, dropbox_manifest, progress.console)
        progress.update(db_setup_task, completed=100, visible=False)

    # 1. Cloud Download (Sync Down)
    if sync_manager:
        sync_id = progress.add_task("☁️  Nextcloud: Syncing from cloud...", total=None)
        try:
            sync_manager.download_steam_games_grid(local_grid_file_path, progress=progress, task_id=sync_id)
            sync_manager.download_non_steam_games_grid(local_grid_file_path, progress=progress, task_id=sync_id)
            
            # Ensure bar looks complete even if 0 files
            # Ensure bar looks complete even if 0 files
            final_total = None
            final_completed = None
            for task in progress.tasks:
                if task.id == sync_id and (task.total is None or task.total == 0):
                    final_total = 1
                    final_completed = 1
            
            p_kwargs = {"description": "[green]☁️  Nextcloud: Download complete"}
            if final_total:
                p_kwargs["total"] = final_total
                p_kwargs["completed"] = final_completed
            progress.update(sync_id, **p_kwargs)
        except Exception as e:
            progress.console.print(f"[red]Nextcloud download error: {e}[/red]")
    
    if dropbox_manager:
        down_task = progress.add_task("[cyan]☁️  Dropbox: Syncing from cloud...", total=None) 
        dropbox_manager.download_newer_files(
            local_grid_file_path,
            non_steam_games,
            progress=progress,
            task_id=down_task)
        
        # Ensure bar looks complete even if 0 files
        # Ensure bar looks complete even if 0 files
        final_total = None
        final_completed = None
        for task in progress.tasks:
            if task.id == down_task and (task.total is None or task.total == 0):
                final_total = 1
                final_completed = 1

        p_kwargs = {"description": "[green]☁️  Dropbox: Download complete", "visible": True}
        if final_total:
            p_kwargs["total"] = final_total
            p_kwargs["completed"] = final_completed
        progress.update(down_task, **p_kwargs)

    # 2. Fetch Missing Art (SteamGridDB)
    if config['download-images']:
        img_task = progress.add_task("[magenta]🎨 Fetching missing art...", total=None)
        download_missing_images(config['steam_api_key'],
                                config['steamgriddb_api_key'],
                                steam_id,
                                progress=progress,
                                task_id=img_task)
        
        # Ensure bar looks complete even if 0 files
        # Ensure bar looks complete even if 0 files
        final_total = None
        final_completed = None
        for task in progress.tasks:
            if task.id == img_task and (task.total is None or task.total == 0):
                final_total = 1
                final_completed = 1

        p_kwargs = {"description": "[green]☁️  Art: Download complete", "visible": True}
        if final_total:
            p_kwargs["total"] = final_total
            p_kwargs["completed"] = final_completed
        progress.update(img_task, **p_kwargs)

    # 3. Cloud Upload (Sync Up)
    if dropbox_manager:
        up_task = progress.add_task("[cyan]☁️  Dropbox: Syncing to cloud...", total=None)
        dropbox_manager.upload_newer_files(
            local_grid_file_path,
            non_steam_games,
            progress=progress,
            task_id=up_task)
        dropbox_manifest_file_manager.save_file(dropbox_manager.get_manifest())
        dropbox_manager.upload_manifest()
        
         # Ensure bar looks complete even if 0 files
         # Ensure bar looks complete even if 0 files
        final_total = None
        final_completed = None
        for task in progress.tasks:
            if task.id == up_task and (task.total is None or task.total == 0):
                final_total = 1
                final_completed = 1
        
        p_kwargs = {"description": "[green]☁️  Dropbox: Upload complete", "visible": True}
        if final_total:
            p_kwargs["total"] = final_total
            p_kwargs["completed"] = final_completed
        progress.update(up_task, **p_kwargs)
    
    if sync_manager:
        sync_up_task = progress.add_task("☁️  Nextcloud: Syncing to cloud...", total=None)
        try:
            sync_manager.upload_directory(local_grid_file_path, progress=progress, task_id=sync_up_task)
            
             # Ensure bar looks complete even if 0 files
            final_total = None
            final_completed = None
            for task in progress.tasks:
                if task.id == sync_up_task and (task.total is None or task.total == 0):
                    final_total = 1
                    final_completed = 1

            p_kwargs = {"description": "[green]☁️  Nextcloud: Upload complete"}
            if final_total:
                p_kwargs["total"] = final_total
                p_kwargs["completed"] = final_completed
            progress.update(sync_up_task, **p_kwargs)
        except Exception as e:
            progress.console.print(f"[red]Nextcloud upload error: {e}[/red]")
            progress.update(sync_up_task, description="[red]☁️  Nextcloud: Upload failed")


def _get_dropbox_manager(config, steam_id, dropbox_manifest, console):
    try:
        return DropboxManager(
            app_key=config['dropbox_app_key'],
            app_secret=config['dropbox_app_secret'],
            refresh_token=config['dropbox_refresh_token'],
            steam_id=steam_id,
            manifest=dropbox_manifest
        )
    except KeyError as e:
        console.print(f"[red]Error reading Dropbox values even though 'dropbox_sync' is true: {e}. Please run the configuration setup.[/red]")
        return None


if __name__ == "__main__":
    main()

