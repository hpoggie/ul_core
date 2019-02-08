from . import enums

Turn = enums.numericEnum('p1', 'p2')
Phase = enums.numericEnum('startOfTurn', 'reveal', 'play')


def destroy(card):
    card.game.destroy(card)


class EndOfGame(BaseException):
    def __init__(self, winner):
        self.winner = winner


def event(func):
    # Automatically generate function names for before and after events
    # e.g. endPhase -> beforeEndPhase
    upperName = func.__name__[0].upper() + func.__name__[1:]
    beforeEventName = 'before' + upperName
    afterEventName = 'after' + upperName

    def fooBeforeAfter(self, *args, **kwargs):
        self.doEventTriggers(beforeEventName, *args, **kwargs)
        func(self, *args, **kwargs)
        self.doEventTriggers(afterEventName, *args, **kwargs)

    return fooBeforeAfter


class Game:
    def __init__(self, p1Type, p2Type):
        """
        p1Type and p2Type are the classes of player 1 and player 2.
        e.g. Templar and Thief
        """
        # It's no one's turn until both players have mulliganed
        self.turn = None
        self.phase = Phase.reveal

        self.players = (p1Type(), p2Type())
        for player in self.players:
            player.game = self
            for card in player.deck:
                card.game = self

    def start(self):
        for player in self.players:
            player.shuffle()
            player.drawOpeningHand()

    def finishMulligans(self):
        self.turn = Turn.p1

    @property
    def activePlayer(self):
        return None if self.turn is None else self.players[self.turn]

    def doEventTriggers(self, name, *args, **kwargs):
        # Find the right function by name and call it
        # If it doesn't exist, don't worry about it
        def doTrigger(obj, name):
            if hasattr(obj, name):
                getattr(obj, name)(*args, **kwargs)

        for pl in self.players:
            doTrigger(pl, name)
            for c in pl.faceups[:]:
                doTrigger(c, name)

    def fight(self, attacker, target):
        self.doEventTriggers('beforeAnyFight', attacker, target)
        attacker.beforeFight(target)
        target.beforeFight(attacker)

        if attacker.zone == attacker.controller.facedowns:
            attacker.visible = True
        if target.zone == target.controller.facedowns:
            target.visible = True

        if attacker.spell or target.spell:
            if attacker.illusion:
                self.destroy(attacker)
            if target.illusion:
                self.destroy(target)
        else:
            if attacker.rank < target.rank:
                self.destroy(attacker)
            if attacker.rank > target.rank:
                self.destroy(target)
            elif attacker.rank == target.rank:
                self.destroy(attacker)
                self.destroy(target)

        self.doEventTriggers('afterAnyFight', attacker, target)
        attacker.afterFight(target)
        target.afterFight(attacker)

    @event
    def destroy(self, card):
        card.zone = card.owner.graveyard

    @event
    def dealDamage(self, player, amount):
        player.manaCap += amount

    @event
    def endPhase(self, keepFacedown=[]):
        if self.phase == Phase.reveal:
            for c in self.activePlayer.facedowns[:]:
                if c not in keepFacedown:
                    c.zone = c.owner.graveyard
            self.activePlayer.drawCard()

        self.phase += 1

        if self.phase == Phase.play:
            for f in self.activePlayer.faceups:
                f.hasAttacked = False
        elif self.phase > Phase.play:
            self.endTurn()

    @event
    def endTurn(self):
        # Make hand cards invisible so you can't easily see what's played
        for pl in self.players:
            for c in pl.hand:
                c.visible = False

        player = self.activePlayer
        player.manaCap += 1
        if player.manaCap > 15:
            player.opponent.win()

        if player.extraTurns > 0:
            player.extraTurns -= 1
        else:
            self.turn = Turn.p2 if self.turn == Turn.p1 else Turn.p1

        self.activePlayer.mana = self.activePlayer.manaCap
        self.phase = Phase.startOfTurn
        self.activePlayer.onStartOfTurn()

    def end(self, winner):
        raise EndOfGame(winner)
