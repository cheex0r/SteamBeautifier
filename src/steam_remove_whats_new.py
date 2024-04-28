import os

from steam_directory_finder import get_steam_path

paths = ['steamui', 'css', 'chunk~2dcc5aaf7.css']
search = "libraryhome_UpdatesContainer_17uEB{"
new_guts = "display: none !important;"

def get_modified_steam_css(data):
    index_start = data.find(search)
    if index_start == -1:
        print("String '{}' not found.".format(search))
        return data

    index_end = data.find("}", index_start)
    if index_end == -1:
        print("Closing brace '}}' not found after '{}'.".format(search))
        return data

    padding = ""
    guts = data[index_start + len(search):index_end]
    while len(guts) > len(new_guts) + len(padding):
        padding += " "

    return data[:index_start] + search + new_guts + padding + data[index_end:]

def remove_whats_new():
    file = os.path.join(get_steam_path(), *paths)
    print('Modifying %s', file)
    try:
        if not os.path.exists(file):
            print("File '{}' does not exist.".format(file))
            exit()

        # Remove the read-only attribute from the file
        os.chmod(file, os.stat(file).st_mode & ~0o400)  # Windows
        os.chmod(file, 0o666) # Unix

        with open(file, 'rb') as f:
            data = f.read().decode('utf-8')
        
        modified_data = get_modified_steam_css(data)

        with open(file, 'wb') as f:
            f.write(modified_data.encode('utf-8'))
            print("Successfully modified '{}'.".format(file))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    # If the script is executed directly, call the main function
    print("Removing 'What's New' shelf from Steam library.")
    remove_whats_new()
