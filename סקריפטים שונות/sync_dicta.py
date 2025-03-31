import requests
import os


BASE_URL = "https://raw.githubusercontent.com/zevisvei/otzaria-library/refs/heads/main/"
BOOKS_FOLDER = ""

list_local_files = []

if os.path.exists(BOOKS_FOLDER):
    for root, _, files in os.walk(BOOKS_FOLDER):
        for file in files:
            if not file.endswith(".txt"):
                continue
            rel_path = os.path.relpath(os.path.join(root, file), BOOKS_FOLDER)
            list_local_files.append(rel_path)

list_from_github = requests.get(BASE_URL + "DictaToOtzaria/ספרים/לא ערוך/list.txt").text.splitlines()
list_all_per_os = [file.replace("/", os.sep) for file in list_from_github]

for file in list_from_github:
    file_name_per_os = file.replace("/", os.sep)
    file_path = os.path.join(BOOKS_FOLDER, file_name_per_os)
    if file not in list_local_files:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        response = requests.get(BASE_URL + f"DictaToOtzaria/ספרים/לא ערוך/אוצריא/{file}")
        if response.status_code != 200:
            print(f"שגיאה בהורדת הקובץ:\n{file}")
            continue
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)

for file in list_local_files:
    if file not in list_all_per_os:
        file_path = os.path.join(BOOKS_FOLDER, file)
        os.remove(file_path)

for root, folder, _ in os.walk(BOOKS_FOLDER):
    for folder in folder:
        folder_path = os.path.join(root, folder)
        if not os.listdir(folder_path):
            os.rmdir(folder_path)
