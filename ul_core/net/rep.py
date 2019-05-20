"""
The way that UL represents entities in packets is context-sensitive.
This module converts entities to the correct representation based on the opcode.

The representations are context sensitive because
  (1) server to client zone updates need cardIds,
  (2) client to server messages can sometimes use a single index, but sometimes not,
  (3) I want to minimize the size of the packets.
"""

from . import zie


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


def c_index(card):
    return card.zone.index(card)


def encode_args_to_client(opcode_name, entities, relative_to_player=None):
    """
    Return the encoded args for a server to client message based on the opcode name
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


def encode_args_to_server(opcode_name, entities, relative_to_player=None):
    """
    Like encode_args_to_client, but to client to server
    """
    if opcode_name == 'mulligan':
        return tuple(c_index(card) for card in entities)
    elif opcode_name in ('revealFacedown', 'playFaceup'):
        if len(entities) > 2:
            raise EncodeError("Multiple targets are not currently supported.")
        elif len(entities) == 2:
            card, target = entities
            return (c_index(card),) + zie.gameEntityToZie(relative_to_player, target)
        else:
            return (c_index(entities[0]),)
    elif opcode_name == 'attack':
        attacker, target = entities
        targetZone, targetIndex, _ = zie.gameEntityToZie(relative_to_player, target)
        return (c_index(attacker), targetZone, targetIndex)
    elif opcode_name == 'endTurn':
        # For each value in args, append it if it's a bool, otherwise
        # assume it's a card and append the indices for it
        return tuple(
            i for arg in entities
            for i in ([arg] if isinstance(arg, bool) else zie.gameEntityToZie(
                relative_to_player, arg)))
