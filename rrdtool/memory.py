import subprocess, getopt, sys

def getMemInfo():
	infoMEM = "free | grep  -E 'Mem' | tr -s ' ' | cut -d ' ' -f 2,3,4,6,7"				# get memory information
	pInfoMEM = subprocess.Popen(infoMEM, stdout = subprocess.PIPE, shell=True)
	(outputInfoMEM, errInfoMEM) = pInfoMEM.communicate()
	return map(int, outputInfoMEM.split())
	
def main(args):
	if args and type(args) == tuple:
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs													# if input in function it returns as shell input

	try:
		opts, args = getopt.getopt(args, "tubcfp", ["total", "used", "buffer", "cached", "free", "percentage"])		# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	totalMEM =	None
	usedMEM =	None
	freeMEM =	None
	percentage =	None

	outputInfoMEM = getMemInfo()
	output = []
	for o, a in opts:
		if o in ('-t', '--total'):								# -t returns as total memory
			totalMEM = outputInfoMEM[0]
			output.append(totalMEM)

		elif o in ("-u", "--used"):
			usedMEM = (outputInfoMEM[1]-outputInfoMEM[3]-outputInfoMEM[4])			# -u returns as used memory
			output.append(usedMEM)

		elif o in ("-b", "--buffer"):
			bufferMEM = outputInfoMEM[3]							# -b returns as buffers' memory
			output.append(bufferMEM)

		elif o in ("-c", "--cached"):
			cachedMEM = outputInfoMEM[4]							# -c returns as cached memory
			output.append(cachedMEM)

		elif o in ("-f", "--free"):								# -f returns as free memory
			usedMEM = (outputInfoMEM[1])
			freeMEM = outputInfoMEM[0] - usedMEM
			output.append(freeMEM)

		elif o in ("-p", "--percentage"):
			usedMEM = (outputInfoMEM[1]-outputInfoMEM[3]-outputInfoMEM[4])			# -p returns as memory usage percent
			totalMEM = float(outputInfoMEM[0])
			output.append(round(100.0*usedMEM/totalMEM,2))

		else:
			assert False, "unhandled option" 
	return output											#returns all of reply of inputs
	
if __name__ == "__main__":
    	print main("")
	#main("")
