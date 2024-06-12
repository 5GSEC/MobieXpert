#!/bin/bash
sudo kubectl logs $(sudo kubectl get pods -o name -n ricxapp | grep "mobiexpert-xapp") -n ricxapp -f
