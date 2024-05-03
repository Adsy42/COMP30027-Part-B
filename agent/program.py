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
        self.parent_node = parent_node
        self.children_nodes = []
        self.number_of_visits = 0
        self.total_score = 0
        self.action = action 
        self.my_board: Board = board
        self.opponent_board = board
        
    def add_children_nodes(self, placements):
        for placement in placements:
            self.children_nodes.append(Monte_Carlo_Tree_Node(self,placement,))
        self.children_nodes.extend(children_nodes)

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
    
    def rollout_policy(self):
        possible_placements = generate_valid_placements()
        self.board.apply_action(choice(possible_placements))

    def rollout(self):
        num_moves = 0
        while self.board.winner_color == None:
            rollout_policy(self)    
            num_moves += 1    
        return self.board.winner_color
    
    def backpropogate(self, winning_colour):
        while num_moves > 0:
            self.board.undo_action()
            num_moves -= 1

        parent_node = self.parent_node
        while parent_node != None:
            if parent_node.colour == winning_colour:
                parent_node.update_stats(1)
            else:
                parent_node.update_stats(0)
            parent_node = parent_node.parent_node
        
    def selection(self):
        current_node = self
        while current_node.children != []:
            # else choose bes uct score
        valid_placements = generate_valid_placements()
        current_node.add_children_nodes(valid_placements)
        for placement in valid_placements:
            current_node

    
    
class Monte_Carlo_Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")
        self.board: dict[Coord, PlayerColor] = {}
        self.first_turn = True

        # HERUISTIC FUNCTION WEIGHTING
        # EXPLORATION VS EXPLOTATION TERM
        

    def action(self, **referee: dict) -> Action:

        if self.first_turn:
            self.first_turn = False
            if self.color == PlayerColor.RED:
                return PlaceAction(
                        Coord(0, 3), 
                        Coord(0, 4), 
                        Coord(0, 5), 
                        Coord(0, 6)
                    )
            else:
                return PlaceAction(
                        Coord(5, 3), 
                        Coord(5, 4), 
                        Coord(5, 5), 
                        Coord(5, 6)
                    )
        else:
            valid_placement = generate_valid_placements(self.board,self.color)
            return valid_placement[0]
        
    def update(self, color: PlayerColor, action: Action, **referee: dict):
        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        list_coords = [place_action.c1,place_action.c2,place_action.c3,place_action.c4]
        _,_,_=line_removal(list_coords,self.board)
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


def line_removal(tiles_placed: list[Coord], board: dict[Coord, PlayerColor]):

    MAX_LINE_LENGTH = 11

    rows_to_remove = set()

    columns_to_remove = set()

    # Implement action 
    for coord in tiles_placed:
        board[coord] = PlayerColor.RED
   
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