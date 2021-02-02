"""til module

has helper functions to manage the til library
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys
from contextlib import contextmanager

import bs4
import urllib3
import discord


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
            title = get_url_title(url=value)
            if title is None:
                title = value
                til_entry["title"] = value
                message = "TIL {} added. URL: {}. Unable to retrieve page title.".format(
                    til_type, value)
            else:
                til_entry["title"] = title
                message = "TIL {} added. Page Title: `{}`".format(
                    til_type, title)
        else:
            message = "TIL {} added.".format(til_type)
        til_json.append(til_entry)
    til_json = sorted(til_json, key=lambda x: x["added_on"], reverse=True)
    write_til_json(til_json)
    generate_til_page()
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
        length = len(relevant_tils)
        if length > 1:
            response = ["Found {} matching TILs.".format(length)]
        else:
            response = []
        for til in relevant_tils:
            type_ = til["type"]
            value = til["value"]

            date = til["added_on"]
            if type_ == "url":
                title = til.get("title", "No Page Title")
                item_embed = discord.Embed(
                    title="URL TIL @ {}".format(date),
                    description=title,
                    url=value
                )
            else:
                item_embed = discord.Embed(
                    title="Factoid TIL @ {}".format(date),
                    description=value
                )
            response.append(item_embed)

        return response


def get_til():
    """Returns the TIL JSON"""

    blog_path = pathlib.Path(os.getenv("BLOG_PATH"))
    with cwd(blog_path):
        output = subprocess.Popen(["git", "pull"])
        stdout, stderr = output.communicate()
    til_path = os.getenv("TIL_JSON_PATH")
    with open(til_path) as f:
        til_json = json.load(f)
    return til_json


def write_til_json(til_json):
    """Writes to the TIL JSON and pushes the file to github."""
    til_path = pathlib.Path(os.getenv("TIL_JSON_PATH"))
    with open(til_path, "w") as f:
        json.dump(til_json, f, indent=4,)

    blog_path = pathlib.Path(os.getenv("BLOG_PATH"))

    if not til_path.is_relative_to(blog_path):
        raise EnvironmentError((
            "The TIL file {} needs to be "
            "in the blog folder {}."
        ).format(
            til_path, blog_path))
    with cwd(blog_path):
        commit_message = "TIL updated by sarathi-bot."
        output = subprocess.Popen(["git", "pull"])
        stdout, stderr = output.communicate()
        output = subprocess.Popen(
            ["git", "commit", "-m", commit_message, "assets/til.json"])
        stdout, stderr = output.communicate()
        output = subprocess.Popen(["git", "push"])
        stdout, stderr = output.communicate()
    return output.returncode == 0


@contextmanager
def cwd(path):
    """Context manager that allows switching to a directory and changing back."""
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


def generate_til_page():
    """Generates the TIL page"""
    from jinja2 import Template
    template_file = os.getenv("TIL_JINJA_TEMPLATE_PATH")
    with open(template_file) as f:
        template_str = f.read()

    template = Template(template_str)
    til_json = get_til()
    dates = list(sorted(set(x["added_on"] for x in til_json), reverse=True))
    til_json_grouped = {}
    for date in dates:
        til_json_grouped[date] = sorted(
            [x for x in til_json if x["added_on"] == date],
            key=lambda y: y.get(
                "title",
                "{} {}".format(y["type"], y["value"]))
        )

    til_file = pathlib.Path(os.getenv("TIL_FILE_PATH"))
    with open(til_file, "w") as f:
        template_rendered = template.render(
            dates=dates,
            til_json=til_json_grouped)
        f.write(template_rendered)
    blog_path = pathlib.Path(os.getenv("BLOG_PATH"))
    if not til_file.is_relative_to(blog_path):
        raise EnvironmentError((
            "The TIL file {} needs to be "
            "in the blog folder {}."
        ).format(
            til_file, blog_path))
    with cwd(blog_path):
        commit_message = "TIL page updated by sarathi-bot."
        output = subprocess.Popen(["git", "pull"])
        stdout, stderr = output.communicate()
        output = subprocess.Popen(
            ["git", "commit", "-m", commit_message, "pages/til.md"])
        stdout, stderr = output.communicate()
        output = subprocess.Popen(["git", "push"])
        stdout, stderr = output.communicate()
    return output.returncode == 0


def get_url_title(url):
    """Returns the title of the page"""
    http = urllib3.PoolManager()
    try:
        r = http.request("GET", url)
        text = r.data.decode("utf-8", "ignore")
    except (
            UnicodeDecodeError,
            urllib3.exceptions.MaxRetryError,
            urllib3.exceptions.LocationValueError):
        sys.stderr.write(f"Getting title for `{url}` FAILED.")
        return None
    else:
        soup = bs4.BeautifulSoup(text, "lxml")
        if soup.title is None:
            sys.stderr.write(f"`{url}` has no title.")
            return None
        return soup.title.string.replace("\n", " ").replace("  ", " ").strip()


def fix_urls():
    """Fix URL entries so that they have a title"""
    import progressbar
    til_json = get_til()
    for ix, til_entry in progressbar.progressbar(enumerate(til_json), max_value=len(til_json)):
        til_type = til_entry["type"]
        if til_type == "url":
            if (title := til_entry.get("title")) is None:
                url = til_entry["value"]
                title = get_url_title(url)
                if title is not None:
                    til_entry["title"] = title
                    til_json[ix] = til_entry
                else:
                    sys.stderr.write(f"Failed getting title for `{url}`")
    write_til_json(til_json)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    fix_urls()
    generate_til_page()
