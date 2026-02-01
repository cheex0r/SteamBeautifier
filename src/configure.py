from filemanagers.config_file_manager import ConfigFileManager

def main():
    config_file_manager = ConfigFileManager()
    # Always launch GUI for this entry point
    config_file_manager.edit_preferences(use_gui=True)

if __name__ == "__main__":
    main()
