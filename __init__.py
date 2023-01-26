import importlib
from .src import ui
from .src import operator
from bpy.types import (Armature, Scene, Operator)
from bpy.utils import (register_class, unregister_class)
from bpy.props import (PointerProperty, IntProperty, CollectionProperty)


bl_info = {
  "name": "Constraint",
  "description": "Quickly constraint bones between armatures",
  "author": "KiraCoding",
  "version": (0, 1, 0),
  "blender": (3, 4, 0),
  "location": "View3D > Tools > Constraint",
  "category": "Tools",
}


def update_constraints(self, context):
    scene = context.scene
    scene.constraints.clear()

    if scene.parent and scene.target:
        for bone in scene.parent.bones:
            item = scene.constraints.add()
            item.parent = bone.name


class HotReloadOperator(Operator):
  bl_label = "HotReload"
  bl_idname = "constraint.hot_reload"

  def execute(self, context):
    unregister()
    register()

    self.report({ "INFO" }, "Addon hot reloaded")

    return { "FINISHED" }


classes = (
  operator. AutoFillOperator,
  operator.ConstraintOperator,
  operator.ImportOperator,
  operator.ExportOperator,
  operator.ClearOperator,
  operator.ClearListOperator,
  HotReloadOperator,
  ui.ConstraintListItem,
  ui.UL_ConstraintList,
  ui.PT_ConstraintPanel,
  ui.PT_AboutPanel,
)


def register():
  for cls in classes:
    register_class(cls)

  Scene.parent = PointerProperty(name="Parent Armature", type=Armature, update=update_constraints)
  Scene.target = PointerProperty(name="Target Armature", type=Armature, update=update_constraints)
  Scene.constraints = CollectionProperty(type=ui.ConstraintListItem)
  Scene.constraints_index = IntProperty()


def unregister():
  for cls in reversed(classes):
    unregister_class(cls)

  del Scene.parent
  del Scene.target
  del Scene.constraints
  del Scene.constraints_index


if __name__ == "__main__":
  register()
