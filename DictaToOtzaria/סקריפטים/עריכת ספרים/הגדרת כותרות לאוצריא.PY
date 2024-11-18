import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Combobox
from pyluach import gematria

# פונקציית תצוגת הודעה מותאמת אישית
def show_custom_message(title, message_parts, window_size="560x330"):
    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry(window_size)  # גודל חלון מותאם

    # הוספת ההודעה עם כל חלק בגודל גופן שונה
    for text, font_size, *style in message_parts:
        font_style = ("Arial", font_size) if not style else ("Arial", font_size, style[0])
        message_label = tk.Label(popup, text=text, font=font_style, justify="center")
        message_label.pack()

    close_button = tk.Button(popup, text="סגור", command=popup.destroy, relief="groove", bd=2)
    close_button.pack(pady=10)

def ot(text, end):
    remove = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", ".", "״", "‚", "”", "’"]
    aa = ["ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"]
    bb = ["ם", "ן", "ץ", "ף", "ך"]
    cc = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "ששי", "שביעי", "שמיני", "תשיעי", "עשירי", "דש", "שדמ", "ער", "שדם", "תשדם", "תשדמ", "ערב", "ערה"]
    append_list = []
    for i in aa:
        for ot_sofit in bb:
            append_list.append(i + ot_sofit)
            
    for tage in remove:
        text = text.replace(tage, "")
    withaute_gershayim = [gematria._num_to_str(i, thousands=False, withgershayim=False) for i in range(1, end)] + bb + cc + append_list
    return text in withaute_gershayim

def strip_html_tages(text):
    html_tages = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", "״", ".", "‚", "”", "’"]
    for tage in html_tages:
        text = text.replace(tage, "")
    return text

def main(book_file, finde, end, level_num):
    found = False
    count_headings = 0
    finde_cleaned = strip_html_tages(finde).strip()  # ניקוי המילה מהתפריט הנפתח
    with open(book_file, "r", encoding="utf-8") as file_input:
        content = file_input.read().splitlines()
        all_lines = content[0:2]
        for line in content[2:]:
            words = line.split()
            try:
                if strip_html_tages(words[0]) == finde and ot(words[1], end):
                    found = True
                    count_headings += 1
                    heading_line = f"<h{level_num}>{strip_html_tages(words[0])} {strip_html_tages(words[1])}</h{level_num}>"
                    all_lines.append(heading_line)
                    if words[2:]:
                        fix_2 = " ".join(words[2:])
                        all_lines.append(fix_2)
                else:
                    all_lines.append(line)
            except IndexError:
                all_lines.append(line)
    join_lines = "\n".join(all_lines)
    with open(book_file, "w", encoding="utf-8") as autpoot:
        autpoot.write(join_lines)

    return found, count_headings

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("קבצי טקסט", "*.txt"), ("כל הפורמטים", "*.*")])
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

def run_script():
    book_file = file_entry.get()
    finde = level_var.get()  
    try:
        end = int(end_var.get())
        level_num = int(heading_level_var.get())  
    except ValueError:
        show_custom_message("קלט לא תקין", [("אנא הזן 'מספר סימן מקסימלי' ו'רמת כותרת' תקינים", 12)], "250x150")
        return
    
    if not book_file or not finde:
        show_custom_message("קלט לא תקין", [("אנא מלא את כל השדות", 12)], "250x80")
        return

    try:
        found, count_headings = main(book_file, finde, end + 1, level_num)
        if found and count_headings > 0:
            # הודעה מפורטת במקרה שנוצרו כותרות
            detailed_message = [
                ("!התוכנה רצה בהצלחה", 12),
                (f"נוצרו {count_headings} כותרות", 15, "bold"),  # הדגשה
                ("\nכעת פתח את הספר בתוכנת 'אוצריא', והשינויים ישתקפו ב'ניווט' שבתפריט הצידי", 11),
                ("אם ישנם טעויות או תיקונים, פתח את הספר בעורך טקסט, כגון פנקס רשימות או וורד", 11),
                ("notepad++ או vs code", 11),
                ("ותקן את הדרוש תיקון\n", 11),
                ("!שים לב", 10),
                ("אם הספר כבר פתוח בתוכנה, יש לסגור אותו ולפתוח אותו שוב", 8),
                ("אבל אין צורך להפעיל את תוכנת אוצריא מחדש", 8)
            ]
            show_custom_message("!מזל טוב", detailed_message, "560x310")
        else:
            # הודעה קצרה אם לא נוצרו כותרות
            show_custom_message("!שים לב", [("לא נמצא מה להחליף", 12)], "250x80")
    except Exception as e:
        show_custom_message("שגיאה", [("אירעה שגיאה: " + str(e), 12)], "250x150")

# GUI הגדרת הממשק הגרפי
root = tk.Tk()
root.title("הגדרת כותרות לאוצריא")

tk.Label(root, text=":נתיב קובץ", font=("Arial", 12), anchor='e').grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
file_entry = tk.Entry(root, relief="groove", bd=2, font=("Arial", 12), width=60, justify=tk.RIGHT)
file_entry.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(root, relief="groove", bd=2, text="עיון", command=browse_file, font=("Arial", 14))
browse_button.grid(row=0, column=0, padx=10, pady=5)

tk.Label(root, text=":מילה לחפש", font=("Arial", 14), anchor='e').grid(row=1, column=2, padx=10, pady=5, sticky=tk.E)
level_var = tk.StringVar(root)
level_choices = ["דף", "עמוד", "פרק", "פסוק", "שאלה", "סימן", "סעיף", "הלכה", "הלכות", "סק"]
level_menu = Combobox(root, textvariable=level_var, values=level_choices, font=("Arial", 14), width=8, justify=tk.RIGHT)
level_menu.grid(row=1, column=1, padx=10, pady=5)

# הודעת הסבר למשתמש
tk.Label(root, text="בתיבת 'מילה לחפש' יש לכתוב את המילה בה אנו רוצים שתתחיל הכותרת. לדוג': פרק/פסוק/סימן/סעיף/הלכה/שאלה/עמוד/סק\n!שים לב\nאין להקליד רווח אחרי המילה, וכן אין להקליד את התו גרש (') או גרשיים (\"), וכן אין להקליד יותר ממילה אחת\n\n").grid(row=2, column=0, columnspan=3, padx=10, pady=5)

tk.Label(root, text=":מספר סימן מקסימלי", font=("Arial", 8), anchor='e').grid(row=3, column=2, padx=10, pady=5, sticky=tk.E)
end_var = tk.StringVar(root)
end_choices = [str(i) for i in range(1, 999)]
end_menu = Combobox(root, textvariable=end_var, values=end_choices, width=3, justify=tk.RIGHT)
end_menu.grid(row=3, column=1, padx=10, pady=5)
end_var.set("999")

# תפריט נפתח לרמת כותרת
tk.Label(root, text=":רמת כותרת", font=("Arial", 14), anchor='e').grid(row=4, column=2, padx=10, pady=5, sticky=tk.E)
heading_level_var = tk.StringVar(root)  
heading_level_choices = [str(i) for i in range(2, 10)]
heading_level_menu = Combobox(root, textvariable=heading_level_var, values=heading_level_choices, font=("Arial", 14), width=1, justify=tk.RIGHT)
heading_level_menu.grid(row=4, column=1, padx=10, pady=5)
heading_level_var.set("2")

run_button = tk.Button(root, relief="groove", bd=2, text="הפעל", command=run_script, font=("Arial", 14))
run_button.grid(row=6, column=1, pady=20)

root.mainloop()
