import requests
import json
import os
import re

def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', '', filename).replace('_', ' ')
    return sanitized_filename.strip()

def get_index():
    url = "https://www.sefaria.org/api/index/"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()

def recursive_register_categories(index, data=None, tree=None):
    if tree is None:
        tree = []
    if data is None:
        data = []
    if isinstance(index, list):
        for item in index:
            recursive_register_categories(item, data, tree)
    elif isinstance(index, dict):
        if index.get('contents'):
            tree.append(index['heCategory'])
            for item in index['contents']:
                recursive_register_categories(item, data, tree)
            tree.pop(-1)
        if index.get('title'):
            data.append({"he_title":index['heTitle'], "en_title":index['title'], "path":tree.copy()})
    return data

def get_book(book_title):
    url = f"https://www.sefaria.org/api/v3/texts/{book_title}?version=hebrew"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()

def get_terms(sectionName):
    url = f"https://www.sefaria.org/api/terms/{sectionName}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers).json()
    for title in response["titles"]:
        if title["lang"] == "he":
            return title["text"] 

def get_links(book_title):
    url = f"https://www.sefaria.org/api/links/{book_title}?with_text=0"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()

index = get_index()
all_books = recursive_register_categories(index)
for book in all_books:
    book_title = book["en_title"]
    print(book_title)
    book_path = book["path"]
    book_name_heb = book["he_title"]
    book_path = [sanitize_filename(path) for path in book_path]
    book_name = sanitize_filename(book_name_heb)
    book_path = os.path.join(*book_path, book_name)
    os.makedirs(os.path.split(book_path)[0], exist_ok=True)
    book_data = get_book(book_title)
    with open(f"{book_path}.json", "w", encoding="utf-8") as f:
        json.dump(book_data, f, ensure_ascii=False, indent=4)
    ref_data = get_links(book_title)
    with open(f"{book_path}_links.json", "w", encoding="utf-8") as f:
        json.dump(ref_data, f, ensure_ascii=False, indent=4)
    print(f"Finished downloading {book_title}")