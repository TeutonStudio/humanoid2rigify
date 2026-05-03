import bpy

from __methoden__ import get_mapping_folder


def my_settings_callback(scene, context):
    # get to mapping_templates folder or create if there isn't one
    mapping_folder = get_mapping_folder()

    json_presets = []
    files = sorted(os.listdir(mapping_folder))
    # get only json files
    for file in files:
        _, file_extension = os.path.splitext(file)
        if file_extension == ".json":
            json_presets.append(file)

    items = []
    for i in json_presets:
        s = (i, i, "")
        items.append(s)

    return items
