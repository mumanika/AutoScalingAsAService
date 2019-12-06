#!/bin/bash

#Desc: Destroy the subnet and remove the corresponding hostsfile and kill the running dnsmasq process
# Args: subnet namespace name

if [ $# -ne 1 ];
then
	exit
fi

br=$(echo ${1}'B')
ip netns exec $1 ip link set dev ${br} down
ip netns exec $1 ip link set dev NS${br} down
ip netns exec $1 ip link set dev ${br}NS down

a=($(ip netns exec $1 brctl show ${br} | awk 'NR==2, NR==$NR { print $NF }'))

for i in "${a[@]}"
do
        ip netns exec $1 ip link set dev $i down
        ip netns exec $1 ip link del dev $i
done


ip netns exec $1 brctl delbr ${br}
ip netns exec $1 ip link del ${br}NS
ip netns exec $1 ip link set dev ${1}Bse down
ip netns exec $1 ip link del dev ${1}Bse
lookStr="--interface=NS${br}"
a=$(ps aux | awk -v var=${lookStr} '{for (I=1;I<=NF;I++) if ($I == var) {printf "%s", $(2) };}')
kill ${a}
ip netns exec $1 rm -rf /etc/netns/${1}
ip netns exec $1 rm -f /etc/${1}.hostsfile
ip netns del ${1}


