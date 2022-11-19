
import bpy
import bmesh


def drawTextShape(textStr = '', position=(0.0,0.0,0.0) ):
    """draw text mesh left aligned at position. position is tuple xyz"""
    #need to be in object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.data.body = textStr
    obj.matrix_world.translation = position
    #convert it to mesh object
    bpy.ops.object.convert(target="MESH")
    
    return obj

def getVertsEdgesFromSelected():
    """help for from_pydata creation of widgets. returns tuple verts and edges of selected
    """
    obj = bpy.context.object
    
    verts = []
    edges = []
    
    for i in range(0,len(obj.data.vertices)):
        verts.append( tuple(bpy.context.object.data.vertices[i].co)  )
    for i in range(0,len(obj.data.edges)):
        edges.append( (bpy.context.object.data.edges[i].vertices[0],bpy.context.object.data.edges[i].vertices[1])  )
        
    return verts,edges
    
def getVertsEdgesFacesFromSelected(context):
    """help for from_pydata creation of meshes. returns tuple verts,edges,faces of selected
    """
    if not context.selected_objects:
        print("need to select mesh object in object mode with all transforms applied")
        return
        
    obj = context.selected_objects[0]
    
    verts = []
    edges = []
    faces = []
    
    for i in range(0,len(obj.data.vertices)):
        pos = context.object.data.vertices[i].co
        verts.append( tuple( (round(pos[0],4),round(pos[1],4),round(pos[2],4)) )  )
    for i in range(0,len(obj.data.edges)):
        edges.append( (context.object.data.edges[i].vertices[0],context.object.data.edges[i].vertices[1])  )
    for i in range(0,len(obj.data.polygons)):
        facei = []
        #to support various polygons not always four sided
        for v in range(0,len(context.object.data.polygons[i].vertices) ):
            facei.append( context.object.data.polygons[i].vertices[v] )
        faces.append(tuple(facei))
        
    return verts,edges,faces


def drawRectangleShape(name = None):
    """ draw square mesh no faces. if it exists does nothing"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = bpy.context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges = ([(-0.25, -1.0, 0.0), (0.25, -1.0, 0.0), (-0.25, 1.0, 0.0), (0.25, 1.0, 0.0)], [(2, 0), (0, 1), (1, 3), (3, 2)])
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    
    return obj
    

def drawCubeShape(name = None):
    """ draw cube mesh no faces. if it exists does nothing"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = bpy.context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges = ([(-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0)], [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1)])
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    return obj
    
def drawSquareShape(name = None):
    """ draw square mesh no faces. if it exists does nothing"""
    if not name:
        print("requires a name >> exiting")
        return
        
    scene = bpy.context.scene
    
    #if data object already created return the object 
    if name in bpy.data.objects:
        print("%s is already created doing nothing" %name)
        return bpy.data.objects[name]

    
    #create the object in data
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    scene.objects.link(obj)
    
    if obj is None:
        print("issue drawing shape")
        return None
        
    #use for from_pydata
    verts,edges = ([(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (-1.0, 1.0, 0.0), (1.0, 1.0, 0.0)], [(2, 0), (0, 1), (1, 3), (3, 2)])
    meshData = obj.data
    meshData.from_pydata(verts,edges,[])
    meshData.update()
    
    
    return obj


def drawCircleShape(name = None):
    
    scene = bpy.context.scene
    
    bpy.ops.object.mode_set(mode='OBJECT')
    #do nothing if shape already exists
    if name in bpy.data.objects.keys():
        return bpy.data.objects[name]
        

    meshObj = bpy.data.meshes.new("Mesh")
    boneShape = bpy.data.objects.new(name, meshObj)
    scene.objects.link(boneShape)
    
    #new bmesh
    bm = bmesh.new()
    #load in a mesh
    bm.from_mesh(meshObj)
    
    #create circle
    bmesh.ops.create_circle(bm,cap_ends=False,diameter=0.1,segments=8)
    
    #write back to mesh
    bm.to_mesh(meshObj)
    bm.free()
    
    #set active selection
    #scene.objects.active = boneShape
    #boneShape.select = True
    scene.update()
    
    #boneShape.layers = [False]*19+[True] #move to different layer
    
    return boneShape
    
def rotateShape(shapeObj,amount = 0.0, axis = 'x'):
    """
    rotate shape in axis. amount in radians
    """
    if axis == 'x':
        rotateAxis = (True,False,False)
    elif axis == 'y':
        rotateAxis = (False,True,False)
    elif axis == 'z':
        rotateAxis = (False,False,True)
        
    bpy.context.scene.objects.active = shapeObj
    bpy.ops.object.mode_set(mode='EDIT',toggle = False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.rotate(value = amount,axis = rotateAxis)
    bpy.ops.object.mode_set(mode='OBJECT',toggle=False)
    
    
    