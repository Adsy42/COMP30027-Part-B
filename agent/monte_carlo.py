from math import log, sqrt
from random import choice
import time
from .bit_board.bitboard import BitBoard
from referee.game.player import PlayerColor
from referee.game.constants import MAX_TURNS
from agent.profiled_functions import profiler, profiled_function, TimeoutException, time_limited_execution
EXPLORATION_CONSTANT = 1.41
MAX_ACTIONS_PER_OPPONENT = 75
AVG_SECS_PER_TURN = 2.4  

class Monte_Carlo_Tree_Node:
    def __init__(self, parent_node, action: int, colour, board: BitBoard, my_colour, opponent_colour):
        self.parent_node = parent_node
        self.action = action
        self.colour = colour
        self.children_nodes = []
        self.number_of_visits = 0
        self.total_score = 0
        self.my_board = board
        self.my_colour = my_colour
        self.opponent_colour = opponent_colour

    def rollout(self, endtime):
        current_board = self.my_board.copy()
        current_color = PlayerColor.RED if self.colour == PlayerColor.BLUE else PlayerColor.BLUE
        while not time_limited_execution(endtime):
            pieces = current_board.valid_pieces(current_color)
            if pieces:
                current_board.apply_action(player_colour=current_color, action=choice(pieces), bit_board=True)
            else:
                break
            current_color = PlayerColor.RED if current_color == PlayerColor.BLUE else PlayerColor.BLUE
        if current_board.turns_played == 150:
            print("reached terminal state")
            red_score = current_board.tiles[PlayerColor.RED]
            blue_score = current_board.tiles[PlayerColor.BLUE]
            winning_color = PlayerColor.RED if red_score > blue_score else PlayerColor.BLUE
            return winning_color
        return PlayerColor.RED if current_color == PlayerColor.BLUE else PlayerColor.BLUE

    def best_child(self):
        if not self.children_nodes:
            return None

        best_score = -float('inf')
        best_node = None
        for child in self.children_nodes:
            if child.number_of_visits > 0:
                child_score = child.total_score / child.number_of_visits
                if child_score > best_score:
                    best_score = child_score
                    best_node = child
        return best_node

    def backpropagate(self, winning_colour, endtime):
        current_node = self
        while current_node and not time_limited_execution(endtime):
            current_node.number_of_visits += 1
            if current_node.colour == self.my_colour and current_node.colour == winning_colour:
                current_node.total_score += 1
            elif current_node.colour == self.opponent_colour and current_node.colour != winning_colour:
                current_node.total_score += 1
            current_node = current_node.parent_node

    def generate_children(self, colour, end_time):
        if not self.children_nodes:
            pieces = self.my_board.valid_pieces(colour)
            op_col = PlayerColor.RED if colour == PlayerColor.BLUE else PlayerColor.BLUE
            for piece in pieces:
                time_limited_execution(end_time)
                new_board = self.my_board.copy()
                new_board.apply_action(player_colour=colour, action=piece, bit_board=True)
                new_node = Monte_Carlo_Tree_Node(self, piece, colour, new_board, self.my_colour, op_col)
                self.children_nodes.append(new_node)

    def selection(self):
        if any(child.number_of_visits == 0 for child in self.children_nodes):
            unvisited = next(child for child in self.children_nodes if child.number_of_visits == 0)
            return unvisited

        total_visits = sum(child.number_of_visits for child in self.children_nodes)
        selected_child = max(self.children_nodes, key=lambda child: child.uct_value(total_visits, EXPLORATION_CONSTANT))
        return selected_child

    def uct_value(self, total_visits, exploration_constant):
        if self.number_of_visits == 0:
            return float("inf") 
        mean_value = self.total_score / self.number_of_visits
        uct_score = mean_value + exploration_constant * sqrt(log(total_visits) / self.number_of_visits)
        return uct_score

    def is_leaf_node(self):
        is_leaf = not self.children_nodes
        return is_leaf