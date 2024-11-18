import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import re

def change_heading_level(file_path, current_level, new_level):
    # פתיחת הקובץ לקריאה
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # החלפת רמת הכותרת
    current_tag = f"h{current_level}"
    new_tag = f"h{new_level}"
    updated_content = re.sub(f"<{current_tag}>(.*?)</{current_tag}>", f"<{new_tag}>\\1</{new_tag}>", content, flags=re.DOTALL)

    # בדיקה אם היו שינויים
    if content == updated_content:
        messagebox.showinfo("!שים לב", "לא נמצא מה להחליף")
    else:
        # שמירת התוכן המעודכן חזרה לקובץ
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        messagebox.showinfo("!מזל טוב", "רמות הכותרות עודכנו בהצלחה")

def browse_file():
    # פתיחת חלון לבחירת קובץ טקסט
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("HTML files", "*.html")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(0, file_path)
    
def execute_change():
    # קבלת ערכי הקלט מהממשק
    file_path = entry_file_path.get()
    current_level = entry_current_level_var.get()
    new_level = entry_new_level_var.get()

    if not file_path:
        messagebox.showerror("קלט לא תקין", "אנא בחר קובץ")
        return
    
    if not current_level.isdigit() or not new_level.isdigit():
        messagebox.showerror("קלט לא תקין", "אנא הכנס רמות מספריות חוקיות")
        return
    
    # קריאה לפונקציה לביצוע השינוי
    change_heading_level(file_path, current_level, new_level)

# יצירת הממשק הגרפי
root = tk.Tk()
root.title("שינוי רמת כותרת")

# תיבת הקובץ וכפתור העיון
tk.Label(root, text=":נתיב קובץ").grid(row=0, column=2, padx=20, pady=20, sticky="e")
entry_file_path = tk.Entry(root, relief="groove", bd=2, width=45)
entry_file_path.grid(row=0, column=1, columnspan=3, padx=10, pady=20)
tk.Button(root, relief="groove", bd=2, text="עיון", command=browse_file).grid(row=0, column=0, columnspan=3, padx=20, pady=20, sticky="w")

# רמת כותרת נוכחית
tk.Label(root, text="רמת כותרת נוכחית: (לדוגמא: 2)\nהזן מספר בלבד").grid(row=1, column=2, padx=30, pady=5, sticky="e")
entry_current_level_var = tk.StringVar(root)  
entry_current_level_choices = [str(i) for i in range(1, 10)]
entry_current_level_menu = Combobox(root, textvariable=entry_current_level_var, values=entry_current_level_choices, font=("Arial", 14), width=1, justify=tk.RIGHT)
entry_current_level_menu.grid(row=2, column=2, padx=10, pady=5)

# רמת כותרת חדשה
tk.Label(root, text="רמת כותרת חדשה: (לדוגמא: 3)\nהזן מספר בלבד").grid(row=1, column=1, padx=30, pady=5, sticky="n")
entry_new_level_var = tk.StringVar(root)  
entry_new_level_choices = [str(i) for i in range(1, 10)]
entry_new_level_menu = Combobox(root, textvariable=entry_new_level_var, values=entry_new_level_choices, font=("Arial", 14), width=1, justify=tk.RIGHT)
entry_new_level_menu.grid(row=2, column=1, padx=1, pady=1)

# כפתור ההרצה
tk.Button(root, relief="groove", bd=2, text="שנה רמת כותרת", command=execute_change).grid(row=3, column=1, columnspan=3, padx=1, pady=20, sticky="n")

root.mainloop()
