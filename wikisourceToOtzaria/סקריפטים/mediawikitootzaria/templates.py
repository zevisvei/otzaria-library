import json
import re

from wikiexpand.expand import ExpansionContext
from wikiexpand.expand.templates import TemplateDict
import mwparserfromhell

from . import mediawikiapi, utils

def filter_templates(string: str, all_templates = None, template_dict = None)-> list[list[str]]|bool:
    """מחזיר את התבניות ברמה העליונה של הטקסט"""
    string_2 = []
    parsed = mwparserfromhell.parse(string)
    templates = parsed.filter_templates(parsed.RECURSE_OTHERS)
    if templates:
        for template in templates:
            if all_templates and template_dict and template.name in all_templates:
                template_str = convert_templates(str(template), template_dict)
            else:
                template_str = " ".join([str(param) for param in template.params])
            string_2.append([str(template),template.name, template_str])
        return string_2
    else:
        return False
    
def clean_comment(comment: str, all_templates: list, template_dict: TemplateDict)->str:
    """מסיר תבניות מההערה"""
    while True:
        replace = filter_templates(comment, all_templates, template_dict)
        if not replace:
            break
        for i in replace:
            rp = i[2]
            comment = comment.replace(i[0], rp)
    return comment

def remove_templates(wikitext:str, template_dict = None)-> tuple[str, dict]:
    """
    מסיר תבניות ללא פרמטרים
    תבנית עם פרמטרים התבנית מוסרת והפרמטרים נשארים
    תבנית הערה מוסרת ונכנסת הפנייה במקומה
    """
    if template_dict:
        all_templates = [i for i in template_dict.keys()]
        template_dict = templates_dict(template_dict)
    else:
        all_templates = None
        template_dict = None

    dict_comments = {}
    sup = 0
    while True:
        replace = filter_templates(wikitext, all_templates, template_dict)
        if not replace:
            break
        for i in replace:
            if i[1].strip() == "הערה":
                sup += 1
                dict_comments[sup] = clean_comment(i[2], all_templates, template_dict)
                rp = f'<sup style="color: gray;">{sup}</sup>'
            elif i[1].strip() == "ש":
                rp = "\n"
            else:
                rp = i[2]
            wikitext = wikitext.replace(i[0], rp)
    counter = 0
    sorted_dict = {}
    for num in re.findall(r'<sup style="color: gray;">(\d+)</sup>', wikitext):
        counter += 1
        wikitext = wikitext.replace(rf'<sup style="color: gray;">{num}</sup>', rf'<sup style="color: gray;">{counter}</sup>')
        sorted_dict[counter] = dict_comments[int(num)]
    return wikitext, sorted_dict

def templates_dict(dict_content: dict)-> TemplateDict:
    tpl = TemplateDict()
    for key, value in dict_content.items():
        tpl[key] = value

    return tpl

def convert_templates(mw_content: str, tpl: TemplateDict)-> str:
    ctx = ExpansionContext(templates=tpl)
    expanded_text = str(ctx.expand(mw_content))
    return expanded_text

def get_all_templates()-> None:
    import os
    base_folder = r"C:\Users\משתמש\Desktop\תבניות ויקיטקסט"
    mediawikiapi.BASE_URL = mediawikiapi.WIKISOURCE
    all_templates = mediawikiapi.get_list_by_ns(10)
    for template in all_templates:
        content = mediawikiapi.get_page_content(template)
        file_path = os.path.join(base_folder, f"{utils.sanitize_filename(template.split(":")[-1])}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(template)

def get_template_from_site(site: str, template_name: str, json_file_path: str)-> None:
    with open(json_file_path, "r", encoding="utf-8") as f:
        template = json.load(f)
    if not template.get(template_name):
        mediawikiapi.BASE_URL = site
        mediawikiapi.get_page_content(f"תבנית:{template_name}")
        template = [template_name] = ""
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=4)

