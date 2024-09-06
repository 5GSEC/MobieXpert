#!/bin/bash
docker build -t localhost:5000/mobiexpert-xapp:0.0.1 .
docker push localhost:5000/mobiexpert-xapp:0.0.1
