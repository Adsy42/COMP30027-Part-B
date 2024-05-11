from referee.game.constants import BOARD_N
from referee.game.player import PlayerColor
from referee.game.actions import PlaceAction
from referee.game.coord import Coord
from .precomputed_bitboards import bitboards_pre_computed, full_rows, full_columns, adjacent_bitboards
from random import choice

BOARD_N = 11
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

    def valid_pieces(self, player_colour: PlayerColor):
        empty_cells = self.empty_adjacent_cells(player_colour)
        valid_pieces = []
        for empty_cell in empty_cells:
            valid_pieces.extend([position
                for position in bitboards_pre_computed[empty_cell]
                if not position & self.Boards['combined']])
        return valid_pieces
    
    def intial_move(self, opponent_colour):
        return choice(self.valid_pieces(opponent_colour))
    
    def lines_removed(self):
        row_checks = [idx for idx, row_bb in enumerate(full_rows)
                      if (self.Boards['combined'] & row_bb) == row_bb]
        column_checks = [idx for idx, col_bb in enumerate(full_columns)
                         if (self.Boards['combined'] & col_bb) == col_bb]
        return (row_checks, column_checks)

    def find_empty_adjacent_cells_from_piece(self, piece_bitboard: int) -> list:
        """Returns a list of bit indexes representing empty adjacent cells to the given piece bitboard."""
        adjacent_positions = set()
        limit = 0
        # Iterate over each bit in the piece_bitboard
        for bit_index in range(BOARD_N * BOARD_N):
            if limit == 4:
                break
            if piece_bitboard & (1 << bit_index):
                limit += 1
                adjacent_cells = adjacent_bitboards[bit_index]
                empty_cells = adjacent_cells & ~self.Boards['combined']
                for shift in range(BOARD_N**2):
                    if empty_cells & (1 << shift):
                        adjacent_positions.add(shift)
        return adjacent_positions

    def empty_adjacent_cells(self, player_colour: PlayerColor) -> list[int]:
            player_cells = self.Boards[player_colour]
            adjacent_empty_cells = set()
            for index in range(BOARD_N**2):
                if player_cells & (1 << index):
                    adjacent_cells = adjacent_bitboards[index]
                    empty_cells = adjacent_cells & ~self.Boards['combined']
                    for shift in range(BOARD_N**2):
                        if empty_cells & (1 << shift):
                            adjacent_empty_cells.add(shift)
            return list(adjacent_empty_cells)


    @staticmethod
    def bitboard_piece_to_placeaction(bitboard_piece_position) -> PlaceAction:
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
    
    def remove_lines(self, rows: list[int], columns: list[int]):
        for color in [PlayerColor.RED, PlayerColor.BLUE]:
            for row in rows:
                row_mask = full_rows[row]
                self.tiles[color] -= self.count_bits(row_mask & self.Boards[color])
                self.Boards[color] &= ~row_mask
            for column in columns:
                col_mask = full_columns[column]
                self.tiles[color] -= self.count_bits(col_mask & self.Boards[color])
                self.Boards[color] &= ~col_mask
        self.Boards['combined'] = self.Boards[PlayerColor.RED] | self.Boards[PlayerColor.BLUE]
    
    def cell_occupied_by(self, bitindex):
        """Determines if a cell at a given bit index is occupied and by which player."""
        if self.Boards[PlayerColor.RED] & (1 << bitindex):
            return 'r'
        elif self.Boards[PlayerColor.BLUE] & (1 << bitindex):
            return 'b'
        return None

    def render(self, use_color=True, use_unicode=True) -> str:
        """
        Returns a visualization of the game board as a multiline string, with
        optional ANSI color codes and Unicode characters (if applicable).
        """
        def apply_ansi(str, bold=True, color=True):
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
    
    def copy(self):
        new_board = BitBoard()
        new_board.Boards = self.Boards.copy()
        new_board.tiles = self.tiles.copy()
        new_board.turns_played = self.turns_played
        return new_board
    
    
    def apply_action(self, action: PlaceAction, player_colour: PlayerColor, bit_board: bool = False):
        if not bit_board:
            bitboard_piece_position = 0
            for coord in action.coords:
                bitindex = self.get_bit_index(coord.r, coord.c)
                bitboard_piece_position |= (1 << bitindex)
        else:
            bitboard_piece_position = action
        
        if not (bitboard_piece_position & self.Boards['combined']):
            self.Boards[player_colour] |= bitboard_piece_position
            self.tiles[player_colour] += TILES_LEN
            self.Boards['combined'] |= bitboard_piece_position
            removed_lines = self.lines_removed()
            self.remove_lines(removed_lines[0], removed_lines[1])
        self.turns_played += 1
    
    def scoring(self, action: int, player_colour: PlayerColor) -> int:
        opponent_colour = PlayerColor.RED if player_colour == PlayerColor.BLUE else PlayerColor.BLUE
        copy_board = self.copy()
        copy_board.apply_action(action, player_colour, bit_board=True)
        return (copy_board.tiles[player_colour] - copy_board.tiles[opponent_colour])
    
    def generate_valid_pieces(self, bitindex: int) -> list:
        """Returns a set of bitboards representing valid pieces that can be placed on the board."""
        return [position
                for position in bitboards_pre_computed[bitindex]
                if not (position & self.Boards['combined'])]
    

    def render1(self, use_color=False, use_unicode=False) -> str:
        """
        Returns a visualization of the game board as a multiline string.
        """
        output = ""
        for r in range(BOARD_N):  # Ensure BOARD_N is defined as the size of the board
            for c in range(BOARD_N):
                bitindex = self.get_bit_index(r, c)  # Ensure this method correctly retrieves the bit index for the cell
                occupied_by = self.cell_occupied_by(bitindex)  # Method to check who occupies the cell
                if occupied_by == 'r':
                    text = 'R'
                elif occupied_by == 'b':
                    text = 'B'
                else:
                    text = '.'
                output += text + " "
            output += "\n"

        # Write the output to a file
        with open("stupid.txt", 'a') as file:
            file.write('\n\n')
            file.write(output)

        return output
    
    def best_piece(self, player_colour: PlayerColor):
        empty_cells = self.empty_adjacent_cells(player_colour)
        best_piece = None
        highest_score = float('-inf')  # Start with the lowest possible score

        for empty_cell in empty_cells:
            valid_positions = [
                position for position in bitboards_pre_computed[empty_cell]
                if not position & self.Boards['combined']
            ]
            
            for position in valid_positions:
                
                # Evaluate the whole board state for the score
                score = self.scoring(position, player_colour)
                if score > highest_score:
                    highest_score = score
                    best_piece = position

        return best_piece # Return the best piece based on the highest scoring