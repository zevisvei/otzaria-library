import os
import shutil


surce_folder = "sefariaToOtzaria/ספרים/לא ממויין/תשפה/שבט"
target_folder = "sefariaToOtzaria/ספרים/אוצריא"
dict_surce = {}
for root, dirs, files in os.walk(surce_folder):
    for file in files:
        if file.endswith(".txt"):
            dict_surce[file] = os.path.join(root, file)
for root, dirs, files in os.walk(target_folder):
    for file in files:
        if file.endswith(".txt"):
            if file in dict_surce:
                shutil.copy(dict_surce[file], os.path.join(root, file))
                print(file)
