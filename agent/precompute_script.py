from referee.game.constants import BOARD_N
from referee.game.pieces import _TEMPLATES, PieceType
from collections import defaultdict

def get_bit_index(row, column):
    return (row * BOARD_N) + column

def create_piece_bitboard(piece, origin_row, origin_col):
    bitboard = 0
    offsets = _TEMPLATES[piece]
    for offset in offsets:
        x = (origin_row + offset.r) % BOARD_N
        y = (origin_col + offset.c) % BOARD_N
        bit_index = get_bit_index(x, y)
        bitboard |= (1 << bit_index)
    return bitboard

def precompute_bitboards():
    piece_bitboards = defaultdict(dict)
    for piece in PieceType:
        for row in range(BOARD_N):
            for col in range(BOARD_N):
                bitboard = create_piece_bitboard(piece, row, col)
                piece_bitboards[piece][(row, col)] = bitboard
    return piece_bitboards

def save_bitboards_to_python_file(bitboards, filename="precomputed_bitboards.py"):
    with open(filename, 'w') as file:
        file.write("from referee.game.pieces import PieceType\n")
        file.write("\n# precomputed_bitboards.py\n")
        file.write("bitboards = {\n")
        
        for piece, boards in bitboards.items():
            file.write(f"    PieceType.{piece.name}: {{\n")
            for (row, col), bitboard in boards.items():
                file.write(f"        ({row}, {col}): {bitboard},\n")
            file.write("    },\n")
        file.write("}\n")

if __name__ == "__main__":
    bitboards = precompute_bitboards()
    save_bitboards_to_python_file(bitboards)
