import os
import csv


authors_list = {}
csv_file_path = "authors.csv"
main_folder = os.path.join("..", "ספרים", "אוצריא")


with open(csv_file_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for line in reader:
        authors_list[line[0].strip()] = line[1].strip()


for root, _, files in os.walk(main_folder):
    for file in files:
        if os.path.splitext(file)[1].lower() != ".txt":
            continue
        if "הערות על" in file:
            continue
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().split("\n")
            if authors_list.get(content[1].strip()):
                content[1] = authors_list[content[1].strip()]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
