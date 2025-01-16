import os
import shutil
import sys



folders = ("Ben-YehudaToOtzaria/ספרים/אוצריא",
            "DictaToOtzaria/ספרים/ערוך/אוצריא",
            "OnYourWayToOtzaria/ספרים/אוצריא",
            "OraytaToOtzaria/ספרים/אוצריא",
            "sefaria and more")


for folder in folders:
    shutil.copytree(folder, f"אוצריא", dirs_exist_ok=True)

