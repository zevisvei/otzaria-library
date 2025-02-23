import os


root_folder = "MoreBooks/תלמוד בבלי/ראשונים/‏‏קובץ שיטות קמאי"

for root, _, files in os.walk(root_folder):
    for file in files:
        print(file)
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        print(len(lines))
        new_content = [line for line in lines if line.strip()]
        print(len(new_content))
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_content))
