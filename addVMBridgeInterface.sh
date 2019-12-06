#!/bin/bash

# Desc: Add a new veth pair, one end to the L2 bridge and the other end to the default namespace. Attach the VM to this hanging end in the caller script.
# Arguments: subnet namespace name, VM name

if [ $# -ne 2 ];
then
	exit
fi

arg=$(echo ${1}'B')
ip link add ${arg}${2} type veth peer name ${2}${arg}
ip link set ${arg}${2} netns $1
ip link set ${2}${arg} up
ip netns exec $1 ip link set ${arg}${2} up
ip netns exec $1 brctl addif ${arg} ${arg}${2}
