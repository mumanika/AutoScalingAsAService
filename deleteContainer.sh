#!/bin/bash

#Args: name of the container

docker kill $1
docker rm $1
