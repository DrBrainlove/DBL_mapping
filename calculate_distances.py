import os,csv, math, collections, random, time,datetime, traceback
import pickle




#TODO: This code works but it needs organization and cleanup.


ground_nodes = ["WAX","AIM","LID","BOX","HUG","FLU","SIR","ONO","TAT","COP","NEW","GET","OAK","CAB","AMP","YAY","HAY","BAM","CIS","OFF","WHO","NIX","PIE","RUM","SIP"]

modelinfo_output_directory="mapping_datasets"

def get_bars():
    bars=[]
    node_connections = collections.defaultdict()
    with open("DBL2_node_info.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for line in rdr:
          startnod=line[1]
          for x in [5,7,9,11,13,15,17,20,21,23,25,27,29,31,33,35]:
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
    with open("DBL2_crossbars.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for line in rdr:
            startnod=line[0]
            endnod=line[1]
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
    return bars
    



def get_ground_bars():
    outer_nodes=get_outer_nodes()
    #copied and pasted from below. not optimized at all and not worth trimming. this is just to load the whole bar map to whittle down from
    bars=get_bars()
    ground_bars=[]
    ground_bars_plus=[]
    nodes_counts=collections.defaultdict()
    for bar in bars:
        both_ground_nodes=True
        one_ground_node=False
        for node in bar:
            if node not in ground_nodes:
                both_ground_nodes=False
            else:
                one_ground_node=True
                groundnod=node
                if groundnod not in nodes_counts:
                    nodes_counts[groundnod]=0
        barinformat='-'.join(sorted(list(bar)))
        if both_ground_nodes:
            ground_bars.append(barinformat)
            ground_bars_plus.append(barinformat)
        if one_ground_node and not both_ground_nodes: 
            if nodes_counts[groundnod]<4 and groundnod not in outer_nodes:
                nodes_counts[groundnod]+=1
                ground_bars_plus.append(barinformat)
    return ground_bars, ground_bars_plus






def make_bars_subset(bars_target=400):

    #copied and pasted from below. not optimized at all and not worth trimming. this is just to load the whole bar map to whittle down from
    bars=get_bars()


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





def get_bar_len_led_info(bar):
    barinfo=collections.defaultdict()
    with open("DBL2_edgelengths_with_led_counts.csv","rb") as f:
        rdr=csv.reader(f)
        for row in rdr:
            barnamset=set(row[0].split('-'))
            if barnamset==bar:
                bar_len=float(row[1])
                num_leds=int(row[3])
                return bar_len,num_leds
    return False


def xyz_dist(point1,point2):
    return math.sqrt(math.pow((point2[0]-point1[0]),2) +  math.pow((point2[1]-point1[1]),2) + math.pow((point2[2]-point1[2]),2))


class BarSubset(object):
    def __init__(self,active_bars=None,filename_append=None,active_modules=None):
        use_these = []
        for active_bar in active_bars:
            sortedbar = '-'.join(sorted(list(active_bar.split('-'))))
            use_these.append(sortedbar)
        self.active_bars = use_these
        self.filename_append=filename_append
        self.active_nodes = []
        if active_modules:
            self.active_modules=active_modules
        else:
            self.active_modules=range(1,15) #this goes 1-14
        #automatically infers active nodes from active bars
        for bar in self.active_bars:
            nodes_in_bar = bar.split('-')
            for node in nodes_in_bar:
                if node not in self.active_nodes:
                    self.active_nodes.append(node)

def get_outer_nodes():
    outer_bars=subset_shells("outer_bars.csv")
    outer_bars_sets=[]
    outer_nodes=[]
    for bar in outer_bars:
         outer_bars_sets.append(set(bar.split('-')))
    for bar in outer_bars_sets:
        for node in bar:
            if node not in outer_nodes:
                outer_nodes.append(node)
    return outer_nodes


def subset_shells(file_to_load):
    """ parameter target is not used, vestigial? """
    all_bars = []
    with open(file_to_load,'r') as f:
        rdr = csv.reader(f)
        for line in rdr:
            all_bars.append(line[0])
    return all_bars
    
def get_other_node(barset,node):
    if node in barset:
        for node_i in barset:
            if node_i != node:
                return node_i
    return False

#returns the polygon if true, false if not
def check_polygon(outer_bars,*barsets):
    yooniun=set()
    for potential_duplicate in barsets:
        collisions=0
        for other_potential_duplicate in barsets:
            if potential_duplicate==other_potential_duplicate:
                collisions+=1
        if collisions>1:
            return False
    nodconts=collections.defaultdict()
    for barset in barsets:
        yooniun=yooniun.union(barset)
        for nod in barset:
            if nod not in nodconts:
                nodconts[nod]=0
            nodconts[nod]+=1
            if nodconts[nod]>2:
                return False

    for bar in outer_bars:
        if bar not in barsets:
            nodes_in_poly=0
            for node in bar:
                if node in yooniun:
                    nodes_in_poly+=1
            if nodes_in_poly>1:
                return False
    if len(yooniun)==len(barsets):
        #print len(yooniun),barsets
        return yooniun
    else:
        return False

def find_polygons_in_outer_shell():
    outer_bars=subset_shells("outer_bars.csv")
    outer_bars_sets=[]
    polygons=[]
    for bar in outer_bars:
         outer_bars_sets.append(set(bar.split('-')))

    #note: in retrospect, there was probably a collapsed way to do this. 
    #whoops.     
    for cnt,bar_i in enumerate(outer_bars_sets):
        if cnt%10==0:
            print bar_i,datetime.datetime.now()
        for bar_j in outer_bars_sets:
            if bar_i.intersection(bar_j):
                for bar_k in outer_bars_sets:
                    if bar_j.intersection(bar_k):
                        triangle_up_in_dis_mofo=check_polygon(outer_bars_sets,bar_i,bar_j,bar_k)
                        if triangle_up_in_dis_mofo:
                            polygons.append(triangle_up_in_dis_mofo)
                        for bar_l in outer_bars_sets:
                            if bar_k.intersection(bar_l):
                                squrr_up_in_dis_mofo=check_polygon(outer_bars_sets,bar_i,bar_j,bar_k,bar_l)
                                if squrr_up_in_dis_mofo:
                                    polygons.append(squrr_up_in_dis_mofo)
                                for bar_m in outer_bars_sets:
                                    if bar_l.intersection(bar_m):
                                        pent_up_in_dis_mofo=check_polygon(outer_bars_sets,bar_i,bar_j,bar_k,bar_l, bar_m)
                                        if pent_up_in_dis_mofo:
                                            polygons.append(pent_up_in_dis_mofo)
                                        for bar_n in outer_bars_sets:
                                            if bar_m.intersection(bar_n):
                                                hex_up_in_dis_mofo=check_polygon(outer_bars_sets,bar_i,bar_j,bar_k,bar_l, bar_m,bar_n)
                                                if hex_up_in_dis_mofo:
                                                    polygons.append(hex_up_in_dis_mofo)
                                                for bar_o in outer_bars_sets:
                                                    if bar_n.intersection(bar_o):
                                                        no_heptagons_right=check_polygon(outer_bars_sets,bar_i,bar_j,bar_k,bar_l, bar_m,bar_n,bar_o)
                                                        if no_heptagons_right:
                                                            polygons.append(no_heptagons_right)
    polygons2=[]
    for polygon in polygons:
        if polygon and polygon not in polygons2:
            polygons2.append(polygon)
    polygons=polygons2
    print polygons
    pickle.dump(polygons,open("polygons.p","wb"))
    return polygons

def load_polygons():
    return pickle.load(open("polygons.p","rb"))


def make_polygonal_subset(polygons):
    inner_outer_bars=subset_shells("in_to_out_bars.csv")
    outer_bars=subset_shells("outer_bars.csv")
    inner_outer_bars_sets=[]
    outer_bars_sets=[]
    for bar in inner_outer_bars:
         inner_outer_bars_sets.append(set(bar.split('-')))
    for bar in outer_bars:
         outer_bars_sets.append(set(bar.split('-')))
    inner_outer_bars=inner_outer_bars_sets
    outer_bars=outer_bars_sets
    add_bars=[]
    for polygon in polygons:
        bars_in_polygon=[]
        for bar in outer_bars:
            nodes_in_poly=0
            for node in bar:
                if node in polygon:
                    nodes_in_poly+=1
            #print nodes_in_poly,bar
            if nodes_in_poly==2:
                bars_in_polygon.append(bar)
        polygon_as_ordered_list=[]
        pnode=random.sample(polygon,1)[0]
        polygon_as_ordered_list.append(pnode)
        while len(polygon_as_ordered_list)<len(polygon):
            for bar in bars_in_polygon:
                if pnode in bar:
                    nextpnode=get_other_node(bar,pnode)
                    if nextpnode not in polygon_as_ordered_list:
                        pnode=nextpnode
                        polygon_as_ordered_list.append(pnode)
        #print polygon_as_ordered_list
        gonalness=len(polygon)
        p_inner_nodes=collections.defaultdict()
        for bar in inner_outer_bars:
            for node in bar:
                if node in polygon:
                    othernode=get_other_node(bar,node)
                    if othernode not in p_inner_nodes:
                        p_inner_nodes[othernode]=0
                    p_inner_nodes[othernode]+=1
        maxedoutnodes=[]
        maxnodevalue=max(p_inner_nodes.values())
        for node in p_inner_nodes:
            if p_inner_nodes[node]==maxnodevalue:
                maxedoutnodes.append(node)
      #  print p_inner_nodes,maxnodevalue,maxedoutnodes
        new_bars_added=0
        new_potential_bars=[]
        for bar in inner_outer_bars:
            if maxedoutnodes[0] in bar:
                new_potential_bars.append(bar)
#        print "P",polygon
#        print new_potential_bars
        position_in_polygon=0
        trybar=set([maxedoutnodes[0], polygon_as_ordered_list[position_in_polygon]])
        if trybar in new_potential_bars:
            add_bars.append(trybar)
            new_bars_added+=1
        iterations=0
        while new_bars_added < (gonalness+1)/2:
            iterations+=1
            position_in_polygon+=2
            position_in_polygon=position_in_polygon % len(polygon_as_ordered_list)
            trybar=set([maxedoutnodes[0], polygon_as_ordered_list[position_in_polygon]])
            if trybar in new_potential_bars:
                add_bars.append(trybar)
                new_bars_added+=1
            if iterations%10==0: #if shit is looping endlessly over a thing with even nodes, try the odd nodes
                position_in_polygon+=1
    add_bars_formatted=[]
    for bar in add_bars:
        add_bars_formatted.append('-'.join(sorted(list(bar))))
   # print add_bars_formatted
    return add_bars_formatted


def get_module_bar_strip_numbers():
    bar_module_strip_dict=collections.defaultdict()
    with open("Module_Bar_Orders.csv","rb") as f2:
        rdr=csv.reader(f2)
        rdr.next()
        for row in rdr:
            modul=row[0]
            bar_module_desig='-'.join(sorted(row[1].split('-')))+"-"+str(modul)
            strip=row[2]
            bar_module_strip_dict[bar_module_desig]=strip
    return bar_module_strip_dict 



#make_polygonal_subset(polys)





if __name__=="__main__":
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
    filename_append = "Module_14"
    active_bars = ["LIE-OLD", "LIE-TAU", "OLD-TAU", "GIG-LIE", "ERA-IRE", "ERA-RIB", "FOG-RIB", "FOG-TAU", "GIG-IRE", "ERA-GIG", "ERA-LAW", "EVE-FOG", "EVE-GIG", "EVE-IRE", "EVE-LAW", "EVE-LIE", "EVE-OLD", "FOG-OLD", "GIG-LAW", "IRE-LAW", "IRE-RIB", "LAW-LIE", "LAW-OLD", "LAW-RIB", "LAW-TAU","FOG-LAW"]
    print len(active_bars)
    partialBrainSubset = BarSubset(active_bars,filename_append,[14])
    bar_subsets.append(partialBrainSubset)



    """
    #PUT THE EXPERIMENTAL BAR SUBSET HERE
    filename_append = "Shitty_Pixelpusher_Test"
    active_bars = ["ERA-GIG","EVE-LAW","GIG-IRE"]
    print len(active_bars)
    partialBrainSubset = BarSubset(active_bars,filename_append,[14])
    bar_subsets.append(partialBrainSubset)
    """




    #PUT THE EXPERIMENTAL BAR SUBSET HERE
    filename_append = "Algorithmic_Brain"
    active_bars = make_bars_subset(400)
    algorithmicBrainSubset = BarSubset(active_bars,filename_append)
    bar_subsets.append(algorithmicBrainSubset)




    filename_append = "Outer_Plus_algorithmic_inner"
    polygons=load_polygons() #or to make from scratch, find_polygons_in_outer_shell(). Takes a little while though.
    selected_mid_bars=make_polygonal_subset(polygons)
    ground_bars,ground_bars_plus=get_ground_bars()
    active_bars=subset_shells("outer_bars.csv")+selected_mid_bars
    #don't want to add bars that are already there
    for bar in ground_bars_plus:
        if bar not in active_bars:
            active_bars.append(bar)
    outer_brain_subset=BarSubset(active_bars,filename_append)
    bar_subsets.append(outer_brain_subset)





    for bar_subset in bar_subsets:
        #load things from the object
        active_nodes = bar_subset.active_nodes
        active_bars = bar_subset.active_bars
        active_modules = bar_subset.active_modules
        filename_append = bar_subset.filename_append

        cross_module_bars=[]
        print "FILE:",filename_append
        bars=[]
        node_connections = collections.defaultdict()
        with open("DBL2_node_info.csv","rb") as f: #old coordinates but still has right bar mapping
           rdr=csv.reader(f)
           rdr.next()
           for line in rdr:
              startnod=line[1]
              for x in [5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35]:
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

        with open("DBL2_crossbars.csv","rb") as f:
            rdr=csv.reader(f)
            rdr.next()
            for line in rdr:
                startnod=line[0]
                endnod=line[1]
                nodes_set=set([startnod,endnod])
                if not active_bars:
                    add_thisn=True
                else:
                    add_thisn=False
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
                    cross_module_bars.append(nodes_set)



        node_xyz=collections.defaultdict()
        node_module_xyz=collections.defaultdict()
        module_dict=collections.defaultdict()
        bars_dict = collections.defaultdict()

        with open("node_locations_150501_zeroed.csv","rU") as f:
            rdr=csv.reader(f)
            rdr.next()
            for line in rdr:
                modul=line[0]
                if int(modul) in active_modules:
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
                        

     #   for bar in bars:
     #       if bar not in module_bars:
     #           cross_module_bars.append(bar)

        #print len(cross_module_bars)

        to_bar_or_not_to_bar = []

        for bar in cross_module_bars:
            barnods=list(bar)
            try:
                barlength=xyz_dist(node_xyz[barnods[0]],node_xyz[barnods[1]])
                bar_lengths[str(barnods[0])+"-"+str(barnods[1])]=barlength
                crossbars+=barlength
            except:
                print traceback.print_exc()
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
        directorypath=modelinfo_output_directory+"/"+filename_append+"/"
        if not os.path.exists(directorypath):
            os.makedirs(directorypath)
        pixelmappingfilename = modelinfo_output_directory+"/%s/pixel_mapping.csv"%(filename_append)

        barmodulestripnumbers=get_module_bar_strip_numbers()

        write_to_pixel_mapping_file=collections.defaultdict()
        led_spacing=0.656168 #inches. the model is in inches. TODO: Use millimeters. One day we will be free from tyanny. And inches.
        
        writ_bars=set()
        #first, load the strips that are defined (when we go full-brain, this will be *every* strip we use)
        pixel_counter=0
        with open("Module_Bar_Orders.csv","rb") as f2:
            rdr=csv.reader(f2)
            rdr.next()
            for row in rdr:
                modul=row[0]
                bar_as_list=row[1].split('-')
                strip=row[2]
                bar_as_list_alphabetical=sorted(bar_as_list)
                barset=set(bar_as_list)
                if barset in bars:
                    #print bar_as_list
                    node1_alphabetic=bar_as_list_alphabetical[0]
                    node2_alphabetic=bar_as_list_alphabetical[1]
                    node1_xyz=node_module_xyz[node1_alphabetic+"-"+str(modul)]
                    node2_xyz=node_module_xyz[node2_alphabetic+"-"+str(modul)]
                    physical_bar_name='-'.join([node1_alphabetic,node2_alphabetic,str(modul)])
                    bar_len,num_pixels=get_bar_len_led_info(barset)
                    barlen_for_calc=xyz_dist(node1_xyz,node2_xyz)
                    #3.0 inch space at the end of the bar where the bolt hole is minus 1.5 inches because of where the hole is. this is rough. might need to adjust.
                    dx_bar_end_space=(node2_xyz[0]-node1_xyz[0])/barlen_for_calc*1.5 
                    dy_bar_end_space=(node2_xyz[1]-node1_xyz[1])/barlen_for_calc*1.5 
                    dz_bar_end_space=(node2_xyz[2]-node1_xyz[2])/barlen_for_calc*1.5 
                    dx=(node2_xyz[0]-node1_xyz[0])/barlen_for_calc*led_spacing
                    dy=(node2_xyz[1]-node1_xyz[1])/barlen_for_calc*led_spacing
                    dz=(node2_xyz[2]-node1_xyz[2])/barlen_for_calc*led_spacing
                    writ_bars.add(physical_bar_name)
                    pixel=[node1_xyz[0]+dx_bar_end_space,node1_xyz[1]+dy_bar_end_space,node1_xyz[2]+dz_bar_end_space]
                    for pixl in range(0,num_pixels):
                        add_row=[pixel_counter,modul,modul,node1_alphabetic,node2_alphabetic]+pixel+[strip]
                        strip_pixel=str(strip).zfill(5)+"-"+str(pixel_counter).zfill(8)
                        write_to_pixel_mapping_file[strip_pixel]=add_row
                        pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
                        pixel_counter+=1


        #then load the rest of the strips
     
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
                    barset=set(barnods)
                    node1_xyz=node_module_xyz[barnods[0]+"-"+str(modul)]
                    node2_xyz=node_module_xyz[barnods[1]+"-"+str(modul)]
                    bar_w_mod_num = barnods[0]+"-"+barnods[1]+"-"+str(modul)
                    if bar_w_mod_num not in bars_with_module_nums:
                        bars_with_module_nums.append(bar_w_mod_num)
                    if bar_w_mod_num not in writ_bars:
                        node_1_name=barnods[0]
                        node_2_name=barnods[1]       
                        #figure out if the alphabetically ordered nodes are increasing or decreasing in the x-direction for 
                        #iteratively adding LEDs down it

                        bar_len_led_info=get_bar_len_led_info(bar)
                        strip=9999 #set strip number to 9999 if not specified
                        bar_mod_key=node_1_name+"-"+node_2_name+"-"+str(modul)
                        if bar_mod_key in barmodulestripnumbers:
                            strip=barmodulestripnumbers[bar_mod_key]

                        bar_len,num_pixels=get_bar_len_led_info(barset)
                        barlen_for_calc=xyz_dist(node1_xyz,node2_xyz)
                        #3.0 inch space at the end of the bar where the bolt hole is minus 1.5 inches because of where the hole is. this is rough. might need to adjust.
                        dx_bar_end_space=(node2_xyz[0]-node1_xyz[0])/barlen_for_calc*1.5 
                        dy_bar_end_space=(node2_xyz[1]-node1_xyz[1])/barlen_for_calc*1.5 
                        dz_bar_end_space=(node2_xyz[2]-node1_xyz[2])/barlen_for_calc*1.5 
                        dx=(node2_xyz[0]-node1_xyz[0])/barlen_for_calc*led_spacing
                        dy=(node2_xyz[1]-node1_xyz[1])/barlen_for_calc*led_spacing
                        dz=(node2_xyz[2]-node1_xyz[2])/barlen_for_calc*led_spacing
                        writ_bars.add(bar_w_mod_num)
                        pixel=[node1_xyz[0]+dx_bar_end_space,node1_xyz[1]+dy_bar_end_space,node1_xyz[2]+dz_bar_end_space]
                        for pixl in range(0,num_pixels):
                            add_row=[pixel_counter,modul,modul,node_1_name,node_2_name]+pixel+[strip]
                            strip_pixel=str(strip).zfill(5)+"-"+str(pixel_counter).zfill(8)
                            write_to_pixel_mapping_file[strip_pixel]=add_row
                            pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
                            pixel_counter+=1

        #same monkey, different banana
        for bar in cross_module_bars:
            barnods=sorted(list(bar))
            barset=set(barnods)
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
                node1_xyz=node_module_xyz[node_1_name]
                node2_xyz=node_module_xyz[node_2_name]
                crossbar_w_mod_num = barnods[0]+"-"+barnods[1]+"-"+str(crossbar_modul)+"-"+str(other_modul)
                crossbar_physical_name='-'.join([barnods[0],barnods[1],str(crossbar_modul)])
                if crossbar_w_mod_num not in crossbars_with_module_nums:
                    crossbars_with_module_nums.append(crossbar_w_mod_num)
                if crossbar_physical_name not in writ_bars:
                    barlen=xyz_dist(node1_xyz,node2_xyz)

                    bar_len_led_info=get_bar_len_led_info(bar)
                    strip=9999 #set strip number to 9999 if not specified
                    bar_mod_key=node_1_name+"-"+node_2_name+"-"+str(modul)
                    if bar_mod_key in barmodulestripnumbers:
                        strip=barmodulestripnumbers[bar_mod_key]

                    bar_len,num_pixels=get_bar_len_led_info(barset)
                    barlen_for_calc=xyz_dist(node1_xyz,node2_xyz)
                    #3.0 inch space at the end of the bar where the bolt hole is minus 1.5 inches because of where the hole is. this is rough. might need to adjust.
                    dx_bar_end_space=(node2_xyz[0]-node1_xyz[0])/barlen_for_calc*1.5 
                    dy_bar_end_space=(node2_xyz[1]-node1_xyz[1])/barlen_for_calc*1.5 
                    dz_bar_end_space=(node2_xyz[2]-node1_xyz[2])/barlen_for_calc*1.5 
                    dx=(node2_xyz[0]-node1_xyz[0])/barlen_for_calc*led_spacing
                    dy=(node2_xyz[1]-node1_xyz[1])/barlen_for_calc*led_spacing
                    dz=(node2_xyz[2]-node1_xyz[2])/barlen_for_calc*led_spacing
                    pixel=[node1_xyz[0]+dx_bar_end_space,node1_xyz[1]+dy_bar_end_space,node1_xyz[2]+dz_bar_end_space]
                    for pixl in range(0,num_pixels):
                        add_row=[pixel_counter,crossbar_modul,other_modul,barnods[0],barnods[1]]+pixel+[strip]
                        strip_pixel=str(strip).zfill(5)+"-"+str(pixel_counter).zfill(8)
                        write_to_pixel_mapping_file[strip_pixel]=add_row
                        pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
                        pixel_counter+=1

                    writ_bars.add(crossbar_physical_name)

        with open(pixelmappingfilename,"wb") as f:
            wrtr=csv.writer(f)
            wrtr.writerow(["Pixel_i","Module1","Module2","Node1","Node2","X","Y","Z","Strip"])
            for strip_pixl_cnt in sorted(write_to_pixel_mapping_file.keys()):
                wrtr.writerow(write_to_pixel_mapping_file[strip_pixl_cnt])

               







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


        modelnodeinfofilename = modelinfo_output_directory+"/%s/Model_Node_Info.csv"%(filename_append)
        structuralnodeinfofilename = modelinfo_output_directory+"/%s/Structural_Node_Info.csv"%(filename_append)
        modelbarinfofilename = modelinfo_output_directory+"/%s/Model_Bar_Info.csv"%(filename_append)

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
