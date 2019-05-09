from . import util
from . import dummyCards
import ul_core.core.player as player
from ul_core.core.player import Player, IllegalMoveError
from ul_core.factions.templars import Templar
import ul_core.factions.base as base
from ul_core.core.event_handler import EventHandler


def deckContainsDuplicates(deck):
    for i, card in enumerate(deck):
        for card2 in deck[i + 1:]:
            if card == card2:
                return True
    return False


def testForDuplicates():
    player = Templar()
    assert not deckContainsDuplicates(player.deck)


def testForDuplicatesBetweenPlayers():
    player1 = Templar()
    player2 = Templar()

    for card1 in player1.deck:
        for card2 in player2.deck:
            assert card1 != card2


def testReveal():
    game, player, p1 = util.newGame(dummyCards.one())
    newCard = player.hand[0]
    player.play(newCard)
    player.endTurn()
    p1.endTurn()
    player.revealFacedown(newCard)
    assert newCard.zone == player.faceups


def testPlay():
    game, player, _ = util.newGame(dummyCards.one())
    newCard = player.hand[0]
    player.play(newCard)
    assert newCard.zone == player.facedowns


def testPlayFaceup():
    newCard = dummyCards.one()
    newCard.fast = True
    newCard.cost = 0
    game, player, _ = util.newGame(newCard)
    player.drawCard()
    instance = player.hand[0]
    player.playFaceup(instance)
    assert instance.zone == player.faceups


def testAttackFace():
    newCard = dummyCards.one()
    newCard.fast = True
    newCard.cost = 0
    game, player, _ = util.newGame(newCard)
    player.drawCard()
    player.playFaceup(player.hand[0])
    player.attackFace(player.faceups[0])
    assert game.players[1].manaCap == 2


def testAttackFacedown():
    newCard = dummyCards.one()
    newCard.cost = 0
    game, p0, p1 = util.newGame(newCard)
    game.start()
    # 1st player plays a facedown
    p0.play(game.players[0].hand[0])
    p0.endTurn()
    # 2nd player attacks it
    p1.hand[0].fast = True
    p1.playFaceup(p1.hand[0])
    p1.attack(p1.faceups[0], p0.facedowns[0])
    assert len(p0.facedowns) == 0
    assert len(p1.faceups) == 0


def testAttackFaceup():
    newCard = dummyCards.one()
    newCard.fast = True
    newCard.cost = 0
    game, p0, p1 = util.newGame(newCard)
    game.start()
    # 1st player plays a faceup
    p0.playFaceup(p0.hand[0])
    p0.endTurn()
    # 2nd player attacks it
    p1.playFaceup(p1.hand[0])
    p1.attack(p1.faceups[0], p0.faceups[0])
    assert len(p0.facedowns) == 0
    assert len(p1.faceups) == 0


def testMulligan():
    from copy import deepcopy

    game, p0, p1 = util.newGame([dummyCards.one() for i in range(40)],
            disableMulligans=False)
    game.start()
    game.turn = None
    hand0 = deepcopy(p0.hand)
    assert len(hand0) == player.startHandSize - 1
    c = p0.hand[0]
    p0.mulligan(c)
    hand1 = deepcopy(p0.hand)
    assert len(hand1) == player.startHandSize - 1
    assert hand0 != hand1

    assert c in p0.deck  # Has the card been returned to the deck

    # Can't mulligan twice
    try:
        p0.mulligan(p0.hand[0])
        assert False
    except IllegalMoveError:
        pass


def testActionsWithIndices():
    game, p0, p1 = util.newGame([dummyCards.one() for i in range(40)])
    game.start()

    print(p0.hand)
    p0.hand[0].fast = True  # Cheat
    p0.playFaceup(0)
    p0.play(0)
    p0.attackFace(0)
    p0.endTurn()

    p1.play(0)
    p1.endTurn()

    p0.revealFacedown(0)
    p0.attackFacedown(0, 0)


def testRepr():
    """
    Make sure repr() isn't broken
    """
    t = Templar()
    print(repr(t.deck))


def testRequiresTarget():
    assert base.spellBlade().requiresTarget
    assert not base.sweep().requiresTarget


def testZoneLists():
    game, p0, p1 = util.newGame()

    for z in p0.zones:
        assert z not in p1.zones


def testCardLocking():
    game, p0, p1 = util.newGame(dummyCards.one())

    p0.play(p0.hand[0])

    # Should not be able to cast a fd on same turn
    try:
        p0.revealFacedown(p0.facedowns[0])
    except IllegalMoveError:
        pass
    else:
        assert False

    p0.endTurn()
    p1.endTurn()
    p0.revealFacedown(p0.facedowns[0])
    assert len(p0.faceups) == 1


def testManualResolve():
    class CustomEventHandler(EventHandler):
        def __init__(self):
            self.nAnimations = 0

        def on_any(self, game):
            self.nAnimations += 1
            game.resolveTriggeredEffects()

    game, p0, p1 = util.newGame(
        [base.sweep()], [dummyCards.fast()], eventHandler=CustomEventHandler())

    p0.play(0)  # Pushes 1
    p0.endTurn()  # 1
    p1.playFaceup(0)  # 2: action + spawn
    p1.endTurn()  # 1
    p0.mana = 4
    p0.revealFacedown(0)  # 4: action + spawn + die + die from spell

    assert game.eventHandler.nAnimations == 9


def testEventsActuallyCalled():
    class CustomEventHandler(EventHandler):
        def __init__(self):
            self.events = []

            # Generate on_x methods for all the events
            for key in [k for k in EventHandler.__dict__.keys()
                        if k.startswith('on_') and k not in ('on_any', 'on_push_action')]:
                def make_on_key(key):
                    # Have to do this b/c of dumb binding rules
                    def on_key(*args, **kwargs):
                        getattr(super(CustomEventHandler, self), key)(*args, **kwargs)
                        self.events.append(key)

                    return on_key

                setattr(self, key, make_on_key(key))

        def on_any(self, game):
            game.resolveTriggeredEffects()

        @property
        def lastEvent(self):
            return self.events[-1]

    eh = CustomEventHandler()

    game, p0, p1 = util.newGame(
        [base.sweep()], [dummyCards.fast()], eventHandler=eh)

    p0.play(0)
    assert eh.lastEvent == "on_play_facedown"
    p0.endTurn()
    assert eh.lastEvent == "on_end_turn"
    p1.playFaceup(0)
    assert eh.lastEvent == "on_play_faceup"
    p1.endTurn()
    p0.mana = 4
    p0.revealFacedown(0)
    # TODO: order events correctly
    assert eh.events[-3] == "on_die"
