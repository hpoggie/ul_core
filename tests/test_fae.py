from ul_core.core.card import Card
from ul_core.core.game import destroy
from ul_core.core.exceptions import InvalidTargetError, IllegalMoveError
import ul_core.factions.fae as fae
import ul_core.factions.thieves as thieves  # For Head Lightning
from .util import newGame
from . import dummyCards


def test_fae_ability():
    game, p0, p1 = newGame(fae.Faerie)
    game.start()
    p0.hand[0].zone = p0.facedowns
    p0.hand[0].zone = p0.facedowns
    p0.endTurn()
    p1.endTurn()
    p0.endTurn(p0.facedowns[0])
    assert len(p0.facedowns) == 1


def test_illusions():
    game, p0, p1 = newGame()

    class DummyIllusion(Card):
        name = "Dummy Illusion"
        cost = 1
        rank = 'il'

    one = dummyCards.one(owner=p0, game=game)
    one.zone = p0.faceups
    di = DummyIllusion(owner=p1, game=game)
    assert di.illusion
    di.zone = p1.facedowns

    p0.endPhase()
    p0.attack(one, di)

    assert di.zone == p1.graveyard


def test_faerie_dragon():
    game, p0, p1 = newGame()

    fd = fae.faerieDragon(owner=p0, game=game, zone=p0.faceups)
    destroy(fd)

    assert fd.zone is p0.facedowns


def test_mesmerism():
    game, p0, p1 = newGame()

    c1 = dummyCards.one(owner=p1, game=game, zone=p1.faceups)
    c2 = dummyCards.one(owner=p1, game=game, zone=p1.faceups)
    c3 = dummyCards.one(owner=p1, game=game, zone=p1.faceups)

    mes = fae.mesmerism(owner=p0, game=game, zone=p0.facedowns)
    p0.mana = 10
    p0.revealFacedown(mes)

    assert len(p1.faceups) == 0
    assert len(p0.faceups) == 3


def test_return_to_sender():
    game, p0, p1 = newGame()

    for i in range(3):
        dummyCards.one(owner=p1, game=game, zone=p1.facedowns)

    rts = fae.returnToSender(owner=p0, game=game, zone=p0.facedowns)
    p0.mana = 9
    p0.revealFacedown(rts)

    assert len(p1.facedowns) == 0
    assert len(p1.hand) == 3


def test_enchanters_trap():
    game, p0, p1 = newGame()

    et = fae.enchantersTrap(owner=p0, game=game, zone=p0.facedowns)
    assert et.zone is p0.facedowns
    et.zone = p0.faceups
    assert et.zone is p0.facedowns


def test_radiance():
    game, p0, p1 = newGame()

    left = dummyCards.one(owner=p0, game=game, zone=p0.facedowns)
    rad = fae.radiance(owner=p0, game=game, zone=p0.facedowns)
    right = dummyCards.one(owner=p0, game=game, zone=p0.facedowns)
    right2 = dummyCards.one(owner=p1, game=game, zone=p0.facedowns)

    p0.mana = rad.cost
    p0.revealFacedown(rad)
    assert game.triggeredEffectStack == []
    assert left.zone == p0.faceups
    assert right.zone == p0.faceups
    assert right2.zone == p0.faceups


def test_radiance_head_lightning():
    game, p0, p1 = newGame()

    rad = fae.radiance(owner=p0, game=game, zone=p0.facedowns)
    thieves.headLightning(owner=p0, game=game, zone=p0.facedowns)

    p0.mana = rad.cost
    p0.revealFacedown(rad)
    assert game.requiredDecision is not None


def test_radiance_enchanters_trap():
    game, p0, p1 = newGame()

    rad = fae.radiance(owner=p0, game=game, zone=p0.facedowns)
    ec = fae.enchantersTrap(owner=p0, game=game, zone=p0.facedowns)

    p0.mana = rad.cost
    p0.revealFacedown(rad)


def test_radiance_oberons_guard():
    """
    Tests popping something from action stack not clobbering further actions
    """

    game, p0, p1 = newGame()

    rad = fae.radiance(owner=p0, game=game, zone=p0.facedowns)
    og = fae.oberonsGuard(owner=p0, game=game, zone=p0.facedowns)
    fae.oberonsGuard(owner=p0, game=game, zone=p0.facedowns)

    p0.mana = rad.cost
    p0.revealFacedown(rad)

    assert og.faceup

    p0.makeRequiredDecision(rad)

    assert game.requiredDecision is not None


def test_gateway():
    game, p0, p1 = newGame()

    gateway = fae.gatewayToFaerie(owner=p0, game=game, zone=p0.facedowns)
    one = dummyCards.one(owner=p0, game=game, zone=p0.facedowns)

    p0.mana = gateway.cost
    p0.revealFacedown(gateway, one)
    assert one.zone is p0.faceups


def test_titanias_guard():
    game, p0, p1 = newGame()

    tg = fae.titaniasGuard(owner=p0, game=game, zone=p0.facedowns)

    p0.mana = 4

    try:
        p0.revealFacedown(tg, None)
    except InvalidTargetError:
        pass


def test_oberons_guard():
    game, p0, p1 = newGame()

    og = fae.oberonsGuard(owner=p0, game=game, zone=p0.facedowns)
    p0.mana = 2
    p0.revealFacedown(og, None)


def test_dullahan():
    game, p0, p1 = newGame()
    d = fae.dullahan(owner=p0, game=game, zone=p0.facedowns)
    one = dummyCards.one(owner=p1, game=game, zone=p1.facedowns)
    one = dummyCards.one(owner=p1, game=game, zone=p1.facedowns)
    two = dummyCards.one(owner=p1, game=game, zone=p1.facedowns)
    two.name = "Two"

    p0.mana = d.cost
    p0.revealFacedown(d)
    assert game.requiredDecision is not None
    p0.makeRequiredDecision('One')
    assert len(p1.facedowns) == 1
    assert p1.facedowns[0] == two
