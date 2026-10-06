# ==================================================================
# rstudio_export.py — Universal RStudio Export Wrapper
# ------------------------------------------------------------------
# Drop this file somewhere on your Python path (or the same folder
# as your GUI scripts) and add two lines to the top of each GUI:
#
#     import sys
#     sys.path.append(r"D:\001_PhD\Scripts")
#     from rstudio_export import install_export_button_for
#
# Then, in the last step of the GUI:
#
#     install_export_button_for(
#         gui=self,
#         parent_layout=some_layout,
#         method="TedeschiOliviera",   # or "auto" for detection
#     )
#
# The wrapper handles:
#   • Subject ID prompt (once per session, with code-version reference image)
#   • Code version prompt (once per session)
#   • Folder picker with persistence across Slicer sessions
#   • Appending to shared measurement.csv + RStudio.csv
#   • Method-specific pair/measurement providers for all ten GUIs
# ==================================================================

import os, csv, re, datetime
import numpy as np

try:
    import qt
    import slicer
except ImportError:
    qt = None
    slicer = None


# ------------------------------------------------------------------
#  Version-guide image — shown in the ID prompt dialog
# ------------------------------------------------------------------
CODE_VERSION_IMAGE_URL = (
    "https://github.com/esomjai/"
    "Forensic-Craniofacial-Approximation-Validation-Tool/raw/"
    "2b64cc450d409ad1dfc19e00d8c6062e4b284fee/"
    "Nose%20predictions/images/"
    "Screenshot%202026-10-06%20111753.png"
)


# ==================================================================
#  RStudioExporter — singleton
# ==================================================================
class RStudioExporter(object):

    STUDIO_HEADER = ["run_id", "subject_id", "method", "method_variant",
                     "code_version",
                     "landmark",
                     "pred_x", "pred_y", "pred_z",
                     "true_x", "true_y", "true_z",
                     "error_x", "error_y", "error_z", "error_3d"]
    MEAS_HEADER   = ["subject_id", "method", "method_variant",
                     "code_version",
                     "Measurement", "Value", "Unit"]

    def __init__(self):
        self._settings = qt.QSettings() if qt else None
        default = os.path.expanduser("~/slicer_errors")
        self.folder = default
        if self._settings:
            self.folder = self._settings.value(
                "RStudioExporter/folder", default)
        try:
            os.makedirs(self.folder, exist_ok=True)
        except Exception:
            pass
        self._subject_id = None
        self._code_version = None

    # ---------- paths ----------
    @property
    def studio_path(self):
        return os.path.join(self.folder, "RStudio.csv")

    @property
    def meas_path(self):
        return os.path.join(self.folder, "measurement.csv")

    # ---------- folder ----------
    def choose_folder(self, parent=None):
        if not qt:
            return self.folder
        chosen = qt.QFileDialog.getExistingDirectory(
            parent, "Choose export folder", self.folder)
        if chosen:
            self.folder = chosen
            if self._settings:
                self._settings.setValue("RStudioExporter/folder", chosen)
            try:
                os.makedirs(self.folder, exist_ok=True)
            except Exception:
                pass
        return self.folder

    # ---------- subject ID + code version ----------
    def prompt_identity(self, parent=None):
        """Single dialog that asks for subject ID and code version,
        showing the reference image for the version codes."""
        if self._subject_id and self._code_version:
            return self._subject_id, self._code_version
        if not qt:
            return None, None

        dialog = qt.QDialog(parent)
        dialog.setWindowTitle("Subject ID and Code Version")
        dialog.setMinimumWidth(520)

        layout = qt.QVBoxLayout(dialog)

        # --- reference image ---
        image_label = qt.QLabel()
        image_label.setAlignment(qt.Qt.AlignCenter)
        image_label.setText("Loading version reference image…")
        layout.addWidget(image_label)

        try:
            import urllib.request
            with urllib.request.urlopen(CODE_VERSION_IMAGE_URL,
                                        timeout=5) as r:
                data = r.read()
            pixmap = qt.QPixmap()
            pixmap.loadFromData(data)
            if not pixmap.isNull():
                max_w = 480
                if pixmap.width() > max_w:
                    pixmap = pixmap.scaledToWidth(
                        max_w, qt.Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setText("")
        except Exception as e:
            image_label.setText(
                f"[Could not load reference image]\n{e}\n\n"
                f"See: {CODE_VERSION_IMAGE_URL}")

        # --- form ---
        form = qt.QFormLayout()

        sid_edit = qt.QLineEdit()
        sid_edit.setPlaceholderText("e.g. 100749")
        if self._subject_id:
            sid_edit.setText(self._subject_id)
        form.addRow("Subject ID:", sid_edit)

        version_edit = qt.QLineEdit()
        version_edit.setPlaceholderText(
            "Enter the code version shown in the image above")
        if self._code_version:
            version_edit.setText(self._code_version)
        form.addRow("Code version:", version_edit)

        layout.addLayout(form)

        # --- buttons ---
        btn_box = qt.QDialogButtonBox(
            qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        if dialog.exec_() != qt.QDialog.Accepted:
            return None, None

        sid = sid_edit.text.strip()
        version = version_edit.text.strip()
        if not sid:
            slicer.util.warningDisplay("Subject ID is required.")
            return None, None

        self._subject_id = sid
        self._code_version = version or "unspecified"
        return self._subject_id, self._code_version

    def set_identity(self, sid, version):
        self._subject_id = sid
        self._code_version = version

    def get_identity(self):
        return self._subject_id, self._code_version

    # ---------- header management ----------
    def _ensure_header(self, path, header, aliases=None):
        """Create file with header, or migrate an existing file that has
        an older header missing 'code_version'."""
        aliases = aliases or {}
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", newline="") as f:
                csv.writer(f).writerow(header)
            return
        # check existing header
        with open(path, "r", newline="") as f:
            r = csv.reader(f)
            try:
                existing = next(r)
            except StopIteration:
                existing = []
        if existing == header:
            return
        # migration needed
        with open(path, "r", newline="") as f:
            rows = list(csv.reader(f))
        old_header = rows[0] if rows else []
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            for row in rows[1:]:
                new_row = []
                for col in header:
                    if col in old_header:
                        new_row.append(row[old_header.index(col)])
                    elif col == "code_version":
                        new_row.append("legacy")
                    else:
                        new_row.append("")
                w.writerow(new_row)

    # ---------- measurement.csv ----------
    def export_measurement(self, subject_id, method, variant,
                           code_version="unspecified",
                           extra_rows=None, table_widget=None):
        self._ensure_header(self.meas_path, self.MEAS_HEADER)

        rows = []
        if table_widget is not None:
            for r in range(table_widget.rowCount):
                row_values = []
                for c in range(table_widget.columnCount):
                    item = table_widget.item(r, c)
                    row_values.append(item.text() if item else "")
                if row_values:
                    name = row_values[0]
                    value = " | ".join(row_values[1:])
                    rows.append((name, value, ""))
        if extra_rows:
            rows.extend(extra_rows)

        with open(self.meas_path, "a", newline="") as f:
            w = csv.writer(f)
            for name, value, unit in rows:
                val = (f"{value:.4f}"
                       if isinstance(value, (int, float, np.floating))
                       else str(value))
                w.writerow([subject_id, method, variant, code_version,
                            name, val, unit])
        return len(rows)

    # ---------- RStudio.csv ----------
    def export_studio(self, subject_id, method, variant,
                      code_version="unspecified", pairs=None):
        self._ensure_header(self.studio_path, self.STUDIO_HEADER)
        n = 0
        with open(self.studio_path, "a", newline="") as f:
            w = csv.writer(f)
            for landmark, p, t in (pairs or []):
                p = np.asarray(p, dtype=float)
                t = np.asarray(t, dtype=float)
                ex, ey, ez = p - t
                e3 = float(np.sqrt(ex*ex + ey*ey + ez*ez))
                run_id = f"{subject_id}_{method}_{variant}"
                w.writerow([
                    run_id, subject_id, method, variant, code_version,
                    landmark,
                    f"{p[0]:.4f}", f"{p[1]:.4f}", f"{p[2]:.4f}",
                    f"{t[0]:.4f}", f"{t[1]:.4f}", f"{t[2]:.4f}",
                    f"{ex:.4f}", f"{ey:.4f}", f"{ez:.4f}", f"{e3:.4f}",
                ])
                n += 1
        return n


# ------------------------------------------------------------------
#  Singleton
# ------------------------------------------------------------------
_EXPORTER = None

def get_exporter():
    global _EXPORTER
    if _EXPORTER is None:
        _EXPORTER = RStudioExporter()
    return _EXPORTER


# ==================================================================
#  Pair providers — one per GUI
# ==================================================================
def _find_by_label(node, needles):
    if node is None:
        return None
    for i in range(node.GetNumberOfControlPoints()):
        low = node.GetNthControlPointLabel(i).lower()
        if any(n.lower() in low for n in needles):
            p = [0.0, 0.0, 0.0]
            node.GetNthControlPointPositionWorld(i, p)
            return p
    return None


def pairs_gerasimow():
    """Tangent-combo error lines + shortcut."""
    pattern = re.compile(r"error_(prn|R2)_(T\d-T\d)_pred_error", re.I)
    out = []
    for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
        m = pattern.match(n.GetName())
        if not m or n.GetNumberOfControlPoints() < 2:
            continue
        ref, combo = m.group(1), m.group(2)
        p = [0.0, 0.0, 0.0]; n.GetNthControlPointPositionWorld(1, p)
        t = [0.0, 0.0, 0.0]; n.GetNthControlPointPositionWorld(0, t)
        lm = "pronasale" if ref.lower() == "prn" else "R2"
        out.append((lm, p, t))
    sc = slicer.util.getFirstNodeByName("T1-T2_prediction_error")
    if sc and sc.GetNumberOfControlPoints() >= 2:
        p = [0.0, 0.0, 0.0]; sc.GetNthControlPointPositionWorld(1, p)
        t = [0.0, 0.0, 0.0]; sc.GetNthControlPointPositionWorld(0, t)
        out.append(("pronasale", p, t))
    return out


def pairs_tedeschi():
    pred = slicer.util.getFirstNodeByName("predicted_pronasale")
    true = slicer.util.getFirstNodeByName("Tedeschi_Oliviera_lmrks")
    if not pred or not true:
        return []
    p = [0.0, 0.0, 0.0]; pred.GetNthControlPointPositionWorld(0, p)
    t = _find_by_label(true, ["pronasale", "prn"])
    return [("pronasale", p, t)] if t else []


def pairs_stephan():
    pred = slicer.util.getFirstNodeByName("pronasale pred")
    true = (slicer.util.getFirstNodeByName("soft_tissue_Stephan") or
            slicer.util.getFirstNodeByName("Pronasale_Stephan") or
            slicer.util.getFirstNodeByName("F"))
    if not pred or not true:
        return []
    if pred.GetNumberOfControlPoints() == 0 or \
       true.GetNumberOfControlPoints() == 0:
        return []
    p = [0.0, 0.0, 0.0]; pred.GetNthControlPointPositionWorld(0, p)
    t = [0.0, 0.0, 0.0]; true.GetNthControlPointPositionWorld(0, t)
    return [("pronasale", p, t)]


def pairs_threefold():
    pred = slicer.util.getFirstNodeByName("predicted pronasale")
    true = slicer.util.getFirstNodeByName("KrogmanIscan_soft_tissue")
    if not pred or not true:
        return []
    p = [0.0, 0.0, 0.0]; pred.GetNthControlPointPositionWorld(0, p)
    t = _find_by_label(true, ["pronasale", "prn"])
    return [("pronasale", p, t)] if t else []


_THITIORUL_LM = ["se'", "npp'", "npa'", "pn'", "nd'", "sn'",
                 "al'L", "als'L", "alp'L", "ali'L",
                 "al'R", "als'R", "alp'R", "ali'R"]

def pairs_thitiorul():
    pred = slicer.util.getFirstNodeByName("Predicted_Thitiorul")
    true = slicer.util.getFirstNodeByName("true_Thitiorul_soft_tissue")
    if not pred or not true:
        return []
    out = []
    for lm in _THITIORUL_LM:
        p = _find_by_label(pred, [lm])
        t = _find_by_label(true, [lm])
        if p and t:
            out.append((lm, p, t))
    return out


_RYU_LM = ["S", "PN", "SN",
           "ACS_L", "ACP_L", "NA_L", "ACI_L",
           "ACS_R", "ACP_R", "NA_R", "ACI_R"]

def pairs_ryu():
    true = slicer.util.getFirstNodeByName("Ryu_soft_tissue")
    if not true:
        return []
    out = []
    for pn in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
        if "Predicted_Soft_Tissue" not in pn.GetName():
            continue
        for lm in _RYU_LM:
            p = _find_by_label(pn, [lm])
            t = _find_by_label(true, [lm])
            if p and t:
                out.append((lm, p, t))
    return out


_RYNN_MAP = {"pronasale": ["pronasale", "pn'", "pn"],
             "subnasale": ["subnasale", "sn'", "sn"],
             "nasion":    ["nasion", "n'", "n"]}

def pairs_rynn():
    true = slicer.util.getFirstNodeByName("Rynn_soft_tissue")
    if not true:
        return []
    out = []
    for pn in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
        if not pn.GetName().startswith("soft_tissue_pred_"):
            continue
        for canon, aliases in _RYNN_MAP.items():
            p = _find_by_label(pn, aliases)
            t = _find_by_label(true, aliases)
            if p and t:
                out.append((canon, p, t))
    return out


_RIDEL_MAP = {"pronasale": ["Pn_", "pn_"],
              "subnasale": ["Sn_", "sn_"],
              "alare_L":   ["AlL_", "al'l", "alare (left)"],
              "alare_R":   ["AlR_", "al'r", "alare (right)"]}

def pairs_ridel():
    true = slicer.util.getFirstNodeByName("Ridel_soft_tissue")
    if not true:
        return []
    out = []
    for pn in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
        if not pn.GetName().startswith("Pred_"):
            continue
        for canon, aliases in _RIDEL_MAP.items():
            p = _find_by_label(pn, aliases)
            t = _find_by_label(true, aliases)
            if p and t:
                out.append((canon, p, t))
    return out


def pairs_purkait():
    pred = slicer.util.getFirstNodeByName("lmrk_predictions")
    true = slicer.util.getFirstNodeByName("PS_soft_tissue")
    if not pred or not true:
        return []
    t = _find_by_label(true, ["prn", "pronasale"])
    if not t:
        return []
    out = []
    for i in range(pred.GetNumberOfControlPoints()):
        lbl = pred.GetNthControlPointLabel(i)
        if not lbl.lower().startswith("prn"):
            continue
        p = [0.0, 0.0, 0.0]
        pred.GetNthControlPointPositionWorld(i, p)
        out.append((lbl.replace("prn_", "").strip("_") or "pronasale",
                    p, t))
    return out


def pairs_prokopec():
    out = []
    pred_lines = {}
    for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
        m = re.match(r"pred soft nose outline (\d+)(.*)$", n.GetName())
        if m:
            pred_lines[int(m.group(1))] = (n, m.group(2))
    if pred_lines:
        suffix = next(iter(pred_lines.values()))[1]
        soft = slicer.util.getFirstNodeByName(
            f"nose_profile_outline{suffix}")
        n_planes = len(pred_lines)
        if soft:
            for pred_num, (pn, _) in sorted(pred_lines.items()):
                if pn.GetNumberOfControlPoints() < 2:
                    continue
                p = [0.0, 0.0, 0.0]
                pn.GetNthControlPointPositionWorld(1, p)
                true_idx = n_planes - pred_num
                if 0 <= true_idx < soft.GetNumberOfControlPoints():
                    t = [0.0, 0.0, 0.0]
                    soft.GetNthControlPointPositionWorld(true_idx, t)
                    out.append((f"outline_{true_idx+1}", p, t))
    # Stephan pair, if present
    pred = None
    for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
        if n.GetName().startswith("Stephan_pronasale"):
            pred = n; break
    true = slicer.util.getFirstNodeByName("Pronasale_Stephan")
    if pred and true and pred.GetNumberOfControlPoints() > 0 \
       and true.GetNumberOfControlPoints() > 0:
        p = [0.0, 0.0, 0.0]; pred.GetNthControlPointPositionWorld(0, p)
        t = [0.0, 0.0, 0.0]; true.GetNthControlPointPositionWorld(0, t)
        out.append(("pronasale", p, t))
    return out


PAIR_PROVIDERS = {
    "Gerasimow":         pairs_gerasimow,
    "TedeschiOliviera":  pairs_tedeschi,
    "Stephan":           pairs_stephan,
    "Threefold":         pairs_threefold,
    "Thitiorul":         pairs_thitiorul,
    "Ryu":               pairs_ryu,
    "Rynn":              pairs_rynn,
    "Ridel":             pairs_ridel,
    "PurkaitSingh":      pairs_purkait,
    "ProkopecUbelaker":  pairs_prokopec,
}


# ==================================================================
#  Button installer
# ==================================================================
def install_export_button_for(gui,
                              parent_layout,
                              method,
                              variant="auto",
                              table_widget=None,
                              measurement_provider=None,
                              button_label="Export for RStudio",
                              style=None):
    """
    Install a single 'Export for RStudio' button on any layout.

    Parameters
    ----------
    gui                : the GUI instance (used as dialog parent)
    parent_layout      : QLayout the button is added to
    method             : one of the keys in PAIR_PROVIDERS
    variant            : static str, or "auto" to derive from the scene
    table_widget       : optional QTableWidget dumped into measurement.csv
    measurement_provider: optional callable() -> [(name, value, unit), ...]
    button_label       : button caption
    style              : optional Qt stylesheet
    """
    if not qt:
        return None

    button = qt.QPushButton(button_label)
    button.setStyleSheet(
        style or
        "background-color: #E67E22; color: white; "
        "font-weight: bold; padding: 8px;")

    def on_click():
        ex = get_exporter()

        sid, version = ex.prompt_identity(gui)
        if not sid:
            return

        # confirm / change folder
        if qt.QMessageBox.question(
            gui, "Export folder",
            f"Export to:\n{ex.folder}\n\nChange folder?",
            qt.QMessageBox.Yes | qt.QMessageBox.No,
            qt.QMessageBox.No
        ) == qt.QMessageBox.Yes:
            ex.choose_folder(gui)

        # resolve variant
        resolved_variant = variant
        if variant == "auto":
            resolved_variant = _derive_variant(method)
        elif callable(variant):
            try:
                resolved_variant = variant()
            except Exception:
                resolved_variant = "auto"

        # gather rows
        pairs = []
        try:
            pairs = PAIR_PROVIDERS.get(method, lambda: [])()
        except Exception as e:
            print(f"pairs provider failed: {e}")

        measurement_rows = []
        if measurement_provider:
            try:
                measurement_rows = list(measurement_provider())
            except Exception as e:
                print(f"measurement provider failed: {e}")

        n_meas = ex.export_measurement(
            subject_id=sid, method=method, variant=resolved_variant,
            code_version=version,
            extra_rows=measurement_rows,
            table_widget=table_widget)
        n_studio = ex.export_studio(
            subject_id=sid, method=method, variant=resolved_variant,
            code_version=version, pairs=pairs)

        slicer.util.infoDisplay(
            f"Exported for subject {sid} (version {version}):\n"
            f"  measurement.csv → {n_meas} rows\n"
            f"  RStudio.csv     → {n_studio} rows\n\n"
            f"Folder: {ex.folder}")

    button.clicked.connect(on_click)
    parent_layout.addWidget(button)
    return button


def _derive_variant(method):
    """Auto-detect a sensible variant string from the loaded scene."""
    if method == "Stephan":
        if slicer.util.getFirstNodeByName("Pronasale_Stephan"):
            return "StandaloneGUI"
        return "EmbeddedStephan"
    if method == "ProkopecUbelaker":
        m = re.match(r"pred soft nose outline (\d+)",
                     next((n.GetName() for n in
                           slicer.util.getNodesByClass(
                               "vtkMRMLMarkupsLineNode")
                           if n.GetName().startswith(
                               "pred soft nose outline")),
                          ""))
        return f"{m.group(1)}p" if m else "unknown"
    if method == "TedeschiOliviera":
        msp = slicer.util.getFirstNodeByName("MSP")
        if msp and msp.GetAttribute("TedeschiPlaneMethod"):
            return "MSP_" + msp.GetAttribute(
                "TedeschiPlaneMethod").replace("-point", "pt")
        return "MSP_unknown"
    return "default"