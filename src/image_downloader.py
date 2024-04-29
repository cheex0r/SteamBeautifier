import argparse
import requests

def save_image(url, filename):
    try:
        # Send a GET request to the image URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file in binary write mode
            with open(filename, 'wb') as file:
                # Write the image data to the file
                file.write(response.content)
            print(f"Image saved successfully as {filename}")
        else:
            print(f"Failed to download image from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while saving image: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for Steam games without 600x900 grid images.')
    parser.add_argument('--url', type=str, help='URL of image being downloads')
    parser.add_argument('--filename', type=str, help='File name of where to save image')

    args = parser.parse_args()

    games = save_image(args.url, args.filename)

