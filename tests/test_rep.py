from . import util
from . import dummyCards
from ul_core.net import rep
from ul_core.net.enums import Zone


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

    p0.hand[0].fast = True
    p0.playFaceup(0)

    assert rep.encode_args_to_server('attack', [p0.faceups[0], p1.face],
                                     relative_to_player=p0) == (0, Zone.face, 0)
