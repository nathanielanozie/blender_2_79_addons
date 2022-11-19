#learning some shape key tools on a robot face. two brows a mouth


#last modified
#052422 -- added ability to add animator controls to shape head
#       -- added ability for having material per character
#051622 -- added ability to add stretching 
#050722,0508 -- added overall head bone, added ability to make multiple heads
#062521 -- added material creation.
#062421 -- work on converting to addon.
#052921 -- added generating the facial mesh. working on creating materials for face mesh
#051421 -- working on initial release 
# 1. needs to be in addon form
# 2. generate face mesh
# 3. create guides for creating the shape keys

import imp
import bpy
import bmesh
from math import pi
from mathutils import Matrix

bl_info = {
    "name":"cube face primitve features shapekey rig",
    "description":"cube face primitve features shapekey rig",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

from bpy.props import(
    StringProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


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
        initGlobalConstants(character = char)
        generateRobotFaceMesh(context = context)
        return {'FINISHED'}

class generateGuidesOperator(Operator):
    """generates guides for rigs. to be placed by user
    """
    bl_idname = "obj.generateguides" #needs to be all lowercase
    bl_label = "generateGuides"
    bl_options = {"REGISTER"}

    def execute(self, context):
        char = context.scene.facerig_prop.char_name
        initGlobalConstants(character = char)
        generateGuides()
        return {'FINISHED'}
        
class generateRigOperator(Operator):
    """generates simple cube mesh with primitive geo shapekeys and controls
    """
    bl_idname = "obj.generaterig" #needs to be all lowercase
    bl_label = "generateRig"
    bl_options = {"REGISTER"}

    def execute(self, context):
        char = context.scene.facerig_prop.char_name
        initGlobalConstants(character = char)        
        doIt(context = context)
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
        
def register():
    bpy.utils.register_class(generateMeshOperator)
    bpy.utils.register_class(generateRigOperator)
    bpy.utils.register_class(generateGuidesOperator)
    bpy.utils.register_class(naSimpleRobotFaceRigPanel)
    bpy.utils.register_class(FaceRigProperties)
    
    #here we name the property that holds all our textfields
    bpy.types.Scene.facerig_prop = PointerProperty(
        type = FaceRigProperties
        )
    
def unregister():
    bpy.utils.unregister_class(generateMeshOperator)
    bpy.utils.unregister_class(generateRigOperator)
    bpy.utils.unregister_class(generateGuidesOperator)
    bpy.utils.unregister_class(naSimpleRobotFaceRigPanel)
    bpy.utils.unregister_class(FaceRigProperties)
    del bpy.types.Scene.facerig_prop

if __name__ == "__main__":
    register()
    


FC_CHAR_NAME = "TestChar"
FC_ARMATURE_NAME = "{}_simpleRobot".format(FC_CHAR_NAME)
FC_ROOT_BONE_NAME = "{}_simpleRobotRoot".format(FC_CHAR_NAME) 
FACEGEO_NAMES = {'brow':'{}_brow'.format(FC_CHAR_NAME),'eye':'{}_eye'.format(FC_CHAR_NAME),'mouth':'{}_mouth'.format(FC_CHAR_NAME),'head':'{}_head'.format(FC_CHAR_NAME)}#{'brow':'brow','eye':'eye','mouth':'mouth','head':'head'}

FC_HEAD_STRETCH_BONE_NAMES = {  'mid': {'name':'{}_STMid'.format(FC_CHAR_NAME), 'position':{'head':(0,0,0),'tail':(0,0,2)} },
                        'hi': {'name':'{}_STHi'.format(FC_CHAR_NAME), 'position':{'head':(0,0,2),'tail':(0,0,3)} },
                        'lo': {'name':'{}_STLo'.format(FC_CHAR_NAME), 'position':{'head':(0,0,-2),'tail':(0,0,0)} }
                     }
FC_HEAD_BONE_NAME = { 'head': {'name':'{}_head'.format(FC_CHAR_NAME), 'position':{'head':(0,0,0),'tail':(0,0,3)}  } }
FC_HEAD_GUIDE_HEAD_NAME = '{}_headGuide'.format(FC_CHAR_NAME)
FC_HEAD_GUIDE_TAIL_NAME = '{}_tailGuide'.format(FC_CHAR_NAME)

def initGlobalConstants(character = "Test"):
    """use the ui inputs to create global variable constants
    """
    global FC_CHAR_NAME, FC_ARMATURE_NAME, FC_ROOT_BONE_NAME, FACEGEO_NAMES, FC_HEAD_STRETCH_BONE_NAMES, FC_HEAD_BONE_NAME, FC_HEAD_GUIDE_HEAD_NAME, FC_HEAD_GUIDE_TAIL_NAME  
    
    FC_CHAR_NAME = character
    FC_ARMATURE_NAME = "{}_simpleRobot".format(FC_CHAR_NAME)
    FC_ROOT_BONE_NAME = "{}_simpleRobotRoot".format(FC_CHAR_NAME) 
    FACEGEO_NAMES = {'brow':'{}_brow'.format(FC_CHAR_NAME),'eye':'{}_eye'.format(FC_CHAR_NAME),'mouth':'{}_mouth'.format(FC_CHAR_NAME),'head':'{}_head'.format(FC_CHAR_NAME)}#{'brow':'brow','eye':'eye','mouth':'mouth','head':'head'}
    FC_HEAD_STRETCH_BONE_NAMES = {  'mid': {'name':'{}_STMid'.format(FC_CHAR_NAME), 'position':{'head':(0,0,0),'tail':(0,0,2)} },
                            'hi': {'name':'{}_STHi'.format(FC_CHAR_NAME), 'position':{'head':(0,0,2),'tail':(0,0,3)} },
                            'lo': {'name':'{}_STLo'.format(FC_CHAR_NAME), 'position':{'head':(0,0,-2),'tail':(0,0,0)} }
                         }
    FC_HEAD_BONE_NAME = { 'head': {'name':'{}_head'.format(FC_CHAR_NAME), 'position':{'head':(0,0,0),'tail':(0,0,3)}  } }        
    
    #head rig guides empties
    FC_HEAD_GUIDE_HEAD_NAME = '{}_headGuide'.format(FC_CHAR_NAME)
    FC_HEAD_GUIDE_TAIL_NAME = '{}_tailGuide'.format(FC_CHAR_NAME)

    #if guide exists update the globals for other bones using guide results
    if FC_HEAD_GUIDE_HEAD_NAME in bpy.data.objects and FC_HEAD_GUIDE_TAIL_NAME in bpy.data.objects:
        headPos = tuple( bpy.data.objects[FC_HEAD_GUIDE_HEAD_NAME].location )
        tailPos = tuple( bpy.data.objects[FC_HEAD_GUIDE_TAIL_NAME].location )
        #update head bone global
        FC_HEAD_BONE_NAME = { 'head': {'name':'{}_head'.format(FC_CHAR_NAME), 'position':{'head':headPos,'tail':tailPos}  } }
        #update head stretch bone globals
        stretchZOffset = 2 #how much should ends of stretch bones extend from head bone. might want this to be a parameter
        FC_HEAD_STRETCH_BONE_NAMES = {  'mid': {'name':'{}_STMid'.format(FC_CHAR_NAME), 'position':{'head':headPos,'tail':tailPos} },
                                'hi': {'name':'{}_STHi'.format(FC_CHAR_NAME), 'position':{'head':tailPos,'tail':(tailPos[0],tailPos[1],tailPos[2]+stretchZOffset)} },
                                'lo': {'name':'{}_STLo'.format(FC_CHAR_NAME), 'position':{'head':(headPos[0],headPos[1],headPos[2]-stretchZOffset),'tail':headPos} }
                             }
                         

##########################bone rigs used for face
def generateGuideHeadRig():
    """in ui guide should be two spheres for length of head bone. the stretch hi and tail should be an offset from head bone.
    """
    for guide in [FC_HEAD_GUIDE_HEAD_NAME,FC_HEAD_GUIDE_TAIL_NAME]:
        guideObj = bpy.data.objects.new( guide, None )
        bpy.context.scene.objects.link( guideObj )
        guideObj.empty_draw_size = 2
        guideObj.empty_draw_type = "SPHERE"
    
    bpy.data.objects[FC_HEAD_GUIDE_HEAD_NAME].location = (0,0,0) #using fixed position for creating guides
    bpy.data.objects[FC_HEAD_GUIDE_TAIL_NAME].location = (0,0,4)


def buildHeadStretch():
    """creates simple head stretch rig. assumes armature already created
    
    returns (low bone, bone with stretching, and end bone )
    """
    armatureName = FC_ARMATURE_NAME
    midBoneName = FC_HEAD_STRETCH_BONE_NAMES['mid']['name']
    midHeadPos = FC_HEAD_STRETCH_BONE_NAMES['mid']['position']['head']
    midTailPos = FC_HEAD_STRETCH_BONE_NAMES['mid']['position']['tail']
    hiBoneName = FC_HEAD_STRETCH_BONE_NAMES['hi']['name']
    hiHeadPos = FC_HEAD_STRETCH_BONE_NAMES['hi']['position']['head']
    hiTailPos = FC_HEAD_STRETCH_BONE_NAMES['hi']['position']['tail']
    loBoneName = FC_HEAD_STRETCH_BONE_NAMES['lo']['name']
    loHeadPos = FC_HEAD_STRETCH_BONE_NAMES['lo']['position']['head']
    loTailPos = FC_HEAD_STRETCH_BONE_NAMES['lo']['position']['tail']
    
    #create stretch bones
    UT_CreateBone( boneName = midBoneName, 
                    armatureName = armatureName, 
                    head = midHeadPos, 
                    tail = midTailPos, 
                    roll = 0 )
    UT_CreateBone( boneName = hiBoneName, 
                    armatureName = armatureName, 
                    head = hiHeadPos, 
                    tail = hiTailPos, 
                    roll = 0 )
    UT_CreateBone( boneName = loBoneName, 
                    armatureName = armatureName, 
                    head = loHeadPos, 
                    tail = loTailPos, 
                    roll = 0 )

    #do any needed bone parenting
    UT_ParentBone( bone = midBoneName, parent = loBoneName, armatureName = armatureName)

    #add stretch constraint
    UT_CreateStretch( bone = midBoneName,
                      endBone = hiBoneName,
                      armatureName = armatureName
                      )
                      
    #add controls to hi and low stretch bones - i think circles
    
    return loBoneName, midBoneName, hiBoneName
    
def buildHeadRig(useStretch = False):
    """assumes armature already created
    useStretch - whether or not using stretch in rig
    """
    armatureName = FC_ARMATURE_NAME
    headBoneName = FC_HEAD_BONE_NAME['head']['name']
    headPos = FC_HEAD_BONE_NAME['head']['position']['head']
    tailPos = FC_HEAD_BONE_NAME['head']['position']['tail']
    
    #create head bone
    UT_CreateBone( boneName = headBoneName, 
                    armatureName = armatureName, 
                    head = headPos, 
                    tail = tailPos, 
                    roll = 0 )

    if useStretch:
        #create head stretch rig
        low, mid, end = buildHeadStretch()
        
        #parent head stretch bones to overall head mover
        for bn in [low,end]:
            UT_ParentBone( bone = bn, parent = headBoneName, armatureName = armatureName)

        #parent face to mid stretch bone
        parentFaceToBone( bone = mid )
        
        #hide backend bones
        UT_PutInLayer( items = [mid], layer = 32, armatureName = armatureName )
        
        #add controls to head stretch bones
        shpLow = addShapeToBone( shapeName = low+'_ctl', 
                            boneName = low, 
                            shape = 'circle', 
                            scale = 4, 
                            armatureName = armatureName )
        shpEnd = addShapeToBone( shapeName = end+'_ctl', 
                            boneName = end, 
                            shape = 'circle', 
                            scale = 4, 
                            armatureName = armatureName )        
        #put shp in different layer
        UT_PutObjectInLayer( items = [shpLow,shpEnd], layer = 19 )        
        
    else:
        #parent face to head bone instead
        parentFaceToBone( bone = headBoneName )
        
    #add control to head bone - i think cube    
    shp = addShapeToBone( shapeName = headBoneName+'_ctl', 
                        boneName = headBoneName, 
                        shape = 'cube', 
                        scale = 1, 
                        armatureName = armatureName )
    #put shp in different layer
    UT_PutObjectInLayer( items = [shp], layer = 19 )

        
def addShapeToBone( shapeName = None,
                    boneName = None,
                    shape = 'cube', 
                    scale = 1, 
                    armatureName = None ):
    """adds a control shape to given bone
    inputs are string shape and bone name. a string shape type supported cube or circle. and string armature name
    """
    if not shapeName or not boneName:
        print("requires a shape and bone name")
        return
    if shape not in ['cube','circle','square']:
        print("requires any shape type of: cube, circle, square")
        return
    if not armatureName:
        print("requires armature string name")
        return
    bpy.ops.object.mode_set(mode='OBJECT')        
    boneShape = None
    #if shape name exists use it
    if shapeName in bpy.data.objects:
        boneShape = bpy.data.objects[shapeName]
    else:
        #do drawing of shape
        if shape == 'cube':
            boneShape = drawCubeShape(name = shapeName)
        elif shape == 'circle':
            boneShape = drawCircleShape(name = shapeName)            
        
    arm_obj = bpy.data.objects[armatureName]
    arm_obj.pose.bones[boneName].custom_shape = boneShape #custom shape is poseBone property
    arm_obj.pose.bones[boneName].custom_shape_scale = scale
    #show_wire property of Bone (editbone)
    arm_obj.data.bones[boneName].show_wire=True
    
    return shapeName

def parentFaceToBone( bone = None ):
    """parent all face geometry to given bone
    """
    armatureName = FC_ARMATURE_NAME
    geo = []
    for key, ge in FACEGEO_NAMES.items():
        if key in ['eye','brow']:
            geo.append(ge+'.L')
            geo.append(ge+'.R')
        else:
            geo.append(ge)
        
    print("geometry>>>")
    print(geo)
    
    #assumes all geo exists. assumes bone in armature
    for g in geo:
        if g not in bpy.data.objects:
            continue
        geoObj = bpy.data.objects[g]
        armObj = bpy.data.objects[armatureName]
        bpy.ops.object.mode_set(mode='POSE')
        #boneObj = armObj.pose.bones.get(bone)
        armObj.data.bones.active = armObj.data.bones[bone]
        geoObj.select = True
        bpy.ops.object.parent_set(type = 'BONE')

    
######################


def UT_CreateBone( boneName = 'testBone', armatureName = None, head = (0,0,0), tail = (0,0,2), roll = 0 ):
    #assumes armature exists. assumes bone doesnt exist
    armObj = bpy.data.objects[armatureName]
    bpy.context.scene.objects.active = armObj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False) #need to be in edit mode to add bones    
    
    if armObj == bpy.context.active_object and bpy.context.mode == "EDIT_ARMATURE":
        bone = armObj.data.edit_bones.new(boneName)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

def UT_ParentBone( bone = None, parent = None, armatureName = None ):
    """parent given bone to given parent bone. inputs are strings
    """
    armObj = bpy.data.objects[armatureName]
    bpy.context.scene.objects.active = armObj    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    armObj.data.edit_bones[bone].parent = armObj.data.edit_bones[parent]

def UT_CreateStretch( bone = None, endBone = None, armatureName = None ):
    """create stretchto constraint on given bone aiming at given end bone
    bone - bone string name with the stretchto constraint
    endBone - end bone, stretching aims at this bone
    armatureName - armature string name
    
    #currently only supporting an endbone
    """
    arm_obj = bpy.data.objects[armatureName]
    bpy.context.scene.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='OBJECT')
    
    constraint = arm_obj.pose.bones[bone].constraints.new('STRETCH_TO')
    constraint.target = arm_obj
    constraint.subtarget = endBone

def UT_PutObjectInLayer( items = [], layer = 20 ):
    """put given items into specified int layer. i think max is 20
    """ 
    layerValues = [False]*20
    layerValues[layer-1] = True
    
    for it in items:
        itObj = bpy.data.objects[it] #assumes it exists
        itObj.layers = layerValues
        
def UT_PutInLayer( items = [], layer = 32, armatureName = None ):
    """put given bones into specified int layer. i think max is 32
    """ 
    layerValues = [False]*32
    layerValues[layer-1] = True

    armObj = bpy.data.objects[armatureName]
    bpy.context.scene.objects.active = armObj    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    for it in items:
        itObj = armObj.data.edit_bones[it] #assumes it exists
        itObj.layers = layerValues


def generateGuides():
    """generate all guides to be used in rig
    """
    generateGuideHeadRig()



def doIt(context):
    """build robot face shape key rig
    """
    browName = '{}'.format( FACEGEO_NAMES['brow'] )
    mouthName = '{}'.format( FACEGEO_NAMES['mouth'] )
    

    #i think used for all slider
    armatureName = FC_ARMATURE_NAME #'simpleRobot'
    rootBoneName = FC_ROOT_BONE_NAME #'simpleRobotRoot'
    armatureObj = makeFaceArmature(name = armatureName, rootBoneName = rootBoneName )
    
    ####for first shape key mesh----------
    #pos and neg shape name for slider, position for slider
    ##brow lf
    faceMesh = browName+'.L'
    browLeft = brow(faceMesh,
                        updnAmount = (0.8,0.9),
                        fwdBckAmount = (.8,.5),
                        inVerts = [2,0],
                        outVerts = [3,1]) 
    data = [
    {'meshes' : browLeft['updnAll'], 'pos':(2,0,4) },
    {'meshes' : browLeft['fwdbckAll'], 'pos':(4,0,4) },
    {'meshes' : browLeft['updnIn'], 'pos':(6,0,4) },
    {'meshes' : browLeft['updnOut'], 'pos':(8,0,4) }
    ]
    """
    data = [\
    {'meshes' : {'neg':'browDn.R','pos':'browUp.R'}, 'pos':(2,0,2) },
    {'meshes' : {'pos':'browFwd.R','neg':'browBck.R'}, 'pos':(4,0,2) }
    ]
    """
    makeRigSliders(faceMesh,armatureObj,rootBoneName,data)
    ###end first shape key mesh --------------
    
    ###brow rt
    faceMesh = browName+'.R'
    browRight = brow(faceMesh,side='rt',
                        updnAmount = (0.8,0.9),
                        fwdBckAmount = (.8,.5),
                        inVerts = [2,0],
                        outVerts = [3,1]) 
    data = [
    {'meshes' : browRight['updnAll'], 'pos':(-2,0,4) },
    {'meshes' : browRight['fwdbckAll'], 'pos':(-4,0,4) },
    {'meshes' : browRight['updnIn'], 'pos':(-6,0,4) },
    {'meshes' : browRight['updnOut'], 'pos':(-8,0,4) }
    ]
    makeRigSliders(faceMesh,armatureObj,rootBoneName,data)
    ########end second mesh
    
    ###lip
    faceMesh = mouthName
    lipShapes = lip(faceMesh,
                    updnAmount = (0.7,0.7),
                    fwdBckAmount = (.8,.5),
                    lfVerts = [3,1],
                    rtVerts = [2,0] ) 
    data = [
    {'meshes' : lipShapes['updnAll'], 'pos':(2,0,-4) },
    {'meshes' : lipShapes['fwdbckAll'], 'pos':(-2,0,-4) },
    {'meshes' : lipShapes['updnLf'], 'pos':(2,0,-12) },
    {'meshes' : lipShapes['updnRt'], 'pos':(-2,0,-12) }
    ]
    makeRigSliders(faceMesh,armatureObj,rootBoneName,data)
    

    #so have overall mover and possibly ability to stretch head
    buildHeadRig(useStretch=True)
    
    #hide anything that needs to be hidden
    #ex hide guides used
    UT_PutObjectInLayer( items = [FC_HEAD_GUIDE_HEAD_NAME,FC_HEAD_GUIDE_TAIL_NAME], layer = 19 )
    

def makeRigSliders(faceMesh=None,armatureObj=None,rootBoneName=None,data=None):
    #draw ui
    #boneControlsText = getBoneControlsText(armatureObj,rootBoneName)
    boneControls = getBoneControls(armatureObj,rootBoneName,data,faceMesh)
    
    #connect sliders to blendshapes
    for boneCtrl in boneControls:
        boneCtrl.connectShapeKey(faceMesh)
        

#up +z
#fwd -x (for character left brow)
def lip(meshName=None,
            updnAmount = (0.7,0.7),
            fwdBckAmount = (.8,.5),
            lfVerts = [],
            rtVerts = [] ):
    """
    #lfVerts are vertex ids on character's left side lip corner
    amounts ex:updnAmount tells how shape should be sculpted. how many units is up shape dn shape
    """
    if meshName not in bpy.data.objects:
        print("cannot find mesh %s" %meshName)
        return
        
    result = {}
    
    meshObj = bpy.data.objects[meshName]
    #assuming mesh exists and no shapekeys on it
    basis = meshObj.shape_key_add('Basis')
    basis.interpolation='KEY_LINEAR'

    vids = range(0,len(meshObj.data.vertices))
    #updnAll
    upAllShape = meshObj.shape_key_add('upAllShape')
    upAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        upAllShape.data[vid].co.z += updnAmount[0]

    dnAllShape = meshObj.shape_key_add('dnAllShape')
    dnAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        dnAllShape.data[vid].co.z -= updnAmount[1]
    
    #fwdbckAll
    fwdAllShape = meshObj.shape_key_add('fwdAllShape')
    fwdAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        fwdAllShape.data[vid].co.x -= fwdBckAmount[0]

            
    bckAllShape = meshObj.shape_key_add('bckAllShape')
    bckAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        bckAllShape.data[vid].co.x += fwdBckAmount[1]
 
                        
    #handle character lf corner/ rt corner shapes
    vids = lfVerts
    upLfShape = meshObj.shape_key_add('upLfShape')
    upLfShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        upLfShape.data[vid].co.z += updnAmount[0]

    dnLfShape = meshObj.shape_key_add('dnLfShape')
    dnLfShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        dnLfShape.data[vid].co.z -= updnAmount[1]

    #rt corner
    vids = rtVerts
    upRtShape = meshObj.shape_key_add('upRtShape')
    upRtShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        upRtShape.data[vid].co.z += updnAmount[0]

    dnRtShape = meshObj.shape_key_add('dnRtShape')
    dnRtShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        dnRtShape.data[vid].co.z -= updnAmount[1]
        
        
    result['updnAll'] = {'pos':'upAllShape','neg':'dnAllShape'}
    result['fwdbckAll'] = {'pos':'fwdAllShape','neg':'bckAllShape'}
    #
    result['updnLf'] = {'pos':'upLfShape','neg':'dnLfShape'}
    result['updnRt'] = {'pos':'upRtShape','neg':'dnRtShape'}
    
    return result            



def brow(meshName=None,
                    side='lf',
                    updnAmount = (0.5,0.5),
                    fwdBckAmount = (.8,.5),
                    inVerts = [],
                    outVerts = []
                    ):

    if meshName not in bpy.data.objects:
        print("cannot find mesh %s" %meshName)
        return
        
    result = {} #{ 'updnAll':{},'fwdbckAll':{} } #this is for all. later add for in/out verts
    
    sideSuffix ='.L'
    if side == 'rt':
        sideSuffix = '.R'
    meshObj = bpy.data.objects[meshName]
    #assuming mesh exists and no shapekeys on it
    basis = meshObj.shape_key_add('Basis')
    basis.interpolation='KEY_LINEAR'
    
    vids = range(0,len(meshObj.data.vertices))
    #updnAll
    upAllShape = meshObj.shape_key_add('upAllShape'+sideSuffix)
    upAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        upAllShape.data[vid].co.z += updnAmount[0]

    dnAllShape = meshObj.shape_key_add('dnAllShape'+sideSuffix)
    dnAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        dnAllShape.data[vid].co.z -= updnAmount[1]
    
    #fwdbckAll
    fwdAllShape = meshObj.shape_key_add('fwdAllShape'+sideSuffix)
    fwdAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        #get fwdbck to work depending on side of brow
        if side == 'lf':
            fwdAllShape.data[vid].co.x -= fwdBckAmount[0]
        else:
            fwdAllShape.data[vid].co.x += fwdBckAmount[0]
            
    bckAllShape = meshObj.shape_key_add('bckAllShape'+sideSuffix)
    bckAllShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        if side == 'lf':
            bckAllShape.data[vid].co.x += fwdBckAmount[1]
        else:
            bckAllShape.data[vid].co.x -= fwdBckAmount[1]
            
        
    #handle in/out shapes (currently using same shapekey deltas as all brow)
    vids = inVerts
    upInShape = meshObj.shape_key_add('upInShape'+sideSuffix)
    upInShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        upInShape.data[vid].co.z += updnAmount[0]

    dnInShape = meshObj.shape_key_add('dnInShape'+sideSuffix)
    dnInShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        dnInShape.data[vid].co.z -= updnAmount[1]

    vids = outVerts
    upOutShape = meshObj.shape_key_add('upOutShape'+sideSuffix)
    upOutShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        upOutShape.data[vid].co.z += updnAmount[0]

    dnOutShape = meshObj.shape_key_add('dnOutShape'+sideSuffix)
    dnOutShape.interpolation = 'KEY_LINEAR'
    for vid in vids:
        dnOutShape.data[vid].co.z -= updnAmount[1]
    
    
    
    result['updnAll'] = {'pos':'upAllShape'+sideSuffix,'neg':'dnAllShape'+sideSuffix}
    result['fwdbckAll'] = {'pos':'fwdAllShape'+sideSuffix,'neg':'bckAllShape'+sideSuffix}
    
    #corners
    result['updnIn'] = {'pos':'upInShape'+sideSuffix,'neg':'dnInShape'+sideSuffix}
    result['updnOut'] = {'pos':'upOutShape'+sideSuffix,'neg':'dnOutShape'+sideSuffix}
    
    return result





####################
#for building simple facial sliders for blendshapes
#
def getBoneControls(armatureObj = None, rootBoneName=None, data=[], faceMesh=None):
    """this draws slider returns slider FaceBoneControl objects.
    """
    boneControls = []

    #bone shapes
    boneShape, bgBoneShape = getUiControlShapes()
        
    for i in range(0,len(data)):
        boneCtrl = FaceUiBoneControl(**data[i],armatureObj=armatureObj,rootBoneName = rootBoneName,boneShape=boneShape,bgBoneShape=bgBoneShape, faceMesh = faceMesh)
        boneControls.append(boneCtrl)
    
    return boneControls

def getUiControlShapes():
    drvShapeName = 'naDriverShape'
    bgShapeName = 'naBgShape'
    #so only rotate controls once when created
    if not drvShapeName in bpy.data.objects:
        boneShape = drawCircleShape(drvShapeName)
        bgBoneShape = drawRectangleShape(bgShapeName)
        #rotate shape so control facing us in xz plane
        rotateShape(boneShape,amount=pi/2,axis='x')
    else:
        boneShape = bpy.data.objects[drvShapeName]
        bgBoneShape = bpy.data.objects[bgShapeName]
    return boneShape, bgBoneShape
    
class FaceUiBoneControl(object):
    """an object that represents a blendshape slider
    """
    def __init__(self,**kwargs):
        self.armatureObj = kwargs.get('armatureObj')
        self.rootBoneName = kwargs.get('rootBoneName')
        self.meshes = kwargs.get('meshes')
        self.pos = kwargs.get('pos')
        self.boneShape = kwargs.get('boneShape')
        self.bgBoneShape =kwargs.get('bgBoneShape')
        self.faceMesh = kwargs.get('faceMesh')
        
        self.driverBone = None #used for circlular shape to be animated
        self.bgBone = None #used for square bg shape
        
        
        self.draw()
            
    def draw(self):
        xzPos = (self.pos[0],self.pos[2])
        boneBaseName = self.faceMesh+self.meshes['pos']+'_anim'#self.rootBoneName+self.meshes['pos']+'_anim'#self.name+'_'+self.param+'_'+self.side+'_posXZ_%s_%s' %(xzPos[0],xzPos[1])
        self.driverBone, self.bgBone = drawBones(self.armatureObj,xzPos,boneBaseName,self.rootBoneName,self.boneShape,self.bgBoneShape)
        #make bg unselectable
        print(self.armatureObj.data)
        self.armatureObj.data.bones[self.bgBone].hide_select = True
        
    def connectShapeKey(self, faceMesh=None):
        """input default base mesh to add shape keys to
        """
        makeDriverForPosNegShapeKey(faceMesh=faceMesh,
                        drvArmature = self.armatureObj.name,
                        drvBoneName=self.driverBone,
                        posShapeKey=self.meshes['pos'],
                        negShapeKey=self.meshes['neg'])


def drawTextBone(armatureObj=None,rootBoneName=None,textStr=None,position=(0,0,0) ):
    """add bones to armature using text as custom shape
    """
    textObjShape = drawTextShape(textStr,(0,0,0))
    textBoneName = textStr+'%s_%s_%s_bone' %(position[0],position[1],position[2])  #assuming these are unique
    arm_obj = armatureObj
    #make bone and add textobj as custom shape
    print("adding text bone")
    if not isExistBone(armatureObj.name,textBoneName):
        bpy.context.scene.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        
        if arm_obj == bpy.context.active_object and bpy.context.mode == "EDIT_ARMATURE":
            print("adding text bone >>")
            #anim bone
            textBone = arm_obj.data.edit_bones.new(textBoneName)#arm_data_obj.edit_bones.new(driverBoneName)
            textBone.head = (position[0],position[1],position[2])
            textBone.tail = (position[0],position[1],position[2]+1)
            
            # exit edit mode to save bones so they can be used in pose mode
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            
            print("start text parenting")
            arm_obj.data.edit_bones[textBoneName].parent = arm_obj.data.edit_bones[rootBoneName]
            print("finished text parenting")
            
            print("start adding text custom shape")
            arm_obj.pose.bones[textBoneName].custom_shape = textObjShape
            print("finished adding text custom shape")
            
    print("finished adding text bone")
    #parent bone to root
        
def drawBones(armatureObj=None,xzPos=(),boneBaseName=None,rootBoneName=None,boneShape=None,bgBoneShape=None):
    """draws 2 bones using position and armature
    """
    driverBone = None
    bgBone = None
    arm_obj = armatureObj
    armatureName = armatureObj.name
    
    driverBoneName = boneBaseName+'_driver'
    bgBoneName = boneBaseName+'_bg'
    if isExistBone(armatureName,driverBoneName) or isExistBone(armatureName,bgBoneName):
        print("bones already created exiting")
        return (None,None)
        
    print('drawBones')    
    print('found armature >> creating bones')
    ###animated bone
    if not isExistBone(armatureName,driverBoneName):
        bpy.context.scene.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False) #need to be in edit mode to add bones
        
        if arm_obj == bpy.context.active_object and bpy.context.mode == "EDIT_ARMATURE":
            print("adding anim bone")
            #anim bone
            driverBone = arm_obj.data.edit_bones.new(driverBoneName)#arm_data_obj.edit_bones.new(driverBoneName)
            driverBone.head = (xzPos[0],0,xzPos[1])#driverBone.head = (xzPos[0],0,xzPos[1])
            driverBone.tail = (xzPos[0],1,xzPos[1])#driverBone.tail = (xzPos[0],0,xzPos[1]+1)
            
            print("adding bg bone")
            #bg bone
            bgBone = arm_obj.data.edit_bones.new(bgBoneName)
            bgBone.head = (xzPos[0],0,xzPos[1])
            bgBone.tail = (xzPos[0],0,xzPos[1]+3)
        
            # exit edit mode to save bones so they can be used in pose mode
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            print("doing nothing not in armature drawing context")
        #"""
        #add shape to bones
        print("adding shape to bones")
        #should be one shape for all bones
        #boneShape = drawCircleShape('naDriverShape')
        #bgBoneShape = drawRectangleShape('naBgShape')
        
        #bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        arm_obj.pose.bones[driverBoneName].custom_shape = boneShape #custom shape is poseBone property
        arm_obj.pose.bones[driverBoneName].custom_shape_scale = 4 #to make it easier to see while testing
        #show_wire property of Bone (editbone)
        arm_obj.data.bones[driverBoneName].show_wire=True
        
        arm_obj.pose.bones[bgBoneName].custom_shape = bgBoneShape
        arm_obj.data.bones[bgBoneName].show_wire=True
        print("finished adding shapes")
        #make bg shape skinnier
        #arm_obj.pose.bones[bgBoneName].scale[0] = 0.25
        
        #parent driver bone to bg bone
        print("doing parenting")
        bpy.context.scene.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        if arm_obj == bpy.context.active_object and bpy.context.mode == "EDIT_ARMATURE":
            print("parenting bone >>")
            arm_obj.data.edit_bones[driverBoneName].parent = arm_obj.data.edit_bones[bgBoneName]
            arm_obj.data.edit_bones[bgBoneName].parent = arm_obj.data.edit_bones[rootBoneName]
            #driverBone.parent = bgBone
        print("finished parenting bone")
        #"""
    print("finished drawing bone")
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("finished drawbones")
    return (driverBoneName,bgBoneName)
    
    
def isExistBone(armatureName, bone):
    result = False
    bpy.context.scene.objects.active = bpy.data.objects[armatureName]
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for boneObj in bpy.data.armatures[armatureName].edit_bones:
        if boneObj.name == bone:
            result = True
            break
    return result
    
def makeFaceArmature(name,rootBoneName):
    #if armature doesnt exist make it
    print('makeFaceArmature')
    
    if name in bpy.data.objects:
        print('armature alread created %s skipping' %(name))
        return bpy.data.objects[name]
        
    arm_dat = bpy.data.armatures.new(name)
    arm_obj = bpy.data.objects.new(name,arm_dat)
    arm_obj.data = arm_dat
    
    scene = bpy.context.scene
    scene.objects.link(arm_obj)
    scene.objects.active = arm_obj #need to select armature to put it in edit mode
    scene.update()
    
    #make bone
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    print('debug second generation of rig errors out. this is data.armatures name >> %s' %name)
    bone = arm_dat.edit_bones.new(rootBoneName)
    bone.head = (0,0,0)
    bone.tail = (0,0,1)
    bpy.ops.object.editmode_toggle()
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return arm_obj

def makeDriverForPosNegShapeKey(faceMesh=None,
                        drvArmature = None,
                        drvBoneName=None,
                        posShapeKey=None,
                        negShapeKey=None):
    """create driver on ex: tz 1 0 to turnon/off meshes. assumes faceMesh has shape key names given.
    all inputs given are strings
    """
    #if faceMesh object doesnt have shape keys exit
    #if armature doesnt have drv bone exit
    print('makeDriverForPosNegShapeKey')
    faceObj = bpy.context.scene.objects[faceMesh]
    drvArmatureObj = bpy.data.objects[drvArmature]
    
    #pos shape key
    driver = faceObj.data.shape_keys.key_blocks[posShapeKey].driver_add("value").driver
    driver.type = "SCRIPTED"
    driver.expression= '0 if drvloc < 0 else drvloc'
    var = driver.variables.new()
    var.name = "drvloc"
    var.type="SINGLE_PROP" #not sure if this is needed
    var.targets[0].id = drvArmatureObj
    var.targets[0].data_path = drvArmatureObj.pose.bones[drvBoneName].path_from_id()+".location.z" #using z location of bone to drive blendshape
    
    #neg shape key
    driver = faceObj.data.shape_keys.key_blocks[negShapeKey].driver_add("value").driver
    driver.type = "SCRIPTED"
    driver.expression= '0 if drvloc > 0 else drvloc*-1.0'
    var = driver.variables.new()
    var.name = "drvloc"
    var.type="SINGLE_PROP" #not sure if this is needed
    var.targets[0].id = drvArmatureObj
    var.targets[0].data_path = drvArmatureObj.pose.bones[drvBoneName].path_from_id()+".location.z" #using z location of bone to drive blendshape
  
"""
def getBoneControlsText(armatureObj=None,rootBoneName=None):
    #text for the simple facial ui. x is right z is up. it needs armature and rootbone name
    print("getBoneControlsText")
    #first column
    drawTextBone(armatureObj,rootBoneName,"up/dn",(-5,0,10) )
    drawTextBone(armatureObj,rootBoneName,"in/out",(-2.5,0,10) )
    
    #middle column
    drawTextBone(armatureObj,rootBoneName,"Brows",(0,0,8) )
    drawTextBone(armatureObj,rootBoneName,"LipCorner",(0,0,4) )
    drawTextBone(armatureObj,rootBoneName,"Mouth",(0,0,0) )
    
    #right column
    drawTextBone(armatureObj,rootBoneName,"up/dn",(5,0,10) )
    drawTextBone(armatureObj,rootBoneName,"in/out",(7.5,0,10) )
    
    print("finished getBoneControlsText")
"""








def drawTextShape(textStr = '', position=(0.0,0.0,0.0) ):
    """draw text mesh left aligned at position. position is tuple xyz"""
    #need to be in object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.data.body = textStr
    obj.matrix_world.translation = position
    #convert it to mesh object
    bpy.ops.object.convert(target="MESH")
    
    return obj

def getVertsEdgesFromSelected():
    """help for from_pydata creation of widgets. returns tuple verts and edges of selected
    """
    obj = bpy.context.object
    
    verts = []
    edges = []
    
    for i in range(0,len(obj.data.vertices)):
        verts.append( tuple(bpy.context.object.data.vertices[i].co)  )
    for i in range(0,len(obj.data.edges)):
        edges.append( (bpy.context.object.data.edges[i].vertices[0],bpy.context.object.data.edges[i].vertices[1])  )
        
    return verts,edges
    

def drawRectangleShape(name = None):
    """ draw square mesh no faces. if it exists does nothing"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = bpy.context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges = ([(-0.25, -1.0, 0.0), (0.25, -1.0, 0.0), (-0.25, 1.0, 0.0), (0.25, 1.0, 0.0)], [(2, 0), (0, 1), (1, 3), (3, 2)])
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    
    return obj
    

def drawCubeShape(name = None):
    """ draw cube mesh no faces. if it exists does nothing"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = bpy.context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges = ([(-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0)], [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1)])
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    return obj
    
def drawSquareShape(name = None):
    """ draw square mesh no faces. if it exists does nothing"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = bpy.context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges = ([(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (-1.0, 1.0, 0.0), (1.0, 1.0, 0.0)], [(2, 0), (0, 1), (1, 3), (3, 2)])
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    
    return obj


def drawCircleShape(name = None):
    
    scene = bpy.context.scene
    
    bpy.ops.object.mode_set(mode='OBJECT')
    #do nothing if shape already exists
    if name in bpy.data.objects.keys():
        return bpy.data.objects[name]
        

    meshObj = bpy.data.meshes.new("Mesh")
    boneShape = bpy.data.objects.new(name, meshObj)
    scene.objects.link(boneShape)
    
    #new bmesh
    bm = bmesh.new()
    #load in a mesh
    bm.from_mesh(meshObj)
    
    #create circle
    bmesh.ops.create_circle(bm,cap_ends=False,diameter=0.1,segments=8)
    
    #write back to mesh
    bm.to_mesh(meshObj)
    bm.free()
    
    #set active selection
    #scene.objects.active = boneShape
    #boneShape.select = True
    scene.update()
    
    #boneShape.layers = [False]*19+[True] #move to different layer
    
    return boneShape
    
def rotateShape(shapeObj,amount = 0.0, axis = 'x'):
    """
    rotate shape in axis. amount in radians
    """
    if axis == 'x':
        rotateAxis = (True,False,False)
    elif axis == 'y':
        rotateAxis = (False,True,False)
    elif axis == 'z':
        rotateAxis = (False,False,True)
        
    bpy.context.scene.objects.active = shapeObj
    bpy.ops.object.mode_set(mode='EDIT',toggle = False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.rotate(value = amount,axis = rotateAxis)
    bpy.ops.object.mode_set(mode='OBJECT',toggle=False)
    
    
    
    

################################
###helper for drawing robot face
################################
def drawRobotFaceMeshPart(context, name = None, shapeData = None):
    """ draw mesh. if it exists does nothing. it takes name of shape and tuple with lists for verts,edges,faces"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges,faces = shapeData
    meshData = obj.data
    meshData.from_pydata(verts,edges,faces)
    meshData.update()
    
    return obj

def getVertsEdgesFacesFromSelected(context):
    """help for from_pydata creation of meshes. returns tuple verts,edges,faces of selected
    """
    if not context.selected_objects:
        print("need to select mesh object in object mode with all transforms applied")
        return
        
    obj = context.selected_objects[0]
    
    verts = []
    edges = []
    faces = []
    
    for i in range(0,len(obj.data.vertices)):
        pos = context.object.data.vertices[i].co
        verts.append( tuple( (round(pos[0],4),round(pos[1],4),round(pos[2],4)) )  )
    for i in range(0,len(obj.data.edges)):
        edges.append( (context.object.data.edges[i].vertices[0],context.object.data.edges[i].vertices[1])  )
    for i in range(0,len(obj.data.polygons)):
        facei = []
        #to support various polygons not always four sided
        for v in range(0,len(context.object.data.polygons[i].vertices) ):
            facei.append( context.object.data.polygons[i].vertices[v] )
        faces.append(tuple(facei))
        
    return verts,edges,faces


def generateRobotFaceMesh(context = bpy.context, character = "TestChar"):
    """this draws the robot face mesh. and adds materials.
    needs to check that names for geometry dont exist
    """
    
    #brows
    browl = ([(1.7577, 0.0, 1.3652), (4.5342, 0.0, 1.3652), (1.7577, 0.0, 2.1959), (4.5342, 0.0, 2.1959)], [(2, 0), (0, 1), (1, 3), (3, 2)], [(0, 1, 3, 2)])
    drawRobotFaceMeshPart(context=context, name = '{}.L'.format( FACEGEO_NAMES['brow'] ), shapeData = browl )
    browr = ([(-1.7577, 0.0, 1.3652), (-4.5342, 0.0, 1.3652), (-1.7577, 0.0, 2.1959), (-4.5342, 0.0, 2.1959)], [(2, 0), (0, 1), (1, 3), (3, 2)], [(0, 1, 3, 2)])
    drawRobotFaceMeshPart(context=context, name = '{}.R'.format( FACEGEO_NAMES['brow'] ), shapeData = browr )

    #eyes
    eyel = ([(3.7955, 0.0, 0.1671), (3.1459, 0.0, 0.8166), (3.1459, 0.0, -0.4825), (2.4964, 0.0, 0.1671)], [(2, 0), (0, 1), (1, 3), (3, 2)], [(0, 1, 3, 2)])
    drawRobotFaceMeshPart(context=context, name = '{}.L'.format( FACEGEO_NAMES['eye'] ), shapeData = eyel )
    eyer = ([(-3.7955, 0.0, 0.1671), (-3.1459, 0.0, 0.8166), (-3.1459, 0.0, -0.4825), (-2.4964, 0.0, 0.1671)], [(2, 0), (0, 1), (1, 3), (3, 2)], [(0, 1, 3, 2)])
    drawRobotFaceMeshPart(context=context, name = '{}.R'.format( FACEGEO_NAMES['eye'] ), shapeData = eyer )
    
    #mouth
    mouth = ([(-2.0174, 0.0, -3.6893), (2.0174, 0.0, -3.6893), (-2.0174, 0.0, -2.3891), (2.0174, 0.0, -2.3891), (0.0, 0.0, -3.6893), (0.0, 0.0, -2.3891)], [(2, 0), (4, 1), (1, 3), (5, 2), (0, 4), (3, 5), (4, 5)], [(4, 1, 3, 5), (0, 4, 5, 2)])
    drawRobotFaceMeshPart(context=context, name = '{}'.format( FACEGEO_NAMES['mouth'] ), shapeData = mouth )
    
    #head
    head = ([(-5.0, 0.0548, 4.1438), (-5.0, 0.0548, -4.1438), (-5.0, 5.7728, 4.1438), (-5.0, 5.7728, -4.1438), (5.0, 0.0548, 4.1438), (5.0, 0.0548, -4.1438), (5.0, 5.7728, 4.1438), (5.0, 5.7728, -4.1438)], [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1)], [(0, 1, 3, 2), (2, 3, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (2, 6, 4, 0), (7, 3, 1, 5)])
    drawRobotFaceMeshPart(context=context, name = '{}'.format( FACEGEO_NAMES['head'] ), shapeData = head )
    
    #texture model
    textureModel()


def textureModel():
    """create and assign materials to face geometry
    """
    def _isMaterialCreated( matname = '' ):
        if not matname:
            return False
        for mat in bpy.data.materials:
            if mat.name == matname:
                return True
        return False
    
    #need to exit if face geometry doesnt exist    
        
    #create head material
    headMatName = '{0}_naSimpleFaceHeadMaterial'.format(FC_CHAR_NAME)
    headmat = bpy.data.materials.new(headMatName) if not _isMaterialCreated(headMatName) else bpy.data.materials[headMatName]
    #create face features material
    partsMatName = '{0}_naSimpleFacePartsMaterial'.format(FC_CHAR_NAME)
    partsmat = bpy.data.materials.new(partsMatName) if not _isMaterialCreated(partsMatName) else bpy.data.materials[partsMatName]
    
    #choose colors for materials
    headmat.diffuse_color = (0.044,0.211,1.0)
    partsmat.diffuse_color = (0.034,0.598,0.405)
    
    ##assign materials
    parts = [
        '{}.L'.format( FACEGEO_NAMES['brow'] ),
        '{}.R'.format( FACEGEO_NAMES['brow'] ),
        '{}.L'.format( FACEGEO_NAMES['eye'] ),
        '{}.R'.format( FACEGEO_NAMES['eye'] ),
        '{}'.format( FACEGEO_NAMES['mouth'] )
         ]
    head = '{}'.format( FACEGEO_NAMES['head'] )
    
    #head
    #not checking if material already assigned
    bpy.data.objects[head].data.materials.append(headmat)
    
    #parts
    for part in parts:
        bpy.data.objects[part].data.materials.append(partsmat)
    

"""
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/riggingTools/faces')

import naSimpleRobotFaceRigAddon as mod
import imp
imp.reload(mod)
#bpy.app.debug=True #temporary
mod.generateRobotFaceMesh(context = bpy.context)
mod.doIt(bpy.context)
"""


    
##inspired by
#Nathan Vegdahl's rigify
#https://blender.stackexchange.com/questions/145472/blender-2-8-python-convert-text-to-mesh
#https://blender.stackexchange.com/questions/143256/animate-text-bpy-ops-transform-translate
#https://stackoverflow.com/questions/17388912/blender-script-how-to-write-to-text-object
#https://blender.stackexchange.com/questions/15072/scripting-modifying-an-object-in-edit-mode
#https://blender.stackexchange.com/questions/51684/python-create-custom-armature-without-ops
#https://blenderscripting.blogspot.com/2011/06/using-frompydata.html
#https://blender.stackexchange.com/questions/51684/python-create-custom-armature-without-ops
#https://blender.stackexchange.com/questions/91400/how-to-add-circle-to-existing-mesh-by-python-script
#https://blender.stackexchange.com/questions/68907/add-armature-at-each-vertex-location
#https://github.com/StefanUlbrich/RobotEditor/blob/master/armatures.py
#https://blender.stackexchange.com/questions/51684/python-create-custom-armature-without-ops
#https://blenderartists.org/t/making-a-mirror-copy/411641/3         editmode p to separate selected verts after mirror modifier
#https://blenderartists.org/t/restrict-selection-script-help/512403/2
#https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
#https://blender.stackexchange.com/questions/112776/how-do-i-prevent-object-from-moving-when-parenting-object-to-a-bone
#https://blender.stackexchange.com/questions/134250/set-active-bone-in-pose-mode-from-python-script
