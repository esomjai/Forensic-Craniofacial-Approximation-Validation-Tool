```python
# Threefold ANS Method GUI - Version 60 (Manual navigation only)

import os
import vtk
import numpy as np
import qt
import slicer
import urllib.request
import tempfile

class ThreefoldANSGUI(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle("Threefold ANS Method")
        self.setObjectName("ThreefoldANSGUI")
        
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setSpacing(10)
        
        self.stepStack = qt.QStackedWidget()
        self.mainLayout.addWidget(self.stepStack)
        
        # Node storage
        self.landmarksNode = None
        self.referencePlane = None
        self.boneModel = None
        self.volumeNode = None
        self.boneLeftModel = None
        self.boneRightModel = None
        self.vmjAcaLine = None
        self.nasalSpineVector = None
        self.subProLine = None
        self.predictedPronasaleNode = None
        self.trueSoftTissueNode = None
        
        # Observers and flags
        self.vmjObserver = None
        self.vectorObserver = None
        self.mpObserver = None
        self.isDynamicModelerInstalled = False
        self._isUpdatingVector = False
        self._isUpdatingMP = False
        self._initialMPPos = None
        self._mp_index = -1
        self.step6_complete = False
        self.step5_complete = False
        self.step4_skipped = False
        self.manualVolumeRendering = False
        
        # Cylinder radius - default 2.0 mm (also used as search radius)
        self.cylinderRadius = 2.0
        
        # IMPORTANT: must exist before syncWithScene(), because syncWithScene()
        # indirectly calls updateStepUI() which reads self.currentStep.
        self.currentStep = 0
        
        self.createAllStepWidgets()
        self.setupNavigation()
        self.checkDependencies()
        self.syncWithScene()
        
        # Now that the scene is synced, detect the real step.
        self.currentStep = self.determineCurrentStep()
        self.updateStepUI()
        
        # No scene observers – manual navigation only

    def createAllStepWidgets(self):
        self.createStep1_Welcome()
        self.createStep2_PlaneSetup()
        self.createStep3_Segmentation()
        self.createStep4_CutModel()
        self.createStep5_VMJ_Line()
        self.createStep6_VectorAndMidphiltrum()
        self.createStep7_PronasalePrediction()
        self.createStep8_Validation()
        self.createStep9_Results()

    def cleanup(self):
        if self.vmjObserver and self.landmarksNode:
            self.landmarksNode.RemoveObserver(self.vmjObserver)
            self.vmjObserver = None
        if self.vectorObserver and self.nasalSpineVector:
            self.nasalSpineVector.RemoveObserver(self.vectorObserver)
            self.vectorObserver = None
        if self.mpObserver and self.landmarksNode:
            self.landmarksNode.RemoveObserver(self.mpObserver)
            self.mpObserver = None

    def checkDependencies(self):
        moduleName = "DynamicModeler"
        if moduleName in slicer.app.moduleManager().factoryManager().registeredModuleNames():
            self.isDynamicModelerInstalled = True
        else:
            self.isDynamicModelerInstalled = False
            msgBox = qt.QMessageBox()
            msgBox.setWindowTitle("Missing Required Extension")
            msgBox.setIcon(qt.QMessageBox.Warning)
            msgBox.setTextFormat(qt.Qt.RichText)
            msgBox.setText(
                "The <b>Dynamic Modeler</b> extension is required for skull cutting (Step 4), but it was not found.<br><br>"
                "Please install it to use that step.<br><br>"
                "If you chose the Volume Rendering option, you can skip cutting and continue without it."
            )
            msgBox.exec_()

    def setupNavigation(self):
        navWidget = qt.QWidget()
        navLayout = qt.QHBoxLayout(navWidget)
        navLayout.setContentsMargins(0, 0, 0, 0)
        self.prevButton = qt.QPushButton("Previous")
        self.prevButton.setToolTip("Go to the previous step.")
        self.prevButton.clicked.connect(self.onPrevButtonClicked)
        self.stepLabel = qt.QLabel("Step 1/9")
        self.stepLabel.setAlignment(qt.Qt.AlignCenter)
        self.stepLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.nextButton = qt.QPushButton("Next")
        self.nextButton.setToolTip("Go to the next step.")
        self.nextButton.clicked.connect(self.onNextButtonClicked)
        navLayout.addWidget(self.prevButton)
        navLayout.addStretch(1)
        navLayout.addWidget(self.stepLabel)
        navLayout.addStretch(1)
        navLayout.addWidget(self.nextButton)
        self.mainLayout.addWidget(navWidget)

    # ==================== AUTO STEP DETECTION (for initial and validation only) ====================
    def determineCurrentStep(self):
        """
        Determine which step the user is at based on scene contents.
        Used only for initial step and validation.
        """
        if self.landmarksNode is None:
            return 0
        if self.referencePlane is None:
            return 1
        if self.boneModel is None and not self.manualVolumeRendering:
            if self.volumeNode is None:
                return 2
        if self.boneLeftModel is None or self.boneRightModel is None:
            if not self.step4_skipped:
                return 3
        if self.vmjAcaLine is None:
            return 4
        if self.nasalSpineVector is None:
            return 5
        if self.landmarksNode and self.findPointIndex("mp") == -1:
            return 5
        if self.predictedPronasaleNode is None:
            return 6
        error_line = slicer.util.getFirstNodeByName("prediction_error")
        if error_line is not None:
            return 8
        else:
            return 7

    # ==================== STEP 1 ====================
    def createStep1_Welcome(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        title = qt.QLabel("Welcome to the Threefold ANS Method")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(title)
        desc = qt.QLabel(
            "This tool will guide you through the workflow step-by-step.\n\n"
            "Please begin by loading the required hard tissue landmarks using one of the options below."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        buttonLayout = qt.QVBoxLayout()
        buttonLayout.setSpacing(10)
        
        self.loadLocalButton = qt.QPushButton("Load Landmarks from Local File")
        self.loadLocalButton.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 8px;")
        self.loadLocalButton.clicked.connect(self.onLoadLocalLandmarks)
        buttonLayout.addWidget(self.loadLocalButton, 0, qt.Qt.AlignHCenter)
        
        self.downloadHardButton = qt.QPushButton("Download hard tissue landmarks")
        self.downloadHardButton.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        self.downloadHardButton.clicked.connect(self.onDownloadHardLandmarks)
        buttonLayout.addWidget(self.downloadHardButton, 0, qt.Qt.AlignHCenter)
        
        self.downloadSoftButton = qt.QPushButton("Download soft tissue landmarks")
        self.downloadSoftButton.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        self.downloadSoftButton.clicked.connect(self.onDownloadSoftLandmarks)
        buttonLayout.addWidget(self.downloadSoftButton, 0, qt.Qt.AlignHCenter)
        
        layout.addLayout(buttonLayout)
        self.step1StatusLabel = qt.QLabel("Status: Waiting for user.")
        self.step1StatusLabel.setWordWrap(True)
        layout.addWidget(self.step1StatusLabel)
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    # ==================== STEP 2 ====================
    def createStep2_PlaneSetup(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        title = qt.QLabel("Step 2: Create a Reference Plane")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        desc_html = """
        <p>Now, create a reference plane using the landmarks you just loaded.</p>
        <p>
            • <b>INB Plane</b>: Uses Nasion, Inion, and Bregma. This creates a simple three-point plane.<br><br>
            • <b>MSP (Best-Fit) Plane</b>: Uses multiple midsagittal landmarks (nasion, acanthion, prosthion, subspinale) to calculate a more robust, best-fit midsagittal plane.
        </p>
        """
        desc = qt.QLabel(desc_html)
        desc.setTextFormat(qt.Qt.RichText)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        planeChoiceLayout = qt.QVBoxLayout()
        planeChoiceLayout.setSpacing(10)
        self.planeChoiceComboBox = qt.QComboBox()
        self.planeChoiceComboBox.addItems(["Select a method...", "INB (Inion-Nasion-Bregma)", "MSP (Midsagittal Best-Fit)"])
        self.createPlaneButton = qt.QPushButton("Create Plane")
        self.createPlaneButton.clicked.connect(self.onCreatePlane)
        planeChoiceLayout.addWidget(self.planeChoiceComboBox)
        planeChoiceLayout.addWidget(self.createPlaneButton)
        layout.addLayout(planeChoiceLayout)
        self.step2StatusLabel = qt.QLabel("Status: Please choose a plane creation method.")
        self.step2StatusLabel.setWordWrap(True)
        layout.addWidget(self.step2StatusLabel)
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    # ==================== STEP 3 ====================
    def createStep3_Segmentation(self):
        widget = qt.QWidget()
        mainLayout = qt.QVBoxLayout(widget)
        mainLayout.setSpacing(15)

        title = qt.QLabel("Step 3: Obtain a Skull Model (or Volume)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        mainLayout.addWidget(title)

        methodGroup = qt.QGroupBox("Choose how to get the Bone model")
        methodLayout = qt.QVBoxLayout(methodGroup)

        self.segmentationRadio = qt.QRadioButton("Perform Segmentation (detailed instructions)")
        self.segmentationRadio.setChecked(True)
        self.loadModelRadio = qt.QRadioButton("Load existing Bone model")
        self.volumeRenderRadio = qt.QRadioButton("Use Volume Rendering (skip model loading)")
        self.volumeRenderRadio.toggled.connect(self.onVolumeRenderToggled)
        self.loadModelRadio.toggled.connect(self.onLoadModelToggled)
        self.segmentationRadio.toggled.connect(self.onSegmentationToggled)

        methodLayout.addWidget(self.segmentationRadio)
        methodLayout.addWidget(self.loadModelRadio)
        methodLayout.addWidget(self.volumeRenderRadio)
        mainLayout.addWidget(methodGroup)

        # ---- Segmentation container ----
        self.segmentationContainer = qt.QWidget()
        segLayout = qt.QVBoxLayout(self.segmentationContainer)
        segLayout.setContentsMargins(0, 0, 0, 0)

        instructions = qt.QLabel()
        instructions.setTextFormat(qt.Qt.RichText)
        instructions.setOpenExternalLinks(True)
        instructions.setWordWrap(True)
        instructions.setText(
            "Follow these steps carefully to create a clean 'Bone' model.<br><br>"
            "<b>1. Open Segment Editor:</b> Click this button to open the module.<br>"
        )
        segLayout.addWidget(instructions)

        self.openSegmentEditorButton = qt.QPushButton("Open Segment Editor Module")
        self.openSegmentEditorButton.clicked.connect(lambda: slicer.util.selectModule('SegmentEditor'))
        segLayout.addWidget(self.openSegmentEditorButton)

        instructions2 = qt.QLabel()
        instructions2.setTextFormat(qt.Qt.RichText)
        instructions2.setOpenExternalLinks(True)
        instructions2.setWordWrap(True)
        instructions2.setText(
            "<br><b>2. Rename your segmentation:</b> Click the dropdown menu next to <b>Segmentation:</b> and choose 'Rename current Segmentation'.<br><br>"
            "<b>3. Source Volume</b> should be the name of your DICOM file.<br><br>"
            "<b>4. Click the plus sign [+] 'Add'.</b><br><br>"
            "<b>5. Choose the Threshold tool</b> from the panel below (in the right column, first row).<br><br>"
            "<b>6. Edit the Threshold Range:</b> The minimum is usually 500. (<a href='https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/003_ROI%20vs%20Segmentation.md'>Refer to this guide for more detail</a>).<br><br>"
            "<b>7. Click 'Apply'</b> (in the Local histogram menu), then find the <b>'Show 3D'</b> button on the top, near to where the 'Add' button was. Click it and wait for the model to appear.<br><br>"
            "<b>8. If you're happy with the details,</b> click on the green right arrow to go to the 'Segmentations' module.<br><br>"
            "<b>9. Double click on the row below 'Name'</b> and in the pop-up, edit the model name into <b>'Bone'</b>.<br><br>"
            "<b>10. Scroll to the dropdown menu 'Export/import models and labelmaps':</b> Make sure the <b>Operation</b> is 'Export' and the <b>Output type</b> is 'Models'. Then move down to the next menu (Export to files), choose the destination folder and click the 'Export' button in this submenu.<br><br>"
            "<b>11. IMPORTANT:</b> You need to import this model back into the scene by clicking the <b>'Data'</b> button (very top of the Slicer window, under 'File'), 'Choose file(s) to add...', and finding the model you just exported.<br><br>"
            "<b>12. Select the re-imported model below.</b>"
        )
        segLayout.addWidget(instructions2)

        confirmGroup = qt.QGroupBox("Final Confirmation")
        confirmLayout = qt.QFormLayout(confirmGroup)
        confirmLabel = qt.QLabel("Once the model is re-imported, please select it below:")
        confirmLabel.setWordWrap(True)

        self.boneModelSelector = slicer.qMRMLNodeComboBox()
        self.boneModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.boneModelSelector.setMRMLScene(slicer.mrmlScene)
        self.boneModelSelector.addEnabled = False
        self.boneModelSelector.removeEnabled = False
        self.boneModelSelector.noneEnabled = True
        self.boneModelSelector.setToolTip("Select the 'Bone' model you just re-imported.")
        self.boneModelSelector.currentNodeChanged.connect(self.onConfirmSegmentation)

        confirmLayout.addRow(confirmLabel)
        confirmLayout.addRow("Re-imported Bone Model:", self.boneModelSelector)
        segLayout.addWidget(confirmGroup)

        mainLayout.addWidget(self.segmentationContainer)

        # ---- Load existing model container ----
        self.loadContainer = qt.QWidget()
        loadLayout = qt.QVBoxLayout(self.loadContainer)
        loadLayout.setContentsMargins(0, 0, 0, 0)

        loadLabel = qt.QLabel(
            "If you already have a bone model (e.g., from a previous segmentation or external file), "
            "you can load it here and skip the segmentation steps."
        )
        loadLabel.setWordWrap(True)
        loadLayout.addWidget(loadLabel)

        self.existingModelSelector = slicer.qMRMLNodeComboBox()
        self.existingModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.existingModelSelector.setMRMLScene(slicer.mrmlScene)
        self.existingModelSelector.addEnabled = False
        self.existingModelSelector.removeEnabled = False
        self.existingModelSelector.noneEnabled = True
        self.existingModelSelector.setToolTip("Select an existing model from the scene.")
        loadLayout.addWidget(self.existingModelSelector)

        self.loadModelButton = qt.QPushButton("Set selected as Bone model")
        self.loadModelButton.clicked.connect(self.onLoadExistingModel)
        loadLayout.addWidget(self.loadModelButton)

        self.importModelButton = qt.QPushButton("Load model from file (STL, VTK, PLY, ...)")
        self.importModelButton.clicked.connect(self.onImportModelFromFile)
        loadLayout.addWidget(self.importModelButton)

        mainLayout.addWidget(self.loadContainer)

        # ---- Volume rendering container ----
        self.volumeContainer = qt.QWidget()
        volLayout = qt.QVBoxLayout(self.volumeContainer)
        volLayout.setContentsMargins(0, 0, 0, 0)

        volTitle = qt.QLabel("<b>📊 Volume Rendering Mode (No Model Required)</b>")
        volTitle.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9800;")
        volTitle.setWordWrap(True)
        volLayout.addWidget(volTitle)

        volDesc = qt.QLabel(
            "You will use the CT volume directly — no bone model is needed.\n\n"
            "<b>Step 1:</b> Select your CT volume from the dropdown below.\n"
            "<b>Step 2:</b> Click 'Open Volume Rendering' to visualise the skull (use the `Shift` toggle to exclude soft tissue).\n"
            "<b>Step 3:</b> Use the Volume Rendering module ROI to cut the skull in half for placing the VMJ and the nasal spine line.\n"
            "<b>Step 4:</b> Click 'Continue without model' to proceed.\n\n"
            "⚠️ <b>Note:</b> The FSTT cylinder will be computed directly from the CT volume."
        )
        volDesc.setWordWrap(True)
        volDesc.setStyleSheet("background-color: #FFF8E1; padding: 8px; border-radius: 5px;")
        volLayout.addWidget(volDesc)

        # Volume selector
        volLayout.addWidget(qt.QLabel("<b>CT Volume:</b>"))
        self.volumeSelectorVR = slicer.qMRMLNodeComboBox()
        self.volumeSelectorVR.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.volumeSelectorVR.setMRMLScene(slicer.mrmlScene)
        self.volumeSelectorVR.addEnabled = False
        self.volumeSelectorVR.removeEnabled = False
        self.volumeSelectorVR.noneEnabled = True
        self.volumeSelectorVR.setToolTip("Select the CT volume for surface normal detection")
        self.volumeSelectorVR.currentNodeChanged.connect(self.onVolumeSelectedVR)
        volLayout.addWidget(self.volumeSelectorVR)

        # Button row
        buttonRow = qt.QHBoxLayout()
        self.openVolumeRenderingButton = qt.QPushButton("📦 Open Volume Rendering Module")
        self.openVolumeRenderingButton.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        self.openVolumeRenderingButton.clicked.connect(lambda: slicer.util.selectModule('VolumeRendering'))
        buttonRow.addWidget(self.openVolumeRenderingButton)

        self.continueWithoutModelButton = qt.QPushButton("✅ Continue without model")
        self.continueWithoutModelButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.continueWithoutModelButton.clicked.connect(self.onContinueWithoutModel)
        buttonRow.addWidget(self.continueWithoutModelButton)
        volLayout.addLayout(buttonRow)

        #Quick volume rendering instructions (collapsible)
        volHelpButton = qt.QPushButton("📖 Show Volume Rendering Tips")
        volHelpButton.setStyleSheet("background-color: #E3F2FD; color: #1565C0; padding: 5px;")
        volHelpButton.setCheckable(True)
        volHelpButton.toggled.connect(lambda checked: volHelpContainer.setVisible(checked))
        volLayout.addWidget(volHelpButton)

        volHelpContainer = qt.QWidget()
        volHelpContainer.setVisible(False)
        volHelpLayout = qt.QVBoxLayout(volHelpContainer)
        volHelpLayout.setContentsMargins(10, 10, 10, 10)
        volHelpContainer.setStyleSheet("background-color: #F5F5F5; border-radius: 5px;")

        volTips = qt.QLabel(
            "<b>💡 Tips for Volume Rendering:</b><br><br>"
            "• <b>To see the current ROI:</b> In the Volume Rendering module, under 'Display', "
            "find the 'Crop' section and click the eye icon next to 'Display ROI' to make the ROI visible.<br><br>"
            "• <b>To cut the skull in half:</b> Tick the 'Enable' checkbox under Crop. "
            "Then drag the ROI box handles to cut the skull around the acanthion landmark.<br><br>"
            "• <b>To orientate the anterior nasal spine vector:</b> It follows the general direction of the anterior nasal spine, like an arrowhead (aca) pointing anteriorly.<br><br>"
            "• <b>When you're done:</b> Untick 'Enable' under Crop to restore the full skull view, "
            "and close the eye icon for 'Display ROI'."
        )
        volTips.setWordWrap(True)
        volHelpLayout.addWidget(volTips)
        volLayout.addWidget(volHelpContainer)

        mainLayout.addWidget(self.volumeContainer)

        # Initially show segmentation container, hide others
        self.segmentationContainer.setVisible(True)
        self.loadContainer.setVisible(False)
        self.volumeContainer.setVisible(False)

        self.step3StatusLabel = qt.QLabel("Status: Waiting for user to obtain a bone model or select volume.")
        self.step3StatusLabel.setWordWrap(True)
        mainLayout.addWidget(self.step3StatusLabel)

        mainLayout.addStretch(1)
        self.stepStack.addWidget(widget)

        self.onSegmentationToggled()

    # ------- Toggle handlers -------
    def onSegmentationToggled(self):
        if self.segmentationRadio.isChecked():
            self.segmentationContainer.setVisible(True)
            self.loadContainer.setVisible(False)
            self.volumeContainer.setVisible(False)
            self.step3StatusLabel.setText("Status: Follow the segmentation instructions above.")
            self.manualVolumeRendering = False

    def onLoadModelToggled(self):
        if self.loadModelRadio.isChecked():
            self.segmentationContainer.setVisible(False)
            self.loadContainer.setVisible(True)
            self.volumeContainer.setVisible(False)
            self.step3StatusLabel.setText("Status: Load an existing model or import from file.")
            self.manualVolumeRendering = False

    def onVolumeRenderToggled(self):
        if self.volumeRenderRadio.isChecked():
            self.segmentationContainer.setVisible(False)
            self.loadContainer.setVisible(False)
            self.volumeContainer.setVisible(True)
            self.step3StatusLabel.setText("Status: Volume Rendering mode selected. Select a volume and click 'Continue'.")
            self.manualVolumeRendering = True

    def onVolumeSelectedVR(self, node):
        if node:
            self.volumeNode = node
            self.step3StatusLabel.setText(f"Status: Volume '{node.GetName()}' selected. You can continue.")
        else:
            self.volumeNode = None
            self.step3StatusLabel.setText("Status: Please select a volume or continue without one (will prompt later).")

    def onContinueWithoutModel(self):
        self.step3StatusLabel.setText("Status: Continuing without bone model. Prediction will use volume if available.")
        self.manualVolumeRendering = True
        # Move to next step manually (if user clicked this button, they want to proceed)
        # We'll simulate a Next click.

    # ------- Load existing model helpers -------
    def onLoadExistingModel(self):
        node = self.existingModelSelector.currentNode()
        if node:
            self.boneModel = node
            self.step3StatusLabel.setText(f"Status: Loaded '{node.GetName()}' as the bone model. Ready to proceed!")
            slicer.util.showStatusMessage(f"Bone model set to '{node.GetName()}'", 3000)
            self.manualVolumeRendering = False
            # Do not auto-step; just update UI
            self.updateStepUI()
        else:
            slicer.util.warningDisplay("Please select a model from the list first.")

    def onImportModelFromFile(self):
        fileNames = qt.QFileDialog.getOpenFileNames(
            self,
            "Select Bone Model File",
            "",
            "Model Files (*.stl *.vtk *.ply *.obj);;All Files (*)"
        )
        if fileNames:
            fileName = fileNames[0]
            try:
                loadedNode = slicer.util.loadModel(fileName)
                if loadedNode:
                    loadedNode.SetName("Bone")
                    self.boneModel = loadedNode
                    self.step3StatusLabel.setText(f"Status: Loaded '{loadedNode.GetName()}' from file. Ready to proceed!")
                    slicer.util.showStatusMessage(f"Bone model loaded from {fileName}", 3000)
                    self.existingModelSelector.setCurrentNode(loadedNode)
                    self.manualVolumeRendering = False
                    self.updateStepUI()
                else:
                    raise RuntimeError("Failed to load model.")
            except Exception as e:
                slicer.util.errorDisplay(f"Could not load model from file: {e}")

    # ==================== STEP 4 ====================
    def createStep4_CutModel(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(10)
        title = qt.QLabel("Step 4: Cut the Bone Model (Optional)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        self.cutWarningLabel = qt.QLabel()
        self.cutWarningLabel.setWordWrap(True)
        self.cutWarningLabel.setStyleSheet("color: #FF5722; font-weight: bold;")
        layout.addWidget(self.cutWarningLabel)

        open_modeller_layout = qt.QHBoxLayout()
        open_modeller_label = qt.QLabel("<b>1.</b> First, click the button to open the Dynamic Modeler module.")
        open_modeller_label.setTextFormat(qt.Qt.RichText)
        self.openDynamicModelerButton = qt.QPushButton("Open Dynamic Modeler")
        self.openDynamicModelerButton.clicked.connect(self.onOpenDynamicModeler)
        open_modeller_layout.addWidget(open_modeller_label)
        open_modeller_layout.addStretch()
        open_modeller_layout.addWidget(self.openDynamicModelerButton)
        layout.addLayout(open_modeller_layout)

        layout.addSpacing(15)

        roi_tip_label = qt.QLabel()
        roi_tip_label.setTextFormat(qt.Qt.RichText)
        roi_tip_label.setWordWrap(True)
        roi_tip_label.setText(
            "<b>If your model is too large</b> or slow to process, you can use the 'ROI cut' tool to trim it down first:<br><br>"
            "&bull; Go to the <b>'Markups'</b> module and create a new <b>ROI</b>, drawing a box around the area you want to keep.<br><br>"
            "&bull; Return to the <b>'Dynamic Modeler'</b> module and use the <b>'ROI cut'</b> tool.<br><br>"
            "&bull; Set the 'Input Model' (your bone model) and the 'ROI node' (the box you just drew).<br><br>"
            "&bull; In 'Output nodes', find 'Clipped output model (inside)' and select your original model. This will <b>replace</b> it with the smaller version.<br><br>"
            "&bull; Click 'Apply' to finish."
        )
        layout.addWidget(roi_tip_label)

        layout.addSpacing(15)

        plane_cut_label = qt.QLabel()
        plane_cut_label.setTextFormat(qt.Qt.RichText)
        plane_cut_label.setWordWrap(True)
        plane_cut_label.setText(
            "<b>2.</b> Now, for the main task, use the '<b>Plane Cut</b>' option in the Dynamic Modeler:<br><br>"
            "&bull; Set the 'Input Model' to your re-imported 'Bone' model and the 'Input Plane' to the reference plane you created in Step 2.<br><br>"
            "&bull; In the 'Parameters' line, tick <b>'Cap surface'</b> for better visibility and leave the 'Operation type' as 'Union'.<br><br>"
            "&bull; Make sure you create new models for each side. Choose <b>'Create new Model as...'</b> in the 'Output models' dropdowns.<br><br>"
            "&bull; Name them '<b>Bone_Left</b>' (for the negative side) and '<b>Bone_Right</b>' (for the positive side).<br><br>"
            "&bull; Click 'Apply' and hide the original 'Bone' model to see the result."
        )
        layout.addWidget(plane_cut_label)

        layout.addSpacing(15)

        confirm_label = qt.QLabel("<b>3.</b> If you've created the cut models you're happy with, please click 'Confirm' below.")
        confirm_label.setTextFormat(qt.Qt.RichText)
        confirm_label.setWordWrap(True)
        layout.addWidget(confirm_label)

        self.confirmCutButton = qt.QPushButton("Confirm Model Cut")
        self.confirmCutButton.clicked.connect(self.onConfirmCut)
        layout.addWidget(self.confirmCutButton, 0, qt.Qt.AlignHCenter)

        self.skipCutButton = qt.QPushButton("Skip Cutting (Volume Rendering mode)")
        self.skipCutButton.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        self.skipCutButton.clicked.connect(self.onSkipCut)
        layout.addWidget(self.skipCutButton, 0, qt.Qt.AlignHCenter)
        self.skipCutButton.setVisible(False)

        layout.addSpacing(10)

        self.step4StatusLabel = qt.QLabel("Status: Waiting for user to cut the model.")
        self.step4StatusLabel.setWordWrap(True)
        layout.addWidget(self.step4StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

        self.updateStep4UI()

    def updateStep4UI(self):
        if self.boneModel is None:
            self.cutWarningLabel.setText("⚠️ No bone model loaded. You can still proceed using Volume Rendering mode.")
            self.openDynamicModelerButton.setEnabled(False)
            self.confirmCutButton.setEnabled(False)
            self.skipCutButton.setVisible(True)
            self.step4StatusLabel.setText("Status: No model loaded. Click 'Skip Cutting' to proceed.")
        else:
            self.cutWarningLabel.setText("")
            self.openDynamicModelerButton.setEnabled(True)
            self.confirmCutButton.setEnabled(True)
            self.skipCutButton.setVisible(False)
            self.step4StatusLabel.setText("Status: Model loaded. Please cut the model using the instructions above.")

    def onSkipCut(self):
        self.step4_skipped = True
        self.step4StatusLabel.setText("Status: Cutting skipped. Proceeding to next step.")
        slicer.util.showStatusMessage("Cutting skipped", 2000)
        # Do not auto-step; user must click Next

    # ==================== STEPS 5-9 ====================
    def createStep5_VMJ_Line(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 5: Confirm VMJ Landmark and Create the ANS measurement")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # ===== INSTRUCTION IMAGE =====
        instructionGroup = qt.QGroupBox("📍 VMJ Landmark Location Guide")
        instructionLayout = qt.QVBoxLayout(instructionGroup)
        
        descLabel = qt.QLabel(
            "<b>The VMJ (Vomer-Maxillary Junction)</b> is the point where the vomer bone meets the maxilla.\n\n"
            "It is located on the midline of the hard palate, at the junction of the vomer and the maxillary bones.\n\n"
            "Use the image below as a reference for correct placement."
        )
        descLabel.setWordWrap(True)
        instructionLayout.addWidget(descLabel)
        
        imageScroll = qt.QScrollArea()
        imageScroll.setWidgetResizable(True)
        imageScroll.setMaximumHeight(400)
        imageScroll.setMinimumHeight(250)
        imageScroll.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        
        imageContainer = qt.QWidget()
        imageLayout = qt.QVBoxLayout(imageContainer)
        imageLayout.setContentsMargins(10, 10, 10, 10)
        imageLayout.setAlignment(qt.Qt.AlignCenter)
        
        self.vmjImageLabel = qt.QLabel()
        self.vmjImageLabel.setAlignment(qt.Qt.AlignCenter)
        self.vmjImageLabel.setStyleSheet("background-color: white; padding: 5px;")
        self.vmjImageLabel.setText("Loading image...")
        
        imageLayout.addWidget(self.vmjImageLabel)
        imageScroll.setWidget(imageContainer)
        instructionLayout.addWidget(imageScroll)
        
        self.loadVMJImage()
        
        layout.addWidget(instructionGroup)
        
        # ===== VMJ CONFIRMATION CONTROLS =====
        layout.addWidget(qt.QLabel("1. Manually adjust the 'VMJ' point position if needed."))
        layout.addWidget(qt.QLabel("2. Click to confirm the VMJ position."))
        self.confirmVMJButton = qt.QPushButton("✅ Confirm VMJ Position")
        self.confirmVMJButton.clicked.connect(self.onConfirmVMJ)
        self.confirmVMJButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(self.confirmVMJButton)

        layout.addWidget(qt.QLabel("3. Click to create the 'VMJ-aca' line."))
        self.measureANSButton = qt.QPushButton("📏 Create VMJ-aca Line")
        self.measureANSButton.clicked.connect(self.onMeasureANS)
        self.measureANSButton.setEnabled(False)
        self.measureANSButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(self.measureANSButton)

        self.step5StatusLabel = qt.QLabel("Status: Please manually adjust VMJ point if needed, then confirm.")
        self.step5StatusLabel.setWordWrap(True)
        self.step5StatusLabel.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.step5StatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep6_VectorAndMidphiltrum(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.addWidget(qt.QLabel("Step 6: Define ANS direction and Midphiltrum Point"))

        layout.addWidget(qt.QLabel("<b>Part A: Define the Nasal Spine Vector</b><br>Manipulate the purple vector to follow the nasal spine."))
        layout.addWidget(qt.QLabel("<b>Part B: Place the Midphiltrum (mp) Point</b>"))

        self.createMPGuideButton = qt.QPushButton("1. Create 'mp' Guide Point")
        self.createMPGuideButton.setToolTip("Creates the 'mp' point between subspinale and prosthion.")
        self.createMPGuideButton.clicked.connect(self.onCreateMPGuide)
        layout.addWidget(self.createMPGuideButton)

        self.adjustMPButton = qt.QPushButton("2. Adjust 'mp' Point")
        self.adjustMPButton.clicked.connect(self.onAdjustMP)
        self.adjustMPButton.setEnabled(False)
        layout.addWidget(self.adjustMPButton)

        self.confirmMPButton = qt.QPushButton("3. Confirm 'mp' Placement")
        self.confirmMPButton.clicked.connect(self.onConfirmMP)
        self.confirmMPButton.setEnabled(False)
        layout.addWidget(self.confirmMPButton)

        self.step6StatusLabel = qt.QLabel("Status: Align the purple vector, then create 'mp' point.")
        layout.addWidget(self.step6StatusLabel)
        self.stepStack.addWidget(widget)

    def createStep7_PronasalePrediction(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 7: Predict Pronasale")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        self.predictionWarningLabel = qt.QLabel()
        self.predictionWarningLabel.setWordWrap(True)
        self.predictionWarningLabel.setStyleSheet("color: #FF5722; font-weight: bold;")
        layout.addWidget(self.predictionWarningLabel)

        instructions = qt.QLabel()
        instructions.setTextFormat(qt.Qt.RichText)
        instructions.setOpenExternalLinks(True)
        instructions.setWordWrap(True)
        instructions.setText(
            "Set the parameters below and click the button to calculate the predicted pronasale position. "
            "The default value for the facial soft tissue thickness is based on "
            "<a href='https://link.springer.com/article/10.1007/s00414-023-03087-x'>Hona and Stephan 2024</a>."
        )
        layout.addWidget(instructions)

        formLayout = qt.QFormLayout()

        self.perpDistanceSpinBox = qt.QDoubleSpinBox()
        self.perpDistanceSpinBox.setRange(0, 100)
        self.perpDistanceSpinBox.setValue(11.5)
        self.perpDistanceSpinBox.setSuffix(" mm")
        formLayout.addRow("Perpendicular Distance from 'mp':", self.perpDistanceSpinBox)

        self.multiplierComboBox = qt.QComboBox()
        self.multiplierComboBox.addItem("3.0 × ANS (Krogman and Iscan, 1986)")
        self.multiplierComboBox.addItem("1.9 × ANS (Matsuda et al., 2023)")
        self.multiplierComboBox.currentIndex = 0
        formLayout.addRow("Multiplier Method:", self.multiplierComboBox)

        self.cylinderRadiusSpinBox = qt.QDoubleSpinBox()
        self.cylinderRadiusSpinBox.setRange(0.5, 10.0)
        self.cylinderRadiusSpinBox.setValue(3.0)
        self.cylinderRadiusSpinBox.setSuffix(" mm")
        self.cylinderRadiusSpinBox.setToolTip("Radius of the cylinder (also used as search radius for surface detection)")
        formLayout.addRow("Cylinder/Search Radius:", self.cylinderRadiusSpinBox)
        self.showCylinderCheckbox = qt.QCheckBox("Show FSTT cylinder")
        self.showCylinderCheckbox.setToolTip("Visualize the FSTT as a 3D cylinder.")
        self.showCylinderCheckbox.setChecked(True)
        formLayout.addRow(self.showCylinderCheckbox)

        layout.addLayout(formLayout)

        self.predictPronasaleButton = qt.QPushButton("Predict Pronasale")
        self.predictPronasaleButton.clicked.connect(self.onPredictPronasale)
        layout.addWidget(self.predictPronasaleButton, 0, qt.Qt.AlignHCenter)

        self.step7StatusLabel = qt.QLabel("Status: Waiting for user to set parameters.")
        self.step7StatusLabel.setWordWrap(True)
        layout.addWidget(self.step7StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

        self.updatePredictionUI()

    def updatePredictionUI(self):
        if self.boneModel is None and self.volumeNode is None:
            self.predictionWarningLabel.setText("⚠️ No bone model or volume loaded. Prediction requires either a model or a CT volume. Please load one in Step 3.")
            self.predictPronasaleButton.setEnabled(False)
        elif self.boneModel is None and self.volumeNode is not None:
            self.predictionWarningLabel.setText("ℹ️ Using CT volume for surface normal detection (no bone model).")
            self.predictPronasaleButton.setEnabled(True)
        else:
            self.predictionWarningLabel.setText("")
            self.predictPronasaleButton.setEnabled(True)

    def createStep8_Validation(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 8: Validate Prediction (Optional)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        self.downloadTrueButton = qt.QPushButton("Download/Load True Landmarks")
        self.downloadTrueButton.clicked.connect(self.onDownloadTrueLandmarks)
        layout.addWidget(self.downloadTrueButton)

        self.trueLandmarksSelector = slicer.qMRMLNodeComboBox()
        self.trueLandmarksSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.trueLandmarksSelector.setMRMLScene(slicer.mrmlScene)
        self.trueLandmarksSelector.currentNodeChanged.connect(self.onTrueLandmarkSelected)
        layout.addWidget(self.trueLandmarksSelector)

        step8Instruction = qt.QLabel("Please allocate the true pronasale point on your CT scan or segmented model before proceeding")
        step8Instruction.wordWrap = True
        layout.addWidget(step8Instruction)

        self.compareButton = qt.QPushButton("Compare True vs. Predicted")
        self.compareButton.clicked.connect(self.onComparePronasale)
        self.compareButton.setEnabled(False)
        layout.addWidget(self.compareButton)

        self.step8StatusLabel = qt.QLabel("Status: Waiting for user.")
        layout.addWidget(self.step8StatusLabel)

        self.stepStack.addWidget(widget)

    def createStep9_Results(self):
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)

        title = qt.QLabel("Step 9: Results and Validation")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        coordsLabel = qt.QLabel("📍 Landmark Coordinates")
        coordsLabel.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(coordsLabel)

        self.coordsTable = qt.QTableWidget()
        self.coordsTable.setRowCount(2)
        self.coordsTable.setColumnCount(4)
        self.coordsTable.setHorizontalHeaderLabels(["Landmark", "X", "Y", "Z"])
        self.coordsTable.horizontalHeader().setStretchLastSection(True)
        self.coordsTable.setAlternatingRowColors(True)
        self.coordsTable.setMinimumHeight(80)

        self.coordsTable.setItem(0, 0, qt.QTableWidgetItem("Predicted Pronasale"))
        self.coordsTable.setItem(1, 0, qt.QTableWidgetItem("True Pronasale"))
        for row in range(2):
            for col in range(1, 4):
                self.coordsTable.setItem(row, col, qt.QTableWidgetItem(""))

        layout.addWidget(self.coordsTable)

        measLabel = qt.QLabel("📏 Measurements")
        measLabel.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(measLabel)

        self.measTable = qt.QTableWidget()
        self.measTable.setRowCount(5)
        self.measTable.setColumnCount(2)
        self.measTable.setHorizontalHeaderLabels(["Measurement", "Value"])
        self.measTable.horizontalHeader().setStretchLastSection(True)
        self.measTable.setAlternatingRowColors(True)
        self.measTable.setMinimumHeight(120)

        row_labels = [
            "Prediction Error (mm)",
            "FSTT (mm)",
            "Cylinder/Search Radius (mm)",
            "VMJ-aca Distance (mm)",
            "Equation Used"
        ]
        for row, label in enumerate(row_labels):
            self.measTable.setItem(row, 0, qt.QTableWidgetItem(label))
            self.measTable.setItem(row, 1, qt.QTableWidgetItem(""))

        layout.addWidget(self.measTable)

        self.copyButton = qt.QPushButton("📋 Copy All Results to Clipboard")
        self.copyButton.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px;")
        self.copyButton.clicked.connect(self.onCopyToClipboard)
        layout.addWidget(self.copyButton)

        self.finishButton = qt.QPushButton("Finish")
        self.finishButton.clicked.connect(self.onFinish)
        layout.addWidget(self.finishButton)

        self.step9StatusLabel = qt.QLabel("Status: Complete! Review results above.")
        self.step9StatusLabel.setWordWrap(True)
        layout.addWidget(self.step9StatusLabel)

        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    # ==================== HELPER METHODS ====================
    def loadVMJImage(self):
        try:
            import urllib.request
            url = "https://github.com/user-attachments/assets/2f8ecbd2-8403-4125-8cc2-d04cd1534cca"
            self.vmjImageLabel.setText("Downloading image...")
            slicer.app.processEvents()
            imageData = urllib.request.urlopen(url).read()
            pixmap = qt.QPixmap()
            pixmap.loadFromData(imageData)
            if not pixmap.isNull():
                max_width = 500
                max_height = 350
                if pixmap.width() > max_width or pixmap.height() > max_height:
                    pixmap = pixmap.scaled(max_width, max_height, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
                self.vmjImageLabel.setPixmap(pixmap)
                self.vmjImageLabel.setText("")
                print("VMJ image loaded successfully")
            else:
                raise Exception("Failed to load image data - pixmap is null")
        except Exception as e:
            print(f"Error loading VMJ image: {e}")
            self.vmjImageLabel.setText(
                "📌 VMJ Landmark Location\n\n"
                "The VMJ (Vomer-Maxillary Junction) is located:\n"
                "• On the midline of the hard palate\n"
                "• At the junction of the vomer and maxillary bones\n"
                "• Posterior to the incisive foramen\n\n"
                "Please refer to the image description above."
            )
            self.vmjImageLabel.setStyleSheet("background-color: #f0f0f0; padding: 20px; font-size: 14px;")

    def onCopyToClipboard(self):
        try:
            clipboard_text = ""
            clipboard_text += "Landmark\tX\tY\tZ\n"
            for row in range(self.coordsTable.rowCount):
                landmark = self.coordsTable.item(row, 0).text() if self.coordsTable.item(row, 0) else ""
                x = self.coordsTable.item(row, 1).text() if self.coordsTable.item(row, 1) else ""
                y = self.coordsTable.item(row, 2).text() if self.coordsTable.item(row, 2) else ""
                z = self.coordsTable.item(row, 3).text() if self.coordsTable.item(row, 3) else ""
                clipboard_text += f"{landmark}\t{x}\t{y}\t{z}\n"
            clipboard_text += "\n"
            clipboard_text += "Measurement\tValue\n"
            for row in range(self.measTable.rowCount):
                label = self.measTable.item(row, 0).text() if self.measTable.item(row, 0) else ""
                value = self.measTable.item(row, 1).text() if self.measTable.item(row, 1) else ""
                clipboard_text += f"{label}\t{value}\n"
            app_clipboard = qt.QApplication.clipboard()
            app_clipboard.setText(clipboard_text)
            slicer.util.infoDisplay("All results copied to clipboard!")
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to copy to clipboard: {e}")

    def updateResultsTable(self):
        try:
            if self.predictedPronasaleNode and self.predictedPronasaleNode.GetNumberOfControlPoints() > 0:
                pred_pos = [0, 0, 0]
                self.predictedPronasaleNode.GetNthControlPointPositionWorld(0, pred_pos)
                self.coordsTable.item(0, 1).setText(f"{pred_pos[0]:.2f}")
                self.coordsTable.item(0, 2).setText(f"{pred_pos[1]:.2f}")
                self.coordsTable.item(0, 3).setText(f"{pred_pos[2]:.2f}")

            if self.trueSoftTissueNode:
                true_pos = [0, 0, 0]
                found = False
                for i in range(self.trueSoftTissueNode.GetNumberOfControlPoints()):
                    label = self.trueSoftTissueNode.GetNthControlPointLabel(i)
                    if "pronasale" in label.lower():
                        self.trueSoftTissueNode.GetNthControlPointPositionWorld(i, true_pos)
                        found = True
                        break
                if found:
                    self.coordsTable.item(1, 1).setText(f"{true_pos[0]:.2f}")
                    self.coordsTable.item(1, 2).setText(f"{true_pos[1]:.2f}")
                    self.coordsTable.item(1, 3).setText(f"{true_pos[2]:.2f}")
                else:
                    for col in range(1, 4):
                        self.coordsTable.item(1, col).setText("Not loaded")

            if self.predictedPronasaleNode and self.trueSoftTissueNode:
                pred_pos = [0, 0, 0]
                true_pos = [0, 0, 0]
                self.predictedPronasaleNode.GetNthControlPointPositionWorld(0, pred_pos)
                found = False
                for i in range(self.trueSoftTissueNode.GetNumberOfControlPoints()):
                    label = self.trueSoftTissueNode.GetNthControlPointLabel(i)
                    if "pronasale" in label.lower():
                        self.trueSoftTissueNode.GetNthControlPointPositionWorld(i, true_pos)
                        found = True
                        break
                if found:
                    error = np.linalg.norm(np.array(pred_pos) - np.array(true_pos))
                    self.measTable.item(0, 1).setText(f"{error:.2f}")
                else:
                    self.measTable.item(0, 1).setText("N/A")
            else:
                self.measTable.item(0, 1).setText("N/A")

            fstt_value = self.perpDistanceSpinBox.value if hasattr(self, 'perpDistanceSpinBox') else 0
            self.measTable.item(1, 1).setText(f"{fstt_value:.2f}")

            radius_value = self.cylinderRadiusSpinBox.value if hasattr(self, 'cylinderRadiusSpinBox') else 2.0
            self.measTable.item(2, 1).setText(f"{radius_value:.2f}")

            if self.vmjAcaLine:
                vmj_length = self.vmjAcaLine.GetLineLengthWorld()
                self.measTable.item(3, 1).setText(f"{vmj_length:.2f}")
            else:
                self.measTable.item(3, 1).setText("N/A")

            multiplier = 3.0 if self.multiplierComboBox.currentIndex == 0 else 1.9
            equation_text = f"{multiplier:.1f} × ANS (VMJ-aca)"
            if multiplier == 3.0:
                equation_text += " [Krogman and Iscan, 1986]"
            else:
                equation_text += " [Matsuda et al., 2023]"
            self.measTable.item(4, 1).setText(equation_text)

        except Exception as e:
            print(f"Error updating results tables: {e}")

    def onFinish(self):
        self.close()

    def syncWithScene(self):
        self.landmarksNode = slicer.util.getFirstNodeByName("KrogmanIscan_hard_tissue")
        if self.landmarksNode:
            self.step1StatusLabel.setText("Status: Found 'KrogmanIscan_hard_tissue'.")

        self.referencePlane = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
        if self.referencePlane:
            self.step2StatusLabel.setText(f"Status: Found '{self.referencePlane.GetName()}'.")

        self.boneModel = slicer.util.getFirstNodeByName("Bone")
        if self.boneModel:
            self.boneModelSelector.setCurrentNode(self.boneModel)

        if not self.volumeNode:
            vols = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
            for vol in vols:
                if not vol.GetName().endswith("_seg") and "label" not in vol.GetName().lower():
                    self.volumeNode = vol
                    self.volumeSelectorVR.setCurrentNode(vol)
                    break

        self.onConfirmCut(updateStatusOnly=True)

        self.vmjAcaLine = slicer.util.getFirstNodeByName("VMJ-aca")
        if self.vmjAcaLine:
            self.confirmVMJButton.setEnabled(False)
            self.measureANSButton.setEnabled(False)
            self.step5_complete = True
            self.step5StatusLabel.setText("Status: Found 'VMJ-aca' line. Step complete.")
        elif self.landmarksNode and self.findPointIndex("vmj") != -1:
            self.confirmVMJButton.setEnabled(True)
            self.measureANSButton.setEnabled(False)
            self.step5StatusLabel.setText("Status: Found VMJ point. Please confirm position.")

        self.nasalSpineVector = slicer.util.getFirstNodeByName("nasal spine vector")

        if self.landmarksNode and self.findPointIndex("mp") != -1:
            self._mp_index = self.findPointIndex("mp")
            self.createMPGuideButton.setEnabled(False)
            self.adjustMPButton.setEnabled(True)
            self.confirmMPButton.setEnabled(True)
            self.step6StatusLabel.setText("Status: Found existing 'mp' point. Please adjust and/or confirm.")

        self.predictedPronasaleNode = slicer.util.getFirstNodeByName("predicted pronasale")
        self.trueSoftTissueNode = slicer.util.getFirstNodeByName("KrogmanIscan_soft_tissue")
        if self.trueSoftTissueNode:
            self.trueLandmarksSelector.setCurrentNode(self.trueSoftTissueNode)

        self.updateStep4UI()
        self.updatePredictionUI()

    def findPointIndex(self, name):
        if not self.landmarksNode:
            return -1
        for i in range(self.landmarksNode.GetNumberOfControlPoints()):
            label = self.landmarksNode.GetNthControlPointLabel(i)
            if name.lower() in label.lower():
                return i
        return -1

    def getPos(self, name, node=None):
        landmark_node = node if node is not None else self.landmarksNode
        if not landmark_node:
            raise ValueError("Landmarks node not found.")
        for i in range(landmark_node.GetNumberOfControlPoints()):
            if name.lower() in landmark_node.GetNthControlPointLabel(i).lower():
                pos = np.zeros(3)
                landmark_node.GetNthControlPointPositionWorld(i, pos)
                return pos
        raise ValueError(f"Landmark '{name}' not found in the specified node!")

    def onLoadLocalLandmarks(self, fileName=None, nodeName=None):
        if not fileName:
            fileName, _ = qt.QFileDialog.getOpenFileName(self, "Load Landmarks", "", "Markup JSON Files (*.mrk.json)")
        if fileName:
            loadedNode = slicer.util.loadMarkups(fileName)
            if loadedNode:
                finalName = nodeName if nodeName else "KrogmanIscan_hard_tissue"
                loadedNode.SetName(finalName)
                if finalName == "KrogmanIscan_hard_tissue":
                    self.landmarksNode = loadedNode
                    self.step1StatusLabel.setText("Status: Successfully loaded 'KrogmanIscan_hard_tissue'.")
                elif finalName == "KrogmanIscan_soft_tissue":
                    self.trueSoftTissueNode = loadedNode
                    self.trueLandmarksSelector.setCurrentNode(loadedNode)
                    self.step8StatusLabel.setText("Status: Successfully loaded 'KrogmanIscan_soft_tissue'.")
                slicer.util.showStatusMessage(f"'{finalName}' loaded!", 3000)
                self.updateStepUI()
            else:
                slicer.util.errorDisplay(f"Failed to load landmarks from {fileName}.")

    def onDownloadHardLandmarks(self):
        self.onDownloadAndLoad(
            "https://github.com/user-attachments/files/20212533/KrogmanIscan_hard_tissue.mrk.json",
            "KrogmanIscan_hard_tissue",
            self.step1StatusLabel
        )

    def onDownloadSoftLandmarks(self):
        self.onDownloadAndLoad(
            "https://github.com/user-attachments/files/20234679/KrogmanIscan_soft_tissue.mrk.json",
            "KrogmanIscan_soft_tissue",
            self.step1StatusLabel
        )

    def onDownloadAndLoad(self, url, nodeName, statusLabel):
        statusLabel.setText("Status: Downloading...")
        slicer.app.processEvents()
        try:
            with urllib.request.urlopen(url) as response:
                fileData = response.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json', mode='wb') as tempFile:
                tempFile.write(fileData)
                tempFilePath = tempFile.name
            self.onLoadLocalLandmarks(tempFilePath, nodeName)
        except Exception as e:
            statusLabel.setText(f"Status: Error! Could not download. Error: {e}")
            slicer.util.errorDisplay(f"Failed to download from the web. Error: {e}")
        finally:
            if 'tempFilePath' in locals() and os.path.exists(tempFilePath):
                os.remove(tempFilePath)

    def onDownloadTrueLandmarks(self):
        self.onDownloadAndLoad(
            "https://github.com/user-attachments/files/20234679/KrogmanIscan_soft_tissue.mrk.json",
            "KrogmanIscan_soft_tissue",
            self.step8StatusLabel
        )

    def onCreatePlane(self):
        if not self.landmarksNode:
            self.syncWithScene()
        if not self.landmarksNode:
            self.step2StatusLabel.setText("Status: Error! Please go back and load the landmarks first.")
            return
        choice_index = self.planeChoiceComboBox.currentIndex
        if choice_index == 0:
            self.step2StatusLabel.setText("Status: Error! Please select a plane creation method.")
            return
        self.step2StatusLabel.setText("Status: Creating plane...")
        slicer.app.processEvents()
        try:
            plane_name = ""
            if choice_index == 1:
                plane_name = "INB"
                p_inion, p_nasion, p_bregma = self.getPos("inion"), self.getPos("nasion"), self.getPos("bregma")
                v1, v2 = p_nasion - p_inion, p_bregma - p_inion
                normal, origin = np.cross(v1, v2), p_inion
                
            elif choice_index == 2:
                plane_name = "MSP"
                required = ["nasion", "acanthion", "prosthion", "subspinale"]
                points = np.array([self.getPos(name) for name in required])
                centroid = np.mean(points, axis=0)
                centered = points - centroid
                U, S, Vt = np.linalg.svd(centered)
                principal_direction = Vt[0, :]
                if principal_direction[1] < 0:
                    principal_direction = -principal_direction
                superior = np.array([0, 0, 1])
                normal = np.cross(principal_direction, superior)
                if np.linalg.norm(normal) < 0.001:
                    normal = np.cross(Vt[0, :], Vt[1, :])
                normal = normal / np.linalg.norm(normal)
                if normal[0] < 0:
                    normal = -normal
                if abs(normal[0]) < 0.5:
                    y_dir = np.array([0, 1, 0])
                    normal = np.cross(principal_direction, y_dir)
                    normal = normal / np.linalg.norm(normal)
                    if normal[0] < 0:
                        normal = -normal
                if abs(normal[0]) < 0.5:
                    normal = np.array([1.0, 0.0, 0.0])
                origin = centroid
                
            try:
                oldPlane = slicer.util.getNode(plane_name)
                slicer.mrmlScene.RemoveNode(oldPlane)
            except:
                pass
            
            planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', plane_name)
            planeNode.SetOrigin(origin)
            planeNode.SetNormal(normal)
            planeNode.SetSize(300, 300)
            planeNode.GetDisplayNode().SetOpacity(0.5)
            
            self.referencePlane = planeNode
            self.step2StatusLabel.setText(f"Status: Successfully created '{plane_name}' plane. You can now proceed.")
            slicer.util.showStatusMessage(f"'{plane_name}' created!", 3000)
            
            self.updateStepUI()
            
        except Exception as e:
            self.step2StatusLabel.setText(f"Status: Error! Could not create plane. Error: {e}")
            slicer.util.errorDisplay(f"Failed to create plane: {e}")

    def onConfirmSegmentation(self, node):
        if node:
            self.boneModel = node
            self.step3StatusLabel.setText(f"Status: Confirmed '{self.boneModel.GetName()}' as the bone model. Ready to proceed!")
            slicer.util.showStatusMessage("Bone model confirmed!", 3000)
            self.manualVolumeRendering = False
            self.updateStep4UI()
            self.updatePredictionUI()
            self.updateStepUI()
        else:
            self.boneModel = None
            self.step3StatusLabel.setText("Status: Waiting for user to select the re-imported 'Bone' model.")

    def onOpenDynamicModeler(self):
        if not self.boneModel:
            slicer.util.warningDisplay("Please load a bone model before using Dynamic Modeler.")
            return
        if self.isDynamicModelerInstalled:
            slicer.util.selectModule('DynamicModeler')
            dynamicModelerWidget = slicer.modules.dynamicmodeler.widgetRepresentation()
            if dynamicModelerWidget:
                modelSelectors = dynamicModelerWidget.findChildren(slicer.qMRMLNodeComboBox)
                for selector in modelSelectors:
                    if "vtkMRMLModelNode" in selector.nodeTypes:
                        selector.setCurrentNode(self.boneModel)
                        return
        else:
            qt.QMessageBox.warning(self, "Extension Not Found", "The 'Dynamic Modeler' extension is not installed.")

    def onConfirmCut(self, updateStatusOnly=False):
        if not updateStatusOnly:
            self.step4StatusLabel.setText("Status: Checking for cut models...")
        left_model_found, right_model_found = None, None
        all_models = slicer.util.getNodesByClass('vtkMRMLModelNode')
        for model in all_models:
            model_name = model.GetName().lower()
            if "bone" in model_name and "left" in model_name:
                left_model_found = model
            if "bone" in model_name and "right" in model_name:
                right_model_found = model

        if left_model_found and right_model_found:
            self.boneLeftModel = left_model_found
            self.boneRightModel = right_model_found
            self.step4StatusLabel.setText(f"Status: Found '{left_model_found.GetName()}' and '{right_model_found.GetName()}'!")
            if not updateStatusOnly:
                slicer.util.showStatusMessage("Model cut confirmed!", 3000)
            self.updateStepUI()
        elif not updateStatusOnly:
            self.step4StatusLabel.setText("Status: Error! Could not find models with 'bone' and 'left'/'right' in their names.")
            slicer.util.errorDisplay("Could not find the left and right bone models.")

    def onConfirmVMJ(self):
        try:
            if not self.landmarksNode:
                self.syncWithScene()
            if not self.landmarksNode:
                raise ValueError("Landmarks node not found.")
            vmj_index = self.findPointIndex("vmj")
            if vmj_index == -1:
                raise ValueError("VMJ point not found. Please ensure it exists in the landmarks.")
            self.step5StatusLabel.setText("Status: VMJ position confirmed. You can now create the line.")
            self.confirmVMJButton.setEnabled(False)
            self.measureANSButton.setEnabled(True)
        except Exception as e:
            self.step5StatusLabel.setText(f"Status: Error! {e}")
            slicer.util.errorDisplay(f"Failed to confirm VMJ: {e}")

    def onMeasureANS(self):
        self.step5StatusLabel.setText("Status: Searching for VMJ and acanthion landmarks...")
        try:
            if not self.landmarksNode:
                self.syncWithScene()
            if not self.landmarksNode:
                raise ValueError("Landmarks node 'KrogmanIscan_hard_tissue' not found.")
            acanthion_pos = self.getPos("acanthion")
            vmj_pos = self.getPos("vmj")
            self.step5StatusLabel.setText("Status: Landmarks found. Creating line...")
            try:
                oldLine = slicer.util.getNode('VMJ-aca')
                slicer.mrmlScene.RemoveNode(oldLine)
            except:
                pass
            lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'VMJ-aca')
            lineNode.AddControlPoint(vmj_pos)
            lineNode.AddControlPoint(acanthion_pos)
            lineNode.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)
            lineNode.GetDisplayNode().SetLineThickness(0.5)
            self.vmjAcaLine = lineNode
            self.step5StatusLabel.setText("Status: 'VMJ-aca' line created successfully! You can now proceed to the next step.")
            self.measureANSButton.setEnabled(False)
            self.updateStepUI()
        except Exception as e:
            self.step5StatusLabel.setText(f"Status: Error! Could not create VMJ-aca line. {e}")
            slicer.util.errorDisplay(f"Failed to create line: {e}")

    def createNasalSpineVector(self):
        self.step6StatusLabel.setText("Status: Creating nasal spine vector...")
        try:
            if not self.referencePlane:
                raise ValueError("Reference plane not found.")
            if not self.landmarksNode:
                raise ValueError("Landmarks node not found.")
            aca_pos = self.getPos("acanthion")
            plane_origin = np.array(self.referencePlane.GetOrigin())
            plane_normal = np.array(self.referencePlane.GetNormal())
            arbitrary_vec = np.array([0, 1, 0])
            direction_on_plane = arbitrary_vec - np.dot(arbitrary_vec, plane_normal) * plane_normal
            direction_on_plane /= np.linalg.norm(direction_on_plane)
            p1 = aca_pos + 30 * direction_on_plane
            p2 = aca_pos - 30 * direction_on_plane
            try:
                oldVector = slicer.util.getNode('nasal spine vector')
                slicer.mrmlScene.RemoveNode(oldVector)
            except:
                pass
            self.nasalSpineVector = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'nasal spine vector')
            self.nasalSpineVector.AddControlPoint(p1)
            self.nasalSpineVector.AddControlPoint(p2)
            displayNode = self.nasalSpineVector.GetDisplayNode()
            displayNode.SetSelectedColor(0.8, 0.4, 0.8)
            displayNode.SetLineThickness(0.5)
            if self.vectorObserver:
                self.nasalSpineVector.RemoveObserver(self.vectorObserver)
            self.vectorObserver = self.nasalSpineVector.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.onNasalSpineVectorModified)
            self.step6StatusLabel.setText("Status: Please align the purple vector.")
        except Exception as e:
            self.step6StatusLabel.setText(f"Status: Error creating vector! {e}")
            slicer.util.errorDisplay(f"Failed to create nasal spine vector: {e}")

    def onNasalSpineVectorModified(self, caller, event):
        if self._isUpdatingVector:
            return
        self._isUpdatingVector = True
        try:
            lineNode = caller
            if not lineNode or lineNode.GetNumberOfControlPoints() != 2:
                self._isUpdatingVector = False
                return
            plane_origin = np.array(self.referencePlane.GetOrigin())
            plane_normal = np.array(self.referencePlane.GetNormal())
            aca_pos = self.getPos("acanthion")
            lastModified = lineNode.GetDisplayNode().GetActiveControlPoint()
            p_moved = np.zeros(3)
            lineNode.GetNthControlPointPositionWorld(lastModified, p_moved)
            p_moved_on_plane = p_moved - (np.dot(p_moved - plane_origin, plane_normal) * plane_normal)
            new_dir = p_moved_on_plane - aca_pos
            if np.linalg.norm(new_dir) < 1e-6:
                self._isUpdatingVector = False
                return
            new_dir /= np.linalg.norm(new_dir)
            p1 = np.zeros(3)
            lineNode.GetNthControlPointPositionWorld(0, p1)
            p2 = np.zeros(3)
            lineNode.GetNthControlPointPositionWorld(1, p2)
            dist = np.linalg.norm(p1 - p2) / 2.0
            new_p1 = aca_pos + dist * new_dir
            new_p2 = aca_pos - dist * new_dir
            lineNode.SetNthControlPointPositionWorld(0, new_p1)
            lineNode.SetNthControlPointPositionWorld(1, new_p2)
        finally:
            self._isUpdatingVector = False

    def createMidphiltrumGuide(self):
        try:
            sub_pos, pro_pos = self.getPos("subspinale"), self.getPos("prosthion")
            self.subProLine = slicer.util.getFirstNodeByName('subspinale-prosthion') or slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'subspinale-prosthion')
            self.subProLine.RemoveAllControlPoints()
            self.subProLine.AddControlPoint(sub_pos)
            self.subProLine.AddControlPoint(pro_pos)
            self.subProLine.GetDisplayNode().SetVisibility(True)
            mid_pos = (sub_pos + pro_pos) / 2.0
            self._mp_index = self.findPointIndex("mp")
            if self._mp_index != -1:
                self.landmarksNode.SetNthControlPointPositionWorld(self._mp_index, mid_pos)
            else:
                self._mp_index = self.landmarksNode.AddControlPoint(mid_pos, "mp")
            self._initialMPPos = mid_pos.copy()
            self.updateStepUI()
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to create 'mp' guide: {e}")

    def onCreateMPGuide(self):
        self.createMidphiltrumGuide()
        self.adjustMPButton.setEnabled(True)
        self.createMPGuideButton.setEnabled(False)
        self.step6StatusLabel.setText("Status: 'mp' point created. You may now adjust it.")

    def onAdjustMP(self):
        try:
            self._mp_index = self.findPointIndex("mp")
            if self._mp_index == -1:
                self.createMidphiltrumGuide()
                self._mp_index = self.findPointIndex("mp")
                if self._mp_index == -1:
                    raise ValueError("Failed to create 'mp' point.")
            self._initialMPPos = np.zeros(3)
            self.landmarksNode.GetNthControlPointPositionWorld(self._mp_index, self._initialMPPos)
            slicer.modules.markups.logic().JumpSlicesToNthPointInMarkup(self.landmarksNode.GetID(), self._mp_index)
            if self.mpObserver and self.landmarksNode:
                self.landmarksNode.RemoveObserver(self.mpObserver)
                self.mpObserver = None
            self.mpObserver = self.landmarksNode.AddObserver(
                slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.onMPModified
            )
            self.confirmMPButton.setEnabled(True)
            self.adjustMPButton.setEnabled(False)
            self.step6StatusLabel.setText("Status: Ready to adjust 'mp' point. Click and drag the point in the 3D view (movement is constrained to Y-axis).")
        except Exception as e:
            slicer.util.warningDisplay(f"Cannot start adjustment: {e}")

    def onMPModified(self, caller, event):
        if self._isUpdatingMP or self._mp_index == -1:
            return
        self._isUpdatingMP = True
        try:
            current_pos = np.zeros(3)
            self.landmarksNode.GetNthControlPointPositionWorld(self._mp_index, current_pos)
            constrained_pos = [self._initialMPPos[0], current_pos[1], self._initialMPPos[2]]
            if not np.allclose(current_pos, constrained_pos, atol=0.01):
                self.landmarksNode.SetNthControlPointPositionWorld(self._mp_index, constrained_pos)
        except Exception:
            pass
        finally:
            self._isUpdatingMP = False

    def onConfirmMP(self):
        self.step6StatusLabel.setText("Status: 'mp' point placement confirmed. Step complete!")
        if self.mpObserver and self.landmarksNode:
            self.landmarksNode.RemoveObserver(self.mpObserver)
            self.mpObserver = None
        self._isUpdatingMP = False
        self.confirmMPButton.setEnabled(False)
        self.step6_complete = True
        self.updateStepUI()

    # ==================== PATCH-BASED SURFACE NORMAL FROM CT ====================
    def computeSurfaceNormalFromVolumePatch(self, landmarkPos, searchRadius=3.0, boneThreshold=200):
        if self.volumeNode is None:
            return None, None

        imageData = self.volumeNode.GetImageData()
        spacing = self.volumeNode.GetSpacing()
        dims = imageData.GetDimensions()

        worldToIJK = vtk.vtkMatrix4x4()
        self.volumeNode.GetRASToIJKMatrix(worldToIJK)
        ijkToWorld = vtk.vtkMatrix4x4()
        self.volumeNode.GetIJKToRASMatrix(ijkToWorld)

        if self.referencePlane is not None:
            plane_normal = np.zeros(3)
            self.referencePlane.GetNormalWorld(plane_normal)
            plane_normal = np.array(plane_normal)
            superior = np.array([0, 0, 1])
            anterior = np.cross(plane_normal, superior)
            if np.linalg.norm(anterior) < 0.001:
                anterior = np.array([0, 1, 0])
            anterior = anterior / np.linalg.norm(anterior)
            if np.dot(anterior, np.array([0, 1, 0])) < 0:
                anterior = -anterior
        else:
            anterior = np.array([0, 1, 0])
        
        print(f"DEBUG: Anterior direction: {anterior}")

        landmarkIJK = [0, 0, 0, 1]
        worldToIJK.MultiplyPoint([landmarkPos[0], landmarkPos[1], landmarkPos[2], 1], landmarkIJK)
        i0, j0, k0 = int(round(landmarkIJK[0])), int(round(landmarkIJK[1])), int(round(landmarkIJK[2]))
        
        val_at_mp = imageData.GetScalarComponentAsDouble(i0, j0, k0, 0)
        print(f"DEBUG: HU value at mp: {val_at_mp}")

        if val_at_mp < boneThreshold:
            print("DEBUG: mp is not in bone. Searching for bone surface...")
            found_bone = False
            for radius in range(1, 20):
                for di in range(-radius, radius + 1):
                    for dj in range(-radius, radius + 1):
                        for dk in range(-radius, radius + 1):
                            if (di*di + dj*dj + dk*dk) > radius * radius:
                                continue
                            i = i0 + di
                            j = j0 + dj
                            k = k0 + dk
                            if (i < 0 or i >= dims[0] or j < 0 or j >= dims[1] or k < 0 or k >= dims[2]):
                                continue
                            val = imageData.GetScalarComponentAsDouble(i, j, k, 0)
                            if val >= boneThreshold:
                                i0, j0, k0 = i, j, k
                                found_bone = True
                                print(f"DEBUG: Found bone at IJK: ({i0}, {j0}, {k0}) with HU: {val}")
                                break
                        if found_bone:
                            break
                    if found_bone:
                        break
                if found_bone:
                    break

        radiusIJK = max(2, int(searchRadius / max(spacing)))
        print(f"DEBUG: radiusIJK: {radiusIJK}")
        
        surfacePoints = []
        totalVoxels = 0
        
        for di in range(-radiusIJK, radiusIJK + 1):
            for dj in range(-radiusIJK, radiusIJK + 1):
                for dk in range(-radiusIJK, radiusIJK + 1):
                    if (di*di + dj*dj + dk*dk) > radiusIJK * radiusIJK:
                        continue
                    i = i0 + di
                    j = j0 + dj
                    k = k0 + dk
                    totalVoxels += 1
                    if (i < 0 or i >= dims[0] or j < 0 or j >= dims[1] or k < 0 or k >= dims[2]):
                        continue
                    val = imageData.GetScalarComponentAsDouble(i, j, k, 0)
                    if val >= boneThreshold:
                        rasPos = [0, 0, 0, 1]
                        ijkToWorld.MultiplyPoint([i, j, k, 1], rasPos)
                        surfacePoints.append(np.array(rasPos[:3]))

        print(f"DEBUG: Found {len(surfacePoints)} bone voxels out of {totalVoxels} sampled")

        if len(surfacePoints) < 4:
            print("DEBUG: Not enough surface points. Trying with lower threshold...")
            surfacePoints = []
            for di in range(-radiusIJK, radiusIJK + 1):
                for dj in range(-radiusIJK, radiusIJK + 1):
                    for dk in range(-radiusIJK, radiusIJK + 1):
                        if (di*di + dj*dj + dk*dk) > radiusIJK * radiusIJK:
                            continue
                        i = i0 + di
                        j = j0 + dj
                        k = k0 + dk
                        if (i < 0 or i >= dims[0] or j < 0 or j >= dims[1] or k < 0 or k >= dims[2]):
                            continue
                        val = imageData.GetScalarComponentAsDouble(i, j, k, 0)
                        if val >= 150:
                            rasPos = [0, 0, 0, 1]
                            ijkToWorld.MultiplyPoint([i, j, k, 1], rasPos)
                            surfacePoints.append(np.array(rasPos[:3]))
            print(f"DEBUG: Found {len(surfacePoints)} bone voxels with lower threshold")

        if len(surfacePoints) < 4:
            print("DEBUG: Still not enough surface points. Using gradient fallback.")
            return None, None

        points = np.array(surfacePoints)
        baseCenter = np.mean(points, axis=0)
        
        normal = anterior.copy()
        
        centered = points - baseCenter
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        pca_normal = eigenvectors[:, np.argmin(eigenvalues)]
        if np.dot(pca_normal, anterior) < 0:
            pca_normal = -pca_normal
        
        combined_normal = 0.7 * anterior + 0.3 * pca_normal
        combined_normal = combined_normal / np.linalg.norm(combined_normal)
        
        if combined_normal[1] < 0:
            combined_normal = -combined_normal
        
        print(f"DEBUG: PCA normal: {pca_normal}")
        print(f"DEBUG: Anterior direction: {anterior}")
        print(f"DEBUG: Combined normal: {combined_normal}")
        print(f"DEBUG: baseCenter: {baseCenter}")

        return combined_normal, baseCenter

    def computeGradientNormal(self, landmarkPos, sampleRadius=3.0):
        if self.volumeNode is None:
            return None
        
        if self.referencePlane is not None:
            plane_normal = np.zeros(3)
            self.referencePlane.GetNormalWorld(plane_normal)
            plane_normal = np.array(plane_normal)
            superior = np.array([0, 0, 1])
            anterior = np.cross(plane_normal, superior)
            if np.linalg.norm(anterior) < 0.001:
                anterior = np.array([0, 1, 0])
            anterior = anterior / np.linalg.norm(anterior)
            if np.dot(anterior, np.array([0, 1, 0])) < 0:
                anterior = -anterior
        else:
            anterior = np.array([0, 1, 0])
        
        imageData = self.volumeNode.GetImageData()
        spacing = self.volumeNode.GetSpacing()
        worldToIJK = vtk.vtkMatrix4x4()
        self.volumeNode.GetRASToIJKMatrix(worldToIJK)

        ijk = [0,0,0,1]
        worldToIJK.MultiplyPoint(np.append(landmarkPos, 1), ijk)
        i, j, k = int(round(ijk[0])), int(round(ijk[1])), int(round(ijk[2]))
        dims = imageData.GetDimensions()
        margin = 5
        if (i < margin or i >= dims[0]-margin or
            j < margin or j >= dims[1]-margin or
            k < margin or k >= dims[2]-margin):
            return None

        grad = np.zeros(3)
        sampleDist = max(2, int(sampleRadius / max(spacing)))
        for axis in range(3):
            offset = [0,0,0]; offset[axis] = sampleDist
            i_plus = i+offset[0]; j_plus = j+offset[1]; k_plus = k+offset[2]
            i_minus = i-offset[0]; j_minus = j-offset[1]; k_minus = k-offset[2]
            i_plus = max(0, min(dims[0]-1, i_plus))
            j_plus = max(0, min(dims[1]-1, j_plus))
            k_plus = max(0, min(dims[2]-1, k_plus))
            i_minus = max(0, min(dims[0]-1, i_minus))
            j_minus = max(0, min(dims[1]-1, j_minus))
            k_minus = max(0, min(dims[2]-1, k_minus))
            val_plus = imageData.GetScalarComponentAsDouble(i_plus, j_plus, k_plus, 0)
            val_minus = imageData.GetScalarComponentAsDouble(i_minus, j_minus, k_minus, 0)
            grad[axis] = (val_plus - val_minus) / (2 * sampleDist * spacing[axis])
        mag = np.linalg.norm(grad)
        if mag < 0.001:
            return None
        normal = -grad / mag
        
        if normal[1] < 0:
            normal = -normal
        if np.dot(normal, anterior) < 0:
            normal = -normal
        if abs(normal[2]) > 0.7:
            normal = 0.5 * normal + 0.5 * anterior
            normal = normal / np.linalg.norm(normal)
        
        return normal

    # ==================== PREDICTION METHOD ====================
    def onPredictPronasale(self):
        try:
            self.step7StatusLabel.setText("Status: Starting prediction...")

            if self.volumeNode is None and self.boneModel is None:
                raise ValueError("No volume or bone model available. Please load one in Step 3.")

            if not all([self.landmarksNode, self.vmjAcaLine, self.nasalSpineVector]):
                raise ValueError("A required node from a previous step is missing.")

            cylinderRadius = self.cylinderRadiusSpinBox.value

            mp_pos = self.getPos("mp")
            baseCenter = None
            normal = None

            if self.volumeNode is not None:
                normal, baseCenter = self.computeSurfaceNormalFromVolumePatch(
                    mp_pos, searchRadius=cylinderRadius, boneThreshold=200
                )
                
            if baseCenter is None or normal is None:
                print("DEBUG: Surface detection failed, using gradient method")
                normal = self.computeGradientNormal(mp_pos)
                if normal is None:
                    raise ValueError("Could not compute normal from CT volume.")
                baseCenter = mp_pos
            
            if normal[1] < 0:
                normal = -normal
            
            if self.referencePlane is not None:
                plane_normal = np.zeros(3)
                self.referencePlane.GetNormalWorld(plane_normal)
                plane_normal = np.array(plane_normal)
                superior = np.array([0, 0, 1])
                anterior = np.cross(plane_normal, superior)
                if np.linalg.norm(anterior) < 0.001:
                    anterior = np.array([0, 1, 0])
                anterior = anterior / np.linalg.norm(anterior)
                if np.dot(anterior, np.array([0, 1, 0])) < 0:
                    anterior = -anterior
                if np.dot(normal, anterior) < 0:
                    normal = -normal
            
            if self.landmarksNode is not None:
                idx = self.findPointIndex("mp")
                if idx != -1:
                    self.landmarksNode.SetNthControlPointPositionWorld(idx, baseCenter)

            if self.volumeNode is None and self.boneModel is not None:
                polyData = self.boneModel.GetPolyData()
                locator = vtk.vtkPointLocator()
                locator.SetDataSet(polyData)
                locator.BuildLocator()
                closestId = locator.FindClosestPoint(mp_pos)
                baseCenter = np.array(polyData.GetPoint(closestId))
                idx = self.findPointIndex("mp")
                if idx != -1:
                    self.landmarksNode.SetNthControlPointPositionWorld(idx, baseCenter)
                normals_filter = vtk.vtkPolyDataNormals()
                normals_filter.SetInputData(polyData)
                normals_filter.ComputePointNormalsOn()
                normals_filter.Update()
                normal = np.array(normals_filter.GetOutput().GetPointData().GetNormals().GetTuple(closestId))
                if self.referencePlane is not None:
                    plane_normal = np.zeros(3)
                    self.referencePlane.GetNormalWorld(plane_normal)
                    plane_normal = np.array(plane_normal)
                    superior = np.array([0,0,1])
                    anterior = np.cross(plane_normal, superior)
                    if np.linalg.norm(anterior) < 0.001:
                        anterior = np.array([0,1,0])
                    anterior = anterior / np.linalg.norm(anterior)
                    if np.dot(anterior, np.array([0,1,0])) < 0:
                        anterior = -anterior
                    if np.dot(normal, anterior) < 0:
                        normal = -normal

            perp_distance = self.perpDistanceSpinBox.value
            end_point_perp = baseCenter + normal * perp_distance

            print(f"DEBUG: Final normal for cylinder: {normal}")
            print(f"DEBUG: baseCenter: {baseCenter}")
            print(f"DEBUG: end_point_perp: {end_point_perp}")

            fstt_line = slicer.util.getFirstNodeByName("FSTT mp")
            if not fstt_line:
                fstt_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "FSTT mp")
            fstt_line.RemoveAllControlPoints()
            fstt_line.AddControlPoint(baseCenter)
            fstt_line.AddControlPoint(end_point_perp)
            fstt_line.GetDisplayNode().SetSelectedColor(0, 1, 0)
            fstt_line.GetDisplayNode().SetLineThickness(0.3)

            cylinder_model = slicer.util.getFirstNodeByName("FSTT mp cylinder")
            if self.showCylinderCheckbox.checked:
                if not cylinder_model:
                    cylinder_model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "FSTT mp cylinder")
                if not cylinder_model.GetDisplayNode():
                    cylinder_model.CreateDefaultDisplayNodes()
                display_node = cylinder_model.GetDisplayNode()
                display_node.SetVisibility(True)

                cylinder = vtk.vtkCylinderSource()
                cylinder.SetRadius(cylinderRadius)
                cylinder.SetHeight(perp_distance)
                cylinder.SetResolution(30)
                cylinder.CappingOn()
                cylinder.Update()

                direction = end_point_perp - baseCenter
                vtk.vtkMath.Normalize(direction)
                
                cylinderCenter = baseCenter + 0.5 * perp_distance * direction

                transform = vtk.vtkTransform()
                initial_axis = np.array([0, 1, 0])
                rotation_axis = np.cross(initial_axis, direction)
                rot_axis_mag = np.linalg.norm(rotation_axis)
                
                if rot_axis_mag > 0.001:
                    rotation_axis = rotation_axis / rot_axis_mag
                    angle_rad = np.arccos(np.clip(np.dot(initial_axis, direction), -1.0, 1.0))
                    transform.Translate(cylinderCenter)
                    transform.RotateWXYZ(np.rad2deg(angle_rad), rotation_axis)
                else:
                    transform.Translate(cylinderCenter)
                    if direction[1] < 0:
                        transform.RotateWXYZ(180, 1, 0, 0)

                transform_polydata = vtk.vtkTransformPolyDataFilter()
                transform_polydata.SetTransform(transform)
                transform_polydata.SetInputConnection(cylinder.GetOutputPort())
                transform_polydata.Update()

                cylinder_model.SetAndObservePolyData(transform_polydata.GetOutput())
                
                if display_node:
                    display_node.SetColor(1, 1, 0)
                    display_node.SetOpacity(0.7)
                    
            elif cylinder_model:
                display_node = cylinder_model.GetDisplayNode()
                if display_node:
                    display_node.SetVisibility(False)

            spine_start = np.zeros(3)
            spine_end = np.zeros(3)
            self.nasalSpineVector.GetNthControlPointPositionWorld(0, spine_start)
            self.nasalSpineVector.GetNthControlPointPositionWorld(1, spine_end)
            spine_dir = spine_end - spine_start
            spine_dir = spine_dir / np.linalg.norm(spine_dir)
            if spine_dir[1] < 0:
                spine_dir = -spine_dir

            multiplier = 3.0 if self.multiplierComboBox.currentIndex == 0 else 1.9
            pronasale_pos = end_point_perp + spine_dir * (self.vmjAcaLine.GetLineLengthWorld() * multiplier)

            final_line = slicer.util.getFirstNodeByName("pronasale_vector")
            if not final_line:
                final_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "pronasale_vector")
            final_line.RemoveAllControlPoints()
            final_line.AddControlPoint(end_point_perp)
            final_line.AddControlPoint(pronasale_pos)
            final_line.GetDisplayNode().SetSelectedColor(0, 0, 1)
            final_line.GetDisplayNode().SetLineThickness(0.3)

            self.predictedPronasaleNode = slicer.util.getFirstNodeByName("predicted pronasale")
            if not self.predictedPronasaleNode:
                self.predictedPronasaleNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "predicted pronasale")
            self.predictedPronasaleNode.RemoveAllControlPoints()
            self.predictedPronasaleNode.AddControlPoint(pronasale_pos, "pronasale")
            self.predictedPronasaleNode.GetDisplayNode().SetSelectedColor(1, 0, 0)
            self.predictedPronasaleNode.GetDisplayNode().SetGlyphScale(3.0)

            self.step7StatusLabel.setText("Status: Prediction complete!")

            if self.trueSoftTissueNode:
                self.compareButton.setEnabled(True)
                self.updateResultsTable()
            
            self.updateStepUI()

        except Exception as e:
            self.step7StatusLabel.setText(f"Status: Error! {e}")
            slicer.util.errorDisplay(f"Prediction failed: {e}")

    def onTrueLandmarkSelected(self, node):
        self.trueSoftTissueNode = node
        if self.predictedPronasaleNode and self.trueSoftTissueNode:
            self.compareButton.setEnabled(True)
            self.step8StatusLabel.setText("Status: Ready to compare.")
        else:
            self.compareButton.setEnabled(False)
        self.updateStepUI()

    def onComparePronasale(self):
        try:
            self.step8StatusLabel.setText("Status: Comparing...")
            if not hasattr(self, 'predictedPronasaleNode') or not self.predictedPronasaleNode:
                raise ValueError("Predicted pronasale not found. Please complete Step 7.")
            if not hasattr(self, 'trueSoftTissueNode') or not self.trueSoftTissueNode:
                raise ValueError("True soft tissue landmarks not loaded or selected.")

            predicted_pos = None
            true_pos = None

            for i in range(self.predictedPronasaleNode.GetNumberOfControlPoints()):
                if "pronasale" in self.predictedPronasaleNode.GetNthControlPointLabel(i).lower():
                    predicted_pos = np.zeros(3)
                    self.predictedPronasaleNode.GetNthControlPointPositionWorld(i, predicted_pos)
                    break

            for i in range(self.trueSoftTissueNode.GetNumberOfControlPoints()):
                if "pronasale" in self.trueSoftTissueNode.GetNthControlPointLabel(i).lower():
                    true_pos = np.zeros(3)
                    self.trueSoftTissueNode.GetNthControlPointPositionWorld(i, true_pos)
                    break

            if predicted_pos is None:
                raise ValueError("Could not find 'pronasale' in predicted landmarks")
            if true_pos is None:
                raise ValueError("Could not find 'pronasale' in true landmarks")

            error_line = slicer.util.getFirstNodeByName("prediction_error") or slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "prediction_error")
            if not error_line.GetDisplayNode():
                error_line.CreateDefaultDisplayNodes()
            error_line.RemoveAllControlPoints()
            error_line.AddControlPoint(predicted_pos)
            error_line.AddControlPoint(true_pos)
            error_line.GetDisplayNode().SetSelectedColor(1, 0, 0)

            error_distance = np.linalg.norm(predicted_pos - true_pos)
            self.step8StatusLabel.setText(f"Status: Comparison complete. Prediction Error: {error_distance:.2f} mm")
            self.updateResultsTable()
            
            self.updateStepUI()

        except Exception as e:
            self.step8StatusLabel.setText(f"Status: Error! {e}")
            slicer.util.errorDisplay(f"Comparison failed: {e}")

    def onPrevButtonClicked(self):
        if self.currentStep > 0:
            self.currentStep -= 1
            self.updateStepUI(forceStep=self.currentStep)

    def onNextButtonClicked(self):
        # Re-sync scene (but don't change step)
        self.syncWithScene()
        
        # Check if current step is complete
        # Use determineCurrentStep only to know which step we are at, but don't auto-jump.
        # Instead, check completeness based on current step.
        stepComplete = False
        if self.currentStep == 0:
            stepComplete = self.landmarksNode is not None
        elif self.currentStep == 1:
            stepComplete = self.referencePlane is not None
        elif self.currentStep == 2:
            stepComplete = (self.boneModel is not None) or self.manualVolumeRendering
        elif self.currentStep == 3:
            # For step 3 (cutting), if volume rendering mode and no model, allow skipping
            if self.manualVolumeRendering and self.boneModel is None:
                stepComplete = True
            else:
                stepComplete = (self.boneLeftModel is not None and self.boneRightModel is not None) or self.step4_skipped
        elif self.currentStep == 4:
            self.vmjAcaLine = slicer.util.getFirstNodeByName("VMJ-aca")
            stepComplete = self.vmjAcaLine is not None
        elif self.currentStep == 5:
            stepComplete = self.step6_complete
        elif self.currentStep == 6:
            stepComplete = self.predictedPronasaleNode is not None
        elif self.currentStep == 7:
            stepComplete = True  # Step 8 optional
        elif self.currentStep == 8:
            stepComplete = True  # Step 9 final

        if not stepComplete:
            if self.currentStep == 6:
                slicer.util.warningDisplay("Please perform the prediction first.")
            else:
                slicer.util.warningDisplay(f"Please complete Step {self.currentStep + 1} before proceeding.")
            return

        if self.currentStep < self.stepStack.count - 1:
            self.currentStep += 1
            self.updateStepUI(forceStep=self.currentStep)

    def updateStepUI(self, forceStep=None):
        self.cleanup()
        
        if forceStep is not None:
            self.currentStep = forceStep
        # No auto-detection – keep current step
        
        self.stepStack.setCurrentIndex(self.currentStep)
        self.stepLabel.setText(f"Step {self.currentStep + 1}/{self.stepStack.count}")
        self.prevButton.setEnabled(self.currentStep > 0)
        self.nextButton.setEnabled(self.currentStep < self.stepStack.count - 1)
        
        is_vector_step = (self.currentStep == 5)
        if self.nasalSpineVector:
            self.nasalSpineVector.GetDisplayNode().SetVisibility(is_vector_step)
            self.nasalSpineVector.SetLocked(not is_vector_step)
        if self.subProLine:
            self.subProLine.GetDisplayNode().SetVisibility(is_vector_step)
        
        if is_vector_step:
            if not self.nasalSpineVector:
                self.createNasalSpineVector()
            if self.nasalSpineVector and not self.vectorObserver:
                self.vectorObserver = self.nasalSpineVector.AddObserver(
                    slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.onNasalSpineVectorModified
                )
        
        if self.currentStep == 3:
            self.updateStep4UI()
        
        if self.currentStep == 6:
            self.updatePredictionUI()
        
        step_names = [
            "Load Landmarks",
            "Create Reference Plane",
            "Load Bone Model or Volume",
            "Cut Bone Model (Optional)",
            "Create VMJ-aca Line",
            "Define Nasal Spine Vector & mp",
            "Predict Pronasale",
            "Validate Prediction",
            "Results"
        ]
        
        if hasattr(self, 'stepStatusLabel'):
            self.stepStatusLabel.setText(f"📍 Step {self.currentStep + 1}: {step_names[self.currentStep]}")


# ====== Entry Point ======
try:
    mainWindow = slicer.util.mainWindow()
    old_gui = mainWindow.findChild(qt.QWidget, "ThreefoldANSGUI")
    if old_gui:
        if hasattr(old_gui, 'cleanup'):
            old_gui.cleanup()
        old_gui.deleteLater()
        slicer.app.processEvents()
except Exception as e:
    print(f"Error during cleanup: {e}")

threefoldGui = ThreefoldANSGUI()
threefoldGui.show()

```
