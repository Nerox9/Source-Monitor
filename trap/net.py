import subprocess, getopt, sys, time

def selectInterface(interface):
	
	interfaceList = getInterfaceList()
	#print interfaceList, type(interface), interface
	selectedInterface = []
	try:
		interface = interface.split(',')
	except:
		pass
	if type(interface) == list:
		#print "list!!!", interface
		try:
			interface = map(int,interface)
		except:
			pass
		for i in range(len(interface)):
			if type(interface[i]) == int:
				selectedInterface.append(interfaceList[interface[i]])
			elif type(interface[i]) == str:
				#print interface[i]
				if interface[i] in interfaceList:
					selectedInterface.append(interface[i])
		selectedInterface.sort(key=lambda (x): interfaceList.index(x))
		#print "Interfaces:",selectedInterface
		
	elif type(interface) == int:
		selectedInterface = [interfaceList[interface]]
		#print "Interface:",selectedInterface
	return selectedInterface
	
def getInterfaceList():
	net = "cat /proc/net/dev | tail -n +3 | cut -d ':' -f 1"
	pNet = subprocess.Popen(net, stdout = subprocess.PIPE, shell=True)
	(oNet, eNet) = pNet.communicate()
	return oNet.split()

def parseData(data):

	netData = data.split('\n')[:-1]
	data = [i.split() for i in netData]
	data = [[float(i[j])*8 if (j == 0) or ( j == 8) else float(i[j]) for j in (0,1,8,9)] for i in data]
	return data
	
def getInterfaceData(interface):
	grepInterface = '|'.join(interface)
	net = "grep -E \'%s\' /proc/net/dev | cut -d ':' -f 2" % grepInterface
	pNet = subprocess.Popen(net, stdout = subprocess.PIPE, shell=True)
	(oNet, eNet) = pNet.communicate()
	return oNet

def calculateDifferance(interface):
	oldData = getInterfaceData(interface)
	oldData = parseData(oldData)
	time.sleep(1)
	newData = getInterfaceData(interface)
	newData = parseData(newData)
	#print oldData
	#print newData
	
	changeData = []
	for i in range(len(newData)):
		changeData.append([t1-t0 for t0, t1 in zip(map(int,oldData[i]), map(int,newData[i]))])
	
	return changeData
	
def main(interface):
	if interface and type(interface) == tuple:		
		args = interface[0].split()
	elif interface:
		interface = interface.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not interface:
		interface = sysArgs
		
	try:
		opts, remainder = getopt.gnu_getopt(interface, "i:", ["interface="])
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
	for o, a in opts:
		#print o
		if o in ('-i', '--interface'):
			if a in ('l', 'list'):
				return getInterfaceList()
			else:
				try:
					a = int(a)
				except ValueError:
					pass
				interface = selectInterface(a)
	
							
	#print interface
	#netList = getInterfaceList()

	#print data
	return calculateDifferance(interface)
	
if __name__ == "__main__":
	print main("")

'''
import subprocess,time, threading, getopt, sys

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
	

def getInterfaceList():
	net = "cat /proc/net/dev | tail -n +3 | cut -d ':' -f 1"
	pNet = subprocess.Popen(net, stdout = subprocess.PIPE, shell=True)
	(oNet, eNet) = pNet.communicate()
	return oNet.split()

def selectInterface(interface):
	interfaceList = getInterfaceList()
	#print interfaceList, type(interface), interface
	selectedInterface = []
	try:
		interface = interface.split(',')
	except:
		pass
	if type(interface) == list:
		#print "list!!!", interface
		try:
			interface = map(int,interface)
		except:
			pass
		for i in range(len(interface)):
			if type(interface[i]) == int:
				selectedInterface.append(interfaceList[interface[i]])
			elif type(interface[i]) == str:
				print interface[i]
				if interface[i] in interfaceList:
					selectedInterface.append(interface[i])
		selectedInterface.sort(key=lambda (x): interfaceList.index(x))
		print "Interfaces:",selectedInterface
		
	elif type(interface) == int:
		selectedInterface = [interfaceList[interface]]
		print "Interface:",selectedInterface
	return selectedInterface


#def calculateDifferance():
#	global oldData, newData, changeData
#	oldData = newData
#	newData = getInterfaceData("eth2")
#	newData = map(int,(newData[0],newData[1],newData[8],newData[9]))
#	changeData = [t1-t0 for t0, t1 in zip(oldData, newData)]
	
		
def getInterfaceData():
	global data, oldData, oNet
	

	if oNet == None:
		print "onet None"
		return 0
	if inputSource == "proc":
		
	
		netData = oNet.split('\n')[:-1]
		#print netData
		data = [i.split() for i in netData]
		data = [[float(i[j])*8 if (j == 0) or ( j == 8) else float(i[j]) for j in (0,1,8,9)] for i in data]
		#for i in range(len(data)):
			#data = [(pData-pOldData) for pData,pOldData in zip(data[i],oldData[i])]
		#print data




	elif inputSource == "netlink":
		grepInterface = ','.join(interface)
		bmon = "bmon -i netlink -p %s -o format:quitafter=1"	% grepInterface # get stat values
		pbmon = subprocess.Popen(bmon, stdout = subprocess.PIPE, shell=True)
		(obmon, eCbmon) = pbmon.communicate()
		bmonData = obmon.split('>')[1].split('\n')[:-1]
		data = [map(int,bmonData[i].split()[1:]) for i in range(len(bmonData))]
	#if type(oldData[0]) != int:
		#print data[0][0] - oldData[0][0]
	#print [ int(data[0][i])-int(oldData[0][i]) for i in range(len(data))]




	elif inputSource == "ipstat":
		grepInterface = [i + ':' for i in interface]
		#print grepInterface
		grepInterface = '|'.join(grepInterface)
		#print grepInterface
		ip = "ip -s link | grep -E \'%s\' -A 5"	% grepInterface
		pIp = subprocess.Popen(ip, stdout = subprocess.PIPE, shell=True)
		(oIp, eIp) = pIp.communicate()

		print oIp
		oIp = [oIp.replace(i, interface[0]) for i in interface[1:]]
		oIp = oIp[0].split(interface[0])[2:]
		print oIp
		oIp = [i.split('\n')[1:] for i in oIp]
		print oIp
		#print [i.split('\n') for i in oIp[0]]
		#print oIp
			
		"""
		grepInterface = ','.join(interface)
		bmon = "bmon -i netlink -p %s -o ascii:quitafter=1"	% grepInterface # get stat values
		pbmon = subprocess.Popen(bmon, stdout = subprocess.PIPE, shell=True)
		(obmon, eCbmon) = pbmon.communicate()
		print obmon
		bmonData = obmon.split('>')[1].split('\n')[1:-1]
		data = [map(int,bmonData[i].split()[1:]) for i in range(len(bmonData))]
		print data
		#from bmon ascii table
		"""

def create(step):

	graphFile = "mkdir -p graphs/m/Net graphs/h/Net graphs/d/Net graphs/w/Net graphs/M/Net"
	pGraphFile = subprocess.Popen(graphFile, stdout = subprocess.PIPE, shell=True)
	(oGraphFile, eGraphFile) = pGraphFile.communicate()
	print "Directories are created"

	interfaceList = getInterfaceList()

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
	getInterfaceData()
	interfaceData = data
	#print interfaceData
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

	"""
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
	"""
def update(interval):
	global interface
	print "Update starting"
	try:
		global rrdUpdate, oNet
		updateString()

		t = intervalTimer(interval,pUpdate)		#start Timer
		t.start()
		while(1):
			#print fetch("now-30", "now")
			grepInterface = '|'.join(interface)
			net = "grep -E \'%s\' /proc/net/dev | cut -d ':' -f 2" % grepInterface
			pNet = subprocess.Popen(net, stdout = subprocess.PIPE, shell=True)
			(oNet, eNet) = pNet.communicate()
			#print oNet
			
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
		opts, remainder = getopt.gnu_getopt(args, "c:l:w:h:i:s:e:g:d:i:t:upa", ["create=", "upperlimit=", "width=", "height=", "interface=", "start=", "end=", "graph=", "delay=", "interval=", "time=", "update", "print", "apart"])
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
		elif o in ('-i', '--interface'):
			if a in ('l', 'list'):
				print getInterfaceList()
			else:
				try:
					a = int(a)
				except ValueError:
					pass
				interface = selectInterface(a)
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
'''


