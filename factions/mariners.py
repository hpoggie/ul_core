import random

from . import base
from ul_core.core.game import Phase, destroy
from ul_core.core.card import Card
from ul_core.core.faction import deck
from ul_core.core.player import Player
from ul_core.core.exceptions import IllegalMoveError, InvalidTargetError

iconPath = "mariner_icons"


def flood(game):
    if hasattr(game, 'flooded'):
        game.flooded += 1
    else:
        game.flooded = 1


def unflood(game):
    game.flooded -= 1
    if game.flooded < 0:
        raise ValueError("Flood counter can't go below 0.")


class AquaticCard(Card):
    @property
    def flooded(self):
        return hasattr(self.game, 'flooded') and self.game.flooded

    def cast(self, *args, **kwargs):
        if not self.flooded:
            raise IllegalMoveError("You can't cast aquatic spells unless the "
                                   "battlefield is flooded.")

        super().cast(*args, **kwargs)

    def afterEndTurn(self):
        if not self.flooded:
            self.zone = self.owner.hand


class kraken(AquaticCard):
    name = "Kraken"
    image = "squid.png"
    cost = 7
    rank = 8
    desc = "Aquatic."


class nuisanceFlooding(Card):
    name = "Nuisance Flooding"
    image = "at-sea.png"
    cost = 3
    rank = 's'
    continuous = True
    desc = "Flood the battlefield for 4 turns."

    def onSpawn(self):
        self.counter = 4
        flood(self.game)

    def beforeEndTurn(self):
        self.counter -= 1
        if self.counter <= 0:
            self.game.destroy(self)

    def onDeath(self):
        unflood(self.game)


class voidstar(AquaticCard):
    name = "Voidstar"
    image = 'voidstar.png'
    cost = 5
    rank = 5
    fast = True
    desc = "Aquatic. Fast."


class grandJelly(AquaticCard):
    name = "Grand Jelly"
    image = 'jellyfish.png'
    cost = 4
    rank = 4
    taunt = True
    desc = "Aquatic. Taunt."


class ripCurrent(Card):
    name = "Rip Current"
    image = 'water-bolt.png'
    cost = 9
    rank = 's'
    continuous = True
    desc = ("Destroy all your opponent's face-up units "
            "and face-down cards. Flood the battlefield for 4 turns.")

    def onSpawn(self):
        self.controller.opponent.facedowns.destroyAll()
        self.controller.opponent.faceups.destroyAllUnits()
        self.counter = 4
        flood(self.game)

    def beforeEndTurn(self):
        self.counter -= 1
        if self.counter <= 0:
            self.game.destroy(self)

    def onDeath(self):
        unflood(self.game)


class highTide(Card):
    name = "High Tide"
    image = 'lighthouse.png'
    cost = 0
    rank = 's'
    continuous = True
    desc = "Flood the battlefield until end of turn. Draw a card."

    def onSpawn(self):
        flood(self.game)
        self.controller.drawCard()

    def beforeEndTurn(self):
        destroy(self)

    def onDeath(self):
        unflood(self.game)


class unexpectedShark(Card):
    name = "Unexpected Shark"
    image = 'shark-jaws.png'
    cost = 3
    rank = 3
    fast = True
    desc = ("Fast. Dies at end of turn if the battlefield isn't flooded. "
            "Can kill spells.")

    def afterEndTurn(self):
        if not hasattr(self.game, 'flooded') or not self.game.flooded:
            destroy(self)

    def beforeFight(self, target):
        if hasattr(target, 'spell') and target.spell:
            destroy(target)


class braintwister(AquaticCard):
    name = "Braintwister"
    image = 'braintwister.png'
    cost = 2
    rank = 2
    desc = ("Aquatic. On Spawn: your opponent discards a random "
            "card.")

    def onSpawn(self):
        self.controller.opponent.discardRandom()


class humboldtSquid(AquaticCard):
    name = "Humboldt Squid"
    image = 'tentacle-strike.png'
    cost = 1
    rank = 1
    fast = True
    desc = "Aquatic. Fast. This has rank 4 while attacking a unit."

    def beforeAttack(self, target):
        self.rank = 4

    def afterAttack(self, target):
        self.rank = 1


allCards = [humboldtSquid, braintwister, nuisanceFlooding,
              highTide, grandJelly, unexpectedShark, kraken,
              voidstar, ripCurrent]


class Mariner(Player):
    iconPath = iconPath
    cardBack = "nautilus-shell.png"
    deck = deck(humboldtSquid, 5,
              braintwister, 4,
              nuisanceFlooding, 3,
              highTide, 3,
              grandJelly, 2,
              unexpectedShark, 3,
              kraken,
              voidstar,
              ripCurrent) + base.deck

    def fish(self):
        def replace(c1, c2, c3):
            """
            Bottomdeck the 3 cards
            """
            cards = (c1, c2, c3)

            for card in cards:
                if card is None or card.zone is not self.hand:
                    raise InvalidTargetError()

            self.bottomdeck(cards)

        self.drawCards(2)

        # If you have <= 3 cards in hand, put all of them back
        if len(self.hand) <= 3:
            for card in self.hand:
                card.zone = card.owner.deck
        else:
            # Can't do anything until calling replace
            self.replaceCallback = replace

    def endPhase(self, fish=False):
        if self.hasFirstPlayerPenalty and fish:
            raise IllegalMoveError("Can't fish if you're not drawing.")

        super().endPhase()

        if self.game.phase == Phase.play and fish:
            self.fish()
