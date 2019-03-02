#!/usr/bin/env bash

rm -rf .build
mkdir .build

cp -rf bms .build
find .build/bms -name '*.py' | xargs -n 1 bin/mpy-cross
find .build/bms -name '*.py' | xargs rm
