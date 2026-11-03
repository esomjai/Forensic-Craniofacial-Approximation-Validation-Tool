[Right Ramus Breadth.mrk.json](https://github.com/user-attachments/files/29254437/Right.Ramus.Breadth.mrk.json)


[Right Minimum zygomatic thickness.mrk.json](https://github.com/user-attachments/files/29254436/Right.Minimum.zygomatic.thickness.mrk.json)


[Right Maximum zygomatic thickness.mrk.json](https://github.com/user-attachments/files/29254435/Right.Maximum.zygomatic.thickness.mrk.json)


[Left Ramus Breadth.mrk.json](https://github.com/user-attachments/files/29254434/Left.Ramus.Breadth.mrk.json)


[Left Minimum zygomatic thickness.mrk.json](https://github.com/user-attachments/files/29254432/Left.Minimum.zygomatic.thickness.mrk.json)


[Left Maximum zygomatic thickness.mrk.json](https://github.com/user-attachments/files/29254431/Left.Maximum.zygomatic.thickness.mrk.json)


[landmarks.mrk.json](https://github.com/user-attachments/files/29254430/landmarks.mrk.json)

```python
"""
Mandibular and Cranial Measurements GUI for 3D Slicer
Copy-paste this entire script into the 3D Slicer Python Interactor and run.

Workflow (beginner-friendly):
1) Download + load landmarks.json (for landmark placement/measurements)
2) Create empty manual line measurements using your provided .mrk.json templates + descriptions
3) Create automatic linear measurements (label-based)
4) Generate comparison table with true vs predicted values
5) Copy linear measurements to clipboard (paste into Excel)

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
# URLs (updated with your new file links)
# ============================================================

ANATOMICAL_LANDMARKS_URL = "https://github.com/user-attachments/files/29254430/landmarks.mrk.json"

MANUAL_TEMPLATE_URLS = {
    "L Maximum Zygomatic Thickness": "https://github.com/user-attachments/files/29254431/Left.Maximum.zygomatic.thickness.mrk.json",
    "L Minimum Zygomatic Thickness": "https://github.com/user-attachments/files/29254432/Left.Minimum.zygomatic.thickness.mrk.json",
    "R Maximum Zygomatic Thickness": "https://github.com/user-attachments/files/29254435/Right.Maximum.zygomatic.thickness.mrk.json",
    "R Minimum Zygomatic Thickness": "https://github.com/user-attachments/files/29254436/Right.Minimum.zygomatic.thickness.mrk.json",
    "L Ramus Breadth": "https://github.com/user-attachments/files/29254434/Left.Ramus.Breadth.mrk.json",
    "R Ramus Breadth": "https://github.com/user-attachments/files/29254437/Right.Ramus.Breadth.mrk.json",
}

MANUAL_DESCRIPTIONS = {
    "R Maximum Zygomatic Thickness": "The thickest point of the RIGHT zygomatic arch",
    "R Minimum Zygomatic Thickness": "The narrowest point of the RIGHT zygomatic arch.",
    "L Maximum Zygomatic Thickness": "The thickest point of the LEFT zygomatic arch",
    "L Minimum Zygomatic Thickness": "The narrowest point of the LEFT zygomatic arch.",
    "L Ramus Breadth": "The narrowest point of the LEFT ramus of the mandible.",
    "R Ramus Breadth": "The narrowest point of the RIGHT ramus of the mandible.",
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
        # Get all labels from this node
        labels = set()
        for i in range(n.GetNumberOfControlPoints()):
            label = n.GetNthControlPointLabel(i)
            if label:
                labels.add(label)
        
        # Check if all required labels are present
        if all(lbl in labels for lbl in required_labels):
            return n
    return None

def get_all_landmark_labels(markups_node):
    """Get all labels from a markups node"""
    labels = []
    for i in range(markups_node.GetNumberOfControlPoints()):
        label = markups_node.GetNthControlPointLabel(i)
        if label:
            labels.append(label)
    return labels

def get_landmark_point(markups_node, label):
    idx = markups_node.GetControlPointIndexByLabel(label)
    if idx < 0:
        return None
    return markups_node.GetNthControlPointPositionVector(idx)

def get_measurement_value(measurement_name):
    """Get the value of a measurement by name"""
    try:
        # Try to find line node
        lineNode = slicer.util.getNode(measurement_name)
        if lineNode and lineNode.GetClassName() == "vtkMRMLMarkupsLineNode":
            if lineNode.GetNumberOfDefinedControlPoints() >= 2:
                lineNode.GetMeasurement("length").SetEnabled(True)
                return lineNode.GetMeasurement("length").GetValue()
    except:
        pass
    return None

# ============================================================
# Step 1: Load anatomical landmarks
# ============================================================

def download_and_load_anatomical_landmarks():
    try:
        path = download_file(ANATOMICAL_LANDMARKS_URL, "landmarks.mrk.json")
        loaded_nodes = slicer.util.loadMarkups(path)
        slicer.util.delayDisplay("Loaded landmarks.mrk.json. Place/verify landmarks, then create measurements.")
        
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to download/load landmarks.mrk.json:\n{e}")

# ============================================================
# Step 2: Create empty manual measurement nodes
# ============================================================

def create_empty_manual_measurement_nodes():
    """
    Creates empty manual line measurement nodes using the provided templates
    """
    try:
        manualMeasurements = [
            ("R Maximum Zygomatic Thickness", "The thickest point of the RIGHT zygomatic arch"),
            ("R Minimum Zygomatic Thickness", "The narrowest point of the RIGHT zygomatic arch."),
            ("L Maximum Zygomatic Thickness", "The thickest point of the LEFT zygomatic arch"),
            ("L Minimum Zygomatic Thickness", "The narrowest point of the LEFT zygomatic arch."),
            ("L Ramus Breadth", "The narrowest point of the LEFT ramus of the mandible."),
            ("R Ramus Breadth", "The narrowest point of the RIGHT ramus of the mandible."),
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

            # Set description
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

            # Hide measurement result until 2 points are placed
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
# Step 3: Automatic linear measurements (label-based)
# ============================================================

def create_linear_measurements():
    
    try:
        # Get ALL fiducial nodes
        all_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")
        if not all_nodes:
            slicer.util.errorDisplay("No fiducial nodes found in the scene. Please load landmarks.mrk.json first.")
            return
        
        # Try to find the landmarks node
        F = None
        
        # First preference: node named exactly 'landmarks'
        try:
            F = slicer.util.getNode("landmarks")
        except slicer.util.MRMLNodeNotFoundException:
            pass
        
        # Second preference: node with most landmarks
        if not F:
            max_labels = 0
            for n in all_nodes:
                labels = get_all_landmark_labels(n)
                if len(labels) > max_labels:
                    max_labels = len(labels)
                    F = n
        
        # Third preference: any node that contains essential landmarks
        if not F:
            essential = ["g", "gn", "id", "n", "zyL", "zyR"]
            F = find_fiducial_node_with_labels(essential)
        
        if not F:
            slicer.util.errorDisplay(
                "Could not find the anatomical landmarks node.\n"
                "Please load landmarks.mrk.json first.\n\n"
                "Make sure the node contains landmarks with labels like: g, gn, id, n, zyL, zyR"
            )
            return

        if F.GetClassName() != "vtkMRMLMarkupsFiducialNode":
            slicer.util.errorDisplay(f"Node '{F.GetName()}' is not a fiducial list (it is {F.GetClassName()}).")
            return

        # Get all available labels from the chosen node
        available_labels = set(get_all_landmark_labels(F))

        # Define all measurements with their required landmarks
        measurements = [
            # Cranial measurements
            ("Maximum Cranial Length", "g", "op"),
            ("Bizygomatic Breadth", "zyR", "zyL"),
            ("Superior Facial Height", "n", "pr"),
            ("Facial Length", "ba", "pr"),
            ("Basion-bregmatic height", "ba", "b"),
            
            # Palatal
            ("Palatal Length", "ol", "pns"),
            
            # Mandibular measurements
            ("Bicondylar Breadth", "kdlR", "kdlL"),
            ("Muscular process breadth", "krL", "krR"),
            ("Bigonial Breadth", "goR", "goL"),
            ("Anterior Height", "id", "gn"),
            
            # Ramus and condylar measurements
            ("Left Ramus height", "kdsL", "goL"),
            ("Right Ramus height", "kdsR", "goR"),
            ("Left Condylar height", "kdsL", "irbL"),
            ("Right Condylar height", "kdsR", "irbR"),
            
            # Temporal fossa
            ("Intertemporal fossa distance", "itR", "itL"),
            
            # Corpus length measurements
            ("Left Corpus length", "kdpL", "irbL"),
            ("Right Corpus length", "kdpR", "irbR"),
        ]

        created = 0
        skipped = 0
        missing_labels = set()

        for name, a, b in measurements:
            # Check if landmarks exist
            has_a = a in available_labels
            has_b = b in available_labels
            
            if not has_a or not has_b:
                skipped += 1
                if not has_a:
                    missing_labels.add(a)
                if not has_b:
                    missing_labels.add(b)
                continue

            p1 = get_landmark_point(F, a)
            p2 = get_landmark_point(F, b)
            
            if p1 is None or p2 is None:
                skipped += 1
                continue

            lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
            lineNode.SetName(name)
            lineNode.AddControlPoint(p1)
            lineNode.AddControlPoint(p2)

            try:
                lineNode.GetMeasurement("length").SetEnabled(False)
            except Exception:
                pass

            created += 1

        # Mandibular body length: midpoint(goL, goR) to pog
        goL_avail = "goL" in available_labels
        goR_avail = "goR" in available_labels
        pog_avail = "pog" in available_labels

        if goL_avail and goR_avail and pog_avail:
            goL = get_landmark_point(F, "goL")
            goR = get_landmark_point(F, "goR")
            pog = get_landmark_point(F, "pog")

            if goL is not None and goR is not None and pog is not None:
                midpoint = [
                    (goL[0] + goR[0]) / 2,
                    (goL[1] + goR[1]) / 2,
                    (goL[2] + goR[2]) / 2,
                ]

                # Create midpoint as fiducial (hidden using display node)
                midNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
                midNode.SetName("goR goL midpoint")
                midNode.AddControlPoint(midpoint[0], midpoint[1], midpoint[2])
                # Hide the node using its display node
                midNode.CreateDefaultDisplayNodes()
                displayNode = midNode.GetDisplayNode()
                if displayNode:
                    displayNode.SetVisibility(False)

                lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")
                lineNode.SetName("Mandibular body length")
                lineNode.AddControlPoint(pog)
                lineNode.AddControlPoint(midpoint)
                created += 1
            else:
                skipped += 1
        else:
            skipped += 1
            if not goL_avail:
                missing_labels.add("goL")
            if not goR_avail:
                missing_labels.add("goR")
            if not pog_avail:
                missing_labels.add("pog")

        # Summary message
        if missing_labels:
            unique_missing = sorted(missing_labels)
            message = (
                f"Created {created} automatic linear measurement line nodes.\n"
                f"Skipped {skipped} (missing landmarks).\n\n"
                f"Missing landmark labels: {', '.join(unique_missing)}\n\n"
                f"Please ensure all required landmarks are placed."
            )
            slicer.util.delayDisplay(message)
        else:
            slicer.util.delayDisplay(
                f"Created {created} automatic linear measurement line nodes.\n"
                f"All measurements completed successfully!"
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        slicer.util.errorDisplay(f"Failed to create linear measurements:\n{e}")

# ============================================================
# Step 4: Comparison Table with Predictions
# ============================================================

def generate_comparison_table():
    """
    Generate a comparison table with true (measured) and predicted values
    Copies tab-separated table to clipboard for Excel
    """
    try:
        # Get all measured values
        values = {}
        
        # Define measurement name mappings (handling variations)
        name_mappings = {
            "Right Minimum zygomatic thickness": "R Minimum Zygomatic Thickness",
            "Right Maximum zygomatic thickness": "R Maximum Zygomatic Thickness",
            "Left Minimum zygomatic thickness": "L Minimum Zygomatic Thickness",
            "Left Maximum zygomatic thickness": "L Maximum Zygomatic Thickness",
            "Right Ramus Breadth": "R Ramus Breadth",
            "Left Ramus Breadth": "L Ramus Breadth",
            "R Minimum Zygomatic Thickness": "R Minimum Zygomatic Thickness",
            "R Maximum Zygomatic Thickness": "R Maximum Zygomatic Thickness",
            "L Minimum Zygomatic Thickness": "L Minimum Zygomatic Thickness",
            "L Maximum Zygomatic Thickness": "L Maximum Zygomatic Thickness",
        }
        
        # Get all line nodes in the scene
        all_line_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
        
        # First, get all measurements from line nodes
        for lineNode in all_line_nodes:
            node_name = lineNode.GetName()
            if lineNode.GetNumberOfDefinedControlPoints() >= 2:
                try:
                    lineNode.GetMeasurement("length").SetEnabled(True)
                    val = lineNode.GetMeasurement("length").GetValue()
                    
                    # Check if this node name matches any of our expected names (with variations)
                    matched = False
                    for key, standard_name in name_mappings.items():
                        if node_name == key or node_name == standard_name:
                            values[standard_name] = val
                            matched = True
                            break
                    
                    # If no match found in mappings, try direct match with our standard names
                    if not matched:
                        standard_names = [
                            "Maximum Cranial Length", "Bizygomatic Breadth", "Superior Facial Height",
                            "Facial Length", "Basion-bregmatic height", "Palatal Length",
                            "Bicondylar Breadth", "Muscular process breadth", "Bigonial Breadth",
                            "Anterior Height", "Left Ramus height", "Right Ramus height",
                            "Left Condylar height", "Right Condylar height", "Intertemporal fossa distance",
                            "Left Corpus length", "Right Corpus length", "Mandibular body length"
                        ]
                        if node_name in standard_names:
                            values[node_name] = val
                except:
                    pass
        
        # Check if we have all required values for predictions
        required_for_ide = [
            "L Minimum Zygomatic Thickness", 
            "R Minimum Zygomatic Thickness", 
            "L Maximum Zygomatic Thickness", 
            "R Maximum Zygomatic Thickness",
            "Superior Facial Height",
            "Intertemporal fossa distance"
        ]
        required_for_namiki = [
            "Bizygomatic Breadth",
            "Intertemporal fossa distance",  # minimum cranial breadth
            "Facial Length",
            "Basion-bregmatic height",
            "Superior Facial Height",
            "Maximum Cranial Length",
            "Palatal Length"
        ]
        
        # Check Ide requirements
        ide_missing = [v for v in required_for_ide if v not in values]
        namiki_missing = [v for v in required_for_namiki if v not in values]
        
        if ide_missing:
            error_msg = (
                f"Missing values for Ide predictions. Please ensure these measurements are completed:\n\n"
                f"Missing measurements:\n"
                f"• {', '.join(ide_missing)}\n\n"
                f"These are manual measurements that need to be placed in the Markups module.\n"
                f"Please place 2 points for each of these measurements and try again."
            )
            slicer.util.delayDisplay(error_msg)
            return
            
        if namiki_missing:
            error_msg = (
                f"Missing values for Namiki predictions. Please ensure these measurements are completed:\n\n"
                f"Missing measurements:\n"
                f"• {', '.join(namiki_missing)}\n\n"
                f"These are automatic measurements that need to be created.\n"
                f"Please run 'Create automatic linear measurements' first."
            )
            slicer.util.delayDisplay(error_msg)
            return
        
        # Calculate predicted values using exact measurement names
        
        # Ide predictions
        L_min_zygo = values["L Minimum Zygomatic Thickness"]
        R_min_zygo = values["R Minimum Zygomatic Thickness"]
        L_max_zygo = values["L Maximum Zygomatic Thickness"]
        R_max_zygo = values["R Maximum Zygomatic Thickness"]
        sfh = values["Superior Facial Height"]
        itfd = values["Intertemporal fossa distance"]
        
        # Predicted Anterior Height (CH in Namiki)
        predicted_anterior_height = 21.33 + (-0.21 * L_min_zygo) + (0.64 * R_min_zygo) + (-0.01 * L_max_zygo) + (0.24 * R_max_zygo)
        
        # Predicted Condylar Height (using Left Corpus length as the true measure - OUR definition)
        predicted_condylar_height = 18.06 + (0.9 * sfh) + (0.36 * itfd)
        
        # Predicted Corpus Length (Mandibular body length in Namiki)
        predicted_corpus_length = 43.01 + (0.17 * sfh) + (0.32 * itfd)
        
        # Namiki predictions
        bzb = values["Bizygomatic Breadth"]
        micb = values["Intertemporal fossa distance"]  # minimum cranial breadth
        fl = values["Facial Length"]
        bbh = values["Basion-bregmatic height"]
        macl = values["Maximum Cranial Length"]
        pl = values["Palatal Length"]
        
        predicted_bcb = 0.760 * bzb + 22.144
        predicted_mpb = 0.469 * bzb + 0.136 * micb + 25.306
        predicted_bgb = 0.736 * bzb - 1.193
        predicted_mbl = 0.499 * fl + 0.234 * bbh - 8.570
        predicted_rh = 0.194 * bzb + 0.351 * sfh + 0.148 * macl + 0.218 * fl - 40.156
        predicted_rb = 0.240 * fl + 0.095 * bzb - 4.144
        predicted_ch = 0.279 * sfh + 0.215 * pl + 0.066 - 6.967
        
        # Calculate averages for RH and RB
        L_RH = values.get("Left Ramus height")
        R_RH = values.get("Right Ramus height")
        L_RB = values.get("L Ramus Breadth")
        R_RB = values.get("R Ramus Breadth")
        
        avg_RH = (L_RH + R_RH) / 2 if (L_RH is not None and R_RH is not None) else None
        avg_RB = (L_RB + R_RB) / 2 if (L_RB is not None and R_RB is not None) else None
        
        # Build comparison table with specified columns
        table_rows = []
        
        # Header
        table_rows.append("Predicted Distance Name\tName in Namiki\tName in Ide\tRegression Used\tPrediction Value (mm)\tTrue Value (mm)\tError (mm)")
        
        # Helper function to add rows
        def add_row(predicted_name, namiki_name, ide_name, regression, pred_val, true_val):
            if true_val is not None and pred_val is not None:
                error = true_val - pred_val
                table_rows.append(
                    f"{predicted_name}\t"
                    f"{namiki_name}\t"
                    f"{ide_name}\t"
                    f"{regression}\t"
                    f"{pred_val:.3f}\t"
                    f"{true_val:.3f}\t"
                    f"{error:.3f}"
                )
            elif true_val is not None:
                table_rows.append(
                    f"{predicted_name}\t"
                    f"{namiki_name}\t"
                    f"{ide_name}\t"
                    f"{regression}\t"
                    f"N/A\t"
                    f"{true_val:.3f}\t"
                    f"N/A"
                )
            elif pred_val is not None:
                table_rows.append(
                    f"{predicted_name}\t"
                    f"{namiki_name}\t"
                    f"{ide_name}\t"
                    f"{regression}\t"
                    f"{pred_val:.3f}\t"
                    f"N/A\t"
                    f"N/A"
                )
        
        # Ide predictions (with correct mappings)
        add_row(
            "Anterior Height", 
            "CH (Chin Height)", 
            "Anterior Height (id-gn)", 
            "Ide",
            predicted_anterior_height,
            values.get('Anterior Height', None)
        )
        
        add_row(
            "Condylar Height", 
            "Condylar Height (Namiki)", 
            "Corpus length (OUR definition: kdpL-irbL)", 
            "Ide",
            predicted_condylar_height,
            values.get('Left Corpus length', None)
        )
        
        add_row(
            "Corpus Length", 
            "MBL (Mandibular Body Length)", 
            "Mandibular body length (goL/R midpoint-pog)", 
            "Ide",
            predicted_corpus_length,
            values.get('Mandibular body length', None)
        )
        
        # Namiki predictions
        add_row(
            "Bicondylar Breadth", 
            "BCB", 
            "Bicondylar Breadth (kdlR-kdlL)", 
            "Namiki",
            predicted_bcb,
            values.get('Bicondylar Breadth', None)
        )
        
        add_row(
            "Muscular Process Breadth", 
            "MPB", 
            "Muscular process breadth (krL-krR)", 
            "Namiki",
            predicted_mpb,
            values.get('Muscular process breadth', None)
        )
        
        add_row(
            "Bigonial Breadth", 
            "BGB", 
            "Bigonial Breadth (goR-goL)", 
            "Namiki",
            predicted_bgb,
            values.get('Bigonial Breadth', None)
        )
        
        add_row(
            "Mandibular Body Length", 
            "MBL", 
            "Mandibular body length (goL/R midpoint-pog)", 
            "Namiki",
            predicted_mbl,
            values.get('Mandibular body length', None)
        )
        
        add_row(
            "Ramus Height", 
            "RH", 
            "Average of Left/Right Ramus height (kdsL-goL / kdsR-goR)", 
            "Namiki",
            predicted_rh,
            avg_RH
        )
        
        add_row(
            "Ramus Breadth", 
            "RB", 
            "Average of Left/Right Ramus Breadth", 
            "Namiki",
            predicted_rb,
            avg_RB
        )
        
        add_row(
            "Chin Height", 
            "CH", 
            "Anterior Height (id-gn)", 
            "Namiki",
            predicted_ch,
            values.get('Anterior Height', None)
        )
        
        # Combine all rows into single text
        clipboard_text = "\n".join(table_rows)
        
        # Copy to clipboard
        slicer.app.clipboard().setText(clipboard_text)
        
        # Show success message with mapping summary
        mapping_message = (
            "✅ Comparison table COPIED TO CLIPBOARD!\n\n"
            "Mappings used:\n"
            "• Anterior Height (id-gn) = CH (Chin Height)\n"
            "• Condylar Height = Corpus length (OUR definition: kdpL-irbL)\n"
            "• Corpus Length = Mandibular body length (goL/R midpoint-pog)\n"
            "• Intertemporal fossa distance (it-it) = minimum cranial breadth\n"
            "• RH = Average of Left/Right Ramus height\n"
            "• RB = Average of Left/Right Ramus Breadth\n\n"
            "Columns:\n"
            "1. Predicted Distance Name\n"
            "2. Name in Namiki\n"
            "3. Name in Ide\n"
            "4. Regression Used\n"
            "5. Prediction Value (mm)\n"
            "6. True Value (mm)\n"
            "7. Error (mm)\n\n"
            "Table is tab-separated. Open Excel and use 'Paste' (Ctrl+V) to import."
        )
        slicer.util.delayDisplay(mapping_message)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        slicer.util.errorDisplay(f"Failed to generate comparison table:\n{e}")

# ============================================================
# Step 5: Copy linear measurements to clipboard
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

            rows.append("\t".join([imagePath, lineNode.GetName(), f"{length:.3f}"]))

        if rows:
            clipboard_text = "\n".join(rows)
            slicer.app.clipboard().setText(clipboard_text)
            slicer.util.delayDisplay(f"✅ Copied {len(rows)} linear measurements to clipboard.\nPaste into Excel (Ctrl+V).")
        else:
            slicer.util.delayDisplay("No completed linear measurements found to copy.")
            
    except Exception as e:
        slicer.util.errorDisplay(f"Failed to copy linear measurements:\n{e}")

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
    g1 = qt.QGroupBox("Step 1: Download + load anatomical landmarks (landmarks.mrk.json)")
    g1l = qt.QVBoxLayout(g1)
    b1 = qt.QPushButton("Download + Load landmarks.mrk.json")
    b1.clicked.connect(download_and_load_anatomical_landmarks)
    g1l.addWidget(b1)
    layout.addWidget(g1)

    # Step 2: Manual measurements
    g2 = qt.QGroupBox("Step 2: Create empty manual measurement line nodes")
    g2l = qt.QVBoxLayout(g2)
    
    b_manual = qt.QPushButton("Create empty manual measurement line nodes (with descriptions)")
    b_manual.clicked.connect(create_empty_manual_measurement_nodes)
    g2l.addWidget(b_manual)

    manualText = qt.QLabel(
        "Manual lines to fill (place 2 points each):\n"
        "• R Maximum Zygomatic Thickness\n"
        "• R Minimum Zygomatic Thickness\n"
        "• L Maximum Zygomatic Thickness\n"
        "• L Minimum Zygomatic Thickness\n"
        "• L Ramus Breadth\n"
        "• R Ramus Breadth"
    )
    manualText.setWordWrap(True)
    g2l.addWidget(manualText)
    layout.addWidget(g2)

    # Step 3: Automatic linear measurements
    g3 = qt.QGroupBox("Step 3: Automatic linear measurements")
    g3l = qt.QVBoxLayout(g3)
    b3 = qt.QPushButton("Create automatic linear measurements (lines)")
    b3.clicked.connect(create_linear_measurements)
    g3l.addWidget(b3)

    autoText = qt.QLabel(
        "Automatic measurements created:\n"
        "• Maximum Cranial Length (g-op)\n"
        "• Bizygomatic Breadth (zyR-zyL)\n"
        "• Superior Facial Height (n-pr)\n"
        "• Facial Length (ba-pr)\n"
        "• Basion-bregmatic height (ba-b)\n"
        "• Palatal Length (ol-pns)\n"
        "• Bicondylar Breadth (kdlR-kdlL)\n"
        "• Muscular process breadth (krL-krR)\n"
        "• Bigonial Breadth (goR-goL)\n"
        "• Anterior Height (id-gn)\n"
        "• Left Ramus height (kdsL-goL)\n"
        "• Right Ramus height (kdsR-goR)\n"
        "• Left Condylar height (kdsL-irbL)\n"
        "• Right Condylar height (kdsR-irbR)\n"
        "• Intertemporal fossa distance (itR-itL)\n"
        "• Left Corpus length (kdpL-irbL)\n"
        "• Right Corpus length (kdpR-irbR)\n"
        "• Mandibular body length (midpoint goL-goR to pog)"
    )
    autoText.setWordWrap(True)
    g3l.addWidget(autoText)
    layout.addWidget(g3)

    # Step 4: Comparison Table
    g4 = qt.QGroupBox("Step 4: Generate Comparison Table (True vs Predicted)")
    g4l = qt.QVBoxLayout(g4)
    b4 = qt.QPushButton("Generate Comparison Table (copies to clipboard)")
    b4.clicked.connect(generate_comparison_table)
    g4l.addWidget(b4)
    
    compText = qt.QLabel(
        "Generates comparison table with:\n"
        "• Ide predictions: Anterior Height, Condylar Height, Corpus Length\n"
        "• Namiki predictions: BCB, MPB, BGB, MBL, RH, RB, CH\n\n"
        "Table is copied to clipboard (tab-separated for Excel)"
    )
    compText.setWordWrap(True)
    g4l.addWidget(compText)
    layout.addWidget(g4)

    # Step 5: Copy buttons
    g5 = qt.QGroupBox("Step 5: Copy measurements to clipboard (paste into Excel)")
    g5l = qt.QVBoxLayout(g5)
    row = qt.QHBoxLayout()

    c1 = qt.QPushButton("Copy linear measurements")
    c1.clicked.connect(copy_linear_measurements_to_clipboard)
    row.addWidget(c1)

    g5l.addLayout(row)
    layout.addWidget(g5)

    layout.addStretch(1)
    mandibular_cranial_gui_window.show()

# Run
build_gui()
```


