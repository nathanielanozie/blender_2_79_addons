#tool is to help with creating bones at vertices. tested in blender 2.79
#
#modify use at your own risk

#last modified
#051521 -- working on initial release.  added 1. and 2. from 051421. 
#       added a. nice to have option to create bones ignoring select order supporting selecting all verts or box select selection. 
#       added b. nice to have option on direction to point created bones
#       added nice to have a picker for armature
#       i think can ignore 4. from 051421 since length field can be used
#       i think 5. should be its own addon since the context is different and its not creating anything
#       for now ignoring 3. since duplicate works pretty effectively
#051421 -- working on initial release
#   1. have by default bone placed upright
#   2. provide bone length float field
#   3. a button for drawing bone at selected bones head.
#   4. for 3. option float field for how much shorter created bone should be from source bone
#   5. a button to snap first editbone selected to second editbone selected.
#031121 -- worked on bone drawing using normal. worked on first ui todo(support more options for bone creating)
#012421 -- added some naming of created bones.  for 3 verts better to select individual verts then try shortest path. still need to add normal option for tail bones
#080120 -- working on bone on vertex tool. added beginning bone drawing no custom names, or bone parenting.


bl_info = {
    "name":"draw bone at selected vertices",
    "description":"tool is to help with creating bones at vertices",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

import bpy
import bmesh
from mathutils import Vector
import math


#simple ui with single button and a few text fields with some defaults
from bpy.props import(
    StringProperty,
    PointerProperty,
    EnumProperty,
    FloatProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class BoneCreateOperator(Operator):
    """create bones on selected vertices options standing upright or at normal.
    requires to be in object or edit mode of selected mesh object.
    """
    bl_idname = "obj.do_bonecreate"
    bl_label = "Bone At Vertex Create"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        #get directory from text field
        armatureName = context.scene.bone_create_prop.armatureName
        
        #get enum option for way to orient created bone
        vboneEnum = context.scene.bone_create_prop.vertexBoneEnum
        #print("vertex drawing option: %s" %vboneEnum)
        useNormal = False
        if vboneEnum != 'standing':
            useNormal = True
        
        #get enum option for way vertexes were selected
        vSelectMethodEnum = context.scene.bone_create_prop.vertexSelectMethodEnum
        ignoreOrder = True
        if vSelectMethodEnum != 'ignoreorder':
            ignoreOrder = False
        
        
        #get enum option for bone direction in non normal mode
        bDirectionEnum = context.scene.bone_create_prop.boneDirectionEnum
        boneDirectionStr = bDirectionEnum
        
        #get length of bone
        lboneFloat = context.scene.bone_create_prop.lenBoneFloat
        #print("bone length: %s" %lboneFloat)
            
        self.report({'INFO'}, "Starting Bone Create ...")
        opCreateBonesOnSelectedVertices( context = context, 
                    armatureName = armatureName,
                    useNormal = useNormal,
                    boneLength = lboneFloat,
                    ignoreOrder = ignoreOrder,
                    boneDirectionStr = boneDirectionStr
                    )
        
        self.report({'INFO'}, "Completed Bone Create")
        return {'FINISHED'}
        
class BoneCreatePanel(Panel):
    bl_label = "Bone Create Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        
        #here we add textfields and button to ui
        #
        layout = self.layout
        layout.label(text = "Bone Create tool")
        
        #enum options
        layout.prop( context.scene.bone_create_prop, "vertexBoneEnum", text = "" )
        layout.prop( context.scene.bone_create_prop, "vertexSelectMethodEnum", text = "" )
        layout.prop( context.scene.bone_create_prop, "boneDirectionEnum", text = "" )

        #float option
        layout.prop( context.scene.bone_create_prop, "lenBoneFloat", text = "length bone" )
        
        #text fields
        #armature selector picker
        layout.prop_search(context.scene.bone_create_prop,"armatureName",bpy.data,"objects")
        
        #button
        layout.operator( "obj.do_bonecreate")
        
class BoneCreateProperties(PropertyGroup):
    #here we make each textfield
    armatureName = StringProperty(
        name = "armatureName",
        description = "armature name"
        )
    
    vertexBoneEnum = EnumProperty(
        name = "options",
        description = "options for drawing bone at vertex",
        items = [   ('standing',"Standing",""),
                    ('normal',"Normal","")
                ]
        )

    vertexSelectMethodEnum = EnumProperty(
        name = "options",
        description = "options for how vertex selection was made. by default allows using all select or box select ignoring order",
        items = [   ('ignoreorder',"IgnoreOrder",""),
                    ('useorder',"UseOrder","")
                ]
        )

    boneDirectionEnum = EnumProperty(
        name = "options",
        description = "options for bone direction. useful in non normal mode",
        items = [   ('x',"X",""),
                    ('y',"Y",""),
                    ('z',"Z",""),
                    ('nx',"-X",""),
                    ('ny',"-Y",""),
                    ('nz',"-Z","")
                ],
        default = 'z'
        )

    lenBoneFloat = FloatProperty(
            name = "length bone",
            description = "length of created bone",
            default = 1.0,
            min = 0.0,
            max = 1000.0
        )

def register():
    bpy.utils.register_class(BoneCreateOperator)
    bpy.utils.register_class(BoneCreatePanel)
    bpy.utils.register_class(BoneCreateProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.bone_create_prop = PointerProperty(
        type = BoneCreateProperties
        )
    
def unregister():
    bpy.utils.unregister_class(BoneCreateOperator)
    bpy.utils.unregister_class(BoneCreatePanel)
    bpy.utils.unregister_class(BoneCreateProperties)
    del bpy.types.Scene.bone_create_prop
    
if __name__ == "__main__":
    register()
    
    

def opCreateBonesOnSelectedVertices( context = None, armatureName = None, useNormal = False, boneLength = 1.0, ignoreOrder = True, boneDirectionStr = 'x' ):
    """to be called by operator
    """
    
    #figure out bone direction from string
    deltaXYZ = (0.0,0.0,boneLength) #default standing in world z
    deltaXYZ = getBoneDeltaFromString(boneDirectionStr, boneLength)
    
    bone_names = createBonesOnSelectedVertices(context = context,
                                                armatureName = armatureName,
                                                ignoreOrder = ignoreOrder,
                                                useNormal=useNormal,
                                                deltaXYZ = deltaXYZ 
                                                )

def getBoneDeltaFromString( boneDirectionStr = 'z', boneLength = 1.0):
    """boneDirectionStr x,y,z,nx,ny,nz
    gets the vector from tail to head to use
    """
    deltaXYZ = (0.0,0.0,boneLength)
    if boneDirectionStr == "x":
        deltaXYZ = (boneLength,0.0,0.0)
    elif boneDirectionStr == "y":
        deltaXYZ = (0.0,boneLength,0.0)
    elif boneDirectionStr == "z":
        deltaXYZ = (0.0,0.0,boneLength)
    elif boneDirectionStr == "nx":
        deltaXYZ = (-boneLength,0.0,0.0)
    elif boneDirectionStr == "ny":
        deltaXYZ = (0.0,-boneLength,0.0)
    elif boneDirectionStr == "nz":
        deltaXYZ = (0.0,0.0,-boneLength)
        
    return deltaXYZ
    
def orientBoneToNormal( bone = None, normVector = (0,1,0), upVector = (0,0,1) ):
    """
    point bone y in direction of normal vector
    roll bone by aligning z axis to upVector
    """
    #point bone y in direction of normal vector
    normV = Vector( normVector )
    normV.normalize()
    normV = normV*bone.length
    bone.tail = bone.head + normV
    
    #roll bone by aligning z axis to upVector
    upV = Vector( upVector )
    axis = bone.y_axis.cross(upV)
    axis.normalize()
    dotP = max( -1.0, min(1.0, bone.x_axis.dot(axis))  ) 
    angle = math.acos(dotP)
    bone.roll += angle
    dotP1 = bone.x_axis.dot(upV)
    bone.roll -= angle*2
    dotP2 = bone.x_axis.dot(upV)
    if dotP1 > dotP2:
        bone.roll += angle*2
        

def createBonesOnSelectedVertices(   context = bpy.context, 
                                    armatureName = None, 
                                    ignoreOrder = True,
                                    parentBoneName = None,
                                    deltaXYZ = (0.0,0.25,0.0),
                                    useNormal = False
                                    ):
    """make bones on selected vertices
    application for eyelid rigging
    supports: user can either select all vertices individually or select exactly 2 verts and use shortest path for inbetween verts
    deltaXYZ is xyz offset from head of bone to use for drawn bones. (0,.25,0) would say offset tail by .25 in y
    useNormal is whether to draw bone using normal of vertex
    ignoreOrder when true allows box selection for selecting verts otherwise requires individual vertex selections
    returns list of string names of bones it created
    """
    #check that mesh is selected
    if armatureName is None:
        return
    if armatureName not in bpy.data.armatures:
        print("requires armature %s to exist" %armatureName)
        return
    
    #get the order of selected vertices
    #get world position of vertices and naming for new bones
    #use the given armature and parent bone to make bones at given positions
    
    obj = context.selected_objects[0]
    
    #if object is not a mesh exit
    if obj.type != "MESH":
        return
        print("requires mesh in object or edit mode selected")
    
    #get order of selected vertices
    vids = []
    
    #get order of selected vertices using selection order
    vids = getVertexSelection( context = context, ignoreOrder = ignoreOrder )
    
    #get positions verts
    if not vids:
        print("couldnt find vert ids exiting")
        return
    vid_pos = []
    oworld_mat = obj.matrix_world
    for vid in vids:
        vworld_vec = oworld_mat* obj.data.vertices[vid].co 
        vid_pos.append( vworld_vec )
    
    #create bones at positions
    #for now make single bone, all bones parented to parent bone parameter
    #print(vid_pos)
    bones_made = []
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj = bpy.data.objects[armatureName]
    context.scene.objects.active = arm_obj
    arm_obj.select = True
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    for vpos, vid in zip(vid_pos,vids):
        bone = bpy.data.armatures[armatureName].edit_bones.new("bone")
        bone.head = ( vpos[0], vpos[1], vpos[2] )
        bone.tail = ( vpos[0]+deltaXYZ[0], vpos[1]+deltaXYZ[1], vpos[2]+deltaXYZ[2] ) #ex length of bones in y a small value
        
        #draw tail differently if useNormal used
        if useNormal:
            vertexNorm = obj.rotation_euler.to_matrix()*obj.data.vertices[vid].normal
            #print("vertex normal %s" %vertexNorm)
            orientBoneToNormal( bone = bone, normVector = vertexNorm, upVector = (0,0,1) )
        
        bones_made.append(bone.name)
        
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.select_all(action='DESELECT')
    
    #print("bones_made",bones_made)
    
    return bones_made



def getVertexSelection( context = None, ignoreOrder = True ):
    """get vertex ids selected whether to use selection order or not.
    when using selection order vertexes cannot be selected with box select or shortcuts.
    """
    vids = []
    
    if ignoreOrder:
        #ignore selection order
        sel_obj = context.selected_objects[0]
        #i think need to toggle mode to register selection
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        vids = [ vid.index for vid in sel_obj.data.vertices if vid.select ]
        #print("getVertexSelection vids: %s" %vids)
    else:
        #use selection order
        num_selhist = getNumberVertsInSelectHistory(context)
        
        if num_selhist == 0:
            print("requires vertices selected")
            return
        if num_selhist == 2:
            vids = getVertexIndexesInOrderOfSelectionShortestPath(context)
        else:
            vids = getVertexIndexesInOrderOfSelectionIndividual(context)
    

    return vids

def getVertexIndexesInOrderOfSelectionIndividual( context = bpy.context ):
    """return list of vertex ids in order of selection
    expects every vertex selected one at a time
    """
    sel_obj = context.selected_objects[0]
    #bmesh needs data
    bm = bmesh.from_edit_mesh( sel_obj.data )
    
    #make sure we had selected vertices
    if not isinstance(bm.select_history[0], bmesh.types.BMVert):
        print("requires vertices selected")
        return
    
    vid_list = [ bv.index for bv in bm.select_history  ]
    
    #i dont think need update_edit_mesh because not changing mesh
    
    return vid_list
    
def getNumberVertsInSelectHistory( context ):
    """get number of vertices in select_history
    """
    sel_obj = context.selected_objects[0] #context.object
    print("getNumberVertsInSelectHistory sel_obj: %s" %sel_obj)
    #bmesh needs data
    bm = bmesh.from_edit_mesh( sel_obj.data )
    return len( [ sel for sel in bm.select_history if isinstance(sel, bmesh.types.BMVert) ] )
    

def getVertexIndexesInOrderOfSelectionShortestPath( context = bpy.context ):
    """return list of vertex ids in order of selection
    expects exactly two vertices first selected and using ctrl to fill in shortest path
    """
    sel_obj = context.selected_objects[0]
    #bmesh needs data
    bm = bmesh.from_edit_mesh( sel_obj.data )
    
    
    #make sure we had selected vertices
    if len(bm.select_history) != 2:
        print("requires two vertices selected and shortest path use for inbetween verts")
        return
        
    if not isinstance(bm.select_history[0], bmesh.types.BMVert):
        print("requires vertices selected")
        return
        
    vstart = bm.select_history[0]
    vend = bm.select_history[1]
    
    bm_list = [vstart]
    vid_list = []
    #number of selected vertices
    num_verts = len( [v for v in bm.verts if v.select]   )
    counter = 0
    
    #tricky part, successively finding nearest vertex. and updating where we start from
    while counter < num_verts:
        bm_vert = bm_list[counter]
        #connected edges to vertex
        cedges = bm_vert.link_edges
        #which of these edges has a selected vertex
        for e in cedges:
            if e.select:
                cvert = e.other_vert(bm_vert)
                if cvert not in bm_list:
                    bm_list.append( cvert )
        counter += 1
    
    vid_list = [ bv.index for bv in bm_list  ]
    
    #i dont think need update_edit_mesh because not changing mesh
    
    return vid_list


def nameBones( bones = [], armatureName = None, charName = 'testChar', facePart = 'testPart', side = 'L'  ):
    """not used currently
    this method can be modified for a different naming convention.
    this convention is to set names to '{charName}_{facePart}_{a-z}.{side}'
    """
    #verify armature exists
    if armatureName is None:
        return
    if armatureName not in bpy.data.armatures:
        print("requires armature %s to exist" %armatureName)
        return    
    
    #go on with naming
    import string
    allLetters = list(string.ascii_lowercase)
    if len(bones) > len(allLetters):
        print("too many bones to name with this naming convention of using letters")
        return 
        
    lettersForBones = allLetters[0:len(bones)] 
    for b,let in zip(bones,lettersForBones):
        bpy.data.objects[armatureName].pose.bones[b].name = '{charName}_{facePart}_{letter}.{side}'.format(charName=charName,facePart=facePart,letter= let, side=side)



#inspired by
#Nathan Vegdahl
#https://blender.stackexchange.com/questions/69796/selection-history-from-shortest-path
#https://blender.stackexchange.com/questions/6155/how-to-convert-coordinates-from-vertex-to-world-space
#https://blenderartists.org/t/blender-panel-adding-prop-search-dynamically/669802