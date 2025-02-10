import requests


class SefariaApi:
    def __init__(self) -> None:
        self.base_url = "https://www.sefaria.org/api/"
        self.headers = {"accept": "application/json"}

    def table_of_contents(self) -> list:
        url = f"{self.base_url}index/"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_book(self, book_title: str, lang: str = "hebrew") -> dict:
        url = f"{self.base_url}v3/texts/{book_title}?version={lang}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_shape(self, book_title: str) -> list:
        url = f"{self.base_url}shape/{book_title}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_index(self, book_title: str) -> dict:
        url = f"{self.base_url}v2/raw/index/{book_title}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_name(self, book_title: str) -> dict:
        url = f"{self.base_url}name/{book_title}?limit=0"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_links(self, book_title: str) -> list[dict[str, str | list | dict] | None] | None:
        try:
            url = f"{self.base_url}links/{book_title}?with_text=0"
            print(book_title)
            response = requests.get(url, headers=self.headers)
            print(response.status_code)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(e)

    def get_terms(self, name: str) -> dict:
        url = f"{self.base_url}terms/{name}"
        response = requests.get(url, headers=self.headers)
        return response.json()
