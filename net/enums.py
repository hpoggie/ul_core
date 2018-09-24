"""
Zone enum for network to use
"""
from ul_core.core.enums import numericEnum

Zone = numericEnum('face', 'faceup', 'facedown', 'hand', 'graveyard')
