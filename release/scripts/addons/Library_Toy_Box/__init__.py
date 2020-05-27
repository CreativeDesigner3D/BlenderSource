import bpy
from .pc_lib import pc_utils
from . import toy_box_ops
from . import toy_box_save_ops
from . import toy_box_drop_ops
from . import toy_box_props
from . import toy_box_ui
from . import toy_box_utils
from bpy.app.handlers import persistent

bl_info = {
    "name": "Toy Box Library",
    "author": "Andrew Peel",
    "version": (0, 0, 1),
    "blender": (2, 83, 0),
    "location": "Asset Library",
    "description": "This is a library for Blenders standard types and assemblies",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}

@persistent
def load_library_on_file_load(scene=None):
    # pc_utils.register_library(name=toy_box_utils.ASSEMBLY_LIBRARY_NAME,
    #                           activate_id='toy_box.activate',
    #                           drop_id='toy_box.drop',
    #                           icon='FILE_3D')

    pc_utils.register_library(name=toy_box_utils.OBJECT_LIBRARY_NAME,
                              activate_id='toy_box.activate',
                              drop_id='toy_box.drop',
                              icon='OBJECT_DATA')

    pc_utils.register_library(name=toy_box_utils.COLLECTION_LIBRARY_NAME,
                              activate_id='toy_box.activate',
                              drop_id='toy_box.drop',
                              icon='GROUP')

    pc_utils.register_library(name=toy_box_utils.MATERIAL_LIBRARY_NAME,
                              activate_id='toy_box.activate',
                              drop_id='toy_box.drop',
                              icon='MATERIAL')

    pc_utils.register_library(name=toy_box_utils.WORLD_LIBRARY_NAME,
                              activate_id='toy_box.activate',
                              drop_id='toy_box.drop',
                              icon='WORLD')                                                                             

    toy_box_utils.update_props_from_xml_file()

#Standard register/unregister Function for Blender Add-ons
def register():
    toy_box_ops.register()
    toy_box_save_ops.register()
    toy_box_drop_ops.register()
    toy_box_props.register()
    toy_box_ui.register()

    load_library_on_file_load()
    bpy.app.handlers.load_post.append(load_library_on_file_load)

def unregister():
    toy_box_ops.unregister()
    toy_box_save_ops.unregister()
    toy_box_drop_ops.unregister()
    toy_box_props.unregister()
    toy_box_ui.unregister()

    bpy.app.handlers.load_post.remove(load_library_on_file_load)  

    pc_utils.unregister_library(toy_box_utils.OBJECT_LIBRARY_NAME)
    pc_utils.unregister_library(toy_box_utils.COLLECTION_LIBRARY_NAME)
    pc_utils.unregister_library(toy_box_utils.MATERIAL_LIBRARY_NAME)
    pc_utils.unregister_library(toy_box_utils.WORLD_LIBRARY_NAME)

