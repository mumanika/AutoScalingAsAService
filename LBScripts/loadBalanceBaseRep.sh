#!/bin/bash

# Desc: Replace the rule in the load balancer table for the particular group. This script is used, when one subnet is deleted, all the rule entries above that subnet's must be updated accordingly. That is, the 'every' part of rule should be reduced by 1. Make sure to run this on both the sites to update the tables.
# Args: Rule number for the subnet within the group's chain, base namespace name, total number of subnets in the group, load balancing group name

if [ $# -ne 4 ]
then
	#echo "Illegal number of parameters"
	exit
fi



ruleToDel=$(($3-$1+1))
every=$(($3-1))
for (( i=1;i<$ruleToDel;i++ )); do
	read ev dstip <<< $(ip netns exec $2 iptables -t nat -L $4 $i | awk '{for (I=1;I<=NF;I++) if ($I == "every") {printf "%s %s", $(I+1), $(I+2) };}')
	IFS=':' read -ra prs <<< "$dstip"
	ipdst=$(echo "${prs[1]}")
	portdst=$(echo "${prs[2]}")
	#echo $prs[2] 	
	if [ $3 -ne 0 ];
	then
		ip netns exec $2 iptables -t nat -R $4 $i -p tcp -m state --state NEW -m statistic --mode nth --every $every --packet 0 -j DNAT --to-destination $ipdst:$portdst
	else
		ip netns exec $2 iptables -t nat -R $4 $i -p tcp -m state --state NEW -m statistic --mode nth --every $every --packet 0 -j DNAT --to-destination $ipdst
	fi
	every=$(($every-1))
done

ip netns exec $2 iptables -t nat -D $4 $ruleToDel
ip netns exec $2 iptables -t nat -Z $4

