import json
from collections import defaultdict
from collections.abc import Iterator, Mapping

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
            l1_category = _l1_categories_raw.get_data()[name]
        except KeyError as err:
            raise ValueError(f"Unknown L1 category name: {orig_name}") from err
        id_, name = l1_category["id"], l1_category["name"]
        return cls(id_, name)

    @classmethod
    def from_id(cls, id_: int, name: str = "Unknown"):
        cls(id_, name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, L1Category):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


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
            l2_category = _l2_categories_raw.get_data()[name]
        except KeyError as err:
            raise ValueError(f"Unknown L2 category name: {orig_name}") from err
        id_, name, parent = l2_category["id"], l2_category["name"], l2_category["parent"]
        parent = L1Category.from_name(parent)
        return cls(id_, name, parent)

    @classmethod
    def from_id(cls, id_: int, parent: L1Category, name: str = "Unknown"):
        cls(id_, name, parent)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, L2Category):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


def category_from_name(name: str) -> Union[L1Category, L2Category]:
    try:
        return L1Category.from_name(name)
    except ValueError:
        return L2Category.from_name(name)


class LazyWrapper:
    def __init__(self, filename: Path):
        self.filename = filename
        self._data = None

    def get_data(self):
        if self._data is None:
            self._build_data()
        return self._data

    def _build_data(self) -> None:
        with self.filename.open() as file:
            self._data = json.load(file)


def get_l1_categories() -> Iterator[L1Category]:
    for category in _l1_categories_raw.get_data().values():
        yield L1Category(category["id"], category["name"])


def get_l2_categories() -> Iterator[L2Category]:
    for category in _l2_categories_raw.get_data().values():
        parent = L1Category.from_name(category["parent"])
        yield L2Category(category["id"], category["name"], parent)


def get_subcategories(l1_category: L1Category) -> Iterator[L2Category]:
    return (cat for cat in get_l2_categories() if cat.parent == l1_category)


def get_l2_categories_by_parent() -> Mapping[L1Category, list[L2Category]]:
    categories = defaultdict(list)
    for category in get_l2_categories():
        categories[category.parent].append(category)
    return categories


_l1_categories_file = (Path(__file__).parent / "l1_categories.json").resolve()
_l1_categories_raw = LazyWrapper(_l1_categories_file)
_l2_categories_file = (Path(__file__).parent / "l2_categories.json").resolve()
_l2_categories_raw = LazyWrapper(_l2_categories_file)
