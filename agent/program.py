# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from typing import List
from referee.game.coord import Direction

BOARD_N = 11
OPONNENT_COLOUR = PlayerColor.BLUE
MY_PLAYER_COLOUR = PlayerColor.RED
TILE_PER_BLOCK_N = 4

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
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        match self._color:
            case PlayerColor.RED:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            case PlayerColor.BLUE:
                print("Testing: BLUE is playing a PLACE action")
                return PlaceAction(
                    Coord(2, 3), 
                    Coord(2, 4), 
                    Coord(2, 5), 
                    Coord(2, 6)
                )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
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


#A micro heurestic that returns the no. of gaps created

def gaps_created(tiles_placed: List[Coord], board: dict[Coord, PlayerColor]):

    adjacent_tiles = set()  # Intialise an empty list to store adjacent unmarked tile coordinates

    #gap_tiles = [] 

    boardCopy = board.copy()

    for tile in tiles_placed:
        boardCopy[tile] = MY_PLAYER_COLOUR

    #Remove any lines 
    line_removal(tiles_placed, boardCopy)

    remaining_action_tiles = set()

    for tile in tiles_placed:
        if tile in boardCopy:
            remaining_action_tiles.add(tile)

    print(remaining_action_tiles)

    no_gaps = 0
    gaps = []
    # Iterate over each tile placed to find unmarked adjacent tiles
    for tile in remaining_action_tiles:
        # Check all four directions around the current tile
        for direction in Direction:
            adjacent_tile = tile + direction.value  # Calculate the adjacent tile's coordinates
            # Check if the adjacent tile is not marked on the board (i.e., is unmarked) and has not already been explored
            if adjacent_tile not in boardCopy and adjacent_tile not in adjacent_tiles:
                # If it's unmarked, add it to the list of adjacent tiles
                adjacent_tiles.add(adjacent_tile)
                #Adjacent tile detected, now see if its a gap
                is_gap = True
                for adj_direction in Direction:
                    surrounding_adj_tile = adjacent_tile + adj_direction.value
                    if surrounding_adj_tile not in boardCopy:
                        is_gap = False
                        break
                if is_gap:
                    print("gap " + str(adjacent_tile))
                    no_gaps+=1

    print(adjacent_tiles)
    return no_gaps  # Return the no of gaps


# Build function that detects if a row or column is removed when a shape is placed then removes any lines
def line_removal(tiles_placed: List[Coord], board: dict[Coord, PlayerColor]):

    MAX_LINE_LENGTH = 11

    rows_to_remove = set()

    columns_to_remove = set()

    # Implement action 
    for coord in tiles_placed:
        board[coord] = PlayerColor.RED
    # print(tiles_placed)
    # print(render_board(board, ansi=True))
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

     # Calculate total number of lines to be removed
    total_lines_removed = len(rows_to_remove) + len(columns_to_remove)

    #original return statement if needed
    #return rows_to_remove, columns_to_remove, remaining
    return total_lines_removed, remaining


def remove_line(rows_to_remove, columns_to_remove, board):
    for row in rows_to_remove:
        for column_tile in range(BOARD_N):
            column_coord = Coord(r=row, c=column_tile)
            if column_coord in board:
                del board[column_coord]
    #column
    for column in columns_to_remove:
        for row_tile in range(BOARD_N):
            row_coord = Coord(r=row_tile,c=column)
            if row_coord in board:
                del board[row_coord]



# A micro heurestic that determines how many are lines removed and how much of other lines are being filled
def lines_filled_removed(tiles_placed: List[Coord], board: dict[Coord, PlayerColor]):

    boardCopy = board.copy()

    for tile in tiles_placed:
        boardCopy[tile] = MY_PLAYER_COLOUR

    #Remove any lines 
    noLinesRemoved, remaining_tiles = line_removal(tiles_placed, boardCopy)

    explored_rows = set()
    explored_columns = set()

    partially_filled_lines = 0
    
    for remaining_tile in remaining_tiles:

        #row
        r_filled = 0
        row = remaining_tile.r

        if row not in explored_rows:
            for column_no in range(BOARD_N):
                column_coord = Coord(r=row, c=column_no)
                if column_coord in boardCopy:
                    r_filled+=1

            r_filled_percent = round(r_filled/BOARD_N,2)
            partially_filled_lines += r_filled_percent

            print("At row " + str(row) + " value: " + str(r_filled_percent))
            #Finished exploring current row
            explored_rows.add(row)
        
        #column
        c_filled = 0
        column = remaining_tile.c
        
        if column not in explored_columns:
            for row_no in range(BOARD_N):
                row_coord = Coord(r=row_no,c=column)
                if row_coord in boardCopy:
                    c_filled+=1
            
            c_filled_percent = round(c_filled/BOARD_N,2)
            partially_filled_lines += c_filled_percent

            print("At column " + str(column) + " value: " + str(c_filled_percent))
            #Finished exploring current column
            explored_columns.add(column)

    value = round(noLinesRemoved + partially_filled_lines,2)
    
    return value


#A Micro heurestic that calculates the path to remove the closest 