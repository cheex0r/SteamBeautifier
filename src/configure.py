from filemanagers.config_file_manager import ConfigFileManager

def main():
    print("Launching Steam Beautifier Configuration Wizard...")
    manager = ConfigFileManager()
    # Force the prompt regardless of existing file
    config = manager._prompt_user_for_config(use_gui=True)
    if config:
        manager.save_file(config)
        print(f"Configuration saved to {manager._get_file_path()}")
    else:
        print("Configuration cancelled.")

if __name__ == "__main__":
    main()
