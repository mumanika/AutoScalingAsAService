#!/bin.bash

#Args: name of tunnel, local IP address, remote IP address

ip tunnel add $1 mode gre local $2 remote $3
