#!/bin/bash

# Desc: Add iptable rules for load balancing for the particular LB group on the tenant base namespace. A group is made up of one or more subnet namespaces. (NOTE: make sure to add the route to the loopback interface here at the other site through the GRE tunnel) 
# Args: Every nth packet, Public IP, Public IP destination port, Private subnet IP exposed to base namespace, Private subnet destination port, namespace name, subnet namespace name

if [ $# -ne 7 ];
then
	echo "Illegal number of params"
	exit
fi

if [ $5 -ne 0 ];
then
	ip netns exec $6 iptables -I $7 1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $4:$5
else
	ip netns exec $6 iptables -I $7 1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $4
fi


