#!/usr/bin/env bash

bin/compile.sh

cp -rX lib /Volumes/CIRCUITPY/
cp -rX .build/bms /Volumes/CIRCUITPY/
cp -X *.py /Volumes/CIRCUITPY/
