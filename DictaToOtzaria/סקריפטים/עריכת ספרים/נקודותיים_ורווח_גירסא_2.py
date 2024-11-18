import re
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# פתיחת חלון לבחירת הקובץ
root = tk.Tk()
root.withdraw()  # מסתיר את החלון הראשי
file_path = filedialog.askopenfilename(title="בחר קובץ טקסט", filetypes=[("Text Files", "*.txt")])

try:
    if not file_path:
        messagebox.showinfo("קלט לא תקין", "לא נבחר קובץ")
    else:
        # קריאת הקובץ שנבחר
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # שלב 1: החלפת רצפים של רווחים באנטר בלבד
        new_content = re.sub(r' {1,5}\n', '\n', content)

        # שלב 2: החלפת נקודותיים ורווח בנקודותיים ואנטר
        new_content = re.sub(r':\s', ':\n', new_content)

        # בדיקה אם בוצעו שינויים
        if content == new_content:
            messagebox.showinfo("!שים לב", "לא נמצא מה להחליף")
        else:
            # כתיבת התוכן המעודכן לקובץ המקורי
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

            messagebox.showinfo("!מזל טוב", "ההחלפה הושלמה בהצלחה! הקובץ המקורי עודכן")

except Exception as e:
    messagebox.showerror("שגיאה", f"ארעה שגיאה במהלך העיבוד: {str(e)}")
