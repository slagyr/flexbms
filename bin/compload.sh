#!/usr/bin/env bash

bin/compile.sh

cp -rX lib /Volumes/CIRCUITPY/
cp -rX .build/bms /Volumes/CIRCUITPY/
cp -X main.py /Volumes/CIRCUITPY/
cp -X repl.py /Volumes/CIRCUITPY/
