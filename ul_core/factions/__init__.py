import sys
sys.path.insert(0, "..")

from . import base
from . import templars
from . import thieves
from . import mariners
from . import fae

availableFactions = [
    templars.Templar, mariners.Mariner, thieves.Thief, fae.Faerie
]

allCards = {}

for module in (base, templars, mariners, thieves, fae):
    for card in module.allCards:
        allCards[card.__name__] = card
        card.iconPath = module.iconPath
