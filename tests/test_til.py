from sarathi.parser import ArgParseError, sarathi_parser
import sarathi.til


def test_process_query(mocker):
    """Tests the process query function"""
    commands = [
        "til", "add",
        # "-c", "programming",
        "-u", "https://localhost",
        "-m", "This is a useful link I found today."]
    mocker.patch("sarathi.til.add_query")
    arguments = sarathi_parser.parse_args(commands)
    sarathi.til.process_query(arguments)
    sarathi.til.add_query.assert_called_once_with(arguments)
