#!/bin/bash

# Desc: Add iptable rules for load balancing. Add the entry for only new connections. Run this on all Namespaces where the tenant needs loadbalancing. .
# Args: Every nth packet, Publically exposed IP to base NS, Public IP destination port exposed to base NS, Private destination IP of the guest VM or container, Private guest VM or container destination port, namespace name of the subnet

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

