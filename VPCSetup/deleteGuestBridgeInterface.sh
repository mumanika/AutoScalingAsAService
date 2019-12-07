#!/bin/bash

# Desc: Delete the veth pair between the VM/container and the subnet bridge
# Arguments: subnet namespace name, VM or conatiner name

if [ $# -ne 2 ];
then
	exit
fi

arg=$(echo ${1}'B')
brctl delif ${arg} ${arg}${2}
ip link set ${arg}${2} down
ip link del ${arg}${2}
