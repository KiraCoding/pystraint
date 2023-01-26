import bpy
from bpy.props import (StringProperty, EnumProperty)
from bpy.types import (Panel, UIList, PropertyGroup, BoolProperty)


class ConstraintListItem(PropertyGroup):
  parent: StringProperty(name="Parent Bone")
  target: StringProperty(name="Target Bone")
  type: EnumProperty(
    name="Constraint Type",
    items=[
      ("COPY_TRANSFORMS", "Transforms", "Copy the transforms from the target bone"),
      ("COPY_LOCATION", "Location", "Copy the location from the target bone"),
      ("COPY_ROTATION", "Rotation", "Copy the rotation from the target bone"),
      ("COPY_SCALE", "Scale", "Copy the scale from the target bone"),
    ],
    default="COPY_TRANSFORMS"
  )


class UL_ConstraintList(UIList):
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
    target = context.scene.target

    layout.label(text=item.parent)
    layout.prop_search(item, "target", target, "bones", text="")
    layout.prop(item, "type", text="")


class PT_ConstraintPanel(Panel):
  bl_region_type = "UI"
  bl_label = "Constraint"
  bl_space_type = "VIEW_3D"
  bl_category = "Constraint"

  def draw(self, context):
    scene = context.scene
    layout = self.layout

    layout.prop_search(scene, "parent", bpy.data, "armatures", text="Parent")
    layout.prop_search(scene, "target", bpy.data, "armatures", text="Target")

    layout.separator()

    layout.template_list("UL_ConstraintList", "Constraint List", scene, "constraints", scene, "constraints_index")

    layout.separator()

    column = layout.column(align=True)

    row = column.row(align=True)
    row.operator("constraint.auto_fill", text="Auto Fill", icon="PASTEFLIPDOWN")
    row.operator("constraint.clear_list", text="", icon="TRASH")

    row = column.row(align=True)
    row.operator("constraint.import", text="Import", icon="IMPORT")
    row.operator("constraint.export", text="Export", icon="EXPORT")
    row.operator("constraint.clear", text="", icon="X")

    row = layout.row()
    row.operator("constraint.constraint", text="Constraint", icon="CONSTRAINT_BONE")
    row.scale_y = 1.5


class PT_AboutPanel(Panel):
  bl_label = "About"
  bl_region_type = "UI"
  bl_space_type = "VIEW_3D"
  bl_category = "Constraint"

  def draw(self, context):
    layout = self.layout

    layout.operator("constraint.hot_reload", text="Hot Reload", icon="FILE_REFRESH")
