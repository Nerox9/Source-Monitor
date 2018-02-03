import subprocess, getopt, sys, threading, time
import netConnection


hostIP =	"localhost"
timeOID =	"iso.3.6.1.2.1.1.3.1"
conTrapOID =	"iso.3.6.1.2.1.31.1.1.1.2"

conLimit =	0
bCONOver =	False
timerCON =	None
t = 		None
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

	
def checkConnection():
	global t
	connection = netConnection.main("-i netstat")
	t = time.time()
	try:
		return int(connection)
	except:
		assert False, "Failed to convert connection number"
	
def sendTrap(trapOID, data):
	snmpMsg = "snmptrap -v 2c -c public " + hostIP + " \'\' " + trapOID + " " + timeOID + " s %s" % t + " iso.3.6.1 s \"%s\"" % data 
	pSNMP = subprocess.Popen(snmpMsg, stdout = subprocess.PIPE, shell=True)

def conLimitInt():
	global  bCONOver, timerCON
	connection = checkConnection()
	if  connection < conLimit:
			bCONOver = False

			
def main(args):
	if args and type(args) == tuple:		
		args = args[0].split()
	elif args and type(args) == list:
		pass
	elif args:
		args = args.split()
		
		
	try:
		opts, remainder = getopt.gnu_getopt(args, "l:i:", ["limit=", "interval="])		# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
		
	global interval, conLimit, bCONOver, timerCON
	for o, a in opts:

		if o in ('-l', '--limit'):				# sets cpu limit
			try:
				global conLimit
				conLimit = int(a)
			except ValueError:
				assert False, "Connection limit could not convert to integer"

		elif o in ('-i', '--interval'):				# sets interval
			try:
				global interval
				interval = float(a)
			except ValueError:
				assert False, "Interval could not convert to float"
			
		else:
			assert False, "unhandled option" 
	
	try:		
		while 1:	
			#print "while"	
			if not bCONOver:
				connection = checkConnection()
				print connection
				if timerCON != None:
					timerCON.cancel()	
			
				
			if connection >= conLimit and not bCONOver:
				print "Connection is over the limit"
				bCONOver = True
				sendTrap(conTrapOID, connection)
				timerCON = intervalTimer(interval - 0.2,conLimitInt)		#start Timer
				timerCON.start()
			time.sleep(0.5)
			
	except KeyboardInterrupt:
		try:
			timerCON.cancel()
		except:
			pass
		print "interrupted"
		sys.exit(0)
		
if __name__ == "__main__":
	print main(sys.argv[1:])	
