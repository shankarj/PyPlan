import dealer

def call_dealer():
	numplayers = int(raw_input("Enter number of agents : "))
	simulator_type = int(raw_input("Enter simulator type : "))
	agents_list = []

	for value in xrange(numplayers):
		inp = int(raw_input("Enter type of Agent {0} : ".format(str(value + 1))))
		agents_list.append(inp)

	dealer_object = dealer.DealerClass(agents_list, simulator_type, numplayers)

if __name__ == "__main__":
	call_dealer()



