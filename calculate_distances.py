import os,csv, math, collections, random


ground_nodes = ["WAX","AIM","LID","BOX","HUG","FLU","SIR","ONO","TAT","COP","NEW","GET","OAK","CAB","AMP","YAY","HAY","BAM","CIS","OFF","WHO","NIX","PIE","RUM","SIP"]



def make_bars_subset(bars_target=400):

	#copied and pasted from below. not optimized at all and not worth trimming. this is just to load the whole bar map to whittle down from
	bars=[]
	node_connections = collections.defaultdict()
	with open("node_info_DBL1.csv","rb") as f: #old coordinates but still has right bar mapping
	   rdr=csv.reader(f)
	   rdr.next()
	   for line in rdr:
	      startnod=line[0]
	      for x in [4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34]:
	         if len(line)>=x+1:
	            endnod=line[x]
	            nodes_set=set([startnod,endnod])
	            if "FEW" not in nodes_set:
		            if startnod not in node_connections:
		            	node_connections[startnod]=[]
		            node_connections[startnod].append(endnod)
		            if endnod not in node_connections:
		            	node_connections[endnod]=[]
		            node_connections[endnod].append(startnod)
		            if nodes_set not in bars: #avoid duplicates
			            bars.append(nodes_set)


	bars_subset_test = bars
	max_connected_nodes = 0
	node_connection_numbers=collections.defaultdict()

	for bar in bars:
		for nod in bar:
			bars_connected=0
			for barrrr in bars:
				if nod in barrrr:
					bars_connected+=1
			if bars_connected > max_connected_nodes:
				max_connected_nodes = bars_connected
			node_connection_numbers[nod]=bars_connected

	node_connected_cutoff=max_connected_nodes
	plz_keep_a_mesh=3
	
	while len(bars_subset_test) > bars_target:
		bars_removed_this_round=0
		remove_these=[]
		for node in node_connection_numbers:
			if node_connection_numbers[node]>=node_connected_cutoff:
				connected_bars=[]
				for barrrr in bars_subset_test:
					if node in barrrr:
						connected_bars.append(barrrr)
				random_removal_candidate=random.choice(connected_bars)
				rrc_nodes=sorted(list(random_removal_candidate))

				bar_is_okay_to_remove=True
				
				#see if the bar is going to create something jutting off into space
				for potentialremovenod in rrc_nodes:
					connected_bars_to_node=0
					for subsetbar in bars_subset_test:
						if potentialremovenod in subsetbar:
							connected_bars_to_node+=1
					if connected_bars_to_node<plz_keep_a_mesh:
						bar_is_okay_to_remove=False

				#no removing ground bars
				if rrc_nodes[0] in ground_nodes and rrc_nodes[1] in ground_nodes:
					bar_is_okay_to_remove=False

				if bar_is_okay_to_remove and random_removal_candidate not in remove_these:
					remove_these.append(random_removal_candidate)


		for removebar in remove_these:
			bars_subset_test.remove(removebar)
			bars_removed_this_round+=1

		if bars_removed_this_round==0:
			node_connected_cutoff-=1
			print node_connected_cutoff


		for bar in bars_subset_test:
			for nod in bar:
				bars_connected=0
				for barrrr in bars_subset_test:
					if nod in barrrr:
						bars_connected+=1
				node_connection_numbers[nod]=bars_connected

		"""
		for bar in bars_subset_test:
			lbar=sorted(list(bar))
			node1=lbar[0]
			node2=lbar[1]
			groundbar=False
			if node1 in ground_nodes and node2 in ground_nodes:
				groundbar=True
			node1conns=0
			node2conns=0
			for barrrr in bars_subset_test:
				if node1 in barrrr:
					node1conns+=1
				if node2 in barrrr:
					node2conns+=1
			if node1conns >= node_connected_cutoff and node2conns <= node_connected_cutoff and bar not in remove_these and not groundbar:
				remove_these.append(bar)
		for removebar in remove_these:
			bars_subset_test.remove(removebar)
			bars_removed_this_round+=1
		if bars_removed_this_round==0:
			node_connected_cutoff+=1
			print node_connected_cutoff"""

	print len(bars_subset_test)

	outputbarlist=[] 

	for bar in bars_subset_test:
		outputbarlist.append('-'.join(sorted(list(bar))))

	return outputbarlist






def xyz_dist(point1,point2):
	return math.sqrt(math.pow((point2[0]-point1[0]),2) +  math.pow((point2[1]-point1[1]),2) + math.pow((point2[2]-point1[2]),2))


class BarSubset(object):
	def __init__(self,active_bars=None,filename_append=None):
		use_these = []
		for active_bar in active_bars:
			sortedbar = '-'.join(sorted(list(active_bar.split('-'))))
			use_these.append(sortedbar)
		self.active_bars = use_these
		self.filename_append=filename_append
		self.active_nodes = []
		#automatically infers active nodes from active bars
		for bar in self.active_bars:
			nodes_in_bar = bar.split('-')
			for node in nodes_in_bar:
				if node not in self.active_nodes:
					self.active_nodes.append(node)

#SETTINGS GO HERE FOR SUBSETS OF BARS TO REGURGITATE
#No module numbers (ABC-DEF not ABC-DEF1) but don't worry about typing them in alphabetically, the object code will handle that.
#Should be sufficient for figuring out which bars to use since P2LX code already just uses the z-highest of any double bars.
#what to append to filename ("full", "one_third_bars", "module_14", etc)
bar_subsets = []

filename_append = "Full_Brain"
active_bars = [] #null value is treated as "just use everything"
fullBrainSubset = BarSubset(active_bars,filename_append)
bar_subsets.append(fullBrainSubset)

#PUT THE EXPERIMENTAL BAR SUBSET HERE
filename_append = "Partial_Brain"
active_bars = ["NIL-AHI","NIL-TOY","NIL-EON","NIL-JOB","NIL-JUG","NIL-ERA","NIL-ADO","JOB-ADO","JOB-NAY","JOB-NIL","JOB-JUG","JOB-TOY","JUG-ERA","JUG-RIB","JUG-SOY","JUG-AHI"] # BAR LIST GOES HERE
partialBrainSubset = BarSubset(active_bars,filename_append)
bar_subsets.append(partialBrainSubset)


#PUT THE EXPERIMENTAL BAR SUBSET HERE
filename_append = "Algorithmic_Brain"
active_bars = make_bars_subset(400)
algorithmicBrainSubset = BarSubset(active_bars,filename_append)
bar_subsets.append(algorithmicBrainSubset)

for bar_subset in bar_subsets:
	#load things from the object
	active_nodes = bar_subset.active_nodes
	active_bars = bar_subset.active_bars
	if filename_append:
		filename_append = '_'+bar_subset.filename_append
	else:
		filename_append = ''
	print "FILE:",filename_append
	bars=[]
	node_connections = collections.defaultdict()
	with open("node_info_DBL1.csv","rb") as f: #old coordinates but still has right bar mapping
	   rdr=csv.reader(f)
	   rdr.next()
	   for line in rdr:
	      startnod=line[0]
	      for x in [4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34]:
	         if len(line)>=x+1:
	            endnod=line[x]
	            nodes_set=set([startnod,endnod])

	            if not active_bars: #if active_bars is null then it's just the full brain mapping
	            	add_thisn = True
	            else:
	            	add_thisn = False
	            	bar_string = '-'.join(sorted(list(nodes_set)))
	            	if bar_string in active_bars:
	            		add_thisn = True

	            if add_thisn:
		            if startnod not in node_connections:
		            	node_connections[startnod]=[]
		            node_connections[startnod].append(endnod)
		            if endnod not in node_connections:
		            	node_connections[endnod]=[]
		            node_connections[endnod].append(startnod)
		            if nodes_set not in bars: #avoid duplicates
			            bars.append(nodes_set)


	node_xyz=collections.defaultdict()
	node_module_xyz=collections.defaultdict()
	module_dict=collections.defaultdict()
	bars_dict = collections.defaultdict()

	with open("node_locations_150501_zeroed.csv","rU") as f:
		rdr=csv.reader(f)
		rdr.next()
		for line in rdr:
			modul=line[0]
			node=line[1]
			x=float(line[2])
			y=float(line[3])
			z=float(line[4])
			add_node = True
			if active_nodes:
				if node in active_nodes:
					add_node = True
				else:
					add_node = False
			if add_node:
				if modul not in module_dict:
					module_dict[modul]=set()
				module_dict[modul].add(node)
				node_xyz[node]=[x,y,z] #just for cross module bars
				node_module_xyz[node+"-"+str(modul)]=[x,y,z]


	total_distance_with_duplicates=0.0
	total_distance_sans_duplicates=0.0
	double_bars_length=0.0
	crossbars=0.0

	module_distances=collections.defaultdict()
	module_bars=[]
	module_bars_sans_doubles=[]
	double_bars=[]
	cross_module_bars=[]
	bar_lengths=collections.defaultdict()


	for modul in module_dict:
		module_distances[modul]=0.0
		nods=module_dict[modul]
		for bar in bars:
			in_module=True
			for barnode in bar:
				if barnode not in nods:
					in_module=False
			if in_module:
				if bar not in module_bars:
					barnods=list(bar)
					barlength=xyz_dist(node_module_xyz[barnods[0]+"-"+str(modul)],node_module_xyz[barnods[1]+"-"+str(modul)])
					total_distance_sans_duplicates+=barlength
					total_distance_with_duplicates+=barlength
					module_distances[modul]+=barlength
					bar_lengths[str(barnods[0])+"-"+str(barnods[1])+"-"+str(modul)]=barlength
					module_bars.append(bar)
					module_bars_sans_doubles.append(bar)
				else: #it's a double bar
					barnods=list(bar)
					barlength=xyz_dist(node_module_xyz[barnods[0]+"-"+str(modul)],node_module_xyz[barnods[1]+"-"+str(modul)])
					total_distance_with_duplicates+=barlength
					module_distances[modul]+=barlength
					bar_lengths[str(barnods[0])+"-"+str(barnods[1])+"-"+str(modul)]=barlength
					module_bars.append(bar)
					double_bars.append(bar)
					double_bars_length+=barlength
					

	for bar in bars:
		if bar not in module_bars:
			cross_module_bars.append(bar)

	#print len(cross_module_bars)

	to_bar_or_not_to_bar = []

	for bar in cross_module_bars:
		barnods=list(bar)
		try:
			barlength=xyz_dist(node_xyz[barnods[0]],node_xyz[barnods[1]])
			bar_lengths[str(barnods[0])+"-"+str(barnods[1])]=barlength
			crossbars+=barlength
		except:
			#print "eh",bar
			to_bar_or_not_to_bar.append(bar)

	for bar in to_bar_or_not_to_bar:
		cross_module_bars.remove(bar)

	bars_with_module_nums=[]
	crossbars_with_module_nums=[]

	model_bars=collections.defaultdict()
	physical_bars=collections.defaultdict()

	#Write out the pixel mappings to read into the model
	#TODO figure out a heuristic for which modules the cross bars attach to and add them into the model. They're currently absent.

	pixelmappingfilename = "pixel_mapping%s.csv"%(filename_append)

	with open(pixelmappingfilename,"wb") as f:
		wrtr=csv.writer(f)
		pixel_counter=0
		led_spacing=0.656168 #inches. the model is in inches. TODO: Use millimeters. One day we will be free from tyanny. And inches.
		wrtr.writerow(["Pixel_i","Module1","Module2","Node1","Node2","X","Y","Z"])
		for modul in module_dict:
			module_distances[modul]=0.0
			nods=module_dict[modul]
			for bar in bars:
				in_module=True
				for barnode in bar:
					if barnode not in nods:
						in_module=False
				if in_module:
					#for consistency always have bar node pairs in alphabetical order
					#Earlier, this was by x-position but was changed because alphabetical is going to make things easier down the line
					barnods=sorted(list(bar))
					nod1=node_module_xyz[barnods[0]+"-"+str(modul)]
					nod2=node_module_xyz[barnods[1]+"-"+str(modul)]
					bar_w_mod_num = barnods[0]+"-"+barnods[1]+"-"+str(modul)
					if bar_w_mod_num not in bars_with_module_nums:
						bars_with_module_nums.append(bar_w_mod_num)
					node_1_name=barnods[0]
					node_2_name=barnods[1]				

					#figure out if the alphabetically ordered nodes are increasing or decreasing in the x-direction for 
					#iteratively adding LEDs down it
					forward_x = nod1[0]<nod2[0]
					barlen=xyz_dist(nod1,nod2)
					dx=(nod2[0]-nod1[0])/barlen*led_spacing
					dy=(nod2[1]-nod1[1])/barlen*led_spacing
					dz=(nod2[2]-nod1[2])/barlen*led_spacing
					pixel=nod1		
					if forward_x:
						while pixel[0]<nod2[0]:
							pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
							pixel_counter+=1
							wrtr.writerow([pixel_counter,modul,modul,node_1_name,node_2_name]+pixel)
					else:
						while pixel[0]>nod2[0]:
							pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
							pixel_counter+=1
							wrtr.writerow([pixel_counter,modul,modul,node_1_name,node_2_name]+pixel)

		#same monkey, different banana
		for bar in cross_module_bars:
			barnods=sorted(list(bar))
			for modul in module_dict:
				if barnods[0] in module_dict[modul]:
					node_1_name = barnods[0]+"-"+str(modul)
					crossbar_modul=modul
				if barnods[1] in module_dict[modul]:
					node_2_name = barnods[1]+"-"+str(modul)
					other_modul=modul
			if not(node_1_name and node_2_name):
				print "Bar:",bar,"...dafuq?"
			else:
				nod1=node_xyz[barnods[0]]
				nod2=node_xyz[barnods[1]]
				forward_x = nod1[0]<nod2[0]
				crossbar_w_mod_num = barnods[0]+"-"+barnods[1]+"-"+str(crossbar_modul)+"-"+str(other_modul)
				if crossbar_w_mod_num not in crossbars_with_module_nums:
					crossbars_with_module_nums.append(crossbar_w_mod_num)

				barlen=xyz_dist(nod1,nod2)
				dx=(nod2[0]-nod1[0])/barlen*led_spacing
				dy=(nod2[1]-nod1[1])/barlen*led_spacing
				dz=(nod2[2]-nod1[2])/barlen*led_spacing
				pixel = nod1
				node_1_name=node_1_name.split('-')[0]
				node_2_name=node_2_name.split('-')[0]
				if forward_x:
					while pixel[0]<nod2[0]:
						pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
						pixel_counter+=1
						wrtr.writerow([pixel_counter,crossbar_modul,other_modul,node_1_name,node_2_name]+pixel)
				else:
					while pixel[0]>nod2[0]:
						pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
						pixel_counter+=1
						wrtr.writerow([pixel_counter,crossbar_modul,other_modul,node_1_name,node_2_name]+pixel)








	nodes_dict=collections.defaultdict()
	nodes_modules_dict = collections.defaultdict()
	for nod in node_module_xyz:
		xyz = node_module_xyz[nod]
		nod_xyz=xyz
		nodenam,modul=nod.split('-')
		subnods=[]
		subnod_xyzs=[]
		for subnod in node_module_xyz:
			if nodenam in subnod:
				subnods.append(subnod)
				subnod_xyzs.append(node_module_xyz[subnod])
				if node_module_xyz[subnod][2]>nod_xyz[2]:
					nod_xyz=node_module_xyz[subnod]
		nod_nods=[]
		nod_nods_w_modules=[]
		nod_bars=[]
		nod_bars_w_modules=[]
		for bar in bars:
			sbar = sorted(bar)
			if nodenam in sbar and "FEW" not in sbar:
				nod_bars.append(sbar[0]+"-"+sbar[1])
				for snod in sbar:
					if snod != nodenam and "FEW" not in snod:
						nod_nods.append(snod)
		for barwmn in bars_with_module_nums:
			if nodenam in barwmn:
				nod_bars_w_modules.append(barwmn)
				nod1,nod2,modul=barwmn.split('-')
				for nodd in [nod1,nod2]:
					if nodd!=nodenam and "FEW" not in nodd:
						nod_nods_w_modules.append(nodd+"-"+str(modul))
		for xbarwmn in crossbars_with_module_nums:
			if nodenam in xbarwmn:
				nod1,nod2,modul1,modul2=xbarwmn.split('-')
				nod_bars_w_modules.append(nod1+"-"+nod2+"-"+str(modul1))
				nodmod1=nod1+"-"+str(modul1)
				nodmod2=nod2+"-"+str(modul2)
				for nodd in [nod1,nod2]:
					if nodd!=nodenam and "FEW" not in nodd:
						if nodd==nod1:
							nod_nods_w_modules.append(nodmod1)
						else:
							nod_nods_w_modules.append(nodmod2)

		#otherwise counting these by columns is going to SUUUUUUCCCCKKK.
		subnods='_'.join(subnods)
		nod_nods='_'.join(nod_nods)
		nod_bars='_'.join(nod_bars)
		nod_nods_w_modules='_'.join(nod_nods_w_modules)
		nod_bars_w_modules='_'.join(nod_bars_w_modules)
		if nodenam in ground_nodes:
			ground="1"
		else:
			ground="0"

		nodes_dict[nodenam]=[nodenam]+nod_xyz+[subnods,nod_nods,nod_bars,nod_bars_w_modules,nod_nods_w_modules,ground]
		nodes_modules_dict[nod]=[nod,nodenam,modul]+xyz+[nod_nods,nod_bars,nod_bars_w_modules,nod_nods_w_modules,ground]




	for bar in bars:
		if 'FEW' not in bar:
			sbar = sorted(bar)
			barstr='-'.join(sbar)
			if sbar[0] in ground_nodes and sbar[1] in ground_nodes:
				ground=1
			else:
				ground=0
			nodenams = '_'.join(sbar)
			testnam = '-'.join(sbar)
			physbars=[]
			physnods=[]
			moduls=[]
			for mbar in bars_with_module_nums:
				if testnam in mbar:
					physbars.append(mbar)
					nodone,nodtoo,modnum=mbar.split('-')
					physnods.append(nodone+"-"+modnum)
					physnods.append(nodtoo+"-"+modnum)
					moduls.append(str(modnum))
			for mbar in crossbars_with_module_nums:
				if sbar[0] in mbar and sbar[1] in mbar:
					physbars.append('-'.join(mbar.split('-')[:3]))
					nodone,nodtoo,modulone,modultoo=mbar.split('-')
					physnods.append(nodone+"-"+modulone)
					physnods.append(nodtoo+"-"+modultoo)
					moduls.append(str(modulone))
			moduls='_'.join(moduls)
			min_x=10000
			min_y=10000
			min_z=10000
			max_x=-10000
			max_y=-10000
			max_z=-10000
			for physnod in physnods:
				xyz=node_module_xyz[physnod]
				if xyz[0]<min_x:
					min_x=xyz[0]
				if xyz[1]<min_y:
					min_y=xyz[1]
				if xyz[2]<min_z:
					min_z=xyz[2]
				if xyz[0]>max_x:
					max_x=xyz[0]
				if xyz[1]>max_y:
					max_y=xyz[1]
				if xyz[2]>max_z:
					max_z=xyz[2]
			physbars='_'.join(physbars)
			physnods='_'.join(physnods)
			adjacent_nods=[]
			adjacent_phys_nods=[]
			adjacent_bars=[]
			adjacent_phys_bars=[]
			for nod in sbar:
				too_much_data=nodes_dict[nod]
				nod_nods=too_much_data[5].split('_')		
				for nodnod in nod_nods:
					if nodnod not in nodenams and nodnod not in adjacent_nods and 'FEW' not in nodnod:
						adjacent_nods.append(nodnod)
				nod_pnods=too_much_data[8].split('_')		
				for pnodnod in nod_pnods:
					if pnodnod not in physnods and pnodnod not in adjacent_nods and 'FEW' not in pnodnod:
						adjacent_phys_nods.append(pnodnod)
				nod_bars=too_much_data[6].split('_')
				for nodbar in nod_bars:
					if nodbar!=barstr and nodbar not in adjacent_bars and 'FEW' not in nodbar:
						adjacent_bars.append(nodbar)
				nod_pbars=too_much_data[7].split('_')
				for pnodbar in nod_pbars:
					if pnodbar not in physbars and pnodbar not in adjacent_phys_bars and 'FEW' not in pnodbar:
						adjacent_phys_bars.append(pnodbar)
			bars_dict[barstr]=[barstr,moduls,min_x,min_y,min_z,max_x,max_y,max_z,nodenams,physbars,adjacent_nods,physnods,adjacent_phys_bars,adjacent_bars,adjacent_phys_nods,ground]


	modelnodeinfofilename = "Model_Node_Info%s.csv"%(filename_append)
	structuralnodeinfofilename = "Structural_Node_Info%s.csv"%(filename_append)
	modelbarinfofilename = "Model_Bar_Info%s.csv"%(filename_append)

	with open(modelnodeinfofilename,"wb") as f:
		wrtr=csv.writer(f)
		wrtr.writerow(["Node","X","Y","Z","Subnodes","Neighbor_Nodes","Bars","Physical_Bars","Physical_Nodes","Ground"])
		for nod in nodes_dict:
			wrtr.writerow(nodes_dict[nod])



	with open(structuralnodeinfofilename,"wb") as f:
		wrtr=csv.writer(f)
		wrtr.writerow(["Node_with_Module","Node","Module","X","Y","Z","Neighbor_Nodes","Bars","Physical_Bars","Physical_Nodes","Ground"])
		for nod in nodes_modules_dict:
			wrtr.writerow(nodes_modules_dict[nod])


	with open(modelbarinfofilename,"wb") as f:
		wrtr=csv.writer(f)
		wrtr.writerow(["Bar_name","Modules","Min_X","Min_Y","Min_Z","Max_X","Max_Y","Max_Z","Nodes","Physical_Bars","Physical_Nodes","Adjacent_Nodes","Adjacent_Physical_Bars","Adjacent_Bars","Adjacent_Physical_Nodes","Ground"])
		for bar in bars_dict:
			wrtr.writerow(bars_dict[bar])




	total_bars_length=0.0
	total_bars=0
	for bar in bar_lengths:
		total_bars+=1
		total_bars_length+=bar_lengths[bar]

	print "Total module bar distance with duplicates: ",int(total_distance_with_duplicates*0.0254),"m across",len(module_bars),"bars = ",int(total_distance_with_duplicates*0.0254*60),"LEDs"
	print "Total module bar distance sans duplicates: ",int(total_distance_sans_duplicates*0.0254),"m across",len(module_bars_sans_doubles),"bars = ",int(total_distance_sans_duplicates*0.0254*60),"LEDs"
	print "Total distance of bar doubles: ",int(double_bars_length*0.0254), " m across",len(double_bars),"bars = ",int(double_bars_length*0.0254*60),"LEDs"
	print "Total distance of cross-module bars: ",int(crossbars*0.0254)," m across",len(cross_module_bars),"bars = ",int(crossbars*0.0254*60),"LEDs"
	print "Total length of bars (with duplicates and cross bars): ", total_bars_length *0.0254,"m"
	print "Average bar length (with duplicates and cross bars): ",total_bars_length/total_bars*0.0254,"m"
	print "Total number of bars (with duplicates and cross bars): ",total_bars
	print "Also, node FEW seems to be missing from the new node coordinates (5 bars attached)"
