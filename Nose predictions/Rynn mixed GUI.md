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


import os
import vtk
import numpy as np
import qt
import slicer
import urllib.request
import tempfile
import re
from functools import partial

# =============================================================================
# REPORT WINDOW
# =============================================================================

class ReportWindow(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculation Report")
        self.setWindowFlag(qt.Qt.WindowStaysOnTopHint, True)
        self.setGeometry(100, 100, 600, 700)

        self.main_layout = qt.QVBoxLayout(self)

        self.report_text_edit = qt.QTextEdit()
        self.report_text_edit.setReadOnly(True)
        self.report_text_edit.setLineWrapMode(qt.QTextEdit.NoWrap)
        self.main_layout.addWidget(self.report_text_edit)

        # Button layout
        self.button_layout = qt.QHBoxLayout()
        self.clear_button = qt.QPushButton("Clear Report")
        self.copy_report_button = qt.QPushButton("Copy Full Report (TSV)")
        self.save_report_button = qt.QPushButton("Save Report as TXT")

        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.copy_report_button)
        self.button_layout.addWidget(self.save_report_button)

        self.main_layout.addLayout(self.button_layout)

        # Connections
        self.clear_button.clicked.connect(self.clear_report)
        self.copy_report_button.clicked.connect(self.copy_full_report)
        self.save_report_button.clicked.connect(self.save_report_to_file)

        # Internal state
        self.results = {}
        self.tables = {}          # for future use
        self.clear_report()       # initialises the report text

    def append_text(self, text_string):
        self.report_text_edit.append(text_string)
        self.report_text_edit.verticalScrollBar().setValue(self.report_text_edit.verticalScrollBar().maximum)

    def store_result(self, category, item_id, measurement, value, unit, std_id=None):
        if category not in self.results:
            self.results[category] = []
        entry = {
            "id": item_id,
            "measurement": measurement,
            "value": value,
            "unit": unit,
            "std_id": std_id if std_id else ""
        }
        self.results[category].append(entry)

    def clear_report(self):
        self.report_text_edit.clear()
        self.results.clear()
        self.append_text("--- Calculation Report ---\n")

    def get_all_standard_ids(self):
        """Return a sorted list of all unique non‑empty standard IDs from all results."""
        ids = set()
        for category, items in self.results.items():
            for item in items:
                std = item.get("std_id", "")
                if std:
                    ids.add(std)
        return sorted(ids)

    def get_run_number_from_id(self, item_id):
        """Extract run number from a node ID (e.g., 'PA_1_1' -> 1)."""
        import re
        match = re.search(r'_(\d+)_', item_id) or re.search(r'_(\d+)$', item_id)
        if match:
            return int(match.group(1))
        return None

    def _generate_report_text_excluding(self, exclude_categories=None):
        """
        Generate the report as TSV but skip certain categories.
        exclude_categories: list of category names to exclude (e.g., ["Basic Errors"])
        """
        if exclude_categories is None:
            exclude_categories = []
        if not self.results:
            return "--- Calculation Report ---\nNo results available."

        lines = ["Category\tID\tMeasurement\tValue\tUnit"]
        for category, items in self.results.items():
            if category in exclude_categories:
                continue
            for item in items:
                if isinstance(item['value'], (float, np.floating)):
                    value_str = f"{item['value']:.2f}"
                else:
                    value_str = str(item['value'])
                lines.append(f"{category}\t{item['id']}\t{item['measurement']}\t{value_str}\t{item['unit']}")
        return "\n".join(lines)

    def _generate_full_report_text(self):
        """Generate the complete report as a TSV string (header + all rows)."""
        if not self.results:
            return "--- Calculation Report ---\nNo results available."

        lines = ["Category\tID\tMeasurement\tValue\tUnit"]
        for category, items in self.results.items():
            for item in items:
                if isinstance(item['value'], (float, np.floating)):
                    value_str = f"{item['value']:.2f}"
                else:
                    value_str = str(item['value'])
                lines.append(f"{category}\t{item['id']}\t{item['measurement']}\t{value_str}\t{item['unit']}")
        return "\n".join(lines)

    def has_result(self, category, item_id):
        """Return True if an item with the given ID already exists in the category."""
        if category not in self.results:
            return False
        for item in self.results[category]:
            if item["id"] == item_id:
                return True
        return False

    def copy_full_report(self):
        """Copy the full report to the clipboard as TSV (Excel‑friendly)."""
        text = self._generate_full_report_text()
        if not text:
            slicer.util.showStatusMessage("Report is empty. Run calculations first.", 3000)
            return
        slicer.app.clipboard().setText(text)
        slicer.util.showStatusMessage("Full report copied to clipboard as TSV!", 3000)

    def save_report_to_file(self):
        """Prompt for a Case ID, then save the full report as a .txt file."""
        if not self.results:
            qt.QMessageBox.warning(self, "Empty Report", "No results to save. Please run calculations first.")
            return

        id_text, ok = qt.QInputDialog.getText(
            self,
            "Enter Case ID",
            "Please enter a Case ID or patient identifier for the report:"
        )
        if not ok:
            return

        clean_id = id_text.strip().replace(" ", "_") if id_text.strip() else "untitled"
        default_name = f"Report_{clean_id}.txt"

        file_path, _ = qt.QFileDialog.getSaveFileName(
            self,
            "Save Report",
            default_name,
            "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        text = self._generate_full_report_text()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            slicer.util.showStatusMessage(f"Report saved to {file_path}", 3000)
        except Exception as e:
            qt.QMessageBox.critical(self, "Save Error", f"Could not save file:\n{str(e)}")

# =============================================================================
# CAMERA UTILITIES
# =============================================================================

def save_camera_state():
    """Save the current 3D camera state."""
    layoutManager = slicer.app.layoutManager()
    if not layoutManager: return None
    threeDWidget = layoutManager.threeDWidget(0)
    if not threeDWidget: return None
    threeDView = threeDWidget.threeDView()
    if not threeDView: return None

    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    if not renderer: return None
    camera = renderer.GetActiveCamera()
    if not camera: return None

    return {
        'position': camera.GetPosition(),
        'focal_point': camera.GetFocalPoint(),
        'view_up': camera.GetViewUp(),
        'view_angle': camera.GetViewAngle(),
        'clipping_range': camera.GetClippingRange()
    }

def restore_camera_state(camera_state):
    """Restore a previously saved camera state."""
    if not camera_state: return

    layoutManager = slicer.app.layoutManager()
    if not layoutManager: return
    threeDWidget = layoutManager.threeDWidget(0)
    if not threeDWidget: return
    threeDView = threeDWidget.threeDView()
    if not threeDView: return

    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    if not renderer: return
    camera = renderer.GetActiveCamera()
    if not camera: return

    camera.SetPosition(camera_state['position'])
    camera.SetFocalPoint(camera_state['focal_point'])
    camera.SetViewUp(camera_state['view_up'])
    camera.SetViewAngle(camera_state['view_angle'])
    camera.SetClippingRange(camera_state['clipping_range'])

    threeDView.forceRender()

# =============================================================================
# MAIN LOGIC (with alias mapping and node attribute storage)
# =============================================================================

class RynnMethodLogic:
    def __init__(self):
        self.run_number = self.get_next_run_number()
        self.item_counters = {}
        # --- Tracking for stale node detection ---
        self.hard_node_guid = None
        self.plane_method = None
        self.scaffold_node_guid = None

        # --- Alias mapping for soft tissue landmarks ---
        self.alias_to_canonical = {
            "nasion": "nasion",
            "soft nasion": "nasion",
            "n'": "nasion",
            "soft tissue nasion": "nasion",
            "pronasale": "pronasale",
            "pn": "pronasale",
            "prn": "pronasale",
            "pn'": "pronasale",
            "subnasale": "subnasale",
            "sn": "subnasale",
            "sn'": "subnasale",
        }

        self.equation_to_formula = {
            # PA
            "pred Rynn PA": "0.83*Y-3.5",
            "pred Sarilita PA": "0.57*Y+2.33",
            "pred Bulut F PA": "0.681*Y+2.711",
            "pred Bulut M PA": "0.776*Y-0.481",
            # PV
            "pred Rynn PV": "0.9*X-2",
            "pred Sarilita PV": "0.88*X+0.68",
            "pred Bulut F PV": "0.779*X+5.501",
            "pred Bulut M PV": "0.954*X-3.53",
            # pFHP
            "pred Rynn pFHP": "0.93*Y-6",
            "pred Sarilita pFHP": "0.58*Y+4.55",
            "pred Bulut F pFHP": "0.775*Y+1.161",
            "pred Bulut M pFHP": "0.777*Y+0.518",
            # ND
            "pred Rynn F ND": "0.5*Y+1.5",
            "pred Rynn M ND": "0.4*Y+5",
            "pred Sarilita M ND": "0.22*Z+4.02",
            "pred Sarilita F ND": "0.29*Y+6.24",
            "pred Bulut F ND": "0.423*Y+5.169",
            "pred Bulut M ND": "0.386*Y+6.587",
            # NH
            "pred Rynn EA M NH": "0.78*Z+9.5",
            "pred Rynn EA F NH": "0.63*Z+17",
            "pred Sarilita M NH": "0.79*Z+3.74",
            "pred Sarilita F NH": "0.69*X+12.36",
            "pred Bulut F NH": "0.687*Z+15.047",
            "pred Bulut M NH": "0.784*Z+9.858",
            # NL
            "pred Rynn EA NL": "0.74*Z+3.5",
            "pred Sarilita F NL": "0.71*Z+6.624",
            "pred Sarilita M NL": "0.807*Z+0.764",
            "pred Bulut F NL": "0.71*Z+6.624",
            "pred Bulut M NL": "0.66*X+7.77",
        }

    def get_landmark_canonical(self, label):
        if label is None:
            return None
        label_lower = label.lower().strip()
        if label_lower in self.alias_to_canonical:
            return self.alias_to_canonical[label_lower]
        for key in self.alias_to_canonical.keys():
            if key in label_lower:
                return self.alias_to_canonical[key]
        return None

    def generate_standard_id(self, category, item_id, measurement, value, unit, equation=None):
        """
        Generate a Zenodo‑compatible standard ID (no run number).
        """
        prefix = "rynn"
        cat_map = {
            "Base Measurements": "base",
            "PA": "pa",
            "PV": "pv",
            "pFHP": "pfhp",
            "ND Radii": "nd",
            "NH Radii": "nh",
            "NL Radii": "nl",
            "Angles": "angle",
            "Projection Network": "proj",
            "Basic Errors": "err",
            "Advanced Errors": "adv",
        }
        cat_code = cat_map.get(category, category.lower().replace(" ", "_"))

        # Extract author and sex from equation
        author = ""
        sex = ""
        if equation:
            for a in ["rynn", "sarilita", "bulut"]:
                if a in equation.lower():
                    author = a
                    break
            if " m " in equation.lower() or " m_" in equation.lower() or "_m" in equation.lower():
                sex = "m"
            elif " f " in equation.lower() or " f_" in equation.lower() or "_f" in equation.lower():
                sex = "f"

        # Special cases
        if category == "Base Measurements":
            axis = measurement.split('-')[0].lower()  # "X-axis" -> "x"
            return f"{prefix}_{axis}_axis"

        if category == "Angles":
            if "True" in measurement:
                return f"{prefix}_true_angle"
            else:
                return f"{prefix}_predicted_angle"

        if category == "Projection Network":
            if item_id.startswith("n-pt"):
                landmark = item_id.replace("n-", "n_")
                return f"{prefix}_{cat_code}_{landmark}"
            elif " lat" in item_id:
                landmark = item_id.replace(" lat", "").replace("n-", "")
                return f"{prefix}_{cat_code}_{landmark}_lat"
            elif " ant" in item_id:
                landmark = item_id.replace(" ant", "").replace("n-", "")
                return f"{prefix}_{cat_code}_{landmark}_ant"
            elif " vert" in item_id:
                landmark = item_id.replace(" vert", "").replace("n-", "")
                return f"{prefix}_{cat_code}_{landmark}_vert"
            elif item_id in ["MAW", "MNW"]:
                return f"{prefix}_{item_id.lower()}"
            else:
                return f"{prefix}_{cat_code}_{item_id}"

        if category == "Basic Errors":
            landmark = item_id.replace("error_", "")
            return f"{prefix}_{cat_code}_{landmark}"

        if category == "Advanced Errors":
            if item_id == "Shortest_MNW-MAW":
                return f"{prefix}_shortest_mnw_maw"
            else:
                parts = item_id.replace("adv_error_", "").split("-")
                if len(parts) == 2:
                    return f"{prefix}_{cat_code}_{parts[0]}_{parts[1]}"
                else:
                    return f"{prefix}_{cat_code}_{item_id}"

        # For PA, PV, pFHP, ND, NH, NL
        if category in ["PA", "PV", "pFHP", "ND Radii", "NH Radii", "NL Radii"]:
            id_parts = [prefix, cat_code]
            if author:
                id_parts.append(author)
            if sex:
                id_parts.append(sex)
            if not sex and author:
                id_parts.append("all")  # sex‑neutral
            if not author:
                clean_meas = measurement.lower().replace(" ", "_").replace("(", "").replace(")", "")
                id_parts.append(clean_meas)
            return "_".join(id_parts)

        # Fallback
        return f"{prefix}_{cat_code}_{item_id}"

    def filter_equations_by_mode(self, equations, mode):
        if not mode:
            return equations
        author = mode.get("author", "")
        sex = mode.get("sex", "All")
        filtered = []
        for eq in equations:
            if author.lower() not in eq.lower():
                continue
            if sex != "All":
                has_m = " M " in eq or " M_" in eq or "_M" in eq or eq.startswith("M_")
                has_f = " F " in eq or " F_" in eq or "_F" in eq or eq.startswith("F_")
                if has_m and sex == "F":
                    continue
                if has_f and sex == "M":
                    continue
            filtered.append(eq)
        return filtered

    def get_next_run_number(self):
        max_run = 0
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            match = re.search(r'_(\d+)_\d+$', node.GetName())
            if match:
                max_run = max(max_run, int(match.group(1)))
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            match = re.search(r'_(\d+)$', node.GetName())
            if match:
                max_run = max(max_run, int(match.group(1)))
        return max_run

    def reset_item_counter(self, category):
        self.item_counters[category] = 0

    def get_next_item_number(self, category):
        if category not in self.item_counters:
            self.item_counters[category] = 0
        self.item_counters[category] += 1
        return self.item_counters[category]

    def make_name(self, base_name, use_run_number=False):
        if use_run_number:
            item_num = self.get_next_item_number(base_name)
            return f"{base_name}_{self.run_number}_{item_num}"
        else:
            return base_name

    def get_landmark_positions(self, landmark_node, required_landmarks):
        if not landmark_node: raise ValueError("Landmark node is not selected.")
        positions = {}
        for i in range(landmark_node.GetNumberOfControlPoints()):
            label = landmark_node.GetNthControlPointLabel(i).lower()
            positions[label] = np.array(landmark_node.GetNthControlPointPositionWorld(i))
        for name in required_landmarks:
            clean_name = name.lower().split(" ")[0]
            if clean_name not in positions and "(if visible)" not in name:
                raise ValueError(f"Required landmark '{name}' not found in the selected node.")
        return positions

    def create_line(self, name, p1, p2, color=(1,1,0), use_run_number=False):
        full_name = self.make_name(name, use_run_number)
        line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', full_name)
        line_node.AddControlPoint(p1); line_node.AddControlPoint(p2)
        displayNode = line_node.GetDisplayNode()
        if not displayNode: line_node.CreateDefaultDisplayNodes(); displayNode = line_node.GetDisplayNode()
        displayNode.SetColor(color); displayNode.SetSelectedColor(color); displayNode.SetLineThickness(0.5)
        return line_node

    def create_circle(self, name, center, radius, plane_normal, color=(0.2, 0.8, 0.2), equation_name=None):
        full_name = self.make_name(name, use_run_number=True)
        curve_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", full_name)
        curve_node.CreateDefaultDisplayNodes()
        display_node = curve_node.GetDisplayNode()
        plane_normal = np.array(plane_normal) / np.linalg.norm(np.array(plane_normal))
        arbitrary_vector = np.array([0, 0, 1]) if not np.allclose(plane_normal, [0, 0, 1]) else np.array([1, 0, 0])
        v1 = np.cross(plane_normal, arbitrary_vector)
        v1 /= np.linalg.norm(v1)
        v2 = np.cross(plane_normal, v1)
        for i in range(36):
            angle = 2 * np.pi * i / 36
            point = center + radius * (np.cos(angle) * v1 + np.sin(angle) * v2)
            curve_node.AddControlPoint(point)
        display_node.SetColor(color)
        display_node.SetSelectedColor(color)
        display_node.SetLineThickness(0.5)
        display_node.SetTextScale(0)
        curve_node.SetAttribute("Radius", str(radius))
        if equation_name:
            curve_node.SetAttribute("Equation", equation_name)
        return curve_node

    def create_reference_planes(self, landmark_node, method):
        def create_plane(name, origin, normal, color):
            plane_node = slicer.util.getFirstNodeByName(name) or slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', name)
            plane_node.SetOrigin(origin); plane_node.SetNormal(normal); plane_node.SetSize(300, 300)
            display_node = plane_node.GetDisplayNode() or plane_node.CreateDefaultDisplayNodes() and plane_node.GetDisplayNode()
            display_node.SetSelectedColor(color)
            return plane_node

        camera_state = save_camera_state()
        try:
            if "INB" in method:
                pos = self.get_landmark_positions(landmark_node, ["inion", "nasion", "bregma"])
                v1, v2 = pos['nasion'] - pos['inion'], pos['bregma'] - pos['inion']
                normal = np.cross(v1, v2); normal /= np.linalg.norm(normal)
                profile_plane = create_plane('INB', pos['inion'], normal, (1, 0, 0))
            elif "MSP" in method:
                pos = self.get_landmark_positions(landmark_node, ["nasion", "acanthion", "prosthion", "subspinale"])
                points = np.array(list(pos.values())); center = np.mean(points, axis=0)
                covariance = np.cov(points - center, rowvar=False); _, eigenvectors = np.linalg.eigh(covariance)
                normal = eigenvectors[:, np.argmin(_)]
                profile_plane = create_plane('MSP', center, normal, (1, 0.5, 0))
            else:
                raise ValueError("Invalid method")

            pos_np = self.get_landmark_positions(landmark_node, ["nasion", "prosthion"])
            profile_normal = np.array(profile_plane.GetNormal())
            vec_np = pos_np['nasion'] - pos_np['prosthion']
            npp_normal = np.cross(profile_normal, vec_np); npp_normal /= np.linalg.norm(npp_normal)
            create_plane('NPP', pos_np['prosthion'], npp_normal, (0, 1, 0))
            ptp_normal = np.cross(profile_normal, npp_normal); ptp_normal /= np.linalg.norm(ptp_normal)
            create_plane('PTP', pos_np['nasion'], ptp_normal, (0, 0, 1))

            self.hard_node_guid = landmark_node.GetID()
            self.plane_method = "INB" if "INB" in method else "MSP"
            if profile_plane:
                profile_plane.SetAttribute("HardNodeID", landmark_node.GetID())
                profile_plane.SetAttribute("PlaneMethod", self.plane_method)
        finally:
            restore_camera_state(camera_state)

    def create_axes(self, landmark_node, report_window):
        pos = self.get_landmark_positions(landmark_node, ["nasion", "acanthion", "rhinion", "subspinale"])
        p_nas, p_aca, p_rhi, p_sub = pos['nasion'], pos['acanthion'], pos['rhinion'], pos['subspinale']
        x_len, y_len, z_len = np.linalg.norm(p_nas - p_aca), np.linalg.norm(p_rhi - p_sub), np.linalg.norm(p_nas - p_sub)

        camera_state = save_camera_state()
        try:
            x_axis = self.create_line('X_axis', p_nas, p_aca, (1,0,0), use_run_number=False)
            self.create_line('Y_axis', p_rhi, p_sub, (0,1,0), use_run_number=False)
            self.create_line('Z_axis', p_nas, p_sub, (0,0,1), use_run_number=False)

            x_axis.SetAttribute(f"Run{self.run_number}_X_length", str(x_len))
            y_axis = slicer.util.getNode('Y_axis')
            z_axis = slicer.util.getNode('Z_axis')
            y_axis.SetAttribute(f"Run{self.run_number}_Y_length", str(y_len))
            z_axis.SetAttribute(f"Run{self.run_number}_Z_length", str(z_len))

            self.scaffold_node_guid = landmark_node.GetID()
            if x_axis:
                x_axis.SetAttribute("HardNodeID", landmark_node.GetID())
        finally:
            restore_camera_state(camera_state)

        report_window.append_text(f"\n=== Run {self.run_number}: Base Measurements ===")
        report_window.append_text(f"X-axis: {x_len:.2f} mm")
        report_window.append_text(f"Y-axis: {y_len:.2f} mm")
        report_window.append_text(f"Z-axis: {z_len:.2f} mm")

        std_id_x = self.generate_standard_id("Base Measurements", f"Run{self.run_number}_X", "X-axis", x_len, "mm")
        report_window.store_result("Base Measurements", f"Run{self.run_number}_X", "X-axis", x_len, "mm", std_id=std_id_x)
        std_id_y = self.generate_standard_id("Base Measurements", f"Run{self.run_number}_Y", "Y-axis", y_len, "mm")
        report_window.store_result("Base Measurements", f"Run{self.run_number}_Y", "Y-axis", y_len, "mm", std_id=std_id_y)
        std_id_z = self.generate_standard_id("Base Measurements", f"Run{self.run_number}_Z", "Z-axis", z_len, "mm")
        report_window.store_result("Base Measurements", f"Run{self.run_number}_Z", "Z-axis", z_len, "mm", std_id=std_id_z)

    def create_network_lines(self, landmark_node, active_profile_plane_name):
        profile_plane = slicer.util.getNode(active_profile_plane_name)
        if not profile_plane: raise ValueError(f"Profile plane '{active_profile_plane_name}' not found.")
        pos = self.get_landmark_positions(landmark_node, ["nasion", "subspinale"])
        profile_normal = np.array(profile_plane.GetNormal())
        horizontal_dir = np.cross(profile_normal, np.array([0,0,1])); horizontal_dir /= np.linalg.norm(horizontal_dir)
        vertical_dir = np.cross(horizontal_dir, profile_normal); vertical_dir /= np.linalg.norm(vertical_dir)

        camera_state = save_camera_state()
        try:
            line1 = self.create_line("Line_1", pos['nasion'] - horizontal_dir*150, pos['nasion'] + horizontal_dir*150, (1,0.5,0), use_run_number=False)
            self.create_line("Line_2", pos['nasion'] - vertical_dir*150, pos['nasion'] + vertical_dir*150, (1,0.5,0), use_run_number=False)
            self.create_line("Line_3", pos['subspinale'] - horizontal_dir*150, pos['subspinale'] + horizontal_dir*150, (1,0.5,0), use_run_number=False)
            self.scaffold_node_guid = landmark_node.GetID()
            if line1:
                line1.SetAttribute("HardNodeID", landmark_node.GetID())
        finally:
            restore_camera_state(camera_state)

    def calculate_pa(self, landmark_node, equations_to_run, report_window):
        self.reset_item_counter("PA")

        y_node = slicer.util.getNode("Y_axis")
        l1_node = slicer.util.getNode("Line_1")
        if not y_node or not l1_node: raise ValueError("Y-axis or Line_1 missing.")

        p1, p2 = np.zeros(3), np.zeros(3)
        y_node.GetNthControlPointPositionWorld(0, p1); y_node.GetNthControlPointPositionWorld(1, p2)
        y_len = np.linalg.norm(p2 - p1)

        start_pos = self.get_landmark_positions(landmark_node, ["nasion"])["nasion"]
        l1_node.GetNthControlPointPositionWorld(0, p1); l1_node.GetNthControlPointPositionWorld(1, p2)
        direction = (p1 - p2) / np.linalg.norm(p1 - p2)
        ptp_node = slicer.util.getNode('PTP')
        if ptp_node and np.dot(direction, start_pos - np.array(ptp_node.GetOrigin())) > 0: direction *= -1

        report_window.append_text(f"\n=== Run {self.run_number}: PA ===")
        camera_state = save_camera_state()
        try:
            for eq in equations_to_run:
                eq_map = {
                    "pred Rynn PA": (0.83, y_len, -3.5, "0.83*Y-3.5"),
                    "pred Sarilita PA": (0.57, y_len, 2.33, "0.57*Y+2.33"),
                    "pred Bulut F PA": (0.681, y_len, 2.711, "0.681*Y+2.711"),
                    "pred Bulut M PA": (0.776, y_len, -0.481, "0.776*Y-0.481")
                }
                coeff, var_len, const, eq_str = eq_map[eq]
                length = coeff * var_len + const
                line_node = self.create_line("PA", start_pos, start_pos + direction * length, (0.85,0.7,0), use_run_number=True)
                line_node.SetAttribute("Equation", eq)
                report_window.append_text(f"{line_node.GetName()}: {eq} = {eq_str} = {length:.2f} mm")
                std_id = self.generate_standard_id("PA", line_node.GetName(), eq, length, "mm", equation=eq)
                formula = self.equation_to_formula.get(eq, eq)  # fallback to name if missing
                report_window.store_result("PA", line_node.GetName(), formula, length, "mm", std_id=std_id)
        finally:
            restore_camera_state(camera_state)

    def calculate_pv(self, pa_line_name, pv_equations_to_run, report_window):
        self.reset_item_counter("PV")

        x_node = slicer.util.getNode("X_axis")
        l2_node = slicer.util.getNode("Line_2")
        pa_node = slicer.util.getNode(pa_line_name)
        if not all([x_node, l2_node, pa_node]): raise ValueError("Required nodes missing.")

        p1, p2 = np.zeros(3), np.zeros(3)
        x_node.GetNthControlPointPositionWorld(0, p1); x_node.GetNthControlPointPositionWorld(1, p2)
        x_len = np.linalg.norm(p2 - p1)

        l2_node.GetNthControlPointPositionWorld(0, p1); l2_node.GetNthControlPointPositionWorld(1, p2)
        direction = (p2 - p1) / np.linalg.norm(p2 - p1)
        if direction[2] > 0: direction *= -1

        pa_end_pos = np.array(pa_node.GetNthControlPointPositionWorld(1))
        pred_node_name = f"soft_tissue_pred_{self.run_number}"
        pred_node = slicer.util.getFirstNodeByName(pred_node_name) or slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", pred_node_name)

        report_window.append_text(f"\n=== Run {self.run_number}: PV (from {pa_line_name}) ===")
        camera_state = save_camera_state()
        try:
            for eq_name in pv_equations_to_run:
                eq_map = {
                    "pred Rynn PV": (0.9, x_len, -2, "0.9*X-2"),
                    "pred Sarilita PV": (0.88, x_len, 0.68, "0.88*X+0.68"),
                    "pred Bulut F PV": (0.779, x_len, 5.501, "0.779*X+5.501"),
                    "pred Bulut M PV": (0.954, x_len, -3.53, "0.954*X-3.53")
                }
                coeff, var_len, const, eq_str = eq_map[eq_name]
                length = coeff * var_len + const
                final_pos = pa_end_pos + direction * length

                line_node = self.create_line("PV", pa_end_pos, final_pos, color=(0.2, 0.8, 0.2), use_run_number=True)
                point_label = f"pronasale_{line_node.GetName()}"
                pred_node.AddControlPoint(final_pos, point_label)

                report_window.append_text(f"{line_node.GetName()}: {eq_name} = {eq_str} = {length:.2f} mm")
                std_id = self.generate_standard_id("PV", line_node.GetName(), eq_name, length, "mm", equation=eq_name)
                formula = self.equation_to_formula.get(eq_name, eq_name)
                report_window.store_result("PV", line_node.GetName(), formula, length, "mm", std_id=std_id)
        finally:
            restore_camera_state(camera_state)

    def calculate_pfhp(self, landmark_node, equations_to_run, report_window):
        self.reset_item_counter("pFHP")

        y_node = slicer.util.getNode("Y_axis")
        l3_node = slicer.util.getNode("Line_3")
        if not y_node or not l3_node: raise ValueError("Y-axis or Line_3 missing.")

        p1,p2 = np.zeros(3),np.zeros(3)
        y_node.GetNthControlPointPositionWorld(0,p1); y_node.GetNthControlPointPositionWorld(1,p2)
        y_len = np.linalg.norm(p2-p1)

        l3_node.GetNthControlPointPositionWorld(0,p1); l3_node.GetNthControlPointPositionWorld(1,p2)
        direction = (p2 - p1) / np.linalg.norm(p2-p1)
        subsp = self.get_landmark_positions(landmark_node, ["subspinale"])["subspinale"]
        if np.dot(direction, subsp - p1) > 0: direction *= -1

        report_window.append_text(f"\n=== Run {self.run_number}: pFHP ===")
        camera_state = save_camera_state()
        try:
            for eq in equations_to_run:
                eq_map = {
                    "pred Rynn pFHP": (0.93, y_len, -6, "0.93*Y-6"),
                    "pred Sarilita pFHP": (0.58, y_len, 4.55, "0.58*Y+4.55"),
                    "pred Bulut F pFHP": (0.775, y_len, 1.161, "0.775*Y+1.161"),
                    "pred Bulut M pFHP": (0.777, y_len, 0.518, "0.777*Y+0.518")
                }
                coeff, var_len, const, eq_str = eq_map[eq]
                length = coeff * var_len + const
                line_node = self.create_line("pFHP", subsp, subsp + direction * length, (0.9,0.4,0.1), use_run_number=True)
                line_node.SetAttribute("Equation", eq)
                report_window.append_text(f"{line_node.GetName()}: {eq} = {eq_str} = {length:.2f} mm")
                std_id = self.generate_standard_id("pFHP", line_node.GetName(), eq, length, "mm", equation=eq)
                formula = self.equation_to_formula.get(eq, eq)
                report_window.store_result("pFHP", line_node.GetName(), formula, length, "mm", std_id=std_id)
        finally:
            restore_camera_state(camera_state)

    def calculate_sn(self, center_point_index, nd_equation, pfhp_line_name, active_profile_plane_name, report_window):
        self.reset_item_counter("ND_circle")

        pred_node = slicer.util.getFirstNodeByName(f"soft_tissue_pred_{self.run_number}")
        y_node = slicer.util.getNode("Y_axis")
        z_node = slicer.util.getNode("Z_axis")
        plane = slicer.util.getNode(active_profile_plane_name)
        line_node = slicer.util.getNode(pfhp_line_name)
        if not all([pred_node, y_node, z_node, plane, line_node]): raise ValueError("Required nodes missing.")

        center_label, center_pos = pred_node.GetNthControlPointLabel(center_point_index), np.array(pred_node.GetNthControlPointPositionWorld(center_point_index))
        p1,p2 = np.zeros(3),np.zeros(3)
        y_node.GetNthControlPointPositionWorld(0,p1); y_node.GetNthControlPointPositionWorld(1,p2); y_len=np.linalg.norm(p2-p1)
        z_node.GetNthControlPointPositionWorld(0,p1); z_node.GetNthControlPointPositionWorld(1,p2); z_len=np.linalg.norm(p2-p1)

        eq_map = {
            "pred Rynn F ND": (0.5, y_len, 1.5, "0.5*Y+1.5"),
            "pred Rynn M ND": (0.4, y_len, 5, "0.4*Y+5"),
            "pred Sarilita M ND": (0.22, z_len, 4.02, "0.22*Z+4.02"),
            "pred Sarilita F ND": (0.29, y_len, 6.24, "0.29*Y+6.24"),
            "pred Bulut F ND": (0.423, y_len, 5.169, "0.423*Y+5.169"),
            "pred Bulut M ND": (0.386, y_len, 6.587, "0.386*Y+6.587")
        }
        coeff, var_len, const, eq_str = eq_map[nd_equation]
        radius = coeff * var_len + const

        report_window.append_text(f"\n=== Run {self.run_number}: sn (ND circle) ===")
        report_window.append_text(f"Center: {center_label}, Line: {pfhp_line_name}")
        report_window.append_text(f"{nd_equation} = {eq_str} = {radius:.2f} mm")
        std_id = self.generate_standard_id("ND Radii", f"Run{self.run_number}_{nd_equation}", "Radius", radius, "mm", equation=nd_equation)
        formula = self.equation_to_formula.get(nd_equation, nd_equation)
        report_window.store_result("ND Radii", f"Run{self.run_number}_{nd_equation}", formula, radius, "mm", std_id=std_id)

        plane_n = np.array(plane.GetNormal())
        camera_state = save_camera_state()
        try:
            self.create_circle("ND_circle", center_pos, radius, plane_n, equation_name=nd_equation)
        finally:
            restore_camera_state(camera_state)

        u=np.cross(plane_n,[0,0,1] if not np.allclose(plane_n,[0,0,1]) else [1,0,0]); u/=np.linalg.norm(u); v=np.cross(u,plane_n)
        lp0,lp1=np.array(line_node.GetNthControlPointPositionWorld(0)),np.array(line_node.GetNthControlPointPositionWorld(1))
        p0_plane=np.array([np.dot(lp0-center_pos,u),np.dot(lp0-center_pos,v)])
        p1_plane=np.array([np.dot(lp1-center_pos,u),np.dot(lp1-center_pos,v)])
        dp = p1_plane - p0_plane; a = np.dot(dp,dp); b = 2*np.dot(p0_plane,dp); c = np.dot(p0_plane,p0_plane) - radius**2
        discriminant = b**2 - 4*a*c
        if discriminant < 0: raise ValueError("No intersection found.")
        t_values = [(-b + np.sqrt(discriminant))/(2*a), (-b - np.sqrt(discriminant))/(2*a)]
        intersections = [lp0 + t*(lp1-lp0) for t in t_values if 0 <= t <= 1]
        if not intersections: raise ValueError("Intersection outside line segment.")

        final_label = f"subnasale_{self.run_number}"
        pred_node.AddControlPoint(intersections[0], final_label)
        report_window.append_text(f"Created: {final_label}")

    def calculate_nasion(self, nh_center_point_index, nh_equation, nl_center_point_index, nl_equation, active_profile_plane_name, report_window):
        self.reset_item_counter("NH_circle")
        self.reset_item_counter("NL_circle")

        pred_node = slicer.util.getFirstNodeByName(f"soft_tissue_pred_{self.run_number}")
        x_node = slicer.util.getNode("X_axis")
        z_node = slicer.util.getNode("Z_axis")
        plane = slicer.util.getNode(active_profile_plane_name)
        if not all([pred_node, x_node, z_node, plane]): raise ValueError("Required nodes missing.")

        nh_label, nh_center_pos = pred_node.GetNthControlPointLabel(nh_center_point_index), np.array(pred_node.GetNthControlPointPositionWorld(nh_center_point_index))
        nl_label, nl_center_pos = pred_node.GetNthControlPointLabel(nl_center_point_index), np.array(pred_node.GetNthControlPointPositionWorld(nl_center_point_index))
        p1,p2=np.zeros(3),np.zeros(3)
        x_node.GetNthControlPointPositionWorld(0,p1); x_node.GetNthControlPointPositionWorld(1,p2); x_len=np.linalg.norm(p2-p1)
        z_node.GetNthControlPointPositionWorld(0,p1); z_node.GetNthControlPointPositionWorld(1,p2); z_len=np.linalg.norm(p2-p1)

        nh_map = {
            "pred Rynn EA M NH": (0.78, z_len, 9.5, "0.78*Z+9.5"),
            "pred Rynn EA F NH": (0.63, z_len, 17, "0.63*Z+17"),
            "pred Sarilita M NH": (0.79, z_len, 3.74, "0.79*Z+3.74"),
            "pred Sarilita F NH": (0.69, x_len, 12.36, "0.69*X+12.36"),
            "pred Bulut F NH": (0.687, z_len, 15.047, "0.687*Z+15.047"),
            "pred Bulut M NH": (0.784, z_len, 9.858, "0.784*Z+9.858")
        }
        nl_map = {
            "pred Rynn EA NL": (0.74, z_len, 3.5, "0.74*Z+3.5"),
            "pred Sarilita F NL": (0.71, z_len, 6.624, "0.71*Z+6.624"),
            "pred Sarilita M NL": (0.807, z_len, 0.764, "0.807*Z+0.764"),
            "pred Bulut F NL": (0.71, z_len, 6.624, "0.71*Z+6.624"),
            "pred Bulut M NL": (0.66, x_len, 7.77, "0.66*X+7.77")
        }

        nh_coeff, nh_var, nh_const, nh_eq_str = nh_map[nh_equation]
        nl_coeff, nl_var, nl_const, nl_eq_str = nl_map[nl_equation]
        nh_radius, nl_radius = nh_coeff * nh_var + nh_const, nl_coeff * nl_var + nl_const

        report_window.append_text(f"\n=== Run {self.run_number}: Nasion ===")
        report_window.append_text(f"NH: {nh_equation} = {nh_eq_str} = {nh_radius:.2f} mm")
        report_window.append_text(f"NL: {nl_equation} = {nl_eq_str} = {nl_radius:.2f} mm")

        # NH
        std_id_nh = self.generate_standard_id("NH Radii", f"Run{self.run_number}_{nh_equation}", "Radius", nh_radius, "mm", equation=nh_equation)
        formula_nh = self.equation_to_formula.get(nh_equation, nh_equation)
        report_window.store_result("NH Radii", f"Run{self.run_number}_{nh_equation}", formula_nh, nh_radius, "mm", std_id=std_id_nh)

        # NL
        std_id_nl = self.generate_standard_id("NL Radii", f"Run{self.run_number}_{nl_equation}", "Radius", nl_radius, "mm", equation=nl_equation)
        formula_nl = self.equation_to_formula.get(nl_equation, nl_equation)
        report_window.store_result("NL Radii", f"Run{self.run_number}_{nl_equation}", formula_nl, nl_radius, "mm", std_id=std_id_nl)

        plane_n = np.array(plane.GetNormal())
        camera_state = save_camera_state()
        try:
            self.create_circle("NH_circle", nh_center_pos, nh_radius, plane_n, color=(1,0,0), equation_name=nh_equation)
            self.create_circle("NL_circle", nl_center_pos, nl_radius, plane_n, color=(0,0,1), equation_name=nl_equation)
        finally:
            restore_camera_state(camera_state)

        c1,r1,c2,r2=nh_center_pos,nh_radius,nl_center_pos,nl_radius
        d_vec=c1-c2; d=np.linalg.norm(d_vec)
        if d > r1+r2 or d < abs(r1-r2) or d==0: raise ValueError("Circles do not intersect.")
        a=(r1**2-r2**2+d**2)/(2*d); h=np.sqrt(max(0,r1**2-a**2)); p2_intersect=c1+a*(c2-c1)/d
        v=np.cross(d_vec,plane_n); v/=np.linalg.norm(v); intersections=[p2_intersect+h*v, p2_intersect-h*v]

        l1_node = slicer.util.getNode("Line_1")
        l1p0,l1p1=np.array(l1_node.GetNthControlPointPositionWorld(0)), np.array(l1_node.GetNthControlPointPositionWorld(1))
        def dist_to_line(pt,p0,p1):
            line_vec=p1-p0; point_vec=pt-p0; line_len=np.linalg.norm(line_vec)
            proj=np.dot(point_vec,line_vec/line_len)
            if proj<0: return np.linalg.norm(pt-p0)
            if proj>line_len: return np.linalg.norm(pt-p1)
            return np.linalg.norm(pt - (p0 + proj*(line_vec/line_len)))
        closest_pt=min(intersections, key=lambda pt: dist_to_line(pt,l1p0,l1p1))

        label=f"nasion_{self.run_number}"
        pred_node.AddControlPoint(closest_pt, label)
        report_window.append_text(f"Created: {label}")

# =============================================================================
# PART 2: GUI
# =============================================================================

class StepWidget(qt.QWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.data = data
        self.main_gui = main_gui
        self.mainLayout = qt.QVBoxLayout(self)
        title_label = qt.QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        self.mainLayout.addWidget(title_label, 0, qt.Qt.AlignHCenter)
    def onEnterStep(self): pass
    def get_landmark_node(self):
        return self.main_gui.get_selected_landmark_node()

# =============================================================================
# STEP 1: LANDMARK SETUP
# =============================================================================

class Step1_LandmarkSetup(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)

        self.downloadHardButton = qt.QPushButton("1. Download Hard Tissue Landmarks (Rynn_hard_tissue)")
        self.downloadHardButton.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 8px;")

        self.downloadSoftButton = qt.QPushButton("2. Download Soft Tissue Landmarks (Rynn_soft_tissue)")
        self.downloadSoftButton.setStyleSheet("background-color: #28A745; color: white; font-weight: bold; padding: 8px;")

        noteLabel = qt.QLabel("<b>3. Place the required hard tissue landmarks on your model, or download them above.</b>")
        noteLabel.setWordWrap(True); noteLabel.setTextFormat(qt.Qt.RichText)

        self.landmarkTable = qt.QTableWidget(7, 1)
        self.landmarkTable.setHorizontalHeaderLabels(["Required Hard Tissue Landmarks"])
        landmarks = ["nasion","inion (if visible)","bregma (if visible)","prosthion","subspinale","rhinion","acanthion"]
        for i, landmark in enumerate(landmarks):
            self.landmarkTable.setItem(i, 0, qt.QTableWidgetItem(landmark))
        self.landmarkTable.horizontalHeader().setStretchLastSection(True)
        self.landmarkTable.verticalHeader().setVisible(False)
        self.landmarkTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.landmarkTable.setFixedHeight(self.landmarkTable.verticalHeader().defaultSectionSize * (self.landmarkTable.rowCount + 1))

        selectorLayout = qt.QFormLayout()
        self.landmarksSelector = slicer.qMRMLNodeComboBox()
        self.landmarksSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.landmarksSelector.setMRMLScene(slicer.mrmlScene)
        self.landmarksSelector.addEnabled = True
        self.landmarksSelector.removeEnabled = False
        self.landmarksSelector.noneEnabled = True
        selectorLayout.addRow("<b>4. Select Landmark Node:</b>", self.landmarksSelector)

        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)

        for w in [self.downloadHardButton, self.downloadSoftButton, noteLabel, self.landmarkTable, self.statusLabel]:
            self.mainLayout.addWidget(w)
        self.mainLayout.addLayout(selectorLayout)
        self.mainLayout.addStretch(1)

        self.downloadHardButton.clicked.connect(self.onDownloadHardLandmarks)
        self.downloadSoftButton.clicked.connect(self.onDownloadSoftLandmarks)
        self.attempt_count = 0

        self.landmarksSelector.currentNodeChanged.connect(self._storeHardNodeID)

    def _storeHardNodeID(self):
        node = self.landmarksSelector.currentNode()
        if node:
            self.data["hard_node_id"] = node.GetID()
        else:
            self.data.pop("hard_node_id", None)

    def _autoSelectHardNode(self):
        preferred_node = None
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            if node.GetName().startswith("Rynn_hard_tissue"):
                preferred_node = node
                break
        if preferred_node:
            self.landmarksSelector.setCurrentNode(preferred_node)
            self.data["hard_node_id"] = preferred_node.GetID()
            return

        stored_id = self.data.get("hard_node_id")
        if stored_id:
            node = slicer.mrmlScene.GetNodeByID(stored_id)
            if node and node.IsA("vtkMRMLMarkupsFiducialNode"):
                self.landmarksSelector.setCurrentNode(node)
                return

        required_labels = ["nasion", "prosthion", "rhinion", "subspinale", "acanthion"]
        best_node = None
        best_score = 0
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            labels = [node.GetNthControlPointLabel(i).lower() for i in range(node.GetNumberOfControlPoints())]
            score = sum(1 for req in required_labels if any(req in label for label in labels))
            if score >= 3 and score > best_score:
                best_score = score
                best_node = node
        if best_node:
            self.landmarksSelector.setCurrentNode(best_node)

    def onEnterStep(self):
        self._autoSelectHardNode()
        if self.landmarksSelector.currentNode():
            self.statusLabel.setText("✓ Status: Landmark node is already selected.")
            return
        self.attempt_count = 0
        self.tryAutoSelect()

    def tryAutoSelect(self):
        slicer.app.processEvents()
        qt.QApplication.instance().processEvents()

        required_landmarks = ["nasion", "prosthion", "rhinion", "subspinale", "acanthion"]
        for node in slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode'):
            landmark_labels = [node.GetNthControlPointLabel(i).lower() for i in range(node.GetNumberOfControlPoints())]
            matches = sum(1 for req in required_landmarks if any(req in label for label in landmark_labels))
            if matches >= 3:
                self.landmarksSelector.setCurrentNode(node)
                self.statusLabel.setText(f"✓ Status: Auto-selected '{node.GetName()}' (found {matches} matching landmarks)")
                return
        self.attempt_count += 1
        if self.attempt_count < 5:
            qt.QTimer.singleShot(200 * self.attempt_count, self.tryAutoSelect)
        else:
            self.statusLabel.setText("Status: Please download or manually select the landmark node.")

    def onDownloadHardLandmarks(self):
        self.statusLabel.setText("Status: Downloading hard tissue...")
        slicer.app.processEvents()
        url = "https://github.com/user-attachments/files/31413384/Rynn_hard_tissue.mrk.json"
        nodeName = "Rynn_hard_tissue"
        try:
            with urllib.request.urlopen(url) as response, tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json', mode='wb') as tempFile:
                tempFile.write(response.read())
                tempFilePath = tempFile.name
            loadedNode = slicer.util.loadMarkups(tempFilePath)
            os.remove(tempFilePath)
            if loadedNode:
                loadedNode.SetName(nodeName)
                slicer.app.processEvents()
                qt.QTimer.singleShot(100, lambda: self.landmarksSelector.setCurrentNode(loadedNode))
                self.statusLabel.setText(f"✓ Status: '{nodeName}' downloaded and selected.")
            else:
                raise IOError("Failed to load landmarks.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def onDownloadSoftLandmarks(self):
        self.statusLabel.setText("Status: Downloading soft tissue...")
        slicer.app.processEvents()
        base_name = self.data["soft_tissue_node_name"]
        nodeName = base_name
        counter = 2
        while slicer.util.getFirstNodeByName(nodeName):
            nodeName = f"{base_name}_{counter}"
            counter += 1
        try:
            with urllib.request.urlopen("https://github.com/user-attachments/files/22989771/Rynn_soft_tissue.mrk.json") as response, \
                 tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json', mode='wb') as tempFile:
                tempFile.write(response.read())
                tempFilePath = tempFile.name
            loadedNode = slicer.util.loadMarkups(tempFilePath)
            os.remove(tempFilePath)
            if loadedNode:
                loadedNode.SetName(nodeName)
                self.statusLabel.setText(f"✓ Status: '{nodeName}' downloaded.")
            else:
                raise IOError("Failed to load landmarks.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

# =============================================================================
# STEP 2: PLANE SETUP
# =============================================================================

class Step2_PlaneSetup(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)

        desc = qt.QLabel("Choose a method to define the primary profile plane (INB or MSP).")
        desc.setWordWrap(True)

        noteLabel = qt.QLabel("<b>📝 Note:</b> The reference planes will be used for all runs. If you want to change from INB to MSP (or vice versa), please save your scene and reload 3D Slicer.")
        noteLabel.setWordWrap(True)
        noteLabel.setStyleSheet("background-color: #FFF3CD; padding: 10px; border-radius: 5px;")

        planeChoiceLayout = qt.QFormLayout()
        self.planeChoiceComboBox = qt.QComboBox()
        self.planeChoiceComboBox.addItems(["Select a method...", "INB (Inion-Nasion-Bregma)", "MSP (Midsagittal Best-Fit)"])
        planeChoiceLayout.addRow("Profile Plane Method:", self.planeChoiceComboBox)

        self.createPlanesButton = qt.QPushButton("Create All Reference Planes")
        self.createPlanesButton.clicked.connect(self.onCreatePlanes)

        self.updatePlanesButton = qt.QPushButton("⚠️ Update Planes (Node Changed)")
        self.updatePlanesButton.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold;")
        self.updatePlanesButton.clicked.connect(self.onUpdatePlanes)
        self.updatePlanesButton.setVisible(False)

        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)

        self.mainLayout.addWidget(desc)
        self.mainLayout.addWidget(noteLabel)
        self.mainLayout.addLayout(planeChoiceLayout)
        self.mainLayout.addWidget(self.createPlanesButton)
        self.mainLayout.addWidget(self.updatePlanesButton)
        self.mainLayout.addWidget(self.statusLabel)

        self.mainLayout.addStretch(1)

    def onEnterStep(self):
        landmark_node = self.get_landmark_node()
        if not landmark_node:
            return

        plane_exists = bool(slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP"))

        profile_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
        if profile_plane:
            stored_method = profile_plane.GetAttribute("PlaneMethod")
            if stored_method:
                if stored_method == "INB":
                    self.planeChoiceComboBox.setCurrentIndex(1)
                elif stored_method == "MSP":
                    self.planeChoiceComboBox.setCurrentIndex(2)

        if plane_exists and self.logic.hard_node_guid and self.logic.hard_node_guid != landmark_node.GetID():
            self.updatePlanesButton.setVisible(True)
            self.statusLabel.setText("⚠️ Hard tissue node changed. Planes are stale. Click 'Update Planes' to refresh them using the current node.")
            self.createPlanesButton.setEnabled(False)
            return

        if plane_exists and self.logic.hard_node_guid == landmark_node.GetID():
            self.updatePlanesButton.setVisible(False)
            self.createPlanesButton.setEnabled(True)
            self.statusLabel.setText("✓ Planes complete. Auto-advancing...")
            if not self.main_gui.manual_navigation:
                qt.QTimer.singleShot(200, self._auto_advance)
            return

        self.updatePlanesButton.setVisible(False)
        self.createPlanesButton.setEnabled(True)
        self.statusLabel.setText("Status: Please select a method and click 'Create All Reference Planes'.")

    def _auto_advance(self):
        if self.main_gui.currentStep < len(self.main_gui.step_widgets) - 1:
            self.main_gui.currentStep += 1
            self.main_gui.update_ui()

    def onUpdatePlanes(self):
        landmark_node = self.get_landmark_node()
        if not landmark_node:
            return
        if not self.logic.plane_method:
            self.statusLabel.setText("❌ Error: No plane method stored. Please use 'Create All Reference Planes'.")
            return
        self.statusLabel.setText("Status: Updating planes...")
        slicer.app.processEvents()
        try:
            self.logic.create_reference_planes(landmark_node, self.logic.plane_method)
            self.updatePlanesButton.setVisible(False)
            self.createPlanesButton.setEnabled(True)
            self.statusLabel.setText(f"✓ Status: Planes updated using {self.logic.plane_method} method.")
            self.onEnterStep()
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def onCreatePlanes(self):
        self.statusLabel.setText("Status: Processing...")
        slicer.app.processEvents()
        try:
            landmark_node = self.get_landmark_node()
            choice = self.planeChoiceComboBox.currentText
            if "Select a method" in choice:
                raise ValueError("Please select a plane creation method.")
            self.logic.create_reference_planes(landmark_node, choice)
            active_plane_name = "INB" if "INB" in choice else "MSP"
            self.statusLabel.setText(f"✓ Status: Created {active_plane_name}, NPP, and PTP planes.")
            self.onEnterStep()
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

# =============================================================================
# STEP 3: SCAFFOLDING
# =============================================================================

class Step3_Scaffolding(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)

        axesGroup = qt.QGroupBox("1. Coordinate Axes")
        axesLayout = qt.QVBoxLayout(axesGroup)
        self.createAxesButton = qt.QPushButton("Create X, Y, Z Axes")
        axesLayout.addWidget(self.createAxesButton)

        networkGroup = qt.QGroupBox("2. Reference Network")
        networkLayout = qt.QVBoxLayout(networkGroup)
        self.createNetworkButton = qt.QPushButton("Create Network Lines 1, 2, 3")
        networkLayout.addWidget(self.createNetworkButton)

        self.updateScaffoldingButton = qt.QPushButton("⚠️ Update Scaffolding (Node Changed)")
        self.updateScaffoldingButton.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold;")
        self.updateScaffoldingButton.clicked.connect(self.onUpdateScaffolding)
        self.updateScaffoldingButton.setVisible(False)

        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)

        self.mainLayout.addWidget(axesGroup)
        self.mainLayout.addWidget(networkGroup)
        self.mainLayout.addWidget(self.updateScaffoldingButton)
        self.mainLayout.addWidget(self.statusLabel)
        self.mainLayout.addStretch(1)

        self.createAxesButton.clicked.connect(self.onCreateAxes)
        self.createNetworkButton.clicked.connect(self.onCreateNetwork)

    def onEnterStep(self):
        landmark_node = self.get_landmark_node()
        if not landmark_node:
            return

        axes_exist = bool(slicer.util.getFirstNodeByName("X_axis") and
                          slicer.util.getFirstNodeByName("Y_axis") and
                          slicer.util.getFirstNodeByName("Z_axis"))
        network_exist = bool(slicer.util.getFirstNodeByName("Line_1") and
                             slicer.util.getFirstNodeByName("Line_2") and
                             slicer.util.getFirstNodeByName("Line_3"))

        if (axes_exist or network_exist) and self.logic.scaffold_node_guid and self.logic.scaffold_node_guid != landmark_node.GetID():
            self.updateScaffoldingButton.setVisible(True)
            self.statusLabel.setText("⚠️ Hard tissue node changed. Scaffolding is stale. Click 'Update Scaffolding' to refresh using the current node.")
            self.createAxesButton.setEnabled(False)
            self.createNetworkButton.setEnabled(False)
            return

        if axes_exist and network_exist and self.logic.scaffold_node_guid == landmark_node.GetID():
            self.updateScaffoldingButton.setVisible(False)
            self.createAxesButton.setEnabled(True)
            self.createNetworkButton.setEnabled(True)
            self.statusLabel.setText("✓ Scaffolding complete. Auto-advancing...")
            if not self.main_gui.manual_navigation:
                qt.QTimer.singleShot(200, self._auto_advance)
            return

        self.updateScaffoldingButton.setVisible(False)
        self.createAxesButton.setEnabled(True)
        self.createNetworkButton.setEnabled(True)
        self.statusLabel.setText("Status: Please click 'Create X, Y, Z Axes' and 'Create Network Lines'.")

    def _auto_advance(self):
        if self.main_gui.currentStep < len(self.main_gui.step_widgets) - 1:
            self.main_gui.currentStep += 1
            self.main_gui.update_ui()

    def onUpdateScaffolding(self):
        landmark_node = self.get_landmark_node()
        if not landmark_node:
            return
        self.statusLabel.setText("Status: Updating scaffolding...")
        slicer.app.processEvents()
        try:
            self.logic.create_axes(landmark_node, self.data["report_window"])
            active_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
            if not active_plane:
                raise ValueError("Please create Reference Planes in Step 2 first.")
            plane_name = active_plane.GetName()
            self.logic.create_network_lines(landmark_node, plane_name)
            self.updateScaffoldingButton.setVisible(False)
            self.createAxesButton.setEnabled(True)
            self.createNetworkButton.setEnabled(True)
            self.statusLabel.setText(f"✓ Status: Scaffolding updated for Run {self.logic.run_number}.")
            self.onEnterStep()
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def onCreateAxes(self):
        self.statusLabel.setText("Status: Creating axes...")
        slicer.app.processEvents()
        try:
            landmark_node = self.get_landmark_node()
            self.logic.create_axes(landmark_node, self.data["report_window"])
            self.statusLabel.setText(f"✓ Status: Axes created for Run {self.logic.run_number}.")
            self.onEnterStep()
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def onCreateNetwork(self):
        self.statusLabel.setText("Status: Creating network lines...")
        slicer.app.processEvents()
        try:
            landmark_node = self.get_landmark_node()
            active_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
            if not active_plane:
                raise ValueError("Please create Reference Planes in Step 2 first.")
            plane_name = active_plane.GetName()
            self.logic.create_network_lines(landmark_node, plane_name)
            self.statusLabel.setText(f"✓ Status: Network lines created.")
            self.onEnterStep()
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

# =============================================================================
# STEPS 4-8 (with consistency mode)
# =============================================================================
class Step4_PronasaleAnterior(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)
        self.mainLayout.addWidget(qt.QLabel("Predict the anterior position of the pronasale."))
        table_html = """<table border="1" cellspacing="0" cellpadding="3" width="100%">
            <tr><th>Literature</th><th>Ancestry</th><th>Sex</th><th>Equation</th></tr>
            <tr><td>Rynn 2010</td><td>ANY</td><td>All</td><td>0.83 * Y - 3.5</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>ANY</td><td>0.57 * Y + 2.33</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Female</td><td>0.681 * Y + 2.711</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Male</td><td>0.776 * Y - 0.481</td></tr>
            </table><br><b>Y</b> = Y-axis length"""
        self.mainLayout.addWidget(qt.QLabel(table_html))
        self.pa_equations = ["pred Rynn PA", "pred Sarilita PA", "pred Bulut F PA", "pred Bulut M PA"]
        self.pa_checkbox_list = []
        for eq in self.pa_equations:
            checkbox = qt.QCheckBox(eq)
            self.mainLayout.addWidget(checkbox)
            self.pa_checkbox_list.append(checkbox)

        self.calculateButton = qt.QPushButton("Calculate Pronasale Anterior")
        self.calculateButton.clicked.connect(self.onCalculatePA)
        self.mainLayout.addWidget(self.calculateButton)

        self.consistencyButton = qt.QPushButton("Select Consistent Equations (Author & Sex)")
        self.consistencyButton.setStyleSheet("background-color: #E8F0FE; font-weight: bold;")
        self.consistencyButton.clicked.connect(self.onConsistencyMode)
        self.mainLayout.addWidget(self.consistencyButton)

        self.workflowButton = qt.QPushButton("▶ Run Consistent Workflow (Auto)")
        self.workflowButton.setStyleSheet("background-color: #28A745; color: white; font-weight: bold;")
        self.workflowButton.clicked.connect(self.run_consistent_workflow)
        self.mainLayout.addWidget(self.workflowButton)

        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.statusLabel)
        self.mainLayout.addStretch(1)

    def onCalculatePA(self):
        self.statusLabel.setText("Status: Calculating...")
        slicer.app.processEvents()
        try:
            landmark_node = self.get_landmark_node()
            chosen = [cb.text for cb in self.pa_checkbox_list if cb.isChecked()]
            if not chosen:
                raise ValueError("Please select at least one equation.")
            self.logic.calculate_pa(landmark_node, chosen, self.data["report_window"])
            self.statusLabel.setText(f"✓ Status: Created {len(chosen)} PA line(s) for Run {self.logic.run_number}.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def onConsistencyMode(self):
        dialog = qt.QDialog(self)
        dialog.setWindowTitle("Select Consistent Equations")
        dialog.setModal(True)
        layout = qt.QVBoxLayout(dialog)

        info = qt.QLabel(
            "Choose an author and biological sex to automatically select matching equations.\n"
            "After clicking 'Proceed', the checkboxes below will be updated.\n"
            "Then click 'Calculate Pronasale Anterior' to create the PA lines, or use 'Run Consistent Workflow' to execute every prediction and error measuring step automatically.\n"
            "Please note that the Rynn (2010) and Sarilita (2018) methods are NOT sex-specific in predicting PA, PV, pFHP; only nasal depth (ND) and nasal length (NL)"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background-color: #FFF3CD; padding: 8px; border-radius: 4px;")
        layout.addWidget(info)

        author_label = qt.QLabel("Author:")
        author_combo = qt.QComboBox()
        author_combo.addItems(["Rynn", "Sarilita", "Bulut"])
        layout.addWidget(author_label)
        layout.addWidget(author_combo)

        sex_label = qt.QLabel("Sex:")
        sex_combo = qt.QComboBox()
        sex_combo.addItems(["Male", "Female"])
        layout.addWidget(sex_label)
        layout.addWidget(sex_combo)

        btn_box = qt.QDialogButtonBox(qt.Qt.Horizontal)
        proceed_btn = qt.QPushButton("Proceed")
        cancel_btn = qt.QPushButton("Cancel")
        btn_box.addButton(proceed_btn, qt.QDialogButtonBox.AcceptRole)
        btn_box.addButton(cancel_btn, qt.QDialogButtonBox.RejectRole)
        btn_box.accepted.connect(lambda: self._apply_consistency_mode(dialog, author_combo, sex_combo))
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        dialog.exec_()

    def _apply_consistency_mode(self, dialog, author_combo, sex_combo):
        author = author_combo.currentText
        sex_text = sex_combo.currentText
        sex_map = {"All": "All", "Male": "M", "Female": "F"}
        sex = sex_map[sex_text]
        self.data["consistency_mode"] = {"author": author, "sex": sex}
        self._apply_to_pa_checkboxes()
        dialog.accept()

    def _apply_to_pa_checkboxes(self):
        mode = self.data.get("consistency_mode")
        if not mode:
            return
        filtered = self.logic.filter_equations_by_mode(self.pa_equations, mode)
        for cb in self.pa_checkbox_list:
            if cb.text in filtered:
                cb.setChecked(True)
            else:
                cb.setChecked(False)

    def onEnterStep(self):
        if self.data.get("consistency_mode"):
            self._apply_to_pa_checkboxes()

    def run_consistent_workflow(self):
        mode = self.data.get("consistency_mode")
        if not mode:
            qt.QMessageBox.warning(self, "No Consistency Mode",
                "Please click 'Select Consistent Equations' first to choose an author and sex.")
            return

        if not slicer.util.getFirstNodeByName("INB") and not slicer.util.getFirstNodeByName("MSP"):
            qt.QMessageBox.warning(self, "Missing Planes",
                "Please complete Steps 2 and 3 (Plane Setup and Scaffolding) first.")
            return

        landmark_node = self.get_landmark_node()
        if not landmark_node:
            qt.QMessageBox.warning(self, "Missing Landmarks",
                "Please select a hard tissue landmark node in Step 1.")
            return

        self.statusLabel.setText("Status: Running consistent workflow...")
        slicer.app.processEvents()

        try:
            pa_equations = self.logic.filter_equations_by_mode(self.pa_equations, mode)
            if not pa_equations:
                raise ValueError("No matching PA equations for the selected mode.")
            self.logic.calculate_pa(landmark_node, pa_equations, self.data["report_window"])
            self.statusLabel.setText("Status: PA done. Running PV...")
            slicer.app.processEvents()

            pa_lines = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
                       if n.GetName().startswith(f"PA_{self.logic.run_number}_")]
            if not pa_lines:
                raise ValueError("No PA lines created.")
            pa_line_name = pa_lines[0].GetName()

            pv_equations = self.logic.filter_equations_by_mode(
                ["pred Rynn PV", "pred Sarilita PV", "pred Bulut F PV", "pred Bulut M PV"], mode)
            if pv_equations:
                self.logic.calculate_pv(pa_line_name, pv_equations, self.data["report_window"])
                self.statusLabel.setText("Status: PV done. Running pFHP...")
                slicer.app.processEvents()
            else:
                self.statusLabel.setText("Status: No PV equations for mode, skipping.")
                slicer.app.processEvents()

            pfhp_equations = self.logic.filter_equations_by_mode(
                ["pred Rynn pFHP", "pred Sarilita pFHP", "pred Bulut F pFHP", "pred Bulut M pFHP"], mode)
            if pfhp_equations:
                self.logic.calculate_pfhp(landmark_node, pfhp_equations, self.data["report_window"])
                self.statusLabel.setText("Status: pFHP done. Running SN...")
                slicer.app.processEvents()
            else:
                self.statusLabel.setText("Status: No pFHP equations for mode, skipping.")
                slicer.app.processEvents()

            pred_node = slicer.util.getFirstNodeByName(f"soft_tissue_pred_{self.logic.run_number}")
            if not pred_node:
                raise ValueError("Prediction node not found. Ensure PV created pronasale points.")

            pronasale_idx = None
            for i in range(pred_node.GetNumberOfControlPoints()):
                label = pred_node.GetNthControlPointLabel(i)
                if "pronasale" in label.lower():
                    pronasale_idx = i
                    break
            if pronasale_idx is None:
                raise ValueError("No pronasale point found in prediction node.")

            pfhp_lines = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
                         if n.GetName().startswith(f"pFHP_{self.logic.run_number}_")]
            if not pfhp_lines:
                raise ValueError("No pFHP lines found.")
            pfhp_line_name = pfhp_lines[0].GetName()

            nd_equations = self.logic.filter_equations_by_mode(
                ["pred Rynn F ND", "pred Rynn M ND", "pred Sarilita M ND", "pred Sarilita F ND",
                 "pred Bulut F ND", "pred Bulut M ND"], mode)
            if not nd_equations:
                raise ValueError("No ND equations for mode.")
            nd_equation = nd_equations[0]

            active_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
            if not active_plane:
                raise ValueError("No profile plane found.")
            plane_name = active_plane.GetName()

            self.logic.calculate_sn(pronasale_idx, nd_equation, pfhp_line_name, plane_name, self.data["report_window"])
            self.statusLabel.setText("Status: SN done. Running Nasion...")
            slicer.app.processEvents()

            subnasale_idx = None
            for i in range(pred_node.GetNumberOfControlPoints()):
                label = pred_node.GetNthControlPointLabel(i)
                if "subnasale" in label.lower():
                    subnasale_idx = i
                    break
            if subnasale_idx is None:
                raise ValueError("No subnasale point found in prediction node.")

            nh_equations = self.logic.filter_equations_by_mode(
                ["pred Rynn EA M NH", "pred Rynn EA F NH", "pred Sarilita M NH",
                 "pred Sarilita F NH", "pred Bulut F NH", "pred Bulut M NH"], mode)
            nl_equations = self.logic.filter_equations_by_mode(
                ["pred Rynn EA NL", "pred Sarilita F NL", "pred Sarilita M NL", "pred Bulut F NL", "pred Bulut M NL"], mode)
            if not nh_equations or not nl_equations:
                raise ValueError("No NH or NL equations for mode.")
            nh_eq = nh_equations[0]
            nl_eq = nl_equations[0]

            self.logic.calculate_nasion(subnasale_idx, nh_eq, pronasale_idx, nl_eq, plane_name, self.data["report_window"])
            self.statusLabel.setText("Status: Nasion done. Running automatic Basic Comparison...")
            slicer.app.processEvents()

            step9 = self.main_gui.step_widgets[8]
            soft_node = step9.softTissueSelector.currentNode()
            if soft_node:
                try:
                    step9.onBasicCompare()
                    self.statusLabel.setText("Status: Workflow complete, including Basic Comparison.")
                except Exception as e:
                    self.statusLabel.setText(f"Status: Basic Comparison failed: {e}")
            else:
                self.statusLabel.setText("Status: Workflow complete. (No soft tissue node for Basic Comparison.)")

            slicer.app.processEvents()

            qt.QMessageBox.information(self, "Workflow Complete",
                "All predictions have been generated using consistent equations.\n"
                "Switching to Step 9 (Analysis). The individual equations and calculations are stored and are visible by clicking the `Show Calculation Report` button.")
            self.main_gui.currentStep = 8
            self.main_gui.update_ui()

        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")
            import traceback
            traceback.print_exc()

class Step5_PronasaleVertical(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)
        self.mainLayout.addWidget(qt.QLabel("Predict the vertical position of the pronasale."))
        table_html = """<table border="1" cellspacing="0" cellpadding="3" width="100%">
            <tr><th>Literature</th><th>Ancestry</th><th>Sex</th><th>Equation</th></tr>
            <tr><td>Rynn 2010</td><td>ANY</td><td>All</td><td>0.9 * X - 2</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>All</td><td>0.88 * X + 0.68</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Female</td><td>0.779 * X + 5.501</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Male</td><td>0.954 * X - 3.53</td></tr>
            </table><br><b>X</b> = X-axis length"""
        self.mainLayout.addWidget(qt.QLabel(table_html))

        self.pa_group = qt.QGroupBox("1. Select PA Line(s) to Use")
        self.mainLayout.addWidget(self.pa_group)
        self.pa_checkbox_list = []

        pv_group = qt.QGroupBox("2. Select PV Equation(s)")
        self.mainLayout.addWidget(pv_group)
        pv_layout = qt.QVBoxLayout(pv_group)
        self.pv_equations = ["pred Rynn PV", "pred Sarilita PV", "pred Bulut F PV", "pred Bulut M PV"]
        self.pv_checkbox_list = []
        for eq in self.pv_equations:
            cb = qt.QCheckBox(eq)
            pv_layout.addWidget(cb)
            self.pv_checkbox_list.append(cb)

        self.calculateButton = qt.QPushButton("Calculate Pronasale Vertical")
        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.calculateButton)
        self.mainLayout.addWidget(self.statusLabel)
        self.mainLayout.addStretch(1)
        self.calculateButton.clicked.connect(self.onCalculatePV)

    def onEnterStep(self):
        layout = self.pa_group.layout() or qt.QVBoxLayout(self.pa_group)
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()
        self.pa_checkbox_list.clear()

        pa_lines = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if n.GetName().startswith(f"PA_{self.logic.run_number}_")]

        if not pa_lines:
            layout.addWidget(qt.QLabel("No PA lines found. Please complete Step 4."))
        else:
            for ln in pa_lines:
                cb = qt.QCheckBox(ln.GetName())
                layout.addWidget(cb)
                self.pa_checkbox_list.append(cb)
            if len(self.pa_checkbox_list) == 1:
                self.pa_checkbox_list[0].setChecked(True)

        self._apply_consistency_to_pa_lines()

    def _apply_consistency_to_pa_lines(self):
        mode = self.data.get("consistency_mode")
        if not mode:
            return
        filtered_lines = []
        for cb in self.pa_checkbox_list:
            line_node = slicer.util.getNode(cb.text)
            if line_node:
                eq_attr = line_node.GetAttribute("Equation")
                if eq_attr and eq_attr in self.logic.filter_equations_by_mode([eq_attr], mode):
                    filtered_lines.append(cb)
        for cb in self.pa_checkbox_list:
            cb.setChecked(False)
        for cb in filtered_lines:
            cb.setChecked(True)

    def onCalculatePV(self):
        self.statusLabel.setText("Status: Calculating...")
        slicer.app.processEvents()
        try:
            chosen_pa_lines = [cb.text for cb in self.pa_checkbox_list if cb.isChecked()]
            chosen_pv_eqs = [cb.text for cb in self.pv_checkbox_list if cb.isChecked()]
            if not chosen_pa_lines or not chosen_pv_eqs:
                raise ValueError("Please select at least one PA line and one PV equation.")
            for pa_line in chosen_pa_lines:
                self.logic.calculate_pv(pa_line, chosen_pv_eqs, self.data["report_window"])
            self.statusLabel.setText(f"✓ Status: Created PV points for Run {self.logic.run_number}.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

class Step6_PFH(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)
        self.mainLayout.addWidget(qt.QLabel("<b>Select pFHP equation(s)</b>"))
        table_html = """<table border="1" cellspacing="0" cellpadding="3" width="100%">
            <tr><th>Literature</th><th>Ancestry</th><th>Sex</th><th>Equation</th></tr>
            <tr><td>Rynn 2010</td><td>ANY</td><td>All</td><td>0.93 * Y - 6</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>All</td><td>0.58 * Y + 4.55</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Female</td><td>1.161 + 0.775 * Y</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Male</td><td>0.518 + 0.777 * Y</td></tr>
            </table><br><b>Y</b> = Y-axis length"""
        self.mainLayout.addWidget(qt.QLabel(table_html))
        self.pfhp_equations = ["pred Rynn pFHP", "pred Sarilita pFHP", "pred Bulut F pFHP", "pred Bulut M pFHP"]
        self.pfhp_checkbox_list = []
        for eq in self.pfhp_equations:
            cb = qt.QCheckBox(eq)
            self.mainLayout.addWidget(cb)
            self.pfhp_checkbox_list.append(cb)
        self.calculateButton = qt.QPushButton("Calculate pFHP")
        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.calculateButton)
        self.mainLayout.addWidget(self.statusLabel)
        self.mainLayout.addStretch(1)
        self.calculateButton.clicked.connect(self.onCalculatePFHP)

    def onEnterStep(self):
        self._apply_consistency_to_pfhp()

    def _apply_consistency_to_pfhp(self):
        mode = self.data.get("consistency_mode")
        if not mode:
            return
        filtered = self.logic.filter_equations_by_mode(self.pfhp_equations, mode)
        for cb in self.pfhp_checkbox_list:
            if cb.text in filtered:
                cb.setChecked(True)
            else:
                cb.setChecked(False)

    def onCalculatePFHP(self):
        self.statusLabel.setText("Status: Calculating...")
        slicer.app.processEvents()
        try:
            landmark_node = self.get_landmark_node()
            chosen = [cb.text for cb in self.pfhp_checkbox_list if cb.isChecked()]
            if not chosen:
                raise ValueError("Please select at least one pFHP equation.")
            self.logic.calculate_pfhp(landmark_node, chosen, self.data["report_window"])
            self.statusLabel.setText(f"✓ Status: Created {len(chosen)} pFHP line(s) for Run {self.logic.run_number}.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

class Step7_SoftTissueSN(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)
        table_html = """<table border="1" cellspacing="0" cellpadding="3" width="100%">
            <tr><th>Literature</th><th>Ancestry</th><th>Sex</th><th>Equation</th></tr>
            <tr><td>Rynn 2010</td><td>ANY</td><td>Female</td><td>0.5 * Y + 1.5</td></tr>
            <tr><td>Rynn 2010</td><td>ANY</td><td>Male</td><td>0.4 * Y + 5</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>Female</td><td>0.29 * Y + 6.24</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>Male</td><td>0.22 * Z + 4.02</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Female</td><td>0.423 * Y + 5.169</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Male</td><td>0.386 * Y + 6.587</td></tr>
            </table><br><b>Y</b> = Y-axis, <b>Z</b> = Z-axis"""
        self.mainLayout.addWidget(qt.QLabel(table_html))

        self.point_group = qt.QGroupBox("1. Choose pronasale pred point")
        self.nd_eq_group = qt.QGroupBox("2. Choose ND radius equation")
        self.line_group = qt.QGroupBox("3. Choose pFHP line")

        nd_layout = qt.QVBoxLayout(self.nd_eq_group)
        self.nd_equations = ["pred Rynn F ND", "pred Rynn M ND", "pred Sarilita M ND", "pred Sarilita F ND", "pred Bulut F ND", "pred Bulut M ND"]
        self.nd_eq_buttons = qt.QButtonGroup(self)
        for i, eq in enumerate(self.nd_equations):
            radio = qt.QRadioButton(eq)
            nd_layout.addWidget(radio)
            self.nd_eq_buttons.addButton(radio, i)

        self.calculateButton = qt.QPushButton("Create ND Circle and Find Intersection")
        self.statusLabel = qt.QLabel("Status: Waiting for user.")
        self.statusLabel.setWordWrap(True)

        for w in [self.point_group, self.nd_eq_group, self.line_group, self.calculateButton, self.statusLabel]:
            self.mainLayout.addWidget(w)
        self.mainLayout.addStretch(1)
        self.calculateButton.clicked.connect(self.onCalculateSN)

    def _populate_radio_group(self, group_box, items, button_group):
        layout = group_box.layout() or qt.QVBoxLayout(group_box)
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()
        for button in button_group.buttons():
            button_group.removeButton(button)
        if not items:
            layout.addWidget(qt.QLabel("No items found."))
        else:
            for i, (label, data) in enumerate(items):
                radio = qt.QRadioButton(label)
                layout.addWidget(radio)
                button_group.addButton(radio, data)
            if button_group.buttons():
                button_group.buttons()[0].setChecked(True)

    def onEnterStep(self):
        pred_node = slicer.util.getFirstNodeByName(f"soft_tissue_pred_{self.logic.run_number}")

        self.pronasale_points_group = qt.QButtonGroup(self)
        pronasale_items = [(pred_node.GetNthControlPointLabel(i), i) for i in range(pred_node.GetNumberOfControlPoints()) if "pronasale" in pred_node.GetNthControlPointLabel(i).lower()] if pred_node else []
        self._populate_radio_group(self.point_group, pronasale_items, self.pronasale_points_group)

        self.pfhp_lines_group = qt.QButtonGroup(self)
        pfhp_nodes = [node for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if node.GetName().startswith(f"pFHP_{self.logic.run_number}_")]
        self.pfhp_line_names = [node.GetName() for node in pfhp_nodes]
        pfhp_items = [(name, i) for i, name in enumerate(self.pfhp_line_names)]
        self._populate_radio_group(self.line_group, pfhp_items, self.pfhp_lines_group)

        self._apply_consistency_to_nd()

    def _apply_consistency_to_nd(self):
        mode = self.data.get("consistency_mode")
        if not mode:
            return
        filtered = self.logic.filter_equations_by_mode(self.nd_equations, mode)
        for i, eq in enumerate(self.nd_equations):
            if eq in filtered:
                self.nd_eq_buttons.button(i).setChecked(True)
                return

    def onCalculateSN(self):
        self.statusLabel.setText("Status: Calculating...")
        slicer.app.processEvents()
        try:
            active_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
            if not active_plane:
                raise ValueError("Please create Reference Planes in Step 2 first.")
            plane_name = active_plane.GetName()

            center_point_index = self.pronasale_points_group.checkedId()
            nd_equation_index = self.nd_eq_buttons.checkedId()
            pfhp_line_index = self.pfhp_lines_group.checkedId()

            if -1 in [center_point_index, nd_equation_index, pfhp_line_index]:
                raise ValueError("Please make a selection in all three sections.")

            self.logic.calculate_sn(center_point_index, self.nd_equations[nd_equation_index], self.pfhp_line_names[pfhp_line_index], plane_name, self.data["report_window"])
            self.statusLabel.setText(f"✓ Status: Created sn point for Run {self.logic.run_number}.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

class Step8_Nasion(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)

        nh_table_html = """<b>NH (Nasal Height) Equations</b><table border="1" cellspacing="0" cellpadding="3" width="100%">
            <tr><th>Literature</th><th>Ancestry</th><th>Sex</th><th>Equation</th></tr>
            <tr><td>Rynn 2010</td><td>European American</td><td>Male</td><td>0.78*Z+9.5</td></tr>
            <tr><td>Rynn 2010</td><td>European American</td><td>Female</td><td>0.63*Z+17</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>Male</td><td>0.79*Z+3.74</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>Female</td><td>0.69*X+12.36</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Female</td><td>0.687*Z+15.047</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Male</td><td>0.784*Z+9.858</td></tr>
            </table>"""

        nl_table_html = """<b>NL (Nasal Length) Equations</b><table border="1" cellspacing="0" cellpadding="3" width="100%">
            <tr><th>Literature</th><th>Ancestry</th><th>Sex</th><th>Equation</th></tr>
            <tr><td>Rynn 2010</td><td>European American</td><td>ANY</td><td>0.74*Z+3.5</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>Female</td><td>0.71*Z+6.624</td></tr>
            <tr><td>Sarilita 2018</td><td>Indonesian</td><td>Male</td><td>0.807*Z+0.764</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Female</td><td>0.71*Z+6.624</td></tr>
            <tr><td>Bulut 2019</td><td>Turkish</td><td>Male</td><td>0.66*X+7.77</td></tr>
            </table><br><b>X</b> = X-axis, <b>Z</b> = Z-axis"""

        self.nh_group = qt.QGroupBox("1. Choose NH center ('sn' point)")
        self.nh_eq_group = qt.QGroupBox("2. Choose NH equation")
        nh_eq_layout = qt.QVBoxLayout(self.nh_eq_group)
        nh_eq_layout.addWidget(qt.QLabel(nh_table_html))

        self.nl_group = qt.QGroupBox("3. Choose NL center ('pronasale' point)")
        self.nl_eq_group = qt.QGroupBox("4. Choose NL equation")
        nl_eq_layout = qt.QVBoxLayout(self.nl_eq_group)
        nl_eq_layout.addWidget(qt.QLabel(nl_table_html))

        self.nh_equations = ["pred Rynn EA M NH", "pred Rynn EA F NH", "pred Sarilita M NH", "pred Sarilita F NH", "pred Bulut F NH", "pred Bulut M NH"]
        self.nh_eq_buttons = self._add_buttons_to_group(nh_eq_layout, self.nh_equations)

        self.nl_equations = ["pred Rynn EA NL", "pred Sarilita F NL", "pred Sarilita M NL","pred Bulut F NL", "pred Bulut M NL"]
        self.nl_eq_buttons = self._add_buttons_to_group(nl_eq_layout, self.nl_equations)

        self.calculateButton = qt.QPushButton("Draw Circles and Predict Nasion")
        self.statusLabel = qt.QLabel("Status: Waiting for user.")

        for w in [self.nh_group, self.nh_eq_group, self.nl_group, self.nl_eq_group, self.calculateButton, self.statusLabel]:
            self.mainLayout.addWidget(w)
        self.mainLayout.addStretch(1)
        self.calculateButton.clicked.connect(self.onCalculateNasion)

    def _add_buttons_to_group(self, layout, equations):
        button_group = qt.QButtonGroup(self)
        for i, eq in enumerate(equations):
            radio = qt.QRadioButton(eq)
            layout.addWidget(radio)
            button_group.addButton(radio, i)
        return button_group

    def _populate_radio_group(self, group_box, items, button_group):
        layout = group_box.layout() or qt.QVBoxLayout(group_box)
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()
        for button in button_group.buttons():
            button_group.removeButton(button)
        if not items:
            layout.addWidget(qt.QLabel("No items found."))
        else:
            for i, (label, data) in enumerate(items):
                radio = qt.QRadioButton(label)
                layout.addWidget(radio)
                button_group.addButton(radio, data)
            if button_group.buttons():
                button_group.buttons()[0].setChecked(True)

    def onEnterStep(self):
        pred_node = slicer.util.getFirstNodeByName(f"soft_tissue_pred_{self.logic.run_number}")

        self.nh_center_points_group = qt.QButtonGroup(self)
        nh_items = [(pred_node.GetNthControlPointLabel(i), i) for i in range(pred_node.GetNumberOfControlPoints()) if "subnasale" in pred_node.GetNthControlPointLabel(i).lower()] if pred_node else []
        self._populate_radio_group(self.nh_group, nh_items, self.nh_center_points_group)

        self.nl_center_points_group = qt.QButtonGroup(self)
        nl_items = [(pred_node.GetNthControlPointLabel(i), i) for i in range(pred_node.GetNumberOfControlPoints()) if "pronasale" in pred_node.GetNthControlPointLabel(i).lower()] if pred_node else []
        self._populate_radio_group(self.nl_group, nl_items, self.nl_center_points_group)

        self._apply_consistency_to_nh_nl()

    def _apply_consistency_to_nh_nl(self):
        mode = self.data.get("consistency_mode")
        if not mode:
            return
        filtered_nh = self.logic.filter_equations_by_mode(self.nh_equations, mode)
        for i, eq in enumerate(self.nh_equations):
            if eq in filtered_nh:
                self.nh_eq_buttons.button(i).setChecked(True)
                break
        filtered_nl = self.logic.filter_equations_by_mode(self.nl_equations, mode)
        for i, eq in enumerate(self.nl_equations):
            if eq in filtered_nl:
                self.nl_eq_buttons.button(i).setChecked(True)
                break

    def onCalculateNasion(self):
        self.statusLabel.setText("Status: Calculating...")
        slicer.app.processEvents()
        try:
            active_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
            if not active_plane:
                raise ValueError("Please create Reference Planes in Step 2 first.")
            plane_name = active_plane.GetName()

            nh_center_idx = self.nh_center_points_group.checkedId()
            nh_eq_idx = self.nh_eq_buttons.checkedId()
            nl_center_idx = self.nl_center_points_group.checkedId()
            nl_eq_idx = self.nl_eq_buttons.checkedId()

            if -1 in [nh_center_idx, nh_eq_idx, nl_center_idx, nl_eq_idx]:
                raise ValueError("Please make a selection in all four sections.")

            self.logic.calculate_nasion(nh_center_idx, self.nh_equations[nh_eq_idx], nl_center_idx, self.nl_equations[nl_eq_idx], plane_name, self.data["report_window"])
            self.statusLabel.setText(f"✓ Status: Created nasion point for Run {self.logic.run_number}.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

# =============================================================================
# STEP 9: ANALYSIS
# =============================================================================
class Step9_Analysis(StepWidget):
    def __init__(self, title, logic, data, main_gui, parent=None):
        super().__init__(title, logic, data, main_gui, parent)

        # --- Run Again Section ---
        run_again_group = qt.QGroupBox("🔄 Start a New Run")
        run_again_layout = qt.QVBoxLayout(run_again_group)

        info_label = qt.QLabel("Click below to start a new run with different equations. Your current geometry will stay visible so you can compare!")
        info_label.setWordWrap(True)
        run_again_layout.addWidget(info_label)

        note_label = qt.QLabel("<b>📝 Note:</b> All runs use the same reference planes (INB/MSP). To change planes, save your scene and reload 3D Slicer.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("background-color: #FFF3CD; padding: 10px; border-radius: 5px;")
        run_again_layout.addWidget(note_label)

        self.runAgainButton = qt.QPushButton("▶ Run Again (Start New Run)")
        self.runAgainButton.setStyleSheet("background-color: #28A745; color: white; font-weight: bold; padding: 10px;")
        run_again_layout.addWidget(self.runAgainButton)

        # --- Analysis Tools Section ---
        compare_group = qt.QGroupBox("📊 Analysis Tools")
        compare_layout = qt.QVBoxLayout(compare_group)

        selectorLayout = qt.QFormLayout()
        self.softTissueSelector = slicer.qMRMLNodeComboBox()
        self.softTissueSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.softTissueSelector.setMRMLScene(slicer.mrmlScene)
        self.softTissueSelector.addEnabled = False
        self.softTissueSelector.removeEnabled = False
        self.softTissueSelector.noneEnabled = True
        self.softTissueSelector.setToolTip("Select the soft tissue landmark file you want to compare against")
        selectorLayout.addRow("<b>Select Soft Tissue Landmarks:</b>", self.softTissueSelector)
        compare_layout.addLayout(selectorLayout)

        self.softNodeStatusLabel = qt.QLabel("Status: No soft tissue node selected.")
        self.softNodeStatusLabel.setWordWrap(True)
        compare_layout.addWidget(self.softNodeStatusLabel)

        self.softTissueSelector.currentNodeChanged.connect(self._updateSoftNodeStatus)
        self.softTissueSelector.currentNodeChanged.connect(self._storeSoftNodeID)

        self.downloadSoftButton = qt.QPushButton("Download 'Rynn_soft_tissue' Landmarks (if not yet downloaded)")
        self.downloadSoftButton.setStyleSheet("background-color: #007BFF; color: white;")
        compare_layout.addWidget(self.downloadSoftButton)

        workflow_text = qt.QLabel(
            "<b>🔍 Recommended Workflow:</b><br>"
            "① <b>Basic Comparison</b> – independent, run anytime.<br>"
            "② <b>Projection Network</b> – creates MAW/MNW lines. <b>Must be run first</b> for Advanced Analysis.<br>"
            "③ <b>Advanced Analysis</b> – requires Projection Network to have been run."
        )
        workflow_text.setWordWrap(True)
        workflow_text.setStyleSheet("background-color: #E8F0FE; padding: 8px; border-radius: 4px;")
        compare_layout.addWidget(workflow_text)

        self.basicCompareButton = qt.QPushButton("① Run Basic Comparison (Errors & Angles)")
        self.basicCompareButton.setToolTip(
            "📏 Measurements created:\n"
            "• Error lines (red) connecting predicted → actual for Nasion, Pronasale, Subnasale.\n"
            "• Predicted & True nasal angles.\n\n"
            "✅ Independent – does not require any other analysis."
        )
        compare_layout.addWidget(self.basicCompareButton)

        self.projectionButton = qt.QPushButton("② Create Rynn Projection Network")
        self.projectionButton.setToolTip(
            "📏 Measurements created:\n"
            "• n-pt1R/L, n-pt2R/L, ... n-pt8R/L (direct distances from nasion to each soft tissue point).\n"
            "• Projected lengths onto NPP (lat), PTP (ant), and INB/MSP (vert) planes.\n"
            "• MAW (hard tissue alare width) and MNW (soft tissue alare width) lines.\n\n"
            "⚠️ Required for Advanced Analysis – run this first!"
        )
        compare_layout.addWidget(self.projectionButton)

        self.advancedCompareButton = qt.QPushButton("③ Run Advanced Network Analysis")
        self.advancedCompareButton.setToolTip(
            "📏 Measurements created:\n"
            "• Displacement error lines (adv_error_*) between corresponding hard/soft points:\n"
            "  pt5L↔CL, pt5R↔CR, pt7L↔LL, pt7R↔LR, pt4L↔XL, pt4R↔XR.\n"
            "• Shortest distance between MAW and MNW lines.\n\n"
            "⛔ Requires the Projection Network to have been run (creates MAW/MNW)."
        )
        compare_layout.addWidget(self.advancedCompareButton)

        self.landmarkCompareButton = qt.QPushButton("📊 Show Landmark Comparison Table")
        self.landmarkCompareButton.setToolTip(
            "Opens a table with RAS coordinates of each predicted landmark, the corresponding true landmark,\n"
            "and the Euclidean error distance. If advanced analysis has been run, it also lists the advanced errors."
        )
        compare_layout.addWidget(self.landmarkCompareButton)
        self.landmarkCompareButton.clicked.connect(self.onShowLandmarkComparison)

        # --- Report & View Section ---
        cleanup_group = qt.QGroupBox("📋 Report & View")
        cleanup_layout = qt.QVBoxLayout(cleanup_group)
        self.toggleReportButton = qt.QPushButton("Show/Hide Calculation Report")
        self.toggleHelpersButton = qt.QPushButton("Toggle All Geometry Visibility")
        cleanup_layout.addWidget(self.toggleReportButton)
        cleanup_layout.addWidget(self.toggleHelpersButton)

        self.tableButton = qt.QPushButton("📊 Show Comprehensive Results Table")
        cleanup_layout.addWidget(self.tableButton)
        self.tableButton.clicked.connect(self.onShowComprehensiveTable)

        self.copyAllButton = qt.QPushButton("📋 Copy ALL Data (Excel)")
        self.copyAllButton.setToolTip("Copies the full calculation report, landmark comparison, and advanced errors into one TSV table.")
        cleanup_layout.addWidget(self.copyAllButton)
        self.copyAllButton.clicked.connect(self.onCopyAll)

        self.statusLabel = qt.QLabel(f"✓ Status: Run {self.logic.run_number} complete!")
        self.statusLabel.setWordWrap(True)

        # Add everything to the main layout
        self.mainLayout.addWidget(run_again_group)
        self.mainLayout.addWidget(compare_group)
        self.mainLayout.addWidget(cleanup_group)
        self.mainLayout.addWidget(self.statusLabel)
        self.mainLayout.addStretch(1)

        # Connect signals
        self.runAgainButton.clicked.connect(self.onRunAgain)
        self.downloadSoftButton.clicked.connect(self.onDownloadSoftLandmarks)
        self.basicCompareButton.clicked.connect(self.onBasicCompare)
        self.projectionButton.clicked.connect(self.onRunProjection)
        self.advancedCompareButton.clicked.connect(self.onAdvancedCompare)
        self.toggleReportButton.clicked.connect(self.onToggleReport)
        self.toggleHelpersButton.clicked.connect(self.onToggleHelpers)

        # ===== EXPORT FOR RSTUDIO =====
        if _rstudio_wrapper:
            _rstudio_wrapper.install_export_button_for(
                gui=self.main_gui,
                parent_layout=self.mainLayout,
                method="Rynn",
                variant="auto",
                table_widget=None,
            )       

    # ----- Helper methods -----
    def _updateSoftNodeStatus(self):
        soft_node = self.softTissueSelector.currentNode()
        if soft_node:
            self.softNodeStatusLabel.setText(f"✓ <b>Info:</b> Using soft tissue node: <b>'{soft_node.GetName()}'</b>.")
        else:
            self.softNodeStatusLabel.setText("<b>Action Needed:</b> Please select a soft tissue node or download one.")

    def _storeSoftNodeID(self):
        soft_node = self.softTissueSelector.currentNode()
        if soft_node:
            self.data["soft_node_id"] = soft_node.GetID()
        else:
            self.data.pop("soft_node_id", None)

    def _autoSelectSoftNode(self):
        preferred_node = None
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            if node.GetName().startswith("Rynn_soft_tissue"):
                preferred_node = node
                break
        if preferred_node:
            self.softTissueSelector.setCurrentNode(preferred_node)
            self.data["soft_node_id"] = preferred_node.GetID()
            return

        stored_id = self.data.get("soft_node_id")
        if stored_id:
            node = slicer.mrmlScene.GetNodeByID(stored_id)
            if node and node.IsA("vtkMRMLMarkupsFiducialNode"):
                self.softTissueSelector.setCurrentNode(node)
                return

        target_labels = ["pt1R", "pt1L", "pt2R", "pt2L", "pt3R", "pt3L", "pt4R", "pt4L",
                         "pt5R", "pt5L", "pt6R", "pt6L", "pt7R", "pt7L", "pt8R", "pt8L",
                         "n'", "sn'", "pn'"]
        best_node = None
        best_score = 0
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            labels = [node.GetNthControlPointLabel(i).lower() for i in range(node.GetNumberOfControlPoints())]
            score = sum(1 for lbl in target_labels if any(lbl in label for label in labels))
            if score >= 3 and score > best_score:
                best_score = score
                best_node = node
        if best_node:
            self.softTissueSelector.setCurrentNode(best_node)

    def onEnterStep(self):
        self._autoSelectSoftNode()
        self._updateSoftNodeStatus()
        has_projection = bool(slicer.util.getFirstNodeByName("MAW") and slicer.util.getFirstNodeByName("MNW"))
        if not has_projection:
            self.advancedCompareButton.setStyleSheet("background-color: #FFF3CD; border: 1px solid #FFA500;")
            self.advancedCompareButton.setToolTip(
                "📏 Measurements created:\n"
                "• Displacement error lines (adv_error_*) between corresponding hard/soft points.\n"
                "• Shortest distance between MAW and MNW lines.\n\n"
                "⚠️ Currently DISABLED – MAW/MNW not found. Please run 'Create Rynn Projection Network' first."
            )
        else:
            self.advancedCompareButton.setStyleSheet("")
            self.advancedCompareButton.setToolTip(
                "📏 Measurements created:\n"
                "• Displacement error lines (adv_error_*) between corresponding hard/soft points.\n"
                "• Shortest distance between MAW and MNW lines.\n\n"
                "✅ MAW/MNW found – ready to run!"
            )
        self.statusLabel.setText(f"✓ Status: Run {self.logic.run_number} complete!")

    def _generate_landmark_comparison_tsv(self):
        soft_node = self.softTissueSelector.currentNode()
        if not soft_node:
            return ""

        all_pred_nodes = []
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            if node.GetName().startswith("soft_tissue_pred_"):
                all_pred_nodes.append(node)

        def get_run_number(node):
            match = re.search(r'soft_tissue_pred_(\d+)', node.GetName())
            return int(match.group(1)) if match else 0

        all_pred_nodes.sort(key=get_run_number)
        if not all_pred_nodes:
            return ""

        true_dict = {}
        for i in range(soft_node.GetNumberOfControlPoints()):
            label = soft_node.GetNthControlPointLabel(i)
            pos = np.array(soft_node.GetNthControlPointPositionWorld(i))
            canonical = self.logic.get_landmark_canonical(label)
            if canonical:
                true_dict[canonical] = pos

        lines = []
        lines.append("=== Landmark Comparison (Predicted vs True) ===")
        lines.append("Run\tLandmark\tPred_X\tPred_Y\tPred_Z\tTrue_X\tTrue_Y\tTrue_Z\tError_mm")

        for pred_node in all_pred_nodes:
            run_name = pred_node.GetName()
            for i in range(pred_node.GetNumberOfControlPoints()):
                pred_label = pred_node.GetNthControlPointLabel(i)
                pred_pos = np.array(pred_node.GetNthControlPointPositionWorld(i))
                canonical = self.logic.get_landmark_canonical(pred_label)
                if canonical and canonical in true_dict:
                    true_pos = true_dict[canonical]
                    error = np.linalg.norm(pred_pos - true_pos)
                    lines.append(f"{run_name}\t{pred_label}\t{pred_pos[0]:.2f}\t{pred_pos[1]:.2f}\t{pred_pos[2]:.2f}\t{true_pos[0]:.2f}\t{true_pos[1]:.2f}\t{true_pos[2]:.2f}\t{error:.2f}")

        return "\n".join(lines)

    def _generate_advanced_errors_tsv(self):
        hard_node = self.get_landmark_node()
        soft_node = self.softTissueSelector.currentNode()
        if not hard_node or not soft_node:
            return ""

        hard_map = {}
        for i in range(hard_node.GetNumberOfControlPoints()):
            label = hard_node.GetNthControlPointLabel(i)
            pos = np.array(hard_node.GetNthControlPointPositionWorld(i))
            hard_map[label] = pos

        soft_map = {}
        for i in range(soft_node.GetNumberOfControlPoints()):
            label = soft_node.GetNthControlPointLabel(i)
            pos = np.array(soft_node.GetNthControlPointPositionWorld(i))
            soft_map[label] = pos

        adv_pairs = [
            ("pt5L", "CL"), ("pt5R", "CR"),
            ("pt7L", "LL"), ("pt7R", "LR"),
            ("pt4L", "XL"), ("pt4R", "XR"),
        ]

        lines = []
        lines.append("=== Advanced Displacement Errors ===")
        lines.append("Pair\tHard_X\tHard_Y\tHard_Z\tSoft_X\tSoft_Y\tSoft_Z\tError_mm")

        found = False
        for soft_label, hard_label in adv_pairs:
            if soft_label in soft_map and hard_label in hard_map:
                found = True
                soft_pos = soft_map[soft_label]
                hard_pos = hard_map[hard_label]
                error = np.linalg.norm(soft_pos - hard_pos)
                lines.append(f"{soft_label}↔{hard_label}\t{hard_pos[0]:.2f}\t{hard_pos[1]:.2f}\t{hard_pos[2]:.2f}\t{soft_pos[0]:.2f}\t{soft_pos[1]:.2f}\t{soft_pos[2]:.2f}\t{error:.2f}")

        return "\n".join(lines) if found else ""

    def onCopyAll(self):
        report_text = self.data["report_window"]._generate_report_text_excluding(["Basic Errors", "Advanced Errors"])
        if not report_text or report_text.startswith("--- Calculation Report ---\nNo results"):
            report_text = "# No calculation results available."

        comp_text = self._generate_landmark_comparison_tsv()
        if not comp_text:
            comp_text = "# No landmark comparison data available."

        adv_text = self._generate_advanced_errors_tsv()
        if not adv_text:
            adv_text = "# No advanced errors available."

        combined = []
        combined.append("===== CALCULATION REPORT =====")
        combined.append(report_text)
        combined.append("")
        combined.append(comp_text)
        combined.append("")
        combined.append(adv_text)

        full_text = "\n".join(combined)
        slicer.app.clipboard().setText(full_text)
        slicer.util.showStatusMessage("All data copied to clipboard as TSV (Excel‑friendly).", 3000)

    # ---------- Robust table copy helpers ----------
    def _copyTableToClipboard(self, table, *args):
        if not isinstance(table, qt.QTableWidget):
            slicer.util.showStatusMessage("Table not available.", 3000)
            return

        row_attr = getattr(table, "rowCount", 0)
        col_attr = getattr(table, "columnCount", 0)
        rows = row_attr() if callable(row_attr) else int(row_attr)
        cols = col_attr() if callable(col_attr) else int(col_attr)

        lines = []
        headers = []
        for c in range(cols):
            h = table.horizontalHeaderItem(c)
            headers.append(h.text() if h else f"Col{c+1}")
        lines.append("\t".join(headers))

        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = table.item(r, c)
                row_data.append(item.text() if item else "")
            lines.append("\t".join(row_data))

        slicer.app.clipboard().setText("\n".join(lines))
        slicer.util.showStatusMessage("Table copied to clipboard as TSV.", 3000)

    # ----- Slot methods for copy buttons -----
    def copy_comprehensive_table(self):
        if hasattr(self, 'comprehensive_table') and self.comprehensive_table:
            self._copyTableToClipboard(self.comprehensive_table)
        else:
            slicer.util.showStatusMessage("No table to copy.", 3000)

    def copy_landmark_table1(self):
        if hasattr(self, 'landmark_table1') and self.landmark_table1:
            self._copyTableToClipboard(self.landmark_table1)
        else:
            slicer.util.showStatusMessage("No table to copy.", 3000)

    def copy_landmark_table2(self):
        if hasattr(self, 'landmark_table2') and self.landmark_table2:
            self._copyTableToClipboard(self.landmark_table2)
        else:
            slicer.util.showStatusMessage("No table to copy.", 3000)

    # ----- Other methods -----
    def onRunAgain(self):
        self.data.pop("consistency_mode", None)
        self.logic.run_number += 1
        self.logic.item_counters = {}
        self.main_gui.updateRunLabel()

        msg = qt.QMessageBox(self)
        msg.setWindowModality(qt.Qt.ApplicationModal)
        msg.setIcon(qt.QMessageBox.Information)
        msg.setText(f"Starting Run {self.logic.run_number}!")
        msg.setInformativeText("Your previous run's geometry will stay visible so you can compare.\n\nClick OK to jump to Step 4 (PA calculation).")
        msg.setWindowTitle("New Run Started")
        msg.setStandardButtons(qt.QMessageBox.Ok)
        msg.exec_()

        self.main_gui.currentStep = 3
        self.main_gui.update_ui()

        self.data["report_window"].append_text(f"\n\n{'='*60}")
        self.data["report_window"].append_text(f"STARTING NEW RUN {self.logic.run_number}")
        self.data["report_window"].append_text(f"{'='*60}")

    def onDownloadSoftLandmarks(self):
        self.statusLabel.setText("Status: Downloading...")
        slicer.app.processEvents()

        base_name = self.data["soft_tissue_node_name"]
        nodeName = base_name
        counter = 2
        while slicer.util.getFirstNodeByName(nodeName):
            nodeName = f"{base_name}_{counter}"
            counter += 1

        try:
            with urllib.request.urlopen("https://github.com/user-attachments/files/22989771/Rynn_soft_tissue.mrk.json") as response, tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json', mode='wb') as tempFile:
                tempFile.write(response.read())
                tempFilePath = tempFile.name
            loadedNode = slicer.util.loadMarkups(tempFilePath)
            os.remove(tempFilePath)
            if loadedNode:
                loadedNode.SetName(nodeName)
                self.softTissueSelector.setCurrentNode(loadedNode)
                self.statusLabel.setText(f"✓ Status: Downloaded as '{nodeName}' and selected.")
                self.onEnterStep()
            else:
                raise IOError("Failed to load landmarks.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def _create_or_update_angle(self, name, p1, p2, p3, color, report_window):
        angle_node = slicer.util.getFirstNodeByName(name) or slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', name)
        angle_node.GetDisplayNode().SetColor(color)
        angle_node.RemoveAllControlPoints()
        angle_node.AddControlPoint(p1)
        angle_node.AddControlPoint(p2)
        angle_node.AddControlPoint(p3)
        return angle_node.GetAngleDegrees()

    def onBasicCompare(self):
        self.statusLabel.setText("Status: Running Basic Comparison...")
        slicer.app.processEvents()
        try:
            pred_node = slicer.util.getNode(f"soft_tissue_pred_{self.logic.run_number}")
            soft_node = self.softTissueSelector.currentNode()
            if not pred_node or not soft_node:
                raise ValueError("Prediction node or soft tissue node not selected.")

            for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
                if node.GetName().startswith("error_"):
                    slicer.mrmlScene.RemoveNode(node)

            pred_points = {"nasion": None, "pronasale": None, "subnasale": None}
            for i in range(pred_node.GetNumberOfControlPoints()):
                label = pred_node.GetNthControlPointLabel(i)
                pos = np.array(pred_node.GetNthControlPointPositionWorld(i))
                canonical = self.logic.get_landmark_canonical(label)
                if canonical and canonical in pred_points:
                    pred_points[canonical] = pos

            true_positions = {"nasion": None, "pronasale": None, "subnasale": None}
            for i in range(soft_node.GetNumberOfControlPoints()):
                label = soft_node.GetNthControlPointLabel(i)
                pos = np.array(soft_node.GetNthControlPointPositionWorld(i))
                canonical = self.logic.get_landmark_canonical(label)
                if canonical and canonical in true_positions:
                    true_positions[canonical] = pos

            error_lines_created = 0
            angles_created = 0

            # Predicted angle
            if all(v is not None for v in pred_points.values()):
                angle_val = self._create_or_update_angle(
                    f"Predicted_Nasal_Angle_Run{self.logic.run_number}",
                    pred_points["nasion"], pred_points["pronasale"], pred_points["subnasale"],
                    (1, 1, 0), self.data["report_window"]
                )
                std_id = self.logic.generate_standard_id("Angles", f"Predicted_Nasal_Angle_Run{self.logic.run_number}", "Predicted Angle", angle_val, "degrees")
                self.data["report_window"].store_result(
                    "Angles", f"Predicted_Nasal_Angle_Run{self.logic.run_number}",
                    "Predicted Angle", angle_val, "degrees",
                    std_id=std_id
                )
                angles_created += 1

            # True angle (store only once)
            if all(v is not None for v in true_positions.values()):
                true_angle_val = self._create_or_update_angle(
                    "True_Nasal_Angle",
                    true_positions["nasion"], true_positions["pronasale"], true_positions["subnasale"],
                    (0, 1, 1), self.data["report_window"]
                )
                if not self.data["report_window"].has_result("Angles", "True_Nasal_Angle"):
                    std_id_true = self.logic.generate_standard_id("Angles", "True_Nasal_Angle", "True Angle", true_angle_val, "degrees")
                    self.data["report_window"].store_result(
                        "Angles", "True_Nasal_Angle",
                        "True Angle", true_angle_val, "degrees",
                        std_id=std_id_true
                    )

            # Error lines
            for i in range(pred_node.GetNumberOfControlPoints()):
                pred_label = pred_node.GetNthControlPointLabel(i)
                pred_pos = np.array(pred_node.GetNthControlPointPositionWorld(i))
                canonical = self.logic.get_landmark_canonical(pred_label)
                if canonical and true_positions.get(canonical) is not None:
                    true_pos = true_positions[canonical]
                    error_dist = np.linalg.norm(pred_pos - true_pos)
                    self.logic.create_line(
                        f"error_{pred_label}",
                        pred_pos, true_pos,
                        color=(1, 0, 0),
                        use_run_number=False
                    )
                    error_lines_created += 1
                    std_id_err = self.logic.generate_standard_id("Basic Errors", f"error_{pred_label}", "Error Distance", error_dist, "mm")
                    self.data["report_window"].store_result(
                        "Basic Errors", f"error_{pred_label}", "Error Distance", error_dist, "mm",
                        std_id=std_id_err
                    )

            self.statusLabel.setText(
                f"✓ Status: Created {error_lines_created} error lines, {angles_created} angles."
            )
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")
            import traceback
            traceback.print_exc()

    def onRunProjection(self):
        self.statusLabel.setText("Status: Running projection network...")
        slicer.app.processEvents()
        try:
            hard_node = self.get_landmark_node()
            soft_node = self.softTissueSelector.currentNode()
            if not soft_node:
                raise ValueError("Soft tissue node not selected.")

            for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
                if node.GetName().startswith("n-pt") or " lat" in node.GetName() or " ant" in node.GetName() or " vert" in node.GetName() or node.GetName() in ["MAW", "MNW"]:
                    slicer.mrmlScene.RemoveNode(node)
            self.data['report_window'].results.pop("Projection Network", None)

            nasion_pos = self.logic.get_landmark_positions(hard_node, ["nasion"])["nasion"]
            point_map = {"pt1R": 3, "pt1L": 4, "pt2R": 5, "pt2L": 6, "pt3R": 7, "pt3L": 8, "pt4R": 9, "pt4L": 10, "pt5R": 11, "pt5L": 12, "pt6R": 13, "pt6L": 14, "pt7R": 15, "pt7L": 16, "pt8R": 17, "pt8L": 18}

            for name, index in point_map.items():
                soft_pos = np.array(soft_node.GetNthControlPointPositionWorld(index))
                line_node = self.logic.create_line(f"n-{name}", nasion_pos, soft_pos, color=(0.5, 0.5, 0.5), use_run_number=False)
                std_id = self.logic.generate_standard_id("Projection Network", line_node.GetName(), "Length", line_node.GetLineLengthWorld(), "mm")
                self.data['report_window'].store_result("Projection Network", line_node.GetName(), "Length", line_node.GetLineLengthWorld(), "mm", std_id=std_id)

                for plane_name_part in ["NPP", "PTP", "INB", "MSP"]:
                    plane_node = slicer.util.getFirstNodeByName(plane_name_part)
                    if not plane_node:
                        continue
                    suffix_map = {"NPP": "lat", "PTP": "ant", "INB": "vert", "MSP": "vert"}
                    suffix, color = suffix_map[plane_node.GetName()], plane_node.GetDisplayNode().GetColor()
                    plane_origin, plane_normal = np.array(plane_node.GetOrigin()), np.array(plane_node.GetNormal())

                    def project(p):
                        return p - np.dot(p - plane_origin, plane_normal) * plane_normal

                    line_node_proj = self.logic.create_line(f"{name} {suffix}", project(nasion_pos), project(soft_pos), color, use_run_number=False)
                    std_id_proj = self.logic.generate_standard_id("Projection Network", line_node_proj.GetName(), "Length", line_node_proj.GetLineLengthWorld(), "mm")
                    self.data['report_window'].store_result("Projection Network", line_node_proj.GetName(), "Length", line_node_proj.GetLineLengthWorld(), "mm", std_id=std_id_proj)

            self.logic.create_line("MAW", self.logic.get_landmark_positions(hard_node, ["XL"])["xl"], self.logic.get_landmark_positions(hard_node, ["XR"])["xr"], (1,0,1), use_run_number=False)
            self.logic.create_line("MNW", self.logic.get_landmark_positions(soft_node, ["pt6r"])["pt6r"], self.logic.get_landmark_positions(soft_node, ["pt6l"])["pt6l"], (1,0,1), use_run_number=False)

            # Store MAW and MNW lengths
            maw_node = slicer.util.getNode("MAW")
            if maw_node:
                maw_len = maw_node.GetLineLengthWorld()
                std_id_maw = self.logic.generate_standard_id("Projection Network", "MAW", "Length", maw_len, "mm")
                self.data['report_window'].store_result("Projection Network", "MAW", "Length", maw_len, "mm", std_id=std_id_maw)

            mnw_node = slicer.util.getNode("MNW")
            if mnw_node:
                mnw_len = mnw_node.GetLineLengthWorld()
                std_id_mnw = self.logic.generate_standard_id("Projection Network", "MNW", "Length", mnw_len, "mm")
                self.data['report_window'].store_result("Projection Network", "MNW", "Length", mnw_len, "mm", std_id=std_id_mnw)

            self.statusLabel.setText(f"✓ Status: Projection Network created successfully.")
            self.onEnterStep()
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")

    def onAdvancedCompare(self):
        self.statusLabel.setText("Status: Running Advanced Analysis...")
        slicer.app.processEvents()
        try:
            hard_node = self.get_landmark_node()
            soft_node = self.softTissueSelector.currentNode()
            if not soft_node:
                raise ValueError("Soft tissue node not selected.")

            if not slicer.util.getFirstNodeByName("MAW") or not slicer.util.getFirstNodeByName("MNW"):
                raise ValueError("MAW/MNW not found. Please run 'Create Rynn Projection Network' first.")

            for node in [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if n.GetName().startswith("adv_error_") or n.GetName() == "Shortest_MNW-MAW"]:
                slicer.mrmlScene.RemoveNode(node)
            self.data['report_window'].results.pop("Advanced Errors", None)

            pairs = [("pt5L", 12, "CL", 7, (1,0,0)), ("pt5R", 11, "CR", 8, (1,0,0)), ("pt7L", 16, "LL", 11, (0.13,0.55,0.13)), ("pt7R", 15, "LR", 12, (0.13,0.55,0.13)), ("pt4L", 10, "XL", 9, (0.13,0.55,0.13)), ("pt4R", 9, "XR", 10, (0.13,0.55,0.13))]

            for soft_label, soft_idx, hard_label_text, hard_idx, color in pairs:
                soft_pos, hard_pos = np.array(soft_node.GetNthControlPointPositionWorld(soft_idx)), np.array(hard_node.GetNthControlPointPositionWorld(hard_idx))
                line_name = f"adv_error_{soft_label}-{hard_label_text}"
                self.logic.create_line(line_name, hard_pos, soft_pos, color, use_run_number=False)
                displacement_len = np.linalg.norm(soft_pos - hard_pos)
                std_id = self.logic.generate_standard_id("Advanced Errors", line_name, "Length", displacement_len, "mm")
                self.data['report_window'].store_result("Advanced Errors", line_name, "Length", displacement_len, "mm", std_id=std_id)

            mnw, maw = slicer.util.getNode("MNW"), slicer.util.getNode("MAW")
            if mnw and maw:
                    p0,p1,q0,q1=np.array(mnw.GetNthControlPointPositionWorld(0)),np.array(mnw.GetNthControlPointPositionWorld(1)),np.array(maw.GetNthControlPointPositionWorld(0)),np.array(maw.GetNthControlPointPositionWorld(1))
                    u,v,w=p1-p0,q1-q0,p0-q0
                    a,b,c,d,e=np.dot(u,u),np.dot(u,v),np.dot(v,v),np.dot(u,w),np.dot(v,w)
                    den=a*c-b*b
                    sc,tc = ((b*e-c*d)/den,(a*e-b*d)/den) if den!=0 else (0,np.dot(-w,v)/c if c!=0 else 0)
                    pa, pb = p0+sc*u, q0+tc*v
                    dist = np.linalg.norm(pa - pb)
                    self.logic.create_line("Shortest_MNW-MAW",pa,pb,color=(0.13,0.55,0.13), use_run_number=False)
                    # Store under Projection Network, NOT Advanced Errors
                    std_id_short = self.logic.generate_standard_id("Projection Network", "Shortest_MNW-MAW", "Distance", dist, "mm")
                    self.data['report_window'].store_result("Projection Network", "Shortest_MNW-MAW", "Distance", dist, "mm", std_id=std_id_short)
                
            # ---- Additional hard tissue measurements (Projection Network) ----
            hard_map = {}
            for i in range(hard_node.GetNumberOfControlPoints()):
                label = hard_node.GetNthControlPointLabel(i)
                pos = np.array(hard_node.GetNthControlPointPositionWorld(i))
                hard_map[label] = pos

            lcil_pos = hard_map.get("LCIL")
            mcil_pos = hard_map.get("MCIL")
            lcir_pos = hard_map.get("LCIR")
            mcir_pos = hard_map.get("MCIR")
            icl_pos = hard_map.get("ICL")
            icr_pos = hard_map.get("ICR")

            if lcil_pos is not None and mcil_pos is not None:
                left_incisor_width = np.linalg.norm(lcil_pos - mcil_pos)
                # Create line in 3D
                self.logic.create_line("Left_Incisor_Width", lcil_pos, mcil_pos, color=(0.8, 0.2, 0.8), use_run_number=False)
                std_id = self.logic.generate_standard_id("Projection Network", "Left_Incisor_Width", "Distance", left_incisor_width, "mm")
                self.data['report_window'].store_result("Projection Network", "Left_Incisor_Width", "Distance", left_incisor_width, "mm", std_id=std_id)

            if lcir_pos is not None and mcir_pos is not None:
                right_incisor_width = np.linalg.norm(lcir_pos - mcir_pos)
                self.logic.create_line("Right_Incisor_Width", lcir_pos, mcir_pos, color=(0.8, 0.2, 0.8), use_run_number=False)
                std_id = self.logic.generate_standard_id("Projection Network", "Right_Incisor_Width", "Distance", right_incisor_width, "mm")
                self.data['report_window'].store_result("Projection Network", "Right_Incisor_Width", "Distance", right_incisor_width, "mm", std_id=std_id)

            if icl_pos is not None and icr_pos is not None:
                intercanine_width = np.linalg.norm(icl_pos - icr_pos)
                self.logic.create_line("Intercanine_Width", icl_pos, icr_pos, color=(0.9, 0.5, 0.1), use_run_number=False)
                std_id = self.logic.generate_standard_id("Projection Network", "Intercanine_Width", "Distance", intercanine_width, "mm")
                self.data['report_window'].store_result("Projection Network", "Intercanine_Width", "Distance", intercanine_width, "mm", std_id=std_id)
            self.statusLabel.setText("✓ Status: Advanced analysis complete.")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error! {e}")
            import traceback
            traceback.print_exc()

    def onToggleHelpers(self):
        nodes = (slicer.util.getNodesByClass("vtkMRMLMarkupsPlaneNode") +
                slicer.util.getNodesByClass("vtkMRMLMarkupsClosedCurveNode") +
                slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") +
                slicer.util.getNodesByClass("vtkMRMLMarkupsAngleNode"))
        if not nodes:
            self.statusLabel.setText("Status: No geometry found.")
            return
        first_node = next((n for n in nodes if n and n.GetDisplayNode()), None)
        if not first_node:
            return
        new_visibility = not first_node.GetDisplayNode().GetVisibility()
        for node in nodes:
            if node and node.GetDisplayNode():
                node.GetDisplayNode().SetVisibility(new_visibility)
        self.statusLabel.setText(f"Status: Geometry is now {'visible' if new_visibility else 'hidden'}.")

    def onToggleReport(self):
        if self.data["report_window"].isVisible():
            self.data["report_window"].hide()
        else:
            self.main_gui._repopulateReportFromScene()
            self.data["report_window"].show()

    # ----------------------------------------------------------------------
    # Comprehensive Results Table
    # ----------------------------------------------------------------------
    def onShowComprehensiveTable(self):
        results = self.data["report_window"].results
        if not results:
            qt.QMessageBox.information(self, "No Results", "No results found. Please run calculations first.")
            return

        all_items = []
        for category, items in results.items():
            if category in ["Basic Errors", "Advanced Errors"]:
                continue
            for item in items:
                all_items.append({
                    "category": category,
                    "id": item["id"],
                    "measurement": item["measurement"],
                    "value": item["value"],
                    "unit": item["unit"]
                })

        if not all_items:
            qt.QMessageBox.information(self, "No Data", "No results to display.")
            return

        dialog = qt.QDialog(self)
        dialog.setWindowTitle("Comprehensive Results Table")
        dialog.setMinimumSize(800, 500)
        layout = qt.QVBoxLayout(dialog)

        self.comprehensive_table = qt.QTableWidget()
        self.comprehensive_table.setColumnCount(4)
        self.comprehensive_table.setHorizontalHeaderLabels(["ID", "Measurement", "Value", "Unit"])
        self.comprehensive_table.setAlternatingRowColors(True)
        self.comprehensive_table.setSortingEnabled(True)
        self.comprehensive_table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

        self.comprehensive_table.setRowCount(len(all_items))
        for row, item in enumerate(all_items):
            self.comprehensive_table.setItem(row, 0, qt.QTableWidgetItem(item["id"]))
            self.comprehensive_table.setItem(row, 1, qt.QTableWidgetItem(item["measurement"]))
            val = item["value"]
            if isinstance(val, (float, np.floating)):
                val_str = f"{val:.2f}"
            else:
                val_str = str(val)
            self.comprehensive_table.setItem(row, 2, qt.QTableWidgetItem(val_str))
            self.comprehensive_table.setItem(row, 3, qt.QTableWidgetItem(item["unit"]))

        self.comprehensive_table.resizeColumnsToContents()
        self.comprehensive_table.setSortingEnabled(True)

        copy_btn = qt.QPushButton("Copy Table to Clipboard (TSV)")
        copy_btn.clicked.connect(self.copy_comprehensive_table)
        layout.addWidget(self.comprehensive_table)
        layout.addWidget(copy_btn)

        dialog.exec_()

    # ----------------------------------------------------------------------
    # Landmark Comparison Table
    # ----------------------------------------------------------------------
    def onShowLandmarkComparison(self):
        soft_node = self.softTissueSelector.currentNode()
        if not soft_node:
            qt.QMessageBox.warning(self, "Missing Data", "Please select a soft tissue node first.")
            return

        all_pred_nodes = []
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            if node.GetName().startswith("soft_tissue_pred_"):
                all_pred_nodes.append(node)

        def get_run_number(node):
            match = re.search(r'soft_tissue_pred_(\d+)', node.GetName())
            return int(match.group(1)) if match else 0

        all_pred_nodes.sort(key=get_run_number)

        if not all_pred_nodes:
            qt.QMessageBox.information(self, "No Predictions", "No prediction nodes found. Please run predictions first.")
            return

        true_dict = {}
        for i in range(soft_node.GetNumberOfControlPoints()):
            label = soft_node.GetNthControlPointLabel(i)
            pos = np.array(soft_node.GetNthControlPointPositionWorld(i))
            canonical = self.logic.get_landmark_canonical(label)
            if canonical:
                true_dict[canonical] = pos

        all_rows = []
        for pred_node in all_pred_nodes:
            run_name = pred_node.GetName()
            for i in range(pred_node.GetNumberOfControlPoints()):
                pred_label = pred_node.GetNthControlPointLabel(i)
                pred_pos = np.array(pred_node.GetNthControlPointPositionWorld(i))
                canonical = self.logic.get_landmark_canonical(pred_label)
                if canonical and canonical in true_dict:
                    true_pos = true_dict[canonical]
                    error = np.linalg.norm(pred_pos - true_pos)
                    all_rows.append({
                        "run": run_name,
                        "landmark": pred_label,
                        "pred_x": pred_pos[0], "pred_y": pred_pos[1], "pred_z": pred_pos[2],
                        "true_x": true_pos[0], "true_y": true_pos[1], "true_z": true_pos[2],
                        "error": error
                    })

        if not all_rows:
            qt.QMessageBox.information(self, "No Match", "No matching landmarks found between predicted and true nodes.")
            return

        dialog = qt.QDialog(self)
        dialog.setWindowTitle("Landmark Comparison – All Runs")
        dialog.setMinimumSize(1200, 600)
        layout = qt.QVBoxLayout(dialog)

        table1_label = qt.QLabel("<b>Predicted vs True Landmark Coordinates and Errors (All Runs)</b>")
        layout.addWidget(table1_label)

        self.landmark_table1 = qt.QTableWidget()
        self.landmark_table1.setColumnCount(9)
        self.landmark_table1.setHorizontalHeaderLabels(
            ["Run", "Landmark", "Pred X", "Pred Y", "Pred Z", "True X", "True Y", "True Z", "Error (mm)"]
        )
        self.landmark_table1.setAlternatingRowColors(True)
        self.landmark_table1.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

        self.landmark_table1.setRowCount(len(all_rows))
        for r, data in enumerate(all_rows):
            self.landmark_table1.setItem(r, 0, qt.QTableWidgetItem(data["run"]))
            self.landmark_table1.setItem(r, 1, qt.QTableWidgetItem(data["landmark"]))
            self.landmark_table1.setItem(r, 2, qt.QTableWidgetItem(f"{data['pred_x']:.2f}"))
            self.landmark_table1.setItem(r, 3, qt.QTableWidgetItem(f"{data['pred_y']:.2f}"))
            self.landmark_table1.setItem(r, 4, qt.QTableWidgetItem(f"{data['pred_z']:.2f}"))
            self.landmark_table1.setItem(r, 5, qt.QTableWidgetItem(f"{data['true_x']:.2f}"))
            self.landmark_table1.setItem(r, 6, qt.QTableWidgetItem(f"{data['true_y']:.2f}"))
            self.landmark_table1.setItem(r, 7, qt.QTableWidgetItem(f"{data['true_z']:.2f}"))
            err_item = qt.QTableWidgetItem(f"{data['error']:.2f}")
            err_item.setForeground(qt.QColor(200, 0, 0) if data['error'] > 5 else qt.QColor(0, 150, 0))
            self.landmark_table1.setItem(r, 8, err_item)

        self.landmark_table1.resizeColumnsToContents()
        layout.addWidget(self.landmark_table1)

        hard_node = self.get_landmark_node()
        adv_rows = []
        if hard_node and soft_node:
            hard_map = {}
            for i in range(hard_node.GetNumberOfControlPoints()):
                label = hard_node.GetNthControlPointLabel(i)
                pos = np.array(hard_node.GetNthControlPointPositionWorld(i))
                hard_map[label] = pos

            soft_map = {}
            for i in range(soft_node.GetNumberOfControlPoints()):
                label = soft_node.GetNthControlPointLabel(i)
                pos = np.array(soft_node.GetNthControlPointPositionWorld(i))
                soft_map[label] = pos

            adv_pairs = [
                ("pt5L", "CL"), ("pt5R", "CR"),
                ("pt7L", "LL"), ("pt7R", "LR"),
                ("pt4L", "XL"), ("pt4R", "XR"),
            ]

            for soft_label, hard_label in adv_pairs:
                if soft_label in soft_map and hard_label in hard_map:
                    soft_pos = soft_map[soft_label]
                    hard_pos = hard_map[hard_label]
                    error = np.linalg.norm(soft_pos - hard_pos)
                    adv_rows.append({
                        "pair": f"{soft_label}↔{hard_label}",
                        "hard_x": hard_pos[0], "hard_y": hard_pos[1], "hard_z": hard_pos[2],
                        "soft_x": soft_pos[0], "soft_y": soft_pos[1], "soft_z": soft_pos[2],
                        "error": error
                    })

        if adv_rows:
            table2_label = qt.QLabel("<b>Advanced Displacement Errors (Current Run – Hard ↔ Soft)</b>")
            layout.addWidget(table2_label)

            self.landmark_table2 = qt.QTableWidget()
            self.landmark_table2.setColumnCount(8)
            self.landmark_table2.setHorizontalHeaderLabels(
                ["Pair", "Hard X", "Hard Y", "Hard Z", "Soft X", "Soft Y", "Soft Z", "Error (mm)"]
            )
            self.landmark_table2.setAlternatingRowColors(True)
            self.landmark_table2.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

            self.landmark_table2.setRowCount(len(adv_rows))
            for r, data in enumerate(adv_rows):
                self.landmark_table2.setItem(r, 0, qt.QTableWidgetItem(data["pair"]))
                self.landmark_table2.setItem(r, 1, qt.QTableWidgetItem(f"{data['hard_x']:.2f}"))
                self.landmark_table2.setItem(r, 2, qt.QTableWidgetItem(f"{data['hard_y']:.2f}"))
                self.landmark_table2.setItem(r, 3, qt.QTableWidgetItem(f"{data['hard_z']:.2f}"))
                self.landmark_table2.setItem(r, 4, qt.QTableWidgetItem(f"{data['soft_x']:.2f}"))
                self.landmark_table2.setItem(r, 5, qt.QTableWidgetItem(f"{data['soft_y']:.2f}"))
                self.landmark_table2.setItem(r, 6, qt.QTableWidgetItem(f"{data['soft_z']:.2f}"))
                err_item = qt.QTableWidgetItem(f"{data['error']:.2f}")
                err_item.setForeground(qt.QColor(200, 0, 0) if data['error'] > 5 else qt.QColor(0, 150, 0))
                self.landmark_table2.setItem(r, 7, err_item)

            self.landmark_table2.resizeColumnsToContents()
            layout.addWidget(self.landmark_table2)
            self.landmark_table2 = self.landmark_table2
        else:
            self.landmark_table2 = None

        copy_layout = qt.QHBoxLayout()
        copy1 = qt.QPushButton("Copy Comparison Table (TSV)")
        copy1.clicked.connect(self.copy_landmark_table1)
        copy_layout.addWidget(copy1)

        if self.landmark_table2:
            copy2 = qt.QPushButton("Copy Advanced Errors (TSV)")
            copy2.clicked.connect(self.copy_landmark_table2)
            copy_layout.addWidget(copy2)

        copy_layout.addStretch()
        layout.addLayout(copy_layout)

        dialog.exec_()

# =============================================================================
# MAIN GUI
# =============================================================================
class RynnMethodSimplifiedGUI(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(qt.Qt.WindowStaysOnTopHint, True)
        self.setWindowTitle("Rynn (2010) Method - Simplified")
        self.setObjectName("RynnMethodSimplifiedGUI")

        self.mainLayout = qt.QVBoxLayout(self)
        self.logic = RynnMethodLogic()
        self.report_window = ReportWindow()
        self.data = {"report_window": self.report_window, "soft_tissue_node_name": "Rynn_soft_tissue"}

        self.manual_navigation = False

        self.run_label = qt.QLabel(f"<b>Current Run: {self.logic.run_number}</b>")
        self.run_label.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; font-size: 14px;")
        self.run_label.setAlignment(qt.Qt.AlignCenter)
        self.mainLayout.addWidget(self.run_label)

        self.step_widgets = []
        self.stepStack = qt.QStackedWidget()
        self.mainLayout.addWidget(self.stepStack)
        self.create_all_steps()
        self.setup_navigation()

        self.currentStep = 0
        self.update_ui()
        self._loadExistingNodeGuids()
        self._jumpToFirstIncompleteStep()
        self._repopulateReportFromScene()

    def updateRunLabel(self):
        self.run_label.setText(f"<b>Current Run: {self.logic.run_number}</b>")

    def create_all_steps(self):
        steps_to_add = [
            ("Step 1: Landmark Setup", Step1_LandmarkSetup),
            ("Step 2: Plane Setup", Step2_PlaneSetup),
            ("Step 3: Scaffolding", Step3_Scaffolding),
            ("Step 4: Pronasale Anterior", Step4_PronasaleAnterior),
            ("Step 5: Pronasale Vertical", Step5_PronasaleVertical),
            ("Step 6: pFHP", Step6_PFH),
            ("Step 7: Soft Tissue sn", Step7_SoftTissueSN),
            ("Step 8: Nasion Prediction", Step8_Nasion),
            ("Step 9: Analysis", Step9_Analysis)
        ]
        for title, TStep in steps_to_add:
            step_widget = TStep(title, self.logic, self.data, self)
            self.step_widgets.append(step_widget)
            self.stepStack.addWidget(step_widget)

    def get_selected_landmark_node(self):
        step1_widget = self.step_widgets[0]
        landmark_node = step1_widget.landmarksSelector.currentNode()
        if not landmark_node:
            raise ValueError("Please select a Landmark Node in Step 1 first.")
        return landmark_node

    def setup_navigation(self):
        nav_widget = qt.QWidget()
        nav_layout = qt.QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        self.prevButton = qt.QPushButton("Previous")
        self.prevButton.clicked.connect(self.on_prev_button_clicked)

        self.stepLabel = qt.QLabel("")
        self.stepLabel.setAlignment(qt.Qt.AlignCenter)
        self.stepLabel.setStyleSheet("font-weight: bold;")

        self.nextButton = qt.QPushButton("Next")
        self.nextButton.clicked.connect(self.on_next_button_clicked)

        nav_layout.addWidget(self.prevButton)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.stepLabel)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.nextButton)

        self.mainLayout.addWidget(nav_widget)

    def update_ui(self):
        self.stepStack.setCurrentIndex(self.currentStep)
        self.stepLabel.setText(f"Step {self.currentStep + 1} / {self.stepStack.count}")
        is_last_step = (self.currentStep == self.stepStack.count - 1)
        self.nextButton.setText("Finish" if is_last_step else "Next")
        self.prevButton.setEnabled(self.currentStep > 0)
        self.step_widgets[self.currentStep].onEnterStep()

    def on_prev_button_clicked(self):
        if self.currentStep > 0:
            self.manual_navigation = True
            self.currentStep -= 1
            self.update_ui()
            qt.QTimer.singleShot(500, lambda: setattr(self, 'manual_navigation', False))

    def on_next_button_clicked(self):
        self.manual_navigation = False
        if self.currentStep == self.stepStack.count - 1:
            self.report_window.close()
            self.close()
        else:
            self.currentStep += 1
            self.update_ui()

    def _loadExistingNodeGuids(self):
        profile_plane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
        if profile_plane:
            hard_id = profile_plane.GetAttribute("HardNodeID")
            if hard_id:
                self.logic.hard_node_guid = hard_id
            method = profile_plane.GetAttribute("PlaneMethod")
            if method:
                self.logic.plane_method = method

        x_axis = slicer.util.getFirstNodeByName("X_axis")
        if x_axis:
            hard_id = x_axis.GetAttribute("HardNodeID")
            if hard_id:
                self.logic.scaffold_node_guid = hard_id

    def _jumpToFirstIncompleteStep(self):
        step1 = self.step_widgets[0]
        current_node = step1.landmarksSelector.currentNode()
        if not current_node:
            self.currentStep = 0
            self.update_ui()
            return

        plane_exists = bool(slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP"))
        plane_ok = plane_exists and self.logic.hard_node_guid == current_node.GetID()

        axes_exist = bool(slicer.util.getFirstNodeByName("X_axis") and
                        slicer.util.getFirstNodeByName("Y_axis") and
                        slicer.util.getFirstNodeByName("Z_axis"))
        network_exist = bool(slicer.util.getFirstNodeByName("Line_1") and
                            slicer.util.getFirstNodeByName("Line_2") and
                            slicer.util.getFirstNodeByName("Line_3"))
        scaffold_ok = axes_exist and network_exist and self.logic.scaffold_node_guid == current_node.GetID()

        pred_node_name = f"soft_tissue_pred_{self.logic.run_number}"
        pred_node_exists = bool(slicer.util.getFirstNodeByName(pred_node_name))

        if plane_ok and scaffold_ok and pred_node_exists:
            self.currentStep = 8
        elif plane_ok and scaffold_ok:
            self.currentStep = 3
        elif plane_ok:
            self.currentStep = 2
        else:
            self.currentStep = 0

        self.update_ui()

    def _repopulateReportFromScene(self):
        report = self.report_window
        report.results = {}

        def get_line_length(node):
            if node.GetNumberOfControlPoints() >= 2:
                p1 = np.zeros(3); p2 = np.zeros(3)
                node.GetNthControlPointPositionWorld(0, p1)
                node.GetNthControlPointPositionWorld(1, p2)
                return np.linalg.norm(p2 - p1)
            return None

        # 1. Base Measurements
        for axis_name, prefix in [("X_axis", "X"), ("Y_axis", "Y"), ("Z_axis", "Z")]:
            axis = slicer.util.getFirstNodeByName(axis_name)
            if axis:
                attribs = axis.GetAttributeNames()
                for attr in attribs:
                    if attr.endswith(f"_{prefix}_length"):
                        run_str = attr.split('_')[0]
                        run_id = run_str[3:]
                        value = float(axis.GetAttribute(attr))
                        std_id = self.logic.generate_standard_id("Base Measurements", f"Run{run_id}_{prefix}", f"{prefix}-axis", value, "mm")
                        report.store_result("Base Measurements", f"Run{run_id}_{prefix}", f"{prefix}-axis", value, "mm", std_id=std_id)

        # 2. Lines: PA, PV, pFHP
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            name = node.GetName()
            if name.startswith(("PA_", "PV_", "pFHP_")):
                length = get_line_length(node)
                if length is not None:
                    eq_attr = node.GetAttribute("Equation")
                    # If we have an equation name, get its formula; otherwise use the raw name.
                    if eq_attr:
                        measurement = self.logic.equation_to_formula.get(eq_attr, eq_attr)
                    else:
                        measurement = name
                    if name.startswith("PA_"):
                        category = "PA"
                    elif name.startswith("PV_"):
                        category = "PV"
                    else:
                        category = "pFHP"
                    std_id = self.logic.generate_standard_id(category, name, measurement, length, "mm", equation=measurement if "pred" in measurement else None)
                    report.store_result(category, name, measurement, length, "mm", std_id=std_id)

        # 3. Circle radii
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsClosedCurveNode"):
            name = node.GetName()
            if name.startswith(("ND_circle", "NH_circle", "NL_circle")):
                radius_attr = node.GetAttribute("Radius")
                if radius_attr:
                    radius = float(radius_attr)
                    eq_attr = node.GetAttribute("Equation")
                    if eq_attr:
                        measurement = self.logic.equation_to_formula.get(eq_attr, eq_attr)    
                    else:
                        measurement = "Radius"
                    if name.startswith("ND_circle"):
                        category = "ND Radii"
                    elif name.startswith("NH_circle"):
                        category = "NH Radii"
                    else:
                        category = "NL Radii"
                    std_id = self.logic.generate_standard_id(category, name, measurement, radius, "mm", equation=measurement if "pred" in measurement else None)
                    report.store_result(category, name, measurement, radius, "mm", std_id=std_id)

        # 4. Angles
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsAngleNode"):
            name = node.GetName()
            if "Nasal_Angle" in name:
                angle_deg = node.GetAngleDegrees()
                if name.startswith("Predicted_Nasal_Angle"):
                    measurement = "Predicted Angle"
                elif name == "True_Nasal_Angle":
                    measurement = "True Angle"
                else:
                    measurement = "Angle"
                std_id = self.logic.generate_standard_id("Angles", name, measurement, angle_deg, "degrees")
                report.store_result("Angles", name, measurement, angle_deg, "degrees", std_id=std_id)

        # 5. Projection Network
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            name = node.GetName()
            if name.startswith("n-pt") or " lat" in name or " ant" in name or " vert" in name or name in ["MAW", "MNW", "Left_Incisor_Width", "Right_Incisor_Width", "Intercanine_Width"]:
                length = get_line_length(node)
                if length is not None:
                    std_id = self.logic.generate_standard_id("Projection Network", name, "Length", length, "mm")
                    report.store_result("Projection Network", name, "Length", length, "mm", std_id=std_id)

        # 6. Basic Errors
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            name = node.GetName()
            if name.startswith("error_"):
                length = get_line_length(node)
                if length is not None:
                    std_id = self.logic.generate_standard_id("Basic Errors", name, "Error Distance", length, "mm")
                    report.store_result("Basic Errors", name, "Error Distance", length, "mm", std_id=std_id)

        # 7. Advanced Errors
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            name = node.GetName()
            if name.startswith("adv_error_") or name == "Shortest_MNW-MAW":
                length = get_line_length(node)
                if length is not None:
                    if name == "Shortest_MNW-MAW":
                        measurement = "Distance"
                    else:
                        measurement = "Length"
                    std_id = self.logic.generate_standard_id("Advanced Errors", name, measurement, length, "mm")
                    report.store_result("Advanced Errors", name, measurement, length, "mm", std_id=std_id)

        report.append_text("\n--- Report repopulated from existing scene ---")

# =============================================================================
# ENTRY POINT
# =============================================================================

try:
    if 'rynnGui' in globals() and rynnGui is not None:
        if hasattr(rynnGui, 'report_window') and rynnGui.report_window is not None:
            rynnGui.report_window.close()
        rynnGui.close()
        rynnGui = None
except (NameError, AttributeError):
    pass

rynnGui = RynnMethodSimplifiedGUI()
rynnGui.show()
print(f"\n✅ Rynn Method GUI loaded successfully!")
print(f"✅ Current run number: {rynnGui.logic.run_number}")
print(f"✅ Ready to go!")



```
