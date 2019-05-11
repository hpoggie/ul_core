from .util import newGame
from ul_core.core.exceptions import IllegalMoveError
from ul_core.core.game import Game, Turn
import ul_core.factions.templars as templars


def testTemplarAbility():
    game, p0, p1 = newGame(templars.Templar, templars.Templar)
    game.start()

    p0.templarAbility(p0.hand[0])

    assert len(p0.hand) == 4  # First player penalty
    assert p0.manaCap == 3

    p1.templarAbility(None)

    assert len(p1.hand) == 6
    assert p1.manaCap == 2

    # Try discarding something not in your hand
    p0.templarAbility(p1.hand[0])
    assert len(p1.hand) == 7
    assert p0.manaCap == 4


def testEquus():
    game, p0, p1 = newGame(templars.equus())
    p0.hand[0].zone = p0.faceups
    p0.manaCap = 3
    assert p0.faceups[0].rank == 5
    p0.manaCap = 4
    assert p0.faceups[0].rank == 2


def testWrathOfGod():
    game, p0, p1 = newGame(
        [templars.corvus(), templars.corvus()],
        [templars.wrathOfGod()])
    p0.drawCard()
    p0.drawCard()
    p0.hand[0].fast = True
    p0.hand[0].cost = 0
    p0.hand[1].fast = True
    p0.hand[1].cost = 0
    p0.playFaceup(p0.hand[0])
    p0.playFaceup(p0.hand[0])
    p0.endTurn()
    p1.drawCard()
    p1.hand[0].cost = 0
    p1.playFaceup(p1.hand[0])
    assert len(p0.faceups) == 0


def testMiracle():
    game, p0, p1 = newGame(
        [templars.corvus() for i in range(6)] + [templars.miracle()])
    assert len(p0.hand) == 1
    p0.hand[0].fast = True
    p0.hand[0].cost = 0
    p0.playFaceup(p0.hand[0])
    assert len(p0.hand) == 5


def testMiracleNotEnoughCards():
    game, p0, p1 = newGame(
        templars.corvus(),
        templars.corvus(),
        templars.miracle()
    )
    assert len(p0.hand) == 1
    p0.hand[0].fast = True
    p0.hand[0].cost = 0
    p0.playFaceup(p0.hand[0])
    assert len(p0.hand) == 2


def testGargoyle():
    game, p0, p1 = newGame()
    p0.faceups.createAndAddCard(templars.gargoyle)
    p1.faceups.createAndAddCard(templars.corvus)
    p1.faceups[0].hasAttacked = False
    game.turn = Turn.p2
    # Should fail if attack works
    try:
        p1.attack(p1.faceups[0], p0.face)
        assert False
    except IllegalMoveError:
        pass


def testCrystalElemental():
    game, p0, p1 = newGame(
        [templars.crystalElemental()],
        [templars.corvus()])

    # Cheat the elemental into play
    p0.drawCard()
    p0.hand[0].fast = True
    p0.mana = templars.crystalElemental().cost
    p0.playFaceup(p0.hand[0])
    p0.endTurn()

    p1.play(p1.hand[0])  # Play the card face-down
    p1.endTurn()

    assert(len(p0.hand) == 0)

    # give them a card to draw
    p0.deck.createAndAddCard(templars.crystalElemental)

    p0.attack(p0.faceups[0], p1.facedowns[0])
    assert(len(p0.hand) == 1)
