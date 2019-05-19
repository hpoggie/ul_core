class EncodeError(Exception):
    pass


def card_to_iden(player, card):
    """
    Convert card to ID/enemy (IDEN) representation.

    ID is the cardId of the card, or -1 if the card is invisible to the player.
    Enemy is True if the card is owned by the opponent, relative to the player argument.
    Otherwise it is False.

    Used for server to client zone updates
    """
    def isVisible(c):
        return (c.zone not in (c.controller.hand, c.controller.facedowns)
                or c.visible or c.controller is player)

    return ((card.cardId if isVisible(card) else -1), card.owner is not player)


def zone_to_idens(player, zone):
    """
    Return the IDENs for each card in zone relative to player as a flat list
    """
    return [i for c in zone for i in card_to_iden(player, c)]


def encode_args(opcode_name, entities, relative_to_player=None):
    """
    The way that UL represents entities in packets is context-sensitive.
    This function converts entities to the correct representation based on the opcode.
    """

    if opcode_name in ('updatePlayerHand',
                       'updateEnemyHand',
                       'updatePlayerFacedowns',
                       'updateEnemyFacedowns',
                       'updatePlayerFaceups',
                       'updateEnemyFaceups',
                       'updatePlayerGraveyard',
                       'updateEnemyGraveyard'):
        if len(entities) > 1:
            raise EncodeError("Arguments to zone updates should be one zone.")

        return zone_to_idens(relative_to_player, entities[0])
