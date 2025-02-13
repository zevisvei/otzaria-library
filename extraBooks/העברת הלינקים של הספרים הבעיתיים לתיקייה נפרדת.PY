import os
import shutil

# הגדרות נתיבים
txt_folder = r"C:\Users\user\Documents\otzaria-library\extraBooks\אוצריא"  # הנתיב לתיקייה עם קבצי ה-TXT
json_folder = r"C:\Users\user\Documents\otzaria-library\links"  # הנתיב לתיקייה עם קבצי ה-JSON (כולל תתי-תיקיות)
destination_folder = r"C:\Users\user\Documents\otzaria-library\extraBooks\links"  # תיקיית היעד להעברת קבצי JSON

# יצירת תיקיית היעד אם אינה קיימת
os.makedirs(destination_folder, exist_ok=True)

# יצירת רשימת שמות קבצי ה-TXT (ללא סיומת) מתיקייה כולל תתי-תיקיות
txt_files = set()
for root, _, files in os.walk(txt_folder):  
    for f in files:
        if f.endswith(".txt"):
            txt_files.add(os.path.splitext(f)[0])  # שמירת שם הקובץ ללא הסיומת

# חיפוש קבצי JSON בתתי-תיקיות והעברתם אם יש התאמה
for root, _, files in os.walk(json_folder):
    for json_file in files:
        if json_file.endswith("_links.json"):
            base_name = json_file.replace("_links.json", "")  # חילוץ השם ללא הסיומת
            if base_name in txt_files:  # בדיקה אם יש קובץ TXT מתאים
                source_path = os.path.join(root, json_file)
                destination_path = os.path.join(destination_folder, json_file)
                shutil.move(source_path, destination_path)  # העברת הקובץ
                print(f"הועבר: {json_file} מ-{source_path}")

print("✅ העברת הקבצים הושלמה!")
