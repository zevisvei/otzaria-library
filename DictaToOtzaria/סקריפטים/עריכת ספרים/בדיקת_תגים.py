from bs4 import BeautifulSoup
import gematriapy
import re
import tkinter as tk
from tkinter import filedialog

def fix(html_content, acton, re_start, re_end, gershayim):
    soup = BeautifulSoup(html_content, 'html.parser')
    tags = soup.find_all("h")
    for tag in tags:
        tag_str = tag.string.split()
        first_word = tag_str[0]
        tag_num = tag_str[1]
        if gershayim:
            if gematriapy.to_number(tag_num) <= 9:
                if not tag_num.endswith("'"):
                    tag_num += "'"
            else:
                if tag_num[-2] != '"':
                    tag_num = f'{tag_num[:-1]}"{tag_num[-1]}'

def process_html(html_content, re_start, re_end, gershayim):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # קומפילציה של תבנית Regex לפי קלט המשתמש
    if re_start and re_end:
        pattern = re.compile(f"^{re_start}.+{re_end}$")
    elif re_start:
        pattern = re.compile(f"^{re_start}.+['א-ת]$")
    elif re_end:
        pattern = re.compile(f"^[א-ת].+{re_end}$")
    else:
        pattern = re.compile(r"^[א-ת].+[א-ת']$")
    
    unmatched_regex = []
    unmatched_tags = []
    
    # מעבר על תגי כותרות מ-h2 עד h6
    for i in range(2, 7):
        tags = soup.find_all(f"h{i}")
        
        # בדיקה אם נמצאו תגים
        if not tags:
            unmatched_tags.append(f"No tags found for h{i}")
            continue
        
        # עיבוד כל התגים למעט האחרון
        for index in range(len(tags) - 1):
            current_tag = tags[index].string or ""
            next_tag = tags[index + 1].string or ""
            
            # וידוא שהמחרוזות של התגים אינן ריקות
            if not current_tag or not next_tag:
                continue
            
            # בהנחה שהפיצול מבוצע על רווח כדי לקבל את הכותרות
            current_heading_parts = current_tag.split()
            next_heading_parts = next_tag.split()
            
            if len(current_heading_parts) > 1:
                current_heading = current_heading_parts[1]
            else:
                current_heading = current_tag
            
            if len(next_heading_parts) > 1:
                next_heading = next_heading_parts[1]
            else:
                next_heading = next_tag
            
            # בדיקה אם התג הנוכחי תואם את התבנית
            if not re.match(pattern, current_tag):
                unmatched_regex.append(current_tag)
            
            # בדיקה עבור תנאי גרשיים
            if gershayim:
                if gematriapy.to_number(current_heading) <= 9:
                    if "'" not in current_heading:
                        unmatched_tags.append(current_heading)
                else:
                    if '"' not in current_heading:
                        unmatched_tags.append(current_heading)
            else:
                if "'" in current_heading or '"' in current_heading:
                    unmatched_tags.append(current_heading)
            
            # בדיקה אם הכותרות הן ברצף
            if not gematriapy.to_number(current_heading) + 1 == gematriapy.to_number(next_heading):
                unmatched_tags.append(f"תג נוכחי {current_tag} תג הבא {next_tag}")

        # עיבוד התג האחרון
        last_tag = tags[-1].string or ""
        if last_tag and not re.match(pattern, last_tag):
            unmatched_regex.append(last_tag)
        
        last_heading_parts = last_tag.split()
        if len(last_heading_parts) > 1:
            last_heading = last_heading_parts[1]
        else:
            last_heading = last_tag
            
        if gershayim:    
            if gematriapy.to_number(last_heading) <= 9:
                if "'" not in last_heading:
                    unmatched_tags.append(last_heading)
            else:
                if '"' not in last_heading:
                    unmatched_tags.append(last_heading)
        else:
            if "'" in last_heading or '"' in last_heading:
                unmatched_tags.append(last_heading)
    
    return unmatched_regex, unmatched_tags

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("txt files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        re_start = re_start_entry.get()
        re_end = re_end_entry.get()
        gershayim = gershayim_var.get()
        unmatched_regex, unmatched_tags = process_html(html_content, re_start, re_end, gershayim)
        unmatched_regex_text.delete(1.0, tk.END)
        unmatched_tags_text.delete(1.0, tk.END)
        unmatched_regex_text.insert(tk.END, "\n".join(unmatched_regex))
        unmatched_tags_text.insert(tk.END, "\n".join(unmatched_tags))

# יצירת החלון הראשי
root = tk.Tk()
root.title("בודק הספרים האוטומטי")

# ערכי ברירת מחדל
default_re_start = ""
default_re_end = ""
default_gershayim = False  # הכפתור 'כולל גרשיים' לא מסומן בברירת מחדל

# יצירה ומיקום של הווידג'טים
tk.Label(root, text="תו בתחילת הכותרת").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
re_start_entry = tk.Entry(root)
re_start_entry.insert(0, default_re_start)  # קביעת ערך ברירת מחדל
re_start_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="תו בסוף הכותרת").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
re_end_entry = tk.Entry(root)
re_end_entry.insert(0, default_re_end)  # קביעת ערך ברירת מחדל
re_end_entry.grid(row=1, column=1, padx=10, pady=5)

gershayim_var = tk.BooleanVar(value=default_gershayim)  # קביעת ערך ברירת מחדל
tk.Checkbutton(root, text="כולל גרשיים", variable=gershayim_var).grid(row=2, columnspan=2, padx=10, pady=5)

tk.Button(root, text="בחר קובץ", command=open_file).grid(row=3, columnspan=2, padx=10, pady=10)

# יצירת ווידג'טים לטקסט עבור תוצאות
tk.Label(root, text="שאינן תואמות Regex תוצאות").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
unmatched_regex_text = tk.Text(root, wrap=tk.WORD, height=10, width=50)
unmatched_regex_text.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

tk.Label(root, text="תגים לא תואמים").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
unmatched_tags_text = tk.Text(root, wrap=tk.WORD, height=10, width=50)
unmatched_tags_text.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

# הפעלת לולאת האירועים של ה-GUI
root.mainloop()
