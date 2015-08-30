FROM ubuntu:trusty

MAINTAINER Filipe Brandao <fdabrandao@dcc.fc.up.pt>

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y install \
    make \
    g++-4.8 \
    python2.7 \
    python-pip \
    python-dev \
    python3 \
    python3-pip \
    python3-dev \
    glpk-utils \
    libglpk-dev \
    libffi-dev \
    libssl-dev

RUN DEBIAN_FRONTEND=noninteractive pip2 install --upgrade requests[security]
RUN DEBIAN_FRONTEND=noninteractive pip3 install --upgrade requests[security]

USER root
RUN mkdir -p /vpsolver
ADD . /vpsolver
ENV HOME=/vpsolver
WORKDIR /vpsolver
EXPOSE 5555

RUN bash build.sh
RUN pip2 install -r requirements.txt
RUN bash test.sh quick_test
RUN pip3 install -r requirements.txt
RUN bash test3.sh quick_test

RUN bash install.sh
RUN bash test.sh test_install quick_test

RUN bash install3.sh
RUN bash test3.sh test_install quick_test

CMD ifconfig eth0 && python -m pyvpsolver.webapp.app
