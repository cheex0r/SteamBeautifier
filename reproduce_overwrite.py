import os
import time
import shutil

def test_overwrite_behavior():
    print("Testing Overwrite Timestamp Behavior...")
    
    # 1. Prepare Target File (Simulate existing grid image)
    target_file = "target_image.jpg"
    with open(target_file, "w") as f:
        f.write("Original Content")
    
    # Set target timestamps to OLD
    now = time.time()
    old_time = now - (3600 * 24 * 100) # 100 days ago
    os.utime(target_file, (old_time, old_time))
    
    # We can't easily set Ctime in Python without Win32 API, 
    # but we can rely on it being "Now" (created just now) or sleep a bit to differentiate?
    # Actually, let's just observe what happens to Ctime.
    
    original_ctime = os.path.getctime(target_file)
    original_mtime = os.path.getmtime(target_file)
    
    print(f"\n[Target File Initial]")
    print(f"Mtime: {original_mtime}")
    print(f"Ctime: {original_ctime}")
    
    time.sleep(2) # Wait to ensure 'Now' is different
    
    # 2. Prepare Source File (Simulate 'Old' backup image user copies in)
    source_file = "source_image.jpg"
    with open(source_file, "w") as f:
        f.write("New Content from Old Backup")
    
    # Set Source timestamps to VERY OLD (older than target)
    very_old_time = now - (3600 * 24 * 365 * 5) # 5 years ago
    os.utime(source_file, (very_old_time, very_old_time))
    
    source_mtime = os.path.getmtime(source_file)
    print(f"\n[Source File (The new image user wants)]")
    print(f"Mtime: {source_mtime} (Very Old)")
    
    # 3. Perform Overwrite (shutil.copy2 - usually what Explorer does)
    print("\nOverwrite: shutil.copy2(source, target)...")
    shutil.copy2(source_file, target_file)
    
    new_ctime = os.path.getctime(target_file)
    new_mtime = os.path.getmtime(target_file)
    
    print(f"\n[Target File After Overwrite]")
    print(f"Mtime: {new_mtime} (Matches Source? {new_mtime == source_mtime})")
    print(f"Ctime: {new_ctime} (Matches Original Target? {new_ctime == original_ctime})")
    
    if new_ctime == original_ctime:
        print("=> CTIME WAS PRESERVED! (Hypothesis Confirmed)")
        print("   Logic relying on Ctime > Remote will FAIL because Ctime is still old (if original target was old)")
    else:
        print("=> Ctime was updated.")

    # Cleanup
    try:
        os.remove(target_file)
        os.remove(source_file)
    except:
        pass

if __name__ == "__main__":
    test_overwrite_behavior()
