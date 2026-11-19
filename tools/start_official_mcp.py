"""Turn on Blender's official MCP plugin (Blender Lab, v1.0.3) on port 9877.

Runs inside Blender, next to the community bridge on 9876. Use it from a
start script (exec this file) or send it through the community bridge to an
already open Blender. Safe to run twice.
"""
import bpy

MODULE = "bl_ext.user_default.mcp"
PORT = 9877


def _start():
    if not bpy.app.online_access:
        bpy.context.preferences.system.use_online_access = True
    try:
        bpy.ops.blmcp.server_start()
    except RuntimeError as ex:
        if "already" not in str(ex).lower():
            print("official MCP:", ex)
    return None


# Enable while online access is still off, so the plugin's own auto start
# (which would take port 9876 from the community bridge) never fires.
if MODULE not in bpy.context.preferences.addons:
    online = bpy.app.online_access
    bpy.context.preferences.system.use_online_access = False
    bpy.ops.preferences.addon_enable(module=MODULE)
    bpy.context.preferences.system.use_online_access = online
prefs = bpy.context.preferences.addons[MODULE].preferences
prefs.use_autostart = False
prefs.port = PORT
bpy.app.timers.register(_start, first_interval=1.5)
