# SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
# SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>
#
# SPDX-License-Identifier: Apache-2.0

FROM python:3.8-slim

# install all deps
WORKDIR /usr/local

# prepare gprpc and pbest dependencies
RUN pip install grpcio grpcio-tools
# RUN dpkg --add-architecture i386 && apt-get update && apt-get -y install libc6:i386 libncurses5:i386 libstdc++6:i386
RUN apt-get update && apt-get -y install build-essential gcc-multilib flex csh

# COPY onos_e2_sm ./onos_e2_sm
# RUN pip install --upgrade pip ./onos_e2_sm --no-cache-dir

# speed up subsequent image builds by pre-dl and pre-installing pre-reqs
COPY mobi-expert-xapp/setup.py ./mobi-expert-xapp/setup.py
RUN pip install ./mobi-expert-xapp --no-cache-dir

# install actual app code
COPY mobi-expert-xapp ./mobi-expert-xapp
RUN pip install ./mobi-expert-xapp --no-cache-dir

# prepare pbest environment
RUN cd mobi-expert-xapp/pbest/expert && make clean && make
RUN cp mobi-expert-xapp/pbest/expert/main ./

ENTRYPOINT [ "python" ]
