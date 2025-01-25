import os
import json

import pandas as pd

from otzaria.get_from_export import Book
from otzaria.utils import sanitize_filename, footnotes


def get_book(book_title: str, text_file_path: str, schema_file_path: str, lang: str):
    book_ins = Book(book_title,
                    lang,
                    text_file_path,
                    schema_file_path)
    book_content = book_ins.process_book()
    metadata, categories = book_ins.get_metadata()
    return book_content, metadata, categories, book_ins.refs


def main(json_folder, schemas_folder, output_folder, lang: str):
    """
    Process all books in the given folder whose path ends with 'Hebrew/Merged.json'.
    It finds the corresponding schema file in the schemas folder by matching the
    pattern '/xxxx/Hebrew/Merged.json' to 'xxxx.json'.

    :param folder_path: Path to the folder containing the book files.
    :param schemas_folder: Path to the folder containing the schema files.
    """
    for root, _, files in os.walk(json_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.lower().endswith(f'{lang}{os.sep}merged.json'):
                try:
                    text_file = file_path
                    print(text_file)
                    title = file_path.split(os.sep)[-3].replace(' ', '_')
                    schema_file_name = os.path.join(schemas_folder, title + '.json')
                    book_content, metadata, categories, refs = get_book(title, text_file, schema_file_name, lang)
                    output_path = [sanitize_filename(i) for i in categories]
                    os.makedirs(os.path.join(output_folder, *output_path), exist_ok=True)
                    output_file_name = os.path.join(output_folder, *output_path, sanitize_filename(metadata["title"]))
                    print(output_file_name)
                    book_content_copy = []
                    dict_links = []
                    all_footnotes = []
                    title = sanitize_filename(metadata["title"])
                    for index, line in enumerate(book_content, start=1):
                        if "footnote-marker" in line:
                            line, footnotes_list = footnotes(line)
                            for foot_note in footnotes_list:
                                dict_links.append({
                                    "line_index_1": index,
                                    "heRef_2": "הערות",
                                    "path_2": f"הערות על {title}.txt",
                                    "line_index_2": len(all_footnotes) + 1,
                                    "Conection Type": "commentary"
                                })
                                all_footnotes.append(foot_note)
                        book_content_copy.append(line)
                    with open(f'{output_file_name}.txt', 'w', encoding='utf-8') as file:
                        file.writelines(book_content_copy)
                    df = pd.DataFrame(refs)
                    df.to_csv(f"{output_file_name}.csv", index=False)
                    if all_footnotes:
                        footnotes_file = os.path.join(output_folder, *output_path, f"הערות על {title}.txt")
                        with open(footnotes_file, 'w', encoding='utf-8') as file:
                            file.write("\n".join(all_footnotes))
                        json_file = os.path.join(output_folder, *output_path, f"{title}_links.json")
                        with open(json_file, "w", encoding="utf-8") as file:
                            json.dump(dict_links, file)
                except Exception as e:
                    with open("error.txt", "a", encoding="utf-8") as f:
                        f.write(f"{file_path} {e}\n")


json_folder = "json"
schemas_folder = "schemas"
output_folder = "output"
lang = "hebrew"
main(json_folder=json_folder, schemas_folder=schemas_folder,
     output_folder=output_folder, lang=lang)
