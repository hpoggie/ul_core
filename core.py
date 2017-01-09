from enums import *
from player import Player


class Game:
    def __init__(self):
        self.turn = Turn.p1
        self.phase = Phase.reveal

        self.players = (Player("Player 1"), Player("Player 2"))
        for player in self.players:
            player.game = self
            for card in player.deck:
                card.game = self
            player.shuffle()
            player.drawOpeningHand()

    @property
    def activePlayer(self):
        return self.players[self.turn]

    def fight(self, c1, c2):
        if c1.rank < c2.rank:
            self.destroy(c1)
        if c1.rank > c2.rank:
            self.destroy(c2)
        elif c1.rank == c2.rank:
            self.destroy(c1)
            self.destroy(c2)

    def destroy(self, card):
        card.moveZone(Zone.graveyard)

    def endPhase(self, player):
        if not player.isActivePlayer():
            print "It is not your turn."
            return

        if self.phase == Phase.reveal:
            self.activePlayer.facedowns = []

        self.phase += 1

        if self.phase == Phase.draw:
            self.activePlayer.drawCard()
        elif self.phase == Phase.attack:
            for f in self.activePlayer.faceups:
                f.hasAttacked = False
        elif self.phase == Phase.play:
            pass
        else:
            self.endTurn()

    def endTurn(self):
        player = self.activePlayer
        player.manaCap += 1
        if player.manaCap > 15:
            player.getEnemy().win()
        player.mana = player.manaCap
        print "player " + player.name + " mana cap is " + str(player.manaCap)
        self.turn = Turn.p2 if self.turn == Turn.p1 else Turn.p1
        self.phase = Phase.reveal
