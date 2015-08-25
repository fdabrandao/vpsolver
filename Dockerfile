FROM ubuntu:trusty

MAINTAINER Filipe Brandao <fdabrandao@dcc.fc.up.pt>

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y install \
    make \
    g++-4.8 \
    python2.7 \
    python-pip \
    python-dev \
    python-pygraphviz \
    glpk-utils \
    libglpk-dev \
    libffi-dev \
    libssl-dev

RUN DEBIAN_FRONTEND=noninteractive pip install --upgrade pip
RUN DEBIAN_FRONTEND=noninteractive pip install --upgrade requests[security]

USER root
RUN mkdir -p /vpsolver
ADD . /vpsolver
ENV HOME=/vpsolver
WORKDIR /vpsolver
EXPOSE 5555

RUN DEBIAN_FRONTEND=noninteractive bash build.sh
RUN DEBIAN_FRONTEND=noninteractive bash install.sh
RUN DEBIAN_FRONTEND=noninteractive bash test.sh test_install quick_test

CMD ifconfig eth0 && python -m pyvpsolver.webapp.app
