import maya.cmds as cmds
import maya.mel as mel
import os

project_dir = cmds.workspace(query=True, rootDirectory=True)
export_dir = os.path.join(project_dir, "export/")

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

selected_groups = cmds.ls(selection=True, type="transform")

for group in selected_groups:
    # I'm used to rename all groups with _GRP suffix, I don't wanna see it in export
    export_name = group.replace("_GRP", "")

    cmds.select(group, hierarchy=True)

    # Export low version (without smooth mesh)
    low_file_path = os.path.join(export_dir, f"{export_name}_low.fbx")
    mel.eval(f'FBXExport -f "{low_file_path}" -s')

    mesh_objects = cmds.listRelatives(group, allDescendents=True, type="mesh", fullPath=True)
    
    # Add smooth mesh to all mesh objects
    smooth_nodes = []
    for mesh in mesh_objects:
        smooth_node = cmds.polySmooth(mesh, divisions=1)[0]
        smooth_nodes.append(smooth_node)

    # Export high version (with smooth mesh)
    high_file_path = os.path.join(export_dir, f"{export_name}_high.fbx")
    mel.eval(f'FBXExport -f "{high_file_path}" -s')

    cmds.delete(smooth_nodes)
    cmds.select(group, replace=True)

print("High/Low Export complete.")
