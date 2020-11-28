"""til module

has helper functions to manage the til library
"""
import sys
import json
import datetime
import os


def process_query(*query) -> str:
    """Processes a TIL query such as
    find <topic>
    add <link>
    add <factoid>
    """
    if len(query) <= 1:
        return "You need to give me something to do. If you want to *find* a TIL you've previously added, use `/til find <topic>`, without the `<>`."
    else:
        command, args = query[0].lower(), query[1:]
        if command == "find":
            return find_query(*args)
        elif command == "add":
            return add_query(*args)
        else:
            return f"Unrecognized command {command}. I don't know how to do that yet."


def add_query(*args):
    """Adds a query into the TIL json
    Accepted formats:

    /til add <http-link> <space separated topics>
    /til add <factoid> <space separated topics>
    /til add book <link> <space separated topics>
    """
    til_json = get_til()
    value, categories = args[0], args[1:]
    categories = [category.strip(",") for category in categories]

    is_url = (
        value.startswith("https://") or
        value.startswith("http://") or
        (not value.endswith(".") and "." in value and " " not in value)
    )
    if is_url:
        til_type = "url"
    else:
        til_type = "factoid"
    message = None
    today = datetime.date.today().strftime("%Y-%m-%d")
    for ix, til_entry in enumerate(til_json):
        # check if this TIL was already reported.
        # if it was, then just append today's date to the repeated_added_on
        til_entry_type = til_entry["type"]
        if til_entry_type == til_type:
            if til_entry["value"] == value:
                if til_entry["added_on"] != today:
                    if today not in til_entry["repeated_added_on"]:
                        til_entry["repeated_added_on"].append(today)
                        message = (
                            f"This TIL was already recorded on {til_entry['added_on']}. "
                            "Adding today's date to the `repeated_added_on` column."
                        )
                        til_json[ix] = til_entry
                if message is None:
                    message = (
                        "Try learning something else today. "
                        "You *just* learnt this thing."
                    )
                break

    if message is None:
        til_entry = dict(
            added_on=today,
            repeated_added_on=[],
            categories=sorted(categories),
            type=til_type,
            value=value
        )

        if til_type == "url":
            # TODO: add title.
            pass

        til_json.append(til_entry)
        message = "TIL {} added.".format(til_type)
    til_json = sorted(til_json, key=lambda x: x["added_on"], reverse=True)
    write_til_json(til_json)
    return message


def find_query(*args):
    """Finds a query into the TIL json"""
    args = [arg.strip(",") for arg in args]
    til_json = get_til()
    relevant_tils = []
    for til in til_json:
        categories = til["categories"]
        has_common_categories = any(
            [category in categories for category in args])
        if has_common_categories:
            relevant_tils.append(til)
        else:
            for keyword in args:
                if keyword in til["value"]:
                    relevant_tils.append(til)
    if len(relevant_tils) == 0:
        return "Sorry, I couldn't find any relevant TILs."
    else:
        response = "Found the following: \n\n{}".format(
            "\n".join(
                "{}. {} \| {} @ {}.".format(ix+1, til["type"], til["value"], til["added_on"]) for ix, til in enumerate(relevant_tils)
            ))
        return response


def get_til():
    """Returns the TIL JSON"""
    til_path = os.getenv("TIL_JSON_PATH")
    with open(til_path) as f:
        til_json = json.load(f)
    return til_json


def write_til_json(til_json):
    """Writes to the TIL JSON"""
    til_path = os.getenv("TIL_JSON_PATH")
    with open(til_path, "w") as f:
        json.dump(til_json, f, indent=4,)
