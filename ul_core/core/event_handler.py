class EventHandler:
    """
    Used for animations

    TODO: should death from spell be different?
    """
    def on_move_card(self, card, old, new):
        """
        Called whenever a card moves to another zone.
        This should not call on_any because it shouldn't resolve triggers.
        """
        pass

    def on_spawn(self, card):
        self.on_any(card.game)

    def on_fight(self, c1, c2):
        self.on_any(c1.game)

    def on_die(self, card):
        self.on_any(card.game)

    def on_change_controller(self, card, original, new):
        self.on_any(card.game)

    def on_reveal_facedown(self, card, targets):
        self.on_any(card.game)

    def on_play_faceup(self, card, targets):
        self.on_any(card.game)

    def on_play_facedown(self, card):
        self.on_any(card.game)

    def on_draw(self, card):
        self.on_any(card.game)

    def on_fizzle(self, card):
        self.on_any(card.game)

    def on_end_turn(self, game):
        self.on_any(game)

    def on_any(self, game):
        pass

    def on_push_action(self, player):
        """
        Called when the player pushes an action onto the stack.

        This should not call on_any.
        """
        player.game.resolveTriggeredEffects()


class EmptyEventHandler:
    """
    If you just need the game to store data
    """
    def on_move_card(self, card, old, new):
        pass

    def on_spawn(self, card):
        pass

    def on_fight(self, c1, c2):
        pass

    def on_die(self, card):
        pass

    def on_change_controller(self, card, original, new):
        pass

    def on_reveal_facedown(self, card, targets):
        pass

    def on_play_faceup(self, card, targets):
        pass

    def on_play_facedown(self, card):
        pass

    def on_draw(self, card):
        pass

    def on_fizzle(self, card):
        pass

    def on_end_turn(self, game):
        pass

    def on_any(self, game):
        pass

    def on_push_action(self, player):
        pass
