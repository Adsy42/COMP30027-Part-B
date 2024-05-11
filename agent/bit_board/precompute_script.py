from referee.game.constants import BOARD_N
from referee.game.coord import Coord, Direction, Vector2
from referee.game.pieces import _TEMPLATES, create_piece
from collections import defaultdict

def get_bit_index(row, column):
    return (row * BOARD_N) + column

def precompute_adjacent_bitboards():
    adjacent_bitboards = {}
    for row in range(BOARD_N):
        for column in range(BOARD_N):
            coord = Coord(row, column)
            neighbors = []
            for direction in Direction:
                new_coord = coord + direction
                neighbors.append(get_bit_index(new_coord.r, new_coord.c))
            adjacent_bitboards[get_bit_index(coord.r, coord.c)] = sum(1 << neighbor for neighbor in neighbors)
        print(adjacent_bitboards)
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
                piece_bitboards[piece_type][(row, col)] = bitboard_piece_position
    return piece_bitboards

def save_bitboards_to_python_file(bitboards, adjacent_bitboards, full_rows, full_columns, filename="precomputed_bitboards.py"):
    with open(filename, 'w') as file:
        file.write("from referee.game.pieces import PieceType\n\n")
        file.write("bitboards_pre_computed = {\n")
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
