#!/bin/bash

if [ $# -ne 5 ]
then
	echo "Illegal number of parameters"
	exit
fi

a=$(($1-1))
if [ $5 -ne 0 ];
then
	iptables -t nat -R PREROUTING $1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $a --packet 0 -j DNAT --to-destination $4:$5 
else
	iptables -t nat -R PREROUTING $1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $a --packet 0 -j DNAT --to-destination $4
fi
