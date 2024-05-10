from referee.game.constants import BOARD_N
from referee.game.coord import Coord
from referee.game.pieces import _TEMPLATES, create_piece
from collections import defaultdict

def get_bit_index(row, column):
    return (row * BOARD_N) + column

def precompute_adjacent_bitboards():
    adjacent_bitboards = {}
    for index in range(BOARD_N**2):
        row, col = divmod(index, BOARD_N)
        neighbors = [
            get_bit_index((row - 1) % BOARD_N, col),  # Up
            get_bit_index((row + 1) % BOARD_N, col),  # Down
            get_bit_index(row, (col - 1) % BOARD_N),  # Left
            get_bit_index(row, (col + 1) % BOARD_N)   # Right
        ]
        adjacent_bitboards[index] = sum(1 << neighbor for neighbor in neighbors)
    return adjacent_bitboards

def precompute_full_rows_columns():
    full_rows = [sum(1 << get_bit_index(row, col) for col in range(BOARD_N)) for row in range(BOARD_N)]
    full_columns = [sum(1 << get_bit_index(row, col) for row in range(BOARD_N)) for col in range(BOARD_N)]
    return full_rows, full_columns

def precompute_bitboards():
    piece_bitboards = defaultdict(dict)
    for piece_type in _TEMPLATES.keys():
        for row in range(BOARD_N):
            for col in range(BOARD_N):
                piece = create_piece(piece_type, Coord(r=row, c=col))
                bitboard_piece_position = 0
                for coord in piece.coords:
                    bitindex = get_bit_index(coord.r, coord.c)
                    bitboard_piece_position |= (1 << bitindex)
                # Change here: Use piece_type as the key, not the piece object
                piece_bitboards[piece_type][(row, col)] = bitboard_piece_position
    return piece_bitboards

def save_bitboards_to_python_file(bitboards, adjacent_bitboards, full_rows, full_columns, filename="precomputed_bitboards.py"):
    with open(filename, 'w') as file:
        file.write("from referee.game.pieces import PieceType\n\n")
        file.write("bitboards = {\n")
        for piece_type, boards in bitboards.items():
            file.write(f"    PieceType.{piece_type.name}: {{\n")
            for (row, col), bitboard in boards.items():
                file.write(f"        ({row}, {col}): {bitboard},\n")
            file.write("    },\n")
        file.write("}\n\n")

        file.write("adjacent_bitboards = {\n")
        for index, bitboard in adjacent_bitboards.items():
            file.write(f"    {index}: {bitboard},\n")
        file.write("}\n\n")

        file.write("full_rows = [\n")
        for row in full_rows:
            file.write(f"    {row},\n")
        file.write("]\n\n")

        file.write("full_columns = [\n")
        for col in full_columns:
            file.write(f"    {col},\n")
        file.write("]\n")

if __name__ == "__main__":
    bitboards = precompute_bitboards()
    adjacent_bitboards = precompute_adjacent_bitboards()
    full_rows, full_columns = precompute_full_rows_columns()
    save_bitboards_to_python_file(bitboards, adjacent_bitboards, full_rows, full_columns)
