[Ramus Breadth.mrk.json](https://github.com/user-attachments/files/26058966/Ramus.Breadth.mrk.json)
[R Minimum zygomatic thickness Rynn.mrk.json](https://github.com/user-attachments/files/26058965/R.Minimum.zygomatic.thickness.Rynn.mrk.json)
[R Maximum zygomatic thickness Rynn.mrk.json](https://github.com/user-attachments/files/26058964/R.Maximum.zygomatic.thickness.Rynn.mrk.json)
[L Minimum zygomatic thickness Rynn.mrk.json](https://github.com/user-attachments/files/26058962/L.Minimum.zygomatic.thickness.Rynn.mrk.json)
[L Maximum zygomatic thickness Rynn.mrk.json](https://github.com/user-attachments/files/26058961/L.Maximum.zygomatic.thickness.Rynn.mrk.json)
[FHP_landmarks.json](https://github.com/user-attachments/files/26058950/FHP_landmarks.json)
[landmarks.mrk.json](https://github.com/user-attachments/files/26087029/landmarks.mrk.json)



# Code 

```python
"""
Mandibular and Cranial Measurements GUI for 3D Slicer
Copy-paste this entire script into the 3D Slicer Python Interactor and run.

Workflow (beginner-friendly):
1) Download + load FHP_landmarks.json (contains: zyoL, poR, poL)
2) Click "Apply FHP alignment (001)" to run the full yaw+roll+pitch alignment and HARDEN the transform
3) Download + load landmarks.json (for landmark placement/measurements)
4) Create automatic linear measurements (label-based; no right gonial angle)
5) Create angles:
   - Gonial angle L (needs manual adjustment of points 1 and 3)
   - Mental angle (id → gn → goL) automatic
6) Create empty manual line measurements using your provided .mrk.json templates + descriptions
7) Copy linear measurements OR angle measurements to clipboard using buttons (paste into Excel)

Notes:
- This script assumes the correct fiducial list is found by checking that it contains expected labels,
  so it works even if multiple markups fiducial lists exist in the scene.
"""

import os
import urllib.request
import numpy as np
import vtk
import qt
import slicer

# ============================================================
# URLs (as provided)
# ============================================================

FHP_LANDMARKS_URL = "https://github.com/user-attachments/files/26058950/FHP_landmarks.json"
ANATOMICAL_LANDMARKS_URL = "https://github.com/user-attachments/files/26087029/landmarks.mrk.json"

MANUAL_TEMPLATE_URLS = {
    "L Maximum Zygomatic Thickness": "https://github.com/user-attachments/files/26058961/L.Maximum.zygomatic.thickness.Rynn.mrk.json",
    "L Minimum Zygomatic Thickness": "https://github.com/user-attachments/files/26058962/L.Minimum.zygomatic.thickness.Rynn.mrk.json",
    "R Maximum Zygomatic Thickness": "https://github.com/user-attachments/files/26058964/R.Maximum.zygomatic.thickness.Rynn.mrk.json",
    "R Minimum Zygomatic Thickness": "https://github.com/user-attachments/files/26058965/R.Minimum.zygomatic.thickness.Rynn.mrk.json",
    "Ramus Breadth": "https://github.com/user-attachments/files/26058966/Ramus.Breadth.mrk.json",
}

MANUAL_DESCRIPTIONS = {
    "R Maximum Zygomatic Thickness": "The thickest point of the RIGHT zygomatic arch",
    "R Minimum Zygomatic Thickness": "The narrowest point of the RIGHT zygomatic arch.",
    "L Maximum Zygomatic Thickness": "The thickest point of the LEFT zygomatic arch",
    "L Minimum Zygomatic Thickness": "The narrowest point of the LEFT zygomatic arch.",
    "Ramus Breadth": "The narrowest point of the LEFT ramus of the mandible.",
}

# ============================================================
# Helper functions
# ============================================================

def download_file(url, filename):
    tempDir = qt.QStandardPaths.writableLocation(qt.QStandardPaths.TempLocation)
    filepath = os.path.join(tempDir, filename)
    slicer.util.delayDisplay(f"Downloading {filename} ...")
    urllib.request.urlretrieve(url, filepath)
    return filepath

def find_fiducial_node_with_labels(required_labels):
    """Return the first fiducial node that contains ALL required_labels."""
    nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")
    for n in nodes:
        labels = set(n.GetNthControlPointLabel(i) for i in range(n.GetNumberOfControlPoints()))
        if all(lbl in labels for lbl in required_labels):
            return n
    return None

def get_landmark_point(markups_node, label):
    idx = markups_node.GetControlPointIndexByLabel(label)
    if idx < 0:
        print(f"Warning: landmark '{label}' not found in node '{markups_node.GetName()}'")
        return None
    return markups_node.GetNthControlPointPositionVector(idx)

def create_or_get_first_volume():
    vols = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
    return vols[0] if vols else None

def harden_transform_on_node(node):
    if not node or not node.GetTransformNodeID():
        return
    slicer.vtkSlicerTransformLogic().hardenTransform(node)

# ============================================================
# Step 1: Download/load FHP landmarks + run full 001 alignment
# ============================================================

def download_and_load_fhp_landmarks():
    try:
        path = download_file(FHP_LANDMARKS_URL, "FHP_landmarks.json")
        slicer.util.loadMarkups(path)
        slicer.util.delayDisplay(
            "Loaded FHP_landmarks.json.\n"
            "Please check/adjust placement of: zyoL, poR, poL.\n"
            "Then click 'Apply FHP alignment (001)'."
        )
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to download/load FHP_landmarks.json:\n{e}")

def apply_fhp_alignment_full_001():
    """
    Implements your original '001_code for fhp alignment.txt' logic:
    - Find poR, poL, zyoL by label
    - Yaw (RotateZ) to align po vector
    - Roll (RotateY) using updated po vector
    - Pitch (RotateX) using vector from midpoint(poR,poL) to zyoL
    - Apply to first volume (if any) and the FHP fiducials
    - Harden transform on the volume (as in your 001 script)
    """
    try:
        scene = slicer.mrmlScene

        F = find_fiducial_node_with_labels(["poR", "poL", "zyoL"])
        if not F:
            slicer.util.errorDisplay("Could not find FHP fiducials node containing labels: poR, poL, zyoL.")
            return

        poR_id = F.GetControlPointIndexByLabel("poR")
        poL_id = F.GetControlPointIndexByLabel("poL")
        zyo_id = F.GetControlPointIndexByLabel("zyoL")

        # Get coordinates
        poR = [0, 0, 0]
        poL = [0, 0, 0]
        zyo = [0, 0, 0]
        F.GetNthControlPointPosition(poR_id, poR)
        F.GetNthControlPointPosition(poL_id, poL)
        F.GetNthControlPointPosition(zyo_id, zyo)

        # -----------------------
        # 1) Yaw (RotateZ)
        # -----------------------
        po = [poR[0] - poL[0], poR[1] - poL[1], poR[2] - poL[2]]
        vTransform = vtk.vtkTransform()
        vTransform.RotateZ(-np.arctan2(po[1], po[0]) * 180 / np.pi)

        transform = slicer.vtkMRMLLinearTransformNode()
        scene.AddNode(transform)
        transform.SetName("FHP_Alignment_Yaw")
        transform.SetMatrixTransformToParent(vTransform.GetMatrix())

        V = create_or_get_first_volume()
        if V:
            V.SetAndObserveTransformNodeID(transform.GetID())
        F.SetAndObserveTransformNodeID(transform.GetID())

        # -----------------------
        # Get transformed coords (like your script)
        # -----------------------
        poR2 = [0, 0, 0]
        poL2 = [0, 0, 0]
        zyo2 = [0, 0, 0]
        F.GetNthControlPointPosition(poR_id, poR2)
        F.GetNthControlPointPosition(poL_id, poL2)
        F.GetNthControlPointPosition(zyo_id, zyo2)

        poR2 = vTransform.GetMatrix().MultiplyPoint([poR2[0], poR2[1], poR2[2], 0])
        poL2 = vTransform.GetMatrix().MultiplyPoint([poL2[0], poL2[1], poL2[2], 0])
        zyo2 = vTransform.GetMatrix().MultiplyPoint([zyo2[0], zyo2[1], zyo2[2], 0])

        po = [poR2[0] - poL2[0], poR2[1] - poL2[1], poR2[2] - poL2[2]]

        # -----------------------
        # 2) Roll (RotateY)
        # -----------------------
        vTransform2 = vtk.vtkTransform()
        vTransform2.RotateY(np.arctan2(po[2], po[0]) * 180 / np.pi)

        transform2 = slicer.vtkMRMLLinearTransformNode()
        scene.AddNode(transform2)
        transform2.SetName("FHP_Alignment_Roll")
        transform2.SetMatrixTransformToParent(vTransform2.GetMatrix())

        # Apply hierarchy: transform (yaw) under transform2 (roll)
        transform.SetAndObserveTransformNodeID(transform2.GetID())

        # -----------------------
        # Get coords again after roll
        # -----------------------
        poR3 = [0, 0, 0]
        poL3 = [0, 0, 0]
        zyo3 = [0, 0, 0]
        F.GetNthControlPointPosition(poR_id, poR3)
        F.GetNthControlPointPosition(poL_id, poL3)
        F.GetNthControlPointPosition(zyo_id, zyo3)

        poR3 = vTransform.GetMatrix().MultiplyPoint([poR3[0], poR3[1], poR3[2], 0])
        poL3 = vTransform.GetMatrix().MultiplyPoint([poL3[0], poL3[1], poL3[2], 0])
        zyo3 = vTransform.GetMatrix().MultiplyPoint([zyo3[0], zyo3[1], zyo3[2], 0])

        poR3 = vTransform2.GetMatrix().MultiplyPoint([poR3[0], poR3[1], poR3[2], 0])
        poL3 = vTransform2.GetMatrix().MultiplyPoint([poL3[0], poL3[1], poL3[2], 0])
        zyo3 = vTransform2.GetMatrix().MultiplyPoint([zyo3[0], zyo3[1], zyo3[2], 0])

        # Vector for pitch: from midpoint of porions to zyoL
        po_zyo = [
            zyo3[0] - (poR3[0] + poL3[0]) / 2,
            zyo3[1] - (poR3[1] + poL3[1]) / 2,
            zyo3[2] - (poR3[2] + poL3[2]) / 2,
        ]

        # -----------------------
        # 3) Pitch (RotateX)
        # -----------------------
        vTransform3 = vtk.vtkTransform()
        vTransform3.RotateX(-np.arctan2(po_zyo[2], po_zyo[1]) * 180 / np.pi)

        transform3 = slicer.vtkMRMLLinearTransformNode()
        scene.AddNode(transform3)
        transform3.SetName("FHP_Alignment_Pitch")
        transform3.SetMatrixTransformToParent(vTransform3.GetMatrix())

        # Apply hierarchy: roll under pitch
        transform2.SetAndObserveTransformNodeID(transform3.GetID())

        # Harden transform on volume (like your script)
        if V:
            slicer.vtkSlicerTransformLogic().hardenTransform(V)

        slicer.util.delayDisplay(
            "Applied full FHP alignment (yaw + roll + pitch) using labels: poR, poL, zyoL.\n"
            "Transform hardened on the volume (if a volume was loaded)."
        )

    except Exception as e:
        slicer.util.errorDisplay(f"Failed to apply full FHP alignment (001):\n{e}")

# ============================================================
# Step 2: Load anatomical landmarks
# ============================================================

def download_and_load_anatomical_landmarks():
    try:
        path = download_file(ANATOMICAL_LANDMARKS_URL, "landmarks.json")
        slicer.util.loadMarkups(path)
        slicer.util.delayDisplay("Loaded landmarks.json. Place/verify landmarks, then click 'Create automatic linear measurements'.")
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to download/load landmarks.json:\n{e}")

# ============================================================
# Step 3: Automatic linear measurements (label-based)
# ============================================================

def create_linear_measurements():
    
    try:
        # Prefer the node named exactly 'landmarks'
        try:
            F = slicer.util.getNode("landmarks")
        except slicer.util.MRMLNodeNotFoundException:
            F = None

        # Fallback: try to find a fiducial list that looks like the anatomical list
        if not F:
            F = find_fiducial_node_with_labels(["n", "gn", "zyL", "zyR"])

        if not F:
            slicer.util.errorDisplay(
                "Could not find the anatomical landmarks node.\n"
                "Please load landmarks.json and make sure the node is named 'landmarks'."
            )
            return

        if F.GetClassName() != "vtkMRMLMarkupsFiducialNode":
            slicer.util.errorDisplay(f"Node 'landmarks' is not a fiducial list (it is {F.GetClassName()}).")
            return

        measurements = [
            ("Bizygomatic Breadth", "zyR", "zyL"),
            ("Facial Height", "n", "gn"),
            ("Superior Facial Height", "n", "pr"),
            ("Maximum Cranial Length", "g", "op"),
            ("Maximum Cranial Breadth", "euR", "euL"),
            ("Intercondylar Breadth", "cdmR", "cdmL"),
            ("Bigonial Breadth", "goR", "goL"),
            ("Anterior Height", "id", "gn"),
            ("Cranial base length", "n", "ba"),
            ("Basion-bregmatic height", "ba", "b"),
            ("Facial length", "ba", "pr"),
            ("Biauricular breadth", "auR", "auL"),
            ("Mastoid breadth", "msR", "msL"),
            ("Upper facial breadth", "fmtR", "fmtL"),
            ("Minimum frontal breadth", "ftR", "ftL"),
            ("Maximum frontal breadth", "coR", "coL"),
            ("Maximum occipital breadth", "astR", "astL"),
            ("Biorbital breadth", "ekR", "ekL"),
            ("Left Orbital Breadth", "mfL", "ekL"),
            ("Right Orbital Breadth", "mfR", "ekR"),
            ("Nasal Height", "n", "ns"),
            ("Nasal Breadth", "alR", "alL"),
            ("Minimum cranial breadth", "itR", "itL"),
            ("Palatal length", "ol", "pns"),
            ("Palatal breadth", "enmR", "enmL"),
            ("Bicondylar breadth", "kdlR", "kdlL"),
            ("Muscular process breadth", "krL", "krR"),
            ("Left Ramus height", "kdsL", "goL"),
            ("Right Ramus height", "kdsR", "goR"),
            ("Chin height", "id", "gn"),
        ]

        created = 0
        skipped = 0

        for name, a, b in measurements:
            p1 = get_landmark_point(F, a)
            p2 = get_landmark_point(F, b)
            if p1 is None or p2 is None:
                skipped += 1
                continue

            lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
            lineNode.SetName(name)
            lineNode.AddControlPoint(p1)
            lineNode.AddControlPoint(p2)

            # Optional usability: hide result until complete (it is complete already, but consistent with manual nodes)
            try:
                lineNode.GetMeasurement("length").SetEnabled(False)
            except Exception:
                pass

            created += 1

        # Mandibular body length: midpoint(goL, goR) to pog
        goL = get_landmark_point(F, "goL")
        goR = get_landmark_point(F, "goR")
        pog = get_landmark_point(F, "pog")

        if goL is not None and goR is not None and pog is not None:
            midpoint = [
                (goL[0] + goR[0]) / 2,
                (goL[1] + goR[1]) / 2,
                (goL[2] + goR[2]) / 2,
            ]

            midNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
            midNode.SetName("goR goL midpoint")
            midNode.AddControlPoint(midpoint[0], midpoint[1], midpoint[2])

            lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
            lineNode.SetName("Mandibular body length")
            lineNode.AddControlPoint(pog)
            lineNode.AddControlPoint(midpoint)
            created += 1
        else:
            skipped += 1

        slicer.util.delayDisplay(
            f"Created {created} automatic linear measurement line nodes.\n"
            f"Skipped {skipped} (missing landmarks)."
        )

    except Exception as e:
        slicer.util.errorDisplay(f"Failed to create linear measurements:\n{e}")

# ============================================================
# Step 4: Angles + manual lines
# ============================================================

def create_gonial_angle_l():
    try:
        F = find_fiducial_node_with_labels(["goL"])
        if not F:
            slicer.util.errorDisplay("Cannot find landmark 'goL'. Load landmarks.json first.")
            return

        goL = get_landmark_point(F, "goL")
        if goL is None:
            slicer.util.errorDisplay("Landmark 'goL' not found.")
            return

        A = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode")
        A.SetName("Gonial angle L")
        A.AddControlPoint([3, 3, 3])        # placeholder 1 (user adjusts)
        A.AddControlPoint(goL)              # vertex
        A.AddControlPoint([-1, 5, 130])     # placeholder 2 (user adjusts)

        slicer.util.delayDisplay("Created 'Gonial angle L'. Adjust control points 1 and 3 manually.")
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to create Gonial angle L:\n{e}")

def create_mental_angle():
    try:
        F = find_fiducial_node_with_labels(["id", "gn", "goL"])
        if not F:
            slicer.util.errorDisplay("Cannot find required landmarks for Mental angle: id, gn, goL.")
            return

        p_id = get_landmark_point(F, "id")
        p_gn = get_landmark_point(F, "gn")
        p_goL = get_landmark_point(F, "goL")
        if p_id is None or p_gn is None or p_goL is None:
            slicer.util.errorDisplay("Missing one of required landmarks: id, gn, goL.")
            return

        A = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode")
        A.SetName("Mental angle")
        A.AddControlPoint(p_id)
        A.AddControlPoint(p_gn)  # vertex
        A.AddControlPoint(p_goL)

        slicer.util.delayDisplay("Created 'Mental angle' (id → gn → goL).")
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to create Mental angle:\n{e}")

def create_empty_manual_measurement_nodes():
    
    try:
        manualMeasurements = [
            ("R Maximum Zygomatic Thickness", "The thickest point of the RIGHT zygomatic arch"),
            ("R Minimum Zygomatic Thickness", "The narrowest point of the RIGHT zygomatic arch."),
            ("L Maximum Zygomatic Thickness", "The thickest point of the LEFT zygomatic arch"),
            ("L Minimum Zygomatic Thickness", "The narrowest point of the LEFT zygomatic arch."),
            ("Ramus Breadth", "The narrowest point of the LEFT ramus of the mandible."),
        ]

        # Index existing line nodes by name
        existing = {n.GetName(): n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")}

        created = 0
        reused = 0

        for name, desc in manualMeasurements:
            lineNode = existing.get(name)
            if not lineNode:
                lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
                lineNode.SetName(name)
                created += 1
            else:
                reused += 1

            # Ensure the line is EMPTY (remove any existing control points)
            for i in range(lineNode.GetNumberOfControlPoints() - 1, -1, -1):
                lineNode.RemoveNthControlPoint(i)

            # Set description (shows in Data module, and can be used as guidance)
            try:
                lineNode.SetDescription(desc)
            except Exception:
                pass

            # Improve usability
            lineNode.CreateDefaultDisplayNodes()
            dn = lineNode.GetDisplayNode()
            if dn:
                dn.SetGlyphTypeFromString("CrossDot2D")
                dn.SetPointLabelsVisibility(False)
                dn.SetPropertiesLabelVisibility(True)

            # Hide measurement result until 2 points are placed (optional)
            try:
                lineNode.GetMeasurement("length").SetEnabled(False)
            except Exception:
                pass

        slicer.util.delayDisplay(
            f"Manual measurement line nodes ready.\n"
            f"Created: {created}, already existed: {reused}\n"
            "Now place 2 points on each line in the Markups module."
        )

    except Exception as e:
        slicer.util.errorDisplay(f"Failed to create manual measurement nodes:\n{e}")

# ============================================================
# Step 5: Copy buttons
# ============================================================

def copy_linear_measurements_to_clipboard():
    try:
        rows = []
        lineNodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")

        for lineNode in lineNodes:
            if lineNode.GetNumberOfDefinedControlPoints() < 2:
                continue

            try:
                lineNode.GetMeasurement("length").SetEnabled(True)
                length = lineNode.GetMeasurement("length").GetValue()
            except Exception:
                continue

            imagePath = "(unknown)"
            try:
                assocId = lineNode.GetNthControlPointAssociatedNodeID(0)
                volumeNode = slicer.mrmlScene.GetNodeByID(assocId) if assocId else None
                if volumeNode and volumeNode.GetStorageNode():
                    imagePath = volumeNode.GetStorageNode().GetFileName()
            except Exception:
                pass

            rows.append("\t".join([imagePath, lineNode.GetName(), f"{length}"]))

        slicer.app.clipboard().setText("\n".join(rows) + "\n")
        slicer.util.delayDisplay(f"Copied {len(rows)} linear measurements to clipboard.")
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to copy linear measurements:\n{e}")

def copy_angle_measurements_to_clipboard():
    try:
        rows = []
        angleNodes = slicer.util.getNodesByClass("vtkMRMLMarkupsAngleNode")

        for angleNode in angleNodes:
            if angleNode.GetNumberOfControlPoints() < 3:
                continue

            p1 = [0, 0, 0]
            p2 = [0, 0, 0]
            p3 = [0, 0, 0]
            angleNode.GetNthControlPointPosition(0, p1)
            angleNode.GetNthControlPointPosition(1, p2)
            angleNode.GetNthControlPointPosition(2, p3)

            v1 = np.array([p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]], dtype=float)
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2]], dtype=float)

            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)
            if n1 == 0 or n2 == 0:
                continue

            v1 /= n1
            v2 /= n2
            dot = float(np.clip(np.dot(v1, v2), -1.0, 1.0))
            angle_deg = float(np.degrees(np.arccos(dot)))

            imageName = "(none)"
            try:
                assocId = angleNode.GetNthControlPointAssociatedNodeID(0)
                volumeNode = slicer.mrmlScene.GetNodeByID(assocId) if assocId else None
                if volumeNode:
                    imageName = volumeNode.GetName()
            except Exception:
                pass

            rows.append("\t".join([imageName, angleNode.GetName(), f"{angle_deg:.2f}"]))

        slicer.app.clipboard().setText("\n".join(rows) + "\n")
        slicer.util.delayDisplay(f"Copied {len(rows)} angle measurements to clipboard.")
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to copy angle measurements:\n{e}")

# ============================================================
# GUI window
# ============================================================

def build_gui():
    global mandibular_cranial_gui_window

    mandibular_cranial_gui_window = qt.QWidget()
    mandibular_cranial_gui_window.setWindowTitle("Mandibular and Cranial Measurements")
    mandibular_cranial_gui_window.setMinimumWidth(860)
    mandibular_cranial_gui_window.setMinimumHeight(920)

    layout = qt.QVBoxLayout(mandibular_cranial_gui_window)

    layout.addWidget(qt.QLabel("<h2>Mandibular and Cranial Measurements</h2>"))
    intro = qt.QLabel(
        "Follow the steps in order. If something is missing, check that the correct landmarks are placed.\n"
        "When finished, use the Copy buttons to paste results into Excel."
    )
    intro.setWordWrap(True)
    layout.addWidget(intro)

    # Step 1
    g1 = qt.QGroupBox("Step 1: FHP alignment (download FHP_landmarks.json → place → align)")
    g1l = qt.QVBoxLayout(g1)
    b1 = qt.QPushButton("Download + Load FHP_landmarks.json")
    b1.clicked.connect(download_and_load_fhp_landmarks)
    g1l.addWidget(b1)

    b2 = qt.QPushButton("Apply FHP alignment (001: yaw + roll + pitch + harden)")
    b2.clicked.connect(apply_fhp_alignment_full_001)
    g1l.addWidget(b2)
    layout.addWidget(g1)

    # Step 2
    g2 = qt.QGroupBox("Step 2: Download + load anatomical landmarks (landmarks.json)")
    g2l = qt.QVBoxLayout(g2)
    b3 = qt.QPushButton("Download + Load landmarks.json")
    b3.clicked.connect(download_and_load_anatomical_landmarks)
    g2l.addWidget(b3)
    layout.addWidget(g2)

    # Step 3
    g3 = qt.QGroupBox("Step 3: Automatic linear measurements")
    g3l = qt.QVBoxLayout(g3)
    b4 = qt.QPushButton("Create automatic linear measurements (lines)")
    b4.clicked.connect(create_linear_measurements)
    g3l.addWidget(b4)
    layout.addWidget(g3)

    # Step 4
    g4 = qt.QGroupBox("Step 4: Angles + manual measurements")
    g4l = qt.QVBoxLayout(g4)

    b5 = qt.QPushButton("Create Gonial angle L (then manually adjust points 1 and 3)")
    b5.clicked.connect(create_gonial_angle_l)
    g4l.addWidget(b5)

    b6 = qt.QPushButton("Create Mental angle (id → gn → goL)")
    b6.clicked.connect(create_mental_angle)
    g4l.addWidget(b6)

    b7 = qt.QPushButton("Create empty manual measurement line nodes (with descriptions)")
    b7.clicked.connect(create_empty_manual_measurement_nodes)
    g4l.addWidget(b7)

    manualText = qt.QLabel(
        "Manual lines to fill (place 2 points each):\n"
        "• R Maximum Zygomatic Thickness\n"
        "• R Minimum Zygomatic Thickness\n"
        "• L Maximum Zygomatic Thickness\n"
        "• L Minimum Zygomatic Thickness\n"
        "• Ramus Breadth"
    )
    manualText.setWordWrap(True)
    g4l.addWidget(manualText)

    layout.addWidget(g4)

    # Step 5
    g5 = qt.QGroupBox("Step 5: Copy measurements to clipboard (paste into Excel)")
    g5l = qt.QVBoxLayout(g5)
    row = qt.QHBoxLayout()

    c1 = qt.QPushButton("Copy linear measurements")
    c1.clicked.connect(copy_linear_measurements_to_clipboard)
    row.addWidget(c1)

    c2 = qt.QPushButton("Copy angles")
    c2.clicked.connect(copy_angle_measurements_to_clipboard)
    row.addWidget(c2)

    g5l.addLayout(row)
    layout.addWidget(g5)

    layout.addStretch(1)
    mandibular_cranial_gui_window.show()

# Run
build_gui()

```
