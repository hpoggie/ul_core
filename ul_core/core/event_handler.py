import functools


class EventHandler:
    """
    Calls the callback in between function invocations

    This is basically a continuation monad
    """

    def __init__(self, callback):
        self.callback = callback

    def bind(self, func):
        """
        func should look like
        func(callback: function) -> EventHandler(callback)
        """
        return func(self.callback)

    def __rshift__(self, func):
        return self.bind(func)

    def do(self, *funcs):
        return functools.reduce(lambda x, y: x >> y, funcs, self)
