#!/bin/bash

# Args: table to delete from, chain to delete from, the rule number to delete

iptables -t $1 -D $2 $3
