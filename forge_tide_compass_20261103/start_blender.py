"""Start the installed local Blender bridge for this authorized modeling run."""
from pathlib import Path
import bpy,sys
addon=Path('/Users/antonioperedo/Library/Application Support/Blender/5.2/scripts/addons')
sys.path.insert(0,str(addon))
import blender_mcp_addon
try:bpy.ops.preferences.addon_enable(module='blender_mcp_addon')
except RuntimeError:pass
def connect():
    if not hasattr(bpy.types,'blendermcp_server'):
        bpy.types.blendermcp_server=blender_mcp_addon.BlenderMCPServer(port=9876)
    server=bpy.types.blendermcp_server
    if not server.running:server.start()
    return None
bpy.app.timers.register(connect,first_interval=1)

# Also start the official Blender MCP plugin on port 9877 (added Nov 14, 2026).
exec(open("/Users/antonioperedo/Desktop/badges/tools/start_official_mcp.py").read())
