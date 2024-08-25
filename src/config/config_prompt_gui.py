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
        for key, config in schema.items():
            if config['type'] == 'bool':
                self.config[key] = tk.BooleanVar(value=config['default'])
                tk.Label(root, text=config['description']).grid(row=row, column=0, sticky='w', padx=5, pady=5)
                self.entries[key] = tk.Checkbutton(root, variable=self.config[key])
                self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
            elif config['type'] == 'str':
                self.config[key] = tk.StringVar(value=config['default'])
                tk.Label(root, text=config['description']).grid(row=row, column=0, sticky='w', padx=5, pady=5)
                self.entries[key] = tk.Entry(root, textvariable=self.config[key])
                self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
                
                # Track changes to specific fields
                if key == 'dropbox_app_key' or key == 'dropbox_app_secret':
                    self.config[key].trace_add("write", self._update_dropbox_url)
                
                # Add link if URL is provided
                if 'url' in config:
                    self._create_link(root, key, config.get('link_text', "Get Key"), config['url'], row, 2)
            row += 1

        self.save_button = tk.Button(root, text="Save", command=self.root.quit)
        self.save_button.grid(row=row, column=0, columnspan=3, pady=10)

        self._update_visibility()


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
        link.grid(row=row, column=column, padx=5, pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))
        self.links[key] = link  # Store the link widget


    def _update_visibility(self):
        for key, config in self.schema.items():
            if 'depends_on' in config:
                dependencies = config['depends_on']
                
                # Ensure dependencies are always a list
                if isinstance(dependencies, str):
                    dependencies = [dependencies]
                
                try:
                    dependencies_met = all(self.config[dep].get() for dep in dependencies)
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
                    self.config[key].set(config['default'])
            else:
                self.entries[key].config(state='normal')  # Ensure all entries are normal by default

        self.root.after(100, self._update_visibility)


if __name__ == "__main__":
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    root = tk.Tk()
    config_app = ConfigPromptGui(root, schema)
    user_config = config_app.get_config()
    print("User Config:", user_config)
