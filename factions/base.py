from ul_core.core.game import destroy
import ul_core.core.card as card

iconPath = 'base_icons/'


class elephant(card.Card):
    name = "Elephant"
    image = "elephant.png"
    cost = 5
    rank = 5


class sweep(card.Card):
    name = "Sweep"
    image = "wind-slap.png"
    cost = 4
    rank = "s"
    spell = True
    desc = "Destroy all face-up units."

    def onSpawn(self):
        for player in self.game.players:
            player.faceups.destroyAllUnits()


class spellBlade(card.Card):
    name = "Spell Blade"
    image = "wave-strike.png"
    cost = 3
    rank = "s"
    spell = True
    fast = True
    desc = "Fast. Destroy target face-down card."

    def onSpawn(self, target):
        if target.facedown:
            destroy(target)


class mindControlTrap(card.Card):
    name = "Mind Control Trap"
    image = "magic-swirl.png"
    cost = 2
    rank = "s"
    spell = True
    desc = ("Draw a card. "
            "If this is attacked while face-down, "
            "gain control of the attacking unit.")

    def onSpawn(self):
        self.controller.drawCard()

    def beforeFight(self, enemy):
        enemy.zone = self.controller.faceups


allCards = [elephant, sweep, spellBlade, mindControlTrap]
deck = [sweep(), spellBlade(), mindControlTrap()]
