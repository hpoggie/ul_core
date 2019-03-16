import types
from . import base
from ul_core.core.player import Player, action
from ul_core.core.exceptions import IllegalMoveError, InvalidTargetError
from ul_core.core.card import Card
from ul_core.core.game import destroy
from ul_core.core.faction import deck

iconPath = "thief_icons"


class MultiattackCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attackedTargets = []

    def onSpawn(self):
        self._attackedTargets = []

    def afterEndTurn(self):
        self._attackedTargets = []

    def attack(self, target):
        if target in self._attackedTargets:
            raise IllegalMoveError("Can't attack the same target twice.")

        super().attack(target)
        self._attackedTargets.append(target)

    @property
    def hasAttacked(self):
        return len(self._attackedTargets) == self.nAttacks

    @hasAttacked.setter
    def hasAttacked(self, value):
        pass


class spectralCrab(Card):
    name = "Spectral Crab"
    image = 'crab.png'
    cost = 2
    desc = "Rank: 4 while face-down, 2 otherwise."

    @property
    def rank(self):
        return 4 if self.facedown else 2


class timeBeing(Card):
    name = "Time Being"
    image = 'dead-eye.png'
    cost = 12
    rank = 3
    desc = "On Spawn: take an extra turn after this one."

    def onSpawn(self):
        self.controller.takeExtraTurn()


class spellScalpel(Card):
    name = "Spell Scalpel"
    image = 'scalpel-strike.png'
    cost = 5
    rank = 's'
    desc = "Destroy target card. Draw a card."

    def onSpawn(self, target):
        destroy(target)
        self.controller.drawCard()


class fog(Card):
    name = "Fog"
    image = 'frog.png'
    cost = 1
    rank = 1
    taunt = True
    desc = "Taunt."


class hydra(MultiattackCard):
    name = "Hydra"
    image = 'hydra.png'
    cost = 6
    rank = 3
    nAttacks = 3
    desc = "Can attack up to 3 different targets per turn."


class doubleDragon(MultiattackCard):
    name = "Double Dragon"
    image = 'double-dragon.png'
    cost = 4
    rank = 2
    nAttacks = 2
    desc = "Can attack up to 2 different targets per turn."


class headLightning(Card):
    name = "Head Lightning"
    image = 'brainstorm.png'
    cost = 1
    rank = 's'
    desc = ("Draw 3 cards, then put 2 cards from your hand on top of"
            "your deck.")

    def onSpawn(self):
        self.controller.drawCards(3)

        def replace(c1, c2):
            if c1.zone == c2.zone == self.controller.hand:
                self.controller.topdeck([c1, c2])
            else:
                raise InvalidTargetError()

        self.controller.pushTriggeredEffect(replace)


class roseEmblem(Card):
    name = "Rose Emblem"
    image = 'rose.png'
    cost = 3
    rank = 's'
    desc = "Draw 2 cards. When you discard this from your hand, draw a card."

    def onSpawn(self):
        self.controller.drawCards(2)

    def onDiscard(self):
        self.controller.drawCard()


class spellHound(Card):
    name = "Spell Hound"
    image = 'wolf-howl.png'
    cost = 3
    rank = 2
    desc = "On Spawn: look at your opponent's hand."

    def onSpawn(self):
        for c in self.controller.opponent.hand:
            c.visible = True


class daggerEmblem(Card):
    name = "Dagger Emblem"
    image = 'stiletto.png'
    cost = 2
    rank = 's'
    desc = ("Destroy target face-up unit. When you discard this from your"
            " hand, draw a card.")

    def onSpawn(self, target):
        if (target.faceup and not target.spell):
            destroy(target)

    def onDiscard(self):
        self.controller.drawCard()


class heavyLightning(Card):
    name = "Heavy Lightning"
    image = 'heavy-lightning.png'
    cost = 11
    rank = 's'
    desc = "Destroy your opponent's board. Ambush: cast this."

    def afterFight(self, c2):
        self.spawn()

    def onSpawn(self):
        self.controller.opponent.facedowns.destroyAll()
        self.controller.opponent.faceups.destroyAllUnits()


allCards = [fog, spectralCrab, spellHound, doubleDragon,
        headLightning, roseEmblem, daggerEmblem, hydra,
        timeBeing, heavyLightning, spellScalpel]


class Thief(Player):
    name = "Thieves"
    iconPath = iconPath
    cardBack = "dagger-rose.png"
    deck = deck(
        base.elephant,
        fog, 5,
        spectralCrab, 4,
        spellHound, 3,
        doubleDragon, 2,
        headLightning, 2,
        roseEmblem,
        daggerEmblem,
        hydra,
        timeBeing,
        heavyLightning,
        spellScalpel) + base.deck

    def validateThiefAbilityInput(self, discard, name, target):
        """
        Check if the input we got is legal.
        Fails if zones are wrong or we get arguments that aren't cards
        Also fails if we did something else before
        """
        if self.hasTakenAction:
            raise IllegalMoveError(
                "α effects can only be done as the first action on your turn.")

        # Check if discard has a zone attribute
        # Done separately to avoid catching possible AttributeErrors from
        # self.hand
        try:
            dzone = discard.zone
        except AttributeError:
            raise IllegalMoveError(
                "Can't discard something that's not a card.")

        if dzone is not self.hand:
            raise IllegalMoveError("That card is not in your hand.")

        try:
            tzone = target.zone
        except AttributeError:
            raise InvalidTargetError(
                "Can't target something with Thief ability that's not a card.")

        if tzone is not self.opponent.facedowns:
            raise InvalidTargetError()

    @action
    def thiefAbility(self, discard, name, target):
        self.validateThiefAbilityInput(discard, name, target)

        if target.name == name:
            target.spawn(newController=self)
        else:
            target.visible = True

        discard.zone = discard.owner.graveyard
