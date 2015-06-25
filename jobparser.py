from xml.dom import minidom
import dealer
from agents import *
from simulators import *

simulation_count = 0
simulation_horizon = 0
players_count = 0
output_file_name = ""
game_name = ""

def get_sim_details():
    return [game_name, output_file_name, players_count, simulation_count, simulation_horizon]

def get_job_count(job_file):
    try:
        xmldoc = minidom.parse(job_file)
    except Exception:
        print "Error opening the Jobs file"
        exit()

    try:
        jobs_list = xmldoc.getElementsByTagName("job")
    except Exception:
        print "Jobs file structure is not valid. Please refer to the usage documentation."
        exit()

    return len(jobs_list)

def parse_jobs_file(job_file, job_number):
    global simulation_count
    global simulation_horizon
    global players_count
    global output_file_name
    global game_name

    try:
        xmldoc = minidom.parse(job_file)
    except Exception:
        print "Error opening the Jobs file"
        exit()

    try:
        jobs_list = xmldoc.getElementsByTagName("job")
    except Exception:
        print "Jobs file structure is not valid. Please refer to the usage documentation."
        exit()

    job_count = 0
    simulator_obj = None
    agents_list = []

    try:
        for job in jobs_list:
            if job_count == job_number:
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
                    simulator_obj = tetrissimulator.TetrisSimulatorClass(num_players = players_count)
                elif game_name == "othello":
                    simulator_obj = othellosimulator.OthelloSimulatorClass(num_players = players_count)
                else:
                    print "Unidentified game name. Please refer developer documentation to know more about how to add a new simulator."
                    exit()

                players_list = job.getElementsByTagName("player")

                for player in players_list:
                    if int(player.attributes["number"].value) == 4:
                        agent_random = randomagent.RandomAgentClass(simulator=simulator_obj)
                        agents_list.append(agent_random)
                    if int(player.attributes["number"].value) == 5:
                        agent_uct = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                                num_simulations=int(player.attributes["num_simulations"].value),
                                                uct_constant=float(player.attributes["uct_constant"].value),
                                                horizon=int(player.attributes["horizon"].value),
                                                time_limit=float(player.attributes["time_limit"].value))
                        agents_list.append(agent_uct)
                    elif int(player.attributes["number"].value) == 6:
                        agent_ensemble = ensembleuct.EnsembleUCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                                num_simulations=int(player.attributes["num_simulations"].value),
                                                uct_constant=float(player.attributes["uct_constant"].value),
                                                horizon=int(player.attributes["horizon"].value),
                                                ensembles=int(player.attributes["ensembles"].value),
                                                parallel=bool(int(player.attributes["parallel"].value)),
                                                time_limit=float(player.attributes["time_limit"].value))
                        agents_list.append(agent_ensemble)
                    elif int(player.attributes["number"].value) == 8:
                        agent_TP_NVL = treeparalleluct_NVL.TreeParallelUCTNVLClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                                threadcount=int(player.attributes["threadcount"].value),
                                                num_simulations=int(player.attributes["num_simulations"].value),
                                                uct_constant=float(player.attributes["uct_constant"].value),
                                                horizon=int(player.attributes["horizon"].value),
                                                time_limit=float(player.attributes["time_limit"].value))
                        agents_list.append(agent_TP_NVL)
                    elif int(player.attributes["number"].value) == 9:
                        agent_LP = leafparalleluct.LeafParallelUCTClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                                num_simulations=int(player.attributes["num_simulations"].value),
                                                num_threads=int(player.attributes["num_threads"].value),
                                                uct_constant=float(player.attributes["uct_constant"].value),
                                                horizon=int(player.attributes["horizon"].value),
                                                time_limit=float(player.attributes["time_limit"].value))
                        agents_list.append(agent_LP)
                    elif int(player.attributes["number"].value) == 10:
                        agent_BP = blockparalleluct.BlockParallelUCTClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                                num_simulations=int(player.attributes["num_simulations"].value),
                                                threadcount=int(player.attributes["threadcount"].value),
                                                ensembles=int(player.attributes["ensembles"].value),
                                                uct_constant=float(player.attributes["uct_constant"].value),
                                                horizon=int(player.attributes["horizon"].value),
                                                time_limit=float(player.attributes["time_limit"].value))
                        agents_list.append(agent_BP)
                    elif int(player.attributes["number"].value) == 11:
                        agent_TP_GM = treeparalleluct_GM.TreeParallelUCTGMClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                                num_simulations=int(player.attributes["num_simulations"].value),
                                                threadcount=int(player.attributes["threadcount"].value),
                                                uct_constant=float(player.attributes["uct_constant"].value),
                                                horizon=int(player.attributes["horizon"].value),
                                                time_limit=float(player.attributes["time_limit"].value))
                        agents_list.append(agent_TP_GM)

                break
            else:
                job_count += 1

    except Exception:
        print "Error while reading the job number", job_count, ". Please refer the usage documentation."
        exit()


    return [simulator_obj, agents_list]