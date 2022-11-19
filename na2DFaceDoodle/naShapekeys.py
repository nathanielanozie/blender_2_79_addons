#this module has methods and class for setting up simple blendshapes with drivers

import bpy
from math import pi
from . import naControls
from . import naUtils

def makeShapekeys( browName, mouthName, rootBoneName, armatureObj ):
    """does all the setting up of shapekeys
    currently assumes only need to blendshape a brow mesh and a mout mesh.
    meshes have 4 verts with assumptions on the indices
    """
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
        boneShape = naControls.drawCircleShape(drvShapeName)
        bgBoneShape = naControls.drawRectangleShape(bgShapeName)
        #rotate shape so control facing us in xz plane
        naControls.rotateShape(boneShape,amount=pi/2,axis='x')
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

"""
def drawTextBone(armatureObj=None,rootBoneName=None,textStr=None,position=(0,0,0) ):
    #add bones to armature using text as custom shape
    
    textObjShape = drawTextShape(textStr,(0,0,0))
    textBoneName = textStr+'%s_%s_%s_bone' %(position[0],position[1],position[2])  #assuming these are unique
    arm_obj = armatureObj
    #make bone and add textobj as custom shape
    print("adding text bone")
    if not naUtils.isExistBone(armatureObj.name,textBoneName):
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
"""

def drawBones(armatureObj=None,xzPos=(),boneBaseName=None,rootBoneName=None,boneShape=None,bgBoneShape=None):
    """draws 2 bones using position and armature
    """
    driverBone = None
    bgBone = None
    arm_obj = armatureObj
    armatureName = armatureObj.name
    
    driverBoneName = boneBaseName+'_driver'
    bgBoneName = boneBaseName+'_bg'
    if naUtils.isExistBone(armatureName,driverBoneName) or naUtils.isExistBone(armatureName,bgBoneName):
        print("bones already created exiting")
        return (None,None)
        
    print('drawBones')    
    print('found armature >> creating bones')
    ###animated bone
    if not naUtils.isExistBone(armatureName,driverBoneName):
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


    

