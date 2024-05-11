from random import choice
from agent.bit_board.bitboard import BitBoard
from referee.game import PlayerColor, Action, PlaceAction, Coord
from agent.bit_board.precomputed_bitboards import bitboards_pre_computed, full_rows, full_columns, adjacent_bitboards
# python -m referee testing_agents.dummy_bot testing_agents.dummy_bot
# python -m referee testing_agents.min-max agent.program
# python -m referee agent.program testing_agents.greedy_search.py 
# python -m referee testing_agents.greedy_search.py  testing_agents.mini_max testing_agents.greedy_search.py 

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
        return BitBoard.bitboard_piece_to_placeaction(choice(self._board.valid_pieces(self._color)))


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self._board.apply_action(action, color)
