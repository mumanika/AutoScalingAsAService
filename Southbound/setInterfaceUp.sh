#!/bin/bash

#Args: name of interface

ip link set dev $1 up
