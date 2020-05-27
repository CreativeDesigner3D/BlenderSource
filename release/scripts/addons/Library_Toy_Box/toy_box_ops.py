import bpy,os,inspect

from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator,
                       PropertyGroup)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)
from . import toy_box_utils
from .pc_lib import pc_utils

class toy_box_OT_activate(Operator):
    bl_idname = "toy_box.activate"
    bl_label = "Activate Library"
    bl_description = "This will active the toy box library"
    bl_options = {'UNDO'}
    
    library_name: StringProperty(name='Library Name')

    def execute(self, context):
        root_path = toy_box_utils.get_active_library_path()

        if not os.path.exists(root_path):
            os.makedirs(root_path)

        folders = toy_box_utils.get_active_categories()
        active_folder_name = toy_box_utils.get_active_category(folders)
        if root_path and active_folder_name and os.path.exists(os.path.join(root_path,active_folder_name)):
            pc_utils.update_file_browser_path(context,os.path.join(root_path,active_folder_name))      
        else:
            pc_utils.update_file_browser_path(context,root_path)
        return {'FINISHED'}


class toy_box_OT_drop(Operator):
    bl_idname = "toy_box.drop"
    bl_description = "Drop Asset from Toy Box Library"
    bl_label = "Drop File"
    bl_options = {'UNDO'}
    
    filepath: StringProperty(name='Library Name')

    def execute(self, context):
        pyclone = pc_utils.get_scene_props(context.scene)

        if pyclone.active_library_name == toy_box_utils.ASSEMBLY_LIBRARY_NAME:
            bpy.ops.toy_box.drop_assembly_from_library(filepath=self.filepath)

        if pyclone.active_library_name == toy_box_utils.OBJECT_LIBRARY_NAME:
            bpy.ops.toy_box.drop_object_from_library(filepath=self.filepath)

        if pyclone.active_library_name == toy_box_utils.COLLECTION_LIBRARY_NAME:
            bpy.ops.toy_box.drop_collection_from_library(filepath=self.filepath)

        if pyclone.active_library_name == toy_box_utils.MATERIAL_LIBRARY_NAME:
            bpy.ops.toy_box.drop_material_from_library(filepath=self.filepath)

        if pyclone.active_library_name == toy_box_utils.WORLD_LIBRARY_NAME:
            bpy.ops.toy_box.drop_world_from_library(filepath=self.filepath)       
        
        return {'FINISHED'}


class toy_box_OT_change_category(bpy.types.Operator):
    bl_idname = "toy_box.change_library_category"
    bl_label = "Change Library Category"
    bl_description = "Change Library Category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        pyclone = pc_utils.get_scene_props(context.scene)
        props = toy_box_utils.get_scene_props(context.scene)

        if pyclone.active_library_name == toy_box_utils.ASSEMBLY_LIBRARY_NAME:
            props.active_assembly_category = self.category
        if pyclone.active_library_name == toy_box_utils.OBJECT_LIBRARY_NAME:
            props.active_object_category = self.category
        if pyclone.active_library_name == toy_box_utils.COLLECTION_LIBRARY_NAME:
            props.active_collection_category = self.category
        if pyclone.active_library_name == toy_box_utils.MATERIAL_LIBRARY_NAME:
            props.active_material_category = self.category
        if pyclone.active_library_name == toy_box_utils.WORLD_LIBRARY_NAME:
            props.active_world_category = self.category

        path = os.path.join(toy_box_utils.get_active_library_path(),self.category)
        if os.path.exists(path):
            pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}


class toy_box_OT_create_new_category(bpy.types.Operator):
    bl_idname = "toy_box.create_new_category"
    bl_label = "Create New Category"
    bl_description = "This will create a new category"
    
    path: bpy.props.StringProperty(name="Path",description="Path to Add Folder to To")
    folder_name: bpy.props.StringProperty(name="Folder Name",description="Folder Name to Create")

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the folder name to add")
        layout.prop(self,'folder_name',icon='FILE_FOLDER')

    def execute(self, context):
        root_path = toy_box_utils.get_active_library_path()
        path = os.path.join(root_path, self.folder_name)
        if not os.path.exists(path):
            os.makedirs(path)
        pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}


class toy_box_OT_open_browser_window(bpy.types.Operator):
    bl_idname = "toy_box.open_browser_window"
    bl_label = "Open Browser Window"
    bl_description = "This will open the active path in your OS file browser"

    path: bpy.props.StringProperty(name="Path",description="Path to Open")

    def execute(self, context):
        import subprocess
        if 'Windows' in str(bpy.app.build_platform):
            subprocess.Popen(r'explorer ' + self.path)
        elif 'Darwin' in str(bpy.app.build_platform):
            subprocess.Popen(['open' , os.path.normpath(self.path)])
        else:
            subprocess.Popen(['xdg-open' , os.path.normpath(self.path)])
        return {'FINISHED'}


class toy_box_OT_change_library_path(bpy.types.Operator):
    bl_idname = "toy_box.change_library_path"
    bl_label = "Change Library Path"
    bl_description = "This will change the location to store the library assets"
    
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def invoke(self, context, event):
        wm = context.window_manager
        if os.path.exists(toy_box_utils.get_active_library_path()):
            self.directory = toy_box_utils.get_active_library_path()
        wm.fileselect_add(self)      
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if os.path.exists(self.directory):
            wm = context.window_manager
            pyclone = pc_utils.get_scene_props(context.scene)
            wm_props = toy_box_utils.get_window_manager_props(context.window_manager)

            if pyclone.active_library_name == toy_box_utils.ASSEMBLY_LIBRARY_NAME:
                wm_props.assembly_library_path = self.directory

            if pyclone.active_library_name == toy_box_utils.OBJECT_LIBRARY_NAME:
                wm_props.object_library_path = self.directory

            if pyclone.active_library_name == toy_box_utils.COLLECTION_LIBRARY_NAME:
                wm_props.collection_library_path = self.directory

            if pyclone.active_library_name == toy_box_utils.MATERIAL_LIBRARY_NAME:
                wm_props.material_library_path = self.directory

            if pyclone.active_library_name == toy_box_utils.WORLD_LIBRARY_NAME:
                wm_props.world_library_path = self.directory                                                
        return {'FINISHED'}


class toy_box_OT_assign_material_dialog(bpy.types.Operator):
    bl_idname = "toy_box.assign_material_dialog"
    bl_label = "Assign Material Dialog"
    bl_description = "This is a dialog to assign materials to material slots"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    obj = None
    material = None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        self.material = bpy.data.materials[self.material_name]
        self.obj = bpy.data.objects[self.object_name]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)
        
    def draw(self,context):
        layout = self.layout
        layout.label(text=self.obj.name,icon='OBJECT_DATA')
        for index, mat_slot in enumerate(self.obj.material_slots):
            row = layout.split(factor=.55)
            if mat_slot.name == "":
                row.label(text='No Material')
            else:
                row.prop(mat_slot,"name",text="",icon='MATERIAL')

            props = row.operator('toy_box.assign_material_to_slot',text="Assign",icon='BACK')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index
        
            props = row.operator('toy_box.replace_all_materials',text="Replace All",icon='FILE_REFRESH')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index
        
    def execute(self,context):
        return {'FINISHED'}        
        
class toy_box_OT_assign_material_to_slot(bpy.types.Operator):
    bl_idname = "toy_box.assign_material_to_slot"
    bl_label = "Assign Material to Slot"
    bl_description = "This will assign a material to a material slot"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    index: bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        obj.material_slots[self.index].material = mat
        return {'FINISHED'}


class toy_box_OT_replace_all_materials(bpy.types.Operator):
    bl_idname = "toy_box.replace_all_materials"
    bl_label = "Assign Material to Slot"
    bl_description = "This will replace all materials in the file with a new material"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    index: bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        mat_to_replace = obj.material_slots[self.index].material
        obj.material_slots[self.index].material = mat
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                if slot.material == mat_to_replace:
                    slot.material = mat
        return {'FINISHED'}


classes = (
    toy_box_OT_activate,
    toy_box_OT_drop,
    toy_box_OT_change_category,
    toy_box_OT_create_new_category,
    toy_box_OT_open_browser_window,
    toy_box_OT_change_library_path,
    toy_box_OT_assign_material_dialog,
    toy_box_OT_assign_material_to_slot,
    toy_box_OT_replace_all_materials
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
