import bpy
import json
from bpy.ops import object
from bpy.types import Operator
from bpy.props import StringProperty


class ConstraintOperator(Operator):
  bl_label = "Constraint"
  bl_idname = "constraint.constraint"
  bl_options = { "REGISTER", "UNDO" }

  @classmethod
  def poll(cls, context):
    scene = context.scene
    return scene.parent and scene.target and any(item.target for item in scene.constraints)

  def execute(self, context):
    scene = context.scene
    return scene.parent and scene.target

  def execute(self, context):
    previous_mode = context.object.mode
    object.mode_set(mode="POSE")

    scene = context.scene
    parent = scene.objects.get(scene.parent.name)
    target = scene.objects.get(scene.target.name)

    for item in scene.constraints:
      if item.parent and item.target:
        bone_parent = parent.pose.bones[item.parent]
        bone_target = target.pose.bones[item.target]

        bone_parent.constraints.new(type=item.type)
        bone_parent.constraints[-1].target = target
        bone_parent.constraints[-1].subtarget = item.target

    return { "FINISHED" }  


def levenshtein(s1, s2):
  s1 = s1.lower().replace(" ", "_")
  s2 = s2.lower().replace(" ", "_")

  if len(s1) < len(s2):
        return levenshtein(s2, s1)

  if len(s2) == 0:
    return len(s1)

  previous_row = range(len(s2) + 1)
  for i, c1 in enumerate(s1):
    current_row = [i + 1]
    for j, c2 in enumerate(s2):
      insertions = previous_row[j + 1] + 1
      deletions = current_row[j] + 1
      substitutions = previous_row[j] + (c1 != c2)
      current_row.append(min(insertions, deletions, substitutions))
    previous_row = current_row

  return previous_row[-1]


class AutoFillOperator(Operator):
  bl_label = "AutoFill"
  bl_idname = "constraint.auto_fill"

  @classmethod
  def poll(cls, context):
    scene = context.scene
    return scene.parent and scene.target

  def execute(self, context):
    scene = context.scene
    parent = scene.parent
    target = scene.target

    for constraint in scene.constraints:
      if not constraint.target:
        best_match = ""
        best_score = float("inf")

        for target_bone in target.bones:
          score = levenshtein(constraint.parent, target_bone.name)

          if score < best_score:
            best_match = target_bone.name
            best_score = score
            constraint.target = best_match

    return { "FINISHED" }


class ImportOperator(Operator):
  bl_label = "Import"
  bl_idname = "constraint.import"

  filepath: StringProperty(subtype="FILE_PATH")
  filter_glob: StringProperty(default="*.json", options={ "HIDDEN" })

  @classmethod
  def poll(cls, context):
    scene = context.scene
    return scene.parent and scene.target

  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return { "RUNNING_MODAL" }

  def execute(self, context):
    scene = context.scene

    with open(self.filepath, "r") as file:
      data = json.load(file)

    parent_armature = bpy.data.armatures.get(data["parent"])
    target_armature = bpy.data.armatures.get(data["target"])

    if parent_armature and target_armature:
        scene.parent = parent_armature
        scene.target = target_armature

    for imported_constraint in data["constraints"]:
      for constraint in scene.constraints:
          if constraint.parent == imported_constraint["parent"]:
            constraint.target = imported_constraint["target"]
            constraint.type = imported_constraint["type"]
            break

    return { "FINISHED" }


class ExportOperator(Operator):
  bl_label = "Export"
  bl_idname = "constraint.export"

  filepath: StringProperty(subtype="FILE_PATH")
  filename: StringProperty(subtype="FILE_NAME")
  filter_glob: StringProperty(default="*.json", options={ "HIDDEN" })

  @classmethod
  def poll(cls, context):
    scene  = context.scene
    return scene.parent and scene.target and any(item.target for item in scene.constraints)

  def invoke(self, context, event):
    self.filename = "Constraints.json"
    context.window_manager.fileselect_add(self)
    return { "RUNNING_MODAL" }

  def execute(self, context):
    scene = context.scene

    data = {
      "parent": scene.parent.name,
      "target": scene.target.name,
      "constraints":  [
        { 
          "parent": item.parent,
          "target": item.target,
          "type": item.type,
        } for item in scene.constraints if item.target
      ],
    }

    with open(self.filepath, "w") as file:
      json.dump(data, file, indent=2)
    
    return { "FINISHED" }


class ClearOperator(Operator):
  bl_label = "Clear All"
  bl_idname = "constraint.clear"

  @classmethod
  def poll(cls, context):
    scene = context.scene
    return scene.parent or scene.target

  def execute(self, context):
    scene = context.scene
    scene.parent = None
    scene.target = None
    scene.constraints.clear()
    scene.constraints_index = 0

    return { "FINISHED" }


class ClearListOperator(Operator):
  bl_label = "Clear List"
  bl_idname = "constraint.clear_list"

  @classmethod
  def poll(cls, context):
    scene = context.scene
    return scene.parent and scene.target and any(item.target for item in scene.constraints)

  def execute(self, context):
    scene = context.scene

    for item in scene.constraints:
      item.target = ""

    return { "FINISHED" }
