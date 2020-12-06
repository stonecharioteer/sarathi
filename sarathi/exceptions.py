
class ServerError(Exception):
    """Raise this when you think there will be a server error and needs to be looked into.

    Typically used in this bot whenever the discord-facing fail-safes
    are bypassed to reach something unexpected."""


class InvalidTILError(Exception):
    """Raise this when the user tries to use a TIL without a message or a url"""
