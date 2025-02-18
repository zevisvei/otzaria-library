import csv
import os
import requests
import subprocess


BASE_URL = "https://script.google.com/macros/s/AKfycbz4pSY2vK8opQeeh2X__PZYDs1EP8Wq77HfoU7F0X_bCErKfl6nvDjnnQ_B4AjpUT-7/exec"


def get_book(start_from_line: int | str = 1) -> dict:
    params = {"action": "get_book", "start_line": start_from_line}
    response = requests.get(BASE_URL, params=params)
    return response.json()


def complete_book(row: int | str) -> dict:
    params = {"action": "complete_book", "row": row}
    response = requests.get(BASE_URL, params=params)
    return response.json()


ver_folder = "library_csv"  # תיקיית קבצי הcsv
root_folder = "אוצריא"
files_folder = ""  # נתיב תיקיית אוצריא ספרים

mapping = {
    "Ben-Yehuda": "Ben-YehudaToOtzaria/ספרים/אוצריא",
    "Dicta": "DictaToOtzaria/ספרים/ערוך/אוצריא",
    "OnYourWay": "OnYourWayToOtzaria/ספרים/אוצריא",
    "Orayta": "OraytaToOtzaria/ספרים/אוצריא",
    "sefaria": "sefaria and more",
    "sefaria_new": "sefariaToOtzaria/ספרים/אוצריא",
    "MoreBooks": "MoreBooks"
}


eroor_dict = {
    "1": "שגיאת כתיב",
    "2": "שגיאת כותרת"
}


line_num = 1
while (book_info := (book := get_book(line_num)).get("values")):
    library_ver, book_id, line, eroor_id, more_info = book_info
    line_in_api = book.get("row", 1)
    line_num = int(line_in_api) + 1
    ver_file = os.path.join(ver_folder, f"{library_ver}.csv")
    if not os.path.exists(ver_file):
        continue
    with open(ver_file, "r", encoding="utf-8") as f_2:
        reader_2 = csv.reader(f_2)
        next(reader_2)
        list_all = list(reader_2)
    line = int(line)
    book_line = list_all[line]
    del list_all
    book_path, book_source, book_len = book_line[1:]
    book_source_path = mapping[book_source]
    book_rel_path = os.path.relpath(book_path, root_folder)
    book_file_path = os.path.join(files_folder, book_source_path, book_rel_path)
    if not os.path.exists(book_file_path):
        print("הקובץ לא נמצא")
        continue
    with open(book_file_path, "r", encoding="utf-8") as f:
        content = f.read().split("\n")
        content_len = len(content)
    if content_len != int(book_len):
        ask = input("מספר השורות שונה, לעקוף? [כן/לא]\n")
        if ask.strip() != "כן":
            continue
    print(f"מקור הקובץ: {book_source}")
    print(f"סוג השגיאה: {eroor_dict.get(eroor_id)}")
    if more_info:
        print(f"פירוט נוסף: {more_info}")
    subprocess.run(["code", "-g", f"{book_file_path}:{line}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    ask = input("לדווח כהושלם? [כן/לא]\n")
    if ask.strip() != "כן":
        continue
    complete_book(line_in_api)

print("כל הקבצים טופלו")
