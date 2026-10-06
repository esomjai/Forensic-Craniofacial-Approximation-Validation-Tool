```python
# ==================================================================
#  Bootstrap: load rStudio_wrapper from GitHub
# ==================================================================
import os, sys, importlib.util
import urllib.request
import tempfile

RSTUDIO_EXPORT_URL = (
    "https://raw.githubusercontent.com/esomjai/"
    "Forensic-Craniofacial-Approximation-Validation-Tool/"
    "refs/heads/basics/Start%20here/rStudio_wrapper.py"
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

class TedeschiOlivieraGUI:
    def __init__(self):
        """Initialize the GUI for Tedeschi-Oliviera method"""
        
        # --- Main Setup ---
        self.mainWidget = qt.QWidget()
        self.mainWidget.setWindowTitle("Tedeschi-Oliviera Pronasale Prediction")
        self.mainWidget.setMinimumSize(550, 700)
        
        # --- Layouts ---
        scrollArea = qt.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = qt.QWidget()
        mainLayout = qt.QVBoxLayout(scrollContent)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(8)
        
        # --- Log Window ---
        self.logWidget = qt.QTextEdit()
        self.logWidget.setWindowTitle("Process Log")
        self.logWidget.setReadOnly(True)
        self.logWidget.setMinimumSize(400, 300)
        self.logWidget.show()
        
        self.log("Starting Tedeschi-Oliviera method")
        
        # --- Title ---
        titleLabel = qt.QLabel("Tedeschi-Oliviera Method (2016)")
        titleLabel.setStyleSheet("font-weight: bold; font-size: 16px;")
        titleLabel.setAlignment(qt.Qt.AlignCenter)
        mainLayout.addWidget(titleLabel)
        
        descriptionLabel = qt.QLabel("This method predicts pronasale using a right triangle formed by rhinion and prosthion.")
        descriptionLabel.setAlignment(qt.Qt.AlignCenter)
        descriptionLabel.setWordWrap(True)
        mainLayout.addWidget(descriptionLabel)
        
        # --- Shared Class Variables ---
        self.buttonWidth = 280
        self.landmarksNode = None
        self.mspPlaneNode = None
        self.predictedPronasaleNode = None
        self.asAngleNode = None
        self.arAngleNode = None
        self.errorLineNode = None
        self.results = {}
        
        # --- UI Group Boxes (Full interface) ---
        
        # ===== STEP 1: LANDMARK SELECTION =====
        step1GroupBox = qt.QGroupBox("Step 1: Load Landmarks")
        step1Layout = qt.QVBoxLayout(step1GroupBox)
        step1Layout.setContentsMargins(8, 10, 8, 10)
        step1Layout.setSpacing(8)
        
        step1Layout.addWidget(qt.QLabel("Landmarks Node:"))
        self.markupsSelector = slicer.qMRMLNodeComboBox()
        self.markupsSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.markupsSelector.selectNodeUponCreation = True
        self.markupsSelector.noneEnabled = True
        self.markupsSelector.addEnabled = False
        self.markupsSelector.removeEnabled = False
        self.markupsSelector.setMRMLScene(slicer.mrmlScene)
        self.markupsSelector.setToolTip("Select the landmarks node")
        step1Layout.addWidget(self.markupsSelector)
        
        self.downloadButton = qt.QPushButton("Download Landmarks from GitHub")
        self.downloadButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.downloadButton.setFixedWidth(self.buttonWidth)
        self.downloadButton.clicked.connect(self.onDownloadLandmarksClicked)
        step1Layout.addWidget(self.downloadButton, 0, qt.Qt.AlignHCenter)
        
        self.loadLocalButton = qt.QPushButton("Load Landmarks from Local File")
        self.loadLocalButton.setFixedWidth(self.buttonWidth)
        self.loadLocalButton.clicked.connect(self.onLoadLocalLandmarksClicked)
        step1Layout.addWidget(self.loadLocalButton, 0, qt.Qt.AlignHCenter)
        
        landmarksInfoLabel = qt.QLabel(
            "<b>Required landmarks (in order):</b><br>"
            "• rhinion (0) • prosthion (1) • pronasale (2)<br>"
            "• inion (3) • nasion (4) • bregma (5)"
        )
        landmarksInfoLabel.setWordWrap(True)
        landmarksInfoLabel.setStyleSheet("font-size: 10px; color: #555;")
        step1Layout.addWidget(landmarksInfoLabel)
        mainLayout.addWidget(step1GroupBox)
        
        # ===== STEP 2: CREATE MSP =====
        step2GroupBox = qt.QGroupBox("Step 2: Create Midsagittal Plane (MSP)")
        step2Layout = qt.QVBoxLayout(step2GroupBox)
        step2Layout.setContentsMargins(8, 10, 8, 10)
        step2Layout.setSpacing(8)
        
        step2Layout.addWidget(qt.QLabel("<b>Choose plane creation method:</b>"))
        self.planeMethodGroup = qt.QButtonGroup()
        self.mspRadioButton = qt.QRadioButton("MSP (3-point plane)")
        self.mspRadioButton.setToolTip("Uses only rhinion, prosthion, and nasion")
        self.planeMethodGroup.addButton(self.mspRadioButton, 1)
        step2Layout.addWidget(self.mspRadioButton)
        
        self.inbMspRadioButton = qt.QRadioButton("INB+MSP (5-point best-fit plane)")
        self.inbMspRadioButton.setToolTip("Uses rhinion, prosthion, inion, nasion, and bregma")
        self.inbMspRadioButton.setChecked(True)
        self.planeMethodGroup.addButton(self.inbMspRadioButton, 2)
        step2Layout.addWidget(self.inbMspRadioButton)
        
        mspInfoLabel = qt.QLabel(
            "<b>MSP (3-point):</b> Simple plane through rhinion, prosthion, and nasion<br>"
            "<b>INB+MSP (5-point):</b> Best-fit plane through rhinion, prosthion, inion, nasion, and bregma"
        )
        mspInfoLabel.setWordWrap(True)
        mspInfoLabel.setStyleSheet("font-size: 10px; color: #555; margin-top: 5px;")
        step2Layout.addWidget(mspInfoLabel)
        
        self.createMSPButton = qt.QPushButton("Create Plane")
        self.createMSPButton.setStyleSheet("background-color: #FFDF00; font-weight: bold; padding: 8px;")
        self.createMSPButton.setFixedWidth(self.buttonWidth)
        self.createMSPButton.clicked.connect(self.onCreateMSPClicked)
        step2Layout.addWidget(self.createMSPButton, 0, qt.Qt.AlignHCenter)
        mainLayout.addWidget(step2GroupBox)
        
        # ===== STEP 3: PREDICT PRONASALE =====
        step3GroupBox = qt.QGroupBox("Step 3: Predict Pronasale Position")
        step3Layout = qt.QVBoxLayout(step3GroupBox)
        step3Layout.setContentsMargins(8, 10, 8, 10)
        step3Layout.setSpacing(8)
        methodInfoLabel = qt.QLabel(
            "This calculates the predicted pronasale as the apex of a right triangle<br>"
            "with rhinion and prosthion as the base, positioned on the MSP."
        )
        methodInfoLabel.setWordWrap(True)
        step3Layout.addWidget(methodInfoLabel)
        self.predictPronasaleButton = qt.QPushButton("Predict Pronasale")
        self.predictPronasaleButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.predictPronasaleButton.setFixedWidth(self.buttonWidth)
        self.predictPronasaleButton.clicked.connect(self.onPredictPronasaleClicked)
        step3Layout.addWidget(self.predictPronasaleButton, 0, qt.Qt.AlignHCenter)
        mainLayout.addWidget(step3GroupBox)

        # ===== STEP 4: CREATE MEASUREMENTS =====
        step4GroupBox = qt.QGroupBox("Step 4: Create Measurements")
        step4Layout = qt.QVBoxLayout(step4GroupBox)
        step4Layout.setContentsMargins(8, 10, 8, 10)
        step4Layout.setSpacing(8)
        measurementInfoLabel = qt.QLabel(
            "Creates measurements for statistical analysis:<br>"
            "• <b>AS:</b> Angle at predicted pronasale (should be ~90°)<br>"
            "• <b>AR:</b> Angle at true pronasale<br>"
            "• <b>Error:</b> Distance between predicted and true pronasale"
        )
        measurementInfoLabel.setWordWrap(True)
        step4Layout.addWidget(measurementInfoLabel)
        self.createMeasurementsButton = qt.QPushButton("Create Measurements")
        self.createMeasurementsButton.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 8px;")
        self.createMeasurementsButton.setFixedWidth(self.buttonWidth)
        self.createMeasurementsButton.clicked.connect(self.onCreateMeasurementsClicked)
        step4Layout.addWidget(self.createMeasurementsButton, 0, qt.Qt.AlignHCenter)
        mainLayout.addWidget(step4GroupBox)

        # ===== STEP 5: RESULTS =====
        step5GroupBox = qt.QGroupBox("Step 5: View & Copy Results")
        step5Layout = qt.QVBoxLayout(step5GroupBox)
        step5Layout.setContentsMargins(8, 10, 8, 10)
        step5Layout.setSpacing(8)
        step5Layout.addWidget(qt.QLabel("<b>Measurement Results:</b>"))
        self.resultsTable = qt.QTableWidget()
        self.resultsTable.setRowCount(3)
        self.resultsTable.setColumnCount(3)
        self.resultsTable.setHorizontalHeaderLabels(["ID", "Measurement", "Value"])
        measurements = ["AS (Predicted angle)", "AR (True angle)", "Error (mm)"]
        for i, measurement in enumerate(measurements):
            id_item = qt.QTableWidgetItem(str(i))
            id_item.setFlags(qt.Qt.ItemIsEnabled)
            self.resultsTable.setItem(i, 0, id_item)
            metric_item = qt.QTableWidgetItem(measurement)
            metric_item.setFlags(qt.Qt.ItemIsEnabled)
            self.resultsTable.setItem(i, 1, metric_item)
            self.resultsTable.setItem(i, 2, qt.QTableWidgetItem(""))
        self.resultsTable.horizontalHeader().setStretchLastSection(True)
        self.resultsTable.setMinimumHeight(120)
        step5Layout.addWidget(self.resultsTable)
        self.copyButton = qt.QPushButton("Copy Results to Clipboard")
        self.copyButton.setFixedWidth(self.buttonWidth)
        self.copyButton.clicked.connect(self.copyMeasurementsToClipboard)
        step5Layout.addWidget(self.copyButton, 0, qt.Qt.AlignHCenter)
        mainLayout.addWidget(step5GroupBox)
        
        # ===== EXPORT FOR RSTUDIO =====
        if _rstudio_wrapper:
            _rstudio_wrapper.install_export_button_for(
                gui=self.mainWidget,
                parent_layout=mainLayout,
                method="TedeschiOliviera",
                variant="auto",
                table_widget=self.resultsTable,
            )

        # ===== UTILITIES =====
        utilGroupBox = qt.QGroupBox("Utilities")
        utilLayout = qt.QVBoxLayout(utilGroupBox)
        self.resetButton = qt.QPushButton("Reset All")
        self.resetButton.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        self.resetButton.setFixedWidth(self.buttonWidth)
        self.resetButton.clicked.connect(self.onResetClicked)
        utilLayout.addWidget(self.resetButton, 0, qt.Qt.AlignHCenter)
        mainLayout.addWidget(utilGroupBox)
        
        # --- Finalize Layout ---
        scrollArea.setWidget(scrollContent)
        outerLayout = qt.QVBoxLayout(self.mainWidget)
        outerLayout.addWidget(scrollArea)
        
        # --- Initializations ---
        self.syncWithScene()
        self.mainWidget.show()

    def log(self, message):
        self.logWidget.append(message)
        print(f"LOG: {message}")

    def copyMeasurementsToClipboard(self):
        """
        This function directly reads from the measurement nodes, calculates
        the values, and copies them to the clipboard, finishing with a pop-up.
        """
        self.log("Copying measurements directly from scene nodes...")
        measurements = []
        
        # Process Angle Nodes
        angle_nodes_to_process = {
            "AS (Predicted angle)": self.asAngleNode,
            "AR (True angle)": self.arAngleNode
        }
        for measurementName, angleNode in angle_nodes_to_process.items():
            if angleNode and angleNode.GetNumberOfControlPoints() >= 3:
                p1, p2, p3 = (np.zeros(3) for _ in range(3))
                angleNode.GetNthControlPointPositionWorld(0, p1)
                angleNode.GetNthControlPointPositionWorld(1, p2)
                angleNode.GetNthControlPointPositionWorld(2, p3)
                v1, v2 = p1 - p2, p3 - p2
                v1_norm, v2_norm = np.linalg.norm(v1), np.linalg.norm(v2)
                angle_degrees = np.degrees(np.arccos(np.clip(np.dot(v1/v1_norm, v2/v2_norm), -1.0, 1.0))) if v1_norm > 0 and v2_norm > 0 else 0
                measurements.append(f"{measurementName}\t{angle_degrees:.2f}°")

        # Process Line Node
        if self.errorLineNode and self.errorLineNode.GetNumberOfControlPoints() >= 2:
            p1, p2 = (np.zeros(3) for _ in range(2))
            self.errorLineNode.GetNthControlPointPositionWorld(0, p1)
            self.errorLineNode.GetNthControlPointPositionWorld(1, p2)
            length = np.linalg.norm(p2 - p1)
            measurements.append(f"Error (mm)\t{length:.2f} mm")
            
        if not measurements:
            self.log("No valid measurements found to copy.")
            slicer.util.warningDisplay("No measurements have been created yet.")
            return
            
        # Copy to Clipboard
        outputText = "Measurement\tValue\n" + "\n".join(measurements)
        slicer.app.clipboard().setText(outputText)
        self.log(f"Copied {len(measurements)} measurements to clipboard.")
        
        # *** THIS IS THE NEW LINE FOR THE POP-UP! ***
        slicer.util.infoDisplay(f"{len(measurements)} measurements have been copied to clipboard.", "Copy Successful")

    def onResetClicked(self):
        """Clears all results, nodes created by the script, and resets the interface."""
        self.log("Resetting application state...")
        nodes_to_remove = [self.mspPlaneNode, self.predictedPronasaleNode, self.asAngleNode, self.arAngleNode, self.errorLineNode]
        for node in nodes_to_remove:
            if node and slicer.mrmlScene.IsNodePresent(node):
                slicer.mrmlScene.RemoveNode(node)
        
        self.landmarksNode, self.mspPlaneNode, self.predictedPronasaleNode, self.asAngleNode, self.arAngleNode, self.errorLineNode = None, None, None, None, None, None
        self.results.clear()
        
        for row in range(self.resultsTable.rowCount()):
            if self.resultsTable.item(row, 2): self.resultsTable.item(row, 2).setText("")
        self.markupsSelector.setCurrentNode(None)
        
        self.log("Application has been reset.")
        slicer.util.showStatusMessage("Module has been reset.", 3000)

    def findLandmarkByName(self, landmarksNode, name):
        """Finds a landmark index by its name (case-insensitive)."""
        if not landmarksNode: return -1
        for i in range(landmarksNode.GetNumberOfControlPoints()):
            if name.lower() in landmarksNode.GetNthControlPointLabel(i).lower(): return i
        return -1
    
    def syncWithScene(self):
        """Checks the scene for existing nodes to potentially sync with."""
        self.log("Checking scene for 'Tedeschi_Oliviera_lmrks'...")
        try:
            node = slicer.util.getNode("Tedeschi_Oliviera_lmrks")
            if node:
                self.landmarksNode = node
                self.markupsSelector.setCurrentNode(node)
                self.log("Found and selected existing landmarks node.")
        except slicer.util.MRMLNodeNotFoundException:
            self.log("No pre-existing landmarks node found. Ready for new data.")
    
    def onDownloadLandmarksClicked(self):
        """Downloads the sample landmark file from GitHub."""
        try:
            url = "https://github.com/user-attachments/files/30263036/Tedeschi_Oliviera_lmrks.mrk.json"
            self.log(f"Downloading landmarks from: {url}")
            with urllib.request.urlopen(url) as response:
                jsonData = response.read().decode('utf-8')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json', mode='w') as temp:
                temp.write(jsonData)
                tempFilename = temp.name
            node = slicer.util.loadMarkups(tempFilename)
            if node:
                node.SetName("Tedeschi_Oliviera_lmrks")
                self.landmarksNode = node
                self.markupsSelector.setCurrentNode(node)
                self.log(f"Successfully loaded {node.GetNumberOfControlPoints()} landmarks.")
            os.unlink(tempFilename)
        except Exception as e:
            slicer.util.errorDisplay(f"Error downloading landmarks: {e}")
            self.log(f"ERROR: {e}")
    
    def onLoadLocalLandmarksClicked(self):
        """Loads landmarks from a local file chosen by the user."""
        try:
            fileName, _ = qt.QFileDialog.getOpenFileName(self.mainWidget, "Load Landmarks", "", "Markup JSON Files (*.mrk.json);;All Files (*.*)")
            if fileName:
                self.landmarksNode = slicer.util.loadMarkups(fileName)
                self.markupsSelector.setCurrentNode(self.landmarksNode)
                self.log(f"Loaded landmarks from {fileName}")
        except Exception as e:
            slicer.util.errorDisplay(f"Error loading landmarks: {e}")
            self.log(f"ERROR: {e}")
    
    def onCreateMSPClicked(self):
        """Creates the Midsagittal Plane based on the selected method."""
        try:
            self.landmarksNode = self.markupsSelector.currentNode()
            if not self.landmarksNode:
                slicer.util.warningDisplay("Please load landmarks first."); return
            if self.mspPlaneNode and slicer.mrmlScene.IsNodePresent(self.mspPlaneNode):
                slicer.mrmlScene.RemoveNode(self.mspPlaneNode)

            selectedMethod = self.planeMethodGroup.checkedId()
            if selectedMethod == 1:
                self.log("Creating MSP using 3-point method..."); names = ["rhinion", "prosthion", "nasion"]
            else:
                self.log("Creating MSP using 5-point method..."); names = ["rhinion", "prosthion", "inion", "nasion", "bregma"]
            indices = [self.findLandmarkByName(self.landmarksNode, name) for name in names]
            if -1 in indices: raise ValueError(f"Required landmarks not found. Needed: {names}")
            points = np.array([self.landmarksNode.GetNthControlPointPositionWorld(i) for i in indices])
            origin = np.mean(points, axis=0)
            if selectedMethod == 1: normal = np.cross(points[1] - points[0], points[2] - points[0])
            else: _, _, Vt = np.linalg.svd(points - origin); normal = Vt[2, :]
            self.mspPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP')
            self.mspPlaneNode.SetCenter(origin)
            self.mspPlaneNode.SetNormal(normal / np.linalg.norm(normal))
            self.log("MSP plane created successfully.")
        except Exception as e:
            slicer.util.errorDisplay(f"Error creating MSP: {e}"); self.log(f"ERROR: {e}")
    
    def onPredictPronasaleClicked(self):
        """Predicts the pronasale position based on the MSP."""
        try:
            if not self.landmarksNode or not self.mspPlaneNode:
                slicer.util.warningDisplay("Please load landmarks and create MSP first."); return
            if self.predictedPronasaleNode and slicer.mrmlScene.IsNodePresent(self.predictedPronasaleNode):
                slicer.mrmlScene.RemoveNode(self.predictedPronasaleNode)
            self.log("Calculating predicted pronasale...")
            rh_idx, pr_idx = self.findLandmarkByName(self.landmarksNode, "rhinion"), self.findLandmarkByName(self.landmarksNode, "prosthion")
            if -1 in [rh_idx, pr_idx]: raise ValueError("Rhinion or Prosthion not found.")
            A, B = np.array(self.landmarksNode.GetNthControlPointPositionWorld(rh_idx)), np.array(self.landmarksNode.GetNthControlPointPositionWorld(pr_idx))
            plane_normal = np.zeros(3); self.mspPlaneNode.GetNormalWorld(plane_normal)
            perp_dir = np.cross(plane_normal, (B - A) / np.linalg.norm(B - A))
            midpoint, radius = (A + B) / 2, np.linalg.norm(B - A) / 2
            C1, C2 = midpoint + perp_dir * radius, midpoint - perp_dir * radius
            pronasale_pred = C1 if C1[1] > C2[1] else C2
            self.predictedPronasaleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'predicted_pronasale')
            self.predictedPronasaleNode.AddControlPoint(vtk.vtkVector3d(pronasale_pred), "pronasale_pred")
            self.predictedPronasaleNode.GetDisplayNode().SetSelectedColor(1.0, 0.0, 0.0)
            self.predictedPronasaleNode.GetDisplayNode().SetGlyphScale(3.0)
            self.log("Predicted pronasale created successfully.")
        except Exception as e:
            slicer.util.errorDisplay(f"Error predicting pronasale: {e}"); self.log(f"ERROR: {e}")
    
    def onCreateMeasurementsClicked(self):
        """Creates measurement angles and the error line for analysis."""
        try:
            if not self.landmarksNode or not self.predictedPronasaleNode:
                slicer.util.warningDisplay("Please load landmarks and predict pronasale first."); return
            self.log("Creating measurements...")
            nodes_to_remove = [self.asAngleNode, self.arAngleNode, self.errorLineNode]
            for node in nodes_to_remove:
                if node and slicer.mrmlScene.IsNodePresent(node): slicer.mrmlScene.RemoveNode(node)
            names = ["rhinion", "prosthion", "pronasale"]
            indices = {name: self.findLandmarkByName(self.landmarksNode, name) for name in names}
            if -1 in indices.values(): raise ValueError("Rhinion, Prosthion, or true Pronasale landmark not found.")
            points = {name: self.landmarksNode.GetNthControlPointPositionWorld(idx) for name, idx in indices.items()}
            points["pronasale_pred"] = self.predictedPronasaleNode.GetNthControlPointPositionWorld(0)
            self.asAngleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'AS_Angle')
            self.asAngleNode.AddControlPoint(vtk.vtkVector3d(points["rhinion"])); self.asAngleNode.AddControlPoint(vtk.vtkVector3d(points["pronasale_pred"])); self.asAngleNode.AddControlPoint(vtk.vtkVector3d(points["prosthion"]))
            self.arAngleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'AR_Angle')
            self.arAngleNode.AddControlPoint(vtk.vtkVector3d(points["rhinion"])); self.arAngleNode.AddControlPoint(vtk.vtkVector3d(points["pronasale"])); self.arAngleNode.AddControlPoint(vtk.vtkVector3d(points["prosthion"]))
            self.errorLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Pronasale_Error')
            self.errorLineNode.AddControlPoint(vtk.vtkVector3d(points["pronasale"])); self.errorLineNode.AddControlPoint(vtk.vtkVector3d(points["pronasale_pred"]))
            self.errorLineNode.GetDisplayNode().SetColor(0.5, 0, 0)
            self.updateResultsTable()
            self.log("Measurements created successfully.")
        except Exception as e:
            slicer.util.errorDisplay(f"Error creating measurements: {e}"); self.log(f"ERROR: {e}")
    
    def updateResultsTable(self):
        """Updates the results table with the latest measurement values."""
        try:
            self.log("Updating results table...")
            if self.asAngleNode: self.resultsTable.item(0, 2).setText(f"{self.asAngleNode.GetMeasurement('angle').GetValue():.2f}°")
            if self.arAngleNode: self.resultsTable.item(1, 2).setText(f"{self.arAngleNode.GetMeasurement('angle').GetValue():.2f}°")
            if self.errorLineNode: self.resultsTable.item(2, 2).setText(f"{self.errorLineNode.GetMeasurement('length').GetValue():.2f} mm")
            self.log("Results table updated.")
        except Exception as e:
            self.log(f"ERROR updating results: {e}")

# --- Run the GUI ---
try:
    gui = TedeschiOlivieraGUI()
except Exception as e:
    print(f"Failed to create the GUI: {e}")



``` 
