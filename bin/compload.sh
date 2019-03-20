#!/usr/bin/env bash

DRIVE=$(cat bin/drive)

bin/compile.sh

cp -rX lib ${DRIVE}/
cp -rX .build/bms ${DRIVE}/
cp -X *.py ${DRIVE}/
