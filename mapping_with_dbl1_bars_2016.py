import os,csv, math, collections, random, time,datetime, traceback, shutil
import pickle


ground_nodes = ["WAX","AIM","LID","BOX","HUG","FLU","SIR","ONO","TAT","COP","NEW","GET","OAK","CAB","AMP","YAY","HAY","BAM","CIS","OFF","WHO","NIX","PIE","RUM","SIP"]

modelinfo_output_directory="mapping_datasets"

removed_bars=[set(["NOR","WIG"]),set(["COY","KIT"]),set(["GIN","SAY"]),set(["ALA","OIL"]), set(["DAY","SAY"])]

mapping_removed_bars=[set(['COY', 'MAD']),
set(['RAW', 'GUN']),
set(['OIL', 'ALA']),
set(['ADO', 'WAR']),
set(['ZIG', 'DAY']),
set(['BRO', 'ACE']),
set(['EON', 'POP']),
set(['DUH', 'ACT']),
set(['COY', 'KIT']),
set(['WIG', 'NOR']),
set(['VOW', 'WIZ']),
set(['GIN', 'SAY'])]

removed_bars=removed_bars+mapping_removed_bars

removed_nodes=['COY']

led_spacing=0.656168 #inches. Le sigh. 

bar_strip_numbers=[]
bar_strip_numbers_dict=collections.defaultdict()
with open("Strip_Channel_Mapping_2016.csv","rb") as f:
    rdr=csv.reader(f)
    rdr.next()
    for row in rdr:
        bar=row[1]
        strip=row[2]
        barname='-'.join(sorted(bar.split('-')))
        bar_strip_numbers.append([barname,strip])
        bar_strip_numbers_dict[barname]=strip



bars_with_clipped_pixels = collections.defaultdict()
with open("chopped_pixels.csv","rb") as f:
    rdr=csv.reader(f)
    for row in rdr:
        nodes=row[:1]
        clipped=int(row[2])
        barname='-'.join(sorted(nodes))
        bars_with_clipped_pixels[barname]=clipped


def get_subset_bars_and_nodes():
    subset_bars=[]
    subset_nodes=[]
    with open("400m_subset_Model_Bar_Info.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for row in rdr:
            barname=row[0]
            barset=set(barname.split('-'))
            if (barset not in subset_bars) and (barset not in removed_bars):
                subset_bars.append(barset)
                for node in barset:
                    if node not in subset_nodes:
                        subset_nodes.append(node)
    #manually added HOW-RUM and RUM-SHY, they're right near the door and it'll look better. 
    #commented out, only needed to do it once but keeping this here as a reminder that these bars were added.
    #remove this later (after the 2015 burn)
   #""" subset_bars.append(set(["RUM","SHY"]))
   # subset_bars.append(set(["RUM","HOW"]))
   # subset_bars.append(set(["SHY","HOW"]))
   # for node in ["RUM","SHY","HOW"]:
   #     if node not in subset_nodes:
   #         subset_nodes.append(node)"""

    return subset_bars, subset_nodes

def get_snowflake_bars_and_nodes():
    snowflake_bars=[]
    snowflake_nodes=[]
    for x in range(1,7):
        node1="100"
        node2="1"+str(x)+"0"
        snowflake_bars.append(set([node1,node2]))
        node1=node2
        node2="1"+str(x)+"2"
        snowflake_bars.append(set([node1,node2]))
        node1="1"+str(x)+"1"
        node2="1"+str(x)+"0"
        snowflake_bars.append(set([node1,node2]))
        node1="1"+str(x)+"0"
        node2="1"+str(x)+"3"
        snowflake_bars.append(set([node1,node2]))
    for bar in snowflake_bars:
        for node in bar:
            if node not in snowflake_nodes:
                snowflake_nodes.append(node)
    return snowflake_bars,snowflake_nodes



def get_snode_xyz():
    node_xyz=collections.defaultdict()
    with open("snowflake_nodes.csv","rU") as f:
        rdr=csv.reader(f)
        for line in rdr:
            node=str(line[0])
            x=float(line[1])
            y=float(line[2])
            z=float(line[3])
            if node!="FEW" and node != 'COY' and node != 'DAY':
                node_xyz[node]=[x,y,z] 
    return node_xyz
    


def get_node_xyz():
    node_xyz=collections.defaultdict()
    with open("DBL1_Node_Coords_zeroed.csv","rU") as f:
        rdr=csv.reader(f)
        for line in rdr:
            node=line[0]
            x=float(line[1])
            y=float(line[2])
            z=float(line[3])
            if node!="FEW" and node != 'COY' and node != 'DAY':
                node_xyz[node]=[x,y,z] 
    return node_xyz


def subset_shells(file_to_load):
    """ parameter target is not used, vestigial? """
    all_bars = []
    with open(file_to_load,'r') as f:
        rdr = csv.reader(f)
        for line in rdr:
            all_bars.append(line[0])
    return all_bars


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

def inner_outer_errthing():
    in_out_mid_bars=collections.defaultdict()
    in_out_nodes=collections.defaultdict()
    filename_designations=[("inner_bars.csv","inner"),("outer_bars.csv","outer"),("in_to_out_bars.csv","in_to_out")]

    #handle bars
    for fildes in filename_designations:
        fil=fildes[0]
        des=fildes[1]
        with open(fil) as f:
            rdr=csv.reader(f)
            for row in rdr:
                nodes=row[0].split('-')
                bar='-'.join(sorted(nodes))
                in_out_mid_bars[bar]=des

    #handle nodes
    for bar in in_out_mid_bars:
        if in_out_mid_bars[bar]=="inner":
            for node in bar.split('-'):
                in_out_nodes[node]="inner"
        if in_out_mid_bars[bar]=="outer":
            for node in bar.split('-'):
                in_out_nodes[node]="outer"
    return in_out_mid_bars,in_out_nodes



def get_bars():
    bars=[]
    node_connections = collections.defaultdict()
    with open("node_info_DBL1.csv","rb") as f:
        rdr=csv.reader(f)
        rdr.next()
        for line in rdr:
          startnod=line[0]
          for x in [4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34]:
             if len(line)>=x+1:
                endnod=line[x]
                nodes_set=set([startnod,endnod])
                if nodes_set not in bars and "FEW" not in nodes_set and "COY" not in nodes_set and 'DAY' not in nodes_set: #avoid duplicates
                    bars.append(nodes_set)
    return bars



def get_ground_bars():
    outer_nodes=get_outer_nodes()
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




def xyz_dist(point1,point2):
    return math.sqrt(math.pow((point2[0]-point1[0]),2) +  math.pow((point2[1]-point1[1]),2) + math.pow((point2[2]-point1[2]),2))



def get_other_node(barset,node):
    if node in barset:
        for node_i in barset:
            if node_i != node:
                return node_i
    return False



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
        #        if barnamstr in bars_with_clipped_pixels:
        #            num_leds = num_leds-bars_with_clipped_pixels[barnamstr]
                return bar_len,num_leds
    return False


def get_modules_for_wiring():
    modulesdict=collections.defaultdict()
    with open("subset_modules_for_wiring.csv","rb") as f:
        rdr=csv.reader(f)
        for row in rdr:
            modulesdict[row[0]]=int(row[1])
    return modulesdict


def left_right_mid(xyz1,xyz2):
    if xyz1[0] > 6 and xyz2[0] > 6:
        return "right"
    elif xyz1[0] < -6 and xyz2[0] < -6:
        return "left"
    else:
        return "mid"


def bar_to_str(bar):
    return '-'.join(sorted(list(bar)))

def are_bars_adjacent(bar1,bar2):
    if bar1==bar2:
        return False
    allnodes=set()
    for node in bar1:
        allnodes.add(node)
    for node in bar2:
        allnodes.add(node)
    other_nodes=[]
    common_node=None
    for node in allnodes:
        if node in bar1 and node in bar2:
            common_node=node
        else:
            other_nodes.append(node)
    if common_node:
        return[common_node,other_nodes]
    return False


def remove_bars_not_in_mapping(subset_bars):
    with open('Node_to_node_in_strip_pixel_order_2016.csv','rb') as f:
        mapping_bars=[]
        rdr=csv.reader(f)
        for row in rdr:
            row2=row
            if row2[0]!="Strip":
                barname=set([row[1],row[2]])
                mapping_bars.append(barname)
    for bar in subset_bars:
        if bar not in mapping_bars:
            print bar
    for bar in mapping_bars:
        if bar not in subset_bars:
            print "DAFUQ",bar
    return mapping_bars



#input: bars and their corresponding nodes
def eulerian_unfuck(bars,nodes,all_possible_bars):
    barcount=collections.defaultdict()
    euler_materializes_out_of_thin_air_with_steel_bars=[]

    extra_possible_bars=[]
    for bar in all_possible_bars:
        if bar not in bars:
            extra_possible_bars.append(bar)

    for node in nodes:
        barcount[node]=0
        for bar in bars:
            if node in bar:
                barcount[node]+=1
    fucked_nodes=0
    for node in barcount:
        if barcount[node]%2>0:
            fucked_nodes+=1
    print "Fucked nodes: ",fucked_nodes
    for bar in all_possible_bars:
        if bar not in bars:
            nodes_in_distress=0
            for node in bar:
                if barcount[node]% 2 > 0:
                    nodes_in_distress+=1
            if nodes_in_distress==2:
                euler_materializes_out_of_thin_air_with_steel_bars.append(bar)
                for node in bar:
                    barcount[node]+=1



    extra_possible_bars=[]
    for bar in all_possible_bars:
        if bar not in bars and bar not in euler_materializes_out_of_thin_air_with_steel_bars:
            extra_possible_bars.append(bar)

    #experimental part...

    for bar1 in extra_possible_bars:
        for bar2 in extra_possible_bars:
            useful_information=are_bars_adjacent(bar1,bar2)
            if useful_information:
                nodes_in_distress=0
                for node in useful_information[1]:
                    if barcount[node]% 2 > 0:
                        nodes_in_distress+=1
                if nodes_in_distress==2:
                    euler_materializes_out_of_thin_air_with_steel_bars.append(bar1)
                    euler_materializes_out_of_thin_air_with_steel_bars.append(bar2)
                    for node in useful_information[1]:
                        barcount[node]+=1

    # remove_bars=[]
    # for node1 in barcount:
    #     if barcount[node1]% 2 > 0:
    #         for node2 in barcount:
    #             if barcount[node2]% 2 > 0:
    #                 if set([node1,node2]) in bars:
    #                     remove_bars.append(set([node1,node2]))
    #                     barcount[node1]-=1
    #                     barcount[node2]-=1



   # for bar in remove_bars:
   #     bars.remove(bar)
    for bar in euler_materializes_out_of_thin_air_with_steel_bars:
        bars.append(bar)

    for node in nodes:
        barcount[node]=0
        for bar in bars:
            if node in bar:
                barcount[node]+=1

    fucked_nodes=0
    for node in barcount:
        if barcount[node]%2>0:
            fucked_nodes+=1
    print "Post-Euler fucked nodes: ",fucked_nodes
    return bars




def write_files(filename_append,bars,nodes_xyz):

    directorypath=modelinfo_output_directory+"/"+filename_append+"/"
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    modelnodeinfofilename = modelinfo_output_directory+"/%s/Model_Node_Info.csv"%(filename_append)
    modelbarinfofilename = modelinfo_output_directory+"/%s/Model_Bar_Info.csv"%(filename_append)
    pixelmappingfilename = modelinfo_output_directory+"/%s/pixel_mapping.csv"%(filename_append)

    in_out_mid_bars,in_out_nodes = inner_outer_errthing()
    groundbars=get_ground_bars()
    wiring_modules=get_modules_for_wiring()







    with open(pixelmappingfilename,"wb") as f:
        wrtr=csv.writer(f)
        wrtr.writerow(["Pixel_i","Module1","Module2","Inner_Outer","Left_Right_Mid","Node1","Node2","X","Y","Z","Strip"])
        pixel_i=0
        bars_in_load_order=[]
        for bar in bar_strip_numbers:
            barset=set(bar[0].split('-'))
            if barset in bars and barset not in removed_bars:
                bars_in_load_order.append(barset)
        for bar in bars:
            if bar not in bars_in_load_order and bar not in removed_bars:
                bars_in_load_order.append(bar)
        for bar in bars_in_load_order:
            barstr=bar_to_str(bar)
          #  print bar
            node_1=sorted(list(bar))[0]
            node_2=sorted(list(bar))[1]
            node_1_xyz = nodes_xyz[node_1]
            node_2_xyz = nodes_xyz[node_2]                    
            strip=9999 #set strip number to 9999 if not specified
            if barstr in bar_strip_numbers_dict:
                strip=int(bar_strip_numbers_dict[barstr])
                strip=str(strip)
            module=1 #no moar modules but keeping this here in case we end up using them to divvy up where shit goes
            if barstr in wiring_modules:
                module=wiring_modules[barstr]
            #print bar
            bar_len,num_pixels=get_bar_len_led_info(bar)
            barlen_for_calc=xyz_dist(node_1_xyz,node_2_xyz)

            inner_outer_mid="inner"
            leftrightmid="mid"

            #3.0 inch space at the end of the bar where the bolt hole is minus 1.5 inches because of where the hole is. this is rough. might need to adjust.
          
            dx_bar_end_space=(node_2_xyz[0]-node_1_xyz[0])/barlen_for_calc*(barlen_for_calc-num_pixels*led_spacing)*1/2
            dy_bar_end_space=(node_2_xyz[1]-node_1_xyz[1])/barlen_for_calc*(barlen_for_calc-num_pixels*led_spacing)*1/2
            dz_bar_end_space=(node_2_xyz[2]-node_1_xyz[2])/barlen_for_calc*(barlen_for_calc-num_pixels*led_spacing)*1/2 
            dx=(node_2_xyz[0]-node_1_xyz[0])/barlen_for_calc*led_spacing
            dy=(node_2_xyz[1]-node_1_xyz[1])/barlen_for_calc*led_spacing
            dz=(node_2_xyz[2]-node_1_xyz[2])/barlen_for_calc*led_spacing
            pixel=[node_1_xyz[0]+dx_bar_end_space,node_1_xyz[1]+dy_bar_end_space,node_1_xyz[2]+dz_bar_end_space]
            for pixl in range(0,num_pixels):
                add_row=[pixel_i,module,module,inner_outer_mid,leftrightmid,node_1,node_2]+pixel+[strip]
                strip_pixel=str(strip).zfill(5)+"-"+str(pixel_i).zfill(8)
                pixel=[pixel[0]+dx, pixel[1]+dy, pixel[2]+dz]
                pixel_i+=1
                wrtr.writerow(add_row)



    with open(modelnodeinfofilename,"wb") as f:
        wrtr=csv.writer(f)
        wrtr.writerow(["Node","X","Y","Z","Subnodes","Neighbor_Nodes","Bars","Physical_Bars","Physical_Nodes","Ground","Inner_Outer","Left_Right_Mid"])
        for node in nodes_xyz:
            
            #get neighboring bars and nodes
            neighbornodes=[]
            neighborbars=[]
            for bar in bars:
                if node in bar and bar not in removed_bars:
                    othernode=get_other_node(bar,node)
                    neighbornodes.append(othernode)
                    neighborbars.append(bar_to_str(bar))
            neighbornodes='_'.join(neighbornodes)
            neighborbars='_'.join(neighborbars)
            
            #is it a ground node?
            if node in ground_nodes:
                ground="1"
            else:
                ground="0"

            #inner shell or outer shell?
            inner_outer="inner"#in_out_nodes[node]

            #which hemisphere?
            leftrightmid="mid"#left_right_mid(nodes_xyz[node],nodes_xyz[node])

            #make the row to put in the file
            row=[node]+nodes_xyz[node]+["DEPRECATED",neighbornodes,neighborbars,"DEPRECATED","DEPRECATED",ground,inner_outer,leftrightmid]
            wrtr.writerow(row)




    with open(modelbarinfofilename,"wb") as f:
        wrtr=csv.writer(f)
        wrtr.writerow(["Bar_name","Module","Min_X","Min_Y","Min_Z","Max_X","Max_Y","Max_Z","Nodes","Physical_Bars","Physical_Nodes","Adjacent_Nodes","Adjacent_Physical_Bars","Adjacent_Bars","Adjacent_Physical_Nodes","Ground","Inner_Outer","Left_Right_Mid"])
        for bar in bars_in_load_order:
            barstr=bar_to_str(bar)
            module=1
            if barstr in wiring_modules:
                module=wiring_modules[barstr]

            #get the min max xyz based on the nodes of the bar
            min_x=10000
            min_y=10000
            min_z=10000
            max_x=-10000
            max_y=-10000
            max_z=-10000
            for node in bar:
                xyz=nodes_xyz[node]
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

            nodes = '_'.join(sorted(list(bar)))


            #get neighboring bars and nodes
            adjacentnodes=[]
            adjacentbars=[]
            for node in bar:
                for bar_in_whole_model in bars:
                    if node in bar_in_whole_model and bar_in_whole_model not in removed_bars:
                        othernode=get_other_node(bar_in_whole_model,node)
                        adjacentnodes.append(othernode)
                        adjacentbars.append(bar_to_str(bar_in_whole_model))
            adjacentnodes='_'.join(adjacentnodes)
            adjacentbars='_'.join(adjacentbars)


            ground=1
            for node in bar:
                if node not in ground_nodes:
                    ground=0
            innerouter="inner"#in_out_mid_bars[barstr]

            node_1=sorted(list(bar))[0]
            node_2=sorted(list(bar))[1]
            node_1_xyz = nodes_xyz[node_1]
            node_2_xyz = nodes_xyz[node_2]

            leftrightmid="mid"#left_right_mid(node_1_xyz,node_2_xyz)
            
            row=[barstr,module,min_x,min_y,min_z,max_x,max_y,max_z,nodes,"DEPRECATED","DEPRECATED",adjacentnodes,"DEPRECATED",adjacentbars,"DEPRECATED",ground,innerouter,leftrightmid]
            wrtr.writerow(row)




    print "SUBSET NAME: ",filename_append
    print "BARS: ", len(bars)
    print "PIXELS: ", pixel_i
    print "METERS OF STRIP: ", pixel_i/60



if __name__=="__main__":

    bar_subsets = []

    all_bars = get_bars()
    active_nodes_xyz=get_node_xyz()
    """filename_append = "Full_Brain_DBL1"
    all_bars = get_bars()
    active_nodes_xyz=get_node_xyz()
    write_files(filename_append,all_bars,active_nodes_xyz)


    filename_append = "Subset_Brain"
    active_bars, active_nodes = get_subset_bars_and_nodes()
    write_files(filename_append,active_bars,active_nodes_xyz)

    filename_append = "Playa_Brain2" #"Eulerian_unfuck"
    active_bars, active_nodes = get_subset_bars_and_nodes()
    active_bars=eulerian_unfuck(active_bars,active_nodes,all_bars)
    for bar in removed_bars:
        if bar in active_bars:
            active_bars.remove(bar)
    write_files(filename_append,active_bars,active_nodes_xyz)"""


    filename_append = "Playa_Brain_2016"
    active_bars, active_nodes = get_subset_bars_and_nodes()
    active_bars =  remove_bars_not_in_mapping(eulerian_unfuck(active_bars,active_nodes,all_bars))

    write_files(filename_append,active_bars,active_nodes_xyz)

    #srsly wtf shutil this should have been one line of code
    #i am angered
    #nothing will actually happen
    #okay fine I'll write the csv and shut up
    #edit: whoops missed a thing god damn it
    with open('Node_to_node_in_strip_pixel_order_2016.csv','rb') as f:
        with open('mapping_datasets/Playa_Brain_2016/Node_to_node_in_strip_pixel_order.csv','wb') as fout:
            rdr=csv.reader(f)
            wrtr=csv.writer(fout)
            for row in rdr:
                row2=row
               # if row2[0]!="Strip":
                #    if int(row2[0])>=4:
                 #       row2[0]=str(int(row2[0])+3)
                wrtr.writerow(row2)


    
