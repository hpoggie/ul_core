class TriggeredEffect:
    def __init__(self, owner, func):
        self.owner = owner
        self.func = func

    def resolve(self, *args):
        self.func(*args)

    @property
    def requiresTarget(self):
        return self.func.__code__.co_argcount > 0
