import os,csv, math, collections


ground_nodes = ["WAX","AIM","LID","BOX","HUG","FLU","SIR","ONO","TAT","COP","NEW","GET","OAK","CAB","AMP","YAY","HAY","BAM","CIS","OFF","WHO","NIX","PIE","RUM","SIP"]

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

def xyz_dist(point1,point2):
	return math.sqrt(math.pow((point2[0]-point1[0]),2) +  math.pow((point2[1]-point1[1]),2) + math.pow((point2[2]-point1[2]),2))

with open("node_locations_150501_zeroed.csv","rU") as f:
	rdr=csv.reader(f)
	rdr.next()
	for line in rdr:
		modul=line[0]
		node=line[1]
		x=float(line[2])
		y=float(line[3])
		z=float(line[4])
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
		print "eh",bar
		to_bar_or_not_to_bar.append(bar)

for bar in to_bar_or_not_to_bar:
	cross_module_bars.remove(bar)

bars_with_module_nums=[]
crossbars_with_module_nums=[]

#Write out the pixel mappings to read into the model
#TODO figure out a heuristic for which modules the cross bars attach to and add them into the model. They're currently absent.
with open("pixel_mapping.csv","wb") as f:
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
		if nodenam in sbar:
			nod_bars.append(sbar[0]+"-"+sbar[1])
			for snod in sbar:
				if snod != nodenam:
					nod_nods.append(snod)
	for barwmn in bars_with_module_nums:
		if nodenam in barwmn:
			nod_bars_w_modules.append(barwmn)
			nod1,nod2,modul=barwmn.split('-')
			for nodd in [nod1,nod2]:
				if nodd!=nodenam:
					nod_nods_w_modules.append(nodd+"-"+str(modul))
	for xbarwmn in crossbars_with_module_nums:
		if nodenam in xbarwmn:
			nod1,nod2,modul1,modul2=xbarwmn.split('-')
			nod_bars_w_modules.append(nod1+"-"+nod2+"-"+str(modul1))
			nodmod1=nod1+"-"+str(modul1)
			nodmod2=nod2+"-"+str(modul2)
			for nodd in [nod1,nod2]:
				if nodd!=nodenam:
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

with open("Model_Node_Info.csv","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Node","X","Y","Z","Subnodes","Neighbor_Nodes","Bars","Physical_Bars","Physical_Nodes","Ground"])
	for nod in nodes_dict:
		wrtr.writerow(nodes_dict[nod])



with open("Structural_Node_Info.csv","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Node_with_Module","Node","Module","X","Y","Z","Neighbor_Nodes","Bars","Physical_Bars","Physical_Nodes","Ground"])
	for nod in nodes_modules_dict:
		wrtr.writerow(nodes_modules_dict[nod])




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
