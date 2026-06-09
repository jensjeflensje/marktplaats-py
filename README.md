# marktplaats-py
A small Python package to request listings from marktplaats.nl. It supports python 3.10+.

## Installing
```shell
pip install marktplaats
```

## Example
### Basics
This is an example on how to use the library:
```py
from datetime import datetime, timedelta

from marktplaats import Condition, SearchQuery, SortBy, SortOrder, category_from_name

search = SearchQuery(
    query="gazelle",  # Search query. Can be left out, but then category must be specified.
    zip_code="1016LV",  # Zip code to base distance from
    distance=100000,  # Max distance from the zip code for listings
    price_from=0,  # Lowest price to search for
    price_to=100,  # Highest price to search for
    limit=5,  # Max listings (page size, max 100)
    offset=0,  # Offset for listings (page * limit)
    sort_by=SortBy.OPTIMIZED,  # DATE, PRICE, LOCATION, OPTIMIZED
    sort_order=SortOrder.ASC,  # ASCending or DESCending
    condition=Condition.NEW,  # NEW, AS_GOOD_AS_NEW, USED or category-specific
    offered_since=datetime.now() - timedelta(days=7),  # Filter listings since a point in time
    category=category_from_name("Fietsen en Brommers"),  # Filter in specific category (L1) or subcategory (L2)
)

listings = search.get_listings()

for listing in listings:
    print(listing.title)
    print(listing.description)
    print(listing.price)
    print(listing.price_as_string(lang="nl"))
    print(listing.price_type)
    print(listing.link)

    # the location object
    print(listing.location)

    # the seller object
    print(listing.seller)

    # the date object
    print(listing.date)

    # the full seller object (another request)
    print(listing.seller.get_seller())

    # medium-sized cover image
    print(listing.first_image.medium)

    # image urls for all the listing's image
    # (this sends another HTTP request)
    for image in listing.get_images():
        print(image)

    print("-----------------------------")
```

### Advanced
More advanced usage examples:

```python
from marktplaats import L1Category, category_from_name, get_l1_categories, get_l2_categories, get_l2_categories_by_parent, get_subcategories

# List all level 1 categories.
for cat in get_l1_categories():
    print(cat.name, cat.id)  # E.g. `Antiek en Kunst 1`

# List all level 2 categories.
for cat in get_l2_categories():
    print(cat.name, cat.id, cat.parent)  # E.g. `Antiek | Bestek 2 Antiek en Kunst`

# Get a level 1 or 2 category by name.
vacation = category_from_name("Vakantie")
print(vacation.name, vacation.id)  # E.g. `Vakantie 856`

# List level 2 categories for a specific level 1 category.
books = L1Category(201, "Boeken")
for cat in get_subcategories(books):
    print(cat.name, cat.id, cat.parent)  # E.g. `Biografieën 205 Boeken`

# Map level 1 categories to their level 2 subcategories.
l1_to_l2_mapping = get_l2_categories_by_parent()
for l1_cat in l1_to_l2_mapping:
    print(l1_cat.name, l1_cat.id, "-" * 60)  # E.g. `Diversen 428 ------`
    for l2_cat in l1_to_l2_mapping[l1_cat]:
        print(l2_cat.name, l2_cat.id, l2_cat.parent)  # E.g. `Kerst 436 Diversen`
```

## Categories
Filtering by Marktplaats category is possible. Please refer to the categories index at [CATEGORIES.md](./CATEGORIES.md)
