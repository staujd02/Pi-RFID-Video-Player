#!/bin/bash

# Declare counter
declare -i c=1

# Create temp
touch bash.temp

# Search media directory for all .mp4 files (ignore all errors)
find $1 -type f -name '*.mp4' -o -name '*.avi' 2>/dev/null | while read entry;
do
#  For each entry, Create tuple: counter,file's name,file path (Space safe)
  echo "$((c++)),$(echo $entry | sed 's/^.*\///g'),${entry//\ /"\\ "}" >> bash.temp
done
echo "$(sort -t ',' -k 2 < bash.temp)"
rm bash.temp
