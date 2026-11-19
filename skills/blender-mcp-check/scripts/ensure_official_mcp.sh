#!/bin/zsh
# Make sure Blender's official MCP plugin listens on 127.0.0.1:9877.
# Prints one final line: READY, STARTED, RELAUNCHED or FAILED <reason>.
# It never closes Blender and never opens or saves a .blend file.
BADGES=/Users/antonioperedo/Desktop/badges
HERE=${0:A:h}
up() { lsof -iTCP:$1 -sTCP:LISTEN -n -P >/dev/null 2>&1 }
wait_for() { for i in {1..30}; do up $1 && return 0; sleep 1; done; return 1 }

if up 9877; then echo READY; exit 0; fi

if up 9876; then
  # Blender is open with the community bridge: start the official plugin through it.
  python3 "$HERE/bridge_send.py" code "$BADGES/tools/start_official_mcp.py" >/dev/null 2>&1
  if wait_for 9877; then echo STARTED; exit 0; fi
  echo "FAILED bridge on 9876 is up but the official plugin did not start on 9877"; exit 1
fi

if pgrep -x Blender >/dev/null; then
  echo "FAILED Blender is open but neither 9876 nor 9877 is listening (start the plugins from Blender's MCP panel)"; exit 1
fi

# Blender is closed: relaunch it with both servers (owner approved, see the reopen-blender memory).
/Applications/Blender.app/Contents/MacOS/Blender --python "$BADGES/forge_tide_compass_20261103/start_blender.py" >/dev/null 2>&1 &
disown
if wait_for 9877; then echo RELAUNCHED; exit 0; fi
echo "FAILED relaunched Blender but 9877 never came up"; exit 1
