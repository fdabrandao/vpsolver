#!/bin/sh
BASEDIR=`dirname $0`
cd $BASEDIR

docker build -t fdabrandao/vpsolver . || exit 1
docker stop $(docker ps -a | grep fdabrandao/vpsolver | cut -d" " -f1) 2>/dev/null
docker rm $(docker ps -a | grep fdabrandao/vpsolver | cut -d" " -f1) 2>/dev/null
docker run -it --rm -p 5555 fdabrandao/vpsolver || exit 1
#docker run -it --rm -p 5555 fdabrandao/vpsolver bash
