import json
import csv
import os
import re
import zipfile
import shutil

from bs4 import BeautifulSoup
import requests
from pyluach import dates

import dif


def new_folder_name() -> tuple[str, str]:
    today = dates.HebrewDate.today()
    month = today.month_name(hebrew=True)
    year = today.hebrew_year(withgershayim=False)
    return year, month


def adjust_html_tag_spaces(html: str) -> str:
    start_pattern = r'(<[^/<>]+?>)([ ]+)'
    end_pattern = r'([ ]+)(</[^<>]+?>)'
    while re.findall(end_pattern, html):
        html = re.sub(end_pattern, r'\2\1', html)
    while re.findall(start_pattern, html):
        html = re.sub(start_pattern, r'\2\1', html)
    html = re.sub(r'[ ]{2,}', ' ', html)
    html = re.sub(r"\s*\n\s*", r"\n", html)
    html = html.replace(": ", ":\n")
    html = re.sub(r"[\n]{2,}", "\n", html)
    return html


def extract_numerical_part(filename: str) -> float:
    name = filename.split("-")[-1]
    match = re.search(r'\d+', name)
    if match:
        return int(match.group())
    return float('inf')


def process_html(file: str) -> None:
    with open(file, 'r', encoding="utf-8") as f:
        html_content = f.read().replace("\n", " ")

    previous_tag = False
    soup = BeautifulSoup(html_content, 'lxml')
    for tag in soup.find_all():
        if "bold" in tag.get('class', []) or "marked-paragraph" in tag.get('class', []):
            if not previous_tag:
                tag.insert_before("\n")
                previous_tag = True
        else:
            previous_tag = False
        if "heading" in tag.get('class', []):
            if tag.parent.name != 'big':
                new_tag_big = soup.new_tag("big")
                if "bold" in tag.get('class', []):
                    new_tag_b = soup.new_tag("b")
                    new_tag_b.string = tag.get_text()
                    new_tag_big.append(new_tag_b)
                else:
                    new_tag_big.string = tag.get_text()
                tag.replace_with(new_tag_big)
        elif "bold" in tag.get('class', []):
            if tag.parent.name != 'b':
                new_tag = soup.new_tag("b")
                new_tag.string = tag.get_text()
                tag.replace_with(new_tag)
        else:
            tag.unwrap()
    for tag in soup.find_all():
        if not tag.get_text(strip=False) and tag.name != "br":
            tag.decompose()
        elif not tag.get_text(strip=True) and tag.name != "br":
            tag.insert_before(" ")
            tag.decompose()

    with open(file, 'w', encoding="utf-8") as f:
        f.write(str(soup))


def sanitize_filename(filename: str) -> str:
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', '', filename).replace('_', ' ')
    return sanitized_filename


def get_new_json(url: str) -> list:
    content = requests.get(url)
    if content.status_code == 200:
        return content.json()


def read_old_json(old_json_path: str) -> list:
    if os.path.exists(old_json_path):
        with open(old_json_path, "r", encoding="utf-8") as old_file:
            content = json.load(old_file)
        return content
    else:
        return []


def get_new_books(new_json: list, old_json: list):
    for book in new_json:
        if book not in old_json:
            yield book


def main(url: str, old_json_path: str, target: str, csv_file_path: str) -> None:
    if os.path.exists("list.csv"):
        shutil.copy("list.csv", "old.csv")
    new_json = get_new_json(url)
    old_books = read_old_json(old_json_path)
    for book in get_new_books(new_json, old_books):
        display_name = book.get('displayName', 'ללא שם')
        category = book.get('category', 'ללא קטגוריה')
        OCRDataURL = book.get('OCRDataURL')
        author = book.get("author")
        if OCRDataURL:
            file_name = sanitize_filename(display_name.strip())
            category = sanitize_filename(category.strip())
            text_response = requests.get(OCRDataURL.strip())
            if text_response.status_code == 200:
                print(file_name)
                if os.path.exists("temp"):
                    shutil.rmtree("temp")
                if os.path.exists("temp.zip"):
                    os.remove("temp.zip")
                with open("temp.zip", "wb") as file:
                    file.write(text_response.content)
                os.makedirs("temp", exist_ok=True)
                with zipfile.ZipFile("temp.zip", 'r') as zip_ref:
                    zip_ref.extractall("temp")
                for file in os.listdir("temp"):
                    file = os.path.join("temp", file)
                    process_html(file)
                text_files = [file for file in os.listdir("temp") if file.lower().endswith('.html')]
                text_files.sort(key=extract_numerical_part)
                merged_content = f"<h1>{display_name}</h1>\n" if display_name != "ללא שם" else ""
                if author:
                    merged_content += f"{author}\n"
                for index, text_file in enumerate(text_files):
                    file_path = os.path.join("temp", text_file)
                    with open(file_path, 'r', encoding="utf-8") as file:
                        file_content = file.read()
                        merged_content += file_content
                        if index < len(text_files) - 1:
                            merged_content += ' '
                merged_content = adjust_html_tag_spaces(merged_content)
                target_path = os.path.join(target, category)
                os.makedirs(target_path, exist_ok=True)
                target_file_path = os.path.join(target_path, f"{file_name}.txt")
                num = 1
                while os.path.exists(target_file_path):
                    num += 1
                    target_file_path = os.path.join(target_path, f"{file_name}_{num}.txt")

                with open(target_file_path, "w", encoding="utf-8") as final_file:
                    final_file.write(merged_content)
                list_all = ['displayName', 'printYear', 'author', 'printLocation', 'category',
                            'source', 'textFileURL', 'nikudMetegFileURL', 'OCRDataURL', 'ocrFeDir',
                            'displayNameEnglish', 'authorEnglish', 'categoryEnglish', 'printLocationEnglish',
                            "underwentBerelUnflagging", 'fileName', 'notHumanReviewed']
                with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    new_dict = {}
                    for item in list_all:
                        new_dict[item] = book.get(item, '')
                    if csv_file.tell() == 0:
                        writer.writerow(list_all)
                    writer.writerow(list(new_dict.values()))
                old_books.append(book)
                with open(old_json_path, "w", encoding="utf-8") as updated_file:
                    json.dump(old_books, updated_file, ensure_ascii=False, indent=4)
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    if os.path.exists("temp.zip"):
        os.remove("temp.zip")
    os.makedirs(target_path, exist_ok=True)
    dif.main(target_path)


url = r"https://raw.githubusercontent.com/Dicta-Israel-Center-for-Text-Analysis/Dicta-Library-Download/refs/heads/main/books.json"
old_json_path = "old books.json"
csv_file_path = "list.csv"
year, month = new_folder_name()
target_path = os.path.join("..", "ספרים", "לא ערוך", "לא ממויין", year, month)
main(url, old_json_path, target_path, csv_file_path)
