"""
The way that UL represents entities in packets is context-sensitive.
This module converts entities to the correct representation based on the opcode.

The representations are context sensitive because
  (1) server to client zone updates need cardIds,
  (2) client to server messages can sometimes use a single index, but sometimes not,
  (3) I want to minimize the size of the packets.
"""

from ul_core.factions.templars import Templar
from ul_core.factions.thieves import Thief
from ul_core.factions.mariners import Mariner
from ul_core.factions.fae import Faerie

from . import zie


class EncodeError(Exception):
    pass


class DecodeError(Exception):
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


def idens_to_cards(player, flat_list):
    """
    Take a flat list of idens and return the cards for them
    """
    idens = zip(flat_list[::2], flat_list[1::2])
    cards = []
    for cardId, ownedByEnemy in idens:
        if cardId == -1:
            cards.append(
                Card(
                    name="mysterious card",
                    owner=player.opponent,
                    game=player.game,
                    cardId=-1))
        else:
            c = (player.opponent.referenceDeck[cardId] if ownedByEnemy
                    else player.referenceDeck[cardId])
            c.visible = True
            cards.append(c)

    return tuple(cards)


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
    elif opcode_name == 'play':
        return (c_index(entities[0]),)
    elif opcode_name == 'endTurn':
        # For each value in args, append it if it's a bool, otherwise
        # assume it's a card and append the indices for it
        return tuple(
            i for arg in entities
            for i in ([arg] if isinstance(arg, bool) else zie.gameEntityToZie(
                relative_to_player, arg)))
    elif opcode_name == 'makeDecision':
        return tuple(i for card in entities
            for i in zie.gameEntityToZie(relative_to_player, card))
    elif opcode_name == 'useFactionAbility':
        return {
            Templar: lambda entities: tuple(c_index(e) for e in entities),
            # Yes, this is really the way thief ability works. TODO: make the arg order consistent
            Thief: lambda entities: (c_index(entities[0]), entities[2], c_index(entities[1])),
            Mariner: lambda entities: (),
        }[type(relative_to_player)](entities)
    else:
        return entities


def decode_args_from_client(opcode_name, args, relative_to_player):
    if opcode_name == 'mulligan':
        return tuple(relative_to_player.hand[arg] for arg in args)
    elif opcode_name in ('revealFacedown', 'playFaceup'):
        if len(args) > 4:  # 4 = index + ZIE
            raise DecodeError("Multiple targets are not currently supported.")
        else:
            card = (relative_to_player.hand[args[0]]
                    if opcode_name == 'playFaceup'
                    else relative_to_player.facedowns[args[0]])

            if len(args) == 4:
                target = zie.zieToGameEntity(relative_to_player, args[1:])
                return (card, target)
            elif len(args) == 1:
                return card
            else:
                raise DecodeError("Wrong number of arguments.")
    elif opcode_name == 'attack':
        index, target_zie = args[0], args[1:] + [True]  # Target is always an enemy
        attacker = relative_to_player.faceups[index]
        target = zie.zieToGameEntity(relative_to_player, target_zie)
        return (attacker, target)
    elif opcode_name == 'play':
        return relative_to_player.hand[args[0]]
    elif opcode_name == 'endTurn':
        target = zie.zieToGameEntity(relative_to_player, args)
        if target is not None and isinstance(relative_to_player, Faerie):
            return (target,)
        else:
            return ()
    elif opcode_name == 'useFactionAbility':
        # TODO: move the faction ability code here
        return entities
    elif opcode_name == 'makeDecision':
        lst = []
        for t_zie in zip(args[::3], args[1::3], args[2::3]):
            lst.append(zie.zieToGameEntity(relative_to_player, t_zie))

        return tuple(lst)
    else:
        return entities


def decode_args_from_server(opcode_name, args, relative_to_player):
    if opcode_name in ('updatePlayerHand',
                       'updateEnemyHand',
                       'updatePlayerFacedowns',
                       'updateEnemyFacedowns',
                       'updatePlayerFaceups',
                       'updateEnemyFaceups',
                       'updatePlayerGraveyard',
                       'updateEnemyGraveyard'):
        return idens_to_cards(relative_to_player, args)
    else:
        return entities
