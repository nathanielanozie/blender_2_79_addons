
#after running in script editor to run operator 'spacebar' and type the bl_label
bl_info = {
    "name": "Move Y",
    "category": "Object",
}

import bpy

class HelloWorldOp(bpy.types.Operator):
    bl_idname = "obj.move_y"
    bl_label = "HelloWorld Label"
    bl_options = {'REGISTER','UNDO'}
    
    def execute(self, context):
        scene = context.scene
        for obj in scene.objects:
            obj.location.y += 1.0
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(HelloWorldOp)
    
def unregister():
    bpy.utils.unregister_class(HelloWorldOp)


if __name__ == "__main__":
    register()
    
#https://docs.blender.org/api/blender_python_api_2_65_5/info_tutorial_addon.html