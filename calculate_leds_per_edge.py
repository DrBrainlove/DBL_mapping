import csv

bar_names_lengths_etc=[]
with open("DBL1_edgelengths.csv","rb") as f:
	rdr=csv.reader(f)
	rdr.next() #header row
	for row in rdr:
		barname=row[0]
		barlength=float(row[1])
		barlengthmeters=float(barlength)*0.0254
		num_leds=int((barlength-6.0)/0.656168) #the 6.0 is subtracting the ~3inch ends, the other thing is a conversion because shit's in inches
		len_leds_inches=0.656168*num_leds
		len_leds_meters=num_leds/60.0
		bar_names_lengths_etc.append([barname,barlength,barlengthmeters,num_leds,len_leds_meters,len_leds_inches])

with open("DBL2_edgelengths_with_led_counts","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Bar name","Bar length (inches)", "Bar length (meters)","Num_leds","len_leds_meters","len_leds_inches"])
	for bar in bar_names_lengths_etc:
		wrtr.writerow(bar)


print "done"
