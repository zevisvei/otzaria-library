import re
import tkinter as tk
from tkinter import filedialog, messagebox

# משתנה לשמירת נתיב הקובץ שנבחר
file_path = None

def choose_file():
    global file_path
    file_path = filedialog.askopenfilename(title="בחר קובץ טקסט", filetypes=[("Text Files", "*.txt")])
    if file_path:
        entry_file_path.delete(0, tk.END)  # מנקה את השדה
        entry_file_path.insert(0, file_path)  # מציג את הנתיב הנבחר
        choose_button.config(text="קובץ נבחר, המשך לבחירת סוג ההחלפה")

def update_file(replace_type):
    if not file_path:
        messagebox.showerror("קלט לא תקין", "לא נבחר קובץ.")
        return

    # קריאת הקובץ שנבחר
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # משתנה לשמירת הכותרת הקודמת
    previous_title = ""
    previous_level = ""
    replacements_made = 0  # ספירת כמות ההחלפות

    # פונקציה שתשנה את הכותרות המתאימות
    def replace_match(match):
        nonlocal previous_title, previous_level, replacements_made
        level = match.group(1)
        title = match.group(2)

        # בדיקה אם הכותרת היא "דף"
        if re.match(r"דף \S+\.?", title):
            previous_title = title.strip()
            previous_level = level
            return match.group(0)

        # בדיקה אם הכותרת היא "עמוד ב"
        elif title == "עמוד ב":
            replacements_made += 1  # הוחלפה כותרת
            if replace_type == "נקודותיים":
                return f'<h{previous_level}>{previous_title.rstrip(".")}:</h{previous_level}>'
            elif replace_type == "ע\"ב":
                # הסרת "ע"א" או "עמוד א" מהכותרת הקודמת אם קיימים
                modified_title = re.sub(r'( ע"א| עמוד א)$', '', previous_title)
                return f'<h{previous_level}>{modified_title.rstrip(".")} ע\"ב</h{previous_level}>'
        
        # אם זה לא אחד המקרים למעלה, נשאיר את הכותרת כפי שהיא
        return match.group(0)

    # עדכון הכותרות בקובץ - עבור כל רמה (h1 עד h9)
    content = re.sub(r'<h([1-9])>(.*?)</h\1>', replace_match, content)

    # שמירת הקובץ המקורי עם התוכן המעודכן
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    # הצגת הודעה אם לא נמצא מה להחליף
    if replacements_made == 0:
        messagebox.showinfo("!שים לב", "לא נמצא מה להחליף")
    else:
        messagebox.showinfo("!מזל טוב", f"!הקובץ עודכן בהצלחה\n\nבוצעו {replacements_made} החלפות")

# יצירת חלון ראשי
root = tk.Tk()
root.title("החלפת כותרות לעמוד ב")
root.geometry("410x510")
root.configure(bg='lightblue')

# יצירת תוויות וכפתורים
label = tk.Label(root, text="!שים לב\nהתוכנה פועלת רק אם הדפים והעמודים הוגדרו כבר ככותרות\n[לא משנה באיזה רמת כותרת]\nוכן הלאה      </h3>עמוד ב<h3> :או    </h2>עמוד ב<h2> :כגון\n\n!זהירות\nבדוק היטיב שלא פספסת שום כותרת של 'דף' לפני שאתה מריץ תוכנה זו\nכי במקרה של פספוס, הכותרת 'עמוד ב' שאחרי הפספוס תהפך לכותרת שגויה", bg='lightblue', anchor='e')
label.pack(pady=10)

# כפתור לבחירת הקובץ
choose_button = tk.Button(root, text="בחר קובץ", relief="groove", bd=2, command=choose_file, bg='lightyellow')
choose_button.pack(pady=10)

# יצירת שורת עריכת נתיב
entry_file_path = tk.Entry(root, relief="groove", bd=2, width=50, bg='lightyellow')
entry_file_path.pack(pady=5)

# הודעת הסבר למשתמש
label = tk.Label(root, text=":בחר את סוג ההחלפה", bg='lightblue', anchor='e')
label.pack(pady=10)

# אפשרויות בחירה
replace_type = tk.StringVar(value="נקודותיים")

radio1 = tk.Radiobutton(root, relief="groove", bd=2, text=":החלפה לנקודותיים", variable=replace_type, value="נקודותיים", anchor='n', bg='lightblue')
radio1.pack(padx=20, pady=0)

# הסבר לדוגמא
example1 = tk.Label(root, text=":לדוגמא\n:דף ב:   דף ג:   דף ד:   דף ה\nוכן הלאה", bg='lightblue')
example1.pack(pady=5)

radio2 = tk.Radiobutton(root, relief="groove", bd=2, text=":החלפה לע\"ב", variable=replace_type, value="ע\"ב", anchor='n', bg='lightblue')
radio2.pack(padx=20, pady=0)

# הסבר לדוגמא
example2 = tk.Label(root, text=":לדוגמא\nדף ב ע\"ב   דף ג ע\"ב   דף ד ע\"ב   דף ה ע\"ב\nוכן הלאה", bg='lightblue')
example2.pack(pady=5)

# כפתור לביצוע ההחלפה
button = tk.Button(root, relief="groove", bd=2, text="בצע החלפה", command=lambda: update_file(replace_type.get()), bg='lightgreen')
button.pack(pady=20)

# התחלת הלולאה הראשית של ה-Tkinter
root.mainloop()
