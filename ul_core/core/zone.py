import random
from ul_core.core.game import destroy


class Zone(list):
    def __init__(self, controller, lst=[]):
        super().__init__(lst)
        self.controller = controller
        self.dirty = True

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.dirty = True

    def __delitem__(self, key):
        super().__delitem__(key)
        self.dirty = True

    def __eq__(self, other):
        return self is other

    def append(self, card):
        super().append(card)
        self.dirty = True

    def remove(self, card):
        super().remove(card)
        self.dirty = True

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
