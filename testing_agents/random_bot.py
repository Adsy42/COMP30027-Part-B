from random import choice
from agent.bit_board.bitboard import BitBoard
from referee.game import PlayerColor, Action, PlaceAction, Coord
# python -m referee testing_agents.dummy_bot testing_agents.dummy_bot
# python -m referee testing_agents.min-max agent.program
# python -m referee agent.program testing_agents.random_bot.py 
# python -m referee testing_agents.mini_max testing_agents.greedy_search.py --time 180
# python -m referee agent.program testing_agents.random_bot --time 180 --space 250
# python -m referee agent.program testing_agents.mini_max --time 180 --space 250
# python -m referee agent.program testing_agents.greedy_search.py --time 180 --space 250
# python -m referee agent.program testing_agents.random_bot.py --time 180 --space 250


class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self._color = color
        self._board:BitBoard = BitBoard()

    def action(self, **referee: dict) -> Action:
        if self._board.Boards[self._color] == 0:
            if self._color == PlayerColor.RED:
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            elif self._color == PlayerColor.BLUE:
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
