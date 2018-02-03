import disk,subprocess,time,getopt,sys

diskName = ["sda1"]
upperLimit = "5184000"
step = 1
graphName = "graph"
startTime = "now-60"
endTime = "now"
delay = 1
printTimes = 'm'
bUpdate = False
bPrinting = False
cPalette = ("E14C00", "DCF600", "FF0000")

def create(step):			# creates a mem.rrd file as defined step
	graphFile = "mkdir -p graphs/m/DISK graphs/h/DISK graphs/d/DISK graphs/w/DISK graphs/M/DISK"
	pGraphFile = subprocess.Popen(graphFile, stdout = subprocess.PIPE, shell=True)
	(oGraphFile, eGraphFile) = pGraphFile.communicate()
	print "Files are created"
	currentTime = time.time()
	rrdCreate = "rrdtool create disk.rrd --step %d " % (step)
	for i in diskName:
		rrdCreate +=   "DS:%sUSED:GAUGE:%d:U:U " % (i, 2 * step)		# the buffers data source has heartbeat as 2 step size
		rrdCreate +=   "DS:%sAVAILABLE:GAUGE:%d:U:U " % (i, 2 * step)	# the cached memory data source has heartbeat as 2 step size
		rrdCreate +=   "DS:%sPERCENT:GAUGE:%d:U:U " % (i, 3 * step)		# the cached memory data source has heartbeat as 2 step size
	rrdCreate += "RRA:AVERAGE:0:1:%s " % (upperLimit)
	pRRD = subprocess.Popen(rrdCreate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def fetch(sTime, eTime):	# fetches the data from sTime to eTime
	rrdFetch = "rrdtool fetch disk.rrd AVERAGE --start %s --end %s " % (sTime, eTime)
	pRRD = subprocess.Popen(rrdFetch, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def update(used, available, perc):	# updates values from input percentage and used memory with timestamp
	t = time.time()
	rrdUpdate = "rrdtool update disk.rrd -t "
	print t, used, available, perc
	for i in diskName:
		j = diskName.index(i)
		rrdUpdate +=  i +"USED:"+ i +"AVAILABLE:"+ i +"PERCENT %f:%d:%d:%f" % (t, used[j], available[j], perc[j])
	pRRD = subprocess.Popen(rrdUpdate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def graph(typ, uColour, aColour, pColour, sTime, eTime, output):	# prints graphs
	for i in diskName:
		rrdGraph = "rrdtool graph graphs/%s_blocks.png --start %s --end %s " % (output, sTime, eTime)
		rrdGraph += " --vertical-label \"Disk Blocks\" --lower-limit 0 --slope-mode --base=1000 "
		rrdGraph += "DEF:used=disk.rrd:"+i+"USED:%s CDEF:na-used=used,UN,0,used,IF AREA:na-used#%s:\"Used Block\" " % (typ, uColour)
		rrdGraph += "DEF:available=disk.rrd:"+i+"AVAILABLE:%s CDEF:na-available=available,UN,0,available,IF STACK:na-available#%s:\"Available Block\" " % (typ, aColour)
		pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
		(oRRD, eRRD) = pRRD.communicate()
		#print rrdGraph
	
		rrdGraph = "rrdtool graph graphs/%s_percentage.png --start %s --end %s " % (output, sTime, eTime)
		rrdGraph += "--vertical-label Usage%% --slope-mode --upper-limit 100 --lower-limit 0 "
		rrdGraph += "DEF:percent=disk.rrd:"+i+"PERCENT:%s CDEF:na-percent=percent,UN,0,percent,IF LINE:na-percent#%s:\"Disk Usage %%\" " % (typ, pColour)
		pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
		(oRRD, eRRD) = pRRD.communicate()
	#return oRRD

def main(args):
	#print 'ARGV      :', args
	if args and type(args) == tuple:
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs

	try:
		opts, remainder = getopt.gnu_getopt(args, "c:l:s:e:g:d:t:upw:", ["create=", "upperlimit=", "start=", "end=", "graph=", "diskname=", "time=", "update", "print", "wait="])
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	global endTime, startTime, graphName, step, delay, bUpdate, bPrinting, upperLimit, diskName
	#print 'OPTIONS   :', opts
	for o, a in opts:
		if o in ('-d', '--diskname'):
			diskName = a.split(',')
			print "diskname =",a
		elif o in ('-c', '--create'):
			if not a:
				create(1)
				print "created with step = 1"
			else:
				step = int(a)
				delay = step
				create(step)
				print "created with step = %d" % step
		elif o in ('-l', '--upperlimit'):
			upperLimit = a
		elif o in ('-s', '--start'):
			startTime = a
			print "start time =",a
		elif o in ('-e', '--end'):
			endTime = a
			print "end time =",a
		elif o in ('-g', '--graph'):
			graphName = a
			print "graphname =",a
		elif o in ('-t', '--time'):
			printTimes = a
		elif o in ('-u', '--update'):
			bUpdate = True
		elif o in ('-p', '--print'):
			bPrinting = True
		elif o in ('-w', '--wait'):
			delay = float(a)
	
	if bUpdate:
		try:
			disks = ','.join(diskName)
			while 1:
				diskInfo = disk.main("-d %s -upf" % disks)
				update(diskInfo[2], diskInfo[3], diskInfo[4])
				time.sleep(step)
				#print fetch("now-30","now")
		except KeyboardInterrupt:
    			print "interrupted"
	elif bPrinting:
		try:
			while 1:
				#print fetch("now-30","now")
				if "m" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], endTime +"-1minute", endTime, "m/DISK/disk")
				if "h" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], endTime +"-1h", endTime, "h/DISK/disk")
				if "d" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], endTime +"-1d", endTime, "d/DISK/disk")
				if "w" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], endTime +"-1w", endTime, "w/DISK/disk")
				if "M" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], endTime +"-1M", endTime, "M/DISK/disk")
				time.sleep(delay)
		except KeyboardInterrupt:
    			print "interrupted"
    					
    	else:
		try:
			while 1:
				diskInfo = disk.main("-d %s -upf" % disks)
				update(diskInfo[2], diskInfo[3], diskInfo[4])
				time.sleep(step)
				graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], startTime, endTime, "disk")
				time.sleep(delay)
		except KeyboardInterrupt:
    			print "interrupted"


if __name__ == "__main__":
	main("")
