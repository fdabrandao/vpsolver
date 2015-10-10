FROM fdabrandao/docker-ubuntu

MAINTAINER Filipe Brandão <fdabrandao@dcc.fc.up.pt>

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
