```python
# ==================================================================
#  Bootstrap: load RStudio_wrapper from GitHub
# ==================================================================
import os, sys, importlib.util
import urllib.request
import tempfile

RSTUDIO_EXPORT_URL = (
    "https://raw.githubusercontent.com/esomjai/"
    "Forensic-Craniofacial-Approximation-Validation-Tool/"
    "refs/heads/basics/Start%20here%20/RStudio_wrapper.py"
)

def _load_rstudio_wrapper(url=RSTUDIO_EXPORT_URL):
    cache_dir = os.path.join(tempfile.gettempdir(),
                             "slicer_rstudio_wrapper")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "rStudio_wrapper.py")
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = r.read()
        with open(cache_file, "wb") as f:
            f.write(data)
        print(f"[rstudio_wrapper] downloaded {len(data)} bytes")
    except Exception as e:
        print(f"[rstudio_wrapper] download failed: {e}")
        if not os.path.exists(cache_file):
            print("[rstudio_wrapper] no cache; export button disabled")
            return None
    spec = importlib.util.spec_from_file_location(
        "rstudio_wrapper", cache_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules["rstudio_wrapper"] = module
    spec.loader.exec_module(module)
    return module

_rstudio_wrapper = _load_rstudio_wrapper()

import slicer
import qt
import numpy as np
import datetime
import vtk

class RyuGUI:
    def __init__(self):
        self.main_widget = qt.QWidget(slicer.util.mainWindow())
        self.main_widget.setWindowFlags(qt.Qt.Tool)
        self.main_widget.setObjectName("RyuGUIWidget")
        self.main_widget.setWindowTitle("Ryu et al.(2020) Nose Prediction")
        self.main_widget.setMinimumSize(400, 600)
        self.vbox = qt.QVBoxLayout(self.main_widget)

        title_label = qt.QLabel("Ryu et al.(2020) Nose Prediction Workflow")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 10px;")
        title_label.setAlignment(qt.Qt.AlignCenter)
        self.vbox.addWidget(title_label)

        self.steps_completed = {
            "planes": False,
            "hard_measurements": False,
            "predicted_lengths": False,
            "predicted_landmarks": False,
            "true_measurements": False,
            "errors": False
        }
        self.last_prediction_sex = None
        self.length_prediction_dialog = None
        self.current_stage = 1
        self.stage_widgets = {}

        # Create a stacked widget to hold different stages
        self.stage_stack = qt.QStackedWidget()
        self.vbox.addWidget(self.stage_stack)

        # STAGE 1
        stage1_container = qt.QWidget()
        stage1_main_layout = qt.QVBoxLayout(stage1_container)
        stage1_group = self.create_stage_group("Stage 1: Hard Tissue Setup")
        stage1_layout = stage1_group.layout()

        # Add download button for hard tissue sample
        download_hard_btn = qt.QPushButton("📥 Load Sample Hard Tissue Landmarks")
        download_hard_btn.setStyleSheet("background-color: #E3F2FD; padding: 8px; margin-bottom: 10px;")
        download_hard_btn.setToolTip("Download and load Ryu_hard_tissue.mrk.json with au_L and au_R landmarks directly into the scene")
        download_hard_btn.clicked.connect(lambda: self.download_and_load_landmarks(
            "https://github.com/user-attachments/files/24859018/Ryu_hard_tissue.mrk.json",
            "Ryu_hard_tissue"
        ))
        stage1_layout.addWidget(download_hard_btn)

        inputs_group1 = qt.QGroupBox("Input")
        inputs_layout1 = qt.QFormLayout(inputs_group1)
        self.hard_tissue_selector = self.create_node_selector("Hard Tissue Fiducials:", "vtkMRMLMarkupsFiducialNode", "Ryu_hard_tissue")
        inputs_layout1.addRow(self.hard_tissue_selector['label'], self.hard_tissue_selector['selector'])
        stage1_layout.addWidget(inputs_group1)
        workflow_group1 = self.create_step_group("Setup Workflow")
        workflow_layout1 = workflow_group1.layout()
        self.add_workflow_step(workflow_layout1, "<b>Step 1: Create Anatomical Planes</b>",
                            "Creates Midsagittal, Orbital, Coronal, Rhinion, and Alare Sagittal planes.",
                            self.create_anatomical_planes)
        self.add_workflow_step(workflow_layout1, "<b>Step 2: Create Hard Tissue Measurements</b>",
                            "Creates measurement lines (N1, N4, etc.) from hard tissue landmarks to planes (Cyan).",
                            self.create_hard_tissue_measurements, is_final_step=True)
        stage1_layout.addWidget(workflow_group1)
        stage1_main_layout.addWidget(stage1_group)
        stage1_main_layout.addStretch()

        # Navigation buttons for Stage 1
        nav_layout1 = qt.QHBoxLayout()
        nav_layout1.addStretch()
        next_btn1 = qt.QPushButton("Next: Stage 2 →")
        next_btn1.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 20px;")
        next_btn1.clicked.connect(lambda: self.go_to_stage(2))
        nav_layout1.addWidget(next_btn1)
        stage1_main_layout.addLayout(nav_layout1)

        self.stage_stack.addWidget(stage1_container)
        self.stage_widgets[1] = stage1_container

        # STAGE 2
        stage2_container = qt.QWidget()
        stage2_main_layout = qt.QVBoxLayout(stage2_container)
        stage2_group = self.create_stage_group("Stage 2: Soft Tissue Prediction")
        stage2_layout = stage2_group.layout()
        self.add_workflow_step(stage2_layout, "<b>Step 3: Predict Soft Tissue Lengths</b>",
                            "Calculates soft tissue measurement lengths and creates 'Predicted' (blue) lines.",
                            self.launch_length_prediction_dialog)
        self.add_workflow_step(stage2_layout, "<b>Step 4: Create Predicted Landmarks</b>",
                            "Uses predicted lengths to create the final soft tissue (pink) fiducial points.",
                            self.create_predicted_landmarks, is_final_step=True)
        stage2_main_layout.addWidget(stage2_group)
        stage2_main_layout.addStretch()

        # Navigation buttons for Stage 2
        nav_layout2 = qt.QHBoxLayout()
        back_btn2 = qt.QPushButton("← Back: Stage 1")
        back_btn2.setStyleSheet("padding: 10px 20px;")
        back_btn2.clicked.connect(lambda: self.go_to_stage(1))
        nav_layout2.addWidget(back_btn2)
        nav_layout2.addStretch()
        next_btn2 = qt.QPushButton("Next: Stage 3 →")
        next_btn2.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 20px;")
        next_btn2.clicked.connect(lambda: self.go_to_stage(3))
        nav_layout2.addWidget(next_btn2)
        stage2_main_layout.addLayout(nav_layout2)

        self.stage_stack.addWidget(stage2_container)
        self.stage_widgets[2] = stage2_container

        # STAGE 3 and 4 COMBINED
        stage3_container = qt.QWidget()
        stage3_main_layout = qt.QVBoxLayout(stage3_container)

        # STAGE 3
        stage3_group = self.create_stage_group("Stage 3: Ground Truth Comparison")
        stage3_layout = stage3_group.layout()

        # Add download button for soft tissue sample
        download_soft_btn = qt.QPushButton("📥 Load Sample Soft Tissue Landmarks")
        download_soft_btn.setStyleSheet("background-color: #E8F5E9; padding: 8px; margin-bottom: 10px;")
        download_soft_btn.setToolTip("Download and load Ryu_soft_tissue.mrk.json ground truth directly into the scene")
        download_soft_btn.clicked.connect(lambda: self.download_and_load_landmarks(
            "https://github.com/user-attachments/files/29245314/Ryu_soft_tissue.mrk.json",
            "Ryu_soft_tissue"
        ))
        stage3_layout.addWidget(download_soft_btn)

        inputs_group3 = qt.QGroupBox("Input")
        inputs_layout3 = qt.QFormLayout(inputs_group3)
        self.soft_tissue_selector = self.create_node_selector("True Soft Tissue Fiducials:", "vtkMRMLMarkupsFiducialNode", "Ryu_soft_tissue")
        inputs_layout3.addRow(self.soft_tissue_selector['label'], self.soft_tissue_selector['selector'])
        stage3_layout.addWidget(inputs_group3)
        self.add_workflow_step(stage3_layout, "<b>Step 5: Create True Soft Tissue Measurements</b>",
                            "Creates 'True' (green) measurement lines from ground truth soft tissue fiducials.",
                            self.create_true_soft_tissue_measurements, is_final_step=True)
        stage3_main_layout.addWidget(stage3_group)

        # STAGE 4
        stage4_group = self.create_stage_group("Stage 4: Error Visualization")
        stage4_layout = stage4_group.layout()
        self.add_workflow_step(stage4_layout, "<b>Step 6: Measure Prediction Error</b>",
                            "Creates error lines (red) between predicted and true soft tissue points.",
                            self.measure_prediction_errors, is_final_step=True)
        stage3_main_layout.addWidget(stage4_group)

        stage3_main_layout.addStretch()

        # Navigation buttons for Stage 3 and 4
        nav_layout3 = qt.QHBoxLayout()
        back_btn3 = qt.QPushButton("← Back: Stage 2")
        back_btn3.setStyleSheet("padding: 10px 20px;")
        back_btn3.clicked.connect(lambda: self.go_to_stage(2))
        nav_layout3.addWidget(back_btn3)
        nav_layout3.addStretch()
        next_btn3 = qt.QPushButton("Next: Results and Visualization →")
        next_btn3.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 20px;")
        next_btn3.clicked.connect(lambda: self.go_to_stage(4))
        nav_layout3.addWidget(next_btn3)
        stage3_main_layout.addLayout(nav_layout3)

        self.stage_stack.addWidget(stage3_container)
        self.stage_widgets[3] = stage3_container

        # STAGE 5 and Visualization - Final view
        stage4_container = qt.QWidget()
        stage4_main_layout = qt.QVBoxLayout(stage4_container)

        # STAGE 5 - Results
        stage5_group = self.create_stage_group("Stage 5: Results and Analysis")
        stage5_layout = stage5_group.layout()
        self.add_workflow_step(stage5_layout, "<b>Step 7: Show Landmark Error Table</b>",
                            "Displays a table with final 3D errors for each landmark.",
                            self.show_landmark_error_table, is_final_step=True)
        stage4_main_layout.addWidget(stage5_group)

        # ===== EXPORT FOR RSTUDIO =====
        if _rstudio_wrapper:
            _rstudio_wrapper.install_export_button_for(
                gui=self.main_widget,
                parent_layout=stage4_main_layout,
                method="Ryu",
                variant="auto",
                table_widget=None,
            )

        # Visualization tools
        viz_group = qt.QGroupBox("Visualization Tools")
        viz_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        viz_layout = qt.QGridLayout(viz_group)
        self.add_toggle_button(viz_layout, "Hard Tissue Measurements (Cyan)", "N", "vtkMRMLMarkupsLineNode", 0)
        self.add_toggle_button(viz_layout, "Predicted Lengths (Blue)", "Predicted_N", "vtkMRMLMarkupsLineNode", 1)
        self.add_toggle_button(viz_layout, "True Lengths (Green)", "True_N", "vtkMRMLMarkupsLineNode", 2)
        self.add_toggle_button(viz_layout, "Error Lines (Red)", "error_", "vtkMRMLMarkupsLineNode", 3)
        self.add_toggle_button(viz_layout, "Predicted Landmarks (Pink)", "Predicted_Soft_Tissue", "vtkMRMLMarkupsFiducialNode", 4)
        stage4_main_layout.addWidget(viz_group)

        stage4_main_layout.addStretch()

        # Navigation button for Stage 5
        nav_layout4 = qt.QHBoxLayout()
        back_btn4 = qt.QPushButton("← Back: Stages 3 and 4")
        back_btn4.setStyleSheet("padding: 10px 20px;")
        back_btn4.clicked.connect(lambda: self.go_to_stage(3))
        nav_layout4.addWidget(back_btn4)
        nav_layout4.addStretch()
        stage4_main_layout.addLayout(nav_layout4)

        self.stage_stack.addWidget(stage4_container)
        self.stage_widgets[4] = stage4_container

        # Set initial stage
        self.stage_stack.setCurrentWidget(stage1_container)

        self.main_widget.show()

    def create_stage_group(self, title):
        g = qt.QGroupBox(title)
        g.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        g.setLayout(qt.QVBoxLayout())
        return g

    def create_node_selector(self, label_text, node_type, default_name=None):
        label = qt.QLabel(label_text)
        selector = slicer.qMRMLNodeComboBox()
        selector.nodeTypes = [node_type]
        selector.setMRMLScene(slicer.mrmlScene)
        selector.addEnabled = False
        selector.removeEnabled = False
        selector.noneEnabled = True
        if default_name:
            node = slicer.mrmlScene.GetFirstNodeByName(default_name)
            if node:
                selector.setCurrentNode(node)
        return {'label': label, 'selector': selector}

    def create_step_group(self, title):
        g = qt.QGroupBox(title)
        g.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        g.setLayout(qt.QVBoxLayout())
        return g

    def add_workflow_step(self, parent_layout, title_html, description, callback, is_final_step=False):
        parent_layout.addWidget(qt.QLabel(title_html))
        desc = qt.QLabel(description)
        desc.setWordWrap(True)
        parent_layout.addWidget(desc)
        btn = qt.QPushButton(title_html.split("</b>")[0].replace("<b>", ""))
        btn.clicked.connect(callback)
        parent_layout.addWidget(btn)
        if not is_final_step:
            sep = qt.QFrame()
            sep.setFrameShape(qt.QFrame.HLine)
            sep.setFrameShadow(qt.QFrame.Sunken)
            parent_layout.addWidget(sep)

    def add_toggle_button(self, layout, text, prefix, node_class_str, row, initial_state=True):
        btn = qt.QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(initial_state)
        btn.toggled.connect(lambda checked: self.toggle_visibility_by_prefix(prefix, checked, node_class_str))
        layout.addWidget(btn, row, 0)

    def get_node(self, selector_dict, friendly_name):
        node = selector_dict['selector'].currentNode()
        if not node:
            slicer.util.errorDisplay("Please select '{}' in the dropdown menu.".format(friendly_name))
            return None
        return node

    def get_landmark_pos(self, landmarks_node, landmark_name):
        for i in range(landmarks_node.GetNumberOfControlPoints()):
            if landmarks_node.GetNthControlPointLabel(i) == landmark_name:
                pos = np.zeros(3)
                landmarks_node.GetNthControlPointPosition(i, pos)
                return pos
        return None

    def get_or_create_node(self, class_name, node_name):
        node = slicer.mrmlScene.GetFirstNodeByName(node_name)
        if not node:
            node = slicer.mrmlScene.AddNewNodeByClass(class_name, node_name)
        return node

    def toggle_visibility_by_prefix(self, prefix, is_visible, node_class_str):
        nodes = slicer.util.getNodesByClass(node_class_str)
        for node in nodes:
            name = node.GetName()
            if name.startswith(prefix):
                if prefix == "N" and (name.startswith("Predicted_") or name.startswith("True_")):
                    continue
                node.SetDisplayVisibility(is_visible)

    def go_to_stage(self, stage_number):
        """Navigate to a specific stage"""
        if stage_number in self.stage_widgets:
            self.current_stage = stage_number
            self.stage_stack.setCurrentWidget(self.stage_widgets[stage_number])

    def download_and_load_landmarks(self, url, node_name):
        """Download landmark file from GitHub and load it directly into the scene"""
        import urllib.request
        import tempfile
        import os
        try:
            # Show progress message
            slicer.app.processEvents()
            
            # Create a temporary file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, node_name + ".mrk.json")
            
            # Download the file
            slicer.util.showStatusMessage("Downloading {} from GitHub...".format(node_name), 2000)
            urllib.request.urlretrieve(url, temp_file)
            
            # Check if node already exists and remove it
            existing_node = slicer.mrmlScene.GetFirstNodeByName(node_name)
            if existing_node:
                slicer.mrmlScene.RemoveNode(existing_node)
            
            # Load the file into the scene
            loaded_node = slicer.util.loadMarkups(temp_file)
            if loaded_node:
                loaded_node.SetName(node_name)
                slicer.util.infoDisplay("✓ {} loaded successfully into the scene!\n\nThe landmarks are now ready to use.".format(node_name))
                
                # Update the selector to show the newly loaded node
                if "hard" in node_name.lower():
                    self.hard_tissue_selector['selector'].setCurrentNode(loaded_node)
                elif "soft" in node_name.lower():
                    self.soft_tissue_selector['selector'].setCurrentNode(loaded_node)
            else:
                slicer.util.errorDisplay("Failed to load the landmarks file.")
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            slicer.util.errorDisplay("Failed to download and load file:\n{}".format(str(e)))

    def create_anatomical_planes(self):
        landmarks_node = self.get_node(self.hard_tissue_selector, "Hard Tissue Fiducials")
        if not landmarks_node:
            return

        required = {
            "Midsagittal": ["N", "lambda", "prosthion"],
            "Orbital": ["O_R", "O_L", "au_R", "au_L"],
            "Coronal": ["bregma"],
            "Rhinion": ["R"],
            "Alare": ["A_L", "A_R"]
        }
        all_landmarks = {}
        for i in range(landmarks_node.GetNumberOfControlPoints()):
            label = landmarks_node.GetNthControlPointLabel(i)
            all_landmarks[label] = self.get_landmark_pos(landmarks_node, label)

        missing = [lm for group in required.values() for lm in group if lm not in all_landmarks or all_landmarks[lm] is None]
        if missing:
            slicer.util.errorDisplay("Missing required landmarks: {}".format(', '.join(sorted(list(set(missing))))))
            return

        # MIDSAGITTAL PLANE: X axis (points Right)
        midsag_pts = np.array([all_landmarks[n] for n in required["Midsagittal"]])
        centroid = midsag_pts.mean(axis=0)
        _, _, vh = np.linalg.svd(midsag_pts - centroid)
        midsag_normal = vh[2]
        if midsag_normal[0] < 0: # Force to point Right (Positive X)
            midsag_normal *= -1
            
        midsagittal_plane = self.get_or_create_node("vtkMRMLMarkupsPlaneNode", "Midsagittal")
        midsagittal_plane.SetOrigin(centroid)
        midsagittal_plane.SetNormal(midsag_normal)

        # ORBITAL PLANE: Z axis (points Inferior/Down)
        au_midpoint = (all_landmarks["au_L"] + all_landmarks["au_R"]) / 2.0
        orbital_pts = np.array([all_landmarks["O_R"], all_landmarks["O_L"], au_midpoint])
        centroid = orbital_pts.mean(axis=0)
        _, _, vh = np.linalg.svd(orbital_pts - centroid)
        initial_normal = vh[2]

        # Make the plane orthogonal to midsagittal plane
        orbital_normal = initial_normal - np.dot(initial_normal, midsag_normal) * midsag_normal
        orbital_normal = orbital_normal / np.linalg.norm(orbital_normal)
        if orbital_normal[2] > 0: # Force to point Inferior (Negative Z)
            orbital_normal *= -1

        orbital_plane = self.get_or_create_node("vtkMRMLMarkupsPlaneNode", "Orbital")
        orbital_plane.SetOrigin(centroid)
        orbital_plane.SetNormal(orbital_normal)

        # CORONAL PLANE: Y axis (points Anterior/Forward)
        # Since we want the face to be at Positive Y, this MUST point Positive Y!
        coronal_normal = np.cross(midsag_normal, orbital_normal)
        if coronal_normal[1] < 0: # Force to point Anterior (Positive Y)
            coronal_normal *= -1
            
        coronal_plane = self.get_or_create_node("vtkMRMLMarkupsPlaneNode", "Coronal")
        coronal_plane.SetOrigin(all_landmarks["bregma"])
        coronal_plane.SetNormal(coronal_normal)

        rhinion_plane = self.get_or_create_node("vtkMRMLMarkupsPlaneNode", "Rhinion")
        rhinion_plane.SetOrigin(all_landmarks["R"])
        rhinion_plane.SetNormal(orbital_normal)

        left_alare_plane = self.get_or_create_node("vtkMRMLMarkupsPlaneNode", "Left Alare Sagittal")
        left_alare_plane.SetOrigin(all_landmarks["A_L"])
        left_alare_plane.SetNormal(midsag_normal)
        right_alare_plane = self.get_or_create_node("vtkMRMLMarkupsPlaneNode", "Right Alare Sagittal")
        right_alare_plane.SetOrigin(all_landmarks["A_R"])
        right_alare_plane.SetNormal(midsag_normal)

        self.steps_completed['planes'] = True
        slicer.util.infoDisplay("Step 1: All anatomical planes created.")

    def create_hard_tissue_measurements(self):
        landmarks_node = self.get_node(self.hard_tissue_selector, "Hard Tissue Fiducials")
        if not landmarks_node:
            return

        plane_names = ["Midsagittal", "Orbital", "Coronal", "Rhinion", "Left Alare Sagittal", "Right Alare Sagittal"]
        if any(not slicer.mrmlScene.GetFirstNodeByName(name) for name in plane_names):
            slicer.util.errorDisplay("Planes not found.Please run Step 1 first.")
            return

        hard_tissue_measurements = [
            ("N1", "AC", "Midsagittal"), ("N2", "AC", "Left Alare Sagittal"), ("N3", "AC", "Right Alare Sagittal"),
            ("N4", "N", "Orbital"), ("N5", "AC", "Orbital"), ("N6", "N", "Coronal"), ("N7", "AC", "Coronal"),
            ("N28", "R", "Coronal"), ("N29", "IC_L", "Midsagittal"), ("N30", "A_L", "Midsagittal"),
            ("N31", "NAG_L", "Midsagittal"), ("N32", "NAI_L", "Midsagittal"), ("N33", "IC_L", "Orbital"),
            ("N34", "A_L", "Orbital"), ("N35", "NAG_L", "Orbital"), ("N36", "NAI_L", "Orbital"),
            ("N37", "IC_L", "Coronal"), ("N38", "A_L", "Coronal"), ("N39", "NAG_L", "Coronal"),
            ("N40", "NAI_L", "Coronal"), ("N53", "IC_R", "Midsagittal"), ("N54", "A_R", "Midsagittal"),
            ("N55", "NAG_R", "Midsagittal"), ("N56", "NAI_R", "Midsagittal"), ("N57", "IC_R", "Orbital"),
            ("N59", "NAG_R", "Orbital"), ("N60", "NAI_R", "Orbital"), ("N61", "IC_R", "Coronal"),
            ("N63", "NAG_R", "Coronal"), ("N64", "NAI_R", "Coronal")
        ]

        for line_name, landmark_name, plane_name in hard_tissue_measurements:
            point = self.get_landmark_pos(landmarks_node, landmark_name)
            if point is None:
                slicer.util.warningDisplay("Skipping {}: Landmark '{}' not found.".format(line_name, landmark_name))
                continue
            plane_node = slicer.mrmlScene.GetFirstNodeByName(plane_name)
            plane_origin = np.zeros(3)
            plane_node.GetOrigin(plane_origin)
            plane_normal = np.zeros(3)
            plane_node.GetNormal(plane_normal)
            vtk_plane = vtk.vtkPlane()
            vtk_plane.SetOrigin(plane_origin)
            vtk_plane.SetNormal(plane_normal)
            projected_point = np.zeros(3)
            vtk_plane.ProjectPoint(point, projected_point)
            
            line_node = self.get_or_create_node("vtkMRMLMarkupsLineNode", line_name)
            line_node.RemoveAllControlPoints()
            line_node.AddControlPoint(point)
            line_node.AddControlPoint(projected_point)
            line_node.GetMeasurement("length").SetEnabled(True)
            display_node = line_node.GetDisplayNode()
            display_node.SetColor(0, 1, 1)
            display_node.SetSelectedColor(0, 1, 1)

        self.steps_completed['hard_measurements'] = True
        slicer.util.infoDisplay("Step 2: Hard tissue measurement lines (cyan) created.")

    def launch_length_prediction_dialog(self):
        required_nodes = ["N4", "N5", "N6", "N7", "N35", "N39", "N59", "N63"]
        if any(not slicer.mrmlScene.GetFirstNodeByName(name) for name in required_nodes):
            slicer.util.errorDisplay("Setup is incomplete.Please run Steps 1 and 2 first.")
            return
        if not self.length_prediction_dialog:
            self.length_prediction_dialog = LengthPredictionDialog(self, parent=self.main_widget)
        self.length_prediction_dialog.show()
        self.length_prediction_dialog.raise_()

    def create_predicted_landmarks(self):
        if self.last_prediction_sex is None:
            slicer.util.errorDisplay("Please predict soft tissue lengths first (Step 3).")
            return

        predicted_lines = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if n.GetName().startswith("Predicted_N")]
        if not predicted_lines:
            slicer.util.errorDisplay("No predicted lengths found.Please run Step 3 first.")
            return

        planes = {name: slicer.mrmlScene.GetFirstNodeByName(name) for name in ["Midsagittal", "Orbital", "Coronal", "Left Alare Sagittal", "Right Alare Sagittal"]}
        hard_tissue_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
        node_name = "Predicted_Soft_Tissue_{}_{}".format(self.last_prediction_sex, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        predicted_landmarks_node = self.get_or_create_node("vtkMRMLMarkupsFiducialNode", node_name)
        predicted_landmarks_node.RemoveAllControlPoints()
        
        pred_display_node = predicted_landmarks_node.GetDisplayNode()
        pred_display_node.SetSelectedColor(1, 0.4, 0.7)
        pred_display_node.SetColor(1, 0.4, 0.7)
        pred_display_node.SetGlyphScale(3.0)

        # Define landmark definitions with their measurement sequences
        landmark_defs = {
            "S": ("N", ["N8", "N17", "N20"]), 
            "PN": ("N", ["N11", "N18", "N21"]), 
            "SN": ("N", ["N14", "N19", "N22"]),
            "ACS_L": ("A_L", ["N41", "N45", "N49"]), 
            "ACP_L": ("A_L", ["N42", "N46", "N50"]),
            "NA_L": ("A_L", ["N43", "N47", "N51"]), 
            "ACI_L": ("A_L", ["N44", "N48", "N52"]),
            "ACS_R": ("A_R", ["N65", "N69", "N73"]), 
            "ACP_R": ("A_R", ["N66", "N70", "N74"]),
            "NA_R": ("A_R", ["N67", "N71", "N75"]), 
            "ACI_R": ("A_R", ["N68", "N72", "N76"])
        }

        # Map predicted measurements to their planes
        plane_map = {
            "N8": "Midsagittal", "N17": "Orbital", "N20": "Coronal",
            "N11": "Midsagittal", "N18": "Orbital", "N21": "Coronal",
            "N14": "Midsagittal", "N19": "Orbital", "N22": "Coronal",
            "N41": "Left Alare Sagittal", "N45": "Orbital", "N49": "Coronal",
            "N42": "Left Alare Sagittal", "N46": "Orbital", "N50": "Coronal",
            "N43": "Left Alare Sagittal", "N47": "Orbital", "N51": "Coronal",
            "N44": "Left Alare Sagittal", "N48": "Orbital", "N52": "Coronal",
            "N65": "Right Alare Sagittal", "N69": "Orbital", "N73": "Coronal",
            "N66": "Right Alare Sagittal", "N70": "Orbital", "N74": "Coronal",
            "N67": "Right Alare Sagittal", "N71": "Orbital", "N75": "Coronal",
            "N68": "Right Alare Sagittal", "N72": "Orbital", "N76": "Coronal"
        }

        # PRE-EXTRACT ORTHOGONAL PLANES (Midsagittal, Orbital, Coronal)
        plane_origins = {}
        plane_normals = {}
        for p_name in ["Midsagittal", "Orbital", "Coronal"]:
            p_node = planes.get(p_name)
            if p_node:
                o = np.zeros(3); p_node.GetOrigin(o)
                n = np.zeros(3); p_node.GetNormal(n)
                plane_origins[p_name] = o
                plane_normals[p_name] = n

        midsag_origin = plane_origins.get("Midsagittal")
        midsag_normal = plane_normals.get("Midsagittal")

        for landmark_name, (start_landmark, measurement_codes) in landmark_defs.items():
            start_pos = self.get_landmark_pos(hard_tissue_node, start_landmark)
            if start_pos is None:
                continue

            # Determine side sign for lateral movement (Left = -1, Right = 1)
            side_sign = 1
            if start_landmark == "A_L": side_sign = -1
            elif start_landmark == "A_R": side_sign = 1

            dist_dict = {"Midsagittal": 0.0, "Orbital": 0.0, "Coronal": 0.0}

            # 1. LATERAL OFFSET (Midsagittal)
            lateral_code = None
            if "ACS_L" in landmark_name or "ACP_L" in landmark_name or "NA_L" in landmark_name or "ACI_L" in landmark_name:
                for code in measurement_codes:
                    if code in ["N41", "N42", "N43", "N44"]: lateral_code = code; break
            elif "ACS_R" in landmark_name or "ACP_R" in landmark_name or "NA_R" in landmark_name or "ACI_R" in landmark_name:
                for code in measurement_codes:
                    if code in ["N65", "N66", "N67", "N68"]: lateral_code = code; break

            if lateral_code:
                predicted_line_node = slicer.mrmlScene.GetFirstNodeByName("Predicted_{}".format(lateral_code))
                if predicted_line_node:
                    dist = predicted_line_node.GetMeasurement('length').GetValue()
                    if abs(dist) > 0.1:
                        dist_dict["Midsagittal"] = side_sign * dist

            # If predicted lateral distance is missing/0, fallback to the bony anchor
            if abs(dist_dict["Midsagittal"]) < 0.1:
                lateral_offset = np.dot(start_pos - midsag_origin, midsag_normal)
                dist_dict["Midsagittal"] = lateral_offset

            # 2. VERTICAL OFFSET (Orbital) & ANTERIOR OFFSET (Coronal)
            for measurement_code in measurement_codes:
                predicted_line_node = slicer.mrmlScene.GetFirstNodeByName("Predicted_{}".format(measurement_code))
                if predicted_line_node:
                    dist = predicted_line_node.GetMeasurement('length').GetValue()
                    plane_name = plane_map.get(measurement_code)
                    
                    if plane_name == "Coronal":
                        dist_dict["Coronal"] = dist
                        
                    elif plane_name == "Orbital":
                        # CRITICAL ANATOMICAL FIX:
                        # Orbital plane points DOWN (-Z). 
                        # For most landmarks (PN, SN, Alars), positive dist moves them downward.
                        # But Selion (S) is SUPERIOR to the Orbital plane. It requires a NEGATIVE dist to move UPWARD.
                        if landmark_name == "S":
                            dist_dict["Orbital"] = -1.0 * dist
                        else:
                            dist_dict["Orbital"] = dist

            # 3. RECONSTRUCT THE 3D POINT FROM THE 3 ORTHOGONAL PLANES
            final_pos = np.zeros(3)
            for p_name, dist in dist_dict.items():
                if p_name not in plane_origins: continue
                origin = plane_origins[p_name]
                normal = plane_normals[p_name]
                scalar = np.dot(origin, normal) + dist
                final_pos += scalar * normal

            # KEEP IN WORLD RAS COORDINATES
            predicted_landmarks_node.AddControlPoint(final_pos, landmark_name)

        self.steps_completed['predicted_landmarks'] = True
        slicer.util.infoDisplay("Step 4: Predicted soft tissue landmarks (pink) created in node '{}'.".format(node_name))

    def create_true_soft_tissue_measurements(self):
        soft_landmarks_node = self.get_node(self.soft_tissue_selector, "True Soft Tissue Fiducials")
        if not soft_landmarks_node:
            return

        plane_names = ["Midsagittal", "Orbital", "Coronal", "Left Alare Sagittal", "Right Alare Sagittal"]
        if any(not slicer.mrmlScene.GetFirstNodeByName(name) for name in plane_names):
            slicer.util.errorDisplay("Planes not found.Please run Step 1 first.")
            return

        true_measurements = [
            ("N8", "S", "Midsagittal"), ("N11", "PN", "Midsagittal"), ("N14", "SN", "Midsagittal"),
            ("N17", "S", "Orbital"), ("N18", "PN", "Orbital"), ("N19", "SN", "Orbital"),
            ("N20", "S", "Coronal"), ("N21", "PN", "Coronal"), ("N22", "SN", "Coronal"),
            ("N41", "ACS_L", "Left Alare Sagittal"), ("N42", "ACP_L", "Left Alare Sagittal"),
            ("N43", "NA_L", "Left Alare Sagittal"), ("N44", "ACI_L", "Left Alare Sagittal"),
            ("N45", "ACS_L", "Orbital"), ("N46", "ACP_L", "Orbital"), ("N47", "NA_L", "Orbital"), ("N48", "ACI_L", "Orbital"),
            ("N49", "ACS_L", "Coronal"), ("N50", "ACP_L", "Coronal"), ("N51", "NA_L", "Coronal"), ("N52", "ACI_L", "Coronal"),
            ("N65", "ACS_R", "Right Alare Sagittal"), ("N66", "ACP_R", "Right Alare Sagittal"), ("N67", "NA_R", "Right Alare Sagittal"),
            ("N68", "ACI_R", "Right Alare Sagittal"), ("N69", "ACS_R", "Orbital"), ("N70", "ACP_R", "Orbital"), ("N71", "NA_R", "Orbital"),
            ("N72", "ACI_R", "Orbital"), ("N73", "ACS_R", "Coronal"), ("N74", "ACP_R", "Coronal"), ("N75", "NA_R", "Coronal"), ("N76", "ACI_R", "Coronal")
        ]

        for meas_name, lm_name, plane_name in true_measurements:
            line_name = "True_{}".format(meas_name)
            point = self.get_landmark_pos(soft_landmarks_node, lm_name)
            if point is None:
                continue
            plane_node = slicer.mrmlScene.GetFirstNodeByName(plane_name)
            plane_origin = np.zeros(3)
            plane_node.GetOrigin(plane_origin)
            plane_normal = np.zeros(3)
            plane_node.GetNormal(plane_normal)
            vtk_plane = vtk.vtkPlane()
            vtk_plane.SetOrigin(plane_origin)
            vtk_plane.SetNormal(plane_normal)
            projected_point = np.zeros(3)
            vtk_plane.ProjectPoint(point, projected_point)
            
            line_node = self.get_or_create_node("vtkMRMLMarkupsLineNode", line_name)
            line_node.RemoveAllControlPoints()
            line_node.AddControlPoint(point)
            line_node.AddControlPoint(projected_point)
            line_node.GetMeasurement("length").SetEnabled(True)
            display_node = line_node.GetDisplayNode()
            display_node.SetSelectedColor(0, 1, 0)
            display_node.SetColor(0, 1, 0)

        self.steps_completed['true_measurements'] = True
        slicer.util.infoDisplay("Step 5: True soft tissue (green) measurement lines created.")

    def measure_prediction_errors(self):
        soft_true_node = self.get_node(self.soft_tissue_selector, "True Soft Tissue Fiducials")
        if not soft_true_node:
            return
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if "Predicted_Soft_Tissue" in n.GetName()]
        if not pred_nodes:
            slicer.util.errorDisplay("No predicted soft tissue nodes found.Please run Step 4 first.")
            return
        pred_node = pred_nodes[-1]
        
        nodes_to_remove = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if n.GetName().startswith("error_")]
        for n in nodes_to_remove:
            slicer.mrmlScene.RemoveNode(n)

        for i in range(soft_true_node.GetNumberOfControlPoints()):
            true_label = soft_true_node.GetNthControlPointLabel(i)
            true_pos = self.get_landmark_pos(soft_true_node, true_label)
            pred_pos = self.get_landmark_pos(pred_node, true_label)
            if true_pos is not None and pred_pos is not None:
                line_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "error_{}".format(true_label))
                line_node.AddControlPoint(true_pos)
                line_node.AddControlPoint(pred_pos)
                line_node.GetMeasurement("length").SetEnabled(True)
                display_node = line_node.GetDisplayNode()
                display_node.SetSelectedColor(1, 0, 0)
                display_node.SetColor(1, 0, 0)

        self.steps_completed['errors'] = True
        slicer.util.infoDisplay("Step 6: Prediction error lines (red) created.")

    def show_landmark_error_table(self):
        self.error_table = LandmarkErrorTable(self, parent=self.main_widget)
        self.error_table.show()


class LengthPredictionDialog(qt.QDialog):
    def __init__(self, main_gui, parent=None):
        super(LengthPredictionDialog, self).__init__(parent)
        self.main_gui = main_gui
        self.setWindowTitle("Predict Soft Tissue Lengths")
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(qt.QLabel("<b>Select Biological Sex:</b>"))
        self.sex_combo = qt.QComboBox()
        self.sex_combo.addItems(["Male", "Female"])
        self.layout().addWidget(self.sex_combo)
        self.predict_btn = qt.QPushButton("Predict Lengths and Create Lines")
        self.predict_btn.setStyleSheet("background-color: #CCFFCC; font-weight: bold; padding: 8px;")
        self.predict_btn.clicked.connect(self.run_length_prediction)
        self.layout().addWidget(self.predict_btn)

    # --------------------------------------------------------------
    # get_regressions with R²-prioritised picking for alar coronal
    # --------------------------------------------------------------
    def get_regressions(self, sex, m):
        # Helper: pick the best equation from a list of options
        # options: list of (R², measurement_key, lambda_equation)
        def pick_best(options):
            for _, key, eq in options:
                if m.get(key, 0) > 0.1:
                    return eq(m.get(key, 0))
            return 0.0

        if sex == "Male":
            # --- Midline (single predictor) ---
            pred = {
                "N17": 0.92 * m.get("N4", 0) - 3.58,
                "N18": 0.91 * m.get("N5", 0) - 6.84,
                "N19": 0.91 * m.get("N5", 0) + 5.81,
                "N20": 0.93 * m.get("N6", 0) + 11.28,
                "N21": 0.96 * m.get("N7", 0) + 24.70,
                "N22": 0.96 * m.get("N7", 0) + 11.20,
            }
            # --- Alare Orbital (single predictor) ---
            pred.update({
                "N45": 0.66 * m.get("N35", 0) - 3.97,
                "N69": 0.62 * m.get("N59", 0) - 2.63,
                "N46": 0.75 * m.get("N35", 0) + 3.07,
                "N70": 0.75 * m.get("N59", 0) + 3.70,
                "N47": 0.66 * m.get("N35", 0) + 6.72,
                "N71": 0.66 * m.get("N59", 0) + 6.77,
                "N48": 0.66 * m.get("N35", 0) + 14.01,
                "N72": 0.69 * m.get("N59", 0) + 13.52,
            })
            # --- Alare Coronal (prioritised by R²) ---
            pred.update({
                "N49": pick_best([
                    (85, "N39", lambda x: 0.91 * x + 19.98),
                    (80, "N7",  lambda x: 0.84 * x + 16.41),
                    (71, "N28", lambda x: 0.85 * x + 11.47)
                ]),
                "N50": pick_best([
                    (90, "N39", lambda x: 0.95 * x + 10.59),
                    (82, "N7",  lambda x: 0.87 * x + 8.61),
                    (66, "N28", lambda x: 0.83 * x + 7.11)
                ]),
                "N51": pick_best([
                    (87, "N39", lambda x: 0.98 * x + 12.26),
                    (82, "N7",  lambda x: 0.92 * x + 8.38),
                    (70, "N28", lambda x: 0.90 * x + 4.58)
                ]),
                "N52": pick_best([
                    (88, "N39", lambda x: 0.96 * x + 15.18),
                    (83, "N7",  lambda x: 0.90 * x + 11.41),
                    (63, "N28", lambda x: 0.83 * x + 12.30)
                ]),
                "N73": pick_best([
                    (84, "N63", lambda x: 0.92 * x + 18.62),
                    (75, "N7",  lambda x: 0.83 * x + 17.20),
                    (69, "N28", lambda x: 0.85 * x + 10.92)
                ]),
                "N74": pick_best([
                    (90, "N63", lambda x: 0.99 * x + 8.11),
                    (81, "N7",  lambda x: 0.90 * x + 6.34),
                    (66, "N28", lambda x: 0.87 * x + 4.21)
                ]),
                "N75": pick_best([
                    (88, "N63", lambda x: 1.02 * x + 9.19),
                    (81, "N7",  lambda x: 0.94 * x + 6.12),
                    (70, "N28", lambda x: 0.94 * x + 1.61)
                ]),
                "N76": pick_best([
                    (88, "N63", lambda x: 0.99 * x + 13.23),
                    (83, "N7",  lambda x: 0.92 * x + 9.52),
                    (62, "N28", lambda x: 0.85 * x + 10.92)
                ]),
            })
            # --- Alare Sagittal (Lateral) ---
            pred.update({
                "N41": 0.56 * m.get("N30", 0) + 7.61,
                "N42": 0.68 * m.get("N30", 0) + 12.51,
                "N43": 0.58 * m.get("N30", 0) + 13.39,
                "N44": 0.65 * m.get("N30", 0) + 6.57,
                "N65": 0.0,  # p>=0.05
                "N66": 0.79 * m.get("N54", 0) + 11.13,
                "N67": 0.68 * m.get("N54", 0) + 12.12,
                "N68": 0.48 * m.get("N54", 0) + 8.83,
            })
        else:  # Female
            # --- Midline ---
            pred = {
                "N17": 0.85 * m.get("N4", 0) - 1.10,
                "N18": 1.01 * m.get("N5", 0) - 9.04,
                "N19": 1.00 * m.get("N5", 0) + 3.23,
                "N20": 0.96 * m.get("N6", 0) + 8.36,
                "N21": 1.00 * m.get("N7", 0) + 19.50,
                "N22": 1.02 * m.get("N7", 0) + 5.18,
            }
            # --- Alare Orbital ---
            pred.update({
                "N45": 0.67 * m.get("N35", 0) - 3.71,
                "N69": 0.66 * m.get("N59", 0) - 3.60,
                "N46": 0.80 * m.get("N35", 0) + 3.27,
                "N70": 0.77 * m.get("N59", 0) + 3.85,
                "N47": 0.65 * m.get("N35", 0) + 6.73,
                "N71": 0.78 * m.get("N59", 0) + 3.82,
                "N48": 0.65 * m.get("N35", 0) + 13.58,
                "N72": 0.65 * m.get("N59", 0) + 13.15,
            })
            # --- Alare Coronal (prioritised by R²) ---
            pred.update({
                "N49": pick_best([
                    (93, "N39", lambda x: 0.97 * x + 14.07),
                    (87, "N28", lambda x: 0.96 * x + 1.71),
                    (86, "N7",  lambda x: 0.95 * x + 7.65)
                ]),
                "N50": pick_best([
                    (97, "N39", lambda x: 0.95 * x + 10.26),
                    (90, "N7",  lambda x: 0.93 * x + 3.83),
                    (87, "N28", lambda x: 0.92 * x - 0.61)
                ]),
                "N51": pick_best([
                    (95, "N39", lambda x: 0.95 * x + 12.71),
                    (93, "N7",  lambda x: 0.95 * x + 4.62),
                    (93, "N28", lambda x: 0.96 * x - 0.93)
                ]),
                "N52": pick_best([
                    (99, "N39", lambda x: 0.99 * x + 11.45),
                    (89, "N7",  lambda x: 0.97 * x + 4.68),
                    (86, "N28", lambda x: 0.96 * x + 0.16)
                ]),
                "N73": pick_best([
                    (95, "N63", lambda x: 0.90 * x + 18.81),
                    (91, "N7",  lambda x: 0.93 * x + 9.62),
                    (89, "N28", lambda x: 0.92 * x + 4.71)
                ]),
                "N74": pick_best([
                    (96, "N63", lambda x: 1.00 * x + 6.55),
                    (91, "N7",  lambda x: 1.03 * x - 3.54),
                    (89, "N28", lambda x: 1.02 * x - 8.55)
                ]),
                "N75": pick_best([
                    (94, "N63", lambda x: 1.03 * x + 7.54),
                    (92, "N7",  lambda x: 1.07 * x - 3.82),
                    (88, "N28", lambda x: 1.05 * x - 8.27)
                ]),
                "N76": pick_best([
                    (95, "N63", lambda x: 1.02 * x + 9.06),
                    (91, "N7",  lambda x: 1.05 * x - 1.35),
                    (87, "N28", lambda x: 1.03 * x - 5.60)
                ]),
            })
            # --- Alare Sagittal (Lateral) — all p>=0.05 ---
            pred.update({
                "N41": 0.0, "N42": 0.0, "N43": 0.0, "N44": 0.0,
                "N65": 0.0, "N66": 0.0, "N67": 0.0, "N68": 0.0,
            })

        return pred

    def run_length_prediction(self):
        sex = str(self.sex_combo.currentText)
        self.main_gui.last_prediction_sex = sex
        
        measurements = {}
        all_line_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
        for n in all_line_nodes:
            name = n.GetName()
            if name.startswith("N") and not name.startswith("Predicted_") and not name.startswith("True_"):
                suffix = name[1:]
                if suffix.isdigit():
                    measurements[name] = n.GetMeasurement('length').GetValue()

        predicted_lengths = self.get_regressions(sex, measurements)

        nodes_to_remove = []
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            if node.GetName().startswith("Predicted_"):
                nodes_to_remove.append(node)
        for node in nodes_to_remove:
            slicer.mrmlScene.RemoveNode(node)

        # Map predicted measurements to their corresponding hard tissue measurements for direction
        hard_measurement_map = {
            "N17": "N4", "N18": "N5", "N19": "N5",
            "N20": "N6", "N21": "N7", "N22": "N7",
            "N45": "N34", "N46": "N34", "N47": "N34", "N48": "N34",
            "N49": "N7", "N50": "N7", "N51": "N7", "N52": "N7",
            "N69": "N34", "N70": "N34", "N71": "N34", "N72": "N34",
            "N73": "N7", "N74": "N7", "N75": "N7", "N76": "N7",
            "N41": "N30", "N42": "N30", "N43": "N30", "N44": "N30",
            "N65": "N54", "N66": "N54", "N67": "N54", "N68": "N54"
        }

        # Plane mapping
        plane_map = {
            "N17": "Orbital", "N18": "Orbital", "N19": "Orbital",
            "N20": "Coronal", "N21": "Coronal", "N22": "Coronal",
            "N45": "Orbital", "N46": "Orbital", "N47": "Orbital", "N48": "Orbital",
            "N49": "Coronal", "N50": "Coronal", "N51": "Coronal", "N52": "Coronal",
            "N69": "Orbital", "N70": "Orbital", "N71": "Orbital", "N72": "Orbital",
            "N73": "Coronal", "N74": "Coronal", "N75": "Coronal", "N76": "Coronal",
            "N41": "Left Alare Sagittal", "N42": "Left Alare Sagittal", 
            "N43": "Left Alare Sagittal", "N44": "Left Alare Sagittal",
            "N65": "Right Alare Sagittal", "N66": "Right Alare Sagittal", 
            "N67": "Right Alare Sagittal", "N68": "Right Alare Sagittal"
        }

        hard_tissue_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
        if hard_tissue_node is None:
            slicer.util.errorDisplay("Hard tissue node 'Ryu_hard_tissue' not found.")
            return

        for pred_name in predicted_lengths:
            length = predicted_lengths[pred_name]
            plane_name = plane_map.get(pred_name)
            if not plane_name:
                continue
            
            # Get the plane node
            plane_node = slicer.mrmlScene.GetFirstNodeByName(plane_name)
            if plane_node is None:
                continue
            
            plane_origin = np.zeros(3)
            plane_node.GetOrigin(plane_origin)
            plane_normal = np.zeros(3)
            plane_node.GetNormal(plane_normal)
            
            # Determine the starting landmark
            num = int(pred_name[1:])
            if num <= 22:
                start_landmark_name = "N"
            elif num <= 52:
                start_landmark_name = "A_L"
            else:
                start_landmark_name = "A_R"
            
            start_pos = self.main_gui.get_landmark_pos(hard_tissue_node, start_landmark_name)
            if start_pos is None:
                continue
            
            # Get the corresponding hard tissue measurement for direction
            hard_code = hard_measurement_map.get(pred_name)
            if not hard_code:
                continue
            hard_line = slicer.mrmlScene.GetFirstNodeByName(hard_code)
            if not hard_line:
                continue
            
            # Get direction from hard tissue line
            landmark_pos = np.zeros(3)
            plane_proj_pos = np.zeros(3)
            hard_line.GetNthControlPointPosition(0, landmark_pos)
            hard_line.GetNthControlPointPosition(1, plane_proj_pos)
            
            # Calculate direction vector (from plane projection to landmark)
            direction = landmark_pos - plane_proj_pos
            direction_norm = np.linalg.norm(direction)
            if direction_norm < 1e-6:
                # If direction is zero, use plane normal
                direction = plane_normal
                direction_norm = np.linalg.norm(direction)
                if direction_norm < 1e-6:
                    print(f"Warning: Cannot determine direction for {pred_name}")
                    continue
            
            direction = direction / direction_norm
            
            # Project the start position onto the plane
            v = start_pos - plane_origin
            d = np.dot(v, plane_normal)
            projected_point = start_pos - d * plane_normal
            
            # Create the predicted line
            end_pos = projected_point + direction * length
            
            line_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "Predicted_{}".format(pred_name))
            line_node.AddControlPoint(projected_point)
            line_node.AddControlPoint(end_pos)
            line_node.GetMeasurement("length").SetEnabled(True)
            display_node = line_node.GetDisplayNode()
            display_node.SetSelectedColor(0, 0, 1)
            display_node.SetColor(0, 0, 1)

        self.main_gui.steps_completed['predicted_lengths'] = True
        slicer.util.infoDisplay("Step 3: Predicted soft tissue lengths calculated and blue lines created.")
        self.close()


class LandmarkErrorTable(qt.QDialog):
    def __init__(self, main_gui, parent=None):
        super(LandmarkErrorTable, self).__init__(parent)
        self.main_gui = main_gui
        self.setWindowTitle("Landmark 3D Error")
        self.setMinimumSize(600, 400)
        self.setLayout(qt.QVBoxLayout())

        self.table = qt.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Prediction Set", "Landmark", "Error (mm)"])
        self.layout().addWidget(self.table)

        btn_layout = qt.QHBoxLayout()
        self.layout().addLayout(btn_layout)
        copy_btn = qt.QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_data)
        btn_layout.addWidget(copy_btn)
        detail_btn = qt.QPushButton("Show Detailed Breakdown")
        detail_btn.clicked.connect(self.show_detailed_table)
        btn_layout.addWidget(detail_btn)
        self.populate_table()

    def show_detailed_table(self):
        self.detailed_window = DetailedBreakdownWindow(self.main_gui, parent=self)
        self.detailed_window.show()

    def populate_table(self):
        true_soft_node = self.main_gui.soft_tissue_selector['selector'].currentNode()
        if not true_soft_node:
            slicer.util.warningDisplay("Please select a 'True Soft Tissue Fiducials' node first.")
            return
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if "Predicted_Soft_Tissue" in n.GetName()]
        if not pred_nodes:
            slicer.util.warningDisplay("No predicted soft tissue nodes found.Run Step 4 first.")
            return

        self.table.setRowCount(0)
        for pred_node in pred_nodes:
            num_points = pred_node.GetNumberOfControlPoints()
            for i in range(num_points):
                label = pred_node.GetNthControlPointLabel(i)
                pred_pos = self.main_gui.get_landmark_pos(pred_node, label)
                true_pos = self.main_gui.get_landmark_pos(true_soft_node, label)
                if pred_pos is not None and true_pos is not None:
                    error = np.linalg.norm(pred_pos - true_pos)
                    current_row = self.table.rowCount
                    self.table.insertRow(current_row)
                    self.table.setItem(current_row, 0, qt.QTableWidgetItem(pred_node.GetName()))
                    self.table.setItem(current_row, 1, qt.QTableWidgetItem(label))
                    self.table.setItem(current_row, 2, qt.QTableWidgetItem("{:.2f}".format(error)))
        self.table.resizeColumnsToContents()

    def copy_data(self):
        clipboard = qt.QApplication.clipboard()
        text = ""
        for c in range(self.table.columnCount):
            hdr = self.table.horizontalHeaderItem(c)
            if hdr:
                text += hdr.text() + "\t"
            else:
                text += "\t"
        text = text.strip() + "\n"
        for r in range(self.table.rowCount):
            for c in range(self.table.columnCount):
                item = self.table.item(r, c)
                if item:
                    text += item.text() + "\t"
                else:
                    text += "\t"
            text = text.strip() + "\n"
        clipboard.setText(text)
        slicer.util.infoDisplay("Table copied to clipboard.")

class DetailedBreakdownWindow(qt.QDialog):
    def __init__(self, main_gui, parent=None):
        super(DetailedBreakdownWindow, self).__init__(parent)
        self.main_gui = main_gui
        self.setWindowTitle("Detailed Prediction Breakdown")
        self.setMinimumSize(1200, 800)
        
        main_layout = qt.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Use a splitter to allow resizable sections
        splitter = qt.QSplitter(qt.Qt.Vertical)
        
        # Section 1: Predicted Landmark Coordinates
        landmark_widget = qt.QWidget()
        landmark_layout = qt.QVBoxLayout(landmark_widget)
        landmark_layout.setContentsMargins(0, 0, 0, 0)
        
        section1_label = qt.QLabel("<h2>Predicted Landmark Coordinates Comparison</h2>")
        landmark_layout.addWidget(section1_label)
        
        self.landmark_table = qt.QTableWidget()
        self.landmark_table.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.landmark_table.setAlternatingRowColors(True)
        self.landmark_table.setHorizontalScrollMode(qt.QAbstractItemView.ScrollPerPixel)
        landmark_headers = ["Prediction Set", "Landmark", "Pred X", "Pred Y", "Pred Z", "True X", "True Y", "True Z", "Euclidean Error (mm)", "Regression Equations Used", "Predicted Measurements Used"]
        self.landmark_table.setColumnCount(len(landmark_headers))
        self.landmark_table.setHorizontalHeaderLabels(landmark_headers)
        landmark_layout.addWidget(self.landmark_table, 1)
        
        copy_landmarks_btn = qt.QPushButton("Copy Landmark Table to Clipboard")
        copy_landmarks_btn.clicked.connect(self.copy_landmark_data)
        landmark_layout.addWidget(copy_landmarks_btn)
        
        splitter.addWidget(landmark_widget)
        
        # Section 2: Predicted Lengths Only
        lengths_widget = qt.QWidget()
        lengths_layout = qt.QVBoxLayout(lengths_widget)
        lengths_layout.setContentsMargins(0, 0, 0, 0)
        
        section2_label = qt.QLabel("<h2>Predicted Soft Tissue Lengths (Estimated Measurements)</h2>")
        lengths_layout.addWidget(section2_label)
        
        self.lengths_table = qt.QTableWidget()
        self.lengths_table.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.lengths_table.setAlternatingRowColors(True)
        self.lengths_table.setHorizontalScrollMode(qt.QAbstractItemView.ScrollPerPixel)
        lengths_headers = ["Measurement", "Regression Equation", "Predicted (mm)", "True (mm)", "Absolute Difference (mm)"]
        self.lengths_table.setColumnCount(len(lengths_headers))
        self.lengths_table.setHorizontalHeaderLabels(lengths_headers)
        lengths_layout.addWidget(self.lengths_table, 1)
        
        copy_lengths_btn = qt.QPushButton("Copy Lengths Table to Clipboard")
        copy_lengths_btn.clicked.connect(self.copy_lengths_data)
        lengths_layout.addWidget(copy_lengths_btn)
        
        splitter.addWidget(lengths_widget)
        
        # Set initial splitter sizes (60% landmarks, 40% lengths)
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter, 1)
        
        # Copy All button at bottom
        copy_all_btn = qt.QPushButton("Copy All Data to Clipboard")
        copy_all_btn.setStyleSheet("font-weight: bold; padding: 10px;")
        copy_all_btn.clicked.connect(self.copy_all_data)
        main_layout.addWidget(copy_all_btn)
        
        self.populate_landmark_table()
        self.populate_lengths_table()
        
        # Auto-size columns after populating
        self.auto_resize_columns()

    def auto_resize_columns(self):
        # Resize columns to fit contents
        self.landmark_table.resizeColumnsToContents()
        self.lengths_table.resizeColumnsToContents()
        
        # Get headers
        landmark_header = self.landmark_table.horizontalHeader()
        lengths_header = self.lengths_table.horizontalHeader()
        
        # Stretch the last column to fill remaining space
        landmark_header.setStretchLastSection(True)
        lengths_header.setStretchLastSection(True)

    def get_regression_equations(self, sex):
        # UPDATED to match the exact Ryu 2020 supplementary tables provided by user
        if sex == "Male":
            return {
                "N17": "0.92 * N4 - 3.58",
                "N18": "0.91 * N5 - 6.84",
                "N19": "0.91 * N5 + 5.81",
                "N20": "0.93 * N6 + 11.28",
                "N21": "0.96 * N7 + 24.70",
                "N22": "0.96 * N7 + 11.20",
                "N45": "0.66 * N35 - 3.97", "N69": "0.62 * N59 - 2.63",
                "N46": "0.75 * N35 + 3.07", "N70": "0.75 * N59 + 3.70",
                "N47": "0.66 * N35 + 6.72", "N71": "0.66 * N59 + 6.77",
                "N48": "0.66 * N35 + 14.01", "N72": "0.69 * N59 + 13.52",
                "N49": "0.84 * N7 + 16.41", "N73": "0.83 * N7 + 17.20",
                "N50": "0.87 * N7 + 8.61", "N74": "0.90 * N7 + 6.34",
                "N51": "0.92 * N7 + 8.38", "N75": "0.94 * N7 + 6.12",
                "N52": "0.90 * N7 + 11.41", "N76": "0.92 * N7 + 9.52",
                "N41": "0.56 * N30 + 7.61", "N65": "N/A (p>=0.05)",
                "N42": "0.68 * N30 + 12.51", "N66": "0.79 * N54 + 11.13",
                "N43": "0.58 * N30 + 13.39", "N67": "0.68 * N54 + 12.12",
                "N44": "0.65 * N30 + 6.57", "N68": "0.48 * N54 + 8.83"
            }
        else:
            return {
                "N17": "0.85 * N4 - 1.10",
                "N18": "1.01 * N5 - 9.04",
                "N19": "1.00 * N5 + 3.23",
                "N20": "0.96 * N6 + 8.36",
                "N21": "1.00 * N7 + 19.50",
                "N22": "1.02 * N7 + 5.18",
                "N45": "0.67 * N35 - 3.71", "N69": "0.66 * N59 - 3.60",
                "N46": "0.80 * N35 + 3.27", "N70": "0.77 * N59 + 3.85",
                "N47": "0.65 * N35 + 6.73", "N71": "0.78 * N59 + 3.82",
                "N48": "0.65 * N35 + 13.58", "N72": "0.65 * N59 + 13.15",
                "N49": "0.95 * N7 + 7.65", "N73": "0.93 * N7 + 9.62",
                "N50": "0.93 * N7 + 3.83", "N74": "1.03 * N7 - 3.54",
                "N51": "0.95 * N7 + 4.62", "N75": "1.07 * N7 - 3.82",
                "N52": "0.97 * N7 + 4.68", "N76": "1.05 * N7 - 1.35",
                "N41": "N/A (p>=0.05)", "N65": "N/A (p>=0.05)",
                "N42": "N/A (p>=0.05)", "N66": "N/A (p>=0.05)",
                "N43": "N/A (p>=0.05)", "N67": "N/A (p>=0.05)",
                "N44": "N/A (p>=0.05)", "N68": "N/A (p>=0.05)"
            }

    def get_landmark_equations(self, label, sex):
        landmark_to_measurements = {
            "S": ["N8", "N17", "N20"],
            "PN": ["N11", "N18", "N21"],
            "SN": ["N14", "N19", "N22"],
            "ACS_L": ["N41", "N45", "N49"],
            "ACP_L": ["N42", "N46", "N50"],
            "NA_L": ["N43", "N47", "N51"],
            "ACI_L": ["N44", "N48", "N52"],
            "ACS_R": ["N65", "N69", "N73"],
            "ACP_R": ["N66", "N70", "N74"],
            "NA_R": ["N67", "N71", "N75"],
            "ACI_R": ["N68", "N72", "N76"]
        }
        
        equations = self.get_regression_equations(sex)
        if label not in landmark_to_measurements:
            return "N/A"
        
        measurement_codes = landmark_to_measurements[label]
        eq_list = []
        for code in measurement_codes:
            if code in equations:
                eq_list.append("{} = {}".format(code, equations[code]))
        
        return "; ".join(eq_list) if eq_list else "N/A"

    def populate_landmark_table(self):
        true_soft_node = self.main_gui.soft_tissue_selector['selector'].currentNode()
        if not true_soft_node:
            return
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if "Predicted_Soft_Tissue" in n.GetName()]
        if not pred_nodes:
            return

        landmark_defs = {
            "S": ("N", ["N8", "N17", "N20"]),
            "PN": ("N", ["N11", "N18", "N21"]),
            "SN": ("N", ["N14", "N19", "N22"]),
            "ACS_L": ("A_L", ["N41", "N45", "N49"]),
            "ACP_L": ("A_L", ["N42", "N46", "N50"]),
            "NA_L": ("A_L", ["N43", "N47", "N51"]),
            "ACI_L": ("A_L", ["N44", "N48", "N52"]),
            "ACS_R": ("A_R", ["N65", "N69", "N73"]),
            "ACP_R": ("A_R", ["N66", "N70", "N74"]),
            "NA_R": ("A_R", ["N67", "N71", "N75"]),
            "ACI_R": ("A_R", ["N68", "N72", "N76"])
        }

        self.landmark_table.setRowCount(0)
        for pred_node in pred_nodes:
            node_name = pred_node.GetName()
            sex = "Male" if "Male" in node_name else "Female"
            
            num_points = pred_node.GetNumberOfControlPoints()
            for i in range(num_points):
                label = pred_node.GetNthControlPointLabel(i)
                pred_pos = self.main_gui.get_landmark_pos(pred_node, label)
                true_pos = self.main_gui.get_landmark_pos(true_soft_node, label)
                if pred_pos is None or true_pos is None:
                    continue
                error = np.linalg.norm(pred_pos - true_pos)

                measurement_codes = []
                if label in landmark_defs:
                    measurement_codes = landmark_defs[label][1]
                predicted_measurements_used = []
                for code in measurement_codes:
                    name = "Predicted_{}".format(code)
                    if slicer.mrmlScene.GetFirstNodeByName(name):
                        predicted_measurements_used.append(name)
                used_text = "; ".join(predicted_measurements_used) if predicted_measurements_used else "N/A"
                
                equations_text = self.get_landmark_equations(label, sex)

                current_row = self.landmark_table.rowCount
                self.landmark_table.insertRow(current_row)
                self.landmark_table.setItem(current_row, 0, qt.QTableWidgetItem(node_name))
                self.landmark_table.setItem(current_row, 1, qt.QTableWidgetItem(label))
                self.landmark_table.setItem(current_row, 2, qt.QTableWidgetItem("{:.2f}".format(pred_pos[0])))
                self.landmark_table.setItem(current_row, 3, qt.QTableWidgetItem("{:.2f}".format(pred_pos[1])))
                self.landmark_table.setItem(current_row, 4, qt.QTableWidgetItem("{:.2f}".format(pred_pos[2])))
                self.landmark_table.setItem(current_row, 5, qt.QTableWidgetItem("{:.2f}".format(true_pos[0])))
                self.landmark_table.setItem(current_row, 6, qt.QTableWidgetItem("{:.2f}".format(true_pos[1])))
                self.landmark_table.setItem(current_row, 7, qt.QTableWidgetItem("{:.2f}".format(true_pos[2])))
                self.landmark_table.setItem(current_row, 8, qt.QTableWidgetItem("{:.2f}".format(error)))
                self.landmark_table.setItem(current_row, 9, qt.QTableWidgetItem(equations_text))
                self.landmark_table.setItem(current_row, 10, qt.QTableWidgetItem(used_text))

    def populate_lengths_table(self):
        sex = self.main_gui.last_prediction_sex if self.main_gui.last_prediction_sex else "Male"
        equations = self.get_regression_equations(sex)
        
        predicted_measurement_keys = list(equations.keys())
        
        pred_lines = {}
        true_lines = {}
        for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            name = n.GetName()
            if name.startswith("Predicted_"):
                key = name.replace("Predicted_", "")
                if key in predicted_measurement_keys:
                    pred_lines[key] = n.GetMeasurement('length').GetValue()
            elif name.startswith("True_"):
                key = name.replace("True_", "")
                if key in predicted_measurement_keys:
                    true_lines[key] = n.GetMeasurement('length').GetValue()

        self.lengths_table.setRowCount(0)
        for key in sorted(predicted_measurement_keys, key=lambda x: int(x[1:])):
            pred_val = pred_lines.get(key)
            true_val = true_lines.get(key)
            equation = equations.get(key, "N/A")
            
            if pred_val is not None and true_val is not None:
                diff = abs(pred_val - true_val)
            else:
                diff = None
            
            current_row = self.lengths_table.rowCount
            self.lengths_table.insertRow(current_row)
            self.lengths_table.setItem(current_row, 0, qt.QTableWidgetItem(key))
            self.lengths_table.setItem(current_row, 1, qt.QTableWidgetItem(equation))
            self.lengths_table.setItem(current_row, 2, qt.QTableWidgetItem("{:.2f}".format(pred_val) if pred_val is not None else "N/A"))
            self.lengths_table.setItem(current_row, 3, qt.QTableWidgetItem("{:.2f}".format(true_val) if true_val is not None else "N/A"))
            self.lengths_table.setItem(current_row, 4, qt.QTableWidgetItem("{:.2f}".format(diff) if diff is not None else "N/A"))

    # --- FIX: table_to_text is now properly aligned at the class level ---
    def table_to_text(self, table):
        text = ""
        # 1. Build the Header
        headers = []
        for c in range(table.columnCount):
            hdr = table.horizontalHeaderItem(c)
            headers.append(hdr.text() if hdr else "")
        text += "\t".join(headers) + "\n"
        
        # 2. Build Rows, skipping empty ones
        for r in range(table.rowCount):
            row_items = []
            has_valid_data = False
            
            for c in range(table.columnCount):
                item = table.item(r, c)
                val = item.text() if item else ""
                row_items.append(val)
                
                # Determine if this row has any actual data (ignore "N/A" and empty strings)
                if val and val != "N/A":
                    has_valid_data = True
            
            # 3. Only add the row if it actually contains measurable data
            if has_valid_data:
                text += "\t".join(row_items) + "\n"
                
        return text.strip()

    def copy_landmark_data(self):
        clipboard = qt.QApplication.clipboard()
        clipboard.setText(self.table_to_text(self.landmark_table))
        slicer.util.infoDisplay("Landmark table copied to clipboard.")

    def copy_lengths_data(self):
        clipboard = qt.QApplication.clipboard()
        clipboard.setText(self.table_to_text(self.lengths_table))
        slicer.util.infoDisplay("Lengths table copied to clipboard.")

    def copy_all_data(self):
        clipboard = qt.QApplication.clipboard()
        all_text = "=== PREDICTED LANDMARK COORDINATES ===\n"
        all_text += self.table_to_text(self.landmark_table)
        all_text += "\n\n=== PREDICTED SOFT TISSUE LENGTHS ===\n"
        all_text += self.table_to_text(self.lengths_table)
        clipboard.setText(all_text)
        slicer.util.infoDisplay("All data copied to clipboard.")

# Cleanup and run
try:
    if 'ryu_gui_instance' in globals():
        if ryu_gui_instance and hasattr(ryu_gui_instance, 'main_widget'):
            if ryu_gui_instance.main_widget.isWidgetType():
                if hasattr(ryu_gui_instance, 'length_prediction_dialog') and ryu_gui_instance.length_prediction_dialog:
                    ryu_gui_instance.length_prediction_dialog.close()
                if hasattr(ryu_gui_instance, 'error_table') and ryu_gui_instance.error_table:
                    ryu_gui_instance.error_table.close()
                ryu_gui_instance.main_widget.close()
        del ryu_gui_instance
except:
    pass
ryu_gui_instance = RyuGUI()



```
