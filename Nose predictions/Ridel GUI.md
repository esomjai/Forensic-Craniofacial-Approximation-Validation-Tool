```python
# Copy-paste into 3D Slicer Python Interactor
import slicer
import qt
import numpy as np
import datetime
import os
import urllib.request
import tempfile

# --- Final Ridel GUI with parenting and parsing fix ---
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
        # --- NEW: Download button for hard tissue landmarks ---
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
        # --- NEW: Download button for soft tissue landmarks ---
        self.download_soft_btn = qt.QPushButton("Download Soft Tissue Landmarks (.mrk.json)")
        self.download_soft_btn.clicked.connect(self.download_soft_tissue)
        inputs_layout2.addRow("", self.download_soft_btn)
        stage2_layout.addWidget(inputs_group2)
        workflow_group2 = self.create_step_group("Comparison Workflow"); workflow_layout2 = workflow_group2.layout()
        self.add_workflow_step(workflow_layout2, "<b>Step 5: Measure Prediction Errors</b>", "Measure distances between predicted and true soft tissue landmarks.", self.measure_prediction_errors)
        self.add_workflow_step(workflow_layout2, "<b>Step 6: Show Detailed Results</b>", "Show a detailed table with distances, errors, and equations.", self.onShowDetailedResults, is_final_step=True)
        stage2_layout.addWidget(workflow_group2)
        self.vbox.addWidget(stage2_group)
        self.vbox.addStretch()
        self.main_widget.show()
        self.prediction_dialog = None
        self.detailedWidget = None

    # --- NEW: Helper method to download and load a markups file from a URL ---
    def _download_and_load_markups(self, url, selector_dict, friendly_name):
        """Download a .mrk.json file from a URL, load it into Slicer,
        and select it in the given node selector."""
        try:
            # Create a temporary file path with a meaningful name
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(url.split("?")[0])  # strip query params
            filepath = os.path.join(temp_dir, filename)

            # Download the file
            slicer.util.showStatusMessage(f"Downloading {friendly_name}...", 3000)
            urllib.request.urlretrieve(url, filepath)

            # Remove any existing node with the same name to avoid duplicates
            existing = slicer.mrmlScene.GetFirstNodeByName(friendly_name)
            if existing:
                slicer.mrmlScene.RemoveNode(existing)

            # Load the markups file into the scene
            loaded_node = slicer.util.loadMarkups(filepath)
            if not loaded_node:
                slicer.util.errorDisplay(f"Failed to load {friendly_name} from {filepath}")
                return

            # Rename the loaded node to the friendly name if it differs
            if loaded_node.GetName() != friendly_name:
                loaded_node.SetName(friendly_name)

            # Select the loaded node in the provided selector
            selector_dict['selector'].setCurrentNode(loaded_node)

            slicer.util.showStatusMessage(f"{friendly_name} loaded successfully.", 3000)
        except Exception as e:
            slicer.util.errorDisplay(f"Error downloading/loading {friendly_name}:\n{str(e)}")

    # --- NEW: Callback for the hard tissue download button ---
    def download_hard_tissue(self):
        url = "https://github.com/user-attachments/files/20970624/Ridel_hard_tissue.mrk.json"
        self._download_and_load_markups(url, self.hard_tissue_selector, "Ridel_hard_tissue")

    # --- NEW: Callback for the soft tissue download button ---
    def download_soft_tissue(self):
        url = "https://github.com/user-attachments/files/20970625/Ridel_soft_tissue.mrk.json"
        self._download_and_load_markups(url, self.soft_tissue_selector, "Ridel_soft_tissue")

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
    def create_blueprint_planes(self):
        fhp_plane = self.get_node(self.fhp_plane_selector, "FHP Plane"); points_node = self.get_node(self.hard_tissue_selector, "Hard Tissue Fiducials")
        if not fhp_plane or not points_node: return
        if points_node.GetNumberOfControlPoints() < 3: slicer.util.errorDisplay("Need at least 3 landmarks."); return
        for name in ['MSP', 'FRP']:
            node = slicer.mrmlScene.GetFirstNodeByName(name)
            if node: slicer.mrmlScene.RemoveNode(node)
        p0,p1,p2 = (np.zeros(3) for _ in range(3)); points_node.GetNthControlPointPosition(0, p0); points_node.GetNthControlPointPosition(1, p1); points_node.GetNthControlPointPosition(2, p2)
        fhp_normal = np.zeros(3); fhp_plane.GetNormal(fhp_normal); msp_normal = np.cross(p1-p0, p2-p0); msp_normal /= np.linalg.norm(msp_normal)
        dotp = np.dot(msp_normal, fhp_normal)
        if not np.isclose(dotp, 0, atol=1e-5): msp_normal = msp_normal - dotp * fhp_normal; msp_normal /= np.linalg.norm(msp_normal)
        center = (p0+p1+p2)/3.0
        msp = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP'); msp.SetNormalWorld(msp_normal); msp.SetOriginWorld(center); msp.SetSize(150, 150)
        frp_normal = np.cross(fhp_normal, msp_normal); frp_normal /= np.linalg.norm(frp_normal)
        frp = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'FRP'); frp.SetNormalWorld(frp_normal); frp.SetOriginWorld(center); frp.SetSize(150,150)
        slicer.util.infoDisplay("Step 1: MSP and FRP created.")
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

    def launch_prediction_dialog(self):
        needed = ["Nasal height","Nasal bone length","Nasal bone projection","nTr_line","nCor_line","Ridel_hard_tissue"]
        if any(not slicer.mrmlScene.GetFirstNodeByName(n) for n in needed): slicer.util.errorDisplay("Run Steps 1-3 first."); return
        if not self.prediction_dialog:
            self.prediction_dialog = PredictionDialog(self.main_widget)
        self.prediction_dialog.refresh_measurements(); self.prediction_dialog.show(); self.prediction_dialog.raise_()

    def measure_prediction_errors(self):
        soft = self.get_node(self.soft_tissue_selector, "True Soft Tissue Fiducials")
        if not soft: return
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if n.GetName().startswith("Pred_")]
        if not pred_nodes: slicer.util.errorDisplay("Run Stage 1 first."); return
        mapping = {"pn'":"Pn_", "sn'":"Sn_", "al'l":"AlL_", "al'r":"AlR_"}
        for i in range(soft.GetNumberOfControlPoints()):
            orig_label = soft.GetNthControlPointLabel(i).lower().replace(" ","")
            for key, prefix in mapping.items():
                if key in orig_label:
                    orig_pt = np.zeros(3); soft.GetNthControlPointPosition(i, orig_pt)
                    for pred_node in pred_nodes:
                        for j in range(pred_node.GetNumberOfControlPoints()):
                            plabel = pred_node.GetNthControlPointLabel(j)
                            if plabel.startswith(prefix):
                                ppt = np.zeros(3); pred_node.GetNthControlPointPosition(j, ppt); name = f"error_{pred_node.GetName()}_{prefix}"
                                node = slicer.mrmlScene.GetFirstNodeByName(name)
                                if node: slicer.mrmlScene.RemoveNode(node)
                                ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name); ln.AddControlPoint(orig_pt); ln.AddControlPoint(ppt); ln.GetDisplayNode().SetColor([0,1,0]); ln.GetDisplayNode().SetLineThickness(0.2); ln.GetMeasurement('length').SetEnabled(True)
        slicer.util.infoDisplay("Step 5: Error lines created.")

    def onShowDetailedResults(self):
        soft_node = self.get_node(self.soft_tissue_selector, "True Soft Tissue Fiducials")
        pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if n.GetName().startswith("Pred_")]
        if not self.prediction_dialog or not pred_nodes:
            slicer.util.warningDisplay("Please run at least one prediction first.")
            return

        self.detailedWidget = qt.QDialog(self.main_widget); self.detailedWidget.setWindowTitle("Detailed Prediction Results"); self.detailedWidget.setMinimumSize(1800, 800)
        layout = qt.QVBoxLayout(self.detailedWidget); table = qt.QTableWidget()
        headers = ["Prediction Set", "Original Landmark", "Predicted Landmark Name", "nTr Calc: HT Measurements", "nTr Calc: Equation", "nTr Calc: Value (mm)", "nCor Calc: HT Measurements", "nCor Calc: Equation", "nCor Calc: Value (mm)", "Ancestry in Equation", "Final Error (mm)"]
        table.setColumnCount(len(headers)); table.setHorizontalHeaderLabels(headers)

        true_map = {"pn'":"Pn_", "sn'":"Sn_", "al'l":"AlL_", "al'r":"AlR_"}; true_dict = {}
        if soft_node:
            for i in range(soft_node.GetNumberOfControlPoints()):
                label = soft_node.GetNthControlPointLabel(i).lower().replace(" ","")
                for key, prefix in true_map.items():
                    if key in label: pos = np.zeros(3); soft_node.GetNthControlPointPosition(i, pos); true_dict[prefix] = pos; break

        all_equations = self.prediction_dialog.get_equations()

        table.setRowCount(sum(node.GetNumberOfControlPoints() for node in pred_nodes)); current_row = 0
        for pred_node in pred_nodes:
            for i in range(pred_node.GetNumberOfControlPoints()):
                pred_label = pred_node.GetNthControlPointLabel(i); pred_pos = np.zeros(3); pred_node.GetNthControlPointPosition(i, pred_pos)
                table.setItem(current_row, 0, qt.QTableWidgetItem(pred_node.GetName()))
                table.setItem(current_row, 2, qt.QTableWidgetItem(pred_label))

                original_lm, ancestry, ntr_breakdown, ncor_breakdown = self.get_calculation_breakdown(pred_label, all_equations)
                table.setItem(current_row, 1, qt.QTableWidgetItem(original_lm))
                table.setItem(current_row, 3, qt.QTableWidgetItem(ntr_breakdown['vars'])); table.setItem(current_row, 4, qt.QTableWidgetItem(ntr_breakdown['eq'])); table.setItem(current_row, 5, qt.QTableWidgetItem(ntr_breakdown['val']))
                table.setItem(current_row, 6, qt.QTableWidgetItem(ncor_breakdown['vars'])); table.setItem(current_row, 7, qt.QTableWidgetItem(ncor_breakdown['eq'])); table.setItem(current_row, 8, qt.QTableWidgetItem(ncor_breakdown['val']))
                table.setItem(current_row, 9, qt.QTableWidgetItem(ancestry))

                base_lm_prefix = pred_label.split('_')[0] + '_'
                if base_lm_prefix in true_dict: error = np.linalg.norm(pred_pos - true_dict[base_lm_prefix]); table.setItem(current_row, 10, qt.QTableWidgetItem(f"{error:.2f}"))
                else: table.setItem(current_row, 10, qt.QTableWidgetItem("N/A"))
                current_row += 1

        table.resizeColumnsToContents(); table.resizeRowsToContents(); layout.addWidget(table)
        copy_button = qt.QPushButton("Copy Table to Clipboard"); copy_button.clicked.connect(lambda: self.onCopyToClipboard(table)); layout.addWidget(copy_button)
        self.detailedWidget.show()

    # --- THE FIX IS HERE: REWRITTEN PARSING LOGIC ---
    def get_calculation_breakdown(self, label, all_equations):
        parts = label.split('_')
        lm_part, eq_parts = parts[0], parts[1:]

        lm_map = {"Pn": "pronasale", "Sn": "subnasale", "AlL": "alare (left)", "AlR": "alare (right)"}
        original_lm = lm_map.get(lm_part, "Unknown")

        # This is the corrected logic to reconstruct codes from the name parts
        eq_codes = []
        if len(eq_parts) > 0:
            if lm_part in ["Pn", "Sn"]: # Expects 2 codes, made of 4 parts
                if len(eq_parts) >= 4:
                    eq_codes.append(f"{eq_parts[0]}_{eq_parts[1]}")
                    eq_codes.append(f"{eq_parts[2]}_{eq_parts[3]}")
            elif lm_part in ["AlL", "AlR"]: # Expects 1 code, made of 2 parts
                if len(eq_parts) >= 2:
                    eq_codes.append(f"{eq_parts[0]}_{eq_parts[1]}")

        ancestry = "Unknown"
        pop_map = {"BSA": "Black South African", "WSA": "White South African"}
        if eq_codes and eq_codes[0].startswith("BSA"): ancestry = pop_map["BSA"]
        if eq_codes and eq_codes[0].startswith("WSA"): ancestry = pop_map["WSA"]

        def get_breakdown_for_eq(eq_code):
            breakdown = {'eq': "N/A", 'vars': "N/A", 'val': "N/A"}
            if self.prediction_dialog and eq_code and eq_code in all_equations:
                eq_text = all_equations[eq_code]['text']
                breakdown['eq'] = eq_text

                used_vars = []; var_map = {"NH": "Nasal height", "NBL": "Nasal bone length", "NBP": "Nasal bone projection"}
                for var_code, var_name in var_map.items():
                    if var_code in eq_text: used_vars.append(var_name)
                breakdown['vars'] = "; ".join(used_vars) if used_vars else "Constant"

                measurements = self.prediction_dialog.measurements
                formula = eq_text.replace('−','-').replace('×','*')
                is_calculable = True
                for var_text, var_name in var_map.items():
                    if var_text in formula:
                        value = measurements.get(var_name)
                        if value is None: is_calculable = False; break
                        formula = formula.replace(var_text, str(value))

                if is_calculable:
                    try:
                        value = eval(formula, {"__builtins__": {}})
                        breakdown['val'] = f"{value:.2f}"
                    except: breakdown['val'] = "Error"
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
        if not clipboard: slicer.util.warningDisplay("Clipboard not available."); return
        text = "\t".join([table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount)]) + "\n"
        for row in range(table_widget.rowCount):
            text += "\t".join([table_widget.item(row, col).text().replace('\n', ' | ') if table_widget.item(row, col) else "" for col in range(table_widget.columnCount)]) + "\n"
        clipboard.setText(text)
        slicer.util.showStatusMessage("Table contents copied to clipboard.", 3000)

    def close_all_dialogs(self):
        if self.detailedWidget and self.detailedWidget.isWidgetType(): self.detailedWidget.close()
        if self.prediction_dialog and self.prediction_dialog.isWidgetType():
            if self.prediction_dialog.manager and self.prediction_dialog.manager.isWidgetType(): self.prediction_dialog.manager.close()
            self.prediction_dialog.close()

class PredictionDialog(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Facial Landmark Prediction Tool"); self.setMinimumWidth(520); self.main_vlayout = qt.QVBoxLayout(self)
        name_h = qt.QHBoxLayout(); name_h.addWidget(qt.QLabel("Prediction Set Name:")); self.name_edit = qt.QLineEdit(f"Pred_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"); name_h.addWidget(self.name_edit); self.main_vlayout.addLayout(name_h)
        pop_h = qt.QHBoxLayout(); pop_h.addWidget(qt.QLabel("Population:")); self.pop_combo = qt.QComboBox(); self.pop_combo.addItems(["Black South African","White South African"]); pop_h.addWidget(self.pop_combo); self.main_vlayout.addLayout(pop_h)
        self.meas_group = qt.QGroupBox("Available Measurements"); self.meas_layout = qt.QFormLayout(self.meas_group); self.main_vlayout.addWidget(self.meas_group)
        self.pn_group = self.create_landmark_group('pn', "Pronasale (Pn)", "Pn to nTr:", "Pn to nCor:"); self.sn_group = self.create_landmark_group('sn', "Subnasale (Sn)", "Sn to nTr:", "Sn to nCor:"); self.al_group = self.create_landmark_group('al', "Alare (Al)", "Al to nTr:", None); self.al_group.layout().addWidget(qt.QLabel("<i>Note: Alare uses Nasal width for lateral placement.</i>"))
        self.create_btn = qt.QPushButton("Create New Prediction Set"); self.create_btn.setStyleSheet("background-color: #CCFFCC; font-weight: bold; padding: 8px;"); self.main_vlayout.addWidget(self.create_btn)
        self.manager_btn = qt.QPushButton("Show/Hide Prediction Manager"); self.main_vlayout.addWidget(self.manager_btn); self.manager = PredictionManager(self)
        self.pop_combo.currentIndexChanged.connect(self.update_equations); self.create_btn.clicked.connect(self.create_prediction_set); self.manager_btn.clicked.connect(self.toggle_manager); self.measurements = {}; self.update_equations()

    def create_landmark_group(self, key, title, label1, label2):
        g = qt.QGroupBox(title); g.setCheckable(True); g.setChecked(True); form = qt.QFormLayout(g); c1 = qt.QComboBox(); setattr(self, f"{key}_combo1", c1); form.addRow(label1, c1)
        if label2: c2 = qt.QComboBox(); setattr(self, f"{key}_combo2", c2); form.addRow(label2, c2)
        else: setattr(self, f"{key}_combo2", None)
        self.main_vlayout.addWidget(g); return g
    def refresh_measurements(self):
        while self.meas_layout.count():
            item = self.meas_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        self.measurements = {}; ok = True
        for n in ["Nasal height","Nasal width","Nasal bone length","Nasal bone projection"]:
            node = slicer.mrmlScene.GetFirstNodeByName(n)
            if node and isinstance(node, slicer.vtkMRMLMarkupsLineNode): val = node.GetMeasurement('length').GetValue(); self.measurements[n] = val; self.meas_layout.addRow(n, qt.QLabel(f"{val:.2f} mm"))
            else: self.measurements[n] = None; ok = False; l = qt.QLabel("NOT FOUND"); l.setStyleSheet("color: red"); self.meas_layout.addRow(n, l)
        self.create_btn.setEnabled(ok)

    def update_equations(self):
        is_bsa = (self.pop_combo.currentText == "Black South African"); eqs = self.get_equations()
        def fill(combo, keys):
            if not combo: return
            combo.clear()
            for k in keys:
                if k in eqs: combo.addItem(eqs[k]['text'], k)
        fill(self.pn_combo1, ["BSA_nh"] if is_bsa else ["WSA_nh","WSA_nbl","WSA_nh+nbl"]); fill(self.pn_combo2, ["BSA_nbl"] if is_bsa else ["WSA_nbp"])
        fill(self.sn_combo1, ["BSA_nh","BSA_nbl","BSA_nh+nbl"] if is_bsa else ["WSA_nh","WSA_nbl","WSA_nh+nbl"]); fill(self.sn_combo2, ["BSA_nbp"] if is_bsa else ["WSA_nbp"])
        fill(self.al_combo1, ["BSA_nh","BSA_nbl","BSA_nh+nbl"] if is_bsa else ["WSA_nh","WSA_nbl","WSA_nh+nbl"])

    def create_prediction_set(self):
        name = self.name_edit.text.strip()
        if not name or not name.startswith("Pred_"): slicer.util.errorDisplay("Name must start with 'Pred_'."); return
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node and qt.QMessageBox.question(self, "Overwrite?", f"'{name}' exists. Overwrite?") == qt.QMessageBox.No: return
        if node: slicer.mrmlScene.RemoveNode(node)
        pred = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", name); pred.GetDisplayNode().SetTextScale(3.0)
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
        slicer.util.infoDisplay(f"Created '{name}'."); self.manager.refresh_list(); self.name_edit.setText(f"Pred_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

    def place_landmark(self, pred_node, name, ntr_dist, ncor_dist, is_alare=False, is_left=None):
        hard = slicer.mrmlScene.GetFirstNodeByName("Ridel_hard_tissue"); nasion = np.zeros(3); hard.GetNthControlPointPosition(0, nasion)
        ntr_line = slicer.mrmlScene.GetFirstNodeByName("nTr_line"); ncor_line = slicer.mrmlScene.GetFirstNodeByName("nCor_line")
        p1,p2 = np.zeros(3), np.zeros(3); ntr_line.GetNthControlPointPosition(0,p1); ntr_line.GetNthControlPointPosition(1,p2); ntr_v = (p2 - p1) / np.linalg.norm(p2 - p1)
        q1,q2 = np.zeros(3), np.zeros(3); ncor_line.GetNthControlPointPosition(0,q1); ncor_line.GetNthControlPointPosition(1,q2); ncor_v = (q2 - q1) / np.linalg.norm(q2 - q1)
        final = nasion + ntr_v * (ncor_dist or 0) + ncor_v * (ntr_dist or 0)
        if is_alare:
            try:
                width = slicer.mrmlScene.GetFirstNodeByName("Nasal width").GetMeasurement('length').GetValue(); msp_n = np.zeros(3); slicer.mrmlScene.GetFirstNodeByName('MSP').GetNormal(msp_n); final += np.cross(ntr_v, msp_n) * (width/2.0) * (-1 if is_left else 1)
            except Exception: pass
        idx = pred_node.AddControlPoint(final); pred_node.SetNthControlPointLabel(idx, name)
    def calculate_from_combo(self, combo):
        if not combo: return None
        eq_text = combo.currentText
        nh = self.measurements.get("Nasal height"); nbl = self.measurements.get("Nasal bone length"); nbp = self.measurements.get("Nasal bone projection")
        if ('NH' in eq_text and nh is None) or ('NBL' in eq_text and nbl is None) or ('NBP' in eq_text and nbp is None): return None
        formula = eq_text.replace('−','-').replace('×','*').replace('NH', str(nh)).replace('NBL', str(nbl)).replace('NBP', str(nbp))
        try: return eval(formula, {"__builtins__": {}})
        except Exception: return None

    def get_equations(self):
        return {
            'BSA_nh': {'text': '−17.805+1.170*NH'},
            'BSA_nbl': {'text': '30.403-0.290*NBL'},
            'BSA_nbp': {'text': '3.063+1.060*NBP'},
            'BSA_nh+nbl': {'text': '2.369+0.782*NH+0.391*NBL'},
            'WSA_nh': {'text': '−7.969+0.963*NH'},
            'WSA_nbl': {'text': '22.859+1.004*NBL'},
            'WSA_nbp': {'text': '19.616+1.085*NBP'},
            'WSA_nh+nbl': {'text': '−1.341+0.633*NH+0.554*NBL'},
        }
    def toggle_manager(self):
        if self.manager.isVisible(): self.manager.hide()
        else: self.manager.show(); self.manager.refresh_list()

class PredictionManager(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Prediction Set Manager"); self.setWindowFlags(self.windowFlags() | qt.Qt.Tool)
        manager_layout = qt.QVBoxLayout(self); self.table = qt.QTableWidget(); self.table.setColumnCount(3); self.table.setHorizontalHeaderLabels(["Name","Visibility","Delete"]); manager_layout.addWidget(self.table); self.refresh_btn = qt.QPushButton("Refresh"); manager_layout.addWidget(self.refresh_btn); self.refresh_btn.clicked.connect(self.refresh_list)
        close_btn = qt.QPushButton("Close Manager"); manager_layout.addWidget(close_btn); close_btn.clicked.connect(lambda: self.close())
        self.refresh_list()
    def refresh_list(self):
        self.table.setRowCount(0)
        nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if n.GetName().startswith("Pred_")]
        self.table.setRowCount(len(nodes))
        for i, n in enumerate(nodes):
            self.table.setItem(i, 0, qt.QTableWidgetItem(n.GetName())); vis_btn = qt.QPushButton("Toggle"); vis_btn.setCheckable(True); vis_btn.setChecked(n.GetDisplayVisibility()); vis_btn.toggled.connect(lambda checked, name=n.GetName(): self.toggle_vis(name, checked)); self.table.setCellWidget(i, 1, vis_btn); del_btn = qt.QPushButton("Delete"); del_btn.clicked.connect(lambda name=n.GetName(): self.delete_node(name)); self.table.setCellWidget(i, 2, del_btn)
        self.table.resizeColumnsToContents()
    def toggle_vis(self, name, checked):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node: node.SetDisplayVisibility(checked)
    def delete_node(self, name):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node and qt.QMessageBox.question(self, "Delete", f"Delete {name}?") == qt.QMessageBox.Yes: slicer.mrmlScene.RemoveNode(node); self.refresh_list()

# --- Cleanup and Run ---
try:
    if 'ridel_gui_instance' in globals() and globals()['ridel_gui_instance'] and globals()['ridel_gui_instance'].main_widget.isWidgetType():
        globals()['ridel_gui_instance'].close_all_dialogs()
        globals()['ridel_gui_instance'].main_widget.close()
except:
    pass

ridel_gui_instance = RidelGUI()

```
