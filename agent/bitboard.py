from referee.game.constants import BOARD_N
from referee.game.player import PlayerColor
from referee.game.pieces import _TEMPLATES, PieceType
from referee.game.actions import PlaceAction
from referee.game.coord import Coord
TILES_LEN = 4
class BitBoard:
    def __init__(self) -> None:
        """Initializes the BitBoard with separate bitboards for RED, BLUE, and a combined bitboard."""
        self.Boards = {
            PlayerColor.RED: 0,
            PlayerColor.BLUE: 0,
            'combined': 0
        }
        self.tiles = {PlayerColor.RED: 0, PlayerColor.BLUE: 0}
        self.turns_played = 0

    @staticmethod
    def get_bit_index(row: int, column: int) -> int:
        """Converts (row, column) coordinate to the bit position in the bitboard, zero-indexed."""
        return (row * BOARD_N) + column

    @staticmethod
    def get_coord(bitindex: int):
        """Converts a bit index back to (row, column) coordinates."""
        return bitindex // BOARD_N, bitindex % BOARD_N

    @staticmethod
    def create_piece_in_position(piece: PieceType, bitindex:int) -> int:
        """Returns a bitboard representation for a given piece placed at a specific (row, column)."""
        bitboard = 0
        offsets = _TEMPLATES[piece]
        row, column = bitindex // BOARD_N, bitindex % BOARD_N
        for offset in offsets:
            x = (row + offset.r) % BOARD_N
            y = (column + offset.c) % BOARD_N
            bit_index = BitBoard.get_bit_index(x, y)
            bitboard |= (1 << bit_index)
        return bitboard

    def generate_valid_pieces(self, bitindex: int) -> list:
        """Returns a set of bitboards representing valid pieces that can be placed on the board."""
        valid_pieces = list()
        for piece in PieceType:
            bitboard_piece_position = self.create_piece_in_position(piece, bitindex)
            if not (bitboard_piece_position & self.Boards['combined']):
                valid_pieces.append(bitboard_piece_position)
        return valid_pieces

    def lines_removed(self) -> tuple[list[int], list[int]]:
        """Identifies full rows and columns that need to be cleared from the board."""
        row_checks = []
        full_row = (1 << BOARD_N) - 1
        for i in range(BOARD_N):
            if (self.Boards["combined"] & (full_row << (i * BOARD_N))) == (full_row << (i * BOARD_N)):
                row_checks.append(i)

        column_checks = []
        for j in range(BOARD_N):
            full_column = 0
            for i in range(BOARD_N):
                full_column |= (1 << (i * BOARD_N + j))
            if (self.Boards["combined"] & full_column) == full_column:
                column_checks.append(j)

        return (row_checks, column_checks)

    def empty_adjacent_cells(self, player_colour: PlayerColor) -> list[int]:
        """Finds all unique empty cell indices that are adjacent to any tile occupied by the specified player."""
        total_empty_cells = ~self.Boards['combined']
        player_colour_cells = self.Boards[player_colour]
        adjacent_empty_cells = list()

        for index in range(BOARD_N**2):
            if player_colour_cells & (1 << index):
                x = index // BOARD_N
                y = index % BOARD_N
                neighbors = [
                    self.get_bit_index((x - 1) % BOARD_N, y),
                    self.get_bit_index((x + 1) % BOARD_N, y),
                    self.get_bit_index(x, (y - 1) % BOARD_N),
                    self.get_bit_index(x, (y + 1) % BOARD_N)
                ]
                for neighbour in neighbors:
                    if total_empty_cells & (1 << neighbour):
                        adjacent_empty_cells.append(neighbour)

        return adjacent_empty_cells

    @staticmethod
    def bitboard_piece_to_placeaction(bitboard_piece_position):
        """Returns a list of (row, column) tuples for each bit set to 1 in the bitboard."""
        coordinates = []
        for index in range(BOARD_N * BOARD_N):  # Assuming a square board
            if bitboard_piece_position & (1 << index):  # Check if the bit at `index` is set
                row = index // BOARD_N
                column = index % BOARD_N
                coordinates.append(Coord(r=row, c=column))
        
        return PlaceAction(*coordinates)

    def count_bits(self, number: int) -> int:
        """Counts the number of 1s in the binary representation of the number."""
        count = 0
        while number:
            count += number & 1
            number >>= 1
        return count

    def apply_action(self, action: PlaceAction, player_colour: PlayerColor):
        bitboard_piece_position = 0
        for coord in action.coords:
            bitindex = self.get_bit_index(coord.r, coord.c)
            bitboard_piece_position |= (1 << bitindex)

        if not (bitboard_piece_position & self.Boards['combined']):
            self.Boards[player_colour] |= bitboard_piece_position
            self.tiles[player_colour] += TILES_LEN
            self.Boards['combined'] |= bitboard_piece_position
            removed_lines = self.lines_removed()
            self.remove_lines(removed_lines[0], removed_lines[1])

    
    def remove_lines(self, rows: list[int], columns: list[int]):
        """Clears specified full rows and columns from each player's board and updates the combined board."""
        print(f"Removing rows: {rows} and columns: {columns}")
        full_row_mask = (1 << BOARD_N) - 1  # Mask for a full row
        for color in [PlayerColor.RED, PlayerColor.BLUE]:
            for row in rows:
                row_mask = full_row_mask << (row * BOARD_N)
                self.tiles[color] -= self.count_bits(row_mask & self.Boards[color])
                self.Boards[color] &= ~row_mask
            for column in columns:
                column_mask = 0
                for i in range(BOARD_N):
                    column_mask |= (1 << (i * BOARD_N + column))
                self.tiles[color] -= self.count_bits(column_mask & self.Boards[color])
                self.Boards[color] &= ~column_mask
        self.Boards['combined'] = self.Boards[PlayerColor.RED] | self.Boards[PlayerColor.BLUE]
    
    def cell_occupied_by(self, bitindex):
        """Determines if a cell at a given bit index is occupied and by which player."""
        if self.Boards[PlayerColor.RED] & (1 << bitindex):
            return 'r'
        elif self.Boards[PlayerColor.BLUE] & (1 << bitindex):
            return 'b'
        return None

    def render(self, use_color=False, use_unicode=False) -> str:
        """
        Returns a visualization of the game board as a multiline string, with
        optional ANSI color codes and Unicode characters (if applicable).
        """
        def apply_ansi(str, bold=True, color=None):
            bold_code = "\033[1m" if bold else ""
            color_code = ""
            if color == "r":
                color_code = "\033[31m"  # Red
            elif color == "b":
                color_code = "\033[34m"  # Blue
            return f"{bold_code}{color_code}{str}\033[0m"

        output = ""
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                bitindex = self.get_bit_index(r, c)
                occupied_by = self.cell_occupied_by(bitindex)
                if occupied_by:
                    text = 'r' if occupied_by == 'r' else 'b'
                    if use_color:
                        output += apply_ansi(text, color=occupied_by, bold=False)
                    else:
                        output += text
                else:
                    output += "."
                output += " "
            output += "\n"
        print(output)

    def board_control(self, player_colour: PlayerColor):
        control = self.tiles[PlayerColor.RED] - self.tiles[PlayerColor.BLUE]
        return -1 * control if player_colour == PlayerColor.BLUE else control
