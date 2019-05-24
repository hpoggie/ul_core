from . import util
from . import dummyCards
from ul_core.net import rep
from ul_core.net.enums import Zone
from ul_core.factions.templars import Templar
from ul_core.factions.thieves import Thief
from ul_core.factions.mariners import Mariner
from ul_core.factions.fae import Faerie


def test_iden():
    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.card_to_iden(p0, p0.hand[0]) == (0, False)
    assert rep.card_to_iden(p1, p0.hand[0]) == (-1, True)

    game, p0, p1 = util.newGame([dummyCards.one() for i in range(5)])
    game.start()

    assert len(rep.zone_to_idens(p0, p0.hand)) == 10


def test_encode_args_to_client():
    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.encode_args_to_client('updatePlayerHand', [p0.hand],
                                     relative_to_player=p0) == [0, False]

    try:
        rep.encode_args_to_client('updatePlayerHand', [p0.hand, 'a'],
                                  relative_to_player=p0) == [0, False]
    except rep.EncodeError:
        pass
    else:
        assert False


def test_encode_args_to_server():
    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.encode_args_to_server('playFaceup', [p0.hand[0]],
                                     relative_to_player=p0) == (0,)

    assert rep.encode_args_to_server('play', [p0.hand[0]],
                                     relative_to_player=p0) == (0,)

    p0.hand[0].fast = True
    p0.playFaceup(0)

    assert rep.encode_args_to_server('attack', [p0.faceups[0], p1.face],
                                     relative_to_player=p0) == (0, Zone.face, 0)

    p1.deck[0].zone = p1.faceups
    assert rep.encode_args_to_server('attack', [p0.faceups[0], p1.faceups[0]],
                                     relative_to_player=p1) == (0, Zone.faceup, 0)

    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.encode_args_to_server('mulligan', [p0.hand[0]],
                                     relative_to_player=p0) == (0,)
    assert rep.encode_args_to_server('mulligan', [],
                                     relative_to_player=p0) == ()

    assert rep.encode_args_to_server('endTurn', [True],
                                     relative_to_player=p0) == (True,)
    assert rep.encode_args_to_server('endTurn', [p0.hand[0]],
                                     relative_to_player=p0) == (Zone.hand, 0, False)

    # Need to do this because deck is not a zone.
    # TODO: make deck a zone.
    p1.deck[0].zone = p1.faceups

    assert rep.encode_args_to_server('makeDecision', [p1.faceups[0]],
                                     relative_to_player=p0) == (Zone.faceup, 0, True)

def test_encode_faction_abilities():
    game, p0, p1 = util.newGame(Templar, Thief)

    assert rep.encode_args_to_server('useFactionAbility', [p0.hand[0]],
                                     relative_to_player=p0) == (0,)

    p0.hand[0].zone = p0.faceups
    p1.drawCard()

    assert rep.encode_args_to_server('useFactionAbility', [p1.hand[0], p0.faceups[0], 'cardname'],
                                     relative_to_player=p1) == (0, 'cardname', 0)

    game, p0, p1 = util.newGame(Mariner, Faerie)

    assert rep.encode_args_to_server('useFactionAbility', [], relative_to_player=p0) == ()

    try:
        rep.encode_args_to_server('useFactionAbility', [], relative_to_player=p1)
    except KeyError:
        pass
    else:
        assert False


def test_decode_args_from_client():
    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.decode_args_from_client('mulligan', [0], p0) == (p0.hand[0],)

    p0.hand[0].zone = p0.facedowns
    p1.drawCard()

    assert rep.decode_args_from_client('revealFacedown',
                                       [0, Zone.hand, 0, True], p0) == (p0.facedowns[0], p1.hand[0])

    assert rep.decode_args_from_client('playFaceup', [0, Zone.facedown, 0, True],
                                       p1) == (p1.hand[0], p0.facedowns[0])

    try:
        rep.decode_args_from_client('playFaceup', [0, Zone.facedown, True], p1)
    except rep.DecodeError:
        pass
    else:
        assert False

    assert rep.decode_args_from_client('play', [0], p1) == p1.hand[0]


def test_decode_attack():
    game, p0, p1 = util.newGame(dummyCards.one())

    p0.hand[0].zone = p0.faceups

    assert rep.decode_args_from_client('attack', [0, Zone.face, -1], p0) == (p0.faceups[0], p1.face)


def test_decode_end_turn():
    game, p0, p1 = util.newGame(Thief, Faerie)

    p0.deck[0].zone = p0.faceups

    assert rep.decode_args_from_client('endTurn', [Zone.face, 0, True], p0) == ()
    assert rep.decode_args_from_client('endTurn', [Zone.faceup, 0, True], p1) == (p0.faceups[0],)


def test_decode_make_decision():
    game, p0, p1 = util.newGame(Thief, Faerie)

    assert rep.decode_args_from_client('makeDecision', [], p0) == ()
    assert rep.decode_args_from_client('makeDecision', [Zone.hand, 0, True, Zone.hand, 0, True],
                                       p1) == (p0.hand[0], p0.hand[0])


def test_decode_args_from_server():
    game, p0, p1 = util.newGame(Thief, Faerie)

    assert rep.decode_args_from_server('updatePlayerFaceups',
                                       [0, False], p0) == (p0.referenceDeck[0],)