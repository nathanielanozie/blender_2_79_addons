#naSimpleWeightAddOn.py
#modify use at your own risk
"""
last modified:
05042021 -- added comment for select active bone
05022021 -- worked on bug in weighting when have a locked bone
         -- fixed bug in mirror weights was using data name
         -- fixed bug mirror weights more than once. i think to use ops right side needs to start with zero weights
05012021 -- added a highlight active vertexgroup button. 
         -- added restoring active group when setting weights
         -- fixed bug when try to add a little bit of weight but vertex not in active vertex group
02272021 -- added beginning mirror weight button
02252021 -- added restoring of user selection when using tool
02242021 -- added some cleanup of zero weight vertices
02172021 -- fixed mode setting bug, fixed mesh naming requirement bug, improved on smooth weight
07172020 -- initial release
07112020 -- added scale add replace and specific buttons
07042020 -- added smooth button, support normalizing of unlocked bones, get mesh and active bone automatically
03282020 -- initial work
"""

bl_info = {
    "name":"tool to set weights on given vertices",
    "description":"tool to help artists with setting weights on many vertices at a time",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}


import bpy
import bmesh

from bpy.props import(
    StringProperty,
    FloatProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class WeightOperator(Operator):
    """set weight on active bone normalizing other unlocked bones
    """
    bl_idname = "obj.do_weights"
    bl_label = "Set Weight"
    bl_options = {"REGISTER"}
    
    weightMode = bpy.props.StringProperty()
    
    def execute(self,context):
        obj = context.object
        weight = round(context.scene.weight_prop.weight,4)
        #print("weightMode>>> %s" %self.weightMode)
        naSimpleWeight( weight = weight,
                    vidList = [],
                    context = context,
                    mode = self.weightMode)
        
        
        return {'FINISHED'}

class WeightSmoothOperator(Operator):
    """smooth weights on selected vertices. for fixed number of times on all unlocked bones.
    """
    bl_idname = "obj.do_smooth_weights"
    bl_label = "Smooth Weight"
    bl_options = {"REGISTER"}
    
    def execute(self,context):
        naSmoothWeight( context = context )
        return {'FINISHED'}

class MirrorWeightOperator(Operator):
    """mirrors weights from +x to -x. assumes blender naming conventions for bones ex ending in .L or .R
    """
    bl_idname = "obj.do_mirror_weights"
    bl_label = "Mirror Weight"
    bl_options = {"REGISTER"}
    
    def execute(self,context):
        naMirrorWeights( context = context )
        return {'FINISHED'}

class WeightSimpleOperator(Operator):
    """set weight on active bone normalizing other unlocked bones
    """
    bl_idname = "obj.do_weights_simple"
    bl_label = "Set Weight"
    bl_options = {"REGISTER"}
    
    weightMode = bpy.props.StringProperty()
    weightValue = bpy.props.FloatProperty()
    
    def execute(self,context):
        obj = context.object
        #print("weightMode>>> %s" %self.weightMode)
        naSimpleWeight( weight = self.weightValue,
                    vidList = [],
                    context = context,
                    mode = self.weightMode)
        
        
        return {'FINISHED'}


class SelectActiveVertexGroupOperator(Operator):
    """select only active vertex group. requires armature to be in pose mode
    """
    bl_idname = "obj.do_select_act_vg"
    bl_label = "Select Active Bone"
    bl_options = {"REGISTER"}
    
    def execute(self,context):
        selectActiveVertexGroup( context = context )
        return {'FINISHED'}
        

class WeightPanel(Panel):
    bl_label = "Weights Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "set weight on active bone normalizing rest")
        layout.label(text = "requires bones unlocked.")

        ##select active vertex group
        layout.operator("obj.do_select_act_vg")
        ##
        
        layout.prop(context.scene.weight_prop,"weight",text="weight")
        ##buttons using weight slider value
        row = layout.row(align=True)
        row.alignment='EXPAND'
        row.operator("obj.do_weights",text="REPLACE").weightMode='REPLACE'
        row.operator("obj.do_weights",text="ADD").weightMode='ADD'
        row.operator("obj.do_weights",text="SUBTRACT").weightMode='SUBTRACT'
        row.operator("obj.do_weights",text="SCALE").weightMode='SCALE'
        ##
        
        ###other buttons
        
        ##replace buttons
        row = layout.row(align=True)
        row.alignment='EXPAND'
        props = row.operator("obj.do_weights_simple",text="SET 1.0")
        props.weightMode = 'REPLACE'
        props.weightValue = 1.0
        #
        props = row.operator("obj.do_weights_simple",text="SET 0.75")
        props.weightMode = 'REPLACE'
        props.weightValue = 0.75
        #
        props = row.operator("obj.do_weights_simple",text="SET 0.5")
        props.weightMode = 'REPLACE'
        props.weightValue = 0.5
        #
        props = row.operator("obj.do_weights_simple",text="SET 0.25")
        props.weightMode = 'REPLACE'
        props.weightValue = 0.25
        #
        props = row.operator("obj.do_weights_simple",text="SET 0.0")
        props.weightMode = 'REPLACE'
        props.weightValue = 0.0
        ##

        ##add buttons
        row = layout.row(align=True)
        row.alignment='EXPAND'
        props = row.operator("obj.do_weights_simple",text="+ 0.05")
        props.weightMode = 'ADD'
        props.weightValue = 0.05
        #
        props = row.operator("obj.do_weights_simple",text="+ 0.10")
        props.weightMode = 'ADD'
        props.weightValue = 0.10
        #
        props = row.operator("obj.do_weights_simple",text="+ 0.15")
        props.weightMode = 'ADD'
        props.weightValue = 0.15
        ##
        
        ##subtract buttons
        row = layout.row(align=True)
        row.alignment='EXPAND'
        props = row.operator("obj.do_weights_simple",text="- 0.05")
        props.weightMode = 'SUBTRACT'
        props.weightValue = 0.05
        #
        props = row.operator("obj.do_weights_simple",text="- 0.10")
        props.weightMode = 'SUBTRACT'
        props.weightValue = 0.10
        #
        props = row.operator("obj.do_weights_simple",text="- 0.15")
        props.weightMode = 'SUBTRACT'
        props.weightValue = 0.15
        ##

        ##scale buttons
        row = layout.row(align=True)
        row.alignment='EXPAND'
        props = row.operator("obj.do_weights_simple",text="SC 0.90")
        props.weightMode = 'SCALE'
        props.weightValue = 0.90
        #
        props = row.operator("obj.do_weights_simple",text="SC 0.95")
        props.weightMode = 'SCALE'
        props.weightValue = 0.95
        #
        props = row.operator("obj.do_weights_simple",text="SC 1.05")
        props.weightMode = 'SCALE'
        props.weightValue = 1.05
        ##

        ###
        layout.operator("obj.do_smooth_weights")
        layout.operator("obj.do_mirror_weights")
        
class WeightProperties(PropertyGroup):

    weight = FloatProperty(
        name="weight",
        description="weight",
        min = 0.0,
        soft_max = 1.0
        )
    """
    weightMode = StringProperty(
        name="weightMode",
        description="weight mode"
        )
    """
    
def register():
    bpy.utils.register_class(WeightOperator)
    bpy.utils.register_class(WeightSmoothOperator)
    bpy.utils.register_class(MirrorWeightOperator)
    bpy.utils.register_class(WeightSimpleOperator)
    bpy.utils.register_class(SelectActiveVertexGroupOperator)
    bpy.utils.register_class(WeightPanel)
    bpy.utils.register_class(WeightProperties)
    bpy.types.Scene.weight_prop = PointerProperty(
        type = WeightProperties
        )

def unregister():
    bpy.utils.unregister_class(WeightOperator)
    bpy.utils.unregister_class(WeightSmoothOperator)
    bpy.utils.unregister_class(MirrorWeightOperator)
    bpy.utils.unregister_class(WeightSimpleOperator)
    bpy.utils.unregister_class(SelectActiveVertexGroupOperator)
    bpy.utils.unregister_class(WeightPanel)
    bpy.utils.unregister_class(WeightProperties)
    del bpy.types.Scene.weight_prop

if __name__ == "__main__":
    register()


def naSmoothWeight( context = None ):
    """smooth weights on all unlocked bones on selected vertices
    """
    #smooth need to be in weight or edit mode
    #curMode = context.selected_objects[0].mode
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    #
    obj = context.object
    #meshName = obj.name
    meshDataName = obj.data.name
    #smoothIterations = 10
    
    #need vertex masking on in weight paint mode
    obj.data.use_paint_mask_vertex = True
    #
    
    print("naSmoothWeight>>")
    
    #-smooth weight
    #-then normalizing unlocked bones for each vertex
    
    #smooth weight
    bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=1, repeat=1)

    
    #normalize unlocked bones for each vertex
    #by setting weight from smooth to each vertex 
    #use selected verts
    vids = []
    numVerts = len(bpy.data.meshes[meshDataName].vertices)
    for v in range(0,numVerts):
        if bpy.data.meshes[meshDataName].vertices[v].select == True:
            vids.append(v)

    activeBoneIndex = obj.vertex_groups.active_index
    for vertId in vids:
        #make sure vertex id is in selected vertex group
        if not isVertInVertexGroup( obj, vertId, activeBoneIndex ):
            continue
            
        weight = obj.vertex_groups[activeBoneIndex].weight(vertId) #bug if vertex id not in vertex group
        naSimpleWeight( weight = weight,
                        vidList = [vertId],
                        context = context )
                        
    
    
    #restore mode
    #bpy.ops.object.mode_set(mode=curMode)
 
def isVertInVertexGroup( obj, vertId, boneIndex ):
    """determine if vert id is in vertex group.
    both vertId and boneIndex are ints
    obj is a bpy.data.object
    """
    result = False
    for g in obj.data.vertices[vertId].groups:
        if g.group == boneIndex:
            result = True
            break
    
    return result
    

def naSimpleWeight( weight = None,
                    vidList = [],
                    context = None,
                    mode = 'REPLACE'
                            ):
    """set weight on active bone.
    on per vertex level normalize weight across unlocked bones excluding active one
    works with selected vertices of mesh
    vidList -- optional list of vertex ids to set weight on. uses selected otherwise
    context -- example bpy.context or gotten from ui
    mode    -- REPLACE, ADD, SUBTRACT, SCALE
    """
    obj = context.object
    """
    if len(unlockedBoneIndices) < 2:
        self.report({'INFO'}, "requires at least 2 non locked bones. skipping" )
        return {'FINISHED'}
    """
    meshName = obj.name
    meshDataName = obj.data.name
    activeBoneIndex = obj.vertex_groups.active_index #needs error checking
    #print("active bone index")
    #print(activeBoneIndex)
    if obj.vertex_groups[activeBoneIndex].lock_weight:
        print("active bone is locked skipping")
        return
        
    activeBoneName = obj.vertex_groups[activeBoneIndex].name #context.scene.weight_prop.boneName    
    
    if not meshName or not activeBoneName:
        return
    if weight is None:
        return
    #check if bone is a vertexGroup of mesh -- mesh bound to an armature  
    if activeBoneName not in bpy.data.objects[meshName].vertex_groups.keys():
        print('%s must be a vertex group of mesh %s' %(activeBoneName,meshName) )
        return
        
    #needs error checking
    #curMode = context.selected_objects[0].mode
    
    bpy.ops.object.mode_set(mode='OBJECT')#need to set weight in object mode
        
    vids = []
    if vidList:
        vids = vidList
    else:
        #use selected verts instead
        numVerts = len(bpy.data.meshes[meshDataName].vertices)
        for v in range(0,numVerts):
            if bpy.data.meshes[meshDataName].vertices[v].select == True:
                vids.append(v)
    
    numUnlockedBones = getNumUnlockedBones(obj)
    numUnlockedExcludingActive = numUnlockedBones - 1


    
    for vertId in vids:
        weightReplace = weight #REPLACE mode
        if mode != 'REPLACE':
            #get the current weight on vertex
            #its 0 if vertex not in active vertexgroup
            curWeight = 0
            if _isVertInVertexGroup( obj, activeBoneIndex, vertId ):
                curWeight = obj.vertex_groups[activeBoneIndex].weight(vertId)
            weightReplace = getReplaceWeight( weight, curWeight, mode )
        
        #check if setting weight on active bone would exceed 1
        #prevent setting weight if locked bones weight plus weight is over 1
        ##get total locked bones weight for vertex
        lboneWeightTotal = getTotalLockedBoneWeight(obj,vertId)
        #print("lboneWeightTotal",lboneWeightTotal)
        checkWeight = weightReplace + lboneWeightTotal
        #print("checkWeight")
        #print(checkWeight)
        if (weightReplace + lboneWeightTotal) > 1:
            print("skipping setting weight on vertex %s because weight plus locked bone weight exceeds 1" %vertId)
            continue

        #set weight on active bone
        bpy.data.objects[meshName].vertex_groups[activeBoneName].add([vertId],weightReplace,'REPLACE')
        
        #if no other unlocked bones do nothing additional
        if numUnlockedExcludingActive == 0:
            continue
            
        #set weight on unlocked bones
        ##compute unlockedWeight to be used for all unlocked bones
        uWeight = (1 - (weightReplace+lboneWeightTotal))/numUnlockedExcludingActive
        ##loop over unlocked bones setting weight on vertex. skip active bone
        setWeightUnlockedExcludeActive(uWeight, obj, vertId)
    
    #add cleanup of zero weight vertex groups from vertices
    deleteZeroWeightVertexGroups( meshName, context )

    #need to temporarily enter edit mode to make change visible
    bpy.ops.object.mode_set(mode='EDIT')
    
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT') #fixing so always end in weight paint mode
    
    #restore active vertex group
    obj.vertex_groups.active_index = activeBoneIndex

def naMirrorWeights(context = None):
    """mirror weights from +x to -x on all (non ending with .R) vertex groups
    assumes mesh is at origin.
    """
    #needs error checking mesh has weights and has blender vertex group naming conventions ex ending with .L or .R
    
    ##
    #save user seletion (for later)
    #select all -x side vertices not including center
    #because of ops mirror vg bug with multiple mirrors. first loop through all .R and mirror them to get them starting with zero weights
    #loop through all non .R vertex groups
    #run bpy.ops.object.vertex_group_mirror()
    #clean up zero vertex weights
    #restore user selection (for later)
    ##
    obj = context.object
    meshName = obj.name
    meshDataName = obj.data.name

    #saving starting selected vertex group
    start_act_vg = obj.vertex_groups.active_index 
    
    _selectMinusXVertices(obj)

    #entering weight paint mode to mirror weights
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.context.object.data.use_paint_mask_vertex = True #i think need vertex masking on in weight paint mode

    ##start by setting all .R vertex groups to zero. needed when use ops mirror multiple times
    _setRightSideVertexGroupsToZero(context,obj)
    
    #loop vertex groups of mesh
    for vgIndex in range(0,len(obj.vertex_groups)):
        vgName = obj.vertex_groups[vgIndex].name
        #skip if vertex group/bone ends with .R
        if vgName.endswith('.R'):
            continue
            
        #select vertex group
        obj.vertex_groups.active_index = vgIndex
        print("mirror weight for %s index %s" %(vgName,vgIndex) )
        
        #doing weight mirror here
        bpy.ops.object.vertex_group_mirror()
    
    deleteZeroWeightVertexGroups( meshName, context )#( meshDataName, context )
    
    #restore active vertex group
    obj.vertex_groups.active_index = start_act_vg
    
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT') #fixing so always end in weight paint mode


def _setRightSideVertexGroupsToZero(context=None, obj=None):
    """needed when doing multiple mirrors. need to start right side with no weights
    """
    obj = context.object
    meshName = obj.name
    meshDataName = obj.data.name

    _selectMinusXVertices(obj)

    #loop vertex groups of mesh
    for vgIndex in range(0,len(obj.vertex_groups)):
        vgName = obj.vertex_groups[vgIndex].name
        #skip if vertex group/bone doesnt ends with .R
        if not vgName.endswith('.R'):
            continue
            
        #select vertex group
        obj.vertex_groups.active_index = vgIndex
        print("mirror weight for %s index %s" %(vgName,vgIndex) )
        
        #doing weight mirror here
        bpy.ops.object.vertex_group_mirror()
    
    
def _selectMinusXVertices(obj):
    """only select all vertices on -x side not including center verts
    """
    #deselect all vertices
    #select -x vertices
    
    #deselect all vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')
    #need to be in object mode to select vertices
    bpy.ops.object.mode_set(mode='OBJECT')

    #select -x vertices
    for vidx in range(0,len(obj.data.vertices)):
        #dont include center verts. excluding +x side
        if obj.data.vertices[vidx].co[0] >= 0:
            continue   
        obj.data.vertices[vidx].select = True

    #end in edit mode
    bpy.ops.object.mode_set(mode='EDIT')

def _getSelectedVertexIndexes(obj):
    """accepts data.objects object ex bpy.data.objects['Plane']
    """
    #no error checking
    selVertexIndexes = []
    for vidx in range(0,len(obj.data.vertices)):
        if obj.data.vertices[vidx].select == True:
            selVertexIndexes.append(vidx)
    return selVertexIndexes

def _getActiveVertexIndex(obj):
    """accepts data.objects object ex bpy.data.objects['Plane']
    """
    #no error checking
    #active vertex
    activeVertexIndex = None
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh( obj.data )
    #sometimes no active vertex, example if selected all verts with a shortcut
    if bm.select_history.active is not None:
        activeVertexIndex = bm.select_history.active.index
    ##       

    return activeVertexIndex
    
def _restoreUserSelection( obj = None, scn = None, selVertexIndexes = [], activeVertexGroupIndex = 0, activeVertexIndex = None ):
    """restore selected vertices, vertex group, active vertex
    accepts obj ex bpy.data.objects['Plane']
    accepts scn ex bpy.context.scene
    and appropriate vertex indexes as ints
    """
    if not obj:
        return
    ##
    #restore user selection
    #vertex
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')
    #need to be in object mode to select vertices
    bpy.ops.object.mode_set(mode='OBJECT')

    for vindex in selVertexIndexes:
        obj.data.vertices[vindex].select = True
        
    #restore vertex group
    obj.vertex_groups.active_index = activeVertexGroupIndex or 0
    
    #restore active vertex index
    #done if no active vertex
    if activeVertexIndex is None:
        return    
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh( obj.data )
    bm.verts.ensure_lookup_table()
    bm.select_history.add(bm.verts[activeVertexIndex])
    #update viewport to show bmesh result
    scn.objects.active = scn.objects.active
    ##
    
    
def deleteZeroWeightVertexGroups( meshName = None, context = None):
    """delete any zero weight vertex groups from all vertices of mesh
    """
    #needs error checking mesh exists
    #needs error checking at least on vertex group on mesh
    
    ###
    #enter edit mode select all vertices
    #enter weight paint mode
    #loop all vertex groups running bpy.ops.object.vertex_group_clean()
    ###
    scn = context.scene
    obj = bpy.data.objects[meshName]
    
    #save current state
    #vertices
    selVertexIndexes = _getSelectedVertexIndexes(obj)
            
    #vertex group
    activeVertexGroupIndex = obj.vertex_groups.active_index

    #active vertex
    activeVertexIndex = _getActiveVertexIndex(obj)
    
    #print("for selected vertex indexes")
    #print(selVertexIndexes)
    
    bpy.ops.object.mode_set(mode='EDIT')
    #select all vertices
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    
    #loop vertex groups of mesh
    for vgIndex in range(0,len(obj.vertex_groups)):
        #select vertex group
        obj.vertex_groups.active_index = vgIndex
        bpy.ops.object.vertex_group_clean() #should work on all selected vertices
    
    #restore user selection
    _restoreUserSelection( obj, scn, selVertexIndexes, activeVertexGroupIndex, activeVertexIndex  )
    

def getReplaceWeight( weight = None, curWeight = None, mode = 'REPLACE'):
    """no error checking on returned weight between 0 and 1
    """
    if weight is None or curWeight is None or mode is None:
        return None
    if mode == 'REPLACE':
        return weight
    elif mode == 'ADD':
        return min(curWeight+weight,1.0)
    elif mode == 'SUBTRACT':
        return max(curWeight-weight,0.0)
    elif mode == 'SCALE':
        return curWeight*weight
        
    return None
        
def setWeightUnlockedExcludeActive(weight = None, obj=None, vertId=None):
    """set weight on unlocked bones for vertex. excludes active bone
    """
    boneIndexes = getUnlockedBoneIndicesExcludingActive(obj)
    #print("boneIndexes >>",boneIndexes)
    
    for i in range(0,len(boneIndexes)):
        bIndex = boneIndexes[i]
        obj.vertex_groups[bIndex].add( [vertId], weight, 'REPLACE')

def getTotalLockedBoneWeight( obj = None, vertId = None ):
    """get total weight on locked bones for vertex
    """
    if obj is None or vertId is None:
        return None
    result = 0
    lockedBoneIndexes = getLockedBoneIndices(obj)
    if not lockedBoneIndexes:
        #no locked bones so no weight on locked bones
        return 0
        
    for j in range(0,len(lockedBoneIndexes)):
        lboneIndex = lockedBoneIndexes[j]
        #if vertex not weighted by bone add 0
        result = 0
        if _isVertInVertexGroup( obj = obj, boneIndex = lboneIndex, vertId = vertId ):
            result += obj.vertex_groups[lboneIndex].weight(vertId)

    result = round(result,4) #rounding 4 places
    return result
    
def getLockedBoneIndices(obj = None):
    """get all locked indices from mesh data.object
    """
    result = []
    all_vgroups = obj.vertex_groups
    for i in range(0,len(all_vgroups)):
        if all_vgroups[i].lock_weight:
            result.append( i )
    return result

def getNumUnlockedBones(obj):
    return len(getUnlockedBoneIndices(obj))  

def getUnlockedBoneIndicesExcludingActive(obj = None):
    unlockedBoneIndices = getUnlockedBoneIndices(obj)
    #print("unlocked bone indices:")
    #print(unlockedBoneIndices)
    activeBoneIndex = obj.vertex_groups.active_index
    #print("activeBoneIndex")
    #print(activeBoneIndex)
    unlockedBoneIndices.remove(activeBoneIndex)
    return unlockedBoneIndices
    
def getUnlockedBoneIndices(obj = None):
    """get all unlocked indices from mesh data.object
    """
    result = []
    all_vgroups = obj.vertex_groups
    for i in range(0,len(all_vgroups)):
        if not all_vgroups[i].lock_weight:
            result.append( i )
    return result


def _isVertInVertexGroup( obj = None, boneIndex = None, vertId = None ):
    """return true if vertex id has some weights by bone
    no error checking. assumes obj is a mesh that is skinned and bone index and vertex ids exist
    """
    result = False
    
    #loop all bones assigned to vertex and exit loop if bone in input is found
    for vg in obj.data.vertices[vertId].groups:
        if vg.group == boneIndex:
            result = True
            break
            
    return result
    
def selectActiveVertexGroup( context = None ):
    """select only the active vertex group. to help with knowing which vertex group to put weights on. 
    """
    mesh_obj = context.object
    #verify obj exists and is a mesh and is skinned
    
    #get armature modifier
    arm_mod = None
    arm_mod_all = [ mod for mod in mesh_obj.modifiers if mod.type == 'ARMATURE']
    if arm_mod_all:
        arm_mod = arm_mod_all[0]
    
    if not arm_mod:
        print("could not find armature skinned to mesh")
        return
    
    armat = arm_mod.object
    
    #deselect all bones
    for bn in armat.data.bones:
        bn.select = False
    #select active vertex group
    act_vg = mesh_obj.vertex_groups.active.name
    armat.data.bones[act_vg].select = True




#inspired by:
#https://blender.stackexchange.com/questions/75814/how-to-make-this-script-to-quickly-set-specific-weights-screenshot-attached/75851#75851
#https://blender.stackexchange.com/questions/2515/how-to-pass-multiple-operator-properties-via-ui-layout
#https://blender.stackexchange.com/questions/8075/checking-if-a-vertex-belongs-to-a-vertex-group-in-python