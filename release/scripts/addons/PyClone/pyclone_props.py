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
        EnumProperty,
        )
import os
import inspect
import math

prompt_types = [('FLOAT',"Float","Float"),
                ('DISTANCE',"Distance","Distance"),
                ('ANGLE',"Angle","Angle"),
                ('QUANTITY',"Quantity","Quantity"),
                ('PERCENTAGE',"Percentage","Percentage"),
                ('CHECKBOX',"Checkbox","Checkbox"),
                ('COMBOBOX',"Combobox","Combobox"),
                ('TEXT',"Text","Text")]

def add_driver_variables(driver,variables):
    for var in variables:
        new_var = driver.driver.variables.new()
        new_var.type = 'SINGLE_PROP'
        new_var.name = var.name
        new_var.targets[0].data_path = var.data_path
        new_var.targets[0].id = var.obj


class Variable():

    obj = None
    data_path = ""
    name = ""

    def __init__(self,obj,data_path,name):
        self.obj = obj
        self.data_path = data_path
        self.name = name


class Combobox_Item(PropertyGroup):
    pass    


class Library_Item(bpy.types.PropertyGroup):
    package_name: bpy.props.StringProperty(name="Package Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    class_name: bpy.props.StringProperty(name="Class Name")
    placement_id: bpy.props.StringProperty(name="Placement ID")
    prompts_id: bpy.props.StringProperty(name="Prompts ID")
    render_id: bpy.props.StringProperty(name="Render ID")
    category_name: bpy.props.StringProperty(name="Category Name")


class Library(bpy.types.PropertyGroup):
    library_items: bpy.props.CollectionProperty(name="Library Items", type=Library_Item)
    activate_id: bpy.props.StringProperty(name="Activate ID",description="This is the operator id that gets called when you activate the library")
    drop_id: bpy.props.StringProperty(name="Drop ID",description="This is the operator id that gets called when you drop a file onto the 3D Viewport")
    icon: bpy.props.StringProperty(name="Icon",description="This is the icon to display in the panel")

    def load_library_items_from_module(self,module):
        package_name1, package_name2, module_name = module.__name__.split(".")
        for name, obj in inspect.getmembers(module):
            if hasattr(obj,'show_in_library') and name != 'ops' and obj.show_in_library:
                item = self.library_items.add()
                item.package_name = package_name1 + "." + package_name2
                item.category_name = obj.category_name
                item.module_name = module_name
                item.class_name = name
                item.name = name


class Pointer_Slot(bpy.types.PropertyGroup):
    pass


class Prompt(PropertyGroup):
    prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)

    float_value: FloatProperty(name="Float Value")
    distance_value: FloatProperty(name="Distance Value",subtype='DISTANCE')
    angle_value: FloatProperty(name="Angle Value",subtype='ANGLE')
    quantity_value: IntProperty(name="Quantity Value",subtype='DISTANCE',min=0)
    percentage_value: FloatProperty(name="Percentage Value",subtype='PERCENTAGE',min=0,max=1)
    checkbox_value: BoolProperty(name="Checkbox Value", description="")
    text_value: StringProperty(name="Text Value", description="")

    calculator_index: IntProperty(name="Calculator Index")

    combobox_items: CollectionProperty(type=Combobox_Item, name="Tabs")
    combobox_index: IntProperty(name="Combobox Index", description="")
    combobox_columns: IntProperty(name="Combobox Columns",default=1,min=1)

    def get_var(self,name):
        prompt_path = 'pyclone.prompts["' + self.name + '"]'
        if self.prompt_type == 'FLOAT':
            return Variable(self.id_data, prompt_path + '.float_value',name)
        if self.prompt_type == 'DISTANCE':
            return Variable(self.id_data, prompt_path + '.distance_value',name)
        if self.prompt_type == 'ANGLE':
            return Variable(self.id_data, prompt_path + '.angle_value',name)
        if self.prompt_type == 'QUANTITY':
            return Variable(self.id_data, prompt_path + '.quantity_value',name)
        if self.prompt_type == 'PERCENTAGE':
            return Variable(self.id_data, prompt_path + '.percentage_value',name)
        if self.prompt_type == 'CHECKBOX':
            return Variable(self.id_data, prompt_path + '.checkbox_value',name)
        if self.prompt_type == 'COMBOBOX':
            return Variable(self.id_data, prompt_path + '.combobox_index',name) #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            return Variable(self.id_data, prompt_path + '.text_value',name)       

    def get_value(self):
        if self.prompt_type == 'FLOAT':
            return self.float_value
        if self.prompt_type == 'DISTANCE':
            return self.distance_value
        if self.prompt_type == 'ANGLE':
            return self.angle_value
        if self.prompt_type == 'QUANTITY':
            return self.quantity_value
        if self.prompt_type == 'PERCENTAGE':
            return self.percentage_value
        if self.prompt_type == 'CHECKBOX':
            return self.checkbox_value
        if self.prompt_type == 'COMBOBOX':
            return self.combobox_index #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            return self.text_value

    def set_value(self,value):
        if self.prompt_type == 'FLOAT':
            self.float_value = value
        if self.prompt_type == 'DISTANCE':
            self.distance_value = value
        if self.prompt_type == 'ANGLE':
            self.angle_value = math.radians(value)
        if self.prompt_type == 'QUANTITY':
            self.quantity_value = value
        if self.prompt_type == 'PERCENTAGE':
            self.percentage_value = value
        if self.prompt_type == 'CHECKBOX':
            self.checkbox_value = value
        if self.prompt_type == 'COMBOBOX':
            self.combobox_index = value #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            self.text_value = value

    def set_formula(self,expression,variables):
        prompt_path = 'pyclone.prompts["' + self.name + '"]'
        data_path = ""
        if self.prompt_type == 'FLOAT':
            data_path = prompt_path + '.float_value'
        if self.prompt_type == 'DISTANCE':
            data_path = prompt_path + '.distance_value'
        if self.prompt_type == 'ANGLE':
            data_path = prompt_path + '.angle_value'
        if self.prompt_type == 'QUANTITY':
            data_path = prompt_path + '.quantity_value'
        if self.prompt_type == 'PERCENTAGE':
            data_path = prompt_path + '.precentage_value'
        if self.prompt_type == 'CHECKBOX':
            data_path = prompt_path + '.checkbox_value'
        if self.prompt_type == 'COMBOBOX':
            data_path = prompt_path + '.combobox_index'
        if self.prompt_type == 'TEXT':
            data_path = prompt_path + '.text_value'

        driver = self.id_data.driver_add(data_path)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def draw_prompt_properties(self,layout):
        pass #RENAME PROMPT, #LOCK VALUE,  #IF COMBOBOX THEN COLUMN NUMBER

    def draw(self,layout):
        row = layout.row()
        row.label(text=self.name)
        if self.prompt_type == 'FLOAT':
            row.prop(self,"float_value",text="")
        if self.prompt_type == 'DISTANCE':
            row.prop(self,"distance_value",text="")
        if self.prompt_type == 'ANGLE':
            row.prop(self,"angle_value",text="")
        if self.prompt_type == 'QUANTITY':
            row.prop(self,"quantity_value",text="")
        if self.prompt_type == 'PERCENTAGE':
            row.prop(self,"percentage_value",text="")
        if self.prompt_type == 'CHECKBOX':
            row.prop(self,"checkbox_value",text="")
        if self.prompt_type == 'COMBOBOX':
            props = row.operator('pc_prompts.add_combobox_value',text="",icon='ADD')
            props.obj_name = self.id_data.name
            props.prompt_name = self.name
            props = row.operator('pc_prompts.delete_combobox_value',text="",icon='X')
            props.obj_name = self.id_data.name
            props.prompt_name = self.name            
            col = layout.column()
            col.template_list("PC_UL_combobox"," ", self, "combobox_items", self, "combobox_index",
                              rows=len(self.combobox_items)/self.combobox_columns,type='GRID',columns=self.combobox_columns)

        if self.prompt_type == 'TEXT':
            row.prop(self,"text_value",text="")


class Calculator_Prompt(PropertyGroup):
    distance_value: FloatProperty(name="Distance Value",subtype='DISTANCE')
    equal: BoolProperty(name="Equal",default=True)

    def draw(self,layout):
        row = layout.row()
        row.active = False if self.equal else True
        row.prop(self,'distance_value',text=self.name)
        row.prop(self,'equal',text="")

    def get_var(self,calculator_name,name):
        prompt_path = 'pyclone.calculators["' + calculator_name + '"].prompts["' + self.name + '"]'
        return Variable(self.id_data, prompt_path + '.distance_value',name)    


class Calculator(PropertyGroup):
    prompts: CollectionProperty(name="Prompts",type=Calculator_Prompt)
    total_distance: FloatProperty(name="Total Distance",subtype='DISTANCE')

    def set_total_distance(self,expression="",variables=[],value=0):
        data_path = 'pyclone.calculators["' + self.name + '"].total_distance'
        driver = self.id_data.driver_add(data_path)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def draw(self,layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text=self.name)
        props = row.operator('pc_prompts.add_calculator_prompt',text="",icon='ADD')
        props.calculator_name = self.name
        props.obj_name = self.id_data.name
        props = row.operator('pc_prompts.edit_calculator',text="",icon='OUTLINER_DATA_GP_LAYER')
        props.calculator_name = self.name
        props.obj_name = self.id_data.name
        
        box.prop(self,'total_distance')
        box = col.box()
        for prompt in self.prompts:
            prompt.draw(box)
        box = col.box()
        row = box.row()
        row.scale_y = 1.3
        props = row.operator('pc_prompts.run_calculator')
        props.calculator_name = self.name
        props.obj_name = self.id_data.name        

    def add_calculator_prompt(self,name):
        prompt = self.prompts.add()
        prompt.name = name

    def remove_calculator_prompt(self,name):
        pass

    def calculate(self):
        non_equal_prompts_total_value = 0
        equal_prompt_qty = 0
        calc_prompts = []
        for prompt in self.prompts:
            if prompt.equal:
                equal_prompt_qty += 1
                calc_prompts.append(prompt)
            else:
                non_equal_prompts_total_value += prompt.distance_value

        if equal_prompt_qty > 0:
            prompt_value = (self.total_distance - non_equal_prompts_total_value) / equal_prompt_qty

            for prompt in calc_prompts:
                prompt.distance_value = prompt_value

            self.id_data.location = self.id_data.location #NOT SURE THIS IS NEEDED


class PC_Object_Props(PropertyGroup):
    show_driver_debug_info: BoolProperty(name="Show Driver Debug Info", default=False)
    pointers: bpy.props.CollectionProperty(name="Slots", type=Pointer_Slot)
    prompts: CollectionProperty(type=Prompt, name="Prompts")
    calculators: CollectionProperty(type=Calculator, name="Calculators")

    def get_var(self,data_path,name):
        return Variable(self.id_data,data_path,name)

    def delete_prompt(self,name):
        for index, prompt in enumerate(self.prompts):
            if prompt.name == name:
                self.prompts.remove(index)

    def draw_prompts(self,layout):
        props = layout.operator('pc_prompts.add_prompt')
        props.obj_name = self.id_data.name
        props = layout.operator('pc_prompts.add_calculator')
        props.obj_name = self.id_data.name        
        for prompt in self.prompts:
            prompt.draw(layout)
        for cal in self.calculators:
            cal.draw(layout)

    def add_prompt(self,prompt_type,prompt_name):
        prompt = self.prompts.add()
        prompt.prompt_type = prompt_type
        prompt.name = prompt_name
        return prompt

    def add_calculator(self,calculator_name):
        calculator = self.calculators.add()
        calculator.name = calculator_name
        return calculator

    def modifier(self,modifier,property_name,index=-1,expression="",variables=[]):
        driver = modifier.driver_add(property_name,index)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def loc_x(self,expression,variables):
        driver = self.id_data.driver_add('location',0)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def loc_y(self,expression,variables):
        driver = self.id_data.driver_add('location',1)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def loc_z(self,expression,variables):
        driver = self.id_data.driver_add('location',2)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def rot_x(self,expression,variables):
        driver = self.id_data.driver_add('rotation_euler',0)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def rot_y(self,expression,variables):
        driver = self.id_data.driver_add('rotation_euler',1)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def rot_z(self,expression,variables):
        driver = self.id_data.driver_add('rotation_euler',2)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    @classmethod
    def register(cls):
        bpy.types.Object.pyclone = PointerProperty(name="PyClone",description="PyClone Properties",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.pyclone


class PC_Window_Manager_Props(bpy.types.PropertyGroup):
    libraries: CollectionProperty(name="Libraries",type=Library)

    def add_library(self,name,activate_id,drop_id,icon):
        lib = self.libraries.add()
        lib.name = name
        lib.activate_id = activate_id
        lib.drop_id = drop_id
        lib.icon = icon
        return lib

    def remove_library(self,name):
        for i, lib in enumerate(self.libraries):
            if lib.name == name:
                self.libraries.remove(i)

    @classmethod
    def register(cls):
        bpy.types.WindowManager.pyclone = bpy.props.PointerProperty(
            name="PyClone",
            description="PyClone Properties",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.pyclone    


class PC_Scene_Props(PropertyGroup):
    assembly_tabs: EnumProperty(name="Assembly Tabs",
                                items=[('MAIN',"Main","Show the Main Properties"),
                                       ('PROMPTS',"Prompts","Show the Prompts"),
                                       ('OBJECTS',"Objects","Show the Objects"),
                                       ('LOGIC',"Logic","Show the Assembly Logic")],
                                default='MAIN')

    active_library_name: StringProperty(name="Active Library Name",default="")

    @classmethod
    def register(cls):
        bpy.types.Scene.pyclone = PointerProperty(
            name="PyClone",
            description="PyClone Properties",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.pyclone


classes = (
    Combobox_Item,
    Library_Item,
    Library,
    Pointer_Slot,
    Prompt,
    Calculator_Prompt,
    Calculator,
    PC_Object_Props,
    PC_Window_Manager_Props,
    PC_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()