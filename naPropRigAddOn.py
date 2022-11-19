#naPropRigAddOn.py
#modify use at your own risk
bl_info = {
    "name":"prop rigging tool",
    "description":"tool to build a simple prop rig in blender",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

import bpy


from bpy.types import(
    Operator,
    Panel
    )

class propRigOperator(Operator):
    """first select single mesh for prop in object mode.
    """
    bl_idname = "obj.buildproprig" #needs to be all lowercase
    bl_label = "build propRig"
    bl_options = {"REGISTER"}

    def execute(self, context):
        naBuildRig(context)
        return {'FINISHED'}

class propRigPanel(Panel):
    bl_label = "propRig Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "first select single mesh geo of prop")
        layout.operator( "obj.buildproprig")

def register():
    bpy.utils.register_class(propRigOperator)
    bpy.utils.register_class(propRigPanel)
    
def unregister():
    bpy.utils.unregister_class(propRigOperator)
    bpy.utils.unregister_class(propRigPanel)
if __name__ == "__main__":
    register()




##actual procs going here
#for widgets
squareShapeVertsEdges = ([(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (-1.0, 1.0, 0.0), (1.0, 1.0, 0.0)], [(2, 0), (0, 1), (1, 3), (3, 2)])
cubeShapeVertsEdges = ([(-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0)], [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1)])
circleShapeVertsEdges = ([(0.0, 1.0, 0.0), (-0.1951, 0.9808, 0.0), (-0.3827, 0.9239, 0.0), (-0.5556, 0.8315, 0.0), (-0.7071, 0.7071, 0.0), (-0.8315, 0.5556, 0.0), (-0.9239, 0.3827, 0.0), (-0.9808, 0.1951, 0.0), (-1.0, 0.0, 0.0), (-0.9808, -0.1951, 0.0), (-0.9239, -0.3827, 0.0), (-0.8315, -0.5556, 0.0), (-0.7071, -0.7071, 0.0), (-0.5556, -0.8315, 0.0), (-0.3827, -0.9239, 0.0), (-0.1951, -0.9808, 0.0), (0.0, -1.0, 0.0), (0.1951, -0.9808, 0.0), (0.3827, -0.9239, 0.0), (0.5556, -0.8315, 0.0), (0.7071, -0.7071, 0.0), (0.8315, -0.5556, 0.0), (0.9239, -0.3827, 0.0), (0.9808, -0.1951, 0.0), (1.0, 0.0, 0.0), (0.9808, 0.1951, 0.0), (0.9239, 0.3827, 0.0), (0.8315, 0.5556, 0.0), (0.7071, 0.7071, 0.0), (0.5556, 0.8315, 0.0), (0.3827, 0.9239, 0.0), (0.1951, 0.9808, 0.0)], [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19), (21, 20), (22, 21), (23, 22), (24, 23), (25, 24), (26, 25), (27, 26), (28, 27), (29, 28), (30, 29), (31, 30), (0, 31)])


def naBuildRig(context):
    """build simple prop rig with 3 animator controls.
    requires single mesh selected in object mode
    """
    #if armature doesnt exist make it
    print('makeArmature')
    
    sel = context.selected_objects #context.object doesnt work for addon
    if not sel:
        print("requires a mesh selected in object mode to prop")
        return
    propObj = sel[0]
    if (propObj is None) or (propObj.type != "MESH"):
        print("requires a mesh selected in object mode to prop")
        return
        
    propName = propObj.name#"Cube" #Change all the hard coded names later
    name = "%s_armature" %(propName)
    
    ###Making armature
    if name in bpy.data.objects:
        print('armature already created %s skipping' %(name))
        return bpy.data.objects[name]
    
    arm_dat = None
    if name in bpy.data.armatures:
        print('armatures with name already created %s removing it' %(name))
        armature = bpy.data.armatures[name]
        bpy.data.armatures.remove(armature)
    
    arm_dat = bpy.data.armatures.new(name)
        
    arm_obj = bpy.data.objects.new(name,arm_dat)
    arm_obj.data = arm_dat
    
    scene = context.scene
    scene.objects.link(arm_obj)
    scene.objects.active = arm_obj #need to select armature to put it in edit mode
    scene.update()
    ####
    
    
    ###Make bones in armature
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    rootBoneName = "%s_root_anim" %(propName)
    rootBone = bpy.data.armatures[name].edit_bones.new(rootBoneName)
    rootBone.head = (0,0,0)
    rootBone.tail = (0,1,0)

    midPosZ = propObj.dimensions.z/2 #midPosZ = 5 #get from dimensions of prop geo
    midABoneName = "%s_mida_anim" %(propName)
    midABone = bpy.data.armatures[name].edit_bones.new(midABoneName)
    midABone.head = (0,0,midPosZ)
    midABone.tail = (0,1,midPosZ)

    midBBoneName = "%s_midb_anim" %(propName)
    midBBone = bpy.data.armatures[name].edit_bones.new(midBBoneName)
    midBBone.head = (0,0,midPosZ)
    midBBone.tail = (0,1,midPosZ)
    
    ##handle parenting of bones
    print("doing parenting")
    context.scene.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    if arm_obj == context.active_object and context.mode == "EDIT_ARMATURE":
        print("parenting bone >>")
        arm_obj.data.edit_bones[midBBoneName].parent = arm_obj.data.edit_bones[midABoneName]
        arm_obj.data.edit_bones[midABoneName].parent = arm_obj.data.edit_bones[rootBoneName]
    print("finished parenting bone")

    bpy.ops.object.mode_set(mode='OBJECT')
    
    ##make widgets for bones
    rootWidgetName = "%s_root_wdgt" %("naProp") #so all prop rigs use same widgets
    midAWidgetName = "%s_mida_wdgt" %("naProp")
    midBWidgetName = "%s_midb_wdgt" %("naProp")
    if not rootWidgetName in bpy.data.objects:
        rootWidgetShape = drawShape( context, name=rootWidgetName, shapeVertsEdges=cubeShapeVertsEdges)
    else:
        rootWidgetShape = bpy.data.objects[rootWidgetName]
    #z scaling of root widget
    rootWidgetShape.scale.z = 0.1
    rootWidgetShape.select = True
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    if not midAWidgetName in bpy.data.objects:
        midAWidgetShape = drawShape( context, name=midAWidgetName, shapeVertsEdges=squareShapeVertsEdges)
    else:
        midAWidgetShape = bpy.data.objects[midAWidgetName]
        
    if not midBWidgetName in bpy.data.objects:
        midBWidgetShape = drawShape( context, name=midBWidgetName, shapeVertsEdges=circleShapeVertsEdges)
    else:
        midBWidgetShape = bpy.data.objects[midBWidgetName]
        
    #put widgets in last layer so they are not seen
    rootWidgetShape.layers = [False]*19+[True]
    midAWidgetShape.layers = [False]*19+[True]
    midBWidgetShape.layers = [False]*19+[True]
    
    ##add widgets to bones
    bpy.ops.object.mode_set(mode='OBJECT')
    arm_obj.pose.bones[rootBoneName].custom_shape = rootWidgetShape
    arm_obj.data.bones[rootBoneName].show_wire=True

    arm_obj.pose.bones[midABoneName].custom_shape = midAWidgetShape
    arm_obj.data.bones[midABoneName].show_wire=True
    
    arm_obj.pose.bones[midBBoneName].custom_shape = midBWidgetShape
    arm_obj.data.bones[midBBoneName].show_wire=True
    
    ##set rotation mode to bones
    arm_obj.pose.bones[rootBoneName].rotation_mode = 'XYZ'
    arm_obj.pose.bones[midABoneName].rotation_mode = 'XYZ'
    arm_obj.pose.bones[midBBoneName].rotation_mode = 'XYZ'

    
    ##resize widgets using prop geo
    propScale = 1.5*propObj.dimensions.x/2
    for boneName in [rootBoneName,midABoneName,midBBoneName]:
        arm_obj.pose.bones[boneName].custom_shape_scale = propScale
    
    #make prop geo follow armature
    #using constraint (possibly later change to parenting)
    cnt = propObj.constraints.new('CHILD_OF')
    cnt.target = arm_obj
    cnt.subtarget = midBBoneName
    poseDrivingBone = arm_obj.pose.bones[midBBoneName]
    ##prevent offset because driving bone not at origin
    cnt.inverse_matrix = (arm_obj.matrix_world*poseDrivingBone.matrix).inverted()
    #end make prop geo follow armature
    
    return arm_obj



###helper for widgets for bones
def drawShape(context, name = None, shapeVertsEdges = None):
    """ draw mesh no faces. if it exists does nothing. it takes name of shape and tuple with lists for verts and edges"""
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
    verts,edges = shapeVertsEdges
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    return obj

def getVertsEdgesFromSelected(context):
    """help for from_pydata creation of widgets. returns tuple verts and edges of selected
    """
    obj = context.object
    
    verts = []
    edges = []
    
    for i in range(0,len(obj.data.vertices)):
        pos = context.object.data.vertices[i].co
        verts.append( tuple( (round(pos[0],4),round(pos[1],4),round(pos[2],4)) )  )
    for i in range(0,len(obj.data.edges)):
        edges.append( (context.object.data.edges[i].vertices[0],context.object.data.edges[i].vertices[1])  )
        
    return verts,edges
    
##inspired by
#Nathan Vegdahl's rigify
#https://blenderartists.org/t/how-to-update-bpy-data-meshes-bpy-data-armatures/592370
#https://blender.stackexchange.com/questions/18562/child-ofs-set-inverse-without-using-bpy-ops
#https://blender.stackexchange.com/questions/112776/parent-object-to-a-bone-and-object-becomes-offsets-how-do-i-prevent-object-from  ##parenting mesh to bone