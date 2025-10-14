import json
import os

import pandas as pd
from otzaria.get_from_export import Book
from otzaria.utils import footnotes, sanitize_filename


def read_file(file_path: str) -> set[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return set(f.read().split("\n"))


def recursive_register_categories(
    index: list | dict,
    data: list[dict[str, str | list[str]]] | None = None,
    tree: list[str] | None = None,
) -> dict[str, int]:
    if tree is None:
        tree = []
    if data is None:
        data = {}
    if isinstance(index, list):
        for item in index:
            recursive_register_categories(item, data, tree)
    elif isinstance(index, dict):
        if index.get("contents"):
            tree.append(index["heCategory"])
            for item in index["contents"]:
                recursive_register_categories(item, data, tree)
            tree.pop()
        if index.get("title") and "order" in index:
            data[index["title"]] = index["order"]
    return data


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
                    if metadata["title"] in files_black_list or any(author in authors_black_list for author in metadata["heAuthors"]):
                        continue
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
                    metadata["order"] = toc_content.get(metadata.get("enTitle"))
                    all_metadata[output_file_name] = metadata
                    # df = pd.DataFrame(refs)
                    for entry in refs:
                        entry["path"] = title
                    refs_list.extend(refs)
                    # df.to_csv(f"{output_file_name}.csv", index=False)
                    if all_footnotes:
                        footnotes_file = os.path.join(output_folder, *output_path, f"הערות על {title}.txt")
                        with open(footnotes_file, 'w', encoding='utf-8') as file:
                            file.write("\n".join(all_footnotes))
                        json_file = os.path.join(links_path, f"{title}_links.json")
                        with open(json_file, "w", encoding="utf-8") as file:
                            json.dump(dict_links, file)
                except Exception as e:
                    with open("error.txt", "a", encoding="utf-8") as f:
                        f.write(f"{file_path} {e}\n")


toc_file_path = r"F:\Sefaria-Export\table_of_contents.json"
with open(toc_file_path, "r", encoding="utf-8") as f:
    toc = json.load(f)
toc_content = recursive_register_categories(toc)
all_metadata = {}
json_folder = r"F:\Sefaria-Export\json"
schemas_folder = r"F:\Sefaria-Export\schemas"
files_black_list_file_path = r""
authors_black_files_list_file_path = r""
files_black_list = read_file(files_black_list_file_path)
authors_black_list = read_file(authors_black_files_list_file_path)
# output_folder = os.path.join("אוצריא", "אוצריא")
output_folder = r"C:\Users\User\Desktop\אוצריא\אוצריא"
os.makedirs(output_folder, exist_ok=True)
# links_path = os.path.join("אוצריא", "links")
links_path = r"C:\Users\User\Desktop\אוצריא\links"
os.makedirs(links_path, exist_ok=True)
lang = "hebrew"
refs_list = []
main(json_folder=json_folder, schemas_folder=schemas_folder,
     output_folder=output_folder, lang=lang)
df = pd.DataFrame(refs_list)
df.to_csv(r"C:\Users\User\Desktop\אוצריא\refs_all.csv", index=False)
with open(r"C:\Users\User\Desktop\אוצריא\books_metadata.json", "w", encoding="utf-8") as f:
    json.dump(all_metadata, f, ensure_ascii=False, indent=4)
