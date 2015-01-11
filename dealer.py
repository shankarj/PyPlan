import timeit

class DealerClass:

	def __init__(self, agents_list, simulator, num_simulations):
		self.simulator = simulator
		self.playerlist = agents_list
		self.playercount = len(agents_list)
		self.simulation_count = num_simulations
		self.simulationhistory = []

	def start_simulation(self):
		start_time = timeit.default_timer()

		print "\nAGENTS LIST :"

		for count in xrange(len(self.playerlist)):
			print "AGENT {0} : ".format(count) + self.playerlist[count].agentname

			current_rollout = self.playerlist[count].rollout_policy

			while current_rollout is not None:
				print "It's Rollout policy is : " + current_rollout.agentname
				current_rollout = current_rollout.rollout_policy

		print "\nSIMULATION RESULTS :"

		for count in xrange(self.simulation_count):
			print "SIMULATION NUMBER : " + str(count)

			game_history = []
			while self.simulator.gameover == False:
				actual_agent_id = self.simulator.playerturn - 1
				action_to_take = self.playerlist[actual_agent_id].select_action(self.simulator.current_state, self.simulator.playerturn)

				#print "TURN : " + str(action_to_take.get_action()["value"])
				#print "ACTION : " + str(action_to_take.get_action()["position"])

				reward = self.simulator.take_action(action_to_take)
				game_history.append([reward, action_to_take])
				self.simulator.change_turn()

			winner = self.simulator.winningplayer
			self.write_simulation_history(game_history)

			print self.simulator.current_state.get_current_state()
			print "WINNER : " + str(winner)
			print "----------------------------------"

			self.simulator.reset_simulator()

		stop_time = timeit.default_timer()
		print "TOTAL TIME : " + str(stop_time - start_time)

	def simulation_stats(self):
		return self.simulationhistory

	def write_simulation_history(self, game_history):
		self.simulationhistory.append(game_history)

class GameHistoryElement():
	def __init__(self):
		self.gamemoves = []
		self.winner = None

	def add_game_move(self, move):
		self.gamemoves.append(move)

class GameMoveElement():
	def __init__(self, reward_vector, move_by):
		self.reward_vector = reward_vector
		self.played_by = move_by