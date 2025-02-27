"""
This module contains functions for adjusting HTML for To otzaria.

It includes the following functions:
--------
* func: process_body_html
* func: adjust_html_tag_spaces
* func: extract_comments
* func: fix_comments

Note:
----
The method of marking footnotes varies from book to book, so it may be necessary to change the extract_comments function.
"""

from bs4 import BeautifulSoup
import re
import html


def extract_comments(html_content: str) -> tuple[str, dict]:
    """
    Extracts comments from the page.

    The method of marking comments varies from book to book, so it may be necessary to change the function.

    Args:
        html_content (str): The HTML content from which to extract comments.

    Returns:
        tuple: A tuple containing the modified HTML content and a dictionary of extracted comments.
    """
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


def fix_comments(comment: str) -> str:
    """
    Removes line breaks from the comment.

    Args:
        comment (str): The comment text to be fixed.

    Returns:
        str: The fixed comment text.
    """
    soup = BeautifulSoup(comment, 'html.parser')
    for tag in soup.find_all(recursive=False):
        tag_str = str(tag)
        re.sub(r"([^>])(\n)(\s*[^<\s])", r"\1<br>\3", tag_str)
        tag_str = tag_str.replace("\n", " ")
        new_tag = BeautifulSoup(tag_str, "html.parser").find()
        tag.replace_with(new_tag)
    text = str(soup).strip()
    text = " ".join(list(map(lambda x: x.strip(), text.split("\n"))))
    text = re.sub(r'[\n\r]+', ' ', text)
    text = re.sub(r'[ ]{2,}', ' ', text)
    return text


def adjust_html_tag_spaces(html: str) -> str:
    """
    Removes unnecessary spaces and empty lines from HTML.

    Args:
        html (str): The HTML content to be adjusted.

    Returns:
        str: The adjusted HTML content.
    """
    start_pattern = r'(<[^/<>]+?>)([ ]+)'
    end_pattern = r'([ ]+)(</[^<>]+?>)'
    while re.findall(end_pattern, html):
        html = re.sub(end_pattern, r'\2\1', html)
    while re.findall(start_pattern, html):
        html = re.sub(start_pattern, r'\2\1', html)
    html = html.replace("<p>", "").replace("</p>", "")
    html = re.sub(r'[ ]{2,}', ' ', html)
    html = "\n".join(list(map(lambda x: x.strip(), html.split("\n"))))
    html = re.sub(r'[\n\r]+', '\n', html)

    return html


def process_body_html(body_html: str, start_heading_level: int = 2) -> str:
    """
    Processes the body HTML by removing unsupported tags, ensuring tags start and end on the same line,
    removing empty tags, and ensuring the sequence of headings.

    Args:
        body_html (str): The body HTML content to be processed.
        start_heading_level (int, optional): The starting heading level. Defaults to 2.

    Returns:
        str: The processed body HTML content.
    """
    body_html = html.unescape(body_html)
    supported_tags = {
        "a", "abbr", "acronym", "address", "article", "aside", "audio", "b", "bdi", "bdo", "big",
        "blockquote", "br", "caption", "cite", "code", "data", "dd", "del", "details", "dfn", "dl", "dt", "em", "figcaption", "figure", "footer", "font", "h1", "h2", "h3", "h4",
        "h5", "h6", "header", "hr", "i", "iframe", "img", "ins", "kbd", "li", "main", "mark", "nav",
        "noscript", "ol", "p", "pre", "q", "rp", "rt", "ruby", "s", "samp", "section", "small",
        "strike", "strong", "sub", "sup", "div", "summary", "svg", "table", "tbody", "td", "template", "tfoot",
        "th", "thead", "time", "tr", "tt", "u", "ul", "var", "video", "math", "mrow", "msup", "msub",
        "mover", "munder", "msubsup", "moverunder", "mfrac", "mlongdiv", "msqrt", "mroot", "mi", "mn", "mo", "span"
    }
    soup = BeautifulSoup(body_html, 'html.parser')

    for tag in soup.find_all(re.compile("^h[1-6]$")):
        if tag.text.strip() == "הערות שוליים" or tag.text.strip() == "הערת שוליים":
            tag.decompose()

    # Check if there is an <h> tag in the document
    for i in range(5, start_heading_level - 1, -1):
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
    text = html.unescape(text)

    return text
