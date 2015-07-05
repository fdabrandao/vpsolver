FROM ubuntu:trusty
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install make python2.7 python-setuptools python-pygraphviz g++-4.8 glpk-utils
RUN ln -s /usr/bin/g++-4.8 /usr/bin/g++
RUN mkdir -p /vpsolver
ADD . /vpsolver
WORKDIR /vpsolver
RUN python setup.py install
