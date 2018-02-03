import subprocess, getopt, sys

def main(args):
	if args and type(args) == tuple:
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs													# if input in function it returns as shell input

	try:
		opts, args = getopt.getopt(args, "d:tfpum", ["diskname=", "total", "used", "free", "percentage", "mount"])	# parse arguments
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	diskName =	"sda"
	'''
	minorPart =	[]
	majorPart =	[]
	'''
	fileSystem =	[]
	totalDisk =	[]
	usedDisk =	[]
	freeDisk =	[]
	percentage =	[]
	mountedOn =	[]

	output =	[]
	
	bTotal = False
	bUsed = False
	bFree = False
	bPerc = False
	bMount = False
	
	for o, a in opts:
		if o in ('-d', '--diskname'):											# change disk name
			diskName = a

		elif o in ("-t", "--total"):
			bTotal = True												# returns total disk blocks
			
		elif o in ("-u", "--used"):
			bUsed = True												# returns used disk blocks
		
		elif o in ("-f", "--free"):
			bFree = True												# returns free disk blocks

		elif o in ("-p", "--percentage"):										# returns percentage of disk usage
			bPerc = True
			
		elif o in ("-m", "--mount"):
			bMount = True												# returns mount directory of disk
			
		else:
			assert False, "unhandled option" 
	
	diskName = diskName.split(',')
	diskName = '|'.join(diskName)		
	#infoDisk = "grep -E \'%s\' /proc/diskstats | tr -s ' ' | cut -d ' ' -f 1-3,5- "	% diskName			# get disk information
	infoDisk = "df | grep -E \'%s\' | tr -s ' '"	% diskName
	pInfoDisk = subprocess.Popen(infoDisk, stdout = subprocess.PIPE, shell=True)
	(outputInfoDisk, errInfoDisk) = pInfoDisk.communicate()
	
	outputInfoDisk = outputInfoDisk.split('\n')[:-1]
	

	#df
	for i in outputInfoDisk:
		line = filter(None, i.split(' '))
		fileSystem.append(line[0])
		if bTotal:
			totalDisk.append(int(line[1]))
		if bUsed:
			usedDisk.append(int(line[2]))
		if bFree:
			freeDisk.append(int(line[3]))
		if bPerc:
			percentage.append(float(line[4][:-1])) 
		if bMount:
			mountedOn.append(line[5]) 
			
		
			
	output = [fileSystem] + [totalDisk] + [usedDisk] + [freeDisk] + [percentage] + [mountedOn]
	return output
	
	'''
	#proc
	for i in outputInfoDisk:
		line = filter(None, i.split(' '))
		print line
		majorPart.append(line[0])
		minorPart.append(line[1])
		#nReadIssued.
	#majorPart = outputInfoDisk[0][0]
	#minorPart = [outputInfoDisk[i][3] for i in len(outputInfoDisk)]
	
	#print outputInfoDisk,majorPart,minorPart
	return output	#returns all of reply of inputs
	'''
	
	
if __name__ == "__main__":
    	print main("")
	#main("")
