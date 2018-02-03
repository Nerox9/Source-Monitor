import subprocess, time, getopt,sys

trapOID =	"iso.3.6.1.4.1.2021.11.9.0"
timeOID =	"iso.3.6.1.2.1.1.3.1"
conTrapOID =	"iso.3.6.1.2.1.31.1.1.1.2"

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
		connection = remainder[remainder.index(conTrapOID) + 1]
	except:
		print "connection OID not found"
		
	try:
		print "Connection = ", connection
	except:
		pass
	
if __name__ == "__main__":
	main()
