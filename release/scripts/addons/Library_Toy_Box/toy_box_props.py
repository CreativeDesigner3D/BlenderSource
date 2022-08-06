import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from . import toy_box_utils
from .pc_lib import pc_utils

def update_library_paths(self,context):
    toy_box_utils.write_xml_file()

class Toy_Box_Library_Window_Manager_Props(PropertyGroup):

    assembly_library_path: bpy.props.StringProperty(name="Assembly Library Path",
                                                    default="",
                                                    subtype='DIR_PATH',
                                                    update=update_library_paths)

    object_library_path: bpy.props.StringProperty(name="Object Library Path",
                                                   default="",
                                                   subtype='DIR_PATH',
                                                   update=update_library_paths)
    
    collection_library_path: bpy.props.StringProperty(name="Collection Library Path",
                                                  default="",
                                                  subtype='DIR_PATH',
                                                  update=update_library_paths)
    
    material_library_path: bpy.props.StringProperty(name="Material Library Path",
                                                     default="",
                                                     subtype='DIR_PATH',
                                                     update=update_library_paths)        

    world_library_path: bpy.props.StringProperty(name="World Library Path",
                                                     default="",
                                                     subtype='DIR_PATH',
                                                     update=update_library_paths)   

    @classmethod
    def register(cls):
        bpy.types.WindowManager.toy_box_library = PointerProperty(
            name="Toy Box Window Manager Props",
            description="Toy Box Window Manager Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.toy_box_library


class Toy_Box_Library_Scene_Props(PropertyGroup):

    active_assembly_category: StringProperty(name="Active Assembly Category",default="")

    active_object_category: StringProperty(name="Active Object Category",default="")

    active_collection_category: StringProperty(name="Active Collection Library",default="")

    active_material_category: StringProperty(name="Active Material Library",default="")

    active_world_category: StringProperty(name="Active World Library",default="")

    def draw_filebrowser_header(self,layout,context):
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

    @classmethod
    def register(cls):
        bpy.types.Scene.toy_box_library = PointerProperty(
            name="Toy Box Scene Props",
            description="Toy Box Scene Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.toy_box_library

classes = (
    Toy_Box_Library_Window_Manager_Props,
    Toy_Box_Library_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)        