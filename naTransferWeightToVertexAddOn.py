#naTransferWeightToVertexAddOn.py
#modify use at your own risk
bl_info = {
    "name":"weighting tools for facial rigging",
    "description":"tool to transfer vertex weight from one vertex to other vertices",
    "category": "Object",
    "author":"Nathaniel Anozie",
    "blender":(2,79,0)
}

import bpy
import bmesh #for getting last selected vertex

from bpy.types import(
    Operator,
    Panel
    )

class transferWeightToVertexOperator(Operator):
    """first select children vertices then last parent.transfers weight from parent to children.
    (doesn't support lasso select because it needs selection history)
    """
    bl_idname = "obj.transferweighttovertex" #needs to be all lowercase
    bl_label = "transferWeightToVertex"
    bl_options = {"REGISTER"}

    def execute(self, context):
        naTransferWeightToVertex(context)
        return {'FINISHED'}
        
class transferWeightToVertexPanel(Panel):
    bl_label = "transferWeightToVertex Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = "first select children then last parent")
        layout.operator( "obj.transferweighttovertex")

def register():
    bpy.utils.register_class(transferWeightToVertexOperator)
    bpy.utils.register_class(transferWeightToVertexPanel)
    
def unregister():
    bpy.utils.unregister_class(transferWeightToVertexOperator)
    bpy.utils.unregister_class(transferWeightToVertexPanel)
if __name__ == "__main__":
    register()
    
#actual procs going here
def naTransferWeightToVertex(context):
    """transfer weights to all selected from last selected.
    similar to how pick chid then parent when binding to armature, or parenting
    this supports single vertex group transfer.
    need to select vertices one at a time cant use lasso select.
    """
    currentMode = context.object.mode
    
    #need to be in edit mode
    bpy.ops.object.mode_set(mode="EDIT")
    obj = context.object
    
    #get selected vertex group
    selectedGrpIndex = obj.vertex_groups.active_index
    selectedGrp = obj.vertex_groups[selectedGrpIndex]
    print("selectedGrpIndex %s" %selectedGrpIndex)
    vtxGroup = (selectedGrp.name,selectedGrp.index)
    
    #get 2 selected vertices, child then active index
    #assuming you only selected vertices
    bm = bmesh.from_edit_mesh(obj.data)
    childVtxs=[]
    parentVtx = None #last thing selected
    
    #exit if select history is not 2 or more
    #might need to check selection history is vert type
    if not len(bm.select_history) >= 2:
        print("please select 2 or more verts >> children then last parent")
        return        
    for i in range(0,len(bm.select_history)-1):
        childVtxs.append(bm.select_history[i].index)
    parentVtx = bm.select_history[len(bm.select_history)-1].index
    
    #get weight from parent vtx
    bone = vtxGroup[0]
    boneIndex = vtxGroup[1]
    print('parent vtx %s bone index %s' %(parentVtx,boneIndex) )
    print('childVtxs')
    print(childVtxs)
    ##need to do this to find proper group to use for getting weight
    groupIndexToUse = None
    for j in range(0,len(obj.data.vertices[parentVtx].groups)):
        grp = obj.data.vertices[parentVtx].groups[j]
        if grp.group == boneIndex:
            groupIndexToUse = j
            break
    weight = obj.data.vertices[parentVtx].groups[groupIndexToUse].weight
    
    #assign weight to children vtxs
    #assuming assign weight on same vertex group as first selected
    
    print('weight %s , vert id %s' %(weight,childVtxs[0]))

    #need to be in object mode
    bpy.ops.object.mode_set(mode="OBJECT")
    for vtx in childVtxs:
        obj.vertex_groups[bone].add( [int(vtx)], float(weight) , 'REPLACE')    

    #flip to edit mode so we can see change
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.object.mode_set(mode="OBJECT")
    
    #restore mode
    bpy.ops.object.mode_set(mode=currentMode)

#inspired by:
#https://blender.stackexchange.com/questions/102562/can-someone-help-make-this-code-work-on-all-vertex-groups-instead-of-just-the-ac
#https://blender.stackexchange.com/questions/30582/get-active-vertex-through-python