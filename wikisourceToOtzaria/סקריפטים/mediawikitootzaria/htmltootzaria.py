"""מודל זה מכיל פונקציות להתאמת html לאוצריא

מכיל את הפונקציות הבאות:
--------
*func:process_body_html
*func:adjust_html_tag_spaces
*func:extract_comments
*func:fix_comments

שים לב:
----
אופן ציון הערות שוליים משתנה בין ספר לספר, כך שיתכן ויהיה צורך לשנות את הפונקציה extract_comments
"""

from bs4 import BeautifulSoup
import re
import html

def extract_comments(html_content: str)-> tuple[str, dict]:
    """
    מחלץ את ההערות מהדף

    אופן ציון ההערות משתנה מספר לספר, כך שיתכן שיהיה צורך לשנות את הפונקציה."""
    sup = 0
    sup_content = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all("ref"):
        sup += 1
        sup_content[sup] = fix_comments(tag.text)
        tag.name = "sup"
        tag.clear()
        tag.attrs["style"] = "color: gray;"
        tag.string = str(sup)
    text = str(soup)
    return text, sup_content

def fix_comments(comment:str)-> str:
    """מסיר ירידת שורה מההערה"""
    soup = BeautifulSoup(comment, 'html.parser')
    for tag in soup.find_all(recursive=False):
        tag_str = str(tag)
        re.sub(r"([^>])(\n)(\s*[^<\s])", r"\1<br>\3", tag_str)
        tag_str = tag_str.replace("\n", " ")
        new_tag = BeautifulSoup(tag_str, "html.parser").find()
        tag.replace_with(new_tag)
    text = str(soup).strip()
    text = text.replace("\n", " ")
    return text

def adjust_html_tag_spaces(html: str)-> str:
    """
    מסיר רווחים מיותרים

    מסיר שורות ריקות
    """
    start_pattern = r'(<[^/<>]+?>)([ ]+)' 
    end_pattern = r'([ ]+)(</[^<>]+?>)' 
    while re.findall(end_pattern , html):
        html = re.sub(end_pattern, r'\2\1', html)
    while re.findall(start_pattern, html):
        html = re.sub(start_pattern , r'\2\1', html)
    html = html.replace("<p>", "").replace("</p>", "")
    html = re.sub(r'[ ]{2,}', ' ', html)
    html = "\n".join(list(map(lambda x: x.strip(), html.split("\n"))))
    html = re.sub(r'[\n\r]+', '\n', html)

    return html

def process_body_html(body_html: str, start_heading_level: int = 2)-> str:
    """
    מסיר תגים לא נתמכים

    מוודא שהתג מתחיל ונגמר באותה שורה

    מסיר תגים ריקים

    מוודא את רצף הכותרות
    """
    body_html = html.unescape(body_html)
    supported_tags = {
    "a", "abbr", "acronym", "address", "article", "aside", "audio", "b", "bdi", "bdo", "big",
    "blockquote", "br", "caption", "cite", "code", "data", "dd", "del", "details", "dfn", "dl", "dt", "em", "figcaption", "figure", "footer", "font", "h1", "h2", "h3", "h4",
    "h5", "h6", "header", "hr", "i", "iframe", "img", "ins", "kbd", "li", "main", "mark", "nav",
    "noscript", "ol", "p", "pre", "q", "rp", "rt", "ruby", "s", "samp", "section", "small",
    "strike", "strong", "sub", "sup", "div", "summary", "svg", "table", "tbody", "td", "template", "tfoot",
    "th", "thead", "time", "tr", "tt", "u", "ul", "var", "video", "math", "mrow", "msup", "msub",
    "mover", "munder", "msubsup", "moverunder", "mfrac", "mlongdiv", "msqrt", "mroot", "mi", "mn", "mo"
}
    soup = BeautifulSoup(body_html, 'html.parser')

    for tag in soup.find_all(re.compile("^h[1-6]$")):
        if tag.text.strip() == "הערות שוליים" or tag.text.strip() == "הערת שוליים":
            tag.decompose()

    # Check if there is an <h> tag in the document
    for i in range(5, start_heading_level-1, -1):
        has_h = soup.find(f'h{i}') is not None
        # Decrease heading levels
        if not has_h:
            for heading in soup.find_all(re.compile(f'^h[{i + 1}-6]$')):
                current_level = int(heading.name[1])
                new_level = current_level - 1
                heading.name = f'h{new_level}'

    for tag in soup.find_all():
        if tag.name not in supported_tags:
            tag.unwrap()

    for tag in soup.find_all():
        if not tag.get_text(strip=True) and tag.name != "br":
            tag.decompose() 
    
    for tag in soup.find_all(recursive=False):
        tag_str = str(tag)
        re.sub(r"([^>])(\n)(\s*[^<\s])", r"\1<br>\3", tag_str)
        tag_str = tag_str.replace("\n", " ")
        new_tag = BeautifulSoup(tag_str, "html.parser").find()
        tag.replace_with(new_tag)

    text = str(soup).strip()

    return text