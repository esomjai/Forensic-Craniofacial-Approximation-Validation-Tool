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
import qt
import slicer
import vtk
import numpy as np
import urllib.request
import tempfile
from collections import OrderedDict

class ThitiorulGUI:
    def __init__(self):
        main_window = slicer.util.mainWindow()
        self.mainWidget = qt.QWidget(main_window)
        self.mainWidget.setWindowTitle("Thitiorul (2020) Nose Prediction Method")
        self.mainWidget.setMinimumSize(650, 800)
        self.mainWidget.setWindowFlags(qt.Qt.Window)

        scrollArea = qt.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = qt.QWidget()
        mainLayout = qt.QVBoxLayout(scrollContent)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(10)

        titleLabel = qt.QLabel("Thitiorul et al. (2020) Method")
        titleLabel.setStyleSheet("font-weight: bold; font-size: 16px;")
        titleLabel.setAlignment(qt.Qt.AlignCenter)
        mainLayout.addWidget(titleLabel)

        # Stay-on-top checkbox
        self.stayOnTopCheckbox = qt.QCheckBox("Keep window on top (toggle to avoid losing the GUI)")
        self.stayOnTopCheckbox.setChecked(False)
        self.stayOnTopCheckbox.stateChanged.connect(self.toggleStayOnTop)
        mainLayout.addWidget(self.stayOnTopCheckbox)

        self.prediction_runs = OrderedDict()
        self.colors = [[1, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0.5, 0], [0.5, 1, 0.5]]

        self.topLayout = mainLayout
        self.populateAllSteps(350)

        scrollArea.setWidget(scrollContent)
        outerLayout = qt.QVBoxLayout(self.mainWidget)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        outerLayout.addWidget(scrollArea)

        # State variables
        self.refNasionNode = None
        self.hardTissueNode = None
        self.softTissueNode = None
        self.mspPlaneNode = None
        self.xzPlaneNode = None
        self.transformNode = None
        self.transform_applied = False

        self.syncWithScene()
        self.mainWidget.show()

    # -------------------- UI Creation --------------------
    def createStepGroupBox(self, title, parentLayout):
        groupBox = qt.QGroupBox(title)
        groupBox.setLayout(qt.QVBoxLayout())
        parentLayout.addWidget(groupBox)
        return groupBox

    def setGuiState(self, transform_done):
        self.transform_applied = transform_done
        if transform_done:
            self.applyTransformButton.setText("✓ Transform Applied - Re-apply if needed")
            self.applyTransformButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        else:
            self.applyTransformButton.setText("Apply Transform (Set Nasion as Origin)")
            self.applyTransformButton.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")

    def populateAllSteps(self, buttonWidth):
        self.step1GroupBox = self.createStepGroupBox("Step 1: Load and Position Landmarks", self.topLayout)
        self.step2GroupBox = self.createStepGroupBox("Step 2: Apply Coordinate Transform", self.topLayout)
        self.step3GroupBox = self.createStepGroupBox("Step 3: Create Reference Planes", self.topLayout)
        self.step4GroupBox = self.createStepGroupBox("Step 4: Run Prediction", self.topLayout)
        self.step5GroupBox = self.createStepGroupBox("Step 5: Calculate Errors", self.topLayout)
        self.step6GroupBox = self.createStepGroupBox("Step 6: View and Export Results", self.topLayout)

        # ---- Step 1 ----
        step1Layout = self.step1GroupBox.layout()
        step1InfoLabel = qt.QLabel(
            "<b>Recommended Workflow:</b><br><br>"
            "1. Download and load <b>hard tissue</b> landmarks<br>"
            "2. Click 'Create Hard Guide Lines' to help positioning<br>"
            "3. Manually adjust hard tissue landmarks to match your scan<br>"
            "4. Download and load <b>soft tissue</b> landmarks<br>"
            "5. Click 'Create Soft Guide Lines' to help positioning<br>"
            "6. Manually adjust soft tissue landmarks to match your scan<br>"
            "7. When satisfied, proceed to Step 2<br><br>"
            "<b>Tip:</b> Pay special attention to nasion 'n' - it will become the origin!"
        )
        step1InfoLabel.setWordWrap(True)
        step1Layout.addWidget(step1InfoLabel)

        # Hard tissue
        hardSeparator = qt.QFrame()
        hardSeparator.setFrameShape(qt.QFrame.HLine)
        hardSeparator.setFrameShadow(qt.QFrame.Sunken)
        step1Layout.addWidget(hardSeparator)
        hardLabel = qt.QLabel("<b>Hard Tissue Landmarks:</b>")
        step1Layout.addWidget(hardLabel)

        self.hardTissueSelector = slicer.qMRMLNodeComboBox()
        self.hardTissueSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.hardTissueSelector.setMRMLScene(slicer.mrmlScene)
        self.hardTissueSelector.noneEnabled = True
        step1Layout.addWidget(self.hardTissueSelector)

        self.downloadHardButton = qt.QPushButton("Download Hard Tissue Template")
        self.downloadHardButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.downloadHardButton.setFixedWidth(buttonWidth)
        self.downloadHardButton.clicked.connect(self.onDownloadHardLandmarksClicked)
        step1Layout.addWidget(self.downloadHardButton, 0, qt.Qt.AlignHCenter)

        self.createHardGuideLinesButton = qt.QPushButton("Create Hard Guide Lines")
        self.createHardGuideLinesButton.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px;")
        self.createHardGuideLinesButton.setFixedWidth(buttonWidth)
        self.createHardGuideLinesButton.clicked.connect(self.onCreateHardGuideLinesClicked)
        step1Layout.addWidget(self.createHardGuideLinesButton, 0, qt.Qt.AlignHCenter)

        # Soft tissue
        softSeparator = qt.QFrame()
        softSeparator.setFrameShape(qt.QFrame.HLine)
        softSeparator.setFrameShadow(qt.QFrame.Sunken)
        step1Layout.addWidget(softSeparator)
        softLabel = qt.QLabel("<b>Soft Tissue Landmarks (for validation):</b>")
        step1Layout.addWidget(softLabel)

        self.softTissueSelector = slicer.qMRMLNodeComboBox()
        self.softTissueSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.softTissueSelector.setMRMLScene(slicer.mrmlScene)
        self.softTissueSelector.noneEnabled = True
        step1Layout.addWidget(self.softTissueSelector)

        self.downloadSoftButton = qt.QPushButton("Download Soft Tissue Template")
        self.downloadSoftButton.setStyleSheet("background-color: #8BC34A; color: white; font-weight: bold; padding: 8px;")
        self.downloadSoftButton.setFixedWidth(buttonWidth)
        self.downloadSoftButton.clicked.connect(self.onDownloadSoftLandmarksClicked)
        step1Layout.addWidget(self.downloadSoftButton, 0, qt.Qt.AlignHCenter)

        self.createSoftGuideLinesButton = qt.QPushButton("Create Soft Guide Lines")
        self.createSoftGuideLinesButton.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px;")
        self.createSoftGuideLinesButton.setFixedWidth(buttonWidth)
        self.createSoftGuideLinesButton.clicked.connect(self.onCreateSoftGuideLinesClicked)
        step1Layout.addWidget(self.createSoftGuideLinesButton, 0, qt.Qt.AlignHCenter)

        # ---- Step 2 ----
        step2Layout = self.step2GroupBox.layout()
        step2InfoLabel = qt.QLabel(
            "<b>Apply coordinate transform:</b><br>"
            "This sets hard tissue nasion 'n' as the origin (0,0,0).<br>"
            "All landmarks and guide lines will be automatically transformed."
        )
        step2InfoLabel.setWordWrap(True)
        step2Layout.addWidget(step2InfoLabel)

        # Checkbox for batch transform
        self.transformAllCheckbox = qt.QCheckBox("Apply transform to ALL fiducial nodes (no per-node prompts)")
        self.transformAllCheckbox.setChecked(True)
        self.transformAllCheckbox.setToolTip(
            "If checked, all fiducial nodes are transformed without asking.\n"
            "Uncheck to confirm for each node individually."
        )
        step2Layout.addWidget(self.transformAllCheckbox)

        self.applyTransformButton = qt.QPushButton("Apply Transform (Set Nasion as Origin)")
        self.applyTransformButton.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        self.applyTransformButton.setFixedWidth(buttonWidth)
        self.applyTransformButton.clicked.connect(self.onApplyTransformClicked)
        step2Layout.addWidget(self.applyTransformButton, 0, qt.Qt.AlignHCenter)

        # ---- NEW: Transform Soft Tissue Only ----
        self.transformSoftButton = qt.QPushButton("Transform Soft Tissue Landmarks Now")
        self.transformSoftButton.setStyleSheet("background-color: #FFA500; color: white; padding: 8px;")
        self.transformSoftButton.setFixedWidth(buttonWidth)
        self.transformSoftButton.clicked.connect(self.transformSoftTissueNow)
        step2Layout.addWidget(self.transformSoftButton, 0, qt.Qt.AlignHCenter)

        # ---- Step 3 ----
        step3Layout = self.step3GroupBox.layout()
        step3InfoLabel = qt.QLabel(
            "<b>Create reference planes (optional):</b><br>"
            "Visualize the midsagittal plane and X-Z plane for verification."
        )
        step3InfoLabel.setWordWrap(True)
        step3Layout.addWidget(step3InfoLabel)

        self.createPlanesButton = qt.QPushButton("Create MSP and X-Z Plane")
        self.createPlanesButton.setStyleSheet("background-color: #FFDF00; font-weight: bold; padding: 8px;")
        self.createPlanesButton.setFixedWidth(buttonWidth)
        self.createPlanesButton.clicked.connect(self.onCreatePlanesClicked)
        step3Layout.addWidget(self.createPlanesButton, 0, qt.Qt.AlignHCenter)

        self.visualizeAxesButton = qt.QPushButton("Visualize Axes (optional)")
        self.visualizeAxesButton.setFixedWidth(buttonWidth)
        self.visualizeAxesButton.clicked.connect(self.onVisualizeAxesClicked)
        step3Layout.addWidget(self.visualizeAxesButton, 0, qt.Qt.AlignHCenter)

        # ---- Step 4 ----
        layout4 = self.step4GroupBox.layout()
        info4Label = qt.QLabel(
            "<b>Run soft tissue prediction:</b><br>"
            "Uses validated regression equations from the Thitiorul et al. (2020) paper."
        )
        info4Label.setWordWrap(True)
        layout4.addWidget(info4Label)

        methodInfoLabel = qt.QLabel("• LEFT side hard tissue landmarks only")
        methodInfoLabel.setWordWrap(True)
        methodInfoLabel.setStyleSheet("margin-left: 20px; color: #666;")
        layout4.addWidget(methodInfoLabel)

        self.autoReplaceCheckbox = qt.QCheckBox("Auto-detect missing bilateral landmarks (mirror from right)")
        self.autoReplaceCheckbox.setChecked(False)
        self.autoReplaceCheckbox.setToolTip(
            "If a LEFT landmark is missing but RIGHT exists, automatically mirror the RIGHT landmark.\n\n"
            "Uses the MSP plane (if available) for mirroring, otherwise simple x-sign flip.\n"
            "Usually keep UNCHECKED if you have complete landmarks."
        )
        layout4.addWidget(self.autoReplaceCheckbox)

        self.predictButton = qt.QPushButton("Run Prediction")
        self.predictButton.setStyleSheet("background-color: #00BCD4; color: white; font-weight: bold; padding: 8px;")
        self.predictButton.setFixedWidth(buttonWidth)
        self.predictButton.clicked.connect(self.onPredictClicked)
        layout4.addWidget(self.predictButton, 0, qt.Qt.AlignHCenter)

        # ---- Step 5 ----
        layout5 = self.step5GroupBox.layout()
        step5InfoLabel = qt.QLabel(
            "<b>Calculate prediction accuracy:</b><br>"
            "Compares predicted landmarks with the true soft tissue landmarks you placed."
        )
        step5InfoLabel.setWordWrap(True)
        layout5.addWidget(step5InfoLabel)

        self.showErrorLinesCheckbox = qt.QCheckBox("Show error lines (connecting predicted to true)")
        self.showErrorLinesCheckbox.setChecked(True)
        self.showErrorLinesCheckbox.setToolTip("Toggle visibility of error lines in the 3D view.")
        self.showErrorLinesCheckbox.stateChanged.connect(self.onToggleErrorLines)
        layout5.addWidget(self.showErrorLinesCheckbox)

        self.calculateErrorsButton = qt.QPushButton("Calculate All Errors")
        self.calculateErrorsButton.setStyleSheet("background-color: #E91E63; color: white; font-weight: bold; padding: 8px;")
        self.calculateErrorsButton.setFixedWidth(buttonWidth)
        self.calculateErrorsButton.clicked.connect(self.onCalculateAllErrors)
        layout5.addWidget(self.calculateErrorsButton, 0, qt.Qt.AlignHCenter)

        # ---- Step 6 ----
        layout6 = self.step6GroupBox.layout()
        step6InfoLabel = qt.QLabel("<b>View and export your results:</b>")
        step6InfoLabel.setWordWrap(True)
        layout6.addWidget(step6InfoLabel)

        self.resultsTable = qt.QTableWidget()
        self.resultsTable.setColumnCount(1)
        self.resultsTable.setHorizontalHeaderLabels(["Landmark"])
        landmarks = ["se'", "npp'", "npa'", "pn'", "nd'", "sn'", 
                     "al'L", "als'L", "alp'L", "ali'L", 
                     "al'R", "als'R", "alp'R", "ali'R"]
        self.resultsTable.setRowCount(len(landmarks))
        for i, name in enumerate(landmarks):
            self.resultsTable.setItem(i, 0, qt.QTableWidgetItem(name))
        self.resultsTable.setMinimumHeight(300)
        layout6.addWidget(self.resultsTable)

        # Export controls
        exportLayout = qt.QHBoxLayout()
        self.saveButton = qt.QPushButton("Save Summary to CSV")
        self.saveButton.setStyleSheet("background-color: #3f51b5; color: white; font-weight: bold; padding: 8px;")
        self.saveButton.clicked.connect(self.onSaveToCSV)
        self.copySummaryButton = qt.QPushButton("Copy Summary to Clipboard")
        self.copySummaryButton.clicked.connect(self.onCopySummaryToClipboard)
        exportLayout.addWidget(self.saveButton)
        exportLayout.addWidget(self.copySummaryButton)
        layout6.addLayout(exportLayout)

        # Separator
        separator = qt.QFrame()
        separator.setFrameShape(qt.QFrame.HLine)
        separator.setFrameShadow(qt.QFrame.Sunken)
        layout6.addWidget(separator)

        # Landmark export
        landmarkExportLabel = qt.QLabel(
            "<b>Export Landmark Coordinates:</b><br>"
            "<small>Export your placed hard and soft tissue landmark coordinates</small>"
        )
        landmarkExportLabel.setWordWrap(True)
        layout6.addWidget(landmarkExportLabel)

        landmarkExportLayout = qt.QHBoxLayout()
        self.exportHardLandmarksButton = qt.QPushButton("Export Hard Tissue Coords")
        self.exportHardLandmarksButton.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.exportHardLandmarksButton.setToolTip("Export Thitiorul_hard_tissue landmark coordinates to CSV")
        self.exportHardLandmarksButton.clicked.connect(self.onExportHardLandmarks)
        landmarkExportLayout.addWidget(self.exportHardLandmarksButton)

        self.exportSoftLandmarksButton = qt.QPushButton("Export Soft Tissue Coords")
        self.exportSoftLandmarksButton.setStyleSheet("background-color: #8BC34A; color: white; padding: 8px;")
        self.exportSoftLandmarksButton.setToolTip("Export true_Thitiorul_soft_tissue landmark coordinates to CSV")
        self.exportSoftLandmarksButton.clicked.connect(self.onExportSoftLandmarks)
        landmarkExportLayout.addWidget(self.exportSoftLandmarksButton)
        layout6.addLayout(landmarkExportLayout)

        # Copy to clipboard
        landmarkCopyLayout = qt.QHBoxLayout()
        self.copyHardLandmarksButton = qt.QPushButton("Copy Hard Coords to Clipboard")
        self.copyHardLandmarksButton.clicked.connect(self.onCopyHardLandmarks)
        landmarkCopyLayout.addWidget(self.copyHardLandmarksButton)
        self.copySoftLandmarksButton = qt.QPushButton("Copy Soft Coords to Clipboard")
        self.copySoftLandmarksButton.clicked.connect(self.onCopySoftLandmarks)
        landmarkCopyLayout.addWidget(self.copySoftLandmarksButton)
        layout6.addLayout(landmarkCopyLayout)

        # Separator
        separator2 = qt.QFrame()
        separator2.setFrameShape(qt.QFrame.HLine)
        separator2.setFrameShadow(qt.QFrame.Sunken)
        layout6.addWidget(separator2)

        self.showDetailedButton = qt.QPushButton("Show Detailed Results...")
        self.showDetailedButton.setStyleSheet("background-color: #795548; color: white; padding: 8px;")
        self.showDetailedButton.clicked.connect(self.onShowDetailedResultsClicked)
        layout6.addWidget(self.showDetailedButton)

        # Clear temporary nodes
        self.clearTempButton = qt.QPushButton("Clear Temporary Nodes (lines, planes, axes)")
        self.clearTempButton.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        self.clearTempButton.clicked.connect(self.clearTemporaryNodes)
        layout6.addWidget(self.clearTempButton)

        # ===== EXPORT FOR RSTUDIO =====
        if _rstudio_wrapper:
            _rstudio_wrapper.install_export_button_for(
                gui=self.mainWidget,
                parent_layout=layout6,
                method="Thitiorul",
                variant="default",
                table_widget=self.resultsTable,
            )

    # -------------------- Utility Methods --------------------
    def toggleStayOnTop(self, state):
        flags = self.mainWidget.windowFlags()
        if state == qt.Qt.Checked:
            flags |= qt.Qt.WindowStaysOnTopHint
        else:
            flags &= ~qt.Qt.WindowStaysOnTopHint
        self.mainWidget.setWindowFlags(flags)
        self.mainWidget.show()
        self.raiseMainWindow()

    def raiseMainWindow(self):
        self.mainWidget.raise_()
        self.mainWidget.activateWindow()

    def clearTemporaryNodes(self):
        to_remove = []
        for node in slicer.util.getNodesByClass('vtkMRMLMarkupsLineNode'):
            name = node.GetName()
            if name.startswith(('for_', 'error_line_', 'X_axis', 'Y_axis', 'Z_axis')):
                to_remove.append(node)
        for node in slicer.util.getNodesByClass('vtkMRMLMarkupsPlaneNode'):
            if node.GetName() in ['MSP', 'X-Z plane']:
                to_remove.append(node)
        for node in to_remove:
            slicer.mrmlScene.RemoveNode(node)
        slicer.util.showStatusMessage("Temporary nodes cleared.", 2000)
        self.raiseMainWindow()

    def onToggleErrorLines(self, state):
        for node in slicer.util.getNodesByClass('vtkMRMLMarkupsLineNode'):
            if node.GetName().startswith('error_line_'):
                node.GetDisplayNode().SetVisibility(state == qt.Qt.Checked)

    def findLandmarkByName(self, node, label):
        for i in range(node.GetNumberOfControlPoints()):
            if node.GetNthControlPointLabel(i) == label:
                return i
        return -1

    def get_point_by_label(self, node, label):
        idx = self.findLandmarkByName(node, label)
        if idx != -1:
            return np.array(node.GetNthControlPointPosition(idx))
        raise ValueError(f"Landmark '{label}' not found in {node.GetName()}")

    def get_msp_plane_normal(self):
        if self.mspPlaneNode:
            return np.array(self.mspPlaneNode.GetNormal())
        return None

    def mirror_point_across_msp(self, point):
        normal = self.get_msp_plane_normal()
        if normal is not None and self.mspPlaneNode:
            origin = np.array(self.mspPlaneNode.GetOrigin())
            p = np.array(point)
            d = np.dot(p - origin, normal)
            return p - 2 * d * normal
        else:
            # Fallback: simple x sign flip
            return np.array([-point[0], point[1], point[2]])

    def isNasionAtOrigin(self, tolerance=0.1):
        hard = self.hardTissueSelector.currentNode()
        if not hard:
            return False
        n_idx = self.findLandmarkByName(hard, "n")
        if n_idx == -1:
            return False
        pos = hard.GetNthControlPointPosition(n_idx)
        return np.linalg.norm(pos) < tolerance

    # -------------------- Transform Soft Tissue --------------------
    def transformSoftTissueNow(self):
        """Apply the current transform to the selected soft tissue landmarks only."""
        if not self.transformNode:
            slicer.util.warningDisplay("No transform node found. Run Step 2 first.")
            self.raiseMainWindow()
            return
        soft = self.softTissueSelector.currentNode()
        if not soft:
            slicer.util.warningDisplay("No soft tissue landmarks selected.")
            self.raiseMainWindow()
            return
        # Check if already transformed
        if soft.GetTransformNodeID() is not None:
            # We'll harden it again to be safe
            pass
        soft.SetAndObserveTransformNodeID(self.transformNode.GetID())
        slicer.vtkSlicerTransformLogic().hardenTransform(soft)
        self.softTissueNode = soft
        self.softTissueSelector.setCurrentNode(soft)
        slicer.util.showStatusMessage("Soft tissue landmarks transformed to nasion origin.", 3000)
        self.raiseMainWindow()

    # -------------------- Download and Load --------------------
    def download_and_load_markup(self, url, name, color, scale, harden=False):
        try:
            slicer.util.showStatusMessage(f"Downloading {name}...", 3000)
            with urllib.request.urlopen(url) as response:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json') as temp:
                    temp.write(response.read())
                    temp_filename = temp.name
            node = slicer.util.loadMarkups(temp_filename)
            if node is None:
                raise Exception("Failed to load markup file.")
            node.SetName(name)
            os.unlink(temp_filename)
            display_node = node.GetDisplayNode()
            display_node.SetSelectedColor(color[0], color[1], color[2])
            display_node.SetGlyphScale(scale)
            display_node.SetVisibility(True)
            if harden and self.transform_applied and self.transformNode:
                node.SetAndObserveTransformNodeID(self.transformNode.GetID())
                slicer.vtkSlicerTransformLogic().hardenTransform(node)
            return node
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to download/load {name}: {e}")
            self.raiseMainWindow()
            return None

    # -------------------- Button Callbacks --------------------
    def onDownloadHardLandmarksClicked(self):
        node = self.download_and_load_markup(
            "https://github.com/user-attachments/files/23696758/Thitiorul_hard_tissue.mrk.json",
            "Thitiorul_hard_tissue",
            [0, 1, 0],
            1.5,
            harden=True
        )
        if node:
            self.hardTissueNode = node
            self.hardTissueSelector.setCurrentNode(node)
            self.show_popup("Hard Tissue Template Loaded",
                           "Template loaded! Adjust landmarks and proceed.")
        self.raiseMainWindow()

    def onDownloadSoftLandmarksClicked(self):
        node = self.download_and_load_markup(
            "https://github.com/user-attachments/files/23696755/true_Thitiorul_soft_tissue.mrk.json",
            "true_Thitiorul_soft_tissue",
            [0, 1, 1],
            1.5,
            harden=True
        )
        if node:
            self.softTissueNode = node
            self.softTissueSelector.setCurrentNode(node)
            self.show_popup("Soft Tissue Template Loaded",
                           "Template loaded! Adjust landmarks and proceed.")
        self.raiseMainWindow()

    def create_line_by_name(self, name, node, label1, label2):
        try:
            old = slicer.util.getNode(name)
            slicer.mrmlScene.RemoveNode(old)
        except:
            pass
        p1_idx = self.findLandmarkByName(node, label1)
        p2_idx = self.findLandmarkByName(node, label2)
        if p1_idx != -1 and p2_idx != -1:
            line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
            line.AddControlPoint(node.GetNthControlPointPosition(p1_idx))
            line.AddControlPoint(node.GetNthControlPointPosition(p2_idx))
            line.GetDisplayNode().SetColor(0.0, 1.0, 0.0)
            return line
        else:
            slicer.util.warningDisplay(f"Cannot create line '{name}': missing '{label1}' or '{label2}' in {node.GetName()}")
            self.raiseMainWindow()
            return None

    def onCreateHardGuideLinesClicked(self):
        node = self.hardTissueSelector.currentNode()
        if not node:
            slicer.util.warningDisplay("Please load or select hard tissue landmarks first!")
            self.raiseMainWindow()
            return
        self.create_line_by_name('for_nr', node, "n", "rhi")
        self.create_line_by_name('for_ss', node, "a", "pr")
        slicer.util.showStatusMessage("Hard tissue guide lines created!", 2000)

    def onCreateSoftGuideLinesClicked(self):
        node = self.softTissueSelector.currentNode()
        if not node:
            slicer.util.warningDisplay("Please load or select soft tissue landmarks first!")
            self.raiseMainWindow()
            return
        self.create_line_by_name('for_npp_and_npa', node, "n'", "pn'")
        self.create_line_by_name('for_nd', node, "pn'", "sn'")
        slicer.util.showStatusMessage("Soft tissue guide lines created!", 2000)

    # -------------------- Transform --------------------
    def onApplyTransformClicked(self):
        try:
            hard_tissue = self.hardTissueSelector.currentNode()
            if not hard_tissue:
                slicer.util.warningDisplay("Please load hard tissue landmarks first.")
                self.raiseMainWindow()
                return
            n_idx = self.findLandmarkByName(hard_tissue, "n")
            if n_idx == -1:
                slicer.util.warningDisplay("Hard tissue nasion 'n' not found!")
                self.raiseMainWindow()
                return

            if self.isNasionAtOrigin(0.01):
                if not self.transform_applied:
                    oldTransform = slicer.mrmlScene.GetFirstNodeByName("MoveToOrigin")
                    if oldTransform:
                        slicer.mrmlScene.RemoveNode(oldTransform)
                    self.transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", "MoveToOrigin")
                    identity = vtk.vtkMatrix4x4()
                    identity.Identity()
                    self.transformNode.SetMatrixTransformToParent(identity)
                    all_fiducials = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
                    for fid in all_fiducials:
                        if fid.GetName() != "reference_nasion":
                            fid.SetAndObserveTransformNodeID(self.transformNode.GetID())
                            slicer.vtkSlicerTransformLogic().hardenTransform(fid)
                    self.setGuiState(True)
                    self.show_popup("Transform", "Nasion is already at origin. Identity transform applied.")
                else:
                    self.show_popup("Transform", "Nasion is already at origin. No need to apply transform again.")
                self.raiseMainWindow()
                return

            if self.transform_applied:
                if not self.show_yes_no_popup(
                    "Transform Already Applied",
                    "A transform has already been applied.\n\n"
                    "Re-applying will use the CURRENT position of nasion 'n'.\n\n"
                    "Continue?"
                ):
                    return

            n_coord = hard_tissue.GetNthControlPointPosition(n_idx)
            oldTransform = slicer.mrmlScene.GetFirstNodeByName("MoveToOrigin")
            if oldTransform:
                slicer.mrmlScene.RemoveNode(oldTransform)

            self.transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", "MoveToOrigin")
            matrix = np.array([
                [1, 0, 0, -n_coord[0]],
                [0, 1, 0, -n_coord[1]],
                [0, 0, 1, -n_coord[2]],
                [0, 0, 0, 1]
            ])
            self.transformNode.SetMatrixTransformToParent(slicer.util.vtkMatrixFromArray(matrix))

            all_fiducials = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
            transformed_nodes = []
            skipped_nodes = []
            transform_all = self.transformAllCheckbox.isChecked()

            for fid in all_fiducials:
                name = fid.GetName()
                if name == "reference_nasion":
                    continue
                if fid.GetTransformNodeID() is not None:
                    continue
                if transform_all or self.show_yes_no_popup(
                    f"Transform '{name}'?",
                    f"Apply transform to '{name}'?\n\n"
                    f"This will move all landmarks so nasion is at origin."
                ):
                    fid.SetAndObserveTransformNodeID(self.transformNode.GetID())
                    slicer.vtkSlicerTransformLogic().hardenTransform(fid)
                    transformed_nodes.append(name)
                    if name == "Thitiorul_hard_tissue":
                        self.hardTissueNode = fid
                        self.hardTissueSelector.setCurrentNode(fid)
                    elif name == "true_Thitiorul_soft_tissue":
                        self.softTissueNode = fid
                        self.softTissueSelector.setCurrentNode(fid)
                else:
                    skipped_nodes.append(name)

            volumes = slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')
            if volumes and self.show_yes_no_popup("Transform Volumes?", "Apply transform to all volume nodes?"):
                for vol in volumes:
                    vol.SetAndObserveTransformNodeID(self.transformNode.GetID())

            self.setGuiState(True)

            # Recreate guide lines that existed before transform
            guide_line_names = ['for_nr', 'for_ss', 'for_npp_and_npa', 'for_nd']
            recreated = []
            for line_name in guide_line_names:
                if line_name == 'for_nr' or line_name == 'for_ss':
                    node = self.hardTissueNode
                else:
                    node = self.softTissueNode
                if node:
                    if line_name == 'for_nr':
                        if self.create_line_by_name(line_name, node, "n", "rhi"):
                            recreated.append(line_name)
                    elif line_name == 'for_ss':
                        if self.create_line_by_name(line_name, node, "a", "pr"):
                            recreated.append(line_name)
                    elif line_name == 'for_npp_and_npa':
                        if self.create_line_by_name(line_name, node, "n'", "pn'"):
                            recreated.append(line_name)
                    elif line_name == 'for_nd':
                        if self.create_line_by_name(line_name, node, "pn'", "sn'"):
                            recreated.append(line_name)

            n_new = hard_tissue.GetNthControlPointPosition(n_idx)
            dist = np.linalg.norm(n_new)
            msg = f"✓ Transform applied. Nasion at ({n_new[0]:.2f}, {n_new[1]:.2f}, {n_new[2]:.2f}) mm from origin.\n"
            if dist > 0.5:
                msg += f"⚠️ Distance from origin: {dist:.2f} mm – you may want to re-adjust nasion and re-apply.\n"
            else:
                msg += "✓ Nasion is at origin.\n"
            if recreated:
                msg += f"Recreated guide lines: {', '.join(recreated)}\n"
            self.show_popup("Transform Applied", msg)
            self.raiseMainWindow()
        except Exception as e:
            slicer.util.errorDisplay(f"Transform failed: {e}")
            self.raiseMainWindow()
            import traceback
            traceback.print_exc()

    # -------------------- Planes and Axes --------------------
    def onCreatePlanesClicked(self):
        hard = self.hardTissueSelector.currentNode()
        if not hard:
            slicer.util.warningDisplay("Load hard tissue landmarks first!")
            self.raiseMainWindow()
            return

        if not self.isNasionAtOrigin(0.5):
            if not self.show_yes_no_popup(
                "Nasion not at origin",
                "The nasion is not at (0,0,0).\n\n"
                "For accurate plane creation, it is recommended to apply the transform first (Step 2).\n"
                "Do you want to create planes anyway?"
            ):
                return

        required = ["n", "a", "pr", "ss", "rhi"]
        try:
            points = [self.get_point_by_label(hard, label) for label in required]
        except ValueError as e:
            slicer.util.warningDisplay(f"Missing landmark: {e}")
            self.raiseMainWindow()
            return

        centroid = np.mean(points, axis=0)
        _, _, Vt = np.linalg.svd(points - centroid)
        plane_normal = Vt[2, :]

        self.mspPlaneNode = self.create_plane('MSP', centroid, plane_normal)

        try:
            nasion = self.get_point_by_label(hard, "n")
            rhi = self.get_point_by_label(hard, "rhi")
            superior = rhi - nasion
            if np.linalg.norm(superior) < 0.1:
                superior = np.array([0, 0, 1])
        except:
            superior = np.array([0, 0, 1])
        xz_normal = np.cross(plane_normal, superior)
        if np.linalg.norm(xz_normal) < 0.1:
            xz_normal = np.array([1, 0, 0])
        xz_normal = xz_normal / np.linalg.norm(xz_normal)
        self.xzPlaneNode = self.create_plane('X-Z plane', nasion, xz_normal)
        slicer.util.showStatusMessage("Planes created!", 2000)

    def create_plane(self, name, origin, normal):
        try:
            old = slicer.util.getNode(name)
            slicer.mrmlScene.RemoveNode(old)
        except:
            pass
        plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', name)
        plane.SetOrigin(origin)
        plane.SetNormal(normal)
        return plane

    def onVisualizeAxesClicked(self):
        if not self.mspPlaneNode or not self.xzPlaneNode:
            slicer.util.warningDisplay("Create planes first (Step 3).")
            self.raiseMainWindow()
            return
        hard = self.hardTissueSelector.currentNode()
        if not hard:
            slicer.util.warningDisplay("Load hard tissue landmarks.")
            self.raiseMainWindow()
            return
        n_idx = self.findLandmarkByName(hard, "n")
        if n_idx == -1:
            slicer.util.warningDisplay("Nasion 'n' not found.")
            self.raiseMainWindow()
            return
        n_coord = hard.GetNthControlPointPosition(n_idx)
        y_axis = np.array(self.mspPlaneNode.GetNormal())
        z_axis = np.array(self.xzPlaneNode.GetNormal())
        x_axis = np.cross(y_axis, z_axis)
        if np.linalg.norm(x_axis) < 0.1:
            x_axis = np.array([1, 0, 0])
        x_axis = x_axis / np.linalg.norm(x_axis)
        y_axis = y_axis / np.linalg.norm(y_axis)
        z_axis = z_axis / np.linalg.norm(z_axis)

        def create_axis(axis_name, vector, color):
            try:
                old = slicer.util.getNode(axis_name)
                slicer.mrmlScene.RemoveNode(old)
            except:
                pass
            line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', axis_name)
            line.AddControlPoint(n_coord)
            line.AddControlPoint(n_coord + vector * 100)
            line.GetDisplayNode().SetSelectedColor(color)
            return line

        create_axis('X_axis', x_axis, [1,0,0])
        create_axis('Y_axis', y_axis, [0,1,0])
        create_axis('Z_axis', z_axis, [0,0,1])
        slicer.util.showStatusMessage("Axes visualized!", 2000)

    # -------------------- Prediction --------------------
    def get_left_with_fallback(self, node, left_label, right_label, use_auto_replace):
        left_idx = self.findLandmarkByName(node, left_label)
        if left_idx != -1:
            return node.GetNthControlPointPosition(left_idx)
        if not use_auto_replace:
            raise ValueError(f"Landmark '{left_label}' not found and auto-replace disabled.")
        right_idx = self.findLandmarkByName(node, right_label)
        if right_idx == -1:
            raise ValueError(f"Landmark '{left_label}' not found, and fallback '{right_label}' also not found.")
        right_pos = node.GetNthControlPointPosition(right_idx)
        left_pos = self.mirror_point_across_msp(right_pos)
        slicer.util.showStatusMessage(f"Auto-replace: mirrored '{right_label}' to '{left_label}'", 3000)
        return left_pos

    def runSoftTissueRegression(self, hardTissueNode, outputName, color, use_auto_replace):
        try:
            ss = self.get_point_by_label(hardTissueNode, "ss")
            nr = self.get_point_by_label(hardTissueNode, "nr")
            pr = self.get_point_by_label(hardTissueNode, "pr")
            iof_L = self.get_left_with_fallback(hardTissueNode, "iof_L", "iof_R", use_auto_replace)
            ecm_L = self.get_left_with_fallback(hardTissueNode, "ecm_L", "ecm_R", use_auto_replace)
            zy_L = self.get_left_with_fallback(hardTissueNode, "zy_L", "zy_R", use_auto_replace)
        except ValueError as e:
            slicer.util.errorDisplay(f"Missing landmark for prediction: {e}")
            self.raiseMainWindow()
            return None

        # ---- Variables: y signed, x and z absolute ----
        ss_y = ss[1]
        ss_z_abs = abs(ss[2])
        nr_y = nr[1]
        nr_z_abs = abs(nr[2])
        pr_y = pr[1]
        pr_z_abs = abs(pr[2])

        iof_L_x_abs = abs(iof_L[0])
        iof_L_y = iof_L[1]
        ecm_L_y = ecm_L[1]
        ecm_L_z_abs = abs(ecm_L[2])
        zy_L_x_abs = abs(zy_L[0])
        zy_L_y = zy_L[1]
        zy_L_z_abs = abs(zy_L[2])

        # ---- Midline landmarks ----
        se_y = -0.869 + 0.212*ss_y + 0.139*zy_L_z_abs - 0.073*ecm_L_y
        se_z = -1.198 - 1.159*nr_y + 0.691*nr_z_abs - 0.208*iof_L_y

        npp_y = 3.182 + 0.271*ss_y + 0.423*nr_y - 0.098*ecm_L_y
        npp_z = 5.345 - 0.607*nr_y + 0.840*nr_z_abs

        npa_y = 0.587 + 0.739*ss_y + 0.109*pr_z_abs + 0.242*zy_L_x_abs
        npa_z = 4.315 - 0.371*ss_y + 0.573*ss_z_abs + 0.285*nr_z_abs

        pn_y = -2.091 + 0.818*ss_y + 0.152*pr_z_abs + 0.251*zy_L_x_abs
        pn_z = 2.095 - 0.288*ss_y + 0.456*ss_z_abs + 0.250*pr_z_abs

        nd_y = -2.040 + 0.865*ss_y + 0.120*pr_z_abs + 0.241*zy_L_x_abs
        nd_z = 3.626 - 0.392*ss_y + 0.842*ss_z_abs

        sn_y = -1.902 + 0.676*ss_y + 0.260*pr_y + 0.198*zy_L_x_abs
        sn_z = 6.455 - 0.269*ss_y + 0.551*ss_z_abs + 0.277*pr_z_abs

        # ---- Left side ----
        alL_x = -(7.101 + 0.107*pr_y + 0.316*iof_L_x_abs - 0.076*zy_L_y)
        alL_y = 2.427 - 0.320*nr_z_abs + 0.733*ss_y + 0.129*pr_z_abs
        alL_z = 2.897 - 0.218*ss_y + 0.464*ss_z_abs + 0.305*pr_z_abs

        alsL_x = -(3.167 + 0.174*iof_L_x_abs + 0.097*zy_L_x_abs)
        alsL_y = 3.993 + 0.453*ss_y + 0.270*pr_y + 0.072*pr_z_abs
        alsL_z = 3.827 - 0.466*ss_y + 0.674*ss_z_abs + 0.257*iof_L_y

        alpL_x = -(7.885 + 0.060*pr_z_abs + 0.310*iof_L_x_abs)
        alpL_y = 4.199 + 0.398*ss_y + 0.224*pr_y + 0.247*iof_L_y
        alpL_z = 2.054 - 0.419*ss_y + 0.433*ss_z_abs + 0.332*pr_z_abs

        aliL_x = -(4.611 + 0.239*iof_L_x_abs - 0.070*zy_L_y)
        aliL_y = -0.890 + 0.476*pr_y + 0.377*ss_y + 0.089*zy_L_x_abs
        aliL_z = 0.404 + 0.499*ss_y + 0.312*pr_z_abs - 0.119*zy_L_y

        # ---- Right side ----
        alR_x = 8.967 + 0.125*pr_y + 0.249*iof_L_x_abs - 0.079*zy_L_y
        alR_y = 0.338 - 0.264*nr_z_abs + 0.760*ss_y + 0.151*pr_z_abs
        alR_z = 2.778 - 0.223*ss_y + 0.437*ss_z_abs + 0.325*pr_z_abs

        alsR_x = 3.244 + 0.225*iof_L_x_abs + 0.079*zy_L_x_abs
        alsR_y = -1.183 + 0.628*pr_y + 0.151*ecm_L_z_abs
        alsR_z = 3.864 - 0.499*ss_y + 0.685*ss_z_abs + 0.350*iof_L_y

        alpR_x = 12.069 + 0.045*pr_z_abs + 0.207*iof_L_x_abs
        alpR_y = 6.126 + 0.626*ss_y + 0.323*iof_L_y
        alpR_z = 2.578 - 0.404*ss_y + 0.403*ss_z_abs + 0.350*pr_z_abs

        aliR_x = 6.729 + 0.100*pr_y + 0.165*iof_L_x_abs - 0.062*zy_L_y
        aliR_y = -2.325 + 0.504*pr_y + 0.345*ss_y + 0.112*zy_L_x_abs
        aliR_z = 6.363 - 0.161*ss_y + 0.468*ss_z_abs + 0.350*pr_z_abs

        # ---- Create output node ----
        try:
            old = slicer.util.getNode(outputName)
            slicer.mrmlScene.RemoveNode(old)
        except:
            pass

        result_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", outputName)
        landmarks = [
            ("se'",   [0, se_y, se_z]),
            ("npp'",  [0, npp_y, npp_z]),
            ("npa'",  [0, npa_y, npa_z]),
            ("pn'",   [0, pn_y, pn_z]),
            ("nd'",   [0, nd_y, nd_z]),
            ("sn'",   [0, sn_y, sn_z]),
            ("al'L",  [alL_x, alL_y, alL_z]),
            ("als'L", [alsL_x, alsL_y, alsL_z]),
            ("alp'L", [alpL_x, alpL_y, alpL_z]),
            ("ali'L", [aliL_x, aliL_y, aliL_z]),
            ("al'R",  [alR_x, alR_y, alR_z]),
            ("als'R", [alsR_x, alsR_y, alsR_z]),
            ("alp'R", [alpR_x, alpR_y, alpR_z]),
            ("ali'R", [aliR_x, aliR_y, aliR_z])
        ]
        for i, (label, coords) in enumerate(landmarks):
            result_node.AddControlPoint([coords[0], coords[1], -coords[2]])   # z sign flip
            result_node.SetNthControlPointLabel(i, label)

        result_node.GetDisplayNode().SetSelectedColor(color[0], color[1], color[2])
        return result_node

    def onPredictClicked(self):
        if "thitiorul" in self.prediction_runs:
            if not self.show_yes_no_popup("Overwrite?", "Prediction already exists. Overwrite?"):
                return
        hard = self.hardTissueSelector.currentNode()
        if not hard:
            slicer.util.warningDisplay("Load hard tissue landmarks first!")
            self.raiseMainWindow()
            return
        use_auto = self.autoReplaceCheckbox.isChecked()
        outputName = "Predicted_Thitiorul"
        color = self.colors[0]
        pred_node = self.runSoftTissueRegression(hard, outputName, color, use_auto)
        if pred_node:
            self.prediction_runs["thitiorul"] = {'node_id': pred_node.GetID(), 'color': color}
            soft = self.softTissueSelector.currentNode()
            if soft:
                self.onCalculateAllErrors()
                self.show_popup("Prediction Complete", "✓ Prediction complete and errors calculated!")
            else:
                self.show_popup("Prediction Complete", "✓ Prediction complete. Load soft tissue and calculate errors in Step 5.")
            self.raiseMainWindow()

    # -------------------- Error Calculation --------------------
    def onCalculateAllErrors(self):
        soft = self.softTissueSelector.currentNode()
        if not soft:
            slicer.util.warningDisplay("Load soft tissue landmarks to calculate errors.")
            self.raiseMainWindow()
            return

        true_dict = {}
        for i in range(soft.GetNumberOfControlPoints()):
            label = soft.GetNthControlPointLabel(i)
            true_dict[label] = np.array(soft.GetNthControlPointPosition(i))

        for node in slicer.util.getNodesByClass('vtkMRMLMarkupsLineNode'):
            if node.GetName().startswith('error_line_'):
                slicer.mrmlScene.RemoveNode(node)

        run_names = list(self.prediction_runs.keys())
        self.resultsTable.setColumnCount(1 + len(run_names))
        headers = ["Landmark"] + [f"{name} (mm)" for name in run_names]
        self.resultsTable.setHorizontalHeaderLabels(headers)

        for col_idx, (method_name, run_data) in enumerate(self.prediction_runs.items(), start=1):
            pred_node = slicer.mrmlScene.GetNodeByID(run_data['node_id'])
            if not pred_node:
                continue
            pred_dict = {}
            for i in range(pred_node.GetNumberOfControlPoints()):
                label = pred_node.GetNthControlPointLabel(i)
                pred_dict[label] = np.array(pred_node.GetNthControlPointPosition(i))

            for row_idx in range(self.resultsTable.rowCount):
                landmark = self.resultsTable.item(row_idx, 0).text()
                if landmark in pred_dict and landmark in true_dict:
                    error = np.linalg.norm(pred_dict[landmark] - true_dict[landmark])
                    self.resultsTable.setItem(row_idx, col_idx, qt.QTableWidgetItem(f"{error:.2f}"))
                    line_name = f"error_line_{landmark}_{method_name}"
                    line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", line_name)
                    line.AddControlPoint(pred_dict[landmark])
                    line.AddControlPoint(true_dict[landmark])
                    display = line.GetDisplayNode()
                    display.SetSelectedColor(run_data['color'][0], run_data['color'][1], run_data['color'][2])
                    display.SetGlyphScale(0)
                    display.SetLineThickness(0.5)
                    display.SetVisibility(self.showErrorLinesCheckbox.isChecked())

        self.resultsTable.resizeColumnsToContents()

    # -------------------- Detailed Results --------------------
    def onShowDetailedResultsClicked(self):
        soft = self.softTissueSelector.currentNode()
        if not soft:
            slicer.util.warningDisplay("Load soft tissue landmarks first.")
            self.raiseMainWindow()
            return
        if not self.prediction_runs:
            slicer.util.warningDisplay("Run prediction first.")
            self.raiseMainWindow()
            return

        dialog = qt.QDialog(self.mainWidget)
        dialog.setWindowTitle("Detailed Prediction Results")
        dialog.setMinimumSize(1200, 700)
        layout = qt.QVBoxLayout(dialog)

        table = qt.QTableWidget()
        headers = ["Landmark", "Pred X", "Pred Y", "Pred Z",
                "True X", "True Y", "True Z", "Error (mm)", "Error Direction", "Equation"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        true_dict = {}
        for i in range(soft.GetNumberOfControlPoints()):
            label = soft.GetNthControlPointLabel(i)
            true_dict[label] = np.array(soft.GetNthControlPointPosition(i))

        run_data = list(self.prediction_runs.values())[0]
        pred_node = slicer.mrmlScene.GetNodeByID(run_data['node_id'])
        if not pred_node:
            return
        pred_dict = {}
        for i in range(pred_node.GetNumberOfControlPoints()):
            label = pred_node.GetNthControlPointLabel(i)
            pred_dict[label] = np.array(pred_node.GetNthControlPointPosition(i))

        formulas = {
            "se'": ["y = -0.869+0.212*ss_y+0.139*zy_z-0.073*ecm_y", "z = -1.198-1.159*nr_y+0.691*nr_z-0.208*iof_y"],
            "npp'": ["y = 3.182+0.271*ss_y+0.423*nr_y-0.098*ecm_y", "z = 5.345-0.607*nr_y+0.840*nr_z"],
            "npa'": ["y = 0.587+0.739*ss_y+0.109*pr_z+0.242*zy_x", "z = 4.315-0.371*ss_y+0.573*ss_z+0.285*nr_z"],
            "pn'": ["y = -2.091+0.818*ss_y+0.152*pr_z+0.251*zy_x", "z = 2.095-0.288*ss_y+0.456*ss_z+0.250*pr_z"],
            "nd'": ["y = -2.040+0.865*ss_y+0.120*pr_z+0.241*zy_x", "z = 3.626-0.392*ss_y+0.842*ss_z"],
            "sn'": ["y = -1.902+0.676*ss_y+0.260*pr_y+0.198*zy_x", "z = 6.455-0.269*ss_y+0.551*ss_z+0.277*pr_z"],
            "al'L": ["x = -(7.101+0.107*pr_y+0.316*iof_x-0.076*zy_y)", "y = 2.427-0.320*nr_z+0.733*ss_y+0.129*pr_z", "z = 2.897-0.218*ss_y+0.464*ss_z+0.305*pr_z"],
            "als'L": ["x = -(3.167+0.174*iof_x+0.097*zy_x)", "y = 3.993+0.453*ss_y+0.270*pr_y+0.072*pr_z", "z = 3.827-0.466*ss_y+0.674*ss_z+0.257*iof_y"],
            "alp'L": ["x = -(7.885+0.060*pr_z+0.310*iof_x)", "y = 4.199+0.398*ss_y+0.224*pr_y+0.247*iof_y", "z = 2.054-0.419*ss_y+0.433*ss_z+0.332*pr_z"],
            "ali'L": ["x = -(4.611+0.239*iof_x-0.070*zy_y)", "y = -0.890+0.476*pr_y+0.377*ss_y+0.089*zy_x", "z = 0.404+0.499*ss_y+0.312*pr_z-0.119*zy_y"],
            "al'R": ["x = 8.967+0.125*pr_y+0.249*iof_x-0.079*zy_y", "y = 0.338-0.264*nr_z+0.760*ss_y+0.151*pr_z", "z = 2.778-0.223*ss_y+0.437*ss_z+0.325*pr_z"],
            "als'R": ["x = 3.244+0.225*iof_x+0.079*zy_x", "y = -1.183+0.628*pr_y+0.151*ecm_z", "z = 3.864-0.499*ss_y+0.685*ss_z+0.350*iof_y"],
            "alp'R": ["x = 12.069+0.045*pr_z+0.207*iof_x", "y = 6.126+0.626*ss_y+0.323*iof_y", "z = 2.578-0.404*ss_y+0.403*ss_z+0.350*pr_z"],
            "ali'R": ["x = 6.729+0.100*pr_y+0.165*iof_x-0.062*zy_y", "y = -2.325+0.504*pr_y+0.345*ss_y+0.112*zy_x", "z = 6.363-0.161*ss_y+0.468*ss_z+0.350*pr_z"]
        }

        all_landmarks = sorted(pred_dict.keys())
        table.setRowCount(len(all_landmarks))
        row = 0
        for landmark in all_landmarks:
            table.setItem(row, 0, qt.QTableWidgetItem(landmark))
            if landmark in pred_dict:
                p = pred_dict[landmark]
                table.setItem(row, 1, qt.QTableWidgetItem(f"{p[0]:.2f}"))
                table.setItem(row, 2, qt.QTableWidgetItem(f"{p[1]:.2f}"))
                table.setItem(row, 3, qt.QTableWidgetItem(f"{p[2]:.2f}"))
            if landmark in true_dict:
                t = true_dict[landmark]
                table.setItem(row, 4, qt.QTableWidgetItem(f"{t[0]:.2f}"))
                table.setItem(row, 5, qt.QTableWidgetItem(f"{t[1]:.2f}"))
                table.setItem(row, 6, qt.QTableWidgetItem(f"{t[2]:.2f}"))
            if landmark in pred_dict and landmark in true_dict:
                err = np.linalg.norm(pred_dict[landmark] - true_dict[landmark])
                table.setItem(row, 7, qt.QTableWidgetItem(f"{err:.2f}"))
                direction = self.get_error_direction_string(true_dict[landmark] - pred_dict[landmark])
                table.setItem(row, 8, qt.QTableWidgetItem(direction))
            eq = "\n".join(formulas.get(landmark, ["Not available"]))
            eq_single_line = eq.replace("\n", "; ")
            table.setItem(row, 9, qt.QTableWidgetItem(eq_single_line))
            row += 1

        table.resizeColumnsToContents()
        layout.addWidget(table)

        copy_button = qt.QPushButton("Copy Table to Clipboard")
        copy_button.clicked.connect(lambda: self.onCopyToClipboard(table))
        layout.addWidget(copy_button)

        dialog.exec_()
        self.raiseMainWindow()

    def get_error_direction_string(self, error_vector):
        x, y, z = error_vector
        dirs = []
        if abs(y) > 0.1:
            dirs.append("Ant(+)" if y > 0 else "Post(-)")
        if abs(z) > 0.1:
            dirs.append("Sup(+)" if z > 0 else "Inf(-)")
        if abs(x) > 0.1:
            dirs.append("Right(+)" if x > 0 else "Left(-)")
        return ", ".join(dirs) if dirs else "Spot on"

    # -------------------- Clipboard and Export --------------------
    def onCopyToClipboard(self, table_widget):
        try:
            app = qt.QApplication.instance()
            if not app:
                slicer.util.errorDisplay("Could not access clipboard.")
                self.raiseMainWindow()
                return False
            clipboard = app.clipboard()
            if not clipboard:
                return False

            text = ""
            headers = []
            for i in range(table_widget.columnCount):
                item = table_widget.horizontalHeaderItem(i)
                headers.append(item.text() if item else f"Col{i}")
            text += "\t".join(headers) + "\n"

            for row in range(table_widget.rowCount):
                row_data = []
                for col in range(table_widget.columnCount):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                text += "\t".join(row_data) + "\n"

            clipboard.setText(text, qt.QClipboard.Clipboard)
            if clipboard.supportsSelection():
                clipboard.setText(text, qt.QClipboard.Selection)
            return True
        except Exception as e:
            slicer.util.errorDisplay(f"Copy error: {e}")
            self.raiseMainWindow()
            return False

    def onCopySummaryToClipboard(self):
        if self.resultsTable.columnCount < 2:
            slicer.util.warningDisplay("No results to copy. Run prediction and calculate errors first.")
            self.raiseMainWindow()
            return
        if self.onCopyToClipboard(self.resultsTable):
            self.show_popup("Copied", "Summary copied to clipboard!")
            self.raiseMainWindow()

    def onSaveToCSV(self):
        result = qt.QFileDialog.getSaveFileName(
            self.mainWidget,
            "Save Summary",
            "thitiorul_summary.csv",
            "CSV Files (*.csv)"
        )
        self.raiseMainWindow()
        fileName = result[0] if isinstance(result, tuple) else result
        if not fileName:
            return
        app = qt.QApplication.instance()
        clipboard = app.clipboard()
        if self.onCopyToClipboard(self.resultsTable):
            try:
                with open(fileName, 'w') as f:
                    f.write(clipboard.text(qt.QClipboard.Clipboard))
                self.show_popup("Saved", f"Summary saved to {fileName}")
                self.raiseMainWindow()
            except Exception as e:
                slicer.util.errorDisplay(f"Could not save: {e}")
                self.raiseMainWindow()

    def export_landmark_coordinates(self, node_name, default_filename):
        try:
            node = slicer.util.getNode(node_name)
            if not node:
                slicer.util.warningDisplay(f"'{node_name}' not found.")
                self.raiseMainWindow()
                return False
            result = qt.QFileDialog.getSaveFileName(
                self.mainWidget,
                f"Export {node_name} Coordinates",
                default_filename,
                "CSV Files (*.csv)"
            )
            self.raiseMainWindow()
            fileName = result[0] if isinstance(result, tuple) else result
            if not fileName:
                return False
            csv = "Label,X,Y,Z,Description\n"
            for i in range(node.GetNumberOfControlPoints()):
                label = node.GetNthControlPointLabel(i)
                pos = node.GetNthControlPointPosition(i)
                desc = node.GetNthControlPointDescription(i) if hasattr(node, 'GetNthControlPointDescription') else ""
                csv += f'"{label}",{pos[0]:.6f},{pos[1]:.6f},{pos[2]:.6f},"{desc}"\n'
            with open(fileName, 'w') as f:
                f.write(csv)
            self.show_popup("Exported", f"Coordinates exported to {fileName}")
            self.raiseMainWindow()
            return True
        except Exception as e:
            slicer.util.errorDisplay(f"Export failed: {e}")
            self.raiseMainWindow()
            return False

    def copy_landmark_coordinates(self, node_name):
        try:
            node = slicer.util.getNode(node_name)
            if not node:
                slicer.util.warningDisplay(f"'{node_name}' not found.")
                self.raiseMainWindow()
                return False
            text = "Label\tX\tY\tZ\tDescription\n"
            for i in range(node.GetNumberOfControlPoints()):
                label = node.GetNthControlPointLabel(i)
                pos = node.GetNthControlPointPosition(i)
                desc = node.GetNthControlPointDescription(i) if hasattr(node, 'GetNthControlPointDescription') else ""
                text += f"{label}\t{pos[0]:.6f}\t{pos[1]:.6f}\t{pos[2]:.6f}\t{desc}\n"
            app = qt.QApplication.instance()
            if not app:
                return False
            clipboard = app.clipboard()
            clipboard.setText(text, qt.QClipboard.Clipboard)
            if clipboard.supportsSelection():
                clipboard.setText(text, qt.QClipboard.Selection)
            self.show_popup("Copied", f"{node_name} coordinates copied to clipboard!")
            self.raiseMainWindow()
            return True
        except Exception as e:
            slicer.util.errorDisplay(f"Copy failed: {e}")
            self.raiseMainWindow()
            return False

    def onExportHardLandmarks(self):
        self.export_landmark_coordinates("Thitiorul_hard_tissue", "hard_tissue_coordinates.csv")

    def onExportSoftLandmarks(self):
        self.export_landmark_coordinates("true_Thitiorul_soft_tissue", "soft_tissue_coordinates.csv")

    def onCopyHardLandmarks(self):
        self.copy_landmark_coordinates("Thitiorul_hard_tissue")

    def onCopySoftLandmarks(self):
        self.copy_landmark_coordinates("true_Thitiorul_soft_tissue")

    # -------------------- State Sync --------------------
    def syncWithScene(self):
        try:
            self.transformNode = slicer.util.getNode("MoveToOrigin")
            self.setGuiState(True)
        except:
            self.setGuiState(False)

        try:
            self.refNasionNode = slicer.util.getNode("reference_nasion")
        except:
            pass

        try:
            hard = slicer.util.getNode("Thitiorul_hard_tissue")
            self.hardTissueSelector.setCurrentNode(hard)
            self.hardTissueNode = hard
        except:
            pass

        try:
            soft = slicer.util.getNode("true_Thitiorul_soft_tissue")
            self.softTissueSelector.setCurrentNode(soft)
            self.softTissueNode = soft
        except:
            pass

        try:
            self.mspPlaneNode = slicer.util.getNode("MSP")
            self.xzPlaneNode = slicer.util.getNode("X-Z plane")
        except:
            pass

        try:
            pred = slicer.util.getNode("Predicted_Thitiorul")
            if pred and "thitiorul" not in self.prediction_runs:
                self.prediction_runs["thitiorul"] = {
                    'node_id': pred.GetID(),
                    'color': self.colors[0]
                }
                pred.GetDisplayNode().SetSelectedColor(self.colors[0][0], self.colors[0][1], self.colors[0][2])
        except:
            pass

        if self.prediction_runs and self.softTissueNode:
            self.onCalculateAllErrors()

    # -------------------- Popups --------------------
    def show_popup(self, title, text):
        slicer.util.infoDisplay(text, title)
        self.raiseMainWindow()

    def show_yes_no_popup(self, title, text):
        result = slicer.util.confirmYesNoDisplay(title, text)
        self.raiseMainWindow()
        return result

# Main execution
try:
    if 'gui' in globals() and isinstance(globals().get('gui'), ThitiorulGUI):
        globals()['gui'].mainWidget.close()
    gui = ThitiorulGUI()
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed to create GUI: {e}")

```
