import json

toc_file_path = r"C:\Users\User\Downloads\table_of_contents.json"
folder_metadata_file_path = r"C:\Users\User\Downloads\folder_metadata.json"


def recursive_register_categories(category: list | dict, data: list | None = None) -> list[dict]:
    if data is None:
        data = []
    if isinstance(category, list):
        for item in category:
            recursive_register_categories(item, data)
    if 'contents' in category:
        for item in category['contents']:
            recursive_register_categories(item, data)
    if 'heCategory' in category:
        he_category = category['heCategory']
        he_short_desc = category['heShortDesc'] if 'heShortDesc' in category else None
        he_desc = category['heDesc'] if 'heDesc' in category else None
        order = category['order'] if 'order' in category else None
        data.append({"title": he_category, 'heDesc': he_desc, "heShortDesc": he_short_desc, "order": order})
    return data


with open(toc_file_path, 'r', encoding='utf-8') as f:
    toc = json.load(f)
data = recursive_register_categories(toc)
with open(folder_metadata_file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
