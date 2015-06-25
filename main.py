import dealer
from agents import *
from simulators import *
import os
import jobparser
import mysimulation
import sys

# --------------------------------------------------------
# THESE VARIABLES SHOULD NOT BE MODIFIED HERE.
# --------------------------------------------------------
verbose = False
job_file = None
read_jobs_file = False
output_file_name = ""

def call_dealer():
    global verbose
    global read_jobs_file
    global output_file_name

    arguments = sys.argv

    # UNDERSTANDING THE COMMAND LINE ARGUMENTS
    next_good = False
    for arg in range(len(arguments)):
        if next_good or arg == 0:
            continue

        if str(arguments[arg]) == "-v" or str(arguments[arg]) == "--verbose":
            verbose = True
        elif str(arguments[arg]) == "-j":
            job_file = str(arguments[arg + 1])
            next_good = True
            read_jobs_file = True
        else:
            print "Unindentified command line argument :", arguments[arg]
            break

    if not verbose:
        print "Starting simulations.\nOutput being written to file. -v for verbose (Command line)."


    # CHECK IF WE NEED TO PARSE JOBS FILE OR RUN MY SIMULATIONS
    if 1:
        job_file = "jobs.xml"
        job_count = jobparser.get_job_count(job_file)
        current_job_number = 0

        for job_num in xrange(job_count):
            [simulator_obj, agents_list] = jobparser.parse_jobs_file(job_file, job_num)
            [game_name, output_file_name, players_count, simulation_count, simulation_horizon] = jobparser.get_sim_details()

            if verbose:
                print "-" * 50
                print "\nJOB", job_num
                print "\n\nPLAYING " + game_name.upper() + "\n"
                print "TOTAL SIMULATIONS : ", simulation_count

            try:
                output_file = open(output_file_name, "w")
                output_file.write("PLAYING " + game_name + "\n")
                output_file.write("TOTAL SIMULATIONS : " + str(simulation_count) + "\n")
            except Exception:
                print "Could not write in the given results file.", output_file_name
                exit()

            dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations=simulation_count,
                                               sim_horizon=simulation_horizon, results_file=output_file,
                                               verbose=verbose)
            dealer_object.start_simulation()
            results = dealer_object.simulation_stats()[0]
            winner_list = dealer_object.simulation_stats()[1]

            results_calculation(results, winner_list, players_count, output_file, mysimulation.simulation_count)
    else:
        [simulator_obj, agents_list] = mysimulation.create_simulation()
        output_file_name = mysimulation.output_file_name
        try:
            output_file = open(output_file_name, "w")
            output_file.write("PLAYING " + mysimulation.game_name + "\n")
            output_file.write("TOTAL SIMULATIONS : " + str(mysimulation.simulation_count) + "\n")
        except Exception:
            print "Could not write in the given results file.", mysimulation.output_file_name
            exit()

        dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations=mysimulation.simulation_count,
                                               sim_horizon=mysimulation.simulation_horizon, results_file=output_file,
                                               verbose=verbose)
        dealer_object.start_simulation()
        results = dealer_object.simulation_stats()[0]
        winner_list = dealer_object.simulation_stats()[1]

        results_calculation(results, winner_list, mysimulation.players_count, output_file, mysimulation.simulation_count)

    if not verbose:
        print "Simulations finished.\nOutput written to file", output_file_name


def results_calculation(results, winner_list, players_count, output_file, simulation_count):
    global verbose

    overall_reward = []
    for game in xrange(len(results)):
        game_reward_sum = [0] * players_count

        for move in xrange(len(results[game])):
            game_reward_sum = [x + y for x, y in zip(game_reward_sum, results[game][move][0])]

        if verbose:
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

    if verbose:
        print temp_print

    output_file.write("\n" + temp_print + "\n")
    output_file.close()



if __name__ == "__main__":
    call_dealer()
