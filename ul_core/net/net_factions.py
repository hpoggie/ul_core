import ul_core.factions.templars as templars
import ul_core.factions.thieves as thieves


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

        self.thiefAbility()
