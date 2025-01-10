# please execute this script from the project root directory
import json


def main():
    try:
        with open("marktplaats/l1_categories.json", "r") as l1, \
                open("marktplaats/l2_categories.json", "r") as l2:
            l1_categories = json.loads(l1.read())
            l2_categories = json.loads(l2.read())
    except OSError:
        print("Category files not found! Are you executing this script from the project root?")
        return

    output = """# Categories
Categories are divided into L1 and L2 categories.
You can use either one to query listings.

Project maintainers update categories periodically to make sure they stay up-to-date.
This file acts as a human-readable index of all categories.
"""

    for l1 in l1_categories.values():
        l2 = filter(lambda e: e["parent"] == l1["name"], l2_categories.values())

        output += f"## {l1['name']} ({l1['id']})\n"
        for l2_category in l2:
            output += f"- {l2_category['name']} ({l2_category['id']})\n"

    with open("./CATEGORIES.md", "w") as file:
        file.write(output)

    print("Success!")


if __name__ == "__main__":
    main()
