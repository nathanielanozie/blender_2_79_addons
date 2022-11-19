import bpy

from bpy.props import(
    StringProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )

from . import naCore

class FaceRigProperties(PropertyGroup):
    #here we make each textfield
    char_name = StringProperty(
        name = "char_name",
        description = "unique name for face rig"
        )
    
class generateMeshOperator(Operator):
    """generates simple cube mesh with primitive geo features
    """
    bl_idname = "obj.generatemesh" #needs to be all lowercase
    bl_label = "generateMesh"
    bl_options = {"REGISTER"}

    def execute(self, context):
        char = context.scene.facerig_prop.char_name
        naCore.initGlobalConstants(character = char)
        naCore.generateRobotFaceMesh(context = context)
        return {'FINISHED'}

class generateGuidesOperator(Operator):
    """generates guides for rigs. to be placed by user
    """
    bl_idname = "obj.generateguides" #needs to be all lowercase
    bl_label = "generateGuides"
    bl_options = {"REGISTER"}

    def execute(self, context):
        char = context.scene.facerig_prop.char_name
        naCore.initGlobalConstants(character = char)
        naCore.generateGuides()
        return {'FINISHED'}
        
class generateRigOperator(Operator):
    """generates simple cube mesh with primitive geo shapekeys and controls
    """
    bl_idname = "obj.generaterig" #needs to be all lowercase
    bl_label = "generateRig"
    bl_options = {"REGISTER"}

    def execute(self, context):
        char = context.scene.facerig_prop.char_name
        naCore.initGlobalConstants(character = char)        
        naCore.doIt(context = context)
        return {'FINISHED'}

class naSimpleRobotFaceRigPanel(Panel):
    bl_label = "Cube Face Primitives Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.prop( context.scene.facerig_prop, "char_name", text = "character_name" )
        layout.operator( "obj.generatemesh")
        layout.operator( "obj.generateguides")
        layout.operator( "obj.generaterig")

classes = (
    generateMeshOperator,
    generateRigOperator,
    generateGuidesOperator,
    naSimpleRobotFaceRigPanel,
    FaceRigProperties  
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    
    
    #here we name the property that holds all our textfields
    bpy.types.Scene.facerig_prop = PointerProperty(
        type = FaceRigProperties
        )
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)    

    del bpy.types.Scene.facerig_prop
