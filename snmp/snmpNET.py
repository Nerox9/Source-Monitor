import threading
import subprocess, time, getopt,sys

trapOID = "iso.3.6.1.2.1.31.1.1.1.1"
timeOID = "iso.3.6.1.2.1.1.3.1"
netOID = "iso.3.6.1"

def main():
	try:
		opts, remainder = getopt.gnu_getopt(sys.argv[1:], "", [])
		#print remainder#[0].split()
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
	
	remainder = [i.strip() for i in remainder[0].replace('=',',').split(',')]
	
	try:
		trap = remainder[remainder.index(trapOID) + 1]
		print "Trap OID = ", trap
	except:
		print "trap OID not found"
		
	try:
		t = remainder[remainder.index(timeOID) + 1]
		print "Time = ", t, "real time =", time.time()
	except:
		print "time OID not found"
		
	try:
		netUsage = remainder[remainder.index(netOID) + 1]
	except:
		print "net OID not found"
	try:
		netUsage = netUsage.split(' ')
		netName = netUsage[0][2:-1].split('-')
		netUsage = netUsage[1][1:-2].split('_')
		netUsage = [i.replace('[','').replace(']','').split('-')for i in netUsage]
		print "Interfaces = ", netName, netUsage
	except:
		pass
	
	
if __name__ == "__main__":
	main()
