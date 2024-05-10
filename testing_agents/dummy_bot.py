from random import choice
from agent.bit_board.bitboard import BitBoard
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N
from agent.monte_carlo import Monte_Carlo_Tree_Node
from agent.bit_board.precomputed_bitboards import bitboards_pre_computed, full_rows, full_columns, adjacent_bitboards
# python -m referee agent.program agent.dummy_bot

EXPLORATION_CONSTANT = 1.41
MAX_ACTIONS_PER_OPPONENT = 75
AVG_SECS_PER_TURN = 2.4  
MAX_ACTIONS = 75

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        self._board:BitBoard = BitBoard()
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        if self._board.Boards[self._color] == 0:
            if self._color == PlayerColor.RED:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            elif self._color == PlayerColor.BLUE:
                print("Testing: BLUE is playing a PLACE action")
                return PlaceAction(
                    Coord(2, 3), 
                    Coord(2, 4), 
                    Coord(2, 5), 
                    Coord(2, 6)
                )
        """Attempts to find an empty cell, generate a valid piece, and apply it."""
        best_piece = self._board.best_valid_piece(self._color)

        empty_cells = self._board.empty_adjacent_cells(player_colour=self._color)
        valid_pieces = []
        for empty_cell in empty_cells:
            valid_pieces.extend(self._board.generate_valid_pieces(empty_cell))

        return BitBoard.bitboard_piece_to_placeaction(choice(valid_pieces))
# row, column = empty_cell // BOARD_N, empty_cell % BOARD_N
# highest_score = float('-inf')

# for positions in bitboards_pre_computed.values():
#     piece_position = positions[(row, column)]
#     if not (piece_position & self.Boards['combined']):
#         score = self.scoring(piece_position, player_colour)
#         if score > highest_score:
#             highest_score = score
#             best_piece = piece_position
# return best_piece

# return BitBoard.bitboard_piece_to_placeaction(best_piece)

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self._board.apply_action(action, color)
