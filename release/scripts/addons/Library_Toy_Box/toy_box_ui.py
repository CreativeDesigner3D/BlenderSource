import bpy
import os
from .pc_lib import pc_utils
from . import toy_box_utils

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
            layout.operator('toy_box.search_directory_to_save_to_object_library',icon='NEWFOLDER') 
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
    FILEBROWSER_MT_library_category_menu,
    LIBRARY_MT_library_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)                