import csv,json,collections

#I'm storing the bars as a list of sets and sometimes it's useful to have it stored as the alphabetical string
def bar_to_str(bar):
    return '-'.join(sorted(list(bar)))

def bar_to_set(bar):
    return set(list(bar.split('-')))

def get_bar_len_led_info(bar):
    barinfo=collections.defaultdict()
    with open("DBL2_edgelengths_with_led_counts.csv","rb") as f:
        rdr=csv.reader(f)
        for row in rdr:
            barnamset=set(row[0].split('-'))
            barnamstr='-'.join(sorted(list(barnamset)))
            if barnamset==bar:
                bar_len=float(row[1])
                num_leds=int(row[3])
                return bar_len,num_leds
    return False

def get_startnode(bar,prev_startnode):
	barset=bar_to_set(bar)
	for node in barset:
		if node != prev_startnode:
			return node


def get_firstnode(firstbar,secondbar):
	barset1=bar_to_set(firstbar)
	barset2=bar_to_set(secondbar)
	for node in barset1:
		if node not in barset2:
			return node

def make_nodes_in_order(firstnode,bar):
	nodes_in_bar=bar_to_set(bar)
	node1=firstnode
	for node in nodes_in_bar:
		if node!=node1:
			node2=node
	return (node1,node2)


module_jsons=	["233504_M1_G2_R3_A2_mapping_78730.json",
				"233632_M2_G1_R3_A1_mapping_58403.json",
				"223751_M3_G1_R3_A2_mapping_22996.json",
				"233917_M4_G2_R3_A1_mapping_12429.json",
				"224141_M5_G2_R3_A2_mapping_40081.json",
				"234233_M6_G2_R3_A3_mapping_8993.json",
				"234451_M7_G0_R2_A2_mapping_36612.json",
				"234708_M8_G0_R3_A2_mapping_52382.json"]



strip=-1
brain_bar_lists=[]
leds_in_strip=0
outputnodes=[]
for modu,mj in enumerate(module_jsons):
	modnumber=modu+1
	modulething=json.load(open("possible_mappings/"+mj,"r"))
	actuallist=modulething[11]
	prevchannel=2
	startnode,receiver,channel=actuallist[0][0].split('_')
	firstnode=startnode
	for rnum,row in enumerate(actuallist):
		startnode,receiver,channel=row[0].split('_')
		receiver=int(receiver)
		channel=int(channel)
		barname=row[1]
		barnameset=bar_to_set(barname)
		if channel!=prevchannel:
			strip+=1
			first_node_in_strip=get_firstnode(barname,actuallist[rnum+1][1])
			firstnode=first_node_in_strip
			outputnodes.append([first_node_in_strip,strip,barname,make_nodes_in_order(first_node_in_strip,barname)])
			print strip,receiver,prevchannel,leds_in_strip
			leds_in_strip=0
		else:
			outputnodes.append([firstnode,strip,barname,make_nodes_in_order(firstnode,barname)])
		firstnode=get_startnode(barname,firstnode)
		leds_in_strip+=get_bar_len_led_info(bar_to_set(barname))[1]
		prevchannel=channel
		actualreceiver=modu*3+int(receiver)
		brain_bar_lists.append([modnumber,barname,strip,actualreceiver,channel,startnode])
print strip,receiver,prevchannel,leds_in_strip

for x in outputnodes: print x

with open("Node_to_node_in_strip_pixel_order.csv","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Strip","Node1","Node2"])	
	for x in outputnodes:
		wrtr.writerow([x[1],x[3][0],x[3][1]])

with open("Strip_Channel_Mapping.csv","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Module","Bar","Strip","Receiver","Channel","Strip start node"])
	for row in brain_bar_lists:
		wrtr.writerow(row)

