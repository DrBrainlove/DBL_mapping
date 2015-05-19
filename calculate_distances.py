import os,csv, math, collections


bars=[]
with open("node_info_old.csv","rb") as f: #old coordinates but still has right bar mapping
   rdr=csv.reader(f)
   rdr.next()
   for line in rdr:
      startnod=line[0]
      for x in [4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34]:
         if len(line)>=x+1:
            endnod=line[x]
            nodes_set=set([startnod,endnod])
            if nodes_set not in bars: #avoid duplicates
	            bars.append(nodes_set)

node_xyz=collections.defaultdict()
node_module_xyz=collections.defaultdict()
module_dict=collections.defaultdict()

def xyz_dist(point1,point2):
	return math.sqrt(math.pow((point2[0]-point1[0]),2) +  math.pow((point2[1]-point1[1]),2) + math.pow((point2[2]-point1[2]),2))

with open("node_locations_150501.csv","rU") as f:
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

for bar in cross_module_bars:
	barnods=list(bar)
	try:
		barlength=xyz_dist(node_xyz[barnods[0]],node_xyz[barnods[1]])
		bar_lengths[str(barnods[0])+"-"+str(barnods[1])]=barlength
		crossbars+=barlength
	except:
		print "eh",bar


#Write out the pixel mappings to read into the model
with open("pixel_mapping.csv","wb") as f:
	wrtr=csv.writer(f)
	pixel_counter=0
	led_spacing=0.656168 #inches. the model is in inches. TODO: Use millimeters. One day we will be free from tyanny. And inches.
	wrtr.writerow(["Pixel_i","Module","Node1","Node2","X","Y","Z"])
	for modul in module_dict:
		module_distances[modul]=0.0
		nods=module_dict[modul]
		for bar in bars:
			in_module=True
			for barnode in bar:
				if barnode not in nods:
					in_module=False
			if in_module:
				barnods=list(bar)
				#for consistency start from the lowest x-coordinate and set all the bars that way.
				#also helps keep track of when the strip hits the end of the bar
				if node_module_xyz[barnods[0]+"-"+str(modul)][0]<node_module_xyz[barnods[1]+"-"+str(modul)][0]:
					nod1=node_module_xyz[barnods[0]+"-"+str(modul)]
					nod2=node_module_xyz[barnods[1]+"-"+str(modul)]
					node_1_name=barnods[0]
					node_2_name=barnods[1]
				else:
					nod1=node_module_xyz[barnods[1]+"-"+str(modul)]
					nod2=node_module_xyz[barnods[0]+"-"+str(modul)]
					node_1_name=barnods[1] 
					node_2_name=barnods[0]

				barlen=xyz_dist(node_module_xyz[barnods[0]+"-"+str(modul)],node_module_xyz[barnods[1]+"-"+str(modul)])
				dx=(nod2[0]-nod1[0])/barlen*led_spacing
				dy=(nod2[1]-nod1[1])/barlen*led_spacing
				dz=(nod2[2]-nod1[2])/barlen*led_spacing
				pixel=nod1		
				while pixel[0]<nod2[0]:
					pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
					pixel_counter+=1
					wrtr.writerow([pixel_counter,modul,node_1_name,node_2_name]+pixel)


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
