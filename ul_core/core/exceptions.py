class IllegalMoveError (Exception):
    pass


class InvalidTargetError(IllegalMoveError):
    pass


class AlphaEffectError(IllegalMoveError):
    pass
