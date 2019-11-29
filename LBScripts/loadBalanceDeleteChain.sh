#This script deletes the chain

#inputs: The group name, base namespace name, 

ip netns exec $2 iptables -t nat -F $1


read a <<< $(ip netns exec $2 iptables -t nat -vL -n --line-numbers | awk -v var=${1} '{for(I=1;I<=$NF;I++) if ($I == var) {printf "%s", $(1) };}')

echo $a
