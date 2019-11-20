#!/bin/bash

#Desc: Destroy the subnet and remove the corresponding hostsfile and kill the running dnsmasq process
# Args: namespace name, bridge name of the subnet and subnet name

if [ $# -ne 3 ];
then
	exit
fi

ip netns exec $1 ip link set dev ${2} down
ip netns exec $1 ip link set dev NS${2} down
ip netns exec $1 ip link set dev ${2}NS down

a=($(brctl show $2 | awk 'NR==2, NR==$NR { print $NF }'))

for i in "${a[@]}"
do
        ip netns exec $1 ip link set dev $i down
        ip netns exec $1 ip link del dev $i
done


ip netns exec $1 brctl delbr ${2}
ip netns exec $1 ip link del ${2}NS
lookStr="--interface=NS${2}"
a=$(ps aux | awk -v var=${lookStr} '{for (I=1;I<=NF;I++) if ($I == var) {printf "%s", $(2) };}')
kill ${a}
ip netns exec $1 rm -f /etc/netns/${1}/${3}.hostsfile
ip netns exec $1 rm -f /etc/${3}.hostsfile 


