# Source-Monitor
RRDTool based Source Monitoring

## Requirements
	subprocess
	getopt
	sys
	time
	threading
	rrdtool
	
	
## Folders
	rrdtool	= rddtool database contains existing code for collecting graphical and source data.
	bash 	= Code containing bash commands prompted by the snmptrapd.conf file. Runs python "* Trap.py" files in the snmp folder.
	snmp	= Used to parse the data received by Trap and print it to the terminal.
	
## Source Data Collection Scripts

### cpu.py
	It returns as a percentage of the options specified by reading the data of the "stat" file through the "/ proc" folder. It has 3 options, "-c", "-a" and "-i";
	    "-c" option returns the usage percentage of "cpu core" in the corresponding argument,
	    "-a" option returns the usage percentages of all "cpu" and all individual "cpu cores" (Format: (% cpu_all,% cpu0,% cpu1,% cpu2,% cpu3,% cpu4,% cpu5,% cpu6 ,% cpu7]),
	    "-i" option assigns the corresponding argument as interval in terms of "float". (default = 1.0 seconds)
		
	When determining the percentage of data, it takes the second sample after sampling the time data in "/proc/stat" and then takes the second sample and determines the time differences and calculates the time spent on "idle" and "io-wait" by dividing it by all the time spent on the content. In the tests, "import (python code)", "subprocess", "mpstat" and "psutil" were compared in terms of time spent among themselves and performed similarly. "Import cpu" 0.250 seconds, "subprocess" 0.272 seconds, "mpstat" 0.255 seconds (returned with different/erroneous results than others), and "psutil" 0.253 seconds with the least delayed results. (Tests python "timeit" function with 10 million repetitions)
		
	Basically, 6 functions are specified in the code content, except that one is "main", the others are explained below:
		getCpuInfo():				Reads "/proc/stat" file and extracts raw data and returns "tuple"
		core():						Reads file "/proc/stat" and returns line count - cpu core count + 1--
		getTimeDiff(list0, list1):	Takes the difference of two examples for each input list and returns this data as "tuple")
		deltaTime(interval): 		Returns the time difference of two lists
		cpuLoad():					Rates the Idle and IO wait times to all elapsed time and subtract from 1, returning "float" for each core
	
#### Examples
	python cpu.py -c 5 -i 2
		Output; "0.5"
		
	python cpu.py -a -i 3
		Output; "[0.71, 1.36, 0.66, 1.32, 0.67, 0.99, 0.0, 1.33, 0.0]"
		
	cpu.main("-a -i 5")

			
### memory.py
	Using the "free" command, it interprets the RAM data and returns, depending on the option. It has 6 options as "-t", "-u", "-b", "-c", "-f" and "-p";
		"-t" option returns the total disk in kB,
		"-u" option returns the RAM used in kB, The "-b" option returns the "buffered" RAM in kbps,
		"-c" option returns the "cached" RAM in kbps,
		"-f" option returns the idle RAM in kbps,
		"-p" option returns the percentage of free RAM..
			
	Only the "free" command interprets the output and returns the result as a list according to the option input order, comparing the data or the part used with the "free - (cached + buffered)" function to the whole RAM.
	
#### Examples
	python memory.py -t
		Output; "[16323620]"
		
	python memory.py -tuf"
		Output; "[16323620, 3783764, 6465584]
		
	python memory.py -ucfbtp
		Output; "[3783192, 5787864, 6441528, 311036, 16323620, 23.18]"
		
	memory.main("-tubcfp")
	
	
	
	
	
### disk.py
	Using the "df" command, it interprets the disk data and returns depending on the option. It has 6 options as "-d", "-t", "-u", "-f", "-p" and "-m"; 
		"-d" option returns the disk name, (default = sda),
		"-t" option returns the total disk in 1k blocks,
		"-u" option returns the used disk in 1k blocks,
		"-f" option returns the idle disk in 1k blocks,
		"-p" option returns the idle disk as a percentage,
		"-m" option returns the "mount" address.
			
	Only the "df" command interprets its output and returns the result as a "tuple" in the order the options are specified.
		
#### Examples
	python disk.py -t
		Output; "[['/dev/sda1'], [944898452], [], [], [], []]"
		
	python disk.py -d none -t
		Output; "[['none', 'none', 'none', 'none'], [4, 5120, 8161808, 102400], [], [], [], []]"
		
	python disk.py -d none -ufmt
		Output; "[['none', 'none', 'none', 'none'], [4, 5120, 8161808, 102400], [0, 0, 354524, 80], [4, 5120, 7807284, 102320], [], ['/sys/fs/cgroup', '/run/lock', '/run/shm', '/run/user']]"
		
	disk.main("-d none -ufmt")
			
			
		
			
			
### net.py
	It returns according to the "interface" determined by reading the "dev" file data through the "/ proc / net" folder. It has only one option as "-i";
		"-i" option assigns the corresponding argument as "interface" in terms of "string", "integer" or "string" is valid as input and must be separated by ',' for multiple entries. If the argument is given as "l" or "list", it returns the "interface" list.
		
	It interprets the data as kB and package in "/proc/net/dev". Each list in "tuple" returns "[received_data, received_package, sent_data, sent_package]" respectively. Only "string", "integer" format only "string" returns.
		
	Basically, 6 functions are specified in the code content, except that one is "main", the others are explained below:
		selectInterface(interface):		The "interface" given as input is parsed provided that it is separated as commas and returns their names according to their order in the system
		getInterfaceList():				Returns the "interface" list in the system
		parseData(data):				Interprets the read data as "RxByte, RxPacket, TxByte, TxPacket"
		getInterfaceData(interface):	reads "/proc/net/dev"
			
			
#### Examples

    python net.py -i eth2
    	Output; "[[3724130297056.0, 309892689.0, 310073815000.0, 51933323.0]]"
    	
    python net.py -i list"
    	Output; "['wlan2', 'lo', 'eth2', 'vmnet1', 'vmnet2', 'vmnet8']"
    	
    python net.py -i eth2,lo
    	Output; "[[7655229009400.0, 32584949.0, 7655229009400.0, 32584949.0], [3724130297536.0, 309892690.0, 310073821816.0, 51933327.0]]" (sırasıyla; [[lo],[eth2]])
    	
    python net.py -i 2,1
    	Output; "[[7655229019792.0, 32584957.0, 7655229019792.0, 32584957.0], [3724130454184.0, 309892759.0, 310074052424.0, 51933404.0]]"
    
    net.main("-i eth2,lo")
		
## RRDTool Data Monitoring Scripts
	
### rrdCPU.py
	The "cpu.py" code writes the data it receives on the database at the interval determined arbitrarily and produces graphical output in minute, hourly, weekly and monthly slices. According to the options specified under the "graphs" folder, it saves "png" graphics for all CPU named "CPU" and for all cores, "CPU" + core number. It has the following 10 options;
		"-c" option assigns the corresponding argument, "cpu.rrd" the number of steps,
		"-l" option sets the corresponding argument, "cpu.rrd" the upper time limit,
		"-s" option determines the corresponding argument, the start time,
		"-e" option determines the related argument, the end time,
		"-i" option determines the corresponding argument, the interval in the code "cpu.py",
		"-m" option specifies the relevant argument, the kernel to be monitored (update and graphics generation) (all cores for 'a' or "all"),
		"-g" option determines the corresponding argument, the name of the chart,
		"-t" option determines the relevant argument, the graph creation time (minute, hourly, weekly, ...),
		"-u" option specifies the corresponding argument, the kernel to be updated (all kernels for 'a' or "all"), The "-p" option generates the graphics.
		
	Basically, 6 functions are specified in the code content, except that one is "main", the others are explained below:
	create(step): creates the database named "cpu.rrd" at a specified time and step interval, creates "/graphs" and the folders below it
	fetch(sTime, eTime): Prints data in the specified range
	update(dataSource, time, value): Uploads instant time and data to database
	graph(core, typ, color, sTime, eTime, output): Writes graphic output to the ./graphs/ folder at specified time intervals
	cpuGet(): Read CPU usage percentage data -commented-
		
#### Examples
	python rrdCPU.py -c 1 -u a			(step interval = 1, updated in all database "cpu.rrd")
	
	python rrdCPU.py -t md -p			('m' = minute and 'd' = generates daily charts)
		
### rrdMem.py
	It writes the data it receives on the "memory.py" code to the database and generates graphic output in minute, hourly, weekly and monthly slices. Under the "graphs" folder, it saves the usage data in kB and two "png" graphs as the percentage usage. It has the following 9 options;
		"-c" option assigns the corresponding argument, the number of steps "mem.rrd",
		"-l" option sets the corresponding argument, "mem.rrd" the upper time limit,
		"-s" option determines the corresponding argument, the start time,
		"-e" option determines the related argument, the end time,
		"-g" option determines the corresponding argument, the name of the chart,
		"-d" option determines the corresponding argument, the delay in the cycle the graphic prints (default = 1 second),
		"-t" option determines the relevant argument, the graph creation time (minute, hourly, weekly, ...),
		"-u" option activates the existing loop flag for update, The "-p" option activates the existing loop flag for graphics generation.
		
	Basically, 5 functions are determined in the code content, except that one is "main", the others are explained below:
		create(step):															creates the database "mem.rrd" at a specified time and step interval, creates "/graphs" and the folders below it
		fetch(sTime,eTime):														Prints data in the specified range, default = "now" / "now-60"
		update(dataSource,time,value):											Uploads instant time and data to database
		graph(typ, uColour, bColour, cColour, pColour, sTime, eTime, output):	Writes graphic output to the ./graphs/ folder at specified time intervals
		
#### Examples
	python rrdMem.py -c 1 -u			(step interval = 1, updated in database "mem.rrd")
	
	python rrdMem.py -t md -p			('m' = minute and 'd' = generates daily charts)
			
			
			
### rrdDisk.py
		The "disk.py" code writes the data it receives on the database and produces graphical output in minute, hourly, weekly and monthly slices. Under the "graphs" folder, it saves usage data in 1k blocks and two "png" graphs as percentage usage. It has the following 10 options;
			"-c" option assigns the corresponding argument, "disk.rrd" the number of steps,
			"-l" option sets the corresponding argument, "disk.rrd" the upper time limit,
			"-s" option determines the corresponding argument, the start time,
			"-e" option determines the related argument, the end time,
			"-g" option determines the corresponding argument, the name of the chart,
			"-d" option specifies the corresponding argument, the disk name in "memory.py" to be updated and graphed,
			"-t" option determines the corresponding argument, the delay in the cycle the graphic prints (default = 1 second)
			"-u" option activates the existing loop flag for update, The "-p" option activates the existing loop flag for graphic generation,
			"-w" option activates the corresponding argument, the loop flag that exists for graphics generation.
			
		Basically, 5 functions are specified in the code content, except that one is "main", the others are explained below:
			create(step):													creates the database named "disk.rrd" at the specified time and step interval, creates "/graphs" and the folders below it
			fetch(sTime,eTime):												Prints data in the specified range, default = "now" / "now-60"
			update(dataSource,time,value):									Uploads instant time and data to database
			graph(typ, uColour, aColour, pColour, sTime, eTime, output):	Writes graphic output to the ./graphs/ folder at specified time intervals
			
#### Examples
	python rrdDisk.py -c 1 -u			(step interval = 1, updated in database "disk.rrd")
	
	python rrdDisk.py -t md -p			('m' = minutes and 'd' = generates daily charts)

			
### rrdNet.py
		The "net.py" code writes the data it receives into the database and produces graphical output in minute, hourly, weekly and monthly slices. Under the "graphs" folder, it saves two "png" graphics in bytes and packages according to the "interfaces" specified. It has the following 14 options;
			"-c" option assigns the corresponding argument, "net.rrd" the number of steps,
			"-l" option sets the corresponding argument, "net.rrd" the upper time limit,
			"-w" option determines the relevant argument, the width in the graphics output,
			"-h" option determines the relevant argument, the height in the graphics output,
			"-f" option determines the relevant argument, the "interfaces" in the update and graphic outputs (different "interfaces" must be separated by commas),
			"-i" option determines the corresponding argument, the interval of the "timer thread",
			"-s" option determines the corresponding argument, the start time,
			"-e" option determines the related argument, the end time, The "-g" option determines the corresponding argument, the name of the chart,
			"-d" option specifies the corresponding argument, the disk name in "memory.py" to be updated and graphed,
			"-t" option determines the corresponding argument, the delay in the cycle the graphic prints (default = 1 second),
			"-u" option is available for update
			
		Basically 7 functions are determined in the code content, except that one is "main", the others are explained below:
			create(step):											creates the database "net.rrd" at a specified time and step interval, creates "/graphs" and the folders below it
			fetch(sTime,eTime):										Displays data in the specified range, default = "now" / "now-60"
			pUpdate():												Uploads instant time and data to database
			updateString():											Prepares the pre-entry that will not change during the update
			update(interval):										Starts the "Timer thread" and enters a 1000-second idle loop
			graph(pInterface, typ, colour, sTime, eTime, output):	Writes graphic output to the ./graphs/ folder at specified time intervals
			
		Timer Thread Class:
			It consists of 4 functions: "__init__", "handleInternalfunction", "start" and "cancel". It calls the "__init__" start "thread" according to the specified "handler" function and again starts a new thread connected to "handleInternalfunction". The "handleInternalfunction" continues to call itself as a "recursive" procedure until the "cancel" function is called.
			
#### Examples
	python rrdNet.py -c 1 -u -f lo,eth2			(step interval = 1, in database "net.rrd", "eth2" and "lo" are updated)
	
	python rrdNet.py -t md -p -f eth2,lo		('m' = minute and 'd' = creates charts of "eth2" and "lo" in daily time frames)
  
## SNMP Trap Scripts
### cpu.py
  See "Source Data Collection Scripts/cpu.py"
### memory.py
  See "Source Data Collection Scripts/memory.py"
### disk.py
  See "Source Data Collection Scripts/disk.py"
### net.py
  The only difference from "Source Data Collection Scripts / net.py" is that the "calculateDifferance (interface)" function and the return in "main" depend on this function. Basically, after taking two different samples like in "cpu.py" with one second interval difference, it takes the differences of the related samples. 
### netConnection.py
	Returns the number of links of the selected type using the "netstat" and "ss" commands, depending on the user selection. It has the following 3 options;
		"-o" option adds the corresponding argument, the options in the query "netstat" or "ss" directly (!) to the command "string" (default = "tan4"),
		"-i" option determines the corresponding argument, whether "netstat" or "ss" commands will be used (default = "netstat"),
		"-s" option makes the corresponding argument that the command returns links in the specified state (default = "", counts all states).
		
	Basically 3 functions are determined in the code content, except that one of them is "main", the others are explained below:
		netstatOpt(options, state):		Adds the specified option and state to the "netstat" command line and returns the result
		ssOpt(options, state):			Adds the specified option and state to the "ss" command line and returns the result
		
#### Examples:
		python netConnection.py									(source = "netstat", state = all, option = "tan4")
		Output; "14"
		python netConnection.py -i ss -s ESTABLISHED -o tan6	(source = "ss", state = "ESTABLISHED", option = "tan6")
		Output; "0"
### cpuTrap.py
### memTrap.py
### diskTrap.py
### netConTrap.py

## SNMP Trapd Scripts and Configuration Files
### /etc/snmp/snmptrapd.conf
### Bash Scripts
### Trap Deamon Scripts
