#naShapekeyUtilAddOn.py
#modify use at your own risk



#last modified
#112321 -- added mirror and copy sculpt to blendshape buttons
#111721 -- added create corrective button. working on create clean mesh button
#070321 -- found bug in mirror topology tool. bug was because mesh had no center line. 
#       -- the mirror topo seems to make all shapekeys in list symmetric. may want to give it a list of shapekeys to mirror. not sure the deleting half of mesh will mess up vertex order
#       -- not really sure the practical use of mirror topo
#050121 -- worked on initial release



import bpy
import os
import bmesh

####add on portion
bl_info = {
    "name":"shapkey editing tools",
    "description":"some tools to edit shapekeys",
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
    EnumProperty,
    PointerProperty
    )


class makeCorrectiveShapeKeyOperator(Operator):
    """create a corrective sculpt which can be added on
    """
    bl_idname = "obj.makecorrectiveshapekey" #needs to be all lowercase
    bl_label = "makeCorrectiveShapeKey"
    bl_options = {"REGISTER"}

    def execute(self, context):
        createCorrectiveSculpt( pose = context.scene.shapekeyutils_prop.poseMesh, sculpt = context.scene.shapekeyutils_prop.sculptMesh, shape_key_mesh = context.scene.shapekeyutils_prop.shapekeyMesh )
        return {'FINISHED'}


class mirrorShapeKeyOperator(Operator):
    """mirror shapekeys. it assumes blendshape mesh is selected. if no shapekeys provided it tries to mirror all shapes ending with .L
    """
    bl_idname = "obj.mirrorshapekey"
    bl_label = "mirrorShapeKey"
    bl_options = {"REGISTER"}

    def execute(self, context):
        mesh = context.selected_objects[0].name
        blendshapes = []
        blendshapes_arg = context.scene.shapekeyutils_prop.mirrorShapekey
        if blendshapes_arg:
            blendshapes = blendshapes_arg.split(' ')
        else:
            #use all left side blendshapes
            blendshapes = getAllLeftSideBlendshapes(mesh)
        print("blendshapes>>",blendshapes)
        use_topology = True if context.scene.shapekeyutils_prop.topoEnum == 'True' else False 
        mirrorBlendshape( mesh = mesh, blendshapes = blendshapes, use_topology = use_topology )
        return {'FINISHED'}
        

class makeCleanPoseOperator(Operator):
    """create a clean mesh (no shapekeys) at the given pose. requires selection of mesh object with shapekeys
    """
    bl_idname = "obj.makecleanpose" #needs to be all lowercase
    bl_label = "makeCleanPose"
    bl_options = {"REGISTER"}

    def execute(self, context):
        apply_types = ["ARMATURE"] if context.scene.shapekeyutils_prop.applyArmatureEnum == 'True' else [] 
        
        createCleanMesh(keepPose=True, apply_types = apply_types)
        return {'FINISHED'}

class copySculptToBlendshapeOperator(Operator):
    """copies a separate sculpt mesh to an existing blendshape. first select sculpt mesh, last mesh with blendshapes with a blendshape highlighted in dropdown
    """
    bl_idname = "obj.copysculpttoblendshape" #needs to be all lowercase
    bl_label = "copySculptToBlendshape"
    bl_options = {"REGISTER"}

    def execute(self, context):
        copySculptToBlendshape()
        return {'FINISHED'}

class splitSymmetricShapeKeyOperator(Operator):
    """split selected shapekey.  first select single mesh with shapekey in object mode and highlight shapekey wish to split.
    """
    bl_idname = "obj.splitsymmetricshapekey" #needs to be all lowercase
    bl_label = "splitSymmetricShapeKey"
    bl_options = {"REGISTER"}

    def execute(self, context):
        splitSymmetricShapeKey(obj=context.selected_objects[0],removeSourceShapeKey = False, context = context)
        return {'FINISHED'}


class mirrorShapekeyTopologyOperator(Operator):
    """first select single mesh with shapekey in object mode. requires mesh to have a center line, required for mirroring.
    """
    bl_idname = "obj.mirrorshapekeytopology"
    bl_label = "mirrorShapekeyTopology"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        mirrorShapekeyTopology(obj=context.selected_objects[0],context=context)
        return {'FINISHED'}

class mergeShapekeysOperator(Operator):
    """merge selected meshes shapekeys into one mesh. places all shapekeys on last selected mesh
    """
    bl_idname = "obj.mergeshapekeys"
    bl_label = "mergeShapekeys"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        mergeShapekeys(context=context)
        return {'FINISHED'}

class zeroKeyOnSelectedVerticesOperator(Operator):
    """set selected vertices to basis position
    """
    bl_idname = "obj.zerokeyonselectedvertices"
    bl_label = "zeroKeyOnSelectedVertices"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        zeroKeyOnSelectedVertices(context=context)
        return {'FINISHED'}

class putMeshesInRowOperator(Operator):
    """arrange selected meshes in row with a little gap
    """
    bl_idname = "obj.putmeshesinrow"
    bl_label = "putMeshesInRow"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        putMeshesInRow(context.selected_objects,gridWidth=1)
        return {'FINISHED'}

class importObjOperator(Operator):
    """import objs in a directory
    """
    bl_idname = "obj.importobj"
    bl_label = "importObj"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        path = context.scene.shapekeyutils_prop.importObjPath
        dirpath = bpy.path.abspath(path)
        print("importObjOperator dir path: %s" %(dirpath))
        importObj(dirpath)
        return {'FINISHED'}
        
class naShapekeyUtilPanel(Panel):
    bl_label = "naShapekeyUtil Panel"
    bl_space_type = "VIEW_3D" #needed for ops working properly
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "for corrective making")
        layout.prop( context.scene.shapekeyutils_prop, "poseMesh", text = "poseMesh" )
        layout.prop( context.scene.shapekeyutils_prop, "sculptMesh", text = "sculptMesh" )
        layout.prop( context.scene.shapekeyutils_prop, "shapekeyMesh", text = "shapekeyMesh" )
        layout.operator( "obj.makecorrectiveshapekey")
        layout.label(text = "-"*50)
        ##
        layout.label(text = "for mirroring")
        layout.prop( context.scene.shapekeyutils_prop, "mirrorShapekey", text = "mirrorShapekey" )
        layout.prop( context.scene.shapekeyutils_prop, "topoEnum", text = "useTopology" )
        layout.operator( "obj.mirrorshapekey")
        layout.label(text = "-"*50)
        ##
        layout.label(text = "for clean pose"+"-"*50)
        layout.operator( "obj.makecleanpose" )
        layout.prop( context.scene.shapekeyutils_prop, "applyArmatureEnum", text = "applyArmature" )
        layout.label(text = "-"*50)
        layout.operator( "obj.copysculpttoblendshape" )
        layout.operator( "obj.splitsymmetricshapekey")
        #layout.operator( "obj.mirrorshapekeytopology")
        layout.operator( "obj.mergeshapekeys")
        layout.operator( "obj.zerokeyonselectedvertices")
        layout.operator( "obj.putmeshesinrow")
        #for import obj
        layout.label(text = "import all obj in directory")
        layout.prop(context.scene.shapekeyutils_prop, "importObjPath")
        layout.operator( "obj.importobj")
        ##


class shapekeyUtilsProperties(PropertyGroup):
    importObjPath = StringProperty(
        name = "Browse Directory",
        description = "Pick directory with .obj files",
        maxlen = 200,
        subtype = 'FILE_PATH'
    )
    
    ##for corrective
    poseMesh = StringProperty(
        name = "poseMesh",
        description = "pose mesh. its the data object name for mesh that differs from default but is before sculpting"
        )    
    
    sculptMesh = StringProperty(
        name = "sculptMesh",
        description = "sculpt mesh. its the data object name for mesh that is a sculpt ontop of pose. it is how we want face to eventually look"
        )   
    
    shapekeyMesh = StringProperty(
        name = "shapekeyMesh",
        description = "shapekey mesh. its the data object name for mesh has all shapekeys. it will be used to get the default face"
        )
    ###
    
    ##for mirror
    mirrorShapekey = StringProperty(
        name = "mirrorShapekey",
        description = "shapekey names to mirror space separated. if non provided it tries to mirror all blendshapes ending with .L"
        )   
    topoEnum = EnumProperty(
        name = "useTopology",
        description = "whether or not to use Blenders use_topology",
        items = [   ('True',"True",""),
                    ('False',"False","")
                ],
        default = 'False'
        )
    ##
    
    #for clean pose
    applyArmatureEnum = EnumProperty(
        name = "applyArmature",
        description = "whether or not to apply armature to clean pose",
        items = [   ('True',"True",""),
                    ('False',"False","")
                ],
        default = 'False'
        )    

def register():
    bpy.utils.register_class(makeCorrectiveShapeKeyOperator)
    bpy.utils.register_class(mirrorShapeKeyOperator)
    bpy.utils.register_class(makeCleanPoseOperator)
    bpy.utils.register_class(copySculptToBlendshapeOperator)
    bpy.utils.register_class(splitSymmetricShapeKeyOperator)
    bpy.utils.register_class(mirrorShapekeyTopologyOperator)
    bpy.utils.register_class(mergeShapekeysOperator)
    bpy.utils.register_class(zeroKeyOnSelectedVerticesOperator)
    bpy.utils.register_class(putMeshesInRowOperator)
    bpy.utils.register_class(importObjOperator)
    bpy.utils.register_class(naShapekeyUtilPanel)
    
    bpy.utils.register_class(shapekeyUtilsProperties)
    bpy.types.Scene.shapekeyutils_prop = PointerProperty( type = shapekeyUtilsProperties )
    
def unregister():
    bpy.utils.unregister_class(makeCorrectiveShapeKeyOperator)
    bpy.utils.unregister_class(mirrorShapeKeyOperator)
    bpy.utils.unregister_class(makeCleanPoseOperator)
    bpy.utils.unregister_class(copySculptToBlendshapeOperator)
    bpy.utils.unregister_class(splitSymmetricShapeKeyOperator)
    bpy.utils.unregister_class(mirrorShapekeyTopologyOperator)
    bpy.utils.unregister_class(mergeShapekeysOperator)
    bpy.utils.unregister_class(zeroKeyOnSelectedVerticesOperator)
    bpy.utils.unregister_class(putMeshesInRowOperator)
    bpy.utils.unregister_class(importObjOperator)
    bpy.utils.unregister_class(naShapekeyUtilPanel)
    
    bpy.utils.unregister_class(shapekeyUtilsProperties)
    del bpy.types.Scene.shapekeyutils_prop
    
if __name__ == "__main__":
    register()
####



def splitSymmetricShapeKey(obj = None, removeSourceShapeKey = False, context = None):
    """going from symmetric shape key to a .L and .R shapekey
    works in xz plane only.
    duplicate shapekey twice > on one shape key set -x side to basis vert position, on other set +x side to basis vert position
    option to remove source shapekey after split
    """
    
    def duplicateShapeKeyAtIndex(obj = None, sourceIndex = None, context = None):
        #returns index of created shapekey
        result = None
        obj.active_shape_key_index = sourceIndex
        obj.show_only_shape_key = True
        bpy.ops.object.shape_key_add(from_mix=True)
        result = context.object.active_shape_key_index
        return result


    #duplicate shape key twice
    #then zero out appropriate side of meshes
    sourceIndex = obj.active_shape_key_index
    sourceName = obj.data.shape_keys.key_blocks[sourceIndex].name
    leftIndex = duplicateShapeKeyAtIndex(obj,sourceIndex,context)
    rightIndex = duplicateShapeKeyAtIndex(obj,sourceIndex,context)
    
    obj.data.shape_keys.key_blocks[leftIndex].name = sourceName+'.L'
    obj.data.shape_keys.key_blocks[rightIndex].name = sourceName+'.R'
    
    context.object.active_shape_key_index = leftIndex
    zeroSelectedKeyInX(sign="-",includeCenter = False, context=context) #to avoid double transformation of center vertices

    bpy.context.object.active_shape_key_index = rightIndex
    zeroSelectedKeyInX(sign="+",includeCenter = True, context=context)
    
    #optionally delete source shape key
    if removeSourceShapeKey:
        obj.active_shape_key_index = sourceIndex
        bpy.ops.object.shape_key_remove(all=False)
        
        

    
    
def mirrorShapekeyTopology(obj=None, context = None):
    """for getting all shapekeys have mirrored topology. requires basis default mesh to have a center line
    
    first copy out all shapekeys to a new mesh > each mesh no shapekeys > each mesh symmetric topology
    second, remove all shapekeys on mesh we wish to mirror > make its topology mirrored
    third, apply all created meshes as shapekeys on mesh
    
    note doesnt preserve drivers on shapkeys.
    """
    dupObjs = [] #list of tuples obj, shapekey name


    def getShapekeyName( geoName = None, dupObjsL = [] ):
        #dependent on data format tuples 
        for arg in dupObjsL:
            if arg[0].name == geoName:
                return arg[1]
        
    if not obj.data.shape_keys:
        return
           
    countShapeKeys = len(obj.data.shape_keys.key_blocks)
    for i in range(1,countShapeKeys):  
        #print('i:%s' %i)
        #print('obj name: %s' %(obj.name))
        dupObj = makeMeshUsingShapekeyIndex(obj,i,context)
        #make dupped object symmetric
        deleteHalfMesh(dupObj)
        makeMeshWhole(dupObj)
        dupObjs.append( (dupObj, obj.data.shape_keys.key_blocks[i].name) )
    
    #print('dupObjs')
    #print(dupObjs)
    
    #done duping all objects
    #remove all shapekeys from source object
    #make it mirrored
    #note not preserving drivers on shapekeys
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    context.scene.objects.active = obj
    bpy.ops.object.shape_key_remove(all=True)
    deleteHalfMesh(obj)
    makeMeshWhole(obj)    
    #
    #apply all of the duped objects as shapekeys
    bpy.ops.object.select_all(action='DESELECT')
    for dupTuple in dupObjs:
        dObj = dupTuple[0]
        dObj.select = True
    obj.select = True
    context.scene.objects.active = obj    
    bpy.ops.object.join_shapes()
    
    
    #fix names of shapekeys to match original
    #getting a bug here 070321
    for j in range(1,len(obj.data.shape_keys.key_blocks)):
        kblock = obj.data.shape_keys.key_blocks[j]
        n = getShapekeyName( kblock.name, dupObjs )
        kblock.name = n
        
    #cleanup
    bpy.ops.object.select_all(action='DESELECT')    
    for dupTuple in dupObjs:
        dObj = dupTuple[0]
        dObj.select = True
    context.scene.objects.active = dupObjs[0][0]
    bpy.ops.object.delete()
    
    #restore selection
    obj.select = True
    context.scene.objects.active = obj


def makeMeshUsingShapekeyIndex( obj=None, index = 1,context=None ):
    """not sure what this does
    """
    #result mesh no shapekeys. its shape would have matched shapekey at index
    dupMeshObj = None
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    context.scene.objects.active = obj
    
    bpy.ops.object.duplicate()
    dupMeshObj = context.selected_objects[-1]
    
    #first remove all shape keys on dupped object
    #then transfer just the given index onto dupped object
    #finally remove the basis shape and then last the only shapekey to get duped object at pose of index
    
    bpy.ops.object.shape_key_remove(all=True)
    obj.active_shape_key_index = index
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    dupMeshObj.select = True
    context.scene.objects.active = dupMeshObj
    bpy.ops.object.shape_key_transfer()

    bpy.ops.object.select_all(action='DESELECT')
    dupMeshObj.select = True
    context.scene.objects.active = dupMeshObj
    dupMeshObj.active_shape_key_index = 0
    bpy.ops.object.shape_key_remove(all=False)
    bpy.ops.object.shape_key_remove(all=True)
    
    return dupMeshObj
        
        
def importObj(shapeDir = ''):
    """import all .obj in shapeDir, use obj names for blender geo names
    """
    
    if not os.path.exists(shapeDir):
        return
    
    #find all objs in folder
    objFileNames = []
    toNames = [] #names to use for meshes in blender
    
    #if its a folder get all objs in it
    if os.path.isdir(shapeDir):
        for fpath in os.listdir(shapeDir):
            ff,fext = os.path.splitext(fpath)
            if fext.lower() == ".obj":
                objFileNames.append(fpath)
                toNames.append(ff)
    else:
        #import just the single obj path
        fpath = shapeDir
        fffull,fext = os.path.splitext(fpath)
        if fext.lower() == ".obj":
            fpathshort = os.path.split(fffull)[-1]
            objFileNames.append(fpath)
            toNames.append(fpathshort)
                
    #import objs into blender
    for f,toName in zip(objFileNames,toNames):
        fileName = os.path.join(shapeDir,f)
        importedObj = bpy.ops.import_scene.obj(filepath = fileName,
                                                use_split_objects = False,
                                                use_split_groups = False)
        obj = bpy.context.selected_objects[0]
        obj.name = toName
        obj.data.name = toName


def putMeshesInRow(meshObjs = [], gridWidth = 1):
    """
    #position given mesh objects in grid > nice to use bounding box
    #input how far apart want mesh
    """
    meshes = [m for m in meshObjs if m.type == 'MESH']
    
    xpos = 0
    for mesh in meshes:
        mesh.location = (xpos,0,0)
        xdim = mesh.dimensions[0]
        xpos += xdim+gridWidth #move a whole width of object plus given x offset
        
        
    
def mergeShapekeys(context = None):
    """
    1.given bunch of meshes with shape keys put all those shape keys on last selected object.
    last selection is target mesh
    """
    targetMesh = context.active_object
    sourceMeshes = [msh for msh in context.selected_objects if msh.name != targetMesh.name] 
    
    if len(sourceMeshes) == 0:
        print("please select 1 or more source meshes then last target mesh")
        return

    for sourceMesh in sourceMeshes:
        #selection
        bpy.ops.object.select_all(action='DESELECT')
        sourceMesh.select = True
        targetMesh.select = True
        context.scene.objects.active = targetMesh
        
        #changing active shapekey index to transfer shapes
        shapeKey = sourceMesh.data.shape_keys
        #if no shape key on source mesh skip it
        if not shapeKey:
            continue
        maxShapeKeyIndex = len(shapeKey.key_blocks) 
        for i in range(1,maxShapeKeyIndex):
            sourceMesh.active_shape_key_index = i
            bpy.ops.object.shape_key_transfer()
            targetMesh.show_only_shape_key = False
    
    #cleanup selection
    bpy.ops.object.select_all(action='DESELECT')
    targetMesh.select = True
    context.scene.objects.active = targetMesh
    
def zeroKeyOnSelectedVertices(context = None):
    """
    this zero out all selected vertices of shape key.
    """

    obj = context.active_object
    
    curMode = None
    if context.object:
        curMode = context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT') #if something is selected go to object mode
    
    #assumes basis shape at index 0
    vertIndex = [v.index for v in obj.data.vertices if v.select]
    for i in vertIndex:
        basisx = obj.data.shape_keys.key_blocks[0].data[i].co.x
        basisy = obj.data.shape_keys.key_blocks[0].data[i].co.y
        basisz = obj.data.shape_keys.key_blocks[0].data[i].co.z
        #modify selected shape key
        activeIndex = obj.active_shape_key_index
        if activeIndex > 0:
            #zero out shape
            obj.data.shape_keys.key_blocks[activeIndex].data[i].co.x = basisx
            obj.data.shape_keys.key_blocks[activeIndex].data[i].co.y = basisy
            obj.data.shape_keys.key_blocks[activeIndex].data[i].co.z = basisz

    #restore mode
    if curMode:
        bpy.ops.object.mode_set(mode=curMode)





def zeroSelectedKeyInX(sign="+", includeCenter = False, context = None):
    """
    this zero out all vertices of shape key that are in direction of x axis.
    supports positive or negative x axis
    optionally zero out center vertices
    """
    def zeroShape(obj=None,vid=None):
        #zero shape on given vertex id
        basisx = obj.data.shape_keys.key_blocks[0].data[vid].co.x
        basisy = obj.data.shape_keys.key_blocks[0].data[vid].co.y
        basisz = obj.data.shape_keys.key_blocks[0].data[vid].co.z        
        activeIndex = obj.active_shape_key_index
        if activeIndex > 0:
            #zero out shape
            obj.data.shape_keys.key_blocks[activeIndex].data[vid].co.x = basisx
            obj.data.shape_keys.key_blocks[activeIndex].data[vid].co.y = basisy
            obj.data.shape_keys.key_blocks[activeIndex].data[vid].co.z = basisz


    obj = context.active_object
    
    #assumes basis shape at index 0
    verts = obj.data.vertices

    if sign == "+":
        for i in range(len(verts)):
            basisx = obj.data.shape_keys.key_blocks[0].data[i].co.x
            if includeCenter:
                if basisx >= 0:
                    zeroShape(obj,i)
            else:
                if basisx > 0:
                    zeroShape(obj,i)            
    else:
        for i in range(len(verts)):
            basisx = obj.data.shape_keys.key_blocks[0].data[i].co.x
            if includeCenter:
                if basisx <= 0:
                    zeroShape(obj,i)
            else:
                if basisx < 0:
                    zeroShape(obj,i)


def zeroAllKeys():
    """
    when first testing shapekeys. this zeros them all out again
    """
    obj = bpy.context.active_object
    allKeys = obj.data.shape_keys.key_blocks.keys()
    for key in allKeys:
        obj.data.shape_keys.key_blocks[key].value = 0



def removeDigitShapeKeys():
    """noticed in fbx import from zbrush extra shape keys with digits at end
    this removes those shape keys
    """
    obj = bpy.context.active_object
    
    allKeys = obj.data.shape_keys.key_blocks.keys()
    keysEndDigit = [x for x in allKeys if x[-1].isdigit()]
    #print(keysEndDigit)
    
    for shape in keysEndDigit:
        index = obj.data.shape_keys.key_blocks.keys().index(shape)
        obj.active_shape_key_index = index
        bpy.ops.object.shape_key_remove()


def makeMeshWhole(obj):
    """default mirror from +x to -x of selected mesh, assumes no mirror modifiers on mesh to start
    """
    bpy.ops.object.modifier_add(type='MIRROR')
    bpy.ops.object.modifier_apply(modifier='Mirror') 
    
    
def deleteHalfMesh(obj):
    """
    default deletes -x side of selected mesh. standalone need give it bpy.context.object for selected object.
    doesnt work if no center line for mesh
    """
    #get current position
    curpos = ()
    curpos = (obj.location.x,obj.location.y,obj.location.z)
    
    #put obj at origin
    setLocation(obj,(0,0,0))
    
    selectedObj = obj #bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all( action='DESELECT')
    bpy.ops.mesh.select_mode(type='FACE')
    
    
    bm = bmesh.from_edit_mesh(selectedObj.data)
    for face in bm.faces:
        faceWorldPos = selectedObj.matrix_world*face.calc_center_median() #calc_center_median same as face.center using obj.data.polygons
        #[0] > 0.0 would be delete right half of mesh
        #[1] < 0.0 would be delete in y direction
        if faceWorldPos[0] < 0.0:
            face.select = True
            
    bm.select_flush(True)
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
            
    #restore location
    setLocation(obj,curpos)
    
def setLocation(obj,pos):
    """ does location only. pos tuple (2.3,0,0) """
    obj.location.x = pos[0]
    obj.location.y = pos[1]
    obj.location.z = pos[2]






def createCorrectiveSculpt( pose = None, sculpt = None, shape_key_mesh = None ):
    """
    1. given a pose mesh name, a sculpt mesh name, and the mesh that has all shape keys (object names)
    2. create a default mesh from the mesh with all shape keys
    3. add pose and sculpt as shapkeys to temp default mesh
    4. set pose -1 value and sculpt to 1
    5. duplicate tmp default mesh keeping the corrective but clean
    6. delete tmp default mesh
    """
    #assumes all inputs provided and exist and in object mode
    
    #create temporary default mesh
    default_mesh = createCleanMesh(mesh = shape_key_mesh, keepPose=False)
    default_mesh_obj = bpy.data.objects[default_mesh]
    
    #add pose and sculpt as shapkeys to temp default mesh
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[pose].select = True
    bpy.data.objects[sculpt].select = True
    bpy.context.scene.objects.active = default_mesh_obj
    bpy.ops.object.join_shapes()
    
    #set pose -1 value and sculpt to 1 > so when we eventually use the corrective can add it ontop of pose
    default_mesh_obj.data.shape_keys.key_blocks[pose].slider_min = -1.0 #needed before can change shapekey value to negative
    default_mesh_obj.data.shape_keys.key_blocks[pose].value = -1.0
    default_mesh_obj.data.shape_keys.key_blocks[sculpt].value = 1.0
    
    #duplicate tmp default mesh keeping the corrective but clean
    corrective_mesh = createCleanMesh(mesh = default_mesh_obj.name, keepPose=True)
    
    #delete tmp default mesh
    tmp_dat = default_mesh_obj.data
    bpy.data.objects.remove(default_mesh_obj)
    bpy.data.meshes.remove(tmp_dat)
    
    #maybe later position corrective mesh, and or give it a name


def createCleanMesh(mesh = None, keepPose=False, apply_types=[]):
    """
    mesh - mesh with shape keys object name > if its not provided it uses current selection
    keepPose - whehter or not to keep the current pose for clean mesh
    apply_types - list of modifier type that should be applied. ex: ["ARMATURE"] if empty it just deletes all modifiers
    
    1. given selected mesh with shape keys
    2. duplicate mesh
    3. create shape from mix (if keepPose)
    4. delete all shape keys except for mix > then delete mix shapekey
    (later add support to delete any modifiers)
    5. position clean mesh next to original
    
    returns the create clean mesh object name
    """
    
    """
    if mesh:
        mesh_obj = bpy.data.objects[mesh]
        #make it only selection
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select = True
        bpy.context.scene.objects.active = mesh_obj
    """
    _selectOnlyMesh(mesh)
    
    #assume have a selected mesh that has shapekeys in object mode
    orig_mesh = bpy.context.object
    
    #duplicate mesh
    bpy.ops.object.duplicate()
    pose_mesh = bpy.context.object
    
    #create shape from mix so we keep the current pose
    if keepPose:
        bpy.ops.object.shape_key_add(from_mix = True)
    
    #delete all shapekeys on mesh > remove all other shapes before last the active shape
    active_index = 0 #the basis by default
    if keepPose:
        active_index = pose_mesh.active_shape_key_index
    active_shapekey_name = pose_mesh.data.shape_keys.key_blocks[active_index].name
    
    non_active_shps = [shp for shp in pose_mesh.data.shape_keys.key_blocks if shp.name != active_shapekey_name]
    for shp in non_active_shps:
        pose_mesh.shape_key_remove(shp)
    mix_shp = pose_mesh.data.shape_keys.key_blocks[0]
    pose_mesh.shape_key_remove(mix_shp)
    
    
    #delete any modifiers
    _cleanModifiers(mesh = pose_mesh.name, apply_types = apply_types )
    #delete any vertex groups
    _cleanVertexGroups(mesh = pose_mesh.name)
    
    #position clean mesh
    width = orig_mesh.dimensions.x 
    pose_mesh.location.x = width+width/3.0
    
    return pose_mesh.name

def _selectOnlyMesh(mesh = None):
    #might need to be in object mode
    if mesh:
        mesh_obj = bpy.data.objects[mesh]
        #make it only selection
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select = True
        bpy.context.scene.objects.active = mesh_obj    
    

def _cleanModifiers(mesh = None, apply_types = [] ):
    """
    mesh - data object name for mesh to edit
    apply_types - list of modifier type that should be applied. ex: ["ARMATURE"] if empty it just deletes all modifiers
    """
    if not mesh:
        return
    
    _selectOnlyMesh(mesh)
    
    modifier_names = [ mod.name for mod in bpy.data.objects[mesh].modifiers ] 
    
    for mod_name in modifier_names:
        if bpy.data.objects[mesh].modifiers[mod_name].type in apply_types:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier = mod_name)
            continue
            
        bpy.ops.object.modifier_remove(modifier = mod_name)
        
    #make sure mesh not parented to anything example armature
    if bpy.data.objects[mesh].parent:
        bpy.data.objects[mesh].parent = None    
    

def _cleanVertexGroups(mesh = None):
    """remove any vertex groups on given mesh
    mesh - data object name for mesh to edit
    """
    if not mesh:
        return
    
    _selectOnlyMesh(mesh)
    
    #ops errors out if no vertex group exists
    if len(bpy.data.objects[mesh].vertex_groups) > 0:
        bpy.ops.object.vertex_group_remove(all=True)

def copySculptToBlendshape():
    """copies a separate sculpt mesh to an existing blendshape
    1. given two things selected: first sculpt mesh, last mesh with blendshapes and a blendshape selected
    2. loop all verts in blendshape and set its local position to the sculpt meshes local position
    """
    sculpt_mesh = None
    mesh = None
    
    #assumes proper selections made
    selection = [obj.name for obj in bpy.context.selected_objects]
    if len(selection) != 2:
        print("please select two meshes first sculpt mesh, last mesh with blendshapes")
        return
    mesh = bpy.context.active_object.name
    #print("selection>>>",selection)
    sculpt_mesh = list( set(selection) - set([mesh]) )[0] #to get first selected remove active selection from selection
    #print("mesh, sculpt_mesh>>>",mesh,sculpt_mesh)

    sculpt_vert_count = len(bpy.data.objects[sculpt_mesh].data.vertices)
    mesh_vert_count = len(bpy.data.objects[mesh].data.vertices)
    if  sculpt_vert_count != mesh_vert_count:
        print("requires same topology sculpt: %s mesh: %s" %(sculpt_vert_count,mesh_vert_count) )
        return

    #2. loop all verts in blendshape and set its local position to the sculpt meshes local position
    active_index = bpy.data.objects[mesh].active_shape_key_index
    for v, key_point in enumerate(bpy.data.objects[mesh].data.shape_keys.key_blocks[active_index].data):
        #might want to later verify sculpt has same topology vertex count as shapekey
        sculpt_pos = bpy.data.objects[sculpt_mesh].data.vertices[v].co
        bpy.data.objects[mesh].data.shape_keys.key_blocks[active_index].data[v].co = sculpt_pos
        
        

def mirrorBlendshape( mesh = None, blendshapes = [], use_topology = False ):
    """
    mesh - name of mesh with blendshapes. the data object name
    blendshapes - list of blendshapes we want to mirror
    use_topology - the bpy.ops shape_key_mirror topology option. i think sometimes might need to have this True
    
    1. given list of shapes
    2. select a shape and isolate it on
    3. make new shape from mix
    4. mirror new shape using argument usetopo
    5. rename new shape (if original shape ends with .L substitute L with R)
    6. repeat for all shapes
    
    for mirror shape when right side already exists:
    1. 1.
    2. 2.
    3. 3.
    4. 4.
    5. get index of temp mirrored shape
    6. get index of existing old mirrored shape
    7. set the old mirrored shape to be same as temp mirrored shape
    8. delete temp mirrored shape
    """
    for blendshape in blendshapes:
        
        exists_rhs = False
        #if right side already exists we need to do some additional steps
        mirrored_blendshape_new_name = blendshape.split('.')[0]+'.R'
        if mirrored_blendshape_new_name in [shp.name for shp in bpy.data.objects[mesh].data.shape_keys.key_blocks]:
            exists_rhs = True
            
        bs_index = getBlendshapeIndexFromName( mesh, blendshape ) #assumes it exists
        if bs_index is None:
            print("skipping %s >> could not find it in blendshapes drop down" %blendshape)
            continue
        #2. select a shape and isolate it on
        bpy.data.objects[mesh].active_shape_key_index = bs_index
        bpy.data.objects[mesh].show_only_shape_key = True

        #3. make new shape from mix
        bpy.ops.object.shape_key_add(from_mix = True)
        active_index = bpy.data.objects[mesh].active_shape_key_index
        
        #4. mirror new shape using argument usetopo
        bpy.ops.object.shape_key_mirror(use_topology = use_topology)
        
        ###additional steps if right side exists
        if exists_rhs:
            #shape key index of already existing right side
            rhs_index = getBlendshapeIndexFromName( mesh, mirrored_blendshape_new_name )
            
            #set the old mirrored shape to be same as temp mirrored shape
            for v, key_point in enumerate(bpy.data.objects[mesh].data.shape_keys.key_blocks[rhs_index].data):
                #print("updating rhs vertex %s" %v)
                mirror_pos = bpy.data.objects[mesh].data.shape_keys.key_blocks[active_index].data[v].co
                bpy.data.objects[mesh].data.shape_keys.key_blocks[rhs_index].data[v].co = mirror_pos
                
            #delete temp mirrored shape
            print("need to delete temp mirrored shape")
            bpy.ops.object.shape_key_remove(all=False)
        ###
        
        
        #5. rename new shape (if original shape ends with .L substitute L with R)
        if blendshape.endswith('.L') and not exists_rhs:
            print(">>>mirroring name")
            bpy.data.objects[mesh].data.shape_keys.key_blocks[active_index].name = mirrored_blendshape_new_name

        #restore might want to be more specific here
        bpy.data.objects[mesh].show_only_shape_key = False
        
def getBlendshapeIndexFromName( mesh = None, blendshape = None):
    result = None
    
    for i in range( 0,len(bpy.data.objects[mesh].data.shape_keys.key_blocks) ):
        if bpy.data.objects[mesh].data.shape_keys.key_blocks[i].name == blendshape:
            result = i
            return result
            
    return result
    
def getAllLeftSideBlendshapes(mesh = None):
    """returns all left side blendshape names
    """
    result = []
    
    for i in range( 0,len(bpy.data.objects[mesh].data.shape_keys.key_blocks) ):
        bs_name = bpy.data.objects[mesh].data.shape_keys.key_blocks[i].name
        if bs_name.endswith(".L"):
            result.append(bs_name)
            
    return result







"""
import bpy
import sys
sys.path.append("/users/Nathaniel/Documents/src_blender/python/naBlendShape")
import naShapekeyUtilAddOn as mod
import imp
imp.reload(mod)

#mod.importObj('/Users/Nathaniel/Documents/src_blender/python/snippets/pipeTools')
#mod.mirrorShapekeyTopology(obj=bpy.context.selected_objects[0],context=bpy.context)

"""

#inspired by
#https://blender.stackexchange.com/questions/1412/efficient-way-to-get-selected-vertices-via-python-without-iterating-over-the-en
#https://blender.stackexchange.com/questions/111661/creating-shape-keys-using-python
#https://blenderartists.org/t/delete-shape-key-by-name-via-python/521762/3
#https://stackoverflow.com/questions/14471177/python-check-if-the-last-characters-in-a-string-are-numbers
#https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
#https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
#https://stackoverflow.com/questions/8933237/how-to-find-if-directory-exists-in-python
#https://blender.stackexchange.com/questions/18035/code-inside-function-not-working-as-it-should
#https://blender.stackexchange.com/questions/43820/how-to-use-the-file-browsers-with-importhelper-execute-function
#https://blender.stackexchange.com/questions/42654/ui-how-to-add-a-file-browser-to-a-panel
#https://blender.stackexchange.com/questions/23258/trouble-file-stringproperty-subtype-file-path
#https://stackoverflow.com/questions/3391076/repeat-string-to-certain-length
