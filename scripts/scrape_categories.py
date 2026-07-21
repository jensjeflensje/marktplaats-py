from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, cast

import requests


if TYPE_CHECKING:
    from marktplaats.api_types import QueryResponse


def request_api_data(extra_params: dict[str, str]) -> QueryResponse:
    """Make a request to the API, and return the JSON response."""  # ruff:ignore[docstring-missing-returns]
    url = "https://www.marktplaats.nl/lrp/api/search"
    params = {
        "limit": "1",
        **extra_params,
    }
    res = requests.get(url, params=params, timeout=15)
    res.raise_for_status()
    return cast("QueryResponse", res.json())


def main() -> None:
    """Save all L1 and L2 categories to JSON files."""  # ruff:ignore[docstring-missing-exception]
    print("Finding L1 categories... ", end="", flush=True)
    l1_categories = {}

    l1_payload = request_api_data({"query": "fiets"})

    for raw_l1_category in l1_payload["searchCategoryOptions"]:
        l1_categories[raw_l1_category["fullName"].lower()] = {
            "id": raw_l1_category["id"],
            "name": raw_l1_category["fullName"],
        }

    print(f"Found {len(l1_categories)}")

    print("Finding L2 categories...")
    l2_categories = {}

    for l1_category in l1_categories.values():
        print(f"Finding for {l1_category['name']}... ", end="", flush=True)

        l2_payload = request_api_data({"l1CategoryId": str(l1_category["id"])})

        for l2_category in l2_payload["searchCategoryOptions"]:
            if l2_category["id"] == l1_category["id"]:  # The L1 category itself
                continue
            l2_categories[l2_category["fullName"].lower()] = {
                "id": l2_category["id"],
                "name": l2_category["fullName"],
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
