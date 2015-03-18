import dealer
from agents import *
from simulators import *

def call_dealer():
    players_count = 1
    simulation_count = 5

    #simulator_obj = connect4simulator.Connect4SimulatorClass(num_players = players_count)
    #simulator_obj = yahtzeesimulator.YahtzeeSimulatorClass(num_players = players_count)
    simulator_obj = tetrissimulator.TetrisSimulatorClass(num_players = players_count)
    #simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(num_players = players_count)

    agent_one = randomagent.RandomAgentClass(simulator=simulator_obj)

    # agent_temp = egreedyagent.EGreedyAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=20,
    #                                             epsilon=0.5, horizon=10)
    # agent_two = egreedyagent.EGreedyAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=20,
    #                                            epsilon=0.5, horizon=10)
    # agent_three = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one,
    #                                                     pull_count=10, horizon=10)
    # agent_four = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_three,
    #                                                    pull_count=5, horizon=10)
    agent_five = incuniformagent.IncUniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one,
                                                              pull_count=20, horizon=20)
    #
    # agent_uct = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
    #                                    num_simulations=512, uct_constant=5, horizon=10)
    #
    # agent_uct_2 = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
    #                                      num_simulations=10, uct_constant=5, horizon=10)
    #

    agent_ensemble = ensembleuct.EnsembleUCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                         num_simulations=20, uct_constant=5, ensembles=10, horizon=10, parallel=True,
                                         ensemble_method=1)

    agents_list = [agent_one]

    dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations=simulation_count)
    dealer_object.start_simulation()
    results = dealer_object.simulation_stats()[0]
    winner_list = dealer_object.simulation_stats()[1]

    # RESULTS CALCULATION
    overall_reward = []
    for game in xrange(len(results)):
        game_reward_sum = [0] * players_count

        for move in xrange(len(results[game])):
            game_reward_sum = [x + y for x, y in zip(game_reward_sum, results[game][move][0])]

        # for x in xrange(len(game_reward_sum)):
        #      game_reward_sum[x] = game_reward_sum[x] / len(results[game])

        print "REWARD OF PLAYERS IN GAME {0} : ".format(game)
        print game_reward_sum
        overall_reward.append(game_reward_sum)

    overall_reward_avg = [0] * players_count
    for game in xrange(len(results)):
        overall_reward_avg = [x + y for x, y in zip(overall_reward_avg, overall_reward[game])]

    for x in xrange(len(overall_reward_avg)):
        overall_reward_avg[x] = overall_reward_avg[x] / simulation_count

    print "\nAVG OF REWARDS (FOR OVERALL SIMULATION) : "
    print overall_reward_avg

    win_counts = [0.0] * players_count

    for val in xrange(len(winner_list)):
        if winner_list[val] is not None:
            win_counts[winner_list[val] - 1] += 1.0

    for val in xrange(players_count):
        print "AVG WINS FOR AGENT {0} : {1}".format(val + 1, win_counts[val] / simulation_count)

if __name__ == "__main__":
    call_dealer()