bl_info = {
    "name": "Blender MCP",
    "author": "Sunmax0731",
    "version": (1, 2, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Blender MCP",
    "description": "Codex and Blender integration scaffold via MCP",
    "category": "3D View",
}

from .registration import register_addon, unregister_addon


def register():
    register_addon()


def unregister():
    unregister_addon()
