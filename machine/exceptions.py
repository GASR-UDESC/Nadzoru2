class NadzoruError(Exception):
    pass


class NoInitialStateError(NadzoruError):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        names = ", ".join(self.args)
        return f"Error: There is no initial state on: {names}"


class NoMarkedStateError(NadzoruError):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        names = ", ".join(self.args)
        return f"Error: There is no marked state on: {names}"


class TooFewArgumentsError(NadzoruError):
    def __str__(self):
        return "Error: Too few arguments"

class ErrorMultiplePropetiesForEventName(NadzoruError):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        if not self.args:
            return f"Error: There are multiple properties for the same event name"
        names = ", ".join(str(s) for s in self.args)
        return f"Error: The following events does not have the same parameters in all automata: {names} "

        
        

 