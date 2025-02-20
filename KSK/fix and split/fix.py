"""
מתקן את סדר הכותרות, מסיר שורות שמכילות רק את התווים ---, מסיר סןגריים מרובעות ורווחים מיותרים מהכותרת, מחליף את '' ל" בכותרת.
"""

import re
import os


def h_2(text: str):
    if "דף" not in text:
        text = f"דף {text}"
    text = text.strip("[]. ")
    text = text.replace("''", '').replace('"', '').replace("'", "").replace(" עא", ".").replace(" עב", ":").strip().replace("דף .", "דף עא").replace("דף :", "דף עב")
    return f"<h2>{text}</h2>"


def h_3(text: str):
    text = text.replace("''", '"').strip("[]. ")
    if len(text) < 150:  # אורך מקסימאלי של כותרת ברמה h3
        text = f"<h3>{text}</h3>"
    return text


def fix_order(content: str, header: str):
    if "<h2>" in content or "<h1>" in content:
        split_content = content.split("\n")
        index = 0
        while "<h2>" in split_content[index] or "<h1>" in split_content[index]:
            index += 1
        split_content.insert(index, header)
        result = "\n".join(split_content)
    else:
        result = f"{header}\n{content}"
    return result


def fix_2(content: str):
    if content.replace("]\n.", "].").strip().strip('ִ').endswith("]."):
        start_index = content.rfind("[")
        if start_index == -1:
            return
        header = content[start_index:]
        print(header)
        content = content[:start_index].strip()
        header = h_3(header.replace("\n", " "))
        print(header)
        return fix_order(content, header)
    elif content.endswith("</h3>"):
        start_index = content.rfind("<h3>")
        if start_index == -1:
            return
        header = content[start_index:].replace("</h3>", "").replace("<h3>", "")
        content = content[:start_index].strip()
        header = h_3(header.replace("\n", " "))
        return fix_order(content, header)
    else:
        print(content)


base_folder = "/home/zevi5/Pictures/‏‏קובץ שיטות קמאי/"
for root, _, files in os.walk(base_folder):
    for file in files:
        print(file)
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().replace("%", "-")
        content = re.sub(r"-{4,}", r"-------", content)
        all_sec = content.split("-------")
        if len(all_sec) == 1:
            print(file_path)
        content = []
        for sec in all_sec:
            result = fix_2(sec.strip())
            if result:
                content.append(result)
            else:
                content.append(sec.strip())
        new = "\n".join(content)
        new = re.sub(r"<h2>(.+)</h2>", lambda match: h_2(match.group(1)), new)
        new = re.sub(r"<h3>(.+)</h3>", lambda match: h_3(match.group(1)), new)
        new = new.replace("''", '"')
        new = re.sub(r"[ ]{2,}", " ", new)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new)
