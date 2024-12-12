"""מודל זה מכיל פונקציות להמרת פורמט mediawiki לhtml

מכיל את הפונקציות הבאות:
--------
*func:remove_templates
*func:wikitext_to_html

שים לב:
----
יתכן שיהיה צורך בהתאמת הפונקציה remove_templates

כמו"כ הפונקציה wikitext_to_html אינה מטפלת ברשימות מקוננות ובטבלאות לע"ע
"""

import re

def remove_templates(wikitext: str)-> str:
    """מסיר תבניות מהתוכן, התבניות שצריך להסיר משתנות בין קובץ לקובץ."""
    wikitext = re.sub(r'{{מקור\|([^}]*)}}', r'\1', wikitext) 
    cleaned_text = re.sub(r'{{[^{}]*}}', '', wikitext)
    return cleaned_text

def wikitext_to_html(wikitext: str, start_heading_level = 2)-> str:
    """ממיר קידודי מדיה ויקי לhtml, עדיין צריך לטפל ברשימות מקוננות וטבלאות"""
    # Step 1: Identify and protect HTML regions
    html_tags_pattern = re.compile(r"<(pre|nowiki)[^>]*>.*?</\1[^>]*>", re.DOTALL)  # Matches complete HTML tags
    html_regions = {}
    protected_text = wikitext

    for i, match in enumerate(html_tags_pattern.finditer(wikitext)):
        key = f"__HTML_REGION_{i}__"
        html_regions[key] = match.group(0)  # Save the HTML region
        protected_text = protected_text.replace(match.group(0), key)

    #protected_text = re.sub(r'==[ ]*?הערות שוליים[ ]*?==', "", protected_text)
    protected_text = re.sub(r'^====(.*?)====\s*$',
        rf'\n<h{start_heading_level+2}>\g<1></h{start_heading_level+2}>\n', protected_text, flags=re.MULTILINE)
    protected_text = re.sub(r'^===(.*?)===\s*$',
        rf'\n<h{start_heading_level+1}>\g<1></h{start_heading_level+1}>\n', protected_text, flags=re.MULTILINE)
    protected_text = re.sub(r'^==(.*?)==\s*$',
        rf'\n<h{start_heading_level}>\g<1></h{start_heading_level}>\n', protected_text, flags=re.MULTILINE)
    
    # המרת רשימות (כוכביות) ל<ul> <li>
    protected_text = re.sub(
    r'(?m)^(?:#\s.*(?:\n|$))+',
    lambda match: f"<ol>{''.join(f'\n<li>{line.strip()[1:].strip()}</li>\n' for line in match.group().splitlines() if line.strip())}</ol>",
    protected_text
)
    protected_text = re.sub(
    r'(?m)^(?:\*\s.*(?:\n|$))+',
    lambda match: f"<ul>{''.join(f'\n<li>{line.strip()[1:].strip()}</li>\n' for line in match.group().splitlines() if line.strip())}</ul>",
    protected_text
)
    
    # המרת קישורים פנימיים
    protected_text = re.sub(r'\[\[קטגוריה:.*?\]\]', '', protected_text)
    protected_text = re.sub(r'\[\[(.*?)\|(.*?)\]\]', r'\2', protected_text)
    protected_text = re.sub(r'\[\[(.*?)\]\]', r'\1', protected_text)  # במקרה של לינק בלי |
    
    # המרת טקסט מודגש ('''text''' -> <b>text</b>)
    protected_text = re.sub(r"'''''(.*?)'''''", r'<b><i>\1</i></b>', protected_text)
    protected_text = re.sub(r"'''(.*?)'''", r"<b>\1</b>", protected_text)
    protected_text = re.sub(r"\+(.+?)\+", r"<b>\1</b>", protected_text)
    protected_text = re.sub(r"__(.*?)__", r'<u>\1</u>', protected_text)
    
    # המרת טקסט נטוי (''text'' -> <i>text</i>)
    protected_text = re.sub(r"''(.*?)''", r"<i>\1</i>", protected_text)
    
    # Convert external links
    protected_text = re.sub(r'\[(http[^\s]+) (.+?)\]', r'<a href="\1">\2</a>', protected_text)
    protected_text = re.sub(r'\[(http[^\s]+)\]', r'<a href="\1">\1</a>', protected_text)

    # Convert blockquotes
    protected_text = re.sub(r'^> (.+)', r'<blockquote>\1</blockquote>', protected_text, flags=re.MULTILINE)

    # Remove comments
    protected_text = re.sub(r'<!--.*?-->', '', protected_text, flags=re.DOTALL)

    for key, html_region in html_regions.items():
        protected_text = protected_text.replace(key, html_region)

    return protected_text