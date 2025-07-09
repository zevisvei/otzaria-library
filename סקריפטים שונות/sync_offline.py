import json
import os
import shutil

import requests


BASE_URL = "https://raw.githubusercontent.com/zevisvei/otzaria-library/refs/heads/main/"
BASE_PATH = "אוצריא"
LOCAL_PATH = ""
DEL_LIST_FILE_NAME = "del_list.txt"
MANIFEST_FILE_NAME = "files_manifest.json"


def copy_manifest(is_dicta: bool = False) -> None:
    os.makedirs(BASE_PATH, exist_ok=True)
    manifest_file_name = MANIFEST_FILE_NAME if not is_dicta else f"dicta_{MANIFEST_FILE_NAME}"
    shutil.copy(os.path.join(LOCAL_PATH, manifest_file_name), os.path.join(BASE_PATH, manifest_file_name))


def copy_files() -> None:
    shutil.copytree(BASE_PATH, LOCAL_PATH, dirs_exist_ok=True, ignore=lambda _, files: [DEL_LIST_FILE_NAME] if DEL_LIST_FILE_NAME in files else [])


def remove_files() -> None:
    del_list_file_path = os.path.join(BASE_PATH, DEL_LIST_FILE_NAME)
    with open(del_list_file_path, "r", encoding="utf-8") as f:
        content = f.readlines()
    for file_path in content:
        file_path = file_path.strip()
        if not file_path:
            continue
        full_path = os.path.join(LOCAL_PATH, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    os.remove(del_list_file_path)


def remove_empty_dirs() -> None:
    for root, dirs, _ in os.walk(LOCAL_PATH, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)


def download_new(is_dicta: bool = False) -> None:
    del_list = []
    manifest_file_name = MANIFEST_FILE_NAME if not is_dicta else f"dicta_{MANIFEST_FILE_NAME}"
    new_manifest_url = f"{BASE_URL}/{manifest_file_name}"
    old_manifest_file_path = os.path.join(BASE_PATH, manifest_file_name)

    new_manifest_content = requests.get(new_manifest_url).json()
    with open(old_manifest_file_path, "r", encoding="utf-8") as f:
        old_manifest_content = json.load(f)

    if new_manifest_content == old_manifest_content:
        return

    for book_name, value in new_manifest_content.items():
        if value["hash"] == old_manifest_content.get(book_name, {}).get("hash"):
            continue
        target_path = os.path.join(BASE_PATH, book_name.replace("/", os.sep))
        file_url = f"{BASE_URL}{book_name}" if not is_dicta else f"{BASE_URL}DictaToOtzaria/ספרים/לא ערוך/{book_name.replace(r"/דיקטה", "")}"
        response = requests.get(file_url)
        response.raise_for_status()
        file_content = response.text
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(file_content)

    for book_name in old_manifest_content:
        if book_name not in new_manifest_content:
            del_list.append(book_name.replace("/", os.sep))

    with open(old_manifest_file_path, "w", encoding="utf-8") as f:
        json.dump(new_manifest_content, f, indent=2, ensure_ascii=False)

    with open(os.path.join(BASE_PATH, DEL_LIST_FILE_NAME), "a", encoding="utf-8") as f:
        f.write("\n".join(del_list) + "\n")


if __name__ == "__main__":
    download_new()
    download_new(is_dicta=True)
