bl_info = {
    "name": "PyClone",
    "author": "Andrew Peel",
    "version": (0, 5, 3),
    "blender": (2, 93, 0),
    "location": "3D Viewport Sidebar and File Browser",
    "description": "This is an asset management and development engine",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Management",
}

import bpy
from bpy.app.handlers import persistent
import os
import sys
import time
PATH = os.path.join(os.path.dirname(__file__),"python_libs")
sys.path.append(PATH)
from .ui import pc_filebrowser_ui
from .ui import pc_lists
from .ui import pc_view3d_ui_menu
from .ui import pc_view3d_ui_sidebar_object
from .ui import pc_text_ui_sidebar_library
from .ui import pc_view3d_ui_sidebar_assemblies
from .ui import pc_view3d_ui_layout_view
from .ops import pc_assembly
from .ops import pc_driver
from .ops import pc_prompts
from .ops import pc_library
from .ops import pc_material
from .ops import pc_object
from .ops import pc_general
from .ops import pc_window_manager
from . import pyclone_props
from . import pyclone_utils
from . import addon_updater_ops

@persistent
def load_driver_functions(scene):
    """ Load Default Drivers
    """
    import inspect
    from . import pyclone_driver_functions
    for name, obj in inspect.getmembers(pyclone_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj
    start_time = time.time()
    for obj in bpy.data.objects:
        if obj.type in {'EMPTY','MESH'}:
            drivers = pyclone_utils.get_drivers(obj)
            for DR in drivers:  
                DR.driver.expression = DR.driver.expression
    print("Reloading Drivers: --- %s seconds ---" % (time.time() - start_time))

addon_keymaps = []

def register():
    addon_updater_ops.register(bl_info)
    pc_filebrowser_ui.register()
    pc_lists.register()
    pc_view3d_ui_menu.register()
    pc_text_ui_sidebar_library.register()
    pc_view3d_ui_sidebar_object.register()
    pc_view3d_ui_sidebar_assemblies.register()
    pc_view3d_ui_layout_view.register()
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
    pyclone_utils.addon_version = bl_info['version']

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View',space_type = 'VIEW_3D')
        kmi = km.keymap_items.new('wm.drag_and_drop', type = 'P', value='PRESS',shift=False)
        addon_keymaps.append((km,kmi))
        
def unregister():
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    pc_filebrowser_ui.unregister()
    pc_lists.unregister()
    pc_view3d_ui_menu.unregister()
    pc_text_ui_sidebar_library.unregister()
    pc_view3d_ui_sidebar_object.unregister()
    pc_view3d_ui_sidebar_assemblies.unregister()
    pc_view3d_ui_layout_view.unregister()
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