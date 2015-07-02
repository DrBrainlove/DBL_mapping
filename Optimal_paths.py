import collections,copy,random, datetime
import numpy

"""
Alex Maki-Jokela
Cosmo also wrote something like this awhile ago
Given a list of bars (as sets of two node strings each), brute-forces and iterates to find various optimized paths through all of those bars.
"""


#Given a list of bars, get a list of nodes in those bars
def nodes_from_bars(barlist):
	nodes=[]
	for bar in barlist:
		for node_in_bar in bar:
			if not node_in_bar in nodes:
				nodes.append(node_in_bar)
	return nodes


#Given a current position node and a set of bars that haven't been used yet, return a list of possible next steps
def get_next_bar_options(node,prevnode,bars_remaining):
	result=[]
	double_back=False
	currentnode=node
	for bar in bars_remaining:
		if node in bar:
			result.append(bar)
			currentnode=node
	if not result:
		double_back=True
		for bar in bars_remaining:
			if prevnode in bar:
				result.append(bar)
				currentnode=prevnode
	return double_back,result,currentnode

#You have a bar. You know one node. What's the other node?
#Simple as fuck but annoying to type out
def get_other_node(bar,node):
	if node in bar:
		for node_iter in bar:
			if node_iter!=node:
				return node_iter
	else:
		print "wtf"
		just_crash_fuck_it



#Set the bars here (currently module ar)
bars=[set(["LIE","OLD"]), set(["LIE","TAU"]), set(["OLD","TAU"]), set(["GIG","LIE"]), set(["ERA","IRE"]), set(["ERA","RIB"]), set(["FOG","RIB"]), set(["FOG","TAU"]), set(["GIG","IRE"]), set(["ERA","GIG"]), set(["ERA","LAW"]), set(["EVE","GIG"]), set(["EVE","IRE"]), set(["EVE","LAW"]), set(["EVE","LIE"]), set(["EVE","OLD"]), set(["FOG","OLD"]), set(["GIG","LAW"]), set(["IRE","LAW"]), set(["IRE","RIB"]), set(["LAW","LIE"]), set(["LAW","OLD"]), set(["LAW","RIB"]), set(["LAW","FOG"]), set(["LAW","TAU"])]

#Yay informations
print "There are", len(bars),"bars in this set."

nodes=nodes_from_bars(bars)

#dictionary, each key is the number of times you have to cut the LED strip
#and each value is a list of possible paths with that number of cuts
paths=collections.defaultdict()
paths[999]=[]


def optimize_for_long_strips_minimal_loopbacks():
	#iterate through starting points
	for startnode in nodes:
		print startnode,datetime.datetime.now() #administer a small amount of dopamine as a treat for good user behavior (e.g. patience)
		for x in range(0,3000):
			num_strips=1
			num_loopbacks=0
			strips_since_last_break=0
			#iterate through first moves
			bars_remaining=copy.deepcopy(bars)
			this_path=[]
			node=startnode
			prevnode="###"
			while len(bars_remaining)>0:
				doubled_back,bar_options,node=get_next_bar_options(node,prevnode,bars_remaining)
				if doubled_back:
					num_loopbacks+=1
					this_path.append("LOOPBACK")
				if bar_options:
					choosethisbar=random.choice(bar_options)
					bars_remaining.remove(choosethisbar)
					strips_since_last_break+=1
					this_path.append([node,get_other_node(choosethisbar,node)])
					prevnode=node
					node=get_other_node(choosethisbar,node)
				else:
					num_strips+=1
					this_path.append("BREAK")
					choosethisbar=random.choice(bars_remaining)
					bars_remaining.remove(choosethisbar)
					strips_since_last_break+=1
					node=random.sample(choosethisbar,1)[0]
					prevnode=get_other_node(choosethisbar,node)
					this_path.append([get_other_node(choosethisbar,node),node])

				if not bars_remaining:
					current_best=min(paths.keys())
					if num_strips <= 8:
						if num_strips not in paths:
							paths[num_strips]=collections.defaultdict()
							minloopbacks=9999
						else:
							minloopbacks=min(paths[num_strips].keys())
						if num_loopbacks <= minloopbacks:
							if num_loopbacks not in paths[num_strips]:
								paths[num_strips][num_loopbacks]=[]
							if this_path not in paths[num_strips][num_loopbacks]:
								paths[num_strips][num_loopbacks].append(this_path)

	#How few strips can we use?
	print paths.keys()
	minkey= min(paths.keys())
	lenpaths=len(paths[minkey])
	minloopbacks=min(paths[minkey].keys())
	lenminpathsminloopbacks=len(paths[minkey][minloopbacks])

	#optimize for lowest number of starting points (aka if there are two strips, is there a solution where they start on the same node)
	closest_start_paths=collections.defaultdict()
	for path in paths[minkey][minloopbacks]:
		set_of_first_nodes=set()
		set_of_first_nodes.add(path[0][0])
		prevbar=path[0][0]
		for bar in path:
			if prevbar=="BREAK":
				set_of_first_nodes.add(bar[0])
			prevbar=bar
		how_many_start_nodes=len(set_of_first_nodes)
		if how_many_start_nodes not in closest_start_paths:
			closest_start_paths[how_many_start_nodes]=[]
		closest_start_paths[how_many_start_nodes].append(path)

	minstartnodes=min(closest_start_paths.keys())
	numminstartnodeoptions=len(closest_start_paths[minstartnodes])


	#optimize for the most even number of strips (if we have to use three strips, let's not have one ten bars long and one two bars long)
	#TODO: calculate with pixel lengths.
	most_even_paths=collections.defaultdict()
	for path in paths[8][0]:
		path_bar_lengths=[]
		bars_in_stretch=0
		for bar in path:
			if prevbar=="BREAK":
				path_bar_lengths.append(bars_in_stretch-1)
				bars_in_stretch=1
			else:
				bars_in_stretch+=1
			prevbar=bar
		path_bar_lengths.append(bars_in_stretch)
		le_variance=numpy.var(path_bar_lengths)
		if le_variance not in most_even_paths:
			most_even_paths[le_variance]=[]
		most_even_paths[le_variance].append(path)


	mostevenpathvariance=min(most_even_paths.keys())
	numevenestoptions=len(most_even_paths[mostevenpathvariance])



	print "Minimum number of strips: ",minkey
	print "Given ^^^, minimum number of loopbacks: ",minloopbacks
	print "Options with that many strips and loopbacks: ", lenminpathsminloopbacks
	print "Given that number of strips, minimum number of start nodes: ",minstartnodes
	print "Options with minimum number of start nodes: ",numminstartnodeoptions
	print "Sample option: ",closest_start_paths[minstartnodes][0]
	print "Or if even strip length is important, lowest variance in lengths (by bars, todo: by pixels): ",mostevenpathvariance
	print "Options with above glimmering awesome variance number: ",numevenestoptions
	print "One of those best possible options: ",most_even_paths[mostevenpathvariance][0]

	for bar in most_even_paths[mostevenpathvariance][0]:
		if bar != "BREAK" and bar !="LOOPBACK":
			print bar[0]+"-"+bar[1]


def optimize_for_many_even_short_strips_one_start_node(max_striplen=4):
	#iterate through starting points
	for startnode in nodes:
		print startnode,datetime.datetime.now() #administer a small amount of dopamine as a treat for good user behavior (e.g. patience)
		for x in range(0,500):
	#		if x % 50:
	#			print x,datetime.datetime.now()
			num_strips=1
			num_loopbacks=0
			strips_since_last_break=0
			#iterate through first moves
			bars_remaining=copy.deepcopy(bars)
			this_path=[]
			node=startnode
			doubled_back,bar_options,node=get_next_bar_options(startnode,"###",bars_remaining)
			while len(bars_remaining)>0:
			#	print bars_remaining,strips_since_last_break
				if doubled_back:
					num_loopbacks+=1
					this_path.append("LOOPBACK")
				if bar_options:
					choosethisbar=random.choice(bar_options)
					bars_remaining.remove(choosethisbar)
					strips_since_last_break+=1
					#print choosethisbar,node,this_path
					this_path.append([node,get_other_node(choosethisbar,node)])
					prevnode=node
					node=get_other_node(choosethisbar,node)
					if strips_since_last_break>=max_striplen:
					#	print "x"
						this_path.append("BREAK")
						strips_since_last_break=0
						node=startnode
						doubled_back,bar_options,node=get_next_bar_options(node,"###",bars_remaining)
						while not bar_options and bars_remaining:
							node=random.choice(nodes)
							doubled_back,bar_options,node=get_next_bar_options(node,"###",bars_remaining)
					else:
						doubled_back,bar_options,node=get_next_bar_options(node,prevnode,bars_remaining)
				else:
					num_strips+=1
					this_path.append("BREAK")
					choosethisbar=random.choice(bars_remaining)
					bars_remaining.remove(choosethisbar)
					strips_since_last_break=0
					node=random.sample(choosethisbar,1)[0]
					prevnode=get_other_node(choosethisbar,node)
					this_path.append([get_other_node(choosethisbar,node),node])
					doubled_back,bar_options,node=get_next_bar_options(node,prevnode,bars_remaining)
				if not bars_remaining:
					current_best=min(paths.keys())
					if num_strips <= 8 and num_strips >=6:
						if num_strips not in paths:
							paths[num_strips]=collections.defaultdict()
							minloopbacks=9999
						else:
							minloopbacks=min(paths[num_strips].keys())
						if num_loopbacks <= minloopbacks:
							if num_loopbacks not in paths[num_strips]:
								paths[num_strips][num_loopbacks]=[]
							if this_path not in paths[num_strips][num_loopbacks]:
								paths[num_strips][num_loopbacks].append(this_path)

	#How few strips can we use?
	print paths.keys()
	minkey= min(paths.keys())
	lenpaths=len(paths[minkey])
	minloopbacks=min(paths[minkey].keys())
	lenminpathsminloopbacks=len(paths[minkey][minloopbacks])

	#optimize for lowest number of starting points (aka if there are two strips, is there a solution where they start on the same node)
	closest_start_paths=collections.defaultdict()
	for path in paths[minkey][minloopbacks]:
		set_of_first_nodes=set()
		set_of_first_nodes.add(path[0][0])
		prevbar=path[0][0]
		for bar in path:
			if prevbar=="BREAK":
				set_of_first_nodes.add(bar[0])
			prevbar=bar
		how_many_start_nodes=len(set_of_first_nodes)
		if how_many_start_nodes not in closest_start_paths:
			closest_start_paths[how_many_start_nodes]=[]
		closest_start_paths[how_many_start_nodes].append(path)

	minstartnodes=min(closest_start_paths.keys())
	numminstartnodeoptions=len(closest_start_paths[minstartnodes])


	#optimize for the most even number of strips (if we have to use three strips, let's not have one ten bars long and one two bars long)
	#TODO: calculate with pixel lengths.
	most_even_paths=collections.defaultdict()
	for path in paths[8][0]:
		path_bar_lengths=[]
		bars_in_stretch=0
		for bar in path:
			if prevbar=="BREAK":
				path_bar_lengths.append(bars_in_stretch-1)
				bars_in_stretch=1
			else:
				bars_in_stretch+=1
			prevbar=bar
		path_bar_lengths.append(bars_in_stretch)
		le_variance=numpy.var(path_bar_lengths)
		if le_variance not in most_even_paths:
			most_even_paths[le_variance]=[]
		most_even_paths[le_variance].append(path)


	mostevenpathvariance=min(most_even_paths.keys())
	numevenestoptions=len(most_even_paths[mostevenpathvariance])



	print "Minimum number of strips: ",minkey
	print "Given ^^^, minimum number of loopbacks: ",minloopbacks
	print "Options with that many strips and loopbacks: ", lenminpathsminloopbacks
	print "Given that number of strips, minimum number of start nodes: ",minstartnodes
	print "Options with minimum number of start nodes: ",numminstartnodeoptions
	print "Sample option: ",closest_start_paths[minstartnodes][0]
	print "Or if even strip length is important, lowest variance in lengths (by bars, todo: by pixels): ",mostevenpathvariance
	print "Options with above glimmering awesome variance number: ",numevenestoptions
	print "One of those best possible options: ",most_even_paths[mostevenpathvariance][0]

	for bar in most_even_paths[mostevenpathvariance][0]:
		if bar != "BREAK" and bar !="LOOPBACK":
			print bar[0]+"-"+bar[1]




if __name__=="__main__":
	optimize_for_many_even_short_strips_one_start_node()



		
