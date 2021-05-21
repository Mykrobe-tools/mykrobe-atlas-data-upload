FROM debian:sid

RUN apt-get update -y
RUN apt-get install -y wget python3 python3-pip
RUN pip3 install --upgrade pip

## Install berkeleydb
ENV BERKELEY_VERSION 4.8.30
# Download, configure and install BerkeleyDB
RUN wget -P /tmp http://download.oracle.com/berkeley-db/db-"${BERKELEY_VERSION}".tar.gz && \
    tar -xf /tmp/db-"${BERKELEY_VERSION}".tar.gz -C /tmp && \
    rm -f /tmp/db-"${BERKELEY_VERSION}".tar.gz
RUN cd /tmp/db-"${BERKELEY_VERSION}"/build_unix && \
    ../dist/configure && make && make install

RUN pip3 install bsddb3==6.2.5
RUN pip3 install numpy
RUN pip3 install scipy

COPY ./bin /usr/src/app/bin
WORKDIR /usr/src/app
