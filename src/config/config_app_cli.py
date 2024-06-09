import json
import os

def prompt_user(config):
    print()
    if config['type'] == 'bool':
        return input(f"{config['description']} (True/False): ").lower() == 'true'
    elif config['type'] == 'str':
        if 'url' in config:
            print(f"You can get your {config['description']} here: {config['url']}")
        return input(f"{config['description']}: ")

def main():
    with open('config_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    preferences = {}
    
    for key, config in schema.items():
        if 'depends_on' in config and not preferences.get(config['depends_on']):
            preferences[key] = config['default']
        else:
            preferences[key] = prompt_user(config)

    config_dir = os.getenv('APPDATA', os.path.expanduser('~'))
    config_path = os.path.join(config_dir, 'steam_beautifier_config', 'config.json')

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as config_file:
        json.dump(preferences, config_file, indent=4)

    print(f"\nPreferences saved to {config_path}")

if __name__ == "__main__":
    main()
