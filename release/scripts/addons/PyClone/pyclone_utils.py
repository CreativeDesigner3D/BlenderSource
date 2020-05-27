

def get_wm_props(window_manager):
    return window_manager.pyclone

def get_scene_props(scene):
    return scene.pyclone    

def get_object_props(obj):
    return obj.pyclone    

def get_drivers(obj):
    drivers = []
    if obj.animation_data:
        for driver in obj.animation_data.drivers:
            drivers.append(driver)

    if obj.data and obj.data.animation_data:
        for driver in obj.data.animation_data.drivers:
            drivers.append(driver)

    return drivers            

def update_file_browser_path(context,path):
    for area in context.screen.areas:
        if area.type == 'FILE_BROWSER':
            for space in area.spaces:
                if space.type == 'FILE_BROWSER':
                    params = space.params
                    params.directory = str.encode(path)
                    if not context.screen.show_fullscreen:
                        params.use_filter = True
                        params.display_type = 'THUMBNAIL'
                        params.use_filter_movie = False
                        params.use_filter_script = False
                        params.use_filter_sound = False
                        params.use_filter_text = False
                        params.use_filter_font = False
                        params.use_filter_folder = False
                        params.use_filter_blender = False
                        params.use_filter_image = True    