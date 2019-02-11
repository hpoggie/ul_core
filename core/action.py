from ul_core.core.card import Card


class Action:
    def __init__(self, func, argTypes):
        self.func = func
        self.nArgs = func.__code__.co_argcount
        if argTypes is None:
            self.argTypes = (Card,) * self.nArgs
        else:
            self.argTypes = argTypes

    def __call__(self, *args):
        self.func(*args)
