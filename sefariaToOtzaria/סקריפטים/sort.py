import os
import shutil
import csv

mapping = {
    "Ben-Yehuda": "Ben-YehudaToOtzaria/ספרים/אוצריא",
    "Dicta": "DictaToOtzaria/ספרים/ערוך/אוצריא",
    "OnYourWay": "OnYourWayToOtzaria/ספרים/אוצריא",
    "Orayta": "OraytaToOtzaria/ספרים/אוצריא"
}

csv_file_path = os.path.join("..", "..", "אוצריא","אודות התוכנה" ,"SourcesBooks.csv")
links_path = os.path.join("..", "..", "links")
month_path = ["תשפה", "שבט"]
new_list = []
main_file_path = os.path.join("..", "ספרים", "לא ממויין", *month_path)
black_list_file_path = "blackList.txt"
target_path = os.path.join("..", "ספרים", "אוצריא")
dicta_path = os.path.join("..", "..", "DictaToOtzaria", "ספרים", "אוצריא")
skip_ext = (".csv", ".log")
with open(black_list_file_path, "r", encoding="utf-8") as f:
    content = f.read()
black_list = [i.strip() for i in content.split("\n")]
for root, _, files in os.walk(main_file_path):
    for file in files:
        file_name_ane_ext = os.path.splitext(file)
        if file_name_ane_ext[0].replace("הערות על ", "").replace("_links", "") in black_list or file_name_ane_ext[1] in skip_ext:
            continue
        file_path = os.path.join(root, file)
        if file_name_ane_ext[1] == ".txt":
            rel_path = os.path.relpath(file_path, main_file_path)
            split_path = rel_path.split(os.sep)
            fix_path = split_path[:-2] + [split_path[-1]]
            target = os.path.join(target_path, *fix_path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy(file_path, target)
            new_list.append(file_name_ane_ext[0])
        elif file.endswith("_links.json"):
            target = os.path.join(links_path, file)
            shutil.copy(file_path, target)

with open(csv_file_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if os.path.splitext(row[0]) in new_list:
            file_path = row[1].split("/")
            file_path = os.path.join(mapping[row[2]], *file_path[1:])
            print(file_path)
            raise NotImplementedError("This script is not yet finished")
