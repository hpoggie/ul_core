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


def zieToGameEntity(player, zie):
    z, i, e = zie
    # TODO: be more strict, check if zie == (-1, -1, 0)
    # Using this for now for compatibility reasons
    if z == -1:
        return None
    elif z == Zone.face:
        return player.opponent.face if e else player.face
    else:
        return zieToCard(player, z, i, e)


def cardToZie(player, card):
    """
    Convert a card to Zone, Index, Enemy representation
    """
    return (card.controller.zones.index(card.zone), card.zone.index(card),
            card.controller is player.opponent)


def zieToCard(pl, targetZone, targetIndex, targetsEnemy):
    if targetsEnemy:
        target = pl.opponent.zones[targetZone][targetIndex]
    else:
        target = pl.zones[targetZone][targetIndex]

    return target


def playerFace():
    return (Zone.face, 0, False)


def enemyFace():
    return (Zone.face, 0, True)
