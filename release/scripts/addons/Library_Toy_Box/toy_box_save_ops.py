import bpy,os,inspect,codecs,subprocess

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
from .pc_lib import pc_utils, pc_types


def create_object_thumbnail_script(source_dir,source_file,object_name):
    file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
    file.write("import bpy\n")
    file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
    file.write("    for obj in data_from.objects:\n")
    file.write("        if obj == '" + object_name + "':\n")
    file.write("            data_to.objects = [obj]\n")
    file.write("            break\n")
    file.write("for obj in data_to.objects:\n")
    file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
    file.write("    obj.select_set(True)\n")
    file.write("    if obj.type == 'CURVE':\n")
    file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
    file.write("        obj.data.dimensions = '2D'\n")
    file.write("    bpy.context.view_layer.objects.active = obj\n")
    file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
    file.write("    render = bpy.context.scene.render\n")
    file.write("    render.use_file_extension = True\n")
    file.write("    render.filepath = r'" + os.path.join(source_dir,object_name) + "'\n")
    file.write("    bpy.ops.render.render(write_still=True)\n")
    file.close()
    
    return os.path.join(bpy.app.tempdir,'thumb_temp.py')
    
def create_object_save_script(source_dir,source_file,object_name):
    file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
    file.write("import bpy\n")
    file.write("import os\n")
    file.write("for mat in bpy.data.materials:\n")
    file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
    file.write("for obj in bpy.data.objects:\n")
    file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
    file.write("bpy.context.preferences.filepaths.save_version = 0\n")
    file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
    file.write("    for obj in data_from.objects:\n")
    file.write("        if obj == '" + object_name + "':\n")
    file.write("            data_to.objects = [obj]\n")
    file.write("            break\n")
    file.write("for obj in data_to.objects:\n")
    file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
    file.write("    obj.select_set(True)\n")
    file.write("    if obj.type == 'CURVE':\n")
    file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
    file.write("        obj.data.dimensions = '2D'\n")
    file.write("    bpy.context.view_layer.objects.active = obj\n")
    file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,object_name) + ".blend')\n")
    file.close()
    
    return os.path.join(bpy.app.tempdir,'save_temp.py')   

class toy_box_OT_save_object_to_asset_library(bpy.types.Operator):
    bl_idname = "toy_box.save_object_to_asset_library"
    bl_label = "Save Object to Library"
    bl_description = "This will save the selected object to the library"
    
    obj_name: bpy.props.StringProperty(name="Obj Name")
    obj = None
    
    @classmethod
    def poll(cls, context):
        return context.object

    def check(self, context):
        return True

    def invoke(self,context,event):
        self.obj_name = context.object.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout

        path = toy_box_utils.get_filebrowser_path(context).decode("utf-8")
        files = os.listdir(path) if os.path.exists(path) else []

        layout.label(text="Object Name: " + self.obj_name)
        
        if self.obj_name + ".blend" in files or self.obj_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")        

    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
        
        directory_to_save_to = toy_box_utils.get_filebrowser_path(context).decode("utf-8")

        thumbnail_script_path = create_object_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.obj_name)
        save_script_path = create_object_save_script(directory_to_save_to, bpy.data.filepath, self.obj_name)

        # subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        tn_command = [bpy.app.binary_path,toy_box_utils.get_thumbnail_file_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]
        
        subprocess.call(tn_command)   
        subprocess.call(save_command)
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)

        bpy.ops.file.refresh()
        
        return {'FINISHED'}


class toy_box_OT_save_collection_to_asset_library(bpy.types.Operator):
    bl_idname = "toy_box.save_collection_to_asset_library"
    bl_label = "Save Collection to Library"
    bl_description = "This will save the selected collection to the library"
    
    collection_name: bpy.props.StringProperty(name="Collection Name")
    
    @classmethod
    def poll(cls, context):
        return True #FIGURE OUT WHAT IS ACTIVE
        # if context.scene.outliner.selected_collection_index + 1 <= len(bpy.data.collections):
        #     return True
        # else:
        #     return False

    def check(self, context):
        return True

    def invoke(self,context,event):
        collection = context.view_layer.active_layer_collection.collection
        self.collection_name = collection.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        path = toy_box_utils.get_filebrowser_path(context).decode("utf-8")
        files = os.listdir(path) if os.path.exists(path) else []

        layout.label(text="Collection Name: " + self.collection_name)

        if self.collection_name + ".blend" in files or self.collection_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")

    def select_collection_objects(self,coll):
        for obj in coll.objects:
            obj.select_set(True)
        for child in coll.children:
            self.select_collection_objects(child)

    def create_collection_thumbnail_script(self,source_dir,source_file,collection_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("def select_collection_objects(coll):\n")
        file.write("    for obj in coll.objects:\n")
        file.write("        obj.select_set(True)\n")
        file.write("    for child in coll.children:\n")
        file.write("        select_collection_objects(child)\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for collection in data_from.collections:\n")
        file.write("        if collection == '" + collection_name + "':\n")
        file.write("            data_to.collections = [collection]\n")
        file.write("            break\n")
        file.write("for collection in data_to.collections:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.children.link(collection)\n")
        file.write("    select_collection_objects(collection)\n")
        # file.write("    for obj in collection.objects:\n")
        # file.write("        bpy.context.scene.objects.link(obj)\n") #TODO: FIX
        # file.write("        obj.select_set(True)\n")
        # file.write("        bpy.context.scene.objects.active = obj\n")
        file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,collection_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_collection_save_script(self,source_dir,source_file,collection_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n") #TODO: FIX THIS
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for collection in data_from.collections:\n")
        file.write("        if collection == '" + collection_name + "':\n")
        file.write("            data_to.collections = [collection]\n")
        file.write("            break\n")
        file.write("for collection in data_to.collections:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.children.link(collection)\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,collection_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
                    
        directory_to_save_to = toy_box_utils.get_filebrowser_path(context).decode("utf-8")

        thumbnail_script_path = self.create_collection_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.collection_name)
        save_script_path = self.create_collection_save_script(directory_to_save_to, bpy.data.filepath, self.collection_name)

#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        tn_command = [bpy.app.binary_path,toy_box_utils.get_thumbnail_file_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]

        subprocess.call(tn_command)
        subprocess.call(save_command)
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        
        bpy.ops.file.refresh()

        return {'FINISHED'}


class toy_box_OT_save_material_to_asset_library(bpy.types.Operator):
    bl_idname = "toy_box.save_material_to_asset_library"
    bl_label = "Save Material to Asset Library"
    bl_description = "This will save the active material to the library"
    
    mat_name: bpy.props.StringProperty(name="Material Name")
        
    @classmethod
    def poll(cls, context):
        if context.object and context.object.active_material:
            return True
        else:
            return False

    def check(self, context):     
        return True

    def invoke(self,context,event):
        mat = context.object.active_material
        self.mat_name = mat.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def create_material_thumbnail_script(self,source_dir,source_file,material_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for mat in data_from.materials:\n")
        file.write("        if mat == '" + material_name + "':\n")
        file.write("            data_to.materials = [mat]\n")
        file.write("            break\n")
        file.write("for mat in data_to.materials:\n")
        file.write("    bpy.ops.mesh.primitive_cube_add()\n")
        file.write("    obj = bpy.context.view_layer.objects.active\n")
        file.write("    bpy.ops.object.shade_smooth()\n")
        file.write("    obj.dimensions = (2,2,2)\n")
        file.write("    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)\n")
        file.write("    mod = obj.modifiers.new('bevel','BEVEL')\n")
        file.write("    mod.segments = 5\n")
        file.write("    mod.width = .05\n")
        file.write("    bpy.ops.object.modifier_apply(modifier='bevel')\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.mesh.select_all(action='SELECT')\n")
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.object.material_slot_add()\n")
        file.write("    for slot in obj.material_slots:\n")
        file.write("        slot.material = mat\n")
        file.write("    bpy.context.view_layer.objects.active = obj\n")
        file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,material_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_material_save_script(self,source_dir,source_file,material_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for mat in data_from.materials:\n")
        file.write("        if mat == '" + material_name + "':\n")
        file.write("            data_to.materials = [mat]\n")
        file.write("            break\n")
        file.write("for mat in data_to.materials:\n")
        file.write("    bpy.ops.mesh.primitive_cube_add()\n")
        file.write("    obj = bpy.context.view_layer.objects.active\n")
        file.write("    bpy.ops.object.shade_smooth()\n")
        file.write("    obj.dimensions = (2,2,2)\n")
        file.write("    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)\n")
        file.write("    mod = obj.modifiers.new('bevel','BEVEL')\n")
        file.write("    mod.segments = 5\n")
        file.write("    mod.width = .05\n")
        file.write("    bpy.ops.object.modifier_apply(modifier='bevel')\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.mesh.select_all(action='SELECT')\n")
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.object.material_slot_add()\n")
        file.write("    for slot in obj.material_slots:\n")
        file.write("        slot.material = mat\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,material_name) + ".blend')\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'save_temp.py')
        
    def draw(self, context):
        layout = self.layout

        path = toy_box_utils.get_filebrowser_path(context).decode("utf-8")
        files = os.listdir(path) if os.path.exists(path) else []
            
        layout.label(text="Material Name: " + self.mat_name)
        
        if self.mat_name + ".blend" in files or self.mat_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")         
        
    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
        
        directory_to_save_to = toy_box_utils.get_filebrowser_path(context).decode("utf-8")

        thumbnail_script_path = self.create_material_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.mat_name)
        save_script_path = self.create_material_save_script(directory_to_save_to, bpy.data.filepath, self.mat_name)
        
#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)

        tn_command = [bpy.app.binary_path,toy_box_utils.get_thumbnail_file_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]        

        subprocess.call(tn_command)   
        subprocess.call(save_command)
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)

        bpy.ops.file.refresh()

        return {'FINISHED'}


class toy_box_OT_save_world_to_asset_library(bpy.types.Operator):
    bl_idname = "toy_box.save_world_to_asset_library"
    bl_label = "Save World to Library"
    bl_description = "This will save the active world to the library"
    
    world_name: bpy.props.StringProperty(name="World Name")
    
    world = None
    
    @classmethod
    def poll(cls, context):
        if context.scene.world:
            return True
        else:
            return False
        return True

    def check(self, context):
        return True

    def invoke(self,context,event):
        self.world_name = context.scene.world.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout

        path = toy_box_utils.get_filebrowser_path(context).decode("utf-8")
        files = os.listdir(path) if os.path.exists(path) else []
            
        layout.label(text="World Name: " + self.world_name)
        
        if self.world_name + ".blend" in files or self.world_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")
        
    def create_world_thumbnail_script(self,source_dir,source_file,world_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for world in data_from.worlds:\n")
        file.write("        if world == '" + world_name + "':\n")
        file.write("            data_to.worlds = [world]\n")
        file.write("            break\n")
        file.write("for world in data_to.worlds:\n")
        file.write("    bpy.context.scene.world = world\n")
        file.write("    bpy.context.scene.camera.data.type = 'PANO'\n")
        file.write("    bpy.context.scene.camera.data.cycles.panorama_type = 'EQUIRECTANGULAR'\n")
        file.write("    bpy.context.scene.render.film_transparent = False\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,world_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        
        file.close()
        
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_world_save_script(self,source_dir,source_file,world_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("for world in bpy.data.worlds:\n")
        file.write("    bpy.data.worlds.remove(world,do_unlink=True)\n")            
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for world in data_from.worlds:\n")
        file.write("        if world == '" + world_name + "':\n")
        file.write("            data_to.worlds = [world]\n")
        file.write("            break\n")
        file.write("for world in data_to.worlds:\n")
        file.write("    bpy.context.scene.world = world\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,world_name) + ".blend')\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'save_temp.py')        
        
    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
        
        directory_to_save_to = toy_box_utils.get_filebrowser_path(context).decode("utf-8")

        thumbnail_script_path = self.create_world_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.world_name)
        save_script_path = self.create_world_save_script(directory_to_save_to, bpy.data.filepath, self.world_name)

        # subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        tn_command = [bpy.app.binary_path,toy_box_utils.get_thumbnail_file_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]

        subprocess.call(tn_command)   
        subprocess.call(save_command)
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        
        bpy.ops.file.refresh()

        return {'FINISHED'}


class toy_box_OT_save_assembly_to_asset_library(bpy.types.Operator):
    bl_idname = "toy_box.save_assembly_to_asset_library"
    bl_label = "Save Assembly to Library"
    bl_description = "This will save the active assembly to the library"
    
    assembly_bp_name: bpy.props.StringProperty(name="Collection Name")

    assembly = None
    assembly_name = ""

    @classmethod
    def poll(cls, context):
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        if assembly_bp:
            return True
        else:
            return False

    def check(self, context):
        return True

    def invoke(self,context,event):
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        self.assembly = pc_types.Assembly(assembly_bp)
        self.assembly_name = self.assembly.obj_bp.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        path = toy_box_utils.get_filebrowser_path(context).decode("utf-8")
        files = os.listdir(path) if os.path.exists(path) else []

        layout.label(text="Assembly Name: " + self.assembly_name)

        if self.assembly_name + ".blend" in files or self.assembly_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")

    def select_assembly_objects(self,coll):
        for obj in coll.objects:
            obj.select_set(True)
        for child in coll.children:
            self.select_collection_objects(child)

    def create_assembly_thumbnail_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")    

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    obj.select_set(True)\n")
        
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        file.write("render = bpy.context.scene.render\n")
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = r'" + os.path.join(source_dir,assembly_name) + "'\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_assembly_save_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")        

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")

        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,assembly_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp.name)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
                    
        directory_to_save_to = toy_box_utils.get_filebrowser_path(context).decode("utf-8")

        obj_list = []
        obj_list = self.get_children_list(self.assembly.obj_bp,obj_list)

        thumbnail_script_path = self.create_assembly_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.assembly_name, obj_list)
        save_script_path = self.create_assembly_save_script(directory_to_save_to, bpy.data.filepath, self.assembly_name, obj_list)

#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        tn_command = [bpy.app.binary_path,toy_box_utils.get_thumbnail_file_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]

        subprocess.call(tn_command)
        subprocess.call(save_command)
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        
        bpy.ops.file.refresh()
        
        return {'FINISHED'}


class Asset(bpy.types.PropertyGroup):
    is_checked: bpy.props.BoolProperty(name="Is Checked",default=False)
    path: bpy.props.StringProperty(name="Asset Path",subtype='DIR_PATH')


class toy_box_OT_search_directory_to_save_to_object_library(bpy.types.Operator):
    bl_idname = "toy_box.search_directory_to_save_to_object_library"
    bl_label = "Save Objects"
    bl_description = "This will allow users to select a directory to search all files to save objects to the active category."
    
    directory: bpy.props.StringProperty(name="Directory",subtype='DIR_PATH')
    previous_directory: bpy.props.StringProperty(name="Previous Directory",subtype='DIR_PATH')

    objects: bpy.props.CollectionProperty(type=Asset)
    
    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        if self.directory != self.previous_directory:
            self.get_objects_from_directory(context)
        self.previous_directory = self.directory
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    def get_objects_from_directory(self,context):
        if not os.path.exists(self.directory):
            return []

        for obj in self.objects:
            self.objects.remove(0)

        files = os.listdir(self.directory)
        for f in files:
            filename, ext = os.path.splitext(f)
            if ext == '.blend':
                with bpy.data.libraries.load(os.path.join(self.directory,f), False, True) as (data_from, data_to):
                    for obj in data_from.objects:
                        o = self.objects.add()
                        o.name = obj
                        o.path = os.path.join(self.directory,f)
                        o.is_checked = True

    def check_for_duplicate_file(self,context,path):
        if os.path.exists(path + ".blend"):
            return True
        if os.path.exists(path + ".png"):
            return True
        return False

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text=str(len(self.objects)) + " Objects Found",icon='OBJECT_DATA')
        for obj in self.objects:
            row = col.row()
            row.prop(obj,'is_checked',text=obj.name)     
        
    def execute(self, context):

        directory_to_save_to = toy_box_utils.get_filebrowser_path(context).decode("utf-8")

        for obj in self.objects:
            if obj.is_checked:
                thumbnail_script_path = create_object_thumbnail_script(directory_to_save_to, obj.path, obj.name)
                save_script_path = create_object_save_script(directory_to_save_to, obj.path, obj.name)

                # subprocess.Popen(r'explorer ' + bpy.app.tempdir)
                tn_command = [bpy.app.binary_path,toy_box_utils.get_thumbnail_file_path(),"-b","--python",thumbnail_script_path]
                save_command = [bpy.app.binary_path,"-b","--python",save_script_path]

                subprocess.call(tn_command)   
                subprocess.call(save_command)
            
                os.remove(thumbnail_script_path)
                os.remove(save_script_path)

        bpy.ops.file.refresh()
        
        return {'FINISHED'}


classes = (
    Asset,
    toy_box_OT_save_object_to_asset_library,
    toy_box_OT_save_collection_to_asset_library,
    toy_box_OT_save_material_to_asset_library,
    toy_box_OT_save_world_to_asset_library,
    toy_box_OT_save_assembly_to_asset_library,
    toy_box_OT_search_directory_to_save_to_object_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
