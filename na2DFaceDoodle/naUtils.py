import bpy

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
    #i think starting with nothing selected is required
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.select_all(action='DESELECT')
    
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
    