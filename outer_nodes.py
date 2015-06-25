import sys, random
from collections import defaultdict

old_new = {}
neighbors = defaultdict(set)
is_outer = {}

def parse_old_new(f):
    
    for line in f:
        fields = line.split('\t')
        old = fields[3].upper()
        new = fields[0].upper()
        old_new[old] = new
        old = fields[4].upper()
        new = fields[1].upper()
        old_new[old] = new

    return old_new

def parse_outer(f, old_new):
    outer_bars = set([])
    is_outer = {}
    for line in f:
        fields = (' '.join(line.split(',')[1].split('.'))).split()
        node1 = fields[0].upper()
        try:
            is_out = fields[2] == 'out'
        except:
            continue
        is_outer[node1] = is_out

        node2 = fields[4].upper()
        is_out = fields[6] == 'out'
        is_outer[node2] = is_out

        #print node1,is_outer[node1],node2,is_outer[node2]
        if not is_outer[node1] and not is_outer[node2]:
            if is_outer[node1] != is_outer[node2] and random.random() < .5:
                continue
            new_node1 = old_new[node1]
            new_node2 = old_new[node2]
            if new_node1 > new_node2:
                bar = new_node2 + '-' + new_node1
            else:
                bar = new_node1 + '-' + new_node2

            outer_bars.add(bar)
        
    return outer_bars

if __name__ == '__main__':
    old_new_file = open(sys.argv[1], 'r')
    outer_file = open(sys.argv[2], 'r')

    old_new = parse_old_new(old_new_file)
    old_new_file.close()

    outer_bars = parse_outer(outer_file, old_new)
    outer_file.close()

    for bar in outer_bars:
        print bar
