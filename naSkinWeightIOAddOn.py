#naSkinWeightIOAddOn.py
#modify use at your own risk


import bpy
import json
import os


####add on portion
bl_info = {
    "name":"skin weights import export",
    "description":"simple skin weights import export",
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


class skinWeightsIOProperties(PropertyGroup):
    dir_path = StringProperty(
        name = "Browse",
        description = "Pick path to export/import to/from either a file or a directory",
        maxlen = 200,
        subtype = 'FILE_PATH'
    )

    file_name = StringProperty(
        name = "file_name",
        description = "file name for weights file ex: test.naSkin"
        ) 

    use_selected = EnumProperty(
        name = "use_selected",
        description = "whether or not to import onto only selected vertices",
        items = [   ('True',"True",""),
                    ('False',"False","")
                ],
        default = 'False'
        )

class exportWeightsOperator(Operator):
    """export weights of selected character in object mode
    """
    bl_idname = "obj.exportweights"
    bl_label = "export"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        file_name = context.scene.skinweightsio_prop.file_name
        path = context.scene.skinweightsio_prop.dir_path
        
        abs_path = bpy.path.abspath(path)
        
        full_path = ''
        #if browsed to a file use that
        if os.path.isfile(abs_path):
            full_path = abs_path
        else:
            #if file_name not specified give an error
            if not file_name:
                self.report({'INFO'},"please enter a file name to export to")
                return {'FINISHED'}
            full_path = os.path.join(abs_path,file_name)
        
        if not context.selected_objects:
            self.report({'INFO'},"please select character in object mode that has skin weights")
            return {'FINISHED'}
        
        sel = context.selected_objects[0]
        if sel.type != 'MESH':
            self.report({'INFO'},"please select character in object mode that has skin weights")
            return {'FINISHED'}            
            
        mesh_name = sel.name
        
        print("exportWeightsOperator dir path: %s character: %s" %(full_path,mesh_name))
        exportWeightOnSelected(mesh_name = mesh_name, weightFile = full_path)
        return {'FINISHED'}


class importWeightsOperator(Operator):
    """import weights of selected character in object mode
    """
    bl_idname = "obj.importweights"
    bl_label = "import"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        file_name = context.scene.skinweightsio_prop.file_name
        path = context.scene.skinweightsio_prop.dir_path
        use_selected = True if context.scene.skinweightsio_prop.use_selected == 'True' else False 
        
        abs_path = bpy.path.abspath(path)
        
        full_path = ''
        #if browsed to a file use that
        if os.path.isfile(abs_path):
            full_path = abs_path
        else:
            #if file_name not specified give an error
            if not file_name:
                self.report({'INFO'},"please enter a file name to import")
                return {'FINISHED'}
            full_path = os.path.join(abs_path,file_name)

        if not context.selected_objects:
            self.report({'INFO'},"please select character in object mode to import weights onto")
            return {'FINISHED'}
            
        sel = context.selected_objects[0]
        if sel.type != 'MESH':
            self.report({'INFO'},"please select character in object mode that has skin weights")
            return {'FINISHED'}  
            
        mesh_name = sel.name


        print("importWeightsOperator dir path: %s" %(full_path))
        importWeightOnSelected(mesh_name = mesh_name, weightFile = full_path, clean_zero_weights = True, use_selected = use_selected )
        return {'FINISHED'}
        
class naSkinWeightIOPanel(Panel):
    bl_label = "naSkinWeightIOPanel Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.skinweightsio_prop, "dir_path")
        layout.prop(context.scene.skinweightsio_prop, "file_name")
        layout.prop(context.scene.skinweightsio_prop, "use_selected")
        layout.operator( "obj.exportweights" )
        layout.operator( "obj.importweights" )
        
def register():
    bpy.utils.register_class(exportWeightsOperator)
    bpy.utils.register_class(importWeightsOperator)
    bpy.utils.register_class(naSkinWeightIOPanel)
    
    bpy.utils.register_class(skinWeightsIOProperties)
    bpy.types.Scene.skinweightsio_prop = PointerProperty( type = skinWeightsIOProperties )

def unregister():
    bpy.utils.unregister_class(exportWeightsOperator)
    bpy.utils.unregister_class(importWeightsOperator)
    bpy.utils.unregister_class(naSkinWeightIOPanel)
    
    bpy.utils.unregister_class(skinWeightsIOProperties)
    del bpy.types.Scene.skinweightsio_prop



####
def exportWeightOnSelected(mesh_name = None, weightFile = ''):
    """
    export skin weights on selected character
    mesh_name - name of character want to export weights the data object name
    weightFile - full path to file to save weights
    """
    def _getBoneNamesWeightedToVertex(mesh_name = None, vert_id = None):
        #get list of bone names weighted to vertex
        result = []
        for i in range(0, len(bpy.data.objects[mesh_name].data.vertices[vert_id].groups) ):
            bone_index = bpy.data.objects[mesh_name].data.vertices[vert_id].groups[i].group
            bone_name = bpy.data.objects[mesh_name].vertex_groups[bone_index].name
            result.append(bone_name)
        return result

    def _getVertBoneIndexForBone(mesh_name = None, vert_id = None, bone = None):
        #get int bone index for given vertex that matches given bone name
        result = None
        for i in range(0, len(bpy.data.objects[mesh_name].data.vertices[vert_id].groups) ):
            bone_index = bpy.data.objects[mesh_name].data.vertices[vert_id].groups[i].group
            bone_name = bpy.data.objects[mesh_name].vertex_groups[bone_index].name
            if bone_name == bone:
                result = i
                break
        return result
        
    #assumes your character is selected
    #no error checking
    outDir = os.path.dirname(weightFile)
    if not os.path.exists(outDir):
        print('Requires an out directory that exists to write weight file')
        return
    
    vertexIds = []
    weightDict = {} #will hold weights info

    charObj = bpy.data.objects[mesh_name]

    vtxGroups = []
    vtxGroups = [ (grp.name,grp.index) for grp in charObj.vertex_groups ]

    mesh = charObj.data

    vertexIds = [ v.index for v in mesh.vertices ]


    for vtxId in vertexIds:
        boneDict = {}
        for bone, boneIndex in vtxGroups:
            weight = 0
            #a vertex might have no weight on a bone
            bone_names_weighted_to_vert = _getBoneNamesWeightedToVertex(mesh_name = charObj.name, vert_id = vtxId)
            if bone in bone_names_weighted_to_vert:
                #the group index on the vertex is different from the entire mesh
                vert_bone_index = _getVertBoneIndexForBone(mesh_name = charObj.name, vert_id = vtxId, bone = bone)
                weight = charObj.data.vertices[vtxId].groups[vert_bone_index].weight
            weight = round(weight,4)
            print('export weights on vtx >>> %s for bone >>> %s weight >> %s' %(vtxId,bone,weight) )
            boneDict[ bone ] = weight
        weightDict[vtxId] = boneDict #update weight info
        
    print(weightDict)
        
    #export weights to file
    with open( weightFile, 'w' ) as f:
        json.dump(weightDict,f, indent = 4)
    
    

def importWeightOnSelected(mesh_name = None, weightFile = '', clean_zero_weights = True, use_selected = False):
    """
    import skin weights on selected character
    mesh_name - name of character to import weights onto
    weightFile - full path to file with weights
    clean_zero_weights - after importing weights should all zero weight vertex groups be removed from all verts. default True to have fewer bones per vert
    use_selected - should we import weights only on selected vertices - default is False
    """
    def _cleanZeroWeightGroups(mesh_name):
        #remove zero weight vertex groups from all vertices
        for i in range(0,len(bpy.data.objects[mesh_name].vertex_groups)):
            bpy.data.objects[mesh_name].vertex_groups.active_index = i
            bpy.ops.object.vertex_group_clean()
    
    if not os.path.exists(weightFile):
        print('Requires weightfile path to exist')
        return
        
    
    #assumes your character is selected
    #no error checking
    
    weightDict = {} #will hold weights info

    with open( weightFile, 'r' ) as f:
        weightDict = json.load(f)
    
    charObj = bpy.data.objects[mesh_name]
    
    #if importing to selected vertices do nothing if no verts are selected
    sel_vertices = []
    if use_selected:
        sel_vertices = [vert.index for vert in charObj.data.vertices if vert.select ]
        if not sel_vertices:
            print("please select some vertices to import onto when using use_selected option - doing nothing")
            return

    for vtxId, bones in weightDict.items():
        if use_selected:
            if int(vtxId) not in sel_vertices:
                continue
                
        print( vtxId )
        for boneName, boneWeight in bones.items():
            print('import weights on vtx >>> %s for bone >>> %s weight >> %s' %(vtxId,boneName,boneWeight) )
            #change weights here. No error checking. example wouldnt work if couldnt find bone in armature
            charObj.vertex_groups[ boneName ].add( [int(vtxId)], float(boneWeight), 'REPLACE' )

    
    if clean_zero_weights:
        _cleanZeroWeightGroups(mesh_name)

#last modified
#112621 -- made into addon
#051421 -- working on initial release
#020219 -- working on initial release


#inspired by online post: https://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-using-blenders-python-api
