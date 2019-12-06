#!/bin/bash

#This script deletes the chain

#inputs: The group name, base namespace name

if [ $# -ne 2 ];
then
	exit
fi

ip netns exec $2 iptables -t nat -F $1


ruleNo=$(ip netns exec $2 iptables -t nat -L PREROUTING --line-numbers | awk -v var=${1} '{for (I=1;I<=NF;I++) if ($I == var) {printf "%s\n", $(1) };}')

#echo ${ruleNo}

ip netns exec $2 iptables -t nat -D PREROUTING ${ruleNo}
ip netns exec $2 iptables -t nat -X $1
