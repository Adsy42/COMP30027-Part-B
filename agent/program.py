# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord, Direction, Board, IllegalActionException
from referee.game.constants import BOARD_N
from referee.game.pieces import PieceType, create_piece
from math import sqrt, log
from random import choice
import time
# python -m referee agent.program:Monte_Carlo_Agent agent.program:Monte_Carlo_Agent
#python -m referee agent agent
EXPLORATION_CONSTANT = 1.41
MAX_ACTIONS_PER_OPPONENT = 75
AVG_SECS_PER_TURN = 2.4    # 180/75
MAX_ACTIONS = 150

class Monte_Carlo_Tree_Node:
    def __init__(self, parent_node, action: PlaceAction, colour, board:Board):
        self.colour = colour
        self.opponent_color = PlayerColor.RED if colour == PlayerColor.BLUE else PlayerColor.BLUE
        self.parent_node = parent_node
        self.children_nodes = []
        self.number_of_visits = 0
        self.total_score = 0
        self.action = action 
        self.my_board: Board = board
        self.move_num = 0
    
    #Untested
    def add_children_nodes(self, actions, board):
        for action in actions:
            new_child = Monte_Carlo_Tree_Node(self, action, self.colour, board)
            new_child.move_num = self.move_num + 1
            self.children_nodes.append(new_child)
    # Works
    def update_stats(self, score):
        self.number_of_visits += 1
        self.total_score += score

    # works
    def uct_value(self, total_visits, exploration_constant):
        if self.number_of_visits == 0:
            return float("inf")    
        mean_value = self.total_score / self.number_of_visits
        return mean_value + exploration_constant*sqrt(log(total_visits)/self.number_of_visits)
    
    # def rollout_policy(self):
    #     possible_placements = generate_valid_placements()
    #     self.board.apply_action(choice(possible_placements))

    def rollout(self):
        #num_moves = 0
        #Intialise game state by implementing current action
        board_updated = self.my_board.copy()
        
        actionPlace = [self.action.c1, self.action.c2, self.action.c3, self.action.c4]
        line_removal(actionPlace, board_updated, self.colour)

        # while board_updated.winner_color() == None:
        #     opponent_move = find_first_valid_placement(board_updated, self.opponent_color)
        #     opponent_coords = [opponent_move.c1, opponent_move.c2, opponent_move.c3, opponent_move.c4]
        #     line_removal(opponent_coords, board_updated, self.opponent_color)

        #     your_move = find_first_valid_placement(board_updated, self.colour)
        #     your_coords = [your_move.c1, your_move.c2, your_move.c3, your_move.c4]
        #     line_removal(your_coords, board_updated, self.colour)

        # return board_updated.winner_color()
        #Keep track of remaining moves for each opponent
        our_move_num = self.move_num + 1  #We just placed our move
        opp_move_num = self.move_num

       
        while 1:
            # Opponent's turn
            opponent_move = find_first_valid_placement(board_updated, self.opponent_color)
            if opponent_move == None:
                return self.colour
            if opp_move_num == MAX_ACTIONS_PER_OPPONENT:
                return self.colour
            opponent_coords = [opponent_move.c1, opponent_move.c2, opponent_move.c3, opponent_move.c4]
            line_removal(opponent_coords, board_updated, self.opponent_color)
            opp_move_num += 1

            # Your turn
            your_move = find_first_valid_placement(board_updated, self.colour)
            if your_move == None:
                return self.colour
            if our_move_num == MAX_ACTIONS_PER_OPPONENT:
                return self.opponent_color
            your_coords = [your_move.c1, your_move.c2, your_move.c3, your_move.c4]
            line_removal(your_coords, board_updated, self.colour)
            our_move_num += 1
       
    def backpropogate(self, winning_colour):

        #Update current node values
        self.number_of_visits += 1
        if self.colour == winning_colour:
            self.total_score += 1
        
        parent_node = self.parent_node
        while parent_node != None:
            #Update the no visited value and score
            parent_node.number_of_visits += 1
            if parent_node.colour == winning_colour:
                parent_node.total_score += 1
                
            parent_node = parent_node.parent_node
    
    def is_leaf_node(self):
        return not self.children_nodes
    

    def selection(self):
        # Check if this node has unexplored children
        #Consider commenting this shit out
        unexplored_children = [child for child in self.children_nodes if child.number_of_visits == 0]
        if unexplored_children:
            return unexplored_children[0]  # Choose the first unexplored child

        # Otherwise, use UCT to select the most promising child
        total_visits = sum(child.number_of_visits for child in self.children_nodes)
        best_child = None
        best_uct_value = float("-inf")
        for child in self.children_nodes:
            uct_value = child.uct_value(total_visits, EXPLORATION_CONSTANT)
            if uct_value > best_uct_value:
                best_uct_value = uct_value
                best_child = child
        return best_child
    
    def highest_avg_win_rate_child(self):
        if not self.children_nodes:
            return None
        
        highest_avg_win_rate = float('-inf')
        best_child = None
        
        for child in self.children_nodes:
            if child.number_of_visits == 0:
                continue
            
            avg_win_rate = child.total_score / child.number_of_visits
            if avg_win_rate > highest_avg_win_rate:
                highest_avg_win_rate = avg_win_rate
                best_child = child
        
        return best_child

    def generate_children(self):

        # Create new board states with opponent's moves
        board_with_action = self.my_board.copy()
        if self.action is not None:
            tiles_placed = [self.action.c1, self.action.c2, self.action.c3, self.action.c4]
            line_removal(tiles_placed, board_with_action, self.colour)

        boards_with_opponent_moves = generate_valid_board_states(board_with_action, self.opponent_color)

         # Generate children nodes for each board state with opponent's moves
        for board_state in boards_with_opponent_moves:
            valid_placements = generate_valid_placements(board_state, self.colour)
            self.add_children_nodes(valid_placements, board_state)

    #This function is different to the normal generate children method as the root node doesnt have an initial action
    def generate_children_for_root_node(self):
        
        #Generate all valid 

        # Create new board states with opponent's moves
        board_with_action = self.my_board.copy()
        if self.action is not None:
            tiles_placed = [self.action.c1, self.action.c2, self.action.c3, self.action.c4]
            line_removal(tiles_placed, board_with_action, self.colour)
            
        boards_with_opponent_moves = generate_valid_board_states(board_with_action, self.opponent_color)

         # Generate children nodes for each board state with opponent's moves
        for board_state in boards_with_opponent_moves:
            valid_placements = generate_valid_placements(board_state, self.colour)
            self.add_children_nodes(valid_placements, board_state)


class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.color = color
        self.opponent_color = PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")
        self.board: dict[Coord, PlayerColor] = {}
        self.first_turn = True

        #Intialise root node to None, will be intiailised when action is called
        self.root_node = None

        # HERUISTIC FUNCTION WEIGHTING
        # EXPLORATION VS EXPLOTATION TERM
        

    def action(self, **referee: dict) -> Action:


        #Intialise the root node if it hasnt already been
        if self.root_node is None:
            #Double check if the board parsed is the referee board or the 
            self.root_node = Monte_Carlo_Tree_Node(parent_node=None, action=None, colour=self.color, board=self.board)

        print("board:")
        print(self.board)
        #Place random action if board is empty
        if len(self.root_node.my_board) == 0:
            return PlaceAction(
                    Coord(2, 3), 
                    Coord(2, 4), 
                    Coord(2, 5), 
                    Coord(2, 6)
                )
        elif is_color_missing(self.root_node.my_board, self.color): #No coloured tiles on board initially
            return PlaceAction(
                    Coord(8, 8), 
                    Coord(8, 7), 
                    Coord(8, 9), 
                    Coord(8, 10)
                )

        # Start with the root node and generate all valid movements as children
        current_node = self.root_node
        valid_placements = generate_valid_placements(self.board, self.color)
        # print("Board")
        # print(self.root_node.my_board)
        print("Valid placements")
        print(valid_placements)

        current_node.generate_children_for_root_node()
    
        # print("Children: ")
        # print(current_node.children_nodes)

        #INCLUDE A BUFFER TIME CONSTANT
        #while round(referee["time_remaining"] / ((MAX_ACTIONS - current_node.my_board.turn_count())/2)) > AVG_SECS_PER_TURN:
        start_time = time.time()
        while (time.time() - start_time) < AVG_SECS_PER_TURN:
            #Iterate through the children until a leaf node is reached
            while not current_node.is_leaf_node(): 
                #Choose the children with the highest UCT score
                #print("Got here!!!!!!")
                current_node = current_node.selection()

            #Found leaf node, now check if it has been visited (or simulated)
            if current_node.number_of_visits == 0:
                #lets Rollout 
                winning_colour = current_node.rollout()
                #print("winning colour")
                #print(winning_colour)
                current_node.backpropogate(winning_colour)

                #current_node = current_node.selection()
                #We need to go back to the root node for the next iteration
                current_node = self.root_node

            else:
                current_node.generate_children()

                #Current node equals first new child node then call the rollout
                current_node = current_node.selection()
                #lets rollout
                winning_colour = current_node.rollout()
                current_node.backpropogate(winning_colour)
                # print("winning colour")
                # print(winning_colour)
                #set current node back to root node for next iteration
                current_node = self.root_node
        
        best_child = self.root_node.highest_avg_win_rate_child()

        return best_child.action
        

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        list_coords = [place_action.c1,place_action.c2,place_action.c3,place_action.c4]
        _,_,_=line_removal(list_coords,self.board, self.color)
        for action in place_action.coords:
            self.board[action] = color

"""
ADD SIMULATION W/ SPACE AND TIME CONSTRAINTS 
"""

# works
def generate_valid_placements(board:dict[Coord], my_player_colour: PlayerColor):
    """Returns a list of all the placeactions"""
    valid_placements:list[PlaceAction] = []
    for coord, board_player_colour in board.items():
        if board_player_colour == my_player_colour:
            for direction in Direction:
                if coord + direction not in board.keys():
                    for piece_type in PieceType:
                        potential_coord = create_piece(piece_type, coord + direction)
                        if all(coord not in board.keys() for coord in potential_coord.coords):
                            valid_placements.append(PlaceAction(*potential_coord.coords))
    return valid_placements

def generate_valid_board_states(board: dict[Coord, PlayerColor], my_player_colour: PlayerColor):
    """Returns a list of valid board states after placing pieces."""
    valid_board_states = []
    for coord, board_player_colour in board.items():
        if board_player_colour == my_player_colour:
            for direction in Direction:
                if coord + direction not in board.keys():
                    for piece_type in PieceType:
                        potential_coord = create_piece(piece_type, coord + direction)
                        if all(coord not in board.keys() for coord in potential_coord.coords):
                            # Copy the board to avoid modifying the original
                            updated_board = board.copy()
                            
                            # Call line removal to update the board
                            line_removal(potential_coord.coords, updated_board, my_player_colour)
                            
                            # Add the updated board state to the result
                            valid_board_states.append(updated_board)
    return valid_board_states


def find_first_valid_placement(board: dict[Coord], my_player_colour: PlayerColor):
    """Returns the first valid placeaction found"""
    for coord, board_player_colour in board.items():
        if board_player_colour == my_player_colour:
            for direction in Direction:
                if coord + direction not in board.keys():
                    for piece_type in PieceType:
                        potential_coord = create_piece(piece_type, coord + direction)
                        if all(coord not in board.keys() for coord in potential_coord.coords):
                            return PlaceAction(*potential_coord.coords)
    return None  # Return None if no valid placement is found


"""def generate_valid_placements(board:Board, my_player_colour: PlayerColor):
    valid_placements:list[PlaceAction] = []
    for piece_type in PieceType:
        try:
            occupied_coords = board._occupied_coords
            for coord in occupied_coords:
                if board._state[coord] == my_player_colour:
                    for direction in Direction:
                        if board._cell_empty(coord + direction):
                            for piece_type in PieceType:
                            try:
                                result = board.apply_action(piece_type)

                            except IllegalActionException:

                        if board._state[coord + direction] 
        except IllegalActionException:"""

#Modified line removal to parse in player colour
def line_removal(tiles_placed: list[Coord], board: dict[Coord, PlayerColor], color: PlayerColor):

    MAX_LINE_LENGTH = 11

    rows_to_remove = set()

    columns_to_remove = set()

    # Implement action 
    for coord in tiles_placed:
        board[coord] = color
    
    #board.apply_action()

    # Iterate through each tile placed seeing if it completed any row or columns
        
    for coord in tiles_placed:

        filled_rows = 0
        filled_columns = 0

        # Check if COLUMN needs to be removed by iterating through rows
        column = coord.c
        for row_tile in range(BOARD_N):
            row_tile_coord = Coord(r=row_tile, c=column)
            if row_tile_coord in board.keys():
                filled_rows += 1
        
        # If all 11 tiles are filled, add column to set
        if filled_rows == MAX_LINE_LENGTH:
            columns_to_remove.add(column)

        # Check if ROW needs to be removed by iterating through columns
        row = coord.r
        for column_tile in range(BOARD_N):
            column_tile_coord = Coord(r=row, c=column_tile)
            if column_tile_coord in board.keys():
                filled_columns += 1
        
        # If all 11 tiles are filled, add row to set
        if filled_columns == MAX_LINE_LENGTH:
            rows_to_remove.add(row)

    #Time to remove the filled rows and columns
    #row
    remove_line(rows_to_remove, columns_to_remove, board)
    remaining = [coord for coord in tiles_placed if coord in board.keys()]
    return rows_to_remove, columns_to_remove, remaining

def remove_line(rows_to_remove, columns_to_remove, board):
    for row in rows_to_remove:
        for column_tile in range(BOARD_N):
            column_coord = Coord(r=row, c=column_tile)
            if column_coord in board:
                del board[column_coord]

    for column in columns_to_remove:
        for row_tile in range(BOARD_N):
            row_coord = Coord(r=row_tile,c=column)
            if row_coord in board:
                del board[row_coord]


def is_color_missing(board, color):
    for tile_color in board.values():
        if tile_color == color:
            return False
    return True
