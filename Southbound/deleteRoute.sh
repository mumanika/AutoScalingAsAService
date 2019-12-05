#!/bin/bash

# Desc: Delete Route
# Args: ip address of route with prefix

if [ $# -ne 1 ];
then
	exit
fi

ip route delete $1
