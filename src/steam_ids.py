import argparse

def steamid64_to_steamid(steamid64):
    steamid = int(steamid64) - 76561197960265728
    return steamid

def steamid_to_steamid64(steamid):
    steamid64 = steamid + 76561197960265728
    return steamid64

def steamid64_to_steamid3(steamid64):
    steamid = steamid64_to_steamid(steamid64)
    steamid3 = "[U:1:" + str(steamid) + "]"
    return steamid3

def steamid3_to_steamid64(steamid3):
    steamid = int(steamid3.split(":")[2][:-1])
    steamid64 = steamid_to_steamid64(steamid)
    return steamid64

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get images from steamgriddb.')
    parser.add_argument('--steamid', type=int)
    parser.add_argument('--steamid3', type=int)
    parser.add_argument('--steamid64', type=int)
    args = parser.parse_args()

    if args.steamid:
        print("Converting Steamid: %s", args.steamid)
        print("Steamid64: %s", steamid_to_steamid64(args.steamid))

    if args.steamid64:
        print("Converting Steamid64: %s", args.steamid64)
        print("Steamid: %s", steamid64_to_steamid(args.steamid64))

