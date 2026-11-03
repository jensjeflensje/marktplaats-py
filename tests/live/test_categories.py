from __future__ import annotations

import pytest

from marktplaats import SearchQuery
from marktplaats.categories import (
    L1Category,
    L2Category,
    get_l1_categories,
    get_subcategories,
)


"""
Live tests (sent to Marktplaats) to check that the bundled category data
still matches Marktplaats, and that filtering by category works.

New categories on Marktplaats don't fail these tests, the weekly
update-categories workflow picks those up. Categories that were removed
or renamed do fail, because searching with them no longer works.
"""

L1_CATEGORIES = list(get_l1_categories())


def _category_options(search: SearchQuery) -> dict[int, str]:
    return {
        option["id"]: option["fullName"]
        for option in search.body_json["searchCategoryOptions"]
    }


@pytest.mark.smoke
def test_l1_categories_still_exist() -> None:
    # A search without a category lists all L1 categories
    live = _category_options(SearchQuery("fiets", limit=1))

    missing = {c.id: c.name for c in L1_CATEGORIES if c.id not in live}
    renamed = {
        c.id: (c.name, live[c.id])
        for c in L1_CATEGORIES
        if c.id in live and live[c.id] != c.name
    }
    assert not missing, f"L1 categories no longer on Marktplaats: {missing}"
    assert not renamed, f"L1 categories renamed (bundled, live): {renamed}"


@pytest.mark.parametrize("l1", L1_CATEGORIES, ids=str)
def test_l2_categories_still_exist(l1: L1Category) -> None:
    # A search in an L1 category lists its L2 categories
    live = _category_options(SearchQuery(category=l1, limit=1))
    bundled = list(get_subcategories(l1))

    assert bundled
    missing = {c.id: c.name for c in bundled if c.id not in live}
    renamed = {
        c.id: (c.name, live[c.id])
        for c in bundled
        if c.id in live and live[c.id] != c.name
    }
    assert not missing, f"L2 categories in {l1} no longer on Marktplaats: {missing}"
    assert not renamed, f"L2 categories in {l1} renamed (bundled, live): {renamed}"


@pytest.mark.parametrize("l1", L1_CATEGORIES, ids=str)
def test_l1_category_filter(l1: L1Category) -> None:
    search = SearchQuery(category=l1, limit=30)
    listings = search.get_listings()
    # Compare with Marktplaats' own list instead of the bundled data,
    #  which is missing some categories (see below).
    allowed = set(_category_options(search))

    assert listings, f"No listings in {l1}"
    outside = {listing.category_id for listing in listings} - allowed
    assert not outside, f"Listings outside {l1}: category ids {outside}"


@pytest.mark.parametrize("l1", L1_CATEGORIES, ids=str)
def test_l2_category_filter(l1: L1Category) -> None:
    # Regression test for #235: the L2 category used to be ignored,
    #  which returned listings from the whole L1 category.
    # Pick the L2 category of a listing in this L1, so it has listings.
    search = SearchQuery(category=l1, limit=1)
    (listing,) = search.get_listings()
    name = _category_options(search)[listing.category_id]
    l2 = L2Category(listing.category_id, name, l1)

    listings = SearchQuery(category=l2, limit=30).get_listings()

    assert listings
    assert all(listing.category_id == l2.id for listing in listings), (
        f"Listings outside {l2}: category ids { ({x.category_id for x in listings}) }"
    )


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("Fietsen | Mountainbikes en ATB", marks=pytest.mark.smoke),
        "Volkswagen",
        "Windows Laptops",
        "Games | Nintendo Switch",
    ],
)
@pytest.mark.parametrize("query", ["", "zwart"])
def test_l2_category_filter_with_query(name: str, query: str) -> None:
    category = L2Category.from_name(name)
    listings = SearchQuery(query, category=category, limit=30).get_listings()

    assert listings
    assert all(listing.category_id == category.id for listing in listings)


def test_l2_filter_is_narrower_than_l1() -> None:
    l2 = L2Category.from_name("Fietsen | Mountainbikes en ATB")
    l1_total = SearchQuery(category=l2.parent).total_result_count
    l2_total = SearchQuery(category=l2).total_result_count

    assert isinstance(l1_total, int)
    assert isinstance(l2_total, int)
    assert 0 < l2_total < l1_total


@pytest.mark.xfail(
    strict=True,
    reason=(
        "scrape_categories.py keys L2 categories by name only, and some names "
        "exist in several L1 categories (e.g. 'Carkits' in Auto diversen and "
        "Telecommunicatie), so all but one of them are dropped"
    ),
)
def test_bundled_data_has_every_l2_category() -> None:
    bundled = {c.id for l1 in L1_CATEGORIES for c in get_subcategories(l1)}
    missing = {}
    for l1 in L1_CATEGORIES:
        live = _category_options(SearchQuery(category=l1, limit=1))
        live.pop(l1.id, None)  # The L1 category itself
        missing.update({i: f"{l1} > {n}" for i, n in live.items() if i not in bundled})
    assert not missing, f"{len(missing)} L2 categories missing: {missing}"
