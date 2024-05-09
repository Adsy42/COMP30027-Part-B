# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent
# python -m referee agent agent
from random import choice
from referee.game import PlayerColor, Action, PlaceAction, Coord
from agent.bitboard import BitBoard
import cProfile
import pstats
from wwww import Monte_Carlo_Tree_Node
import io
import time

EXPLORATION_CONSTANT = 1.41
MAX_ACTIONS_PER_OPPONENT = 75
AVG_SECS_PER_TURN = 2.4  
MAX_ACTIONS = 75

def profiled_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return result
    return wrapper

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self._color = color
        self._root:Monte_Carlo_Tree_Node = None
        print(f"IM {color} GONNA OBLITERATE!")

    def action(self, **referee: dict) -> Action:
        if not self._root or not self._root.my_board.Boards[self._color]:
            initial_action = self.get_initial_action()
            return initial_action

        if not self._root.children_nodes:
            self._root.generate_children()

        best_move = self.mcts_select_best_move()
        self._root = best_move  
        return BitBoard.bitboard_piece_to_placeaction(best_move.action)  # Assuming conversion
        
    def get_initial_action(self):
        initial_board = BitBoard()        
        if self._color == PlayerColor.RED:
            action = PlaceAction(Coord(3, 3), Coord(3, 4), Coord(4, 3), Coord(4, 4))
        else:
            action = PlaceAction(Coord(2, 3), Coord(2, 4), Coord(2, 5), Coord(2, 6))

        if self._root:
            self._root.my_board.apply_action(action, self._color)
        else:
            initial_board.apply_action(action, self._color)
            self._root = Monte_Carlo_Tree_Node(None, None, self._color, initial_board)

        return action
    
    def mcts_select_best_move(self):
        start_time = time.time()
        while time.time() - start_time < AVG_SECS_PER_TURN:
            leaf_node = self.traverse(self._root)
            simulation_result = leaf_node.rollout()
            leaf_node.backpropagate(simulation_result)
        return self._root.best_child()
    

    def traverse(self, node):
        current_node:Monte_Carlo_Tree_Node = node
        while not current_node.is_leaf_node():
            current_node = current_node.selection()
        return current_node
    
    def update(self, color: PlayerColor, action: PlaceAction, **referee: dict):
        # Check if the action comes from the opponent
        if color != self._color:
            # Check if the root has been initialized
            if not self._root:
                new_board = BitBoard()
                new_board.apply_action(action, color)
                self._root = Monte_Carlo_Tree_Node(None, None, self._color, new_board)
                return

            bitboard_action = self._root.my_board.action_to_bitboard(action)
            found_child = next((child for child in self._root.children_nodes if child.action == bitboard_action), None)

            print(f"NEW MONTE_CARLO: {found_child}")
            if found_child:
                # If a corresponding child node is found, update the root to this child
                self._root = found_child
            else:
                # If no corresponding child node is found, we assume that this part of the tree has not been explored.
                # Create a new board state by copying the root's board and applying the action
                new_board = self._root.my_board.copy()
                new_board.apply_bit_action(color, bitboard_action)
                # Initialize a new Monte Carlo Tree Node as the new root with this updated board state
                self._root = Monte_Carlo_Tree_Node(None, None, self._color, new_board)
