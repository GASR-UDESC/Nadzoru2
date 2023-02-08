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

class NotEquivalentEventsError(NadzoruError):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        print(self.args[0])
        print(type(self.args[0]))
        names = ", ".join(str(s) for s in self.args[0])
        return f"Error: The following events does not have the same parameters in all automata: {names} "
        

 