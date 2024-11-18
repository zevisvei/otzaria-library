import tkinter as tk
from tkinter import filedialog, messagebox
import re

def process_file(filename, replace_with):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.readlines()
    except FileNotFoundError:
        messagebox.showerror("קלט לא תקין", "הקובץ לא נמצא")
        return

    updated_content = []
    changes_made = False

    i = 0
    while i < len(content):
        line = content[i]
        match = re.match(r'<h([2-9])>(דף \S+)</h\1>', line)
        if match:
            level = match.group(1)
            title = match.group(2)
            next_line_index = i + 1
            if next_line_index < len(content):
                next_line = content[next_line_index].strip()

                # תבנית שמזהה את המילים והתגיות השונות
                pattern = r'(<[a-z]+>)?(ע"?[א-ב]|עמוד [א-ב])[.,:()\[\]\'"״׳]?(</[a-z]+>)?\s?'
                match_next_line = re.match(pattern, next_line)

                if match_next_line:
                    changes_made = True

                    # קביעה האם להחליף לנקודה או לנקודותיים
                    if replace_with == 'נקודה ונקודותיים':
                        if "א" in match_next_line.group(2):
                            new_title = f'<h{level}>{title}.</h{level}>\n'
                        else:
                            new_title = f'<h{level}>{title}:</h{level}>\n'
                    elif replace_with == 'ע"א וע"ב':
                        suffix = "ע\"א" if "א" in match_next_line.group(2) else "ע\"ב"
                        new_title = f'<h{level}>{title} {suffix}</h{level}>\n'

                    updated_content.append(new_title)

                    # מחיקת המילים והסימנים בשורה הבאה והשארת התוכן הנותר
                    modified_next_line = re.sub(pattern, '', next_line).strip()
                    if modified_next_line != '':
                        updated_content.append(modified_next_line + '\n')

                    i += 1  # דילוג על השורה הבאה כיוון שהיא טופלה כבר
                else:
                    updated_content.append(line)
            else:
                updated_content.append(line)
        else:
            updated_content.append(line)
        i += 1

    if changes_made:
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(updated_content)
        messagebox.showinfo("!מזל טוב", "החלפה הושלמה בהצלחה")
    else:
        messagebox.showinfo("!שים לב", "אין מה להחליף בקובץ זה")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("HTML files", "*.html")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def run_script():
    file_path = file_entry.get()
    if file_path:
        replace_with = replace_option.get()
        process_file(file_path, replace_with)
    else:
        messagebox.showwarning("קלט לא תקין", "אנא בחר או הזן נתיב קובץ")

root = tk.Tk()
root.title("הוספת מספר עמוד בכותרת הדף")
replace_option = tk.StringVar(value="נקודה ונקודותיים")

# הודעת הסבר למשתמש
label = tk.Label(root, text="הסבר על פעולת התוכנה\n'התוכנה מחליפה בקובץ בכל מקום שיש כותרת 'דף\n:ובתחילת שורה הבאה כתוב: ע\"א או ע\"ב, כגון\n\n </h2>דף ב<h2> \nע\"א [טקסט כלשהו]\n\n:הרצת התוכנה תעדכן את הכותרת ל\n\n</h2>.דף ב<h2>\n[טקסט כלשהו]")
label.grid(row=0, columnspan=3, sticky="n", pady=10)

tk.Label(root, text=":נתיב קובץ", anchor='e').grid(row=1, column=1, columnspan=3, sticky="e", padx=20)
file_entry = tk.Entry(root, relief="groove", bd=2, width=45)
file_entry.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
tk.Button(root, text="בחר קובץ", command=browse_file, anchor='n', relief="groove").grid(row=1, columnspan=3, pady=5, padx=20, sticky="w")

# הודעת הסבר למשתמש
label = tk.Label(root, text=":בחר את סוג ההחלפה", anchor='e')
label.grid(row=2, columnspan=3, pady=30, sticky="n")

tk.Radiobutton(root, text="החלף לנקודה ונקודותיים", variable=replace_option, value="נקודה ונקודותיים", anchor="e", relief="groove", padx=10).grid(row=3, column=1, sticky="n", padx=20)
# הסבר לדוגמא
example1 = tk.Label(root, text=":לדוגמא\n:דף ב.   דף ב:   דף ג.   דף ג\nוכן הלאה")
example1.grid(row=4, column=1, pady=5, sticky="n")

tk.Radiobutton(root, text="החלף לע\"א וע\"ב", variable=replace_option, value="ע\"א וע\"ב", anchor="e", relief="groove", padx=10).grid(row=3, column=0, sticky="n")
# הסבר לדוגמא
example2 = tk.Label(root, text=":לדוגמא\nדף ב ע\"א   דף ב ע\"ב   דף ג ע\"א   דף ג ע\"ב\nוכן הלאה")
example2.grid(row=4, column=0, pady=5, padx=20, sticky="n")

tk.Button(root, text="הרץ כעת", command=run_script, font=("Arial", 13), anchor='n', relief="groove").grid(row=5, columnspan=3, pady=20, sticky="n")

root.mainloop()
