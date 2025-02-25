import os
import subprocess

import requests

BASE_URL = "https://script.google.com/macros/s/AKfycbz4pSY2vK8opQeeh2X__PZYDs1EP8Wq77HfoU7F0X_bCErKfl6nvDjnnQ_B4AjpUT-7/exec"


def get_books():
    params = {"action": "get_book"}
    response = requests.get(BASE_URL, params=params).json()
    if response["success"]:
        for i in response["data"]:
            yield i


def complete_book(row: int | str, comment: str | None = None) -> bool:
    params = {"action": "complete_book", "row": row, "comments": comment}
    response = requests.get(BASE_URL, params=params).json()
    return response["success"]


def main(library_path: str) -> None:
    for book in get_books():
        fix_file_path = book["bookFilePath"].replace("/", os.sep)
        file_path = os.path.join(library_path, fix_file_path)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            file_len = len(content.split("\n"))
        if file_len != book["lines_num"]:
            print(f"File length mismatch: {file_len} != {book['bookLength']}")
            continue
        print(f"סוג שגיאה: {book['eroorStr']}")
        print(f"מקור הקובץ: {book['bookSource']}")
        if book["file_path_in_yemot"]:
            print(f"נתיב ימות: {book['file_path_in_yemot']}")
        if book["comments"]:
            print(f"הערה: {book['comments']}")
        if book["more_info"]:
            print(f"מידע נוסף: {book['more_info']}")
        print(f"מספר שורה: {book['line']}")
        subprocess.run(["code", "-g", f"{file_path}:{book['line']}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        ask = input("לדווח כהושלם? [כן/לא]\n")
        if ask.strip() != "כן":
            continue
        commnt = input("הערה: ")
        line_in_api = book["row"]
        result = complete_book(line_in_api, commnt)
        if result:
            print("נשלח בהצלחה")
        else:
            print("שגיאה בשליחה")


library_path = "/home/zevi5/Downloads/otzaria-library/"
main(library_path)
