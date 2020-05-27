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
from .pc_lib import pc_utils

def event_is_place_asset(event):
    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        return True
    elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
        return True
    elif event.type == 'RET' and event.value == 'PRESS':
        return True
    else:
        return False

def event_is_cancel_command(event):
    if event.type in {'RIGHTMOUSE', 'ESC'}:
        return True
    else:
        return False

def event_is_pass_through(event):
    if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
        return True
    else:
        return False

class toy_box_OT_drop_object_from_library(bpy.types.Operator):
    bl_idname = "toy_box.drop_object_from_library"
    bl_label = "Drop Object From Library"
    bl_description = "This drops an object from the library"

    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    drawing_plane = None
    obj = None
    
    def execute(self, context):
        self.create_drawing_plane(context)
        self.obj = self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        path, ext = os.path.splitext(self.filepath)
        object_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(object_file_path, False, False) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            context.view_layer.active_layer_collection.collection.objects.link(obj)
            return obj

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=[self.obj])

        if event.ctrl:
            if event.mouse_y > event.mouse_prev_y:
                self.obj.rotation_euler.z += .1
            else:
                self.obj.rotation_euler.z -= .1
        else:
            self.position_object(selected_point,selected_obj)

        if event_is_place_asset(event):
            return self.finish(context)

        if event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        self.obj.location = selected_point

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.obj)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)  
        context.view_layer.objects.active = self.obj 
        context.area.tag_redraw()
        return {'FINISHED'}


class toy_box_OT_drop_collection_from_library(bpy.types.Operator):
    bl_idname = "toy_box.drop_collection_from_library"
    bl_label = "Drop Collection From Library"
    bl_description = "This drops a collection from the library"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    drawing_plane = None
    grp = None
    parent_obj_dict = {}
    collection_objects = []
    
    @classmethod
    def poll(cls, context):
        active_col = context.view_layer.active_layer_collection.collection
        if active_col.hide_viewport:
            return False
        if context.object and context.object.mode != 'OBJECT':
            return False        
        return True

    def execute(self, context):
        self.parent_obj_dict = {}
        self.collection_objects = []
        self.create_drawing_plane(context)
        self.grp = self.get_collection(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_collection_objects(self,coll):
        for obj in coll.objects:
            self.collection_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)

        for child in coll.children:
            self.get_collection_objects(child)

    def get_collection(self,context):
        path, ext = os.path.splitext(self.filepath)
        self.collection_name = os.path.basename(path)
        collection_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(collection_file_path, False, False) as (data_from, data_to):
            
            for coll in data_from.collections:
                if coll == self.collection_name:
                    data_to.collections = [coll]
                    break
            
        for coll in data_to.collections:
            context.view_layer.active_layer_collection.collection.children.link(coll)
            self.get_collection_objects(coll)
            return coll

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def position_collection(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=self.collection_objects)

        self.position_collection(selected_point,selected_obj)
        
        if event_is_place_asset(event):
            return self.finish(context)

        if event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.collection_objects:
            obj_list.append(obj)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        for obj, location in self.parent_obj_dict.items():
            obj.select_set(True)  
            context.view_layer.objects.active = obj             
        context.area.tag_redraw()
        return {'FINISHED'}


class toy_box_OT_drop_material_from_library(bpy.types.Operator):
    bl_idname = "toy_box.drop_material_from_library"
    bl_label = "Drop Material From Library"
    bl_description = "This drops a material from the library"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    mat = None
    
    @classmethod
    def poll(cls, context):  
        if context.object and context.object.mode != 'OBJECT':
            return False
        return True
        
    def execute(self, context):
        self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def get_material(self,context):
        path, ext = os.path.splitext(self.filepath)
        material_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(material_file_path, False, False) as (data_from, data_to):
            
            for mat in data_from.materials:
                data_to.materials = [mat]
                break
            
        for mat in data_to.materials:
            return mat
    
    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = pc_utils.get_selection_point(context,event)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select_set(True)
            context.view_layer.objects.active = selected_obj
        
            if event_is_place_asset(event):
                if len(selected_obj.data.uv_layers) == 0:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT') 
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)  
                    bpy.ops.object.editmode_toggle()

                if len(selected_obj.material_slots) == 0:
                    bpy.ops.object.material_slot_add()

                if len(selected_obj.material_slots) > 1:
                    bpy.ops.toy_box.assign_material_dialog('INVOKE_DEFAULT',material_name = self.mat.name, object_name = selected_obj.name)
                    return self.finish(context)
                else:
                    for slot in selected_obj.material_slots:
                        slot.material = self.mat
                        
                return self.finish(context)

        if event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}


class toy_box_OT_drop_world_from_library(bpy.types.Operator):
    bl_idname = "toy_box.drop_world_from_library"
    bl_label = "Drop World From Library"
    bl_description = "This drops a world from the library"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")
    
    def execute(self, context):
        context.scene.world = self.get_world(context)
        context.area.tag_redraw()
        return {'FINISHED'}

    def get_world(self,context):
        path, ext = os.path.splitext(self.filepath)
        world_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(world_file_path, False, False) as (data_from, data_to):
            for world in data_from.worlds:
                data_to.worlds = [world]
                break
        for world in data_to.worlds:
            return world


class toy_box_OT_drop_assembly_from_library(bpy.types.Operator):
    bl_idname = "toy_box.drop_assembly_from_library"
    bl_label = "Drop Assembly From Library"
    bl_description = "This drops an assembly from the library"

    filepath: bpy.props.StringProperty(name="Filepath",default="Error")
    
    def execute(self, context):
        #TODO:
        return {'FINISHED'}


classes = (
    toy_box_OT_drop_object_from_library,
    toy_box_OT_drop_collection_from_library,
    toy_box_OT_drop_material_from_library,
    toy_box_OT_drop_world_from_library,
    toy_box_OT_drop_assembly_from_library
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()