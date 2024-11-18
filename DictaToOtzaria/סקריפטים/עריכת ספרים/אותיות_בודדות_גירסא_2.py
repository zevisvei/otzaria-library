import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  
from pyluach import gematria

def ot(text, end):
    # פונקציה לבדיקת התאמה של טקסט לאותיות בגימטריה ללא גרשיים
    remove = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", ".", "״", "‚", "”", "’"]
    aa = ["ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"]
    bb = ["ם", "ן", "ץ", "ף", "ך"]
    cc = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "ששי", "שביעי", "שמיני", "תשיעי", "עשירי", "חי", "טל", "דש", "שדמ", "ער", "שדם", "תשדם", "תשדמ", "ערה"]
    append_list = []
    for i in aa:
        for ot_sofit in bb:
            append_list.append(i + ot_sofit)
                       
    # הסרת תווים לא רצויים מהטקסט
    for tage in remove:
        text = text.replace(tage, "")
    withaute_gershayim = [gematria._num_to_str(i, thousands=False, withgershayim=False) for i in range(1, end)] + bb + cc + append_list
    return text in withaute_gershayim
        
def strip_html_tages(text, ignore):
    # פונקציה להסרת תגים מתוך טקסט לפי רשימת התעלמות
    for tage in ignore:
        text = text.replace(tage, "")
    return text
        
def main(book_file, finde, end, level_num, ignore, start, remove):
    # פונקציה עיקרית לטיפול בקובץ הטקסט לפי פרמטרים שניתנו
    with open(book_file, "r", encoding="utf-8") as file_input:
        content = file_input.read().splitlines()
        all_lines = content[0:1]
        for line in content[1:]:
            words = line.split()
            try:
                # בדיקת התאמה לכותרת ושמירה אם יש צורך
                if strip_html_tages(words[0], ignore).endswith(finde) and strip_html_tages(words[0], ignore).startswith(start) and ot(words[0], end):
                    heading_line = f"<h{level_num}>{strip_html_tages(words[0], remove)}</h{level_num}>"
                    all_lines.append(heading_line)
                    if words[1:]:
                        fix_2 = " ".join(words[1:])
                        all_lines.append(fix_2)
                else:
                    all_lines.append(line)
            except IndexError:
                all_lines.append(line)
    join_lines = "\n".join(all_lines)
    with open(book_file, "w", encoding="utf-8") as autpoot:
        autpoot.write(join_lines)
              
def browse_file():
    # פונקציה לפתיחת סייר קבצים לבחירת קובץ
    filename = filedialog.askopenfilename(filetypes=[("קבצי טקסט", "*.txt"), ("כל הפורמטים", "*.*")])
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)
               
def run_script():
    # פונקציה להפעלת הסקריפט עם הערכים שנבחרו בממשק הגרפי
    book_file = file_entry.get()
    finde = finde_var.get()
    remove =["<b>", "</b>"] + remove_entry.get().split()
    ignore = ignore_entry.get().split()
    start = start_var.get()
    is_bold_checked = bold_var.get()
    if is_bold_checked:
        finde += "</b>"
        start = "<b>" + start
    else:
        ignore += ["<b>", "</b>"]
                
    try:
        end = int(end_var.get())
        level_num = int(level_var.get())
    except ValueError:
        messagebox.showerror("קלט לא תקין", "אנא הזן 'מספר סימן מקסימלי' ו'רמת כותרת' תקינים")
        return
            
    if not book_file:
        messagebox.showerror("קלט לא תקין", "אנא בחר קובץ")
        return
        
    try:
        main(book_file, finde, end + 1, level_num , ignore, start, remove)
        messagebox.showinfo("!מזל טוב", "!הסקריפט רץ בהצלחה")
    except Exception as e:
        messagebox.showerror("שגיאה", f"אירעה שגיאה: {e}")
        
# הגדרת הממשק הגרפי (GUI)
root = tk.Tk()
root.title("כותרות לאותיות בודדות לאוצריא")

# תווית ושדה להזנת נתיב קובץ
tk.Label(root, text=":נתיב קובץ", anchor='e').grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
file_entry = tk.Entry(root, relief="groove", bd=2, width=50, justify=tk.RIGHT)
file_entry.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(root, relief="groove", bd=2, text="עיון", command=browse_file)
browse_button.grid(row=0, column=0, padx=10, pady=5)

# תווית ושדה להזנת תו בסוף האות
tk.Label(root, text=":תו בסוף האות", anchor='e').grid(row=1, column=2, padx=10, pady=5, sticky=tk.E)
finde_var = tk.StringVar(root)
finde_choices = [".", ",", "'", "',", "'.", "]", ")", "']", "')", "].", ").", "],", "),", "'),", "').", "'],", "']."]
finde_menu = ttk.Combobox(root, textvariable=finde_var, values=finde_choices, width=3, justify=tk.RIGHT)
finde_menu.grid(row=1, column=1, padx=10, pady=5)

# תווית ושדה להזנת תו בתחילת האות
tk.Label(root, text=":תו בתחילת האות", anchor='e').grid(row=2, column=2, padx=10, pady=5, sticky=tk.E)
start_var = tk.StringVar(root)
start_choices = ["(", "["]
start_menu = ttk.Combobox(root, textvariable=start_var, values=start_choices, width=3, justify=tk.RIGHT)
start_menu.grid(row=2, column=1, padx=10, pady=5)

# הודעת הסבר למשתמש
tk.Label(root, text="-->  שים לב!  תווי הסוגריים מוצגים הפוך, וכן סדר הכתיבה הוא משמאל לימין, אך הכל פועל כמצופה  <--").grid(row=3, column=0, columnspan=3, padx=10, pady=5)

tk.Label(root, text=":התעלם מהתווים הבאים", anchor='e').grid(row=4, column=2, padx=10, pady=5, sticky=tk.E)
ignore_entry = tk.Entry(root, relief="groove", bd=2, width=50, justify=tk.RIGHT)
ignore_entry.grid(row=4, column=1, padx=10, pady=5)
ignore_entry.insert(0, """<big> </big> " """)

# תווית ושדה להסרת תווים
tk.Label(root, text=":הסר את התווים הבאים", anchor='e').grid(row=5, column=2, padx=10, pady=5, sticky=tk.E)
remove_entry = tk.Entry(root, relief="groove", bd=2, width=50, justify=tk.RIGHT)
remove_entry.grid(row=5, column=1, padx=10, pady=5)
remove_entry.insert(0, """<b> </b> <big> </big> , : " ' . ( ) [ ] { }""")

# תווית ותיבת בחירה למספר סימן מקסימלי
tk.Label(root, text=":מספר סימן מקסימלי", anchor='e').grid(row=6, column=2, padx=10, pady=5, sticky=tk.E)
end_var = tk.StringVar(root)
end_choices = [str(i) for i in range(1, 999)]
end_menu = ttk.Combobox(root, textvariable=end_var, values=end_choices, width=3, justify=tk.RIGHT)
end_menu.grid(row=6, column=1, padx=10, pady=5)
end_var.set("999")

# תווית ותיבת בחירה לרמת כותרת
tk.Label(root, text=":רמת כותרת", anchor='e').grid(row=7, column=2, padx=10, pady=5, sticky=tk.E)
level_var = tk.StringVar(root)
level_choices = [str(i) for i in range(1, 9)]
level_menu = ttk.Combobox(root, textvariable=level_var, values=level_choices, width=1, justify=tk.RIGHT)
level_menu.grid(row=7, column=1, padx=10, pady=5)
level_var.set("3")

# תיבת סימון לחיפוש עם תווי הדגשה בלבד
bold_var = tk.BooleanVar()
bold_var.set(True)  # הגדרה ברירת מחדל לתיבה מסומנת
bold_check = tk.Checkbutton(root, relief="groove", bd=2, text="לחפש עם תווי הדגשה בלבד", variable=bold_var)
bold_check.grid(row=8, column=1, pady=10)

# כפתור להפעלת הסקריפט
run_button = tk.Button(root, relief="groove", bd=2, text="הפעל", command=run_script)
run_button.grid(row=9, column=1, pady=10)

root.mainloop()
