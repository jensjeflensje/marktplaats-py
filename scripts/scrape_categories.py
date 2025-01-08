import json
from string import ascii_lowercase

from bs4 import BeautifulSoup, Tag
from requests import get


def parse(url: str) -> BeautifulSoup:
    resp = get(url)
    return BeautifulSoup(resp.text, "html.parser")


print("Finding L1 categories... ", end="", flush=True)
l1_categories = {}

url = "https://www.marktplaats.nl/"
soup = parse(url)
print(f"(url: {url}) ", end="", flush=True)
select = soup.find("select", {"id": "categoryId"})
for option in select.children:
    assert isinstance(option, Tag)
    if (
        # "Kies categorie:"
        option.get("disabled") is not None
        # "Alle categorieën…"
        or option["value"] == "0"
    ):
        continue
    l1_categories[option.text.lower()] = {
        "id": int(option["value"]),
        "name": option.text,
    }

print(f"Found {len(l1_categories)}")


print("Finding L2 categories...")
l2_categories = {}

for l1_category in l1_categories.values():
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
    select = soup.find("select", {"id": "categoryId"})
    for option in select.children:
        assert isinstance(option, Tag)
        if (
            # "Kies categorie:"
            option.get("disabled") is not None
            # "Alle categorieën…"
            or option["value"] == "0"
            # The L1 category itself
            or int(option["value"]) == l1_category["id"]
        ):
            continue
        l2_categories[option.text.lower()] = {
            "id": int(option["value"]),
            "name": option.text,
            "parent": l1_category["name"],
        }
    found = len(list(filter(lambda x: x["parent"] == l1_category["name"], l2_categories.values())))
    print(f"Found {found}")
    if found == 0:
        raise Exception(f"Found no L2 categories for {l1_category['name']}")

print(f"Found in total {len(l2_categories)}")

print("Writing to files... ", end="", flush=True)

with open("l1_categories.json", "w") as file:
    json.dump(l1_categories, file)

with open("l2_categories.json", "w") as file:
    json.dump(l2_categories, file)

print("Done")
