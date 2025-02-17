import os
import shutil
import csv

mapping = {
    "Ben-YehudaToOtzaria": "Ben-Yehuda",
    "DictaToOtzaria": "Dicta",
    "OnYourWayToOtzaria": "OnYourWay",
    "OraytaToOtzaria": "Orayta",
    "sefaria and more": "sefaria",
    "sefariaToOtzaria": "sefaria_new",
    "MoreBooks": "MoreBooks"
}


def sync_files(folder_path, target_folder_path, csv_writer):
    source_key = folder_path.split(os.sep)[0]
    original_folder = mapping.get(source_key, source_key)
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, folder_path)
            target_file_path = os.path.join(target_folder_path, rel_file_path)
            sync_folder = os.path.split(target_file_path)[0]
            os.makedirs(sync_folder, exist_ok=True)
            shutil.copy(file_path, target_file_path)
            if not file.lower().endswith(".txt"):
                continue
            with open(target_file_path, "r", encoding="utf-8") as f:
                content = f.read().split("\n")
            csv_writer.writerow([file, target_file_path, original_folder, str(len(content))])


def sync_folders(folder_path, folders_to_update):
    for root, folders, _ in os.walk(folder_path):
        for folder in folders:
            full_folder_path = os.path.join(root, folder)
            rel_folder_path = os.path.relpath(full_folder_path, folder_path)
            for folder_to_update in folders_to_update:
                full_target_folder_path = os.path.join(folder_to_update, rel_folder_path)
                os.makedirs(full_target_folder_path, exist_ok=True)


def remove_old(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


target_folder = "אוצריא"
ver_file_path = os.path.join("אוצריא", "אודות התוכנה", "גירסת ספריה.txt")
with open(ver_file_path, "r", encoding="utf-8") as f:
    library_ver = int(f.read())
remove_old(target_folder)

folders = (
    "Ben-YehudaToOtzaria/ספרים/אוצריא",
    "DictaToOtzaria/ספרים/ערוך/אוצריא",
    "OnYourWayToOtzaria/ספרים/אוצריא",
    "OraytaToOtzaria/ספרים/אוצריא",
    "sefariaToOtzaria/ספרים/אוצריא",
    "sefaria and more",
    "MoreBooks"
)

with open("SourcesBooks.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["שם הקובץ", "נתיב הקובץ", "תיקיית המקור", "מספר שורות"])
    for folder in folders:
        sync_files(folder, target_folder, csv_writer)

for folder in folders:
    sync_folders(folder, folders)

csv_file_path = os.path.join("אוצריא", "אודות התוכנה", "SourcesBooks.csv")
shutil.copy("SourcesBooks.csv", csv_file_path)
os.makedirs("library_csv", exist_ok=True)
os.rename("SourcesBooks.csv", os.path.join("library_csv", f"{library_ver + 1}.csv"))
with open(ver_file_path, "w", encoding="utf-8") as f:
    f.write(str(library_ver + 1))
