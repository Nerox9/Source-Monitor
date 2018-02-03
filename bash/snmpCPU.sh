#!/bin/sh

 read host
 read ip
 vars=
 
 while read oid val
 do
   if [ "$vars" = "" ]
   then
     vars="$oid = $val"
   else
     vars="$vars, $oid = $val"
   fi
 done
 
python /home/droid/Desktop/rrd/snmp/snmpCPU.py "$vars"
