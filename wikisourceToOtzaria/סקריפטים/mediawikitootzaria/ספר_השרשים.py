import csv
import re
import html
import json

from mediawikitootzaria import mediawikiapi, mediawikitohtml, htmltootzaria, templates

dict_templates = {
    "ערך": """===<span style="font-size:165%; font-family:david; color: #660066;">{{{1}}}</span>===""",
    "צ": """{{#ifeq:{{{מרכאות|}}}|לא||&quot;}}<span class='{{{סוג|psuq2}}}' style="font-size:{{#ifeq:{{{סוג|}}}|psuq2|{{{גודל|108}}}%|103%}}">{{{תוכן|{{{1}}}}}}</span>{{#ifeq:{{{מרכאות|}}}|לא||&quot;}}""",
    "דגש-בפסוק": """{{צ|סוג=psuq2|תוכן={{{1}}} {{הדגש|{{{2}}}}} {{{3}}}}} {{#if:{{{4|}}}|<span style="font-size:80%">([[{{{4|}}}]])</span>}}""",
    "הדגש": """<span style="color: #660000;">{{{1}}}</span>""",
    "תת-ערך": """<div style="font-family: david; font-size: 130%"></span><span style="color: #660000;">
* '''{{{1}}}''' {{#if:{{{2|}}}|{{גודל גופן|2.5|({{{2}}})}}}}</div></font>""",
    "גע": """ ֽ""",
    "גודל גופן": """<font size={{{1}}}>{{{2}}}</font>""",
    "צבע גופן": """<span style="color:{{#switch:{{{1|שחור}}}|
שחור=black|
לבן=white|
אדום=red|
ארגמן=Crimson|
מג'נטה=Magenta|
ורוד=pink|
כתום=orange|
צהוב=yellow|
זהב=Gold|
זהב כהה=#C58917|
ירוק=green|
ירוק בהיר=Lime|
ירוק כהה=darkgreen|
חאקי=khaki|
חום=brown|
חום כהה=#660000|
ערמון=Maroon|
אפור=Gray|
כסף=silver|
טורקיז=turquoise|
כחול=blue|
כחול כהה=#0000A0|
תכלת=#007FFF|
אינדיגו=indigo|
שזיף=Plum|
סגול=purple|
סגול-כחול=BlueViolet|
מלכותי=BlueViolet|
#default={{{1|black}}}}};">{{{2}}}</span>"""
}

mediawikiapi.BASE_URL = mediawikiapi.WIKISOURCE


def read_order_from_csv(csv_file_path):
    with open(csv_file_path, "r", encoding="windows-1255") as csv_file:
        csv_reader = csv.reader(csv_file)
        for i in csv_reader:
            yield i


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


def main():
    sup_num = 0
    all_sup = []
    title = "ספר השרשים"
    dict_links = []
    all_content = [f"<h1>{title}</h1>", 'רד"ק']
    lines = len(all_content)
    for book in read_order_from_csv("ספר השרשים.csv"):
        h_level = 0
        book_url = book[0]
        content = mediawikiapi.get_page_content(book_url)
        for index, i in enumerate(book[1:], start=1):
            if i:
                all_content.append(f"<h{index}>{i}</h{index}>")
                lines += 1
                h_level = index + 1

        content, sup = templates.remove_templates(content)
        content = mediawikitohtml.wikitext_to_html(content, h_level)
        content = htmltootzaria.process_body_html(content, h_level)
        content = htmltootzaria.adjust_html_tag_spaces(content)
        content = re.sub(r"<קטע (?:התחלה|סוף)=[^>]+/?>", "", content)
        strip_all = content.split("\n")
        all_content.extend(strip_all)
        for index, line in enumerate(strip_all, start=lines + 1):
            find = re.findall(r'<sup style="color: gray;">(\d+)</sup>', line)
            for i in find:
                dict_links.append({
                    "line_index_1": index,
                    "heRef_2": "הערות",
                    "path_2": f"הערות על {title}.txt",
                    "line_index_2": int(i) + sup_num,
                    "Conection Type": "commentary"
                })

        lines += len(strip_all)

        for k, value in sup.items():
            v = mediawikitohtml.wikitext_to_html(value)
            v = htmltootzaria.fix_comments(v)
            v = html.unescape(v)
            all_sup.append(f'{k} {v}')
            sup_num += 1

    json_file = f"{title}_links.json"

    if dict_links:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(dict_links, f)
    with open(f"{title}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_content))
    if all_sup:
        with open(f"הערות על {title}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(all_sup))


file_path = r"ספר השרשים.csv"
# book_name = 'ספר השרשים (רד"ק)/'
# books_list = get_list(book_name)
# write_order_to_csv(file_path, books_list)
main()
