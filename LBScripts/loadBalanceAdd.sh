#!/bin/bash

# Desc: Add iptable rules for load balancing. Add the entry for only new connections.
# Args: Every nth packet, Public Destination IP address, Public IP destination port, Private destination IP, Private destination port, namespace name

if [ $# -ne 6 ];
then
	echo "Illegal number of params"
	exit
fi

if [ $5 -ne 0 ];
then
	ip netns exec $6 iptables -t nat -I PREROUTING 1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $4:$5
else
	ip netns exec $6 iptables -t nat -I PREROUTING 1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $4
fi
