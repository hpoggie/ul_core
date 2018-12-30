from ul_core.core.player import Player
from ul_core.core.exceptions import InvalidTargetError
from ul_core.core.faction import deck
from ul_core.core.card import Card
from ul_core.core.game import destroy
import ul_core.factions.base as base

iconPath = "fae_icons"


class faerieMoth(Card):
    name = "Faerie Moth"
    image = 'butterfly.png'
    cost = 1
    rank = 1
    fast = True
    desc = "Fast."


class oberonsGuard(Card):
    name = "Oberon's Guard"
    image = 'elf-helmet.png'
    cost = 2
    rank = 2
    desc = ("When this spawns, you may return target face-down card you "
            "control to its owner's hand.")

    def onSpawn(self, target):
        if target.zone is not self.controller.facedowns:
            raise InvalidTargetError()

        target.zone = target.owner.hand


class titaniasGuard(Card):
    name = "Titania's Guard"
    image = 'batwing-emblem.png'
    cost = 4
    rank = 4
    desc = "On Spawn: You may turn target face-up unit face-down."

    def onSpawn(self, target):
        if not target.faceup or target.spell:
            raise InvalidTargetError()

        target.zone = target.controller.facedowns


class faerieDragon(Card):
    name = "Faerie Dragon"
    image = 'chameleon-glyph.png'
    cost = 5
    rank = 4
    desc = ("If this would be destroyed while face-up, turn it face-down "
            "instead.")

    def moveToZone(self, zone):
        if self.faceup and zone is self.owner.graveyard:
            super().moveToZone(self.controller.facedowns)
        else:
            super().moveToZone(zone)


class mesmerism(Card):
    name = "Mesmerism"
    image = 'night-vision.png'
    cost = 10
    rank = 'il'
    desc = "Gain control of all your opponent's face-up units."

    def onSpawn(self):
        for c in self.controller.opponent.faceups[:]:
            c.zone = self.controller.faceups


class returnToSender(Card):
    name = "Return to Sender"
    image = 'return-arrow.png'
    cost = 9
    rank = 'il'
    desc = ("Return all enemy face-up units and face-down cards to their "
            "owners' hands.")

    def onSpawn(self):
        for fd in self.controller.opponent.facedowns[:]:
            fd.zone = fd.owner.hand

        for c in self.controller.opponent.faceups[:]:
            c.zone = c.owner.hand


class enchantersTrap(Card):
    name = "Enchanter's Trap"
    image = 'portal.png'
    cost = 16
    rank = 15
    desc = "Can't be face-up."

    def moveToZone(self, zone):
        if (zone is self.game.players[0].faceups or
                zone is self.game.players[1].faceups):
            return

        super().moveToZone(zone)


class radiance(Card):
    name = "Radiance"
    image = 'sun.png'
    cost = 4
    rank = 'il'
    continuous = True
    desc = ("Until end of turn, for every 1 damage you deal to your opponent,"
            "they must discard a random card.")

    def afterDealDamage(self, player, amount):
        if player is self.controller.opponent:
            for i in range(amount):
                player.discardRandom()

    def beforeEndTurn(self):
        destroy(self)


allCards = [faerieMoth, oberonsGuard, titaniasGuard, mesmerism, returnToSender,
            enchantersTrap, radiance]


class Faerie(Player):
    name = "Fae"
    iconPath = iconPath
    cardBack = "fairy.png"
    deck = deck(
        faerieMoth, 5,
        oberonsGuard, 2,
        titaniasGuard, 2,
        mesmerism, 1,
        returnToSender, 1,
        enchantersTrap, 2,
        radiance, 2) + base.deck

    def endPhase(self, card=None):
        self.failIfInactive()
        self.game.endPhase(keepFacedown=[card])
