import sys
sys.path.insert(0, "..")

from . import templars
from . import thieves
from . import mariners
from . import fae

availableFactions = [
    templars.Templar, mariners.Mariner, thieves.Thief, fae.Faerie
]
