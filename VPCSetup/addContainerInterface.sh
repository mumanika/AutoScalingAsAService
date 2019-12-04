#!/bin/bash

# Desc: Attach the veth pair to the container 
# Arguments: subnet namespace name, Conatiner name, Container process ID

if [ $# -ne 3 ];
then
	exit
fi

arg=$(echo ${1}'B')
ip link set dev ${2}${arg} netns ${3}
docker container exec --privileged ${2} ip link set dev ${2}${arg} up
docker container exec --privileged ${2} dhclient ${2}${arg}
docker container exec --privileged ${2} ip route del default
read x <<< $(docker container exec ${2} ip -4 addr show ${2}${arg} | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
ip=$(echo $x | cut -d '.' -f 1-3)
docker container exec --privileged ${2} ip route add default via ${ip}'.1' 

