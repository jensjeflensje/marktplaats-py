from __future__ import annotations

import json
from pathlib import Path
from string import ascii_lowercase

from bs4 import BeautifulSoup, Tag
from requests import get


def parse(url: str) -> BeautifulSoup:
    resp = get(url, timeout=15)
    return BeautifulSoup(resp.text, "html.parser")


def main() -> None:
    print("Finding L1 categories... ", end="", flush=True)
    l1_categories = {}

    url = "https://www.marktplaats.nl/"
    soup = parse(url)
    print(f"(url: {url}) ", end="", flush=True)
    ul = soup.find("ul", {"class": "CategoriesBlock-list"})
    assert isinstance(ul, Tag)
    for li in ul.children:
        assert isinstance(li, Tag)
        a = next(iter(li.children))
        assert isinstance(a, Tag)
        href = a["href"]
        assert isinstance(href, str)
        _, _, id_, _ = href.split("/", 3)
        l1_categories[a.text.lower()] = {
            "id": int(id_),
            "name": a.text,
        }

    print(f"Found {len(l1_categories)}")

    print("Finding L2 categories...")
    l2_categories = {}

    for l1_category in l1_categories.values():
        assert isinstance(l1_category["name"], str)

        print(f"Finding for {l1_category['name']}... ", end="", flush=True)

        # Replace some characters with dashes
        stub = (
            l1_category["name"]
            .lower()
            .replace(" | ", "-")
            .replace(" ", "-")
            .replace("'", "-")
        )
        # And remove any leftover characters
        stub = "".join(filter(lambda c: c in ascii_lowercase + "-", stub))
        url = f"https://www.marktplaats.nl/l/{stub}/"
        soup = parse(url)
        print(f"(url: {url}) ", end="", flush=True)
        data = soup.find("script", {"id": "__NEXT_DATA__"})
        assert isinstance(data, Tag)
        data = json.loads(data.text)
        cats = data["props"]["pageProps"]["searchRequestAndResponse"][
            "searchCategoryOptions"
        ]
        for cat in cats:
            if (
                # The L1 category itself
                cat["id"] == l1_category["id"]
            ):
                continue
            l2_categories[cat["fullName"].lower()] = {
                "id": cat["id"],
                "name": cat["fullName"],
                "parent": l1_category["name"],
            }
        found = len(
            list(
                filter(
                    lambda x: x["parent"] == l1_category["name"], l2_categories.values()
                )
            )
        )
        print(f"Found {found}")
        if found == 0:
            msg = f"Found no L2 categories for {l1_category['name']}"
            raise Exception(msg)

    print(f"Found in total {len(l2_categories)}")

    print("Writing to files... ", end="", flush=True)

    with Path("l1_categories.json").open("w", encoding="utf-8") as file:
        json.dump(l1_categories, file)

    with Path("l2_categories.json").open("w", encoding="utf-8") as file:
        json.dump(l2_categories, file)

    print("Done")


if __name__ == "__main__":
    main()
