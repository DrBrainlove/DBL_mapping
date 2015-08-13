import os,csv, math, collections, random, time,datetime, traceback,pickle,json, copy



MAX_CHANNELS_TOTAL=48
MAX_LEDS_PER_CHANNEL=512
NUM_CONTROLLERS_TOTAL=24 #28 but trying to get away with having four spare
CHANNELS_PER_RECEIVER=2


ground_nodes = ["WAX","AIM","LID","BOX","HUG","FLU","SIR","ONO","TAT","COP","NEW","GET","OAK","CAB","AMP","YAY","HAY","BAM","CIS","OFF","WHO","NIX","PIE","RUM","SIP"]

#nodes near the top of the brain with 6 led paths coming out of them
highly_connected_nodes_near_top=["OLD", "IRE", "JUG", "DUH", "LAB", "TOY", "ASH", "PRO", "EON", "POP", "FIG", "DRY", "WIZ"]


leds_per_bar_dict=collections.defaultdict()
with open("DBL2_edgelengths_with_led_counts.csv","rb") as f:
    rdr=csv.reader(f)
    rdr.next()
    for row in rdr:
        barnamset=set(row[0].split('-'))
        barnamstr='-'.join(sorted(list(barnamset)))
        num_leds=int(row[3])
        leds_per_bar_dict[barnamstr]=num_leds




#gets the list of subset bars and nodes
#bars are a list of sets of strings: [set([ABC,DEF]),set([DEF,GHI])] etc
#nodes are a list of strings [ABC,DEF,ETC]
def get_subset_bars_and_nodes():
    subset_bars=[]
    subset_nodes=[]
    with open("400m_subset_Model_Bar_Info.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for row in rdr:
            barname=row[0]
            barset=set(barname.split('-'))
            if barset not in subset_bars:
                subset_bars.append(barset)
            for node in barset:
                if node not in subset_nodes:
                    subset_nodes.append(node)
    return subset_bars, subset_nodes

#I'm storing the bars as a list of sets and sometimes it's useful to have it stored as the alphabetical string
def bar_to_str(bar):
    return '-'.join(sorted(list(bar)))




#Given a list of bars, get a list of nodes in those bars
def nodes_from_bars(barlist):
    nodes=[]
    for bar in barlist:
        for node_in_bar in bar:
            if not node_in_bar in nodes:
                nodes.append(node_in_bar)
    return nodes


#Given a current position node and a set of bars that haven't been used yet, return a list of possible next steps that don't double back
def get_next_bar_options(node,prevnode,bars_remaining):
    result=[]
    current_node=node
    for bar in bars_remaining:
        if node in bar and prevnode not in bar:
            result.append(bar)
    return result

def is_dead_end(node):
    result=[]
    for bar in bars_remaining:
        if node in bar:
            result.append(bar)
    return result>=2

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

#number of leds in a bar
def get_leds_per_bar(bar):
    barstr=bar_to_str(bar)
    return leds_per_bar_dict[barstr]




RECEIVERS_PER_BASE_NODE=2
RECEIVERS_PER_TOP_NODE=3

all_possible_mappings=collections.defaultdict()
leftover_bars=collections.defaultdict()

bars,nodes=get_subset_bars_and_nodes()

#try 10000 different combinations
for x in range(0,100000000):
    if x % 1000==0:
        print x,datetime.datetime.now()
    mapping_name="mapping_"+str(x)
    this_mapping=[]
    num_top_nodes=random.randint(2,6)
    num_base_nodes=(24-num_top_nodes*RECEIVERS_PER_TOP_NODE)/RECEIVERS_PER_BASE_NODE
    base_nodes = random.sample(set(ground_nodes),num_base_nodes)
    top_nodes = random.sample(set(highly_connected_top_nodes),num_top_nodes)
    bars_remaining=copy.deepcopy(bars)
    nodes_remaining=copy.deepcopy(nodes)
    for startnode in base_nodes:
        for node_channel in range(0,RECEIVERS_PER_BASE_NODE*CHANNELS_PER_RECEIVER):
            node_channel_name=startnode+"_"+str(node_channel)
            attempts=0
            too_short=True
            while too_short==True and attempts<20:
                attempts+=1
                current_node=startnode
                prevnode="N/A"
                leds_used=0
                end_of_strip=False
                while not end_of_strip:
                    next_bar_options=get_next_bar_options(current_node,prevnode,bars_remaining)
                    if next_bar_options:
                        next_bar=random.choice(next_bar_options)
                        attempts_nodes=0
                        if leds_used<250:
                            next_node=get_other_node(next_bar,current_node)
                            while is_dead_end(next_node) and attempts_nodes<10:
                                attempts_nodes+=1
                                next_node=get_other_node(next_bar,current_node)
                                next_bar=random.choice(next_bar_options)
                        nextbarstr=bar_to_str(next_bar)
                        prevnode=current_node
                        current_node=get_other_node(next_bar,current_node)
                        leds_used+=leds_per_bar_dict[nextbarstr]
                        if leds_used>MAX_LEDS_PER_CHANNEL:
                            end_of_strip=True
                            too_short=False
                        else:
                            this_mapping.append([node_channel_name,nextbarstr])
                            bars_remaining.remove(next_bar)
                    else:
                        end_of_strip=True
                        if leds_used<250:
                            too_short=True
                        else:
                            too_short=False

    for startnode in top_nodes:
        for node_channel in range(0,RECEIVERS_PER_TOP_NODE*CHANNELS_PER_RECEIVER):
            node_channel_name=startnode+"_"+str(node_channel)
            attempts=0
            too_short=True
            while too_short==True and attempts<20:
                attempts+=1
                current_node=startnode
                prevnode="N/A"
                leds_used=0
                end_of_strip=False
                while not end_of_strip:
                    next_bar_options=get_next_bar_options(current_node,prevnode,bars_remaining)
                    if next_bar_options:
                        next_bar=random.choice(next_bar_options)
                        attempts_nodes=0
                        if leds_used<250:
                            next_node=get_other_node(next_bar,current_node)
                            while is_dead_end(next_node) and attempts_nodes<10:
                                attempts_nodes+=1
                                next_node=get_other_node(next_bar,current_node)
                                next_bar=random.choice(next_bar_options)
                        nextbarstr=bar_to_str(next_bar)
                        prevnode=current_node
                        current_node=get_other_node(next_bar,current_node)
                        leds_used+=leds_per_bar_dict[nextbarstr]
                        if leds_used>MAX_LEDS_PER_CHANNEL:
                            end_of_strip=True
                            too_short=False
                        else:
                            this_mapping.append([node_channel_name,nextbarstr])
                            bars_remaining.remove(next_bar)
                    else:
                        end_of_strip=True
                        if leds_used<250:
                            too_short=True
                        else:
                            too_short=False

    #run is over. how'd it do? if the run was even remotely successsful, dump it to a file
    if len(bars_remaining)<150:
        all_possible_mappings[mapping_name]=this_mapping
        leftover_bars[mapping_name]=bars_remaining
        bars_remaining_serializable=[]

        #json and sets don't like each other
        for bar in bars_remaining:
            bars_remaining_serializable.append(list(bar))

        dumptojson=[len(bars_remaining_serializable),num_top_nodes,num_base_nodes,bars_remaining_serializable,this_mapping]
        nowstamp=datetime.datetime.now().strftime("%H%M%S")
        json.dump(dumptojson,open("possible_mappings/"+nowstamp+"_"+mapping_name+".json","w"))


