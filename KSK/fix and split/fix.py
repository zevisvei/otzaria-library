"""
מתקן את סדר הכותרות, מסיר שורות שמכילות רק את התווים ---, מסיר סןגריים מרובעות ורווחים מיותרים מהכותרת, מחליף את '' ל" בכותרת.
"""

import re
import os


def h_2(text: str):
    if "דף" not in text:
        text = f"דף {text}"
    text = text.replace("''", '').replace('"', '').replace("עא", ".").replace("עב", ":").strip()
    return f"<h2>{text}</h2>"


def h_3(text: str):
    if len(text) < 60:  # אורך מקסימאלי של כותרת ברמה h3
        text = f"<h3>{text}</h3>"
    return text


base_folder = "/home/zevi5/Desktop/ksk/‏‏קובץ שיטות קמאי"
for root, _, files in os.walk(base_folder):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        all_headings = re.findall(r"<h3>(.+?)</h3>", content)
        all_headings = list(map(lambda x: x.replace("''", '"').strip().strip("][").strip(), all_headings))
        all_lines = content.split("\n")
        new_list = [*all_lines[0:2], h_3(all_headings[0])]
        index = 0
        for line in all_lines[2:]:
            if re.match(r"<h3>.+?</h3>", line):
                index += 1
                if index + 1 <= len(all_headings):
                    new_list.append(h_3(all_headings[index]))
            elif line.strip() == "------":
                continue
            else:
                new_list.append(line)
        new = "\n".join(new_list)
        new = re.sub(r"<h2>(.+)</h2>", lambda match: h_2(match.group(1)), new)
        new = new.replace("''", '"')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new)
