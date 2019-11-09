#!/bin/bash

if [ $# -ne 5 ];
then
	echo "Illegal number of params"
	exit
fi

if [ $1 -eq 0 ];
then
	iptables -t nat -I PREROUTING 1 -p tcp -d $2 --dport $3 -j DNAT --to-destination $4:$5
	exit
fi

iptables -t nat -I PREROUTING 1 -p tcp -d $2 --dport $3 -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $4:$5
