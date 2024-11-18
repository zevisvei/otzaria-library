import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  
from pyluach import gematria

def ot(text, end):
    remove = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", ".", "״", "‚", "”", "’"]
    aa = ["ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"]
    bb = ["ם", "ן", "ץ", "ף", "ך"]
    cc = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שביעי", "שמיני", "תשיעי", "עשירי", "דש", "שדמ", "ער", "שדם", "תשדם", "תשדמ", "ערה"]
    append_list = []
    for i in aa:
        for ot_sofit in bb:
            append_list.append(i + ot_sofit)
            
    for tage in remove:
        text = text.replace(tage, "")
    withaute_gershayim = [gematria._num_to_str(i, thousands=False, withgershayim=False) for i in range(1, end)] + bb + cc + append_list
    return text in withaute_gershayim
    
def strip_html_tages(text, ignore):
    for tage in ignore:
        text = text.replace(tage, "")
    return text
    
def main(book_file, finde, end, level_num, ignore, start, remove, is_bold_checked):
    with open(book_file, "r", encoding="utf-8") as file_input:
        content = file_input.read().splitlines()
        all_lines = content[0:1]
        for line in content[1:]:
            words = line.split()
            try:
                is_finde_end = [strip_html_tages(words[0], ignore).endswith(i) for i in finde]
                is_finde_start = [strip_html_tages(words[0], ignore).startswith(i) for i in start]
                if any(is_finde_end) and any(is_finde_start) and ot(words[0], end) and ((is_bold_checked and strip_html_tages(words[0], ignore).startswith("<b>") and strip_html_tages(words[0], ignore).startswith("</b>")) or (not is_bold_checked and "<b>" not in words[0] and "</b>" not in words[0])):
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
    filename = filedialog.askopenfilename(filetypes=[("קבצי טקסט", "*.txt"), ("כל הפורמטים", "*.*")])
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)
        
def run_script():
    book_file = file_entry.get()
    finde = finde_entry.get().split()
    remove =["<b>", "</b>"] + remove_entry.get().split()
    ignore = ignore_entry.get().split()
    start = start_entry.get().split()
    is_bold_checked = bold_var.get()
    	
    try:
        end = int(end_var.get())
        level_num = int(level_var.get())
    except ValueError:
        messagebox.showerror("קלט לא תקין", "אנא הזן 'מספר סימן מקסימלי' ו'רמת כותרת' תקינים")
        return
    
    if not book_file or not finde:
        messagebox.showerror("קלט לא תקין", "אנא מלא את כל השדות")
        return
        
    try:
        main(book_file, finde, end + 1, level_num , ignore, start, remove, is_bold_checked)
        messagebox.showinfo("מזל טוב!", "הסקריפט רץ בהצלחה!")
    except Exception as e:
        messagebox.showerror("שגיאה", f"אירעה שגיאה: {e}")
        
# GUI setup
root = tk.Tk()
root.title("מקודד לאוצריא")

# File path label and entry
tk.Label(root, text=":נתיב קובץ", anchor='e').grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
file_entry = tk.Entry(root, width=50, justify=tk.RIGHT)
file_entry.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="עיון", command=browse_file)
browse_button.grid(row=0, column=0, padx=10, pady=5)

# Character at the end label and entry
tk.Label(root, text="תו בסוף האות", anchor='e').grid(row=1, column=2, padx=10, pady=5, sticky=tk.E)
finde_entry = tk.Entry(root, width=50, justify=tk.RIGHT)
finde_entry.grid(row=1, column=1, padx=10, pady=5)
finde_entry.insert(0, ":")

# Character at the start label and entry
tk.Label(root, text="תו בתחילת האות", anchor='e').grid(row=2, column=2, padx=10, pady=5, sticky=tk.E)
start_entry = tk.Entry(root, width=50, justify=tk.RIGHT)
start_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="התעלם מהתווים הבאים:", anchor='e').grid(row=3, column=2, padx=10, pady=5, sticky=tk.E)
ignore_entry = tk.Entry(root, width=50, justify=tk.RIGHT)
ignore_entry.grid(row=3, column=1, padx=10, pady=5)
ignore_entry.insert(0, """<b> </b> <big> </big> , : " [ ] { }""")

# Ignore characters label and entry
tk.Label(root, text="הסר את התווים הבאים", anchor='e').grid(row=4, column=2, padx=10, pady=5, sticky=tk.E)
remove_entry = tk.Entry(root, width=50, justify=tk.RIGHT)
remove_entry.grid(row=4, column=1, padx=10, pady=5)
remove_entry.insert(0, """<b> </b> <big> </big> , : " [ ] { }""")

# Maximum character number label and combobox
tk.Label(root, text=":מספר סימן מקסימלי", anchor='e').grid(row=5, column=2, padx=10, pady=5, sticky=tk.E)
end_var = tk.StringVar(root)
end_choices = [str(i) for i in range(1, 301)]
end_menu = ttk.Combobox(root, textvariable=end_var, values=end_choices, justify=tk.RIGHT)
end_menu.grid(row=5, column=1, padx=10, pady=5)
end_var.set("999")

# Heading level label and combobox
tk.Label(root, text=":רמת כותרת", anchor='e').grid(row=6, column=2, padx=10, pady=5, sticky=tk.E)
level_var = tk.StringVar(root)
level_choices = [str(i) for i in range(1, 7)]
level_menu = ttk.Combobox(root, textvariable=level_var, values=level_choices, justify=tk.RIGHT)
level_menu.grid(row=6, column=1, padx=10, pady=5)
level_var.set("2")

# Checkbox for bold search
bold_var = tk.BooleanVar()
bold_var.set(True)  # Set the checkbox to be checked by default
bold_check = tk.Checkbutton(root, text="לחפש עם תווי הדגשה בלבד", variable=bold_var)
bold_check.grid(row=7, column=1, pady=20)

# Run button
run_button = tk.Button(root, text="הפעל", command=run_script)
run_button.grid(row=8, column=1, pady=20)

root.mainloop()