from random import choice
from referee.game import PlayerColor, Action, PlaceAction, Coord
from agent.bitboard import BitBoard
import cProfile
import pstats
from wwww import Monte_Carlo_Tree_Node
import io
import time
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
        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        """Attempts to find an empty cell, generate a valid piece, and apply it."""
        empty_cells = self._board.empty_adjacent_cells(self._color)
        if not empty_cells:
            return False  # No empty cells available
        for empty_cell in empty_cells:
            valid_pieces = self._board.generate_valid_pieces(empty_cell)
            if valid_pieces:
                valid_piece = valid_pieces[0]  # Check if there are any valid pieces to place
        return self._board.bitboard_piece_to_placeaction(valid_piece)

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self._board.apply_action(action, color)
