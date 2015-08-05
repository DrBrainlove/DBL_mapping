import csv
import collections

module_14=[
["LAW", 	 "Fog"],
["Fog", 	 "Rib"],
["Rib", 	 "Era"],
["Era", 	 "LAW"],
["Old", 	 "Eve"],
["Eve", 	 "LAW"],
["LAW", 	 "Old"],
["Old", 	 "Fog"],
["Gig", 	 "Lie"],
["Old", 	 "Lie"],
["LAW", 	 "Lie"],
["Lie", 	 "Eve"],
["Eve", 	 "Gig"],
["Gig", 	 "Ire"],
["Ire", 	 "Era"],
["Era", 	 "Gig"],
["Gig", 	 "LAW"],
["Rib", 	 "Ire"],
["Ire", 	 "Eve"]]

modules_and_whatnot=collections.defaultdict()

with open("DBL2_module_edges.csv","rb") as f:
	rdr=csv.reader(f)
	rdr.next()
	for row in rdr:
		barnammod=row[0]
		barnam=set(barnammod.split('-')[:2])
		barmod=int(barnammod.split('-')[2])
		if barmod not in modules_and_whatnot:
			modules_and_whatnot[barmod]=[]
		modules_and_whatnot[barmod].append(barnam)




module_14_fixed=[]

for x in module_14:
	new_barthing=[]
	for thing in x:
		new_barthing.append(thing.upper())
	snew_barthing=set(new_barthing)
	module_14_fixed.append(snew_barthing)


module_14=module_14_fixed




module_bar_orders_etc=collections.defaultdict()


mod14_bars=collections.defaultdict()

with open("new_and_old_nodes.csv","rbU") as f:
	rdr=csv.reader(f)
	for line in rdr:
		bar_name=set([line[0],line[1]])
		bar_numbr=line[8]
		for module in modules_and_whatnot:
			if bar_name in modules_and_whatnot[module]:
				if module not in module_bar_orders_etc:
					module_bar_orders_etc[module]=collections.defaultdict()
				module_bar_orders_etc[module][int(bar_numbr)]=str(module)+"\t"+str(bar_numbr)+"\t"+'-'.join(sorted(bar_name))


for module in sorted(module_bar_orders_etc.keys()):
	print 
	for bar_numbr in sorted(module_bar_orders_etc[module].keys()):
		print module_bar_orders_etc[module][bar_numbr]


#for key in sorted(mod14_bars.keys()):
#	print key,mod14_bars[key]

