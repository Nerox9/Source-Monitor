import subprocess, getopt, sys, threading, time
import disk


hostIP =	"localhost"
timeOID =	"iso.3.6.1.2.1.1.3.1"
diskTrapOID =	"iso.3.6.1.4.1.2021.9.1.3.1"

diskLimit =	0
bDISKOver =	False
timerDISK =	None
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


def checkDISK():
	global t
	diskUsage = disk.main("-tufp")
	t = time.time()
	return diskUsage
	
def sendTrap(trapOID, data):
	snmpMsg = "snmptrap -v 2c -c public " + hostIP + " \'\' " + trapOID + " " + timeOID + " s %s" % t + " iso.3.6.1 s \"%s\"" % data 
	pSNMP = subprocess.Popen(snmpMsg, stdout = subprocess.PIPE, shell=True)

def diskLimitInt():
	global  diskUsage, bDISKOver, timerDISK
	checkUsage = float(diskUsage[4])
	if  checkUsage < diskLimit:
			bDISKOver = False
		
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
		
		
	global interval, diskLimit, bDISKOver, timerDISK
	for o, a in opts:

		if o in ('-l', '--limit'):				# sets cpu limit
			try:
				diskLimit = float(a)
			except ValueError:
				assert False, "Disk limit could not convert to float"

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
			if not bDISKOver:
				diskUsage = checkDISK()
				print diskUsage[4]
				if timerDISK != None:
					timerDISK.cancel()
			
			if float(diskUsage[4][0]) >= diskLimit and not bDISKOver:
				print "Disk Usage is over the limit"
				bDISKOver = True
				sendTrap(diskTrapOID, [diskUsage])
				timerDISK = intervalTimer(interval - 0.2,diskLimitInt)		#start Timer
				timerDISK.start()
			time.sleep(0.5)
			
	except KeyboardInterrupt:
		try:
			timerDISK.cancel()
		except:
			pass
		print "interrupted"
		sys.exit(0)
		
if __name__ == "__main__":
	print main("")	
