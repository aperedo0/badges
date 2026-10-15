#!/bin/zsh
# try.sh <tier> <candidate.usdz> <out_prefix> [poses...] : put a candidate in the lab, build, install, shoot rest + turn poses
R=~/Desktop/badges/rim_fix_20261012; L=$R/tools/lab.sh; t=$1; c=$2; o=$3; shift 3
$L model $t $c >/dev/null && $L build | grep -q SUCCEEDED || { echo BUILD FAILED; exit 1; }
xcrun simctl install 3B38C5E6-1859-463F-93F5-9BE140BC7C14 /private/tmp/claude-501/-Users-antonioperedo-Desktop-screen-time/2fb41ee0-9803-40f8-8d1a-b588b87537b9/scratchpad/rimlab/dd/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app
$L rest $t ${o}_rest.png >/dev/null
for p in "$@"; do $L turn $t $p ${o}_t$p.png >/dev/null; done
echo done $o
