from agent.bit_board.precomputed_bitboards import bitboards_pre_computed, adjacent_bitboards
from agent.bit_board import BitBoard
from referee.game import PlayerColor
def debug():
    for placement in adjacent_bitboards.values():
        new = BitBoard()
        new.apply_action(placement, PlayerColor.RED, True )
        new.render1()
    return

if __name__ == "__main__":
    debug()