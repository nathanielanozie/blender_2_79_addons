import bpy 
import imp

bl_info = {
    "name": "Simple Blendshape based face rig",
    "author": "Nathaniel Anozie",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "3D View",
    "description": "Simple Blendshape based face rig for 2d four vert planes and a cube.",
    "category": "Object",
}

from . import naUI
imp.reload(naUI)
from . import naCore
imp.reload(naCore)
from . import naControls
imp.reload(naControls)
from . import naUtils
imp.reload(naUtils)
from . import naShapekeys
imp.reload(naShapekeys)

def register():
    naUI.register()
    
def unregister():
    naUI.unregister()
    
if __name__ == "__main__":
    register()