#modify use at your own risk
#snippets for face modeling/rigging
"""need imp to reload script
import bpy
import sys
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/snippets/modeling')

import naModelingUtils as mod
import imp
imp.reload(mod)
mod.deleteHalfMesh(bpy.context.selected_objects[0]) #default deletes -x side of selected face mesh
#mod.makeMeshWhole(bpy.context.selected_objects[0])
#mod.centerSelectedVertices(bpy.context.selected_objects[0])
"""
#last update: 022220 - added so delete halfmesh supports mesh not at origin

import bpy
import bmesh

def makeMeshWhole(obj):
    """default mirror from +x to -x of selected mesh, assumes no mirror modifiers on mesh to start
    """
    bpy.ops.object.modifier_add(type='MIRROR')
    bpy.ops.object.modifier_apply(modifier='Mirror') 
    
def centerSelectedVertices(obj):
    """
    default uses x. assumes obj at origin
    """
    selectedObj = obj #for addon passing in bpy.context.selected_objects[0] instead of bpy.context.object
    bm = bmesh.from_edit_mesh(selectedObj.data)
    
    for vert in bm.verts:
        if vert.select == True:
            #print('Found Selected Vertex %s' %vert.index)
            vert.co[0] = 0.0
    
    selectedObj.data.update() #to see change in viewport
    
    
def deleteHalfMesh(obj):
    """
    default deletes -x side of selected mesh. standalone need give it bpy.context.object for selected object
    """
    #get current position
    curpos = ()
    curpos = (obj.location.x,obj.location.y,obj.location.z)
    
    #put obj at origin
    setLocation(obj,(0,0,0))
    
    selectedObj = obj #bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all( action='DESELECT')
    bpy.ops.mesh.select_mode(type='FACE')
    
    
    bm = bmesh.from_edit_mesh(selectedObj.data)
    for face in bm.faces:
        faceWorldPos = selectedObj.matrix_world*face.calc_center_median() #calc_center_median same as face.center using obj.data.polygons
        #[0] > 0.0 would be delete right half of mesh
        #[1] < 0.0 would be delete in y direction
        if faceWorldPos[0] < 0.0:
            face.select = True
            
    bm.select_flush(True)
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
            
    #restore location
    setLocation(obj,curpos)
    
def setLocation(obj,pos):
    """ does location only. pos tuple (2.3,0,0) """
    obj.location.x = pos[0]
    obj.location.y = pos[1]
    obj.location.z = pos[2]
    
    
def doDissolveEdges():
    """assumes in edit mode with some edges selected
    """
    bpy.ops.mesh.dissolve_edges()


#inspired by:
#https://blender.stackexchange.com/questions/44506/how-to-apply-a-several-modifiers-with-python-but-not-necessarily-all-modifiers
#https://blender.stackexchange.com/questions/55484/when-to-use-bmesh-update-edit-mesh-and-when-mesh-update
#https://blenderartists.org/t/select-and-translate-vertices-with-python/555961/2
#https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/mirror.html
#https://blender.stackexchange.com/questions/44981/face-center-returning-wrong-location
#https://blender.stackexchange.com/questions/40974/how-to-delete-all-faces-with-distance-to-other-object

