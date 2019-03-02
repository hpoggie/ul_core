from . import enums

Turn = enums.numericEnum('p1', 'p2')


def destroy(card):
    card.game.destroy(card)


class EndOfGame(BaseException):
    def __init__(self, winner):
        self.winner = winner


def event(func):
    # Automatically generate function names for before and after events
    # e.g. endTurn -> beforeEndTurn
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

        self.players = (p1Type(), p2Type())
        for player in self.players:
            player.game = self
            for card in player.deck:
                card.game = self

        # Stack used for resolving triggered effects.
        self.triggeredEffectStack = []

        # Decision that must be made for the game to progress
        self.requiredDecision = None

    def start(self):
        for player in self.players:
            player.shuffle()
            player.drawOpeningHand()

    def finishMulligans(self):
        self.turn = Turn.p1
        self.startTurn()

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
        attacker.beforeAttack(target)
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
        attacker.afterAttack(target)
        attacker.afterFight(target)
        target.afterFight(attacker)

    @event
    def destroy(self, card):
        card.zone = card.owner.graveyard

    @event
    def dealDamage(self, player, amount):
        player.manaCap += amount

    @event
    def endTurn(self, keepFacedown=[]):
        # Make hand cards invisible so you can't easily see what's played
        for pl in self.players:
            for c in pl.hand:
                c.visible = False

        for c in self.activePlayer.facedowns[:]:
            if c.stale and c not in keepFacedown:
                c.zone = c.owner.graveyard
            else:
                c.stale = True

        player = self.activePlayer
        player.manaCap += 1
        if player.manaCap > 15:
            player.opponent.win()

        if player.extraTurns > 0:
            player.extraTurns -= 1
        else:
            self.turn = Turn.p2 if self.turn == Turn.p1 else Turn.p1

        self.startTurn()

    @event
    def startTurn(self):
        self.activePlayer.mana = self.activePlayer.manaCap

        for f in self.activePlayer.faceups:
            f.hasAttacked = False

        self.activePlayer.hasTakenAction = False
        self.activePlayer.drawCard()

    def end(self, winner):
        raise EndOfGame(winner)

    def pushTriggeredEffect(self, effect):
        self.triggeredEffectStack.append(effect)

    def resolveTriggeredEffects(self):
        """
        Pop effects off the stack until we get a decision or it's empty
        """
        while (len(self.triggeredEffectStack) > 0
                and self.requiredDecision is None):
            effect = self.triggeredEffectStack.pop()

            if effect.requiresTarget:
                self.requiredDecision = effect
                break
            else:
                effect.resolve()
