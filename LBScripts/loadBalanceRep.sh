#!/bin/bash

# Desc: Replace the rule in the load balancer table. This script is used, when one VM goes down, all the rule entries above that VM must be updated accordingly. That is, the 'every' part of rule should be reduced by 1.
# Args: Rule number, public destination IP, public port, private destination IP, private port, namespace name, total number of vms for the tenant.
# teh number of VMS for the tenant has the be the total number before deletion
if [ $# -ne 7 ]
then
	#echo "Illegal number of parameters"
	exit
fi



ruleToDel=$(($7-$1+1))
every=$(($7-1))
for (i=1;i<$ruleToDel;i++); do
	read ev dstip <<< $(ip netns exec $6 iptables -t nat -L PREROUTING $i | awk '{for (I=1;I<=NF;I++) if ($I == "every") {printf "%s %s", $(I+1), $(I+2) };}')
	IFS=':' read -ra prs <<< "$dstip"
	ipdst=$(echo "$prs[1]")
	portdst=$(echo "$prs[2]")	
	if [ $5 -ne 0 ];
	then
		ip netns exec $6 iptables -t nat -R PREROUTING $i -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $every --packet 0 -j DNAT --to-destination $ipdst:$portdst
	else
		ip netns exec $6 iptables -t nat -R PREROUTING $i -p tcp -d $2 --dport $3 -m state --state NEW -m statistic --mode nth --every $every --packet 0 -j DNAT --to-destination $ipdst
	fi
	every=$(($every-1))
done

ip netns exec $6 iptables -t nat -D PREROUTING $ruleToDel
