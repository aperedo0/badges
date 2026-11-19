---
name: blender-mcp-check
description: Gate before ANY work that uses Blender (badges, the treasure chest, props, animation, renders, materials, opening or inspecting a .blend). Confirms Blender's official MCP connection (port 9877, mcp__blender-official__* tools) actually answers, starts it if it is only switched off, and if it still does not work, stops and tells the owner instead of working around it. Use at the start of every Blender task and again whenever an official Blender MCP call fails mid task.
---

# Blender MCP check

The owner's rule (2026-11-17): make sure the official Blender MCP works before any Blender work. If it just will not work, pause and tell the owner. Do not quietly carry on with background Blender or the old bridge instead.

## Steps

1. **Ask Blender directly.** Load the tools if they are deferred (one ToolSearch call, for example `select:mcp__blender-official__get_blendfile_summary_path_info,mcp__blender-official__execute_blender_code,mcp__blender-official__get_screenshot_of_window_as_image`). Then call `mcp__blender-official__get_blendfile_summary_path_info`. If it returns `status: ok`, the check passes. Go to step 4.
2. **If it fails** (for example `Cannot connect to Blender at localhost:9877`), run:
   ```sh
   /Users/antonioperedo/Desktop/badges/skills/blender-mcp-check/scripts/ensure_official_mcp.sh
   ```
   * `READY`: the port is up but the call failed. Retry the call once.
   * `STARTED`: Blender was open with only the community bridge (port 9876) running. The script started the official plugin through it.
   * `RELAUNCHED`: Blender was closed. The script reopened it with both servers, as the reopen-blender memory allows. Tell the owner that Blender was reopened.
   * `FAILED ...`: go to step 3.

   After `STARTED` or `RELAUNCHED`, call `get_blendfile_summary_path_info` again.
3. **Still not working: pause.** Stop the Blender work and tell the owner in a few lines:
   * what failed, with the exact error,
   * what you tried (the script's output line),
   * what they can do, for example: open Blender, then in the sidebar MCP panel press Start Server, or run `! /Users/antonioperedo/Desktop/badges/skills/blender-mcp-check/scripts/ensure_official_mcp.sh`.

   Then wait for their answer. Do not switch to background Blender, the 9876 bridge or Computer Use as a quiet substitute, and do not call the work done.
4. **Report it in one line**, for example "Official Blender MCP is working (port 9877)", then start the task.

## Mid task

If an official Blender MCP call fails later in the task, run steps 2 and 3 again before anything else. Background Blender (`blender -b`) is still fine for heavy steps, such as renders, once the check has passed. It is never a replacement for a broken live connection.

## Notes

* The script never closes Blender, never opens or saves a file, and never deletes anything.
* `scripts/bridge_send.py` talks to the community bridge on 9876. The script only uses it to start the official plugin (`badges/tools/start_official_mcp.py`).
* Blender closed by itself before (Nov 8, 2026), right after objects were deleted in the open window. Avoid deleting objects in the live scene.
