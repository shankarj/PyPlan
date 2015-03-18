PyPlan
======

PyPlan is a set of modular Monte-Carlo planning libraries for Python. The main goal of this project is to offer easy-to-use and flexible planning algorithms. Flexibility is offered in terms of input parameters to the algorithms and easily altering the parameters of execution environments.

This python library provides an API to easily create planning algorithms, domains and also easily interface between them. Using this, any developer would be easily able to create various domains and agents, plug various other agents for the same domain and make effective comparisons.

Basic Architecture
==================

<i>(Third draft. Frozen 1/27/15.)</i>

![archimage](https://raw.githubusercontent.com/shankarj/PyPlan/master/resources/updated_3.png "Architecture of PyPlan")

Usage
=====

The DealerClass initiates a simulation between a given number of agents for the chosen simulator. The constructor is given below.

```
def __init__(self, agents_list, simulator, num_simulations):
```

Input the list of agent objects, simulator object, and the number of simulations(int). A sample usage is given as follows :

Create the simulator object

```
simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(starting_player = 1, num_players = 2)
```

Create agents

```
agent_one = randomagent.RandomAgentClass(simulator = simulator_obj)
agent_two = uniformagent.UniformRolloutAgentClass(simulator = simulator_obj, rollout_policy = agent_one, pull_count = 3)
agent_three = uniformagent.UniformRolloutAgentClass(simulator = simulator_obj, rollout_policy = agent_two, pull_count = 3)

agents_list = [agent_three, agent_one]
```

You can see that the first agent (agent_three) is a nested uniform rollout agent. The second agent (agent_one) is a simple random agent.

Create dealer object and start simulation

```
dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations = 1)
dealer_object.start_simulation()
```
Modules available
=================
<i>(Available as of now)</i>  

Agents:  
1. Uniform Rollout  
2. Incremental Uniform Rollout  
3. e-Greedy Rollout  
4. Random  
5. UCT  
6. Ensemble UCT  

Simulators:  
1. Tic Tac Toe  
2. Connect4  
3. Yahtzee  
4. Tetris  

Note
====
1. starting_player, playerturn are One based indexes.
2. Bitboard representation is used for Connect4. Runs pretty good.
