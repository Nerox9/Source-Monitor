import subprocess, sys, getopt

state =		""
options =	"tan4"
dataFrom =	"netstat"

def netstatOpt(options, state):
	if state == "":
		netstatStr = "netstat -%s | wc -l" % (options)
	else:
		netstatStr = "netstat -%s | grep %s | wc -l" % (options, state)
	pNetstat = subprocess.Popen(netstatStr, stdout = subprocess.PIPE, shell=True)
	(oNetstat, eNetstat) = pNetstat.communicate()
	return oNetstat
	
def ssOpt(options, state):
	if state == "":
		ssStr = "ss -%s | wc -l" % (options)
	else:
		ssStr = "ss -%s | grep %s | wc -l" % (options, state)
	pSS = subprocess.Popen(ssStr, stdout = subprocess.PIPE, shell=True)
	(oSS, eSS) = pSS.communicate()
	return oSS
	
def main(args):
	if args and type(args) == tuple:		
		args = args[0].split()
	elif args and type(args) == list:
		pass
	elif args:
		args = args.split()
		
	global dataFrom, options
	try:
		opts, remainder = getopt.gnu_getopt(args, "o:i:s:", ["option=", "input=", "state="])		# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
	#print opts
	for o, a in opts:
			
		if o in ('-o', '--option'):				# sets interval
			global options
			options = a
		
		elif o in ('-i', '--input'):
			global dataFrom
			dataFrom = a
		
		elif o in ('-s', '--state'):
			global state
			state = a
			
		else:
			assert False, "unhandled option" 
		
	
	if dataFrom == "netstat" or "n":
		return netstatOpt(options, state)
	elif dataFrom == "ss":
		return ssOpt(options, state)
	else:
		assert False, "Invalid input name"
		
		
		
if __name__ == "__main__":
	print main(sys.argv[1:])
