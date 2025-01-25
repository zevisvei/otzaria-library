from .utils import to_daf, to_gematria, has_value, read_json, to_eng_daf


class Book:
    def __init__(
        self,
        book_title: str,
        lang: str,
        text_file_path: str,
        schema_file_path: str,
        he_title: str | None = None
    ) -> None:

        self.book_title = book_title
        self.metadata = {}
        self.lang = lang[:2]
        self.refs = []
        self.long_lang = lang
        self.section_names_lang = (self.lang
                                   if self.lang in ("he", "en")
                                   else "en")
        self.book_content = []
        self.text = read_json(text_file_path)
        self.schema = read_json(schema_file_path)
        self.he_title = he_title

    def get_metadata(self) -> dict[str, str]:
        era_dict = {
            "GN": {"en": "Gaonim", "he": "גאונים"},
            "RI": {"en": "Rishonim", "he": "ראשונים"},
            "AH": {"en": "Achronim", "he": "אחרונים"},
            "T": {"en": "Tannaim", "he": "תנאים"},
            "A": {"en": "Amoraim", "he": "אמוראים"},
            "CO": {"en": "Contemporary", "he": "מחברי זמננו"},
        }
        authors_list = []
        authors = self.schema.get("authors")
        if authors:
            for i in authors:
                i = i.get(self.section_names_lang)
                if i:
                    authors_list.append(i)
        if authors:
            self.metadata["authors"] = "&".join(authors_list)

        if self.section_names_lang == "he" and (
            self.he_title or self.schema.get("heTitle")
        ):
            self.metadata["title"] = self.he_title or self.schema.get("heTitle")
        else:
            self.metadata["title"] = self.book_title

        long_Desc = self.schema.get(f"{self.section_names_lang}Desc")
        ShortDesc = self.schema.get(f"{self.section_names_lang}ShortDesc")
        era = self.schema.get("era")

        if long_Desc:
            self.metadata["comments"] = long_Desc
        elif ShortDesc:
            self.metadata["comments"] = ShortDesc

        self.metadata["publisher"] = "sefaria"
        categories = self.schema.get("categories")
        he_categories = self.schema.get("heCategories")
        if he_categories and self.section_names_lang == "he":
            self.metadata["tags"] = ",".join(he_categories)
            categories = he_categories
            if not self.metadata.get("series"):
                self.metadata["series"] = he_categories[-1]
        elif categories:
            self.metadata["tags"] = ",".join(categories)
            if not self.metadata.get("series"):
                self.metadata["series"] = categories[-1]

        if era:
            era_in_dict = era_dict.get(era)
            if era_in_dict:
                if self.metadata.get("tags"):
                    self.metadata["tags"] += f",{era_in_dict[self.section_names_lang]}"
                else:
                    self.metadata["tags"] = era_in_dict[self.section_names_lang]

        self.metadata["language"] = self.lang
        return self.metadata, categories

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
        self.book_content.append(f"<h1>{self.he_title or self.schema.get("heTitle")}</h1>\n")
        authors_list = []
        authors = self.schema.get("authors")
        if authors:
            for i in authors:
                i = i.get(self.section_names_lang)
                if i:
                    authors_list.append(i)
        if authors:
            self.book_content.append(f"{' ,  '.join(authors_list)}\n")
        if self.schema["schema"].get("nodes"):
            for node in self.schema['schema']['nodes']:
                key = [self.schema["schema"]["title"]]
                if node["key"] != "default":
                    key.append(node["key"])
                self.process_node(key, node, self.text['text'][node['title']] if node['key'] != 'default' else self.text['text'][''], level=2)
        else:
            self.process_simple_book(self.schema["schema"]["title"])
        return self.book_content

    def process_simple_book(self, ref: str) -> None:
        if self.section_names_lang == "he":
            section_names = self.schema["schema"].get(
                "heSectionNames"
            )
        else:
            section_names = self.schema["schema"].get(
                "sectionNames"
            )
        depth = self.schema["schema"]["depth"]
        text = self.text.get("text")
        if text:
            if has_value(text):
                self.recursive_sections(ref, section_names, text, depth, 2)
            else:
                print(self.book_title)

    def process_node(self, key: list, node: dict, text: list, level: int = 1) -> None:
        node_title = node['heTitle'] if self.section_names_lang == "he" else node["title"]
        if node_title:
            self.book_content.append(f"<h{min(level, 6)}>{node_title}</h{min(level, 6)}>\n")
            level += 1
        if node.get("nodes"):
            for sub_node in node['nodes']:
                if node["key"] != "default":
                    key.append(node["key"])
                self.process_node(key, sub_node, text[sub_node['title']] if sub_node['key'] != 'default' else text[''], level=level)
                if node["key"] != "default":
                    key.pop()
        else:  # Process nested arrays
            if self.section_names_lang == "he":
                section_names = node.get(
                    "heSectionNames"
                )
            else:
                section_names = node.get(
                    "sectionNames"
                )
            depth = node.get('depth', 1)
            ref = ", ".join(key)
            self.recursive_sections(ref, section_names, text, depth, level)

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
        skip_section_names = ("שורה", "פירוש", "פסקה", "Line", "Comment", "Paragraph")
        """
        Recursively generates section names based on depth and appends to output list.
        :param section_names: list of section names
        :param text: input text
        :param depth: current depth of recursion
        :return: None
        """
        if depth == 0 and text != [] and not isinstance(text, bool):
            assert isinstance(text, str)
            anchor_ref_address = f"{ref} {":".join(anchor_ref)}"
            self.book_content.append(text.strip().replace("\n", "<br>") + "\n")
            self.refs.append({"ref": anchor_ref_address, "line_index": len(self.book_content)})
        elif not isinstance(text, bool):
            if depth == 1:
                assert isinstance(text, list)
            for i, item in enumerate(text, start=1):
                if has_value(item):
                    letter = ""
                    if section_names:
                        letter = (
                            to_daf(i)
                            if section_names[-depth] in ("דף", "Daf")
                            else to_gematria(i)
                        )
                    if depth > 1 and section_names and section_names[-depth] not in skip_section_names:
                        self.book_content.append(
                            f"<h{min(level, 6)}>{section_names[-depth]} {letter}</h{min(level, 6)}>\n"
                        )
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
