import csv
import os


ver_folder = "library_csv"
root_folder = "אוצריא"

mapping = {
    "Ben-Yehuda": "Ben-YehudaToOtzaria/ספרים/אוצריא",
    "Dicta": "DictaToOtzaria/ספרים/ערוך/אוצריא",
    "OnYourWay": "OnYourWayToOtzaria/ספרים/אוצריא",
    "Orayta": "OraytaToOtzaria/ספרים/אוצריא",
    "sefaria": "sefaria and more",
    "sefaria_new": "sefariaToOtzaria/ספרים/אוצריא",
    "MoreBooks": "MoreBooks"
}


csv_file_path = ""
with open(csv_file_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for line in reader:
        book_index, start_line, end_line, library_ver = line
        ver_file = os.path.join(ver_folder, f"{library_ver}.csv")
        if not os.path.exists(ver_file):
            continue
        with open(ver_file, "r", encoding="utf-8") as f_2:
            reader_2 = csv.reader(f_2)
            next(reader_2)
            list_all = list(reader_2)
        book_index = int(book_index)
        book_line = list_all[book_index]
        del list_all
        book_source, book_path = book_line
        book_source_path = mapping[book_source]
        book_rel_path = os.path.relpath(book_path, root_folder)
        book_file_path = os.path.join(book_source_path, book_rel_path)
        assert os.path.exists(book_file_path)
