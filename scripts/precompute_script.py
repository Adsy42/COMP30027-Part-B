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
    return adjacent_bitboards

def precompute_full_rows_columns():
    full_rows = [sum(1 << get_bit_index(row, col) for col in range(BOARD_N)) for row in range(BOARD_N)]
    full_columns = [sum(1 << get_bit_index(row, col) for row in range(BOARD_N)) for col in range(BOARD_N)]
    return full_rows, full_columns

from collections import defaultdict

def precompute_bitboards():
    # Mapping from each bit index to bitboards of pieces that occupy that index
    result = defaultdict(list)

    # Loop through all piece types and positions on the board
    for piece_type in _TEMPLATES.keys():
        for row in range(BOARD_N):
            for col in range(BOARD_N):
                # Create a piece at the given position
                piece = create_piece(piece_type, Coord(r=row, c=col))
                # Track the bitboard for this piece
                bitboard_piece_position = 0
                # Calculate bitboard and map each occupied tile to this piece's bitboard
                for coord in piece.coords:
                    # Calculate the bit index for each coordinate
                    bitindex = get_bit_index(coord.r, coord.c)
                    # Set the corresponding bit in the bitboard
                    bitboard_piece_position |= (1 << bitindex)
                # Append this piece's bitboard to all relevant bit indices in the result
                for coord in piece.coords:
                    bitindex = get_bit_index(coord.r, coord.c)
                    result[bitindex].append(bitboard_piece_position)

    # Return the dictionary with bit index keys and list of all bitboards that touch that index
    return result


def save_bitboards_to_python_file(bitboards, adjacent_bitboards, full_rows, full_columns, filename="precomputed_bitboards.py"):
    with open(filename, 'w') as file:
        file.write("from referee.game.pieces import PieceType\n\n")
        file.write("bitboards_pre_computed = {\n")
        for index, boards in bitboards.items():
            file.write(f"    {index}: [\n")
            for board in boards:
                file.write(f"        {board},\n")
            file.write("    ],\n")
        file.write("}\n")

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
