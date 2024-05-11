# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent
# python -m referee agent agent
from referee.game import PlayerColor, Action, PlaceAction, Coord, MAX_TURNS
from .bit_board.bitboard import BitBoard
from agent.monte_carlo import Monte_Carlo_Tree_Node 
import time
EXPLORATION_CONSTANT = 1.41
MAX_ACTIONS_PER_OPPONENT = 75
AVG_SECS_PER_TURN = 2.4 
MAX_ACTIONS = MAX_TURNS/2

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self._color = color
        self.board = BitBoard() 
        self.played = False
        self.intial_move = None
        self._root = None
        self._opponent_colour = PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE
        print(f"IM {color} GONNA OBLITERATE!")

    def action(self, **referee: dict) -> Action:
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
        
        self._root.generate_children(self._color)
        best_move = self.mcts_select_best_move()
        self._root = None 
        return BitBoard.bitboard_piece_to_placeaction(best_move.action)
    
    def mcts_select_best_move(self):
        start_time = time.time()
        simulation_count = 0
        while time.time() - start_time < AVG_SECS_PER_TURN:
            leaf_node = self.traverse(self._root)
            simulation_result = leaf_node.rollout()
            leaf_node.backpropagate(simulation_result)
            simulation_count += 1
        print(f"Total simulations conducted in this round: {simulation_count}")
        return self._root.best_child()

    def traverse(self, node):
        current_node = node
        while not current_node.is_leaf_node():
            current_node:Monte_Carlo_Tree_Node = current_node.selection()

        if current_node.number_of_visits == 0:
            # Switch to the opponent's color for the next move
            next_colour = PlayerColor.RED if current_node.colour == PlayerColor.BLUE else PlayerColor.BLUE
            current_node.generate_children(next_colour)
            # best_piece = current_node.my_board.best_valid_piece(next_colour)
            
            # if best_piece is not None:
            #     new_board = current_node.my_board.copy()
            #     new_board.apply_action(best_piece, next_colour, True) 
            #     new_child = Monte_Carlo_Tree_Node(current_node, best_piece, next_colour, new_board, self._color, self._opponent_colour)
            #     current_node.children_nodes.append(new_child)
            #     current_node = new_child
        
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