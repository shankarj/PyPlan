PyPlan
======

PyPlan is a set of modular Monte-Carlo planning libraries for Python. The main goal of this project is to offer easy-to-use and flexible planning algorithms. Flexibility is offered in terms of input parameters to the algorithms and easily altering the parameters of execution environments. 

Basic Architecture
==================

<i>(First draft)</i>

![archimage](https://raw.githubusercontent.com/shankarj/PyPlan/master/resources/updated.png "Architecture of PyPlan")

Usage
=====

The DealerClass initiates a simulation between a given number of agents for the chosen simulator. The constructor is given below.

```
def __init__(self, agents_list, simulator_type, **other_args):
```

Input the list of agent ids, simulator's id, other_args including rollout_policy, heuristic value. (Revision needed).

Agent IDs:

1 - Random agent  
2 - Uniform agent

Simulator IDs:

1 - TicTacToe  
2 - Backgammon (Not yet finished)

other_args["rollout_policy"] = AGENT_ID
