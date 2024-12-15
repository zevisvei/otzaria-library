import os
import shutil
import sys

def sync_files(folder_path, target_folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, folder_path)
            target_file_path = os.path.join(target_folder_path, rel_file_path)
            target_folder_path = os.path.split(target_file_path)[0]
            os.makedirs(target_folder_path, exist_ok=True)
            shutil.copy(file_path, target_file_path)

def sync_folders(folder_path, folders_to_update):
    for root, folders, _ in os.walk(folder_path):
        for folder in folders:
            full_folder_path = os.path.join(folder, root)
            rel_folder_path = os.path.relpath(full_folder_path, folder_path)
            for folder_to_update in folders_to_update:
                full_target_folder_path = os.path.join(folder_to_update, rel_folder_path)
                os.makedirs(full_target_folder_path, exist_ok=True)

def remove_old(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

target_folder = "אוצריא"
remove_old(target_folder)

folders = ("Ben-YehudaToOtzaria/ספרים/אוצריא",
            "DictaToOtzaria/ספרים/ערוך/אוצריא",
            "OnYourWayToOtzaria/ספרים/אוצריא",
            "OraytaToOtzaria/ספרים/אוצריא",
            "sefaria and more")
for folder in folders:
    sync_files(folder, target_folder)

folders_updated = sys.argv[1:]

for folder in folders_updated:
    folders_to_update = (folder for folder in folders if folder not in folders_updated)
    sync_folders(folder, folders_to_update)
