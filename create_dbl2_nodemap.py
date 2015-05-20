"""
create node map for each module

Merge the original DBL1 node coordinate and connected node file with the DBL2 node coordinates.
We want a file that has a list of each node in each module, dinstinguished by module number, the coordinates of that node, all of the edges it connects to within a module, and the bolt-to-bolt distance between the nodes
"""

import os
import csv
import math
import collections

import numpy as np

class DBLModule:
    """
    class that holds list of nodes and edges in a module
    """
    def __init__(self):
        self.nNodes = 0  # number of nodes
        self.moduleName = ""
        self.nodes = [] # list of node names
        self.nodeCoords = {} # key:nodename, val=(x,y,z)
        self.edges = []  # list of edge tuple, avoiding duplicates
        self.edgeNames = [] # list of edge names, 14-NOD-NAM, no duplicates
        self.edgeLengths = {}  # dict with lengths, key by edgename
        self.totalLength = 0
        self.totalLengthWDuplicates = 0


def normL2(point1, point2):
    """
    return the euclidian distance between two 3D points
    expects list or tuple of xyz coords per point
    can also use numpy.linalg.norm()
    """
    point1 = np.array(point1)
    point2 = np.array(point2)
    return np.sqrt(np.sum((point1 - point2) ** 2))


# =================================
if __name__ == "__main__":

    bars = []
    barLengths = []
    print("loading old nodes and edges")
    # old coordinates but still has right bar mapping, including crossmodule bars
    with open("node_info_DBL1.csv", "rb") as f:
        rdr = csv.reader(f)
        rdr.next()  # skip the header line
        for line in rdr:
            startnod = line[0]  # node name
            # go through all connected node names.
            # elements 1:3 are old coordinates, then alternates NODE, LENGTH
            # across the rest of the connected edges.
            n = len(line)
            if n % 1 == 1:
                raise ValueError(
                    "odd number of elements for line (node %s), error in file?" % startnod)
            for x in range(4, n, 2):
                edgename = sorted([startnod, line[x]])
                # nodes_set = set((startnod, line[x]))
                barlen = line[x+1]
                if edgename not in bars:  # avoid duplicates
                    bars.append(edgename)
                    barLengths.append((edgename, barlen))

    # write edge lengths for DBL1
    with open("DBL1_edgelengths.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerow(["# edge", "length (in)"])
        for edge in barLengths:
            node1=edge[0][0]
            node2=edge[0][1]
            nodename = node1+"-"+node2
            writer.writerow([nodename, edge[1]])
    print("wrote DBL1_edgelengths.csv to file")

    # Read in module coordinates
    # This is where we get our list of nodes in a module,
    # and what we need to create a list of edges across modules.
    # There is a subset of edges that will be duplicated across modules,
    # these are the frames, or module edges.
    #
    # all coordinates loaded are in INCHES. TODO: fix that shit

    moduleList = collections.defaultdict(DBLModule)

    allbars = []
    nodeCoordsAll = {}
    crossbars = [] #remove edges from this as we find them

    print("loading new coordinates")
    with open("DBL2_node_locations_150501.csv", "rU") as f:
        rdr = csv.reader(f)
        rdr.next() # skip header line
        for line in rdr:
            modul = int(line[0])
            node = line[1]
            x = float(line[2])
            y = float(line[3])
            z = float(line[4])
            moduleList[modul].nNodes +=1
            moduleList[modul].moduleName = str(modul)
            moduleList[modul].nodes.append(node)
            moduleList[modul].nodeCoords[node] = (x, y, z)
            nodeCoordsAll[node] = (x, y, z)


    print("creating new edges for each module")
    for i,m in moduleList.items():
        # dicts aren't ordered, this will be sorted later
        # look through barLengths to find previous edge definition
        # when we create an edge, sort the node names aphabetically
        for bar in bars:
            in_module = True
            # check if one of the nodes is in the current module
            for barnode in bar:
                if barnode not in m.nodes:
                    in_module= False # exit out, go to next bar
            if in_module:
                # edgename = bar[0] + "-" + bar[1]
                edgename = bar[0] + "-" + bar[1] + "-" + m.moduleName
                edgelen = normL2(m.nodeCoords[bar[0]], m.nodeCoords[bar[1]])

                if bar not in m.edges:
                    m.edges.append(bar)
                    m.edgeNames.append(edgename)
                    m.edgeLengths[edgename] = edgelen
                    m.totalLength += edgelen
                    m.totalLengthWDuplicates += edgelen
                    allbars.append(bar)
                else:
                    # do we want to add duplicate bars to the module?
                    m.totalLengthWDuplicates += edgelen

    # in the translation from DBL1 to DBL2, there looks like there
    # is a partial list of dropped bars in the "Brain_struts_Register-01-15-15.xlsx"
    # MJP created this subset from that list
    missingbars = []
    with open("DBL2_registry_missingedges.csv", "rb") as f:
        reader = csv.reader(f)
        reader.next() # skip two comment lines
        reader.next()
        for line in reader:
            modul = line[0]
            bar = [line[1], line[2]]
            missingbars.append(bar)

    # get the crossbar list
    # this is currently the list of ALL bars that cross the modules.
    # in reality, we will only be using a subset of this list
    print("Checking crossbars not explicitly in a module")

    crossbar_length = 0.
    crossbar_count = 0
    with open("DBL2_crossbars.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerow(["crossbars not in specific module",""])
        for bar in bars:
            if bar not in allbars: # and bar not in missingbars:
                # we could be smarter about looking for the KeyError, but don't know which node is missing a priori
                try:
                    cbarLength = normL2(nodeCoordsAll[bar[0]], nodeCoordsAll[bar[1]])
                    crossbars.append(bar)
                    crossbar_length += cbarLength
                    crossbar_count += 1
                    # it would be nice to report which module which node is in as well
                    # that is a nontrivial search though
                    writer.writerow([bar[0], bar[1]])
                except KeyError as e:
                    print "Bar doesn't exist: ", bar
                    print "\tNo reference to node: ", e.args[0]

    print("wrote DBL2_crossbars.csv to file")


    # write out the database to match the format of the DBL1_node_info
    with open("DBL2_node_info.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerow(["module","name","x(inches)","y(inches)","z(inches)","[name and distance (inches) for all connected nodes]"])
        for i,m in moduleList.items():
            for node in m.nodes:
                row=[i]
                row.append(node)
                row.extend(m.nodeCoords[node])
                # find all edges that have this node
                connected = []
                for edgeix, (n1,n2) in enumerate(m.edges):
                    if n1==node:
                        # find the edge connecting with n2 and get the length
                        edgelen = m.edgeLengths[m.edgeNames[edgeix]]
                        connected.extend([n2, "{0:.3f}".format(edgelen)])
                    if n2==node:
                        edgelen = m.edgeLengths[m.edgeNames[edgeix]]
                        connected.extend([n1, "{0:.3f}".format(edgelen)])
                # print(connected)
                row.extend(connected)
                writer.writerow(row)
    print("wrote DBL2_node_info.csv to file")

    # print all of the edge names and lengths out
    total_barlengths = []
    with open("DBL2_module_edges.csv","wb") as f:
        writer = csv.writer(f)
        writer.writerow([ "edge name", "edge length"])
        for i,m in moduleList.items():
            for edge in m.edgeNames:
                writer.writerow([edge, m.edgeLengths[edge]])
        # another thing I could add to this is a list of all the
        # crossbars, linking between modules
    print("wrote DBL2_module_edges.csv to file")



# I need to manually create a list of the edges that
# will not have lights on them, and pull those out of the main estimates

# # print measurements
# print "Total module bar distance with duplicates: ",
# print int(total_distance_with_duplicates*0.0254),"m across",len(module_bars),"bars = ",int(total_distance_with_duplicates*0.0254*60),"LEDs"

# print "Total module bar distance sans duplicates: ",
# print int(total_distance_sans_duplicates*0.0254),"m across",len(module_bars_sans_doubles),"bars = ",int(total_distance_sans_duplicates*0.0254*60),"LEDs"

# print "Total distance of bar doubles: ",
# print int(double_bars_length*0.0254), " m across",len(double_bars),"bars = ",int(double_bars_length*0.0254*60),"LEDs"

# print "Total distance of cross-module bars: ",
# print int(crossbars*0.0254)," m across",len(cross_module_bars),"bars = ",int(crossbars*0.0254*60),"LEDs"

# print "Total length of bars (with duplicates and cross bars): ", 
# print total_bars_length *0.0254,"m"

# print "Average bar length (with duplicates and cross bars): ",
# print total_bars_length/total_bars*0.0254,"m"

# print "Total number of bars (with duplicates and cross bars): ",total_bars

# print "Also, node FEW seems to be missing from the new node coordinates (5 bars attached)"

