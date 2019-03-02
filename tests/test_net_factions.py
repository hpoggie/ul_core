from .util import newGame
import ul_core.net.net_factions as nf


def testTemplarAbilityIndices():
    game, p0, p1 = newGame(nf.Templar)
    game.start()
    
    try:
        p0.factionAbility(100)  # index way too big
    except nf.ProtocolError:
        pass
    else:
        assert False

    p0.factionAbility(0)


def testFactionAbilityIndices():
    game, p0, p1 = newGame(nf.Thief)

    p0.endTurn()
    c = next(c for c in p1.deck + p1.hand if c.name == 'Elephant')
    c.zone = p1.facedowns

    p1.endTurn()
    try:
        p0.factionAbility(9, c, 'Elephant')
    except nf.ProtocolError:
        pass
