import pytest
from sarathi.parser import sarathi_parser, ArgParseError


def test_til_parser_add_exists():
    """Tests the TIL Parser"""
    til_string = ["til", "add"]
    namespace = sarathi_parser.parse_args(til_string)
    assert namespace.command == "til", "The `til` command doesn't exist!"
    assert namespace.subcommand == "add", "The `til add` subcommand doesn't exist."


def test_til_parser_find_exists():
    """Tests the TIL Parser"""
    til_string = ["til", "find", "test"]
    namespace = sarathi_parser.parse_args(til_string)
    assert namespace.command == "til", "The `til` command doesn't exist!"
    assert namespace.subcommand == "find", "The `til find` subcommand doesn't exist."


def test_til_parser_add_simple():
    """Tests the TIL Parser"""
    til_string = ["til", "add", "-u", "https://localhost"]
    namespace = sarathi_parser.parse_args(til_string)
    assert namespace.command == "til", "The `til` command doesn't exist!"
    assert namespace.subcommand == "add", "The `til add` subcommand doesn't exist."
    assert isinstance(namespace.url, list), "The `url` should be a list"


def test_til_parser_add_multicategory_multiurl():
    """Tests that the category and url can be multiple
    when adding a TIL
    """
    til_string = [
        "til",  "add", "-m", "This is a test", "-c", "category-1", "-c", "category-2", "-u",
        "https://google.com", "-u", "https://localhost:5000"]

    namespace = sarathi_parser.parse_args(til_string)
    assert namespace.command == "til", "`til` command was not invoked."
    assert namespace.subcommand == "add", "`til add` command was not invoked."
    assert namespace.message == til_string[3], "Message was not stored in `message`."
    assert isinstance(namespace.category,
                      list), "Categories was not stored as a list."
    assert set(namespace.category) - set((til_string[5], til_string[7])) == set(
    ), "The categories are not both stored in the namespace."

    assert isinstance(
        namespace.url, list), "The urls are not stored as a list."
    assert set(namespace.url) - set((til_string[9], til_string[11])) == set(
    ), "Both URLs are not stored in the `url` property"


@pytest.mark.parametrize(
    "cmd",
    [
        (
            ["invalid-command"]
        ),
        (
            ["invalid-command", "invalid-subcommand"]
        ),
        (
            [
                "til"
            ]),
        (
            ["til", "invalid"]
        ),
        (
            ["til", "add", "invalid"]
        ),
        (
            ["til", "find"]
        ),
    ]
)
def test_parse_invalid_command(cmd):
    """Tests what happens when the arg parser
    gets an invalid command"""

    with pytest.raises(ArgParseError):
        _ = sarathi_parser.parse_args(cmd)
