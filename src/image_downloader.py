import argparse
import os
import requests

from PIL import Image
from io import BytesIO


def save_image_as_png(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image.save(filename, format='PNG')
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

    games = save_image_as_png(args.url, args.filename)

