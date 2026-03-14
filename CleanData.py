import os
import hashlib
from PIL import Image, UnidentifiedImageError

def get_file_hash(filepath, chunk_size=8192):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def clean_folder(folder_path, min_width=150, min_height=150):
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    seen_hashes = set()
    duplicates_removed = 0
    small_images_removed = 0

    for root, _, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)

            # --- STEP 1: Check for Duplicates ---
            file_hash = get_file_hash(filepath)
            
            if file_hash in seen_hashes:
                os.remove(filepath)
                duplicates_removed += 1
                print(f"Deleted duplicate: {filename}")
                continue
            else:
                seen_hashes.add(file_hash)

            # --- STEP 2: Check Image Resolution ---
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                
                if width < min_width or height < min_height:
                    os.remove(filepath)
                    small_images_removed += 1
                    print(f"Deleted small image ({width}x{height}): {filename}")
                    
            except (UnidentifiedImageError, IOError):
                pass

    print("\n--- Cleanup Summary ---")
    print(f"Duplicates deleted: {duplicates_removed}")
    print(f"Small images deleted: {small_images_removed}")

# --- Execution ---
if __name__ == "__main__":
    TARGET_FOLDER = r"images" 
    clean_folder(TARGET_FOLDER)