import json
import tkinter as tk
import webbrowser

from cloud.dropbox_token_setup import DropboxTokenSetup


class ConfigPromptGui:
    def __init__(self, root, schema):
        self.root = root
        self.schema = schema
        self.root.title("Steam Beautifier Configuration")

        # Configure padding around the main window
        self.root.configure(padx=20, pady=20)
        
        self.config = {}
        self.entries = {}
        self.links = {}  # To store all link widgets

        row = 0
        for group_key, items in schema.items():
            group = tk.LabelFrame(root, text=group_key, padx=5, pady=5)
            group.pack(padx=10, pady=10)  # Use pack for the frame itself
            group_row = 0
            for key, config in items.items():
                self.add_item_to_group(group, key, config, group_row)
                group_row += 1
            row += 1

        # Place the Save button below the form
        self.save_button = tk.Button(root, text="Save", command=self.root.quit)
        self.save_button.pack(pady=10)  # Use pack for the Save button

        self._update_visibility()


    def add_item_to_group(self, group, key, config, row):
        print(f"Adding item to group: {key}")
        print(f"Config: {config}")
        # Create a label and the corresponding widget for each config
        tk.Label(group, text=config['description']).grid(row=row, column=0, sticky='w', padx=5, pady=5)

        if config['type'] == 'bool':
            # For boolean values, create a Checkbutton
            self.config[key] = tk.BooleanVar(value=config['default'])
            self.entries[key] = tk.Checkbutton(group, variable=self.config[key])
            self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
        elif config['type'] == 'str':
            # For string values, create an Entry field
            self.config[key] = tk.StringVar(value=config['default'])
            self.entries[key] = tk.Entry(group, textvariable=self.config[key])
            self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
            
            # Track changes to specific fields
            if key in ('dropbox_app_key', 'dropbox_app_secret'):
                self.config[key].trace_add("write", self._update_dropbox_url)
            
            # Add a link if a URL is provided
            if 'url' in config:
                self._create_link(group, key, config.get('link_text', "Get Key"), config['url'], row, 2)


    def get_config(self):
        self.root.mainloop()
        config = {}
        for key, var in self.config.items():
            config[key] = var.get()

        if config.get('dropbox_sync') and \
           config.get('dropbox_app_key') and \
           config.get('dropbox_app_secret') and \
           config.get('dropbox_access_code'):

            access_code = config['dropbox_access_code']
            config.pop('dropbox_access_code', None)
            oauth_result = self.dropbox_token_setup.get_authorization_token_with_access_code(self.auth_flow, access_code)
            config['dropbox_refresh_token'] = oauth_result.refresh_token
        return config


    def _update_dropbox_url(self, *args):
        app_key = self.config.get('dropbox_app_key').get()
        app_secret = self.config.get('dropbox_app_secret').get()
        if app_key and app_secret:
            if (
                not hasattr(self, 'dropbox_token_setup')
                or self.dropbox_token_setup.app_key != app_key
                or self.dropbox_token_setup.app_secret != app_secret
            ): 
                self.dropbox_token_setup = DropboxTokenSetup(app_key, app_secret)
            auth_flow, url = self.dropbox_token_setup.start_authorization_flow()
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
                self._create_link(self.root, 'dropbox_access_code', self.schema['dropbox_access_code']['link_text'], url, row, 2)


    def _create_link(self, root, key, text, url, row, column):
        link = tk.Label(root, text=text, fg="blue", cursor="hand2")
        link.grid(row=row, column=column, padx=5, pady=5, sticky='w')  # Use grid instead of pack
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))
        self.links[key] = link  # Store the link widget


    def _update_visibility(self):
        def are_dependencies_met(dependencies):
            # Ensure all dependencies are met
            try:
                return all(self.config[dep].get() for dep in dependencies)
            except KeyError as e:
                raise KeyError(f"KeyError: '{e.args[0]}' - Check if '{e.args[0]}' is defined in the schema.")

        for group_key, items in self.schema.items():
            for key, config in items.items():
                # Check if there are dependencies for this config item
                if 'depends_on' in config:
                    dependencies = config['depends_on']
                    
                    # Ensure dependencies is always a list
                    if isinstance(dependencies, str):
                        dependencies = [dependencies]

                    # Check if all dependencies are met
                    if are_dependencies_met(dependencies):
                        self.entries[key].config(state='normal')
                        # Special handling for 'dropbox_access_code' and other specific keys
                        if key == 'dropbox_access_code' and key in self.links:
                            self.links[key].grid()  # Show the link if dependencies are met
                    else:
                        self.entries[key].config(state='disabled')
                        if key == 'dropbox_access_code' and key in self.links:
                            self.links[key].grid_remove()  # Hide the link if dependencies are not met
                        # Reset to default if the dependencies are not met
                        self.config[key].set(config['default'])
                else:
                    # If no dependencies, ensure the entry is enabled by default
                    self.entries[key].config(state='normal')

        # Schedule the next update if needed
        self.root.after(100, self._update_visibility)


if __name__ == "__main__":
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    root = tk.Tk()
    config_app = ConfigPromptGui(root, schema)
    user_config = config_app.get_config()
    print("User Config:", user_config)
