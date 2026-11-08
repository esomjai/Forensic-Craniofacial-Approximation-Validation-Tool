# ==================================================================
# RStudio_wrapper.py — Per-session export with scene metadata
# ------------------------------------------------------------------
# One file per export:
#   YYYYMMDD_HHMMSS_<method>_<subject_id>_<region>.csv
#
# Two prompts per click:
#   1. Subject ID
#   2. DICOM source folder (optional — first time prompts for archive
#      root, remembers it, then tries to auto-locate <root>/<ID>/)
#   Then a session dialog (region, plane, patient/scan info,
#   auto-filled metadata, extras, notes)
#
# File layout:
#   key,value
#   # SESSION  (export info, subject, method, DICOM source)
#   # PATIENT  (age, sex, ancestry, stature, weight)
#   # ACQUISITION (scanner, exposure, geometry)
#   # SLICER
#   # SCENE CONTENTS
#   # VOLUME N
#   # MODEL N
#   # MARKUPS
#   # GUI STATE (optional, per-GUI)
#   # NOTES
#   # BEGIN_DATA
#   point_list,landmark,definition,role,R_A_S_X,R_A_S_Y,R_A_S_Z
#
# role is "true" | "pred" | "reference" | "hard_tissue" | "error" | "unknown"
# and is derived by _classify_role() from node name and landmark labels.
# Older CSVs (without the role column) are still readable by the R side.
# ==================================================================

import os, csv, re, datetime
import numpy as np

try:
    import qt
    import slicer
except ImportError:
    qt = None
    slicer = None

# Optional pydicom
try:
    import pydicom
    _PYDICOM_AVAILABLE = True
except ImportError:
    pydicom = None
    _PYDICOM_AVAILABLE = False


# ------------------------------------------------------------------
#  Version-reference image shown in the identity prompt
# ------------------------------------------------------------------
CODE_VERSION_IMAGE_URL = (
    "https://raw.githubusercontent.com/esomjai/"
    "Forensic-Craniofacial-Approximation-Validation-Tool/"
    "2b64cc450d409ad1dfc19e00d8c6062e4b284fee/"
    "Nose%20predictions/images/"
    "Screenshot%202026-10-06%20111753.png"
)

# Text used for fields that could not be retrieved automatically
FAILED_TAG = "(failed to retrieve from DICOM)"

# The tags the wrapper reads from DICOM
DICOM_TAG_MAP = {
    # Patient module
    "age":                          "PatientAge",
    "biological_sex_raw":           "PatientSex",
    "dicom_patient_id":             "PatientID",
    # General equipment
    "scan_Manufacturer":            "Manufacturer",
    "scan_Model":                   "ManufacturerModelName",
    "scan_Software":                "SoftwareVersions",
    "scan_InstitutionName":         "InstitutionName",
    "scan_StationName":             "StationName",
    "scan_InstitutionalDepartment": "InstitutionalDepartmentName",
    # Study / series
    "scan_StudyDescription":        "StudyDescription",
    "scan_SeriesDescription":       "SeriesDescription",
    "scan_ProtocolName":            "ProtocolName",
    "scan_StudyDate":               "StudyDate",
    "scan_StudyTime":               "StudyTime",
    "scan_AcquisitionTime":         "AcquisitionTime",
    "scan_Modality":                "Modality",
    "scan_StudyID":                 "StudyID",
    # Image geometry
    "scan_SliceThickness":          "SliceThickness",
    "scan_SpacingBetweenSlices":    "SpacingBetweenSlices",
    "scan_NumberofDetectorRows":    "Rows",
    "scan_NumberofDetectorColumns": "Columns",
    "scan_PatientPosition":         "PatientPosition",
    # Acquisition
    "scan_PeakTubeVoltage_kVp":     "KVP",
    "scan_XRayTubeCurrent":         "XRayTubeCurrent",
    "scan_Exposure":                "Exposure",
    "scan_ConvolutionKernel":       "ConvolutionKernel",
    "scan_FilterType":              "FilterType",
    "scan_ReconstructionDiameter":  "ReconstructionDiameter",
    "scan_DataCollectionDiameter":  "DataCollectionDiameter",
    "scan_ExposureModulationType":  "ExposureModulationType",
    "scan_CTDIvol":                 "CTDIvol",
    "scan_ScanOptions":             "ScanOptions",
    "scan_GantryDetectorTilt":      "GantryDetectorTilt",
    "scan_TableHeight":             "TableHeight",
    "scan_RotationDirection":       "RotationDirection",
}

# Nested-sequence tags (read from CTExposureSequence)
DICOM_NESTED_MAP = {
    "scan_RevolutionTime_Sec":         "RevolutionTime",
    "scan_SingleCollimationWidth":     "SingleCollimationWidth",
    "scan_TotalCollimationWidth":      "TotalCollimationWidth",
    "scan_SpiralPitchFactor":          "SpiralPitchFactor",
    "scan_ExposureTime_ms":            "ExposureTime",
}

# Markup node classes collected from the scene. Only fiducial nodes
# carry meaningful per-point labels, so non-fiducial classes are
# deliberately NOT exported (they'd produce rows with empty labels).
MARKUP_CLASSES = [
    "vtkMRMLMarkupsFiducialNode",
]


def _classify_role(node_name, landmark_labels=None):
    """Classify a markup node's role for validation analysis.

    Returns one of: "true", "pred", "reference", "hard_tissue",
                    "error", "unknown".

    Roles other than "true"/"pred" are excluded from the error tables
    downstream. Keep this in sync with the R-side fallback in
    validation_wrapper.R's `source = case_when(...)` block.
    """
    n = (node_name or "").lower()

    # ---- REFERENCE / HARD TISSUE / ERROR (excluded) ----
    if any(p in n for p in ("fhp", "frankfort", "reference", "npp", "ptp")):
        return "reference"
    if n.startswith("plane_") or n.endswith("_plane") or n in ("msp", "inb"):
        return "reference"
    if n in ("f", "nab point", "point x", "x_axis", "y_axis", "z_axis",
             "line_1", "line_2", "line_3", "subspinale-prosthion"):
        return "reference"
    if "hard_tissue" in n or "hardtissue" in n:
        return "hard_tissue"
    if n.startswith("bone"):
        return "hard_tissue"
    if n.startswith(("error_", "adv_error_", "pred error", "stephan_error")):
        return "error"
    if any(p in n for p in ("nasal_angle", "incisor_width",
                             "intercanine_width", "maw", "mnw",
                             "vmj-aca", "nasal spine vector", "fstt mp",
                             "pronasale_vector", "prediction_error",
                             "nd_circle", "nh_circle", "nl_circle")):
        return "reference"
    if n.startswith(("pa_", "pv_", "pfhp_",
                     "mirrora_", "mirrorb_", "nasal outline", "nasalbonetob")):
        return "reference"
    if n.startswith("nasal_bone_outline"):
        return "reference"
    if n.startswith("krogmaniscan_hard"):
        return "hard_tissue"

    # ---- PREDICTIONS (exact node names first) ----
    if n.startswith("predicted_soft_tissue"):                  return "pred"  # Ryu
    if n.startswith("soft_tissue_pred_"):                      return "pred"  # Rynn
    if n.startswith("pred_"):                                  return "pred"  # Ridel
    if n == "lmrk_predictions":                                return "pred"  # Purkait
    if n.startswith("pronasale_stephan"):                      return "pred"  # Stephan
    if n == "pronasale pred":                                  return "pred"  # Stephan (older)
    if n.startswith(("predicted_pronasale", "predicted_pro")): return "pred"  # Tedeschi
    if n == "predicted pronasale":                             return "pred"  # Threefold
    if n.startswith("stephan_pronasale"):                      return "pred"  # Prokopec

    # ---- TRUE (ground truth, exact node names) ----
    if n.startswith("lmrks_stephan"):                          return "true"  # Stephan hard-tissue
    if n.startswith("soft_tissue_stephan"):                    return "true"  # Stephan soft-tissue truth
    if n.endswith("_lmrks"):                                   return "true"  # Tedeschi
    if n == "krogmaniscan_soft_tissue":                        return "true"  # Threefold
    if n.startswith("ryu_soft_tissue"):                        return "true"  # Ryu
    if n.startswith("rynn_soft_tissue"):                       return "true"  # Rynn
    if n == "ridel_soft_tissue":                               return "true"  # Ridel
    if n == "ps_soft_tissue":                                  return "true"  # Purkait
    if n.startswith("nose_profile_outline"):                   return "true"  # Prokopec

    # ---- Generic fallbacks (Gerasimov, Thitiorul, future methods) ----
    if n.startswith("true"):                                   return "true"
    if n.startswith(("pred", "predicted")):                    return "pred"

    return "unknown"
# ==================================================================
#  Per-run detection
# ------------------------------------------------------------------
# Each method has a different convention for what constitutes a "run":
#
#   Ridel        — one run per Pred_<timestamp> or Pred_<timestamp>_cNN
#   Rynn         — one run per soft_tissue_pred_<N>
#   Ryu          — one run per Predicted_Soft_Tissue_<sex>_<timestamp>
#   Purkait      — one run per prn variant in lmrk_predictions
#   Gerasimov    — one run per <True|Predicted>_R2_<combo> (or T1-T2_shortcut)
#   Prokopec     — one run per <N>p suffix (5p, 6p, 7p, …)
#   Stephan, TedeschiOliviera, Thitiorul, Threefold
#                — single run ("default")
#
# Returns a list of (variant_name, {point_list -> filter mode}) tuples.
# Empty list means "no runs — don't write any files for this scene".
# ==================================================================

def _detect_runs(method):
    """Return a list of (variant_name, variant_meta) for the current scene.

    variant_meta is used by _collect_landmarks_for_variant to filter
    which rows of the CSV belong to this run.
    """
    method = (method or "").strip()

    # ---- Ridel: one file per Pred_<timestamp>[_cNN] node ----
    if method == "Ridel":
        runs = set()
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            n = node.GetName()
            if n.startswith("Pred_"):
                runs.add(n)
        return [(r, {"point_list_filter": r}) for r in sorted(runs)]

    # ---- Rynn: one file per soft_tissue_pred_<N> ----
    if method == "Rynn":
        runs = set()
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            import re
            m = re.match(r"soft_tissue_pred_(\d+)", node.GetName())
            if m:
                runs.add(f"run{m.group(1)}")
        return [(r, {"point_list_filter": f"soft_tissue_pred_{r[3:]}"})
                for r in sorted(runs)]

    # ---- Ryu: one file per Predicted_Soft_Tissue_<sex>_* ----
    if method == "Ryu":
        runs = set()
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            n = node.GetName()
            if "Predicted_Soft_Tissue" in n:
                if "Male" in n:   runs.add("Male")
                elif "Female" in n: runs.add("Female")
                else:             runs.add("Unknown")
        return [(s, {"point_list_filter_contains": f"Predicted_Soft_Tissue_{s}"})
                for s in sorted(runs)]

    # ---- PurkaitSingh: one file per prn variant ----
    if method == "PurkaitSingh":
        pred = slicer.util.getFirstNodeByName("lmrk_predictions")
        runs = set()
        if pred:
            for i in range(pred.GetNumberOfControlPoints()):
                lbl = pred.GetNthControlPointLabel(i)
                if lbl.lower().startswith("prn"):
                    variant = lbl.replace("prn_", "").strip("_") or "default"
                    runs.add(variant)
        return [(r, {"landmark_filter": r}) for r in sorted(runs)]

    # ---- Gerasimov: one file per T-combination ----
    if method == "Gerasimov" or method == "Gerasimov":
        runs = set()
        import re
        # Fiducial-based layout (True_R2_<combo>)
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            m = re.match(r"(?:True|Predicted)_R2_(T\d-T\d)", node.GetName())
            if m:
                runs.add(m.group(1))
        # Line-based layout (error_prn_<combo>_pred_error)
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            m = re.match(r"error_(?:prn|R2)_(T\d-T\d)_pred_error",
                         node.GetName())
            if m:
                runs.add(m.group(1))
        if slicer.util.getFirstNodeByName("T1-T2_prediction_error"):
            runs.add("T1-T2_shortcut")
        return [(c, {"Gerasimov_combo": c}) for c in sorted(runs)]

    # ---- Prokopec: one file per <N>p suffix ----
    if method == "ProkopecUbelaker":
        import re
        suffixes = set()
        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
            m = re.match(r"Stephan_pronasale_(\d+p)", node.GetName())
            if m:
                suffixes.add(m.group(1))
        # SkipScene: no prediction node → return empty list
        return [(s, {"prokopec_suffix": s}) for s in sorted(suffixes)]

    # ---- Everything else: single run ----
    return [("default", {})]
def _collect_landmarks_for_variant(all_landmarks, method, variant_meta):
    """Filter all_landmarks to only the rows that belong to this run/variant."""
    method = (method or "").strip()
    meta = variant_meta or {}

    # ---- Ridel / Rynn: exact point_list match + truth ----
    if method == "Ridel" and "point_list_filter" in meta:
        target = meta["point_list_filter"]
        return [r for r in all_landmarks
                if r["point_list"] == target
                or r["point_list"] == "Ridel_soft_tissue"]

    if method == "Rynn" and "point_list_filter" in meta:
        target = meta["point_list_filter"]
        return [r for r in all_landmarks
                if r["point_list"] == target
                or r["point_list"].startswith("Rynn_soft_tissue")]

    # ---- Ryu: substring match on the pred node + truth ----
    if method == "Ryu" and "point_list_filter_contains" in meta:
        needle = meta["point_list_filter_contains"]
        return [r for r in all_landmarks
                if (needle in r["point_list"])
                or r["point_list"] == "Ryu_soft_tissue"]

    # ---- Purkait: filter by landmark within lmrk_predictions + truth ----
    if method == "PurkaitSingh" and "landmark_filter" in meta:
        v = meta["landmark_filter"]
        return [r for r in all_landmarks
                if (r["point_list"] == "lmrk_predictions"
                    and v in r["landmark"])
                or r["point_list"] == "PS_soft_tissue"]

    # ---- Gerasimov: build per-variant truth + pred rows ----
    if (method in ("Gerasimov", "Gerasimov")) and "Gerasimov_combo" in meta:
        return _collect_Gerasimov_variant(all_landmarks,
                                          meta["Gerasimov_combo"])

    # ---- Prokopec: rename truth/pred labels for this suffix ----
    if method == "ProkopecUbelaker" and "prokopec_suffix" in meta:
        return _collect_prokopec_variant(all_landmarks,
                                         meta["prokopec_suffix"])

    # ---- Everything else: no filtering ----
    return all_landmarks


def _collect_Gerasimov_variant(all_landmarks, variant):
    """Extract truth+pred for one Gerasimov combination."""
    rows = []

    # Layout 1: True_R2_<combo> / Predicted_R2_<combo> fiducials
    if variant != "T1-T2_shortcut":
        for r in all_landmarks:
            pl = r["point_list"]
            if pl == f"True_R2_{variant}" or pl == f"Predicted_R2_{variant}":
                rows.append(r)
        if rows:
            return rows

    # Layout 2: error lines (prn/R2)
    for prefix, landmark in (("prn", "pronasale"), ("R2", "R2")):
        line_name = f"error_{prefix}_{variant}_pred_error"
        for r in all_landmarks:
            if r["point_list"] == line_name:
                rows.append(r)

    # Layout 3: shortcut
    if variant == "T1-T2_shortcut":
        for r in all_landmarks:
            pl = r["point_list"]
            if pl == "T1-T2_predicted_pronasale":
                rows.append({**r, "landmark": "pronasale"})
            elif pl == "Gerasimov_landmarks" and "pronasale" in r["landmark"].lower():
                rows.append(r)

    return rows


def _collect_prokopec_variant(all_landmarks, suffix):
    """Extract Prokopec rows for one <N>p suffix; rename truth/pred to pronasale."""
    rows = [r for r in all_landmarks if suffix in r["point_list"]]

    # Rename Stephan_pronasale_<N>p → pronasale
    for r in rows:
        if r["point_list"].startswith("Stephan_pronasale"):
            r = dict(r)          # copy so we don't mutate the original
            r["landmark"] = "pronasale"

    # Rename highest-numbered nose_profile_outline truth → pronasale
    truth_labels = [
        int(r["landmark"]) for r in rows
        if r["point_list"].startswith("nose_profile_outline")
        and r["landmark"].isdigit()
    ]
    highest = str(max(truth_labels)) if truth_labels else None

    out = []
    for r in rows:
        r = dict(r)
        if r["point_list"].startswith("Stephan_pronasale"):
            r["landmark"] = "pronasale"
        elif (r["point_list"].startswith("nose_profile_outline")
              and highest is not None
              and r["landmark"] == highest):
            r["landmark"] = "pronasale"
        out.append(r)
    return out
# ==================================================================
#  RStudioExporter
# ==================================================================
class RStudioExporter(object):

    def __init__(self):
        self._settings = qt.QSettings() if qt else None
        default = os.path.expanduser("~/slicer_exports")
        self.folder = default
        if self._settings:
            self.folder = self._settings.value(
                "RStudioExporter/folder", default)
        try:
            os.makedirs(self.folder, exist_ok=True)
        except Exception:
            pass
        self._subject_id = None

    # ----------------------------------------------------------
    #  Folder
    # ----------------------------------------------------------
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

    # ----------------------------------------------------------
    #  Top-level prompt flow
    # ----------------------------------------------------------
    def prompt_all(self, parent, method, scene_auto_plane):
        """
        Runs the two prompts plus the session dialog.
        Returns a session dict, or None.
        """
        sid = self._prompt_identity(parent)
        if not sid:
            return None

        dicom_info = self._prompt_dicom_folder(parent, sid)
        # dicom_info may be:
        #   {"status": "skipped"}                       — user skipped
        #   {"status": "matched", "folder": ..., "data": {...}}
        #   {"status": "anonymised", "folder": ..., "data": {...}}
        #   None                                        — user cancelled
        if dicom_info is None:
            return None

        session = self._prompt_session(
            parent, method, scene_auto_plane,
            prefill=dicom_info.get("data", {}))
        if session is None:
            return None

        session["subject_id"]         = sid
        session["method"]             = method
        session["dicom_folder"]       = dicom_info.get("folder", "")
        session["dicom_patient_id"]   = dicom_info.get("dicom_patient_id", "")
        session["dicom_match_status"] = dicom_info.get("status", "skipped")
        return session

    # ==========================================================
    #  Prompt 1 — identity (Subject ID only)
    # ==========================================================
    def _prompt_identity(self, parent):
        if self._subject_id:
            return self._subject_id
        if not qt:
            return None

        from qt import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                        QLabel, QLineEdit, QPixmap, Qt, QPushButton)

        dialog = QDialog(parent)
        dialog.setWindowTitle("Subject ID")
        dialog.setWindowFlags(
            dialog.windowFlags() | qt.Qt.WindowStaysOnTopHint)
        dialog.setMinimumSize(520, 280)
        dialog.resize(520, 320)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setText("Loading reference image...")
        layout.addWidget(image_label)

        try:
            import urllib.request
            with urllib.request.urlopen(CODE_VERSION_IMAGE_URL,
                                        timeout=8) as r:
                data = r.read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            if not pixmap.isNull():
                target_h = 180
                if pixmap.height() > target_h:
                    pixmap = pixmap.scaledToHeight(
                        target_h, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setText("")
        except Exception as e:
            image_label.setText(f"[Could not load reference image]\n{e}")

        form = QFormLayout()
        sid_edit = QLineEdit()
        sid_edit.setPlaceholderText("e.g. 100749")
        if self._subject_id:
            sid_edit.setText(self._subject_id)
        form.addRow("Subject ID:", sid_edit)
        layout.addLayout(form)

        row = QHBoxLayout()
        row.addStretch(1)
        cancel_btn = QPushButton("Cancel")
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 6px 20px;")
        cancel_btn.setStyleSheet("padding: 6px 20px;")
        row.addWidget(cancel_btn)
        row.addWidget(ok_btn)
        layout.addLayout(row)

        accepted = {"v": False}
        ok_btn.clicked.connect(
            lambda: (accepted.update(v=True), dialog.accept()))
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()

        if not accepted["v"]:
            return None
        sid = sid_edit.text.strip()
        if not sid:
            slicer.util.warningDisplay("Subject ID is required.")
            return None
        self._subject_id = sid
        return self._subject_id

    # ==========================================================
    #  Prompt 2 — DICOM source folder
    # ==========================================================
    def _prompt_dicom_folder(self, parent, subject_id):
        """
        Asks for the DICOM folder. On the first use ever, also asks
        for a "DICOM archive root" that is remembered for future runs.
        Returns:
            None                      → user cancelled the whole export
            {"status": "skipped"}     → user skipped DICOM
            {"status": "matched", ...} or
            {"status": "anonymised", ...} → folder chosen & read
        """
        if not qt or not _PYDICOM_AVAILABLE:
            # No way to read DICOM — skip silently
            return {"status": "skipped"}

        from qt import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                        QLineEdit, QPushButton, QMessageBox)

        archive_root = ""
        if self._settings:
            archive_root = self._settings.value(
                "RStudioExporter/dicom_archive_root", "")

        # ---------- First-use prompt for archive root ----------
        if not archive_root:
            root, ok = qt.QInputDialog.getText(
                parent,
                "Set DICOM archive root",
                "Enter the folder where all subject DICOM archives live.\n\n"
                "The wrapper will look for a subfolder named after the "
                "subject ID inside this root on every export.\n\n"
                "You can leave this blank and pick folders manually each time.",
                text="")
            if ok and root.strip():
                archive_root = root.strip()
                if self._settings:
                    self._settings.setValue(
                        "RStudioExporter/dicom_archive_root", archive_root)
            else:
                archive_root = ""

        # ---------- Try auto-locate: <root>/<subject_id> ----------
        auto_folder = ""
        if archive_root and subject_id:
            candidate = os.path.join(archive_root, subject_id)
            if os.path.isdir(candidate):
                auto_folder = candidate

        # ---------- Build the folder-picker dialog ----------
        dialog = QDialog(parent)
        dialog.setWindowTitle("DICOM source folder")
        dialog.setWindowFlags(
            dialog.windowFlags() | qt.Qt.WindowStaysOnTopHint)
        dialog.setMinimumWidth(560)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        info = QLabel(
            "Point at the folder containing the original DICOM files "
            "for this subject.\n\n"
            "The wrapper will read acquisition metadata (scanner, "
            "exposure, slice thickness, patient demographics) and "
            "write it into the export file. If the folder cannot be "
            "found, click Skip and fill the values manually.")
        info.setWordWrap(True)
        layout.addWidget(info)

        folder_edit = QLineEdit()
        folder_edit.setPlaceholderText("Path to DICOM folder")
        if auto_folder:
            folder_edit.setText(auto_folder)
        layout.addWidget(folder_edit)

        browse_row = QHBoxLayout()
        browse_row.addStretch(1)
        browse_btn = QPushButton("Browse...")
        browse_row.addWidget(browse_btn)
        layout.addLayout(browse_row)

        # ---------- Buttons ----------
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("Cancel")
        skip_btn = QPushButton("Skip DICOM")
        ok_btn = QPushButton("Continue")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 6px 20px;")
        cancel_btn.setStyleSheet("padding: 6px 20px;")
        skip_btn.setStyleSheet("padding: 6px 20px;")
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(skip_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        result = {"choice": None, "folder": ""}

        def do_browse():
            chosen = qt.QFileDialog.getExistingDirectory(
                dialog, "Choose DICOM folder", folder_edit.text or "")
            if chosen:
                folder_edit.setText(chosen)

        def do_skip():
            result["choice"] = "skip"
            dialog.accept()

        def do_ok():
            result["choice"] = "ok"
            result["folder"] = folder_edit.text.strip()
            dialog.accept()

        browse_btn.clicked.connect(do_browse)
        skip_btn.clicked.connect(do_skip)
        ok_btn.clicked.connect(do_ok)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec_()

        if result["choice"] == "skip":
            return {"status": "skipped"}
        if result["choice"] != "ok":
            return None    # cancelled

        folder = result["folder"]
        if not folder or not os.path.isdir(folder):
            slicer.util.warningDisplay(
                "Folder does not exist. Skipping DICOM metadata.")
            return {"status": "skipped"}

        # ---------- Read the folder ----------
        data = self._read_dicom_folder(folder)
        if not data:
            slicer.util.warningDisplay(
                "No readable DICOM files found. Skipping metadata.")
            return {"status": "skipped"}

        # ---------- Check ID match ----------
        dicom_id = data.get("dicom_patient_id", "")
        if dicom_id and dicom_id.strip() != subject_id.strip():
            reply = QMessageBox(dialog)
            reply.setWindowTitle("Subject ID mismatch")
            reply.setIcon(QMessageBox.Warning)
            reply.setWindowFlags(
                reply.windowFlags() | qt.Qt.WindowStaysOnTopHint)
            reply.setText(
                f"You entered:      {subject_id}\n"
                f"DICOM PatientID:  {dicom_id}\n\n"
                "The DICOM appears anonymised. Use the DICOM "
                "metadata anyway?")
            use_btn = reply.addButton("Use DICOM",
                                      QMessageBox.AcceptRole)
            skip2_btn = reply.addButton("Skip DICOM",
                                        QMessageBox.RejectRole)
            reply.setDefaultButton(use_btn)
            reply.exec_()
            if reply.clickedButton() == skip2_btn:
                return {"status": "skipped"}
            status = "anonymised"
        else:
            status = "matched"

        return {
            "status": status,
            "folder": folder,
            "dicom_patient_id": dicom_id,
            "data": data,
        }

    # ----------------------------------------------------------
    #  DICOM folder reader
    # ----------------------------------------------------------
    def _read_dicom_folder(self, folder_path):
        """
        Walk the folder tree, find the first valid .dcm file, and
        read every tag we care about. Returns {} on any failure.
        """
        if not _PYDICOM_AVAILABLE:
            return {}
        if not os.path.isdir(folder_path):
            return {}

        # ---- Find first valid DICOM ----
        first_dcm = None
        slice_count = 0
        for root, _, files in os.walk(folder_path):
            for fn in files:
                full = os.path.join(root, fn)
                try:
                    with open(full, "rb") as f:
                        f.seek(128)
                        if f.read(4) == b"DICM":
                            slice_count += 1
                            if first_dcm is None:
                                first_dcm = full
                except Exception:
                    continue

        if not first_dcm:
            return {}

        try:
            ds = pydicom.dcmread(first_dcm, stop_before_pixels=True)
        except Exception as e:
            print(f"[dicom] could not read {first_dcm}: {e}")
            return {}

        out = {}
        for wrapper_field, dicom_attr in DICOM_TAG_MAP.items():
            v = getattr(ds, dicom_attr, None)
            if v is not None and str(v).strip():
                out[wrapper_field] = str(v).strip()

        # Nested
        ct_exp = getattr(ds, "CTExposureSequence", None)
        if ct_exp and len(ct_exp) > 0:
            seq0 = ct_exp[0]
            for wrapper_field, dicom_attr in DICOM_NESTED_MAP.items():
                v = getattr(seq0, dicom_attr, None)
                if v is not None and str(v).strip():
                    out[wrapper_field] = str(v).strip()

        # Normalise sex
        raw = out.pop("biological_sex_raw", "")
        if raw:
            r = raw.upper()
            if r in ("M", "MALE"):
                out["biological_sex"] = "Male"
            elif r in ("F", "FEMALE"):
                out["biological_sex"] = "Female"
            else:
                out["biological_sex"] = "Other"

        # Slice count
        if slice_count > 0:
            out["scan_NumberofSlices"] = str(slice_count)

        # Pixel spacing
        ps = getattr(ds, "PixelSpacing", None)
        if ps and len(ps) == 2:
            out["scan_PixelSpacing"] = f"{float(ps[0]):.4f} x {float(ps[1]):.4f}"

        return out

    # ==========================================================
    #  Prompt 3 — session details
    # ==========================================================
    def _prompt_session(self, parent, method, scene_auto_plane, prefill):
        if not qt:
            return None

        from qt import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                        QLabel, QLineEdit, QComboBox, QPushButton,
                        QGroupBox, QScrollArea, QWidget, QTextEdit)

        dialog = QDialog(parent)
        dialog.setWindowTitle(f"Export details — {method}")
        dialog.setWindowFlags(
            dialog.windowFlags() | qt.Qt.WindowStaysOnTopHint)
        dialog.setMinimumSize(640, 700)
        dialog.resize(680, 800)

        outer = QVBoxLayout(dialog)
        outer.setSpacing(10)
        outer.setContentsMargins(15, 15, 15, 15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        # ============ Section A ============
        grpA = QGroupBox("A. Session details (required)")
        formA = QFormLayout(grpA)

        region_combo = QComboBox()
        region_combo.addItems(["", "Nose", "Eye", "Mouth", "FSTT"])
        formA.addRow("Region:", region_combo)

        plane_combo = QComboBox()
        plane_combo.addItems(["", "INB", "MSP", "MSP-3pt", "MSP-5pt",
                              "None", "Other"])
        if scene_auto_plane in ("INB", "MSP", "MSP-3pt", "MSP-5pt"):
            plane_combo.setCurrentText(scene_auto_plane)
        formA.addRow("Plane method:", plane_combo)

        position_combo = QComboBox()
        position_combo.addItems(["", "Supine", "Upright"])
        formA.addRow("Patient position:", position_combo)

        scan_combo = QComboBox()
        scan_combo.addItems(["", "CT", "CBCT", "PMCT"])
        formA.addRow("Scan type:", scan_combo)

        ptype_combo = QComboBox()
        ptype_combo.addItems(["", "Living", "Deceased"])
        formA.addRow("Patient type:", ptype_combo)

        layout.addWidget(grpA)

        # ============ Section B ============
        grpB = QGroupBox(
            "B. Scan & patient metadata "
            "(auto-filled from DICOM; edit if needed)")
        formB = QFormLayout(grpB)

        field_specs = [
            ("age",                        "Age:"),
            ("biological_sex",             "Biological sex:"),
            ("Stature_cm",                 "Stature (cm):"),
            ("Weight_kg",                  "Weight (kg):"),
            ("scan_Manufacturer",          "Scanner manufacturer:"),
            ("scan_Model",                 "Scanner model:"),
            ("scan_Software",              "Scanner software:"),
            ("scan_SliceThickness",        "Slice thickness (mm):"),
            ("scan_NumberofSlices",        "Number of slices:"),
            ("scan_NumberofDetectorRows",  "Detector rows:"),
            ("scan_NumberofDetectorColumns","Detector columns:"),
            ("scan_PeakTubeVoltage_kVp",   "Peak tube voltage (kVp):"),
            ("scan_RevolutionTime_Sec",    "Revolution time (s):"),
            ("scan_SingleCollimationWidth","Single collimation width (mm):"),
            ("scan_TotalCollimationWidth", "Total collimation width (mm):"),
            ("scan_SpiralPitchFactor",     "Spiral pitch factor:"),
        ]
        b_fields = {}
        for key, label in field_specs:
            edit = QLineEdit()
            if key in prefill and prefill[key]:
                edit.setText(prefill[key])
            else:
                edit.setText(FAILED_TAG)
            formB.addRow(label, edit)
            b_fields[key] = edit

        layout.addWidget(grpB)

        # ============ Section C ============
        grpC = QGroupBox("C. Additional information")
        formC = QFormLayout(grpC)

        stature_type_edit = QLineEdit()
        stature_type_edit.setPlaceholderText("measured / estimated")
        formC.addRow("Stature type:", stature_type_edit)

        weight_type_edit = QLineEdit()
        weight_type_edit.setPlaceholderText("measured / estimated")
        formC.addRow("Weight type:", weight_type_edit)

        ancestry_edit = QLineEdit()
        ancestry_edit.setPlaceholderText(
            "e.g. White South African, Black South African, Turkish")
        formC.addRow("Ancestry:", ancestry_edit)

        ancestry_type_combo = QComboBox()
        ancestry_type_combo.addItems(["", "self_declared",
                                      "next_of_kin", "by_practitioner"])
        formC.addRow("Ancestry by:", ancestry_type_combo)

        notes_edit = QTextEdit()
        notes_edit.setPlaceholderText(
            "e.g. inion not allocated as scanning area excluded it; "
            "dental filling obscuring prosthion landmark")
        notes_edit.setMaximumHeight(80)
        formC.addRow("Notes:", notes_edit)

        layout.addWidget(grpC)
        layout.addStretch(1)

        # ============ Buttons ============
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("Cancel")
        ok_btn = QPushButton("Export")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 6px 24px;")
        cancel_btn.setStyleSheet("padding: 6px 24px;")
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        outer.addLayout(btn_row)

        accepted = {"v": False}
        ok_btn.clicked.connect(
            lambda: (accepted.update(v=True), dialog.accept()))
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()

        if not accepted["v"]:
            return None

        # Validate required
        missing = []
        if not region_combo.currentText.strip():
            missing.append("Region")
        if not plane_combo.currentText.strip():
            missing.append("Plane method")
        if not position_combo.currentText.strip():
            missing.append("Patient position")
        if not scan_combo.currentText.strip():
            missing.append("Scan type")
        if not ptype_combo.currentText.strip():
            missing.append("Patient type")
        if missing:
            slicer.util.warningDisplay(
                "Please fill the following required fields:\n  " +
                "\n  ".join(missing))
            return None

        session = {
            "region": region_combo.currentText.strip(),
            "plane_method": plane_combo.currentText.strip(),
            "patient_position": position_combo.currentText.strip(),
            "scan_type": scan_combo.currentText.strip(),
            "patient_type": ptype_combo.currentText.strip(),
            "stature_type": stature_type_edit.text.strip(),
            "weight_type": weight_type_edit.text.strip(),
            "ancestry": ancestry_edit.text.strip(),
            "ancestry_type": ancestry_type_combo.currentText.strip(),
            "notes": notes_edit.toPlainText().strip(),
        }
        for key, edit in b_fields.items():
            session[key] = edit.text().strip()
        return session

    # ==========================================================
    #  Scene metadata
    # ==========================================================
    def _collect_scene_metadata(self):
        out = {}
        try:
            out["slicer_version"] = slicer.app.applicationVersion
            out["slicer_revision"] = slicer.app.applicationRevision
        except Exception:
            pass
        try:
            out["scene_node_count"] = slicer.mrmlScene.GetNumberOfNodes()
        except Exception:
            pass
        try:
            out["markup_nodes"] = len(
                slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"))
            out["model_nodes"] = len(
                slicer.util.getNodesByClass("vtkMRMLModelNode"))
            out["volume_nodes"] = len(
                slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"))
            out["transform_nodes"] = len(
                slicer.util.getNodesByClass("vtkMRMLTransformNode"))
        except Exception:
            pass
        return out

    # ==========================================================
    #  Plane method detection
    # ==========================================================
    def _detect_plane_method(self):
        try:
            planes = slicer.util.getNodesByClass("vtkMRMLMarkupsPlaneNode")
        except Exception:
            planes = []
        for p in planes:
            for attr in ("PlaneMethod", "TedeschiPlaneMethod"):
                try:
                    v = p.GetAttribute(attr)
                    if v:
                        v_low = v.lower()
                        if "3" in v_low or "three" in v_low:
                            return "MSP-3pt"
                        if "5" in v_low or "five" in v_low:
                            return "MSP-5pt"
                        if "inb" in v_low:
                            return "INB"
                        if "msp" in v_low:
                            return "MSP"
                        return v
                except Exception:
                    pass
        for name in ("INB", "MSP"):
            try:
                if slicer.util.getFirstNodeByName(name):
                    return name
            except Exception:
                pass
        return ""

    # ==========================================================
    #  Landmarks
    # ==========================================================
    def _collect_landmarks(self):
        rows = []
        all_nodes = []
        for class_name in MARKUP_CLASSES:
            try:
                all_nodes.extend(slicer.util.getNodesByClass(class_name))
            except Exception:
                pass

        for node in all_nodes:
            try:
                node_name = node.GetName()
                n_points  = node.GetNumberOfControlPoints()
            except Exception:
                continue
            if n_points == 0:
                continue

            labels = []
            for i in range(n_points):
                try:
                    labels.append(node.GetNthControlPointLabel(i) or "")
                except Exception:
                    labels.append("")

            node_role = _classify_role(node_name, labels)

            for i in range(n_points):
                p = [0.0, 0.0, 0.0]
                try:
                    node.GetNthControlPointPositionWorld(i, p)
                except Exception:
                    continue
                try:
                    description = node.GetNthControlPointDescription(i) or ""
                except Exception:
                    description = ""
                rows.append({
                    "point_list": node_name,
                    "landmark":   labels[i],
                    "definition": description,
                    "role":       node_role,
                    "R": p[0], "A": p[1], "S": p[2],
                })
        return rows

    def _pick_primary_volume(self):
        try:
            vols = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
        except Exception:
            return None
        for vol in vols:
            n = vol.GetName().lower()
            if n.endswith("_seg") or "label" in n:
                continue
            return vol
        return vols[0] if vols else None

    # ==========================================================
    #  Write file
    # ==========================================================
    def write_session_file(self, method, subject_id, session, extra_meta=None,
                           variant=None, landmark_rows=None):
        """Write one CSV for one run.

        Parameters
        ----------
        method : str
        subject_id : str
        session : dict   (metadata from prompt_all)
        extra_meta : dict or None  (per-GUI extras)
        variant : str or None      (e.g. "Pred_20260914_125422", "run0", "Male")
        landmark_rows : list or None
            Pre-filtered landmark rows for this variant.
            If None, all fiducials are written (single-run mode).
        """
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        region = session.get("region", "unknown")

        safe_method  = re.sub(r"[^A-Za-z0-9_-]", "_", method)
        safe_id      = re.sub(r"[^A-Za-z0-9_-]", "_", subject_id)
        safe_region  = re.sub(r"[^A-Za-z0-9_-]", "_", region)
        safe_variant = re.sub(r"[^A-Za-z0-9_-]", "_",
                              variant if variant else "default")

        # ---- Per-method folder + per-run filename ----
        filename = (f"{stamp}_{safe_method}_{safe_id}_{safe_region}"
                    f"_{safe_variant}.csv")
        method_folder = os.path.join(self.folder, safe_method)
        os.makedirs(method_folder, exist_ok=True)
        path = os.path.join(method_folder, filename)

        # ---- Metadata (same as before) ----
        meta_rows = []
        meta_rows.append(("# SESSION", ""))
        meta_rows.append(("export_datetime",
                          datetime.datetime.now().isoformat(timespec="seconds")))
        meta_rows.append(("method", method))
        meta_rows.append(("variant", variant or "default"))
        meta_rows.append(("region", session.get("region", "")))
        meta_rows.append(("plane_method", session.get("plane_method", "")))
        meta_rows.append(("subject_id", subject_id))
        meta_rows.append(("dicom_folder", session.get("dicom_folder", "")))
        meta_rows.append(("dicom_patient_id", session.get("dicom_patient_id", "")))
        meta_rows.append(("dicom_match_status", session.get("dicom_match_status", "")))
        meta_rows.append(("patient_position", session.get("patient_position", "")))
        meta_rows.append(("scan_type", session.get("scan_type", "")))
        meta_rows.append(("patient_type", session.get("patient_type", "")))

        meta_rows.append(("# PATIENT", ""))
        for k in ("age", "biological_sex", "ancestry", "ancestry_type",
                  "Stature_cm", "stature_type", "Weight_kg", "weight_type"):
            meta_rows.append((k, session.get(k, "")))

        meta_rows.append(("# ACQUISITION", ""))
        for k in ("scan_Manufacturer", "scan_Model", "scan_Software",
                  "scan_SliceThickness", "scan_NumberofSlices",
                  "scan_NumberofDetectorRows", "scan_NumberofDetectorColumns",
                  "scan_PeakTubeVoltage_kVp", "scan_RevolutionTime_Sec",
                  "scan_SingleCollimationWidth", "scan_TotalCollimationWidth",
                  "scan_SpiralPitchFactor"):
            meta_rows.append((k, session.get(k, "")))

        # Scene metadata
        scene_meta = self._collect_scene_metadata()
        meta_rows.append(("# SLICER", ""))
        for k, v in scene_meta.items():
            meta_rows.append((k, v))

        # Volumes
        try:
            vols = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
            for idx, v in enumerate(vols, start=1):
                meta_rows.append((f"# VOLUME {idx}", ""))
                meta_rows.append((f"volume_{idx}_name", v.GetName()))
                try:
                    dims = v.GetImageData().GetDimensions()
                    meta_rows.append((f"volume_{idx}_dimensions",
                                      f"{dims[0]} {dims[1]} {dims[2]}"))
                except Exception:
                    pass
                try:
                    sp = v.GetSpacing()
                    meta_rows.append((f"volume_{idx}_spacing_mm",
                                      f"{sp[0]:.3f} {sp[1]:.3f} {sp[2]:.3f}"))
                except Exception:
                    pass
        except Exception:
            pass

        # Models
        try:
            models = slicer.util.getNodesByClass("vtkMRMLModelNode")
            for idx, m in enumerate(models, start=1):
                meta_rows.append((f"# MODEL {idx}", ""))
                meta_rows.append((f"model_{idx}_name", m.GetName()))
                try:
                    pd = m.GetPolyData()
                    meta_rows.append((f"model_{idx}_points", pd.GetNumberOfPoints()))
                    meta_rows.append((f"model_{idx}_cells", pd.GetNumberOfCells()))
                except Exception:
                    pass
        except Exception:
            pass

        # Markups
        try:
            markups = slicer.util.getNodesByClass(
                "vtkMRMLMarkupsFiducialNode")
            meta_rows.append(("# MARKUPS", ""))
            for idx, m in enumerate(markups, start=1):
                meta_rows.append((f"markup_{idx}_name", m.GetName()))
                meta_rows.append((f"markup_{idx}_type", "Fiducial"))
                meta_rows.append((f"markup_{idx}_points",
                                  m.GetNumberOfControlPoints()))
        except Exception:
            pass

        # Per-GUI extras
        if extra_meta:
            meta_rows.append(("# GUI STATE", ""))
            for k, v in extra_meta.items():
                meta_rows.append((k, v))

        # Notes
        meta_rows.append(("# NOTES", ""))
        meta_rows.append(("notes", session.get("notes", "")))

        # ---- Landmarks: use filtered rows if provided ----
        if landmark_rows is None:
            landmark_rows = self._collect_landmarks()

        # ---- Write ----
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["key", "value"])
            for k, v in meta_rows:
                w.writerow([k, v])
            w.writerow(["# BEGIN_DATA", ""])
            w.writerow(["point_list", "landmark", "definition", "role",
                        "R_A_S_X", "R_A_S_Y", "R_A_S_Z"])
            for r in landmark_rows:
                w.writerow([r["point_list"], r["landmark"], r["definition"],
                            r.get("role", "unknown"),
                            f"{r['R']:.4f}", f"{r['A']:.4f}", f"{r['S']:.4f}"])

        return path

# ==================================================================
#  Singleton
# ==================================================================
_EXPORTER = None

def get_exporter():
    global _EXPORTER
    if _EXPORTER is None:
        _EXPORTER = RStudioExporter()
    return _EXPORTER


# ==================================================================
#  Button installer
# ==================================================================
def install_export_button_for(gui,
                              parent_layout,
                              method,
                              variant="auto",
                              table_widget=None,
                              measurement_provider=None,
                              metadata_provider=None,
                              button_label="Export for RStudio",
                              style=None):
    if not qt:
        return None

    button = qt.QPushButton(button_label)
    button.setStyleSheet(
        style or
        "background-color: #E67E22; color: white; "
        "font-weight: bold; padding: 8px;")

    def on_click():
        ex = get_exporter()

        # Ask user about folder
        if qt.QMessageBox.question(
            gui, "Export folder",
            f"Export to:\n{ex.folder}\n\nChange folder?",
            qt.QMessageBox.Yes | qt.QMessageBox.No,
            qt.QMessageBox.No
        ) == qt.QMessageBox.Yes:
            ex.choose_folder(gui)

        auto_plane = ex._detect_plane_method()

        # Two prompts (identity + DICOM) + session dialog
        session = ex.prompt_all(gui, method, auto_plane)
        if session is None:
            return

        # ---- Detect runs for this method ----
        runs = _detect_runs(method)
        if not runs:
            slicer.util.infoDisplay(
                f"No runs detected for {method}. "
                "Nothing was written.")
            return

        # ---- Collect all landmarks once (expensive; do it once) ----
        all_landmarks = ex._collect_landmarks()

        # ---- Write one CSV per run ----
        written = []
        for variant_name, variant_meta in runs:
            # Filter landmarks for this run
            filtered = _collect_landmarks_for_variant(
                all_landmarks, method, variant_meta)
            if not filtered:
                print(f"[export] {method} / {variant_name}: "
                      "no landmarks matched — skipping")
                continue

            # Variant resolution
            resolved_variant = variant
            if variant == "auto":
                resolved_variant = _derive_variant(method, session)
            elif callable(variant):
                try:
                    resolved_variant = variant()
                except Exception:
                    resolved_variant = "default"

            session["variant"] = resolved_variant

            extra = None
            if metadata_provider:
                try:
                    extra = metadata_provider()
                except Exception as e:
                    print(f"metadata_provider failed: {e}")

            try:
                path = ex.write_session_file(
                    method=method,
                    subject_id=session["subject_id"],
                    session=session,
                    extra_meta=extra,
                    variant=variant_name,
                    landmark_rows=filtered,
                )
                written.append((variant_name, os.path.basename(path),
                                len(filtered)))
            except Exception as e:
                print(f"[export] {method} / {variant_name}: "
                      f"write failed — {e}")

        # ---- Summary dialog ----
        if not written:
            slicer.util.warningDisplay(
                f"No files written for {method}.")
            return

        summary_lines = [
            f"Exported {len(written)} file(s) for {method}:",
            ""
        ]
        for vname, fname, nrows in written:
            summary_lines.append(f"  [{vname}] {fname}  ({nrows} landmarks)")
        summary_lines.append("")
        summary_lines.append(f"Folder: {os.path.join(ex.folder, method)}")

        slicer.util.infoDisplay("\n".join(summary_lines))

    button.clicked.connect(on_click)
    parent_layout.addWidget(button)
    return button


def _derive_variant(method, session):
    plane = session.get("plane_method", "")
    if method == "TedeschiOliviera":
        if plane == "MSP-3pt":
            return "MSP_3pt"
        if plane == "MSP-5pt":
            return "MSP_5pt"
        return "MSP_unknown"
    if method == "Stephan":
        try:
            if slicer.util.getFirstNodeByName("Pronasale_Stephan"):
                return "StandaloneGUI"
        except Exception:
            pass
        return "EmbeddedStephan"
    if method == "ProkopecUbelaker":
        try:
            for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
                m = re.match(r"pred soft nose outline (\d+)", n.GetName())
                if m:
                    return f"{m.group(1)}p"
        except Exception:
            pass
        return "unknown"
    return plane or "default"