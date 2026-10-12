#!/bin/zsh
# sweep.sh <outdir> <distances...> : drag poses of the Diamond with the installed build (no rebuild).
W=/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011
OUT=$1; shift; mkdir -p $OUT
for d in "$@"; do $W/tools/quickpose.sh $OUT/d$d.png $d >/dev/null; echo -n "$d "; done; echo
