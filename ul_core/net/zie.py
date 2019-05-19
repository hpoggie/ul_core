from ul_core.net.enums import Zone


def gameEntityToZie(player, entity):
    if entity is None:
        return (-1, -1, 0)
    elif entity is player.face:
        return playerFace()
    elif entity is player.opponent.face:
        return enemyFace()
    else:
        return cardToZie(player, entity)


def cardToZie(player, card):
    """
    Convert a card to Zone, Index, Enemy representation
    """
    return (card.controller.zones.index(card.zone), card.zone.index(card),
            card.controller is player.opponent)


def playerFace():
    return (Zone.face, 0, False)


def enemyFace():
    return (Zone.face, 0, True)
