# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Any Rig to Rigify",
    "author": "demania",
    "description": "Convert arbitrary armatures to Rigify with Blender 4.x/5.x compatibility.",
    "blender": (4, 0, 0),
    "version": (0, 1, 0),
    "location": "View3D",
    "warning": "",
    "category": "Object",
}

from . import ui
from .ui import (
    # CustomPanel,
    ObjectOperator,
    MappingSaveOperator,
    MappingImportOperator,
    MappingDeleteOperator,
    MappingRenameOperator,
    GENERATE_panel,
    MAPPING_panel,
    UPPER_BODY_panel,
    SPINES_panel,
    ARMS_panel,
    FINGERS_panel,
    LEGS_panel,
)
import bpy

# ===========================================================


classes = [
    # CustomPanel,
    ObjectOperator,
    MappingSaveOperator,
    MappingImportOperator,
    MappingDeleteOperator,
    MappingRenameOperator,
    GENERATE_panel,
    MAPPING_panel,
    UPPER_BODY_panel,
    SPINES_panel,
    ARMS_panel,
    FINGERS_panel,
    LEGS_panel,
]


def register():
    for (prop_name, prop_value) in ui.PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for (prop_name, _) in ui.PROPS:
        delattr(bpy.types.Scene, prop_name)

    for c in classes:
        bpy.utils.unregister_class(c)
