from __future__ import annotations

import pytest

from marktplaats import category_from_name
from marktplaats.categories import (
    L1Category,
    L2Category,
    get_l1_categories,
    get_l2_categories,
    get_l2_categories_by_parent,
    get_subcategories,
)


"""Tests for looking up categories from the bundled category data."""


@pytest.mark.parametrize(
    ("name", "expected_id", "expected_name"),
    [
        ("Fietsen en Brommers", 445, "Fietsen en Brommers"),
        ("fietsen en brommers", 445, "Fietsen en Brommers"),
        ("FIETSEN EN BROMMERS", 445, "Fietsen en Brommers"),
        ("Auto's", 91, "Auto's"),
        ("Computers en Software", 322, "Computers en Software"),
        ("Antiek en Kunst", 1, "Antiek en Kunst"),
    ],
)
def test_l1_from_name(name: str, expected_id: int, expected_name: str) -> None:
    category = L1Category.from_name(name)
    assert category.id == expected_id
    assert category.name == expected_name
    assert str(category) == expected_name


@pytest.mark.parametrize(
    ("name", "expected_id", "expected_parent_id"),
    [
        ("Fietsen | Mountainbikes en ATB", 460, 445),
        ("fietsen | mountainbikes en atb", 460, 445),
        ("Volkswagen", 157, 91),
        ("Windows Laptops", 339, 322),
        ("Beschrijfbare discs", 1415, 322),
        ("Antiek | Bestek", 2, 1),
        ("Games | Nintendo Switch", 2942, 356),
    ],
)
def test_l2_from_name(name: str, expected_id: int, expected_parent_id: int) -> None:
    category = L2Category.from_name(name)
    assert category.id == expected_id
    assert isinstance(category.parent, L1Category)
    assert category.parent.id == expected_parent_id
    assert str(category) == category.name


@pytest.mark.parametrize(
    "name", ["", "Fietsen", "Not a category", "Volkswagen", "Fietsen en Brommers "]
)
def test_l1_unknown_name(name: str) -> None:
    with pytest.raises(ValueError, match=r"^Unknown L1 category name: "):
        L1Category.from_name(name)


@pytest.mark.parametrize("name", ["", "Not a category", "Fietsen en Brommers"])
def test_l2_unknown_name(name: str) -> None:
    with pytest.raises(ValueError, match=r"^Unknown L2 category name: "):
        L2Category.from_name(name)


@pytest.mark.parametrize(
    ("name", "expected_type", "expected_id"),
    [
        ("Fietsen en Brommers", L1Category, 445),
        ("Auto's", L1Category, 91),
        ("Fietsen | Mountainbikes en ATB", L2Category, 460),
        ("Volkswagen", L2Category, 157),
        ("windows laptops", L2Category, 339),
    ],
)
def test_category_from_name(
    name: str, expected_type: type[L1Category | L2Category], expected_id: int
) -> None:
    category = category_from_name(name)
    assert type(category) is expected_type
    assert category.id == expected_id


def test_category_from_name_unknown() -> None:
    # Falls through to the L2 lookup, so that's the error you get
    with pytest.raises(ValueError, match=r"^Unknown L2 category name: Nope$"):
        category_from_name("Nope")


def test_l1_equality_and_hash() -> None:
    a = L1Category(445, "Fietsen en Brommers")
    b = L1Category(445, "Other name, same id")
    c = L1Category(91, "Auto's")
    assert a == b
    assert a != c
    assert a != 445
    assert len({a, b, c}) == 2


def test_l2_equality_and_hash() -> None:
    parent = L1Category(445, "Fietsen en Brommers")
    a = L2Category(460, "Fietsen | Mountainbikes en ATB", parent)
    b = L2Category(460, "Other name, same id", parent)
    c = L2Category(464, "Something else", parent)
    assert a == b
    assert a != c
    # An L1 and L2 category with the same id are not the same
    assert L1Category(460, "x") != a
    assert len({a, b, c}) == 2


def test_get_l1_categories() -> None:
    categories = list(get_l1_categories())
    assert len(categories) >= 30
    assert all(isinstance(c, L1Category) for c in categories)
    ids = [c.id for c in categories]
    assert len(ids) == len(set(ids)), "Duplicate L1 ids"
    assert 445 in ids


def test_get_l2_categories() -> None:
    categories = list(get_l2_categories())
    assert len(categories) >= 1000
    assert all(isinstance(c, L2Category) for c in categories)
    ids = [c.id for c in categories]
    assert len(ids) == len(set(ids)), "Duplicate L2 ids"

    l1_ids = {c.id for c in get_l1_categories()}
    assert all(c.parent.id in l1_ids for c in categories)


@pytest.mark.parametrize(
    ("l1_name", "contains"),
    [
        ("Fietsen en Brommers", "Fietsen | Mountainbikes en ATB"),
        ("Auto's", "Volkswagen"),
        ("Computers en Software", "Windows Laptops"),
    ],
)
def test_get_subcategories(l1_name: str, contains: str) -> None:
    parent = L1Category.from_name(l1_name)
    subcategories = list(get_subcategories(parent))
    assert subcategories
    assert all(c.parent == parent for c in subcategories)
    assert contains in {c.name for c in subcategories}


def test_every_l1_category_has_subcategories() -> None:
    by_parent = get_l2_categories_by_parent()
    for l1 in get_l1_categories():
        assert by_parent[l1], f"{l1} has no L2 categories"


def test_get_l2_categories_by_parent_is_complete() -> None:
    by_parent = get_l2_categories_by_parent()
    assert sum(len(v) for v in by_parent.values()) == len(list(get_l2_categories()))
    for parent, children in by_parent.items():
        assert all(child.parent == parent for child in children)


@pytest.mark.parametrize(
    ("args", "expected_id", "expected_name"),
    [
        ((445, "Fietsen en Brommers"), 445, "Fietsen en Brommers"),
        ((91,), 91, "Unknown"),
        ((999999, "Not bundled"), 999999, "Not bundled"),
    ],
)
def test_l1_from_id(
    args: tuple[int] | tuple[int, str], expected_id: int, expected_name: str
) -> None:
    category = L1Category.from_id(*args)
    assert isinstance(category, L1Category)
    assert category.id == expected_id
    assert category.name == expected_name
    # Equal to the bundled category with the same id
    if expected_id == 445:
        assert category == L1Category.from_name("Fietsen en Brommers")


@pytest.mark.parametrize(
    ("id_", "name", "expected_name"),
    [
        (460, "Fietsen | Mountainbikes en ATB", "Fietsen | Mountainbikes en ATB"),
        (464, None, "Unknown"),
        (999999, "Not bundled", "Not bundled"),
    ],
)
def test_l2_from_id(id_: int, name: str | None, expected_name: str) -> None:
    parent = L1Category(445, "Fietsen en Brommers")
    category = (
        L2Category.from_id(id_, parent)
        if name is None
        else L2Category.from_id(id_, parent, name)
    )
    assert isinstance(category, L2Category)
    assert category.id == id_
    assert category.name == expected_name
    assert category.parent is parent
