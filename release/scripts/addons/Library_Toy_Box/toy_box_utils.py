import bpy
import os
import xml.etree.ElementTree as ET
from .pc_lib import pc_pointer_utils, pc_utils

DEFAULT_LIBRARY_ROOT_FOLDER = os.path.join(bpy.utils.user_resource('SCRIPTS'), "PyClone")
ASSEMBLY_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"assemblies")
OBJECT_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"objects")
COLLECTION_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"collections")
MATERIAL_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"materials")
WORLD_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"worlds")
LIBRARY_PATH_FILENAME = "toy_box_library_paths.xml"
ASSEMBLY_LIBRARY_NAME = "Assembly Library"
OBJECT_LIBRARY_NAME = "Object Library"
COLLECTION_LIBRARY_NAME = "Collection Library"
MATERIAL_LIBRARY_NAME = "Material Library"
WORLD_LIBRARY_NAME = "World Library"

def get_window_manager_props(window_manager):
    return window_manager.toy_box_library

def get_scene_props(scene):
    return scene.toy_box_library

def get_library_path_file():
    """ Returns the path to the file that stores all of the library paths.
    """
    if not os.path.exists(DEFAULT_LIBRARY_ROOT_FOLDER):
        os.makedirs(DEFAULT_LIBRARY_ROOT_FOLDER)
        
    return os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,LIBRARY_PATH_FILENAME)

def get_active_library_icon():
    pyclone = pc_utils.get_scene_props(bpy.context.scene)
    if pyclone.active_library_name == ASSEMBLY_LIBRARY_NAME:
        return 'FILE_3D'
    if pyclone.active_library_name == OBJECT_LIBRARY_NAME:
        return 'OBJECT_DATA'
    if pyclone.active_library_name == COLLECTION_LIBRARY_NAME:
        return 'GROUP'
    if pyclone.active_library_name == MATERIAL_LIBRARY_NAME:
        return 'MATERIAL'
    if pyclone.active_library_name == WORLD_LIBRARY_NAME:
        return 'WORLD'                                

def get_thumbnail_file_path():
    return os.path.join(os.path.dirname(__file__),"thumbnail.blend")

def get_filebrowser_path(context):
    return context.space_data.params.directory

def get_active_category(folders):
    """ Gets the active folder for the active library
    """
    pyclone = pc_utils.get_scene_props(bpy.context.scene)
    scene_props = get_scene_props(bpy.context.scene)
    if pyclone.active_library_name == ASSEMBLY_LIBRARY_NAME:
        if scene_props.active_assembly_category in folders:
            for folder in folders:
                if scene_props.active_assembly_category == folder:
                    return folder
    if pyclone.active_library_name == OBJECT_LIBRARY_NAME:
        if scene_props.active_object_category in folders:
            for folder in folders:
                if scene_props.active_object_category == folder:
                    return folder
    if pyclone.active_library_name == COLLECTION_LIBRARY_NAME:
        if scene_props.active_collection_category in folders:
            for folder in folders:
                if scene_props.active_collection_category == folder:
                    return folder
    if pyclone.active_library_name == MATERIAL_LIBRARY_NAME:
        if scene_props.active_material_category in folders:
            for folder in folders:
                if scene_props.active_material_category == folder:
                    return folder                 
    if pyclone.active_library_name == WORLD_LIBRARY_NAME:
        if scene_props.active_world_category in folders:
            for folder in folders:
                if scene_props.active_world_category == folder:
                    return folder   
    if len(folders) > 0:
        return folders[0]

def get_active_categories():
    """ Gets a list of all of the categories
    """
    path = get_active_library_path()
    folders = []
    if path and os.path.exists(path):
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)    
    return folders

def get_active_library_path():
    pyclone = pc_utils.get_scene_props(bpy.context.scene)
    if pyclone.active_library_name == ASSEMBLY_LIBRARY_NAME:
        return get_assembly_library_path()     
    if pyclone.active_library_name == OBJECT_LIBRARY_NAME:
        return get_object_library_path()
    if pyclone.active_library_name == COLLECTION_LIBRARY_NAME:
        return get_collection_library_path()
    if pyclone.active_library_name == MATERIAL_LIBRARY_NAME:
        return get_material_library_path()
    if pyclone.active_library_name == WORLD_LIBRARY_NAME:
        return get_world_library_path()

def get_assembly_library_path():
    wm_props = get_window_manager_props(bpy.context.window_manager)
    if os.path.exists(wm_props.assembly_library_path):
        return wm_props.assembly_library_path
    else:
        return ASSEMBLY_FOLDER

def get_object_library_path():
    wm_props = get_window_manager_props(bpy.context.window_manager)
    if os.path.exists(wm_props.object_library_path):
        return wm_props.object_library_path
    else:
        return OBJECT_FOLDER

def get_collection_library_path():
    wm_props = get_window_manager_props(bpy.context.window_manager)
    if os.path.exists(wm_props.collection_library_path):
        return wm_props.collection_library_path
    else:
        return COLLECTION_FOLDER

def get_material_library_path():
    wm_props = get_window_manager_props(bpy.context.window_manager)
    if os.path.exists(wm_props.material_library_path):
        return wm_props.material_library_path
    else:
        return MATERIAL_FOLDER                

def get_world_library_path():
    wm_props = get_window_manager_props(bpy.context.window_manager)
    if os.path.exists(wm_props.world_library_path):
        return wm_props.world_library_path
    else:
        return WORLD_FOLDER   

def write_xml_file():
    '''
    This writes the XML file from the current props. 
    This file gets written everytime a property changes.
    '''
    xml = pc_pointer_utils.Pointer_XML()
    root = xml.create_tree()
    paths = xml.add_element(root,'LibraryPaths')

    wm_props = get_window_manager_props(bpy.context.window_manager)
    
    if os.path.exists(wm_props.object_library_path):
        xml.add_element_with_text(paths,'Objects',wm_props.object_library_path)
    else:
        xml.add_element_with_text(paths,'Objects',"")
        
    if os.path.exists(wm_props.material_library_path):
        xml.add_element_with_text(paths,'Materials',wm_props.material_library_path)
    else:
        xml.add_element_with_text(paths,'Materials',"")
        
    if os.path.exists(wm_props.collection_library_path):
        xml.add_element_with_text(paths,'Collections',wm_props.collection_library_path)
    else:
        xml.add_element_with_text(paths,'Collections',"")
    
    if os.path.exists(wm_props.world_library_path):
        xml.add_element_with_text(paths,'Worlds',wm_props.world_library_path)
    else:
        xml.add_element_with_text(paths,'Worlds',"")

    if os.path.exists(wm_props.assembly_library_path):
        xml.add_element_with_text(paths,'Assemblies',wm_props.assembly_library_path)
    else:
        xml.add_element_with_text(paths,'Assemblies',"")

    xml.write(get_library_path_file())

def update_props_from_xml_file():
    '''
    This gets read on startup and sets the window manager props
    '''
    wm_props = get_window_manager_props(bpy.context.window_manager)

    if os.path.exists(get_library_path_file()):
        tree = ET.parse(get_library_path_file())
        root = tree.getroot()
        for elm in root.findall("LibraryPaths"):
            items = elm.getchildren()
            for item in items:
                
                if item.tag == 'Objects':
                    if os.path.exists(str(item.text)):
                        wm_props.object_library_path = item.text
                    else:
                        wm_props.object_library_path = ""
                        
                if item.tag == 'Materials':
                    if os.path.exists(str(item.text)):
                        wm_props.material_library_path = item.text
                    else:
                        wm_props.material_library_path = ""
                        
                if item.tag == 'Collections':
                    if os.path.exists(str(item.text)):
                        wm_props.collection_library_path = item.text
                    else:
                        wm_props.collection_library_path = "" 

                if item.tag == 'Worlds':
                    if os.path.exists(str(item.text)):
                        wm_props.world_library_path = item.text
                    else:
                        wm_props.world_library_path = "" 

                if item.tag == 'Assemblies':
                    if os.path.exists(str(item.text)):
                        wm_props.assembly_library_path = item.text
                    else:
                        wm_props.assembly_library_path = "" 
