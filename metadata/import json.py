import json
import os
import csv
import re


def sanitize_filename(filename: str) -> str:
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', "", filename)
    sanitized_filename = sanitized_filename.replace("_", " ")
    return sanitized_filename.strip()


def new_sefaria_metadata(list_of_files: list):
    meta_file_path = ""
    root_folder = ""
    list_new = []
    new_data = []
    for _, _, files in os.walk(root_folder):
        list_new.extend([os.path.splitext(file)[0] for file in files if os.path.splitext(file)[1] == ".txt" and os.path.splitext(file)[0] not in list_of_files])
    with open(meta_file_path, "r") as f:
        data = json.load(f)
    for entry in data:
        if sanitize_filename(entry["he_title"]) in list_new:
            new_entry = {"title": sanitize_filename(entry["he_title"]), "authors": entry["authors"], "heShortDesc": entry["he_short_desc"], "heDesc": entry["he_long_desc"]}
            new_data.append(new_entry)
    return new_data


new_files_data = []
file_path = "/home/zevi5/Downloads/otzaria-library/metadata.json"
root_folder = "/home/zevi5/Downloads/otzaria-library/אוצריא"
files_list = {}
folders_list = []
folders = (
    "Ben-YehudaToOtzaria/ספרים/אוצריא",
    "DictaToOtzaria/ספרים/ערוך/אוצריא",
    "OnYourWayToOtzaria/ספרים/אוצריא",
    "OraytaToOtzaria/ספרים/אוצריא",
    "sefariaToOtzaria/ספרים/אוצריא",
    "sefaria and more",
    "MoreBooks"
)
mapping = {
    "Ben-YehudaToOtzaria": "Ben-Yehuda",
    "DictaToOtzaria": "Dicta",
    "OnYourWayToOtzaria": "OnYourWay",
    "OraytaToOtzaria": "Orayta",
    "sefaria and more": "sefaria",
    "sefariaToOtzaria": "sefaria_new",
    "MoreBooks": "MoreBooks"
}
for root, dirs, files in os.walk(root_folder):
    for file in files:
        files_list[os.path.splitext(file)[0]] = os.path.join(root, file)
    folders_list.extend(list(dirs))

with open(file_path, "r") as f:
    data = json.load(f)
all_titles = [entry["title"] for entry in data]
for key, value in files_list.items():
    if key not in all_titles:
        if os.path.splitext(value)[1] != ".txt":
            continue
        new_entry = {"title": key}
        with open(value, "r", encoding="utf-8") as f:
            content = f.read().split("\n")
            if len(content) < 2:
                continue
            new_entry["author"] = content[1]
        new_files_data.append(new_entry)
new_folders_data = [folder for folder in folders_list if folder not in all_titles]
with open("new.csv", "w", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author"])
    writer.writeheader()
    writer.writerows(new_files_data)
    writer.writerows([{"title": folder} for folder in new_folders_data])
