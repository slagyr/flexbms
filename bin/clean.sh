#!/usr/bin/env bash

DRIVE=$(cat bin/drive)

rm -r ${DRIVE}/lib
rm -r ${DRIVE}/bms
rm ${DRIVE}/*.py