import subprocess, getopt, sys, threading, time
import net


hostIP =	"localhost"
timeOID =	"iso.3.6.1.2.1.1.3.1"
netTrapOID =	"iso.3.6.1.2.1.31.1.1.1.1"

netLimit =	0
bNETOver =	False
timerNET =	None
t = 		None
interface =	""
limitType = 	0
interval =	1

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
		
	def join(self):
		self.thread.join()

	
def checkNET(interface):
	global t
	netUsage = net.main("-i %s" % interface)
	t = time.time()
	return netUsage
	
def sendTrap(trapOID, data):
	snmpMsg = "snmptrap -v 2c -c public " + hostIP + " \'\' " + trapOID + " " + timeOID + " s %s" % t + " iso.3.6.1 s \"%s\"" % data 
	pSNMP = subprocess.Popen(snmpMsg, stdout = subprocess.PIPE, shell=True)

def netLimitInt():
	global  netUsage, bNETOver, timerNET, interface, limitType
	checkUsage = checkNET(interface)[0][limitType]
	if  checkUsage < netLimit:
			bNETOver = False
	
def limitTypeEnum(limitTypeName):
		if limitTypeName == "RXByte":
			return 0
		elif limitTypeName == "TXByte":
			return 2
		elif limitTypeName == "RXPacket":
			return 1
		elif limitTypeName == "TXPacket":
			return 3
		else:
			assert False, "Invalid limit type"
			
def main(args):
	if args and type(args) == tuple:		
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs
		
		
	try:
		opts, remainder = getopt.gnu_getopt(args, "l:t:i:f:", ["limit=", "type=", "interval=", "interface="])		# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
		
	global interval, netLimit, bNETOver, timerNET, interface
	for o, a in opts:

		if o in ('-l', '--limit'):				# sets cpu limit
			try:
				global netLimit
				netLimit = float(a)
			except ValueError:
				assert False, "Disk limit could not convert to float"

		elif o in ('-i', '--interval'):				# sets interval
			try:
				global interval
				interval = float(a)
			except ValueError:
				assert False, "Interval could not convert to float"
			
		elif o in ('-t', '--type'):				# sets interval
			global limitType
			limitType = limitTypeEnum(a)
		
		elif o in ('-f', '--interface'):
			global interface
			interface = a
			
		else:
			assert False, "unhandled option" 
	
	try:		
		while 1:	
			#print "while"	
			if not bNETOver:
				netUsage = checkNET(interface)
				print netUsage
				if timerNET != None:
					timerNET.cancel()	
			
				
			if netUsage[0][limitType] >= netLimit and not bNETOver:
				print "Network Usage is over the limit"
				bNETOver = True
				sendTrap(netTrapOID, [netUsage[0][limitType]])
				timerNET = intervalTimer(interval - 0.2,netLimitInt)		#start Timer
				timerNET.start()
			time.sleep(0.5)
			
	except KeyboardInterrupt:
		try:
			timerNET.cancel()
		except:
			pass
		print "interrupted"
		sys.exit(0)
		
if __name__ == "__main__":
	print main("")	
