import subprocess, time, getopt, sys

intv = 1.0													# wait interval between samples of /proc/stat values

def getCpuInfo():												# returns CPU cores time values
	cpuStats = "grep cpu /proc/stat"									# get stat values
	pCpuStats = subprocess.Popen(cpuStats, stdout = subprocess.PIPE, shell=True)
	(oCpuStats, eCpuStats) = pCpuStats.communicate()

	rows = oCpuStats.replace("cpu", "").split('\n')[:-1]							#parse them
	columns = [filter(None,i.split(' ')[1:]) for i in rows]
	return columns

def core():													# returns total core number plus the cpu (8cores+1cpu)		
	cpuStats = "grep -n cpu /proc/stat | wc -l"
	pCpuStats = subprocess.Popen(cpuStats, stdout = subprocess.PIPE, shell=True)
	(oCpuStats, eCpuStats) = pCpuStats.communicate()
	return int(oCpuStats)

def getTimeDiff(list0, list1):											# returns time differences between lists
	return [(t1-t0) for t0, t1 in zip(list0, list1)] 

def deltaTime(interval):											# calculates time difference of each core and total cpu
	timeList0 = getCpuInfo()										# get first sample
	time.sleep(interval)											# wait for interval value
	timeList1 = getCpuInfo()										# get second sample

	thread = len(timeList0)											#thread count
	dtCpu = [getTimeDiff(map(int, timeList0[i]), map(int, timeList1[i])) for i in range(0,thread)]		#calculate time differences
	return dtCpu

def cpuLoad():													# returns percentage of usage
	global intv
	dt = list(deltaTime(intv))
	thread = len(dt)

	idle_time = [float(dt[i][3])+float(dt[i][4]) for i in range (0,thread)]		
	total_time = [sum(dt[i]) for i in range (0,thread)]
	try:													# idle and io wait time divided by total time for percentage
		load = [(1-(idle_time[i]/total_time[i])) for i in range (0,thread)]
	except ZeroDivisionError:
		load = [0.0 for i in range (0,thread)]
	return load

def main(args):
	#print args
	if args and type(args) == tuple:		
		args = args[0].split()
	elif args:
		args = args.split()
	sysArgs = sys.argv[1:]
	if sysArgs and not args:
		args = sysArgs											# if input in function it returns as shell input
	#print 'ARGV      :', args

	try:
		opts, remainder = getopt.gnu_getopt(args, "c:ai:", ["core=","all","interval="])			# parse arguments
	except getopt.GetoptError as err:
		print (str(err))
		sys.exit(2)
	
	#print 'OPTIONS   :', opts

	try:
		intv_index = [i for i, v in opts ].index('-i')							# if options has -i it changes interval
		global intv
		intv = float(opts[intv_index][1])
	except ValueError:
		pass
	
	usage = [i*100.0 for i in  cpuLoad()]									# calculate cpu usage percent

	#print 'Interval	:', intv
	#print 'REMAINING	:', remainder
	
	for o, a in opts:

		if o in ('-c', '--core'):									# -c returns usage of defined single core
			try:
				a = int(a)
				return round(usage[a],2)
			except (IndexError,ValueError):
				assert False, "out of core index"

		elif o in ('-a', '--all'):									# -a returns usage of all cores and total cpu
			return [round(i,2) for i in usage]

		elif o in ('-i', '-interval'):
			pass
		else:
			assert False, "unhandled option" 
		
	
if __name__ == "__main__":
	print str(main(""))[1:-1]
