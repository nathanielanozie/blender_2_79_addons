import bpy 
import imp

bl_info = {
    "name": "Test MultiFile Addon",
    "author": "Nathaniel Anozie",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "3D View",
    "description": "does nothing",
    "category": "Object",
}

from . import ui
imp.reload(ui)
from . import test
imp.reload(test)

def register():
    ui.register()
    
def unregister():
    ui.unregister()
    
if __name__ == "__main__":
    register()