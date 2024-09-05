# Duplicate selected camera into a new window (tear off copy like)
# Hide UI / Manipulator / Enable resolution gate + mask

import maya.cmds as cmds

def create_custom_camera_window():

    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.error("Please select a camera.")
        return
    
    camera_shape = None
    for obj in selected_objects:
        shapes = cmds.listRelatives(obj, shapes=True, type="camera")
        if shapes:
            camera_shape = shapes[0]
            break
    
    if not camera_shape:
        cmds.error("Selected object is not a camera.")
        return

    camera_transform = cmds.listRelatives(camera_shape, parent=True)[0]

    window_name = "CustomCameraWindow"
    
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    window = cmds.window(window_name, title="Camera View", widthHeight=(800, 600))
    layout = cmds.paneLayout()
    
    model_panel = cmds.modelPanel()
    cmds.modelPanel(model_panel, edit=True, cam=camera_shape)
    
    cmds.camera(camera_shape, edit=True, displayFilmGate=False, displayResolution=True, overscan=1.3)
    
    cmds.modelEditor(model_panel, edit=True, displayAppearance='smoothShaded')
    cmds.modelEditor(model_panel, edit=True, displayTextures=True)
    
    cmds.showWindow(window)

    # Hide everything except polygons, nParticles, nCloths, particle instancers, dynamics, subdivs
    cmds.modelEditor(model_panel, edit=True, allObjects=False)
    cmds.modelEditor(model_panel, edit=True, polymeshes=True)
    cmds.modelEditor(model_panel, edit=True, nParticles=True)
    cmds.modelEditor(model_panel, edit=True, nCloths=True)
    cmds.modelEditor(model_panel, edit=True, particleInstancers=True)
    cmds.modelEditor(model_panel, edit=True, dynamics=True)
    cmds.modelEditor(model_panel, edit=True, subdivSurfaces=True)
    
    # Hide manipulator, grid, and selection highlighting
    cmds.modelEditor(model_panel, edit=True, manipulators=False)
    cmds.modelEditor(model_panel, edit=True, grid=False)
    cmds.modelEditor(model_panel, edit=True, selectionHiliteDisplay=False)

create_custom_camera_window()
