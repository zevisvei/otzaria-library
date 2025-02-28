"""
מתקן את סדר הכותרות, מסיר שורות שמכילות רק את התווים ---, מסיר סןגריים מרובעות ורווחים מיותרים מהכותרת, מחליף את '' ל" בכותרת.
"""

import re
import os
import json


def h_2(text: str):
    if "דף" not in text:
        text = f"דף {text}"
    text = text.strip("[]. ")
    text = text.replace("''", '').replace('"', '').replace("'", "").replace(" עא", ".").replace(" עב", ":").strip().replace("דף .", "דף עא").replace("דף :", "דף עב")
    return f"<h2>{text}</h2>"


def h_3(text: str):
    text = text.replace("''", '"').replace("0", " ").strip("[]. ").strip()
    if "הערוך" in text:
        text = f"<h4>{text}</h4>"
    elif len(text) < 150:  # אורך מקסימאלי של כותרת ברמה h3
        text = f"<h3>{text}</h3>"
    return text


def fix_h2_order(content: str, header: str):
    if "<h2>" in content or "<h1>" in content:
        # if header == "<h3>ערוך</h3>" and "h3" in fix_aruch(content):
        #     print(content)
        split_content = content.split("\n")
        index = 0
        while "<h2>" in split_content[index] or "<h1>" in split_content[index] or not split_content[index].strip(" ."):
            index += 1
        split_content.insert(index, header)
        content = "\n".join(split_content)
    else:
        content = f"{header}\n{content}"
    return content


def fix_order(content: str, header: str):
    if "הערוך" in header:
        result = f"------\n{content}\n{header}\n------\n"
    else:
        result = fix_h2_order(content, header)
    return result


def fix_2(content: str):
    if content.replace("]\n.", "].").strip().strip('ִ').endswith("]."):
        start_index = content.rfind("[")
        if start_index == -1:
            return
        header = content[start_index:]
        # print(header)
        content = content[:start_index].strip()
        header = h_3(header.replace("\n", " "))
        # print(header)
        return fix_order(content, header)
    elif content.endswith("</h3>"):
        start_index = content.rfind("<h3>")
        if start_index == -1:
            return
        header = content[start_index:].replace("</h3>", "").replace("<h3>", "")
        content = content[:start_index].strip()
        header = h_3(header.replace("\n", " "))
        return fix_order(content, header)
    # else:
    #     print(content)


def fix_aruch(text: str):
    return re.sub(r"\[(.*?הערוך ערך.*?)\]", r"\n<b>\1</b>\n", text)


base_folder = "/home/zevi5/Pictures/‏‏קובץ שיטות קמאי/"
for root, _, files in os.walk(base_folder):
    for file in files:
        print(file)
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().replace("%", "-")
        content = re.sub(r"</h3>\s*-*", "</h3>\n-------", content)
        content = re.sub(r"-{4,}", r"-------", content)
        all_sec = content.split("-------")
        # if len(all_sec) == 1:
        #     print(file_path)
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
        new_list = []
        aruch = False
        for part in new.split("------"):
            if "<h4>" in part:
                if not aruch:
                    part = fix_h2_order(part, "<h3>ערוך</h3>")
                # else:
                #     print(part)
                new_list.append(part.replace("<h4>", "[").replace("</h4>", "]"))
                aruch = True
            elif part.strip():
                new_list.append(part)
                aruch = False
        new = "\n".join(new_list)
        new = fix_aruch(new)
        new = new.split("\n")
        new = [line.strip().lstrip(".").strip() for line in new if line.strip().lstrip(".").strip()]
        # mas = new[0].replace("</h1>", "").replace("<h1>קובץ שיטות קמאי על ", "")
        # link_path = os.path.join("/home/zevi5/Downloads/otzaria-library/אוצריא/תלמוד בבלי/", file_path.split(os.sep)[-2], f"{mas}.txt")
        # if os.path.exists(link_path):
        #     with open(link_path, "r", encoding="utf-8") as f:
        #         link_content = f.read().split("\n")
        #     gmara_index = {page.replace("<h2>", "").replace("</h2>", ""): index for index, page in enumerate(link_content, start=1) if "h2" in page}
        #     all_pages = {page.replace("<h2>", "").replace("</h2>", ""): index for index, page in enumerate(new, start=1) if "h2" in page}
        #     all_links = []
        #     for page, index in all_pages.items():
        #         if gmara_index.get(page):
        #             all_links.append({
        #                     "line_index_1": index,
        #                     "heRef_2": "גמרא",
        #                     "path_2": f"{mas}.txt",
        #                     "line_index_2": gmara_index[page],
        #                     "Conection Type": "commentary"
        #                 })
        #     if all_links:
        #         with open(f"{os.path.splitext(file_path)[0]}_links.json", "w", encoding="utf-8") as f:
        #             json.dump(all_links, f, indent=4, ensure_ascii=False)
        # print(mas)
        new = "\n".join(new)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new)
