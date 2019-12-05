#!/bin/bash

#Args: table to add to, chain to add to, position to add to, string for all the options to send, target for the rule, options for the target

iptables -t $1 -I $2 $3 ${4} -j ${5} ${6}
