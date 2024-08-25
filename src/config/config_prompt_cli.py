import json

from cloud.dropbox_token_setup import DropboxTokenSetup
from interfaces.cli_user_interaction import CLIUserInteraction


class ConfigPromptCli:
    def prompt_user(self, config):
        print()
        if config['type'] == 'bool':
            user_input = input(f"{config['description']} (True/False): ").lower()
            return user_input in ['true', 't', 'yes', 'y', '1']
        elif config['type'] == 'str':
            if 'url' in config:
                print(f"You can get your {config['description']} here: {config['url']}")
            return input(f"{config['description']}: ")


    def get_user_preferences(self, schema):
        preferences = {}
        for key, config in schema.items():
            if config.get('skip_cli', False):
                continue
            if 'depends_on' in config and not preferences.get(config['depends_on']):
                preferences[key] = config['default']
            else:
                preferences[key] = self.prompt_user(config)
        self.add_dropbox_tokens(preferences)
        return preferences


    def add_dropbox_tokens(self, preferences):
        app_key = preferences.get('dropbox_app_key', None)
        app_secret = preferences.get('dropbox_app_secret', None)
        if app_key and app_secret:
            dropbox_token_setup = DropboxTokenSetup(app_key, app_secret)
            try:
                oauth_result = dropbox_token_setup.get_authorization_token_from_user(CLIUserInteraction())
                preferences['dropbox_refresh_token'] = oauth_result.refresh_token
                print("Dropbox authentication successful.")
            except Exception as e:
                print(f"Error getting Dropbox tokens: {e}")
        del preferences['dropbox_access_code']


def main():
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    config_prompt = ConfigPromptCli()
    prefs = config_prompt.get_user_preferences(schema)
    print(prefs)


if __name__ == "__main__":
    main()
