
import bpy
import os
import json


####add on portion
bl_info = {
    "name":"driver blendshapes import export",
    "description":"driver blendshapes import export",
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


class driverIOProperties(PropertyGroup):
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

class exportDriverOperator(Operator):
    """export driver. first enter in some blendshapes and enter in face mesh with blendshapes to export. if no blendshapes provided it exports all blendshapes.
    """
    bl_idname = "obj.exportdriver"
    bl_label = "export"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        path = context.scene.driverio_prop.dir_path
        mesh = context.scene.driverio_prop.mesh
        blendshapes_arg = context.scene.driverio_prop.blendshapes
        
        abs_path = bpy.path.abspath(path)
        
        if not os.path.isdir(abs_path):
            self.report({'INFO'},"please navigate to a folder to export drivers")
            return {'FINISHED'}

        if not mesh:
            self.report({'INFO'},"please enter in name for the mesh with shape keys - the data object name")
            return {'FINISHED'}

        blendshapes = []
        if blendshapes_arg:
            blendshapes = blendshapes_arg.split(',')
        
        #if no blendshapes provided export all blendshapes of mesh
        if not blendshapes:
            blendshapes = getAllBlendshapes( mesh )
        
        print("exporting >>> to directory %s blendshapes: %s for mesh %s" %(abs_path,blendshapes,mesh) )
        
        exportDriver(export_dir = abs_path, blendshapes = blendshapes, face_mesh = mesh )
        return {'FINISHED'}
        

class importDriverOperator(Operator):
    """import driver. first enter in some blendshapes and enter in face mesh with blendshapes to import. if no blendshapes provided it imports all blendshapes that exist in folder specified.
    """
    bl_idname = "obj.importdriver"
    bl_label = "import"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        path = context.scene.driverio_prop.dir_path
        mesh = context.scene.driverio_prop.mesh
        blendshapes_arg = context.scene.driverio_prop.blendshapes
        
        abs_path = bpy.path.abspath(path)

        if not os.path.isdir(abs_path) and not os.path.isfile(abs_path) :
            self.report({'INFO'},"please navigate to a folder or file to import drivers")
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
            
            #if no blendshapes provided import all blendshapes of mesh that exist in folder
            if not blendshapes:
                blendshapes = getAllBlendshapes( mesh )
        
            import_file_paths = getAllDriverFullFilePathsForBlendshapes( folder = abs_path, blendshapes = blendshapes)
        
        print("importing >>> mesh %s file_paths %s" %(mesh,import_file_paths) )
        
        importDriver( face_mesh = mesh, file_paths = import_file_paths  )
        return {'FINISHED'}


class naDriverIOPanel(Panel):
    bl_label = "Driver Import/Export Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.driverio_prop, "dir_path")
        layout.prop(context.scene.driverio_prop, "mesh")
        layout.prop(context.scene.driverio_prop, "blendshapes")
        layout.operator( "obj.exportdriver" )
        layout.operator( "obj.importdriver" )
        
def register():
    bpy.utils.register_class(exportDriverOperator)
    bpy.utils.register_class(importDriverOperator)
    bpy.utils.register_class(naDriverIOPanel)
    
    bpy.utils.register_class(driverIOProperties)
    bpy.types.Scene.driverio_prop = PointerProperty( type = driverIOProperties )

def unregister():
    bpy.utils.unregister_class(exportDriverOperator)
    bpy.utils.unregister_class(importDriverOperator)
    bpy.utils.unregister_class(naDriverIOPanel)
    
    bpy.utils.unregister_class(driverIOProperties)
    del bpy.types.Scene.driverio_prop



def exportDriver( export_dir = '/Users/Nathaniel/Documents/src_blender/python/snippets/tmp',
                                    face_mesh = None, 
                                    blendshapes = [] ):
    """
    export_dir - the directory in which to export the blendshape drivers. 1 file per blendshape
    face_mesh - this is the mesh object name that has shapekeys
    blendshapes - this is a list of shapekey names to export
    """
    
    if not os.path.isdir(export_dir):
        print("could not find export directory %s. enter one that exists" %export_dir)
        return
        
    export_data_list = [] #list of dictionaries to export
    
    for shp in blendshapes:
        export_data = {}
        
        
        drv_info = _getDriverFromShapekey( face_mesh = face_mesh, blendshape = shp ) 
        drv = drv_info.get('driver') or None
        fcrv = drv_info.get('fcurve') or None
        
        if drv is None:
            print("skipping blendshape: %s could not find driver for it" %shp)
            continue
            
        var_data_list = []  # [ {var 0 info}, {var 1 info} ...]

        #extract variable info
        for var in drv.variables:
            var_info = {}
            var_info['name'] = var.name
            var_info['type'] = var.type #ex: 'SINGLE_PROP'
            var_target = var.targets[0] #assuming single DriverTarget exists
            var_info['id_type'] = var_target.id_type #ex: 'OBJECT' or 'KEY'
            var_info['id_name'] = var_target.id.name #on import setting id and need to use bpy.data.objects or bpy.data.shape_keys with key depending on id_type
            var_info['data_path'] = var_target.data_path #ex: 'pose.bones["pos_anim"].location.z'
            
            var_data_list.append(var_info)
            
        #extract keyframe info    
        keyframe_data_list = [] #[ {keyframe point 0 info}, {keyframe point 1 info} ...  ]
        for point in fcrv.keyframe_points:
            point_info = {}
            point_info['co'] = tuple(point.co)
            point_info['interpolation'] = point.interpolation
            point_info['handle_left'] = tuple(point.handle_left)
            point_info['handle_left_type'] = point.handle_left_type
            point_info['handle_right'] = tuple(point.handle_right)
            point_info['handle_right_type'] = point.handle_right_type
            
            keyframe_data_list.append(point_info)
        
        export_data['type'] = drv.type #ex: 'SCRIPTED'    
        export_data['expression'] = drv.expression #ex: '0 if drvloc < 0 else drvloc'
        export_data['shapekey'] = shp
        export_data['var_data_list'] = var_data_list
        export_data['keyframe_data_list'] = keyframe_data_list
        
        
        export_data_list.append(export_data)    
        
    #export to json the drivers
    for dat_dict in export_data_list:
        shp = dat_dict['shapekey']
        export_file_name = _getDriverFileFromBlendshape(shp)
        export_fullpath = os.path.join(export_dir,export_file_name)
        print("exporting >>> %s to file name: %s" %(dat_dict,export_fullpath) )
        
        with open(export_fullpath,"w") as outf:
            json.dump(dat_dict,outf, indent=4)        

def _getDriverFileFromBlendshape(blendshape = ''):
    shp_edit = blendshape.replace(' ','_') #dont want spaces in file names
    return shp_edit+'_driver.json'
    

def importDriver(face_mesh = None, file_paths = ['/Users/Nathaniel/Documents/src_blender/python/snippets/tmp/Key_1_driver.json']):
    """
    face_mesh - mesh data object name with shapekeys
    file_paths - full file paths to driver json file
    """
    
    #no error checking - assumes everything exists to import driver
    faceObj = bpy.data.objects[face_mesh]
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print("could not find %s skipping" %file_path)
            continue
            
        dat_dict = {}
        with open(file_path) as f:
            dat_dict = json.load(f)
        print("read driver info>>",dat_dict)

        shapekey = dat_dict['shapekey']
        driver = faceObj.data.shape_keys.key_blocks[shapekey].driver_add("value").driver
        driver.type = dat_dict['type']
        driver.expression = dat_dict['expression']
        
        #import variable info
        var_data_list = dat_dict['var_data_list']
        for var_info in var_data_list:
            
            var = driver.variables.new()
            var.name = var_info['name']
            var.type = var_info['type']
            id_type = var_info['id_type']
            var.targets[0].id_type = id_type #assuming single target exists
            if id_type == 'OBJECT':
                var.targets[0].id = bpy.data.objects[ var_info['id_name'] ]
            elif id_type == 'KEY':
                var.targets[0].id = bpy.data.shape_keys[ var_info['id_name'] ]
            else:
                print("import doesnt support id_type %s" %id_type )
            var.targets[0].data_path = var_info['data_path']
        
        #import keyframe info
        keyframe_data_list = dat_dict['keyframe_data_list']
        
        fcurve = faceObj.data.shape_keys.animation_data.drivers[-1] #assuming last driver is latest just added #faceObj.data.shape_keys.animation_data.drivers[0]
        print("going to edit fcurve on datapath >>> %s" %(fcurve.data_path) )
    
        #need to remove the modifier on fcurve so can create custom keyframes
        fcurve.modifiers.remove( fcurve.modifiers[0] )
    
    
        for keyframe_info in keyframe_data_list:
            #create keyframe point - assumes all keys exist
            position = keyframe_info['co']
            point = fcurve.keyframe_points.insert(position[0],position[1])
            point.interpolation = keyframe_info['interpolation']
            point.handle_left_type = keyframe_info['handle_left_type']
            point.handle_right_type = keyframe_info['handle_right_type']
            point.handle_left = keyframe_info['handle_left']
            point.handle_right = keyframe_info['handle_right']
            
            
def _getDriverFromShapekey( face_mesh = None, blendshape = None ):
    """get the Driver object and fcurve that is driving given blendshape. result is dict with 'driver' and 'fcurve' keys
    """
    
    result = {}
    
    for fcrv in bpy.data.objects[face_mesh].data.shape_keys.animation_data.drivers:
        dat_path = fcrv.data_path #ex: 'key_blocks["Key 1"].value' 
        #check whether blendshape in data path
        shp_str = (dat_path.split('[')[1]).split(']')[0]
        if shp_str == '"%s"' %blendshape:
            result['driver'] = fcrv.driver
            result['fcurve'] = fcrv
            break
            
    return result
        
    
def getAllBlendshapes( face_mesh = None ):
    """return blendshape names excluding Basis
    """
    faceObj = bpy.data.objects[face_mesh]
    return [x.name for x in faceObj.data.shape_keys.key_blocks if x.name != 'Basis']
    
def getAllFilesWithSuffixInFolder( folder = '', suffix = '_driver.json' ):
    """assumes all driver files end with given suffix. returns only file names not the full paths
    """
    if not os.path.isdir(folder):
        print("requires a folder to exist: %s" %folder)
        return []
    
    files_in_folder = os.listdir(folder)   #might want to check if files have a shapekey name that is in current scene
    return [x for x in files_in_folder if x.endswith(suffix) ]
    
def getAllDriverFullFilePathsForBlendshapes( folder = '', blendshapes = []):
    """returns list of full file paths to driver files given some blendshape names and a folder to check
    """
    result = []
    all_driver_files = getAllFilesWithSuffixInFolder(folder = folder)
    for shp in blendshapes:
        driver_file_name = _getDriverFileFromBlendshape(blendshape = shp)
        if not driver_file_name in all_driver_files:
            print("skipping blendshape %s could not find it in folder %s" %(shp,folder) )
            continue
        result.append( os.path.join(folder,driver_file_name) )
        
    return result    

"""
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/naBlendShape')

import naShapekeyDriverIOAddOn as mod
import imp
imp.reload(mod)

#mod._getDriverFromShapekey( face_mesh = 'Plane', blendshape = 'Key 1' )


mod.exportDriver( export_dir = '/Users/Nathaniel/Documents/src_blender/python/snippets/tmp',
                                    face_mesh = 'Plane', 
                                    blendshapes = ['Key 1'])

#mod.importDriver(face_mesh = 'Plane', file_paths = ['/Users/Nathaniel/Documents/src_blender/python/snippets/tmp/Key_1_driver.json'])
 
"""


#last modified
#122221,1223 -- working on export that works for multiple cases automatically as well as exporting driver keyframes
#120121,1202 -- added support for bone driver or two shapekeys driving corrective shape. working on initial release


#inspired by:
#https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python/42123260

