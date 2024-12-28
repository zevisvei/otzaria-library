"""מודל זה מכיל פונקציות עזרה שונות

מכיל את הפונקציות הבאות:
--------
*func:split_list_by_first_letter
*func:sanitize_filename
*func:sort_by_name
"""

from collections import defaultdict
import re
import gematriapy

def split_list_by_first_letter(input_list: list, folder: str)-> dict[str,list[str]]:
    """מחזיר מילון של הרשימה מחולקת לפי האות הראשונה כשהאות משמשת כמפתח"""
    grouped = defaultdict(list)
    for item in input_list:
        name = item.replace(folder, "")
        first_letter = name.strip()[0]
        grouped[first_letter].append(item)
    return dict(grouped)

def sanitize_filename(filename: str)->str:
    """מסיר תווים לא חוקיים לשמות תיקייה וקובץ ב windows"""
    sanitized_filename = re.sub(r'[\\/:*?<>|]', '', filename).replace('"', "''").replace('_', ' ')
    return sanitized_filename.strip()

def sort_by_name(file_name: str)->int:
    """מחזיר את הגימטריא של המחרוזת, שימושי למקרה שצריך למיין את הקבצים לפי סימנים (סימן א', ב' וכו')"""
    if file_name == "הקדמה":
        return 0
    elif file_name == "פתח דבר":
        return -1
    return gematriapy.to_number(file_name)