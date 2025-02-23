get_all_file = ""  # נתיב הקובץ של כל הכותרות
file_path = ""  # נתיב הקובץ של המסכת
with open(get_all_file, 'r', encoding='utf-8') as file:
    get_all_content = file.read().split("\n")
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read().split("\n")
new_list = [heading for heading in file_content if heading in get_all_content]  # רשימת הכותרות הקיימות בקובץ של כל הכותרות
#  new_list = [heading for heading in file_content if heading not in get_all_content] # רשימת הכותרות שלא קיימות בקובץ של כל הכותרות
with open(file_path, 'w', encoding='utf-8') as file:
    file.write("\n".join(new_list))
