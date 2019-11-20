#!/bin/bash

# Desc: Add a new veth pair, one end to the L2 bridge and the other end to the default namespace. Attach the VM to this hanging end in the caller script.
# Arguments: namespace name, bridge name, VM name

if [ $# -ne 3 ];
then
	exit
fi


ip link add ${3}${2} type veth peer name ${2}${3}
ip link set ${2}${3} netns $1
ip link set ${3}${2} up
ip netns exec $1 ip link set ${2}${3} up
ip netns exec $1 brctl addif ${2} ${2}${3}
