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
            if not decoded_line.lower().endswith(".txt"):
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
    content_yemot = f"עדכון {date}\n"
    if added_files:
        content_mitmachim += f"\nהתווספו הקבצים הבאים:\n* {"\n* ".join(added_files)}\n"
        content_yemot += f"\nהתווספו הקבצים הבאים:\n{"\n".join([i.split('/')[-1].split('.')[0] for i in added_files])}"
    if modified_files:
        content_mitmachim += f"\nהשתנו הקבצים הבאים:\n* {"\n* ".join(modified_files)}\n"
        content_yemot += f"\nהשתנו הקבצים הבאים:\n{"\n".join([i.split('/')[-1].split('.')[0] for i in modified_files])}"
    if deleted_files:
        content_mitmachim += f"\nנמחקו הקבצים הבאים:\n* {"\n* ".join(deleted_files)}\n"
        content_yemot += f"\nנמחקו הקבצים הבאים:\n{"\n".join([i.split('/')[-1].split('.')[0] for i in deleted_files])}"

    username = os.getenv("USER_NAME")
    password = os.getenv("PASSWORD")
    yemot_token = os.getenv("TOKEN_YEMOT")
    yemot_path = "ivr2:/1"
    tzintuk_list_name = "books update"

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
        if len(content_yemot) > 2000:
            send_to_yemot(content_yemot, yemot_token, yemot_path, tzintuk_list_name)
    except Exception as e:
        print(e)
