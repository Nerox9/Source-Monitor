import subprocess, time, getopt,sys

trapOID = "iso.3.6.1.4.1.2021.11.9.0"
timeOID = "iso.3.6.1.2.1.1.3.1"
cpuOID = "iso.3.6.1"

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
		cpuUsage = remainder[remainder.index(cpuOID) + 1]
	except:
		print "cpu OID not found"
		
	try:
		cpuUsage = cpuUsage.split(':')
		#print cpuUsage
		print "Core = ", cpuUsage[0][1:]
		print "CPU Usage = ", cpuUsage[1][1:-2]
	except:
		pass
	
if __name__ == "__main__":
	main()
