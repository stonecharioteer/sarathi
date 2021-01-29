"""til module

has helper functions to manage the til library
"""

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys
import textwrap
from contextlib import contextmanager

import bs4
import discord
import urllib3

from sarathi.exceptions import ServerError, InvalidTILError

help_text = textwrap.dedent(
    f"""A command to help manage the today-i-learned database of my blog.
        usage: til [subcommand] ... [-m message] [-c categories] [value]

        These are the common `til` commands used in various situations:

        {"add".ljust(15, " ")}: Add a new TIL entry
        {"find".ljust(15, " ")}: Find a previous entry.

        Options and arguments:\n

        {"[subcommand]".ljust(15, " ")}: Required.
                        Choose from `add` or `find`.
        {"-m".ljust(15, " ")}: TIL message text.
                        Ignored for factoids.
                        Default: Page title for URL,
                        file name for attachments.
        {"-c".ljust(15, " ")}: Categories/tags for the TIL entry.
                        Accepts multiple.
        {"value".ljust(15, " ")}: Value for the TIL.
                        Required unless a file is attached.
                        Accepts URL, quoted string or file.
                        File read from attachment.
        """
)


def process_query(arguments, **kwargs) -> str:
    """Processes a til query"""
    # arguments is from argparse.
    subcommand = arguments.subcommand
    if subcommand == "find":
        return find_query(arguments, **kwargs)
    elif subcommand == "add":
        return add_query(arguments, **kwargs)
    else:
        raise ServerError(
            f"`{subcommand}` is an unaccounted subcommand to `til`. "
            "The `sarathi_parser` should have caught this error.")


def add_query(arguments, **kwargs):
    """Adds a query into the TIL json

    Each 'entry' is:
    {
        "message": "Some useful message",
        "categories": [
            "category-1", "category-2"
        ],
        "links": [
            {
                "url": "https://localhost-1",
                "title": "Page Title 1",
            },
            {
                "url": "https://localhost-2",
                "title": "Page Title 2",
            },
        ],

    }
    """
    testing = kwargs.get("testing")
    raw_message = kwargs.get("message")
    # TODO: Get attachment from here and use it.

    categories = arguments.category or []
    urls = arguments.url or []
    message = arguments.message
    if message is None and len(urls) == 0:
        # TODO: This needs to be accounted for in the argparsing itself.
        raise InvalidTILError(
            f"You need to provide a message or at least 1 URL for a TIL entry.")

    til_json = get_til()
    today = datetime.date.today().strftime("%Y-%m-%d")

    # check if this TIL is already in the corpus.
    response = None
    for ix, til_entry in enumerate(til_json):
        # check if this TIL was already reported.
        # if it was, then just append today's date to the repeated_added_on
        til_message = til_entry["message"]
        til_links = til_entry["links"]
        til_categories = til_entry["categories"]
        til_added_on = til_entry["added_on"]
        # check if the message string matches. Case insensitive.
        message_matches = isinstance(message, str) and isinstance(
            til_message, str) and til_message.lower() == message.lower()

        # check if one or more of the URLs in the given list were in some other TIL.
        matching_url = 0
        til_urls = [link["url"].lower() for link in til_links]

        for url in urls:
            if url.lower() in til_urls:
                matching_url += 1

        if matching_url:
            # TODO: How do I handle this?
            raise NotImplementedError(
                f"{matching_url} URL(s) match an entry from {til_added_on}."
                "While that has been detected, I am not yet sure what is "
                "the right thing to do here. This is a TODO item that "
                "I should tackle later.")

        if message_matches or matching_url:
            # url or message matches.
            if til_added_on != today:
                if today not in til_entry["repeated_added_on"]:
                    til_entry["repeated_added_on"].append(today)
                    # update categories silently if required.
                    for category in categories:
                        if category not in til_categories:
                            til_entry["categories"].append(category)
                    response = (
                        f"This TIL was already recorded on {til_added_on}. "
                        "Adding today's date to the `repeated_added_on` column."
                    )
                    til_json[ix] = til_entry
                if response is None:
                    response = (
                        "Try learning something else today. "
                        "You *just* learnt this thing."
                    )
                break

    if response is None:
        til_entry = dict(
            added_on=today,
            repeated_added_on=[],
            categories=sorted(set(categories)),
        )

        links = [dict(title=get_url_title, url=url) for url in urls]
        if message is not None:
            til_entry["message"] = message

        if links:
            til_entry["links"] = links
            response = "TIL Added. {} links included.".format(len(links))
        else:
            response = "TIL Added."
        til_json.append(til_entry)

    til_json = sorted(til_json, key=lambda x: x["added_on"], reverse=True)
    if not testing:
        write_til_json(til_json)
        generate_til_page()
        return f"Test successful. {message=}"
    return message


def find_query(arguments, **kwargs):
    """Finds a query into the TIL json"""
    categories = arguments.category or []
    domains = arguments.domains or []
    keywords = arguments.keywords
    limit = arguments.limit or 5

    if len(categories) == 0 and len(domains) == 0 and len(keywords) == 0:
        raise InvalidTILError(
            "Cannot find anything for such a filter. "
            "Ensure that the user doesn't reach this point.")

    til_json = get_til()
    relevant_tils = []
    for til in til_json:
        relevant = False

        if len(categories) > 0:
            til_categories = til["categories"]
            # check if the categories match.
            has_matching_category = any(
                [category in til_categories for category in categories])
        else:
            has_matching_category = None

        links = til.get("links", [])
        if len(domains) > 0:
            # filter for domains.
            has_matching_domain = any(
                [domain in link["url"] for link in links])
        else:
            has_matching_domain = None

        til_message = til.get("message", "")
        has_matching_keyword = any([
            # check the message and the title of every link therein.
            (
                # keyword is in the message for each keyword in keywords
                keyword.lower() in til_message.lower()
            ) or (
                # keyword is in one of the link titles for each link in links for each keyword in keywords
                keyword in link["title"] for link in links
            )
            for keyword in keywords
        ])

        relevant = has_matching_keyword or has_matching_domain or has_matching_category
        if relevant:
            relevant_tils.append(til)
    # TODO: Limit to required number of TILs and return the reponse.
    # FIXME: How do I account for multiple links in a discord response.

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
        output = subprocess.Popen(
            ["git", "pull"]
        )
        stdout, stderr = output.communicate()
        commit_message = "TIL updated by sarathi-bot."
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
        output = subprocess.Popen(
            ["git", "pull"]
        )
        stdout, stderr = output.communicate()
        commit_message = "TIL page updated by sarathi-bot."
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
        return soup.title.string


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
