class NoInitialStateError(Exception):
    user_message = "Error: There is no initial state"
    """Error description"""


class NoMarkedStateError(Exception):
    user_message = "Error: There is no marked state"
    """Error description"""


class TooFewArgumentsError(Exception):
    user_message = "Error: Too few arguments"
    """Error description"""
