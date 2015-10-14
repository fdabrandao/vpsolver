FROM fdabrandao/docker-ubuntu

MAINTAINER Filipe Brandão <fdabrandao@dcc.fc.up.pt>

USER root
RUN mkdir -p /vpsolver
ADD . /vpsolver
ENV HOME=/vpsolver
WORKDIR /vpsolver

# python2.7 virtualenv
RUN rm -rf venv2.7
RUN bash virtualenv.sh -p python2.7 --venv venv2.7

# python3.5 virtualenv
RUN rm -rf venv3.5
RUN bash virtualenv.sh -p python3.5 --venv venv3.5

EXPOSE 5555
CMD bash webapp.sh --venv venv2.7 --port 5555
