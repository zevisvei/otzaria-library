import json

from otzaria.utils import recursive_register_categories

with open('old.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
new_data = recursive_register_categories(data)
with open('toc.json', 'w', encoding='utf-8') as file:
    json.dump(new_data, file, ensure_ascii=False, indent=2)
