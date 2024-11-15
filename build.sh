#!/bin/bash
docker build -t localhost:5000/mobiexpert-xapp:0.0.2 .
docker push localhost:5000/mobiexpert-xapp:0.0.2
