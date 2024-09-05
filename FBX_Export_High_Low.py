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

    # Select all geometry inside the group
    cmds.select(group, replace=True)
    geometry = cmds.listRelatives(allDescendents=True, type="mesh", fullPath=True)
    cmds.select(geometry, replace=True)

    # Export low version (without smooth mesh)
    low_file_path = os.path.join(export_dir, f"{export_name}_low.fbx")
    mel.eval(f'FBXExport -f "{low_file_path}" -s')

    # Add smooth mesh to all selected geometry
    smooth_nodes = []
    for geo in geometry:
        smooth_node = cmds.polySmooth(geo, divisions=1)[0]
        smooth_nodes.append(smooth_node)

    # Export high version (with smooth mesh)
    high_file_path = os.path.join(export_dir, f"{export_name}_high.fbx")
    mel.eval(f'FBXExport -f "{high_file_path}" -s')

    # Remove smooth mesh nodes
    cmds.delete(smooth_nodes)

    # Reselect the original group
    cmds.select(group, replace=True)

print("High/Low Export complete.")
