# VERSION: 1.0
# AUTHORS: OpenAI
# python .\torrent9.py "reacher" # for command line search
import argparse
import re
from datetime import datetime
from html.parser import HTMLParser
from typing import Callable, Dict, List, Mapping, Optional, Tuple, Union
from urllib.request import Request, urlopen
from urllib.parse import quote, unquote, urljoin

try:
    from helpers import retrieve_url
    from novaprinter import prettyPrinter
except ImportError:
    def retrieve_url(url: str) -> str:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request) as response:
            return response.read().decode("utf-8", "replace")

    def prettyPrinter(item: Mapping[str, Union[str, int]]) -> None:
        print(
            f"{item['name']}\n"
            f"  Size: {item['size']} | Seeds: {item['seeds']} | "
            f"Leech: {item['leech']}\n"
            f"  Details: {item['desc_link']}\n"
        )


class torrent9:
    url = "https://www6.torrent9.to"
    name = "Torrent9"
    supported_categories = {
        "all": "",
        "movies": "films",
        "tv": "series",
        "music": "musique",
        "books": "ebook",
        "software": "logiciels",
        "games": "jeux-pc",
    }

    @staticmethod
    def _retrieve_page(url: str) -> str:
        html = retrieve_url(url)
        if html:
            return html

        request = Request(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            },
        )
        with urlopen(request) as response:
            return response.read().decode("utf-8", "replace")

    class SearchParser(HTMLParser):
        def __init__(
            self,
            base_url: str,
            printer: Callable[[Mapping[str, Union[str, int]]], None],
        ) -> None:
            super().__init__()
            self.base_url = base_url
            self.printer = printer
            self.in_row = False
            self.in_result_table = False
            self.current_item: Dict[str, Union[str, int]] = {}
            self.current_cell = -1
            self.cell_text: List[str] = []
            self.page_items = 0

        def handle_starttag(
            self, tag: str, attrs: List[Tuple[str, Optional[str]]]
        ) -> None:
            attributes = dict(attrs)
            classes = attributes.get("class", "") or ""

            if tag == "table" and "cust-table" in classes:
                self.in_result_table = True
            elif self.in_result_table and tag == "tr":
                self.in_row = True
                self.current_cell = -1
                self.cell_text = []
                self.current_item = {
                    "engine_url": self.base_url,
                    "name": "",
                    "size": "-1",
                    "seeds": "-1",
                    "leech": "-1",
                    "pub_date": -1,
                }
            elif self.in_row and tag == "td":
                self.current_cell += 1
                self.cell_text = []
            elif self.in_row and tag == "a":
                href = attributes.get("href")
                if href and re.match(r"^/torrent/\d+/", href):
                    name = attributes.get("title", "")
                    self.current_item["desc_link"] = urljoin(self.base_url, href)
                    self.current_item["name"] = name

        def handle_data(self, data: str) -> None:
            if self.in_row and self.current_cell >= 0:
                self.cell_text.append(data)

        def handle_endtag(self, tag: str) -> None:
            if self.in_row and tag == "td":
                value = " ".join("".join(self.cell_text).split())
                if self.current_cell == 0 and value and not self.current_item.get("name"):
                    self.current_item["name"] = value
                elif self.current_cell == 1:
                    self.current_item["pub_date"] = self.parse_date(value)
                elif self.current_cell == 2:
                    self.current_item["size"] = value
                elif self.current_cell == 3:
                    self.current_item["seeds"] = self.parse_number(value)
                elif self.current_cell == 4:
                    self.current_item["leech"] = self.parse_number(value)
                self.cell_text = []
            elif self.in_row and tag == "tr":
                self.in_row = False
                if self.current_item.get("desc_link") and self.current_item.get("name"):
                    self.current_item["link"] = self.current_item["desc_link"]
                    self.printer(self.current_item)
                    self.page_items += 1
                self.current_item = {}
            elif self.in_result_table and tag == "table":
                self.in_result_table = False

        @staticmethod
        def parse_number(value: str) -> str:
            match = re.search(r"-?\d+", value)
            return match.group(0) if match else "-1"

        @staticmethod
        def parse_date(value: str) -> int:
            try:
                date = datetime.strptime(value, "%d/%m/%Y")
                return int((date - datetime(1970, 1, 1)).total_seconds())
            except ValueError:
                return -1

    class MagnetParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.magnet: Optional[str] = None

        def handle_starttag(
            self, tag: str, attrs: List[Tuple[str, Optional[str]]]
        ) -> None:
            if self.magnet is not None or tag != "a":
                return
            href = dict(attrs).get("href")
            if href and href.startswith("magnet:?"):
                self.magnet = href

    def search(
        self,
        query: str,
        cat: str = "all",
        printer: Callable[[Mapping[str, Union[str, int]]], None] = prettyPrinter,
    ) -> None:
        search_term = "-".join(unquote(query).split())
        category = self.supported_categories[cat]
        search_path = f"{category + '/' if category else ''}{quote(search_term, safe='')}"

        for page in range(1, 11):
            if page == 1:
                path = f"/search_torrent/{search_path}.html,trie-seeds-d"
            else:
                path = f"/search_torrent/{search_path}/page-{page},trie-seeds-d"

            parser = self.SearchParser(self.url, printer)
            parser.feed(self._retrieve_page(urljoin(self.url, path)))
            parser.close()
            if parser.page_items < 20:
                break

    def download_torrent(self, info: str) -> None:
        parser = self.MagnetParser()
        parser.feed(self._retrieve_page(info))
        parser.close()
        if parser.magnet is None:
            raise ValueError("Torrent9 detail page did not contain a magnet link")
        # qBittorrent expects the downloadable link followed by the source URL.
        print(f"{parser.magnet} {info}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Torrent9 and display matching torrents."
    )
    parser.add_argument("query", help="Search terms, for example: ubuntu 24.04")
    parser.add_argument(
        "--category",
        choices=sorted(torrent9.supported_categories),
        default="all",
        help="Torrent9 category (default: all)",
    )
    args = parser.parse_args()
    torrent9().search(args.query, args.category)


if __name__ == "__main__":
    main()
