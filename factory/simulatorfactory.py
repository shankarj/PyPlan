from simulators import tictactoesimulator

def create_simulator(simulator_type, player_turn, num_players):
	if simulator_type == 1:
		return tictactoesimulator.TicTacToeSimulatorClass(player_turn, num_players)
	else:
		print "Invalid Simulator type"
