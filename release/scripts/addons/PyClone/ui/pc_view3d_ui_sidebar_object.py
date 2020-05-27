import bpy
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
        )

from .. import pyclone_utils
from ..pc_lib import pc_utils, pc_types

class VIEW3D_PT_pc_object_prompts(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Prompts"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='LINENUMBERS_ON')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        obj.pyclone.draw_prompts(layout)

class VIEW3D_PT_pc_object_material_pointers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Material Pointers"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='SHADING_TEXTURE')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        slot = None
        if len(obj.material_slots) >= obj.active_material_index + 1:
            slot = obj.material_slots[obj.active_material_index]

        is_sortable = len(obj.material_slots) > 1
        rows = 3
        if (is_sortable):
            rows = 5

        row = layout.row()

        if obj.type == 'GPENCIL':
            row.template_list("GPENCIL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=rows)
        else:
            row.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=rows)

        col = row.column(align=True)
        col.operator("pc_material.add_material_slot", icon='ADD', text="").object_name = obj.name
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        if is_sortable:
            col.separator()

            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if slot:
            row = layout.row()
            if len(obj.pyclone.pointers) >= obj.active_material_index + 1:
                pointer_slot = obj.pyclone.pointers[obj.active_material_index]
                row.prop(pointer_slot,'name')
            else:
                row.operator('pc_material.add_material_pointers').object_name = obj.name

        # row = layout.row()
        # row.template_ID(obj, "active_material", new="material.new")
        # if slot:
        #     icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
        #     row.prop(slot, "link", icon=icon_link, icon_only=True)

        if obj.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

        # if obj.type == 'GPENCIL':
        #     pass
        # else:
        #     layout.operator("bp_general.open_new_editor",text="Open Material Editor",icon='MATERIAL').space_type = 'NODE_EDITOR'


class VIEW3D_PT_pc_object_drivers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Drivers"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='AUTO')

    def draw_driver_expression(self,layout,driver):
        row = layout.row(align=True)
        # row.prop(driver.driver,'show_debug_info',text="",icon='DECORATE')
        if driver.driver.is_valid:
            row.prop(driver.driver,"expression",text="",expand=True,icon='DECORATE')
            if driver.mute:
                row.prop(driver,"mute",text="",icon='DECORATE')
            else:
                row.prop(driver,"mute",text="",icon='DECORATE')
        else:
            row.prop(driver.driver,"expression",text="",expand=True,icon='ERROR')
            if driver.mute:
                row.prop(driver,"mute",text="",icon='DECORATE')
            else:
                row.prop(driver,"mute",text="",icon='DECORATE')

    def draw_driver_variable(self,layout,driver,obj):
        for var in driver.driver.variables:
            col = layout.column()
            boxvar = col.box()
            row = boxvar.row(align=True)
            row.prop(var,"name",text="",icon='FORWARD')
            
            props = row.operator("pc_driver.remove_variable",text="",icon='X',emboss=False)
            props.object_name = obj.name
            props.data_path = driver.data_path
            props.array_index = driver.array_index
            props.var_name = var.name

            for target in var.targets:
                if obj.pyclone.show_driver_debug_info:
                    row = boxvar.row()
                    row.prop(var,"type",text="")
                    row = boxvar.row()
                    row.prop(target,"id",text="")
                    row = boxvar.row(align=True)
                    row.prop(target,"data_path",text="",icon='ANIM_DATA')

                if target.id and target.data_path != "":
                    value = eval('bpy.data.objects["' + target.id.name + '"]'"." + target.data_path)
                else:
                    value = "ERROR#"
                row = boxvar.row()
                row.alignment = 'CENTER'
                if type(value).__name__ == 'str':
                    row.label(text="Value: " + value)
                elif type(value).__name__ == 'float':
                    row.label(text="Value: " + str(bpy.utils.units.to_string(bpy.context.scene.unit_settings.system,'LENGTH',value)))
                elif type(value).__name__ == 'int':
                    row.label(text="Value: " + str(value))
                elif type(value).__name__ == 'bool':
                    row.label(text="Value: " + str(value))       

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            drivers = pyclone_utils.get_drivers(obj)

            # if not obj.animation_data:
            #     layout.label(text="There are no drivers assigned to the object",icon='ERROR')
            # else:
            #     if len(obj.animation_data.drivers) == 0:
            #         layout.label(text="There are no drivers assigned to the object",icon='ERROR')
            #     else:
            #         layout.prop(obj.ap_props,'show_driver_debug_info')

#FIGURE OUT HOW TO GET DRIVERS FROM DATA

            if len(drivers) == 0:
                layout.label(text="No Drivers Found on Object")

            for driver in drivers:
                box = layout.box()
                row = box.row()
                driver_name = driver.data_path
                if driver_name in {"location","rotation_euler","dimensions" ,"lock_scale",'lock_location','lock_rotation'}:
                    if driver.array_index == 0:
                        driver_name = driver_name + " X"
                    if driver.array_index == 1:
                        driver_name = driver_name + " Y"
                    if driver.array_index == 2:
                        driver_name = driver_name + " Z"    
                try:
                    value = eval('bpy.data.objects["' + obj.name + '"].' + driver.data_path)
                except:
                    value = eval('bpy.data.objects["' + obj.name + '"].data.' + driver.data_path)
                if type(value).__name__ == 'str':
                    row.label(text=driver_name + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'float':
                    row.label(text=driver_name + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'int':
                    row.label(text=driver_name + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'bool':
                    row.label(text=driver_name + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'bpy_prop_array':
                    row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
                elif type(value).__name__ == 'Vector':
                    row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
                elif type(value).__name__ == 'Euler':
                    row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
                else:
                    row.label(text=driver_name + " = " + str(type(value)),icon='AUTO')

                obj_bp = pc_utils.get_assembly_bp(obj)
                if obj_bp:
                    assembly = pc_types.Assembly(obj_bp)
                    props = row.operator('pc_driver.get_vars_from_object',text="",icon='DRIVER')
                    props.object_name = obj.name
                    props.var_object_name = assembly.obj_prompts.name
                    props.data_path = driver.data_path
                    props.array_index = driver.array_index
                else:
                    props = row.operator('pc_driver.get_vars_from_object',text="",icon='DRIVER')
                    props.object_name = obj.name
                    props.var_object_name = obj.name
                    props.data_path = driver.data_path
                    props.array_index = driver.array_index
                
                self.draw_driver_expression(box,driver)
                self.draw_driver_variable(box,driver,obj)     

classes = (
    VIEW3D_PT_pc_object_prompts,
    VIEW3D_PT_pc_object_drivers,
    VIEW3D_PT_pc_object_material_pointers
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
