
import bpy
import os
import json


####add on portion
bl_info = {
    "name":"armature bones import export",
    "description":"armature import export",
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


class armatureIOProperties(PropertyGroup):
    dir_path = StringProperty(
        name = "Browse",
        description = "Pick path to export/import to/from either a file or a directory",
        maxlen = 200,
        subtype = 'FILE_PATH'
    )

    file_name = StringProperty(
        name = "file_name",
        description = "file name for armature file ex: Armature.json"
        ) 

    armature = StringProperty(
        name = "armature",
        description = "armature name - the data object name"
        )
    
    bones = StringProperty(
        name = "bones",
        description = "optional specific bones to import - space separated. if none specified it exports all bones of armature"
        )    

    #for default face skeleton
    face_parts = StringProperty(
        name = "face_parts",
        description = "when specified only build the given face parts otherwise build all face parts. space separated. face parts supported: head,jaw,neck,tounge,ears,eyes"
        )     
    ##

class exportArmatureOperator(Operator):
    """export armature
    """
    bl_idname = "obj.exportarmature"
    bl_label = "export"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        file_name = context.scene.armatureio_prop.file_name
        path = context.scene.armatureio_prop.dir_path
        armature = context.scene.armatureio_prop.armature
        bones_arg = context.scene.armatureio_prop.bones
        
        abs_path = bpy.path.abspath(path)
        
        bones = []
        if bones_arg:
            bones = bones_arg.split(' ')
        
        exportArmature(armature = armature, export_dir = abs_path, bones = bones, file_name = file_name )
        return {'FINISHED'}


class importArmatureOperator(Operator):
    """export armature
    """
    bl_idname = "obj.importarmature"
    bl_label = "import"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        file_name = context.scene.armatureio_prop.file_name
        path = context.scene.armatureio_prop.dir_path
        armature = context.scene.armatureio_prop.armature
        
        abs_path = bpy.path.abspath(path)
        
        full_path = abs_path
        
        #if navigated to directory require using the file_name input
        if os.path.isdir(abs_path):
            #if file_name not specified give an error
            if not file_name:
                self.report({'INFO'},"please enter a file name to import")
                return {'FINISHED'}
            full_path = os.path.join( abs_path, file_name )
        
        importArmature(armature = armature, file_path = full_path )
        return {'FINISHED'}

class importDefaultFaceArmatureOperator(Operator):
    """export armature
    """
    bl_idname = "obj.importdefaultfacearmature"
    bl_label = "build face armature"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        #get the face parts should import
        armature = context.scene.armatureio_prop.armature
        face_parts = context.scene.armatureio_prop.face_parts
        import_types = face_parts.split(' ')
        
        importDefaultFaceSkeletonDict( armature = armature, data_dict = FACE_DEFAULT_DICT, import_types = import_types )
        return {'FINISHED'}

class naArmatureIOPanel(Panel):
    bl_label = "Armature Import/Export Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.armatureio_prop, "dir_path")
        layout.prop(context.scene.armatureio_prop, "file_name")
        layout.prop(context.scene.armatureio_prop, "armature")
        layout.prop(context.scene.armatureio_prop, "bones")
        layout.operator( "obj.exportarmature" )
        layout.operator( "obj.importarmature" )
        layout.label(text = "-"*50)
        layout.label(text = "For creating a default Face Skeleton")
        layout.prop(context.scene.armatureio_prop, "face_parts")
        layout.prop(context.scene.armatureio_prop, "armature")
        layout.operator( "obj.importdefaultfacearmature" )
        
        
def register():
    bpy.utils.register_class(exportArmatureOperator)
    bpy.utils.register_class(importArmatureOperator)
    bpy.utils.register_class(importDefaultFaceArmatureOperator)
    bpy.utils.register_class(naArmatureIOPanel)
    
    bpy.utils.register_class(armatureIOProperties)
    bpy.types.Scene.armatureio_prop = PointerProperty( type = armatureIOProperties )

def unregister():
    bpy.utils.unregister_class(exportArmatureOperator)
    bpy.utils.unregister_class(importArmatureOperator)
    bpy.utils.unregister_class(importDefaultFaceArmatureOperator)
    bpy.utils.unregister_class(naArmatureIOPanel)
    
    bpy.utils.unregister_class(armatureIOProperties)
    del bpy.types.Scene.armatureio_prop



def exportArmature( armature = None, export_dir = '/Users/Nathaniel/Documents/src_blender/python/snippets/tmp', bones = [], file_name = ''  ):
    """
    armature - name for armature the data object name
    export_dir - directory in which to save armature json. if this is a full path to a file name it uses this instead of the file_name argument
    bones - optional list of bones to export. if empty it exports all bones in armature
    file_name - optional name for json file to save such as Armature.json. if it is not provided it uses the armature name
    """
    if not os.path.isdir(export_dir) and not os.path.isfile(export_dir) :
        print("could not find export path %s. enter one that exists" %export_dir)
        return
        
    if not armature:
        print("requires an armature name. the data object name")
        return
    
    dat_dict = {} #what we want to export
    
    #need to have armature selected
    _selectOnlyThing(thing = armature)
    
    #compiling the data for armature
    bpy.ops.object.mode_set(mode='EDIT')
    bone_names = [ eb.name for eb in bpy.data.objects[armature].data.edit_bones] #default to all bones in armature
    if bones:
        bone_names = bones
    
    for bone in bone_names:
        edit_bone_data = {}
        pose_bone_data = {}
        
        #edit bone data
        #need to be in edit mode for getting parent - assumes armature is selected
        bpy.ops.object.mode_set(mode='EDIT')
        eb = bpy.data.objects[armature].data.edit_bones[bone]
        
        #adding edit bone attributes here
        edit_bone_data['head'] = tuple( eb.head )#(0,3,5)
        edit_bone_data['tail'] = tuple( eb.tail )
        edit_bone_data['roll'] = eb.roll #in radians
        edit_bone_data['parent'] = eb.parent.name if eb.parent else ''
        ##
        
        #pose bone data
        bpy.ops.object.mode_set(mode='POSE')
        pb = bpy.data.objects[armature].pose.bones[bone]
        
        #adding pose bone attributes here
        pose_bone_data['location'] = tuple( pb.location ) #(4,5,6)
        pose_bone_data['scale'] = tuple( pb.scale )
        pose_bone_data['rotation_mode'] = pb.rotation_mode
        pose_bone_data['rotation'] = tuple( pb.rotation_euler )
        if pb.rotation_mode == 'QUATERNION':
            pose_bone_data['rotation'] = tuple( pb.rotation_quaternion )
        pose_bone_data['custom_shape'] = pb.custom_shape.name if pb.custom_shape else '' #animator curve for bone - remember on import data bones should have show_wire to True if using curve shape for bone
        pose_bone_data['custom_shape_scale'] = pb.custom_shape_scale
        ##
        
        dat_dict[bone] = {'edit_bone_data':edit_bone_data, 'pose_bone_data':pose_bone_data}
    
    #exporting armature to json
    ##
    #if directory provided is a full path to a file name use it
    export_fullpath = ''
    if os.path.isfile(export_dir):
        export_fullpath = export_dir
    else:
        #use the file_name if it exists
        export_file_name = ''
        if file_name:
            export_file_name = file_name
        else:
            #use the armature name to figure out file name
            armature_edit = armature.replace(' ','_')    
            export_file_name = armature_edit+'.json'
            
        export_fullpath = os.path.join(export_dir,export_file_name)

    ##
    outDir = os.path.dirname(export_fullpath)
    if not os.path.exists(outDir):
        print('Requires an out directory that exists to write armature file %s' %outDir)
        return
    ##
    
    print("exporting >>> %s to file name: %s" %(dat_dict,export_fullpath) )
    
    with open(export_fullpath,"w") as outf:
        json.dump(dat_dict,outf, indent=4)

def _selectOnlyThing(thing = None):
    #might need to be in object mode
    bpy.ops.object.mode_set(mode="OBJECT")
    if thing:
        thing_obj = bpy.data.objects[thing]
        #make it only selection
        bpy.ops.object.select_all(action='DESELECT')
        thing_obj.select = True
        bpy.context.scene.objects.active = thing_obj    
    

def importArmature(armature = None, file_path = ''):
    """
    armature - armature name - the data object name
    """
    if not os.path.exists(file_path):
        print("could not find %s skipping" %file_path)
        return

    if not armature:
        print("requires armature to exist already")
        return

    dat_dict = {}
    with open(file_path) as f:
        dat_dict = json.load(f)
    print("read armature info>>",dat_dict)
    
    importArmatureFromDict( armature = armature, data_dict = dat_dict )


def importArmatureFromDict( armature = None, data_dict = None, use_bones = []):
    """
    armature - armature name - the data object name
    data_dict - see export for the format it is a dictionary with edit bone and pose bone information
    use_bones - when specified it limits import to only provide bone names
    """
    if not data_dict:
        print("requires data dictionary with bone information")
        return

    if not armature:
        print("requires armature to exist already")
        return
        
    dat_dict = {}
    dat_dict = data_dict
    print("using armature info>>",dat_dict)
    

    #ensure in edit mode of armature
    bpy.context.scene.objects.active = bpy.data.objects[armature]
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        
    for bone, dat in dat_dict.items():
        
        #only import specified bones in input parameter
        if use_bones:
            if bone not in use_bones:
                continue
        
        print(bone)
        edit_bone_data = dat.get('edit_bone_data') or None #assuming all keys exist
        head = edit_bone_data.get('head') or None
        tail = edit_bone_data.get('tail') or None
        roll = edit_bone_data.get('roll') or 0.0
        
        pose_bone_data = dat.get('pose_bone_data') or None
        location = pose_bone_data.get('location') or None
        scale = pose_bone_data.get('scale') or None
        rotation_mode = pose_bone_data.get('rotation_mode') or None
        rotation = pose_bone_data.get('rotation') or None        
        custom_shape = pose_bone_data.get('custom_shape') or '' 
        custom_shape_scale = pose_bone_data.get('custom_shape_scale') or 1.0
        
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone_obj = None
        #if it exists already use it.
        if bone in bpy.data.objects[armature].data.edit_bones:
            bone_obj = bpy.data.objects[armature].data.edit_bones[bone]
        if not bone_obj:
            #make edit bone from scratch
            bone_obj = bpy.data.objects[armature].data.edit_bones.new(bone)
            
        #position edit bone
        bone_obj.head = head
        bone_obj.tail = tail
        bone_obj.roll = roll
        
        #position pose bone
        bpy.ops.object.mode_set(mode='POSE')
        pb = bpy.data.objects[armature].pose.bones[bone]
        pb.location = location
        pb.scale = scale
        pb.rotation_mode = rotation_mode
        if rotation_mode != 'QUATERNION':
            pb.rotation_euler = rotation
        else:
            pb.rotation_quaternion = rotation
        #if custom shape doesnt exist dont try to add it to bone
        if custom_shape in bpy.data.objects:
            pb.custom_shape = bpy.data.objects[custom_shape]
            pb.custom_shape_scale = custom_shape_scale
            bpy.data.objects[armature].data.bones[bone].show_wire = True #show wire


    #do the bone parenting at end so have all bones created
    #ensure in edit mode of armature
    bpy.context.scene.objects.active = bpy.data.objects[armature]
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    for bone, dat in dat_dict.items():
        #only import specified bones in input parameter
        #if use_bones:
        #    if bone not in use_bones:
        #        continue
        
        #allowing any existing bone to be considered for parenting to support successive build workflow. like built jaw and head then later neck.
        if not bone in bpy.data.objects[armature].data.edit_bones:
            continue
            
        bone_obj = bpy.data.objects[armature].data.edit_bones[bone]
        edit_bone_data = dat.get('edit_bone_data') or None #assuming all keys exist
        parent = edit_bone_data.get('parent') or None 
        
        #skip parenting to parent if cannot find it in scene
        if not parent:
            continue
            
        if not parent in bpy.data.objects[armature].data.edit_bones:
            continue
            
        if parent:
            bone_obj.parent = bpy.data.objects[armature].data.edit_bones[parent]     
    ####



##for a simple default face skeleton
FACE_DEFAULT_DICT = {}
FACE_DEFAULT_DICT ={
    
    "eye.L": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                0.9440985321998596,
                -1.4067391157150269,
                2.620311975479126
            ],
            "parent": "head",
            "roll": -3.141594648361206,
            "tail": [
                0.9440985321998596,
                -2.330247402191162,
                2.620311975479126
            ]
        }
    },
    "head": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                -0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                0.0,
                0.0,
                0.0
            ],
            "parent": "neck_top",
            "roll": 0.0,
            "tail": [
                0.0,
                0.0,
                2.7171976566314697
            ]
        }
    },
    "ear.L": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                -0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                1.8274961709976196,
                0.0,
                1.2506003379821777
            ],
            "parent": "head",
            "roll": 1.570796251296997,
            "tail": [
                2.82749605178833,
                0.0,
                1.2506003379821777
            ]
        }
    },
    "eye.R": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                -0.9440985321998596,
                -1.4067391157150269,
                2.620311975479126
            ],
            "parent": "head",
            "roll": 3.141594648361206,
            "tail": [
                -0.9440985321998596,
                -2.330247402191162,
                2.620311975479126
            ]
        }
    },
    "ear.R": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                -1.8274961709976196,
                0.0,
                1.2506003379821777
            ],
            "parent": "head",
            "roll": -1.570796251296997,
            "tail": [
                -2.82749605178833,
                0.0,
                1.2506003379821777
            ]
        }
    },
    "jaw": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                -0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                0.0,
                -0.6735531091690063,
                0.0
            ],
            "parent": "head",
            "roll": -3.1415932178497314,
            "tail": [
                0.0,
                -2.843705415725708,
                0.0
            ]
        }
    },
    "neck_top": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                -0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                0.0,
                0.0,
                -1.516793966293335
            ],
            "parent": "neck_base",
            "roll": 0.0,
            "tail": [
                0.0,
                0.0,
                0.0
            ]
        }
    },
    "tounge_base": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                -0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                0.0,
                -0.6735531091690063,
                0.6236732602119446
            ],
            "parent": "head",
            "roll": -3.1415936946868896,
            "tail": [
                0.0,
                -2.2545957565307617,
                0.6236732602119446
            ]
        }
    },
    "neck_base": {
        "pose_bone_data": {
            "custom_shape": "",
            "rotation": [
                0.0,
                -0.0,
                0.0
            ],
            "location": [
                0.0,
                0.0,
                0.0
            ],
            "rotation_mode": "XYZ",
            "scale": [
                1.0,
                1.0,
                1.0
            ]
        },
        "edit_bone_data": {
            "head": [
                0.0,
                0.0,
                -2.516793966293335
            ],
            "parent": "",
            "roll": 0.0,
            "tail": [
                0.0,
                0.0,
                -1.516793966293335
            ]
        }
    }
}

def _getFaceBoneNamesFromImportTypes( import_types = [] ):
    """only used for importing default skeleton. the names here depend on keys of FACE_DEFAULT_DICT
    """
    result = []
    
    if not import_types:
        #build all face parts
        result.extend( ['head','jaw','neck_base','neck_top','ear.L','ear.R','eyes.L','eyes.R','tounge_base'] ) 
        return result
        
    for typ in import_types:
        if typ == "head":
            result.append( 'head' )
        elif typ == "jaw":
            result.append( 'jaw' )
        elif typ == "neck":
            result.extend( ['neck_base','neck_top'] )
        elif typ == "ears":
            result.extend( ['ear.L','ear.R'] )
        elif typ == "eyes":
            result.extend( ['eye.L','eye.R'] )
        elif typ == "tounge":
            result.extend( ["tounge_base"] )
            
    return result
            

def importDefaultFaceSkeletonDict( armature = None, data_dict = FACE_DEFAULT_DICT, import_types = [] ):
    """will import a simple face skeleton that can be used for weighting
    data_dict - face skeleton dictionary information for edit and pose bones - usually not provided
    import_types - when specified only face parts specified here will be created ex: ['head','jaw'] will only import head and jaw
    available types: head, jaw, neck, eyes, tounge, ears
    """
    use_bones = []
    use_bones = _getFaceBoneNamesFromImportTypes( import_types )
    
    importArmatureFromDict( armature = armature, data_dict = data_dict, use_bones = use_bones )




"""
import bpy
import sys
#example if wanted to test script without addon part. change to your path here
sys.path.append('/Users/Nathaniel/Documents/src_blender/python/naBlendShape')

import naArmatureIOAddOn as mod
import imp
imp.reload(mod)

#mod.exportArmature( armature = 'Armature', export_dir = '/Users/Nathaniel/Documents/src_blender/python/snippets/tmp',bones = [] )
    
mod.importArmature( armature = 'Armature', file_path = '/Users/Nathaniel/Documents/src_blender/python/snippets/tmp/Armature.json' )    
"""


#last modified
#122021,1221 -- working on initial release - worked on import. worked on export.
