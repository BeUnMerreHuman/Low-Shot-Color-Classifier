import pandas as pd
import os
import shutil
from pathlib import Path

csv_file = 'selected_images.csv' 
source_root = 'images'          
destination_folder = 'SelectedImages' 

def organize_dataset():
    try:
        df = pd.read_csv(csv_file)
        target_ids = set(df['ID'].astype(str)) 
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
        return
    except KeyError:
        print("Error: The CSV does not contain an 'ID' column. Please check your CSV headers.")
        return

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"Created target folder: {destination_folder}\n")

    moved_count = 0

    for root, dirs, files in os.walk(source_root):
        if os.path.abspath(root) == os.path.abspath(destination_folder):
            continue

        for file in files:
            file_stem = Path(file).stem
            
            if file_stem in target_ids:
                current_img_location = os.path.join(root, file)
                new_img_location = os.path.join(destination_folder, file)

                if not os.path.exists(new_img_location):
                    shutil.move(current_img_location, new_img_location)
                    print(f"Moved: {file} -> {destination_folder}/")
                    moved_count += 1
                else:
                    print(f"Warning: {file} already exists in {destination_folder}/")

    print(f"\nOrganization complete! Successfully moved {moved_count} images.")

if __name__ == "__main__":
    organize_dataset()