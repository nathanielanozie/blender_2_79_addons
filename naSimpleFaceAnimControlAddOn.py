#tool to create simple blendshape animator control
#naSimpleFaceAnimControlAddOn.py
#modify use at your own risk

import bpy
import bmesh
import math

bl_info = {
    "name":"blendshape control tool",
    "description":"help with creating blendshape animator control",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )

from bpy.props import(
    StringProperty,
    EnumProperty,
    PointerProperty
    )


class faceAnimControlProperties(PropertyGroup):
    
    ##for shapes supported
    up_shape = StringProperty(
        name = "up_shape",
        description = "shapekey name for up_shape"
        ) 

    dn_shape = StringProperty(
        name = "dn_shape",
        description = "shapekey name for dn_shape"
        ) 
    
    out_shape = StringProperty(
        name = "out_shape",
        description = "shapekey name for out_shape"
        ) 
    
    in_shape = StringProperty(
        name = "in_shape",
        description = "shapekey name for in_shape"
        ) 
    
    up_out_shape = StringProperty(
        name = "up_out_shape",
        description = "shapekey name for up_out_shape"
        )     

    up_in_shape = StringProperty(
        name = "up_in_shape",
        description = "shapekey name for up_in_shape"
        ) 
    
    dn_out_shape = StringProperty(
        name = "dn_out_shape",
        description = "shapekey name for dn_out_shape"
        ) 
    
    dn_in_shape = StringProperty(
        name = "dn_in_shape",
        description = "shapekey name for dn_in_shape"
        ) 
    ##
    
    face_mesh = StringProperty(
        name = "face_mesh",
        description = "face mesh name with shapekeys. the data object name"
        ) 

    bone_name = StringProperty(
        name = "bone_name",
        description = "name for animator control bone that drives blendshapes. it needs to be unique"
        ) 


    ##for switching background shapes
    shapesEnum = EnumProperty(
    name = "shapes_enum",
    description = "background shape options",
    items = [   ('Square',"Square",""),
                ('Vertical',"Vertical",""),
                ('Horizontal',"Horizontal","")
            ],
    default = 'Square'
        )
    ##


    ##for post corrective making
    corrective_shape = StringProperty(
        name = "corrective_shape",
        description = "shapekey name for corrective_shape"
        )
    corrective_driver_a_shape = StringProperty(
        name = "corrective_driver_a_shape",
        description = "shapekey name for corrective_driver_a_shape"
        )        
    corrective_driver_b_shape = StringProperty(
        name = "corrective_driver_b_shape",
        description = "shapekey name for corrective_driver_b_shape"
        )            
    ##



class makeFaceAnimControlOperator(Operator):
    """create blendshape animator control for given shapes
    """
    bl_idname = "obj.makefaceanimcontrol" #needs to be all lowercase
    bl_label = "makeFaceAnimControl"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene_prop = context.scene.faceanimcontrol_prop
        meshes = {  'up': scene_prop.up_shape , 
                    'dn': scene_prop.dn_shape ,
                    'out': scene_prop.out_shape ,
                    'in': scene_prop.in_shape , 
                    'up_out': scene_prop.up_out_shape , 
                    'up_in': scene_prop.up_in_shape ,
                    'dn_out': scene_prop.dn_out_shape ,
                    'dn_in': scene_prop.dn_in_shape}
        
        face_mesh = scene_prop.face_mesh
        if not face_mesh:
            self.report({'INFO'},"please provide a face that holds the blendshapes")
            return {'FINISHED'}
            
        bone_name = scene_prop.bone_name
        if not bone_name:
            self.report({'INFO'},"please provide name for animator control bone")
            return {'FINISHED'}
            
        createAnimFaceControl(context = bpy.context, face = face_mesh , meshes = meshes, bone_name = bone_name)
        return {'FINISHED'}
        
class mirrorFaceAnimControlOperator(Operator):
    """mirror blendshape animator control - you need to enter in all the .L blendshapes into ui for the source control.
    if just transfering over background size change from left to right i dont think the hole ui needs to be filled out.
    """
    bl_idname = "obj.mirrorfaceanimcontrol" #needs to be all lowercase
    bl_label = "mirrorFaceAnimControl"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene_prop = context.scene.faceanimcontrol_prop
        meshes = {  'up': scene_prop.up_shape , 
                    'dn': scene_prop.dn_shape ,
                    'out': scene_prop.out_shape ,
                    'in': scene_prop.in_shape , 
                    'up_out': scene_prop.up_out_shape , 
                    'up_in': scene_prop.up_in_shape ,
                    'dn_out': scene_prop.dn_out_shape ,
                    'dn_in': scene_prop.dn_in_shape}
        
        face_mesh = scene_prop.face_mesh
        if not face_mesh:
            self.report({'INFO'},"please provide a face that holds the blendshapes")
            return {'FINISHED'}
        
        #get selected bone and armature_name
        sel_bone = context.selected_pose_bones
        if not sel_bone or ('_bg' in sel_bone[0].name):
            self.report({'INFO'},"please select left side animator control pose bone to mirror")
            return {'FINISHED'}
        
        armature = context.selected_objects[0].name
        
        mirrorFaceControl(  face = face_mesh,
                        meshes = meshes,
                        bone_name = sel_bone[0].name,
                        armature = armature)

        return {'FINISHED'}        

class regenerateShapesOperator(Operator):
    """create shape curves to be used if none already exist
    """
    bl_idname = "obj.regenerateshapes" #needs to be all lowercase
    bl_label = "regenerateShapes"
    bl_options = {"REGISTER"}

    def execute(self, context):
        regenerateShapes()
        return {'FINISHED'}

class switchShapesOperator(Operator):
    """switch the selected bones shape to chosen. assumes in pose mode. should work with multiple selection
    """
    bl_idname = "obj.switchshapes" #needs to be all lowercase
    bl_label = "switchShapes"
    bl_options = {"REGISTER"}

    def execute(self, context):
        
        switchShapes(option = context.scene.faceanimcontrol_prop.shapesEnum)
        return {'FINISHED'}
        

class makeCorrectiveOperator(Operator):
    """make driver for corrective shape using two shapekeys by multiplying their weights.
    """
    bl_idname = "obj.makecorrective" #needs to be all lowercase
    bl_label = "makeCorrectivePost"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene_prop = context.scene.faceanimcontrol_prop
        
        face_mesh = scene_prop.face_mesh
        if not face_mesh:
            self.report({'INFO'},"please provide a face that holds the blendshapes")
            return {'FINISHED'}
            
        makeDriverForCorrectivePost(faceMesh=face_mesh, corrective = scene_prop.corrective_shape, shapekeys = [scene_prop.corrective_driver_a_shape,scene_prop.corrective_driver_b_shape] )
        return {'FINISHED'}

class makeInbetweenCorrectiveOperator(Operator):
    """make driver for an inbetween corrective shape using single shapekey driver_a driving corrective via its weights.
    the inbetween corrective is turned on when driver shapekey weight is at 0.5 and is off at 0 and 1 frames
    """
    bl_idname = "obj.makeinbetwncorrective" #needs to be all lowercase
    bl_label = "makeInbetweenCorrective"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene_prop = context.scene.faceanimcontrol_prop
        
        face_mesh = scene_prop.face_mesh
        if not face_mesh:
            self.report({'INFO'},"please provide a face that holds the blendshapes")
            return {'FINISHED'}
            
        createInbetweenBlendshape(face_mesh =face_mesh, blendshape = scene_prop.corrective_shape, driver_blendshape = scene_prop.corrective_driver_a_shape )
        return {'FINISHED'}
        
class naSimpleFaceAnimControlPanel(Panel):
    bl_label = "naSimpleFaceAnimControl Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        #layout.label(text = "for corrective making")
        layout.prop( context.scene.faceanimcontrol_prop, "up_shape", text = "up" )
        layout.prop( context.scene.faceanimcontrol_prop, "dn_shape", text = "dn" )
        layout.prop( context.scene.faceanimcontrol_prop, "out_shape", text = "out" )
        layout.prop( context.scene.faceanimcontrol_prop, "in_shape", text = "in" )
        layout.prop( context.scene.faceanimcontrol_prop, "up_out_shape", text = "up_out" )
        layout.prop( context.scene.faceanimcontrol_prop, "up_in_shape", text = "up_in" )
        layout.prop( context.scene.faceanimcontrol_prop, "dn_out_shape", text = "dn_out" )
        layout.prop( context.scene.faceanimcontrol_prop, "dn_in_shape", text = "dn_in" )
        layout.prop( context.scene.faceanimcontrol_prop, "face_mesh", text = "face" )
        layout.prop( context.scene.faceanimcontrol_prop, "bone_name", text = "bone" )
        
        layout.operator( "obj.makefaceanimcontrol")
        layout.operator( "obj.mirrorfaceanimcontrol")
        ##
        layout.label(text = "-"*50)
        layout.label(text = "for background shape customization")        
        layout.operator( "obj.regenerateshapes")
        layout.prop( context.scene.faceanimcontrol_prop, "shapesEnum", text = "shapeOptions" )
        layout.operator( "obj.switchshapes")
        layout.label(text = "-"*50)
        ##
        layout.label(text = "-"*50)
        layout.label(text = "post corrective making")
        layout.prop( context.scene.faceanimcontrol_prop, "corrective_shape", text = "corrective" )
        layout.prop( context.scene.faceanimcontrol_prop, "corrective_driver_a_shape", text = "corrective_driver_a" )
        layout.prop( context.scene.faceanimcontrol_prop, "corrective_driver_b_shape", text = "corrective_driver_b" )
        layout.prop( context.scene.faceanimcontrol_prop, "face_mesh", text = "face" )
        layout.operator( "obj.makecorrective")
        layout.operator( "obj.makeinbetwncorrective" )
        layout.label(text = "-"*50)
        ##        
        

def register():
    bpy.utils.register_class(makeFaceAnimControlOperator)
    bpy.utils.register_class(mirrorFaceAnimControlOperator)
    bpy.utils.register_class(regenerateShapesOperator)
    bpy.utils.register_class(switchShapesOperator)
    bpy.utils.register_class(makeCorrectiveOperator)    
    bpy.utils.register_class(makeInbetweenCorrectiveOperator)
    bpy.utils.register_class(naSimpleFaceAnimControlPanel)
    
    bpy.utils.register_class(faceAnimControlProperties)
    bpy.types.Scene.faceanimcontrol_prop = PointerProperty( type = faceAnimControlProperties )
    
def unregister():
    bpy.utils.unregister_class(makeFaceAnimControlOperator)
    bpy.utils.unregister_class(mirrorFaceAnimControlOperator)
    bpy.utils.unregister_class(regenerateShapesOperator)
    bpy.utils.unregister_class(switchShapesOperator)
    bpy.utils.unregister_class(makeCorrectiveOperator)  
    bpy.utils.unregister_class(makeInbetweenCorrectiveOperator)
    bpy.utils.unregister_class(naSimpleFaceAnimControlPanel)
    
    bpy.utils.unregister_class(faceAnimControlProperties)
    del bpy.types.Scene.faceanimcontrol_prop
    
if __name__ == "__main__":
    register()
    
##########end of addon part


def createAnimFaceControl(context = None,
                            face = None,
                            meshes = {},
                            bone_name = 'naTestBone',
                            side = 'L',
                            armature = 'naFCArmature',
                            root_bone = 'naFCRoot'
                            ):
    """this draws animator control for blendshapes
    face - data object name for face mesh with blendshapes
    meshes - dict for blendshape names ex {'up':'browUp.L','dn':'browDn.L'} supported keys are: up,dn,out and in
	side - so when make control to help with mirroring later options C, R or L
	bone_name - so can find bone later (without side suffix that will get added automatically)
	armature - data object name so could add blendshape controls to an existing potentially a weighted armature
	root_bone - name for root bone
    #
    """
    bone_controls = []
    
    face_mesh = face #None
    
    armature_obj = None
    rbone_name = None

    amt_name = armature
    rbone_name = root_bone
    
    #make container for anim controls if it doesnt exist
    if amt_name not in bpy.data.objects: #bpy.data.armatures:
        #make armature
        amt_dat = bpy.data.armatures.new(amt_name)
        amt_obj = bpy.data.objects.new(amt_name,amt_dat)
        scene = context.scene
        scene.objects.link(amt_obj)
        scene.objects.active = amt_obj #need to select armature
        scene.update()
    
        #make root bone
        amt_obj.select = True
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        rbone = bpy.data.armatures[amt_name].edit_bones.new(rbone_name)
        rbone.head = (0,0,0)
        rbone.tail = (0,1,0)
        
        
    armature_obj = bpy.data.objects[amt_name]
    
    #bone shapes - if get more 4 shapes might want to use dictionary instead
    boneShape, bgBoneShape_vertical, bgBoneShape_wide, bgBoneShape_horizontal = getUiControlShapes()
    
    #by default use the square for four shapes
    bgBoneShape = bgBoneShape_wide
    #print("using shape>> %s" %bgBoneShape )    
    
    #bone animator uses to control blendshapes
    anim_bone = bone_name
        
    #create slider and connect it to shapes    
    boneCtrl = FaceUiBoneControl(meshes=meshes, #how it gets the shapekeys to use
                    anim_bone = anim_bone,
                    armatureObj=armature_obj,
                    rootBoneName = rbone_name,
                    boneShape=boneShape,
                    bgBoneShape=bgBoneShape, 
                    faceMesh = face_mesh,
                    side = side
                    )
    
    
        

class FaceUiBoneControl(object):
    """an object that represents a blendshape slider
    """
    def __init__(self,**kwargs):
        self.armatureObj = kwargs.get('armatureObj')
        self.rootBoneName = kwargs.get('rootBoneName')
        self.meshes = kwargs.get('meshes')
        self.anim_bone = kwargs.get('anim_bone') 
        self.boneShape = kwargs.get('boneShape')
        self.bgBoneShape =kwargs.get('bgBoneShape')
        self.faceMesh = kwargs.get('faceMesh')
        self.side = kwargs.get('side')
        
        pos = (0,0,0)
        if self.side == 'L':
            pos = (2.0,0,0) #start left side anim controls a little in positive x
        self.pos = pos
                
        self.driverBone = None #used for circlular shape to be animated
        self.bgBone = None #used for square bg shape
        
        
        self.draw()
        self.connectShapeKey()
        
    def draw(self):
        xzPos = (self.pos[0],self.pos[2])
        boneBaseName = self.anim_bone
        
        #if bone was already created it uses existing bone and doesnt make anything new
        self.driverBone, self.bgBone = drawBones(self.armatureObj,xzPos,boneBaseName,self.rootBoneName,self.boneShape,self.bgBoneShape)
        
        #make bg unselectable
        #print(self.armatureObj.data)
        #self.armatureObj.data.bones[self.bgBone].hide_select = True
        
        #make bones undeformable
        for bone in [self.driverBone,self.bgBone]:
            bpy.data.objects[self.armatureObj.name].data.bones[bone].use_deform = False
        
    def connectShapeKey(self):
        """this setsup the drivers to get the animator control working with the shapekeys
        """
        connectShapeKeyHelper(  faceMesh = self.faceMesh,
                                meshes = self.meshes,
                                armature = self.armatureObj.name,
                                bone = self.driverBone)
       
def connectShapeKeyHelper(  faceMesh = '',
                            meshes = {},
                            armature = '',
                            bone = ''):
    """this setsup the drivers to get the animator control working with the shapekeys
    faceMesh - mesh with shapekeys
    meshes - dict with specific keys and values the shapekey names
    armature - data object name for armature with bone
    bone - anim driver bone name
    """
    if len(meshes) == 2:
        makeDriverForPosNegShapeKey(faceMesh=faceMesh,
                        drvArmature = armature,
                        drvBoneName=bone,
                        posShapeKey=meshes['up'],
                        negShapeKey=meshes['dn'])
    elif len(meshes) == 4:
        #needs support for 4way shape
        makeDriverForPosNegShapeKey(faceMesh=faceMesh,
                        drvArmature = armature,
                        drvBoneName=bone,
                        posShapeKey=meshes['up'],
                        negShapeKey=meshes['dn'],
                        axis='z')
        makeDriverForPosNegShapeKey(faceMesh=faceMesh,
                        drvArmature = armature,
                        drvBoneName=bone,
                        posShapeKey=meshes['out'],
                        negShapeKey=meshes['in'],
                        axis='x')
    elif len(meshes) > 4:
        #needs support 4way shape with additional shapes at corners
        makeDriverForPosNegShapeKey(faceMesh=faceMesh,
                        drvArmature = armature,
                        drvBoneName=bone,
                        posShapeKey=meshes['up'],
                        negShapeKey=meshes['dn'],
                        axis='z')
        makeDriverForPosNegShapeKey(faceMesh=faceMesh,
                        drvArmature = armature,
                        drvBoneName=bone,
                        posShapeKey=meshes['out'],
                        negShapeKey=meshes['in'],
                        axis='x')
        
        correctiveShapeNames = [shp for shp in list(meshes.keys()) if shp not in ['up','dn','out','in'] ]
        makeDriverForCorrective(faceMesh=faceMesh, correctiveType = correctiveShapeNames, shapekeyDict = meshes )

        
def makeDriverForPosNegShapeKey(faceMesh=None,
                        drvArmature = None,
                        drvBoneName=None,
                        posShapeKey=None,
                        negShapeKey=None,
                        axis = 'z'):
    """create driver on ex: tz 1 0 to turnon/off meshes. assumes faceMesh has shape key names given.
    all inputs given are strings
    axis - how to drive blendshape, default to z direction driving blendshape
    """
    print("makeDriverForPosNegShapeKey >>> using driver bone name: %s" %drvBoneName)
    #if faceMesh object doesnt have shape keys exit
    #if armature doesnt have drv bone exit
    print("makeDriverForPosNegShapeKey >>> using pos: %s neg: %s blendshapes'" %(posShapeKey,negShapeKey))
    faceObj = bpy.context.scene.objects[faceMesh]
    drvArmatureObj = bpy.data.objects[drvArmature]
    
    #skip if shapekey doesnt exist
    if posShapeKey in faceObj.data.shape_keys.key_blocks:
        #pos shape key
        driver = faceObj.data.shape_keys.key_blocks[posShapeKey].driver_add("value").driver
        driver.type = "SCRIPTED"
        driver.expression= '0 if drvloc < 0 else drvloc'
        var = driver.variables.new()
        var.name = "drvloc"
        var.type="SINGLE_PROP" #not sure if this is needed
        var.targets[0].id = drvArmatureObj
        var.targets[0].data_path = drvArmatureObj.pose.bones[drvBoneName].path_from_id()+".location.%s"%axis #using deault z location of bone to drive blendshape
        
    if negShapeKey in faceObj.data.shape_keys.key_blocks:
        #neg shape key
        driver = faceObj.data.shape_keys.key_blocks[negShapeKey].driver_add("value").driver
        driver.type = "SCRIPTED"
        driver.expression= '0 if drvloc > 0 else drvloc*-1.0'
        var = driver.variables.new()
        var.name = "drvloc"
        var.type="SINGLE_PROP" #not sure if this is needed
        var.targets[0].id = drvArmatureObj
        var.targets[0].data_path = drvArmatureObj.pose.bones[drvBoneName].path_from_id()+".location.%s"%axis


def makeDriverForCorrective(faceMesh=None, correctiveType = [], shapekeyDict = {} ):
    """
    faceMesh - mesh with shapkeys
    shapekeyDict - dictionary of the shapkey names for given key direction. ex: {'up':'upShapeName','dn':'dnShapeName'}
    correctiveType - supported corrective type. example up_out,up_in, dn_out, dn_in. to get shapkey name it looks for key in shapekeyDict
    """
    faceObj = bpy.context.scene.objects[faceMesh]

    for correctiveTyp in correctiveType:
        #name for corrective shapekey we want to drive. assumes it exists
        #correctiveTyp = correctiveType[0]
        correctiveShapeKey = shapekeyDict[correctiveTyp]
        
        #skip if cant find shape key
        if correctiveShapeKey not in faceObj.data.shape_keys.key_blocks:
            print("makeDriverForCorrective>>> skipping blendshape:%s cannot find it in scene for %s" %(correctiveShapeKey,correctiveTyp) )
            continue
        
        #driver shapekey names
        driver_a_key, driver_b_key = correctiveTyp.split('_')
        driver_a = shapekeyDict[driver_a_key]
        driver_b = shapekeyDict[driver_b_key]
        
        ##make the driver
        driver = faceObj.data.shape_keys.key_blocks[correctiveShapeKey].driver_add("value").driver
        driver.type = "SCRIPTED"
        driver.expression= 'drvloc_a * drvloc_b'
        
        #make first variable for first driving shapekey
        var_a = driver.variables.new()
        var_a.name = "drvloc_a"
        var_a.type="SINGLE_PROP"
        var_a.targets[0].id_type = 'KEY'
        var_a.targets[0].id = faceObj.data.shape_keys
        var_a.targets[0].data_path = 'key_blocks[\"%s\"].value' %(driver_a)
        
        
        #make second variable
        var_b = driver.variables.new()
        var_b.name = "drvloc_b"
        var_b.type="SINGLE_PROP"
        var_b.targets[0].id_type = 'KEY'
        var_b.targets[0].id = faceObj.data.shape_keys
        var_b.targets[0].data_path = 'key_blocks[\"%s\"].value' %(driver_b)
    


def makeDriverForCorrectivePost(faceMesh=None, corrective = None, shapekeys = [] ):
    """this is more general than other corrective method. it allows two shapekey weights to drive a corrective shapekey
    faceMesh - mesh with shapkeys
    shapekeys - pair of shapekey names whose weights when multiplied drive corrective example ['browRotateUp.L','browRotateUp.R']
    corrective- corrective shapekey name example ['browRotateCorrective']
    """
    faceObj = bpy.context.scene.objects[faceMesh]

    if len(shapekeys) != 2:
        print("requires exactly two shapekeys to drive corrective")
        return
        
    #name for corrective shapekey we want to drive. assumes it exists
    correctiveShapeKey = corrective
    
    #skip if cant find shape key
    if correctiveShapeKey not in faceObj.data.shape_keys.key_blocks:
        print("makeDriverForCorrective>>> skipping blendshape:%s cannot find it in scene" %(correctiveShapeKey) )
    
    #driver shapekey names
    driver_a, driver_b = shapekeys

    ##make the driver. it assumes no driver already exists on corrective
    driver = faceObj.data.shape_keys.key_blocks[correctiveShapeKey].driver_add("value").driver
    driver.type = "SCRIPTED"
    driver.expression= 'drvloc_a * drvloc_b'
    
    #make first variable for first driving shapekey
    var_a = driver.variables.new()
    var_a.name = "drvloc_a"
    var_a.type="SINGLE_PROP"
    var_a.targets[0].id_type = 'KEY'
    var_a.targets[0].id = faceObj.data.shape_keys
    var_a.targets[0].data_path = 'key_blocks[\"%s\"].value' %(driver_a)
    
    
    #make second variable
    var_b = driver.variables.new()
    var_b.name = "drvloc_b"
    var_b.type="SINGLE_PROP"
    var_b.targets[0].id_type = 'KEY'
    var_b.targets[0].id = faceObj.data.shape_keys
    var_b.targets[0].data_path = 'key_blocks[\"%s\"].value' %(driver_b)
        

def createInbetweenBlendshape( blendshape = None, driver_blendshape = None, face_mesh = None):
    """
    blendshape - blendshape name to be driven. its the corrective shape
    driver_blendshape - driver blendshape name. its weight is used to drive the corrective shape
    face_mesh - name for the mesh that has blendshapes. its the data object name
    
    1. given all needed information
    2. create a driver on blendshape
    3. create the driver curve
    """
    #assumes all inputs exist
    faceObj = bpy.context.scene.objects[face_mesh]
    
    #2. create a driver on blendshape
    driver = faceObj.data.shape_keys.key_blocks[blendshape].driver_add("value").driver
    driver.type = "SCRIPTED"
    driver.expression= 'var_wgt'
        
    var_wgt = driver.variables.new()
    var_wgt.name = "var_wgt"
    var_wgt.type="SINGLE_PROP"
    var_wgt.targets[0].id_type = 'KEY'
    var_wgt.targets[0].id = faceObj.data.shape_keys
    var_wgt.targets[0].data_path = 'key_blocks[\"%s\"].value' %(driver_blendshape)

    #need to get the proper fcurve we wish to create a curve for
    fcurve = faceObj.data.shape_keys.animation_data.drivers[-1] #assuming last driver is latest just added #faceObj.data.shape_keys.animation_data.drivers[0]
    print("going to edit fcurve on datapath >>> %s" %(fcurve.data_path) )
    
    #need to remove the modifier on fcurve so can create custom keyframes
    fcurve.modifiers.remove( fcurve.modifiers[0] )
    
    #3. create the driver curve
    #when driver made from scratch it starts with no keyframe points
    #the created curve should be zeroes at end and 1 at middle
    middle_frame = 0.5 #this could later be made into an optional parameter when dealing with multiple inbetweens
    start_key = fcurve.keyframe_points.insert(0.0,0.0)
    start_key.interpolation = 'LINEAR'
    mid_key = fcurve.keyframe_points.insert(middle_frame,1.0)
    mid_key.interpolation = 'LINEAR'
    end_key = fcurve.keyframe_points.insert(1.0,0.0)
    end_key.interpolation = 'LINEAR'
    
    


def drawBones(armatureObj=None,xzPos=(),boneBaseName=None,rootBoneName=None,boneShape=None,bgBoneShape=None):
    """draws 2 bones using position and armature
    """
    driverBone = None
    bgBone = None
    arm_obj = armatureObj
    armatureName = armatureObj.name
    
    #naming of bones
    driverBoneName = boneBaseName
    bgBoneName = boneBaseName+'_bg'
    
    #assuming used a side suffix. only accounts for one dot in bone name
    if '.' in boneBaseName:
        side = boneBaseName.split('.')[1]
        bgBoneName = boneBaseName.split('.')[0]+'_bg'+'.'+side
    
    if isExistBone(armatureName,driverBoneName) or isExistBone(armatureName,bgBoneName):
        print("bones already created exiting")
        return (driverBoneName,bgBoneName)
    
    #how big should bones look
    driver_y = 0.5
    bg_tail_z_offset = 1
    
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
            driverBone.tail = (xzPos[0],driver_y,xzPos[1])#(xzPos[0],1,xzPos[1])
            
            print("adding bg bone")
            #bg bone
            bgBone = arm_obj.data.edit_bones.new(bgBoneName)
            bgBone.head = (xzPos[0],0,xzPos[1])
            bgBone.tail = (xzPos[0],0,xzPos[1]+bg_tail_z_offset) #(xzPos[0],0,xzPos[1]+3)
        
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
    bpy.ops.object.mode_set(mode='POSE', toggle=False)        
    return result



#for help mirroring
def mirrorFaceControl(  face = '',
                        meshes = {},
                        bone_name = 'naTestBone.L',
                        armature = 'naFCArmature'):
    """
    face - name for the face that has shapekeys
    meshes - dict of blendshapes wish to mirror
    bone_name - name of anim bone want to mirror
    armature - data object name of armature that has the bones
    
	1. given .L anim bone is provided and given list of .L blendshapes wish to mirror
	2. select the anim and bg bones and symmetrize them
	3. tail y of .R anim bone should be multiplied by -1 instead of 1 to help with mirror
	4. find .R blendshapes from .L blend shapes
	5. connect the .R anim bone to the .R blendshapes    
    """
    print("mirrorFaceControl >>> mirroring bone: %s mirroring meshes %s" %(bone_name,meshes))
    
    side = bone_name.split('.')[1]
    bgBoneName = bone_name.split('.')[0]+'_bg'+'.'+side
    
    #2. select the anim and bg bones and symmetrize them
    #assumes armature is selected
    bpy.ops.object.mode_set(mode='EDIT')
    #assumes no bones already selected
    for bone in [bone_name, bgBoneName]:
        bpy.data.objects[armature].data.edit_bones[bone].select = True
        bpy.data.objects[armature].data.edit_bones[bone].select_head = True
        bpy.data.objects[armature].data.edit_bones[bone].select_tail = True
    bpy.ops.armature.symmetrize()

    #3. tail y of .R anim bone should be multiplied by -1 instead of 1 to help with mirror
    #so animator's curves in graph editor look similar when animating both sides
    r_bone_name = bone_name.split('.')[0]+'.R'
    bpy.data.objects[armature].data.edit_bones[r_bone_name].tail.y *= -1.0
    
    #4. find .R blendshapes from .L blend shapes
    r_meshes = {}
    for k,v in meshes.items():
        r_meshes[k] = v.split('.')[0]+'.R'
    #assumes right side blendshapes all exist

    
    #5. connect the .R anim bone to the .R blendshapes
    connectShapeKeyHelper(  faceMesh = face,
                            meshes = r_meshes,
                            armature = armature,
                            bone = r_bone_name)
    

    #6. for case the bg bone size was modified and we want to keep it on left side
    _mirrorBonePose( source_bone = bgBoneName, destination_bone = bgBoneName.replace('.L','.R'), armature = armature ) #assuming mirroring bg bone only and has a side

    #cleanup
    #enter pose mode
    bpy.ops.object.mode_set(mode='POSE')
    
    #deselect all
    bpy.ops.pose.select_all(action='DESELECT')


def _mirrorBonePose( source_bone = None, destination_bone = None, armature = None):
    """apply the pose values from left side to right side - should be negative tx and same ty tz and scales 
    armature - name for armature the data object name
    """
    #enter pose mode - assumes armature is already selected
    bpy.ops.object.mode_set(mode='POSE')
    
    src_tx = bpy.data.objects[armature].pose.bones[source_bone].location.x
    bpy.data.objects[armature].pose.bones[destination_bone].location.x = -1*src_tx
    
    #for remaining translates
    for i in [1,2]:
        bpy.data.objects[armature].pose.bones[destination_bone].location[i] = bpy.data.objects[armature].pose.bones[source_bone].location[i]
        
    #for scales
    for i in [0,1,2]:
        bpy.data.objects[armature].pose.bones[destination_bone].scale[i] = bpy.data.objects[armature].pose.bones[source_bone].scale[i]
        


def switchShapes(option = "Square"):
    """switch the shape on selected bones. assumes have bones selected in pose mode.
    assumes the shapes have already been created.
    """
    print("switchShapes >>> option: %s" %option)
    
    #assumes a bone in pose mode selected. assumes shapes already exists
    
    armature_name = bpy.context.object.name
    
    #get selected bone names
    sel_bones = []
    sel_bones = [ bone.name for bone in bpy.data.objects[armature_name].data.bones if bone.select ]

    #switch shape on selected bones
    if option == "Square":
        for bone_name in sel_bones:
            #the shapes might not already exist
            bpy.data.objects[armature_name].pose.bones[bone_name].custom_shape = bpy.data.objects['naBgShape_wide'] #might want to replace with variable
    elif option == "Horizontal":
        for bone_name in sel_bones:
            bpy.data.objects[armature_name].pose.bones[bone_name].custom_shape = bpy.data.objects['naBgShape_horizontal'] #might want to replace with variable
    elif option == "Vertical":
        for bone_name in sel_bones:
            bpy.data.objects[armature_name].pose.bones[bone_name].custom_shape = bpy.data.objects['naBgShape_vertical'] #might want to replace with variable

        
    
def regenerateShapes():
    """draws shapes if they dont already exist
    """
    getUiControlShapes()
    
def getUiControlShapes():
    """make the shapes for the animator control.
    might want to pass names as paramters so they can be change or have them at top of script
    """
    drvShapeName = 'naDriverShape'
    bgShapeName_vertical = 'naBgShape_vertical'
    bgShapeName_wide = 'naBgShape_wide'
    bgShapeName_horizontal = 'naBgShape_horizontal'
    
    #make any shapes if they dont already exist
    #so only rotate controls once when created
    if not drvShapeName in bpy.data.objects:
        boneShape = drawCircleShape(drvShapeName)
        #rotate circular shape so control facing us in xz plane
        rotateShape(boneShape,amount= math.pi/2,axis='x')        
    else:
        boneShape = bpy.data.objects[drvShapeName]
        
    if not bgShapeName_vertical in bpy.data.objects:    
        bgBoneShape_vertical = drawRectangleShape(bgShapeName_vertical)
    else:
        bgBoneShape_vertical = bpy.data.objects[bgShapeName_vertical]
        
    if not bgShapeName_wide in bpy.data.objects:        
        bgBoneShape_wide = drawRectangleShape(bgShapeName_wide)
        #widen the background shape when dealing with 4 or more shapes
        scaleShape(bgBoneShape_wide,amount= (4.0,1.0,1.0),axis='x')        
    else:
        bgBoneShape_wide = bpy.data.objects[bgShapeName_wide]
        
    if not bgShapeName_horizontal in bpy.data.objects:
        bgBoneShape_horizontal = drawRectangleShape(bgShapeName_horizontal)
        #make horizontal shape
        scaleShape(bgBoneShape_horizontal,amount= (4.0,1.0,1.0),axis='x')
        scaleShape(bgBoneShape_horizontal,amount= (1.0,0.25,1.0),axis='y')
    else:
        bgBoneShape_horizontal = bpy.data.objects[bgShapeName_horizontal]

    #cleanup
    #hide the created shapes
    for shape in [drvShapeName,bgShapeName_vertical,bgShapeName_wide,bgShapeName_horizontal]:
        bpy.data.objects[shape].hide = True
    
    return boneShape, bgBoneShape_vertical, bgBoneShape_wide, bgShapeName_horizontal




#######
def drawCircleShape(shapeName = None):
    
    scene = bpy.context.scene
    
    bpy.ops.object.mode_set(mode='OBJECT')
    #do nothing if shape already exists
    if shapeName in bpy.data.objects.keys():
        return bpy.data.objects[shapeName]
        

    meshObj = bpy.data.meshes.new("Mesh")
    boneShape = bpy.data.objects.new(shapeName, meshObj)
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
    verts,edges = ([(-0.25, -1.0, 0.0), (0.25, -1.0, 0.0), (-0.25, 1.0, 0.0), (0.25, 1.0, 0.0)], [(2, 0), (0, 1), (1, 3), (3, 2)]) #this is for skinny rectangle would be nice to be able to make square shape
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    
    return obj
    
    
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
    
def scaleShape(shapeObj,amount = (1,1,1), axis = 'x'):
    """
    scale shape in axis. 
    amount - tuple for scale value ex (1,1,3)
    """
    if axis == 'x':
        scaleAxis = (True,False,False)
    elif axis == 'y':
        scaleAxis = (False,True,False)
    elif axis == 'z':
        scaleAxis = (False,False,True)
        
    bpy.context.scene.objects.active = shapeObj
    bpy.ops.object.mode_set(mode='EDIT',toggle = False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value = amount,constraint_axis = scaleAxis)
    bpy.ops.object.mode_set(mode='OBJECT',toggle=False)

"""
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/riggingTools/faceTools')

import naSimpleFaceAnimControlAddOn as mod
import imp
imp.reload(mod)
#bpy.app.debug=True #temporary
#mod.createAnimFaceControl(context = bpy.context, meshes = {'up': 'up' , 'dn': 'dn'})
#mod.createAnimFaceControl(context = bpy.context, meshes = {'up': 'up' , 'dn': 'dn', 'out':'wide','in':'narrow'})
#mod.makeDriverForCorrective(faceMesh='Plane', correctiveType = ['up_out','up_in'], shapekeyDict = {'up': 'up' , 'dn': 'dn', 'out':'wide','in':'narrow', 'up_out':'Key 5', 'up_in':'Key 6'} )

#mod.createAnimFaceControl(context = bpy.context, meshes = {'up': 'up' , 'dn': 'dn', 'out':'wide','in':'narrow', 'up_out':'Key 5', 'up_in':'Key 6'})


meshes ={'up': 'cornerUp.L' ,
        'dn': 'cornerDn.L', 
        'out':'cornerWide.L',
        'in':'cornerNarrow.L',
        'up_out':'cornerUpWide.L',
        'up_in':'cornerUpNarrow.L',
        'dn_in':'cornerDnNarrow.L'}
mod.mirrorFaceControl(face = 'default', meshes=meshes,bone_name='naTestBone.L')
        
"""


#last modified
#112421,1125 -- added mirror support. made into addon
#111721 -- added correctives support
#111521 -- added 4 shapes support
#072720 --- worked on simplifying input parameters. prepping for addon
#072220 --- working on initial slider. would be nice to support combo shapes eventually
#im not sure if shapes need to be already made into shapekeys before using tool
#would like to simplify some more. like create armature and rootbone if they dont exist.
#find the mesh name from the shapekey meshes
#for addon might want push buttons to populate shapes. facemesh. etc


#inspired by:
#https://blender.stackexchange.com/questions/86757/python-how-to-connect-shapekeys-via-drivers
#https://blender.stackexchange.com/questions/58646/script-to-add-and-remove-f-curve-modifiers-to-multiple-selected-f-cruves

