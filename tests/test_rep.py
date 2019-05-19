from . import util
from . import dummyCards
from ul_core.net import rep


def test_iden():
    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.card_to_iden(p0, p0.hand[0]) == (0, False)
    assert rep.card_to_iden(p1, p0.hand[0]) == (-1, True)

    game, p0, p1 = util.newGame([dummyCards.one() for i in range(5)])
    game.start()

    assert len(rep.zone_to_idens(p0, p0.hand)) == 10


def test_encode_args():
    game, p0, p1 = util.newGame(dummyCards.one())

    assert rep.encode_args('updatePlayerHand', [p0.hand], relative_to_player=p0) == [0, False]

    try:
        rep.encode_args('updatePlayerHand', [p0.hand, 'a'], relative_to_player=p0) == [0, False]
    except rep.EncodeError:
        pass
    else:
        assert False
