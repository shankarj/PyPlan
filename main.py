import dealer
from agents import *
from simulators import *
import os
from xml.dom import minidom

def call_dealer():
    xmldoc = minidom.parse("jobs.xml")
    jobs_list = xmldoc.getElementsByTagName("job")
    job_count = 0

    for job in jobs_list:
        job_count += 1
        players_count = int(job.attributes["playercount"].value)
        simulation_count = int(job.attributes["sim_count"].value)
        simulation_horizon = int(job.attributes["sim_horizon"].value)
        output_file_name = job.attributes["output_file"].value
        game_name = str(job.attributes["game"].value)

        if game_name == "connect4":
            simulator_obj = connect4simulator.Connect4SimulatorClass(num_players = players_count)
        elif game_name == "yahtzee":
            simulator_obj = yahtzeesimulator.YahtzeeSimulatorClass(num_players = players_count)
        elif game_name == "tictactoe":
            simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(num_players = players_count)
        elif game_name == "tetris":
            tetrissimulator.TetrisSimulatorClass(num_players = players_count)

        players_list = job.getElementsByTagName("player")
        agents_list = []

        agent_one = randomagent.RandomAgentClass(simulator=simulator_obj)

        for player in players_list:
            if int(player.attributes["number"].value) == 5:
                agent_uct = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=int(player.attributes["num_simulations"].value),
                                        uct_constant=float(player.attributes["uct_constant"].value),
                                        horizon=int(player.attributes["horizon"].value),
                                        time_limit=int(player.attributes["time_limit"].value))
                agents_list.append(agent_uct)
            elif int(player.attributes["number"].value) == 6:
                agent_ensemble = ensembleuct.EnsembleUCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=int(player.attributes["num_simulations"].value),
                                        uct_constant=float(player.attributes["uct_constant"].value),
                                        horizon=int(player.attributes["horizon"].value),
                                        ensembles=int(player.attributes["ensembles"].value),
                                        parallel=bool(int(player.attributes["parallel"].value)),
                                        time_limit=int(player.attributes["time_limit"].value))
                agents_list.append(agent_ensemble)

        output_file = open(output_file_name, "w")
        output_file.write("PLAYING " + game_name + "\n")
        output_file.write("TOTAL SIMULATIONS : " + str(simulation_count) + "\n")

        print "-" * 50
        print "\nJOB", job_count
        print "\n\nPLAYING " + game_name.upper() + "\n"
        print "TOTAL SIMULATIONS : ", simulation_count

        dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations=simulation_count,
                                           sim_horizon=simulation_horizon, results_file=output_file)
        dealer_object.start_simulation()
        results = dealer_object.simulation_stats()[0]
        winner_list = dealer_object.simulation_stats()[1]

        # RESULTS CALCULATION
        overall_reward = []
        for game in xrange(len(results)):
            game_reward_sum = [0] * players_count

            for move in xrange(len(results[game])):
                game_reward_sum = [x + y for x, y in zip(game_reward_sum, results[game][move][0])]

            print "REWARD OF PLAYERS IN GAME {0} : ".format(game)
            print game_reward_sum
            overall_reward.append(game_reward_sum)

        overall_reward_avg = [0] * players_count
        for game in xrange(len(results)):
            overall_reward_avg = [x + y for x, y in zip(overall_reward_avg, overall_reward[game])]

        for x in xrange(len(overall_reward_avg)):
            overall_reward_avg[x] = overall_reward_avg[x] / simulation_count

        temp_print = "\nAVG OF REWARDS (FOR OVERALL SIMULATION) : " + str(overall_reward_avg)

        win_counts = [0.0] * players_count

        for val in xrange(len(winner_list)):
            if winner_list[val] is not None:
                win_counts[winner_list[val] - 1] += 1.0

        for val in xrange(players_count):
            temp_print += "\nAVG WINS FOR AGENT {0} : {1}".format(val + 1, win_counts[val] / simulation_count)

        print temp_print
        output_file.write("\n" + temp_print + "\n")
        output_file.close()


if __name__ == "__main__":
    call_dealer()




        # agent_temp = egreedyagent.EGreedyAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=20,
        #                                             epsilon=0.5, horizon=10)
        # agent_two = egreedyagent.EGreedyAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=20,
        #                                            epsilon=0.5, horizon=10)
        # agent_three = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one,
        #                                                     pull_count=10, horizon=10)
        # agent_four = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_three,
        #                                                    pull_count=5, horizon=10)
        # agent_five = incuniformagent.IncUniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one,
        #                                                           pull_count=10, horizon=100)
        #
        # agent_LP = leafparalleluct.LeafParallelUCTClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
        #                                     num_simulations=100, num_threads=8, uct_constant=5, horizon=70, time_limit=1)
        #
        # agent_TP_NVL = treeparalleluct_NVL.TreeParallelUCTNVLClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
        #                                     num_simulations=5, threadcount=2,  uct_constant=0.1, horizon=20, time_limit=-1)
        #
        # agent_TP_GM = treeparalleluct_GM.TreeParallelUCTGMClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
        #                                     num_simulations=128, threadcount=2, uct_constant=0.8, horizon=20, time_limit=-1)
        #
        # agent_block = blockparalleluct.BlockParallelUCTClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
        #                                      num_simulations=100, threadcount=2, uct_constant=5, ensembles=4, horizon=100,
        #                                      parallel=True, time_limit=1)