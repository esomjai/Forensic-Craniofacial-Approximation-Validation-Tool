```python
import numpy as np
import slicer
import qt
import vtk
import urllib.request
import tempfile
import os


class PurkaitSinghGUI(qt.QWidget):
    """
    Purkait and Singh (2024; 2026) Nasal Prediction Method.

    Only one 3D soft-tissue landmark is predicted: the pronasale (prn),
    via the regression  prn_perp_baseline = intercept + slope * (bony rhi_perp_baseline),
    placed along the line through ANS perpendicular to the baseline.

    All other regression outputs (bony n-sn, soft n-nt, al-al, nb-nb) and
    FSTT values from the papers are reported as scalars, compared against
    their directly-measured soft-tissue counterparts when PS_soft_tissue
    is loaded. When the "Compare 2024 and 2026" option is selected, both
    regression sets are computed and shown side by side.
    """

    REGRESSION_TABLE = {
        "2024": {
            "male": {
                "bony_n_sn":    (4.385,  0.988),
                "soft_n_nt":    (31.76,  1.009),
                "prn_baseline": (19.544, 0.299),
                "al_al":        (25.256, 0.55),
                "nb_nb":        (33.433, 0.362),
            },
            "female": {
                "bony_n_sn":    (7.673,  0.909),
                "soft_n_nt":    (33.23,  0.768),
                "prn_baseline": (15.056, 0.622),
                "al_al":        None,
                "nb_nb":        None,
            },
        },
        "2026": {
            "male": {
                "bony_n_sn":    (2.213,  1.037),
                "soft_n_nt":    (36.942, 0.790),
                "prn_baseline": (18.568, 0.480),
                "al_al":        (25.006, 0.557),
                "nb_nb":        (33.594, 0.331),
            },
            "female": {
                "bony_n_sn":    (6.192,  0.946),
                "soft_n_nt":    (33.100, 0.784),
                "prn_baseline": (15.599, 0.555),
                "al_al":        (28.254, 0.255),
                "nb_nb":        (31.279, 0.250),
            },
        },
    }

    REGRESSION_LABEL = {
        "2024": {
            "male":   "prn_perp_baseline = 19.544 + 0.299 * (bony rhi_perp_baseline)  [2024 male, R^2=0.049, SEE=2.208]",
            "female": "prn_perp_baseline = 15.056 + 0.622 * (bony rhi_perp_baseline)  [2024 female, R^2=0.189, SEE=1.576]",
        },
        "2026": {
            "male":   "prn_perp_baseline = 18.568 + 0.480 * (bony rhi_perp_baseline)  [2026 male, R^2=0.098, SEE=2.258]",
            "female": "prn_perp_baseline = 15.599 + 0.555 * (bony rhi_perp_baseline)  [2026 female, R^2=0.144, SEE=1.822]",
        },
    }

    FSTT_TABLE = {
        "2024": {
            "n":   {"male": 5.02,  "female": 3.97},
            "rhi": {"male": 1.20,  "female": 0.85},
            "sn":  {"male": 11.61, "female": 10.27},
        },
        "2026": {
            "n":   {"male": 5.54,  "female": 4.33},
            "rhi": {"male": 1.44,  "female": 0.98},
            "sn":  {"male": 12.17, "female": 10.12},
        },
    }

    def detectRunCombinations(self):
        """Scan the scene for prn predictions and return a set of
        (version, sex) combinations that were run. Also rebuilds
        self.prn_predictions.

        Recognises labels of the form:
            prn_<sex>_<version>
        plus tolerant variants such as 'prn_m_2024', 'prn_male_2024',
        'prn_2024_male', 'prn_F_2026', etc.
        """
        import re

        sex_aliases = {
            "m": "male", "male": "male",
            "f": "female", "female": "female",
        }
        version_aliases = {
            "2024": "2024", "24": "2024",
            "2026": "2026", "26": "2026",
        }

        # Look for prediction nodes under common names
        pred_node = None
        for name in ["lmrk_predictions", "predicted_landmarks",
                     "predictions", "pred_landmarks"]:
            node = slicer.util.getFirstNodeByName(name)
            if node and "Fiducial" in node.GetClassName():
                pred_node = node
                break

        self.prn_predictions = {}
        combos = set()

        if pred_node is None:
            return combos

        for i in range(pred_node.GetNumberOfControlPoints()):
            label = pred_node.GetNthControlPointLabel(i)
            if not label.lower().startswith("prn"):
                continue

            # tokenise: split on '_' or '-'
            tokens = re.split(r"[_\-]+", label)
            tokens = [t.lower() for t in tokens if t]

            sex = None
            version = None
            for t in tokens:
                if t in sex_aliases and sex is None:
                    sex = sex_aliases[t]
                if t in version_aliases and version is None:
                    version = version_aliases[t]

            if sex is None or version is None:
                # Can't interpret this label; skip but note it
                print("Skipping prediction label (unrecognised format): "
                      "'{0}'".format(label))
                continue

            point = np.array(pred_node.GetNthControlPointPositionWorld(i))
            self.prn_predictions[label] = {
                "prn": point,
                "predicted_distance": None,
                "rhi_to_baseline_length": None,
                "regression_sex": sex,
                "study_version": version,
            }
            combos.add((version, sex))

        print("Detected prediction combinations: {0}".format(sorted(combos)))
        return combos

    def preselectVersionFromScene(self):
        """Set the Step 3 version radios and Step 4 sex radios to match
        whatever combinations are actually present in the scene."""
        combos = self.detectRunCombinations()
        if not combos:
            return

        versions = {v for v, s in combos}
        sexes    = {s for v, s in combos}

        if versions == {"2024"}:
            self.version2024Radio.setChecked(True)
        elif versions == {"2026"}:
            self.version2026Radio.setChecked(True)
        elif versions == {"2024", "2026"}:
            self.versionBothRadio.setChecked(True)

        if sexes == {"male"}:
            self.maleRadio.setChecked(True)
        elif sexes == {"female"}:
            self.femaleRadio.setChecked(True)
        elif sexes == {"male", "female"}:
            self.bothRadio.setChecked(True)

    def isSceneComplete(self):
        """True if every node required for the full report is present
        in the scene."""
        if self.hardTissueNode is None:
            return False
        if self.hardTissueNode.GetNumberOfControlPoints() < 8:
            return False
        if self.softTissueNode is None:
            return False
        if self.fhpNode is None:
            return False
        if self.mspNode is None:
            return False

        # Use detectRunCombinations() so we know which (version, sex)
        # pairs are actually in the scene
        combos = self.detectRunCombinations()
        if not combos:
            return False

        return True

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle("Purkait and Singh (2024; 2026) — prn prediction")
        self.setObjectName("PurkaitSinghGUI")

        self.setWindowFlags(qt.Qt.Window)

        self.hardTissueNode = None
        self.softTissueNode = None
        self.mspNode = None
        self.fhpNode = None
        self.all_measurements = {}
        self.prn_predictions = {}

        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setSpacing(10)
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.stepStack = qt.QStackedWidget()
        self.mainLayout.addWidget(self.stepStack)

        self.createAllStepWidgets()
        self.setupNavigation()

        self.currentStep = 0
        self.syncWithScene()
        self.rescanScene()
        self.preselectVersionFromScene()
        self.ensureFhpDetected()
        self.showDetectionSummary()

        # If the entire pipeline output is already in the scene, jump straight
        # to Step 5 so the user can refresh the report without re-running
        # any of the earlier steps.
        if self.isSceneComplete():
            self.currentStep = 4                    # Step 5 (0-indexed)
            self.updateResultsTables()              # populate tables now
            self.step5StatusLabel.setText(
                "Status: All nodes detected — comparisons populated. "
                "Click 'Refresh Comparisons' to re-scan if the scene changes."
            )
            self.step5StatusLabel.setStyleSheet("color: green; font-weight: bold;")
            print("Scene complete: jumping to Step 5 (Refresh Comparisons).")
        else:
            self.currentStep = 0

        self.updateStepUI()

       
    def createAllStepWidgets(self):
        self.createStep1_Welcome()
        self.createStep2_PlaneSetup()
        self.createStep3_Measurements()
        self.createStep4_Prediction()
        self.createStep5_Validation()
        self.createStep6_Results()

    def setupNavigation(self):
        navWidget = qt.QWidget()
        navLayout = qt.QHBoxLayout(navWidget)
        navLayout.setContentsMargins(0, 0, 0, 0)

        self.prevButton = qt.QPushButton("Previous")
        self.prevButton.clicked.connect(self.onPrevButtonClicked)

        self.stepLabel = qt.QLabel("Step 1/6")
        self.stepLabel.setAlignment(qt.Qt.AlignCenter)
        self.stepLabel.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.nextButton = qt.QPushButton("Next")
        self.nextButton.clicked.connect(self.onNextButtonClicked)

        navLayout.addWidget(self.prevButton)
        navLayout.addStretch(1)
        navLayout.addWidget(self.stepLabel)
        navLayout.addStretch(1)
        navLayout.addWidget(self.nextButton)

        self.mainLayout.addWidget(navWidget)

    def createStep1_Welcome(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Welcome to Purkait and Singh (2024; 2026) Method")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(title)

        desc = qt.QLabel(
            "This tool predicts the pronasale (prn) as a 3D soft-tissue landmark "
            "using the regression equations of Purkait and Singh.\n\n"
            "All other quantities from the papers (bony n-sn, soft n-nt, al-al, nb-nb, "
            "and FSTT values at n, rhi, sn) are reported as scalar measurements and "
            "compared against their directly-measured soft-tissue counterparts when "
            "PS_soft_tissue is loaded.\n\n"
            "Use the 'Compare 2024 and 2026' option in Step 3 to view both regression "
            "sets side by side."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        downloadGroup = qt.QGroupBox("Download Example Landmarks")
        downloadLayout = qt.QVBoxLayout(downloadGroup)

        downloadDesc = qt.QLabel(
            "Click below to download example landmark files from the GitHub repository.\n"
            "These will be automatically loaded into 3D Slicer."
        )
        downloadDesc.setWordWrap(True)
        downloadLayout.addWidget(downloadDesc)

        self.downloadHardButton = qt.QPushButton("Download Hard Tissue Landmarks")
        self.downloadHardButton.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px; font-weight: bold;"
        )
        self.downloadHardButton.clicked.connect(self.onDownloadHardTissue)
        downloadLayout.addWidget(self.downloadHardButton)

        self.downloadSoftButton = qt.QPushButton("Download Soft Tissue Landmarks")
        self.downloadSoftButton.setStyleSheet(
            "background-color: #9b59b6; color: white; padding: 8px; font-weight: bold;"
        )
        self.downloadSoftButton.clicked.connect(self.onDownloadSoftTissue)
        downloadLayout.addWidget(self.downloadSoftButton)

        self.downloadStatusLabel = qt.QLabel("")
        self.downloadStatusLabel.setWordWrap(True)
        downloadLayout.addWidget(self.downloadStatusLabel)

        layout.addWidget(downloadGroup)

        selectionGroup = qt.QGroupBox("Or Select Existing Landmarks")
        selectionLayout = qt.QVBoxLayout(selectionGroup)

        self.hardTissueSelector = slicer.qMRMLNodeComboBox()
        self.hardTissueSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.hardTissueSelector.setMRMLScene(slicer.mrmlScene)
        self.hardTissueSelector.noneEnabled = True
        self.hardTissueSelector.addEnabled = False
        self.hardTissueSelector.removeEnabled = False
        self.hardTissueSelector.selectNodeUponCreation = True
        self.hardTissueSelector.currentNodeChanged.connect(self.onHardTissueSelected)

        formLayout = qt.QFormLayout()
        formLayout.addRow("Hard Tissue Landmarks:", self.hardTissueSelector)
        selectionLayout.addLayout(formLayout)

        layout.addWidget(selectionGroup)

        self.step1StatusLabel = qt.QLabel("Status: Download landmarks or select 'PS_hard_tissue' node.")
        self.step1StatusLabel.setWordWrap(True)
        layout.addWidget(self.step1StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def onDownloadHardTissue(self):
        try:
            self.downloadStatusLabel.setText("Downloading hard tissue landmarks...")
            slicer.app.processEvents()

            url = "https://github.com/user-attachments/files/21217369/PS_hard_tissue.mrk.json"
            temp_file = os.path.join(tempfile.gettempdir(), "PS_hard_tissue.mrk.json")

            urllib.request.urlretrieve(url, temp_file)
            success = slicer.util.loadMarkups(temp_file)

            if success:
                self.hardTissueNode = slicer.util.getNode("PS_hard_tissue")
                self.hardTissueSelector.setCurrentNode(self.hardTissueNode)

                self.downloadStatusLabel.setText("Hard tissue landmarks downloaded and loaded successfully.")
                self.step1StatusLabel.setText("Status: Hard tissue landmarks ready.")
                self.step1StatusLabel.setStyleSheet("color: green; font-weight: bold;")
                slicer.util.showStatusMessage("Hard tissue landmarks loaded.", 3000)
            else:
                raise Exception("Failed to load file")

        except Exception as e:
            self.downloadStatusLabel.setText("Error: {0}".format(str(e)))
            slicer.util.errorDisplay("Failed to download hard tissue landmarks: {0}".format(str(e)))

    def onDownloadSoftTissue(self):
        try:
            self.downloadStatusLabel.setText("Downloading soft tissue landmarks...")
            slicer.app.processEvents()

            url = "https://github.com/user-attachments/files/21217705/PS_soft_tissue.mrk.json"
            temp_file = os.path.join(tempfile.gettempdir(), "PS_soft_tissue.mrk.json")

            urllib.request.urlretrieve(url, temp_file)
            success = slicer.util.loadMarkups(temp_file)

            if success:
                self.softTissueNode = slicer.util.getNode("PS_soft_tissue")
                if hasattr(self, 'softTissueSelector'):
                    self.softTissueSelector.setCurrentNode(self.softTissueNode)

                self.downloadStatusLabel.setText("Soft tissue landmarks downloaded and loaded successfully.")
                slicer.util.showStatusMessage("Soft tissue landmarks loaded.", 3000)
            else:
                raise Exception("Failed to load file")

        except Exception as e:
            self.downloadStatusLabel.setText("Error: {0}".format(str(e)))
            slicer.util.errorDisplay("Failed to download soft tissue landmarks: {0}".format(str(e)))

    def createStep2_PlaneSetup(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 2: Setup Reference Planes")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        mspGroup = qt.QGroupBox("Midsagittal Plane (MSP)")
        mspLayout = qt.QVBoxLayout(mspGroup)

        mspDesc = qt.QLabel("Create MSP using best-fit through: nasion, rhinion, subspinale, and ANS.")
        mspDesc.setWordWrap(True)
        mspLayout.addWidget(mspDesc)

        self.createMSPButton = qt.QPushButton("Create MSP from Landmarks")
        self.createMSPButton.clicked.connect(self.onCreateMSP)
        mspLayout.addWidget(self.createMSPButton)

        layout.addWidget(mspGroup)

        fhpGroup = qt.QGroupBox("Frankfurt Horizontal Plane (FHP)")
        fhpLayout = qt.QVBoxLayout(fhpGroup)

        fhpDesc = qt.QLabel("Please ensure you have created your FHP before proceeding.")
        fhpDesc.setWordWrap(True)
        fhpLayout.addWidget(fhpDesc)

        self.fhpSelector = slicer.qMRMLNodeComboBox()
        self.fhpSelector.nodeTypes = ["vtkMRMLMarkupsPlaneNode"]
        self.fhpSelector.setMRMLScene(slicer.mrmlScene)
        self.fhpSelector.noneEnabled = True
        self.fhpSelector.selectNodeUponCreation = True
        self.fhpSelector.currentNodeChanged.connect(self.onFHPSelected)

        fhpFormLayout = qt.QFormLayout()
        fhpFormLayout.addRow("FHP Plane:", self.fhpSelector)
        fhpLayout.addLayout(fhpFormLayout)

        layout.addWidget(fhpGroup)

        self.step2StatusLabel = qt.QLabel("Status: Please create MSP and select FHP.")
        self.step2StatusLabel.setWordWrap(True)
        layout.addWidget(self.step2StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep3_Measurements(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 3: Create Hard Tissue Measurements")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        desc = qt.QLabel(
            "This step creates all hard-tissue guide lines and measurements. "
            "These feed the prn regression and provide the inputs for all other "
            "regression-derived scalar values reported in Step 6."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        versionGroup = qt.QGroupBox("Study Version")
        versionLayout = qt.QVBoxLayout(versionGroup)

        self.version2024Radio = qt.QRadioButton(
            "Purkait and Singh (2024)  —  n = 200 (100 males; 100 females)"
        )
        self.version2026Radio = qt.QRadioButton(
            "Purkait and Singh (2026)  —  n = 409 (226 males; 183 females)"
        )
        self.versionBothRadio = qt.QRadioButton(
            "Compare 2024 and 2026  —  run both regression sets and show paired values"
        )
        self.version2024Radio.setChecked(True)
        versionLayout.addWidget(self.version2024Radio)
        versionLayout.addWidget(self.version2026Radio)
        versionLayout.addWidget(self.versionBothRadio)
        layout.addWidget(versionGroup)

        self.createMeasurementsButton = qt.QPushButton("Create All Measurements")
        self.createMeasurementsButton.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px; font-weight: bold;"
        )
        self.createMeasurementsButton.clicked.connect(self.onCreateMeasurements)
        layout.addWidget(self.createMeasurementsButton)

        self.step3StatusLabel = qt.QLabel("Status: Ready to create measurements.")
        self.step3StatusLabel.setWordWrap(True)
        layout.addWidget(self.step3StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def getStudyVersion(self):
        """Returns '2024', '2026' or 'both'."""
        if self.versionBothRadio.isChecked():
            return "both"
        return "2026" if self.version2026Radio.isChecked() else "2024"

    def getActiveVersions(self):
        """Returns the list of version keys that should be run."""
        v = self.getStudyVersion()
        if v == "both":
            return ["2024", "2026"]
        return [v]

    def getActiveSexes(self):
        if self.bothRadio.isChecked():
            return ["male", "female"]
        if self.femaleRadio.isChecked():
            return ["female"]
        return ["male"]

    def createStep4_Prediction(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 4: Predict Pronasale (prn)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        desc = qt.QLabel(
            "The pronasale (prn) is the only soft-tissue landmark predicted as a 3D point. "
            "Its position is determined by the regression equation\n\n"
            "    prn_perp_baseline = intercept + slope * (bony rhi_perp_baseline)\n\n"
            "combined with the geometric constraint that prn lies on the line through ANS "
            "perpendicular to the baseline (anteriorly). No FSTT value is required.\n\n"
            "If 'Compare 2024 and 2026' was selected in Step 3, one prediction row is produced "
            "per (version, sex) combination."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        sexGroup = qt.QGroupBox("Regression Equation to Use (Sex)")
        sexLayout = qt.QVBoxLayout(sexGroup)

        sexButtonLayout = qt.QHBoxLayout()
        self.maleRadio = qt.QRadioButton("Male")
        self.femaleRadio = qt.QRadioButton("Female")
        self.bothRadio = qt.QRadioButton("Both (for comparison)")
        self.maleRadio.setChecked(True)

        sexButtonLayout.addWidget(self.maleRadio)
        sexButtonLayout.addWidget(self.femaleRadio)
        sexButtonLayout.addWidget(self.bothRadio)
        sexButtonLayout.addStretch()
        sexLayout.addLayout(sexButtonLayout)

        layout.addWidget(sexGroup)

        self.showLinesCheckbox = qt.QCheckBox("Show visualization lines (ANS perpendicular, ANS to prn)")
        self.showLinesCheckbox.setChecked(True)
        layout.addWidget(self.showLinesCheckbox)

        self.predictButton = qt.QPushButton("Run prn Prediction")
        self.predictButton.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px; font-weight: bold;"
        )
        self.predictButton.clicked.connect(self.onRunPrediction)
        layout.addWidget(self.predictButton)

        self.step4StatusLabel = qt.QLabel("Status: Ready to predict.")
        self.step4StatusLabel.setWordWrap(True)
        layout.addWidget(self.step4StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep5_Validation(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 5: Validation (Optional)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        desc = qt.QLabel(
            "Load ground-truth soft-tissue landmarks to enable comparison of all "
            "regression-derived values and FSTT values against their directly-measured "
            "counterparts in Step 6."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.softTissueSelector = slicer.qMRMLNodeComboBox()
        self.softTissueSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.softTissueSelector.setMRMLScene(slicer.mrmlScene)
        self.softTissueSelector.noneEnabled = True
        self.softTissueSelector.selectNodeUponCreation = True
        self.softTissueSelector.currentNodeChanged.connect(self.onSoftTissueSelected)

        formLayout = qt.QFormLayout()
        formLayout.addRow("Soft Tissue Landmarks:", self.softTissueSelector)
        layout.addLayout(formLayout)

        self.calculateErrorButton = qt.QPushButton("Refresh Comparisons")
        self.calculateErrorButton.setStyleSheet(
            "background-color: #9b59b6; color: white; padding: 8px; font-weight: bold;"
        )
        self.calculateErrorButton.clicked.connect(self.onCalculateErrors)
        layout.addWidget(self.calculateErrorButton)

        self.step5StatusLabel = qt.QLabel("Status: Optional step.")
        self.step5StatusLabel.setWordWrap(True)
        layout.addWidget(self.step5StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep6_Results(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        title = qt.QLabel("Step 6: Results and Export")
        title.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 10px;")
        title.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(title)

        # ========== TABLE 1 ==========
        coordLabel = qt.QLabel("<b>Table 1 — Predicted vs True Coordinates (prn only)</b>")
        coordLabel.setStyleSheet("font-size: 14px; margin-top: 15px; margin-bottom: 5px;")
        layout.addWidget(coordLabel)

        coordDesc = qt.QLabel(
            "RAS coordinate system (Right, Anterior, Superior). One row per (study version, sex) "
            "prn prediction. When 'Compare 2024 and 2026' is used, each version's regression equation "
            "is stated in the second column so the two predictions can be compared."
        )
        coordDesc.setWordWrap(True)
        coordDesc.setStyleSheet("margin-bottom: 10px; color: #666; padding: 5px; background-color: #f5f5f5; border-radius: 4px;")
        layout.addWidget(coordDesc)

        self.coordinatesTable = qt.QTableWidget()
        self.coordinatesTable.setColumnCount(9)
        self.coordinatesTable.setHorizontalHeaderLabels([
            "Prediction ID",
            "Regression Equation",
            "Pred X", "Pred Y", "Pred Z",
            "True X", "True Y", "True Z",
            "3D Error (mm)"
        ])

        coordHeader = self.coordinatesTable.horizontalHeader()
        coordHeader.setSectionResizeMode(0, qt.QHeaderView.ResizeToContents)
        coordHeader.setSectionResizeMode(1, qt.QHeaderView.Interactive)
        for col in range(2, 9):
            coordHeader.setSectionResizeMode(col, qt.QHeaderView.ResizeToContents)

        self.coordinatesTable.setColumnWidth(1, 440)
        self.coordinatesTable.setMinimumHeight(150)
        self.coordinatesTable.setMaximumHeight(320)
        self.coordinatesTable.setAlternatingRowColors(True)
        self.coordinatesTable.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        layout.addWidget(self.coordinatesTable)

        spacer1 = qt.QLabel()
        spacer1.setFixedHeight(15)
        layout.addWidget(spacer1)

        # ========== TABLE 2 ==========
        measLabel = qt.QLabel("<b>Table 2 — Measurements: Calculated vs True (2024 &amp; 2026 side by side)</b>")
        measLabel.setStyleSheet("font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(measLabel)

        measDesc = qt.QLabel(
            "<b>Columns:</b> one row per measurement; 2024 and 2026 columns sit side by side. "
            "Blank cells (light grey) mean that version/sex combination was not run or the "
            "regression is not applicable (e.g. 2024 female al-al and nb-nb are not significant). "
            "Green background = |value - true| ≤ 2 mm; yellow = 2-5 mm; red = &gt; 5 mm. "
            "<b>Type key:</b> <i>input</i> = hard-tissue measurement; "
            "<i>regression</i> = value from the paper's equation; "
            "<i>FSTT</i> = paper-reported soft-tissue thickness; "
            "<i>true-only</i> = soft-tissue measurement with no regression counterpart."
        )
        measDesc.setWordWrap(True)
        measDesc.setStyleSheet("margin-bottom: 10px; color: #666; padding: 5px; background-color: #f5f5f5; border-radius: 4px;")
        layout.addWidget(measDesc)

        self.measurementsTable = qt.QTableWidget()
        self.measurementsTable.setColumnCount(8)
        self.measurementsTable.setHorizontalHeaderLabels([
            "Measurement", "Type",
            "2024 M", "2024 F",
            "2026 M", "2026 F",
            "True", "Unit"
        ])

        measHeader = self.measurementsTable.horizontalHeader()
        measHeader.setSectionResizeMode(0, qt.QHeaderView.Stretch)
        for col in range(1, 8):
            measHeader.setSectionResizeMode(col, qt.QHeaderView.ResizeToContents)

        self.measurementsTable.setMinimumHeight(450)
        self.measurementsTable.setMaximumHeight(700)
        self.measurementsTable.setAlternatingRowColors(True)
        self.measurementsTable.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        layout.addWidget(self.measurementsTable)

        # ========== BUTTONS ==========
        buttonLayout = qt.QHBoxLayout()
        buttonLayout.setSpacing(10)

        self.copyAllButton = qt.QPushButton("Copy All")
        self.copyAllButton.setStyleSheet(
            "background-color: #e67e22; color: white; padding: 8px; font-weight: bold; min-width: 150px;"
        )
        self.copyAllButton.clicked.connect(self.onCopyAll)
        buttonLayout.addWidget(self.copyAllButton)

        self.copyCoordinatesButton = qt.QPushButton("Copy Table 1")
        self.copyCoordinatesButton.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px; font-weight: bold; min-width: 150px;"
        )
        self.copyCoordinatesButton.clicked.connect(self.onCopyCoordinates)
        buttonLayout.addWidget(self.copyCoordinatesButton)

        self.copyMeasurementsButton = qt.QPushButton("Copy Table 2")
        self.copyMeasurementsButton.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px; font-weight: bold; min-width: 150px;"
        )
        self.copyMeasurementsButton.clicked.connect(self.onCopyMeasurements)
        buttonLayout.addWidget(self.copyMeasurementsButton)

        buttonLayout.addStretch(1)

        self.finishButton = qt.QPushButton("Finish")
        self.finishButton.setStyleSheet("padding: 8px; min-width: 100px;")
        self.finishButton.clicked.connect(lambda: self.close())
        buttonLayout.addWidget(self.finishButton)

        layout.addLayout(buttonLayout)
        layout.addStretch(1)

        self.step6StatusLabel = qt.QLabel("Status: Review results above.")
        self.step6StatusLabel.setWordWrap(True)
        self.step6StatusLabel.setStyleSheet("margin-top: 15px; color: #666; padding: 5px;")
        layout.addWidget(self.step6StatusLabel)

        scrollArea = qt.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(widget)

        container = qt.QWidget()
        containerLayout = qt.QVBoxLayout(container)
        containerLayout.addWidget(scrollArea)

        self.stepStack.addWidget(container)

    # ==================== SCENE SYNC ====================

    def syncWithScene(self):
        possible_hard_names = ["PS_hard_tissue", "hard_tissue", "Hard_tissue", "hard", "Hard Tissue", "HardTissue"]
        for name in possible_hard_names:
            node = slicer.util.getFirstNodeByName(name)
            if node:
                self.hardTissueNode = node
                self.hardTissueSelector.setCurrentNode(node)
                print("Auto-detected hard tissue: '{0}'".format(name))
                break

        possible_msp_names = ["MSP", "msp", "Midsagittal", "midsagittal", "Mid-Sagittal", "mid-sagittal"]
        for name in possible_msp_names:
            node = slicer.util.getFirstNodeByName(name)
            if node:
                self.mspNode = node
                print("Auto-detected MSP: '{0}'".format(name))
                break

        possible_fhp_names = ["FHP", "fhp", "Frankfurt", "frankfurt", "Frankfort", "frankfort",
                              "FH", "fh", "Frankfurt Horizontal", "frankfurt horizontal"]
        for name in possible_fhp_names:
            node = slicer.util.getFirstNodeByName(name)
            if node:
                self.fhpNode = node
                self.fhpSelector.setCurrentNode(node)
                print("Auto-detected FHP: '{0}'".format(name))
                break

        possible_soft_names = ["PS_soft_tissue", "soft_tissue", "Soft_tissue", "soft", "Soft Tissue", "SoftTissue"]
        for name in possible_soft_names:
            node = slicer.util.getFirstNodeByName(name)
            if node:
                self.softTissueNode = node
                if hasattr(self, 'softTissueSelector'):
                    self.softTissueSelector.setCurrentNode(node)
                print("Auto-detected soft tissue: '{0}'".format(name))
                break

    def showDetectionSummary(self):
        detected = []
        if self.hardTissueNode:
            detected.append("Hard tissue landmarks")
        if self.mspNode:
            detected.append("MSP plane")
        if self.fhpNode:
            detected.append("FHP plane")
        if self.softTissueNode:
            detected.append("Soft tissue landmarks")

        if detected:
            summary = "Auto-detected nodes:\n" + "\n".join(detected)
            print("\n" + "=" * 50)
            print(summary)
            print("=" * 50 + "\n")
            slicer.util.showStatusMessage("Auto-detection complete.", 3000)

            if self.hardTissueNode:
                self.step1StatusLabel.setText("Status: Hard tissue detected.")
                self.step1StatusLabel.setStyleSheet("color: green; font-weight: bold;")
        else:
            print("No existing nodes detected. Please load or create landmarks.")

    # ==================== HELPERS ====================

    def getPoint(self, node, index):
        point = [0, 0, 0]
        node.GetNthControlPointPosition(index, point)
        return np.array(point)

    def getPointByLabel(self, node, label):
        for i in range(node.GetNumberOfControlPoints()):
            if node.GetNthControlPointLabel(i) == label:
                return self.getPoint(node, i)
        raise ValueError("Point '{0}' not found".format(label))

    def getPlaneData(self, planeNode):
        if 'Plane' in planeNode.GetClassName():
            origin = [0, 0, 0]
            normal = [0, 0, 0]
            planeNode.GetOrigin(origin)
            planeNode.GetNormal(normal)
            return np.array(origin), np.array(normal)
        else:
            raise ValueError("Node is not a plane")

    def createLine(self, p1, p2, name, color=[1.0, 1.0, 1.0], selected_color=[1.0, 0.5, 0.0], thickness=0.25):
        existing = slicer.util.getFirstNodeByName(name)
        if existing:
            slicer.mrmlScene.RemoveNode(existing)

        lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
        lineNode.AddControlPoint(p1.tolist())
        lineNode.AddControlPoint(p2.tolist())

        displayNode = lineNode.GetDisplayNode()
        if displayNode:
            displayNode.SetColor(*color)
            displayNode.SetSelectedColor(*selected_color)
            displayNode.SetLineThickness(thickness)
            displayNode.SetGlyphScale(1.8)

        return lineNode

    def getLineLength(self, lineNode):
        start = [0, 0, 0]
        end = [0, 0, 0]
        lineNode.GetNthControlPointPosition(0, start)
        lineNode.GetNthControlPointPosition(1, end)
        return float(np.linalg.norm(np.array(end) - np.array(start)))

    def storeMeasurement(self, name, value, unit="mm"):
        self.all_measurements[name] = {"value": float(value), "unit": unit}

    def onHardTissueSelected(self, node):
        if node:
            self.hardTissueNode = node
            self.step1StatusLabel.setText("Status: Selected '{0}'.".format(node.GetName()))
            self.step1StatusLabel.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.hardTissueNode = None
            self.step1StatusLabel.setText("Status: Download landmarks or select 'PS_hard_tissue' node.")
            self.step1StatusLabel.setStyleSheet("")

    def onFHPSelected(self, node):
        if node:
            self.fhpNode = node
            self.updateStep2Status()
        else:
            self.fhpNode = None
            self.updateStep2Status()

    def onSoftTissueSelected(self, node):
        if node:
            self.softTissueNode = node
            self.step5StatusLabel.setText("Status: Selected '{0}'.".format(node.GetName()))
            self.step5StatusLabel.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.softTissueNode = None
            self.step5StatusLabel.setText("Status: Optional step.")
            self.step5StatusLabel.setStyleSheet("")

    def updateStep2Status(self):
        if self.mspNode and self.fhpNode:
            self.step2StatusLabel.setText("Status: MSP and FHP ready. Click 'Next' to continue.")
            self.step2StatusLabel.setStyleSheet("color: green; font-weight: bold;")
        elif self.mspNode:
            self.step2StatusLabel.setText("Status: MSP created. Please select FHP plane.")
            self.step2StatusLabel.setStyleSheet("color: orange; font-weight: bold;")
        elif self.fhpNode:
            self.step2StatusLabel.setText("Status: FHP selected. Please create MSP.")
            self.step2StatusLabel.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.step2StatusLabel.setText("Status: Please create MSP and select FHP.")
            self.step2StatusLabel.setStyleSheet("color: red; font-weight: bold;")

    def onCreateMSP(self):
        try:
            if not self.hardTissueNode:
                raise ValueError("Please select hard tissue landmarks first.")
            self.ensureFhpDetected()   # <-- add this
            if not self.fhpNode:
                raise ValueError("Please create or select the FHP first.")

            self.step2StatusLabel.setText("Status: Creating MSP...")
            slicer.app.processEvents()

            points = []
            for i in range(4):
                points.append(self.getPoint(self.hardTissueNode, i))
            points = np.array(points)

            centroid = np.mean(points, axis=0)
            pts_centered = points - centroid
            U, S, Vt = np.linalg.svd(pts_centered)
            normal = Vt[2, :]

            existing = slicer.util.getFirstNodeByName('MSP')
            if existing:
                slicer.mrmlScene.RemoveNode(existing)

            self.mspNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP')
            self.mspNode.SetOriginWorld(centroid)
            self.mspNode.SetNormalWorld(normal)

            self.updateStep2Status()
            slicer.util.showStatusMessage("MSP created.", 3000)
            print("MSP created from landmarks.")

        except Exception as e:
            self.step2StatusLabel.setText("Status: Error - {0}".format(str(e)))
            self.step2StatusLabel.setStyleSheet("color: red; font-weight: bold;")
            slicer.util.errorDisplay("Failed to create MSP: {0}".format(str(e)))

    def onCreateMeasurements(self):
        try:
            self.ensureFhpDetected()
            if not all([self.hardTissueNode, self.mspNode, self.fhpNode]):
                raise ValueError("Please complete previous steps first.")

            self.step3StatusLabel.setText("Status: Creating measurements...")
            slicer.app.processEvents()

            msp_origin, msp_normal = self.getPlaneData(self.mspNode)
            fhp_origin, fhp_normal = self.getPlaneData(self.fhpNode)

            line_direction = np.cross(msp_normal, fhp_normal)
            line_direction = line_direction / np.linalg.norm(line_direction)

            length = 70.0
            half_vec = 0.5 * length * line_direction
            fhp_start = msp_origin - half_vec
            fhp_end = msp_origin + half_vec

            self.createLine(fhp_start, fhp_end, 'FHP guide', [1.0, 1.0, 1.0], [1.0, 0.0, 0.0])

            guide_names = ['st n guide', 'st rhi guide', 'st sn guide']
            guide_colors = {
                'st n guide':   ([1.0, 1.0, 1.0], [0.0, 1.0, 0.0]),
                'st rhi guide': ([1.0, 1.0, 1.0], [0.0, 0.0, 1.0]),
                'st sn guide':  ([1.0, 1.0, 1.0], [1.0, 1.0, 0.0]),
            }

            for i, name in enumerate(guide_names):
                landmark_pos = self.getPoint(self.hardTissueNode, i)
                start = landmark_pos - half_vec
                end = landmark_pos + half_vec
                self.createLine(start, end, name, *guide_colors[name])

            baseline_start = self.getPoint(self.hardTissueNode, 0)
            baseline_end = self.getPoint(self.hardTissueNode, 3)
            baseline_line = self.createLine(baseline_start, baseline_end, 'baseline',
                                            [1.0, 1.0, 1.0], [1.0, 0.5, 0.0])
            self.storeMeasurement("bony n-ans (baseline)", self.getLineLength(baseline_line))

            n_to_rhi_line = self.createLine(
                self.getPoint(self.hardTissueNode, 0),
                self.getPoint(self.hardTissueNode, 1),
                'n to rhi', [1.0, 1.0, 1.0], [0.5, 0.0, 0.5])
            self.storeMeasurement("bony n-rhi", self.getLineLength(n_to_rhi_line))

            rhi_point = self.getPoint(self.hardTissueNode, 1)
            baseline_vec = baseline_end - baseline_start
            line_unit_vec = baseline_vec / np.linalg.norm(baseline_vec)
            v = rhi_point - baseline_start
            proj_length = np.dot(v, line_unit_vec)
            closest_point = baseline_start + proj_length * line_unit_vec
            rhi_to_baseline_line = self.createLine(rhi_point, closest_point, 'rhi to baseline',
                                                   [1.0, 1.0, 1.0], [0.7, 0.3, 0.3])
            self.storeMeasurement("bony rhi perp baseline", self.getLineLength(rhi_to_baseline_line))

            ab_line = self.createLine(
                self.getPoint(self.hardTissueNode, 4),
                self.getPoint(self.hardTissueNode, 5),
                'AB', [1.0, 1.0, 1.0], [1.0, 0.0, 1.0])
            self.storeMeasurement("AB", self.getLineLength(ab_line))

            cd_line = self.createLine(
                self.getPoint(self.hardTissueNode, 6),
                self.getPoint(self.hardTissueNode, 7),
                'CD', [1.0, 1.0, 1.0], [0.0, 1.0, 1.0])
            self.storeMeasurement("CD", self.getLineLength(cd_line))

            n_ss_line = self.createLine(
                self.getPoint(self.hardTissueNode, 0),
                self.getPoint(self.hardTissueNode, 2),
                'bony n-ss', [1.0, 1.0, 1.0], [0.2, 0.7, 0.2])
            self.storeMeasurement("bony n-ss (measured)", self.getLineLength(n_ss_line))

            self.step3StatusLabel.setText(
                "Status: Measurements created (version selection: {0}).".format(self.getStudyVersion())
            )
            self.step3StatusLabel.setStyleSheet("color: green; font-weight: bold;")
            slicer.util.showStatusMessage("Measurements created.", 3000)

            self.updateResultsTables()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.step3StatusLabel.setText("Status: Error - {0}".format(str(e)))
            self.step3StatusLabel.setStyleSheet("color: red; font-weight: bold;")
            slicer.util.errorDisplay("Failed to create measurements: {0}".format(str(e)))

    # ==================== PREDICTION ====================

    def runPrnPrediction(self, regression_sex, version):
        coeffs = self.REGRESSION_TABLE.get(version, {}).get(regression_sex, {})
        prn_coeffs = coeffs.get("prn_baseline", None)
        if prn_coeffs is None:
            raise ValueError("No prn regression available for version {0}, sex {1}.".format(version, regression_sex))

        baselineNode = slicer.util.getNode('baseline')
        rhiToBaselineNode = slicer.util.getNode('rhi to baseline')
        if not all([self.hardTissueNode, baselineNode, rhiToBaselineNode, self.mspNode]):
            raise ValueError("Required measurements not found. Please run Step 3.")

        msp_origin, msp_normal = self.getPlaneData(self.mspNode)
        ans_point = self.getPoint(self.hardTissueNode, 3)

        baseline_start = self.getPoint(baselineNode, 0)
        baseline_end = self.getPoint(baselineNode, 1)
        baseline_vec = baseline_end - baseline_start
        baseline_unit = baseline_vec / np.linalg.norm(baseline_vec)

        perp_vec = np.cross(baseline_unit, msp_normal)
        perp_vec = perp_vec / np.linalg.norm(perp_vec)
        if perp_vec[1] < 0:
            perp_vec = -perp_vec

        rhi_to_baseline_length = self.getLineLength(rhiToBaselineNode)
        intercept, slope = prn_coeffs
        pred_prn_distance = intercept + slope * rhi_to_baseline_length
        pred_prn_point = ans_point + pred_prn_distance * perp_vec

        return {
            "prn": pred_prn_point,
            "predicted_distance": pred_prn_distance,
            "rhi_to_baseline_length": rhi_to_baseline_length,
            "regression_sex": regression_sex,
            "study_version": version,
        }

    def onRunPrediction(self):
        try:
            self.ensureFhpDetected()
            existing = slicer.util.getFirstNodeByName('lmrk_predictions')
            if existing:
                slicer.mrmlScene.RemoveNode(existing)
            lmrk_pred_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'lmrk_predictions')

            displayNode = lmrk_pred_node.GetDisplayNode()
            if displayNode:
                displayNode.SetColor(0.0, 0.0, 0.8)
                displayNode.SetSelectedColor(1.0, 0.0, 0.0)
                displayNode.SetGlyphScale(1.8)
                displayNode.SetTextScale(3.0)
                displayNode.SetGlyphType(1)
                displayNode.SetSliceProjection(True)

            self.prn_predictions = {}

            versions = self.getActiveVersions()
            sexes = self.getActiveSexes()

            for version in versions:
                for sex in sexes:
                    pred = self.runPrnPrediction(sex, version)
                    combo_key = "prn_{0}_{1}".format(sex, version)
                    self.prn_predictions[combo_key] = pred

                    lmrk_pred_node.AddControlPoint(pred["prn"].tolist(), combo_key)
                    print("Predicted {0} at {1}".format(combo_key, pred["prn"]))

            if self.showLinesCheckbox.isChecked():
                msp_origin, msp_normal = self.getPlaneData(self.mspNode)
                ans_point = self.getPoint(self.hardTissueNode, 3)
                baselineNode = slicer.util.getNode('baseline')
                baseline_start = self.getPoint(baselineNode, 0)
                baseline_end = self.getPoint(baselineNode, 1)
                baseline_unit = (baseline_end - baseline_start) / np.linalg.norm(baseline_end - baseline_start)
                perp_vec = np.cross(baseline_unit, msp_normal)
                perp_vec = perp_vec / np.linalg.norm(perp_vec)
                if perp_vec[1] < 0:
                    perp_vec = -perp_vec

                ans_perp_length = 60.0
                self.createLine(ans_point - (ans_perp_length / 2.0) * perp_vec,
                                ans_point + (ans_perp_length / 2.0) * perp_vec,
                                "ANS_perp", [0.0, 0.8, 0.8], [0.0, 1.0, 1.0])

                for combo_key, pred in self.prn_predictions.items():
                    self.createLine(ans_point, pred["prn"],
                                    "ANS_to_{0}".format(combo_key),
                                    [0.8, 0.8, 0.0], [1.0, 0.7, 0.0])

            self.step4StatusLabel.setText(
                "Status: prn prediction complete ({0} version(s) x {1} sex(es)).".format(
                    len(versions), len(sexes))
            )
            self.step4StatusLabel.setStyleSheet("color: green; font-weight: bold;")
            slicer.util.showStatusMessage("prn prediction complete.", 3000)

            self.updateResultsTables()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.step4StatusLabel.setText("Status: Error - {0}".format(str(e)))
            self.step4StatusLabel.setStyleSheet("color: red; font-weight: bold;")
            slicer.util.errorDisplay("Failed to predict: {0}".format(str(e)))

    # ==================== VALIDATION ====================
    def ensureFhpDetected(self):
        """If self.fhpNode is None, try to find an FHP plane in the scene by name.
        Returns the FHP node (or None). Updates self.fhpNode and the selector."""
        if self.fhpNode is not None:
            return self.fhpNode

        candidates = ["FHP", "fhp", "Frankfurt", "frankfurt",
                      "Frankfort", "frankfort", "FH", "fh",
                      "Frankfurt Horizontal", "frankfurt horizontal",
                      "Frankfurt Horizontal Plane", "FHP plane", "fhp plane"]
        for name in candidates:
            node = slicer.util.getFirstNodeByName(name)
            if node and "Plane" in node.GetClassName():
                self.fhpNode = node
                if hasattr(self, 'fhpSelector'):
                    self.fhpSelector.setCurrentNode(node)
                if hasattr(self, 'step2StatusLabel'):
                    self.updateStep2Status()
                print("Detected FHP: '{0}'".format(name))
                return node

        # ---- Safety net ----
        # No FHP matched by name. If other markups planes exist in the scene,
        # print a helpful note so the user knows why detection failed.
        plane_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsPlaneNode")
        if plane_nodes:
            print("Note: {0} markups plane(s) exist in the scene, but none match "
                  "the FHP naming convention. Please select the FHP manually in "
                  "Step 2.".format(len(plane_nodes)))
        return None

    def rescanScene(self, redrawLines=False):
        """Re-detect nodes present in the scene and rebuild the internal
        dictionaries so results can be reported without re-running the
        workflow. Called at startup and on 'Refresh Comparisons'.

        If redrawLines is True, also recreate the visible scene lines
        (FHP guide, baseline, AB, CD, etc.). Normally False for a simple
        refresh; True only if the user explicitly wants the scene rebuilt.
        """
        # ---------- Node detection ----------
        def find_first(names, classes=None):
            for name in names:
                node = slicer.util.getFirstNodeByName(name)
                if node and (classes is None or node.GetClassName() in classes):
                    return node
            return None

        self.hardTissueNode = find_first(
            ["PS_hard_tissue", "hard_tissue", "Hard_tissue", "hard", "Hard Tissue", "HardTissue"],
            classes=["vtkMRMLMarkupsFiducialNode"]
        )
        self.softTissueNode = find_first(
            ["PS_soft_tissue", "soft_tissue", "Soft_tissue", "soft", "Soft Tissue", "SoftTissue"],
            classes=["vtkMRMLMarkupsFiducialNode"]
        )
        self.mspNode = find_first(
            ["MSP", "msp", "Midsagittal", "midsagittal", "Mid-Sagittal", "mid-sagittal"],
            classes=["vtkMRMLMarkupsPlaneNode"]
        )
        # Try a broad list first, then fall back to the ensure helper
        self.fhpNode = None
        self.fhpNode = find_first(
            ["FHP", "fhp", "Frankfurt", "frankfurt", "Frankfort", "frankfort",
             "FH", "fh", "Frankfurt Horizontal", "frankfurt horizontal",
             "Frankfurt Horizontal Plane", "FHP plane", "fhp plane"],
            classes=["vtkMRMLMarkupsPlaneNode"]
        )
        if self.fhpNode is None:
            # ensureFhpDetected also sets the selector and updates Step 2 status
            self.ensureFhpDetected()

        # Sync UI widgets
        if hasattr(self, 'hardTissueSelector') and self.hardTissueNode:
            self.hardTissueSelector.setCurrentNode(self.hardTissueNode)
        if hasattr(self, 'softTissueSelector') and self.softTissueNode:
            self.softTissueSelector.setCurrentNode(self.softTissueNode)
        if hasattr(self, 'fhpSelector') and self.fhpNode:
            self.fhpSelector.setCurrentNode(self.fhpNode)
        if hasattr(self, 'step1StatusLabel') and self.hardTissueNode:
            self.step1StatusLabel.setText(
                "Status: Hard tissue detected ({0}).".format(self.hardTissueNode.GetName()))
            self.step1StatusLabel.setStyleSheet("color: green; font-weight: bold;")
        if hasattr(self, 'step5StatusLabel') and self.softTissueNode:
            self.step5StatusLabel.setText(
                "Status: Soft tissue detected ({0}).".format(self.softTissueNode.GetName()))
            self.step5StatusLabel.setStyleSheet("color: green; font-weight: bold;")
        if hasattr(self, 'step2StatusLabel'):
            self.updateStep2Status()

        # ---------- Rebuild measurement dictionary ----------
        # The measurements are deterministic given the landmarks, so we can
        # recompute them from scratch without needing the scene lines.
        self.all_measurements = {}
        if self.hardTissueNode and self.hardTissueNode.GetNumberOfControlPoints() >= 8:
            self._recomputeHardTissueMeasurements()
            if redrawLines and self.mspNode and self.fhpNode:
                self._redrawMeasurementLines()

        # ---------- Rebuild prn predictions from lmrk_predictions node ----------
        self.detectRunCombinations()

        # ---------- Summary ----------
        print("Scene rescan complete:")
        print("  hard tissue node:   {0}".format(
            self.hardTissueNode.GetName() if self.hardTissueNode else "None"))
        print("  soft tissue node:   {0}".format(
            self.softTissueNode.GetName() if self.softTissueNode else "None"))
        print("  MSP node:           {0}".format(
            self.mspNode.GetName() if self.mspNode else "None"))
        print("  FHP node:           {0}".format(
            self.fhpNode.GetName() if self.fhpNode else "None"))
        print("  measurements:       {0}".format(len(self.all_measurements)))
        print("  prn predictions:    {0}".format(len(self.prn_predictions)))

    def _recomputeHardTissueMeasurements(self):
        """Recompute the hard-tissue measurements from the landmark node.
        Mirrors the geometry in onCreateMeasurements() but does not draw lines.
        """
        node = self.hardTissueNode
        try:
            n_pt    = self.getPoint(node, 0)
            rhi_pt  = self.getPoint(node, 1)
            ss_pt   = self.getPoint(node, 2)
            ans_pt  = self.getPoint(node, 3)
            a_pt    = self.getPoint(node, 4)
            b_pt    = self.getPoint(node, 5)
            c_pt    = self.getPoint(node, 6)
            d_pt    = self.getPoint(node, 7)
        except Exception as e:
            print("Cannot recompute measurements: {0}".format(e))
            return

        # baseline (n -> ANS)
        baseline_vec = ans_pt - n_pt
        baseline_len = float(np.linalg.norm(baseline_vec))
        self.storeMeasurement("bony n-ans (baseline)", baseline_len)

        # bony n-rhi
        self.storeMeasurement("bony n-rhi", float(np.linalg.norm(rhi_pt - n_pt)))

        # bony rhi perpendicular to baseline
        baseline_unit = baseline_vec / baseline_len if baseline_len > 1e-9 else baseline_vec
        v = rhi_pt - n_pt
        proj_len = float(np.dot(v, baseline_unit))
        closest = n_pt + proj_len * baseline_unit
        self.storeMeasurement("bony rhi perp baseline", float(np.linalg.norm(rhi_pt - closest)))

        # AB, CD
        self.storeMeasurement("AB", float(np.linalg.norm(b_pt - a_pt)))
        self.storeMeasurement("CD", float(np.linalg.norm(d_pt - c_pt)))

        # bony n-ss
        self.storeMeasurement("bony n-ss (measured)", float(np.linalg.norm(ss_pt - n_pt)))

    def onCalculateErrors(self):
        try:
            self.rescanScene(redrawLines=False)
            self.updateResultsTables()
            self.step5StatusLabel.setText(
                "Status: Scene re-scanned. Comparisons refreshed."
            )
            self.step5StatusLabel.setStyleSheet("color: green; font-weight: bold;")
            slicer.util.showStatusMessage("Comparisons refreshed.", 3000)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.step5StatusLabel.setText("Status: Error - {0}".format(str(e)))
            self.step5StatusLabel.setStyleSheet("color: red; font-weight: bold;")
            slicer.util.errorDisplay("Failed to refresh comparisons: {0}".format(str(e)))

    # ==================== MEASUREMENT COMPUTATION ====================

    def shortestDistanceBetweenLines(self, p1, p2, q1, q2):
        v = p2 - p1
        u = q2 - q1
        w0 = p1 - q1

        a = float(np.dot(v, v))
        b = float(np.dot(v, u))
        c = float(np.dot(u, u))
        d = float(np.dot(v, w0))
        e = float(np.dot(u, w0))

        denom = a * c - b * b

        if abs(denom) < 1e-9:
            t = d / a if a > 0 else 0.0
            t = max(0.0, min(1.0, t))
            closest1 = p1 + t * v
            s = 0.5
            closest2 = q1 + s * u
            return closest1, closest2, float(np.linalg.norm(closest2 - closest1))

        s = (b * e - c * d) / denom
        t = (a * e - b * d) / denom
        s = max(0.0, min(1.0, s))
        t = max(0.0, min(1.0, t))

        P = p1 + s * v
        Q = q1 + t * u
        return P, Q, float(np.linalg.norm(P - Q))

    def angle_at(self, a, b, c):
        v1 = a - b
        v2 = c - b
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom < 1e-9:
            return None
        cosang = np.dot(v1, v2) / denom
        cosang = max(-1.0, min(1.0, cosang))
        return float(np.degrees(np.arccos(cosang)))

    def computeTrueMeasurements(self):
        true_meas = {}
        if not self.softTissueNode or not self.hardTissueNode:
            return true_meas

        try:
            n_soft = self.getPointByLabel(self.softTissueNode, "n'")
            rhi_soft = self.getPointByLabel(self.softTissueNode, "rhi'")
            sn_soft = self.getPointByLabel(self.softTissueNode, "sn'")
            prn_soft = self.getPointByLabel(self.softTissueNode, "prn")
            nt_soft = self.getPointByLabel(self.softTissueNode, "nt")
        except ValueError as e:
            print("Could not retrieve soft-tissue landmarks: {0}".format(e))
            return true_meas

        try:
            n_hard = self.getPoint(self.hardTissueNode, 0)
            rhi_hard = self.getPoint(self.hardTissueNode, 1)
            ss_hard = self.getPoint(self.hardTissueNode, 2)
            ans_hard = self.getPoint(self.hardTissueNode, 3)
        except Exception as e:
            print("Could not retrieve hard-tissue landmarks: {0}".format(e))
            return true_meas

        true_meas["FSTT n' (true)"] = float(np.linalg.norm(n_soft - n_hard))
        true_meas["FSTT rhi' (true)"] = float(np.linalg.norm(rhi_soft - rhi_hard))
        true_meas["FSTT sn' (true)"] = float(np.linalg.norm(sn_soft - ss_hard))

        true_meas["bony n-sn (measured)"] = float(np.linalg.norm(ss_hard - n_hard))
        true_meas["soft n-nt (true)"] = float(np.linalg.norm(nt_soft - n_soft))
        true_meas["soft n-sn (true)"] = float(np.linalg.norm(sn_soft - n_soft))

        alL = alR = nbL = nbR = None
        try:
            alL = self.getPointByLabel(self.softTissueNode, "X1(alL)")
            alR = self.getPointByLabel(self.softTissueNode, "X2(alR)")
            true_meas["al-al (true)"] = float(np.linalg.norm(alL - alR))
        except ValueError:
            pass

        try:
            nbL = self.getPointByLabel(self.softTissueNode, "Y1(nbL)")
            nbR = self.getPointByLabel(self.softTissueNode, "Y2(nbR)")
            true_meas["nb-nb (true)"] = float(np.linalg.norm(nbL - nbR))
        except ValueError:
            pass

        if alL is not None and alR is not None and nbL is not None and nbR is not None:
            _, _, xy = self.shortestDistanceBetweenLines(alL, alR, nbL, nbR)
            true_meas["X-Y (true)"] = xy

        baseline_vec = ans_hard - n_hard
        baseline_unit = baseline_vec / np.linalg.norm(baseline_vec)
        v = prn_soft - n_hard
        proj = np.dot(v, baseline_unit)
        closest = n_hard + proj * baseline_unit
        true_meas["prn perp baseline (true)"] = float(np.linalg.norm(prn_soft - closest))

        a = self.angle_at(rhi_soft, prn_soft, sn_soft)
        if a is not None:
            true_meas["soft rhi'-prn-sn' (true)"] = a

        a = self.angle_at(prn_soft, sn_soft, nt_soft)
        if a is not None:
            true_meas["prn-sn'-nt (true)"] = a

        if alL is not None and alR is not None:
            a = self.angle_at(alL, prn_soft, alR)
            if a is not None:
                true_meas["al-prn-al (true)"] = a

        return true_meas

    # ==================== RESULTS TABLES ====================

    def updateResultsTables(self):
        self.updateCoordinatesTable()
        self.updateMeasurementsTable()

    def getTruePrnFromSoftTissue(self):
        if not self.softTissueNode:
            return None
        try:
            return self.getPointByLabel(self.softTissueNode, "prn")
        except ValueError:
            return None

    def updateCoordinatesTable(self):
        rows = list(self.prn_predictions.items())
        self.coordinatesTable.setRowCount(len(rows))

        true_prn = self.getTruePrnFromSoftTissue()

        for row, (combo_key, pred) in enumerate(rows):
            pred_point = pred["prn"]
            sex = pred["regression_sex"]
            version = pred["study_version"]

            id_item = qt.QTableWidgetItem(combo_key)
            id_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            self.coordinatesTable.setItem(row, 0, id_item)

            reg_label = self.REGRESSION_LABEL.get(version, {}).get(sex, "N/A")
            reg_item = qt.QTableWidgetItem(reg_label)
            reg_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            self.coordinatesTable.setItem(row, 1, reg_item)

            for col, val in enumerate([pred_point[0], pred_point[1], pred_point[2]]):
                it = qt.QTableWidgetItem("{0:.2f}".format(val))
                it.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
                self.coordinatesTable.setItem(row, 2 + col, it)

            if true_prn is not None:
                for col, val in enumerate([true_prn[0], true_prn[1], true_prn[2]]):
                    it = qt.QTableWidgetItem("{0:.2f}".format(val))
                    it.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
                    it.setBackground(qt.QColor(220, 255, 220))
                    self.coordinatesTable.setItem(row, 5 + col, it)

                error_3d = float(np.linalg.norm(pred_point - true_prn))
                err_item = qt.QTableWidgetItem("{0:.2f}".format(error_3d))
                err_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
                font = qt.QFont()
                font.setBold(True)
                err_item.setFont(font)
                if error_3d > 5.0:
                    err_item.setBackground(qt.QColor(255, 200, 200))
                elif error_3d > 2.0:
                    err_item.setBackground(qt.QColor(255, 255, 200))
                else:
                    err_item.setBackground(qt.QColor(200, 255, 200))
                self.coordinatesTable.setItem(row, 8, err_item)
            else:
                for col in range(3):
                    it = qt.QTableWidgetItem("N/A")
                    it.setFlags(qt.Qt.ItemIsEnabled)
                    self.coordinatesTable.setItem(row, 5 + col, it)
                it = qt.QTableWidgetItem("N/A")
                it.setFlags(qt.Qt.ItemIsEnabled)
                self.coordinatesTable.setItem(row, 8, it)

        self.coordinatesTable.resizeColumnsToContents()
        self.coordinatesTable.setColumnWidth(1, 440)

    def _regression_scalar(self, version, sex, key, input_value):
        """Return regression scalar for a given version / sex / key, or None."""
        coeffs = self.REGRESSION_TABLE.get(version, {}).get(sex, {}).get(key, None)
        if coeffs is None or input_value is None:
            return None
        intercept, slope = coeffs
        return intercept + slope * input_value

    def updateMeasurementsTable(self):
        """Reorganised Table 2: one row per measurement.
        Columns: Measurement | Type | 2024 M | 2024 F | 2026 M | 2026 F | True | Unit
        Sex and version are expressed as columns, not repeated per-row.
        """
        true_meas = self.computeTrueMeasurements()

        versions = self.getActiveVersions()   # ['2024'], ['2026'], or ['2024','2026']
        sexes = self.getActiveSexes()         # ['male'], ['female'], or ['male','female']

        def allow(version, sex):
            return version in versions and sex in sexes

        # Helper to fetch regression scalar
        def reg(version, sex, key, input_value):
            if not allow(version, sex):
                return None
            return self._regression_scalar(version, sex, key, input_value)

        # Helper to fetch FSTT value
        def fstt(version, sex, landmark_key):
            if not allow(version, sex):
                return None
            return self.FSTT_TABLE.get(version, {}).get(landmark_key, {}).get(sex, None)

        rows = []

        # --- 1. Input (hard-tissue) measurements ---
        # These are physical measurements of the hard tissue, not predictions.
        # They are shown only in the True column; version/sex cells stay blank.
        input_keys = [
            ("bony n-ans (baseline)",  "bony n-ans (baseline)"),
            ("bony n-rhi",             "bony n-rhi"),
            ("bony rhi perp baseline", "bony rhi perp baseline"),
            ("AB",                     "AB"),
            ("CD",                     "CD"),
            ("bony n-ss (measured)",   "bony n-ss (measured)"),
        ]
        for key, label in input_keys:
            if key in self.all_measurements:
                v = self.all_measurements[key]["value"]
                rows.append({
                    "name": label,
                    "type": "input",
                    "v2024M": None, "v2024F": None,
                    "v2026M": None, "v2026F": None,
                    "true": v,           # <- measured value goes here
                    "unit": self.all_measurements[key]["unit"],
                })

        # --- 2. Regression-derived measurements ---
        base_val = self.all_measurements.get("bony n-ans (baseline)", {}).get("value", None)
        nrhi_val = self.all_measurements.get("bony n-rhi", {}).get("value", None)
        rhib_val = self.all_measurements.get("bony rhi perp baseline", {}).get("value", None)
        ab_val   = self.all_measurements.get("AB", {}).get("value", None)
        cd_val   = self.all_measurements.get("CD", {}).get("value", None)

        rows.append({
            "name": "bony n-sn",
            "type": "regression",
            "v2024M": reg("2024", "male",   "bony_n_sn", base_val),
            "v2024F": reg("2024", "female", "bony_n_sn", base_val),
            "v2026M": reg("2026", "male",   "bony_n_sn", base_val),
            "v2026F": reg("2026", "female", "bony_n_sn", base_val),
            "true": true_meas.get("bony n-sn (measured)", None),
            "unit": "mm",
        })

        rows.append({
            "name": "soft n-nt",
            "type": "regression",
            "v2024M": reg("2024", "male",   "soft_n_nt", nrhi_val),
            "v2024F": reg("2024", "female", "soft_n_nt", nrhi_val),
            "v2026M": reg("2026", "male",   "soft_n_nt", nrhi_val),
            "v2026F": reg("2026", "female", "soft_n_nt", nrhi_val),
            "true": true_meas.get("soft n-nt (true)", None),
            "unit": "mm",
        })

        rows.append({
            "name": "prn perp baseline",
            "type": "regression",
            "v2024M": reg("2024", "male",   "prn_baseline", rhib_val),
            "v2024F": reg("2024", "female", "prn_baseline", rhib_val),
            "v2026M": reg("2026", "male",   "prn_baseline", rhib_val),
            "v2026F": reg("2026", "female", "prn_baseline", rhib_val),
            "true": true_meas.get("prn perp baseline (true)", None),
            "unit": "mm",
        })

        rows.append({
            "name": "al-al",
            "type": "regression",
            # 2024 female is None by design (not significant)
            "v2024M": reg("2024", "male",   "al_al", ab_val),
            "v2024F": reg("2024", "female", "al_al", ab_val),
            "v2026M": reg("2026", "male",   "al_al", ab_val),
            "v2026F": reg("2026", "female", "al_al", ab_val),
            "true": true_meas.get("al-al (true)", None),
            "unit": "mm",
            "note": "2024 female al-al regression is not significant (p=0.07) and is intentionally blank.",
        })

        rows.append({
            "name": "nb-nb",
            "type": "regression",
            "v2024M": reg("2024", "male",   "nb_nb", cd_val),
            "v2024F": reg("2024", "female", "nb_nb", cd_val),
            "v2026M": reg("2026", "male",   "nb_nb", cd_val),
            "v2026F": reg("2026", "female", "nb_nb", cd_val),
            "true": true_meas.get("nb-nb (true)", None),
            "unit": "mm",
            "note": "2024 female nb-nb regression is not significant (p=0.269) and is intentionally blank.",
        })

        # --- 3. FSTT values ---
        for landmark_key, label, true_key in [
            ("n",   "FSTT n'",   "FSTT n' (true)"),
            ("rhi", "FSTT rhi'", "FSTT rhi' (true)"),
            ("sn",  "FSTT sn'",  "FSTT sn' (true)"),
        ]:
            rows.append({
                "name": label,
                "type": "FSTT",
                "v2024M": fstt("2024", "male",   landmark_key),
                "v2024F": fstt("2024", "female", landmark_key),
                "v2026M": fstt("2026", "male",   landmark_key),
                "v2026F": fstt("2026", "female", landmark_key),
                "true": true_meas.get(true_key, None),
                "unit": "mm",
            })

        # --- 4. True-only soft-tissue measurements ---
        for label, key in [
            ("soft n-sn",  "soft n-sn (true)"),
            ("X-Y",        "X-Y (true)"),
        ]:
            if key in true_meas:
                rows.append({
                    "name": label,
                    "type": "true-only",
                    "v2024M": None, "v2024F": None,
                    "v2026M": None, "v2026F": None,
                    "true": true_meas[key],
                    "unit": "mm",
                })

        # --- 5. True-only angles ---
        for label, key in [
            ("soft rhi'-prn-sn'", "soft rhi'-prn-sn' (true)"),
            ("prn-sn'-nt",        "prn-sn'-nt (true)"),
            ("al-prn-al",         "al-prn-al (true)"),
        ]:
            if key in true_meas:
                rows.append({
                    "name": label,
                    "type": "true-only",
                    "v2024M": None, "v2024F": None,
                    "v2026M": None, "v2026F": None,
                    "true": true_meas[key],
                    "unit": "degrees",
                })

        # ===== Render =====
        self.measurementsTable.setRowCount(len(rows))

        def fmt(v):
            return "{0:.2f}".format(v) if v is not None else ""

        # Colour a data cell according to |value - true|
        def make_data_cell(value, true_value, unit):
            it = qt.QTableWidgetItem(fmt(value))
            it.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            if value is not None and true_value is not None and unit == "mm":
                diff = abs(value - true_value)
                if diff > 5.0:
                    it.setBackground(qt.QColor(255, 200, 200))
                elif diff > 2.0:
                    it.setBackground(qt.QColor(255, 255, 200))
                else:
                    it.setBackground(qt.QColor(200, 255, 200))
            elif value is not None and true_value is not None and unit == "degrees":
                diff = abs(value - true_value)
                if diff > 5.0:
                    it.setBackground(qt.QColor(255, 200, 200))
                elif diff > 2.0:
                    it.setBackground(qt.QColor(255, 255, 200))
                else:
                    it.setBackground(qt.QColor(200, 255, 200))
            return it

        # Colour empty cells subtly so they don't dominate visually
        def make_blank_cell():
            it = qt.QTableWidgetItem("")
            it.setFlags(qt.Qt.ItemIsEnabled)
            it.setBackground(qt.QColor(250, 250, 250))
            return it

        for r, row in enumerate(rows):
            name_item = qt.QTableWidgetItem(row["name"])
            name_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            if "note" in row and row["note"]:
                name_item.setToolTip(row["note"])

            type_item = qt.QTableWidgetItem(row["type"])
            type_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)

            # Data cells — blank ones use a subtle grey rather than "N/A"
            def cell_for(v):
                if v is None:
                    return make_blank_cell()
                return make_data_cell(v, row["true"], row["unit"])

            c24m = cell_for(row["v2024M"])
            c24f = cell_for(row["v2024F"])
            c26m = cell_for(row["v2026M"])
            c26f = cell_for(row["v2026F"])

            true_item = qt.QTableWidgetItem(fmt(row["true"]))
            true_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            if row["true"] is not None:
                true_item.setBackground(qt.QColor(220, 255, 220))

            unit_item = qt.QTableWidgetItem(row["unit"])
            unit_item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)

            # Light colour band by type
            t = row["type"]
            if t == "regression":
                band = qt.QColor(255, 245, 220)
                for it in (name_item, type_item):
                    it.setBackground(band)
            elif t == "FSTT":
                band = qt.QColor(235, 245, 255)
                for it in (name_item, type_item):
                    it.setBackground(band)
            elif t == "true-only":
                band = qt.QColor(245, 255, 245)
                for it in (name_item, type_item):
                    it.setBackground(band)
            elif t == "input":
                band = qt.QColor(245, 245, 245)
                for it in (name_item, type_item):
                    it.setBackground(band)

            self.measurementsTable.setItem(r, 0, name_item)
            self.measurementsTable.setItem(r, 1, type_item)
            self.measurementsTable.setItem(r, 2, c24m)
            self.measurementsTable.setItem(r, 3, c24f)
            self.measurementsTable.setItem(r, 4, c26m)
            self.measurementsTable.setItem(r, 5, c26f)
            self.measurementsTable.setItem(r, 6, true_item)
            self.measurementsTable.setItem(r, 7, unit_item)

        self.measurementsTable.resizeColumnsToContents()

    # ==================== COPY ====================

    def onCopyCoordinates(self):
        try:
            if self.coordinatesTable.rowCount == 0:
                slicer.util.warningDisplay("No coordinates to copy.")
                return

            export = "\t".join([
                "Prediction ID", "Regression Equation",
                "Pred X", "Pred Y", "Pred Z",
                "True X", "True Y", "True Z",
                "3D Error (mm)"
            ]) + "\n"

            for r in range(self.coordinatesTable.rowCount):
                cells = []
                for c in range(self.coordinatesTable.columnCount):
                    it = self.coordinatesTable.item(r, c)
                    cells.append(it.text() if it else "")
                export += "\t".join(cells) + "\n"

            qt.QApplication.clipboard().setText(export)
            self.step6StatusLabel.setText("Status: Table 1 copied to clipboard.")
            slicer.util.showStatusMessage("Table 1 copied.", 3000)
        except Exception as e:
            slicer.util.errorDisplay("Failed to copy Table 1: {0}".format(str(e)))

    def onCopyMeasurements(self):
        try:
            if self.measurementsTable.rowCount == 0:
                slicer.util.warningDisplay("No measurements to copy.")
                return

            export = "\t".join([
                "Measurement", "Type",
                "2024 M", "2024 F",
                "2026 M", "2026 F",
                "True", "Unit"
            ]) + "\n"

            for r in range(self.measurementsTable.rowCount):
                cells = []
                for c in range(self.measurementsTable.columnCount):
                    it = self.measurementsTable.item(r, c)
                    cells.append(it.text() if it else "")
                export += "\t".join(cells) + "\n"

            qt.QApplication.clipboard().setText(export)
            self.step6StatusLabel.setText("Status: Table 2 copied to clipboard.")
            slicer.util.showStatusMessage("Table 2 copied.", 3000)
        except Exception as e:
            slicer.util.errorDisplay("Failed to copy Table 2: {0}".format(str(e)))

    def onCopyAll(self):
        try:
            blocks = []
            blocks.append("=== SESSION INFO ===")
            blocks.append("Study version selection:\t{0}".format(self.getStudyVersion()))
            blocks.append("")

            blocks.append("=== TABLE 1 — PREDICTED vs TRUE COORDINATES (prn) ===")
            blocks.append("\t".join([
                "Prediction ID", "Regression Equation",
                "Pred X", "Pred Y", "Pred Z",
                "True X", "True Y", "True Z",
                "3D Error (mm)"
            ]))
            for r in range(self.coordinatesTable.rowCount):
                cells = []
                for c in range(self.coordinatesTable.columnCount):
                    it = self.coordinatesTable.item(r, c)
                    cells.append(it.text() if it else "")
                blocks.append("\t".join(cells))
            blocks.append("")

            blocks.append("=== TABLE 2 — MEASUREMENTS: CALCULATED vs TRUE ===")
            blocks.append("\t".join([
                "Measurement", "Type",
                "2024 M", "2024 F",
                "2026 M", "2026 F",
                "True", "Unit"
            ]))
            for r in range(self.measurementsTable.rowCount):
                cells = []
                for c in range(self.measurementsTable.columnCount):
                    it = self.measurementsTable.item(r, c)
                    cells.append(it.text() if it else "")
                blocks.append("\t".join(cells))

            qt.QApplication.clipboard().setText("\n".join(blocks))
            self.step6StatusLabel.setText("Status: All tables copied to clipboard.")
            slicer.util.showStatusMessage("All results copied.", 3000)
        except Exception as e:
            slicer.util.errorDisplay("Failed to copy all results: {0}".format(str(e)))

    # ==================== NAVIGATION ====================

    def onPrevButtonClicked(self):
        if self.currentStep > 0:
            self.currentStep -= 1
            self.updateStepUI()

    def onNextButtonClicked(self):
        if self.currentStep < self.stepStack.count - 1:
            self.currentStep += 1
            self.updateStepUI()

    def updateStepUI(self):
        self.stepStack.setCurrentIndex(self.currentStep)
        self.stepLabel.setText("Step {0}/{1}".format(self.currentStep + 1, self.stepStack.count))
        self.prevButton.setEnabled(self.currentStep > 0)
        self.nextButton.setEnabled(self.currentStep < self.stepStack.count - 1)


# Create and show the widget
widget = PurkaitSinghGUI()
widget.show()

```
