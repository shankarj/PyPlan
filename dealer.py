import timeit
import multiprocessing
import psutil
import time
import os
import subprocess

class DealerClass:
    def __init__(self, agents_list, simulator, num_simulations, sim_horizon, results_file, verbose=False):
        self.simulator = simulator
        self.playerlist = agents_list
        self.playercount = len(agents_list)
        self.simulation_count = num_simulations
        self.simulationhistory = []
        self.verbose = verbose
        self.simulation_horizon = sim_horizon
        self.output_file = results_file

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

                if "UCT" in self.playerlist[count].agentname:
                    print_output += "\nNo. of simulations per move :" + str(self.playerlist[count].simulation_count)
                    print_output += "\nTime limit per move :" + str(self.playerlist[count].time_limit)
                    print_output += "\nHorizon value :" + str(self.playerlist[count].horizon)
                    print_output += "\nConstant value :" + str(self.playerlist[count].uct_constant)

                if self.playerlist[count].agentname == "EnsembleUCT":
                    print_output += "\nEnsemble Count : " + str(self.playerlist[count].ensemble_count)
                    print_output += "\nRun in Parallel : " + str(self.playerlist[count].is_parallel)
                    if self.playerlist[count].is_parallel:
                        print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())

                if self.playerlist[count].agentname == "UCT-LP":
                    print_output += "\nThread Count : " + str(self.playerlist[count].threadcount)
                    print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())

                if self.playerlist[count].agentname == "UCT-BP":
                    print_output += "\nEnsemble Count : " + str(self.playerlist[count].ensemble_count)
                    print_output += "\nThread Count : " + str(self.playerlist[count].thread_count)

                if self.playerlist[count].agentname == "UCT-TP-GM":
                    print_output += "\nThread Count : " + str(self.playerlist[count].thread_count)
                    print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())

                if self.playerlist[count].agentname == "UCT-TP-NVL":
                    print_output += "\nThread Count : " + str(self.playerlist[count].thread_count)
                    print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())

                if self.playerlist[count].agentname == "UCT-TP-LM-THREAD":
                    print_output += "\nThread Count : " + str(self.playerlist[count].thread_count)
                    print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())

                if self.playerlist[count].agentname == "UCT-TP-GM-THREAD":
                    print_output += "\nThread Count : " + str(self.playerlist[count].thread_count)
                    print_output += "\nCores in Machine : " + str(multiprocessing.cpu_count())


        self.output_file.write(print_output + "\n")

        for player in xrange(self.playercount):
            self.output_file.write("REWARD FOR " + str(player + 1) + ",")

        self.output_file.write("WINNER,")

        for player in xrange(self.playercount):
            self.output_file.write("AVERAGE TIME/MOVE FOR " + str(player + 1) + ",")

        self.output_file.write("\n")

        if self.verbose:
            print print_output
            print_output = ""
            print ("-" * 50)

        print_output += str("-" * 50) + "\nSIMULATION RESULTS :"

        for count in xrange(self.simulation_count):
            if self.verbose:
                print "CURRENT SIMULATION : " + str(count)

            print_output += "\n\nSIMULATION NUMBER : " + str(count)
            game_history = []
            current_play = 0
            h = 0
            time_values = []

            while self.simulator.gameover == False and h < self.simulation_horizon:
                actual_agent_id = self.simulator.current_state.get_current_state()["current_player"] - 1

                # ASK FOR AN ACTION FROM THE AGENT. MOVE TIME CALCULATION.
                move_start_time = timeit.default_timer()
                action_to_take = self.playerlist[actual_agent_id].select_action(self.simulator.current_state)
                move_end_time = timeit.default_timer()

                # ADD THE TIME VALUES TO A VARIABLE TO CALCULATE AVG TIME PER MOVE.
                time_values.append([actual_agent_id, move_end_time - move_start_time])

                # TAKE THE RETURNED ACTION ON SIMULATOR.
                reward = self.simulator.take_action(action_to_take)
                game_history.append([reward, action_to_take])
                self.simulator.change_turn()
                h += 1

                if self.verbose:
                    print "AGENT", actual_agent_id
                    print "TIME FOR LAST MOVE ", move_end_time - move_start_time
                    print self.simulator.print_board()

            # ----------------------
            # STATISTICS OF THE GAME.
            # ----------------------
            total_game_rew = [0.0] * self.playercount
            for turn in xrange(len(game_history)):
                total_game_rew = [x + y for x, y in zip(total_game_rew, game_history[turn][0])]

            winner = self.simulator.winningplayer
            if self.verbose:
                print "\nREWARDS :", total_game_rew
                print "WINNER :", str(winner)
                print "-" * 50

            for player in xrange(self.playercount):
                self.output_file.write(str(total_game_rew[player]) + ",")

            self.output_file.write(str(winner))

            # CALCULATE AVG TIME PER MOVE
            time_sums = [0.0] * self.playercount
            moves_per_player = float(h / self.playercount)
            for val in time_values:
                time_sums[val[0]] += val[1]

            # time_sums WILL HAVE AVERAGE OF TIME TAKEN BY EACH PLAYER PER MOVE (FOR GIVEN SIMULATION COUNT).
            moves_per_second = [0] * self.playercount
            for sum_value in xrange(len(time_sums)):
                time_sums[sum_value] = time_sums[sum_value] / moves_per_player
                self.output_file.write("," + str(time_sums[sum_value]))

            self.output_file.write("\n")
            self.output_file.flush()
            # --------------
            # END OF STATISTICS
            # ---------------


            self.game_winner_list.append(winner)
            self.write_simulation_history(game_history)
            # print_output += "\n" + str(self.simulator.current_state.get_current_state()["state_val"])
            print_output += "\n" + self.simulator.print_board()
            print_output += "\nWINNER : " + str(winner)
            print_output += "\n----------------------------------"
            self.simulator.reset_simulator()

        stop_time = timeit.default_timer()
        print_output += "\nTOTAL TIME FOR " + str(self.simulation_count) + " SIMULATIONS: " + str(stop_time - start_time) + "\n\n"

        if self.verbose:
            print print_output

    def simulation_stats(self):
        return self.simulationhistory, self.game_winner_list

    def write_simulation_history(self, game_history):
        self.simulationhistory.append(game_history)