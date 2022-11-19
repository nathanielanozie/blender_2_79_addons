#simple tool to help transfer weights from a partial mesh to a whole mesh.
#it assumes partial mesh is whole mesh with some faces deleted.
#
#modify use at your own risk

#last modified
#102621 -- working on initial release
#101521,1016 -- wrote main class - working on blocking

bl_info = {
    "name":"weights copy tool",
    "description":"copy weights from a partial mesh to whole mesh",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}


import bpy

from bpy.props import(
    StringProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class WeightsTransferOperator(Operator):
    """transfer weights from a partial mesh to a whole mesh
    """
    bl_idname = "obj.do_weightstransfer"
    bl_label = "Weights Transfer"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
    
        self.report({'INFO'}, "Starting Weights Transfer ...")
        wtc_obj = WeightsTransferCreator(source_mesh = context.scene.weightstransfer_prop.source_mesh, 
                                destination_mesh= context.scene.weightstransfer_prop.destination_mesh, 
                                remainder_bone_source = context.scene.weightstransfer_prop.remainder_bone_source,
                                remainder_bone_destination = context.scene.weightstransfer_prop.remainder_bone_destination
                                )
        wtc_obj.run()

        self.report({'INFO'}, "Completed Weights Transfer")
        return {'FINISHED'}
        
class WeightsTransferPanel(Panel):
    bl_label = "Weights Transfer Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        
        #here we add textfields and button to ui
        #
        layout = self.layout
        layout.label(text = "Weights Transfer tool")
        
        #4 text fields in a row
        #text fields
        layout.prop( context.scene.weightstransfer_prop, "source_mesh", text = "source mesh" )
        layout.prop( context.scene.weightstransfer_prop, "destination_mesh", text = "destination mesh" )
        layout.prop( context.scene.weightstransfer_prop, "remainder_bone_source", text = "source remainder bone" )
        layout.prop( context.scene.weightstransfer_prop, "remainder_bone_destination", text = "destination remainder bone" )
        
        #button
        layout.operator( "obj.do_weightstransfer")
 
 
class WeightsTransferProperties(PropertyGroup):
    #here we make each textfield
    source_mesh = StringProperty(
        name = "source_mesh",
        description = "this is the source partial mesh object name. it should have the same faces as destination mesh with some deleted"
        )

    destination_mesh = StringProperty(
        name = "destination_mesh",
        description = "this is the destination whole mesh object name"
        )

    remainder_bone_source = StringProperty(
        name = "remainder_bone_source",
        description = "bone to hold remainder weights of source mesh"
        )

    remainder_bone_destination = StringProperty(
        name = "remainder_bone_destination",
        description = "bone to hold remainder weights of destination mesh"
        )

def register():
    bpy.utils.register_class(WeightsTransferOperator)
    bpy.utils.register_class(WeightsTransferPanel)
    bpy.utils.register_class(WeightsTransferProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.weightstransfer_prop = PointerProperty(
        type = WeightsTransferProperties
        )

def unregister():
    bpy.utils.unregister_class(WeightsTransferOperator)
    bpy.utils.unregister_class(WeightsTransferPanel)
    bpy.utils.unregister_class(WeightsTransferProperties)
    del bpy.types.Scene.weightstransfer_prop


class WeightsTransferCreator(object):
    """this object helps with transfering weights from a partial source mesh to a whole destination mesh
    """
    def __init__(self, source_mesh = None, destination_mesh = None, bones_source_to_destination = None, remainder_bone_source = None, remainder_bone_destination = None ):
        """
        source_mesh - this is the source partial mesh object str name
        destination_mesh - this is the destination whole mesh object str name
        bones_source_to_destination - this is a mapping from the source bones to destination bones as dictionary ex: {'bone_a':'bone_a','bone_b':'bone_b'}
         if nothing provided it assumes same bone names in destination as there are in source
        remainder_bone_source - bone to hold remainder weights of source mesh
        remainder_bone_destination - bone to hold remainder weights of destination mesh
        """
        #verify inputs exist (meshes exist, bones exist etc)
        self.source_mesh = source_mesh
        self.destination_mesh = destination_mesh
        self.remainder_bone_source = remainder_bone_source
        self.remainder_bone_destination = remainder_bone_destination
        self.bones_source_to_destination = {}
        if bones_source_to_destination:
            self.bones_source_to_destination = bones_source_to_destination
        else:
            #assume same bone names in destination as there are in source
            self.bones_source_to_destination = self._getDefaultSourceToDestinationMapping(mesh_name = source_mesh, excludes = [remainder_bone_source])
        
    def run(self):
        """to be called by user to do the entire weight transfer process
        """
        vertex_source_to_destination = self._getVertexIDSourceToDestination()
        if not vertex_source_to_destination:
            print("could not do the weight transfer cannot find source to destination vertex mapping")
            return
        self._transferWeights(vertex_source_to_destination)
    
    def _transferWeights(self, vertices_source_to_destination = None ):
        """this changes weights on destination mesh. it uses source meshes weights
        vertices_source_to_destination - mapping of source vertex id to its closes destination vertex ex: {0:3,1:2}
        """
        #print("vertices_source_to_destination >>",vertices_source_to_destination)
        
        #loop vertices of source mesh
        for src_vert_id, dest_vert_id in vertices_source_to_destination.items():
            bones_affecting_vertex = self._getBoneNamesAffectingVertex( vertex_id = src_vert_id, mesh_name = self.source_mesh )
            
            #get weights from source mesh
            for src_bone, dest_bone in self.bones_source_to_destination.items():
                #skip if src_bone has no weights on source vertex
                if src_bone not in bones_affecting_vertex:
                    continue
                src_weight = bpy.data.objects[self.source_mesh].vertex_groups[src_bone].weight(src_vert_id)
                #print("for destination vert %s and dest bone %s source weight is %s" %(dest_vert_id, dest_bone, src_weight) )
                ##do the actual setting of individual bone weight on destination mesh
                bpy.data.objects[self.destination_mesh].vertex_groups[dest_bone].add([dest_vert_id], src_weight, 'REPLACE' )
                
            #handle the remainder bone weight to be set once per vertex
            src_remainder_weight = bpy.data.objects[self.source_mesh].vertex_groups[self.remainder_bone_source].weight(src_vert_id)
            #print("for destination vert %s and dest bone %s source remainder weight is %s" %(dest_vert_id, dest_bone, src_remainder_weight) )              
            ##set the remainder weight on destination mesh
            bpy.data.objects[self.destination_mesh].vertex_groups[self.remainder_bone_destination].add([dest_vert_id], src_remainder_weight, 'REPLACE' )

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

    def _getVertexIDSourceToDestination(self):
        """uses nearest position of vertices to find closes destination mesh vertex to source mesh vertex
        """
        result = {}
        close_enough_dist = 0.00001 #closer than this counts as a match
        
        #loop MeshVertex objects of source finding closest in destination
        for src_vert in bpy.data.objects[self.source_mesh].data.vertices:
            src_pos = src_vert.co
            for dest_vert in bpy.data.objects[self.destination_mesh].data.vertices:
                dest_pos = dest_vert.co
                if (src_pos - dest_pos).magnitude < close_enough_dist:
                    #found closest vertex
                    result[src_vert.index] = dest_vert.index
                    break
        #might be nice to check if number keys match number verts of source mesh to indicate we found a match for all verts
        if len(bpy.data.objects[self.source_mesh].data.vertices) != len(result.keys()):
            print("check that source partial mesh is the whole mesh with some faces deleted. need them to overlap exactly")
            return False
        return result

    def _getDefaultSourceToDestinationMapping(self, mesh_name = None, excludes = []):
        """returns a dictionary of form {"Bone.001":"Bone.001","Bone.002":"Bone.002"} 
        they are all the bone names bound to mesh excluding the bone names in excludes list.
        it assumes mesh_name is already bound to some bones
        """
        result = {}
        bones = [vg.name for vg in bpy.data.objects[mesh_name].vertex_groups if vg.name not in excludes]
        for bone in bones:
            result[bone] = bone
        return result

"""
import bpy
import sys
sys.path.append("/users/Nathaniel/Documents/src_blender/python/weightTools")
import naPartPaintToWholeAddon as mod
import imp
imp.reload(mod)

obj = mod.WeightsTransferCreator(source_mesh = "partial", 
                                destination_mesh="whole", 
                                remainder_bone_source = "Bone",
                                remainder_bone_destination = "Bone"
                                )
obj.run()

"""

"""
obj = mod.WeightsTransferCreator(source_mesh = "partial", 
                                destination_mesh="whole", 
                                remainder_bone_source = "Bone",
                                remainder_bone_destination = "Bone",
                                bones_source_to_destination = {"Bone.001":"Bone.001","Bone.002":"Bone.002"}
                                )
obj.run()
"""


"""getting world position of a vertex or face
this gets local position - it doesnt change when mesh is moved in object space
#uses vertex id
>>> bpy.data.objects['Cube'].data.vertices[4].co
Vector((1.0, -1.0, -1.0))

#uses face id
>>> bpy.data.objects['Cube'].data.polygons[2].center
Vector((1.0, 0.0, 0.0))

"""

"""getting all the bones with some weight on a vertex

#getting a bone weighted to a vertex id (vertex id is 1, assumes groups has a zero index
>>> bpy.data.objects['Cube'].data.vertices[1].groups[0].group
1
#the number returned above is the index in panel of vertex groups
>>> bpy.data.objects['Cube'].vertex_groups[1].name
'Bone.001'

#two ways to find weight of a vertex id. (vertex id is 1)
>>> bpy.data.objects['Cube'].vertex_groups[1].weight(1)
1.0
#or
>>> bpy.data.objects['Cube'].data.vertices[1].groups[0].weight
1.0

####to get all bone names with some weight for vertex id (vertex id is 5)
import bpy
vgListGroups = bpy.data.objects['Cube'].vertex_groups
for grp in bpy.data.objects['Cube'].data.vertices[5].groups:
    if grp.weight > 0.0:
        vgListIndex = grp.group
        print(vgListGroups[vgListIndex].name)
"""


"""setting weight on a vertex id and bone name (vertex id is 1)
#need to be in object mode
>>> bpy.data.objects['Cube'].vertex_groups['Bone'].add([1], 0.5, 'REPLACE' )
"""





