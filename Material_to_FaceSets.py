
import maya.cmds as cmds
import maya.api.OpenMaya as om
from collections import defaultdict


def convert_materials_to_faces():
    """Convert selected meshes' material assignments to face assignments."""

    selection = cmds.ls(selection=True, long=True, objectsOnly=True) or []

    if not selection:
        cmds.warning("Select one or more meshes.")
        return

    # Collect mesh shapes, including those inside selected groups.
    meshes = set()

    for obj in selection:
        if cmds.nodeType(obj) == "mesh":
            meshes.add(obj)

        descendants = cmds.listRelatives(
            obj, allDescendents=True, type="mesh",
            fullPath=True
        ) or []

        meshes.update(descendants)

        shapes = cmds.listRelatives(
            obj, shapes=True, type="mesh",
            fullPath=True
        ) or []

        meshes.update(shapes)

    meshes = [
        mesh for mesh in sorted(meshes)
        if not cmds.getAttr(mesh + ".intermediateObject")
    ]

    if not meshes:
        cmds.warning("No polygon meshes found.")
        return

    converted = 0

    cmds.undoInfo(openChunk=True)

    try:
        for shape in meshes:
            try:
                # Skip instanced meshes.
                parents = cmds.listRelatives(
                    shape, allParents=True, fullPath=True
                ) or []

                if len(parents) > 1:
                    cmds.warning("Skipping instanced mesh: " + shape)
                    continue

                transform = parents[0] if parents else shape

                # Get effective material assignment for every face.
                sel = om.MSelectionList()
                sel.add(shape)
                dag = sel.getDagPath(0)

                mesh_fn = om.MFnMesh(dag)

                shading_groups, shader_indices = (
                    mesh_fn.getConnectedShaders(dag.instanceNumber())
                )

                if not shading_groups:
                    continue

                assignments = defaultdict(list)

                for face_id, shader_id in enumerate(shader_indices):
                    if shader_id < 0:
                        continue

                    sg = om.MFnDependencyNode(
                        shading_groups[shader_id]
                    ).name()

                    assignments[sg].append(face_id)

                if not assignments:
                    continue

                # Remove whole-object memberships, which can prevent
                # Maya's Alembic exporter from writing Face Sets.
                for sg in assignments:
                    members = cmds.sets(sg, query=True) or []

                    for member in members:
                        if "." in member:
                            continue

                        resolved = cmds.ls(member, long=True) or []

                        if shape in resolved or transform in resolved:
                            cmds.sets(member, remove=sg)

                # Reassign each material directly to its original faces.
                for sg, face_ids in assignments.items():
                    face_ids.sort()

                    ranges = []
                    start = previous = face_ids[0]

                    for face_id in face_ids[1:]:
                        if face_id == previous + 1:
                            previous = face_id
                            continue

                        ranges.append((start, previous))
                        start = previous = face_id

                    ranges.append((start, previous))

                    components = []

                    for start, end in ranges:
                        if start == end:
                            components.append(
                                "{}.f[{}]".format(shape, start)
                            )
                        else:
                            components.append(
                                "{}.f[{}:{}]".format(shape, start, end)
                            )

                    # Process in batches for meshes with many face ranges.
                    for i in range(0, len(components), 200):
                        cmds.sets(
                            *components[i:i + 200],
                            edit=True,
                            forceElement=sg
                        )

                converted += 1
                print(
                    "[Alembic] Converted: {} ({} materials)".format(
                        transform, len(assignments)
                    )
                )

            except Exception as exc:
                cmds.warning(
                    "Failed to convert {}: {}".format(shape, exc)
                )

    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.select(selection, replace=True)

    print(
        "[Alembic] Done: {} / {} meshes converted.".format(
            converted, len(meshes)
        )
    )


convert_materials_to_faces()
