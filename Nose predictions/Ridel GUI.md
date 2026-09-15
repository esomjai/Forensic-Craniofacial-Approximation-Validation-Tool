```python
# Copy-paste into 3D Slicer Python Interactor
import slicer
import qt
import numpy as np
import datetime
import os
import urllib.request
import tempfile

def _process_gui_events():
    """Yield to the Qt event loop so the UI can repaint.
    Tries both common entry points; silently no-ops if neither works."""
    for fn in (lambda: _process_gui_events(),
               lambda: qt.QApplication.processEvents()):
        try:
            fn()
            return
        except Exception:
            continue

def _progress_was_cancelled(progress):
    """Return True if the user clicked Cancel on a QProgressDialog.
    Works around PythonQt builds that expose wasCanceled as a bool
    attribute instead of a callable method."""
    attr = progress.wasCanceled
    if callable(attr):
        return bool(attr())
    return bool(attr)

# --- Ridel GUI with simultaneous plane-intersection placement and Alare caveat ---
class RidelGUI:
    def __init__(self):
        self.main_widget = qt.QWidget(slicer.util.mainWindow())
        self.main_widget.setWindowFlags(qt.Qt.Tool)
        self.main_widget.setObjectName("RidelGUIWidget")
        self.main_widget.setWindowTitle("Ridel et al. (2018) Nose Prediction")
        self.main_widget.setMinimumSize(550, 800)
        self.vbox = qt.QVBoxLayout(self.main_widget)
        title_label = qt.QLabel("Ridel et al. (2018) Nose Prediction Workflow")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 10px;")
        title_label.setAlignment(qt.Qt.AlignCenter)
        self.vbox.addWidget(title_label)

        # --- STAGE 1 ---
        stage1_group = self.create_stage_group("Stage 1: Hard Tissue Prediction")
        stage1_layout = stage1_group.layout()
        inputs_group1 = qt.QGroupBox("Inputs"); inputs_layout1 = qt.QFormLayout(inputs_group1)
        self.hard_tissue_selector = self.create_node_selector("Hard Tissue Fiducials:", "vtkMRMLMarkupsFiducialNode", "Ridel_hard_tissue")
        inputs_layout1.addRow(self.hard_tissue_selector['label'], self.hard_tissue_selector['selector'])
        self.download_hard_btn = qt.QPushButton("Download Hard Tissue Landmarks (.mrk.json)")
        self.download_hard_btn.clicked.connect(self.download_hard_tissue)
        inputs_layout1.addRow("", self.download_hard_btn)
        self.fhp_plane_selector = self.create_node_selector("FHP Plane:", "vtkMRMLMarkupsPlaneNode", "FHP")
        inputs_layout1.addRow(self.fhp_plane_selector['label'], self.fhp_plane_selector['selector'])
        stage1_layout.addWidget(inputs_group1)
        workflow_group1 = self.create_step_group("Prediction Workflow"); workflow_layout1 = workflow_group1.layout()
        self.add_workflow_step(workflow_layout1, "<b>Step 1: Create Blueprint Planes</b>", "Creates MSP and FRP from FHP and hard tissue landmarks.", self.create_blueprint_planes)
        self.add_workflow_step(workflow_layout1, "<b>Step 2: Create 7 Anatomical Planes</b>", "Creates nTr, rhiTr, nsTr, alLSa, alRSa, nCor, and rhiCor.", self.create_anatomical_planes)
        self.add_workflow_step(workflow_layout1, "<b>Step 3: Create Hard Tissue Measurements</b>", "Creates Nasal width, Nasal height, Nasal bone length, Nasal bone projection and angle.", self.create_measurements)
        self.add_workflow_step(workflow_layout1, "<b>Step 4: Predict Soft Tissue Landmarks</b>", "Opens prediction dialog for Pn, Sn, Al.", self.launch_prediction_dialog, is_final_step=True)
        stage1_layout.addWidget(workflow_group1)
        self.vbox.addWidget(stage1_group)

        # --- STAGE 2 ---
        stage2_group = self.create_stage_group("Stage 2: Optional Soft Tissue Comparison")
        stage2_layout = stage2_group.layout()
        inputs_group2 = qt.QGroupBox("Input"); inputs_layout2 = qt.QFormLayout(inputs_group2)
        self.soft_tissue_selector = self.create_node_selector("True Soft Tissue Fiducials:", "vtkMRMLMarkupsFiducialNode", "Ridel_soft_tissue")
        inputs_layout2.addRow(self.soft_tissue_selector['label'], self.soft_tissue_selector['selector'])
        self.download_soft_btn = qt.QPushButton("Download Soft Tissue Landmarks (.mrk.json)")
        self.download_soft_btn.clicked.connect(self.download_soft_tissue)
        inputs_layout2.addRow("", self.download_soft_btn)
        stage2_layout.addWidget(inputs_group2)
        workflow_group2 = self.create_step_group("Comparison Workflow"); workflow_layout2 = workflow_group2.layout()
        self.add_workflow_step(workflow_layout2, "<b>Step 5: Measure Prediction Errors</b>", "Measure distances between predicted and true soft tissue landmarks (Alare flagged per Ridel caveat).", self.measure_prediction_errors)
        self.add_workflow_step(workflow_layout2, "<b>Step 6: Show Detailed Results</b>", "Show a detailed table with distances, errors, and equations.", self.onShowDetailedResults, is_final_step=True)
        stage2_layout.addWidget(workflow_group2)
        self.vbox.addWidget(stage2_group)
        self.vbox.addStretch()
        self.main_widget.show()
        self.prediction_dialog = None
        self.detailedWidget = None

    # --- Download helpers ---
    def _download_and_load_markups(self, url, selector_dict, friendly_name):
        try:
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(url.split("?")[0])
            filepath = os.path.join(temp_dir, filename)
            slicer.util.showStatusMessage(f"Downloading {friendly_name}...", 3000)
            urllib.request.urlretrieve(url, filepath)
            existing = slicer.mrmlScene.GetFirstNodeByName(friendly_name)
            if existing:
                slicer.mrmlScene.RemoveNode(existing)
            loaded_node = slicer.util.loadMarkups(filepath)
            if not loaded_node:
                slicer.util.errorDisplay(f"Failed to load {friendly_name} from {filepath}")
                return
            if loaded_node.GetName() != friendly_name:
                loaded_node.SetName(friendly_name)
            selector_dict['selector'].setCurrentNode(loaded_node)
            slicer.util.showStatusMessage(f"{friendly_name} loaded successfully.", 3000)
        except Exception as e:
            slicer.util.errorDisplay(f"Error downloading/loading {friendly_name}:\n{str(e)}")

    def download_hard_tissue(self):
        url = "https://github.com/user-attachments/files/20970624/Ridel_hard_tissue.mrk.json"
        self._download_and_load_markups(url, self.hard_tissue_selector, "Ridel_hard_tissue")

    def download_soft_tissue(self):
        url = "https://github.com/user-attachments/files/20970625/Ridel_soft_tissue.mrk.json"
        self._download_and_load_markups(url, self.soft_tissue_selector, "Ridel_soft_tissue")

    # --- Layout helpers ---
    def create_stage_group(self, title):
        g = qt.QGroupBox(title); g.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }"); g.setLayout(qt.QVBoxLayout()); return g
    def create_node_selector(self, label_text, node_type, default_name=None):
        label = qt.QLabel(label_text); selector = slicer.qMRMLNodeComboBox(); selector.nodeTypes = [node_type]; selector.setMRMLScene(slicer.mrmlScene); selector.addEnabled = False; selector.removeEnabled = False; selector.noneEnabled = True
        if default_name:
            n = slicer.mrmlScene.GetFirstNodeByName(default_name)
            if n: selector.setCurrentNode(n)
        return {'label': label, 'selector': selector}
    def create_step_group(self, title):
        g = qt.QGroupBox(title); g.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }"); g.setLayout(qt.QVBoxLayout()); return g
    def add_workflow_step(self, parent_layout, title_html, description, callback, is_final_step=False):
        parent_layout.addWidget(qt.QLabel(title_html)); desc = qt.QLabel(description); desc.setWordWrap(True); parent_layout.addWidget(desc); btn = qt.QPushButton(title_html.split("</b>")[0].replace("<b>", "")); btn.clicked.connect(callback); parent_layout.addWidget(btn)
        if not is_final_step: sep = qt.QFrame(); sep.setFrameShape(qt.QFrame.HLine); sep.setFrameShadow(qt.QFrame.Sunken); parent_layout.addWidget(sep)
    def get_node(self, selector_dict, friendly_name):
        node = selector_dict['selector'].currentNode()
        if not node: slicer.util.warningDisplay(f"Please select '{friendly_name}'."); return None
        return node

    # --- Step 1 ---
    def create_blueprint_planes(self):
        fhp_plane = self.get_node(self.fhp_plane_selector, "FHP Plane")
        points_node = self.get_node(self.hard_tissue_selector, "Hard Tissue Fiducials")
        if not fhp_plane or not points_node:
            return
        if points_node.GetNumberOfControlPoints() < 5:
            slicer.util.errorDisplay("Need at least 5 landmarks: nasion, "
                                     "nasospinale, rhinion, right alare, left alare.")
            return

        for name in ['MSP', 'FRP']:
            node = slicer.mrmlScene.GetFirstNodeByName(name)
            if node:
                slicer.mrmlScene.RemoveNode(node)

        pts = [np.zeros(3) for _ in range(5)]
        for i in range(5):
            points_node.GetNthControlPointPosition(i, pts[i])
        nasion, nasospinale, rhinion, right_alare, left_alare = pts

        # ---- FHP normal (used exactly as the plane stores it) ----
        fhp_normal = np.zeros(3)
        fhp_plane.GetNormal(fhp_normal)
        if np.linalg.norm(fhp_normal) < 1e-9:
            slicer.util.errorDisplay("FHP plane has no valid normal.")
            return
        fhp_normal /= np.linalg.norm(fhp_normal)

        # ---- MSP normal: least-squares fit perpendicular to FHP ----
        # Build an orthonormal basis (u, v) of the plane perpendicular to FHP.
        u = np.array([1.0, 0.0, 0.0])
        u -= np.dot(u, fhp_normal) * fhp_normal
        if np.linalg.norm(u) < 1e-6:
            u = np.array([0.0, 1.0, 0.0])
            u -= np.dot(u, fhp_normal) * fhp_normal
        if np.linalg.norm(u) < 1e-6:
            slicer.util.errorDisplay("Cannot build a basis perpendicular to FHP.")
            return
        u /= np.linalg.norm(u)
        v = np.cross(fhp_normal, u)

        # Project the two landmark displacements from nasion into (u, v)
        d1 = nasospinale - nasion
        d2 = rhinion - nasion
        u1, v1 = np.dot(d1, u), np.dot(d1, v)
        u2, v2 = np.dot(d2, u), np.dot(d2, v)

        # 2x2 scatter matrix. Its smallest eigenvector is the plane normal
        # (in the (u, v) basis), i.e. the direction the plane should face so
        # that the three landmarks lie as close to it as possible.
        xx = u1 * u1 + u2 * u2
        xy = u1 * v1 + u2 * v2
        yy = v1 * v1 + v2 * v2
        if (xx + yy) < 1e-12:
            slicer.util.errorDisplay("Nasion, nasospinale, and rhinion coincide.")
            return
        _, evecs = np.linalg.eigh(np.array([[xx, xy], [xy, yy]]))
        a, b = evecs[0, 0], evecs[1, 0]      # smallest eigenvalue
        msp_normal = a * u + b * v
        msp_normal /= np.linalg.norm(msp_normal)

        # Canonicalize to point to the patient's right
        if np.dot(msp_normal, right_alare - left_alare) < 0:
            msp_normal = -msp_normal

        # ---- Anchor BOTH reference planes at the nasion ----
        anchor = nasion.copy()

        msp = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP')
        msp.SetNormalWorld(msp_normal)
        msp.SetOriginWorld(anchor)
        msp.SetSize(150, 150)

        frp_normal = np.cross(fhp_normal, msp_normal)
        frp_normal /= np.linalg.norm(frp_normal)

        frp = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'FRP')
        frp.SetNormalWorld(frp_normal)
        frp.SetOriginWorld(anchor)
        frp.SetSize(150, 150)
        frp_disp = frp.GetDisplayNode()
        frp_disp.SetColor(0.0, 0.75, 0.0)
        frp_disp.SetSelectedColor(0.0, 0.75, 0.0)
        frp_disp.SetOpacity(0.70)

        slicer.util.infoDisplay("Step 1: MSP and FRP created.")

    # --- Step 2 ---
    def create_anatomical_planes(self):
        points_node = self.get_node(self.hard_tissue_selector, "Hard Tissue Fiducials")
        if not points_node: return
        blueprint_nodes = {name: slicer.mrmlScene.GetFirstNodeByName(name) for name in ['FHP', 'MSP', 'FRP']}
        if not all(blueprint_nodes.values()): slicer.util.errorDisplay("Run Step 1 first."); return
        if points_node.GetNumberOfControlPoints() < 5: slicer.util.errorDisplay("Need at least 5 landmarks."); return
        pts = [np.zeros(3) for _ in range(5)]; [points_node.GetNthControlPointPosition(i, pts[i]) for i in range(5)]; nasion, nasospinale, rhinion, right_alare, left_alare = pts
        normals = {name: np.zeros(3) for name in blueprint_nodes}; [node.GetNormal(normals[name]) for name, node in blueprint_nodes.items()]
        plane_defs = [("nTr", nasion, normals['FHP'], [0,0,1]), ("rhiTr", rhinion, normals['FHP'], [0,0,1]), ("nsTr", nasospinale, normals['FHP'], [0,0,1]),("alLSa", left_alare, normals['MSP'], [1,1,0]), ("alRSa", right_alare, normals['MSP'], [1,1,0]),("nCor", nasion, normals['FRP'], [0,1,0]), ("rhiCor", rhinion, normals['FRP'], [0,1,0])]
        for name, point, normal, color in plane_defs:
            node = slicer.mrmlScene.GetFirstNodeByName(name)
            if node: slicer.mrmlScene.RemoveNode(node)
            plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', name); plane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneTypePointNormal); plane.SetNormalWorld(normal); plane.SetOriginWorld(point); plane.SetSize(180,180); d = plane.GetDisplayNode(); d.SetSelectedColor(color); d.SetColor(color); d.SetTextScale(4)
        slicer.util.infoDisplay("Step 2: Anatomical planes created.")

    # --- Step 3 ---
    def create_measurements(self):
        hard_tissue = self.get_node(self.hard_tissue_selector, "Hard Tissue Fiducials")
        if not hard_tissue: return
        needed = ["nTr","rhiTr","nsTr","alLSa","alRSa","nCor","rhiCor"]; planes = {n: slicer.mrmlScene.GetFirstNodeByName(n) for n in needed}
        if not all(planes.values()): slicer.util.errorDisplay("Run Step 2 first."); return
        for m_name in ["Nasal width", "Nasal height", "Nasal bone length", "Nasal bone projection", "Nasal bone angle", "nCor_line", "nTr_line"]:
            node = slicer.mrmlScene.GetFirstNodeByName(m_name)
            if node: slicer.mrmlScene.RemoveNode(node)
        def plane_dist(name, p1_name, p2_name):
            p1, p2 = planes[p1_name], planes[p2_name]; o1, n1, o2 = (np.zeros(3) for _ in range(3)); p1.GetOriginWorld(o1); p1.GetNormalWorld(n1); p2.GetOriginWorld(o2); dist = abs(np.dot(n1, o2 - o1))
            lm_indices = {'alLSa': 4, 'alRSa': 3, 'nTr': 0, 'nsTr': 1, 'rhiTr': 2, 'nCor': 0, 'rhiCor': 2}
            lm1, lm2 = np.zeros(3), np.zeros(3); hard_tissue.GetNthControlPointPosition(lm_indices[p1_name], lm1); hard_tissue.GetNthControlPointPosition(lm_indices[p2_name], lm2); mid = (lm1 + lm2) / 2.0
            s = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name); s.AddControlPointWorld(mid - n1 * dist/2.0); s.AddControlPointWorld(mid + n1 * dist/2.0); s.GetMeasurement('length').SetEnabled(True); s.GetDisplayNode().SetTextScale(4); s.GetDisplayNode().SetSelectedColor([0.2,0.8,0.2])
        plane_dist("Nasal width", "alLSa", "alRSa"); plane_dist("Nasal height", "nTr", "nsTr"); plane_dist("Nasal bone length", "nTr", "rhiTr"); plane_dist("Nasal bone projection", "nCor", "rhiCor")
        nasion, rhinion = np.zeros(3), np.zeros(3); hard_tissue.GetNthControlPointPosition(0, nasion); hard_tissue.GetNthControlPointPosition(2, rhinion); nasal_vec = rhinion - nasion; sup = nasion - nasal_vec * 1.5
        ntr_origin, ntr_n = np.zeros(3), np.zeros(3); planes["nTr"].GetOriginWorld(ntr_origin); planes["nTr"].GetNormalWorld(ntr_n); projected = nasion - np.dot(nasion - ntr_origin, ntr_n) * ntr_n
        ant_post_dir = np.cross(ntr_n, np.array([1,0,0])); ant_post_dir /= np.linalg.norm(ant_post_dir); posterior = projected - ant_post_dir * 25
        angle = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "Nasal bone angle"); angle.AddControlPointWorld(posterior); angle.AddControlPointWorld(nasion); angle.AddControlPointWorld(sup); angle.GetMeasurement('angle').SetEnabled(True); angle.GetDisplayNode().SetTextScale(4); angle.GetDisplayNode().SetSelectedColor([0.8,0.2,0.2])
        self.create_intersection_line("MSP","nCor", hard_tissue, 0, "nCor_line"); self.create_intersection_line("MSP","nTr", hard_tissue, 0, "nTr_line")
        slicer.util.infoDisplay("Step 3: Measurements created.")

    def create_intersection_line(self, p1_name, p2_name, pt_node, pt_idx, line_name):
        plane1, plane2 = slicer.mrmlScene.GetFirstNodeByName(p1_name), slicer.mrmlScene.GetFirstNodeByName(p2_name)
        if not (plane1 and plane2): return
        pt, n1, n2 = (np.zeros(3) for _ in range(3)); pt_node.GetNthControlPointPosition(pt_idx, pt); plane1.GetNormal(n1); plane2.GetNormal(n2); d = np.cross(n1, n2)
        if np.linalg.norm(d) > 1e-6: d /= np.linalg.norm(d)
        else: return
        ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", line_name); ln.AddControlPoint(pt - d*100); ln.AddControlPoint(pt + d*100); ln.GetDisplayNode().SetVisibility(False)

    # --- Step 4 ---
    def launch_prediction_dialog(self):
        needed = ["Nasal height","Nasal bone length","Nasal bone projection","nTr_line","nCor_line","Ridel_hard_tissue"]
        if any(not slicer.mrmlScene.GetFirstNodeByName(n) for n in needed):
            slicer.util.errorDisplay("Run Steps 1-3 first."); return
        if not self.prediction_dialog:
            self.prediction_dialog = PredictionDialog(self.main_widget)
        self.prediction_dialog.refresh_measurements()
        self.prediction_dialog.show()
        self.prediction_dialog.raise_()
        # Auto-open the Prediction Manager alongside the Prediction dialog
        self.prediction_dialog.manager.show()
        self.prediction_dialog.manager.refresh_list()
        self.prediction_dialog.manager.raise_()

    # --- Step 5 ---
    def measure_prediction_errors(self):
        # Ridel et al. (2018) caveat: Alare prediction is incomplete. Alare
        # error lines are still created for visualisation, but are drawn in
        # ORANGE and flagged in the results table.
        soft = self.get_node(self.soft_tissue_selector, "True Soft Tissue Fiducials")
        if not soft:
            return
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")
                      if n.GetName().startswith("Pred_")]
        if not pred_nodes:
            slicer.util.errorDisplay("Run Stage 1 first.")
            return

        # ---- Build the complete work list first (so we know the total) ----
        mapping = {"pn'": "Pn_", "sn'": "Sn_", "al'l": "AlL_", "al'r": "AlR_"}
        work_items = []   # (orig_pt, pred_node, pred_cp_index, target_name, is_alare)

        for i in range(soft.GetNumberOfControlPoints()):
            orig_label = soft.GetNthControlPointLabel(i).lower().replace(" ", "")
            orig_pt = np.zeros(3)
            soft.GetNthControlPointPosition(i, orig_pt)
            for key, prefix in mapping.items():
                if key in orig_label:
                    is_alare = prefix.startswith("Al")
                    for pred_node in pred_nodes:
                        for j in range(pred_node.GetNumberOfControlPoints()):
                            plabel = pred_node.GetNthControlPointLabel(j)
                            if plabel.startswith(prefix):
                                target_name = f"error_{pred_node.GetName()}_{prefix}"
                                work_items.append((orig_pt, pred_node, j,
                                                   target_name, is_alare))

        total = len(work_items)
        if total == 0:
            slicer.util.warningDisplay(
                "No matching predicted-vs-true landmark pairs were found.\n"
                "Check that the soft-tissue landmark labels contain "
                "pn', sn', al'l, or al'r."
            )
            return

        # ---- Progress dialog (cancellable, non-auto-closing) ----
        progress = qt.QProgressDialog(
            f"Measuring prediction errors ({total} line(s))...",
            "Cancel", 0, total, self.main_widget
        )
        progress.setWindowTitle("Measuring Prediction Errors")
        progress.setWindowModality(qt.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setValue(0)
        _process_gui_events()

        created = 0
        cancelled = False

        for idx, (orig_pt, pred_node, j, target_name, is_alare) in enumerate(work_items, start=1):
            # ---- Cancellation check at the top of the iteration ----
            if _progress_was_cancelled(progress):
                cancelled = True
                break

            progress.setLabelText(
                f"Creating error line {idx} of {total}...\n"
                f"Created: {created}"
            )
            progress.setValue(idx - 1)
            _process_gui_events()

            ppt = np.zeros(3)
            pred_node.GetNthControlPointPosition(j, ppt)

            existing = slicer.mrmlScene.GetFirstNodeByName(target_name)
            if existing:
                slicer.mrmlScene.RemoveNode(existing)

            ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", target_name)
            ln.AddControlPoint(orig_pt)
            ln.AddControlPoint(ppt)
            if is_alare:
                ln.GetDisplayNode().SetColor([1.0, 0.55, 0.0])   # orange = caveat
            else:
                ln.GetDisplayNode().SetColor([0.0, 1.0, 0.0])    # green  = valid
            ln.GetDisplayNode().SetLineThickness(0.2)
            ln.GetMeasurement('length').SetEnabled(True)
            created += 1

        # ---- Close out the progress dialog ----
        progress.setValue(total)
        progress.close()
        _process_gui_events()

        # ---- Summary ----
        if cancelled:
            msg = f"Cancelled after creating {created} of {total} error line(s)."
        else:
            msg = f"Step 5: {created} error line(s) created."
        msg += (
            "\n\nAlare error lines are drawn in ORANGE and must be interpreted "
            "with the Ridel et al. (2018) caveat: Alare prediction is incomplete "
            "and is NOT recommended for quantitative error comparison."
        )
        slicer.util.infoDisplay(msg)

    # --- Step 6 ---
    def onShowDetailedResults(self):
        soft_node = self.get_node(self.soft_tissue_selector, "True Soft Tissue Fiducials")
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if n.GetName().startswith("Pred_")]
        if not self.prediction_dialog or not pred_nodes:
            slicer.util.warningDisplay("Please run at least one prediction first.")
            return

        self.detailedWidget = qt.QDialog(self.main_widget)
        self.detailedWidget.setWindowTitle("Detailed Prediction Results")
        self.detailedWidget.setMinimumSize(2200, 900)
        layout = qt.QVBoxLayout(self.detailedWidget)
        table = qt.QTableWidget()

        headers = [
            "Prediction Set", "Original Landmark", "Predicted Landmark Name",
            "nTr Calc: HT Measurements", "nTr Calc: Equation", "nTr Calc: Value (mm)",
            "nCor Calc: HT Measurements", "nCor Calc: Equation", "nCor Calc: Value (mm)",
            "Ancestry in Equation",
            "Predicted X (mm)", "Predicted Y (mm)", "Predicted Z (mm)",
            "True X (mm)", "True Y (mm)", "True Z (mm)",
            "Final Error (mm)"
        ]
        # Column index constants (keeps row-writing readable and less error-prone)
        COL_PRED_SET       = 0
        COL_ORIG_LM        = 1
        COL_PRED_NAME      = 2
        COL_NTR_VARS       = 3
        COL_NTR_EQ         = 4
        COL_NTR_VAL        = 5
        COL_NCOR_VARS      = 6
        COL_NCOR_EQ        = 7
        COL_NCOR_VAL       = 8
        COL_ANCESTRY       = 9
        COL_PRED_X         = 10
        COL_PRED_Y         = 11
        COL_PRED_Z         = 12
        COL_TRUE_X         = 13
        COL_TRUE_Y         = 14
        COL_TRUE_Z         = 15
        COL_ERROR          = 16

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        true_map = {"pn'":"Pn_", "sn'":"Sn_", "al'l":"AlL_", "al'r":"AlR_"}
        true_dict = {}
        if soft_node:
            for i in range(soft_node.GetNumberOfControlPoints()):
                label = soft_node.GetNthControlPointLabel(i).lower().replace(" ","")
                for key, prefix in true_map.items():
                    if key in label:
                        pos = np.zeros(3)
                        soft_node.GetNthControlPointPosition(i, pos)
                        true_dict[prefix] = pos
                        break

        all_equations = self.prediction_dialog.get_equations()

        table.setRowCount(sum(node.GetNumberOfControlPoints() for node in pred_nodes))
        current_row = 0
        for pred_node in pred_nodes:
            for i in range(pred_node.GetNumberOfControlPoints()):
                pred_label = pred_node.GetNthControlPointLabel(i)
                pred_pos = np.zeros(3)
                pred_node.GetNthControlPointPosition(i, pred_pos)

                table.setItem(current_row, COL_PRED_SET,  qt.QTableWidgetItem(pred_node.GetName()))
                table.setItem(current_row, COL_PRED_NAME, qt.QTableWidgetItem(pred_label))

                original_lm, ancestry, ntr_breakdown, ncor_breakdown = \
                    self.get_calculation_breakdown(pred_label, all_equations)

                table.setItem(current_row, COL_ORIG_LM,   qt.QTableWidgetItem(original_lm))
                table.setItem(current_row, COL_NTR_VARS,  qt.QTableWidgetItem(ntr_breakdown['vars']))
                table.setItem(current_row, COL_NTR_EQ,    qt.QTableWidgetItem(ntr_breakdown['eq']))
                table.setItem(current_row, COL_NTR_VAL,   qt.QTableWidgetItem(ntr_breakdown['val']))
                table.setItem(current_row, COL_NCOR_VARS, qt.QTableWidgetItem(ncor_breakdown['vars']))
                table.setItem(current_row, COL_NCOR_EQ,   qt.QTableWidgetItem(ncor_breakdown['eq']))
                table.setItem(current_row, COL_NCOR_VAL,  qt.QTableWidgetItem(ncor_breakdown['val']))
                table.setItem(current_row, COL_ANCESTRY,  qt.QTableWidgetItem(ancestry))

                # ---- Predicted XYZ ----
                table.setItem(current_row, COL_PRED_X, qt.QTableWidgetItem(f"{pred_pos[0]:.2f}"))
                table.setItem(current_row, COL_PRED_Y, qt.QTableWidgetItem(f"{pred_pos[1]:.2f}"))
                table.setItem(current_row, COL_PRED_Z, qt.QTableWidgetItem(f"{pred_pos[2]:.2f}"))

                # ---- True XYZ (and error) ----
                base_lm_prefix = pred_label.split('_')[0] + '_'
                is_alare = base_lm_prefix.startswith("Al")

                if base_lm_prefix in true_dict:
                    true_pos = true_dict[base_lm_prefix]
                    table.setItem(current_row, COL_TRUE_X, qt.QTableWidgetItem(f"{true_pos[0]:.2f}"))
                    table.setItem(current_row, COL_TRUE_Y, qt.QTableWidgetItem(f"{true_pos[1]:.2f}"))
                    table.setItem(current_row, COL_TRUE_Z, qt.QTableWidgetItem(f"{true_pos[2]:.2f}"))

                    error = np.linalg.norm(pred_pos - true_pos)
                    if is_alare:
                        # Ridel caveat: mark with warning glyph
                        cell = qt.QTableWidgetItem(f"{error:.2f} ⚠")
                        cell.setBackground(qt.QColor(255, 235, 200))
                        table.setItem(current_row, COL_ERROR, cell)
                    else:
                        table.setItem(current_row, COL_ERROR, qt.QTableWidgetItem(f"{error:.2f}"))
                else:
                    for c in (COL_TRUE_X, COL_TRUE_Y, COL_TRUE_Z, COL_ERROR):
                        table.setItem(current_row, c, qt.QTableWidgetItem("N/A"))

                # Tint the "Original Landmark" cell for Al rows too
                if is_alare:
                    lc = table.item(current_row, COL_ORIG_LM)
                    if lc:
                        lc.setBackground(qt.QColor(255, 235, 200))

                current_row += 1

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        layout.addWidget(table)

        # ---- Caveat banner ----
        caveat = qt.QLabel(
            "<b>⚠ Alare caveat (Ridel et al. 2018):</b> "
            "The regression for the alare is <i>incomplete</i> by the authors' own "
            "statement. Predicted alare points are shown for visualisation only. "
            "The distance displayed for AlL/AlR is provided for completeness and "
            "must NOT be interpreted as a validated prediction error."
        )
        caveat.setWordWrap(True)
        caveat.setStyleSheet(
            "QLabel { background-color: #FFF3CD; color: #664D03; "
            "border: 1px solid #FFECB5; border-radius: 4px; padding: 8px; }"
        )
        layout.addWidget(caveat)

        copy_button = qt.QPushButton("Copy Table to Clipboard")
        copy_button.clicked.connect(lambda: self.onCopyToClipboard(table))
        layout.addWidget(copy_button)
        self.detailedWidget.show() 
    # --- Parsing ---
    def get_calculation_breakdown(self, label, all_equations):
        parts = label.split('_')
        lm_part, eq_parts = parts[0], parts[1:]

        lm_map = {"Pn": "pronasale", "Sn": "subnasale", "AlL": "alare (left)", "AlR": "alare (right)"}
        original_lm = lm_map.get(lm_part, "Unknown")

        eq_codes = []
        if lm_part in ["Pn", "Sn"]:
            if len(eq_parts) >= 6:
                eq_codes.append("_".join(eq_parts[0:3]))
                eq_codes.append("_".join(eq_parts[3:6]))
        elif lm_part in ["AlL", "AlR"]:
            if len(eq_parts) >= 3:
                eq_codes.append("_".join(eq_parts[0:3]))

        ancestry = "Unknown"
        pop_map = {"BSA": "Black South African", "WSA": "White South African"}
        if eq_codes and eq_codes[0].startswith("BSA"): ancestry = pop_map["BSA"]
        if eq_codes and eq_codes[0].startswith("WSA"): ancestry = pop_map["WSA"]

        def get_breakdown_for_eq(eq_code):
            breakdown = {'eq': "N/A", 'vars': "N/A", 'val': "N/A"}
            if self.prediction_dialog and eq_code and eq_code in all_equations:
                eq_text = all_equations[eq_code]['text']
                breakdown['eq'] = eq_text
                used_vars = []
                var_map = {"NH": "Nasal height", "NBL": "Nasal bone length", "NBP": "Nasal bone projection"}
                for var_code, var_name in var_map.items():
                    if var_code in eq_text: used_vars.append(var_name)
                breakdown['vars'] = "; ".join(used_vars) if used_vars else "Constant"
                measurements = self.prediction_dialog.measurements
                formula = eq_text.replace('−','-').replace('×','*')
                is_calculable = True
                for var_text, var_name in var_map.items():
                    if var_text in formula:
                        value = measurements.get(var_name)
                        if value is None:
                            is_calculable = False; break
                        formula = formula.replace(var_text, str(value))
                if is_calculable:
                    try:
                        value = eval(formula, {"__builtins__": {}})
                        breakdown['val'] = f"{value:.2f}"
                    except:
                        breakdown['val'] = "Error"
                else:
                    breakdown['val'] = "Missing HT"
            return breakdown

        ntr_code = eq_codes[0] if len(eq_codes) > 0 else None
        ncor_code = eq_codes[1] if len(eq_codes) > 1 else None
        ntr_breakdown = get_breakdown_for_eq(ntr_code)
        ncor_breakdown = get_breakdown_for_eq(ncor_code)
        return original_lm, ancestry, ntr_breakdown, ncor_breakdown

    def onCopyToClipboard(self, table_widget):
        clipboard = qt.QApplication.clipboard()
        if not clipboard:
            slicer.util.warningDisplay("Clipboard not available."); return
        text = "\t".join([table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount)]) + "\n"
        for row in range(table_widget.rowCount):
            text += "\t".join([table_widget.item(row, col).text().replace('\n', ' | ') if table_widget.item(row, col) else "" for col in range(table_widget.columnCount)]) + "\n"
        clipboard.setText(text)
        slicer.util.showStatusMessage("Table contents copied to clipboard.", 3000)

    def close_all_dialogs(self):
        if self.detailedWidget and self.detailedWidget.isWidgetType(): self.detailedWidget.close()
        if self.prediction_dialog and self.prediction_dialog.isWidgetType():
            if self.prediction_dialog.manager and self.prediction_dialog.manager.isWidgetType():
                self.prediction_dialog.manager.close()
            self.prediction_dialog.close()


class PredictionDialog(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Facial Landmark Prediction Tool")
        self.setMinimumWidth(560)
        self.main_vlayout = qt.QVBoxLayout(self)

        name_h = qt.QHBoxLayout(); name_h.addWidget(qt.QLabel("Prediction Set Name:"))
        self.name_edit = qt.QLineEdit(f"Pred_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        name_h.addWidget(self.name_edit); self.main_vlayout.addLayout(name_h)

        pop_h = qt.QHBoxLayout(); pop_h.addWidget(qt.QLabel("Population:"))
        self.pop_combo = qt.QComboBox(); self.pop_combo.addItems(["Black South African","White South African"])
        pop_h.addWidget(self.pop_combo); self.main_vlayout.addLayout(pop_h)

        self.meas_group = qt.QGroupBox("Available Measurements")
        self.meas_layout = qt.QFormLayout(self.meas_group)
        self.main_vlayout.addWidget(self.meas_group)

        self.pn_group = self.create_landmark_group('pn', "Pronasale (Pn)", "Pn to nTr:", "Pn to nCor:")
        self.sn_group = self.create_landmark_group('sn', "Subnasale (Sn)", "Sn to nTr:", "Sn to nCor:")
        self.al_group = self.create_landmark_group('al', "Alare (Al)", "Al to nTr:", None)

        al_caveat = qt.QLabel(
            "<i>Note: Alare uses Nasal width for lateral placement. "
            "Ridel et al. (2018) warn that Alare prediction is incomplete — "
            "predicted alare points are for visualisation only and are not "
            "recommended for quantitative error comparison.</i>"
        )
        al_caveat.setWordWrap(True)
        al_caveat.setStyleSheet("QLabel { color: #8A6D3B; }")
        self.al_group.layout().addWidget(al_caveat)

        self.create_btn = qt.QPushButton("Create New Prediction Set")
        self.create_btn.setStyleSheet("background-color: #CCFFCC; font-weight: bold; padding: 8px;")
        self.main_vlayout.addWidget(self.create_btn)

        # --- NEW: Run all combinations button ---
        self.run_all_btn = qt.QPushButton("Run All Possible Combinations for Group")
        self.run_all_btn.setStyleSheet("background-color: #CCE5FF; font-weight: bold; padding: 8px;")
        self.run_all_btn.setToolTip(
            "Creates one prediction set per combination of the regressions "
            "available for the chosen population, across every checked "
            "landmark group. Respects the checkboxes for Pn, Sn, and Al."
        )
        self.main_vlayout.addWidget(self.run_all_btn)

        self.manager_btn = qt.QPushButton("Show/Hide Prediction Manager")
        self.main_vlayout.addWidget(self.manager_btn)
        self.manager = PredictionManager(self)

        self.pop_combo.currentIndexChanged.connect(self.update_equations)
        self.create_btn.clicked.connect(self.create_prediction_set)
        self.run_all_btn.clicked.connect(self.run_all_combinations)
        self.manager_btn.clicked.connect(self.toggle_manager)
        self.measurements = {}
        self.update_equations()

    # ---------------------------------------------------------------
    def create_landmark_group(self, key, title, label1, label2):
        g = qt.QGroupBox(title); g.setCheckable(True); g.setChecked(True)
        form = qt.QFormLayout(g)
        c1 = qt.QComboBox(); setattr(self, f"{key}_combo1", c1); form.addRow(label1, c1)
        if label2:
            c2 = qt.QComboBox(); setattr(self, f"{key}_combo2", c2); form.addRow(label2, c2)
        else:
            setattr(self, f"{key}_combo2", None)
        self.main_vlayout.addWidget(g); return g

    # ---------------------------------------------------------------
    def refresh_measurements(self):
        while self.meas_layout.count():
            item = self.meas_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        self.measurements = {}; ok = True
        for n in ["Nasal height","Nasal width","Nasal bone length","Nasal bone projection"]:
            node = slicer.mrmlScene.GetFirstNodeByName(n)
            if node and isinstance(node, slicer.vtkMRMLMarkupsLineNode):
                val = node.GetMeasurement('length').GetValue()
                self.measurements[n] = val
                self.meas_layout.addRow(n, qt.QLabel(f"{val:.2f} mm"))
            else:
                self.measurements[n] = None; ok = False
                l = qt.QLabel("NOT FOUND"); l.setStyleSheet("color: red")
                self.meas_layout.addRow(n, l)
        self.create_btn.setEnabled(ok)
        self.run_all_btn.setEnabled(ok)

    # ---------------------------------------------------------------
    def update_equations(self):
        is_bsa = (self.pop_combo.currentText == "Black South African")
        pop = "BSA" if is_bsa else "WSA"
        eqs = self.get_equations()

        def fill(combo, keys):
            if not combo: return
            combo.clear()
            for k in keys:
                if k in eqs:
                    combo.addItem(eqs[k]['text'], k)

        # ---- Pronasale (Pn) ----
        if is_bsa:
            fill(self.pn_combo1, ["BSA_pn_nh"])
            fill(self.pn_combo2, ["BSA_pn_nbl"])
        else:
            fill(self.pn_combo1, ["WSA_pn_nh", "WSA_pn_nbl", "WSA_pn_nh+nbl"])
            fill(self.pn_combo2, ["WSA_pn_nbp"])

        # ---- Subnasale (Sn) ----
        fill(self.sn_combo1, [f"{pop}_sn_nh", f"{pop}_sn_nbl", f"{pop}_sn_nh+nbl"])
        fill(self.sn_combo2, [f"{pop}_sn_nbp"])

        # ---- Alare (Al) ----
        fill(self.al_combo1, [f"{pop}_al_nh", f"{pop}_al_nbl", f"{pop}_al_nh+nbl"])

    # ---------------------------------------------------------------
    def create_prediction_set(self):
        name = self.name_edit.text.strip()
        if not name or not name.startswith("Pred_"):
            slicer.util.errorDisplay("Name must start with 'Pred_'."); return
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node and qt.QMessageBox.question(self, "Overwrite?", f"'{name}' exists. Overwrite?") == qt.QMessageBox.No:
            return
        if node:
            slicer.mrmlScene.RemoveNode(node)
        pred = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", name)
        pred.GetDisplayNode().SetTextScale(3.0)

        for key in ['pn', 'sn']:
            group = getattr(self, f"{key}_group")
            if group.isChecked():
                c1, c2 = getattr(self, f"{key}_combo1"), getattr(self, f"{key}_combo2")
                d1 = self.calculate_from_combo(c1); d2 = self.calculate_from_combo(c2)
                if d1 is not None and d2 is not None:
                    self.place_landmark(pred, f"{key.capitalize()}_{c1.currentData}_{c2.currentData}", d1, d2)

        if self.al_group.isChecked():
            c1 = self.al_combo1; d1 = self.calculate_from_combo(c1)
            if d1 is not None:
                self.place_landmark(pred, f"AlL_{c1.currentData}", d1, None, is_alare=True, is_left=True)
                self.place_landmark(pred, f"AlR_{c1.currentData}", d1, None, is_alare=True, is_left=False)

        slicer.util.infoDisplay(f"Created '{name}'.")
        self.manager.refresh_list()
        self.name_edit.setText(f"Pred_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # ---------------------------------------------------------------
    # --- NEW: Run all combinations for the chosen population ---
    def run_all_combinations(self):
        import itertools

        pop_label = self.pop_combo.currentText
        pop = "BSA" if pop_label == "Black South African" else "WSA"

        # --- Collect the available regression keys per landmark group ---
        group_combos = {}
        if self.pn_group.isChecked():
            k1 = [self.pn_combo1.itemData(i) for i in range(self.pn_combo1.count)]
            k2 = [self.pn_combo2.itemData(i) for i in range(self.pn_combo2.count)]
            group_combos['pn'] = [(a, b) for a in k1 for b in k2]
        if self.sn_group.isChecked():
            k1 = [self.sn_combo1.itemData(i) for i in range(self.sn_combo1.count)]
            k2 = [self.sn_combo2.itemData(i) for i in range(self.sn_combo2.count)]
            group_combos['sn'] = [(a, b) for a in k1 for b in k2]
        if self.al_group.isChecked():
            k1 = [self.al_combo1.itemData(i) for i in range(self.al_combo1.count)]
            group_combos['al'] = [(a,) for a in k1]

        if not group_combos:
            slicer.util.warningDisplay("No landmark groups are checked. "
                                       "Tick at least one of Pn, Sn, or Al.")
            return

        # --- Cartesian product across all checked groups ---
        group_keys = list(group_combos.keys())
        all_combos = list(itertools.product(*[group_combos[k] for k in group_keys]))
        total = len(all_combos)

        if total > 100:
            if qt.QMessageBox.question(
                    self, "Large batch",
                    f"This will create {total} prediction sets. Continue?"
                 ) == qt.QMessageBox.No:
                return

        # --- Progress dialog ---
        progress = qt.QProgressDialog(
            f"Creating {total} prediction set(s) for {pop_label}...",
            "Cancel", 0, total, self
        )
        progress.setWindowTitle("Running all combinations")
        progress.setWindowModality(qt.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setValue(0)
        progress.show()
        _process_gui_events()
        

        base_ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        created = []
        skipped = 0
        cancelled = False

        for idx, combo_tuple in enumerate(all_combos, start=1):
            if _progress_was_cancelled(progress):
                cancelled = True
                break

            combo_bits = []
            for key, combo in zip(group_keys, combo_tuple):
                if isinstance(combo, tuple):
                    combo_bits.append(" + ".join(combo))
                else:
                    combo_bits.append(combo)
            combo_desc = "  |  ".join(combo_bits)

            progress.setLabelText(
                f"Creating set {idx} of {total} for {pop_label}...\n"
                f"{combo_desc}\n"
                f"Created: {len(created)}   Skipped: {skipped}"
            )
            progress.setValue(idx - 1)
            _process_gui_events()
            

            name = f"Pred_{base_ts}_c{idx:02d}"
            existing = slicer.mrmlScene.GetFirstNodeByName(name)
            if existing:
                slicer.mrmlScene.RemoveNode(existing)

            pred = slicer.mrmlScene.AddNewNodeByClass(
                "vtkMRMLMarkupsFiducialNode", name
            )
            pred.GetDisplayNode().SetTextScale(3.0)

            placed_any = False
            for key, combo in zip(group_keys, combo_tuple):
                if key in ('pn', 'sn'):
                    c1_data, c2_data = combo
                    d1 = self.calculate_from_data(c1_data)
                    d2 = self.calculate_from_data(c2_data)
                    if d1 is not None and d2 is not None:
                        self.place_landmark(
                            pred,
                            f"{key.capitalize()}_{c1_data}_{c2_data}",
                            d1, d2
                        )
                        placed_any = True
                elif key == 'al':
                    c1_data = combo[0]
                    d1 = self.calculate_from_data(c1_data)
                    if d1 is not None:
                        self.place_landmark(pred, f"AlL_{c1_data}", d1, None,
                                            is_alare=True, is_left=True)
                        self.place_landmark(pred, f"AlR_{c1_data}", d1, None,
                                            is_alare=True, is_left=False)
                        placed_any = True

            if placed_any:
                created.append(name)
            else:
                slicer.mrmlScene.RemoveNode(pred)
                skipped += 1

            progress.setValue(idx)
            _process_gui_events()
            

        progress.setValue(total)
        progress.close()
        _process_gui_events()
        

        self.manager.refresh_list()

        # --- Summary ---
        if cancelled:
            msg = (f"Cancelled after creating {len(created)} of {total} "
                   f"set(s) for {pop_label}.")
        else:
            msg = (f"Created {len(created)} prediction set(s) for {pop_label}.\n"
                   f"Total combinations attempted: {total}.")
        if skipped:
            msg += f"\nSkipped (missing measurements): {skipped}."
        msg += "\n\nCheck the Prediction Set Manager to toggle visibility or delete sets."
        slicer.util.infoDisplay(msg)

    # ---------------------------------------------------------------
    def place_landmark(self, pred_node, name, ntr_dist, ncor_dist,
                       is_alare=False, is_left=None):
        """
        Place a predicted landmark at the intersection of two offset planes:

            - a plane parallel to nCor (normal = FRP_normal), offset ANTERIORLY
              by ncor_dist
            - a plane parallel to nTr  (normal = FHP_normal), offset INFERIORLY
              by ntr_dist

        Both offsets are applied SIMULTANEOUSLY from the nasion. Because
        FRP_normal ⊥ FHP_normal by construction, the two offsets are
        independent and their sum is the exact intersection of the two
        offset planes.
        """
        hard = slicer.mrmlScene.GetFirstNodeByName("Ridel_hard_tissue")
        if not hard:
            return

        nasion      = np.zeros(3); hard.GetNthControlPointPosition(0, nasion)
        nasospinale = np.zeros(3); hard.GetNthControlPointPosition(1, nasospinale)
        rhinion     = np.zeros(3); hard.GetNthControlPointPosition(2, rhinion)

        msp_n = np.zeros(3); slicer.mrmlScene.GetFirstNodeByName('MSP').GetNormal(msp_n)
        msp_n /= np.linalg.norm(msp_n)

        fhp_n = np.zeros(3); slicer.mrmlScene.GetFirstNodeByName('FHP').GetNormal(fhp_n)
        fhp_n /= np.linalg.norm(fhp_n)
        if np.dot(fhp_n, nasion - nasospinale) < 0:
            fhp_n = -fhp_n

        frp_n = np.zeros(3); slicer.mrmlScene.GetFirstNodeByName('FRP').GetNormal(frp_n)
        frp_n /= np.linalg.norm(frp_n)
        if np.dot(frp_n, rhinion - nasion) < 0:
            frp_n = -frp_n

        a = ncor_dist if ncor_dist is not None else 0.0
        b = ntr_dist  if ntr_dist  is not None else 0.0

        final = nasion + frp_n * a - fhp_n * b

        if is_alare:
            try:
                width = slicer.mrmlScene.GetFirstNodeByName("Nasal width") \
                            .GetMeasurement('length').GetValue()
                side = -1.0 if is_left else 1.0
                final = final + msp_n * (width / 2.0) * side
            except Exception as e:
                print(f"Warning: alare lateral offset skipped: {e}")

        idx = pred_node.AddControlPoint(final)
        pred_node.SetNthControlPointLabel(idx, name)

    # ---------------------------------------------------------------
    def calculate_from_data(self, key):
        """Evaluate the equation keyed by `key` using the current HT
        measurements. Returns None if the key is unknown or a required
        measurement is missing."""
        if not key:
            return None
        eqs = self.get_equations()
        if key not in eqs:
            return None
        eq_text = eqs[key]['text']
        nh  = self.measurements.get("Nasal height")
        nbl = self.measurements.get("Nasal bone length")
        nbp = self.measurements.get("Nasal bone projection")
        if ('NH'  in eq_text and nh  is None) or \
           ('NBL' in eq_text and nbl is None) or \
           ('NBP' in eq_text and nbp is None):
            return None
        formula = (eq_text.replace('−','-').replace('×','*')
                          .replace('NH',  str(nh))
                          .replace('NBL', str(nbl))
                          .replace('NBP', str(nbp)))
        try:
            return eval(formula, {"__builtins__": {}})
        except Exception:
            return None

    def calculate_from_combo(self, combo):
        if not combo:
            return None
        return self.calculate_from_data(combo.currentData)

    # ---------------------------------------------------------------
    def get_equations(self):
        # Keys: <POP>_<LM>_<PREDICTOR>. POP: BSA|WSA ; LM: pn|sn|al
        #   *_nh, *_nbl, *_nh+nbl  -> distance to nTr plane
        #   *_nbp                  -> distance to nCor plane
        # Special BSA Pronasale case: Pn-to-nCor uses NBL (not NBP).
        return {
            # ---------------- Black South Africans ----------------
            'BSA_pn_nh':      {'text': '−17.805+1.170*NH'},
            'BSA_pn_nbl':     {'text': '30.403-0.290*NBL'},
            'BSA_sn_nh':      {'text': '−5.208+1.140*NH'},
            'BSA_sn_nbl':     {'text': '29.723+1.092*NBL'},
            'BSA_sn_nh+nbl':  {'text': '1.270+0.795*NH+0.531*NBL'},
            'BSA_sn_nbp':     {'text': '3.063+1.060*NBP'},
            'BSA_al_nh':      {'text': '−7.148+1.036*NH'},
            'BSA_al_nbl':     {'text': '25.608+0.943*NBL'},
            'BSA_al_nh+nbl':  {'text': '−2.369+0.782*NH+0.391*NBL'},

            # ---------------- White South Africans ----------------
            'WSA_pn_nh':      {'text': '−7.969+0.963*NH'},
            'WSA_pn_nbl':     {'text': '22.859+1.004*NBL'},
            'WSA_pn_nh+nbl':  {'text': '−1.341+0.633*NH+0.554*NBL'},
            'WSA_pn_nbp':     {'text': '19.616+1.085*NBP'},
            'WSA_sn_nh':      {'text': '2.950+0.991*NH'},
            'WSA_sn_nbl':     {'text': '37.287+0.891*NBL'},
            'WSA_sn_nh+nbl':  {'text': '6.850+0.797*NH+0.326*NBL'},
            'WSA_sn_nbp':     {'text': '5.055+1.050*NBP'},
            'WSA_al_nh':      {'text': '1.974+0.876*NH'},
            'WSA_al_nbl':     {'text': '32.924+0.757*NBL'},
            'WSA_al_nh+nbl':  {'text': '4.779+0.737*NH+0.234*NBL'},
        }

    # ---------------------------------------------------------------
    def toggle_manager(self):
        if self.manager.isVisible():
            self.manager.hide()
        else:
            self.manager.show(); self.manager.refresh_list()


class PredictionManager(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prediction Set Manager")
        self.setWindowFlags(self.windowFlags() | qt.Qt.Tool)
        manager_layout = qt.QVBoxLayout(self)
        self.table = qt.QTableWidget(); self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name","Visibility","Delete"])
        manager_layout.addWidget(self.table)
        self.refresh_btn = qt.QPushButton("Refresh")
        manager_layout.addWidget(self.refresh_btn)
        self.refresh_btn.clicked.connect(self.refresh_list)
        close_btn = qt.QPushButton("Close Manager")
        manager_layout.addWidget(close_btn)
        close_btn.clicked.connect(lambda: self.close())
        self.refresh_list()

    def refresh_list(self):
        self.table.setRowCount(0)
        nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if n.GetName().startswith("Pred_")]
        self.table.setRowCount(len(nodes))
        for i, n in enumerate(nodes):
            self.table.setItem(i, 0, qt.QTableWidgetItem(n.GetName()))
            vis_btn = qt.QPushButton("Toggle"); vis_btn.setCheckable(True)
            vis_btn.setChecked(n.GetDisplayVisibility())
            vis_btn.toggled.connect(lambda checked, name=n.GetName(): self.toggle_vis(name, checked))
            self.table.setCellWidget(i, 1, vis_btn)
            del_btn = qt.QPushButton("Delete")
            del_btn.clicked.connect(lambda name=n.GetName(): self.delete_node(name))
            self.table.setCellWidget(i, 2, del_btn)
        self.table.resizeColumnsToContents()

    def toggle_vis(self, name, checked):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node: node.SetDisplayVisibility(checked)

    def delete_node(self, name):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node and qt.QMessageBox.question(self, "Delete", f"Delete {name}?") == qt.QMessageBox.Yes:
            slicer.mrmlScene.RemoveNode(node); self.refresh_list()


# --- Cleanup and Run ---
try:
    if 'ridel_gui_instance' in globals() and globals()['ridel_gui_instance'] and globals()['ridel_gui_instance'].main_widget.isWidgetType():
        globals()['ridel_gui_instance'].close_all_dialogs()
        globals()['ridel_gui_instance'].main_widget.close()
except:
    pass

ridel_gui_instance = RidelGUI()


```
