#tool to help splitting weight from broad weight to each span

#last modified
#101821,1019 -- working on blocking

import bpy



####ui portion
bl_info = {
    "name":"broad weights spltting to individual spans",
    "description":"broad weights spltting to individual spans",
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
    PointerProperty
    )


class WeightSplitterProperties(PropertyGroup):
    destination_mesh = StringProperty(
        name = "destination_mesh",
        description = "this is the mesh we wish to edit weights on"
        ) 

    broad_bone = StringProperty(
        name = "broad_bone",
        description = "this is the bone that mostly has all the weight for the region of interest"
        ) 

    remainder_bone = StringProperty(
        name = "remainder_bone",
        description = "this is bone that should have remainder weights"
        ) 

    per_span_bones = StringProperty(
        name = "per_span_bones",
        description = "list of names of per span bones. assumes these all are all already empty groups of armature - space separated"
        ) 


class createGuideOperator(Operator):
    """creates a guide mesh
    """
    bl_idname = "obj.createguide"
    bl_label = "1. create guide"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        destination_mesh = context.scene.weightsplitter_prop.destination_mesh
        per_span_bones_arg = context.scene.weightsplitter_prop.per_span_bones
        
        per_span_bones = per_span_bones_arg.split(' ')
        
        createGuideMesh( destination_mesh = destination_mesh, per_span_bones = per_span_bones )

        return {'FINISHED'}
        
class donePerSpanAssignmentOperator(Operator):
    """click when done with per span assignment on guide mesh
    """
    bl_idname = "obj.doneguideassignment"
    bl_label = "2. done guide assignment"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        destination_mesh = context.scene.weightsplitter_prop.destination_mesh
        
        doneWithPerSpanAssignment( destination_mesh = destination_mesh )

        return {'FINISHED'}
        
class splitWeightsOperator(Operator):
    """split weights.
    """
    bl_idname = "obj.splitweights"
    bl_label = "3. split weights"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        destination_mesh = context.scene.weightsplitter_prop.destination_mesh
        guide_mesh = None
        guide_mesh = _getGuideMesh(destination_mesh)
        broad_bone = context.scene.weightsplitter_prop.broad_bone
        remainder_bone = context.scene.weightsplitter_prop.remainder_bone
        per_span_bones_arg = context.scene.weightsplitter_prop.per_span_bones
        per_span_bones = per_span_bones_arg.split(' ')
        vertex_group_map = None
        vertex_group_map = _getVertexGroupMap(per_span_bones)
        
        #assuming all inputs exist
        
        obj = WeightSplitter(   destination_mesh = destination_mesh,
                                guide_mesh = guide_mesh,
                                broad_bone = broad_bone, 
                                remainder_bone = remainder_bone,
                                vertex_group_map = vertex_group_map #{"Group":"Bone.001","Group.001":"Bone.002"} 
                                )
        obj.run()
        
        return {'FINISHED'}


class naWeightSplitterPanel(Panel):
    bl_label = "Weight Splitting Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.weightsplitter_prop, "destination_mesh")
        layout.prop(context.scene.weightsplitter_prop, "broad_bone")
        layout.prop(context.scene.weightsplitter_prop, "remainder_bone")
        layout.prop(context.scene.weightsplitter_prop, "per_span_bones")
        
        layout.operator( "obj.createguide" )
        layout.operator( "obj.doneguideassignment" )
        layout.operator( "obj.splitweights" )
        
        
def register():
    bpy.utils.register_class(createGuideOperator)
    bpy.utils.register_class(donePerSpanAssignmentOperator)
    bpy.utils.register_class(splitWeightsOperator)
    bpy.utils.register_class(naWeightSplitterPanel)
    
    bpy.utils.register_class(WeightSplitterProperties)
    bpy.types.Scene.weightsplitter_prop = PointerProperty( type = WeightSplitterProperties )

def unregister():
    bpy.utils.unregister_class(createGuideOperator)
    bpy.utils.unregister_class(donePerSpanAssignmentOperator)
    bpy.utils.unregister_class(splitWeightsOperator)
    bpy.utils.unregister_class(naWeightSplitterPanel)
    
    bpy.utils.unregister_class(WeightSplitterProperties)
    del bpy.types.Scene.weightsplitter_prop



######end ui portion


def createGuideMesh( destination_mesh = None, per_span_bones = [] ):
    """
    it duplicates mesh - removes any armature - removes unneeded vertex groups keeps ones of interest and hides original
    destination_mesh - name of skinned mesh to duplicate
    per_span_bones - list of names of per span bones. these vertex groups should be preserved on guide mesh
    """
    print("createGuideMesh")
    
    #duplicate destination mesh
    guide_mesh_obj = None
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.data.objects[destination_mesh].select = True
    bpy.context.scene.objects.active = bpy.data.objects[destination_mesh]
    bpy.ops.object.duplicate()
    guide_mesh_obj = bpy.context.selected_objects[-1]

    #remove armature
    bpy.ops.object.modifier_remove(modifier = guide_mesh_obj.modifiers[0].name )
    
    #remove unneeded vertex groups
    for i in range(0,len(guide_mesh_obj.vertex_groups)-1):
        vg = guide_mesh_obj.vertex_groups[i]
        #print("vg >>>%s",vg)
        #only remove non per span bones
        if vg.name in per_span_bones:
            continue
        guide_mesh_obj.vertex_groups.remove( vg )
    
    #unparent guide    
    bpy.ops.object.parent_clear(type='CLEAR')
    
    #hide original
    bpy.data.objects[destination_mesh].hide = True
    
    #rename guide mesh object name
    guide_mesh_obj.name = _getGuideMesh( destination_mesh = destination_mesh ) 
    
    
def doneWithPerSpanAssignment( destination_mesh = None ):
    """
    it hides temp mesh and shows original
    """
    print("doneWithPerSpanAssignment")
    guide_mesh = _getGuideMesh( destination_mesh = destination_mesh )
    
    bpy.data.objects[guide_mesh].hide = True
    bpy.data.objects[destination_mesh].hide = False
    

def _getGuideMesh( destination_mesh = None ):
    return destination_mesh+"_guide"

def _getVertexGroupMap( per_span_bones = [] ):
    result = {}
    #by default assuming keys are same as values
    for bone in per_span_bones:
        result[bone] = bone
    return result
    

class WeightSplitter(object):
    """this object helps split weights from a broad weighted bone to individual span bones using a guide mesh with per span weights
    """
    def __init__(self, destination_mesh = None, guide_mesh = None, broad_bone = None, remainder_bone = None, vertex_group_map = None):
        """
        destination_mesh - this is the mesh we wish to edit weights on
        guide_mesh - this is mesh that has a vertex group for each span of interest str name of object
        broad_bone - this is the bone that mostly has all the weight for the region of interest
        remainder_bone - this is bone that should have remainder weights
        vertex_group_map - this maps the vertex groups from the guide mesh to the destination mesh individual bones dict ex: {'group1':'bone1','group2':'bone2'}
        """
        self.destination_mesh = destination_mesh
        self.guide_mesh = guide_mesh
        self.broad_bone = broad_bone
        self.remainder_bone = remainder_bone
        self.vertex_group_map = vertex_group_map

        #need to verify input (meshes exist, vertex groups exist in destination and guide meshes, guide_mesh has identical topology with destination_mesh)
        
    def run(self):
        """to be called by user to do the split weighting
        """
        
        for guide_vg, destination_vg in self.vertex_group_map.items():
            verts_in_span = self._getAllVerticesAssignedToVertexGroup(guide_vg)
            for vert_id in verts_in_span:
                if not self._isBoneInfluencingVertex(vert_id, self.broad_bone):
                    continue
                #vertex has some weights by broad_bone
                #assign vertex the overall bones weight on the individual span bone
                broad_weight = bpy.data.objects[self.destination_mesh].vertex_groups[self.broad_bone].weight(vert_id)
                remainder_weight = 1 - broad_weight
                print("setting weight on vertex %s broad_weight %s on span bone %s" %(vert_id, broad_weight, destination_vg))
                
                bpy.data.objects[self.destination_mesh].vertex_groups[destination_vg].add([vert_id], broad_weight, 'REPLACE' )
                
                #to normalize values remove weight on vertex from broad_bone
                bpy.data.objects[self.destination_mesh].vertex_groups[self.broad_bone].add([vert_id], 1-broad_weight, 'REPLACE' )
                
                #assign remainder weight to remainder bone
                bpy.data.objects[self.destination_mesh].vertex_groups[self.remainder_bone].add([vert_id], remainder_weight, 'REPLACE' )
                
    
    
    def _isBoneInfluencingVertex(self, vertex_id = None, bone_name = None):
        """returns true if vertex is weighted to bone_name  
        """
        result = False
        if bone_name in self._getBoneNamesAffectingVertex(vertex_id,self.destination_mesh):
            result = True
        return result
        
    def _getAllVerticesAssignedToVertexGroup(self, vertex_group = None):
        """returns a list of vertex ids of vertices that are assigned to given vertex group
        """
        verts_in_vgroup = []
        
        guide_mesh = self.guide_mesh
        match_vg = vertex_group
        
        #get match_vg index
        match_vg_index = bpy.data.objects[guide_mesh].vertex_groups[match_vg].index
        #loop through all vertices
        for vert in bpy.data.objects[guide_mesh].data.vertices:
            for grp in vert.groups:
                if grp.group == match_vg_index:
                    verts_in_vgroup.append(vert.index)
                    
        return verts_in_vgroup
    
    def _getBoneNamesAffectingVertex( self, vertex_id = None, mesh_name = None ):
        """get all bone names that have a weight on vertex id
        mesh_name - mesh object name str that has given vertex_id
        """
        result = []
        vgListGroups = bpy.data.objects[mesh_name].vertex_groups
        for grp in bpy.data.objects[mesh_name].data.vertices[vertex_id].groups:
            if grp.weight > 0.0:
                vgListIndex = grp.group
                #print(vgListGroups[vgListIndex].name)
                result.append(vgListGroups[vgListIndex].name)
        return result    




"""getting all vertices weighted to a given vertex group
import bpy
verts_in_vgroup = []
match_vg = "Group"
#get match_vg index
match_vg_index = bpy.data.objects['Plane'].vertex_groups[match_vg].index
#loop through all vertices

for vert in bpy.data.objects['Plane'].data.vertices:
    for grp in vert.groups:
        if grp.group == match_vg_index:
            verts_in_vgroup.append(vert.index)
            
print(verts_in_vgroup)
"""



"""helpers for

#duplicating a mesh

#creating/removing vertex groups from mesh

#hiding mesh
"""



"""
import bpy
import sys
sys.path.append("/users/Nathaniel/Documents/src_blender/python/weightTools")
import naWholePaintToEachSpanAddOn as mod
import imp
imp.reload(mod)

#obj = mod.WeightSplitter( destination_mesh = "Cube", guide_mesh = "Cube.001", broad_bone = "Bone", remainder_bone = "root", vertex_group_map = {"Group":"Bone.001","Group.001":"Bone.002"} )
#obj.run()

mod.createGuideMesh( destination_mesh = "Plane", per_span_bones = ["Bone"] )

"""