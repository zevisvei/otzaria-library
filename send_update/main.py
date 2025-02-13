import subprocess
import codecs
import os

from pyluach import dates

from mitmachim import MitmachimClient
from yemot import send_to_yemot


FOLDER = "אוצריא"


def heb_date() -> str:
    today = dates.HebrewDate.today()
    date_str = today.hebrew_date_string()
    return date_str


def get_changed_files(status_filter):
    result = subprocess.run(
        ["git", "diff", "--name-only", f"--diff-filter={status_filter}", "HEAD^", "HEAD", "--", FOLDER],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    raw_output = result.stdout.strip()
    decoded_files = []
    for line in raw_output.split("\n"):
        if line:
            decoded_line = codecs.escape_decode(line.strip())[0].decode("utf-8").strip('''"''')
            decoded_files.append(decoded_line)

    return decoded_files


added_files = get_changed_files("A")
modified_files = get_changed_files("M")
deleted_files = get_changed_files("D")
date = heb_date()
print(added_files)
print(modified_files)
print(deleted_files)

if any([added_files, modified_files, deleted_files]):
    content_mitmachim = f"**עדכון {date}**\n"
    if added_files:
        content_mitmachim += f"\nהתווספו הקבצים הבאים:\n* {"\n* ".join(added_files)}\n"
    if modified_files:
        content_mitmachim += f"\nהשתנו הקבצים הבאים:\n* {"\n* ".join(modified_files)}\n"
    if deleted_files:
        content_mitmachim += f"\nנמחקו הקבצים הבאים:\n* {"\n* ".join(deleted_files)}\n"
    content_yemot = content_mitmachim.replace("* ", "").replace("*", "")

    username = os.getenv("USER_NAME")
    password = os.getenv("PASSWORD")
    yemot_token = os.getenv("TOKEN_YEMOT")
    yemot_path = ""
    client = MitmachimClient(username.strip().replace(" ", "+"), password.strip())

    try:
        client.login()
        topic_id = 76899
        client.send_post(content_mitmachim, topic_id)
        send_to_yemot(content_yemot, yemot_token, yemot_path)
    finally:
        client.logout()
