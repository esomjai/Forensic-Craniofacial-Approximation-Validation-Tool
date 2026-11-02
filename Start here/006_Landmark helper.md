## Are you trying out multiple methods on the same sample population?

When there is overlap between the landmarks in different methods, it is tedious to re-allocate the same ones - not to mention, introducing possible inconsistencies. 

When using this GUI, you can export the coordinates of already existing landmarks into the "New" method's coordinates - so if you had nasion at 0,0,0, in method1; and you have method2's landmark ALSO in the scene, the script compares the two for identical landmarks and copies the landmark coordinates from method1 to method2 - saving time for you. 


Currently, the dictionary only contains the landmarks in Nose prediction guidelines, however, I plan on expanding it later. For the full list of landmarks included, please see the drop-down menu below.

<details>
<summary>Landmarks compared</summary>

| Unique ID | Canonical Name | Canonical Definition | Tissue Type | AKA (Also Known As) | Used In (Studies) |
|-----------|----------------|----------------------|-------------|----------------------|-------------------|
| HT-1 | Nasion | Intersection of the nasofrontal sutures in the median plane / most anterior point on the frontonasal suture in the midline | hard tissue | nasion; N; n | Rynn et al. 2010; Ryu 2020; Gerasimov & Maltais Lapointe; Prokopec & Ubelaker; Purkait & Singh; Ridel; Stephan; Tedeschi-Oliveira; Thitiorul et al. 2020; Krogman & Iscan |
| HT-2 | Inion | Median point between the apices of the superior nuchal lines and at the base of the external occipital protuberance | hard tissue | inion | Rynn et al. 2010; Gerasimov & Maltais Lapointe; Prokopec & Ubelaker; Stephan; Tedeschi-Oliveira; Krogman & Iscan |
| HT-3 | Bregma | Where the sagittal and coronal sutures meet | hard tissue | bregma | Rynn et al. 2010; Gerasimov & Maltais Lapointe; Prokopec & Ubelaker; Stephan; Tedeschi-Oliveira; Krogman & Iscan |
| HT-4 | Prosthion | Median point between the central incisors on the anterior most margin of the maxillary alveolar rim | hard tissue | prosthion; pr | Rynn et al. 2010; Prokopec & Ubelaker; Stephan; Tedeschi-Oliveira; Thitiorul et al. 2020; Krogman & Iscan |
| HT-5 | Subspinale | The deepest point seen in the profile view below the anterior nasal spine (orthodontic point A) | hard tissue | subspinale; ss; point A | Rynn et al. 2010; Prokopec & Ubelaker; Purkait & Singh; Stephan; Thitiorul et al. 2020 |
| HT-6 | Rhinion | Most rostral (end) point on the internasal suture / midline point at the inferior free end of the internasal suture | hard tissue | rhinion; R; rhi; subspinale (Krogman & Iscan, label used in error) | Rynn et al. 2010; Ryu 2020; Gerasimov & Maltais Lapointe; Prokopec & Ubelaker; Purkait & Singh; Ridel; Stephan; Tedeschi-Oliveira; Thitiorul et al. 2020; Krogman & Iscan |
| HT-7 | Acanthion / Anterior Nasal Spine | Most anterior tip of the anterior nasal spine | hard tissue | acanthion; AC; ANS; ns; a | Rynn et al. 2010; Ryu 2020; Gerasimov & Maltais Lapointe; Prokopec & Ubelaker; Purkait & Singh; Ridel; Stephan; Thitiorul et al. 2020; Krogman & Iscan |
| HT-8 | Orbitale Left | Most inferior point on the left inferior orbital rim. Usually falls along the lateral half of the orbital margin | hard tissue | O_L | Ryu 2020 |
| HT-9 | Orbitale Right | Most inferior point on the right inferior orbital rim. Usually falls along the lateral half of the orbital margin | hard tissue | O_R | Ryu 2020 |
| HT-10 | Inferior Nasal Concha Left | Point where the left inferior nasal concha is submerged into the medial wall of the nasal aperture | hard tissue | IC_L | Ryu 2020 |
| HT-11 | Inferior Nasal Concha Right | Point where the right inferior nasal concha is submerged into the medial wall of the nasal aperture | hard tissue | IC_R | Ryu 2020 |
| HT-12 | Hard Tissue Alare Left (Most Lateral Nasal/Piriform Aperture Left) | Instrumentally determined as the most lateral point on the left of the nasal aperture in a transverse plane / most lateral point on the left of the bony pyriform aperture | hard tissue | A_L; alL; B (PA_L) | Ryu 2020; Ridel; Purkait & Singh |
| HT-13 | Hard Tissue Alare Right (Most Lateral Nasal/Piriform Aperture Right) | Instrumentally determined as the most lateral point on the right of the nasal aperture in a transverse plane / most lateral point on the right of the bony pyriform aperture | hard tissue | A_R; alR; A (PA_R) | Ryu 2020; Ridel; Purkait & Singh |
| HT-14 | Left Posterior Piriform Aperture Border | Most posterior point on the left lateral curvature of the nasal aperture from profile view | hard tissue | NAG_L | Ryu 2020 |
| HT-15 | Right Posterior Piriform Aperture Border | Most posterior point on the right lateral curvature of the nasal aperture from profile view | hard tissue | NAG_R | Ryu 2020 |
| HT-16 | Left Nasal Aperture Inferior / Lowest Bony Pyriform Aperture Base Left | Most inferior point on the left of the nasal aperture from the frontal view / left lowest point on the aperture border in profile view / lowest point on the left base of the bony pyriform aperture | hard tissue | NAI_L; LL; D (PAB_L) | Ryu 2020; Stephan; Purkait & Singh |
| HT-17 | Right Nasal Aperture Inferior / Lowest Bony Pyriform Aperture Base Right | Most inferior point on the right of the nasal aperture from the frontal view / right lowest point on the aperture border in profile view / lowest point on the right base of the bony pyriform aperture | hard tissue | NAI_R; RL; C (PAB_R) | Ryu 2020; Stephan; Purkait & Singh |
| HT-18 | Left Zygion | The most lateral point on the outline of the LEFT zygomatic arch | hard tissue | zy_L | Thitiorul et al. 2020 |
| HT-19 | Right Zygion | The most lateral point on the outline of the RIGHT zygomatic arch | hard tissue | zy_R | Thitiorul et al. 2020 |
| HT-20 | Left Ectomolare | The most lateral point on the outer surface of the LEFT maxillary alveolar margin | hard tissue | ecm_L | Thitiorul et al. 2020 |
| HT-21 | Right Ectomolare | The most lateral point on the outer surface of the RIGHT maxillary alveolar margin | hard tissue | ecm_R | Thitiorul et al. 2020 |
| HT-22 | Left Infraorbital Foramen | The most superior point on the margin of the LEFT infraorbital foramen | hard tissue | iof_L | Thitiorul et al. 2020 |
| HT-23 | Right Infraorbital Foramen | The most superior point on the margin of the RIGHT infraorbital foramen | hard tissue | iof_R | Thitiorul et al. 2020 |
| HT-24 | Nasal Suture Depth Point | The farthest point perpendicular from the line between n and rhi | hard tissue | nr | Thitiorul et al. 2020 |
| HT-25 | Vomer-Maxillary Junction | The point on the cranium where the maxilla and the vomer meet in the midline, at the posterior end of the anterior nasal spine | hard tissue | VMJ | Krogman & Iscan |
| ST-1 | Soft Tissue Nasion | Point directly anterior to the nasofrontal suture, in the midline, overlying nasion | soft tissue | soft nasion; n'; soft tissue nasion | Rynn et al. 2010; Purkait & Singh; Thitiorul et al. 2020 |
| ST-2 | Subnasale | Median point at the junction between the lower border of the nasal septum and the philtrum area | soft tissue | subnasale; SN; sn' | Rynn et al. 2010; Ryu 2020; Purkait & Singh; Ridel; Thitiorul et al. 2020 |
| ST-3 | Pronasale | The most anteriorly protruded point of the apex nasi. In the case of a bifid nose, the more protruding tip is chosen | soft tissue | pronasale; PN; prn; pn' | Rynn et al. 2010; Ryu 2020; Gerasimov & Maltais Lapointe; Purkait & Singh; Ridel; Stephan; Tedeschi-Oliveira; Thitiorul et al. 2020; Krogman & Iscan |
| ST-4 | Selion / Sellion | Deepest midline point of the nasofrontal angle / most posterior point in the midline of the nasal root | soft tissue | S; se' | Ryu 2020; Thitiorul et al. 2020 |
| ST-5 | Left Alar Groove / Curvature Superior | Highest point on the left ala nasi / most superior point on the left alar groove | soft tissue | ACS_L; als'L | Ryu 2020; Thitiorul et al. 2020 |
| ST-6 | Right Alar Groove / Curvature Superior | Highest point on the right ala nasi / most superior point on the right alar groove | soft tissue | ACS_R; als'R | Ryu 2020; Thitiorul et al. 2020 |
| ST-7 | Left Alar Groove / Curvature Posterior | Most posterolateral point of the left curvature of the base of the nasal alae / most posterior point on the left alar groove | soft tissue | ACP_L; alp'L | Ryu 2020; Thitiorul et al. 2020 |
| ST-8 | Right Alar Groove / Curvature Posterior | Most posterolateral point of the right curvature of the base of the nasal alae / most posterior point on the right alar groove | soft tissue | ACP_R; alp'R | Ryu 2020; Thitiorul et al. 2020 |
| ST-9 | Left Alare (Soft Tissue) | The most lateral point on the left nasal ala | soft tissue | NA_L; X1(alL); al'L | Ryu 2020; Purkait & Singh; Ridel; Thitiorul et al. 2020 |
| ST-10 | Right Alare (Soft Tissue) | The most lateral point on the right nasal ala | soft tissue | NA_R; X2(alR); al'R | Ryu 2020; Purkait & Singh; Ridel; Thitiorul et al. 2020 |
| ST-11 | Left Alar Groove / Curvature Inferior | Most posterolateral point of the curvature of the base line of the left nasal ala / most inferior point on the left alar groove | soft tissue | ACI_L; ali'L | Ryu 2020; Thitiorul et al. 2020 |
| ST-12 | Right Alar Groove / Curvature Inferior | Most posterolateral point of the curvature of the base line of the right nasal ala / most inferior point on the right alar groove | soft tissue | ACI_R; ali'R | Ryu 2020; Thitiorul et al. 2020 |
| ST-13 | Right Reference Point 2 | The point where the T4R crosses the surface of the nasal soft tissue on the right | soft tissue | RR2 | Gerasimov & Maltais Lapointe |
| ST-14 | Left Reference Point 2 | The point where the T4L crosses the surface of the nasal soft tissue on the left | soft tissue | LR2 | Gerasimov & Maltais Lapointe |
| ST-15 | Midsagittal Reference Point 2 | The point where the T4 crosses the surface of the nasal soft tissue on the midsagittal plane | soft tissue | R2 | Gerasimov & Maltais Lapointe |
| ST-16 | Soft Tissue Rhinion | Point overlying rhinion, at the end of the internasal suture where bone ends and cartilage begins | soft tissue | rhi' | Purkait & Singh |
| ST-17 | Nasal Tip Inferior | Lowest point on the lower margin of the nasal tip in the midsagittal plane | soft tissue | nt | Purkait & Singh |
| ST-18 | Left Nasal Base Attachment | The base of the left attachment of nasal wings on the upper lip | soft tissue | Y1(nbL) | Purkait & Singh |
| ST-19 | Right Nasal Base Attachment | The base of the right attachment of nasal wings on the upper lip | soft tissue | Y2(nbR) | Purkait & Singh |
| ST-20 | n-prn Posterior | The farthest point perpendicular from the line between n' and prn, located posteriorly | soft tissue | npp' | Thitiorul et al. 2020 |
| ST-21 | n-prn Anterior | The farthest point perpendicular from the line between n' and prn, located anteriorly | soft tissue | npa' | Thitiorul et al. 2020 |
| ST-22 | Nasal Drop | The farthest point perpendicular from the line between prn and sn, located inferiorly | soft tissue | nd' | Thitiorul et al. 2020 |


</details>


```python
import json
import re
import numpy as np
import qt
import slicer

SCHEMA_JSON = r'''{
  "schemaVersion": "1.0.0",
  "landmarks": [
    {"id":"HT-1","canonicalName":"Nasion","tissueType":"hard","aka":["nasion","N","n"]},
    {"id":"HT-2","canonicalName":"Inion","tissueType":"hard","aka":["inion"]},
    {"id":"HT-3","canonicalName":"Bregma","tissueType":"hard","aka":["bregma"]},
    {"id":"HT-4","canonicalName":"Prosthion","tissueType":"hard","aka":["prosthion","pr"]},
    {"id":"HT-5","canonicalName":"Subspinale","tissueType":"hard","aka":["subspinale","ss","point A"]},
    {"id":"HT-6","canonicalName":"Rhinion","tissueType":"hard","aka":["rhinion","R","rhi"]},
    {"id":"HT-7","canonicalName":"Acanthion / Anterior Nasal Spine","tissueType":"hard","aka":["acanthion","AC","ANS","ns","a"]},
    {"id":"HT-8","canonicalName":"Orbitale Left","tissueType":"hard","aka":["O_L","orbitale_left","orb_L"]},
    {"id":"HT-9","canonicalName":"Orbitale Right","tissueType":"hard","aka":["O_R","orbitale_right","orb_R"]},
    {"id":"HT-10","canonicalName":"Inferior Nasal Concha Left (Ryu)","tissueType":"hard","aka":["IC_L"]},
    {"id":"HT-11","canonicalName":"Inferior Nasal Concha Right (Ryu)","tissueType":"hard","aka":["IC_R"]},
    {"id":"HT-12","canonicalName":"Hard Tissue Alare Left","tissueType":"hard","aka":["A_L","alL","B (PA_L)"]},
    {"id":"HT-13","canonicalName":"Hard Tissue Alare Right","tissueType":"hard","aka":["A_R","alR","A (PA_R)"]},
    {"id":"HT-14","canonicalName":"Left Posterior Piriform Aperture Border","tissueType":"hard","aka":["NAG_L","XL"]},
    {"id":"HT-15","canonicalName":"Right Posterior Piriform Aperture Border","tissueType":"hard","aka":["NAG_R","XR"]},
    {"id":"HT-16","canonicalName":"Left Nasal Aperture Inferior","tissueType":"hard","aka":["NAI_L","LL","D (PAB_L)"]},
    {"id":"HT-17","canonicalName":"Right Nasal Aperture Inferior","tissueType":"hard","aka":["NAI_R","RL","LR","C (PAB_R)"]},
    {"id":"HT-18","canonicalName":"Left Zygion","tissueType":"hard","aka":["zy_L"]},
    {"id":"HT-19","canonicalName":"Right Zygion","tissueType":"hard","aka":["zy_R"]},
    {"id":"HT-20","canonicalName":"Left Ectomolare","tissueType":"hard","aka":["ecm_L"]},
    {"id":"HT-21","canonicalName":"Right Ectomolare","tissueType":"hard","aka":["ecm_R"]},
    {"id":"HT-22","canonicalName":"Left Infraorbital Foramen","tissueType":"hard","aka":["iof_L"]},
    {"id":"HT-23","canonicalName":"Right Infraorbital Foramen","tissueType":"hard","aka":["iof_R"]},
    {"id":"HT-25","canonicalName":"Vomer-Maxillary Junction","tissueType":"hard","aka":["VMJ"]},
    {"id":"HT-26","canonicalName":"Maxillary Canine Cusp Tip Left","tissueType":"hard","aka":["ICL","left canine cusp"]},
    {"id":"HT-27","canonicalName":"Maxillary Canine Cusp Tip Right","tissueType":"hard","aka":["ICR","right canine cusp"]},
    {"id":"HT-28","canonicalName":"Lateral Point Left Central Incisor","tissueType":"hard","aka":["LCIL"]},
    {"id":"HT-29","canonicalName":"Lateral Point Right Central Incisor","tissueType":"hard","aka":["LCIR"]},
    {"id":"HT-30","canonicalName":"Medial Point Left Central Incisor","tissueType":"hard","aka":["MCIL"]},
    {"id":"HT-31","canonicalName":"Medial Point Right Central Incisor","tissueType":"hard","aka":["MCIR"]},
    {"id":"HT-32","canonicalName":"Rynn Left Concha / Inferior Turbinate Meets Nasal Border","tissueType":"hard","aka":["CL"]},
    {"id":"HT-33","canonicalName":"Rynn Right Concha / Inferior Turbinate Meets Nasal Border","tissueType":"hard","aka":["CR"]},
    {"id":"ST-1","canonicalName":"Soft Tissue Nasion","tissueType":"soft","aka":["soft nasion","n'","soft tissue nasion"]},
    {"id":"ST-2","canonicalName":"Subnasale","tissueType":"soft","aka":["subnasale","SN","sn'"]},
    {"id":"ST-3","canonicalName":"Pronasale","tissueType":"soft","aka":["pronasale","PN","prn","pn'"]},
    {"id":"ST-4","canonicalName":"Selion / Sellion","tissueType":"soft","aka":["S","se'"]},
    {"id":"ST-5","canonicalName":"Left Alar Groove / Curvature Superior","tissueType":"soft","aka":["ACS_L","als'L","pt5L"]},
    {"id":"ST-6","canonicalName":"Right Alar Groove / Curvature Superior","tissueType":"soft","aka":["ACS_R","als'R","pt5R"]},
    {"id":"ST-7","canonicalName":"Left Alar Groove / Curvature Posterior","tissueType":"soft","aka":["ACP_L","alp'L","pt4L"]},
    {"id":"ST-8","canonicalName":"Right Alar Groove / Curvature Posterior","tissueType":"soft","aka":["ACP_R","alp'R","pt4R"]},
    {"id":"ST-9","canonicalName":"Left Alare (Soft Tissue)","tissueType":"soft","aka":["NA_L","X1(alL)","al'L","pt6L"]},
    {"id":"ST-10","canonicalName":"Right Alare (Soft Tissue)","tissueType":"soft","aka":["NA_R","X2(alR)","al'R","pt6R"]},
    {"id":"ST-11","canonicalName":"Left Alar Groove / Curvature Inferior","tissueType":"soft","aka":["ACI_L","ali'L","pt7L"]},
    {"id":"ST-12","canonicalName":"Right Alar Groove / Curvature Inferior","tissueType":"soft","aka":["ACI_R","ali'R","pt7R"]},
    {"id":"ST-13","canonicalName":"Soft Tissue Rhinion","tissueType":"soft","aka":["rhi'"]},
    {"id":"ST-14","canonicalName":"Nasal Tip Inferior","tissueType":"soft","aka":["nt"]},
    {"id":"ST-15","canonicalName":"Left Nasal Base Attachment","tissueType":"soft","aka":["Y1(nbL)"]},
    {"id":"ST-16","canonicalName":"Right Nasal Base Attachment","tissueType":"soft","aka":["Y2(nbR)"]},
    {"id":"ST-17","canonicalName":"Anterior Nostril Border Left","tissueType":"soft","aka":["pt1L"]},
    {"id":"ST-18","canonicalName":"Anterior Nostril Border Right","tissueType":"soft","aka":["pt1R"]},
    {"id":"ST-19","canonicalName":"Posterior Nostril Border Left","tissueType":"soft","aka":["pt2L"]},
    {"id":"ST-20","canonicalName":"Posterior Nostril Border Right","tissueType":"soft","aka":["pt2R"]},
    {"id":"ST-21","canonicalName":"Superior Nostril Border Left","tissueType":"soft","aka":["pt3L"]},
    {"id":"ST-22","canonicalName":"Superior Nostril Border Right","tissueType":"soft","aka":["pt3R"]},
    {"id":"ST-23","canonicalName":"Columella Break Point Left","tissueType":"soft","aka":["pt8L"]},
    {"id":"ST-24","canonicalName":"Columella Break Point Right","tissueType":"soft","aka":["pt8R"]}
  ]
}'''


def _normalize_label(label):
    """Normalize a label for comparison."""
    if label is None:
        return ""
    s = str(label).lower().strip()
    s = s.replace("left", "_l").replace("right", "_r")
    s = s.replace("'", "").replace("`", "")
    s = re.sub(r"[^a-z0-9_]+", "", s)
    s = s.replace("__", "_")
    return s


class LandmarkMergerTool(qt.QDialog):
    """
    Landmark Merger Tool – with Matching table, no Unmatched tables.
    """

    def __init__(self, parent=None):
        super(LandmarkMergerTool, self).__init__(parent)
        self.setWindowTitle("Landmark Merger Tool")
        self.setMinimumSize(500, 400)
        self.setMaximumSize(1200, 800)
        self.setModal(False)

        self.setWindowFlags(qt.Qt.Window | qt.Qt.WindowCloseButtonHint | qt.Qt.WindowMinimizeButtonHint)
        self._applyTheme()

        self.schema = json.loads(SCHEMA_JSON)
        self.landmarkById = {lm["id"]: lm for lm in self.schema["landmarks"]}
        self._buildAliasIndex()

        self.matches = []
        self.unmatchedTarget = []
        self.unmatchedSource = []
        self._buildUI()

    def _applyTheme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d7de;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                border-radius: 5px;
                padding: 6px 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { opacity: 0.9; }
            QPushButton:pressed { opacity: 0.7; }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 1px solid #d0d7de;
                border-radius: 5px;
            }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
            QComboBox {
                padding: 4px;
                border: 1px solid #d0d7de;
                border-radius: 4px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:hover { border-color: #3498db; }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #e0e0e0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #b0b0b0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #909090; }
        """)

    def _buildAliasIndex(self):
        self.aliasToLandmarkIdsExact = {}
        self.aliasToLandmarkIdsNormalized = {}
        for lm in self.schema["landmarks"]:
            values = [lm["canonicalName"]] + lm.get("aka", [])
            for v in values:
                if str(v) not in self.aliasToLandmarkIdsExact:
                    self.aliasToLandmarkIdsExact[str(v)] = []
                self.aliasToLandmarkIdsExact[str(v)].append(lm["id"])
                norm_v = _normalize_label(v)
                if norm_v not in self.aliasToLandmarkIdsNormalized:
                    self.aliasToLandmarkIdsNormalized[norm_v] = []
                self.aliasToLandmarkIdsNormalized[norm_v].append(lm["id"])

    def _buildUI(self):
        mainLayout = qt.QVBoxLayout(self)
        mainLayout.setSpacing(8)
        mainLayout.setContentsMargins(12, 12, 12, 12)

        # Header
        headerLayout = qt.QHBoxLayout()
        titleLabel = qt.QLabel("🔬 Landmark Merger Tool")
        titleLabel.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 3px;")
        headerLayout.addWidget(titleLabel)
        headerLayout.addStretch()
        self.toggleCompactBtn = qt.QPushButton("⊞ Toggle Compact Mode")
        self.toggleCompactBtn.setStyleSheet("""
            QPushButton {
                background-color: #5d6d7e;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #34495e; }
        """)
        self.toggleCompactBtn.clicked.connect(self.toggleCompactMode)
        headerLayout.addWidget(self.toggleCompactBtn)
        mainLayout.addLayout(headerLayout)

        self.scrollArea = qt.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(qt.QFrame.NoFrame)
        scrollContent = qt.QWidget()
        scrollLayout = qt.QVBoxLayout(scrollContent)
        scrollLayout.setSpacing(10)
        scrollLayout.setContentsMargins(0, 0, 0, 0)

        # Description
        self.descBox = qt.QGroupBox()
        descLayout = qt.QVBoxLayout(self.descBox)
        descLayout.setContentsMargins(10, 5, 10, 5)
        desc = qt.QLabel(
            "Compare two landmark files and selectively import coordinates from Source to Target.\n"
            "Check the box for each landmark you want to update. After applying, matched points are hidden in the 3D scene; unmatched points remain visible."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #555555; font-size: 12px; background-color: #f8f9fa; padding: 6px; border-radius: 4px;")
        descLayout.addWidget(desc)
        scrollLayout.addWidget(self.descBox)

        # File selectors
        filesBox = qt.QGroupBox("📂 Select Landmark Files")
        filesLayout = qt.QFormLayout(filesBox)
        filesLayout.setSpacing(6)
        filesLayout.setContentsMargins(10, 15, 10, 10)
        self.sourceSelector = slicer.qMRMLNodeComboBox()
        self.sourceSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.sourceSelector.noneEnabled = True
        self.sourceSelector.addEnabled = False
        self.sourceSelector.removeEnabled = False
        self.sourceSelector.setMRMLScene(slicer.mrmlScene)
        self.sourceSelector.setToolTip("Select the source landmark file (coordinates will be imported FROM this file)")
        self.sourceSelector.setMinimumHeight(25)
        self.targetSelector = slicer.qMRMLNodeComboBox()
        self.targetSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.targetSelector.noneEnabled = True
        self.targetSelector.addEnabled = False
        self.targetSelector.removeEnabled = False
        self.targetSelector.setMRMLScene(slicer.mrmlScene)
        self.targetSelector.setToolTip("Select the target landmark file (coordinates will be imported TO this file)")
        self.targetSelector.setMinimumHeight(25)
        filesLayout.addRow("📤 Source (Import FROM):", self.sourceSelector)
        filesLayout.addRow("📥 Target (Import TO):", self.targetSelector)
        scrollLayout.addWidget(filesBox)

        # Compare button
        btnLayout = qt.QHBoxLayout()
        btnLayout.setContentsMargins(0, 3, 0, 3)
        self.compareBtn = qt.QPushButton("🔍 Compare Landmarks")
        self.compareBtn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 25px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #21618c; }
        """)
        self.compareBtn.setMinimumHeight(32)
        self.compareBtn.clicked.connect(self.compareLandmarks)
        btnLayout.addStretch()
        btnLayout.addWidget(self.compareBtn)
        btnLayout.addStretch()
        scrollLayout.addLayout(btnLayout)

        # ===== Matching Landmarks Table =====
        resultsBox = qt.QGroupBox("📋 Matching Landmarks")
        resultsLayout = qt.QVBoxLayout(resultsBox)
        resultsLayout.setContentsMargins(10, 15, 10, 10)
        instr = qt.QLabel(
            "✓ Check the box to import coordinates from the Source file\n"
            "✗ Uncheck to keep the Target file's coordinates"
        )
        instr.setWordWrap(True)
        instr.setStyleSheet("color: #555555; background-color: #f8f9fa; padding: 5px; border-radius: 4px; font-size: 11px;")
        resultsLayout.addWidget(instr)
        self.resultsTable = qt.QTableWidget()
        self.resultsTable.setColumnCount(8)
        self.resultsTable.setHorizontalHeaderLabels([
            "Use Source", "ID", "Canonical Name",
            "Source Definition", "Target Definition",
            "Source Label", "Target Label", "Coordinates"
        ])
        self.resultsTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.resultsTable.verticalHeader().setVisible(False)
        self.resultsTable.setMinimumHeight(150)
        self.resultsTable.setMaximumHeight(400)
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.setColumnWidth(0, 70)
        self.resultsTable.setColumnWidth(1, 80)
        self.resultsTable.setColumnWidth(2, 180)
        self.resultsTable.setColumnWidth(3, 200)
        self.resultsTable.setColumnWidth(4, 200)
        self.resultsTable.setColumnWidth(5, 130)
        self.resultsTable.setColumnWidth(6, 130)
        self.resultsTable.setColumnWidth(7, 90)
        resultsLayout.addWidget(self.resultsTable)
        scrollLayout.addWidget(resultsBox)
        self.resultsBox = resultsBox

        # Action buttons (Select All, Select None, Apply)
        actionLayout = qt.QHBoxLayout()
        actionLayout.setSpacing(8)
        self.selectAllBtn = qt.QPushButton("✅ Select All")
        self.selectAllBtn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        self.selectAllBtn.clicked.connect(self.selectAll)
        self.selectNoneBtn = qt.QPushButton("❌ Select None")
        self.selectNoneBtn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.selectNoneBtn.clicked.connect(self.selectNone)
        self.applyBtn = qt.QPushButton("📥 Apply Selected Changes")
        self.applyBtn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 8px 25px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #27ae60; }
            QPushButton:disabled { background-color: #95a5a6; color: #ecf0f1; }
        """)
        self.applyBtn.clicked.connect(self.applyChanges)
        self.applyBtn.setEnabled(False)
        self.applyBtn.setMinimumHeight(32)
        actionLayout.addWidget(self.selectAllBtn)
        actionLayout.addWidget(self.selectNoneBtn)
        actionLayout.addStretch(1)
        actionLayout.addWidget(self.applyBtn)
        scrollLayout.addLayout(actionLayout)

        # Delete Source button
        deleteLayout = qt.QHBoxLayout()
        deleteLayout.setContentsMargins(0, 2, 0, 2)
        self.deleteBtn = qt.QPushButton("🗑️ Delete Source File (Optional)")
        self.deleteBtn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #d35400; }
            QPushButton:disabled { background-color: #95a5a6; color: #ecf0f1; }
        """)
        self.deleteBtn.clicked.connect(self.deleteSourceFile)
        self.deleteBtn.setEnabled(False)
        self.deleteBtn.setMinimumHeight(28)
        deleteLayout.addStretch()
        deleteLayout.addWidget(self.deleteBtn)
        scrollLayout.addLayout(deleteLayout)
        scrollLayout.addStretch()

        self.scrollArea.setWidget(scrollContent)
        mainLayout.addWidget(self.scrollArea)

        # Status bar
        self.status = qt.QLabel("🔹 Ready - Select two landmark files and click 'Compare Landmarks'")
        self.status.setStyleSheet("background-color:#ecf0f1; padding:6px; border-radius:4px; color:#2c3e50; font-weight:bold; font-size:12px;")
        self.status.setMinimumHeight(28)
        mainLayout.addWidget(self.status)

        self.footerLayout = qt.QHBoxLayout()
        self.footerLayout.setContentsMargins(0, 2, 0, 0)
        self.footerLabel = qt.QLabel("Landmark Merger Tool v2.0 | 3D Slicer compatible")
        self.footerLabel.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 3px;")
        self.footerLayout.addWidget(self.footerLabel)
        self.footerLayout.addStretch()
        mainLayout.addLayout(self.footerLayout)

        self.mainLayout = mainLayout
        self.scrollContent = scrollContent

    # ===== Compact mode toggle =====
    def toggleCompactMode(self):
        self.compactMode = not self.compactMode
        if self.compactMode:
            self.descBox.setVisible(False)
            self.resultsTable.setMaximumHeight(200)
            self.footerLabel.setVisible(False)
            self.mainLayout.setContentsMargins(8, 8, 8, 8)
            self.toggleCompactBtn.setText("⊟ Expand")
        else:
            self.descBox.setVisible(True)
            self.resultsTable.setMaximumHeight(400)
            self.footerLabel.setVisible(True)
            self.mainLayout.setContentsMargins(12, 12, 12, 12)
            self.toggleCompactBtn.setText("⊞ Toggle Compact Mode")
        self.adjustSize()
        if self.size().width() < 500 or self.size().height() < 400:
            self.resize(max(self.size().width(), 500), max(self.size().height(), 400))

    # ===== Core logic =====
    def _collectNodeLabels(self, node):
        labels = []
        if not node:
            return labels
        for i in range(node.GetNumberOfControlPoints()):
            label = node.GetNthControlPointLabel(i)
            desc = node.GetNthControlPointDescription(i) if hasattr(node, 'GetNthControlPointDescription') else ""
            labels.append((i, label, desc))
        return labels

    def _findLandmarkId(self, label):
        if label in self.aliasToLandmarkIdsExact:
            ids = self.aliasToLandmarkIdsExact[label]
            if len(ids) == 1:
                return ids[0]
        norm = _normalize_label(label)
        if norm in self.aliasToLandmarkIdsNormalized:
            ids = self.aliasToLandmarkIdsNormalized[norm]
            if len(ids) == 1:
                return ids[0]
        return None

    def _getAllLandmarkIds(self, node):
        ids = set()
        if node:
            for i in range(node.GetNumberOfControlPoints()):
                label = node.GetNthControlPointLabel(i)
                lm_id = self._findLandmarkId(label)
                if lm_id:
                    ids.add(lm_id)
        return ids

    def _getUnmatchedLandmarks(self, sourceNode, targetNode):
        sourceIds = self._getAllLandmarkIds(sourceNode)
        targetIds = self._getAllLandmarkIds(targetNode)
        targetOnly = []
        for lm_id in sorted(targetIds - sourceIds):
            targetOnly.append({
                'id': lm_id,
                'canonicalName': self.landmarkById[lm_id]['canonicalName'],
                'tissueType': self.landmarkById[lm_id]['tissueType']
            })
        sourceOnly = []
        for lm_id in sorted(sourceIds - targetIds):
            sourceOnly.append({
                'id': lm_id,
                'canonicalName': self.landmarkById[lm_id]['canonicalName'],
                'tissueType': self.landmarkById[lm_id]['tissueType']
            })
        return targetOnly, sourceOnly

    def _applyVisibility(self, sourceNode, targetNode):
        """Hide matched points, show unmatched points in the 3D scene."""
        if not sourceNode or not targetNode:
            return

        matched_source_idx = set(m['source_idx'] for m in self.matches)
        matched_target_idx = set(m['target_idx'] for m in self.matches)

        for i in range(sourceNode.GetNumberOfControlPoints()):
            sourceNode.SetNthControlPointVisibility(i, 0 if i in matched_source_idx else 1)
        for i in range(targetNode.GetNumberOfControlPoints()):
            targetNode.SetNthControlPointVisibility(i, 0 if i in matched_target_idx else 1)

        self._setStatus("👁️ Matched points hidden, unmatched points visible in 3D view", "info")

    def _setStatus(self, message, status_type="info"):
        styles = {
            "info": "background-color:#ecf0f1; padding:6px; border-radius:4px; color:#2c3e50; font-weight:bold; font-size:12px;",
            "success": "background-color:#e8f8f5; padding:6px; border-radius:4px; color:#1a7a5a; font-weight:bold; font-size:12px;",
            "error": "background-color:#fde8e8; padding:6px; border-radius:4px; color:#c0392b; font-weight:bold; font-size:12px;",
            "warning": "background-color:#fef9e7; padding:6px; border-radius:4px; color:#b7950b; font-weight:bold; font-size:12px;"
        }
        self.status.setText(message)
        self.status.setStyleSheet(styles.get(status_type, styles["info"]))

    def _updateTable(self):
        self.resultsTable.setRowCount(len(self.matches))
        for row, match in enumerate(self.matches):
            checkbox = qt.QCheckBox()
            checkbox.setChecked(match.get('use_source', True))
            checkbox.stateChanged.connect(lambda state, r=row: self._onCheckboxChanged(r, state))
            self.resultsTable.setCellWidget(row, 0, checkbox)

            item = qt.QTableWidgetItem(match['landmark_id'])
            item.setTextAlignment(qt.Qt.AlignCenter)
            self.resultsTable.setItem(row, 1, item)

            item = qt.QTableWidgetItem(match['canonical_name'])
            self.resultsTable.setItem(row, 2, item)

            item = qt.QTableWidgetItem(match['source_desc'] if match['source_desc'] else "")
            item.setToolTip(match['source_desc'] if match['source_desc'] else "")
            self.resultsTable.setItem(row, 3, item)

            item = qt.QTableWidgetItem(match['target_desc'] if match['target_desc'] else "")
            item.setToolTip(match['target_desc'] if match['target_desc'] else "")
            self.resultsTable.setItem(row, 4, item)

            item = qt.QTableWidgetItem(match['source_label'])
            self.resultsTable.setItem(row, 5, item)

            item = qt.QTableWidgetItem(match['target_label'])
            self.resultsTable.setItem(row, 6, item)

            status = "✓ OK"
            statusColor = "#27ae60"
            sourceNode = self.sourceSelector.currentNode()
            targetNode = self.targetSelector.currentNode()
            if sourceNode and targetNode:
                try:
                    sourcePos = sourceNode.GetNthControlPointPosition(match['source_idx'])
                    targetPos = targetNode.GetNthControlPointPosition(match['target_idx'])
                    if np.isnan(sourcePos[0]) or np.isnan(targetPos[0]):
                        status = "⚠ Missing"
                        statusColor = "#e67e22"
                    elif np.allclose(sourcePos, targetPos, rtol=1e-5, atol=1e-5):
                        status = "✓ Identical"
                        statusColor = "#3498db"
                    else:
                        status = "✓ Different"
                        statusColor = "#27ae60"
                except:
                    status = "✗ Error"
                    statusColor = "#e74c3c"
            item = qt.QTableWidgetItem(status)
            item.setTextAlignment(qt.Qt.AlignCenter)
            item.setForeground(qt.QColor(statusColor))
            self.resultsTable.setItem(row, 7, item)

    def _onCheckboxChanged(self, row, state):
        if row < len(self.matches):
            self.matches[row]['use_source'] = (state == qt.Qt.Checked)

    def selectAll(self):
        for row in range(self.resultsTable.rowCount()):
            checkbox = self.resultsTable.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
                self.matches[row]['use_source'] = True

    def selectNone(self):
        for row in range(self.resultsTable.rowCount()):
            checkbox = self.resultsTable.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
                self.matches[row]['use_source'] = False

    def _isNodeLocked(self, node):
        try:
            return node.locked
        except AttributeError:
            try:
                return node.IsLocked()
            except AttributeError:
                return False

    def _setNodeLocked(self, node, locked):
        try:
            node.locked = locked
        except AttributeError:
            try:
                if locked:
                    node.Lock()
                else:
                    node.Unlock()
            except AttributeError:
                pass

    def compareLandmarks(self):
        sourceNode = self.sourceSelector.currentNode()
        targetNode = self.targetSelector.currentNode()
        if not sourceNode or not targetNode:
            self._setStatus("❌ Error: Please select both source and target landmark files", "error")
            return
        if sourceNode == targetNode:
            self._setStatus("❌ Error: Source and target files must be different", "error")
            return

        sourceLabels = self._collectNodeLabels(sourceNode)
        targetLabels = self._collectNodeLabels(targetNode)
        if not sourceLabels:
            self._setStatus("❌ Error: Source file has no landmarks", "error")
            return
        if not targetLabels:
            self._setStatus("❌ Error: Target file has no landmarks", "error")
            return

        # Build matches
        self.matches = []
        for sourceIdx, sourceLabel, sourceDesc in sourceLabels:
            sourceLandmarkId = self._findLandmarkId(sourceLabel)
            if sourceLandmarkId:
                canonicalName = self.landmarkById[sourceLandmarkId]["canonicalName"]
                targetIdx = None
                targetLabel = None
                targetDesc = ""
                for tIdx, tLabel, tDesc in targetLabels:
                    tLandmarkId = self._findLandmarkId(tLabel)
                    if tLandmarkId == sourceLandmarkId:
                        targetIdx = tIdx
                        targetLabel = tLabel
                        targetDesc = tDesc
                        break
                if targetIdx is None:
                    for tIdx, tLabel, tDesc in targetLabels:
                        tLandmarkId = self._findLandmarkId(tLabel)
                        if tLandmarkId and self.landmarkById[tLandmarkId]["canonicalName"] == canonicalName:
                            targetIdx = tIdx
                            targetLabel = tLabel
                            targetDesc = tDesc
                            break
                if targetIdx is not None:
                    self.matches.append({
                        'landmark_id': sourceLandmarkId,
                        'canonical_name': canonicalName,
                        'source_idx': sourceIdx,
                        'source_label': sourceLabel,
                        'source_desc': sourceDesc,
                        'target_idx': targetIdx,
                        'target_label': targetLabel,
                        'target_desc': targetDesc,
                        'use_source': True
                    })
        self.matches.sort(key=lambda x: x['canonical_name'])

        # Get unmatched (only for summary)
        self.unmatchedTarget, self.unmatchedSource = self._getUnmatchedLandmarks(sourceNode, targetNode)

        # Apply visibility
        self._applyVisibility(sourceNode, targetNode)

        # Update table
        self._updateTable()
        self.applyBtn.setEnabled(True)
        self.deleteBtn.setEnabled(True)
        self._setStatus("✅ Found " + str(len(self.matches)) + " matching landmarks. Select which coordinates to import.", "success")

    def applyChanges(self):
        sourceNode = self.sourceSelector.currentNode()
        targetNode = self.targetSelector.currentNode()
        if not sourceNode or not targetNode:
            self._setStatus("❌ Error: Source or target node not available", "error")
            return
        if not self.matches:
            self._setStatus("⚠️ No matches to apply", "warning")
            return

        if self._isNodeLocked(targetNode):
            reply = qt.QMessageBox.question(
                self,
                "Node Locked",
                "The target landmark file is locked. Do you want to unlock it to apply changes?",
                qt.QMessageBox.Yes | qt.QMessageBox.No
            )
            if reply == qt.QMessageBox.Yes:
                self._setNodeLocked(targetNode, False)
            else:
                self._setStatus("⚠️ Operation cancelled - target file is locked", "warning")
                return

        changesApplied = 0
        changesSkipped = 0
        updatedLandmarks = []
        skippedLandmarks = []
        originalTargetCount = targetNode.GetNumberOfControlPoints()
        for match in self.matches:
            if match['use_source']:
                try:
                    sourcePos = sourceNode.GetNthControlPointPosition(match['source_idx'])
                    if np.isnan(sourcePos[0]) or np.isnan(sourcePos[1]) or np.isnan(sourcePos[2]):
                        changesSkipped += 1
                        skippedLandmarks.append(match['canonical_name'] + " (invalid source position)")
                        continue
                    targetPos = targetNode.GetNthControlPointPosition(match['target_idx'])
                    if np.allclose(sourcePos, targetPos, rtol=1e-5, atol=1e-5):
                        changesSkipped += 1
                        skippedLandmarks.append(match['canonical_name'] + " (already identical)")
                        continue
                    targetNode.SetNthControlPointPosition(match['target_idx'], sourcePos[0], sourcePos[1], sourcePos[2])
                    changesApplied += 1
                    updatedLandmarks.append(match['canonical_name'])
                except Exception as e:
                    self._setStatus("❌ Error applying change for " + match['canonical_name'] + ": " + str(e), "error")
                    return

        finalTargetCount = targetNode.GetNumberOfControlPoints()
        if finalTargetCount != originalTargetCount:
            self._setStatus("❌ Error: Target file point count changed! This should not happen.", "error")
            return

        self._updateTable()
        self._showMergeSummary(updatedLandmarks, skippedLandmarks, changesApplied, changesSkipped)

        if changesApplied > 0:
            self._setStatus("✅ Updated coordinates for " + str(changesApplied) + " landmark(s).", "success")
        else:
            self._setStatus("ℹ️ No coordinates were updated.", "warning")

    def _showMergeSummary(self, updated, skipped, changesApplied, changesSkipped):
        summary = "📊 MERGE COMPLETE\n" + "=" * 65 + "\n\n"
        if changesApplied > 0:
            summary += "✅ Successfully updated coordinates for " + str(changesApplied) + " landmark(s):\n"
            for name in updated:
                summary += "  ✓ " + name + "\n"
            summary += "\n"
        else:
            summary += "ℹ️ No coordinates were updated.\n\n"
        if changesSkipped > 0:
            summary += "⏭️ Skipped " + str(changesSkipped) + " landmark(s):\n"
            for skip in skipped:
                summary += "  • " + skip + "\n"
            summary += "\n"
        if self.unmatchedTarget:
            summary += "📋 LANDMARKS IN TARGET BUT NOT IN SOURCE (" + str(len(self.unmatchedTarget)) + "):\n"
            summary += "   These landmarks exist in target but not in source.\n"
            summary += "   They were NOT updated (no source coordinates available).\n\n"
            hard_unmatched = [lm for lm in self.unmatchedTarget if lm['tissueType'] == 'hard']
            soft_unmatched = [lm for lm in self.unmatchedTarget if lm['tissueType'] == 'soft']
            if hard_unmatched:
                summary += "  🔷 Hard tissue:\n"
                for lm in hard_unmatched:
                    summary += "    • " + lm['id'] + ": " + lm['canonicalName'] + "\n"
            if soft_unmatched:
                summary += "  🔶 Soft tissue:\n"
                for lm in soft_unmatched:
                    summary += "    • " + lm['id'] + ": " + lm['canonicalName'] + "\n"
        else:
            targetIds = self._getAllLandmarkIds(self.targetSelector.currentNode())
            if targetIds:
                summary += "🎉 ALL " + str(len(targetIds)) + " target landmarks have matches in the source file!\n"
                summary += "   All available landmarks have been updated."
        summary += "\n\n📌 Note: Only RAS coordinates were updated. Labels, descriptions, and point count remain unchanged."
        summary += "\n\n💡 Tip: You can now delete the source file using the 'Delete Source File' button below."

        msgBox = qt.QMessageBox(self)
        msgBox.setWindowTitle("Merge Summary")
        msgBox.setText(summary)
        msgBox.setIcon(qt.QMessageBox.Warning if self.unmatchedTarget else qt.QMessageBox.Information)
        msgBox.setStandardButtons(qt.QMessageBox.Ok)
        msgBox.setSizeGripEnabled(True)
        msgBox.exec_()

    def deleteSourceFile(self):
        sourceNode = self.sourceSelector.currentNode()
        if not sourceNode:
            return
        reply = qt.QMessageBox.question(
            self,
            "Delete Source File?",
            "Are you sure you want to delete the source landmark file?\n\n"
            "File: " + sourceNode.GetName() + "\n\n"
            "This action cannot be undone.",
            qt.QMessageBox.Yes | qt.QMessageBox.No
        )
        if reply == qt.QMessageBox.Yes:
            try:
                scene = slicer.mrmlScene
                scene.RemoveNode(sourceNode)
                self._setStatus("🗑️ Source file deleted: " + sourceNode.GetName(), "info")
                self.sourceSelector.setCurrentNode(None)
                self.deleteBtn.setEnabled(False)
                self.applyBtn.setEnabled(False)
                self.matches = []
                self.resultsTable.setRowCount(0)
                self.unmatchedTarget = []
                self.unmatchedSource = []
            except Exception as e:
                self._setStatus("❌ Error deleting file: " + str(e), "error")

    def closeEvent(self, event):
        event.accept()


# Launch function
def launchLandmarkMerger():
    for widget in qt.QApplication.topLevelWidgets():
        if isinstance(widget, LandmarkMergerTool):
            widget.raise_()
            widget.activateWindow()
            widget.show()
            return widget
    merger = LandmarkMergerTool(slicer.util.mainWindow())
    merger.show()
    return merger


# Launch the tool
merger = launchLandmarkMerger()

```
