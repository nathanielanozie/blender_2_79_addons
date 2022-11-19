#tool to help straighten vertices during modeling


#last modified
#070321 -- working on initial release
#070221 -- added method to straighten verts. matching to random vert. needs to make into addon


import bpy
import bmesh


bl_info = {
    "name":"straighten vertices",
    "description":"tool to help straighten vertices during modeling",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}


from bpy.props import(
    StringProperty
    )

from bpy.types import(
    Operator,
    Panel
    )

class StraightenVertsOperator(Operator):
    """generates simple cube mesh with primitive geo features
    """
    bl_idname = "obj.straighten_verts" #needs to be all lowercase
    bl_label = "Straighten Vertices"
    bl_options = {"REGISTER"}

    axisMode = bpy.props.StringProperty()
    
    def execute(self, context):
        obj = context.selected_objects[0]        
        if self.axisMode == 'x':
            straightenVertsMatchToRandom(objectName = obj.name, axis = 0)
        elif self.axisMode == 'y':
            straightenVertsMatchToRandom(objectName = obj.name, axis = 1)
        elif self.axisMode == 'z':
            straightenVertsMatchToRandom(objectName = obj.name, axis = 2)

        return {'FINISHED'}


class StraightenVertsPanel(Panel):
    bl_label = "Straighten Verts Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "straighten verts in given axis")

        ##buttons
        row = layout.row(align=True)
        row.alignment='EXPAND'
        row.operator("obj.straighten_verts",text="x").axisMode='x'
        row.operator("obj.straighten_verts",text="y").axisMode='y'
        row.operator("obj.straighten_verts",text="z").axisMode='z'

def register():
    bpy.utils.register_class(StraightenVertsOperator)
    bpy.utils.register_class(StraightenVertsPanel)

def unregister():
    bpy.utils.unregister_class(StraightenVertsOperator)
    bpy.utils.unregister_class(StraightenVertsPanel)

if __name__=="__main__":
    register()
    
    

#start code for tool here
def straightenVertsMatchToRandom(objectName = '', axis = 0):
    """move all selected verts in axis direction to match a random selected vert.
    this is so can allow box or lasso selection of verts.
    assumes start in edit mode.
    axis 0,1,2 for x,y or z
    """
    if not objectName in bpy.data.objects:
        print('requires a mesh object to exist')
        return
        
    #check we are in edit mode
    if bpy.data.objects[objectName].mode != 'EDIT':
        print('requires mesh in edit mode')
        return
        
    #i think using bmesh over vertices.select cause get update immediately
    mesh = bpy.data.objects[objectName].data
    b = bmesh.from_edit_mesh(mesh) #make a copy of mesh to work on
    
    selectedBVerts = [ v for v in b.verts if v.select == True]
    if not selectedBVerts:
        print('nothing to do no verts selected')
        return
        
    target = selectedBVerts[0].co[axis]
    #match all vertices location to target in axis only
    for vert in selectedBVerts:
        vert.co[axis] = target
        
    #update original mesh
    bmesh.update_edit_mesh(mesh)
       
    #i think freeing was causing crash so skipping b.free
    
    
"""
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/modeling')

import naStraightenVertsAddOn as mod
import imp
imp.reload(mod)
#bpy.app.debug=True #temporary
mod.straightenVertsMatchToRandom(objectName = 'Plane', axis = 0)
"""