import os
import time
import shutil

def test_timestamps():
    print("Testing timestamp behavior...")
    
    # 1. Create a "Remote" time reference (e.g., 1 hour ago)
    now = time.time()
    remote_time = now - 3600 # 1 hour ago
    
    print(f"Current Time: {now}")
    print(f"Remote Time: {remote_time}")
    
    # 2. Simulate a "Downloaded" file (Synced)
    # It should have mtime = remote_time (set by utime)
    # and ctime = now (set by creation)
    
    synced_file = "synced_file.txt"
    with open(synced_file, "w") as f:
        f.write("synced content")
    
    # Set mtime to remote_time
    os.utime(synced_file, (remote_time, remote_time))
    
    synced_mtime = os.path.getmtime(synced_file)
    synced_ctime = os.path.getctime(synced_file)
    
    print(f"\n[Synced File] {synced_file}")
    print(f"Mtime: {synced_mtime} (Diff from remote: {synced_mtime - remote_time})")
    print(f"Ctime: {synced_ctime} (Diff from now: {synced_ctime - now})")
    
    if abs(synced_mtime - remote_time) < 2:
        print("=> Synced file matches remote time (Correct)")
    else:
        print("=> Synced file does DOES NOT match remote time (Problem!)")

    # 3. Simulate "User copies OLD file" (The Bug Scenario)
    # User creates a file that has OLD mtime (e.g. 5 years ago)
    # But Ctime should be Recent (Now)
    
    old_source_file = "old_source.txt"
    with open(old_source_file, "w") as f:
        f.write("old content")
    very_old_time = now - (3600 * 24 * 365) # 1 year ago
    os.utime(old_source_file, (very_old_time, very_old_time))
    
    # Simulate copy
    local_user_file = "local_user_file_from_copy.txt"
    shutil.copy2(old_source_file, local_user_file) # copy2 attempts to preserve metadata
    
    user_mtime = os.path.getmtime(local_user_file)
    user_ctime = os.path.getctime(local_user_file)
    
    print(f"\n[User Copied Old File] {local_user_file}")
    print(f"Mtime: {user_mtime} (Age: {(now - user_mtime)/3600} hours)")
    print(f"Ctime: {user_ctime} (Age: {(now - user_ctime)/3600} hours)")
    print(f"Remote Time was: {remote_time}")

    # Current Logic Evaluation
    print("\nEvaluating Logic:")
    
    # Current Download Logic:
    # if local_mtime >= remote_mtime: Skip
    # else: Download (Overwrite)
    
    if user_mtime >= remote_time:
        print("Current Logic: SKIP Download (Preserve User File) - unexpected for old file")
    else:
        print("Current Logic: DOWNLOAD (Overwrite User File) - BUG REPRODUCED")

    # Proposed Logic Evaluation
    # if abs(local_mtime - remote_time) < 2: Synced
    # elif local_mtime > remote_time: Newer
    # elif local_ctime > remote_time: User Created Recently (Newer)
    
    print("\nProposed Logic:")
    is_synced = abs(user_mtime - remote_time) < 2
    is_newer_mtime = user_mtime > remote_time
    is_newer_ctime = user_ctime > remote_time
    
    print(f"Is Synced? {is_synced}")
    print(f"Is Newer Mtime? {is_newer_mtime}")
    print(f"Is Newer Ctime? {is_newer_ctime}")
    
    if is_synced:
        print("Result: Treated as Synced")
    elif is_newer_mtime:
        print("Result: Treated as Newer (Mtime)")
    elif is_newer_ctime:
        print("Result: Treated as Newer (Ctime) - FIX WORKS")
    else:
        print("Result: Treated as Older (Overwrite) - Fix Failed")
        
    # Cleanup
    try:
        os.remove(synced_file)
        os.remove(old_source_file)
        os.remove(local_user_file)
    except:
        pass

if __name__ == "__main__":
    test_timestamps()
