bl_info = {
    "name": "PyClone",
    "author": "Andrew Peel",
    "version": (0, 0, 1),
    "blender": (2, 83, 0),
    "location": "3D Viewport Sidebar and File Browser",
    "description": "This is an asset management and development engine",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Management",
}

import bpy
from bpy.app.handlers import persistent
from .ui import pc_filebrowser_ui
from .ui import pc_lists
from .ui import pc_view3d_ui_menu
from .ui import pc_view3d_ui_sidebar_object
from .ui import pc_view3d_ui_sidebar_assemblies
from .ops import pc_assembly
from .ops import pc_driver
from .ops import pc_prompts
from .ops import pc_library
from .ops import pc_material
from .ops import pc_object
from .ops import pc_general
from .ops import pc_window_manager
from . import pyclone_props

@persistent
def load_driver_functions(scene):
    """ Load Default Drivers
    """
    import inspect
    from . import pyclone_driver_functions
    for name, obj in inspect.getmembers(pyclone_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj

def register():
    pc_filebrowser_ui.register()
    pc_lists.register()
    pc_view3d_ui_menu.register()
    pc_view3d_ui_sidebar_object.register()
    pc_view3d_ui_sidebar_assemblies.register()
    pc_assembly.register()
    pc_driver.register()
    pc_prompts.register()
    pc_library.register()
    pc_material.register()
    pc_object.register()
    pc_general.register()
    pc_window_manager.register()
    pyclone_props.register()
    bpy.app.handlers.load_post.append(load_driver_functions)

def unregister():
    pc_filebrowser_ui.unregister()
    pc_lists.unregister()
    pc_view3d_ui_menu.unregister()
    pc_view3d_ui_sidebar_object.unregister()
    pc_view3d_ui_sidebar_assemblies.unregister()
    pc_assembly.unregister()
    pc_driver.unregister()
    pc_prompts.unregister()
    pc_library.unregister()
    pc_material.unregister()
    pc_object.unregister()
    pc_general.unregister()
    pc_window_manager.unregister()
    pyclone_props.unregister()
    bpy.app.handlers.load_post.append(load_driver_functions)