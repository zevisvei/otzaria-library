from typing import Optional


def convert_ref_to_int(link_range: list[str]) -> list[int]:
    return [int(link.replace("a", "1").replace("b", "2")) for link in link_range]


def map_links(
        otzaria_link: list[int],
        sefaria_start_range: list[int],
        sefaria_end_range: Optional[list[int]] = None
) -> bool:
    if not sefaria_end_range:
        common_len = min(len(sefaria_start_range), len(otzaria_link))
        if sefaria_start_range[:common_len] == otzaria_link[:common_len]:
            return True
        return False

    for start, end, link in zip(sefaria_start_range, sefaria_end_range, otzaria_link):
        if not start <= link <= end:
            return False
    return True


start_index = convert_ref_to_int(["1", "2", "a"])
end_index = convert_ref_to_int(["1", "4", "b"])
otzaria_link = convert_ref_to_int(["1", "3", "b"])
if map_links(start_index, end_index, otzaria_link):
    print("Links match!")
else:
    print("Links do not match.")
