import timeit
import multiprocessing

class DealerClass:
    def __init__(self, agents_list, simulator, num_simulations, sim_horizon, verbose=True):
        self.simulator = simulator
        self.playerlist = agents_list
        self.playercount = len(agents_list)
        self.simulation_count = num_simulations
        self.simulationhistory = []
        self.verbose = verbose
        self.simulation_horizon = sim_horizon

    def start_simulation(self):
        print_output = ""
        self.game_winner_list = []
        start_time = timeit.default_timer()
        print_output += "\nAGENTS LIST :"

        for count in xrange(len(self.playerlist)):
            print_output += "\n\nAGENT {0} : ".format(count) + self.playerlist[count].agentname
            current_rollout = self.playerlist[count].rollout_policy

            while current_rollout is not None:
                print_output += "\nIt's Rollout policy is : " + current_rollout.agentname
                current_rollout = current_rollout.rollout_policy

            if self.playerlist[count].agentname == "EnsembleUCT":
                print_output += "\nEnsemble Count : " + str(self.playerlist[count].ensemble_count)
                print_output += "\nRun in Parallel : " + str(self.playerlist[count].is_parallel)
                if self.playerlist[count].is_parallel:
                    print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())

        print_output += "\n" + str("-" * 50) + "\nSIMULATION RESULTS :"

        for count in xrange(self.simulation_count):
            print "CURRENT SIMULATION : " + str(count)
            print_output += "\n\nSIMULATION NUMBER : " + str(count)
            game_history = []
            current_play = 0
            h = 0

            while self.simulator.gameover == False and h < self.simulation_horizon:
                actual_agent_id = self.simulator.current_state.get_current_state()["current_player"] - 1
                action_to_take = self.playerlist[actual_agent_id].select_action(self.simulator.current_state)
                # print self.simulator.print_board()
                # print "SHAPE : " + str(action_to_take.get_action()["piece_number"])
                # print "ROT : " + str(action_to_take.get_action()["rot_number"])
                # print "POSITION : " + str(action_to_take.get_action()["position"])
                # print "---------------------------------------------------------"
                reward = self.simulator.take_action(action_to_take)
                # if reward[0] > 0.0:
                #     print "something"
                game_history.append([reward, action_to_take])
                self.simulator.change_turn()
                h += 1

            winner = self.simulator.winningplayer
            self.game_winner_list.append(winner)
            self.write_simulation_history(game_history)
            # print_output += "\n" + str(self.simulator.current_state.get_current_state()["state_val"])
            print_output += "\n" + self.simulator.print_board()
            print_output += "\nWINNER : " + str(winner)
            print_output += "\n----------------------------------"
            self.simulator.reset_simulator()

        stop_time = timeit.default_timer()
        print_output += "\nTOTAL TIME : " + str(stop_time - start_time) + "\n\n"

        if self.verbose:
            print print_output

    def simulation_stats(self):
        return self.simulationhistory, self.game_winner_list

    def write_simulation_history(self, game_history):
        self.simulationhistory.append(game_history)