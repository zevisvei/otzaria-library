"""
מפצל את הקבצים לקבצים נפרדים לפי כותרות הh3
"""

import re
from collections import defaultdict
import os


def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[\\/:"*?<>|]', '', filename).replace('_', ' ')
    return sanitized_filename


def split_file(file_path):
    dict_all = defaultdict(lambda: defaultdict(list))
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    lines = content.split("\n")
    h_2 = re.compile(r"<h2>(.+?)</h2>")
    h_3 = re.compile(r"<h3>(.+?)</h3>")
    h_2_level = None
    h_3_level = None
    for line in lines[1:]:
        if re.search(h_2, line):
            h_2_level = re.search(h_2, line).group(1).strip().strip("][").strip()
        elif re.search(h_3, line):
            h_3_level = re.search(h_3, line).group(1)
        else:
            dict_all[h_3_level][h_2_level].append(line)
    return dict_all


def main(base_folder):
    for root, _, files in os.walk(base_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_split = split_file(file_path)
            file_folder = sanitize_filename(os.path.splitext(file)[0])
            os.makedirs(file_folder, exist_ok=True)
            for key, value in file_split.items():
                target_path = os.path.join(file_folder, f"{sanitize_filename(key)}.txt")
                all_lines = [f"<h1>{key}</h1>"]
                for k, v in value.items():
                    all_lines.append(f"<h2>{k}</h2>")
                    all_lines.extend(v)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(all_lines))


base_folder = "/home/zevi5/Desktop/ksk/tt"
main(base_folder)
