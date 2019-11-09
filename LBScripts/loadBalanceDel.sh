#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Illegal number of parameters"
	exit
fi

iptables -t nat -D PREROUTING $1 
