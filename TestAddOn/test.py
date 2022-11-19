
import bpy

def printObjects():
    for obj in bpy.data.objects:
        print( obj.name )
        
def printMessage():
    print("Great happy day >>")
