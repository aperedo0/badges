#!/bin/zsh
# shootall.sh <copper.usdz> <bronze.usdz> <platinum.usdz> <outdir> : one build with all three, then rest + 72/82/133/171 for each
R=~/Desktop/badges/rim_fix_20261012; L=$R/tools/lab.sh; o=$4; mkdir -p $o
$L model copper $1 >/dev/null; $L model bronze $2 >/dev/null; $L model platinum $3 >/dev/null
$L build | grep -q SUCCEEDED || { echo BUILD FAILED; exit 1; }
xcrun simctl install 3B38C5E6-1859-463F-93F5-9BE140BC7C14 /private/tmp/claude-501/-Users-antonioperedo-Desktop-screen-time/2fb41ee0-9803-40f8-8d1a-b588b87537b9/scratchpad/rimlab/dd/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app
for t in copper bronze platinum; do
  $L rest $t $o/${t}_rest.png >/dev/null
  for p in 72 82 133 171; do $L turn $t $p $o/${t}_t$p.png >/dev/null; done
done
echo shot $o
