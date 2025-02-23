import re
import os


base_folder = "MoreBooks/תלמוד בבלי/ראשונים/‏‏קובץ שיטות קמאי"  # התיקייה שמכילה את הקבצים
target_folder = "lists"  # התיקייה שבה יהיו כל הקבצים
os.makedirs(target_folder, exist_ok=True)
for root, _, files in os.walk(base_folder):
    for file in files:
        file_path = os.path.join(root, file)
        print(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        all_h3 = re.findall(r"<h3>(.+?)</h3>", content)
        list_all = map(lambda x: x.strip().strip("][").strip(), all_h3)
        list_all = set(list_all)
        list_all = list(list_all)
        list_all.sort()
        target_file = os.path.join(target_folder, file)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("\n".join(list_all))
