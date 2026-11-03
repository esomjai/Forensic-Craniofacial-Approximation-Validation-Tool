```python
# =============================================================================
# Ryu et al. 2024 Method – FINAL with Folders (Fixed API)
# =============================================================================
# Fixed: Subject hierarchy GetSceneItemID() instead of GetSceneItem()
# Fixed: Undefined variables in _execute_step4 (eyeball_node, hard_tissue_node)
# Fixed: Function definition order in _execute_step4
# Fixed: Proper nested folder organization for all generated nodes
# =============================================================================

import slicer
import qt
import logging
import numpy as np
import os
import urllib.request
import vtk

try:
    import gdown
except ImportError:
    slicer.util.pip_install('gdown')
    import gdown

# -----------------------------------------------------------------------------
# Subject hierarchy folder management (FIXED with nested folders)
# -----------------------------------------------------------------------------
sh = None

def get_or_create_folder(folder_path):
    """
    Get or create a nested folder structure in subject hierarchy.
    folder_path can be a single name or a list of names for nested folders.
    Example: get_or_create_folder(["Reference Planes", "Marginal Planes"])
    """
    global sh
    if sh is None:
        sh = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    
    scene_root = sh.GetSceneItemID()
    current_parent = scene_root
    
    if isinstance(folder_path, str):
        folder_path = [folder_path]
    
    for folder_name in folder_path:
        # Look for existing folder under current parent
        folder_id = sh.GetItemChildWithName(current_parent, folder_name)
        if folder_id == 0:
            # Create new folder
            folder_id = sh.CreateFolderItem(current_parent, folder_name)
            # Set folder color and properties (optional)
            if folder_id:
                sh.SetItemAttribute(folder_id, "Color", "0.7,0.7,0.7")
        current_parent = folder_id
    
    return current_parent

def add_node_to_folder(node, folder_path):
    """Add a node to a nested folder structure."""
    global sh
    if sh is None:
        sh = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    
    if not node:
        return
    
    # Get the folder ID (creates if needed)
    folder_id = get_or_create_folder(folder_path)
    
    # Find the subject hierarchy item for this node
    sh_item_id = sh.GetItemByDataNode(node)
    
    if sh_item_id == 0:
        # Node doesn't have a hierarchy item yet - create one
        sh_item_id = sh.CreateItem(folder_id, node)
    else:
        # Node already has an item - reparent it
        current_parent = sh.GetItemParent(sh_item_id)
        if current_parent != folder_id:
            sh.SetItemParent(sh_item_id, folder_id)
    
    return sh_item_id

# -----------------------------------------------------------------------------
# Helper to set node colour reliably
# -----------------------------------------------------------------------------
def set_node_color(node, color_rgb):
    dn = node.GetDisplayNode()
    if not dn:
        node.CreateDefaultDisplayNodes()
        dn = node.GetDisplayNode()
    if dn:
        dn.SetColor(color_rgb[0], color_rgb[1], color_rgb[2])
        dn.SetSelectedColor(color_rgb[0], color_rgb[1], color_rgb[2])

# -----------------------------------------------------------------------------
# Standalone mid‑au calculation function
# -----------------------------------------------------------------------------
def update_mid_auriculare_midpoint():
    fiducials_node_name = "Ryu_hard_tissue"
    try:
        landmarks_node = slicer.util.getNode(fiducials_node_name)
    except slicer.util.MRMLNodeNotFoundException:
        slicer.util.errorDisplay(f"Landmark node '{fiducials_node_name}' not found.")
        return

    auL_pos = auR_pos = None
    for i in range(landmarks_node.GetNumberOfControlPoints()):
        label = landmarks_node.GetNthControlPointLabel(i)
        pos = np.zeros(3)
        landmarks_node.GetNthControlPointPosition(i, pos)
        if label == "auL":
            auL_pos = pos
        elif label == "auR":
            auR_pos = pos

    if auL_pos is None or auR_pos is None:
        slicer.util.errorDisplay("Could not find 'auL' and/or 'auR'.")
        return

    mid_pos = (auL_pos + auR_pos) / 2.0
    mid_idx = -1
    for i in range(landmarks_node.GetNumberOfControlPoints()):
        if landmarks_node.GetNthControlPointLabel(i) == "mid_au":
            mid_idx = i
            break
    if mid_idx != -1:
        landmarks_node.SetNthControlPointPosition(mid_idx, mid_pos)
    else:
        landmarks_node.AddControlPoint(mid_pos, "mid_au")
    slicer.util.infoDisplay(f"mid_au updated: {mid_pos}")

# -----------------------------------------------------------------------------
# Re‑orient slice views
# -----------------------------------------------------------------------------
def reorient_slice_views():
    def get_node(name, cls="vtkMRMLMarkupsPlaneNode"):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if not node:
            raise ValueError(f"Required plane '{name}' not found.")
        if not node.IsA(cls):
            raise ValueError(f"Node '{name}' is not of type {cls}.")
        return node

    try:
        midsagittal_plane = get_node("Median Sagittal Plane")
        axis_x = np.array(midsagittal_plane.GetNormal())
        coronal_plane = get_node("Coronal Plane")
        axis_y = np.array(coronal_plane.GetNormal())
        orbital_plane = get_node("Orbitale Transverse Plane")
        axis_z = np.array(orbital_plane.GetNormal())

        axis_x /= np.linalg.norm(axis_x)
        axis_y /= np.linalg.norm(axis_y)
        axis_z = np.cross(axis_x, axis_y)
        axis_z /= np.linalg.norm(axis_z)
        axis_y = np.cross(axis_z, axis_x)
        axis_y /= np.linalg.norm(axis_y)

        red = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
        yellow = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
        green = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')

        # Axial (red)
        mat = np.identity(4)
        mat[0, 0:3] = axis_x
        mat[1, 0:3] = axis_y
        mat[2, 0:3] = axis_z
        red.GetSliceToRAS().DeepCopy(slicer.util.vtkMatrixFromArray(mat.T))
        red.UpdateMatrices()

        # Sagittal (yellow)
        mat = np.identity(4)
        mat[0, 0:3] = axis_y
        mat[1, 0:3] = axis_z
        mat[2, 0:3] = axis_x
        yellow.GetSliceToRAS().DeepCopy(slicer.util.vtkMatrixFromArray(mat.T))
        yellow.UpdateMatrices()

        # Coronal (green)
        mat = np.identity(4)
        mat[0, 0:3] = axis_x
        mat[1, 0:3] = axis_z
        mat[2, 0:3] = axis_y
        green.GetSliceToRAS().DeepCopy(slicer.util.vtkMatrixFromArray(mat.T))
        green.UpdateMatrices()

        # Centre on nasion
        hard_node = slicer.util.getNode("Ryu_hard_tissue")
        for i in range(hard_node.GetNumberOfControlPoints()):
            if hard_node.GetNthControlPointLabel(i) == 'n':
                pos = np.zeros(3)
                hard_node.GetNthControlPointPositionWorld(i, pos)
                for node in [red, yellow, green]:
                    node.JumpSlice(pos[0], pos[1], pos[2])
                break

        slicer.util.infoDisplay("Slice views re‑oriented to anatomical planes and centred on nasion.")
    except Exception as e:
        slicer.util.errorDisplay(f"Re‑orientation failed: {e}")

# -----------------------------------------------------------------------------
# Logic Class
# -----------------------------------------------------------------------------
class Ryu2024WorkflowLogic:
    def __init__(self, gui):
        self.gui = gui

    def trackNode(self, node, folder_path=None):
        """Track created nodes and optionally add them to nested folder structure."""
        if node and node.GetID() not in self.gui.createdNodeIDs:
            self.gui.createdNodeIDs.append(node.GetID())
        if folder_path and node:
            try:
                add_node_to_folder(node, folder_path)
                logging.info(f"Added {node.GetName()} to folder: {folder_path}")
            except Exception as e:
                logging.warning(f"Could not add {node.GetName()} to folder: {e}")

    def undo_all(self):
        logging.info(f"Cleaning up {len(self.gui.createdNodeIDs)} generated nodes...")
        for nodeID in self.gui.createdNodeIDs:
            node = slicer.mrmlScene.GetNodeByID(nodeID)
            if node:
                slicer.mrmlScene.RemoveNode(node)
        self.gui.createdNodeIDs.clear()

    def run_script_with_error_handling(self, script_function, *args):
        try:
            return script_function(*args)
        except Exception as e:
            slicer.util.errorDisplay(f"An error occurred: {e}", 30)
            logging.error(f"Error: {e}", exc_info=True)
            return None

    # -------------------------------------------------------------------------
    # Step 1: Main planes
    # -------------------------------------------------------------------------
    def _execute_step1(self):
        logging.info("Step 1: Create Main Anatomical Planes")
        hard_node = slicer.util.getFirstNodeByName('Ryu_hard_tissue')
        if not hard_node:
            raise ValueError("Ryu_hard_tissue not found.")

        def get_landmark(label):
            for i in range(hard_node.GetNumberOfControlPoints()):
                if hard_node.GetNthControlPointLabel(i) == label:
                    pos = np.zeros(3)
                    hard_node.GetNthControlPointPositionWorld(i, pos)
                    return pos
            raise ValueError(f"Landmark '{label}' missing.")

        def unit(v):
            n = np.linalg.norm(v)
            return v / n if n > 1e-9 else v

        auR = get_landmark('auR')
        auL = get_landmark('auL')
        n_pos = get_landmark('n')
        orL = get_landmark('orL')
        b_pos = get_landmark('b')

        vec_right = unit(auR - auL)
        vec_anterior_raw = unit(n_pos - (auR + auL) / 2.0)
        vec_anterior = unit(vec_anterior_raw - np.dot(vec_anterior_raw, vec_right) * vec_right)
        vec_superior = unit(np.cross(vec_right, vec_anterior))

        def create_plane(name, origin, normal, color):
            plane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", name)
            plane.SetOrigin(origin)
            plane.SetNormal(normal)
            set_node_color(plane, color)
            self.trackNode(plane, ["Reference Planes", "Main Planes"])
            return plane

        create_plane("Median Sagittal Plane", n_pos, vec_right, (0.2, 0.8, 0.2))
        create_plane("Orbitale Transverse Plane", orL, vec_superior, (0.8, 0.2, 0.2))
        create_plane("Coronal Plane", b_pos, vec_anterior, (0.2, 0.2, 0.8))
        return True

    # -------------------------------------------------------------------------
    # Step 2: Marginal planes and guiding lines
    # -------------------------------------------------------------------------
    def _execute_step2(self):
        logging.info("Step 2: Create Marginal Planes and Guiding Lines")
        hard_node = slicer.util.getFirstNodeByName('Ryu_hard_tissue')
        if not hard_node:
            raise ValueError("Ryu_hard_tissue not found.")

        def get_landmark(label):
            for i in range(hard_node.GetNumberOfControlPoints()):
                if hard_node.GetNthControlPointLabel(i) == label:
                    pos = np.zeros(3)
                    hard_node.GetNthControlPointPositionWorld(i, pos)
                    return pos
            raise ValueError(f"Landmark '{label}' missing.")

        vec_superior = np.array(slicer.util.getFirstNodeByName("Orbitale Transverse Plane").GetNormal())
        vec_right = np.array(slicer.util.getFirstNodeByName("Median Sagittal Plane").GetNormal())

        defs = [
            ("SOM", "sk", vec_superior, vec_right),
            ("IOM", "or", vec_superior, vec_right),
            ("MOM", "d", vec_right, vec_superior),
            ("LOM", "lat_or", vec_right, vec_superior),
        ]

        for base, lm_prefix, plane_n, line_dir in defs:
            for side in ["L", "R"]:
                p = get_landmark(f"{lm_prefix}{side}")
                color = (1, 0.7, 0.2) if side == "L" else (0.2, 0.7, 1)

                plane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", f"marginal_{base}_{side}")
                plane.SetOrigin(p)
                plane.SetNormal(plane_n)
                set_node_color(plane, color)
                self.trackNode(plane, ["Reference Planes", "Marginal Planes"])

                line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"guiding_{base}_{side}")
                line.AddControlPoint(p - line_dir * 37.5)
                line.AddControlPoint(p + line_dir * 37.5)
                line.GetMeasurement("length").SetEnabled(True)
                set_node_color(line, color)
                self.trackNode(line, ["Reference Planes", "Guiding Lines"])

        return True

    # -------------------------------------------------------------------------
    # Step 3: Essential hard tissue (cyan)
    # -------------------------------------------------------------------------
    def _execute_step3(self):
        logging.info("Step 3: Essential Hard Tissue Measurements")
        hard_node = slicer.util.getFirstNodeByName('Ryu_hard_tissue')
        if not hard_node:
            raise ValueError("Ryu_hard_tissue not found.")

        def get_landmark(label):
            for i in range(hard_node.GetNumberOfControlPoints()):
                if hard_node.GetNthControlPointLabel(i) == label:
                    pos = np.zeros(3)
                    hard_node.GetNthControlPointPositionWorld(i, pos)
                    return pos
            raise ValueError(f"Landmark '{label}' missing.")

        vec_superior = np.array(slicer.util.getFirstNodeByName("Orbitale Transverse Plane").GetNormal())
        vec_right = np.array(slicer.util.getFirstNodeByName("Median Sagittal Plane").GetNormal())
        vec_anterior = np.array(slicer.util.getFirstNodeByName("Coronal Plane").GetNormal())
        coronal_origin = np.array(slicer.util.getFirstNodeByName("Coronal Plane").GetOrigin())

        cyan = (0, 1, 1)

        def create_line(name, p1, p2, length):
            line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
            line.AddControlPoint(p1)
            line.AddControlPoint(p2)
            line.GetMeasurement("length").SetEnabled(True)
            line.GetMeasurement("length").SetValue(length)
            set_node_color(line, cyan)
            self.trackNode(line, ["Predictive Hard Tissue", "Essential"])
            return line

        for side in ["L", "R"]:
            lat_or = get_landmark(f"lat_or{side}")
            d = get_landmark(f"d{side}")
            dist = abs(np.dot(lat_or - d, vec_right))
            create_line(f"{side}1", d, d + vec_right * np.dot(lat_or - d, vec_right), dist)

            sk = get_landmark(f"sk{side}")
            or_ = get_landmark(f"or{side}")
            dist = abs(np.dot(sk - or_, vec_superior))
            create_line(f"{side}8", or_, or_ + vec_superior * np.dot(sk - or_, vec_superior), dist)

            lat_or = get_landmark(f"lat_or{side}")
            dist = abs(np.dot(lat_or - coronal_origin, vec_anterior))
            create_line(f"{side}15", lat_or, lat_or - vec_anterior * np.dot(lat_or - coronal_origin, vec_anterior), dist)

        return True

    # -------------------------------------------------------------------------
    # Step 4: Place eyeball + core predicted lines (yellow) - FIXED VERSION
    # -------------------------------------------------------------------------
    def _execute_step4(self, sex, side):
        logging.info(f"Step 4: Place Eyeball ({sex} {side})")
        hard_node = slicer.util.getFirstNodeByName('Ryu_hard_tissue')
        if not hard_node:
            raise ValueError("Ryu_hard_tissue not found.")

        side_char = side[0]

        def get_line_length(name):
            ln = slicer.mrmlScene.GetFirstNodeByName(name)
            if not ln:
                raise ValueError(f"Line '{name}' not found.")
            return ln.GetMeasurement("length").GetValue()

        L1 = get_line_length(f"{side_char}1")
        L8 = get_line_length(f"{side_char}8")
        L15 = get_line_length(f"{side_char}15")

        if sex == "Female":
            pred_L21 = 0.349 * L8 + 4.320
            pred_L22 = 0.652 * L8 - 4.353
            pred_L23 = 0.619 * L1 - 2.175
            pred33 = 1.005 * L15 + 14.700
        else:
            pred_L21 = 0.560 * L8 - 3.648
            pred_L22 = 0.439 * L8 + 3.662
            pred_L23 = 0.844 * L1 - 11.224
            pred33 = 0.950 * L15 + 19.126

        vec_superior = np.array(slicer.util.getFirstNodeByName("Orbitale Transverse Plane").GetNormal())
        vec_right = np.array(slicer.util.getFirstNodeByName("Median Sagittal Plane").GetNormal())
        vec_anterior = np.array(slicer.util.getFirstNodeByName("Coronal Plane").GetNormal())
        coronal_plane = slicer.util.getFirstNodeByName("Coronal Plane")
        coronal_origin = np.array(coronal_plane.GetOrigin())

        p_si_1 = np.array(slicer.util.getFirstNodeByName(f"marginal_SOM_{side_char}").GetOrigin()) - vec_superior * pred_L21
        p_si_2 = np.array(slicer.util.getFirstNodeByName(f"marginal_IOM_{side_char}").GetOrigin()) + vec_superior * pred_L22
        d_si = 0.5 * (np.dot(vec_superior, p_si_1) + np.dot(vec_superior, p_si_2))

        lat_dir = -vec_right if side_char == "L" else vec_right
        p_ml = np.array(slicer.util.getFirstNodeByName(f"marginal_MOM_{side_char}").GetOrigin()) + lat_dir * pred_L23
        d_ml = np.dot(vec_right, p_ml)

        p_ap = coronal_origin + vec_anterior * pred33
        d_ap = np.dot(vec_anterior, p_ap)

        target_pos = np.linalg.solve(np.array([vec_superior, vec_right, vec_anterior]), np.array([d_si, d_ml, d_ap]))

        # Download and load model
        IDS = {
            "Female Left": "1p8rCfH7g35sAKXl0HeVf8PHzPt_xmSes",
            "Female Right": "1SK4alr7IumBGPm9OFUbNTCRAvJCPCpDR",
            "Male Left": "1X7JllfMrZM-AZpSrNh1CZwMGUTnHcqfG",
            "Male Right": "1rKmPbzuC1EjNoxLwoKNLIqLpZcVSxNYh"
        }
        key = f"{sex} {side}"
        mrb_path = os.path.join(slicer.app.temporaryPath, f"ryu_{key.replace(' ','_')}.mrb")

        # Save camera
        view = slicer.app.layoutManager().threeDWidget(0).threeDView()
        renderer = view.renderWindow().GetRenderers().GetFirstRenderer()
        cam = renderer.GetActiveCamera()
        cam_pos, cam_fp, cam_up = cam.GetPosition(), cam.GetFocalPoint(), cam.GetViewUp()

        gdown.download(id=IDS[key], output=mrb_path, quiet=False)
        nodes_before = set(slicer.util.getNodesByClass("vtkMRMLNode"))
        slicer.util.loadScene(mrb_path, {"clear": False, "loadCamera": False})
        
        # Track all loaded nodes with proper folder organization
        for node in set(slicer.util.getNodesByClass("vtkMRMLNode")) - nodes_before:
            if node.IsA("vtkMRMLModelNode"):
                self.trackNode(node, ["Eye Models", f"{sex} {side} Eye"])
            elif node.IsA("vtkMRMLMarkupsFiducialNode"):
                self.trackNode(node, ["Eye Models", f"{sex} {side} Eye", "Landmarks"])
            else:
                self.trackNode(node, ["Eye Models", f"{sex} {side} Eye"])

        # Find transform and oa
        xform_node, oa0_pos = None, None
        for node in slicer.util.getNodesByClass("vtkMRMLNode"):
            if node.IsA("vtkMRMLLinearTransformNode") and "EyeTransform" in node.GetName():
                xform_node = node
            if node.IsA("vtkMRMLMarkupsFiducialNode"):
                idx = node.GetControlPointIndexByLabel(f"oa{side_char}")
                if idx != -1:
                    p = np.zeros(3)
                    node.GetNthControlPointPositionWorld(idx, p)
                    oa0_pos = p

        if xform_node is None or oa0_pos is None:
            raise ValueError("Could not find model transform or 'oa' landmark.")

        translation = target_pos - oa0_pos
        matrix = vtk.vtkMatrix4x4()
        xform_node.GetMatrixTransformToParent(matrix)
        for i in range(3):
            matrix.SetElement(i, 3, matrix.GetElement(i, 3) + translation[i])
        xform_node.SetMatrixTransformToParent(matrix)

        # Restore camera
        cam.SetPosition(cam_pos)
        cam.SetFocalPoint(cam_fp)
        cam.SetViewUp(cam_up)
        view.renderWindow().Render()

        # ========== FIX: Find the eyeball landmarks node ==========
        eyeball_node = None
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            if node.GetName() == f"{side} Eyeball lmrks" or node.GetName() == f"{side} Eyeball lmrks (2)":
                eyeball_node = node
                break

        if eyeball_node is None:
            raise ValueError(f"Could not find eyeball landmarks node for {side}")

        # Move eyeball node to proper folder if not already there
        self.trackNode(eyeball_node, ["Eye Models", f"{sex} {side} Eye", "Landmarks"])

        hard_tissue_node = slicer.util.getFirstNodeByName('Ryu_hard_tissue')
        if not hard_tissue_node:
            raise ValueError("Ryu_hard_tissue not found.")

        # Create core predicted lines (yellow)
        yellow = (1, 1, 0)

        def get_node(name):
            node = slicer.mrmlScene.GetFirstNodeByName(name)
            if not node:
                raise ValueError(f"Node '{name}' not found.")
            return node

        def get_landmark_pos(node, label):
            for lbl in [label, f"{label[0]}_{label[1]}"]:
                idx = node.GetControlPointIndexByLabel(lbl)
                if idx != -1:
                    pos = np.zeros(3)
                    node.GetNthControlPointPositionWorld(idx, pos)
                    return pos
            raise ValueError(f"Landmark '{label}' not found.")

        def create_line(name, p1, p2):
            ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
            ln.AddControlPoint(p1)
            ln.AddControlPoint(p2)
            ln.GetMeasurement("length").SetEnabled(True)
            set_node_color(ln, yellow)
            self.trackNode(ln, ["Predicted Soft Tissue", "Core"])
            return ln

        def project_to_plane(point, plane):
            o = np.zeros(3)
            n = np.zeros(3)
            plane.GetOrigin(o)
            plane.GetNormal(n)
            return point - np.dot(point - o, n) * n

        marginal_SOM = get_node(f"marginal_SOM_{side_char}")
        marginal_MOM = get_node(f"marginal_MOM_{side_char}")
        lc = get_landmark_pos(eyeball_node, f"lc{side_char}")
        oa = get_landmark_pos(eyeball_node, f"oa{side_char}")
        ocp = get_landmark_pos(hard_tissue_node, f"ocp{side_char}")

        create_line(f"pred_{side_char}21", lc, project_to_plane(lc, marginal_SOM))
        create_line(f"pred_{side_char}23", lc, project_to_plane(lc, marginal_MOM))
        create_line(f"pred_{side_char}33", oa, project_to_plane(oa, coronal_plane))
        create_line(f"pred_{side_char}32", oa, ocp)

        l27 = np.linalg.norm(lc - project_to_plane(lc, coronal_plane))
        slicer.util.infoDisplay(f"{sex} {side} eyeball placed.\nPredicted lines created.\n{side_char}27 = {l27:.2f} mm (no line)")

        return True

    # -------------------------------------------------------------------------
    # Step 5: Descriptive hard tissue (orange)
    # -------------------------------------------------------------------------
    def _execute_step5(self):
        logging.info("Step 5: Descriptive Hard Tissue Measurements")
        hard_node = slicer.util.getFirstNodeByName("Ryu_hard_tissue")
        if not hard_node:
            raise ValueError("Ryu_hard_tissue not found.")
        coronal_plane = slicer.util.getFirstNodeByName("Coronal Plane")
        orbital_plane = slicer.util.getFirstNodeByName("Orbitale Transverse Plane")
        if not coronal_plane or not orbital_plane:
            raise ValueError("Missing anatomical planes.")

        def get_landmark(label):
            for i in range(hard_node.GetNumberOfControlPoints()):
                if hard_node.GetNthControlPointLabel(i) == label:
                    pos = np.zeros(3)
                    hard_node.GetNthControlPointPositionWorld(i, pos)
                    return pos
            raise ValueError(f"Landmark '{label}' missing.")

        def create_line(name, p1, p2):
            ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
            ln.AddControlPoint(p1)
            ln.AddControlPoint(p2)
            ln.GetMeasurement("length").SetEnabled(True)
            set_node_color(ln, (1, 0.5, 0))
            self.trackNode(ln, ["Descriptive Hard Tissue", "Measurements"])
            return ln

        def measure_point_to_plane(point, plane):
            o = np.zeros(3); n = np.zeros(3)
            plane.GetOrigin(o); plane.GetNormal(n)
            return point - np.dot(point - o, n) * n

        def measure_point_to_line(point, line):
            p1 = np.zeros(3); p2 = np.zeros(3)
            line.GetNthControlPointPositionWorld(0, p1)
            line.GetNthControlPointPositionWorld(1, p2)
            line_vec = p2 - p1
            point_vec = point - p1
            t = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
            return p1 + t * line_vec

        # C1
        lom_l = slicer.util.getFirstNodeByName("marginal_LOM_L")
        lom_r = slicer.util.getFirstNodeByName("marginal_LOM_R")
        if lom_l and lom_r:
            o_l = np.zeros(3); o_r = np.zeros(3)
            lom_l.GetOrigin(o_l); lom_r.GetOrigin(o_r)
            n = np.zeros(3); lom_l.GetNormal(n)
            dist = abs(np.dot(o_r - o_l, n))
            ln = create_line("C1", o_l, o_r)
            ln.GetMeasurement("length").SetValue(dist)

        # C2
        n_pos = get_landmark("n")
        proj = measure_point_to_plane(n_pos, coronal_plane)
        create_line("C2", n_pos, proj)

        for side in ["L", "R"]:
            marginal_SOM = slicer.util.getFirstNodeByName(f"marginal_SOM_{side}")
            marginal_MOM = slicer.util.getFirstNodeByName(f"marginal_MOM_{side}")
            marginal_LOM = slicer.util.getFirstNodeByName(f"marginal_LOM_{side}")
            guiding_LOM = slicer.util.getFirstNodeByName(f"guiding_LOM_{side}")
            sk = get_landmark(f"sk{side}")
            or_ = get_landmark(f"or{side}")
            d = get_landmark(f"d{side}")
            lat_or = get_landmark(f"lat_or{side}")
            ocp = get_landmark(f"ocp{side}") if hard_node.GetControlPointIndexByLabel(f"ocp{side}") != -1 else None

            # All orange lines
            create_line(f"{side}2", sk, measure_point_to_plane(sk, marginal_MOM))
            create_line(f"{side}3", sk, measure_point_to_plane(sk, marginal_LOM))
            create_line(f"{side}4", or_, measure_point_to_plane(or_, marginal_MOM))
            create_line(f"{side}5", or_, measure_point_to_plane(or_, marginal_LOM))
            create_line(f"{side}6", d, measure_point_to_plane(d, marginal_SOM))
            create_line(f"{side}7", d, measure_point_to_plane(d, orbital_plane))
            create_line(f"{side}9", lat_or, measure_point_to_plane(lat_or, marginal_SOM))
            create_line(f"{side}10", lat_or, measure_point_to_plane(lat_or, orbital_plane))
            create_line(f"{side}11", sk, measure_point_to_line(sk, guiding_LOM))
            create_line(f"{side}12", n_pos, measure_point_to_line(n_pos, guiding_LOM))
            create_line(f"{side}13", d, measure_point_to_line(d, guiding_LOM))
            create_line(f"{side}14", or_, measure_point_to_line(or_, guiding_LOM))
            create_line(f"{side}16", sk, measure_point_to_plane(sk, coronal_plane))
            create_line(f"{side}19", d, measure_point_to_plane(d, coronal_plane))
            create_line(f"{side}20", or_, measure_point_to_plane(or_, coronal_plane))
            if ocp is not None:
                create_line(f"{side}17", ocp, measure_point_to_plane(ocp, coronal_plane))
                create_line(f"{side}18", ocp, measure_point_to_line(ocp, guiding_LOM))

        return True

    # -------------------------------------------------------------------------
    # Step 6: Additional predicted soft tissue (yellow)
    # -------------------------------------------------------------------------
    def _execute_step6(self):
        logging.info("Step 6: Additional Predicted Soft Tissue Lines")
        yellow = (1, 1, 0)
        hard_node = slicer.util.getFirstNodeByName("Ryu_hard_tissue")
        coronal_plane = slicer.util.getFirstNodeByName("Coronal Plane")
        orbital_plane = slicer.util.getFirstNodeByName("Orbitale Transverse Plane")

        def get_node(name):
            node = slicer.mrmlScene.GetFirstNodeByName(name)
            if not node:
                raise ValueError(f"Node '{name}' not found.")
            return node

        def get_landmark_pos(node, label):
            for lbl in [label, f"{label[0]}_{label[1]}"]:
                idx = node.GetControlPointIndexByLabel(lbl)
                if idx != -1:
                    pos = np.zeros(3)
                    node.GetNthControlPointPositionWorld(idx, pos)
                    return pos
            raise ValueError(f"Landmark '{label}' not found.")

        def create_line(name, p1, p2):
            ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
            ln.AddControlPoint(p1)
            ln.AddControlPoint(p2)
            ln.GetMeasurement("length").SetEnabled(True)
            set_node_color(ln, yellow)
            self.trackNode(ln, ["Predicted Soft Tissue", "Additional"])
            return ln

        def project_to_plane(point, plane):
            o = np.zeros(3); n = np.zeros(3)
            plane.GetOrigin(o); plane.GetNormal(n)
            return point - np.dot(point - o, n) * n

        def project_to_line(point, line):
            p1 = np.zeros(3); p2 = np.zeros(3)
            line.GetNthControlPointPositionWorld(0, p1)
            line.GetNthControlPointPositionWorld(1, p2)
            line_vec = p2 - p1
            point_vec = point - p1
            t = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
            return p1 + t * line_vec

        for side in ["L", "R"]:
            eyeball = get_node(f"{'Left' if side=='L' else 'Right'} Eyeball lmrks")
            lc = get_landmark_pos(eyeball, f"lc{side}")
            la = get_landmark_pos(eyeball, f"la{side}")
            lp = get_landmark_pos(eyeball, f"lp{side}")
            oa = get_landmark_pos(eyeball, f"oa{side}")
            os = get_landmark_pos(eyeball, f"os{side}")
            oi = get_landmark_pos(eyeball, f"oi{side}")
            ol = get_landmark_pos(eyeball, f"ol{side}")
            om = get_landmark_pos(eyeball, f"om{side}")
            gc = get_landmark_pos(eyeball, f"gc{side}")
            ocp = get_landmark_pos(hard_node, f"ocp{side}")

            marginal_SOM = get_node(f"marginal_SOM_{side}")
            marginal_MOM = get_node(f"marginal_MOM_{side}")
            marginal_LOM = get_node(f"marginal_LOM_{side}")
            guiding_LOM = get_node(f"guiding_LOM_{side}")

            create_line(f"pred_{side}22", lc, project_to_plane(lc, orbital_plane))
            create_line(f"pred_{side}24", lc, project_to_plane(lc, marginal_LOM))
            create_line(f"pred_{side}25", lc, project_to_line(lc, guiding_LOM))
            if ocp is not None:
                create_line(f"pred_{side}26", lc, ocp)
            create_line(f"pred_{side}28", la, lp)
            create_line(f"pred_{side}29", oa, lc)
            create_line(f"pred_{side}31", oa, project_to_line(oa, guiding_LOM))
            create_line(f"pred_E1_{side}", lc, os)
            create_line(f"pred_E2_{side}", lc, om)
            create_line(f"pred_E3_{side}", gc, os)
            create_line(f"pred_E4_{side}", gc, om)
            create_line(f"pred_E5_{side}", os, oi)
            create_line(f"pred_E6_{side}", ol, om)

        return True

    # -------------------------------------------------------------------------
    # Step 7: True soft tissue (green)
    # -------------------------------------------------------------------------
    def _execute_step7(self):
        logging.info("Step 7: True Soft Tissue Lines")
        true_node = slicer.util.getFirstNodeByName("Ryu_soft_tissue")
        if not true_node:
            raise ValueError("Ryu_soft_tissue not found. Please load it first.")
        
        # Move true node to proper folder
        self.trackNode(true_node, ["True Soft Tissue", "Landmarks"])

        # Compute lens centre and globe centre if missing
        for side in ["L", "R"]:
            def get_true(label):
                idx = true_node.GetControlPointIndexByLabel(f"true_{label}{side}")
                if idx == -1: return None
                p = np.zeros(3)
                true_node.GetNthControlPointPositionWorld(idx, p)
                return p

            la = get_true("la")
            lp = get_true("lp")
            if la is not None and lp is not None:
                lc = (la + lp) / 2.0
                idx = true_node.GetControlPointIndexByLabel(f"true_lc{side}")
                if idx == -1:
                    true_node.AddControlPoint(lc, f"true_lc{side}")
                else:
                    true_node.SetNthControlPointPositionWorld(idx, lc)

            extremes = ["oa","op","os","oi","om","ol"]
            pts = [get_true(e) for e in extremes if get_true(e) is not None]
            if len(pts) == 6:
                gc = np.mean(pts, axis=0)
                idx = true_node.GetControlPointIndexByLabel(f"true_gc{side}")
                if idx == -1:
                    true_node.AddControlPoint(gc, f"true_gc{side}")
                else:
                    true_node.SetNthControlPointPositionWorld(idx, gc)

        green = (0, 1, 0)
        hard_node = slicer.util.getFirstNodeByName("Ryu_hard_tissue")
        coronal_plane = slicer.util.getFirstNodeByName("Coronal Plane")
        orbital_plane = slicer.util.getFirstNodeByName("Orbitale Transverse Plane")

        def get_node(name):
            node = slicer.mrmlScene.GetFirstNodeByName(name)
            if not node:
                raise ValueError(f"Node '{name}' not found.")
            return node

        def get_landmark_pos(node, label):
            idx = node.GetControlPointIndexByLabel(label)
            if idx == -1:
                raise ValueError(f"Landmark '{label}' not found in '{node.GetName()}'.")
            pos = np.zeros(3)
            node.GetNthControlPointPositionWorld(idx, pos)
            return pos

        def create_line(name, p1, p2):
            ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
            ln.AddControlPoint(p1)
            ln.AddControlPoint(p2)
            ln.GetMeasurement("length").SetEnabled(True)
            set_node_color(ln, green)
            self.trackNode(ln, ["True Soft Tissue", "Measurements"])
            return ln

        def project_to_plane(point, plane):
            o = np.zeros(3); n = np.zeros(3)
            plane.GetOrigin(o); plane.GetNormal(n)
            return point - np.dot(point - o, n) * n

        def project_to_line(point, line):
            p1 = np.zeros(3); p2 = np.zeros(3)
            line.GetNthControlPointPositionWorld(0, p1)
            line.GetNthControlPointPositionWorld(1, p2)
            line_vec = p2 - p1
            point_vec = point - p1
            t = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
            return p1 + t * line_vec

        for side in ["L", "R"]:
            marginal_SOM = get_node(f"marginal_SOM_{side}")
            marginal_MOM = get_node(f"marginal_MOM_{side}")
            marginal_LOM = get_node(f"marginal_LOM_{side}")
            guiding_LOM = get_node(f"guiding_LOM_{side}")

            lc = get_landmark_pos(true_node, f"true_lc{side}")
            la = get_landmark_pos(true_node, f"true_la{side}")
            lp = get_landmark_pos(true_node, f"true_lp{side}")
            oa = get_landmark_pos(true_node, f"true_oa{side}")
            os = get_landmark_pos(true_node, f"true_os{side}")
            oi = get_landmark_pos(true_node, f"true_oi{side}")
            ol = get_landmark_pos(true_node, f"true_ol{side}")
            om = get_landmark_pos(true_node, f"true_om{side}")
            gc = get_landmark_pos(true_node, f"true_gc{side}")
            ocp = get_landmark_pos(hard_node, f"ocp{side}")

            if lc is not None:
                create_line(f"true_{side}21", lc, project_to_plane(lc, marginal_SOM))
                create_line(f"true_{side}22", lc, project_to_plane(lc, orbital_plane))
                create_line(f"true_{side}23", lc, project_to_plane(lc, marginal_MOM))
                create_line(f"true_{side}24", lc, project_to_plane(lc, marginal_LOM))
                create_line(f"true_{side}25", lc, project_to_line(lc, guiding_LOM))
                if ocp is not None:
                    create_line(f"true_{side}26", lc, ocp)
            if la is not None and lp is not None:
                create_line(f"true_{side}28", la, lp)
            if oa is not None and lc is not None:
                create_line(f"true_{side}29", oa, lc)
                create_line(f"true_{side}31", oa, project_to_line(oa, guiding_LOM))
                create_line(f"true_{side}33", oa, project_to_plane(oa, coronal_plane))
                if ocp is not None:
                    create_line(f"true_{side}32", oa, ocp)
            if lc is not None and os is not None:
                create_line(f"true_E1_{side}", lc, os)
            if lc is not None and om is not None:
                create_line(f"true_E2_{side}", lc, om)
            if gc is not None and os is not None:
                create_line(f"true_E3_{side}", gc, os)
            if gc is not None and om is not None:
                create_line(f"true_E4_{side}", gc, om)
            if os is not None and oi is not None:
                create_line(f"true_E5_{side}", os, oi)
            if ol is not None and om is not None:
                create_line(f"true_E6_{side}", ol, om)

        return True

    # -------------------------------------------------------------------------
    # Step 8: Additional predictions (Table 3)
    # -------------------------------------------------------------------------
    def _execute_step8(self):
        results = []
        for side in ["L", "R"]:
            L15 = self._get_line_length(f"{side}15")
            if L15 is None:
                continue
            male_L27 = 0.989 * L15 + 11.550
            female_L27 = 1.007 * L15 + 9.552
            male_L33 = 0.950 * L15 + 19.126
            female_L33 = 1.005 * L15 + 14.700
            results.append((f"{side}27_from_L15 (Male)", f"{male_L27:.2f}"))
            results.append((f"{side}27_from_L15 (Female)", f"{female_L27:.2f}"))
            results.append((f"{side}33_from_L15 (Male)", f"{male_L33:.2f}"))
            results.append((f"{side}33_from_L15 (Female)", f"{female_L33:.2f}"))
        return results

    def _get_line_length(self, name):
        ln = slicer.mrmlScene.GetFirstNodeByName(name)
        if ln and ln.IsA("vtkMRMLMarkupsLineNode"):
            return ln.GetMeasurement("length").GetValue()
        return None

    # -------------------------------------------------------------------------
    # Step 9: Validation comparison
    # -------------------------------------------------------------------------
    def _execute_step9(self):
        true_node = slicer.util.getFirstNodeByName("Ryu_soft_tissue")
        pred_left = slicer.util.getFirstNodeByName("Left Eyeball lmrks")
        pred_right = slicer.util.getFirstNodeByName("Right Eyeball lmrks")
        if not true_node or not pred_left or not pred_right:
            raise ValueError("Missing soft tissue or predicted eyeball nodes.")
        hard_node = slicer.util.getFirstNodeByName("Ryu_hard_tissue")
        if not hard_node:
            raise ValueError("Ryu_hard_tissue not found.")

        results = []

        def get_pos(node, label):
            if not node:
                return None
            idx = node.GetControlPointIndexByLabel(label)
            if idx == -1:
                return None
            p = np.zeros(3)
            node.GetNthControlPointPositionWorld(idx, p)
            return p

        # Landmark errors
        landmark_types = ['lc','la','lp','oa','os','oi','ol','om','gc']
        for side, pred_node in [('L', pred_left), ('R', pred_right)]:
            for lmk in landmark_types:
                true_label = f"true_{lmk}{side}"
                pred_label = f"{lmk}{side}"
                true_p = get_pos(true_node, true_label)
                pred_p = get_pos(pred_node, pred_label)
                if true_p is not None and pred_p is not None:
                    err = np.linalg.norm(true_p - pred_p)
                    results.append((f"{pred_label}_error", f"{err:.2f}", "Landmark 3D error"))

        # Length differences for drawn lines
        pred_lines = {n.GetName().replace("pred_",""): n.GetMeasurement("length").GetValue()
                      for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
                      if n.GetName().startswith("pred_")}
        true_lines = {n.GetName().replace("true_",""): n.GetMeasurement("length").GetValue()
                      for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
                      if n.GetName().startswith("true_")}
        for key in set(pred_lines.keys()) & set(true_lines.keys()):
            diff = abs(pred_lines[key] - true_lines[key])
            results.append((key, f"{diff:.2f}", "Length difference"))

        # Calculated L27 and Table 3
        coronal_plane = slicer.util.getFirstNodeByName("Coronal Plane")
        if coronal_plane:
            def proj(p):
                o = np.zeros(3); n = np.zeros(3)
                coronal_plane.GetOrigin(o); coronal_plane.GetNormal(n)
                return p - np.dot(p - o, n) * n
            for side, pred_node in [('L', pred_left), ('R', pred_right)]:
                pred_lc = get_pos(pred_node, f"lc{side}")
                true_lc = get_pos(true_node, f"true_lc{side}")
                if pred_lc is not None and true_lc is not None:
                    pred_l27 = np.linalg.norm(pred_lc - proj(pred_lc))
                    true_l27 = np.linalg.norm(true_lc - proj(true_lc))
                    results.append((f"{side}27 (calc)", f"{abs(pred_l27 - true_l27):.2f}", "Calculated (no line)"))

        # Table 3 predictions vs true
        for side in ["L", "R"]:
            L15 = self._get_line_length(f"{side}15")
            if L15 is None:
                continue
            male_L27_pred = 0.989 * L15 + 11.550
            female_L27_pred = 1.007 * L15 + 9.552
            male_L33_pred = 0.950 * L15 + 19.126
            female_L33_pred = 1.005 * L15 + 14.700

            true_lc = get_pos(true_node, f"true_lc{side}")
            true_l27 = None
            if coronal_plane and true_lc is not None:
                true_l27 = np.linalg.norm(true_lc - proj(true_lc))

            true_33_line = slicer.mrmlScene.GetFirstNodeByName(f"true_{side}33")
            true_l33 = true_33_line.GetMeasurement("length").GetValue() if true_33_line else None

            if true_l27 is not None:
                results.append((f"{side}27_from_L15 (Male)", f"{abs(male_L27_pred - true_l27):.2f}", "Calculated (Table 3)"))
                results.append((f"{side}27_from_L15 (Female)", f"{abs(female_L27_pred - true_l27):.2f}", "Calculated (Table 3)"))
            if true_l33 is not None:
                results.append((f"{side}33_from_L15 (Male)", f"{abs(male_L33_pred - true_l33):.2f}", "Calculated (Table 3)"))
                results.append((f"{side}33_from_L15 (Female)", f"{abs(female_L33_pred - true_l33):.2f}", "Calculated (Table 3)"))

        return results

# -----------------------------------------------------------------------------
# GUI Widget Class
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# GUI Widget Class (UPDATED with scroll area and no window resizing)
# -----------------------------------------------------------------------------
class Ryu2024WorkflowGUI(qt.QWidget):
    def __init__(self, parent=None):
        super(Ryu2024WorkflowGUI, self).__init__(parent)
        self.logic = Ryu2024WorkflowLogic(self)
        self.createdNodeIDs = []
        self.setup()

    def setup(self):
        self.setWindowTitle("Ryu et al. 2024 Workflow (Organised Folders)")
        
        # Create a scroll area to contain the workflow
        scroll_area = qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(qt.Qt.ScrollBarAsNeeded)
        
        # Create the main container widget for the scroll area
        container_widget = qt.QWidget()
        self.mainLayout = qt.QVBoxLayout(container_widget)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(5)
        
        # Set a fixed maximum width for the dock widget (prevents window resizing)
        self.setMaximumWidth(450)
        self.setMinimumWidth(350)

        self.hard_tissue_url = "https://github.com/user-attachments/files/28905389/Ryu_2024_hard_tissue_lmrks.mrk.json"
        self.soft_tissue_url = "https://github.com/user-attachments/files/27196663/Ryu_soft_tissue.mrk.json"

        # Step 0
        step0Box = self._create_collapsible_box("Step 0: Load Hard Tissue & Compute mid‑au")
        self.loadHardButton = qt.QPushButton("Download/Load Ryu Hard Tissue Landmarks")
        self.midAuButton = qt.QPushButton("Calculate mid‑au (from auL/auR)")
        self._add_to_box_layout(step0Box, [self.loadHardButton, self.midAuButton])

        # Step 1-3
        step1Box = self._create_collapsible_box("Step 1: Create Main Anatomical Planes")
        self.step1Button = qt.QPushButton("Run Step 1")
        self._add_to_box_layout(step1Box, [self.step1Button])

        step2Box = self._create_collapsible_box("Step 2: Create Marginal Planes and Guiding Lines")
        self.step2Button = qt.QPushButton("Run Step 2")
        self._add_to_box_layout(step2Box, [self.step2Button])

        step3Box = self._create_collapsible_box("Step 3: Create Essential Hard Tissue (cyan)")
        self.step3Button = qt.QPushButton("Run Step 3")
        self._add_to_box_layout(step3Box, [self.step3Button])

        # Step 4
        step4Box = self._create_collapsible_box("Step 4: Place Eyeball + Core Predicted Lines (yellow)")
        formLayout = qt.QFormLayout()
        self.sexCombo = qt.QComboBox()
        self.sexCombo.addItems(["Female", "Male"])
        self.sideCombo = qt.QComboBox()
        self.sideCombo.addItems(["Left", "Right"])
        self.step4Button = qt.QPushButton("Download and Place Eyeball")
        self.placementStatus = qt.QLabel("Ready.")
        self.placementStatus.setWordWrap(True)
        formLayout.addRow("Sex:", self.sexCombo)
        formLayout.addRow("Side:", self.sideCombo)
        formLayout.addRow(self.step4Button)
        formLayout.addRow("Status:", self.placementStatus)
        self._add_to_box_layout(step4Box, [formLayout])
        self.predLensButton = qt.QPushButton("📏 Instructions: Create pred_L30 / pred_R30")
        self._add_to_box_layout(step4Box, [self.predLensButton])

        # Step 5
        step5Box = self._create_collapsible_box("Step 5: Create Descriptive Hard Tissue (orange)")
        self.step5Button = qt.QPushButton("Run Step 5")
        self._add_to_box_layout(step5Box, [self.step5Button])

        # Step 6
        step6Box = self._create_collapsible_box("Step 6: Create Additional Predicted Soft Tissue (yellow)")
        self.step6Button = qt.QPushButton("Run Step 6")
        self._add_to_box_layout(step6Box, [self.step6Button])

        # Soft tissue loading + helpers
        softBox = self._create_collapsible_box("Load Soft Tissue & Prepare for True Measurements")
        self.loadSoftButton = qt.QPushButton("Download/Load Ryu Soft Tissue Landmarks")
        self.reorientButton = qt.QPushButton("🔄 Re‑orient Slice Views to Anatomical Planes")
        self.trueLensButton = qt.QPushButton("📏 Instructions: Create true_L30 / true_R30")
        self._add_to_box_layout(softBox, [self.loadSoftButton, self.reorientButton, self.trueLensButton])

        # Step 7
        step7Box = self._create_collapsible_box("Step 7: Create True Soft Tissue Lines (green)")
        self.step7Button = qt.QPushButton("Run Step 7")
        self._add_to_box_layout(step7Box, [self.step7Button])

        # Step 8
        step8Box = self._create_collapsible_box("Step 8: Additional Predictions (Table 3)")
        self.step8Button = qt.QPushButton("Show Additional Predictions")
        self.additionalTable = qt.QTableWidget()
        self.additionalTable.setColumnCount(2)
        self.additionalTable.setHorizontalHeaderLabels(["Prediction", "Value (mm)"])
        self.additionalTable.setMinimumHeight(150)
        self.additionalTable.setMaximumHeight(200)
        self._add_to_box_layout(step8Box, [self.step8Button, self.additionalTable])

        # Step 9
        step9Box = self._create_collapsible_box("Step 9: Validation Comparison")
        self.step9Button = qt.QPushButton("Run Validation")
        self.resultTable = qt.QTableWidget()
        self.resultTable.setColumnCount(3)
        self.resultTable.setHorizontalHeaderLabels(["Measurement", "Value (mm)", "Method"])
        self.resultTable.setMinimumHeight(200)
        self.resultTable.setMaximumHeight(300)
        self.copyButton = qt.QPushButton("Copy Table to Clipboard")
        self._add_to_box_layout(step9Box, [self.step9Button, self.resultTable, self.copyButton])

        # Management
        manageBox = self._create_collapsible_box("Management")
        self.cleanupButton = qt.QPushButton("Clean Up All Generated Nodes")
        self._add_to_box_layout(manageBox, [self.cleanupButton])

        self.mainLayout.addStretch(1)
        
        # Set the container widget as the scroll area's widget
        scroll_area.setWidget(container_widget)
        
        # Create a layout for this widget and add the scroll area
        main_layout = qt.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Connections
        self.loadHardButton.clicked.connect(lambda: self.onLoadMarkups(self.hard_tissue_url, "Ryu_hard_tissue"))
        self.midAuButton.clicked.connect(lambda: update_mid_auriculare_midpoint())
        self.loadSoftButton.clicked.connect(lambda: self.onLoadMarkups(self.soft_tissue_url, "Ryu_soft_tissue"))
        self.reorientButton.clicked.connect(lambda: reorient_slice_views())
        self.predLensButton.clicked.connect(self.showPredLensInstructions)
        self.trueLensButton.clicked.connect(self.showTrueLensInstructions)

        self.step1Button.clicked.connect(lambda: self.logic.run_script_with_error_handling(self.logic._execute_step1))
        self.step2Button.clicked.connect(lambda: self.logic.run_script_with_error_handling(self.logic._execute_step2))
        self.step3Button.clicked.connect(lambda: self.logic.run_script_with_error_handling(self.logic._execute_step3))
        self.step4Button.clicked.connect(self.onRunStep4)
        self.step5Button.clicked.connect(lambda: self.logic.run_script_with_error_handling(self.logic._execute_step5))
        self.step6Button.clicked.connect(lambda: self.logic.run_script_with_error_handling(self.logic._execute_step6))
        self.step7Button.clicked.connect(lambda: self.logic.run_script_with_error_handling(self.logic._execute_step7))
        self.step8Button.clicked.connect(self.onShowAdditional)
        self.step9Button.clicked.connect(self.onValidate)
        self.copyButton.clicked.connect(self.onCopy)
        self.cleanupButton.clicked.connect(self.onCleanup)
        
        # Set size policy to prevent resizing of main window
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Expanding)

    def _create_collapsible_box(self, title):
        try:
            import ctk
            box = ctk.ctkCollapsibleButton()
            box.text = title
            # Set size policy to prevent expansion
            box.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        except ImportError:
            box = qt.QGroupBox(title)
            box.setCheckable(True)
            box.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.mainLayout.addWidget(box)
        return box

    def _add_to_box_layout(self, box, widgets):
        if len(widgets) > 0 and isinstance(widgets[0], qt.QFormLayout):
            layout = widgets[0]
        else:
            layout = qt.QVBoxLayout()
            for w in widgets:
                layout.addWidget(w)
        # Only set the layout if the box doesn't already have one
        if not box.layout():
            box.setLayout(layout)

    def onLoadMarkups(self, url, node_name):
        if slicer.util.getFirstNodeByName(node_name):
            slicer.util.infoDisplay(f"Node '{node_name}' already exists.")
            return
        try:
            temp_path = os.path.join(slicer.app.temporaryPath, os.path.basename(url))
            slicer.util.showStatusMessage(f"Downloading '{node_name}'...")
            urllib.request.urlretrieve(url, temp_path)
            node = slicer.util.loadMarkups(temp_path)
            node.SetName(node_name)
            # Move to appropriate folder after loading
            if node_name == "Ryu_hard_tissue":
                self.logic.trackNode(node, ["Hard Tissue Landmarks"])
            elif node_name == "Ryu_soft_tissue":
                self.logic.trackNode(node, ["True Soft Tissue", "Landmarks"])
            slicer.util.infoDisplay(f"Successfully loaded '{node_name}'.")
        except Exception as e:
            slicer.util.errorDisplay(f"Failed: {e}")
        finally:
            slicer.util.showStatusMessage("")

    def onRunStep4(self):
        self.placementStatus.setText("Working...")
        slicer.app.processEvents()
        sex = self.sexCombo.currentText
        side = self.sideCombo.currentText
        result = self.logic.run_script_with_error_handling(self.logic._execute_step4, sex, side)
        if result:
            self.placementStatus.setText(f"SUCCESS! {sex} {side} eyeball placed + core yellow lines.")
        else:
            self.placementStatus.setText("ERROR.")

    def showPredLensInstructions(self):
        msg = (
            "📏 **Manual creation of predicted lens diameter lines (pred_L30 / pred_R30)**\n\n"
            "The lens diameter is visible on the artificial eye model. To measure:\n"
            "1. Go to **Models** module and hide cornea, iris, pupil layers.\n"
            "2. Use the **lcL/R** landmarks as a guide (the line must cross the lens centre).\n"
            "3. Open **Markups** → **Create Markups > Line**.\n"
            "4. Place two points on opposite sides of the lens (anterior/posterior view).\n"
            "5. **Rename** the line to exactly **`pred_L30`** (left) or **`pred_R30`** (right).\n\n"
            "The length will be automatically stored and used in validation."
        )
        slicer.util.infoDisplay(msg, windowTitle="Predicted Lens Diameter")

    def showTrueLensInstructions(self):
        msg = (
            "📏 **Manual creation of true lens diameter lines (true_L30 / true_R30)**\n\n"
            "After loading the soft tissue landmarks, measure the true lens on the CT:\n"
            "1. Use **Re‑orient Slice Views** to align with anatomical planes.\n"
            "2. Scroll to find the lens (axial or coronal view).\n"
            "3. Open **Markups** → **Create Markups > Line**.\n"
            "4. Place points on opposite lens edges crossing the true lens centre (use `true_lcL/R` as guide).\n"
            "5. **Rename** the line to exactly **`true_L30`** (left) or **`true_R30`** (right).\n\n"
            "These will be included in the validation comparison."
        )
        slicer.util.infoDisplay(msg, windowTitle="True Lens Diameter")

    def onShowAdditional(self):
        preds = self.logic.run_script_with_error_handling(self.logic._execute_step8)
        if not preds:
            return
        self.additionalTable.setRowCount(0)
        self.additionalTable.setRowCount(len(preds))
        for row, (name, val) in enumerate(preds):
            self.additionalTable.setItem(row, 0, qt.QTableWidgetItem(name))
            self.additionalTable.setItem(row, 1, qt.QTableWidgetItem(val))
        self.additionalTable.resizeColumnsToContents()

    def onValidate(self):
        results = self.logic.run_script_with_error_handling(self.logic._execute_step9)
        if not results:
            return
        self.resultTable.setRowCount(0)
        self.resultTable.setRowCount(len(results))
        for row, (meas, val, method) in enumerate(results):
            self.resultTable.setItem(row, 0, qt.QTableWidgetItem(meas))
            self.resultTable.setItem(row, 1, qt.QTableWidgetItem(val))
            self.resultTable.setItem(row, 2, qt.QTableWidgetItem(method))
        self.resultTable.resizeColumnsToContents()

    def onCopy(self):
        clipboard = qt.QApplication.clipboard()
        text = ""
        headers = [self.resultTable.horizontalHeaderItem(c).text() for c in range(self.resultTable.columnCount)]
        text += "\t".join(headers) + "\n"
        for r in range(self.resultTable.rowCount):
            row_items = [self.resultTable.item(r, c).text() if self.resultTable.item(r, c) else "" for c in range(self.resultTable.columnCount)]
            text += "\t".join(row_items) + "\n"
        clipboard.setText(text)
        slicer.util.infoDisplay("Table copied.")

    def onCleanup(self):
        self.logic.undo_all()
        self.placementStatus.setText("Ready.")
        self.additionalTable.setRowCount(0)
        self.resultTable.setRowCount(0)
        slicer.util.infoDisplay("Cleanup done.")

# -----------------------------------------------------------------------------
# Run GUI (UPDATED - prevents main window resizing)
# -----------------------------------------------------------------------------
try:
    if 'ryu2024WorkflowGUI' in globals() and ryu2024WorkflowGUI.parent():
        globals()['ryu2024WorkflowGUI'].parent().close()
    del globals()['ryu2024WorkflowGUI']
except (NameError, KeyError):
    pass

ryu2024WorkflowGUI = Ryu2024WorkflowGUI()
dock = qt.QDockWidget("Ryu 2024 Workflow (Organised)")
dock.setWidget(ryu2024WorkflowGUI)
dock.setFeatures(qt.QDockWidget.DockWidgetClosable | qt.QDockWidget.DockWidgetMovable)
dock.setAllowedAreas(qt.Qt.LeftDockWidgetArea | qt.Qt.RightDockWidgetArea)

# Add dock without forcing the main window to resize
slicer.util.mainWindow().addDockWidget(qt.Qt.RightDockWidgetArea, dock)

# Ensure the dock widget doesn't cause the main window to resize
dock.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Minimum)
dock.setMaximumWidth(450)

dock.show()

```
