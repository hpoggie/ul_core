from ul_core.core.player import Player, action
from ul_core.core.exceptions import InvalidTargetError
from ul_core.core.faction import deck
from ul_core.core.card import Card
from ul_core.core.game import destroy
from . import base

iconPath = "fae_icons"


class faerieMoth(Card):
    name = "Faerie Moth"
    image = 'butterfly.png'
    cost = 1
    rank = 1
    fast = True
    desc = "Fast. On Spawn: Play the top card of your deck face-down."

    def onSpawn(self):
        self.controller.deck[-1].zone = self.controller.facedowns


class oberonsGuard(Card):
    name = "Oberon's Guard"
    image = 'elf-helmet.png'
    cost = 2
    rank = 2
    desc = ("On Spawn: you may turn target face-up card you "
            "control face-down.")

    def onSpawn(self, target):
        if target.zone is not self.controller.faceups:
            raise InvalidTargetError()

        target.zone = target.controller.facedowns


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
        super().moveToZone(zone)

        if self.faceup:
            super().moveToZone(self.controller.facedowns)


class radiance(Card):
    name = "Radiance"
    image = 'sun.png'
    cost = 8
    rank = 'il'
    desc = "Turn all your face-down cards face-up."

    def onSpawn(self):
        player = self.controller
        affectedCards = []  # Don't turn the same card face-up twice

        def nextCard():
            try:
                c = next(c for c in player.facedowns if c not in affectedCards)
            except StopIteration:
                pass
            else:
                self.controller.pushTriggeredEffect(nextCard)
                # Do this before c.spawn() because that will pop actions
                # Causing nextCard to be called
                affectedCards.append(c)
                c.spawn()

        self.controller.pushTriggeredEffect(nextCard)


class wildMagic(Card):
    name = "Wild Magic"
    image = 'spiky-explosion.png'
    cost = 5
    rank = 'il'
    desc = "Discard your hand. Draw three cards."

    def onSpawn(self):
        self.controller.hand.destroyAll()
        self.controller.drawCards(3)


class gatewayToFaerie(Card):
    name = "Gateway to Faerie"
    image = 'magic-portal.png'
    cost = 3
    rank = 'il'
    alpha = True
    desc = "α: Turn target face-down card face-up."

    def onSpawn(self, target):
        if not target.facedown:
            raise InvalidTargetError()

        target.spawn()


class dullahan(Card):
    name = "Dullahan"
    image = 'dullahan.png'
    cost = 3
    rank = 2
    desc = ("On Spawn: Name a card. Look at all your opponent's "
            "face-down cards and turn all of them with the chosen name "
            "face-up.")

    def onSpawn(self):
        def nameAndDestroy(name):
            if not isinstance(name, str):
                raise InvalidTargetError("Card name must be a string.")

            self.controller.opponent.facedowns.destroyAll(lambda c: c.name == name)

        self.controller.pushTriggeredEffect(nameAndDestroy)


allCards = [faerieMoth, oberonsGuard, titaniasGuard, mesmerism, returnToSender,
            enchantersTrap, radiance, wildMagic, gatewayToFaerie]


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
        radiance, 2,
        wildMagic, 2,
        gatewayToFaerie, 3) + base.deck

    @action
    def endTurn(self, card=None):
        self.game.endTurn(keepFacedown=[card])
