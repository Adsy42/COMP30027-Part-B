from referee.game import PlayerColor, Action, PlaceAction, Coord
from agent.bit_board.bitboard import BitBoard
import time

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
        self.time_limit = 2.4
        self.played = False
        self.intial_move = None
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        if not self.played:
            self.played = True
            if not self.intial_move:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            else:
                return self._board.bitboard_piece_to_placeaction(self.intial_move)
        return BitBoard.bitboard_piece_to_placeaction(self._board.best_piece(self._color))

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self._board.apply_action(action, color)
        if not self._board.Boards[self._color]:
            self.intial_move = self._board.intial_move(color)