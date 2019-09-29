import random
from ul_core.core.game import destroy


class Zone(list):
    def __init__(self, name, controller, lst=[]):
        super().__init__(lst)
        self.name = name
        self.controller = controller

    def __eq__(self, other):
        return self is other

    def __repr__(self):
        return "Zone %s of %s containing %s" % (self.name, self.controller, self[:])

    def destroyAll(self, fltr=lambda c: True):
        for card in [c for c in self if fltr(c)]:
            destroy(card)

    def destroyAllUnits(self):
        self.destroyAll(lambda c: c.isUnit)

    def shuffle(self):
        random.shuffle(self)

    def createAndAddCard(self, card_func):
        """
        Call card_func and add the card to this zone
        """
        c = card_func()
        c.owner = self.controller
        c.game = self.controller.game
        c.zone = self
        self.append(c)
