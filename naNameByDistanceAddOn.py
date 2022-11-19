#tool to help with naming bones
#
#modify use at your own risk


#last modified
#1023 -- working on addon ui
#102021,1021 -- working on blocking


bl_info = {
    "name":"tool to help with naming bones",
    "description":"name selected bones by distance using active bone name",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

import bpy
import re

from bpy.props import(
    EnumProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )


class NameMakerOperator(Operator):
    """name selected bones by distance using active bone name
    naming supported '*_letter.*' or '*_number.*'
    """
    bl_idname = "obj.do_namemaker"
    bl_label = "Name Bones by Distance"
    bl_options = {"REGISTER"}

    def execute(self, context):
        self.report({'INFO'}, "Naming Bones ...")
        
        #get axis
        axis = context.scene.name_maker_prop.axisEnum
        
        #might need to pass context
        obj = NameMaker( axis = axis )
        obj.run()
        return {'FINISHED'} 
        

class NameMakerPanel(Panel):
    bl_label = "NameMaker Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "Name Bone tool")
        
        #enum option for axis
        layout.prop(context.scene.name_maker_prop, "axisEnum" )

        #button
        layout.operator("obj.do_namemaker")
        
class NameMakerProperties(PropertyGroup):
    axisEnum = EnumProperty(
        name = "axis",
        description = "options for world axis to use in calculating bone naming order by distance ",
        items = [   ('x',"X",""),
                    ('y',"Y",""),
                    ('z',"Z","")
                ],
        default = 'x'
        )    

def register():
    bpy.utils.register_class(NameMakerOperator)
    bpy.utils.register_class(NameMakerPanel)
    bpy.utils.register_class(NameMakerProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.name_maker_prop = PointerProperty(
        type = NameMakerProperties
        )
    
def unregister():
    bpy.utils.unregister_class(NameMakerOperator)
    bpy.utils.unregister_class(NameMakerPanel)
    bpy.utils.unregister_class(NameMakerProperties)
    del bpy.types.Scene.name_maker_prop
    
if __name__ == "__main__":
    register()
    
####






class NameMaker(object):
    """
    """
    def __init__(self, axis = 'x'):
        """
        axis -- world axis to be used to figure out bone order from distance to active bone. ex: 'x'
        """
        self.axis = axis.lower()
        self.armature_object_name = '' #object name of armature with the bones to name
        self.active_bone = '' #active bone name
        self.bones = [] #all non active bones
        
    def run(self):
        """main method to be called by user
        """
        #do nothing if not in pose mode
        if bpy.context.mode != 'POSE':
            print("requires to be in pose mode")
            return
        
        
        self.armature_object_name = self._getActiveArmature()
        
        #figure out active bone for reference
        self.active_bone = self._getActiveBone()
        
        #do nothing if active bone name doesnt meet example naming supported
        if not self._isNameSupported():
            print("only supports naming of form: ex: lid_up_a.L or lid_up_1.L or lid_up_0001.L")
            return
        
        #figure out all other bones selected
        self.bones = self._getNonActiveBones()
        #print("self.bones",self.bones)
        #do nothing if nothing is selected 
        if not self.bones:
            print("please make sure to select two or more bones to do naming")
            return
        
        
        
        ordered_bones = self._orderBonesByDistance()
        #print('ordered bones', ordered_bones)
        
        ordered_bones_names = self._computeNames()
        print('ordered bone names', ordered_bones_names)
        
        if len(ordered_bones) != len(ordered_bones_names):
            print("could not rename bones lengths of computed names not matching")
            return
            
        #do the actual naming of bones
        for bone, bone_name in zip(ordered_bones, ordered_bones_names):
            bpy.data.objects[self.armature_object_name].pose.bones[bone].name = bone_name
            

    def _computeNames(self):
        """returns a list of names for bone based on active bone name.
        assumes active bone name is supported
        """
        def _incrementName(mode = 'single letter'):
            #returns list of names for non active bones after incrementing by given mode
            result = []
            regex_grp = None
            if mode == 'single letter':
                regex_grp = self._getLetterRegEx()
            else:
                regex_grp = self._getNumberRegEx()
            active_name = self.active_bone
            active_symbol = regex_grp.group(1)
            
            for i in range(0,len(self.bones)):
                bone_symbol = ''
                if mode == 'single letter':
                    #increment a single letter
                    bone_symbol = chr( ord(active_symbol)+(i+1) )
                else:
                    #increment possibly padded number
                    bone_symbol = str(int(active_symbol) +(i+1) ).zfill(len(active_symbol))
                #print("bone_symbol>>",bone_symbol)
                #dependency on _symbol. type of active_bone naming
                bone_name = active_name.replace('_%s.' %active_symbol, '_%s.' %bone_symbol )
                result.append(bone_name)
            return result    
            
        result = []
        
        mode = 'single letter'
        #figure out whether to return letter incremented or number incremented names
        regex_letter_grp = self._getLetterRegEx()
        regex_number_grp = self._getNumberRegEx()
        
        if not regex_letter_grp:
            mode = 'number'
        
        print("mode>>",mode)
        #get computed names for non active bones
        result = _incrementName(mode)

        return result

    def _orderBonesByDistance(self):
        """returns bone names ordered according to world distance to active_bone
        """
        result = []
            
        #get distances to active_bone in direction axis
        axis_index = self._getIndexAxis()
        active_bone_head = bpy.data.objects[self.armature_object_name].pose.bones[self.active_bone].head
        bone_tuple_list = []
        for bone in self.bones:
            print(">>",bone)
            bone_head = bpy.data.objects[self.armature_object_name].pose.bones[bone].head
            dist_to_bone = bone_head - active_bone_head
            abs_dist = abs( dist_to_bone[axis_index] )
            bone_tuple_list.append( (abs_dist, bone) ) 
        
        #sort list by tuples first key which should be distance
        bone_tuple_list.sort(key = lambda tup: tup[0] )
        result = [ i[1] for i in bone_tuple_list ] #second element is the bone name
        return result
        
    def _isNameSupported(self):
        """returns true if active bone name is supported for naming others
        """
        result = False
        
        #does it look like ex: lid_up_a.L or lid_up_1.L or lid_up_0001.L
        regex_letter_grp = self._getLetterRegEx()
        regex_number_grp = self._getNumberRegEx()
        
        if regex_letter_grp or regex_number_grp:
            result = True
            
        return result  
    def _getLetterRegEx(self):
        return re.search('._([a-zA-z]{1})\..', self.active_bone)
    def _getNumberRegEx(self):
        return re.search('._(\d+)\..', self.active_bone)
        
    def _getActiveBone(self):
        result = ''
        result = bpy.data.objects[self.armature_object_name].data.bones.active.name
        return result
    def _getNonActiveBones(self):
        result = []
        active_bone = self._getActiveBone()
        selected_bones = [bone.name for bone in bpy.data.objects[self.armature_object_name].data.bones if bone.select ]
        result = list( set(selected_bones) - set([active_bone]) )
        return result
    def _getActiveArmature(self):
        #return armature object name selected
        result = ''
        result = bpy.context.object.name
        return result
    def _getIndexAxis(self):
        """returns index of head position to use for computing distance
        """
        result = 0
        if self.axis == 'x':
            result = 0
        elif self.axis == 'y':
            result = 1
        elif self.axis == 'z':
            result = 2
        return result
        
"""
import bpy
import sys
sys.path.append("/Users/Nathaniel/Documents/src_blender/python/riggingTools")
import naNameByDistanceAddOn as mod
import imp
imp.reload(mod)

obj = mod.NameMaker()
obj.run()
"""

#inspired by
#https://blender.stackexchange.com/questions/134250/set-active-bone-in-pose-mode-from-python-script
#https://stackoverflow.com/questions/587647/how-to-increment-a-value-with-leading-zeroes
#https://stackoverflow.com/questions/2156892/how-can-i-increment-a-char
#https://stackoverflow.com/questions/3121979/how-to-sort-a-list-tuple-of-lists-tuples-by-the-element-at-a-given-index
