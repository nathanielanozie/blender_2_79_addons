import bpy 
import imp

bl_info = {
    "name": "modeling tools for facial modeling rigging (package)",
    "author": "Nathaniel Anozie",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "3D View",
    "description": "modeling tools for facial modeling rigging (package)",
    "category": "Object",
}

from . import ui
imp.reload(ui)
from . import core
imp.reload(core)


def register():
    ui.register()
    
def unregister():
    ui.unregister()
    
if __name__ == "__main__":
    register()