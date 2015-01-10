import timeit

class DealerClass:

	def __init__(self, agents_list, simulator, num_simulations):
		self.simulator = simulator
		self.playerlist = agents_list
		self.playercount = len(agents_list)
		self.simulation_count = num_simulations

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

			while self.simulator.is_terminal() == False:
				actual_agent_id = self.simulator.playerturn - 1
				action_to_take = self.playerlist[actual_agent_id].select_action(self.simulator.current_state, self.simulator.playerturn)

				print "TURN : " + str(action_to_take.get_action()["value"])
				print "ACTION : " + str(action_to_take.get_action()["position"])

				self.simulator.take_action(action_to_take)
				self.simulator.change_turn()

			winner = self.simulator.winningplayer

			print self.simulator.current_state.get_current_state()
			print "WINNER : " + str(winner)
			print "----------------------------------"

			self.simulator.reset_simulator()

		stop_time = timeit.default_timer()
		print "TOTAL TIME : " + str(stop_time - start_time)

	def write_history(self):
		raise NotImplementedError
