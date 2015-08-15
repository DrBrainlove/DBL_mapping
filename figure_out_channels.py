import os,csv, math, collections, random, time,datetime, traceback,pickle,json, copy, operator
import numpy as np



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


def get_bar_center_xyzs():
    bar_xyz=collections.defaultdict()
    with open("mapping_datasets/Full_Brain_DBL1/Model_Bar_Info.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for row in rdr:
            barname=row[0]
            if barname not in bar_xyz:
                min_x=float(row[2])
                min_y=float(row[3])
                min_z=float(row[4])
                max_x=float(row[5])
                max_y=float(row[6])
                max_z=float(row[7])
                bar_xyz[barname]=[(min_x+max_x)/2,(min_y+max_y)/2,(min_z+max_z)/2]
    return bar_xyz


def get_bar_min_xyzs():
    bar_xyz=collections.defaultdict()
    with open("mapping_datasets/Full_Brain_DBL1/Model_Bar_Info.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for row in rdr:
            barname=row[0]
            if barname not in bar_xyz:
                min_x=float(row[2])
                min_y=float(row[3])
                min_z=float(row[4])
                bar_xyz[barname]=[min_x,min_y,min_z]
    return bar_xyz




#take in barlist, strings
#return, sorted by minimum y value
def sort_bar_list_by_min_y(barlist):
    minxyzs=get_bar_min_xyzs()
    bardict=collections.defaultdict()
    for bar in barlist:
        barstr=bar_to_str(bar)
        bardict[barstr]=minxyzs[barstr][1]
    sorted_by_y = sorted(bardict.items(), key=operator.itemgetter(1))
    returnlist=[]
    for x in sorted_by_y:
        returnlist.append(x[0])
    return returnlist


def get_module_14_bars_and_nodes():
    subset_bars=[]
    subset_nodes=[]
    with open("mapping_datasets/Module_14/Model_Bar_Info.csv","rb") as f:
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



#gets the list of subset bars and nodes
#bars are a list of sets of strings: [set([ABC,DEF]),set([DEF,GHI])] etc
#nodes are a list of strings [ABC,DEF,ETC]
def get_subset_bars_and_nodes():
    subset_bars=[]
    subset_nodes=[]
    #with open("400m_subset_Model_Bar_Info.csv","rb") as f:
    with open("mapping_datasets/Eulerian_unfuck/Model_Bar_Info.csv","rb") as f:
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



def move_bar_between_modules(modules,bar,frommod,tomod):
    modules[frommod].remove(bar)
    modules[tomod].append(bar)
    return modules


def form_new_modules(bars):
    xyzs=get_bar_min_xyzs()
    #bisect top to bottom at ~3/4 of the pixels
    top_bars=[]
    bottom_bars=[]
    for bar in bars:
        barstr=bar_to_str(bar)
        if xyzs[barstr][2]>27:
            top_bars.append(bar)
        else:
            bottom_bars.append(bar)
    #bisect the bottom in half down the centerline
    bottom_left=[]
    bottom_right=[]
    for bar in bottom_bars:
        barstr=bar_to_str(bar)
        if xyzs[barstr][0]>0:
            bottom_right.append(bar)
        else:
            bottom_left.append(bar)

    bottom_left=sort_bar_list_by_min_y(bottom_left)
    bottom_right=sort_bar_list_by_min_y(bottom_right)
    top=sort_bar_list_by_min_y(top_bars)
    lenbl=len(bottom_left)
    lenbl13=lenbl/3
    lenbl23=lenbl*2/3
    lenbr=len(bottom_right)
    lenbr13=lenbr/3
    lenbr23=lenbr*2/3
    lentop=len(top)
    lentop12=lentop/2
    mod1=bottom_left[:lenbl13]
    mod2=bottom_left[lenbl13:lenbl23]
    mod3=bottom_left[lenbl23:]
    mod4=bottom_right[:lenbr13]
    mod5=bottom_right[lenbr13:lenbr23]
    mod6=bottom_right[lenbr23:]
    mod7=top[:lentop12]
    mod8=top[lentop12:]
    modules=[mod1,mod2,mod3,mod4,mod5,mod6,mod7,mod8]
    countsdict=collections.defaultdict()

    modules=move_bar_between_modules(modules,"CHI-KIT",0,1)
    modules=move_bar_between_modules(modules,"AGE-KIT",0,1)
    modules=move_bar_between_modules(modules,"ART-MAD",0,1)
    modules=move_bar_between_modules(modules,"ART-KIT",0,1)
    modules=move_bar_between_modules(modules,"COY-KIT",0,1)
    modules=move_bar_between_modules(modules,"ASH-HAM",6,1)
    modules=move_bar_between_modules(modules,"ASH-LAX",6,1)
    modules=move_bar_between_modules(modules,"HAM-LAX",7,1)
    modules=move_bar_between_modules(modules,"ACT-DUH",7,6)
    modules=move_bar_between_modules(modules,"DUH-TRY",7,6)
    modules=move_bar_between_modules(modules,"GIG-IRE",7,6)
    modules=move_bar_between_modules(modules,"EGG-PIG",3,6)
    modules=move_bar_between_modules(modules,"WAS-ZOO",3,6)
    modules=move_bar_between_modules(modules,"EGG-MOO",3,6)
    modules=move_bar_between_modules(modules,"DUI-GUN",5,4)
    modules=move_bar_between_modules(modules,"BRO-EON",4,7)
    modules=move_bar_between_modules(modules,"ACE-WET",4,7)
    modules=move_bar_between_modules(modules,"DIG-HIT",5,4)
    modules=move_bar_between_modules(modules,"ALL-PRO",6,0)
    modules=move_bar_between_modules(modules,"GOO-PRO",6,0)
    modules=move_bar_between_modules(modules,"IRE-MAC",7,6)
    modules=move_bar_between_modules(modules,"TAX-WIZ",2,1)
    modules=move_bar_between_modules(modules,"DRY-REF",7,2)
    modules=move_bar_between_modules(modules,"AGE-SIR",1,0)
    modules=move_bar_between_modules(modules,"BAR-SIR",1,0)
    modules=move_bar_between_modules(modules,"FLU-SIR",1,0)
    modules=move_bar_between_modules(modules,"AGE-KIT",1,0)
    modules=move_bar_between_modules(modules,"LUG-ODD",4,3)
    modules=move_bar_between_modules(modules,"BRO-WET",5,7)
    modules=move_bar_between_modules(modules,"BAR-FLU",1,0)
    modules=move_bar_between_modules(modules,"COW-WAS",3,6)
    modules=move_bar_between_modules(modules,"BOX-LID",1,2)
    modules=move_bar_between_modules(modules,"PIE-RUM",2,5)
    modules=move_bar_between_modules(modules,"HOW-RUM",2,5)

    modules=move_bar_between_modules(modules,"ETA-LUG",4,3)
    modules=move_bar_between_modules(modules,"ETA-PAY",4,3)
    modules=move_bar_between_modules(modules,"LUG-TUX",4,3)
    modules=move_bar_between_modules(modules,"PAY-TUX",4,3)
    modules=move_bar_between_modules(modules,"PAY-WIN",4,3)
    modules=move_bar_between_modules(modules,"BAH-WIN",4,3)
    modules=move_bar_between_modules(modules,"BAH-BAM",4,3)
    modules=move_bar_between_modules(modules,"GUN-OFF",5,4)

 #   modules=move_bar_between_modules(modules,"BOA-SHY",2,5)
 #   modules=move_bar_between_modules(modules,"BOA-HOW",2,5)
 #   modules=move_bar_between_modules(modules,"HOW-SHY",2,5)



    for bar in modules[3]:
        barset=bar_to_set(bar)
        for node in barset:
            for bar2 in modules[4]:
                if node in bar2:
                   # print node
                    if node in ground_nodes:
                        print node

  

    for m,module in enumerate(modules):
        modnum=m+1
        bars_in_mod=len(module)
        ledcount=0
        for bar in module:
            barstr=bar_to_set(bar)
            ledcount+=get_leds_per_bar(barstr)
        countsdict[modnum]=[bars_in_mod,ledcount]
        print modnum,bars_in_mod,ledcount


    for m,module in enumerate(modules):
        for bar in module:
            barset=bar_to_set(bar)
            for node in barset:
                node_connections=0
                for bar2 in module:
                    if node in bar2:
                        node_connections+=1
                if node_connections==1:
                  print m,node,bar

    with open("subset_modules_for_wiring.csv","wb") as f:
        wrtr=csv.writer(f)
        for m,module in enumerate(modules):
            modnum=m+1
            for bar in module:
                wrtr.writerow([bar,modnum])
    modules_out=collections.defaultdict()
    for m,module in enumerate(modules):
        modnum=m+1
        modulebars=[]
        modulenodes=[]
        for bar in module:
            barset=bar_to_set(bar)
            modulebars.append(barset)
            for node in barset:
                if node not in modulenodes:
                    modulenodes.append(node)
        modules_out[modnum]=(modulebars,modulenodes)
    return modules_out



#I'm storing the bars as a list of sets and sometimes it's useful to have it stored as the alphabetical string
def bar_to_str(bar):
    return '-'.join(sorted(list(bar)))

def bar_to_set(bar):
    return set(list(bar.split('-')))

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


def get_adjacent_nodes(node,bars):
    result=[]
    for bar in bars_remaining:
        if node in bar:
            othernode=get_other_node(bar,node)
            result.append(othernode)
    return result


RECEIVERS_PER_BASE_NODE=2
RECEIVERS_PER_TOP_NODE=3

all_possible_mappings=collections.defaultdict()
leftover_bars=collections.defaultdict()

#bars,nodes=get_module_14_bars_and_nodes()

bars,nodes=get_subset_bars_and_nodes()
modulelists=form_new_modules(bars)

for module in range(1,9):
    (bars,nodes)=modulelists[module]



    for x in range(0,500000):
        if x % 1000==0:
            print x,datetime.datetime.now()

        num_alternative_startnodes=0
        strip_leds=[]
        mapping_name="mapping_"+str(x)
        this_mapping=[]
        bars_remaining=copy.deepcopy(bars)
        jumps=0
        receiver_nodes=set()
        startnode=random.sample(set(nodes),1)[0]
        module_origin_startnode=startnode
        alternative_startnodes=[]
        for receiver in range(0,3):

            receiver_nodes.add(startnode)
            alternative_startnodes=get_adjacent_nodes(module_origin_startnode,bars_remaining)
            for node_channel in range(0,2):#range(0,RECEIVERS_PER_BASE_NODE*CHANNELS_PER_RECEIVER):
                use_alternative_node=random.randint(0,1)
                if use_alternative_node:
                    try:
                        startnode=random.choice(alternative_startnodes)
                        num_alternative_startnodes+=1
                        alternative_startnodes.append(startnode)
                    except:
                        pass
                node_channel_name=startnode+"_"+str(receiver)+"_"+str(node_channel)
                attempts=0
                too_short=True
                current_node=startnode
                prevnode="N/A"
                leds_used=0
                end_of_strip=False
                while not end_of_strip:
                    next_bar_options=get_next_bar_options(current_node,prevnode,bars_remaining)
                  #  if leds_used > 300:
                  #      randomly_stop=random.randint(0,2)
                  #      if randomly_stop==2:
                  #          end_of_strip=True
                  #          next_bar_options=[]
                    if next_bar_options:
                        next_bar=random.choice(next_bar_options)
                        attempts_nodes=0
                        nextbarstr=bar_to_str(next_bar)
                        prevnode=current_node
                        current_node=get_other_node(next_bar,current_node)
                        leds_used+=leds_per_bar_dict[nextbarstr]
                        if leds_used>MAX_LEDS_PER_CHANNEL:
                            leds_used-=leds_per_bar_dict[nextbarstr]
                            end_of_strip=True
                            strip_leds.append(leds_used)
                            too_short=False
                        else:
                            this_mapping.append([node_channel_name,startnode,nextbarstr])
                            bars_remaining.remove(next_bar)
                    else:
                        if receiver==2:
                            for adjnode in get_adjacent_nodes(current_node,bars_remaining):
                                next_bar_options=get_next_bar_options(adjnode,current_node,bars_remaining)
                                if next_bar_options:
                                    jumpstr="JUMP_"+current_node+"_"+adjnode
                                    current_node=adjnode
                                    prevnode=current_node
                                    break
                        if next_bar_options:
                            next_bar=random.choice(next_bar_options)
                            nextbarstr=bar_to_str(next_bar)
                            prevnode=current_node
                            current_node=get_other_node(next_bar,current_node)
                            leds_used+=leds_per_bar_dict[nextbarstr]
                            if leds_used>MAX_LEDS_PER_CHANNEL:
                                leds_used-=leds_per_bar_dict[nextbarstr]
                                end_of_strip=True
                                strip_leds.append(leds_used)
                                too_short=False
                            else:
                                this_mapping.append([node_channel_name,module_origin_startnode,startnode,jumpstr])
                                jumps+=1
                                this_mapping.append([node_channel_name,module_origin_startnode,startnode,nextbarstr])
                                bars_remaining.remove(next_bar)
                        else:
                            end_of_strip=True
                            strip_leds.append(leds_used)
                            if leds_used<250:
                                too_short=True
                            else:
                                too_short=False


        #run is over. how'd it do? if the run was even remotely successsful, dump it to a file
        if len(bars_remaining)<1 and jumps<3:
            all_possible_mappings[mapping_name]=this_mapping
            leftover_bars[mapping_name]=bars_remaining
            bars_remaining_serializable=[]
            leds_min=min(strip_leds)
            leds_max=max(strip_leds)
            leds_avg=np.mean(strip_leds)
            leds_variance=np.var(strip_leds)
            distinct_receivernodes=len(receiver_nodes)
            groundnode_utilization=0
            for node in receiver_nodes:
                if node in ground_nodes:
                    groundnode_utilization+=1
            #json and sets don't like each other
            for bar in bars_remaining:
                bars_remaining_serializable.append(list(bar))

            dumptojson=[module,len(bars_remaining_serializable),jumps,groundnode_utilization,distinct_receivernodes,num_alternative_startnodes,module_origin_startnode,alternative_startnodes,leds_min,leds_max,leds_avg,leds_variance,bars_remaining_serializable,this_mapping]
            nowstamp=datetime.datetime.now().strftime("%H%M%S")
            json.dump(dumptojson,open("possible_mappings/r4_"+nowstamp+"_M"+str(module)+"_G"+str(groundnode_utilization)+"_R"+str(distinct_receivernodes)+"_A"+str(num_alternative_startnodes)+"_"+mapping_name+".json","w"))


