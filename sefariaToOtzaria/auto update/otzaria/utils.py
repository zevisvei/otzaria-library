import re
#import typing as t
from hebrew_numbers import int_to_gematria

# https://stackoverflow.com/questions/58400724/type-hint-for-nested-dict
#JsonType: t.TypeAlias = t.List['JsonValue'] | t.Dict[str, 'JsonValue']
#JsonValue: t.TypeAlias = str | JsonType


def recursive_register_categories(
    index: list | dict,
    data: list[dict[str, str | list[str]]] | None = None,
    tree: list[str] | None = None,
) -> list[dict[str, str | list[str]]]:
    if tree is None:
        tree = []
    if data is None:
        data = []
    if isinstance(index, list):
        for item in index:
            recursive_register_categories(item, data, tree)
    elif isinstance(index, dict):
        if index.get("contents"):
            tree.append(index["heCategory"])
            for item in index["contents"]:
                recursive_register_categories(item, data, tree)
            tree.pop()
        if index.get("title"):
            data.append(
                {
                    "he_title": index["heTitle"],
                    "en_title": index["title"],
                    "path": tree.copy(),
                }
            )
    return data


def sanitize_filename(filename: str) -> str:
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', "", filename)
    sanitized_filename = sanitized_filename.replace("_", " ")
    return sanitized_filename.strip()


def to_daf(i: int) -> str:
    i += 1
    if i % 2 == 0:
        return to_gematria(i//2)+'.'
    else:
        return to_gematria(i//2)+':'


def to_gematria(i: int) -> str:
    s = ''
    i = i % 1000
    j = i / 1000
    if j < 0:
        s = int_to_gematria(j, gershayim=False) + ' '
    s = s + int_to_gematria(i, gershayim=False)
    return s


def to_eng_daf(i) -> str:
    i += 1
    if i % 2 == 0:
        return str(i//2)+'a'
    else:
        return str(i//2)+'b'


def has_value(data: list):
    return any(has_value(item) if isinstance(item, list) else item for item in data)
