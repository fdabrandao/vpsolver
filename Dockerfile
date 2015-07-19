FROM ubuntu:trusty

MAINTAINER Filipe Brandao <fdabrandao@dcc.fc.up.pt>

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
    make \
    python2.7 \
    python-setuptools \
    python-pygraphviz \
    python-flask \
    g++-4.8 \
    glpk-utils
RUN ln -s /usr/bin/g++-4.8 /usr/bin/g++

RUN mkdir -p /vpsolver
ADD . /vpsolver

USER root
ENV HOME=/vpsolver
WORKDIR /vpsolver

EXPOSE 5555

RUN python setup.py install

CMD ifconfig eth0 && python /vpsolver/pyvpsolver/webapp/app.py
