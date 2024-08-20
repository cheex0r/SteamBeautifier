import json


class ConfigPromptCli:
    def prompt_user(self, config):
        print()
        if config['type'] == 'bool':
            return input(f"{config['description']} (True/False): ").lower() == 'true'
        elif config['type'] == 'str':
            if 'url' in config:
                print(f"You can get your {config['description']} here: {config['url']}")
            return input(f"{config['description']}: ")
        
    def get_user_preferences(self, schema):
        preferences = {}
    
        for key, config in schema.items():
            if 'depends_on' in config and not preferences.get(config['depends_on']):
                preferences[key] = config['default']
            else:
                preferences[key] = self.prompt_user(config)

        return preferences


def main():
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    config_prompt = ConfigPromptCli()
    prefs = config_prompt.get_user_preferences(schema)
    print(prefs)

if __name__ == "__main__":
    main()
