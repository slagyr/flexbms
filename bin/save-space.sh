#!/usr/bin/env bash

DRIVE=$(cat bin/drive)

mdutil -i off ${DRIVE}
cd ${DRIVE}
rm -rf .{,_.}{fseventsd,Spotlight-V*,Trashes}
mkdir .fseventsd
touch .fseventsd/no_log .metadata_never_index .Trashes
cd -