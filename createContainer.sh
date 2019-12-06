#!/bin/bash

# Create container. Make sure the shell scripts are in the same folder
# Args: name of container, subnet namespace name

docker run -itd --name $1 ece792 '/bin/bash'
pid=$(docker inspect -f '{{.State.Pid}}' $1)
./addGuestBridgeInterface.sh $2 $1
./addContainerInterface.sh $2 $1 $pid
docker exec --privileged $1 service ssh start
