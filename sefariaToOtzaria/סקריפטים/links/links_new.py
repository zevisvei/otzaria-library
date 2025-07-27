import os
import csv
from collections import defaultdict
import json
from typing import TypedDict, Generator

from tqdm import tqdm


class Link(TypedDict):
    first_part: list[str]
    start_index: list[int]
    end_index: list[int]


# class OtzariaLink(TypedDict):
#     line_index_1: int
#     line_index_2: int
#     heRef_2: str
#     path_2: str
#     Conection_Type: str

OtzariaLink = TypedDict("OtzariaLink", {"line_index_1": int, "line_index_2": int, "heRef_2": str, "path_2": str, "Conection Type": str})


LINKS_PATH = r"C:\Users\User\Desktop\links"
set_links: set[str] = set()
set_range: set[str] = set()
otzaria_links: defaultdict[str, list[list[str]]] = defaultdict(list)
otzaria_parse: defaultdict[str, list[Link]] = defaultdict(list)
all_otzaria_links: defaultdict[str, list[list[str]]] = defaultdict(list)
final_links: defaultdict[str, list[OtzariaLink]] = defaultdict(list)
target_links_path = "links"
not_found_links: set[str] = set()
not_found_books: set[str] = set()
found_links: set[str] = set()
found_links_dict = {}


def match_range(
        otzaria_link: list[int],
        sefaria_start_range: list[int],
        sefaria_end_range: list[int]
) -> bool:
    if any([not isinstance(x, int)
            for link in [otzaria_link, sefaria_start_range, sefaria_end_range]
            for x in link]):
        return False
    common_len = min(len(sefaria_start_range), len(sefaria_end_range), len(otzaria_link))
    return sefaria_start_range[:common_len] <= otzaria_link[:common_len] <= sefaria_end_range[:common_len]
    # for start, end, link in zip(sefaria_start_range, sefaria_end_range, otzaria_link):
    #     if not start <= link <= end:  # type: ignore צריך לתקן למקרה שהפסוק קטן מהפסוק שבפרק הקודם.
    #         return False
    # return True


def match_links(sefaria_start_range: list[int] | list[str], otzaria_link: list[int] | list[str]) -> bool:
    common_len = min(len(sefaria_start_range), len(otzaria_link))
    if sefaria_start_range[:common_len] == otzaria_link[:common_len]:
        return True
    return False


def get_best_match(otzaria_links: list[Link]) -> list[Link]:
    max_length = max(len(link["start_index"]) for link in otzaria_links)
    best_results = [i for i in otzaria_links if len(i["start_index"]) == max_length]
    best_results.sort(key=lambda x: x["start_index"])
    return best_results


def get_best_match_with_first_part(otzaria_links: list[Link]) -> list[Link]:
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


def split_link(link: str) -> Link:
    first_part = []
    start_index = []
    end_index = []
    parts = link.split(", ")
    last_part = parts[-1]
    if len(parts) == 1:
        last_part = parts[-1]
        parts = []
        # return {"first_part": parts, "start_index": [], "end_index": []}
    split_last_part = last_part.split(" ")
    parse_split_last_part = split_last_part[-1].split("-")
    if len(parse_split_last_part) == 2:
        start_index, end_index = parse_range(parse_split_last_part[0], parse_split_last_part[1])
        start_index = parse_split_last_part[0].split(":")
        end_index = parse_split_last_part[1].split(":")

        if len(start_index) != len(end_index):
            for index, i in enumerate(start_index):
                if len(start_index) > len(end_index):
                    end_index.insert(index, i)
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


def read_links() -> Generator[list[str]]:
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
                yield line


for line in read_links():
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
    for line in tqdm(reader):
        parse = split_link(line[0].strip())
        # if parse["first_part"][0] == "Shabbat" and len(parse["first_part"]) == 1:
        #     print(line)
        #     print(parse)
        all_otzaria_links[f"{", ".join(parse["first_part"])} {":".join(map(str, parse["start_index"]))}"].append(line)
        otzaria_parse[parse["first_part"][0]].append(parse)
        if line[0].strip() in set_links:
            otzaria_links[line[0].strip()].append(line)
            set_links.remove(line[0].strip())
num = len(set_links)

print(f"{num=}")
set_links_copy = set_links.copy()
for i in tqdm(set_links):
    parse = split_link(i)
    if parse["first_part"][0] in otzaria_parse:
        not_found_links.add(i)
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
            # otzaria_links[i] = [all_otzaria_links[f"{", ".join(best_match[0]["first_part"])} {":".join(map(str, best_match[0]["start_index"]))}"]] if best_match else []
            otzaria_links[i].extend([otzaria_link
                                    for otzaria_link in all_otzaria_links[f"{", ".join(best_match[0]["first_part"])} {":".join(map(str, best_match[0]["start_index"]))}"]]
                                    if best_match else []
                                    )
            set_links_copy.remove(i)
            found_links.add(i)
            found_links_dict[i] = [all_otzaria_links[f"{", ".join(best_match[0]["first_part"])} {":".join(map(str, best_match[0]["start_index"]))}"]] if best_match else []

        num -= 1
    else:
        not_found_books.add(parse["first_part"][0])
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
            # print(parse["first_part"][0])
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
            # print(f"{result=}")
            # result_link = max(result, key=lambda x: len(x["start_index"]))
            # otzaria_links[i] = [all_otzaria_links[f"{", ".join(match["first_part"])} {":".join(map(str, match["start_index"]))}"]
            #                     for match in best_match] if best_match else []
            otzaria_links[i].extend([otzaria_link
                                    for match in best_match
                                    for otzaria_link in all_otzaria_links[f"{", ".join(match["first_part"])} {":".join(map(str, match["start_index"]))}"]]
                                    if best_match else []
                                    )
            range_links_copy.remove(i)
            found_links.add(i)
            found_links_dict[i] = [all_otzaria_links[f"{", ".join(match["first_part"])} {":".join(map(str, match["start_index"]))}"]
                                   for match in best_match] if best_match else []
        else:
            not_found_links.add(i)
    else:
        not_found_books.add(parse["first_part"][0])

set_range = range_links_copy
print(f"{num=}")

for line in read_links():
    part_a = line[0]
    part_b = line[1]
    link_1 = otzaria_links.get(part_a)
    link_2 = otzaria_links.get(part_b)
    if not link_1 or not link_2:
        continue
    for link in link_1:
        final_links[link[3]].extend([{"line_index_1": int(link[2]), "line_index_2": int(link_2_link[2]), "heRef_2": link_2_link[1], "path_2": f"{link_2_link[3]}.txt", "Conection Type": line[2]}
                                     for link_2_link in link_2])
    for link in link_2:
        final_links[link[3]].extend([{"line_index_1": int(link[2]), "line_index_2": int(link_2_link[2]), "heRef_2": link_2_link[1], "path_2": f"{link_2_link[3]}.txt", "Conection Type": line[2]}
                                     for link_2_link in link_1])

os.makedirs(target_links_path, exist_ok=True)
for key, values in final_links.items():
    if os.path.exists(os.path.join(target_links_path, f"{key}.json")):
        with open(os.path.join(target_links_path, f"{key}.json"), "r", encoding="utf-8") as f:
            existing_values = json.load(f)
        values.extend(existing_values)
    with open(os.path.join(target_links_path, f"{key}.json"), "w", encoding="utf-8") as f:
        json.dump(values, f, indent=2, ensure_ascii=False)


print(f"{len(set_links)=} {len(set_range)=} {len(otzaria_links)=}")
# # print(set_links)

with open("otzaria_links_found.json", "w", encoding="utf-8") as f:
    json.dump(found_links_dict, f, ensure_ascii=False, indent=4)

with open("not_found_links.txt", "w", encoding="utf-8") as f:
    for link in not_found_links:
        f.write(f"{link}\n")
with open("not_found_books.txt", "w", encoding="utf-8") as f:
    for book in not_found_books:
        f.write(f"{book}\n")
with open("found_links.txt", "w", encoding="utf-8") as f:
    for book in found_links:
        f.write(f"{book}\n")
