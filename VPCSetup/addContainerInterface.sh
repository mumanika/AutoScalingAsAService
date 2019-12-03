#!/bin/bash

# Desc: Attach the veth pair to the container 
# Arguments: subnet namespace name, Conatiner name, Container process ID

if [ $# -ne 3 ];
then
	exit
fi

arg=$(echo ${1}'B')
ip link set ${2}${arg} netns $3
ip netns exec ${3} ip link set ${2}${arg} up
