import bpy

from pathlib import Path

def get_mapping_folder():
    mapping_folder = Path(__file__).resolve().parent / "mapping_templates"
    mapping_folder.mkdir(parents=True, exist_ok=True)
    return mapping_folder.as_posix()
