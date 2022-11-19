#tool to ease animation curve keys
#
#steps to install plugin
#1. save file to disk
#2. file > user preferences > addon >install addon from file > navigate to file
#3. click install addon > check the box next to addon to register it.
# if need to remove can expand clicking arrow and remove addon
#
#usage:
#select some keys in graph editor (assumes there are keys to left and right of selection)
#find ease panel at bottom of properties panel
#change slider (to change slider click drag a little and let go or type value.)
#
#modify and use at own risk

#062320 -- worked on speed of slider and keyframe tangent handles
#042719 -- initial release
 
bl_info = {
    "name":"ease_tool",
    "description":"tool to ease in ease out keyframes",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

import bpy

from bpy.props import(
    FloatProperty,
    PointerProperty
    )

from bpy.types import(
    Panel,
    PropertyGroup
    )

def onSliderChange(self,context):
    #this is called on slider change
    sliderV = context.scene.ease_prop.easeSlider
    #print( "Ease Value %s" %(sliderV) )
    #do the easing here
    naEaseMain(sliderV)
    
    return None
        
class EasePanel(Panel):
    bl_label = "Ease Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "Ease tool")
        #add slider to ui
        layout.prop(context.scene.ease_prop, "easeSlider", slider = True)
        
class EaseProperties(PropertyGroup):
    easeSlider = FloatProperty(default = 0.0, soft_min=-10.0, soft_max=10.0, min = -10.0, max = 10.0, update = onSliderChange )
    
def register():
    bpy.utils.register_class(EasePanel)
    bpy.utils.register_class(EaseProperties)
    bpy.types.Scene.ease_prop = PointerProperty( type = EaseProperties )
    
def unregister():
    bpy.utils.unregister_class(EasePanel)
    bpy.utils.unregister_class(EaseProperties)
    del bpy.types.Scene.ease_prop

if __name__ == "__main__":
    register()
    
    
##put ease code here

#modify use at your own risk

import bpy

def naEaseMain(sliderValue = None):
    """make the animation curve resemble an ease in or ease out pattern. it runs on selected keyframes. should support multiple curves.
    currently only works if there is at least one keyframe before and after selected keyframes
    @param sliderValue -10 to 10
    """

    def naEaseGetValue( curve = None, selectedKeyIndex=None, leftIndex=None, rightIndex=None, sliderValue=None ):
        """
        get new value for key
        @param curve , is the curve working on 
        @param sliderValue -10, 10 negative means favor left index
        """
        result = None
        sliderV = abs(sliderValue) + 1
        
        frameAllDistance = curve.keyframe_points[rightIndex].co[0] - curve.keyframe_points[leftIndex].co[0]
        frameDistance = curve.keyframe_points[selectedKeyIndex].co[0] - curve.keyframe_points[leftIndex].co[0]
        propFrameDistance = frameDistance/frameAllDistance
        lastValueMinusFirstValue = curve.keyframe_points[rightIndex].co[1] - curve.keyframe_points[leftIndex].co[1]
        firstValue = curve.keyframe_points[leftIndex].co[1]
        
        valuePosSlider = lastValueMinusFirstValue*( 1-(abs(propFrameDistance-1))**(sliderV) ) + firstValue
        valueNegSlider = lastValueMinusFirstValue*( (propFrameDistance)**(sliderV) ) + firstValue
        result = valuePosSlider
        if sliderValue < 0:
            result = valueNegSlider
        
        return result
        
    def naEaseSetValue( curve = None, selectedKeyIndex = None, value = None ):
        """change key in graph editor
        """
        curve.keyframe_points[selectedKeyIndex].co[1] = value
        #this bit changes tangent type of selected key
        curve.keyframe_points[selectedKeyIndex].interpolation='BEZIER'#'LINEAR'
        curve.keyframe_points[selectedKeyIndex].handle_left_type = 'AUTO_CLAMPED'#'VECTOR'
        curve.keyframe_points[selectedKeyIndex].handle_right_type = 'AUTO_CLAMPED'#'VECTOR'#AUTO 
        #take care of handle types
        curve.update()
        
        #need to update 3d view
        curFrame = bpy.context.scene.frame_current
        bpy.context.scene.frame_set(curFrame)
    
    #get selected curve
    curves = bpy.context.selected_objects[0].animation_data.action.fcurves #need to error check
    curveIndexes = []
    for i in range( len(curves) ):
        if curves[i].select:
            curveIndexes.append(i)
    
    for curveIndex in curveIndexes:
        #this loop is for all translate x,y,z etc channels that have a selected key
        #curveIndex = curveIndexes[0] #need to support all selected curves
        curve = curves[ curveIndex ]
        
        #get neighbor keys
        selectedKeyIndexes = []
        for i in range( len(curve.keyframe_points) ):
            if curve.keyframe_points[i].select_control_point:
                selectedKeyIndexes.append(i)
                
        #print('selected key indexes', selectedKeyIndexes)
        leftIndex = min(selectedKeyIndexes)-1
        rightIndex = max(selectedKeyIndexes)+1
        #assert left and right index exist
        if leftIndex < 0:
            print('cannot find a neighbor key to left of selected. skipping curve index %s' %curveIndex)
            continue
        if rightIndex > len(curve.keyframe_points):
            print('cannot find a neighbor key to right of selected. skipping curve index %s' %curveIndex)
            continue
        #print('left %s, right %s indexes' %(leftIndex,rightIndex) )
        for selectedKeyIndex in selectedKeyIndexes:
            #pass
            #this loop is for all selected keyframes for this curve
            
            #allow to use different sliderValues -10 to 10
            value = naEaseGetValue( curve = curve, selectedKeyIndex=selectedKeyIndex, leftIndex=leftIndex, rightIndex=rightIndex, sliderValue=sliderValue )
            #print("value>>",value)
            #set value in graph editor
            naEaseSetValue( curve = curve, selectedKeyIndex = selectedKeyIndex, value = value )
            
            
    
    #end for
        
#Inspired by:
#Alan Camilo's Atools alancamilo dot com
#Joan Marc Fuentes Iglesias
#https://blenderartists.org/t/change-fcurve-mode-via-python/530691
#https://blender.stackexchange.com/questions/115019/program-ui-slider
#https://blenderartists.org/t/how-to-adjust-min-max-values-of-a-custom-property/618238/2
#https://blenderartists.org/t/make-slider-for-multi-file-pie-menu-work/668412