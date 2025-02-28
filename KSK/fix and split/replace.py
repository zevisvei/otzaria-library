import os
import csv


base_folder = "/home/zevi5/Pictures/‏‏קובץ שיטות קמאי/"
csv_path = "/home/zevi5/Pictures/replace.csv"
replace_dict = {}
with open(csv_path, 'r', newline='', encoding="windows-1255") as file:
    reader = csv.reader(file)
    for row in reader:
        replace_dict[row[0].strip()] = row[1].strip()

for root, _, files in os.walk(base_folder):
    for file in files:
        print(file)
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        for key, value in replace_dict.items():
            content = content.replace(key, value)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
