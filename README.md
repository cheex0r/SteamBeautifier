# SteamBeautifier
A utility to enhance the visual aesthetics and organization of games within the Steam library.

# Create Windows Executable
pyinstaller --onefile --distpath .\installer\windows\dist --add-data "config_schema.json;." --hidden-import win32com --hidden-import cffi --hidden-import six --hidden-import urllib3 --name steam_beautifier --hidden-import idna .\src\main.py