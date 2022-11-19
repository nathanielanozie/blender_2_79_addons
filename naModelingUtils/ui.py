#some tools to help with modeling retopologizing
#modify use at your own risk
import bpy

from bpy.types import(
    Operator,
    Panel
    )

from . import core

class makeMeshWholeOperator(Operator):
    bl_idname = "obj.makemeshwhole" #needs to be all lowercase
    bl_label = "makeMeshWhole"
    bl_options = {"REGISTER"}

    def execute(self, context):
        core.makeMeshWhole(context.selected_objects[0])
        return {'FINISHED'}
        
class centerSelectedVerticesOperator(Operator):
    bl_idname = "obj.centerselectedvertices"
    bl_label = "centerSelectedVertices"
    bl_options = {"REGISTER"}

    def execute(self, context):
        #print(context.selected_objects)
        #self.report({'INFO'}, "context.selected_objects: %s" %context.selected_objects )
        core.centerSelectedVertices(context.selected_objects[0])
        return {'FINISHED'}
        
class deleteHalfMeshOperator(Operator):
    bl_idname = "obj.deletehalfmesh"
    bl_label = "deleteHalfMesh"
    bl_options = {"REGISTER"}

    def execute(self, context):
        #print(context.selected_objects)
        #self.report({'INFO'}, "context.selected_objects: %s" %context.selected_objects )
        core.deleteHalfMesh(context.selected_objects[0])
        return {'FINISHED'}

class dissolveEdgeOperator(Operator):
    bl_idname = "obj.dissolveedge"
    bl_label = "dissolveEdge"
    bl_options = {"REGISTER"}

    def execute(self, context):
        core.doDissolveEdges()
        return {'FINISHED'}
        
        
class naModelingUtilsPanel(Panel):
    bl_label = "naModelingUtils Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        #layout.label(text = "Modeling tool")
        layout.operator( "obj.makemeshwhole")
        layout.operator( "obj.centerselectedvertices")
        layout.operator( "obj.deletehalfmesh")
        layout.operator( "obj.dissolveedge")
        
def register():
    bpy.utils.register_class(makeMeshWholeOperator)
    bpy.utils.register_class(centerSelectedVerticesOperator)
    bpy.utils.register_class(deleteHalfMeshOperator)
    bpy.utils.register_class(dissolveEdgeOperator)
    bpy.utils.register_class(naModelingUtilsPanel)
    
def unregister():
    bpy.utils.unregister_class(makeMeshWholeOperator)
    bpy.utils.unregister_class(centerSelectedVerticesOperator)
    bpy.utils.unregister_class(deleteHalfMeshOperator)
    bpy.utils.unregister_class(dissolveEdgeOperator)
    bpy.utils.unregister_class(naModelingUtilsPanel)
