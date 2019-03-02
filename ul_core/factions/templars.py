from . import base
from ul_core.core.game import destroy, Phase
from ul_core.core.card import Card
from ul_core.core.faction import deck
from ul_core.core.player import Player

iconPath = "templar_icons"


class equus(Card):
    name = "Equus"
    image = "horse-head.png"
    cost = 4
    desc = "Rank: 5 if your mana cap is odd, 2 if it's even."

    @property
    def rank(self):
        return 2 if (self.controller.manaCap % 2 == 0) else 5


class archangel(Card):
    name = "Archangel"
    image = "angel-wings.png"
    cost = 13
    rank = 15


class wrathOfGod(Card):
    name = "Wrath of God"
    image = "wind-hole.png"
    cost = 5
    rank = 's'
    fast = True
    desc = "Fast. Destroy all face-up units."

    def onSpawn(self):
        for player in self.game.players:
            player.faceups.destroyAllUnits()


class corvus(Card):
    name = "Corvus"
    image = "raven.png"
    cost = 1
    desc = "Rank: 2 if your mana cap is odd, 1 if it's even."

    @property
    def rank(self):
        return 1 if (self.controller.manaCap % 2 == 0) else 2


class miracle(Card):
    name = "Miracle"
    image = "sundial.png"
    cost = 8
    rank = 's'
    desc = "Draw until you have 5 cards in hand."

    def onSpawn(self):
        self.controller.drawTo(5)


class crystalElemental(Card):
    name = "Crystal Elemental"
    image = "crystal-cluster.png"
    cost = 5
    rank = 3
    desc = "Whenever an enemy face-down card is destroyed, draw a card."

    def beforeDestroy(self, card):
        if card.zone is self.controller.opponent.facedowns:
            self.controller.drawCard()


class gargoyle(Card):
    name = "Gargoyle"
    image = "gargoyle.png"
    cost = 2
    rank = 2
    taunt = True
    desc = "Taunt."


class guardianAngel(Card):
    name = "Guardian Angel"
    image = "winged-shield.png"
    cost = 4
    rank = 3
    taunt = True
    desc = "Taunt."


class crystalLance(Card):
    name = "Crystal Lance"
    image = "ice-spear.png"
    cost = 5
    rank = 's'
    desc = ("Destroy target face-down card. "
            "If this is attacked while face-down, "
            "destroy the attacking unit and draw a card.")
    targetDesc = "Destroy target face-down card."

    def onSpawn(self, target):
        if target.facedown:
            destroy(target)

    def afterFight(self, enemy):
        destroy(enemy)
        self.controller.drawCard()


class crystalRain(Card):
    name = "Crystal Rain"
    image = "crystal-bars.png"
    cost = 4
    rank = 's'
    fast = True
    desc = ("Fast. Destroy target face-down card. "
            "If this is attacked while face-down, "
            "destroy all face-up units.")
    targetDesc = "Destroy target face-down card."

    def onSpawn(self, target):
        if target.facedown:
            destroy(target)

    def afterFight(self, enemy):
        for player in self.game.players:
            player.faceups.destroyAllUnits()


allCards = [corvus, gargoyle, equus, guardianAngel, wrathOfGod, archangel,
            miracle, crystalLance, crystalRain, crystalElemental]


class Templar(Player):
    name = "Templars"
    iconPath = iconPath
    cardBack = "egyptian-temple.png"
    deck = deck(
            corvus, 5,
            gargoyle, 4,
            equus, 3,
            guardianAngel, 2,
            base.elephant,
            wrathOfGod,
            archangel,
            miracle,
            crystalLance, 2,
            crystalRain, 2,
            crystalElemental) + base.deck

    def templarAbility(self, card):
        if card and card in self.hand:
            card.zone = self.graveyard
            self.manaCap += 1

        self.endTurn()
