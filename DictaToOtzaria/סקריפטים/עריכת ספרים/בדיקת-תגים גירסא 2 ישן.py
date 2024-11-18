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
    
    # Compile the regex pattern based on user input
    if re_start and re_end:
        pattern = re.compile(f"^{re_start}.+[{re_end}]$")
    elif re_start:
        pattern = re.compile(f"^{re_start}.+['א-ת]$")
    elif re_end:
        pattern = re.compile(f"^[א-ת].+[{re_end}]$")
    else:
        pattern = re.compile(r"^[א-ת].+[א-ת']$")
    
    unmatched_regex = []
    unmatched_tags = []
    
    # Iterate over header tags h2 to h6
    for i in range(2, 7):
        tags = soup.find_all(f"h{i}")
        
        # Check if tags were found
        if not tags:
            unmatched_tags.append(f"No tags found for h{i}")
            continue
        
        # Process all tags except the last one
        for index in range(len(tags) - 2):
            current_tag = tags[index].string or ""
            next_tag = tags[index + 2].string or ""
            
            # Ensure the tag strings are not empty
            if not current_tag or not next_tag:
                continue
            
            # Assuming split on space to get headings
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
            
            # Check if the current tag matches the pattern
            if not re.match(pattern, current_tag):
                unmatched_regex.append(current_tag)
            
            # Check for gershayim conditions
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
            
            # Check if headings are consecutive
            if not gematriapy.to_number(current_heading) + 1 == gematriapy.to_number(next_heading):
                unmatched_tags.append(f"תג נוכחי {current_tag} תג הבא {next_tag}")

        # Process the last tag
        last_tages = (tags[-2].string or "", tags[-1].string or "")
        for last_tag in last_tages:
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

# Create the main window
root = tk.Tk()
root.title("בודק הספרים האוטומטי")

# Default values
default_re_start = ""
default_re_end = ""
default_gershayim = True

# Create and place widgets
tk.Label(root, text="תו בתחילת הכותרת").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
re_start_entry = tk.Entry(root)
re_start_entry.insert(0, default_re_start)  # Set default value
re_start_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="תו בסוף הכותרת").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
re_end_entry = tk.Entry(root)
re_end_entry.insert(0, default_re_end)  # Set default value
re_end_entry.grid(row=1, column=1, padx=10, pady=5)

gershayim_var = tk.BooleanVar(value=default_gershayim)  # Set default value
tk.Checkbutton(root, text="כולל גרשיים", variable=gershayim_var).grid(row=2, columnspan=2, padx=10, pady=5)

tk.Button(root, text="פתח קובץ", command=open_file).grid(row=3, columnspan=2, padx=10, pady=10)

# Create text widgets for results
tk.Label(root, text="שאינן תואמות Regex תוצאות").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
unmatched_regex_text = tk.Text(root, wrap=tk.WORD, height=10, width=50)
unmatched_regex_text.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

tk.Label(root, text="תגים לא תואמים").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
unmatched_tags_text = tk.Text(root, wrap=tk.WORD, height=10, width=50)
unmatched_tags_text.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

# Start the GUI event loop
root.mainloop()