import json

from otzaria.utils import recursive_register_categories
from otzaria.sefaria_api import SefariaApi


def json_read(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return recursive_register_categories(data)


def json_write(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def get_titles(index):
    list_all_he = [i["he_title"] for i in index]
    list_all_en = [i["en_title"] for i in index]
    return list_all_he, list_all_en


def new_vs_old(new, old):
    not_in_new = []
    not_in_old = []
    list_he_titles_new, list_en_titles_new = get_titles(new)
    list_he_titles_old, list_en_titles_old = get_titles(old)
    for i in new:
        if i["he_title"] not in list_he_titles_old and i["en_title"] not in list_en_titles_old:
            not_in_old.append(i)
    for i in old:
        if i["he_title"] not in list_he_titles_new and i["en_title"] not in list_en_titles_new:
            not_in_new.append(i)
    return not_in_old, not_in_new


old_books_toc = "old.json"
new_books_toc = SefariaApi().table_of_contents()
old = json_read(old_books_toc)
new = recursive_register_categories(new_books_toc)
not_in_old, not_in_new = new_vs_old(new, old)
json_write("not_in_old.json", not_in_old)
json_write("not_in_new.json", not_in_new)
print(len(not_in_new))
print(len(not_in_old))
