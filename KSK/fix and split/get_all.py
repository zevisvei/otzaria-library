"""
כותב לקובץ את כל הערכים הייחודיים הקיימים ברמת הכותרת h3 בקבצים שבתיקיות ותתי תיקיות
"""

import re
import os

list_all = []
base_folder = "/home/zevi5/Desktop/ksk/‏‏קובץ שיטות קמאי"
for root, _, files in os.walk(base_folder):
    for file in files:
        file_path = os.path.join(root, file)
        print(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        all_h3 = re.findall(r"<h3>(.+?)</h3>", content)
        list_all.extend(all_h3)
list_all = map(lambda x: x.strip().strip("][").strip(), list_all)
list_all = set(list_all)
list_all = list(list_all)
list_all.sort()
print(len(list_all))
with open("list all.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(list_all))
