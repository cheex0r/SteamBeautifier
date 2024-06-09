import tkinter as tk
from tkinter import messagebox
import json
import os
import webbrowser


class ConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam Beautifier Configuration")
        self.root.configure(padx=20, pady=20)
        
        self.preferences = {
            'remove_whats_new': tk.BooleanVar(),
            'launch': tk.BooleanVar(),
            'bigpicture': tk.BooleanVar(),
            'download-images': tk.BooleanVar(),
            'steam_api_key': tk.StringVar(),
            'steamgriddb_api_key': tk.StringVar(),
            'steam_id': tk.StringVar()
        }
        
        tk.Label(root, text="Remove What's New shelf?").grid(row=0, column=0, sticky='w')
        tk.Checkbutton(root, variable=self.preferences['remove_whats_new']).grid(row=0, column=1, sticky='w')
        
        tk.Label(root, text="Launch Steam?").grid(row=1, column=0, sticky='w')
        tk.Checkbutton(root, variable=self.preferences['launch'], command=self.toggle_launch_options).grid(row=1, column=1, sticky='w')
        
        tk.Label(root, text="Start Steam in Big Picture mode?").grid(row=2, column=0, sticky='w')
        self.bigpicture_check = tk.Checkbutton(root, variable=self.preferences['bigpicture'])
        self.bigpicture_check.grid(row=2, column=1, sticky='w')
        
        tk.Label(root, text="Download missing grid art?").grid(row=3, column=0, sticky='w')
        tk.Checkbutton(root, variable=self.preferences['download-images'], command=self.toggle_download_options).grid(row=3, column=1, sticky='w')
        
        tk.Label(root, text="Steam API Key:").grid(row=4, column=0, sticky='w')
        self.steam_api_key_entry = tk.Entry(root, textvariable=self.preferences['steam_api_key'])
        self.steam_api_key_entry.grid(row=4, column=1, sticky='w')
        self.create_link(root, "Get Steam API Key", "https://steamcommunity.com/dev/apikey", 4, 2)
        
        tk.Label(root, text="SteamGridDB API Key:").grid(row=5, column=0, sticky='w')
        self.steamgriddb_api_key_entry = tk.Entry(root, textvariable=self.preferences['steamgriddb_api_key'])
        self.steamgriddb_api_key_entry.grid(row=5, column=1, sticky='w')
        self.create_link(root, "Get SteamGridDB API Key", "https://www.steamgriddb.com/profile/preferences/api", 5, 2)
        
        tk.Label(root, text="SteamID64:").grid(row=6, column=0, sticky='w')
        self.steam_id_entry = tk.Entry(root, textvariable=self.preferences['steam_id'])
        self.steam_id_entry.grid(row=6, column=1, sticky='w')
        self.create_link(root, "Find Your SteamID64", "https://steamid.io", 6, 2)
        
        self.save_button = tk.Button(root, text="Save", command=self.save_preferences)
        self.save_button.grid(row=7, column=0, columnspan=2)
        
        self.toggle_launch_options()
        self.toggle_download_options()

    def create_link(self, root, text, url, row, column):
        link = tk.Label(root, text=text, fg="blue", cursor="hand2")
        link.grid(row=row, column=column, padx=5, pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))

    def toggle_launch_options(self):
        if self.preferences['launch'].get():
            self.bigpicture_check.config(state='normal')
        else:
            self.bigpicture_check.config(state='disabled')
            self.preferences['bigpicture'].set(False)

    def toggle_download_options(self):
        if self.preferences['download-images'].get():
            self.steam_api_key_entry.config(state='normal')
            self.steamgriddb_api_key_entry.config(state='normal')
            self.steam_id_entry.config(state='normal')
        else:
            self.steam_api_key_entry.config(state='disabled')
            self.steamgriddb_api_key_entry.config(state='disabled')
            self.steam_id_entry.config(state='disabled')
            self.preferences['steam_api_key'].set('')
            self.preferences['steamgriddb_api_key'].set('')
            self.preferences['steam_id'].set('')

    def save_preferences(self):
        config_dir = os.getenv('APPDATA', os.path.expanduser('~'))
        config_path = os.path.join(config_dir, 'steam_beautifier_config', 'config.json')

        preferences = {
            'remove_whats_new': self.preferences['remove_whats_new'].get(),
            'launch': self.preferences['launch'].get(),
            'bigpicture': self.preferences['bigpicture'].get(),
            'download-images': self.preferences['download-images'].get(),
            'steam_api_key': self.preferences['steam_api_key'].get(),
            'steamgriddb_api_key': self.preferences['steamgriddb_api_key'].get(),
            'steam_id': self.preferences['steam_id'].get()
        }
        
        with open(config_path, 'w') as config_file:
            json.dump(preferences, config_file, indent=4)

        messagebox.showinfo("Configuration Saved", f"Preferences saved to {config_path}")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()
