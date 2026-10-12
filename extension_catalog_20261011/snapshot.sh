#!/bin/zsh
# Usage: snapshot.sh <output-dir>
# Records, from the built ScreenTime.app, the evidence the extension-catalog plan compares before and after.
set -eu
OUT="$1"
APP=/Users/antonioperedo/Library/Developer/Xcode/DerivedData/ScreenTime-cuxjmudqlniejlbrmoridmtkswhs/Build/Products/Debug-iphoneos/ScreenTime.app
mkdir -p "$OUT"

: > "$OUT/car_sizes.txt"
find "$APP" -name Assets.car -exec ls -l {} \; | awk '{print $5, $9}' | sed "s#$APP#APP#" | sort -k2 >> "$OUT/car_sizes.txt"

xcrun assetutil --info "$APP/Assets.car" > "$OUT/app_assetutil.json"
xcrun assetutil --info "$APP/PlugIns/DeviceActivityMonitorExtension.appex/Assets.car" > "$OUT/monitor_assetutil.json"
xcrun assetutil --info "$APP/PlugIns/ShieldActionExtension.appex/Assets.car" > "$OUT/shield_action_assetutil.json"

plutil -convert xml1 -o "$OUT/monitor_Info.plist.xml" "$APP/PlugIns/DeviceActivityMonitorExtension.appex/Info.plist"
plutil -convert xml1 -o "$OUT/shield_action_Info.plist.xml" "$APP/PlugIns/ShieldActionExtension.appex/Info.plist"

for name in app monitor shield_action; do
  python3 -c 'import json,sys; print(sorted({e["Name"] for e in json.load(sys.stdin)[1:]}))' < "$OUT/${name}_assetutil.json" > "$OUT/${name}_asset_names.txt"
  python3 -c '
import json,sys
entries = json.load(sys.stdin)[1:]
print(sorted(e.get("SHA1Digest","") for e in entries if e.get("Name") == "AppIcon"))
' < "$OUT/${name}_assetutil.json" > "$OUT/${name}_appicon_sha1.txt"
done

du -sk "$APP" | awk '{print $1}' > "$OUT/du_sk.txt"
