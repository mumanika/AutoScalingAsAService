#!/bin/bash

# Desc: Remove the tenant namespace and also delete the routes to the remote IPs from the Provider namespace
# Args: namespace name, the remote IP on the other site

if [ $# -ne 2 ];
then
	exit
fi

ip netns delete $1
rm -rf /etc/netns/$1/*
#rmdir /etc/netns/$1
ip netns exec Provider ip route delete $2
