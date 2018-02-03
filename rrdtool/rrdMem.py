import memory,subprocess,time,getopt,sys

upperLimit = "5184000"
step = 1
graphName = "graph"
startTime = "now-60"
endTime = "now"
limit = 0
delay = 1
printTimes = 'm'
bUpdate = False
bPrinting = False
cPalette = ("109919", "1C2F84", "E5E011", "FF0000")

def create(step):			# creates a mem.rrd file as defined step
	graphFile = "mkdir -p graphs/m/MEM graphs/h/MEM graphs/d/MEM graphs/w/MEM graphs/M/MEM"
	pGraphFile = subprocess.Popen(graphFile, stdout = subprocess.PIPE, shell=True)
	(oGraphFile, eGraphFile) = pGraphFile.communicate()
	print "Files are created"
	currentTime = time.time()
	rrdCreate = "rrdtool create mem.rrd --step %d " % (step)
	rrdCreate += "DS:MEM:GAUGE:%d:U:U " % (2 * step)	# the memory percent data source has heartbeat as 2 step size
	rrdCreate +=   "DS:USED:GAUGE:%d:U:U " % (2 * step)		# the used data source has heartbeat as 2 step size
	rrdCreate +=   "DS:BUFFER:GAUGE:%d:U:U " % (2 * step)		# the buffers data source has heartbeat as 2 step size
	rrdCreate +=   "DS:CACHED:GAUGE:%d:U:U " % (2 * step)		# the cached memory data source has heartbeat as 2 step size
	rrdCreate += "RRA:AVERAGE:0:1:%s " % (upperLimit)
	pRRD = subprocess.Popen(rrdCreate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def fetch(sTime, eTime):	# fetches the data from sTime to eTime
	rrdFetch = "rrdtool fetch mem.rrd AVERAGE --start %s --end %s " % (sTime, eTime)
	pRRD = subprocess.Popen(rrdFetch, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def update(time, perc, used, buffers, cached):	# updates values from input percentage and used memory with timestamp
	rrdUpdate = "rrdtool update mem.rrd -t MEM:USED:BUFFER:CACHED %d:%f:%f:%f:%f" % (time, perc, used, buffers, cached)
	pRRD = subprocess.Popen(rrdUpdate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def graph(typ, uColour, bColour, cColour, pColour, sTime, eTime, output):	# prints graphs
	global limit
	rrdGraph = "rrdtool graph graphs/%s_usage.png --start %s --end %s " % (output, sTime, eTime)
	rrdGraph += " --vertical-label \"Used Memory\" --upper-limit %s --lower-limit 0 --slope-mode --base=1024 " % (limit)
	rrdGraph += "DEF:used=mem.rrd:USED:%s CDEF:na-used=used,UN,0,used,IF AREA:na-used#%s:\"Used Memory\" " % (typ, uColour)
	rrdGraph += "DEF:buffer=mem.rrd:BUFFER:%s CDEF:na-buffer=buffer,UN,0,buffer,IF STACK:na-buffer#%s:\"Buffers Memory\" " % (typ, bColour)
	rrdGraph += "DEF:cached=mem.rrd:CACHED:%s CDEF:na-cached=cached,UN,0,cached,IF STACK:na-cached#%s:\"Cached Memory\" " % (typ, cColour)
	rrdGraph += "HRULE:%d#FF0000:\"Maximum Available Memory\"" % (limit)
	pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	#print rrdGraph
	rrdGraph = "rrdtool graph graphs/%s_percentage.png --start %s --end %s " % (output, sTime, eTime)
	rrdGraph += "--vertical-label Usage%% --slope-mode --upper-limit 100 --lower-limit 0  DEF:mem=mem.rrd:MEM:%s CDEF:non-ans=mem,UN,0,mem,IF LINE1:non-ans#%s:\"Memory Usage %%\" " % (typ, pColour)
	pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

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
		opts, remainder = getopt.gnu_getopt(args, "c:l:s:e:g:d:t:up", ["create=", "upperlimit=", "start=", "end=", "graph=", "delay=", "time=", "update", "print"])
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	global endTime, startTime, graphName, step, delay, bUpdate, bPrinting, upperLimit
	#print 'OPTIONS   :', opts
	for o, a in opts:
		if o in ('-c', '--create'):
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
		elif o in ('-d', '--delay'):
			delay = float(a)
		elif o in ('-t', '--time'):
			printTimes = a
		elif o in ('-u', '--update'):
			bUpdate = True
		elif o in ('-p', '--print'):
			bPrinting = True

	global limit
	limit = memory.main("-t")[0]
	
	if bUpdate:
		try:
			while 1:
				t = time.time()
				mem = memory.main("-p -u -b -c")
				update(t,mem[0],mem[1], mem[2], mem[3])
				print t,mem
				time.sleep(step)
		except KeyboardInterrupt:
    			print "interrupted"
	elif bPrinting:
		try:
			while 1:
				#print fetch("now-30","now")
				if "m" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], cPalette[3], endTime +"-1minute", endTime, "m/MEM/mem")
				if "h" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], cPalette[3], endTime +"-1h", endTime, "h/MEM/mem")
				if "d" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], cPalette[3], endTime +"-1d", endTime, "d/MEM/mem")
				if "w" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], cPalette[3], endTime +"-1w", endTime, "w/MEM/mem")
				if "M" in printTimes:
					graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], cPalette[3], endTime +"-1M", endTime, "M/MEM/mem")
				time.sleep(delay)
		except KeyboardInterrupt:
    			print "interrupted"
	else:
		try:
			while 1:
				t = time.time()
				mem = memory.main("-p -u -b -c")
				update(t,mem[0],mem[1], mem[2], mem[3])
				print t,mem
				graph("AVERAGE", cPalette[0], cPalette[1], cPalette[2], cPalette[3], startTime, endTime, "m/MEM/mem")
				time.sleep(delay)
		except KeyboardInterrupt:
    			print "interrupted"

if __name__ == "__main__":
	main("")
