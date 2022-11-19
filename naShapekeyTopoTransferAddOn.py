#shapekey topology transfer. tested in blender 2.79
#
#modify use at your own risk

#last modified
#123021 -- removed scaling of mesh before bind
#051421,102521 -- working on initial release
#   1. an offset x,y,z for where to put created shapes 
#   2. needs to be tested on test facial mesh
#   3. option to position the created shapes in offset way or overlapping.
#050921 -- working on initial release
#050421 -- working on initial release 

bl_info = {
    "name":"shapekey topology transfer",
    "description":"shapekey topology transfer. Inspired by Chris Pagoria online topology transfer tutorial",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

import bpy


#simple ui with single button and a few text fields with some defaults
from bpy.props import(
    StringProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class TopoTransferOperator(Operator):
    """transfer topology onto already created shapekeys. it may lose some finer grained modeling when using mesh_deform bind
    """
    bl_idname = "obj.do_topotransfer"
    bl_label = "Topology Transfer To Shapekeys"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        #get text field input
        meshWithShapekeys = context.scene.topo_transfer_prop.meshWithShapekeys
        meshNewTopology = context.scene.topo_transfer_prop.meshNewTopology
    
        self.report({'INFO'}, "Starting Shapkey Topology transfer ...")
        opTopoTransferToShapekeys( context = context,
                    newTopology = meshNewTopology,
                    oldTopology = meshWithShapekeys
                    )
        
        self.report({'INFO'}, "Completed Shapkey Topology transfer")
        return {'FINISHED'}
        
class TopoTransferPanel(Panel):
    bl_label = "Topo Transfer Panel"
    bl_space_type = "VIEW_3D" #for helping with scene selections in tool
    bl_region_type = "UI"
    
    def draw(self, context):
        
        #here we add textfields and button to ui
        #
        layout = self.layout
        layout.label(text = "Topology transfer tool")
        
        #2 text fields in a row
        #row = layout.row(align=True)
        #row.alignment='EXPAND'
        #text fields
        layout.prop( context.scene.topo_transfer_prop, "meshWithShapekeys", text = "old topology" )
        layout.prop( context.scene.topo_transfer_prop, "meshNewTopology", text = "new topology" )
        #button
        layout.operator( "obj.do_topotransfer")
        
class TopoTransferProperties(PropertyGroup):
    #here we make each textfield
    meshWithShapekeys = StringProperty(
        name = "meshWithShapekeys",
        description = "old topology mesh with shapekeys. its the data object name"
        )

    meshNewTopology = StringProperty(
        name = "meshNewTopology",
        description = "new topology mesh. its the data object name"
        )

def register():
    bpy.utils.register_class(TopoTransferOperator)
    bpy.utils.register_class(TopoTransferPanel)
    bpy.utils.register_class(TopoTransferProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.topo_transfer_prop = PointerProperty(
        type = TopoTransferProperties
        )
    
def unregister():
    bpy.utils.unregister_class(TopoTransferOperator)
    bpy.utils.unregister_class(TopoTransferPanel)
    bpy.utils.unregister_class(TopoTransferProperties)
    del bpy.types.Scene.topo_transfer_prop
    
if __name__ == "__main__":
    register()


def opTopoTransferToShapekeys(context = None, newTopology=None, oldTopology=None):
    """apply new topology to given shape keys. should create all of the shapekeys again but using new topology
    works with a separate newTopology mesh. when done all the shapekeys of old topology mesh are created using new topology.
    optionally new shapes can be added to new topology mesh.
    assumes oldTopology has shapekeys. assumes in object mode
    context is bpy.context
    """
    #1. not scaling down new topology mesh by .98, zero out translations
    #2. create mesh deform modifier where old topology mesh drives new topology mesh
    #3. loop through each shapekey of oldTopology
    #   a. turn on shape key
    #   b. copy new topology mesh shape to a new mesh
    #4. cleanup newly created shape keys
    #   #a. scale it back to 1.0
    #   b. place it a little off origin to make it clearly visible
    #   c. cleanup (i think need to remove any copied modifier)
    #   d. add name corresponding to original shapekeys
    #5. restore for new topology mesh
    #   a. remove mesh deform modifier
    #   b. scale new topology mesh back to 1.0
    #   c. place it back at starting position
    # (optional join as shapes all the created shapekeys onto new topology mesh)
    
    #assumes meshes exist
    new_topo_obj = bpy.data.objects[newTopology]
    old_topo_obj = bpy.data.objects[oldTopology]
    #1.
    start_newtopo_pos = (new_topo_obj.location.x,new_topo_obj.location.y,new_topo_obj.location.z)
    new_topo_obj.location = (0,0,0)
    #i think scaling messes things up
    #new_topo_obj.scale = (0.98,0.98,0.98) 
    ##
    
    #2.
    #assumes all shapekeys turned off on old topology mesh
    mesh_def= new_topo_obj.modifiers.new("mesh_def",type="MESH_DEFORM")
    mesh_def.object = old_topo_obj
    #trying higher precision for more precise bind
    mesh_def.precision = 6 #default is 5
    context.scene.objects.active = new_topo_obj #in 2.8 this is different
    bpy.ops.object.meshdeform_bind(modifier=mesh_def.name) #i dont think theres non ops replacement
    ##
    
    #3.
    #assumes all shapekeys turned off for old topology mesh. assumes Basis is first key.
    num_keys = len( old_topo_obj.data.shape_keys.key_blocks)
    created_shape_names = []
    orig_shapekey_names = []
    for key_index in range(1,num_keys): #skipping Basis first shape
        #a. turn on shape key
        old_topo_obj.active_shape_key_index = key_index
        old_topo_obj.show_only_shape_key = True
        
        #b. copy new topology mesh shape to a new mesh
        cp_mesh = _copyMesh( context = context, srcMesh = new_topo_obj.name )
        #need to apply mesh deform modifier so its effect sticks on copied mesh
        #i think created mesh needs to be active object for ops to work
        #bpy.ops.object.select_all(action='DESELECT')
        #bpy.data.objects[cp_mesh].select=True
        context.scene.objects.active = bpy.data.objects[cp_mesh]
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier= mesh_def.name)
        # i think might want to name created shape mesh with shape key name
        orig_shapekey_names.append(old_topo_obj.active_shape_key.name)
        created_shape_names.append(cp_mesh)
        ##
    old_topo_obj.show_only_shape_key = False #restore shape key setting
    
    #4.
    #cleanup newly created shapekeys
    for mname in created_shape_names:
        cp_obj = bpy.data.objects[mname]
        cp_obj.location = (0,0,5.0) #needs more work on placing newly created meshes
        #cp_obj.scale = (1,1,1)
    
    #name the newly created shapekey meshes
    for mname,origname in zip(created_shape_names,orig_shapekey_names):
        cp_obj = bpy.data.objects[mname]
        cp_obj.data.name = origname+'.new'
        cp_obj.name = origname+'.new'
    ##
    
    #5.
    context.scene.objects.active = new_topo_obj
    bpy.ops.object.modifier_remove(modifier=mesh_def.name) #there might be a non ops way that is better
    new_topo_obj.location = start_newtopo_pos
    new_topo_obj.scale = (1,1,1)
    ##

def _copyMesh( context = None, srcMesh = None ):
    """copies source mesh and returns created mesh name. assumes input is a mesh object name.
    context is bpy.context.
    """
    src_obj = bpy.data.objects[srcMesh]
    dup_obj = src_obj.copy()
    dup_obj.data = src_obj.data.copy()
    dup_obj.animation_data_clear() #not sure this is needed
    context.scene.objects.link(dup_obj) #different for blender 2.8
    
    return dup_obj.name

"""testing why bind not working with certain selection
import bpy

new_topo_obj = bpy.data.objects["Cube.001"]
old_topo_obj = bpy.data.objects["Cube"]
    
mesh_def= new_topo_obj.modifiers.new("mesh_def",type="MESH_DEFORM")
mesh_def.object = old_topo_obj
#without next line bind doesnt work with orig selected
#bpy.context.scene.objects.active = new_topo_obj #in 2.8 this is different
bpy.ops.object.meshdeform_bind(modifier=mesh_def.name) #i dont think theres non ops replacement

"""

#inspired by
#Chris Pagoria's online topology transfer tutorial: 'Transfering Facial Blend Shapes'
#https://blender.stackexchange.com/questions/18292/setting-active-object-through-python-issues