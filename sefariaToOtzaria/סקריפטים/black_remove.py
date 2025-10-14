import json
import os

meta_data_file_path = r"C:\Users\Otzaria\Desktop\ייצוא\metadata1.json"
files_folder_path = r"C:\Users\Otzaria\Desktop\ייצוא\אוצריא"
black_list_files_path = r"C:\Users\Otzaria\Desktop\ייצוא\ספרים.txt"
black_authors_file_path = r"C:\Users\Otzaria\Desktop\ייצוא\מחברים.txt"
links_folder = r"C:\Users\Otzaria\Desktop\ייצוא\links"


def read_file(file_path: str) -> set[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return set(f.read().split("\n"))


black_authors = {i.strip() for i in read_file(black_authors_file_path) if i.strip()}
black_list = {i.strip() for i in read_file(black_list_files_path) if i.strip()}
with open(meta_data_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
deleted_files = []
for key, value in data.items():
    authors = value.get("heAuthors", [])
    title = value["title"]
    if (title in black_list) or any(author in black_authors for author in authors):
        file_path = key.replace("C:\\Users\\Otzaria\\Desktop\\ייצוא", files_folder_path) + ".txt"
        file_name = key.split("\\")[-1]
        if os.path.exists(file_path):
            os.remove(file_path)
            if os.path.exists(os.path.join(links_folder, f"{file_name}_links.json")):
                os.remove(os.path.join(links_folder, f"{file_name}_links.json"))
            print(f"{file_path=} נמחק")
        else:
            print(f"{file_path=} לא קיים")
        deleted_files.append(file_name)

for file in os.listdir(links_folder):
    if not file.endswith("_links.json"):
        continue
    file_path = os.path.join(links_folder, file)
    with open(file_path, "r", encoding="utf-8") as f:
        links = json.load(f)
    links_copy = links.copy()
    for link in links:
        if link["path_2"].replace(".txt", "") in deleted_files:
            links_copy.remove(link)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(links_copy, f, ensure_ascii=False, indent=2)

for root, dirs, _ in os.walk(files_folder_path):
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
            print(f"{dir_path} נמחק")
