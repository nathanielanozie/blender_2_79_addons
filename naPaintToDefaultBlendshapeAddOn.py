#this is a tool to help modify shapekeys using painted weights. example used to paint out eyelids from smile shape key
#modify use at your own risk

#last modified
#111921 -- changed name from naPaintBlendshapeAddOn to naPaintToDefaultBlendshapeAddOn 
#made into single file addon and added some directions. 
#fixed error when paint all of side to zero
#added ability to zero out right side of multiple shapes
#added zero blendshape ability to ui

bl_info = {
    "name":"paint blendshape weights to default",
    "description":"example used to paint out eyelids from smile blendshape made in ZBrush",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)    
}

import bpy
import re

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )

from bpy.props import(
    StringProperty,
    PointerProperty
    )

class defaultBlendshapeProperties(PropertyGroup):
    blendshapes = StringProperty(
        name = "blendshapes",
        description = "optional specific blendshapes to edit space separated. (shapekey names cant have spaces)"
    )
    

class paintBSWeightsOperator(Operator):
    """first select blendshape then last the default mesh. it creates a naPnt_ mesh to be used for painting
    """
    bl_idname = "obj.paintbsweights" #needs to be all lowercase
    bl_label = "1.paintBSWeights"
    bl_options = {"REGISTER"}

    def execute(self, context):
        paintBSWeights(context)
        return {'FINISHED'}
        
class doItOperator(Operator):
    """paint weights on the created mesh then click this button to see result
    """
    bl_idname = "obj.doit"
    bl_label = "2.doIt"
    bl_options = {"REGISTER"}

    def execute(self, context):
        #self.report({'INFO'}, "context.selected_objects: %s" %context.selected_objects )
        previewShape(context)
        return {'FINISHED'}
        
class cleanUpOperator(Operator):
    """clean up after done with edited shape
    """
    bl_idname = "obj.cleanup"
    bl_label = "3.cleanUp"
    bl_options = {"REGISTER"}

    def execute(self, context):
        cleanUp(context)
        return {'FINISHED'}
        


class setBSSideToDefaultOperator(Operator):
    """with a selected mesh with shapekeys in object mode. if no blendshapes specified sets all .L ending blendshapes right side to default
    """
    bl_idname = "obj.setdefaultblendshape" #needs to be all lowercase
    bl_label = "set blendshape side to default"
    bl_options = {"REGISTER"}

    def execute(self, context):
        blendshapes_arg = context.scene.defaultblendshape_prop.blendshapes
        blendshapes = []
        if blendshapes_arg:
            blendshapes = blendshapes_arg.split(' ')
        mesh = context.selected_objects[0].name
        print("mesh>>>",mesh)
        print("blendshapes>>>",blendshapes)
        setToDefaultBlendshapesSide( side = 'R', mesh = mesh, blendshapes = blendshapes)
        return {'FINISHED'}


class setBSCenterToDefaultOperator(Operator):
    """with a selected mesh with shapekeys in object mode. if no blendshapes specified sets all .R ending blendshapes center to default
    """
    bl_idname = "obj.setcenterdefaultblendshape" #needs to be all lowercase
    bl_label = "set right blendshapes center to default"
    bl_options = {"REGISTER"}

    def execute(self, context):
        blendshapes_arg = context.scene.defaultblendshape_prop.blendshapes
        blendshapes = []
        if blendshapes_arg:
            blendshapes = blendshapes_arg.split(' ')
        mesh = context.selected_objects[0].name
        print("mesh>>>",mesh)
        print("blendshapes>>>",blendshapes)
        setToDefaultCenter( side = 'R', mesh = mesh, blendshapes = blendshapes)
        return {'FINISHED'}

class naPaintBlendshapePanel(Panel):
    bl_label = "naPaintToDefaultBlendshape Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    #bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "for painting blendshape to default")
        layout.operator( "obj.paintbsweights")
        layout.operator( "obj.doit")
        layout.operator( "obj.cleanup")
        layout.label(text = "-"*100 )
        
        layout.label(text = "for setting blendshape side to default")
        layout.prop( context.scene.defaultblendshape_prop, "blendshapes", text = "blendshapes" )
        
        layout.operator( "obj.setdefaultblendshape")
        layout.operator( "obj.setcenterdefaultblendshape")
        layout.label(text = "-"*100 )
        
def register():
    bpy.utils.register_class(paintBSWeightsOperator)
    bpy.utils.register_class(doItOperator)
    bpy.utils.register_class(cleanUpOperator)
    bpy.utils.register_class(setBSSideToDefaultOperator)
    bpy.utils.register_class(setBSCenterToDefaultOperator)
    bpy.utils.register_class(naPaintBlendshapePanel)
    
    bpy.utils.register_class(defaultBlendshapeProperties)
    bpy.types.Scene.defaultblendshape_prop = PointerProperty( type = defaultBlendshapeProperties )
   
   
def unregister():
    bpy.utils.unregister_class(paintBSWeightsOperator)
    bpy.utils.unregister_class(doItOperator)
    bpy.utils.unregister_class(cleanUpOperator)
    bpy.utils.unregister_class(setBSSideToDefaultOperator)
    bpy.utils.unregister_class(setBSCenterToDefaultOperator)
    bpy.utils.unregister_class(naPaintBlendshapePanel)

    bpy.utils.unregister_class(defaultBlendshapeProperties)
    del bpy.types.Scene.defaultblendshape_prop
    
    
if __name__ == "__main__":
    register()
    



def previewShape(context = None):
    """
    sculpt new blendshape using painted weights
    assumes painted mesh is selected
    it assumes a painted mesh is available with same name as shape mesh with _naPaint suffix
    
    """
    if not context.active_object:
        print("requires paint mesh selected")
        return
        
    paintMeshName = context.active_object.name
    
    if not bpy.data.objects.get(paintMeshName):
        print("cannot find paint mesh %s. first click paint weight button" %paintMeshName)
        return

    pattern = re.compile(".*naPnt_(.*)_naPnt_(.*)")
    if not pattern.match(paintMeshName):
        print("cannot find default and blendshape from painted mesh name")
        return
    patternGroups = pattern.match(paintMeshName).groups()
    if not patternGroups or len(patternGroups) != 2:
        print("cannot find default and blendshape from painted mesh name")
        return
        
    defaultMeshObj = bpy.data.objects[patternGroups[0]]
    bsMeshObj = bpy.data.objects[patternGroups[1]]
    
    print("using defaultMesh:%s reference shape:%s painted weights:%s" %(defaultMeshObj.name,bsMeshObj.name,paintMeshName) )

    weightsObj = bpy.data.objects[paintMeshName]
    newBS = weightsObj #maybe in future make another mesh for newBS
    wObj = weightsObj
    
    #get new position for vertex
    #set vertex position on newBS
    for i in range(len(wObj.data.vertices)):
        wt = 0.0
        #if no vertex group weight should be zero. this happens if remove verts from vertex group created
        if len(wObj.data.vertices[i].groups) == 1:
            wt = wObj.data.vertices[i].groups[0].weight
        posx = wt*bsMeshObj.data.vertices[i].co[0]+(1-wt)*defaultMeshObj.data.vertices[i].co[0]
        posy = wt*bsMeshObj.data.vertices[i].co[1]+(1-wt)*defaultMeshObj.data.vertices[i].co[1]
        posz = wt*bsMeshObj.data.vertices[i].co[2]+(1-wt)*defaultMeshObj.data.vertices[i].co[2]
        
        newBS.data.vertices[i].co[0] = posx
        newBS.data.vertices[i].co[1] = posy
        newBS.data.vertices[i].co[2] = posz

def paintBSWeights(context = None):
    """
    returns mesh to paint weights for blendshape
    assumes first selected is shape
    second selected is default mesh
    """
    #get selection
    selected = context.selected_objects
    if not len(selected) == 2:
        print("please select shape then default mesh")
        return
    defaultMeshObj = context.active_object
    selected.remove(defaultMeshObj)
    bsMeshObj = selected[0]
    ###    
    
    paintMeshName = 'naPnt_%s_naPnt_%s'%(defaultMeshObj.name,bsMeshObj.name)
    if bpy.data.objects.get(paintMeshName):
        print("painted mesh for selection already exists doing nothing")
        return
        
    weightsObj = duplicateMesh( context, defaultMeshObj)
    #rename it so we can keep track whether it was made already
    weightsObj.name = paintMeshName
    weightsObj.data.name = paintMeshName
    
    #bboxy = defaultMeshObj.dimensions.y
    #weightsObj.location = [0,-(bboxy+0.25*bboxy),0] #using y, and using bounding box to place new bs
    makeObjActive(context,weightsObj)
    
    #create vertex group for weights
    vgrp = weightsObj.vertex_groups.new(name='naPnt')
    verts = []
    for vert in weightsObj.data.vertices:
        verts.append(vert.index)
    vgrp.add(verts,0.0,'ADD') #by default non of blendshape used

    bpy.ops.paint.weight_paint_toggle()
    
    return weightsObj

def cleanUp(context = None):
    """
    removes vertex group created, cleans up name
    assumes painted mesh is selected
    """
    if not context.active_object:
        print("requires paint mesh selected")
        return
        
    obj = context.active_object

    removeVertexGroupsFromObj(obj)
    #bpy.ops.paint.weight_paint_toggle() #get out of paint mode
    #rename mesh
    simpleName = obj.name.split('naPnt_')[-1]+'_New'
    obj.name = simpleName
    obj.data.name = simpleName
    
def duplicateMesh(context, sourceObj=None):
    """
    return new mesh (ex: bpy.data.objects['Plane.001']) given sourceObj ex:bpy.data.objects['Plane'] and context bpy.context
    """
    if not sourceObj:
        return
    scn = context.scene
    srcObj = sourceObj #bpy.data.objects['Plane'] #change this
    
    newObj = srcObj.copy()
    newObj.data = srcObj.data.copy()
    newObj.animation_data_clear()
    scn.objects.link(newObj)
    
    return newObj
    
def makeObjActive(context,obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select=True
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    
def removeVertexGroupsFromObj(obj):
    for vgroup in obj.vertex_groups:
        obj.vertex_groups.remove(vgroup)
        


def setToDefaultBlendshapesSide( side = 'R', mesh = None, blendshapes = []):
    """ex: zero out right side of multiple shapes
    side - side that should get set to default. default is right side of face or screen left
    mesh - mesh object name that has all shapekeys we want to edit
    blendshapes - (optional) blendshape names we wish to edit. if empty it edits all blendshapes ending with .L
    
    1. given mesh with all .L blendshapes
    2. get all .L blendshapes
    3. for each ex .L blendshape  use basis default to set position of all verts on right side
    """
    #assumes mesh has all shapekeys we wish to edit and in object mode with no blendshapes isolated
    
    blendshape_names = []
    if blendshapes:
        blendshape_names = blendshapes
    else:
        left_side_shps = [shp.name for shp in bpy.data.objects[mesh].data.shape_keys.key_blocks if shp.name.endswith('.L')]
        blendshape_names = left_side_shps
    
    if not blendshape_names:
        print("could not find any blendshapes to edit. either add suffix like .L to blendshapes or provide specific blendshape names in text field")
        
    #for each ex .L blendshape  use basis default to set position of all verts on right side
    for shp in blendshape_names:
        for vert_id, shp_key_point in enumerate( bpy.data.objects[mesh].data.shape_keys.key_blocks[shp].data ):
            should_edit_vert = False #should this vertex be set to default position
            
            if side == 'R' and shp_key_point.co.x < 0.0: #vertex on screen left
                should_edit_vert = True
            elif side == 'L' and shp_key_point.co.x > 0.0: #vertex on screen right
                should_edit_vert = True
                
            if not should_edit_vert:
                continue
                
            default_pos = bpy.data.objects[mesh].data.shape_keys.key_blocks['Basis'].data[vert_id].co #vert_id is the vertex index
            #does the actual changing of shapekey vertex position
            shp_key_point.co = default_pos
        
        
def setToDefaultCenter( side = 'R', mesh = None, blendshapes = []):
    """ex: zero out center of multiple shapes
    side - side whose center should get set to default. default is right side blendshapes
    mesh - mesh object name that has all shapekeys we want to edit
    blendshapes - (optional) blendshape names we wish to edit. if empty it edits all blendshapes ending with .L
    
    """
    #assumes mesh has all shapekeys we wish to edit and in object mode with no blendshapes isolated
    
    blendshape_names = []
    if blendshapes:
        blendshape_names = blendshapes
    else:
        shps = []
        if side == 'R':
            shps = [shp.name for shp in bpy.data.objects[mesh].data.shape_keys.key_blocks if shp.name.endswith('.R')]
        else:
            shps = [shp.name for shp in bpy.data.objects[mesh].data.shape_keys.key_blocks if shp.name.endswith('.L')]  
        blendshape_names = shps
    
    if not blendshape_names:
        print("could not find any blendshapes to edit. either add suffix like .L to blendshapes or provide specific blendshape names in text field")
    
    is_center_epsilon = 0.00001 #how far away from zero is still considered a center vertex
    
    #get vert_id of center vertices from Basis shape
    center_vert_ids = []
    for vert_id, shp_key_point in enumerate( bpy.data.objects[mesh].data.shape_keys.key_blocks['Basis'].data ):
        if abs(shp_key_point.co.x) < is_center_epsilon: #vertex in center
            center_vert_ids.append(vert_id)
        
        
    #for each ex .R blendshape  use basis default to set position of all verts on center
    for shp in blendshape_names:
        for vert_id, shp_key_point in enumerate( bpy.data.objects[mesh].data.shape_keys.key_blocks[shp].data ):

            if not vert_id in center_vert_ids:
                continue
                
            default_pos = bpy.data.objects[mesh].data.shape_keys.key_blocks['Basis'].data[vert_id].co #vert_id is the vertex index
            
            #print("shp %s setting position >> %s" %(shp,default_pos) )
            
            #does the actual changing of shapekey vertex position
            shp_key_point.co = default_pos
            
            

"""need imp to reload script
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/naBlendShape')

import naPaintToDefaultBlendshapeAddOn as mod
import imp
imp.reload(mod)
#bpy.app.debug=True #temporary

#mod.setToDefaultBlendshapesSide(mesh = 'Plane', blendshapes = ['Key 1'] )

mod.setToDefaultBlendshapesSide(mesh = 'Plane')
"""

    
#inspired by:
#https://blenderartists.org/t/batch-delete-vertex-groups-script/449881/7
#https://blender.stackexchange.com/questions/7412/how-to-rename-selected-objects-using-python
#https://blenderartists.org/t/how-to-test-if-an-object-exists/566990
#https://blender.stackexchange.com/questions/8459/get-blender-x-y-z-and-bounding-box-with-script
#https://blender.stackexchange.com/questions/109700/how-to-clean-weight-groups-by-script
#https://blender.stackexchange.com/questions/26852/python-move-object-on-local-axis
#https://blender.stackexchange.com/questions/45099/duplicating-a-mesh-object