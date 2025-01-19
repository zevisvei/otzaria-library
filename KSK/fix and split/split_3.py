"""
מוציא כותרות h3 שזהות בתוכנן לטקסט שסופק
"""

import re
from collections import defaultdict
import os


def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[\\/:"*?<>|]', '', filename).replace('_', ' ')
    return sanitized_filename


def split_file(file_path, name):
    dict_all = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    lines = content.split("\n")
    h_2 = re.compile(r"<h2>(.+?)</h2>")
    h_3_not = re.compile(r"<h3>(.+?)</h3>")
    h_2_level = None
    start = True
    for line in lines[1:]:
        if re.search(h_2, line):
            h_2_level = re.search(h_2, line).group(1).strip().strip("][").strip()
        elif line == f"<h3>{name}</h3>":
            start = True
        elif re.search(h_3_not, line):
            start = False
        elif start:
            dict_all[h_2_level].append(line)
    return dict_all


def main(base_folder, name):
    for root, _, files in os.walk(base_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_split = split_file(file_path, name)
            file_folder = sanitize_filename(os.path.splitext(file)[0])
            os.makedirs(file_folder, exist_ok=True)
            target_path = os.path.join(file_folder, f"{sanitize_filename(name)}.txt")
            all_lines = [f"<h1>{name}</h1>"]
            for key, value in file_split.items():
                all_lines.append(f"<h2>{key}</h2>")
                all_lines.extend(value)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("\n".join(all_lines))


base_folder = "/home/zevi5/Desktop/ksk/tt"
name = "ערוך"
main(base_folder, name)
