#!/bin/sh

docker build -t fdabrandao/vpsolver .
docker run -it -p 5555 fdabrandao/vpsolver
