import json
import re
import os
import csv
import pandas as pd


def get_source(csv_file_path: str) -> dict[str, str]:
    all_sources = {}
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for line in reader:
            source = line[2]
            if source == "sefaria_new":
                source = "sefaria"
            all_sources[line[1]] = source
    return all_sources


def files_list(base_folder: str) -> tuple[dict[str, str], list[str]]:
    files_list = {}
    folders_list = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            files_list[os.path.splitext(file)[0]] = os.path.join(root, file)
        folders_list.extend(list(dirs))
    print(len(files_list) + len(folders_list))
    temp_files = []
    temp_files_2 = []
    for file in files_list:
        if file in folders_list:
            temp_files.append(file)
    for folder in folders_list:
        if folder not in temp_files_2:
            temp_files_2.append(folder)
    print(f"{len(folders_list) - len(temp_files_2)=}")

    print(len(temp_files))
    print(temp_files)
    return files_list, folders_list


def sanitize_filename(filename: str | None) -> str | None:
    if not filename:
        return
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', "", filename)
    sanitized_filename = sanitized_filename.replace("_", " ")
    return sanitized_filename.strip()


def json_read(file_path: str) -> list[dict[str, str | None]]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def sefaria_new(file_path: str) -> list[dict[str, str | None]]:
    new_data = []
    for entry in json_read(file_path):
        new_entry = {
            "title": sanitize_filename(entry.get("he_title")),
            "author": entry.get("he_authors"),
            "pubDate": None,
            "pubPlace": None,
            "compPlace": None,
            "compDate": None,
            "תיאור_חדש": None,
            "heShortDesc": entry.get("heShortDesc"),
            "heDesc": entry.get("heDesc"),
            "order": None,
            "Source": "sefaria",
            "type": "file"
        }
        new_data.append(new_entry)

    return new_data


def dicta_metadata(file_path: str) -> list[dict[str, str | None]]:
    new_data = []
    for entry in json_read(file_path):
        new_entry = {
            "title": sanitize_filename(entry.get("displayName")),
            "author": entry.get("author"),
            "pubDate": entry.get("printYear"),
            "pubPlace": entry.get("printLocation"),
            "compPlace": None,
            "compDate": None,
            "תיאור_חדש": None,
            "heShortDesc": entry.get("heShortDesc"),
            "heDesc": entry.get("heDesc"),
            "order": None,
            "Source": "Dicta",
            "type": "file"
        }
        new_data.append(new_entry)
    return new_data


def old_metadata(file_path: str) -> list[dict[str, str | None]]:
    new_data = []
    for entry in json_read(file_path):
        # del entry['Unnamed: 9']
        entry["Source"] = "sefaria"
        entry["type"] = None
        new_data.append(entry)
    return new_data


def main():
    num = 0
    all_sources = get_source("אוצריא/אודות התוכנה/SourcesBooks.csv")
    new_metadata = []
    dif_metadata = []
    base_folder = "אוצריא"
    new_sefaria_metadata_path = "sefariaToOtzaria/סקריפטים/metadata.json"
    dicta_metadata_path = "DictaToOtzaria/סקריפטים/old books.json"
    old_metadata_path = "metadata/new_metadata.json"
    files, folders = files_list(base_folder)
    new_sefaria = sefaria_new(new_sefaria_metadata_path)
    dicta = dicta_metadata(dicta_metadata_path)
    old_sefaria = old_metadata(old_metadata_path)
    for entry in old_sefaria:
        entry_title = entry["title"]
        if entry_title in files or entry_title in folders:
            if entry_title in files:
                entry["type"] = "file"
            else:
                entry["type"] = "folder"

            if files.get(entry_title) and files[entry_title].endswith(".txt") and all_sources[files[entry_title]] != "sefaria":
                entry["Source"] = all_sources[files[entry_title]]
            new_metadata.append(entry)
        else:
            dif_metadata.append(entry)

    all_titles = [entry["title"] for entry in new_metadata]
    for entry in new_sefaria:
        entry_title = entry["title"]
        if entry_title not in all_titles and (entry_title in files or entry_title in folders):
            new_metadata.append(entry)
            all_titles.append(entry_title)
        else:
            dif_metadata.append(entry)
    for entry in dicta:
        entry_title = entry["title"]
        if entry_title not in all_titles and (entry_title in files or entry_title in folders):
            new_metadata.append(entry)
            all_titles.append(entry_title)
        else:
            dif_metadata.append(entry)
    dif_metadata = {i["title"]: i for i in dif_metadata}

    for key, value in files.items():
        if key in all_titles:
            continue
        if os.path.splitext(value)[1] != ".txt":
            continue
        num += 1
        with open(value, "r", encoding="utf-8") as file:
            content = file.read().split("\n")
        if len(content) < 2:
            continue
        author = content[1]
        title = content[0].replace("<h1>", "").replace("</h1>", "").strip()
        if title != key and dif_metadata.get(title):
            new_entry = dif_metadata[title]
            del dif_metadata[title]
            new_entry["title"] = key
            new_metadata.append(new_entry)
            all_titles.append(key)
            continue
        new_entry = {
            "title": key,
            "author": author,
            "pubDate": None,
            "pubPlace": None,
            "compPlace": None,
            "compDate": None,
            "תיאור_חדש": None,
            "heShortDesc": None,
            "heDesc": None,
            "order": None,
            "Source": None if not value.endswith(".txt") else all_sources[value],
            "type": "file"
        }
        new_metadata.append(new_entry)
        all_titles.append(key)
    for folder in folders:
        if folder in all_titles:
            continue
        new_entry = {
            "title": folder,
            "author": None,
            "pubDate": None,
            "pubPlace": None,
            "compPlace": None,
            "compDate": None,
            "תיאור_חדש": None,
            "heShortDesc": None,
            "heDesc": None,
            "order": None,
            "Source": None,
            "type": "folder"
        }
        new_metadata.append(new_entry)
        all_titles.append(folder)
    with open('metadata/new_metadata.json', 'w', encoding='utf-8') as json_file:
        json.dump(new_metadata, json_file, indent=4, ensure_ascii=False)
    df = pd.DataFrame(new_metadata)
    df.to_csv("metadata/new_metadata.csv", encoding="utf-8", index=False)
    print(len(new_metadata))


if __name__ == "__main__":
    main()
