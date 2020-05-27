import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os
from ..pc_lib import pc_types, pc_utils
from .. import pyclone_utils 

class pc_general_OT_change_file_browser_path(bpy.types.Operator):
    bl_idname = "pc_general.change_file_browser_path"
    bl_label = "Change File Browser Path"
    bl_description = "Changes the file browser path"
    bl_options = {'UNDO'}

    file_path: StringProperty(name='File Path')

    def execute(self, context):
        pyclone_utils.update_file_browser_path(context,self.file_path)
        return {'FINISHED'}

classes = (
    pc_general_OT_change_file_browser_path,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()