import json
import os

import requests


BASE_URL = "https://raw.githubusercontent.com/zevisvei/otzaria-library/refs/heads/main/"
MANIFEST_FILE_NAME = "files_manifest.json"
BASE_PATH = "אוצריא"
DEL_LIST_FILE_NAME = "del_list.txt"


def main():
    del_list = []
    new_manifest_url = f"{BASE_URL}/{MANIFEST_FILE_NAME}"
    old_manifest_file_path = os.path.join(BASE_PATH, MANIFEST_FILE_NAME)

    new_manifest_content = requests.get(new_manifest_url).json()
    with open(old_manifest_file_path, "r", encoding="utf-8") as f:
        old_manifest_content = json.load(f)

    if new_manifest_content == old_manifest_content:
        return

    for book_name, value in new_manifest_content.items():
        if value["hash"] == old_manifest_content.get(book_name, {}).get("hash"):
            continue
        target_path = os.path.join(BASE_PATH, book_name.replace("/", os.sep))
        file_url = f"{BASE_URL}{book_name}"
        response = requests.get(file_url)
        response.raise_for_status()
        file_content = response.text
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(file_content)

    for book_name in old_manifest_content:
        if book_name not in new_manifest_content:
            del_list.append(os.path.join(BASE_PATH, book_name.replace("/", os.sep)))

    with open(old_manifest_file_path, "w", encoding="utf-8") as f:
        json.dump(new_manifest_content, f, indent=2, ensure_ascii=False)

    with open(os.path.join(BASE_PATH, DEL_LIST_FILE_NAME), "w", encoding="utf-8") as f:
        f.write("\n".join(del_list))


if __name__ == "__main__":
    main()
