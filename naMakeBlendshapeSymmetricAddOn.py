#tool to help symmetrize a mesh. useful for when work on just one half of face and want to changes on other side too


#last modified
#070321 -- added addon. ready to be tested on more complex face meshes
#051921 -- started working on tool



bl_info = {
    "name":"make mesh symmetric tool",
    "description":"make mesh symmetric",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}


import bpy


#simple ui with single button and a few text fields
from bpy.props import(
    StringProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class SymmetrizeMeshOperator(Operator):
    """make mesh symmetric in X axis. requires a default mesh object name and a posed mesh object name.
    requires to be in object mode.
    """
    bl_idname = "obj.do_symmetrizemesh"
    bl_label = "Make Mesh Symmetric"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        #get text field input
        meshDefault = context.scene.symmetrizemesh_prop.meshDefault
        meshPosed = context.scene.symmetrizemesh_prop.meshPosed
    
        self.report({'INFO'}, "Starting Symmetrize Mesh ...")
        naMakeBlendshapeSymmetric(defaultMeshName = meshDefault, posedMeshName = meshPosed, mirrorAxis = 0) #could make mirrorAxis an option in ui. currently assuming x is correct axis
        self.report({'INFO'}, "Completed Symmetrize Mesh")
        return {'FINISHED'}


class SymmetrizeMeshPanel(Panel):
    bl_label = "Symmetrize Mesh Panel"
    bl_space_type = "VIEW_3D" #for helping with scene selections in tool
    bl_region_type = "UI"
    
    def draw(self, context):
        
        #here we add textfields and button to ui
        #
        layout = self.layout
        layout.label(text = "Symmetrize Mesh tool")
        
        #2 text fields in a row
        #text fields
        layout.prop( context.scene.symmetrizemesh_prop, "meshDefault", text = "Default Mesh" )
        layout.prop( context.scene.symmetrizemesh_prop, "meshPosed", text = "Posed Mesh" )
        #button
        layout.operator( "obj.do_symmetrizemesh")
        
class SymmetrizeMeshProperties(PropertyGroup):
    #here we make each textfield
    meshDefault = StringProperty(
        name = "meshDefault",
        description = "Default Mesh name. its the data object name"
        )

    meshPosed = StringProperty(
        name = "meshPosed",
        description = "Posed Mesh name. its the data object name"
        )
    
def register():
    bpy.utils.register_class(SymmetrizeMeshOperator)
    bpy.utils.register_class(SymmetrizeMeshPanel)
    bpy.utils.register_class(SymmetrizeMeshProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.symmetrizemesh_prop = PointerProperty(
        type = SymmetrizeMeshProperties
        )

def unregister():
    bpy.utils.unregister_class(SymmetrizeMeshOperator)
    bpy.utils.unregister_class(SymmetrizeMeshPanel)
    bpy.utils.unregister_class(SymmetrizeMeshProperties)
    del bpy.types.Scene.symmetrizemesh_prop
    
if __name__ == "__main__":
    register()

    
    
#start tool code here
def naMakeBlendshapeSymmetric(defaultMeshName = '', posedMeshName = '', mirrorAxis = 0):
    """
    this should be able to make both sides of blendshape/shape key symmetric on the posed mesh.
    assumes your posed mesh is external that is not in shapekey list yet. (todo add support for in shapekey list editing)
    TODO: edit duplicate of posed mesh
    mirrorAxis: 0 for x,1 for y,2 for z
    """
    def isObjectNameExist( objName = '' ):
        if objName not in bpy.data.objects:
            print('cannot find {} in data objects. please check spelling'.format(objName))
            return False
        return True
        
    #validate input
    if not isObjectNameExist(defaultMeshName):
        return
    if not isObjectNameExist(posedMeshName):
        return
    
    ###first figure out correspondence between source and destination
    #ex {2: 0, 3: 1, 6: 4, 7: 5} says source vertex index 2's mirror index is 0 etc
    blendshapeInfo = {}
    defaultObj = bpy.data.objects[defaultMeshName]
    for v in defaultObj.data.vertices:
        #store key only if vertex world position in source side
        sourcePosition = v.co
        if sourcePosition[mirrorAxis] > 0: #0,1,2 : x,y,z
            sourceVertex = v.index
            #print('source vertex: '+str(sourceVertex))
            #print('source vertex: %d pos: %d %d %d' %(sourceVertex, sourcePosition[0], sourcePosition[1], sourcePosition[2]) )
            #loop all vertices of mesh to find vertex on destination side
            for v1 in defaultObj.data.vertices:
                #if all positions same and negative value for destination side, its a mirror save it
                xx = [0,1,2] #will hold all but source side index
                xx.remove(mirrorAxis)
                pos = v1.co
                if pos[mirrorAxis] == -sourcePosition[mirrorAxis]:
                    if pos[xx[0]] == sourcePosition[xx[0]] and pos[xx[1]] == sourcePosition[xx[1]]:
                        #found a mirror, mirror side is negative source side and all other positions are same
                        destinationVertex = v1.index
                        #print('destination vertex: %d pos: %d %d %d' %(destinationVertex, pos[0], pos[1], pos[2]) )
                        blendshapeInfo[sourceVertex] =  destinationVertex
    #print("blendshapeInfo")
    #print(blendshapeInfo)
    #########
    
    
    
    ###now actual do vertex movement
    posedObj = bpy.data.objects[posedMeshName]
    
    #assuming posedObj.data.vertices[i].index = i #not sure whether this is always true
    
    for sourceVertexIndex in blendshapeInfo:
        #we want to edit mirror side by making it the source position with one axis negated
        sourcePosition = posedObj.data.vertices[sourceVertexIndex].co
        m = [1,1,1]
        m[mirrorAxis] = -1
        mirrorPosition = [ sourcePosition[0]*m[0], sourcePosition[1]*m[1], sourcePosition[2]*m[2] ]
        destinationVertexIndex = blendshapeInfo[sourceVertexIndex]
        #actually move mirror side
        posedObj.data.vertices[destinationVertexIndex].co = mirrorPosition
    #########
    
    

"""need imp to reload script
import sys
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/naBlendShape')
import naMakeBlendshapeSymmetric as mod
import imp
imp.reload(mod)

mod.naMakeBlendshapeSymmetric(defaultMeshName = 'defaultFace', posedMeshName = 'posedFace', mirrorAxis = 0)  
"""