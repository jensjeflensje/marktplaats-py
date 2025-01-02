import json

from pathlib import Path

from typing import Union


class L1Category:
    def __init__(self, id_: int, name: str):
        self.id = id_
        self.name = name

    @classmethod
    def from_name(cls, name: str):
        orig_name = name
        name = name.lower()
        try:
            l1_category = l1_categories[name]
        except KeyError as err:
            raise ValueError(f"Unknown L1 category name: {orig_name}") from err
        id_, name = l1_category["id"], l1_category["name"]
        return cls(id_, name)

    def __str__(self):
        return self.name


class L2Category:
    def __init__(self, id_: int, name: str, parent: L1Category):
        self.id = id_
        self.name = name
        self.parent = parent

    @classmethod
    def from_name(cls, name: str):
        orig_name = name
        name = name.lower()
        try:
            l2_category = l2_categories[name]
        except KeyError as err:
            raise ValueError(f"Unknown L2 category name: {orig_name}") from err
        id_, name, parent = l2_category["id"], l2_category["name"], l2_category["parent"]
        parent = L1Category.from_name(parent)
        return cls(id_, name, parent)

    def __str__(self):
        return self.name


def category_from_name(name: str) -> Union[L1Category, L2Category]:
    try:
        return L1Category.from_name(name)
    except ValueError:
        return L2Category.from_name(name)


l1_categories_file = (Path(__file__).parent / "l1_categories.json").resolve()
l2_categories_file = (Path(__file__).parent / "l2_categories.json").resolve()

with l1_categories_file.open() as file:
    l1_categories = json.load(file)

with l2_categories_file.open() as file:
    l2_categories = json.load(file)
