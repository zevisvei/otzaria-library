"""
כותב לקובץ את כל הערכים הייחודיים הקיימים ברמת הכותרת h3 בקבצים שבתיקיות ותתי תיקיות
"""

import os

list_all = []
base_folder = "MoreBooks/תלמוד בבלי/ראשונים/‏‏קובץ שיטות קמאי"
for root, _, files in os.walk(base_folder):
    for file in files:
        file_path = os.path.join(root, file)
        print(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        zero_lines = [line for line in content.split("\n") if "0" in line]
        list_all.extend(zero_lines)
list_all = set(list_all)
list_all = list(list_all)
list_all.sort()
print(len(list_all))
with open("list all zero.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(list_all))
