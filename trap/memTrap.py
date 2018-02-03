import subprocess, getopt, sys, threading, time
import memory


hostIP =	"localhost"
timeOID =	"iso.3.6.1.2.1.1.3.1"
memTrapOID =	"iso.3.6.1.4.1.2021.4.5.0"

memLimit =	0
bMEMOver =	False
timerMEM =	None
t = 		None

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


def checkMEM():
	global t
	memUsage = memory.main("-p")
	t = time.time()
	return memUsage
	
def sendTrap(trapOID, data):
	snmpMsg = "snmptrap -v 2c -c public " + hostIP + " \'\' " + trapOID + " " + timeOID + " s %s" % t + " iso.3.6.1 s \"%s\"" % data 
	pSNMP = subprocess.Popen(snmpMsg, stdout = subprocess.PIPE, shell=True)

def memLimitInt():
	global  memUsage, bMEMOver, timerMEM
	checkUsage = checkMEM()[0]
	if  checkUsage < memLimit:
			bMEMOver = False
		
def main(args):
	if args and type(args) == tuple:		
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs
		
		
	try:
		opts, remainder = getopt.gnu_getopt(args, "l:i:", ["limit=", "interval="])		# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
		
	global interval, memLimit, bMEMOver, timerMEM
	for o, a in opts:

		if o in ('-l', '--limit'):				# sets cpu limit
			try:
				memLimit = float(a)
			except ValueError:
				assert False, "Memory limit could not convert to float"

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
			print "while"	
			if not bMEMOver:
				memUsage = checkMEM()
				if timerMEM != None:
					timerMEM.cancel()
			
			if memUsage[0] >= memLimit and not bMEMOver:
				print "Memory Usage is over the limit"
				bMEMOver = True
				sendTrap(memTrapOID, [memUsage[0]])
				timerMEM = intervalTimer(interval - 0.2,memLimitInt)		#start Timer
				timerMEM.start()
			time.sleep(0.5)
			
	except KeyboardInterrupt:
		try:
			timerMEM.cancel()
		except:
			pass
		print "interrupted"
		sys.exit(0)
		
if __name__ == "__main__":
	print main("")	
