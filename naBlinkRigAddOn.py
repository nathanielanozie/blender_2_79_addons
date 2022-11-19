#has an object for helping to create a blink with ability to sculpt vertical and fwdBck blink closing


#last modified
#110621 -- added ui
#071421 -- added setting some defaults for how blink should look
#071321 -- working on initial release. tested property and driver making


bl_info = {
    "name":"make simple blink for flat eyelid",
    "description":"make simple blink for flat eyelid",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}


#for tool
import bpy
from rna_prop_ui import rna_idprop_ui_prop_get
import re

#for ui need seven string fields
from bpy.props import(
    StringProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class BlinkMakerProperties(PropertyGroup):
    #here we make each textfield
    anim_bone = StringProperty(
        name = "anim_bone",
        description = "this is the bone we want to use for animating blink"
        )

    anim_blink_prop = StringProperty(
        name = "anim_blink_prop",
        description = "this is the custom property on the bone to be used for blink"
        )

    armature_name = StringProperty(
        name = "armature_name",
        description = "this is armature object name that has all bones to be blinked"
        )

    up_bones = StringProperty(
        name = "up_bones",
        description = "(optional) this is list of upper bones of blink (space separated)"
        )

    up_search_regex_string = StringProperty(
        name = "up_search_regex_string",
        description = "if no up_bones provided use this regular expression to find upper bones. ex: upLid_.+\.L"
        )

    dn_search_string = StringProperty(
        name = "dn_search_string",
        description = "string to search for in upper that we will replace to figure out lower bone ex: up"
        )
    dn_replace_string = StringProperty(
        name = "dn_replace_string",
        description = "string to replace in upper to figure out lower bone ex: dn"
        )


class BlinkMakerPanel(Panel):
    bl_label = "BlinkMakerPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        
        #here we add textfields and button to ui
        #
        layout = self.layout
        layout.label(text = "BlinkMakerPanel")
        
        #4 text fields in a row
        #text fields
        layout.prop( context.scene.blinkmaker_prop, "anim_bone", text = "anim_bone" )
        layout.prop( context.scene.blinkmaker_prop, "anim_blink_prop", text = "anim_blink_prop" )
        layout.prop( context.scene.blinkmaker_prop, "armature_name", text = "armature_name" )
        layout.prop( context.scene.blinkmaker_prop, "up_bones", text = "up_bones" )
        layout.prop( context.scene.blinkmaker_prop, "up_search_regex_string", text = "up_search_regex_string" )
        layout.prop( context.scene.blinkmaker_prop, "dn_search_string", text = "dn_search_string" )
        layout.prop( context.scene.blinkmaker_prop, "dn_replace_string", text = "dn_replace_string" )
        
        #button
        layout.operator( "obj.do_blinkmaker")
 
class BlinkMakerOperator(Operator):
    """create simple blink for flat eyelids/lips
    """
    bl_idname = "obj.do_blinkmaker"
    bl_label = "BlinkMaker"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
    
        self.report({'INFO'}, "Starting Blink Maker ...")
        
        bones_up_dn_data = get_bones_up_dn_data( up_search_regex_string = context.scene.blinkmaker_prop.up_search_regex_string, 
                                                    dn_search_string = context.scene.blinkmaker_prop.dn_search_string, 
                                                    dn_replace_string = context.scene.blinkmaker_prop.dn_replace_string, 
                                                    armature_object_name = context.scene.blinkmaker_prop.armature_name,
                                                    up_bones = context.scene.blinkmaker_prop.up_bones.split(' ') )
        
        print('bones_up_dn_data>>>',bones_up_dn_data)
        bobj = BlinkMaker(bones_up_dn_data = bones_up_dn_data, 
                            anim_bone= context.scene.blinkmaker_prop.anim_bone, 
                            anim_blink_prop = context.scene.blinkmaker_prop.anim_blink_prop, 
                            armature_name = context.scene.blinkmaker_prop.armature_name)
        bobj.run()


        self.report({'INFO'}, "Completed Blink Maker")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BlinkMakerOperator)
    bpy.utils.register_class(BlinkMakerPanel)
    bpy.utils.register_class(BlinkMakerProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.blinkmaker_prop = PointerProperty(
        type = BlinkMakerProperties
        )

def unregister():
    bpy.utils.unregister_class(BlinkMakerOperator)
    bpy.utils.unregister_class(BlinkMakerPanel)
    bpy.utils.unregister_class(BlinkMakerProperties)
    del bpy.types.Scene.blinkmaker_prop
###end ui





####For Tool
def get_bones_up_dn_data( up_search_regex_string = 'lid_up_.+\.L', dn_search_string = 'up', dn_replace_string ='dn', armature_object_name = '', up_bones=[] ):
    """returns dictionary of form {'lid_up_a.L':'lid_dn_a.L','lid_up_b.L':'lid_dn_b.L'}
    up_search_regex_string - used to figure out up bones. ex: 'lid_up_.+\.L' it searches all bones in armature that match this regular expression search string
    dn_search_replace_string - used to figure out dn bones. first in tuple what to search for, second in tuple what to replace with 
    up_bones - optional if provided it uses this list for the upper bone names instead of using regex ex: [lid_up_a.L,lid_up_b.L]
    (possibly later allow dn_bones list to be provided)
    """
    #assumes inputs provided
    
    result = {}
    
    #get upper bones
    upper_bones = up_bones
    if not upper_bones:
        upper_bones = [bone.name for bone in bpy.data.objects[armature_object_name].pose.bones if re.search(up_search_regex_string,bone.name) is not None ]
    
    #get lower bones using upper bones
    lower_bones = [b.replace(dn_search_string,dn_replace_string) for b in upper_bones]
    
    #construct result dictionary
    for up_bone, low_bone in zip(upper_bones,lower_bones):
        result[up_bone] = low_bone
    
    return result


class BlinkMaker(object):
    """an object for helping to create a blink with ability to sculpt vertical and fwdBck blink closing
    """
    def __init__(self, bones_up_dn_data = {},
            up_dn_axis = 'Y',
            fwd_bck_axis = 'Z',
            up_dn_blink_prop = 'blinkY',
            fwd_bck_blink_prop = 'blinkZ',
            anim_bone = 'anim',
            anim_blink_prop = 'blink',
            armature_name = 'Armature',
            up_close_pct = 70,
            dn_close_pct = 30
        ):
        self.bones_up_dn_data = bones_up_dn_data# {'upLid':'lowLid'} #keys are upper lid bones values is corresponding lower lid bone
        self.up_dn_axis = up_dn_axis    #'Y' #what direction does vertical motion of blink happen in
        self.fwd_bck_axis = fwd_bck_axis #'Z' ,                 #what directions does forward back motion of blink happen in
        self.up_dn_blink_prop = up_dn_blink_prop #'blinkY',  #tunable property for designing shape of blink in vertical motion
        self.fwd_bck_blink_prop = fwd_bck_blink_prop#'blinkZ'  #tunable property for designing shape of blink in forward back motion
        self.anim_bone = anim_bone #'anim'	#animator control bone that has the blink property to animate
        self.anim_blink_prop = anim_blink_prop #'blink'  #name of blink property control on animator control
        self.armature_name = armature_name #'Armature'     #armature object name
        self.up_close_pct = up_close_pct #70 #what percentage of total distance between up and bottom lid should top lids blink occur on
        self.dn_close_pct = dn_close_pct #30 #what percentage of total distance between up and bottom lid should bottom lids blink occur on
        
    def run(self):
        """
        creates blink properties on lid bones
        creates blink expressions
        sets blink defaults
        """
        self._createBlinkProperties()
        self._createBlinkExpressions()
        self._setBlinkPropertiesDefaults()
        
    def _createBlinkProperties(self):
        """
        create upDn property
        create fwdBck property
        assumes: the properties dont already exist
        """
        for up_bone, lo_bone in self.bones_up_dn_data.items():
            #make properties on both up and lo lid bones
            for blink_bone in [up_bone,lo_bone]:
                blinkbone = bpy.data.objects[self.armature_name].pose.bones[blink_bone]
              
                for bone_prop in [self.up_dn_blink_prop, self.fwd_bck_blink_prop]:
                    blinkbone[bone_prop] = 0.0
                    bone_prop = rna_idprop_ui_prop_get(blinkbone, bone_prop, create = True)
                    bone_prop['default']= 0.0
                    bone_prop['min']= -10.0
                    bone_prop['max']= 10.0
    
    def _createBlinkExpressions(self):
        """make animation bone blink property drive the vertical and fwd back motion of all lid bones
        assumes animation ctrl bone with blink property exists already
        """
        
        #for all bones of eyelid
        for up_bone, lo_bone in self.bones_up_dn_data.items():
            
            #for both upper and lower lid bone
            for bone, expr_multiplier in zip( [up_bone,lo_bone], [-1,1] ): #expr_multiplier is what to multiply final scripted expression by.needed because upLid goes down for blink. loLid goes up for blink.
                pbone = bpy.data.objects[self.armature_name].pose.bones[bone]
                
                #create driver on both upDn and fwdBck axis
                for axis_index, lid_bone_prop in zip( [ ['X','Y','Z'].index(self.up_dn_axis), ['X','Y','Z'].index(self.fwd_bck_axis) ], #might want to add support for lowercase axis 
                                                    [self.up_dn_blink_prop,self.fwd_bck_blink_prop] ):
                
                    drv = pbone.driver_add('location', axis_index ).driver 
                    drv.type = 'SCRIPTED'
                    #blink variable
                    var_blink = drv.variables.new()
                    var_blink.name = 'var_blink'
                    var_blink.targets[0].id = bpy.data.objects[self.armature_name]
                    var_blink.targets[0].data_path = 'pose.bones[\"%s\"][\"%s\"]' %(self.anim_bone,self.anim_blink_prop)
                    #upDn variable
                    var = drv.variables.new()
                    var.name = 'var'
                    var.targets[0].id = bpy.data.objects[self.armature_name]
                    var.targets[0].data_path = 'pose.bones[\"%s\"][\"%s\"]' %(pbone.name,lid_bone_prop)
                    #fwdBck motion should not have negative multiplier
                    if axis_index == ['X','Y','Z'].index(self.fwd_bck_axis):
                        expr_multiplier = 1
                    #blink * upDn motion gives final result of lid
                    drv.expression = 'var_blink*var*(%s)' %expr_multiplier

    def _setBlinkPropertiesDefaults(self):
        """add defaults for upDn position of up and lo lid at blink
        doesnt know how to set defaults for fwdBck motion
        assumes to use worldspace z for upDn axis
        """
        
        for up_bone, lo_bone in self.bones_up_dn_data.items():
            upbone = bpy.data.objects[self.armature_name].pose.bones[up_bone]
            lobone = bpy.data.objects[self.armature_name].pose.bones[lo_bone]
            
            #for getting distances lids travel for a blink
            up_close_dist = 0
            dn_close_dist = 0
            up_close_dist = abs( upbone.matrix.translation.z - lobone.matrix.translation.z )*(self.up_close_pct/100) #using worldspace z for upDn
            lo_close_dist = abs( upbone.matrix.translation.z - lobone.matrix.translation.z )*(1- self.up_close_pct/100)

            #set defaults on upDn motion properties
            upbone[self.up_dn_blink_prop] = up_close_dist
            lobone[self.up_dn_blink_prop] = lo_close_dist

            #fwdBck motion defaults to 0
            
    def setFwdBckPropertiesDefaults(self, val = 0.0):   
        """allow to set fwdBck motion default value for all bones at once to a given value
        """
        for up_bone, lo_bone in self.bones_up_dn_data.items():
            upbone = bpy.data.objects[self.armature_name].pose.bones[up_bone]
            lobone = bpy.data.objects[self.armature_name].pose.bones[lo_bone]
            upbone[self.fwd_bck_blink_prop] = val
            lobone[self.fwd_bck_blink_prop] = val
            

"""
import bpy
import sys
sys.path.append("/users/Nathaniel/Documents/src_blender/python/riggingTools/faceTools")
import naBlinkRigAddOn as mod
import imp
imp.reload(mod)

#usage for left side blink
bobj = mod.BlinkMaker(bones_up_dn_data = {'upLid.L':'lowLid.L'}, anim_bone= 'anim', anim_blink_prop = 'blink', armature_name = 'Armature')
bobj.run()
"""

"""using regular expression to find bones to use
#usage for left side blink
bones_up_dn_data = mod.get_bones_up_dn_data( up_search_regex_string = 'upLid_.+\.L', dn_search_string = 'up', dn_replace_string = 'low', armature_object_name = 'Armature')

#print(bones_up_dn_data)
bobj = mod.BlinkMaker(bones_up_dn_data = bones_up_dn_data, anim_bone= 'anim', anim_blink_prop = 'blink', armature_name = 'Armature')
bobj.run()
"""




"""
#creating a property on a pose bone
import bpy
from rna_prop_ui import rna_idprop_ui_prop_get

pb = bpy.data.objects['Armature'].pose.bones['Bone']
pb['blinkY'] = 0.0
prop = rna_idprop_ui_prop_get(pb,'blinkY',create = True)

prop['default']=0.0
prop['min']= -10.0
prop['max']= 10.0

"""

"""
#creating a scripted expression on a pose bone
#blinkY of bone moves y of a different bone
import bpy
drivenBone = bpy.data.objects['Armature'].pose.bones['Bone.001']
drv = drivenBone.driver_add('location',1).driver #this is where specify what channel gets driven
drv.type='SCRIPTED'
var = drv.variables.new()
var.name = 'varBlink'
var.targets[0].id = bpy.data.objects['Armature']
var.targets[0].data_path = 'pose.bones["Bone"]["blinkY"]'
drv.expression='varBlink'

"""

"""
#getting distance between two pose bones
#getting worldspace z distance
pointA = bpy.data.objects['Armature'].pose.bones['Bone'].matrix.translation.z
pointB = bpy.data.objects['Armature'].pose.bones['Bone.001'].matrix.translation.z
abs(pointA - pointB)
#2.0
"""