import os
import csv
from collections import defaultdict
import json

from tqdm import tqdm


LINKS_PATH = r"C:\Users\User\Desktop\links"
set_links = set()
set_range = set()
otzaria_links = {}
otzaria_parse = defaultdict(list)
all_otzaria_links = {}


def match_range(
        otzaria_link: list[int] | list[str],
        sefaria_start_range: list[int],
        sefaria_end_range: list[int]
) -> bool:
    if any([not isinstance(x, int) for x in otzaria_link]):
        return False
    for start, end, link in zip(sefaria_start_range, sefaria_end_range, otzaria_link):
        if not start <= link <= end:  # type: ignore
            return False
    return True


def match_links(sefaria_start_range: list[int] | list[str], otzaria_link: list[int] | list[str]) -> bool:
    common_len = min(len(sefaria_start_range), len(otzaria_link))
    if sefaria_start_range[:common_len] == otzaria_link[:common_len]:
        return True
    return False


def get_best_match(otzaria_links: list[dict]) -> list[dict]:
    max_length = max(len(link["start_index"]) for link in otzaria_links)
    best_results = [i for i in otzaria_links if len(i["start_index"]) == max_length]
    best_results.sort(key=lambda x: x["start_index"])
    return best_results


def get_best_match_with_first_part(otzaria_links: list[dict]) -> list[dict]:
    max_length = max(len(link["first_part"]) for link in otzaria_links)
    best_results = [i for i in otzaria_links if len(i["first_part"]) == max_length]
    return get_best_match(best_results)


def convert_ref_to_int(link_range: list[str]) -> list[int]:
    return [int(link.replace("a", "1").replace("b", "2")) for link in link_range]


def parse_range(start_index: str, end_index: str) -> tuple[list[str], list[str]]:
    start = start_index.split(":")
    end = end_index.split(":")
    if len(start) != len(end):
        for i in start:
            if len(start) > len(end):
                end.insert(0, i)
    return start, end


def split_link(link: str) -> dict[str, list[str] | list[int]]:
    first_part = []
    start_index = []
    end_index = []
    parts = link.split(", ")
    last_part = parts[-1]
    if len(parts) == 1:
        return {"first_part": parts, "start_index": [], "end_index": []}
    split_last_part = last_part.split(" ")
    parse_split_last_part = split_last_part[-1].split("-")
    if len(parse_split_last_part) == 2:
        start_index, end_index = parse_range(parse_split_last_part[0], parse_split_last_part[1])
        start_index = parse_split_last_part[0].split(":")
        end_index = parse_split_last_part[1].split(":")

        if len(start_index) != len(end_index):
            for i in start_index:
                if len(start_index) > len(end_index):
                    end_index.insert(0, i)
    else:
        start_index = parse_split_last_part[0].split(":")
    if len(parts) > 1:
        first_part = parts[:-1]
    if len(split_last_part) > 1:
        first_part.append(" ".join(split_last_part[:-1]))
    try:
        return {"first_part": first_part, "start_index": convert_ref_to_int(start_index), "end_index": convert_ref_to_int(end_index)}
    except ValueError:
        return {"first_part": first_part + start_index, "start_index": [], "end_index": []}


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
            for i in [0, 1]:
                if "-" in line[i].split(", ")[-1].split(" ")[-1]:
                    set_range.add(line[i].strip())
                else:
                    set_links.add(line[i].strip())

refs_file_path = r"C:\Users\User\Desktop\אוצריא\refs_all.csv"
print(f"{len(set_links)=} {len(set_range)=}")
with open(refs_file_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    headers = next(reader)
    print(headers)
    for line in reader:
        parse = split_link(line[0].strip())
        all_otzaria_links[line[0].strip()] = line
        otzaria_parse[parse["first_part"][0]].append(parse)
        if line[0].strip() in set_links:
            otzaria_links[line[0].strip()] = line
            set_links.remove(line[0].strip())
num = len(set_links)

print(f"{num=}")
set_links_copy = set_links.copy()
for i in tqdm(set_links):
    parse = split_link(i)
    if parse["first_part"][0] in otzaria_parse:
        # print(otzaria_parse[parse["first_part"][0]])
        result = []
        best_match = None
        for j in otzaria_parse[parse["first_part"][0]]:
            if j["first_part"] == parse["first_part"]:
                if match_links(parse["start_index"], j["start_index"]):
                    result.append(j)
        if result:
            best_match = get_best_match(result)
        else:
            for j in otzaria_parse[parse["first_part"][0]]:
                if match_links(parse["first_part"], j["first_part"]):
                    if match_links(parse["start_index"], j["start_index"]):
                        result.append(j)
            best_match = get_best_match_with_first_part(result) if result else None

        if result:
            # result_link = max(result, key=lambda x: len(x["start_index"]))
            otzaria_links[i] = f"{", ".join(best_match[0]["first_part"])} {":".join(map(str, best_match[0]["start_index"]))}" if best_match else None
            set_links_copy.remove(i)

        num -= 1
print(f"{num=}")
set_links = set_links_copy
num = len(set_range)
print(f"{num=}")
range_links_copy = set_range.copy()
for i in tqdm(set_range):
    parse = split_link(i)
    if parse["first_part"][0] in otzaria_parse:
        num -= 1
        result = []
        best_match = []
        for j in otzaria_parse[parse["first_part"][0]]:
            if j["first_part"] == parse["first_part"]:
                if match_range(j["start_index"], parse["start_index"], parse["end_index"]):
                    result.append(j)
        if result:
            best_match = result
        else:
            for j in otzaria_parse[parse["first_part"][0]]:
                if match_links(parse["first_part"], j["first_part"]):
                    if match_range(j["start_index"], parse["start_index"], parse["end_index"]):
                        result.append(j)
            best_match = get_best_match_with_first_part(result) if result else None

        if result:
            # result_link = max(result, key=lambda x: len(x["start_index"]))
            otzaria_links[i] = [all_otzaria_links[f"{", ".join(match["first_part"])} {":".join(map(str, match["start_index"]))}"] for match in best_match]
            range_links_copy.remove(i)

set_range = range_links_copy
print(f"{num=}")

print(f"{len(set_links)=} {len(set_range)=} {len(otzaria_links)=}")
# print(set_links)
with open("otzaria_links_2_range_2.json", "w", encoding="utf-8") as f:
    json.dump(otzaria_links, f, ensure_ascii=False, indent=4)
