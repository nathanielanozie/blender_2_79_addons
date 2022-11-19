

import bpy
from mathutils import Vector
import json
import os


####add on portion
bl_info = {
    "name":"blendshapes import export",
    "description":"blendshapes import export",
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


class blendshapeIOProperties(PropertyGroup):
    dir_path = StringProperty(
        name = "Browse",
        description = "Pick path to export/import to/from either a file or a directory",
        maxlen = 200,
        subtype = 'FILE_PATH'
    )

    mesh = StringProperty(
        name = "mesh",
        description = "mesh name with shapekeys - the data object name"
        )
    
    blendshapes = StringProperty(
        name = "blendshapes",
        description = "optional specific blendshapes to export/import - comma separated. if none specified it exports/imports all blendshapes of mesh"
        ) 

class exportBlendshapeOperator(Operator):
    """export blendshape. first enter in some blendshapes and enter in face mesh with blendshapes to export. if no blendshapes provided it exports all blendshapes.
    """
    bl_idname = "obj.exportblendshape"
    bl_label = "export"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        path = context.scene.blendshapeio_prop.dir_path
        mesh = context.scene.blendshapeio_prop.mesh
        blendshapes_arg = context.scene.blendshapeio_prop.blendshapes
        
        abs_path = bpy.path.abspath(path)
        
        if not os.path.isdir(abs_path):
            self.report({'INFO'},"please navigate to a folder to export blendshapes")
            return {'FINISHED'}

        if not mesh:
            self.report({'INFO'},"please enter in name for the mesh with shape keys - the data object name")
            return {'FINISHED'}

        blendshapes = []
        if blendshapes_arg:
            blendshapes = blendshapes_arg.split(',')
        
        exportShapeKey(mesh = mesh, shapes = blendshapes, dirPath = abs_path  )
        return {'FINISHED'}


class importBlendshapeOperator(Operator):
    """import blendshape. first enter in some blendshapes and enter in face mesh with blendshapes to import. if no blendshapes provided it imports all blendshapes that exist in folder specified.
    """
    bl_idname = "obj.importblendshape"
    bl_label = "import"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        path = context.scene.blendshapeio_prop.dir_path
        mesh = context.scene.blendshapeio_prop.mesh
        blendshapes_arg = context.scene.blendshapeio_prop.blendshapes
        
        abs_path = bpy.path.abspath(path)

        if not os.path.isdir(abs_path) and not os.path.isfile(abs_path) :
            self.report({'INFO'},"please navigate to a folder or file to import blendshapes")
            return {'FINISHED'}

        if not mesh:
            self.report({'INFO'},"please enter in name for the mesh with shape keys - the data object name")
            return {'FINISHED'}
            
        import_file_paths = []
        #if navigated to an exact file only import that file
        
        if os.path.isfile(abs_path):
            import_file_paths = [abs_path]
        
        else:
            #since navigated to a directory figure out files to import
            blendshapes = []
            if blendshapes_arg:
                blendshapes = blendshapes_arg.split(',')     
        
            #try to import only the blendshapes specified
            if blendshapes:
                for shp in blendshapes:
                    fname = _getBlendshapeFileFromBlendshape(shp)
                    import_file_paths.append( os.path.join(abs_path,fname) )
                    
            else:
                #otherwise try to import all blendshape files in folder
                import_file_paths = getAllFullFilesWithSuffixInFolder( folder = abs_path )
   
        print("importing >>> mesh %s file_paths %s" %(mesh,import_file_paths) )
        
        importShapeKey( mesh = mesh, shapeFiles = import_file_paths  )
        return {'FINISHED'}


class naBlendshapeIOPanel(Panel):
    bl_label = "Blendshape Import/Export Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.blendshapeio_prop, "dir_path")
        layout.prop(context.scene.blendshapeio_prop, "mesh")
        layout.prop(context.scene.blendshapeio_prop, "blendshapes")
        layout.operator( "obj.exportblendshape" )
        layout.operator( "obj.importblendshape" )

def register():
    bpy.utils.register_class(exportBlendshapeOperator)
    bpy.utils.register_class(importBlendshapeOperator)
    bpy.utils.register_class(naBlendshapeIOPanel)
    
    bpy.utils.register_class(blendshapeIOProperties)
    bpy.types.Scene.blendshapeio_prop = PointerProperty( type = blendshapeIOProperties )

def unregister():
    bpy.utils.unregister_class(exportBlendshapeOperator)
    bpy.utils.unregister_class(importBlendshapeOperator)
    bpy.utils.unregister_class(naBlendshapeIOPanel)
    
    bpy.utils.unregister_class(blendshapeIOProperties)
    del bpy.types.Scene.blendshapeio_prop
##end ui portion






def exportShapeKey( mesh = '', shapes = [], dirPath = '' ):
    """exports one file per blendshape
    mesh - is the data.objects name, it can be different from data.objects.data name
    shapes - are the actual shapekey names wish to export. if none provided it expects to export all blendshapes
    note it saves file names of form shape_shapeName where it replaces spaces with underscores
    so exporting a 'Key 1' shape with an already saved shape_Key_1.json would overwrite that shape
    dirPath - is directory to save the shape json files
    """

    """form of shape key data written out (vertDelta is in order of all vertices)
    
    {
    'shape':{ 'shapeName':'Key 1', 'vertDelta':[(0,0,0),(0,.25,.35)...(0,0,0)]
        }
    }
    
    """

    if not os.path.isdir(dirPath):
        print('Requires an out directory that exists to write shapekey file')
        return

    if not mesh in bpy.data.objects:
        print('Requires mesh: %s to exist in scene' %mesh)
        return

    if not bpy.data.objects[mesh].type == 'MESH':
        print('Requires mesh type for %s' %mesh)
        return

    #require mesh to have shape keys
    mesh_obj = bpy.data.objects[mesh].data
    
    if mesh_obj.shape_keys is None:
        print('requires mesh %s to have shape keys' %mesh)
        return
    
    #exit if no Basis shape key
    basis_name = 'Basis'
    if not basis_name in mesh_obj.shape_keys.key_blocks.keys():
        print('requires a basis shape named Basis on mesh %s exiting' %mesh)
        return
        
    if not shapes:
        print('trying to export all blendshapes')
        shapes = [x.name for x in mesh_obj.shape_keys.key_blocks if x.name != 'Basis']

    #start looping over shape keys to export
    print("trying to export shapes: %s" %shapes)
    for shp in shapes:
        shape_dict = {}
        num_verts = 0
        
        #check shp shapekey exists on mesh
        if not shp in mesh_obj.shape_keys.key_blocks.keys():
            print('could not find shapekey %s in mesh %s so skipping it' %(shp,mesh) )
            continue
            
        #todo: verify only upper and lower case letters and spaces and dots in shape key name
         
        num_verts = len( mesh_obj.shape_keys.key_blocks[shp].data )
        
        vert_delta_list = []
        
        for i in range(num_verts):
            vdelta = mesh_obj.shape_keys.key_blocks[basis_name].data[i].co - mesh_obj.shape_keys.key_blocks[shp].data[i].co
            vert_delta_list.append( (vdelta.x, vdelta.y, vdelta.z) )
        
        shape_dict['shape']={'shapeName':shp,'vertDelta':vert_delta_list}
        
        #export this shapekey and continue to next
        shp_filename = _getBlendshapeFileFromBlendshape(shp)
        shp_file = os.path.join(dirPath,shp_filename)
        with open( shp_file, 'w' ) as f:
            json.dump(shape_dict, f, indent=4)
            
def _getBlendshapeFileFromBlendshape(blendshape = ''):
    shp_edit = blendshape.replace(' ','_') #dont want spaces in file names
    return shp_edit+'_shape.json'
    


def importShapeKey( mesh = '', shapeFiles = [] ):
    """ 
    it should create the shape key if it doesnt exist if it does exist should overwrite only that shape key. not saving mesh in shape paths in case want to import onto a different named mesh
    with same topology.
    mesh -  is mesh data.objects name it needs to have at least a Basis shape.
    shapeFiles - list of full path to blendshape files - a shape file has vertex deltas from basis for a single shape key.
    """
    def _isShapeExists( mesh, shapeName ):
        mesh_obj = bpy.data.objects[mesh].data
        return shapeName in mesh_obj.shape_keys.key_blocks
        
    def _sculptShape( mesh, shapeName, vertDelta ):
        #sculpt shape using delta from basis
        mesh_obj = bpy.data.objects[mesh].data
        ##go through each vertex using the basis and the delta stored on disc
        for vid in range(num_mesh_verts):
            basis_pos = mesh_obj.shape_keys.key_blocks['Basis'].data[vid].co
            shp_pos = Vector( vertDelta[vid] ) #Vector so can subtract it
            #move vertices to sculpt shape
            mesh_obj.shape_keys.key_blocks[shapeName].data[vid].co = basis_pos - shp_pos
            
    ##check inputs
    #assert mesh exists
    #assert shapeFiles provided
    #assert mesh has a shapekey
    #check Basis shape exists on mesh
    
    if not mesh in bpy.data.objects:
        print('Requires mesh: %s to exist in scene' %mesh)
        return
        
    if not shapeFiles:
        print('Requires shape file names to import')
        return
        
    mesh_obj = bpy.data.objects[mesh].data #bpy.data.meshes[mesh]
    mesh_name = mesh_obj.name
    
    if mesh_obj.shape_keys is None:
        print("Requires at least a Basis shape on mesh %s" %mesh)
        return

    #exit if no Basis shape key on mesh
    basis_name = 'Basis'
    if not basis_name in mesh_obj.shape_keys.key_blocks.keys():
        print('requires a basis shape named Basis on mesh %s exiting' %mesh)
        return
        
    #need to be in object mode to edit shape keys
    bpy.ops.object.mode_set(mode="OBJECT")
    
    #loop over shape files 
    for shp_file in shapeFiles:
        if not os.path.exists(shp_file):
            print('could not find shape file %s , skipping' %shp_file)
            continue
        
        #read shape from disc
        shp_dict = {}
        with open( shp_file, 'r' ) as f:
            shp_dict = json.load(f)
        
        shapeName = shp_dict['shape']['shapeName']
        vertDelta = shp_dict['shape']['vertDelta']
        
        #skip if saved shape has different topology as mesh
        num_mesh_verts = len( mesh_obj.shape_keys.key_blocks['Basis'].data )
        num_shp_file_verts = len(vertDelta)
        if num_mesh_verts != num_shp_file_verts:
            print('Requires shape stored on file %s to have same topology as mesh %s, skipping' %(shp_file,mesh) )
            continue
            
        if _isShapeExists( mesh, shapeName ):
            #Edit existing shape
            _sculptShape( mesh, shapeName, vertDelta )

        else:
            #Create a new shape
            new_shp = bpy.data.objects[mesh].shape_key_add(shapeName)
            _sculptShape( mesh, shapeName, vertDelta )
            new_shp.interpolation = 'KEY_LINEAR'

def getAllFullFilesWithSuffixInFolder( folder = '', suffix = '_shape.json' ):
    """assumes all files end with given suffix. returns full paths
    """
    if not os.path.isdir(folder):
        print("requires a folder to exist: %s" %folder)
        return []
    
    files_in_folder = os.listdir(folder)
    return [os.path.join(folder,x) for x in files_in_folder if x.endswith(suffix) ]
    


#last modified
#042721 -- working on initial release - worked on initial import
#042621 -- working on initial release - worked on initial export


"""some examples of usage of some of the methods when not using ui
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/naBlendShape')

import naShapekeyIO as mod
import imp
imp.reload(mod)
#bpy.app.debug=True #temporary

#mod.exportShapeKey( mesh = 'Plane', shapes = ['Key 1'], dirPath = '/Users/Nathaniel/Documents/src_blender/python/naBlendShape/tmp' )
#mod.importShapeKey( mesh = 'Plane', shapeFiles = ['/Users/Nathaniel/Documents/src_blender/python/naBlendShape/tmp/shape_Key_1.json']) 


"""