#!/bin/bash

#Args: Address to add to interface, interface name

ip addr add ${1} dev ${2}
