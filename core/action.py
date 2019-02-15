class Action:
    def __init__(self, func, argType):
        self.func = func
        self.nArgs = func.__code__.co_argcount
        self.argType = argType

    def __call__(self, *args):
        self.func(*args)
