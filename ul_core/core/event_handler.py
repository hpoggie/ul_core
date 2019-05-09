class EventHandler:
    """
    Used for animations

    TODO: should death from spell be different?
    """

    # ok
    def on_spawn(self, card):
        self.on_any(card.game)

    def on_fight(self, c1, c2):
        self.on_any(c1.game)

    def on_die(self, card):
        self.on_any(card.game)

    # TODO: call
    def on_change_controller(self, card, original, new):
        self.on_any(card.game)

    # ok
    def on_reveal_facedown(self, card, targets):
        self.on_any(card.game)

    # ok
    def on_play_faceup(self, card, targets):
        self.on_any(card.game)

    # ok
    def on_play_facedown(self, card):
        self.on_any(card.game)

    # TODO: call
    def on_draw(self, card):
        self.on_any(card.game)

    # ok
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
