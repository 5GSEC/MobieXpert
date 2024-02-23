#!/usr/bin/env bash
set -e
sudo make image/mobi-expert-xapp
sudo docker push localhost:5000/mobi-expert-xapp
