import json
import tkinter as tk
import webbrowser

from cloud.dropbox_manager import DropboxManager


class ConfigPromptGui:
    def __init__(self, root, schema):
        self.root = root
        self.schema = schema
        self.root.title("Steam Beautifier Configuration")
        self.dropbox_manager = DropboxManager()

        # Configure padding around the main window
        self.root.configure(padx=20, pady=20)
        
        self.preferences = {}
        self.entries = {}
        self.links = {}  # To store all link widgets

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
                
                # Track changes to specific fields
                if key == 'dropbox_app_key' or key == 'dropbox_app_secret':
                    self.preferences[key].trace_add("write", self.update_dropbox_url)
                
                # Add link if URL is provided
                if 'url' in config:
                    self.create_link(root, key, config.get('link_text', "Get Key"), config['url'], row, 2)
            row += 1

        self.save_button = tk.Button(root, text="Save", command=self.root.quit)
        self.save_button.grid(row=row, column=0, columnspan=3, pady=10)

        self.update_visibility()


    def update_dropbox_url(self, *args):
        app_key = self.preferences.get('dropbox_app_key').get()
        app_secret = self.preferences.get('dropbox_app_secret').get()
        if app_key and app_secret:
            auth_flow, url = self.dropbox_manager.start_authorization_flow(app_key, app_secret)
            self.auth_flow = auth_flow
            self.schema['dropbox_access_code']['url'] = url

            # Update the URL link
            if 'dropbox_access_code' in self.links:
                link_widget = self.links['dropbox_access_code']
                link_widget.config(text=self.schema['dropbox_access_code']['link_text'], fg="blue", cursor="hand2")
                link_widget.bind("<Button-1>", lambda e: webbrowser.open_new(url))
            else:
                # If the link isn't already created, create it now
                row = self.entries['dropbox_access_code'].grid_info()["row"]
                self.create_link(self.root, 'dropbox_access_code', self.schema['dropbox_access_code']['link_text'], url, row, 2)


    def check_dependencies(self, config, preferences):
        dependencies = config.get('depends_on', [])
        if isinstance(dependencies, str):
            dependencies = [dependencies]
        return all(preferences.get(dep) for dep in dependencies)


    def create_link(self, root, key, text, url, row, column):
        link = tk.Label(root, text=text, fg="blue", cursor="hand2")
        link.grid(row=row, column=column, padx=5, pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))
        self.links[key] = link  # Store the link widget


    def update_visibility(self):
        for key, config in self.schema.items():
            if 'depends_on' in config:
                dependencies = config['depends_on']
                
                # Ensure dependencies are always a list
                if isinstance(dependencies, str):
                    dependencies = [dependencies]
                
                try:
                    dependencies_met = all(self.preferences[dep].get() for dep in dependencies)
                except KeyError as e:
                    # print(f"KeyError: '{e.args[0]}' - Check if '{e.args[0]}' is defined in the schema.")
                    raise

                if dependencies_met:
                    self.entries[key].config(state='normal')
                    if key == 'dropbox_access_code' and 'dropbox_access_code' in self.links:
                        self.links['dropbox_access_code'].grid()  # Show the link if dependencies are met
                else:
                    self.entries[key].config(state='disabled')
                    if key == 'dropbox_access_code' and 'dropbox_access_code' in self.links:
                        self.links['dropbox_access_code'].grid_remove()  # Hide the link if dependencies are not met
                    self.preferences[key].set(config['default'])
            else:
                self.entries[key].config(state='normal')  # Ensure all entries are normal by default

        self.root.after(100, self.update_visibility)


    def get_user_preferences(self):
        self.root.mainloop()
        preferences = {}
        for key, var in self.preferences.items():
            preferences[key] = var.get()

        if preferences.get('dropbox_sync') and \
           preferences.get('dropbox_app_key') and \
           preferences.get('dropbox_app_secret') and \
           preferences.get('dropbox_access_code'):

            access_code = preferences['dropbox_access_code']
            oauth_result = self.dropbox_manager.get_authorization_token_with_access_code(self.auth_flow, access_code)
            preferences['dropbox_access_token'] = oauth_result.access_token
            preferences['dropbox_refresh_token'] = oauth_result.refresh_token
            preferences['dropbox_token_expiry'] = self.dropbox_manager.get_token_expiry_now()
        return preferences


if __name__ == "__main__":
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    root = tk.Tk()
    config_app = ConfigPromptGui(root, schema)
    user_preferences = config_app.get_user_preferences()
    print("User Preferences:", user_preferences)
