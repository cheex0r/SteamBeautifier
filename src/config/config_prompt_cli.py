import json

from cloud.dropbox_token_setup import DropboxTokenSetup
from interfaces.cli_user_interaction import CLIUserInteraction


class ConfigPromptCli:
    def get_config(self, schema):
        config = {}
        for group_key, group in schema.items():
            print(f"\n==== {group_key} Parameters ====")
            for key, item_config in group.items():
                if item_config.get('skip_cli', False):
                    continue
                # Check dependencies
                if 'depends_on' in item_config:
                    dependency = item_config['depends_on']
                    if not config.get(dependency, False):
                        config[key] = item_config['default']
                        continue
                # Prompt user
                config[key] = self._prompt_user(item_config, key)
                # Re-evaluate dependencies after each prompt
                for re_key, re_item_config in group.items():
                    if 'depends_on' in re_item_config:
                        dependency = re_item_config['depends_on']
                        if config.get(dependency, False) and re_key not in config:
                            config[re_key] = self._prompt_user(re_item_config, re_key)
        self._add_dropbox_tokens(config)
        return config

    def _prompt_user(self, item_config, parameter):
        print()
        if item_config['type'] == 'bool':
            user_input = input(f"{item_config['description']} (True/False): ").lower()
            return user_input in ['true', 't', 'yes', 'y', '1']
        elif item_config['type'] == 'str':
            if 'url' in item_config:
                print(f"You can get your {parameter} here: {item_config['url']}")
            return input(f"{item_config['description']}: ")

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