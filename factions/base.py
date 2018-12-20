from ul_core.core.game import destroy
import ul_core.core.card as card


class Card(card.Card):
    """
    Override the image path to use base_icons
    """
    @property
    def imagePath(self):
        return 'base_icons/' + self.image


class elephant(Card):
    name = "Elephant"
    image = "elephant.png"
    cost = 5
    rank = 5


class sweep(Card):
    name = "Sweep"
    image = "wind-slap.png"
    cost = 4
    rank = "s"
    spell = True
    desc = "Destroy all face-up units."

    def onSpawn(self):
        for player in self.game.players:
            player.faceups.destroyAllUnits()


class spellBlade(Card):
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


class mindControlTrap(Card):
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

for c in allCards:
    c.iconPath = Card().imagePath

deck = [sweep(), spellBlade(), mindControlTrap()]
