import bpy
import os
from .pc_lib import pc_utils
from . import toy_box_utils

LIBRARY_NAMES = {toy_box_utils.ASSEMBLY_LIBRARY_NAME,
                 toy_box_utils.OBJECT_LIBRARY_NAME,
                 toy_box_utils.COLLECTION_LIBRARY_NAME,
                 toy_box_utils.MATERIAL_LIBRARY_NAME,
                 toy_box_utils.WORLD_LIBRARY_NAME}

class FILEBROWSER_PT_toy_box_library_headers(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'UI'
    bl_label = "Library"
    bl_category = "Attributes"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        #Only display when active and File Browser is not open as separate window
        if len(context.area.spaces) > 1:
            pyclone = pc_utils.get_scene_props(context.scene)
            if pyclone.active_library_name in LIBRARY_NAMES:
                return True   
        return False

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        pyclone = pc_utils.get_scene_props(context.scene)
        row = col.row()
        row.scale_y = 1.3       
        row.label(text=pyclone.active_library_name,icon=toy_box_utils.get_active_library_icon()) 
        row.separator()
        row.menu('LIBRARY_MT_library_commands',text="",icon='SETTINGS') 

        folders = toy_box_utils.get_active_categories()

        row = col.row()

        if len(folders) == 0:
            row.scale_y = 1.3            
            row.operator('toy_box.create_new_category',text="Create New Category",icon='ADD')
        else:
            row.scale_y = 1.3
            row.menu('FILEBROWSER_MT_library_category_menu',text=toy_box_utils.get_active_category(folders),icon='FILEBROWSER')  


class FILEBROWSER_MT_library_category_menu(bpy.types.Menu):
    bl_label = "Library"

    def draw(self, _context):
        layout = self.layout
        folders = toy_box_utils.get_active_categories()
        for folder in folders:
            layout.operator('toy_box.change_library_category',text=folder,icon='FILE_FOLDER').category = folder

class LIBRARY_MT_library_commands(bpy.types.Menu):
    bl_label = "Library Commands"

    def draw(self, context):
        layout = self.layout
        pyclone = pc_utils.get_scene_props(context.scene)
        if pyclone.active_library_name == toy_box_utils.ASSEMBLY_LIBRARY_NAME:
            layout.operator('toy_box.save_assembly_to_asset_library',icon='BACK')
        if pyclone.active_library_name == toy_box_utils.OBJECT_LIBRARY_NAME:
            layout.operator('toy_box.save_object_to_asset_library',icon='BACK')
        if pyclone.active_library_name == toy_box_utils.COLLECTION_LIBRARY_NAME:
            layout.operator('toy_box.save_collection_to_asset_library',icon='BACK')
        if pyclone.active_library_name == toy_box_utils.MATERIAL_LIBRARY_NAME:
            layout.operator('toy_box.save_material_to_asset_library',icon='BACK')
        if pyclone.active_library_name == toy_box_utils.WORLD_LIBRARY_NAME:
            layout.operator('toy_box.save_world_to_asset_library',icon='BACK')                                        
        layout.separator()
        layout.operator('toy_box.open_browser_window',icon='FILE_FOLDER').path = context.space_data.params.directory.decode("utf-8")
        layout.operator('toy_box.create_new_category',icon='NEWFOLDER')     
        layout.operator('toy_box.change_library_path',icon='FILE_FOLDER')

classes = (
    FILEBROWSER_PT_toy_box_library_headers,
    FILEBROWSER_MT_library_category_menu,
    LIBRARY_MT_library_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)                