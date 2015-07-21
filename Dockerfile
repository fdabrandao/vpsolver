FROM ubuntu:trusty

MAINTAINER Filipe Brandao <fdabrandao@dcc.fc.up.pt>

RUN DEBIAN_FRONTEND=noninteractive apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
    make \
    g++-4.8 \
    python2.7 \
    python-pip \
    python-dev \
    python-pygraphviz \
    glpk-utils

USER root
RUN mkdir -p /vpsolver
ADD . /vpsolver
ENV HOME=/vpsolver
WORKDIR /vpsolver
EXPOSE 5555

RUN DEBIAN_FRONTEND=noninteractive pip install -r requirements.txt
RUN python setup.py install

CMD ifconfig eth0 && python /vpsolver/pyvpsolver/webapp/app.py
