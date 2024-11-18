import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import re

# פונקציה שמסירה תגים מסביב ל"עמוד ב" ומחליפה אותם בתגי כותרת
def strip_and_replace(text, header_level, counter):
    # ביטוי רגולרי שמזהה את "עמוד ב" ומסיר תגים מסביב, תוך זיהוי המילים עם או בלי תגים מסביב
    match_pattern = re.compile(
        r"^\s*(?!<h\d>)(?:<[^>]+>\s*)*(?:שם\s*)?(?:<[^>]+>\s*)*(בגמרא|גמרא|גמ\'|בגמ\')?\s*(?:<[^>]+>\s*)*(עמוד|ע)(?:<[^>]+>\s*)*[\"'’]?\s*[\"'’]?(?:<[^>]+>\s*)*ב(?:<[^>]+>\s*)*(.*)", re.IGNORECASE)

    # פונקציה מחליפה שתיצור את תגי הכותרת
    def replace_function(match):
        # יצירת תג הכותרת "עמוד ב"
        header = f"<h{header_level}>עמוד ב</h{header_level}>"
        rest_of_line = match.group(3).strip()  # הטקסט אחרי "עמוד ב"

        # שמירה על תגים אם קיימים סביב "גמרא", "בגמרא", "גמ'", "בגמ'"
        gmarah_text = match.group(1).strip() if match.group(1) else ""
        gmarah_tags_match = re.search(r'(<[^>]+>)?\s*(בגמרא|גמרא|גמ\'|בגמ\')\s*(</[^>]+>)?', match.group(0))

        # בדיקה אם נמצאו תגים סביב "גמרא"
        if gmarah_tags_match:
            gmarah_prefix = gmarah_tags_match.group(1) if gmarah_tags_match.group(1) else ""
            gmarah_suffix = gmarah_tags_match.group(3) if gmarah_tags_match.group(3) else ""
            gmarah_text = f"{gmarah_prefix}{gmarah_tags_match.group(2)}{gmarah_suffix}"

        # הסרת תווים לא רצויים (כגון ' . , : ) ]) אחרי הכותרת יחד עם התגים שלהם
        rest_of_line = re.sub(r"(?:<[^>]+>\s*)*['.,:\)\]]+(?:<[^>]+>\s*)*", "", rest_of_line)

        # אם יש "גמרא" או המילים האחרות - נשאיר אותם באותה שורה עם שאר הטקסט
        if gmarah_text:
            counter[0] += 1  # עדכון המונה
            return f"{header}\n{gmarah_text} {rest_of_line}\n" if rest_of_line else f"{header}\n{gmarah_text}\n"
        
        # אם אין "גמרא", יוצרים את הכותרת עם שאר השורה אחרי "עמוד ב"
        counter[0] += 1  # עדכון המונה
        return f"{header}\n{rest_of_line}\n" if rest_of_line else f"{header}\n"

    # ביטוי שמזהה אם כבר יש תג כותרת
    header_tag_pattern = re.compile(r"<h\d>.*?</h\d>", re.IGNORECASE)

    # אם כבר יש תג כותרת, לא נבצע שום החלפה
    if header_tag_pattern.search(text):
        return text

    # ביצוע ההחלפה של הכותרת "עמוד ב"
    new_text = match_pattern.sub(replace_function, text)

    # הסרת שורות ריקות כפולות
    new_text = re.sub(r'\n\s*\n', '\n', new_text)

    return new_text

# פונקציה שמעבדת את הקובץ ומבצעת את השינויים
def process_file(file_path, header_level):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    counter = [0]  # מונה כותרות

    for line in lines:
        new_line = strip_and_replace(line, header_level, counter)
        new_lines.append(new_line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

    # הצגת הודעה מתאימה לפי כמות הכותרות שנוצרו
    if counter[0] == 0:
        messagebox.showinfo("!שים לב", "לא נמצא מה להחליף")
    else:
        messagebox.showinfo("!מזל טוב", f"נוספו {counter[0]} כותרות לקובץ.")

# פונקציה לבחירת קובץ
def select_file():
    file_path = filedialog.askopenfilename(
        title="בחר קובץ", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# פונקציה להרצת הסקריפט
def run_script():
    file_path = file_entry.get()

    try:
        header_level = int(header_var.get())  # המרה למספר שלם
    except ValueError:
        messagebox.showwarning("שגיאה", "רמת הכותרת צריכה להיות מספר בין 2 ל-9")
        return    

    if not file_path:
        messagebox.showwarning("קלט לא תקין", "בחר קובץ תחילה")
        return
    
    if header_level < 2 or header_level > 9:
        messagebox.showwarning("שגיאה", "בחר רמת כותרת בין 2 ל-9")
        return
    
    process_file(file_path, header_level)

# יצירת ממשק גרפי
root = tk.Tk()
root.title("'יצירת כותרות ל'עמוד ב")
root.configure(bg='lightyellow')

label = tk.Label(root, text="'התוכנה יוצרת כותרת בכל מקום בקובץ שכתוב בתחילת שורה - 'עמוד ב', או 'ע\"ב\nבאם כתוב את המילה 'שם' לפני המילים הנ\"ל, המילה 'שם' נמחקת\n'ובאם כתוב את המילה 'גמרא' לפני המילים 'עמוד ב' או 'ע\"ב\nהתוכנה תעביר את המילה 'גמרא' לתחילת השורה שאחרי הכותרת\n!בזכות כללים אלו בעז\"ה לא נפספס שום כותרת", bg='lightyellow')
label.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=15)

# שדה לבחירת קובץ
tk.Label(root, text=":נתיב קובץ", bg='lightyellow').grid(row=1, column=2, padx=20, pady=5, sticky="e")
file_entry = tk.Entry(root, relief="groove", bd=2, width=41)
file_entry.grid(row=1, column=1, columnspan=3, padx=0, pady=5, sticky="w")
tk.Button(root, text="עיון", command=select_file, bg='#F0E68C', relief="groove").grid(row=1, column=0, columnspan=3, padx=30, pady=5, sticky="w")

# בחירת רמת כותרת
tk.Label(root, text=":בחר רמת כותרת", bg='lightyellow', anchor='e').grid(row=2, column=2, padx=1, pady=5, sticky="nw")
header_var = tk.StringVar(root)  
header_choices = [str(i) for i in range(2, 10)]  # ערכים תקינים בין 2 ל-9
header_menu = Combobox(root, textvariable=header_var, values=header_choices, width=1, justify=tk.RIGHT)
header_menu.grid(row=2, column=1, padx=1, pady=5, sticky="e")
header_var.set("3")

# כפתור 'הרץ כעת'
tk.Button(root, text="הרץ כעת", command=run_script, bg='#F0E68C', relief="groove").grid(row=3, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
