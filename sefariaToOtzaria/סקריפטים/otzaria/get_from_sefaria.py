from collections import defaultdict

from .sefaria_api import SefariaApi
from .utils import to_daf, to_gematria, has_value, to_eng_daf


class Book:
    def __init__(
        self,
        book_title: str,
        lang: str,
        he_title: str | None = None,
        categories: list | None = None,
        get_links: bool = True,
    ) -> None:

        self.book_title = book_title
        self.metadata = {}
        self.lang = lang[:2]
        self.long_lang = lang
        self.section_names_lang = (self.lang
                                   if self.lang in ("he", "en")
                                   else "en")
        self.book_content = []
        self.sefaria_api = SefariaApi()
        self.he_title = he_title
        self.categories = categories
        self.refs = []
        self.links = defaultdict(list)
        self.shape = self.sefaria_api.get_shape(self.book_title)
        self.get_links = get_links
        self.exists = isinstance(self.shape, list)
        if self.exists:
            self.is_complex = bool(self.shape[0].get("isComplex"))
            self.index = self.sefaria_api.get_index(self.book_title)
            self.is_complex_and_simple = bool(
                self.is_complex != bool(self.index["schema"].get("nodes"))
            )

    def get_metadata(self) -> dict[str, str] | None:
        if not self.exists:
            return
        era_dict = {
            "GN": {"en": "Gaonim", "he": "גאונים"},
            "RI": {"en": "Rishonim", "he": "ראשונים"},
            "AH": {"en": "Achronim", "he": "אחרונים"},
            "T": {"en": "Tannaim", "he": "תנאים"},
            "A": {"en": "Amoraim", "he": "אמוראים"},
            "CO": {"en": "Contemporary", "he": "מחברי זמננו"},
        }
        self.metadata["he_title"] = self.he_title or self.shape[0].get("heBook")
        self.metadata["en_title"] = self.book_title
        self.metadata["heDesc"] = self.index.get("heDesc")
        self.metadata["enDesc"] = self.index.get("enDesc")
        self.metadata["heShortDesc"] = self.index.get("heShortDesc")
        self.metadata["enShortDesc"] = self.index.get("enShortDesc")
        self.metadata["he_categories"] = self.categories
        self.metadata["en_categories"] = self.index.get("categories")
        era = self.index.get("era")
        era_value = era_dict.get(era, {})
        self.metadata["he_era"] = era_value.get("he")
        self.metadata["he_era"] = era_value.get("en")
        self.metadata["language"] = self.lang
        return self.metadata

    def set_series(self, text: dict) -> None:
        if not self.metadata.get("series"):
            if self.section_names_lang == "he" and text.get("heCollectiveTitle"):
                self.metadata["series"] = text.get("heCollectiveTitle")
            elif text.get("collectiveTitle"):
                self.metadata["series"] = text.get("collectiveTitle")
        if not self.metadata.get("series-index") and not self.metadata.get("series"):
            if text.get("order"):
                self.metadata["series-index"] = text["order"][-1]

    def process_book(self) -> list | None:
        if not self.exists:
            return

        level = self.add_heading(1, self.he_title)
        authors = self.index.get("authors", [{}])
        for lang in ["he", "en"]:
            authors_list = [i.get(lang) for i in authors if i.get(lang) is not None]
            self.metadata[f"{lang}_authors"] = ", ".join(authors_list) if authors_list else None
        authors = self.metadata["he_authors"] or self.metadata["en_authors"]
        self.book_content.append((authors if authors else "") + "\n")
        if self.is_complex:
            self.node_num = 0
            self.process_node(self.index["schema"], level=level)
        elif self.is_complex_and_simple:
            self.node_num = 0
            self.process_complex_and_simple_book(self.index["schema"], level=level)
        else:
            self.process_simple_book(level=level)
        return self.book_content

    def process_complex_and_simple_book(self, node: dict, level: int = 1) -> None:
        nodes = node["nodes"]
        key = [self.book_title]
        for node in nodes:
            if self.section_names_lang == "he":
                section_names = node.get("heSectionNames")
            else:
                section_names = node.get("sectionNames")
            node_level = level
            node_titles = node.get("titles", {})
            he_title, en_title = self.parse_titles(node_titles)
            node_title = None
            if node_titles:
                node_title = he_title if self.section_names_lang == "he" else en_title
            if node_title is None and node.get("heTitle" if self.section_names_lang == "he" else "title"):
                node_title = node.get("heTitle" if self.section_names_lang == "he" else "title")
            if node_title is None and node.get("sharedTitle"):
                node_title = self.parse_terms(node["sharedTitle"])
            node_level = self.add_heading(node_level + 1, node_title)
            depth = node["depth"]
            if node["key"] == "default":
                node_len = self.shape[0]["length"]
                ref = ", ".join(key)
                key.append(f"1-{node_len}")
                node_index = ", ".join(key)
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            else:
                key.append(en_title)
                node_index = ", ".join(key)
                ref = node_index
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            self.set_series(text)
            text = text.get("versions")
            if text:
                text = text[0]["text"]
                if has_value(text):
                    self.recursive_sections(ref, section_names, text, depth, node_level + 1)
                else:
                    print(self.book_title)
            key.pop()

    def process_simple_book(self, level: int = 1) -> None:
        index = self.index
        if self.section_names_lang == "he":
            section_names = index["schema"].get("heSectionNames")
        else:
            section_names = index.get("sectionNames")
        depth = index["schema"]["depth"]
        text = self.sefaria_api.get_book(self.book_title, self.long_lang)
        self.set_series(text)
        text = text.get("versions")
        if text:
            text = text[0]["text"]
            if has_value(text):
                self.recursive_sections(self.book_title, section_names, text, depth, level + 1)
            else:
                print(self.book_title)

    def process_node(self, node: dict, key: list | None = None, level: int = 1) -> None:
        """
        Process a given node, handling both nested nodes and nested arrays.
        :param node: the current node being processed
        :param text: the text associated with the node
        :param output: the output list to which the processed text is appended
        :return: None
        """
        if key is None:
            key = []
        node_title = None
        node_titles = node.get("titles", {})
        he_title, en_title = self.parse_titles(node_titles)
        if node_titles:
            node_title = he_title if self.section_names_lang == "he" else en_title
        if node_title is None and node.get("heTitle" if self.section_names_lang == "he" else "title"):
            node_title = node.get("heTitle" if self.section_names_lang == "he" else "title")
        if node_title is None and node.get("sharedTitle"):
            node_title = self.parse_terms(node["sharedTitle"])

        if not node_title:
            node_title = (
                self.shape[0]["chapters"][self.node_num]["heTitle"]
                if self.section_names_lang == "he"
                else self.shape[0]["chapters"][self.node_num]["title"]
            )
            node_title = node_title.split(",")[-1].strip()

        level = self.add_heading(level + 1, node_title)
        if node.get("nodes"):  # Process nested nodes
            node_key = node["key"]
            key.append(en_title)
            for sub_node in node["nodes"]:
                self.process_node(sub_node, key, level=level)
            key.pop(-1)
        else:  # Process nested arrays
            node_key = node["key"]
            depth = node.get("depth", 1)
            if node_key == "default":
                node_len = self.shape[0]["chapters"][self.node_num]["length"]
                assert isinstance(node_len, int)
                ref = ", ".join(key)
                key.append(f"1-{node_len}")
                node_index = ", ".join(key)
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            else:
                key.append(en_title)
                node_index = ", ".join(key)
                ref = node_index
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            self.set_series(text)
            if self.section_names_lang == "he":
                section_names = node.get("heSectionNames")
            else:
                section_names = node.get("sectionNames")
            text = text.get("versions")
            if text:
                text = text[0]["text"]
                if has_value(text):
                    self.recursive_sections(ref, section_names, text, depth, level + 1)
                else:
                    print(self.book_title)
            key.pop()
            self.node_num += 1

    def recursive_sections(
        self,
        ref: str,
        section_names: list | None,
        text: list,
        depth: int,
        level: int = 0,
        anchor_ref: list | None = None,
        links: bool = False
    ) -> None:

        if anchor_ref is None:
            anchor_ref = []
        if links is False and self.get_links:
            ref_links = f"{ref} {":".join(anchor_ref)}" if anchor_ref else ref
            links_dict = self.sefaria_api.get_links(ref_links)
            if links_dict is not None:
                self.parse_links(links_dict)
                links = True

        skip_section_names = ("שורה", "פירוש", "פסקה", "Line", "Comment", "Paragraph")
        """
        Recursively generates section names based on depth and appends to output list.
        :param section_names: list of section names
        :param text: input text
        :param depth: current depth of recursion
        :return: None
        """
        if depth == 0 and text != [] and not isinstance(text, bool):
            if isinstance(text, list):
                for line in text:
                    self.recursive_sections(ref, section_names, line, depth, level, anchor_ref, links)
            else:
                anchor_ref_address = f"{ref} {":".join(anchor_ref)}"
                self.book_content.append(text.strip().replace("\n", "<br>") + "\n")
                self.refs.append({"ref": anchor_ref_address, "line_index": len(self.book_content)})
        elif not isinstance(text, bool):
            if depth == 1 and isinstance(text, str):
                self.recursive_sections(ref, section_names, text, depth - 1, level, anchor_ref, links)
            else:
                for i, item in enumerate(text, start=1):
                    if has_value(item):
                        letter = ""
                        if section_names:
                            letter = to_daf(i) if section_names[-depth] in ("דף", "Daf") else to_gematria(i)

                        if depth > 1 and section_names and section_names[-depth] not in skip_section_names:
                            self.add_heading(level, f"{section_names[-depth]} {letter}")
                        elif section_names and section_names[-depth] not in skip_section_names and letter:
                            self.book_content.append(f"({letter}) ")
                    anchor_ref.append(to_eng_daf(i) if section_names[-depth] in ("דף", "Daf") else str(i))
                    self.recursive_sections(
                        ref,
                        section_names, item,
                        depth - 1, level + 1,
                        anchor_ref,
                        links
                    )
                    anchor_ref.pop()

    def parse_terms(self, term: str) -> str | None:
        terms = self.sefaria_api.get_terms(term)
        if terms.get("titles"):
            for i in terms["titles"]:
                if i.get("lang") == self.section_names_lang and i.get("primary"):
                    title = i.get("text")
                    return title

    def parse_titles(self, titles: dict) -> tuple[str, str]:
        he_title = ""
        en_title = ""
        for i in titles:
            if i.get("lang") == "he" and i.get("primary"):
                he_title = i.get("text")
            elif i.get("lang") == "en" and i.get("primary"):
                en_title = i.get("text")
        return he_title, en_title

    def parse_links(self, links: list[dict[str, str | list | dict] | None]) -> None:
        for link in links:
            link_type = link.get("type")
            ref = link.get("ref")
            anchor_ref = link.get("anchorRef")
            text = link.get("he")
            if not anchor_ref or not ref or not text:
                continue

            self.links[anchor_ref].append({"ref": ref, "link_type": link_type})

    def add_heading(self, level: int, text: str | None) -> int:
        if not text or not text.strip() or (level == 2 and text == self.he_title):
            return level - 1
        self.book_content.append(
            f"<h{min(level, 6)}>{text}</h{min(level, 6)}>\n"
        )
        return level
