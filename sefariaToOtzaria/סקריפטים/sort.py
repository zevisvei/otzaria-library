import os
import shutil

links_path = os.path.join("..", "..", "links")
month_path = ["תשפה", "שבט"]
main_file_path = os.path.join("..", "ספרים", "לא ממויין", *month_path)
black_list_file_path = "blackList.txt"
target_path = os.path.join("..", "ספרים", "אוצריא")
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
        elif file.endswith("_links.json"):
            target = os.path.join(links_path, file)
            shutil.copy(file_path, target)
