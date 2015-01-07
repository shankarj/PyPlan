import dealer
import timeit

def call_dealer():
	numsimulations = int(raw_input("Enter number of simulations to run : "))
	numplayers = int(raw_input("Enter number of agents : "))

	if numplayers < 2:
		print("NUMBER OF PLAYERS CAN'T BE LESS THAN 2. SET TO DEFAULT VALUE")
		numplayers = 2

	simulator_type = int(raw_input("Enter simulator type : "))
	agents_list = []

	for value in xrange(numplayers):
		inp = int(raw_input("Enter type of Agent {0} : ".format(str(value + 1))))
		agents_list.append(inp)

	#START SIMULATION
	start_time = timeit.default_timer()

	for sim in xrange(numsimulations):
		print "\nSIMULATION NUMBER : " + str(sim)
		dealer_object = dealer.DealerClass(agents_list, simulator_type, numplayers)
		dealer_object.start_simulation()

	stop_time = timeit.default_timer()

	print "TOTAL TIME : " + str(stop_time - start_time)

if __name__ == "__main__":
	call_dealer()