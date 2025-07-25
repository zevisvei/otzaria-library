import os
import csv
import json

LINKS_PATH = r"C:\Users\User\Desktop\links"


def parse_range(start_index: str, end_index: str) -> tuple[list[str], list[str]]:
    start = start_index.split(":")
    end = end_index.split(":")
    if len(start) != len(end):
        for i in start:
            if len(start) > len(end):
                end.insert(0, i)
    return start, end


def split_link(link: str) -> tuple[list[str], list[str], list[str]]:
    first_part = []
    start_index = []
    end_index = []
    parts = link.split(", ")
    last_part = parts[-1]
    split_last_part = last_part.split(" ")
    parse_split_last_part = split_last_part[-1].split("-")
    # if len(parse_split_last_part) > 2:
    #     print(f"Warning: {link} has more than two parts in the last part.")
    #     print(f"Last part: {split_last_part}")
    #     raise ValueError(f"Unexpected format in link: {link}")
    if len(parse_split_last_part) == 2:
        # print(f"{link=} has a range in the last part.")
        start_index, end_index = parse_range(parse_split_last_part[0], parse_split_last_part[1])
        # print(f"{start_index=} {end_index=}")
        start_index = parse_split_last_part[0].split(":")
        end_index = parse_split_last_part[1].split(":")
        # if len(end_index) > len(start_index):
        #     print(f"Warning: {link} has more parts in the second part than in the first part.")
        #     print(f"First part: {start_index}, Second part: {end_index}")
        #     raise ValueError(f"Unexpected format in link: {link}")
        if len(start_index) != len(end_index):
            # print(f"{start_index=} {end_index=}")
            for i in start_index:
                if len(start_index) > len(end_index):
                    end_index.insert(0, i)
            # print(f"{end_index=}")
    else:
        start_index = parse_split_last_part[0].split(":")
    # print(f"{start_index=} {end_index=}")

    if len(parts) > 1:
        first_part = parts[:-1]
    if len(split_last_part) > 1:
        first_part.append(" ".join(split_last_part[:-1]))
    # if any("-" in part for part in first_part):
    #     print(f"Warning: {link} has a hyphen in the first part.")
    #     print(f"First part: {first_part}")
        # raise ValueError(f"Unexpected format in link: {link}")
    # print(split_last_part)
    # print(f"{first_part=}, {start_index=}, {end_index=}")
    return first_part, start_index, end_index


sefaria_links = []
for file in os.listdir(LINKS_PATH):
    if not file.lower().endswith(".csv"):
        continue
    file_path = os.path.join(LINKS_PATH, file)
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        if headers[0] != "Citation 1" or headers[1] != "Citation 2":
            continue
        print(headers)
        for line in reader:
            citation_1 = split_link(line[0])
            citation_2 = split_link(line[1])
            entry = {
                "Citation 1": {
                    "first_part": citation_1[0],
                    "start_index": citation_1[1],
                    "end_index": citation_1[2]
                },
                "Citation 2": {
                    "first_part": citation_2[0],
                    "start_index": citation_2[1],
                    "end_index": citation_2[2]
                },
                "Connection Type": line[2]
            }
            sefaria_links.append(entry)

with open("sefaria_links.json", "w", encoding="utf-8") as f:
    json.dump(sefaria_links, f, ensure_ascii=False, indent=4)

otzaria_links = []
refs_file_path = r"C:\Users\User\Desktop\אוצריא\refs_all.csv"
with open(refs_file_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    headers = next(reader)
    print(headers)
    for row in reader:
        ref = split_link(row[0])
        otzaria_links.append({
            "first_part": ref[0],
            "start_index": ref[1],
            "end_index": ref[2],
            "he_ref": row[1],
            "otzaria_line": row[2],
            "file_name": row[3],
        })
with open("otzaria_links.json", "w", encoding="utf-8") as f:
    json.dump(otzaria_links, f, ensure_ascii=False, indent=4)
