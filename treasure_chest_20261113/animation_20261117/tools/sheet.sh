#!/bin/zsh
# sheet.sh <frames dir> <first> <count> <cols> <out.png> [scale]
# contact sheet of numbered frames, left to right, top to bottom, starting at <first>
dir=$1; first=$2; count=$3; cols=$4; out=$5; sc=${6:-1}
rows=$(( (count + cols - 1) / cols ))
ffmpeg -loglevel error -y -start_number $first -i "$dir/%04d.png" \
  -vf "scale=iw*$sc:ih*$sc,tile=${cols}x${rows}:padding=2:color=0x303030" -frames:v 1 "$out"
