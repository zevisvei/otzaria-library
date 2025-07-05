import subprocess
import codecs
import os

from pyluach import dates
import requests

from mitmachim import MitmachimClient
from yemot import split_and_send


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
            if not decoded_line.lower().endswith(".txt") or decoded_line.lower().endswith("גירסת ספריה.txt"):
                continue
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
    date_yemot = f"עדכון {date}\n"
    content_yemot = {}
    if added_files:
        content_mitmachim += f"\nהתווספו הקבצים הבאים:\n* {"\n* ".join(added_files)}\n"
        content_yemot["התווספו הקבצים הבאים:"] = f"{"\n".join([i.split('/')[-1].split('.')[0] for i in added_files])}"
    if modified_files:
        content_mitmachim += f"\nהשתנו הקבצים הבאים:\n* {"\n* ".join(modified_files)}\n"
        content_yemot["השתנו הקבצים הבאים:"] = f"{"\n".join([i.split('/')[-1].split('.')[0] for i in modified_files])}"
    if deleted_files:
        content_mitmachim += f"\nנמחקו הקבצים הבאים:\n* {"\n* ".join(deleted_files)}\n"
        content_yemot["נמחקו הקבצים הבאים:"] = f"{"\n".join([i.split('/')[-1].split('.')[0] for i in deleted_files])}"

    username = os.getenv("USER_NAME")
    password = os.getenv("PASSWORD")
    yemot_token = os.getenv("TOKEN_YEMOT")
    google_chat_url = os.getenv("GOOGLE_CHAT_URL")
    yemot_path = "ivr2:/1"
    tzintuk_list_name = "books update"

    requests.post(google_chat_url, json={"text": content_mitmachim})

    client = MitmachimClient(username.strip().replace(" ", "+"), password.strip())

    try:
        client.login()
        topic_id = 80213
        client.send_post(content_mitmachim, topic_id)
    except Exception as e:
        print(e)
    finally:
        client.logout()

    try:
        split_and_send(content_yemot, date_yemot, yemot_token, yemot_path, tzintuk_list_name)
    except Exception as e:
        print(e)
