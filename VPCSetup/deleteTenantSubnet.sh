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
ip link set dev ${br}NS down

a=($(brctl show ${br} | awk 'NR==2, NR==$NR { print $NF }'))

for i in "${a[@]}"
do
        ip link set dev $i down
        ip link del dev $i
done


brctl delbr ${br}
ip netns exec $1 ip link del NS${br}
ip netns exec $1 ip link set dev ${1}Bse down
ip netns exec $1 ip link del dev ${1}Bse
lookStr="--interface=NS${br}"
a=$(ps aux | awk -v var=${lookStr} '{for (I=1;I<=NF;I++) if ($I == var) {printf "%s", $(2) };}')
kill ${a}
ip netns exec $1 rm -rf /etc/netns/${1}
ip netns exec $1 rm -f /etc/${1}.hostsfile
ip netns del ${1}


