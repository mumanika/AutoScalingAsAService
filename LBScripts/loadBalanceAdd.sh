#!/bin/bash

# Desc: Add iptable rules for load balancing. Add the entry for only new connections. Run this on all Namespaces where the tenant needs loadbalancing. .
# Args: Every nth packet, IP address assigned to loopback, Public IP, Public IP destination port, Private destination IP of the guest VM/Destination IP of the public interface of the loadbalanced subnet, Private destination port, namespace name

if [ $# -ne 7 ];
then
	echo "Illegal number of params"
	exit
fi

if [ $6 -ne 0 ];
then
	ip netns exec $7 iptables -t nat -I PREROUTING 1 -p tcp -d $3 --dport $4 -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $5:$6
else
	ip netns exec $7 iptables -t nat -I PREROUTING 1 -p tcp -d $3 --dport $4 -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $5
fi

ip=$(echo $5 | cut -d '.' -f 1-3)

ip netns exec $7 iptables -t nat -I POSTROUTING 1 -p tcp -d $ip.0/24 -j SNAT --to-source $2
