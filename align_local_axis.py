#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/
#  or write to the Free Software Foundation, Inc., 51 Franklin Street,
#  Fifth Floor, Boston, MA 02110-1301, USA.
#
#  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Align local axis",
    "author": "Eleanor Howick (elfnor.com)",
    "version": (0, 2),
    "blender": (2,80,61),
    "location": "3D View > Object > Transform > Align local axis",
    "description": "Operator to set selected object's local axis to align with active object, custom transform or 3D cursor",
    "warning": "",
    "category": "Object",
}

import bpy

from mathutils import Matrix


# ------------------------------------------------------


def align_local(obj, euler_rot):
    """
    rotate the local axis of obj to align in the direction given by euler_rot
    the object's vertices and origin should remain in the same location in world space
    any scale on obj will be applied
    """
    # separate the object's world matrix into a translation matrix and a combined scale rotation matrix
    mw = obj.matrix_world
    mwsr = mw.to_3x3().to_4x4()
    mwl = Matrix.Translation(mw.to_translation())   
    # construct a matrix for the target local axis
    mrot = euler_rot.to_matrix().to_4x4() 
    # apply the transforms to the data and to object
    obj.matrix_world = mwl @ mrot   
    obj.data.transform(mrot.transposed() @ mwsr)
    
# ---------------------------------------------------------


class VIEW3D_OT_align_local(bpy.types.Operator):
    bl_idname = "object.align_local"
    bl_label = "align local"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    def execute(self, context):
        if len(context.selected_objects) > 1:
            src = context.active_object
            euler_rot = src.rotation_euler
            for obj in context.selected_objects:
                if obj != src:
                    align_local(obj, euler_rot)           
        else:
            obj = context.active_object
            trans_slot = context.scene.transform_orientation_slots[0]
            co = trans_slot.custom_orientation
            if co:
                euler_rot = co.matrix.to_euler()                
            else:
                euler_rot = context.scene.cursor.rotation_euler
                    
            align_local(obj, euler_rot)     

        return {"FINISHED"}


def add_to_menu(self, context):
    self.layout.separator()
    self.layout.operator(VIEW3D_OT_align_local.bl_idname, icon="PLUGIN")
    self.layout.separator()
    return


def register():
    bpy.utils.register_class(VIEW3D_OT_align_local)
    bpy.types.VIEW3D_MT_transform_object.append(add_to_menu)
    return


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_align_local)
    bpy.types.VIEW3D_MT_transform_object.remove(add_to_menu)   
    return


if __name__ == "__main__":
    register()
    
