from agent.bit_board.precomputed_bitboards import bitboards_pre_computed, adjacent_bitboards
from agent.bit_board import BitBoard
from referee.game import PlayerColor
def debug():
    for index, placement in bitboards_pre_computed.items():
        for placy in placement:
            new = BitBoard()
            new.apply_action(placy, PlayerColor.RED, True )
            with open("stupid.txt", 'a') as file:
                file.write('\n\n')
                file.write(f"{index}")
            new.render1()
        return

if __name__ == "__main__":
    debug()