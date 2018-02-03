import subprocess, getopt, sys, threading, time
import cpu


hostIP =	"localhost"
timeOID =	"iso.3.6.1.2.1.1.3.1"
cpuTrapOID =	"iso.3.6.1.4.1.2021.11.9.0"

cpuLimit =	0
bCPUOver =	False
timerCPU = 	None
t = 		None
waitTime =	0.5
interval =	1
cpuCore =	0
cpuIntv = 	0.1	#bigger is more precise

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


def checkCPU():
	global t, cpuIntv
	cpuUsage = cpu.main("-a -i %f" % cpuIntv)
	t = time.time()
	return cpuUsage
	
def sendTrap(trapOID, data):
	snmpMsg = "snmptrap -v 2c -c public " + hostIP + " \'\' " + trapOID + " " + timeOID + " s %s" % t + " iso.3.6.1 s \"%s:%s\"" % ((cpuCore-1) if cpuCore > 0 else "all", data)
	pSNMP = subprocess.Popen(snmpMsg, stdout = subprocess.PIPE, shell=True)

def cpuLimitInt():
	global  cpuUsage, bCPUOver, timerCPU, cpuCore
	checkUsage = checkCPU()[cpuCore]
	print checkUsage
	if  checkUsage < cpuLimit:
			bCPUOver = False	
		
def main(args):
	if args and type(args) == tuple:		
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs
		
		
	try:
		opts, remainder = getopt.gnu_getopt(args, "l:i:c:", ["limit=", "interval=", "core="])		# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
		
	global interval, cpuLimit, bCPUOver, timerCPU, waitTime, cpuCore, cpuIntv
	for o, a in opts:

		if o in ('-l', '--limit'):								# sets cpu limit
			try:
				cpuLimit = float(a)
			except ValueError:
				assert False, "CPU limit could not convert to float"

		elif o in ('-i', '--interval'):								# sets interval
			try:
				global interval
				interval = float(a)
			except ValueError:
				assert False, "Interval could not convert to float"
		
		elif o in ('-c', '--core'):
			global 	cpuCore	
			try:										# sets cpu core		
				if a == "all" or a == "a":
					cpuCore = 0
				else:
					cpuCore = int(a)+1
			except:
				assert False, "CPU core selection is false"
		else:
			assert False, "unhandled option" 
	
	try:	
		while 1:	
			#print "while"	
			if not bCPUOver:
				cpuUsage = checkCPU()
				if timerCPU != None:
					timerCPU.cancel()
				#print cpuUsage
				print cpuUsage[cpuCore]
		
			if cpuUsage[cpuCore] >= cpuLimit and not bCPUOver:
				print "CPU Usage is over the limit"
				bCPUOver = True
				sendTrap(cpuTrapOID, [cpuUsage[cpuCore]])
				timerCPU = intervalTimer(interval - cpuIntv,cpuLimitInt)		#start Timer
				timerCPU.start()
			time.sleep(waitTime)
			
	except KeyboardInterrupt:
		try:
			timerCPU.cancel()
		except:
			pass
		print "interrupted"
		sys.exit(0)
		
if __name__ == "__main__":
	print main("")	
