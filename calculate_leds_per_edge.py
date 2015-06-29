import csv

module_14_bars=[set(["LIE","OLD"]), set(["LIE","TAU"]), set(["OLD","TAU"]), set(["GIG","LIE"]), set(["ERA","IRE"]), set(["ERA","RIB"]), set(["FOG","RIB"]), set(["FOG","TAU"]), set(["GIG","IRE"]), set(["ERA","GIG"]), set(["ERA","LAW"]), set(["EVE","GIG"]), set(["EVE","IRE"]), set(["EVE","LAW"]), set(["EVE","LIE"]), set(["EVE","OLD"]), set(["FOG","OLD"]), set(["GIG","LAW"]), set(["IRE","LAW"]), set(["IRE","RIB"]), set(["LAW","LIE"]), set(["LAW","OLD"]), set(["LAW","RIB"]), set(["LAW","FOG"]), set(["LAW","TAU"])]


bar_names_lengths_etc=[]
bar_names_lengths_etc_m14=[] #TODO: Make this handle all modules, not just 14 (and with the right layout)
with open("DBL1_edgelengths.csv","rb") as f:
	rdr=csv.reader(f)
	rdr.next() #header row
	for row in rdr:
		barname=row[0]
		barname_set=set(row[0].split('-'))
		module_14=False
		if barname_set in module_14_bars:
			module_14=True
		barlength=float(row[1])
		barlengthmeters=float(barlength)*0.0254
		num_leds=int((barlength-6.0)/0.656168) #the 6.0 is subtracting the ~3inch ends, the other thing is a conversion because shit's in inches
		len_leds_inches=0.656168*num_leds
		len_leds_meters=num_leds/60.0
		bar_names_lengths_etc.append([barname,barlength,barlengthmeters,num_leds,len_leds_meters,len_leds_inches])
		if module_14:
			bar_names_lengths_etc_m14.append([barname,barlength,barlengthmeters,num_leds,len_leds_meters,len_leds_inches])

with open("DBL2_edgelengths_with_led_counts.csv","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Bar name","Bar length (inches)", "Bar length (meters)","Num_leds","len_leds_meters","len_leds_inches"])
	for bar in bar_names_lengths_etc:
		wrtr.writerow(bar)


with open("DBL2_edgelengths_with_led_counts_mod14.csv","wb") as f:
	wrtr=csv.writer(f)
	wrtr.writerow(["Bar name","Bar length (inches)", "Bar length (meters)","Num_leds","len_leds_meters","len_leds_inches"])
	for bar in bar_names_lengths_etc_m14:
		wrtr.writerow(bar)


print "done"
