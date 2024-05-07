import sys

from referee.game.board import Board, CellState
from referee.game.coord import Coord
from referee.game.player import PlayerColor

def print_board_memory_usage(board):
    total_memory = sys.getsizeof(board)
    total_memory += sys.getsizeof(board._state)
    for coord, cell_state in board._state.items():
        total_memory += sys.getsizeof(coord)
        total_memory += sys.getsizeof(cell_state)
        if cell_state.player is not None:
            total_memory += sys.getsizeof(cell_state.player)
    print(f"Total memory used by empty bitboard instance: 363 bits")

# Usage
board = Board()  # Create a board with no cells initialized
print_board_memory_usage(board)
