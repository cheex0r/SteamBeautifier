import re


def extract_appid_and_postfix(filename):
    """
    Extracts the appid (leading digits) and the postfix from a filename.
    
    Expected filename forms:
      - 123.jpg            -> appid: 123, postfix: ""
      - 123p.jpg           -> appid: 123, postfix: "p"
      - 123_hero.jpg       -> appid: 123, postfix: "_hero"
      - 123_logo.jpg       -> appid: 123, postfix: "_logo"
      - 123.json           -> appid: 123, postfix: ""
    
    Args:
        filename (str): The filename, e.g., "123_hero.jpg"
    
    Returns:
        tuple: (appid: str, postfix: str, extension: str)
    """
    pattern = r'^(\d+)(p|_[^.]+)?(\..+)$'
    m = re.match(pattern, filename)
    if m:
        appid = m.group(1)
        postfix = m.group(2) if m.group(2) else ""
        extension = m.group(3)

        print(f"=================================")
        print(f"Filename: {filename}")
        print(f"Extracted appid: {appid}, postfix: {postfix}, extension: {extension}")

        return appid, postfix, extension
    else:
        raise ValueError(f"Filename {filename} doesn't match the expected pattern.")
