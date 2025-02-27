import csv

from mediawikitootzaria import mediawikiapi

mediawikiapi.BASE_URL = mediawikiapi.WIKISOURCE


def write_order_to_csv(csv_file_path, books_list):
    with open(csv_file_path, "w", newline="", encoding="windows-1255") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(books_list)


def get_list(book_name):
    list_all = []
    all_pages = mediawikiapi.get_list_by_name(book_name)
    print(all_pages)
    for page in all_pages:
        page_split = page.split("/")
        list_all.append([page, *page_split])
    return list_all


file_path = "ספר השרשים.csv"
book_name = 'ספר השרשים (רד"ק)/'
books_list = get_list(book_name)
write_order_to_csv(file_path, books_list)
