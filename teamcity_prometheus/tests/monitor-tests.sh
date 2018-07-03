#!/usr/bin/env bash

until ack -f --python | entr -d python -m unittest discover; do sleep 1; done