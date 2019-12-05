#!/bin/bash

#Args: name of one end of veth pair, name of other end 

ip link add ${1} type veth peer name ${2}
