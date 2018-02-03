import subprocess,time, threading, getopt, sys, net

oldData = None

inputSource = "proc"
upperLimit = "5184000"
width = 400
height = 100
interval = 1
data = [[0,0,0,0]]
oNet = None
interface = None
rrdUpdateString = None
rrdUpdate = None
endTime = "now" 
startTime = "now-60"
graphName = "net" 
step = 1
delay = 1
bUpdate = False
bPrinting = False
bAparted = False
cPalette = ("109919", "1C2F84", "E5E511", "FF0000")
	
class intervalTimer():	#define Timer

   def __init__(self,t,handleFunction):
      self.t=t
      self.handleFunction = handleFunction
      self.thread = threading.Timer(self.t,self.handleInternalfunction)

   def handleInternalfunction(self):
      self.handleFunction()
      self.thread = threading.Timer(self.t,self.handleInternalfunction)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
	
	
def create(step):

	graphFile = "mkdir -p graphs/m/Net graphs/h/Net graphs/d/Net graphs/w/Net graphs/M/Net"
	pGraphFile = subprocess.Popen(graphFile, stdout = subprocess.PIPE, shell=True)
	(oGraphFile, eGraphFile) = pGraphFile.communicate()
	print "Directories are created"

	interfaceList = net.getInterfaceList()
	#print interfaceList
	rrdCreate = "rrdtool create net.rrd --step %d " %(step)
	for i in range(len(interfaceList)):
		rrdCreate +=   "DS:%sRxByte:COUNTER:%d:U:U " % (interfaceList[i], 2 * step)
		rrdCreate +=   "DS:%sRxPack:COUNTER:%d:U:U " % (interfaceList[i], 2 * step)
		rrdCreate +=   "DS:%sTxByte:COUNTER:%d:U:U " % (interfaceList[i], 2 * step)
		rrdCreate +=   "DS:%sTxPack:COUNTER:%d:U:U " % (interfaceList[i], 2 * step)
	rrdCreate += "RRA:AVERAGE:0:1:%s " % (upperLimit)
	#print rrdCreate
	pRRD = subprocess.Popen(rrdCreate, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	print "RRD file is created", oRRD
	return oRRD

def fetch(sTime, eTime):	# fetches the data from sTime to eTime
	rrdFetch = "rrdtool fetch net.rrd AVERAGE --start %s --end %s" % (sTime, eTime)
	pRRD = subprocess.Popen(rrdFetch, stdout = subprocess.PIPE, shell=True)
	(oRRD, eRRD) = pRRD.communicate()
	return oRRD

def pUpdate():	# updates values from input percentage and used memory with timestamp
	
	global rrdUpdateString, rrdUpdate
	
	interfaceData = net.getInterfaceData(interface)
	interfaceData = net.parseData(interfaceData)
	uTime = time.time()
	
	rrdUpdate = rrdUpdateString
	
	rrdUpdate += " %d" % (uTime)
	if interfaceData:
		for i in range(len(interfaceData)):
			if type(interfaceData[0]) == list:
				for j in range(len(interfaceData[i])):
					rrdUpdate += ":%d" % (interfaceData[i][j]) 
			else:
				rrdUpdate += ":%d" % (interfaceData[i])
	
	pRRD = subprocess.Popen(rrdUpdate, stdout = subprocess.PIPE, shell=True)
	#print rrdUpdate
	#print uTime, interfaceData
	#print fetch("now-10","now")

def updateString():
	global rrdUpdateString, interface
	interfaceList = interface
	rrdUpdateString = "rrdtool update net.rrd -t "
	#print interfaceList
	
	for i in range(len(interfaceList)):

		rrdUpdateString += "%sRxByte:" % (interfaceList[i])
		rrdUpdateString += "%sRxPack:" % (interfaceList[i])
		rrdUpdateString += "%sTxByte:" % (interfaceList[i])
		
		if i != len(interfaceList)-1:
			rrdUpdateString += "%sTxPack:" % (interfaceList[i])
		else:
			rrdUpdateString += "%sTxPack" % (interfaceList[i])
	#print rrdUpdateString
	'''
	if type(interfaceList) == list:
		print  "list"
		rrdUpdateString += "%s" % (interfaceList[0]) 

		for i in range(1, len(interfaceList)):
			rrdUpdateString += ":%s" % (interfaceList[i]) 
	else:
		rrdUpdateString += "%sRxByte:" % (interfaceList)
		rrdUpdateString += "%sRxPack:" % (interfaceList)
		rrdUpdateString += "%sTxByte:" % (interfaceList)
		rrdUpdateString += "%sTxPack" % (interfaceList)
	'''
def update(interval):
	global interface
	print "Update starting"
	try:
		global rrdUpdate, oNet
		updateString()
		
		t = intervalTimer(interval,pUpdate)		#start Timer
		t.start()
		while 1:
			time.sleep(1000)
			pass	
			
	except KeyboardInterrupt:
		t.cancel()
		print "Interrupted"
		sys.exit(2)
		#print fetch("now-60","now")

def graph(pInterface, typ, colour, sTime, eTime, output):
	if bAparted:
		
		rrdGraph = "rrdtool graph graphs/%s_RXbyte.png --start %s --end %s " % (output, sTime, eTime)
		rrdGraph += " --vertical-label \"RX Data (Bps)\" --upper-limit 5000 --lower-limit 0 -w %d -h %d " % (width, height)
		rrdGraph += "DEF:"+pInterface+"rxb=net.rrd:"+pInterface+"RxByte:%s " % (typ)
		rrdGraph += "CDEF:na-"+pInterface+"rxb="+pInterface+"rxb,UN,0,"+pInterface+"rxb,IF "
		rrdGraph += "AREA:na-"+pInterface+"rxb#%s:\"%s-RX Bytes\" " % (colour[1], pInterface)
		pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
		(oRRD, eRRD) = pRRD.communicate()

		rrdGraph = "rrdtool graph graphs/%s_TXbyte.png --start %s --end %s " % (output, sTime, eTime)
		rrdGraph += " --vertical-label \"TX Data (Bps)\" --upper-limit 1000 --lower-limit 0 -w %d -h %d " % (width, height)
		rrdGraph += "DEF:"+pInterface+"txb=net.rrd:"+pInterface+"TxByte:%s " % (typ)
		rrdGraph += "CDEF:na-"+pInterface+"txb="+pInterface+"txb,UN,0,"+pInterface+"txb,IF "
		rrdGraph += "AREA:na-"+pInterface+"txb#%s:\"%s-TX Bytes\" " % (colour[0], pInterface)
		pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
		(oRRD, eRRD) = pRRD.communicate()
	else:
		rrdGraph = "rrdtool graph graphs/%s_byte.png --start %s --end %s " % (output, sTime, eTime)
		rrdGraph += " --vertical-label \"RX Data (Bps)\" --right-axis 1:0 --right-axis-label \"TX Data (Bps)\"  --upper-limit 5000 --lower-limit 0 -w %d -h %d --base 1024 " % (width, height)
		rrdGraph += "DEF:"+pInterface+"rxb=net.rrd:"+pInterface+"RxByte:%s " % (typ)
		rrdGraph += "DEF:"+pInterface+"txb=net.rrd:"+pInterface+"TxByte:%s " % (typ)
		rrdGraph += "CDEF:na-"+pInterface+"rxb="+pInterface+"rxb,UN,0,"+pInterface+"rxb,IF "
		rrdGraph += "CDEF:na-"+pInterface+"txb="+pInterface+"txb,UN,0,"+pInterface+"txb,IF "
		rrdGraph += "CDEF:tx-rx=na-"+pInterface+"txb,na-"+pInterface+"rxb,- "
		rrdGraph += "CDEF:rx-tx=na-"+pInterface+"rxb,na-"+pInterface+"txb,- "
		rrdGraph += "CDEF:intersection=" + "na-"+pInterface+"rxb," + "na-"+pInterface+"txb" + ",GE," + "na-"+pInterface+"txb,0,IF "
		rrdGraph += "CDEF:intersection2=" + "na-"+pInterface+"txb," + "na-"+pInterface+"rxb" + ",GT," + "na-"+pInterface+"rxb,0,IF "
		rrdGraph += "CDEF:oversection=" + "na-"+pInterface+"rxb," + "na-"+pInterface+"txb" + ",GE," +"na-"+pInterface+"rxb," + "na-"+pInterface+"txb," + "-,0,IF "
		rrdGraph += "CDEF:oversection2=" + "na-"+pInterface+"txb," + "na-"+pInterface+"rxb" + ",GT," + "na-"+pInterface+"txb," + "na-"+pInterface+"rxb," + "-,0,IF "
		#rrdGraph += "AREA:na-"+pInterface+"txb#%s:\"%s-TX Bytes\" " % (colour[1], pInterface)
		#rrdGraph += "AREA:na-"+pInterface+"rxb#%s:\"%s-RX Bytes\" " % (colour[0], pInterface)
		rrdGraph += "AREA:intersection#%s " % ("16846F")
		rrdGraph += "STACK:oversection#%s:\"%s-RX Bytes\" " % (colour[1], pInterface)
		rrdGraph += "AREA:intersection2#%s " % ("16646F")
		rrdGraph += "STACK:oversection2#%s:\"%s-TX Bytes\" " % (colour[0], pInterface)
		#rrdGraph += "AREA:na-"+pInterface+"rxb#%s:\"%s-RX Bytes\" " % (colour[0], pInterface)
		#rrdGraph += "AREA:na-"+pInterface+"txb#%s:\"%s-TX Bytes\" " % (colour[1], pInterface)
		#print rrdGraph
		pRRD = subprocess.Popen(rrdGraph, stdout = subprocess.PIPE, shell=True)
		(oRRD, eRRD) = pRRD.communicate()

	rrdGraph = "rrdtool graph graphs/%s_packet.png --start %s --end %s " % (output, sTime, eTime)
	rrdGraph += "--vertical-label \"RX Packets (pps)\" --right-axis 1:0 --right-axis-label \"TX Packets (Bps)\"  --upper-limit 10 --lower-limit 0 -w %d -h %d " % (width, height)
	rrdGraph += "DEF:"+pInterface+"rxp=net.rrd:"+pInterface+"RxPack:%s "% (typ)
	rrdGraph += "DEF:"+pInterface+"txp=net.rrd:"+pInterface+"TxPack:%s "% (typ)
	rrdGraph += "CDEF:na-"+pInterface+"rxp="+pInterface+"rxp,UN,0,"+pInterface+"rxp,IF "
	rrdGraph += "CDEF:na-"+pInterface+"txp="+pInterface+"txp,UN,0,"+pInterface+"txp,IF "
	rrdGraph += "CDEF:intersection=" + "na-"+pInterface+"rxp," + "na-"+pInterface+"txp" + ",GE," + "na-"+pInterface+"txp,0,IF "
	rrdGraph += "CDEF:intersection2=" + "na-"+pInterface+"txp," + "na-"+pInterface+"rxp" + ",GT," + "na-"+pInterface+"rxp,0,IF "
	rrdGraph += "CDEF:oversection=" + "na-"+pInterface+"rxp," + "na-"+pInterface+"txp" + ",GE," +"na-"+pInterface+"rxp," + "na-"+pInterface+"txp," + "-,0,IF "
	rrdGraph += "CDEF:oversection2=" + "na-"+pInterface+"txp," + "na-"+pInterface+"rxp" + ",GT," + "na-"+pInterface+"txp," + "na-"+pInterface+"rxp," + "-,0,IF "
	#rrdGraph += "AREA:na-"+pInterface+"txp#%s:\"%s-TX Packets\" " % (colour[3], pInterface)
	#rrdGraph += "AREA:na-"+pInterface+"rxp#%s:\"%s-RX Packets\" " % (colour[2], pInterface)
	rrdGraph += "AREA:intersection#%s " % ("E1BD06") #"F2D809"
	rrdGraph += "STACK:oversection#%s:\"%s-RX Bytes\" " % (colour[3], pInterface)
	rrdGraph += "AREA:intersection2#%s " % ("E16D06")
	rrdGraph += "STACK:oversection2#%s:\"%s-TX Bytes\" " % (colour[2], pInterface)
	#print rrdGraph
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
		opts, remainder = getopt.gnu_getopt(args, "c:l:w:h:f:s:e:g:d:i:t:upa", ["create=", "upperlimit=", "width=", "height=", "interface=", "start=", "end=", "graph=", "delay=", "interval=", "time=", "update", "print", "apart"])
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	global endTime, startTime, graphName, step, delay, bUpdate, bPrinting, interface, width, height, bAparted, upperLimit
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
		elif o in ('-w', '--width'):
			width = a
		elif o in ('-h', '--height'):
			height = a
		elif o in ('-f', '--interface'):
			if a in ('l', 'list'):
				print net.getInterfaceList()
			else:
				try:
					a = int(a)
				except ValueError:
					pass
				interface = net.selectInterface(a)
				#print interface
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
		elif o in ('-a', '--apart'):
			bAparted = True

	if bUpdate:
			update(1)
	elif bPrinting:
		try:
			while 1:
				#print fetch("now-60","now")
				if "m" in printTimes:
					if type(interface) == list:
						for i in range(len(interface)):
							graph(interface[i],"AVERAGE", cPalette, endTime+"-60", endTime, "m/Net/%s" % (interface[i]))
					else:
						graph(interface,"AVERAGE", cPalette, endTime+"-60", endTime, "m/Net/%s" % (interface))
				if "h" in printTimes:
					if type(interface) == list:
						for i in range(len(interface)):
							graph(interface[i],"AVERAGE", cPalette, endTime+"-1h", endTime, "h/Net/%s" % (interface[i]))
					else:
						graph(interface,"AVERAGE", cPalette, endTime+"-1h", endTime, "h/Net/%s" % (interface))	
				if "d" in printTimes:
					if type(interface) == list:
						for i in range(len(interface)):
							graph(interface[i],"AVERAGE", cPalette, endTime+"-1d", endTime, "d/Net/%s" % (interface[i]))
					else:
						graph(interface,"AVERAGE", cPalette, endTime+"-1d", endTime, "d/Net/%s" % (interface))	
				if "w" in printTimes:
					if type(interface) == list:
						for i in range(len(interface)):
							graph(interface[i],"AVERAGE", cPalette, endTime+"-1w", endTime, "w/Net/%s" % (interface[i]))
					else:
						graph(interface,"AVERAGE", cPalette, endTime+"-1w", endTime, "w/Net/%s" % (interface))	
				if "M" in printTimes:
					if type(interface) == list:
						for i in range(len(interface)):
							graph(interface[i],"AVERAGE", cPalette, endTime+"-1M", endTime, "M/Net/%s" % (interface[i]))
					else:
						graph(interface,"AVERAGE", cPalette, endTime+"-1M", endTime, "M/Net/%s" % (interface))	
				time.sleep(delay)
		except KeyboardInterrupt:
    			print "interrupted"

	
if __name__ == "__main__":
	main("")



