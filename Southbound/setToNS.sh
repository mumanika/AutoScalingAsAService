#!/bin/bash

#Args: name of interface, name of the namespace to set the interface to

ip link set dev $1 netns $2
