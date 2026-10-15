#!/bin/zsh
# lab.sh: private badge test bench. A clone of the app repo and its own simulator, so tests never touch
# the real repo or the shared test simulator.
#   lab.sh model <tier> <file.usdz>   put a candidate model into the lab copy (same filename)
#   lab.sh build                      build the lab copy (UI-only app) into the lab DerivedData
#   lab.sh run <tier>                 install, launch three times showing <tier> on Home (first launch is flat)
#   lab.sh shot <out.png>             screenshot
#   lab.sh turn <tier> <points> <out.png>   relaunch, slow upward drag of <points>, screenshot
set -e
S=/private/tmp/claude-501/-Users-antonioperedo-Desktop-screen-time/2fb41ee0-9803-40f8-8d1a-b588b87537b9/scratchpad/rimlab
SIM=3B38C5E6-1859-463F-93F5-9BE140BC7C14; BID=com.antonioperedo.screentime.uidev
APP=$S/dd/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app
AXE=$(ls -t ~/.npm/_npx/*/node_modules/xcodebuildmcp/bundled/axe | head -1)
cap() { echo ${(C)1}; }
launch3() { for i in 1 2 3; do xcrun simctl terminate $SIM $BID 2>/dev/null || true; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier $1 >/dev/null; sleep ${2:-12}; done; }
case $1 in
  model) T=$(cap $2); cp "$3" "$S/app/ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModel$T.dataset/$2_badge_mobile.usdz"; echo "lab model $2 <- $3" ;;
  build) xcodebuild -project $S/app/ScreenTime.xcodeproj -scheme ScreenTime-UIOnly -destination "platform=iOS Simulator,id=$SIM" -derivedDataPath $S/dd -configuration Debug build > $S/build.log 2>&1 || true; grep -E '\*\* BUILD' $S/build.log | tail -1 ;;
  run) [[ $(xcrun simctl list devices | grep $SIM) == *Booted* ]] || xcrun simctl boot $SIM; xcrun simctl install $SIM $APP; launch3 $2 ;;
  rest) launch3 $2 12; xcrun simctl io $SIM screenshot "$3" >/dev/null 2>&1; echo "$3" ;;
  shot) xcrun simctl io $SIM screenshot "$2" >/dev/null 2>&1; echo "$2" ;;
  turn) launch3 $2 12; $AXE swipe --start-x 200 --start-y 700 --end-x 200 --end-y $((700 - $3)) --duration 1.5 --udid $SIM >/dev/null; sleep 3; xcrun simctl io $SIM screenshot "$4" >/dev/null 2>&1; echo "$4" ;;
esac
