"""
Given the machine readable node and pixel lists, create a human readable
map of the LED channels, consisting of the channel number, the node to node connections,
the number of pixels on each strip and the associated color code, and the total channel length
"""

import numpy as np
import csv

filename = "mapping_datasets\Playa_Brain\Node_to_node_in_strip_pixel_order.csv"

with open(filename, 'r') as f:
	reader = csv.reader(f)
	channellist = [ [] for x in range(48)]
	curchannel = -1
	for i, row in enumerate(reader):
		if i==0: 
			continue
		ch = int(row[0])
		if curchannel != ch:
			curchannel = ch
			channellist[curchannel].append(row[1])
		channellist[curchannel].append(row[2])


pixelfn = "mapping_datasets\Playa_Brain\pixel_mapping.csv"
with open(pixelfn, 'r') as f:
	rdr = csv.reader(f)
	rdr.next()  # skip the header
	curchannel = -1
	curedgecount = 0
	curbar = ()
	barlengths = {}
	for row in rdr:
		pixNum = int(row[0])
		moduleNum = int(row[1])
		node1 = row[5]
		node2 = row[6]
		barname = (node1, node2)
		channelNum = int(row[10])
		if barname not in barlengths.keys():
			# new bar, create it and add one pixel
			barlengths.update({barname: 1})
		else:
			barlengths[barname] += 1

barlist = barlengths.keys()



colormap ={ 27: None,
			32: 'blk',
			36: 'yel',
			41: 'blu',
			45: 'red',
			50: 'grn',
			54: 'pnk',
			59: 'pur',
			64: 'ltgrn',
			68: 'pnkstr',
			73: 'yelstr',
			77: None,
			86: None
			}
meterPerPix = 1 / 60.
meter2inch = 39.3701
meter2ft = 3.28084

outfile = "mapping_datasets\Playa_Brain\Channel_bar_map.txt"

totalCableLength = 0

with open(outfile, "w") as f:
	for i, channel in enumerate(channellist):
		f.write("module %i, channel %i:  " % (int(i/6)+1, i))
		lastnode=''
		curlength = 0
		for j, curnode in enumerate(channel):
			if lastnode != '':  # we have at least one bar
				targetbar = ''
				for bar in barlist:
					if lastnode in bar and curnode in bar:
						targetbar = bar
						break
				if targetbar == '':
					print("couldnt find targetbar: %s-%s" % (lastnode, curnode))
				pxLength = barlengths[targetbar]
				# print(pxLength * meterPerPix)
				curlength += pxLength * meterPerPix + 0.3  # add 30cm for connector cable 
				f.write("[%i:%s] -%s" % (barlengths[targetbar], colormap[pxLength], curnode))
				if j == len(channel)-1:
					f.write("   [length: %.2f m (%.2f ft)]\n" % (curlength, curlength * meter2ft))
					totalCableLength += curlength * meter2ft
					f.write("\n")
			else:
				f.write(curnode)  #write the first node on the channel

			lastnode = curnode
	f.write("total strip length: %.2f" % totalCableLength)
