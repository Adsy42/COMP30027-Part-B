from referee.game import PlayerColor, Action, PlaceAction, Coord, Direction, Board, IllegalActionException
from referee.game.constants import BOARD_N
from referee.game.pieces import PieceType, create_piece
from math import sqrt, log
from random import choice

def get_bit_index(x, y, board_size=8):
    """ Convert board coordinates to bit index. """
    return x * board_size + y

def piece_to_bitboard(piece_type, origin, board_size=8):
    """ Translate a piece type and origin to a bitboard representation. """
    bitboard = 0
    offsets = _TEMPLATES[piece_type]
    origin_index = get_bit_index(origin.r, origin.c, board_size)
    for offset in offsets:
        # Calculate the actual board position considering wrapping
        x = (origin.r + offset.r) % board_size
        y = (origin.c + offset.c) % board_size
        bit_index = get_bit_index(x, y, board_size)
        bitboard |= (1 << bit_index)
    return bitboard

def apply_action
def undo_action
def adjacent_empty_tiles(action)
def generate_valid_actions()
def lines_removed()
def 