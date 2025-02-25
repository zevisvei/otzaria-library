import re

file_path = "אוצריא/ספרות עזר/מילונים/ספר הערוך.txt"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
list_all = re.findall(r"<b><big>(.+?)</big></b>", content)

list_all = set(list_all)
list_all = list(list_all)
list_all.sort()
print(len(list_all))
with open("ערכי הערוך.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(list_all))
