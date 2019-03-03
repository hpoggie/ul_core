import ul_core.factions.templars as templars
import ul_core.factions.thieves as thieves
import ul_core.factions.mariners as mariners
import ul_core.factions.fae as fae


class ProtocolError(Exception):
    pass


class Templar(templars.Templar):
    def factionAbility(self, discardIndex):
        try:
            discard = self.hand[discardIndex]
        except IndexError as e:
            raise ProtocolError("Bad discard index.", e)

        self.templarAbility(discard)


class Thief(thieves.Thief):
    def factionAbility(self, discard, name, target):
        if isinstance(discard, int):
            try:
                discard = self.hand[discard]
            except IndexError as e:
                raise ProtocolError("Bad discard index.", e)

        if isinstance(target, int):
            try:
                target = self.opponent.facedowns[target]
            except IndexError as e:
                raise ProtocolError("Bad target index.", e)

        self.thiefAbility(discard, name, target)


class Mariner(mariners.Mariner):
    def factionAbility(self):
        self.fish()


class Faerie(fae.Faerie):
    pass


availableFactions = [Templar, Mariner, Thief, Faerie]
