#!/bin/bash

# Desc: Replace the rule in the load balancer table. This script is used, when one VM goes down, all the rule entries above that VM must be updated accordingly. That is, the 'every' part of rule should be reduced by 1.
# Args: Rule number, public destination IP, public port, private destination IP, private port, namespace name.

if [ $# -ne 6 ]
then
	echo "Illegal number of parameters"
	exit
fi

a=$(($1-1))
if [ $5 -ne 0 ];
then
	ip netns exec $6 iptables -t nat -R PREROUTING $1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $a --packet 0 -j DNAT --to-destination $4:$5 
else
	ip netns exec $6 iptables -t nat -R PREROUTING $1 -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $a --packet 0 -j DNAT --to-destination $4
fi
