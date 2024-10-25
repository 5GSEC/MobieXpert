# ==================================================================================
#   Copyright (c) 2020 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ==================================================================================

FROM python:3.8-slim as stretch

# sdl needs gcc
RUN apt-get update && apt-get -y install bash gcc musl-dev wget
RUN ln -s /usr/lib/x86_64-linux-musl/libc.so /lib/libc.musl-x86_64.so.1
RUN apt-get -y install build-essential flex csh

# install rmr e2ap
ARG rmr_version=4.9.4
ARG e2ap_version=1.1.0

# download rmr and e2ap libraries from package cloud
RUN wget -nv --content-disposition https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/rmr_${rmr_version}_amd64.deb/download.deb
RUN wget -nv --content-disposition https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/rmr-dev_${rmr_version}_amd64.deb/download.deb

RUN wget -nv --content-disposition https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/riclibe2ap_${e2ap_version}_amd64.deb/download.deb
RUN wget -nv --content-disposition https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/riclibe2ap-dev_${e2ap_version}_amd64.deb/download.deb

RUN dpkg -i rmr_${rmr_version}_amd64.deb
RUN dpkg -i rmr-dev_${rmr_version}_amd64.deb

RUN dpkg -i riclibe2ap_${e2ap_version}_amd64.deb
RUN dpkg -i riclibe2ap-dev_${e2ap_version}_amd64.deb

# RMR setup
RUN mkdir -p /opt/route/
COPY init/test_route.rt /opt/route/test_route.rt
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
ENV RMR_SEED_RT /opt/route/test_route.rt
# install a legacy ver of betterproto TODO: upgrade later
# RUN pip install betterproto==2.0.0b4 

# Install
COPY setup.py /tmp
COPY README.md /tmp
COPY LICENSE /tmp/
COPY src/ /tmp/src
COPY init/ /tmp/init

# prepare pbest environment
RUN cd /tmp/src/pbest/expert && make clean && make
RUN cp /tmp/src/pbest/expert/main /usr/local/bin/main

RUN pip install /tmp

# Env - TODO- Configmap
ENV PYTHONUNBUFFERED 1
ENV CONFIG_FILE=/tmp/init/config-file.json

# For Default DB connection, modify for resp kubernetes env
ENV DBAAS_SERVICE_PORT=6379
ENV DBAAS_SERVICE_HOST=service-ricplt-dbaas-tcp.ricplt.svc.cluster.local

#Run
CMD run-xapp.py
