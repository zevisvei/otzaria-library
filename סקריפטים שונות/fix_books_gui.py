import os
import sys
import subprocess
import requests
from PyQt6 import QtWidgets, QtCore

BASE_URL = "https://script.google.com/macros/s/AKfycbz4pSY2vK8opQeeh2X__PZYDs1EP8Wq77HfoU7F0X_bCErKfl6nvDjnnQ_B4AjpUT-7/exec"


def get_books():
    params = {"action": "get_book"}
    response = requests.get(BASE_URL, params=params).json()
    if response.get("success"):
        return response.get("data", [])
    return []


def complete_book(row, comment=None):
    params = {"action": "complete_book", "row": row, "comments": comment}
    response = requests.get(BASE_URL, params=params).json()
    return response.get("success", False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ניהול ספרים - תיקון ספרים")
        # הגדרת כיוון הממשק למימין לשמאל
        self.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.books = []  # רשימה לכל הספרים

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # חלונית עליונה: כפתור לבחירת תיקייה, תיבת טקסט להצגת הנתיב וכפתור טעינה
        top_layout = QtWidgets.QHBoxLayout()
        self.dir_button = QtWidgets.QPushButton("בחר תיקייה")
        self.dir_button.clicked.connect(self.browse_directory)
        top_layout.addWidget(self.dir_button)

        self.load_button = QtWidgets.QPushButton("טעינת ספרים")
        self.load_button.clicked.connect(self.load_books)
        top_layout.addWidget(self.load_button)

        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("בחר נתיב ספריה")
        self.path_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        top_layout.addWidget(self.path_edit)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # טבלה - תופסת את רוב החלון
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["סוג שגיאה", "מקור הקובץ", "נתיב ימות", "הערה", "מידע נוסף", "מספר שורה", "פעולות"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        main_layout.addWidget(self.table, stretch=1)

        # הפעלה בלחיצה כפולה על שורה
        self.table.doubleClicked.connect(lambda: self.run_book_at_row(self.table.currentRow()))

    def browse_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "בחר תיקיית ספריה")
        if directory:
            self.path_edit.setText(directory)

    def load_books(self):
        self.books = get_books()
        self.refresh_table()

    def refresh_table(self):
        """מרעננת את הטבלה מהנתונים הקיימים ב־self.books."""
        self.table.setRowCount(0)
        for row, book in enumerate(self.books):
            self.table.insertRow(row)
            error_str = book.get("eroorStr", "")
            source = book.get("bookSource", "")
            yemot = book.get("file_path_in_yemot", "")
            comments = book.get("comments", "")
            more_info = book.get("more_info", "")
            line = str(book.get("line", ""))
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(error_str))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(source))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(yemot))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(comments))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(more_info))
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(line))
            for col in range(6):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            # עמודת פעולות: כפתור להרצת הסקריפט על שורה זו עם צבע שונה ואייקון הפעלה
            run_btn = QtWidgets.QPushButton("הרץ")
            # הוספת אייקון הפעלה מהסטייל של Qt
            icon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
            run_btn.setIcon(icon)
            # שינוי צבע הרקע והטקסט
            run_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            run_btn.clicked.connect(lambda checked, r=row: self.run_book_at_row(r))
            self.table.setCellWidget(row, 6, run_btn)

        # הגדרת רוחב עמודות:
        self.table.setColumnWidth(5, 80)   # "מספר שורה" – צרה
        self.table.setColumnWidth(6, 40)   # "פעולות" – צרה
        self.table.setColumnWidth(4, 300)  # "מידע נוסף" – רחבה יותר

    def run_book_at_row(self, row):
        if row < 0 or row >= len(self.books):
            return
        book = self.books[row]
        library_path = self.path_edit.text().strip()
        if not library_path:
            QtWidgets.QMessageBox.critical(self, "שגיאה", "יש להזין נתיב ספריה או לבחור תיקייה")
            return
        fix_file_path = book["bookFilePath"].replace("/", os.sep)
        file_path = os.path.join(library_path, fix_file_path)
        if not os.path.exists(file_path):
            QtWidgets.QMessageBox.critical(self, "שגיאה", f"קובץ לא נמצא: {file_path}")
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "שגיאה", f"שגיאה בקריאת הקובץ: {e}")
            return
        file_len = len(content.split("\n"))
        if file_len != book.get("lines_num", file_len):
            QtWidgets.QMessageBox.critical(self, "שגיאה", f"אורך הקובץ לא תואם: {file_len} != {book.get('bookLength', 'לא ידוע')}")
            return
        try:
            subprocess.run(["gedit", f"+{book.get('line', 1)}", file_path],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           check=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "שגיאה", f"לא ניתן לפתוח את הקובץ ב-VS Code: {e}")
            return
        # הצגת פרטי הספר ובקשת אישור
        info = f"סוג שגיאה: {book.get('eroorStr', '')}\n"
        info += f"מקור הקובץ: {book.get('bookSource', '')}\n"
        if book.get("file_path_in_yemot"):
            info += f"נתיב ימות: {book.get('file_path_in_yemot', '')}\n"
        if book.get("comments"):
            info += f"הערה: {book.get('comments', '')}\n"
        if book.get("more_info"):
            info += f"מידע נוסף: {book.get('more_info', '')}\n"
        info += f"מספר שורה: {book.get('line', '')}\n\n"
        info += "האם לדווח כהושלם?"
        reply = QtWidgets.QMessageBox.question(self, "אישור", info,
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return


        comment, ok = QtWidgets.QInputDialog.getText(self, "הערה", "הערה:")
        if not ok:
            comment = ""
        result = complete_book(book.get("row"), comment)
        if result:
            QtWidgets.QMessageBox.information(self, "הצלחה", "נשלח בהצלחה")
            # הסרת השורה מהרשימה ועדכון הטבלה
            del self.books[row]
            self.refresh_table()
        else:
            QtWidgets.QMessageBox.critical(self, "שגיאה", "שגיאה בשליחה")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())
