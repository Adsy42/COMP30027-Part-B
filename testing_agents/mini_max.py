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
        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        """Attempts to find an empty cell, generate a valid piece, and apply it."""
        start_time = time.time()
        end_time = start_time + self.time_limit  # Define end time based on the current time and time limit
        best_move = None
        best_value = float('-inf')
        for move in self._board.valid_pieces(self._color):
            new_board = self._board.copy()
            new_board.apply_action(move, self._color, True)
            move_value = self.minimax(new_board, float('-inf'), float('inf'), False, end_time)
            if move_value > best_value:
                best_value = move_value
                best_move = move
        return BitBoard.bitboard_piece_to_placeaction(best_move)

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self._board.apply_action(action, color)
        if not self._board.Boards[self._color]:
            self.intial_move = self._board.intial_move(color)
            print(self.intial_move)

        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")

    def minimax(self, board, alpha, beta, maximizingPlayer, end_time, depth = 0):
        if time.time() > end_time or depth > 2:  # Check if the current time exceeds the end time
            player_colour = self._color if maximizingPlayer else PlayerColor.BLUE if self._color == PlayerColor.RED else PlayerColor.RED
            return self.evaluate(player_colour, board)

        if maximizingPlayer:
            maxEval = float('-inf')
            for move in board.valid_pieces(self._color):
                if time.time() > end_time:
                    break  # Early exit if time limit is reached during loop
                new_board = board.copy()
                new_board.apply_action(move,self._color, True)
                eval = self.minimax(new_board, alpha, beta, False, end_time, depth + 1)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = float('inf')
            opponent_color = self.opponent_color(self._color)
            for move in board.valid_pieces(opponent_color):
                if time.time() > end_time:
                    break  # Early exit if time limit is reached during loop
                new_board = board.copy()
                new_board.apply_action(move,opponent_color, True)
                eval = self.minimax(new_board, alpha, beta, True, end_time, depth + 1)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval

    def evaluate(self, current_player, board: BitBoard):
        # Check if the game should end by move limit
        if board.turns_played == 150:
            # Check if the current player has no valid moves
            if not len(board.valid_pieces(current_player)):
                # Determine the outcome based on which player is out of moves
                return float('-inf') if self._color == current_player else float('inf')

        # Check if the current player has no valid moves (game might end)
        elif not len(board.valid_pieces(current_player)):
            # Return the game outcome based on current player and their available moves
            return float('-inf') if self._color == current_player else float('inf')
        
        opponent_colour = PlayerColor.RED if self._color == PlayerColor.BLUE else PlayerColor.BLUE
        my_score = len(board.valid_pieces(self._color))
        opponent_score = len(board.valid_pieces(opponent_colour))
        return (board.tiles[self._color] - board.tiles[opponent_colour]) + (my_score - opponent_score)

    def opponent_color(self, color):
        return PlayerColor.BLUE if color == PlayerColor.RED else PlayerColor.RED