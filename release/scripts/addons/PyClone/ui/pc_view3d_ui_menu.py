import bpy

def draw_assembly_properties(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_AREA'
    obj = context.object
    if obj and "PROMPT_ID" in obj and obj["PROMPT_ID"] != "":
        layout.operator(obj["PROMPT_ID"],icon='SETTINGS')
        layout.separator()
    if obj and "MENU_ID" in obj and obj["MENU_ID"] != "":
        layout.operator('INVOKE_DEFAULT',obj["MENU_ID"],icon='SETTINGS')
        layout.separator()   

def draw_mesh_context(self, context):
    layout = self.layout
    layout.menu("VIEW3D_MT_assembly_vertex_groups",icon='GROUP_VERTEX')
    layout.separator()

class VIEW3D_MT_assembly_vertex_groups(bpy.types.Menu):
    bl_label = "Assembly Vertex Groups"

    def draw(self, context):
        layout = self.layout
        for vgroup in context.active_object.vertex_groups:
            count = 0
            for vert in context.active_object.data.vertices:
                for group in vert.groups:
                    if group.group == vgroup.index:
                        count += 1
            layout.operator('pc_object.assign_verties_to_vertex_group',text="Assign to - " + vgroup.name + " (" + str(count) + ")").vertex_group_name = vgroup.name
        layout.separator()
        layout.operator('pc_assembly.connect_meshes_to_hooks_in_assembly',text='Connect Hooks',icon='HOOK').obj_name = context.active_object.name
        layout.operator('pc_object.clear_vertex_groups',text='Clear All Vertex Group Assignments',icon='X').obj_name = context.active_object.name

def draw_add_object(self,context):
    layout = self.layout
    layout.operator_context = 'INVOKE_AREA'
    layout.operator('pc_assembly.create_new_assembly',text="Add Assembly",icon='FILE_3D')
    layout.separator()    

def register():
    # bpy.types.FILEBROWSER_MT_context_menu.prepend(draw_file_browser_menu)
    # bpy.types.VIEW3D_MT_object_context_menu.prepend(draw_assembly_properties)

    bpy.utils.register_class(VIEW3D_MT_assembly_vertex_groups)
    bpy.types.VIEW3D_MT_edit_mesh.prepend(draw_mesh_context)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(draw_assembly_properties)    
    bpy.types.VIEW3D_MT_add.prepend(draw_add_object)
    # bpy.types.VIEW3D_MT_edit_curve_context_menu.prepend()

def unregister():
    # bpy.types.FILEBROWSER_MT_context_menu.remove(draw_file_browser_menu)
    # bpy.types.VIEW3D_MT_object_context_menu.remove(draw_assembly_properties)
    bpy.utils.unregister_class(VIEW3D_MT_assembly_vertex_groups)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_mesh_context)
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_assembly_properties)    
    bpy.types.VIEW3D_MT_add.remove(draw_add_object)
    # bpy.types.VIEW3D_MT_edit_curve_context_menu.remove