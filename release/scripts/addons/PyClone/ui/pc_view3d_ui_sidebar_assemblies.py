import bpy
from ..pc_lib import pc_types, pc_utils
from .. import pyclone_utils


def draw_assembly_properties(context, layout, assembly):
    scene_props = pyclone_utils.get_scene_props(context.scene)

    col = layout.column(align=True)
    box = col.box()
    row = box.row()
    row.label(text="Assembly Name: " + assembly.obj_bp.name)
    row.operator('pc_assembly.select_parent',text="",icon='SORT_DESC')

    row = box.row(align=True)
    row.prop(scene_props,'assembly_tabs',expand=True)
    box = col.box()
    if scene_props.assembly_tabs == 'MAIN':
        box.prop(assembly.obj_bp,'name')

        col = box.column(align=True)
        col.label(text="Dimensions:")
        col.prop(assembly.obj_x,'location',index=0,text="X")
        col.prop(assembly.obj_y,'location',index=1,text="Y")
        col.prop(assembly.obj_z,'location',index=2,text="Z")

        col = box.column()
        s_col = col.split()
        s_col.prop(assembly.obj_bp,'location')
        s_col.prop(assembly.obj_bp,'rotation_euler',text="Rotation")

    if scene_props.assembly_tabs == 'PROMPTS':
        assembly.obj_prompts.pyclone.draw_prompts(box)

    if scene_props.assembly_tabs == 'OBJECTS':

        skip_names = {assembly.obj_bp.name,assembly.obj_x.name,assembly.obj_y.name,assembly.obj_z.name,assembly.obj_prompts.name}

        row = box.row()
        row.label(text="Objects",icon='OUTLINER_OB_MESH')
        row.operator('pc_assembly.add_object',text="Add Object",icon='ADD')

        mesh_col = box.column(align=True)

        for child in assembly.obj_bp.children:
            if child.name not in skip_names:
                row = mesh_col.row(align=True)
                if child == context.object:
                    row.label(text="",icon='RADIOBUT_ON')
                elif child in context.selected_objects:
                    row.label(text="",icon='DECORATE')
                else:
                    row.label(text="",icon='RADIOBUT_OFF')
                row.operator('pc_object.select_object',text=child.name,icon=pc_utils.get_object_icon(child)).obj_name = child.name

    if scene_props.assembly_tabs == 'LOGIC':
        pass#TODO: IMPLEMENT DRIVER INTERFACE

class VIEW3D_PT_pc_assembly_properties(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Assembly"
    bl_category = "Assembly"    
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.object and pc_utils.get_assembly_bp(context.object):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        assembly = pc_types.Assembly(assembly_bp)   
        draw_assembly_properties(context,layout,assembly)     

classes = (
    VIEW3D_PT_pc_assembly_properties,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                