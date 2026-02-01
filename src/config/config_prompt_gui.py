import json
import tkinter as tk
import webbrowser

from cloud.dropbox_token_setup import DropboxTokenSetup


class ConfigPromptGui:
    def __init__(self, root, schema, current_config=None):
        self.root = root
        self.schema = schema
        self.current_config = current_config or {}
        self.root.title("Steam Beautifier Configuration")

        # Configure padding around the main window
        self.root.configure(padx=20, pady=20)
        
        self.config = {}
        self.entries = {}
        self.links = {}  # To store all link widgets
        self.visible_states = {} # Track password visibility states

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
        # Create a label and the corresponding widget for each config
        tk.Label(group, text=config['description']).grid(row=row, column=0, sticky='w', padx=5, pady=5)
        
        # Determine initial value (from current_config or default)
        initial_value = self.current_config.get(key, config['default'])

        if config['type'] == 'bool':
            # For boolean values, create a Checkbutton
            self.config[key] = tk.BooleanVar(value=initial_value)
            self.entries[key] = tk.Checkbutton(group, variable=self.config[key])
            self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)
        elif config['type'] == 'str':
            # For string values, create an Entry field
            self.config[key] = tk.StringVar(value=initial_value)
            
            is_secret = config.get('secret', False)
            entry_opts = {}
            if is_secret:
                entry_opts['show'] = '*'
                
            self.entries[key] = tk.Entry(group, textvariable=self.config[key], **entry_opts)
            self.entries[key].grid(row=row, column=1, sticky='w', padx=5, pady=5)

            if is_secret:
                # Add show/hide toggle for secrets
                # Using a distinct internal name or logic
                self.visible_states[key] = False
                
                # Using a small button or checkbutton for toggle
                # Using Checkbutton for "Show"
                show_var = tk.BooleanVar(value=False)
                # Keep reference to avoid garbage collection if needed
                # We can use a lambda to toggle
                toggle_btn = tk.Checkbutton(group, text="Show", variable=show_var, 
                                            command=lambda k=key, v=show_var: self._toggle_password(k, v))
                toggle_btn.grid(row=row, column=2, sticky='w', padx=5)

            # Track changes to specific fields
            if key in ('dropbox_app_key', 'dropbox_app_secret'):
                self.config[key].trace_add("write", self._update_dropbox_url)
            
            # Add a link if a URL is provided
            if 'url' in config:
                # If secret, shift link column
                col = 3 if is_secret else 2
                self._create_link(group, key, config.get('link_text', "Get Key"), config['url'], row, col)


    def _toggle_password(self, key, var):
        entry = self.entries[key]
        if var.get():
            entry.config(show="")
        else:
            entry.config(show="*")


    def get_config(self):
        self.root.mainloop()
        config = {}
        for key, var in self.config.items():
            config[key] = var.get()

        if config.get('dropbox_sync') and \
           config.get('dropbox_app_key') and \
           config.get('dropbox_app_secret') and \
           config.get('dropbox_access_code'):

            # If the user changed credentials, or if we need to refresh token
            # Note: If reusing existing config, we might already have a refresh token.
            # But here we only re-run OAuth if user provides a NEW access code mostly.
            # However, logic below always runs if access code is present.
            # Ideally we only run if access code changed or refresh token missing.
            
            access_code = config['dropbox_access_code']
            if access_code and access_code != self.current_config.get('dropbox_access_code'):
                 # Only exchange if it looks like a new code or we are forced
                 # Actually, the logic usually consumes the access code to get refresh token
                 # and then discards access code from final config.
                 pass

            # Existing logic:
            config.pop('dropbox_access_code', None)
            
            # If we already have a refresh token and credentials didn't change, we might keep it
            # But the current logic seems to rely on access code to get refresh token.
            # If user edits config, they might want to keep existing refresh token.
            
            if 'dropbox_refresh_token' in self.current_config and \
               config['dropbox_app_key'] == self.current_config.get('dropbox_app_key') and \
               config['dropbox_app_secret'] == self.current_config.get('dropbox_app_secret') and \
               not access_code:
                # Keep existing token if not trying to get new one
                config['dropbox_refresh_token'] = self.current_config['dropbox_refresh_token']
            elif access_code:
                # Try to exchange
                try:
                    # ensure setup is ready
                    self._update_dropbox_url() 
                    oauth_result = self.dropbox_token_setup.get_authorization_token_with_access_code(self.auth_flow, access_code)
                    config['dropbox_refresh_token'] = oauth_result.refresh_token
                except Exception as e:
                    print(f"Failed to get DropBox token: {e}")
            
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
                if 'dropbox_access_code' in self.entries:
                    row = self.entries['dropbox_access_code'].grid_info()["row"]
                    # Check if secret (it is in updated schema) -> col 3, else 2
                    col = 3 if self.schema['dropbox_access_code'].get('secret') else 2
                    self._create_link(self.root, 'dropbox_access_code', self.schema['dropbox_access_code']['link_text'], url, row, col)


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
                # print(f"KeyError: '{e.args[0]}' - Check if '{e.args[0]}' is defined in the schema.")
                return False

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
                        # Reset to default if the dependencies are not met BUT only if strictly necessary?
                        # Actually if we disable it, usually we might want to keep the value or reset?
                        # Resetting might be annoying if user just toggled parent briefly.
                        # Original code reset it:
                        # self.config[key].set(config['default']) 
                        # I'll keep it for now primarily for boolean sub-options, but for text it might be annoying.
                        pass
                else:
                    # If no dependencies, ensure the entry is enabled by default
                    self.entries[key].config(state='normal')

        # Schedule the next update if needed
        self.root.after(100, self._update_visibility)


if __name__ == "__main__":
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    root = tk.Tk()
    # Test with empty config
    config_app = ConfigPromptGui(root, schema)
    user_config = config_app.get_config()
    print("User Config:", user_config)
