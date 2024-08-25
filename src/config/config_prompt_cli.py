import json

from cloud.dropbox_token_setup import DropboxTokenSetup
from interfaces.cli_user_interaction import CLIUserInteraction


class ConfigPromptCli:
    def get_config(self, schema):
        config = {}
        for key, config in schema.items():
            if config.get('skip_cli', False):
                continue
            if 'depends_on' in config and not config.get(config['depends_on']):
                config[key] = config['default']
            else:
                config[key] = self._prompt_user(config)
        self._add_dropbox_tokens(config)
        return config


    def _prompt_user(self, config):
        print()
        if config['type'] == 'bool':
            user_input = input(f"{config['description']} (True/False): ").lower()
            return user_input in ['true', 't', 'yes', 'y', '1']
        elif config['type'] == 'str':
            if 'url' in config:
                print(f"You can get your {config['description']} here: {config['url']}")
            return input(f"{config['description']}: ")


    def _add_dropbox_tokens(self, config):
        app_key = config.get('dropbox_app_key', None)
        app_secret = config.get('dropbox_app_secret', None)
        if app_key and app_secret:
            dropbox_token_setup = DropboxTokenSetup(app_key, app_secret)
            try:
                oauth_result = dropbox_token_setup.get_authorization_token_from_user(CLIUserInteraction())
                config['dropbox_refresh_token'] = oauth_result.refresh_token
                print("Dropbox authentication successful.")
            except Exception as e:
                print(f"Error getting Dropbox tokens: {e}")
        config.pop('dropbox_access_code', None)


def main():
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    config_prompt = ConfigPromptCli()
    config = config_prompt.get_config(schema)
    print(config)


if __name__ == "__main__":
    main()
