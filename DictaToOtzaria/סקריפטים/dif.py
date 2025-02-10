import csv
import os


def read_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return list(reader)


def write_csv(file, data):
    list_all = ['displayName', 'printYear', 'author', 'printLocation', 'category',
                'source', 'textFileURL', 'nikudMetegFileURL', 'OCRDataURL', 'ocrFeDir',
                'displayNameEnglish', 'authorEnglish', 'categoryEnglish', 'printLocationEnglish',
                "underwentBerelUnflagging", 'fileName', 'notHumanReviewed']
    with open(file, "w", encoding="utf-8", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(list_all)
        for i in data:
            csv_writer.writerow(i)


def dict_csv(data):
    dict_all = {}
    for i in data:
        dict_all[i[8]] = i[0:8] + i[9:]
    return dict_all


def new_vs_old(dict_1, dict_2):
    list_all = []
    list_2 = []
    for key, value in dict_1.items():
        old = dict_2.get(key)
        if old:
            if old == value:
                continue
            list_dif = [key]
            for index, i in enumerate(value):
                if i == old[index]:
                    list_dif.append("")
                else:
                    list_dif.append(i)
            list_all.append(list_dif)
        else:
            list_2.append([key] + value)
    return list_all, list_2


def main(file_path: str) -> None:
    old_list = read_csv("old.csv")
    new_list = read_csv("list.csv")
    if old_list != new_list:
        dict_new = dict_csv(new_list)
        dict_old = dict_csv(old_list)
        not_in_old, not_in_old_2 = new_vs_old(dict_new, dict_old)
        not_in_new, not_in_new_2 = new_vs_old(dict_old, dict_new)
        write_csv(os.path.join(file_path, "not_in_old.csv"), not_in_old)
        write_csv(os.path.join(file_path, "not_in_new.csv"), not_in_new)
        write_csv(os.path.join(file_path, "not_in_old_2.csv"), not_in_old_2)
        write_csv(os.path.join(file_path, "not_in_new_2.csv"), not_in_new_2)
