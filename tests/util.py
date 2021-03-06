from ul_core.core.game import Game, Turn
from ul_core.core.event_handler import EventHandler
from ul_core.core.player import Player


def dummyFactionPlayer(deck):
    return type('DFP', (Player,), {'deck': list(deck)})


class AutoResolver(EventHandler):
    def on_any(self, game):
        game.resolveTriggeredEffects()


def newGame(*args, disableMulligans=True, eventHandler=None):
    """
    Helper function for writing cleaner tests.
    Tries to intelligently create a new game from the arguments you give it.
    If you give it 2 factions, it will make a game with those factions
    If you give it one faction, both players will be that faction
    If you give it 2 lists, it will give the players those lists as decks.
    If you give it one list, it will make that the deck for both players.
    If you give it some cards, it will make those the deck for both players.
    """
    if eventHandler is None:
        eventHandler = AutoResolver()

    def makeGame(p1Type, p2Type):
        return Game(p1Type, p2Type, eventHandler)

    if (len(args) == 2 and
            isinstance(args[0], type) and
            isinstance(args[1], type)):
        game = makeGame(*args)
    elif len(args) == 1 and isinstance(args[0], type):
        game = makeGame(args[0], args[0])
    # If we got 2 arguments and at least one of them is a list
    elif len(args) == 2 and len(
            [x for x in args if hasattr(x, '__iter__')]) > 0:
        # For each of the arguments, if it's a list, make that the player's
        # deck, otherwise make a list containing only that card and make it
        # the player's deck
        players = [dummyFactionPlayer(arg)
                   if hasattr(arg, '__iter__')
                   else dummyFactionPlayer([arg]) for arg in args]
        game = makeGame(*players)
    elif len(args) == 0:
        pl = dummyFactionPlayer([])
        game = makeGame(pl, pl)
    elif hasattr(args[0], '__iter__'):
        # if we only got one list, treat that the same as a bunch of cards
        pl = dummyFactionPlayer(args[0])
        game = makeGame(pl, pl)
    else:
        pl = dummyFactionPlayer(args)
        game = makeGame(pl, pl)

    # Disable mulligans by default
    if disableMulligans:
        game.finishMulligans()

    # Return the players for convenience
    return game, game.players[0], game.players[1]
