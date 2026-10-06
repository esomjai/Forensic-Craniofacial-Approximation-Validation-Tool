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
import logging
import math

class StephanMethodGUI(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle("Stephan Method GUI")
        self.setObjectName("StephanMethodGUI")
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setSpacing(10)
        self.stepStack = qt.QStackedWidget()
        self.mainLayout.addWidget(self.stepStack)
        self.logic = StephanMethodLogic()
        self.currentStep = 0
        self.createAllStepWidgets()
        self.setupNavigation()
        self.updateStepUI()

    def createAllStepWidgets(self):
        self.createStep1_Setup()
        self.createStep2_PlaneSetup()
        self.createStep3_Framework()
        self.createStep4_Measurements()
        self.createStep5_Prediction()
        self.createStep6_Validation()

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
        navLayout.addWidget(self.prevButton); navLayout.addStretch(1)
        navLayout.addWidget(self.stepLabel); navLayout.addStretch(1)
        navLayout.addWidget(self.nextButton)
        self.mainLayout.addWidget(navWidget)

    def createStep1_Setup(self):
        widget = qt.QWidget(); layout = qt.QVBoxLayout(widget); layout.setSpacing(15)
        title = qt.QLabel("Step 1: Load Hard Tissue Landmarks")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        desc = qt.QLabel("Load the hard tissue landmarks required for the workflow. "
                         "If a 'lmrks_Stephan' node is already in the scene, you can "
                         "reuse it directly.")
        desc.setWordWrap(True)

        # --- Two distinct actions ---
        self.useExistingLandmarksButton = qt.QPushButton("Use Landmarks Already in Scene")
        self.useExistingLandmarksButton.setStyleSheet(
            "background-color: #6c757d; color: white; font-weight: bold; padding: 8px;")
        self.useExistingLandmarksButton.clicked.connect(self.onUseExistingLandmarks)

        self.downloadLandmarksButton = qt.QPushButton("Download and Load Fresh Copy")
        self.downloadLandmarksButton.setStyleSheet(
            "background-color: #007BFF; color: white; font-weight: bold; padding: 8px;")
        self.downloadLandmarksButton.clicked.connect(self.onDownloadHardTissue)

        self.step1StatusLabel = qt.QLabel("Status: Waiting for user.")

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(self.useExistingLandmarksButton, 0, qt.Qt.AlignHCenter)
        layout.addWidget(self.downloadLandmarksButton, 0, qt.Qt.AlignHCenter)
        layout.addWidget(self.step1StatusLabel)
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep2_PlaneSetup(self):
        widget = qt.QWidget(); layout = qt.QVBoxLayout(widget); layout.setSpacing(15)
        title = qt.QLabel("Step 2: Create a Reference Plane"); title.setStyleSheet("font-weight: bold; font-size: 16px;")
        desc = qt.QLabel("Choose a method to create the main reference plane for all subsequent geometric constructions.")
        desc.setWordWrap(True)
        buttonLayout = qt.QHBoxLayout()
        self.createINBButton = qt.QPushButton("Create INB Plane"); self.createMSPButton = qt.QPushButton("Create MSP Plane")
        buttonLayout.addWidget(self.createINBButton); buttonLayout.addWidget(self.createMSPButton)
        self.createINBButton.clicked.connect(lambda: self.onCreatePlane('INB'))
        self.createMSPButton.clicked.connect(lambda: self.onCreatePlane('MSP'))
        self.step2StatusLabel = qt.QLabel("Status: Waiting for user.")
        layout.addWidget(title); layout.addWidget(desc); layout.addLayout(buttonLayout)
        layout.addWidget(self.step2StatusLabel); layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep3_Framework(self):
        widget = qt.QWidget(); layout = qt.QVBoxLayout(widget); layout.setSpacing(15)
        title = qt.QLabel("Step 3: Create Geometric Framework"); title.setStyleSheet("font-weight: bold; font-size: 16px;")
        desc = qt.QLabel("This step builds the foundational network of reference lines and points. The table below explains what will be created.")
        desc.setWordWrap(True)
        table = qt.QTableWidget(6, 2)
        table.setHorizontalHeaderLabels(["Item to be Created", "Description"])
        table.setItem(0, 0, qt.QTableWidgetItem("nasion-point A")); table.setItem(0, 1, qt.QTableWidgetItem("Line from Nasion through Point A, on the reference plane."))
        table.setItem(1, 0, qt.QTableWidgetItem("AA FHP")); table.setItem(1, 1, qt.QTableWidgetItem("Line parallel to FHP, bisecting Point AA."))
        table.setItem(2, 0, qt.QTableWidgetItem("Point X")); table.setItem(2, 1, qt.QTableWidgetItem("Intersection of the two lines above."))
        table.setItem(3, 0, qt.QTableWidgetItem("nasal aperture base")); table.setItem(3, 1, qt.QTableWidgetItem("Line connecting LL and RL, the lowest part of the nasal aperture in profile view."))
        table.setItem(4, 0, qt.QTableWidgetItem("NAB point")); table.setItem(4, 1, qt.QTableWidgetItem("Intersection of the nasal aperture base and the plane."))
        table.setItem(5, 0, qt.QTableWidgetItem("for c)")); table.setItem(5, 1, qt.QTableWidgetItem("Line through NAB point, parallel to nasion-point A."))
        table.horizontalHeader().setStretchLastSection(True); table.verticalHeader().setVisible(False)
        table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        table.setFixedHeight(table.verticalHeader().defaultSectionSize * table.rowCount + table.horizontalHeader().height)
        self.createFrameworkButton = qt.QPushButton("Create Framework")
        self.createFrameworkButton.clicked.connect(self.onCreateFramework)
        self.step3StatusLabel = qt.QLabel("Status: Waiting for user.")
        layout.addWidget(title); layout.addWidget(desc); layout.addWidget(table)
        layout.addWidget(self.createFrameworkButton); layout.addWidget(self.step3StatusLabel); layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep4_Measurements(self):
        widget = qt.QWidget(); layout = qt.QVBoxLayout(widget); layout.setSpacing(15)
        title = qt.QLabel("Step 4: Create All Measurements"); title.setStyleSheet("font-weight: bold; font-size: 16px;")
        desc = qt.QLabel("Click the button below to create all the final measurements. This requires the framework from Step 3 to be complete.")
        desc.setWordWrap(True)
        
        table = qt.QTableWidget(5, 2)
        table.setHorizontalHeaderLabels(["Measurement", "Description"])
        table.setItem(0, 0, qt.QTableWidgetItem("A) nasal bone angle")); table.setItem(0, 1, qt.QTableWidgetItem("Angle from FHP, at nasion, to rhinion."))
        table.setItem(1, 0, qt.QTableWidgetItem("B) line")); table.setItem(1, 1, qt.QTableWidgetItem("Shortest distance from acanthion to the nasal aperture base."))
        table.setItem(2, 0, qt.QTableWidgetItem("C) line")); table.setItem(2, 1, qt.QTableWidgetItem("Shortest distance from rhinion to the 'for c)' line."))
        table.setItem(3, 0, qt.QTableWidgetItem("D) nasal spine angle")); table.setItem(3, 1, qt.QTableWidgetItem("Angle from acanthion, at Point X, to the FHP."))
        table.setItem(4, 0, qt.QTableWidgetItem("E) line")); table.setItem(4, 1, qt.QTableWidgetItem("Distance from nasion to Point X."))
        table.horizontalHeader().setStretchLastSection(True); table.verticalHeader().setVisible(False)
        table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        table.setFixedHeight(table.verticalHeader().defaultSectionSize * table.rowCount + table.horizontalHeader().height)
        
        self.createMeasurementsButton = qt.QPushButton("Create Measurements (A, B, C, D, E)")
        self.createMeasurementsButton.clicked.connect(self.onCreateMeasurements)
        self.step4StatusLabel = qt.QLabel("Status: Waiting for user.")
        layout.addWidget(title); layout.addWidget(desc); layout.addWidget(table)
        layout.addWidget(self.createMeasurementsButton)
        layout.addWidget(self.step4StatusLabel); layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep5_Prediction(self):
        widget = qt.QWidget(); layout = qt.QVBoxLayout(widget); layout.setSpacing(15)
        title = qt.QLabel("Step 5: Final Pronasale Prediction"); title.setStyleSheet("font-weight: bold; font-size: 16px;")
        desc = qt.QLabel("Select the subject's sex and click the button to run the final prediction formulas and create the result.")
        desc.setWordWrap(True)
        
        formulas_label = qt.QLabel("<b>Prediction Formulas:</b><br>"
                                     "<i>Projection (x) for Males:</i> x = -0.32(a) + 0.85(b) - 0.42(c) + 49.58<br>"
                                     "<i>Projection (x) for Females:</i> x = -0.41(a) + 0.37(b) + 49.87<br>"
                                     "<i>Height (y) for Both:</i> y = (-0.002(d) + 0.83) * e")
        formulas_label.setWordWrap(True)

        formLayout = qt.QFormLayout()
        self.sexSelector = qt.QComboBox(); self.sexSelector.addItems(["Female", "Male"])
        formLayout.addRow("Sex:", self.sexSelector)
        
        self.calculatePredictionButton = qt.QPushButton("Calculate Prediction")
        self.calculatePredictionButton.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.calculatePredictionButton.clicked.connect(self.onCalculatePrediction)
        
        self.step5StatusLabel = qt.QLabel("Status: Waiting for user.")
        layout.addWidget(title); layout.addWidget(desc); layout.addWidget(formulas_label)
        layout.addLayout(formLayout)
        layout.addWidget(self.calculatePredictionButton); layout.addWidget(self.step5StatusLabel); layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep6_Validation(self):
        widget = qt.QWidget(); layout = qt.QVBoxLayout(widget); layout.setSpacing(15)
        title = qt.QLabel("Step 6: Validation"); title.setStyleSheet("font-weight: bold; font-size: 16px;")
        desc = qt.QLabel("If you have the 'true' soft tissue landmarks, load them, then measure the prediction error.")
        desc.setWordWrap(True)
        
        self.downloadSoftTissueButton = qt.QPushButton("Download and Load True Soft Tissue Points")
        self.downloadSoftTissueButton.clicked.connect(self.onDownloadSoftTissue)
        
        self.compareButton = qt.QPushButton("Measure Prediction Error")
        self.compareButton.clicked.connect(self.onCompare)
        
        # Results panel (hidden until user clicks "Measure Prediction Error")
        self.step6ResultsWidget = qt.QWidget()
        resultsLayout = qt.QVBoxLayout(self.step6ResultsWidget)
        self.step6ResultsWidget.setVisible(False)

        # --- Table: Per-landmark predicted vs. true comparison -------------
        resultsLayout.addWidget(qt.QLabel("<b>Landmark Comparison</b>"))
        self.landmarkTable = qt.QTableWidget(1, 8)
        self.landmarkTable.setHorizontalHeaderLabels([
            "Landmark",
            "Pred X", "Pred Y", "Pred Z",
            "True X", "True Y", "True Z",
            "Error (mm)",
        ])
        self.landmarkTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.landmarkTable.verticalHeader().setVisible(False)
        resultsLayout.addWidget(self.landmarkTable)

        
        # --- Table 3: Measurements A–E ----------------------------------
        resultsLayout.addWidget(qt.QLabel("<b>Measurements</b>"))
        self.measurementsTable = qt.QTableWidget(5, 3)
        self.measurementsTable.setHorizontalHeaderLabels(
            ["Measurement", "Value", "Unit"])
        self.measurementsTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.measurementsTable.verticalHeader().setVisible(False)
        resultsLayout.addWidget(self.measurementsTable)

        # --- Single copy button -----------------------------------------
        self.copyAllButton = qt.QPushButton("Copy All Results to Clipboard")
        self.copyAllButton.clicked.connect(self.onCopyAll)
        resultsLayout.addWidget(self.copyAllButton)
        self.step6StatusLabel = qt.QLabel("Status: Waiting for user.")

        # A finish button to close the GUI
        finishButton = qt.QPushButton("Finish")
        finishButton.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        finishButton.clicked.connect(self.onFinishClicked)

        layout.addWidget(title); layout.addWidget(desc); layout.addWidget(self.downloadSoftTissueButton)
        layout.addWidget(self.compareButton); layout.addWidget(self.step6ResultsWidget); layout.addWidget(self.step6StatusLabel); layout.addStretch(1)
        layout.addWidget(finishButton) 

        # ===== EXPORT FOR RSTUDIO =====
        if _rstudio_wrapper:
            _rstudio_wrapper.install_export_button_for(
                gui=self,
                parent_layout=layout,
                method="Stephan",
                variant="auto",
                table_widget=self.landmarkTable,
            )

        self.stepStack.addWidget(widget)

    def onPrevButtonClicked(self):
        if self.currentStep > 0: self.currentStep -= 1; self.updateStepUI()
    
    def onNextButtonClicked(self):
        self.updateStepUI()
        isComplete, _ = self.logic.isStepComplete(self.currentStep)
        if isComplete:
            if self.currentStep < self.stepStack.count - 1: self.currentStep += 1; self.updateStepUI()
        else: slicer.util.warningDisplay("Please complete the current step before proceeding.")
    
    def onFinishClicked(self):
        self.hide()

    def updateStepUI(self):
        self.checkSceneAndSetState()
        self.stepStack.setCurrentIndex(self.currentStep)
        self.stepLabel.setText(f"Step {self.currentStep + 1}/{self.stepStack.count}")
        self.prevButton.setEnabled(self.currentStep > 0)
        self.nextButton.setEnabled(self.currentStep < self.stepStack.count - 1)

    def checkSceneAndSetState(self):
        status_labels = [self.step1StatusLabel, self.step2StatusLabel, self.step3StatusLabel, self.step4StatusLabel, self.step5StatusLabel, self.step6StatusLabel]
        for i, label in enumerate(status_labels):
            isComplete, message = self.logic.isStepComplete(i)
            label.setText(f"Status: {message}" if isComplete else "Status: Waiting for user.")
    
    def onUseExistingLandmarks(self):
        node = self.logic.getNode('lmrks_Stephan', "vtkMRMLMarkupsFiducialNode")
        if not node:
            slicer.util.warningDisplay(
                "No 'lmrks_Stephan' fiducial node was found in the scene.\n"
                "Use 'Download and Load Fresh Copy' instead.")
            return
        self.updateStepUI()

    def onDownloadHardTissue(self):
        existing = self.logic.getNode('lmrks_Stephan', "vtkMRMLMarkupsFiducialNode", exact=True)
        if existing:
            ok = slicer.util.confirmOkCancelDisplay(
                f"'{existing.GetName()}' already exists in the scene.\n\n"
                "Downloading a fresh copy will REPLACE it and discard any\n"
                "edits you have made to the current landmarks.\n\n"
                "Continue?")
            if not ok:
                return
        self.logic.downloadAndLoadHardTissue()
        self.updateStepUI()

    def onCreatePlane(self, plane_type): self.logic.createReferencePlane(plane_type); self.updateStepUI()
    def onCreateFramework(self): self.logic.createFramework(); self.updateStepUI()
    def onCreateMeasurements(self): self.logic.createMeasurements(); self.updateStepUI()
    def onCalculatePrediction(self): self.logic.calculatePrediction(self.sexSelector.currentText); self.updateStepUI()
    def onDownloadSoftTissue(self): self.logic.downloadAndLoadSoftTissue(); self.updateStepUI()
    
    def onCompare(self):
        try:
            rows = self.logic.comparePrediction()
        except Exception as e:
            slicer.util.errorDisplay(str(e))
            return

        # --- Per-landmark table ---
        try:
            self.landmarkTable.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.landmarkTable.setItem(r, 0, qt.QTableWidgetItem(row["name"]))
                for c, key in enumerate(("pred", "true")):
                    pos = row[key]
                    if pos is None:
                        for k in range(3):
                            self.landmarkTable.setItem(
                                r, 1 + c * 3 + k, qt.QTableWidgetItem("-"))
                    else:
                        for k in range(3):
                            self.landmarkTable.setItem(
                                r, 1 + c * 3 + k,
                                qt.QTableWidgetItem(f"{pos[k]:.2f}"))
                err_txt = "-" if row["error"] is None else f"{row['error']:.2f}"
                self.landmarkTable.setItem(r, 7, qt.QTableWidgetItem(err_txt))
            self.landmarkTable.resizeColumnsToContents()
        except Exception as e:
            print(f"Landmark table failed: {e}")

        
        # --- Measurements table ---
        try:
            specs = [
                ("A) nasal bone angle",  "GetAngleDegrees", "deg"),
                ("B) line",              "length",          "mm"),
                ("C) line",              "length",          "mm"),
                ("D) nasal spine angle", "GetAngleDegrees", "deg"),
                ("E) line",              "length",          "mm"),
            ]
            for r, (node_name, kind, unit) in enumerate(specs):
                value = self.logic.getMeasurementValue(node_name, kind)
                self.measurementsTable.setItem(r, 0, qt.QTableWidgetItem(node_name))
                self.measurementsTable.setItem(
                    r, 1, qt.QTableWidgetItem("-" if value is None else f"{value:.2f}"))
                self.measurementsTable.setItem(r, 2, qt.QTableWidgetItem(unit))
            self.measurementsTable.resizeColumnsToContents()
        except Exception as e:
            print(f"Measurements table failed: {e}")

        # Always reveal the panel — even a partially-filled one is useful
        self.step6ResultsWidget.setVisible(True)
        self.updateStepUI()
    def onCopyAll(self):
        if not self.step6ResultsWidget.isVisible():
            slicer.util.warningDisplay("Run 'Measure Prediction Error' first.")
            return

        def dump_table(table):
            rows = []
            headers = [table.horizontalHeaderItem(c).text()
                       for c in range(table.columnCount)]
            rows.append("\t".join(headers))
            for r in range(table.rowCount):
                cells = []
                for c in range(table.columnCount):
                    item = table.item(r, c)
                    cells.append(item.text() if item else "")
                rows.append("\t".join(cells))
            return rows

        lines = []
        lines.append("=== Landmark Comparison ===")
        lines.extend(dump_table(self.landmarkTable))
        lines.append("")     
        
        lines.append("=== Measurements ===")
        lines.extend(dump_table(self.measurementsTable))

        qt.QApplication.clipboard().setText("\n".join(lines))
        slicer.util.infoDisplay("All results copied to clipboard.")

#
# LOGIC CLASS - THE "ENGINE"
#
class StephanMethodLogic:
    def isStepComplete(self, step_index):
        if step_index == 0:
            return self.getNode('lmrks_Stephan', "vtkMRMLMarkupsFiducialNode", exact=True) is not None, "Landmarks loaded successfully."
        elif step_index == 1:
            plane_node = self.getNode('INB', "vtkMRMLMarkupsPlaneNode") or self.getNode('MSP', "vtkMRMLMarkupsPlaneNode")
            return plane_node is not None, f"'{plane_node.GetName()}' plane is active." if plane_node else ""
        elif step_index == 2:
            return self.isFrameworkComplete(), "Geometric framework is complete."
        elif step_index == 3:
            return self.areMeasurementsComplete(), "All measurements created successfully."
        elif step_index == 4:
            return self.getNode('pronasale pred', "vtkMRMLMarkupsFiducialNode") is not None, "Prediction complete."
        elif step_index == 5:
            if self.getNode('pronasale error', 'vtkMRMLMarkupsLineNode'):
                return True, "Comparison complete."
            if self.findPronasaleInAllLandmarks():
                return True, "True pronasale found. Ready to measure error."
            return False, ""
        return False, ""

    def cleanup(self, partial=False, measurements=False, prediction=False, comparison=False):
        nodes_to_remove = []
        framework_nodes = ["x axis", "y axis", "AA FHP", "nasion-point A", "nasal aperture base", "for c)", "Point X", "NAB point"]
        measurement_nodes = ["A) nasal bone angle", "B) line", "C) line", "D) nasal spine angle", "E) line"]
        prediction_nodes = ["pronasale pred"]
        comparison_nodes = ["pronasale error"]
        
        if comparison: nodes_to_remove.extend(comparison_nodes)
        if prediction: nodes_to_remove.extend(prediction_nodes)
        if measurements: nodes_to_remove.extend(measurement_nodes)
        if partial: nodes_to_remove.extend(framework_nodes)
        if not any([partial, measurements, prediction, comparison]):
             nodes_to_remove.extend(["INB", "MSP"] + framework_nodes + measurement_nodes + prediction_nodes + comparison_nodes)
        
        for name in nodes_to_remove:
            node = self.getNode(name, exact=True)
            if node: slicer.mrmlScene.RemoveNode(node)

    def getNode(self, name, className=None, exact=False):
        if exact: return slicer.util.getFirstNodeByName(name)
        name_lower = name.lower().strip()
        nodes = slicer.mrmlScene.GetNodesByClass(className if className else "vtkMRMLNode")
        for i in range(nodes.GetNumberOfItems()):
            node = nodes.GetItemAsObject(i)
            if name_lower in node.GetName().lower(): return node
        return None

    def buildLandmarkComparison(self, pred_node_name="pronasale pred"):
        pred_node = self.getNode(pred_node_name, "vtkMRMLMarkupsFiducialNode")
        if not pred_node:
            return []

        # Harvest every (label → position) from every non-prediction fiducial node
        true_index = {}   # key: normalised label -> (pos, node_name, original_label)
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
        for i in range(nodes.GetNumberOfItems()):
            node = nodes.GetItemAsObject(i)
            if node is pred_node or node.GetName() == pred_node_name:
                continue
            for j in range(node.GetNumberOfControlPoints()):
                label = node.GetNthControlPointLabel(j)
                key = label.lower().replace(" ", "").replace("(", "").replace(")", "")
                pos = self.getNthPointPos(node, j)
                # Prefer nodes whose name suggests "true" / "soft" tissue
                pref = 0 if "soft" in node.GetName().lower() else 1
                prev = true_index.get(key)
                if prev is None or pref < prev[3]:
                    true_index[key] = (pos, node.GetName(), label, pref)

        results = []
        for i in range(pred_node.GetNumberOfControlPoints()):
            pred_label = pred_node.GetNthControlPointLabel(i)
            pred_pos = self.getNthPointPos(pred_node, i)

            # Strip the "(Predicted)" suffix, then normalise
            key = pred_label.lower()
            for suffix in ("(predicted)", "pred", "predicted"):
                key = key.replace(suffix, "")
            key = key.replace(" ", "").replace("(", "").replace(")", "")

            match = true_index.get(key)
            if match is None:
                # Loose fallback: substring match either way
                for k, v in true_index.items():
                    if key and (key in k or k in key):
                        match = v
                        break

            if match is not None:
                true_pos, src_node, src_label, _ = match
                err = float(np.linalg.norm(np.asarray(pred_pos) - np.asarray(true_pos)))
                results.append({
                    "name": pred_label,
                    "pred": np.asarray(pred_pos, dtype=float),
                    "true": np.asarray(true_pos, dtype=float),
                    "error": err,
                    "true_source": (src_node, src_label),
                })
            else:
                results.append({
                    "name": pred_label,
                    "pred": np.asarray(pred_pos, dtype=float),
                    "true": None,
                    "error": None,
                    "true_source": None,
                })
        return results

    def lineIntersection(self, p1, v1, p2, v2):
        A = np.array([v1, -v2]).T; b = p2 - p1
        try:
            ts = np.linalg.lstsq(A, b, rcond=None)[0]; return p1 + ts[0] * v1
        except np.linalg.LinAlgError: return None

    def _safe_normalize(self, v, fallback=None):
        v = np.asarray(v, dtype=float)
        n = np.linalg.norm(v)
        if not np.isfinite(n) or n < 1e-8:
            return np.asarray(fallback, dtype=float) if fallback is not None else None
        return v / n


    def getPointPosByName(self, nodeName, pointNames):
        node = self.getNode(nodeName, className="vtkMRMLMarkupsFiducialNode")
        if not node: return None
        available_points_lower = {node.GetNthControlPointLabel(i).lower(): self.getNthPointPos(node, i) for i in range(node.GetNumberOfControlPoints())}
        found_pos = {}
        for name in pointNames:
            name_lower = name.lower().replace(" ", "")
            for label, pos in available_points_lower.items():
                label_lower = label.lower().replace(" ", "")
                if name_lower in label_lower:
                    found_pos[name] = pos
                    break
        if len(found_pos) != len(pointNames):
            missing = set(pointNames) - set(found_pos.keys()); logging.warning(f"Could not find points: {missing} in node '{nodeName}'"); return None
        return [found_pos[name] for name in pointNames] if len(pointNames) > 1 else found_pos[pointNames[0]]

    def getNthPointPos(self, node, i):
        pos = np.zeros(3); node.GetNthControlPointPositionWorld(i, pos); return pos

    def downloadFile(self, url, filename, force=False):
        local_path = os.path.join(slicer.app.temporaryPath, filename)
        if not force and os.path.exists(local_path):
            return local_path
        try:
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, local_path)
            return local_path
        except Exception as e:
            slicer.util.errorDisplay(f"Download failed: {e}")
            return None

    def downloadAndLoadHardTissue(self):
        path = self.downloadFile("https://github.com/user-attachments/files/22662064/lmrks_Stephan.mrk.json", "lmrks_Stephan.mrk.json")
        if path:
            self.getNode("lmrks_Stephan", exact=True) and slicer.mrmlScene.RemoveNode(self.getNode("lmrks_Stephan", exact=True))
            node = slicer.util.loadMarkups(path); node.SetName("lmrks_Stephan")
            return True
        return False

    def createReferencePlane(self, plane_type):
        self.cleanup()
        points = self.getPointPosByName('lmrks_Stephan',
            ["Inion", "Nasion", "Bregma"] if plane_type == 'INB'
            else ["Nasion", "Rhinion", "Acanthion", "Point A", "Prosthion"])
        if not points:
            slicer.util.errorDisplay(f"Required landmarks for {plane_type} plane not found.")
            return False

        if plane_type == 'INB':
            v1 = np.asarray(points[1]) - np.asarray(points[0])
            v2 = np.asarray(points[2]) - np.asarray(points[0])
            normal = np.cross(v1, v2)
            origin = np.asarray(points[0], dtype=float)
        else:
            pts = np.asarray(points, dtype=float)
            centroid = pts.mean(axis=0)
            # Use SVD — more numerically stable than eigh on covariance
            U, S, Vt = np.linalg.svd(pts - centroid, full_matrices=False)
            normal = Vt[-1]              # smallest singular vector = plane normal
            origin = centroid

        # --- GUARD: reject / repair zero-length normals ---
        norm = np.linalg.norm(normal)
        if not np.isfinite(norm) or norm < 1e-8:
            slicer.util.errorDisplay(
                f"Cannot compute a valid {plane_type} plane: the selected "
                f"landmarks are collinear or coincident.")
            return False
        normal = normal / norm

        planeNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsPlaneNode", plane_type)
        planeNode.SetOrigin(origin.tolist())
        planeNode.SetNormal(normal.tolist())
        planeNode.GetDisplayNode().SetOpacity(0.7)
        return True

    def isFrameworkComplete(self):
        items = { "x axis": "vtkMRMLMarkupsLineNode", "y axis": "vtkMRMLMarkupsLineNode", "nasion-point A": "vtkMRMLMarkupsLineNode",
                  "AA FHP": "vtkMRMLMarkupsLineNode", "nasal aperture base": "vtkMRMLMarkupsLineNode", "for c)": "vtkMRMLMarkupsLineNode", 
                  "Point X": "vtkMRMLMarkupsFiducialNode", "NAB point": "vtkMRMLMarkupsFiducialNode" }
        return all(self.getNode(name, className) for name, className in items.items())

    def areMeasurementsComplete(self):
        items = { "A) nasal bone angle": "vtkMRMLMarkupsAngleNode", "B) line": "vtkMRMLMarkupsLineNode", "C) line": "vtkMRMLMarkupsLineNode",
                  "D) nasal spine angle": "vtkMRMLMarkupsAngleNode", "E) line": "vtkMRMLMarkupsLineNode" }
        return all(self.getNode(name, className) for name, className in items.items())

    def getMeasurementValue(self, node_name, kind):
        """Return a scalar value for a measurement node.
        kind='GetAngleDegrees' → returns angle node's degrees.
        kind='length'           → returns length of the line node in mm.
        Returns None if the node is missing or malformed."""
        if kind == "GetAngleDegrees":
            node = self.getNode(node_name, "vtkMRMLMarkupsAngleNode")
            if not node:
                return None
            try:
                return float(node.GetAngleDegrees())
            except AttributeError:
                # Fallback for Slicer builds that expose only GetMeasurement
                try:
                    return float(node.GetMeasurement('angle'))
                except Exception:
                    return None
        if kind == "length":
            node = self.getNode(node_name, "vtkMRMLMarkupsLineNode")
            if not node or node.GetNumberOfControlPoints() < 2:
                return None
            p0 = self.getNthPointPos(node, 0)
            p1 = self.getNthPointPos(node, 1)
            return float(np.linalg.norm(np.asarray(p0) - np.asarray(p1)))
        return None

    def createFramework(self):
        self.cleanup(partial=True)
        planeNode = self.getNode('INB', "vtkMRMLMarkupsPlaneNode") or self.getNode('MSP', "vtkMRMLMarkupsPlaneNode")
        lmrks_node = self.getNode('lmrks_Stephan', "vtkMRMLMarkupsFiducialNode")
        if not all([lmrks_node, planeNode]): 
            slicer.util.errorDisplay("Please ensure landmarks (Step 1) and a plane (Step 2) are created first.")
            return False
        
        points = self.getPointPosByName('lmrks_Stephan', ["Nasion", "Point A", "point AA", "LL", "RL"])
        if not points: return False

        nasion_pos, pointA_pos, pointAA_pos, ll_pos, rl_pos = points
        planeNormal = self._safe_normalize(np.array(planeNode.GetNormal()))
        if planeNormal is None:
            slicer.util.errorDisplay("Reference plane has a degenerate normal.")
            return False

        # FHP is assumed to be the axial plane (S-I normal).
        fhpNormal = np.array([0.0, 0.0, 1.0])

        # dirX = intersection of the reference plane with FHP.
        dirX = np.cross(fhpNormal, planeNormal)
        n_dirX = np.linalg.norm(dirX)
        if n_dirX < 1e-6:
            # Reference plane is ~parallel to FHP → no unique intersection.
            # Fall back to a direction defined by real landmarks on the plane.
            inion_pos = self.getPointPosByName('lmrks_Stephan', ["Inion"])
            if inion_pos is not None and np.linalg.norm(np.array(inion_pos) - nasion_pos) > 1e-6:
                dirX = np.array(inion_pos) - nasion_pos   # Nasion→Inion line
            else:
                dirX = np.array([0.0, 1.0, 0.0])          # anterior, last resort
            n_dirX = np.linalg.norm(dirX)
        dirX = dirX / n_dirX

        # dirY is the plane normal (out of plane).
        dirY = planeNormal
        
        def create_line(name, p1, p2, color):
            node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
            node.AddControlPoint(p1); node.AddControlPoint(p2)
            node.GetDisplayNode().SetColor(color); node.GetDisplayNode().SetSelectedColor(color)
            return node
        create_line("x axis", nasion_pos - 100*dirX, nasion_pos + 100*dirX, [0, 1, 1])
        create_line("y axis", nasion_pos - 100*dirY, nasion_pos + 100*dirY, [0, 1, 1])
        nasion_proj = [0,0,0]; vtk.vtkPlane.ProjectPoint(nasion_pos, planeNode.GetOrigin(), planeNode.GetNormal(), nasion_proj)
        pointA_proj = [0,0,0]; vtk.vtkPlane.ProjectPoint(pointA_pos, planeNode.GetOrigin(), planeNode.GetNormal(), pointA_proj)
        dir_n_A = np.array(pointA_proj) - np.array(nasion_proj); dir_n_A /= np.linalg.norm(dir_n_A)
        n_A_line = create_line("nasion-point A", np.array(nasion_proj) - 100 * dir_n_A, np.array(nasion_proj) + 100 * dir_n_A, [0, 0, 1])
        aa_fhp_line = create_line("AA FHP", pointAA_pos - 100 * dirX, pointAA_pos + 100 * dirX, [1, 0.5, 0])
        pX_pos = self.lineIntersection(self.getNthPointPos(n_A_line, 0), dir_n_A, self.getNthPointPos(aa_fhp_line, 0), dirX)
        if pX_pos is None: return False
        
        nab_base_line = create_line("nasal aperture base", ll_pos, rl_pos, [0.1, 0.5, 0.1])
        
        t = vtk.mutable(0); intersection_point = [0,0,0]
        intersect_status = vtk.vtkPlane.IntersectWithLine(ll_pos, rl_pos, planeNode.GetOrigin(), planeNode.GetNormal(), t, intersection_point)
        if intersect_status != 0: nab_point_pos = intersection_point
        else: nab_point_pos = (np.array(ll_pos) + np.array(rl_pos)) / 2.0

        create_line("for c)", nab_point_pos - 100 * dir_n_A, nab_point_pos + 100 * dir_n_A, [1, 0.7, 0.8])
        pointX_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', "Point X"); pointX_node.AddControlPoint(pX_pos, "Point X")
        nab_point_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', "NAB point"); nab_point_node.AddControlPoint(nab_point_pos, "NAB point")
        return True

    def createMeasurements(self):
        self.cleanup(measurements=True)
        try:
            required_nodes = { "lmrks_Stephan": self.getNode("lmrks_Stephan", "vtkMRMLMarkupsFiducialNode"), "Point X": self.getNode("Point X", "vtkMRMLMarkupsFiducialNode"),
                               "x axis": self.getNode("x axis", "vtkMRMLMarkupsLineNode"), "nasal aperture base": self.getNode("nasal aperture base", "vtkMRMLMarkupsLineNode"),
                               "for c)": self.getNode("for c)", "vtkMRMLMarkupsLineNode"), "AA FHP": self.getNode("AA FHP", "vtkMRMLMarkupsLineNode") }
            for name, node in required_nodes.items():
                if not node: raise ValueError(f"Required node '{name}' not found in the scene.")

            points = self.getPointPosByName('lmrks_Stephan', ["Nasion", "Rhinion", "Acanthion"])
            if not points: raise ValueError("Required points (Nasion, Rhinion, Acanthion) not found in 'lmrks_Stephan'.")
            
            nasion_pos, rhinion_pos, acanthion_pos = points
            pointX_pos = self.getNthPointPos(required_nodes["Point X"], 0)
            
            x_axis_p2 = self.getNthPointPos(required_nodes["x axis"], 1)
            angleNodeA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'A) nasal bone angle'); angleNodeA.AddControlPoint(x_axis_p2); angleNodeA.AddControlPoint(nasion_pos); angleNodeA.AddControlPoint(rhinion_pos)

            nab_base_line = required_nodes["nasal aperture base"]
            p1 = self.getNthPointPos(nab_base_line, 0); p2 = self.getNthPointPos(nab_base_line, 1)
            closest_point_b = [0,0,0]; vtk.vtkLine.DistanceToLine(acanthion_pos, p1, p2, vtk.mutable(0), closest_point_b)
            line_b = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'B) line'); line_b.AddControlPoint(acanthion_pos); line_b.AddControlPoint(closest_point_b)

            for_c_line = required_nodes["for c)"]
            p1_c = self.getNthPointPos(for_c_line, 0); p2_c = self.getNthPointPos(for_c_line, 1)
            closest_point_c = [0,0,0]; vtk.vtkLine.DistanceToLine(rhinion_pos, p1_c, p2_c, vtk.mutable(0), closest_point_c)
            line_c = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'C) line'); line_c.AddControlPoint(rhinion_pos); line_c.AddControlPoint(closest_point_c)

            aa_fhp_ant = self.getNthPointPos(required_nodes["AA FHP"], 1)
            angleNodeD = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'D) nasal spine angle'); angleNodeD.AddControlPoint(acanthion_pos); angleNodeD.AddControlPoint(pointX_pos); angleNodeD.AddControlPoint(aa_fhp_ant)
            
            line_e = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'E) line'); line_e.AddControlPoint(nasion_pos); line_e.AddControlPoint(pointX_pos)
            return True
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to create measurements. Please ensure the framework is complete. Error: {e}")
            return False

    def calculatePrediction(self, sex):
        self.cleanup(prediction=True)
        try:
            measurement_nodes = { "A) nasal bone angle": self.getNode("A) nasal bone angle", "vtkMRMLMarkupsAngleNode"),
                                  "B) line": self.getNode("B) line", "vtkMRMLMarkupsLineNode"), "C) line": self.getNode("C) line", "vtkMRMLMarkupsLineNode"),
                                  "D) nasal spine angle": self.getNode("D) nasal spine angle", "vtkMRMLMarkupsAngleNode"), "E) line": self.getNode("E) line", "vtkMRMLMarkupsLineNode") }
            if not all(measurement_nodes.values()): raise ValueError("Not all measurement nodes (A, B, C, D, E) were found.")
            
            nasion_pos = self.getPointPosByName("lmrks_Stephan", ["Nasion"])
            if nasion_pos is None: raise ValueError("Nasion point not found in 'lmrks_Stephan'.")

            val_a = measurement_nodes["A) nasal bone angle"].GetAngleDegrees()
            val_b = np.linalg.norm(self.getNthPointPos(measurement_nodes["B) line"], 0) - self.getNthPointPos(measurement_nodes["B) line"], 1))
            val_c = np.linalg.norm(self.getNthPointPos(measurement_nodes["C) line"], 0) - self.getNthPointPos(measurement_nodes["C) line"], 1))
            val_d = measurement_nodes["D) nasal spine angle"].GetAngleDegrees()
            val_e = np.linalg.norm(self.getNthPointPos(measurement_nodes["E) line"], 0) - self.getNthPointPos(measurement_nodes["E) line"], 1))

            if sex == "Female":
                pos_x = -0.41 * val_a + 0.37 * val_b + 49.87
            else: # Male
                pos_x = -0.32 * val_a + 0.85 * val_b - 0.42 * val_c + 49.58
            pos_y = (-0.002 * val_d + 0.83) * val_e

            anterior_dir = np.array([0, 1, 0]); inferior_dir = np.array([0, 0, -1])
            intermediate_point = np.array(nasion_pos) + (inferior_dir * pos_y)
            final_point = intermediate_point + (anterior_dir * pos_x)

            pred_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'pronasale pred')
            pred_node.AddControlPoint(final_point, 'Pronasale (Predicted)')
            pred_node.GetDisplayNode().SetSelectedColor(1, 0, 0)
            return True
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to calculate prediction. Error: {e}")
            return False

    def downloadAndLoadSoftTissue(self):
        path = self.downloadFile("https://github.com/user-attachments/files/20213398/soft_tissue_Stephan.mrk.json", "soft_tissue_Stephan.mrk.json")
        if path:
            self.getNode("soft_tissue_Stephan", exact=True) and slicer.mrmlScene.RemoveNode(self.getNode("soft_tissue_Stephan", exact=True))
            node = slicer.util.loadMarkups(path); node.SetName("soft_tissue_Stephan")
            return True
        return False

    def findPronasaleInAllLandmarks(self):
        """
        Search every vtkMRMLMarkupsFiducialNode in the scene (excluding our own
        prediction node) for a control point whose label contains 'pronasale'.
        Returns (position_np_array, node_name, point_label) or None.
        """
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
        matches = []
        for i in range(nodes.GetNumberOfItems()):
            node = nodes.GetItemAsObject(i)
            if node.GetName() == "pronasale pred":
                continue
            for j in range(node.GetNumberOfControlPoints()):
                label = node.GetNthControlPointLabel(j)
                if "pronasale" in label.lower():
                    pos = np.zeros(3)
                    node.GetNthControlPointPositionWorld(j, pos)
                    matches.append((pos.copy(), node.GetName(), label))
        if not matches:
            return None
        # If multiple matches, prefer the one from a node whose name
        # contains 'soft' (i.e. the true soft-tissue file); else first match.
        matches.sort(key=lambda m: (("soft" not in m[1].lower()), m[1]))
        return matches[0]

    def listPronasaleMatches(self):
        """Return all matches for display/debugging."""
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
        out = []
        for i in range(nodes.GetNumberOfItems()):
            node = nodes.GetItemAsObject(i)
            if node.GetName() == "pronasale pred":
                continue
            for j in range(node.GetNumberOfControlPoints()):
                label = node.GetNthControlPointLabel(j)
                if "pronasale" in label.lower():
                    pos = np.zeros(3); node.GetNthControlPointPositionWorld(j, pos)
                    out.append((node.GetName(), label, pos.copy()))
        return out
    
    def comparePrediction(self):
        """Returns (rows, overall_error_mm) where rows is the list produced
        by buildLandmarkComparison. Also draws one error line per matched
        landmark."""
        self.cleanup(comparison=True)
        rows = self.buildLandmarkComparison()
        if not rows:
            raise ValueError("No predicted landmarks found. Run Step 5 first.")
        matched = [r for r in rows if r["error"] is not None]
        if not matched:
            raise ValueError(
                "No matching true landmarks were found. Load a fiducial list "
                "that contains a 'pronasale' (or corresponding) control point.")

        for r in matched:
            line = slicer.mrmlScene.AddNewNodeByClass(
                "vtkMRMLMarkupsLineNode", f"error_{r['name']}")
            line.AddControlPoint(r["pred"].tolist())
            line.AddControlPoint(r["true"].tolist())
            line.GetDisplayNode().SetSelectedColor(1, 1, 0)
        return rows

# --- Entry Point to start the GUI ---
# Close any previous top-level GUI windows of this type
try:
    for w in qt.QApplication.topLevelWidgets():
        if w.objectName == "StephanMethodGUI":
            w.close()
            w.deleteLater()
except Exception:
    pass

stephanGui = StephanMethodGUI()
stephanGui.show()

```
