# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent
# python -m referee agent agent
from referee.game import PlayerColor, Action, PlaceAction, Coord
from .bit_board.bitboard import BitBoard
from .monte_carlo import Monte_Carlo_Tree_Node 
import time
import os
from .profiled_functions import profiler, profiled_function, TimeoutException, time_limited_execution
EXPLORATION_CONSTANT = 1.41
MAX_ACTIONS_PER_OPPONENT = 75

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self._color = color
        self.board = BitBoard() 
        self.played = False
        self.intial_move = None
        self._root = None
        self.profiler = profiler
        self._opponent_colour = PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE
        self.turns_played = 0
        self.param1 = float(os.getenv('PARAM1', '0.0'))
        self.param2 = float(os.getenv('PARAM2', '0.0'))
        self.param3 = float(os.getenv('PARAM3', '0.0'))
        self.param4 = float(os.getenv('PARAM4', '0.0'))
        
        print(f"I'M {self._color.name} AND I'M GONNA OBLITERATE!")
    def monte_carlo_const(self, time_remaining, turns_played, board_dominance, board_gaps):
        return self.param1 * time_remaining +  self.param2* turns_played + self.param3*board_dominance* self.param4*board_gaps
    
    @profiled_function
    def action(self, **referee: dict) -> Action:
        self.profiler.record_action_call()
        self.time_remaining = referee["time_remaining"]
        EXPLORATION_CONSTANT = self.monte_carlo_const(referee["time_remaining"], self.turns_played, 
                                                      self.board.tiles[self._color] - self.board.tiles[self._opponent_colour], 
                                                      len(self.board.valid_pieces(self._color)) - len(self.board.valid_pieces(self._opponent_colour)))
        if not self.played and not self.intial_move:
            self.played = True
            if self._color == self._color:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            else:
                return self.board.bitboard_piece_to_placeaction(self.intial_move)
        self._root = Monte_Carlo_Tree_Node(None, None, self._color, self.board.copy(), self._color, self._opponent_colour)
        start_time = time.time()
        end_time = start_time + 2.4
        self._root.generate_children(self._color, end_time)
        best_move = self.mcts_select_best_move()
        self._root = None 
        self.profiler.export_to_csv()
        self.turns_played += 1
        return BitBoard.bitboard_piece_to_placeaction(best_move.action)
    
    def mcts_select_best_move(self):
        start_time = time.time()
        print(self.time_remaining)
        end_time = start_time + self.time_remaining/(MAX_ACTIONS_PER_OPPONENT - self.turns_played)
        simulation_count = 0
        try:
            while not time_limited_execution(end_time):
                    leaf_node = self.traverse(self._root, end_time)
                    simulation_result = leaf_node.rollout(end_time)
                    leaf_node.backpropagate(simulation_result, end_time)
                    simulation_count += 1
                    self.profiler.record_simulation()
        except(TimeoutException):
            return self._root.best_child()
        print(f"Total simulations conducted in this round: {simulation_count}")
        return self._root.best_child()

    def traverse(self, node, end_time):
        current_node = node
        while not current_node.is_leaf_node() and not time_limited_execution(end_time):
            current_node:Monte_Carlo_Tree_Node = current_node.selection()

        if current_node.number_of_visits == 0:
            # Switch to the opponent's color for the next move
            next_colour = PlayerColor.RED if current_node.colour == PlayerColor.BLUE else PlayerColor.BLUE
            current_node.generate_children(next_colour, end_time)        
        return current_node

    
    def update(self, color: PlayerColor, action: PlaceAction, **referee: dict):
        
        self.board.apply_action(action=action, player_colour=color)
        if not self.board.Boards[self._color]:
            self.intial_move = self.board.intial_move(color)
       
    def print_tree_actions(self, node, depth=0):
        """
        Recursively prints the action for each node in the Monte Carlo tree.

        Parameters:
            node (Monte_Carlo_Tree_Node): The current node in the tree.
            depth (int): The current depth in the tree, used for indentation to visualize tree structure.
        """
        # Print the current node's action, indenting based on the depth in the tree
        indent = "  " * depth  # Indentation based on the depth of the node
        print(f"{indent}Action: {node.action}, Colour: {node.colour}, Visits: {node.number_of_visits}, Score: {node.total_score}, Depth: {depth}")

        # Recursively call this function for all child nodes
        for child in node.children_nodes:
            self.print_tree_actions(child, depth + 1)