FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y \
        locales \
        python3-pip

RUN locale-gen en_GB.UTF-8

RUN mkdir /home/nobody && \
    chown nobody /home/nobody

USER nobody
ENV HOME=/home/nobody \
    PATH=/home/nobody/.local/bin:$PATH \
    LANG=en_GB.UTF-8
# LANG needed for httpretty install on Py3

WORKDIR /home/nobody

RUN pip3 install --user nose messytables pyhamcrest

COPY . /home/nobody/
