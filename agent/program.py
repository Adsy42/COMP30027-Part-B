# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord, Direction, Board, IllegalActionException
from referee.game.constants import BOARD_N
from referee.game.pieces import PieceType, create_piece
from math import sqrt, log
from random import choice
# python -m referee agent.program:Monte_Carlo_Agent agent.program:Monte_Carlo_Agent

EXPLORATION_CONSTANT = 1.41

class Monte_Carlo_Tree_Node:
    def __init__(self, parent_node, action, colour, board:Board):
        self.colour = colour
        self.opponent_color = PlayerColor.RED if colour == PlayerColor.BLUE else PlayerColor.BLUE
        self.parent_node = parent_node
        self.children_nodes = []
        self.number_of_visits = 0
        self.total_score = 0
        self.action = action 
        self.my_board: Board = board
        #self.opponent_board = board
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
        line_removal(self.action, board_updated, self.colour)

        while board_updated.winner_color is None:
            #Opponents turn
            opponent_move = find_first_valid_placement(board_updated, self.opponent_color)
            line_removal(opponent_move, board_updated, self.opponent_color)
            #Our turn
            our_move = find_first_valid_placement(board_updated, self.colour)
            line_removal(our_move, board_updated, self.colour)

        return board_updated.winner_color
    
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
    
    # def selection(self):
    #     current_node = self
    #     while current_node.children != []:
            
    #         # else choose bes uct score
    #         valid_placements = generate_valid_placements()
    #         current_node.add_children_nodes(valid_placements)
    #     for placement in valid_placements:
    #         current_node


    def selection(self):
        # Check if this node has unexplored children
        #Consider commenting this shit out
        # unexplored_children = [child for child in self.children_nodes if child.number_of_visits == 0]
        # if unexplored_children:
        #     return unexplored_children[0]  # Choose the first unexplored child

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
    
    
class Monte_Carlo_Agent:
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
            self.root_node = Monte_Carlo_Tree_Node(parent_node=None, action=None, colour=self.color, board=referee['board'])        
            
        # Start with the root node and generate all valid movements as children
        current_node = self.root_node
        valid_placement = generate_valid_placements(self.board,self.color)
        current_node.add_children_nodes(valid_placement, current_node.my_board)
        
        
        #Iterate through the children until a leaf node is reached
        while not current_node.is_leaf_node():
            #Choose the children with the highest UCT score
            current_node = current_node.selection()

        #Found leaf node, now check if it has been visited (or simulated)
        if current_node.number_of_visits == 0:
            #lets Rollout 
            winning_colour = current_node.rollout()
            current_node.backpropogate(winning_colour)
        else:
            #We to create a new states of games with all the various possible moves of our opponent
            #First implement action
            board_w_action = self.board.copy()
            # Line removal implements action on board and removes lines
            line_removal(current_node.action, board_w_action, self.color)
            
            boards_w_opp = generate_valid_board_states(board_w_action,self.opponent_color)
            #Create children by generate all the possible actions for those board states with opponents valid moves
            for board_w_opp in boards_w_opp:
                valid_placements = generate_valid_placements(board_w_opp, self.color)
                current_node.add_children_nodes(valid_placements, board_w_opp)
            
            #Current node equals first new child node then call the rollout
            current_node = current_node.selection()
            #lets rollout
            winning_colour = current_node.rollout()
            current_node.backpropogate(winning_colour)



        
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