import tkinter as tk
from tkinter import filedialog, messagebox

def process_file(file_path, add_ending, emphasize_start):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        changed = False
        for i in range(3, len(lines)):  # מתחיל מהשורה הרביעית (אינדקס 3)
            line = lines[i].rstrip()
            words = line.split()

            # בדיקה אם יש יותר מעשר מילים ושאין סימן כותרת בהתחלה
            if len(words) > 10 and not any(line.startswith(f'<h{n}>') for n in range(2, 10)):
                # הסרת רווחים ותווים מיותרים בסוף השורה לפני בדיקה
                stripped_line = line.rstrip(" .,;:!?)</small></big></b>")  # מסיר תווים מיותרים מסוף השורה

                # מחיקת רווחים לפני נקודה או נקודתיים קיימים בסוף השורה
                if line.endswith(('.', ':')):
                    line = line.rstrip()  # הסרת רווחים מיותרים לפני הסימן

                # הוספת נקודה או נקודתיים בסוף השורה
                if add_ending:
                    if line.endswith(','):
                        line = line.rstrip()  # הסרת רווחים מיותרים לפני הוספת הסימן
                        if add_ending == "נקודה":
                            lines[i] = line[:-1] + '.\n'
                        elif add_ending == "נקודתיים":
                            lines[i] = line[:-1] + ':\n'
                        changed = True
                    elif not line.endswith(('.', ':', '!', '?')) and not any(line.endswith(tag) for tag in ['</small>', '</big>', '</b>']):
                        line = line.rstrip()  # הסרת רווחים מיותרים לפני הוספת הסימן
                        if add_ending == "נקודה":
                            lines[i] = line.rstrip() + '.\n'
                        elif add_ending == "נקודתיים":
                            lines[i] = line.rstrip() + ':\n'
                        changed = True

                # הדגשת המילה הראשונה אם אין סימנים מיוחדים
                if emphasize_start:
                    first_word = words[0]
                    if not any(tag in first_word for tag in ['<b>', '<small>', '<big>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>', '<h7>', '<h8>', '<h9>']):
                        if not (first_word.startswith('<') and first_word.endswith('>')):
                            lines[i] = '<b>' + first_word + '</b> ' + ' '.join(words[1:]) + (('.' if line == stripped_line and add_ending == "נקודה" else '') or (':' if line == stripped_line and add_ending == "נקודתיים" else '')) + '\n'
                            changed = True

        if changed:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            messagebox.showinfo("!מזל טוב", "השינויים נשמרו בהצלחה")
        else:
            messagebox.showinfo("!שים לב", "אין מה לשנות")

    except Exception as e:
        messagebox.showerror("!שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")

def select_file():
    file_path = filedialog.askopenfilename(title="בחר קובץ", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        file_path_entry.delete(0, tk.END)
        file_path_entry.insert(0, file_path)

def update_file_path():
    global selected_file_path
    selected_file_path = file_path_entry.get()

def run_processing():
    if selected_file_path:
        add_ending = ending_var.get()
        emphasize_start = emphasize_var.get()
        process_file(selected_file_path, add_ending, emphasize_start)
    else:
        messagebox.showinfo("קלט לא תקין", "אנא בחר קובץ תחילה")

# יצירת הממשק הגרפי
root = tk.Tk()
root.title("הדגשה וניקוד")
root.geometry("280x350")

selected_file_path = None

open_button = tk.Button(root, relief="groove", bd=2, text="בחר קובץ", command=select_file)
open_button.pack(pady=10)

tk.Label(root, text=":נתיב קובץ").pack(pady=0)
file_path_entry = tk.Entry(root, relief="groove", bd=2, width=40)
file_path_entry.pack(pady=10)

# בחירה להוספת נקודה או נקודותיים
ending_var = tk.StringVar(value="נקודה")
tk.Label(root, text=":בחר פעולה לסוף קטע").pack(padx=10, pady=5)
tk.Radiobutton(root, text="הוסף נקודה", variable=ending_var, value="נקודה").pack(padx=15, anchor=tk.E)
tk.Radiobutton(root, text="הוסף נקודתיים", variable=ending_var, value="נקודתיים").pack(padx=15, anchor=tk.E)
tk.Radiobutton(root, text="ללא הוספת סימן", variable=ending_var, value=None).pack(padx=15, anchor=tk.E)

# בחירה להדגשת תחילת קטע
emphasize_var = tk.BooleanVar()
tk.Checkbutton(root, text="הדגש את תחילת הקטעים", variable=emphasize_var).pack(padx=15, pady=20, anchor=tk.E)

run_button = tk.Button(root, relief="groove", bd=2, text="הרץ כעת", command=run_processing)
run_button.pack(pady=20)

root.mainloop()
