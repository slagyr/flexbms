#!/usr/bin/env bash

DRIVE=$(cat bin/drive)

cp -rX lib ${DRIVE}/
cp -rX bms ${DRIVE}/
cp -X *.py ${DRIVE}/