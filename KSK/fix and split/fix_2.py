import os

"""
לא רלוונטי, כלול כבר בfix
"""

base_folder = "sefaria and more/תלמוד בבלי/ראשונים/‏‏קובץ שיטות קמאי"
for root, _, files in os.walk(base_folder):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = content.split("\n")
        content_copy = content.copy()
        for index, line in enumerate(content):
            try:
                if line.startswith("<h3>") and content[index + 1].startswith("<h2>"):
                    content_copy[index] = content[index + 1]
                    content_copy[index + 1] = line
            except IndexError:
                pass
        new = "\n".join(content_copy)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new)
