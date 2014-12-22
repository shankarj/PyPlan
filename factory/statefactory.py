from states import tictactoestate

def create_state(simulator_type):
	if simulator_type == 1:
		return tictactoestate.TicTacToeStateClass()
	else:
		print "Invalid Simulator type"