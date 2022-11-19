
import bpy
from bpy.types import(
    Operator,
    Panel,
    )

from . import test

class ButtonOperator(Operator):
    bl_idname = "obj.button"
    bl_label = "Button Operator"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        scene = context.scene
        test.printObjects()
        test.printMessage()
        return {'FINISHED'}

class ButtonPanel(Panel):
    bl_label = "Button Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout
        layout.label(text="A Button")
        layout.operator("obj.button")
        
classes = (
    ButtonOperator,
    ButtonPanel
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)