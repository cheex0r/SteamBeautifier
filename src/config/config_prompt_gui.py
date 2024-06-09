import tkinter as tk
from tkinter import messagebox
import json
import os
import pprint
import webbrowser

class ConfigPromptGui:
    def __init__(self, root, schema):
        self.root = root
        self.schema = schema
        self.root.title("Steam Beautifier Configuration")

        # Configure padding around the main window
        self.root.configure(padx=20, pady=20)
        
        self.preferences = {}
        self.entries = {}

        row = 0
        for key, config in schema.items():
            if config['type'] == 'bool':
                self.preferences[key] = tk.BooleanVar(value=config['default'])
                tk.Label(root, text=config['description']).grid(row=row, column=0, sticky='w', padx=5, pady=5)
                self.entries[key] = tk.Checkbutton(root, variable=self.preferences[key])
                self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
            elif config['type'] == 'str':
                self.preferences[key] = tk.StringVar(value=config['default'])
                tk.Label(root, text=config['description']).grid(row=row, column=0, sticky='w', padx=5, pady=5)
                self.entries[key] = tk.Entry(root, textvariable=self.preferences[key])
                self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
                if 'url' in config:
                    self.create_link(root, config.get('link_text', "Get Key"), config['url'], row, 2)

            row += 1

        self.save_button = tk.Button(root, text="Save", command=self.root.quit)
        self.save_button.grid(row=row, column=0, columnspan=3, pady=10)

        self.update_visibility()

    def create_link(self, root, text, url, row, column):
        link = tk.Label(root, text=text, fg="blue", cursor="hand2")
        link.grid(row=row, column=column, padx=5, pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))

    def update_visibility(self):
        for key, config in self.schema.items():
            if 'depends_on' in config:
                parent_key = config['depends_on']
                if self.preferences[parent_key].get():
                    self.entries[key].config(state='normal')
                else:
                    self.entries[key].config(state='disabled')
                    if 'default' in config:
                        self.preferences[key].set(config['default'])
            else:
                self.entries[key].config(state='normal')  # Ensure all entries are normal by default
        self.root.after(100, self.update_visibility)

    def get_user_preferences(self):
        self.root.mainloop()
        preferences = {}
        for key, var in self.preferences.items():
            preferences[key] = var.get()
        return preferences


if __name__ == "__main__":
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    root = tk.Tk()
    config_app = ConfigPromptGui(root, schema)
    user_preferences = config_app.get_user_preferences()
    print("User Preferences:", user_preferences)
