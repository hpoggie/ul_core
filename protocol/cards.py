class ZIE:
    """
    ZIE = Zone, Index, Enemy
    Enemy is true if this is controlled by the opponent.

    ZIE is relative to a player, meaning if you get a ZIE from a client, enemy
    is true if it's controlled by that client's opponent. If you get a ZIE from
    the server, enemy is true if the card is controlled by your opponent.
    """
    Null = ZIE(-1, -1, False)

    def __init__(self, zone, index, enemy):
        self.zone = zone
        self.index = index
        self.enemy = enemy


def zieToCard(pl, zie):
    targetZone, targetIndex, targetsEnemy = zie.zone, zie.index, zie.enemy

    if targetZone == -1:
        return None

    if targetsEnemy:
        target = pl.opponent.zones[targetZone][targetIndex]
    else:
        target = pl.zones[targetZone][targetIndex]

    return target


def cardToZie(player, card):
    if card is None:
        return ZIE.Null

    zone = card.controller.zones.index(card.zone)
    index = card.zone.index(card)
    enemy = card.controller is player.opponent

    return ZIE(zone, index, enemy)
