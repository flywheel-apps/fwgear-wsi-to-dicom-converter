FROM ubuntu:focal-20200606
MAINTAINER Flywheel <support@flywheel.io>

ENV DEBIAN_FRONTEND noninteractive
RUN echo "deb http://us.archive.ubuntu.com/ubuntu/ focal universe" | tee -a /etc/apt/sources.list && \
    apt-get update -qq && \
    apt-get install -y \
        unzip \
        wget \
        python3-pip \
        libtiff-dev \
        libjsoncpp-dev \
        libjpeg8-dev \
        libgdk-pixbuf2.0-dev \
        libcairo2-dev \
        libsqlite3-dev \
        libglib2.0-dev \
        libxml2-dev \
        libopenjp2-7-dev \
        libgtest-dev

ENV FLYWHEEL="/flywheel/v0"
COPY ["requirements.txt", "/opt/requirements.txt"]
RUN pip3 install -r /opt/requirements.txt \
    && mkdir -p $FLYWHEEL

WORKDIR $FLYWHEEL
ENV VERSION 1.0.3
ADD https://github.com/GoogleCloudPlatform/wsi-to-dicom-converter/releases/download/v$VERSION/wsi2dcm_$VERSION.deb .
RUN dpkg -i ./wsi2dcm_$VERSION.deb && rm ./wsi2dcm_$VERSION.deb

COPY run.py manifest.json $FLYWHEEL/
RUN chmod +x $FLYWHEEL/run.py
ENTRYPOINT /bin/bash

