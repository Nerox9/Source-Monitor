import cpu,subprocess,time,getopt,sys

upperLimit = "5184000"
thread = 'a'
graphName = "graph"
cpuInterval = 1
startTime = "now-60"
endTime = "now"
bMonitor = False
bUpdate = False
bPrinting = False

def create(step):
	global cpuInterval, upperLimit
	graphFile = "mkdir -p graphs/m/CPU graphs/h/CPU graphs/d/CPU graphs/w/CPU graphs/M/CPU"
	pGraphFile = subprocess.Popen(graphFile, stdout = subprocess.PIPE, shell=True)
	(oGraphFile, eGraphFile) = pGraphFile.communicate()
	print "Files are created"
	
	rrdCreate = "rrdtool create cpu.rrd --step %d DS:CPU:GAUGE:%d:U:U " %(step, 2 * step)
	for i in range(0, cpu.core()-1):
		rrdCreate +=   "DS:CPU%d:GAUGE:%d:U:U " % (i, 2 * step)
	rrdCreate += "RRA:AVERAGE:0:1:%s " % (upperLimit)
	#RRA:AVERAGE:0.25:15:288 RRA:MIN:0.25:15:288 RRA:MAX:0.25:15:288 RRA:AVERAGE:0.25:60:504 RRA:MIN:0.25:180:744 RRA:MIN:0.25:180:744 RRA:MAX:0.25:180:744 RRA:AVERAGE:0.25:4320:366 RRA:MIN:0.25:4320:366 RRA:MAX:0.25:4320:366
	pRRD = subprocess.Popen(rrdCreate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def fetch(sTime,eTime):
	rrdFetch = "rrdtool fetch cpu.rrd AVERAGE --start %d --end %d" % (sTime,eTime)
	pRRD = subprocess.Popen(rrdFetch, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def update(dataSource,time,value):
	if dataSource == "a":
		rrdUpdate = "rrdtool update cpu.rrd -t CPU:"
		for i in range(0,len(value)-2):
			rrdUpdate += "CPU%d:" % i
		rrdUpdate += "CPU%d " % (i+1)
		rrdUpdate += "%d" % (time) 
		for i in range(0,len(value)):
			rrdUpdate += ":%f" % value[i]
	else:
		rrdUpdate = "rrdtool update cpu.rrd -t CPU%d %d:%f" % (dataSource,time,value)
	pRRD = subprocess.Popen(rrdUpdate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def graph(core,typ,colour,sTime,eTime,output):
	if core == "a":
		colourSet = ("00FF00", "0000FF", "1F6F6F", "B86F33", "299429", "761C6B", "AA5929", "FFFC19")

		rrdGraph = "rrdtool graph graphs/%s.png --start %s --end %s --vertical-label Usage%% --upper-limit 100 --lower-limit 0 --slope-mode DEF:cpu=cpu.rrd:CPU:%s CDEF:non-ans=cpu,UN,0,cpu,IF " % (output, sTime, eTime, typ)

		for i in range(0, cpu.core()-1):
	 		rrdGraph += "DEF:cpu%d=cpu.rrd:CPU%d:%s " % (i, i, typ)
			rrdGraph += "CDEF:non-ans%d=cpu%d,UN,0,cpu%d,IF " % (i, i, i)
			rrdGraph += "LINE1:non-ans%d#%s:\"cpu%d\" " % (i, colourSet[i], i)
		rrdGraph += "STACK:non-ans#%s:\"Total CPU\"" % colour
		#print rrdGraph

	else:
		rrdGraph = "rrdtool graph graphs/%s.png --start %s --end %s --vertical-label Usage%% --upper-limit 100 --lower-limit 0 --slope-mode DEF:cpu=cpu.rrd:CPU%s:%s CDEF:non-ans=cpu,UN,0,cpu,IF LINE1:non-ans#%s:\"CPU%s Usage\"" % (output,sTime,eTime,core,typ,colour, core)
	pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD
'''
def cpuGet():
	cpu = "python cpu.py -c 0 -i 1"
	pCPU = subprocess.Popen(cpu, stdout = subprocess.PIPE, shell=True)
	(oCPU, eCPU) = pCPU.communicate()
	print float(oCPU)
	return 0.0
'''
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
		opts, remainder = getopt.gnu_getopt(args, "c:l:s:e:i:m:g:t:u:p", ["create=", "upperlimit=", "start=", "end=", "interval=", "monitor=", "graph=","time=","update=","print"])
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	global endTime, startTime, thread, graphName, cpuInterval, bMonitor, bUpdate, bPrinting, upperLimit
	
	
	try:
		limit_index = [i for i, v in opts ].index('-l')							# if options has -i it changes interval
		upperLimit = int(opts[limit_index][1])
	except ValueError:
		pass
		
	#print 'OPTIONS   :', opts
	for o, a in opts:
		if o in ('-c', '--create'):
			if not a:
				create(1)
				print "created with step = 1"
			else:
				a = int(a)
				create(a)
				print "created with step = %d" % a
		elif o in ('-l', '--upperlimit'):
			pass
		elif o in ('-s', '--start'):
			startTime = a
			print "start time =",a
		elif o in ('-e', '--end'):
			endTime = a
			print "end time =",a
		elif o in ('-g', '--graph'):
			graphName = a
			print "graphname =",a
		elif o in ('-i', '--interval'):
			cpuInterval = a
			print "cpuInterval =",a
		elif o in ('-m', '--monitor'):
			thread = a
			bMonitor = True
		elif o in ('-t', '--time'):
			printTimes = a
		elif o in ('-u', '--update'):
			thread = a
			bUpdate = True
		elif o in ('-p', '--print'):
			bPrinting = True
		else:
			assert False, "unhandled option" 
	

	#print 'REMAINING	:', remainder
	if bMonitor:
		
		if thread == ('a' or "all"):
			print "all threads monitoring"
			try:
				while 1:
					t = time.time()
					cpuU = cpu.main("-a -i %f" % float(cpuInterval))
					update("a",t,cpuU)
					print t,cpuU
					
					if "m" in printTimes:
						graph("","AVERAGE","FF0000","now-1minute",endTime,"m/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1minute",endTime,"m/CPU/CPU%s" % i)
					if "h" in printTimes:
						graph("","AVERAGE","FF0000","now-1h",endTime,"h/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1h",endTime,"h/CPU/CPU%s" % i)
					if "d" in printTimes:
						graph("","AVERAGE","FF0000","now-1d",endTime,"d/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1d",endTime,"d/CPU/CPU%s" % i)
					if "w" in printTimes:
						graph("","AVERAGE","FF0000","now-1w",endTime,"w/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1w",endTime,"w/CPU/CPU%s" % i)
					if "M" in printTimes:
						graph("","AVERAGE","FF0000","now-1M",endTime,"m/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1M",endTime,"M/CPU/CPU%s" % i)
			except KeyboardInterrupt:
				print "interrupted"
					
		else:
			thread = int(thread)
			cpuInterval = float(cpuInterval)
			print "%dth thread monitoring in interval %.2f s" % (thread, float(cpuInterval))
			try:
				while 1:
					t = time.time()
					cpuU = cpu.main("-c %d -i %f" % (thread, cpuInterval))
					print thread,t,cpuU
					update(thread,t,cpuU)
					graph("%s" % (thread),"AVERAGE","FF0000",startTime,endTime,"%s" % (graphName))
			except KeyboardInterrupt:
    			 print "interrupted"


	elif bUpdate:
		if thread == ('a' or "all"):
			print "all threads updating"
			try:
				while 1:
					t = time.time()
					cpuU = cpu.main("-a -i %f" % float(cpuInterval))
					update("a",t,cpuU)
					print t,cpuU
			except KeyboardInterrupt:
				print "interrupted"

		else:
			thread = int(thread)
			cpuInterval = float(cpuInterval)
			print "%dth thread updating in interval %.2f s" % (thread, float(cpuInterval))
			try:
				while 1:
					t = time.time()
					cpuU = cpu.main("-c %d -i %f" % (thread, cpuInterval))
					update(thread,t,cpuU)
					print thread,t,cpuU
			except KeyboardInterrupt:
    			 print "interrupted"

	elif bPrinting:
			print "all threads printing"
			try:
				while 1:
					if "m" in printTimes:
						graph("","AVERAGE","FF0000","now-1minute",endTime,"m/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1minute",endTime,"m/CPU/CPU%s" % i)
					if "h" in printTimes:
						graph("","AVERAGE","FF0000","now-1h",endTime,"h/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1h",endTime,"h/CPU/CPU%s" % i)
					if "d" in printTimes:
						graph("","AVERAGE","FF0000","now-1d",endTime,"d/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1d",endTime,"d/CPU/CPU%s" % i)
					if "w" in printTimes:
						graph("","AVERAGE","FF0000","now-1w",endTime,"w/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1w",endTime,"w/CPU/CPU%s" % i)
					if "M" in printTimes:
						graph("","AVERAGE","FF0000","now-1M",endTime,"m/CPU/CPU")
						for i in range(0, cpu.core()-1):
							graph("%s" % i,"AVERAGE","FF0000","now-1M",endTime,"M/CPU/CPU%s" % i)
		
			except KeyboardInterrupt:
				print "interrupted"

	 	#print fetch(t-20,t+1)
	

if __name__ == "__main__":
	main("")
