import os
import json

import pandas as pd
from tqdm import tqdm

from otzaria.sefaria_api import SefariaApi
from otzaria.get_from_sefaria import Book
from otzaria.utils import sanitize_filename, recursive_register_categories, footnotes


def filter_new_books(new_list: list[dict[str, str | list]], file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    get_book_names = recursive_register_categories(content)
    en_titles = [i["en_title"] for i in get_book_names]
    he_titles = [i["he_title"] for i in get_book_names]
    filtered_list = [i for i in new_list if i["en_title"] not in en_titles and i["he_title"] not in he_titles]
    return filtered_list


def main(get_links: bool = False, only_new: bool = True, old_json_file_path: str = ""):
    new_index = SefariaApi().table_of_contents()
    get_new_book_names = recursive_register_categories(new_index)
    if only_new:
        get_new_book_names = filter_new_books(get_new_book_names, old_json_file_path)
    for book in tqdm(get_new_book_names, desc="", unit="books"):
        try:
            book_en_title = book["en_title"]
            book_he_title = book["he_title"]
            book_path = book["path"]
            file_name = sanitize_filename(book_he_title)
            file_path = [sanitize_filename(category) for category in book_path]
            file_path = os.path.join(*file_path, file_name)
            book_ins = Book(book_en_title, "hebrew", book_he_title, book_path, get_links=get_links)
            book_content = book_ins.process_book()
            book_refs = book_ins.refs
            if book_content:
                os.makedirs(file_path, exist_ok=True)
                book_file = os.path.join(file_path, file_name)
                book_content_copy = []
                dict_links = []
                all_footnotes = []
                for index, line in enumerate(book_content, start=1):
                    if "footnote-marker" in line:
                        line, footnotes_list = footnotes(line)
                        for foot_note in footnotes_list:
                            dict_links.append({
                                "line_index_1": index,
                                "heRef_2": "הערות",
                                "path_2": f"הערות על {file_name}.txt",
                                "line_index_2": len(all_footnotes) + 1,
                                "Conection Type": "commentary"
                            })
                            all_footnotes.append(foot_note)
                    book_content_copy.append(line)
                with open(f"{book_file}.txt", "w", encoding="utf-8") as f:
                    f.writelines(book_content_copy)
                if all_footnotes:
                    footnotes_file = os.path.join(file_path, f"הערות על {file_name}.txt")
                    with open(footnotes_file, 'w', encoding='utf-8') as file:
                        file.write("\n".join(all_footnotes))
                    json_file = os.path.join(file_path, f"{file_name}_links.json")
                    with open(json_file, "w", encoding="utf-8") as file:
                        json.dump(dict_links, file)
                if book_ins.links:
                    with open(f'{book_file}.json', 'w', encoding='utf-8') as json_file:
                        json.dump(book_ins.links, json_file, indent=4, ensure_ascii=False)
                if book_refs:
                    df = pd.DataFrame(book_refs)
                    df.to_csv(f"{book_file}.csv", index=False)
        except Exception as e:
            print(e)
            with open("error.txt", "a", encoding="utf-8") as f:
                f.write(f"{book_he_title} error {e}\n")


if __name__ == "__main__":
    main()
