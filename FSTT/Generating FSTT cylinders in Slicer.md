# Interactive Facial Soft Tissue Thickness Generation Tool

> [!IMPORTANT]
> YOU MUST HAVE THE SLICERMORPH EXTENSION INSTALLED IN YOUR 3D SLICER

## Contents

The code below opens a Graphic User Interface in 3D Slicer[^1] guiding through the process of landmark placement and the virtual FSTT cylinder creation. 
<details>
<summary> Full GUI for FSTT </summary>
```python
import os
import vtk
import numpy as np
import qt
import slicer
import json

class SoftTissueThicknessPegsGUI(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle("Soft Tissue Thickness Cylinders Tool")
        self.setObjectName("SoftTissueThicknessPegsGUI")
        
        # ✨ KEEP WINDOW ON TOP
        self.setWindowFlags(
            self.windowFlags() | 
            qt.Qt.WindowStaysOnTopHint |
            qt.Qt.Window
        )
        
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setSpacing(10)
        
        self.stepStack = qt.QStackedWidget()
        self.mainLayout.addWidget(self.stepStack)
        
        # Node storage
        self.landmarksNode = None
        self.surfaceModel = None
        self.volumeNode = None
        self.useVolumeMode = False
        self.pegModels = {}
        self.pegLines = {}
        self.pegLengthData = {}
        
        # Storage for construction lines and curves (Step 3.5)
        self.constructionLines = {}
        self.orbitCurves = {}
        
        # NEW: Realignment and segmentation tracking
        self.needsRealignment = False
        self.needsSegmentation = False
        self.croppedVolume = None
        self.boneSegmentationNode = None
        self.fhpTransformNode = None
        
        # Default FSTT values (mean and SD) - UPDATED with mn
        self.defaultFSTT = {
            "op": {"mean": 6.0, "sd": 2.0},
            "v": {"mean": 5.0, "sd": 1.5},
            "g": {"mean": 5.5, "sd": 1.0},
            "n": {"mean": 6.0, "sd": 1.5},
            "mn": {"mean": 4.5, "sd": 1.5},
            "me": {"mean": 7.0, "sd": 2.5},
            "rhi": {"mean": 3.0, "sd": 1.0},
            "ss": {"mean": 13.5, "sd": 3.5},
            "mp": {"mean": 11.5, "sd": 2.5},
            "pr": {"mean": 12.0, "sd": 3.0},
            "id": {"mean": 13.5, "sd": 3.0},
            "sm": {"mean": 11.0, "sd": 2.0},
            "pg": {"mean": 11.0, "sd": 2.5},
            "gn": {"mean": 7.5, "sd": 2.5},
            "msoL": {"mean": 7.0, "sd": 2.0},
            "msoR": {"mean": 7.0, "sd": 2.0},
            "mioL": {"mean": 6.5, "sd": 3.0},
            "mioR": {"mean": 6.5, "sd": 3.0},
            "acL": {"mean": 10.0, "sd": 3.0},
            "acR": {"mean": 10.0, "sd": 3.0},
            "goL": {"mean": 12.5, "sd": 6.0},
            "goR": {"mean": 12.5, "sd": 6.0},
            "zyL": {"mean": 7.5, "sd": 3.0},
            "zyR": {"mean": 7.5, "sd": 3.0},
            "sCL": {"mean": 10.5, "sd": 2.5},
            "sCR": {"mean": 10.5, "sd": 2.5},
            "iCL": {"mean": 11.0, "sd": 2.5},
            "iCR": {"mean": 11.0, "sd": 2.5},
            "ecm2(s)L": {"mean": 26.0, "sd": 7.0},
            "ecm2(s)R": {"mean": 26.0, "sd": 7.0},
            "ecm2(i)L": {"mean": 22.0, "sd": 6.5},
            "ecm2(i)R": {"mean": 22.0, "sd": 6.5},
            "mrL": {"mean": 19.5, "sd": 5.0},
            "mrR": {"mean": 19.5, "sd": 5.0},
            "mmbL": {"mean": 11.0, "sd": 4.0},
            "mmbR": {"mean": 11.0, "sd": 4.0}
        }
        
        # Current step tracking
        self.currentStep = 0
        self.currentSelectedLandmark = None
        
        # Create all steps
        self.createAllStepWidgets()
        self.setupNavigation()
        self.syncWithScene()
        self.updateStepUI()

    def createAllStepWidgets(self):
        self.createStep0_Welcome()
        self.createStep0_5_FHPRealignment()
        self.createStep0_75_ROICrop()
        self.createStep1_SegmentationOption()
        self.createStep1_5_BoneSegmentation()
        self.createStep2_LoadSurface()
        self.createStep3_LoadLandmarks()
        self.createStep3_5_LandmarkHelpers()
        self.createStep4_GeneratePegs()
        self.createStep5_AdjustPegs()
        self.createStep6_Export()

    def setupNavigation(self):
        navWidget = qt.QWidget()
        navLayout = qt.QHBoxLayout(navWidget)
        navLayout.setContentsMargins(0, 0, 0, 0)
        
        self.prevButton = qt.QPushButton("Previous")
        self.prevButton.setToolTip("Go to the previous step.")
        self.prevButton.clicked.connect(self.onPrevButtonClicked)
        
        self.stepLabel = qt.QLabel("Step 1/11")
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

    # ==================== STEP CREATION METHODS ====================

    def createStep0_Welcome(self):
        """Simplified welcome screen without volume selector"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Welcome to the Soft Tissue Thickness Cylinders Tool")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "This tool helps you create facial soft tissue thickness (FSTT) predictions "
            "for craniofacial approximation.\n\n"
            "This workflow includes optional preprocessing steps:"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Workflow options
        optionsGroup = qt.QGroupBox("Workflow Setup")
        optionsLayout = qt.QVBoxLayout(optionsGroup)
        
        # Realignment option
        self.needRealignmentCheckbox = qt.QCheckBox("🔄 My volume needs FHP realignment")
        self.needRealignmentCheckbox.setToolTip(
            "Check this if your skull is not aligned to the Frankfort Horizontal Plane.\n"
            "This will add a re-orientation step to the workflow."
        )
        self.needRealignmentCheckbox.setChecked(False)
        optionsLayout.addWidget(self.needRealignmentCheckbox)
        
        # Segmentation option
        self.needSegmentationCheckbox = qt.QCheckBox("🦴 I need to create bone segmentation")
        self.needSegmentationCheckbox.setToolTip(
            "Check this if you don't have a 3D skull model yet.\n"
            "This will add automatic segmentation steps to create a bone model."
        )
        self.needSegmentationCheckbox.setChecked(False)
        optionsLayout.addWidget(self.needSegmentationCheckbox)
        
        layout.addWidget(optionsGroup)
        
        # Info box
        infoLabel = qt.QLabel(
            "<b>ℹ️ What you'll do next:</b><br>"
            "✓ (Optional) Realign volume to FHP<br>"
            "✓ (Optional) Crop volume with ROI<br>"
            "✓ (Optional) Create bone segmentation<br>"
            "✓ Load or create your 3D skull model<br>"
            "✓ Load hard tissue landmarks<br>"
            "✓ Use helpers to place Type II/III landmarks<br>"
            "✓ Generate FSTT cylinders automatically<br>"
            "✓ Adjust and export your results"
        )
        infoLabel.setTextFormat(qt.Qt.RichText)
        infoLabel.setWordWrap(True)
        infoLabel.setStyleSheet(
            "background-color: #E3F2FD; "
            "border: 1px solid #2196F3; "
            "border-radius: 5px; "
            "padding: 10px;"
        )
        layout.addWidget(infoLabel)
        
        self.step0StatusLabel = qt.QLabel("Status: Check the options above, then click 'Next' to begin.")
        self.step0StatusLabel.setWordWrap(True)
        layout.addWidget(self.step0StatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep0_5_FHPRealignment(self):
        """FHP Realignment step with volume selector"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step: FHP Realignment")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Realign your volume to the Frankfort Horizontal Plane (FHP) for proper orientation.\n\n"
            "The FHP is defined by three landmarks: left porion (poL), right porion (poR), "
            "and left orbitale (zyoL)."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # ✅ VOLUME SELECTOR (MOVED FROM WELCOME SCREEN)
        volumeGroup = qt.QGroupBox("1. Select Volume")
        volumeLayout = qt.QFormLayout(volumeGroup)
        
        self.fhpVolumeSelector = slicer.qMRMLNodeComboBox()
        self.fhpVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.fhpVolumeSelector.setMRMLScene(slicer.mrmlScene)
        self.fhpVolumeSelector.addEnabled = False
        self.fhpVolumeSelector.removeEnabled = False
        self.fhpVolumeSelector.noneEnabled = False
        self.fhpVolumeSelector.setToolTip("Select the CT volume to realign")
        self.fhpVolumeSelector.currentNodeChanged.connect(self.onFHPVolumeSelected)
        volumeLayout.addRow("CT Volume:", self.fhpVolumeSelector)
        
        layout.addWidget(volumeGroup)
        
        # FHP landmarks selector
        landmarkGroup = qt.QGroupBox("2. Select or Load FHP Landmarks")
        landmarkLayout = qt.QVBoxLayout(landmarkGroup)
        
        formLayout = qt.QFormLayout()
        self.fhpLandmarksSelector = slicer.qMRMLNodeComboBox()
        self.fhpLandmarksSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.fhpLandmarksSelector.setMRMLScene(slicer.mrmlScene)
        self.fhpLandmarksSelector.addEnabled = False
        self.fhpLandmarksSelector.removeEnabled = False
        self.fhpLandmarksSelector.noneEnabled = True
        self.fhpLandmarksSelector.setToolTip("Select FHP landmarks (poL, poR, zyoL)")
        formLayout.addRow("FHP Landmarks:", self.fhpLandmarksSelector)
        landmarkLayout.addLayout(formLayout)
        
        # Quick load button
        self.autoLoadFHPButton = qt.QPushButton("📥 Download FHP Landmark Template")
        self.autoLoadFHPButton.setToolTip("Download standard FHP landmarks template")
        self.autoLoadFHPButton.clicked.connect(self.autoLoadFHPLandmarks)
        landmarkLayout.addWidget(self.autoLoadFHPButton)
        
        layout.addWidget(landmarkGroup)
        
        # Apply section
        applyGroup = qt.QGroupBox("3. Apply Realignment")
        applyLayout = qt.QVBoxLayout(applyGroup)
        
        # Apply button
        self.applyFHPButton = qt.QPushButton("🔄 Apply FHP Realignment")
        self.applyFHPButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.applyFHPButton.setEnabled(True)  # ✅ ALWAYS ENABLED
        self.applyFHPButton.clicked.connect(self.onApplyFHP)
        applyLayout.addWidget(self.applyFHPButton)
        
        # Undo button
        self.undoFHPButton = qt.QPushButton("↩️ Undo Realignment")
        self.undoFHPButton.setEnabled(False)
        self.undoFHPButton.clicked.connect(self.onUndoFHP)
        applyLayout.addWidget(self.undoFHPButton)
        
        layout.addWidget(applyGroup)
        
        self.stepFHPStatusLabel = qt.QLabel("Status: Select a volume and load FHP landmarks.")
        self.stepFHPStatusLabel.setWordWrap(True)
        layout.addWidget(self.stepFHPStatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep0_75_ROICrop(self):
        """Optional ROI crop step"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step (Optional): Crop Volume with ROI")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "If your volume is very large, you can crop it to the region of interest "
            "to speed up processing.\n\n"
            "This step is optional - click 'Next' to skip."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Volume rendering button
        vrButton = qt.QPushButton("📦 Open Volume Rendering Module")
        vrButton.setIcon(qt.QIcon(":/Icons/VolumeRendering.png"))
        vrButton.clicked.connect(lambda: slicer.util.selectModule("VolumeRendering"))
        layout.addWidget(vrButton)
        
        # ROI selector
        formLayout = qt.QFormLayout()
        self.roiSelector = slicer.qMRMLNodeComboBox()
        self.roiSelector.nodeTypes = ["vtkMRMLAnnotationROINode", "vtkMRMLMarkupsROINode"]
        self.roiSelector.setMRMLScene(slicer.mrmlScene)
        self.roiSelector.addEnabled = False
        self.roiSelector.removeEnabled = False
        self.roiSelector.noneEnabled = True
        self.roiSelector.setToolTip("Select an ROI box")
        formLayout.addRow("ROI:", self.roiSelector)
        layout.addLayout(formLayout)
        
        # Crop button
        self.cropButton = qt.QPushButton("✂ Crop Volume")
        self.cropButton.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        self.cropButton.clicked.connect(self.onCropVolume)
        layout.addWidget(self.cropButton)
        
        self.stepCropStatusLabel = qt.QLabel("Status: Optional - draw an ROI box and click 'Crop', or skip.")
        self.stepCropStatusLabel.setWordWrap(True)
        layout.addWidget(self.stepCropStatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep1_SegmentationOption(self):
        """Ask if user wants segmentation"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step (Optional): Create Bone Segmentation")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Do you want to create a 3D bone model for visualization?\n\n"
            "This is optional - you can work directly with the CT volume if you prefer."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        self.wantSegmentationYes = qt.QRadioButton("Yes, create bone model (recommended)")
        self.wantSegmentationYes.setChecked(True)
        self.wantSegmentationNo = qt.QRadioButton("No, I'll use the CT volume only")
        
        layout.addWidget(self.wantSegmentationYes)
        layout.addWidget(self.wantSegmentationNo)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep1_5_BoneSegmentation(self):
        """Automatic bone segmentation"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step: Create Bone Model")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Click the button below to automatically create a 3D bone model.\n"
            "This usually takes 10-30 seconds."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        self.createBoneModelButton = qt.QPushButton("🦴 Create Bone Model Automatically")
        self.createBoneModelButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.createBoneModelButton.clicked.connect(self.onCreateBoneModel)
        layout.addWidget(self.createBoneModelButton)
        
        # Model selector for confirmation
        formLayout = qt.QFormLayout()
        self.boneModelSelectorAuto = slicer.qMRMLNodeComboBox()
        self.boneModelSelectorAuto.nodeTypes = ["vtkMRMLModelNode"]
        self.boneModelSelectorAuto.setMRMLScene(slicer.mrmlScene)
        self.boneModelSelectorAuto.addEnabled = False
        self.boneModelSelectorAuto.removeEnabled = False
        self.boneModelSelectorAuto.noneEnabled = True
        self.boneModelSelectorAuto.currentNodeChanged.connect(self.onBoneModelSelected)
        formLayout.addRow("Bone Model:", self.boneModelSelectorAuto)
        layout.addLayout(formLayout)
        
        self.stepSegStatusLabel = qt.QLabel("Status: Ready to create bone model.")
        self.stepSegStatusLabel.setWordWrap(True)
        layout.addWidget(self.stepSegStatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep2_LoadSurface(self):
        """Original Step 2 - Load Surface Data"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step: Load Surface Data")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Choose your input type:\n"
            "• <b>Segmented Model:</b> Use if you already have a 3D skull model\n"
            "• <b>CT Volume:</b> Use if you have raw DICOM/CT scan data\n\n"
            "The tool will automatically detect the bone surface from the CT scan."
        )
        desc.setTextFormat(qt.Qt.RichText)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Mode selection
        modeGroup = qt.QGroupBox("Input Mode")
        modeLayout = qt.QVBoxLayout(modeGroup)
        
        self.modelModeRadio = qt.QRadioButton("Use Segmented Model")
        self.modelModeRadio.setChecked(True)
        self.modelModeRadio.toggled.connect(self.onInputModeChanged)
        
        self.volumeModeRadio = qt.QRadioButton("Use CT Volume (Auto-detect surface)")
        self.volumeModeRadio.toggled.connect(self.onInputModeChanged)
        
        modeLayout.addWidget(self.modelModeRadio)
        modeLayout.addWidget(self.volumeModeRadio)
        layout.addWidget(modeGroup)
        
        # Model selector
        self.modelSelectorWidget = qt.QWidget()
        modelSelectorLayout = qt.QVBoxLayout(self.modelSelectorWidget)
        modelSelectorLayout.setContentsMargins(0, 0, 0, 0)
        
        self.surfaceModelSelector = slicer.qMRMLNodeComboBox()
        self.surfaceModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.surfaceModelSelector.setMRMLScene(slicer.mrmlScene)
        self.surfaceModelSelector.addEnabled = False
        self.surfaceModelSelector.removeEnabled = False
        self.surfaceModelSelector.noneEnabled = True
        self.surfaceModelSelector.showHidden = False
        self.surfaceModelSelector.showChildNodeTypes = False
        self.surfaceModelSelector.selectNodeUponCreation = False
        self.surfaceModelSelector.setToolTip("Select the bone surface model for peg placement.")
        self.surfaceModelSelector.currentNodeChanged.connect(self.onSurfaceModelSelected)
        
        modelSelectorLayout.addWidget(qt.QLabel("Surface Model:"))
        modelSelectorLayout.addWidget(self.surfaceModelSelector)
        layout.addWidget(self.modelSelectorWidget)
        
        # Volume selector
        self.volumeSelectorWidget = qt.QWidget()
        volumeSelectorLayout = qt.QVBoxLayout(self.volumeSelectorWidget)
        volumeSelectorLayout.setContentsMargins(0, 0, 0, 0)
        
        self.volumeSelector = slicer.qMRMLNodeComboBox()
        self.volumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.volumeSelector.setMRMLScene(slicer.mrmlScene)
        self.volumeSelector.addEnabled = False
        self.volumeSelector.removeEnabled = False
        self.volumeSelector.noneEnabled = True
        self.volumeSelector.showHidden = False
        self.volumeSelector.showChildNodeTypes = False
        self.volumeSelector.selectNodeUponCreation = False
        self.volumeSelector.renameEnabled = False
        self.volumeSelector.setToolTip("Select the CT volume for surface detection.")
        self.volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onVolumeSelected)
        
        volumeSelectorLayout.addWidget(qt.QLabel("CT Volume:"))
        volumeSelectorLayout.addWidget(self.volumeSelector)
        
        thresholdGroup = qt.QGroupBox("Surface Detection Settings")
        thresholdLayout = qt.QFormLayout(thresholdGroup)
        # In createStep2_LoadSurface, inside thresholdGroup:
        self.suggestThresholdButton = qt.QPushButton("🔍 Suggest HU Threshold from Landmarks")
        self.suggestThresholdButton.setToolTip("Sample voxels around all placed landmarks to find the best bone threshold.")
        self.suggestThresholdButton.clicked.connect(self.suggestHUThreshold)
        thresholdLayout.addRow("", self.suggestThresholdButton)  # or add it below the spinboxes
                
        self.boneThresholdMinSpinBox = qt.QDoubleSpinBox()
        self.boneThresholdMinSpinBox.setRange(-1000, 3000)
        self.boneThresholdMinSpinBox.setValue(300)
        self.boneThresholdMinSpinBox.setSuffix(" HU")
        self.boneThresholdMinSpinBox.setToolTip("Minimum Hounsfield Unit for bone (typical: 300)")
        thresholdLayout.addRow("Bone Threshold (Min):", self.boneThresholdMinSpinBox)
        
        self.boneThresholdMaxSpinBox = qt.QDoubleSpinBox()
        self.boneThresholdMaxSpinBox.setRange(-1000, 3000)
        self.boneThresholdMaxSpinBox.setValue(3000)
        self.boneThresholdMaxSpinBox.setSuffix(" HU")
        self.boneThresholdMaxSpinBox.setToolTip("Maximum Hounsfield Unit for bone (typical: 3000)")
        thresholdLayout.addRow("Bone Threshold (Max):", self.boneThresholdMaxSpinBox)
        
        self.normalSampleRadiusSpinBox = qt.QDoubleSpinBox()
        self.normalSampleRadiusSpinBox.setRange(1, 15)  # Increased max range
        self.normalSampleRadiusSpinBox.setValue(5)      # Increased default value
        self.normalSampleRadiusSpinBox.setSuffix(" mm")
        self.normalSampleRadiusSpinBox.setToolTip("Radius for sampling surface normal around landmark. Increase for noisy/curved bone.")
        thresholdLayout.addRow("Normal Sample Radius:", self.normalSampleRadiusSpinBox)
        
        volumeSelectorLayout.addWidget(thresholdGroup)
        layout.addWidget(self.volumeSelectorWidget)
        
        # Initially hide volume selector
        self.volumeSelectorWidget.setVisible(False)
        
        self.step2StatusLabel = qt.QLabel("Status: Waiting for user to select input data.")
        self.step2StatusLabel.setWordWrap(True)
        layout.addWidget(self.step2StatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def suggestHUThreshold(self):
        """
        Samples voxels around all placed landmarks and suggests an optimal
        bone threshold (minimum HU) based on the histogram.
        Updates the spinbox and prints statistics.
        """
        # First, try to get the volume from the current selector (if visible)
        volume = None
        if self.volumeSelectorWidget.isVisible():
            volume = self.volumeSelector.currentNode()
        if volume is None:
            volume = self.volumeNode   # fallback to the stored node

        if volume is None:
            # Try the FHP selector as a last resort
            if hasattr(self, 'fhpVolumeSelector'):
                volume = self.fhpVolumeSelector.currentNode()
        if volume is None:
            slicer.util.warningDisplay(
                "No CT volume found.\n\n"
                "Please select a CT volume in Step 2 (under 'Use CT Volume') "
                "or in the FHP realignment step first."
            )
            return

        # Ensure landmarks are loaded
        if not self.landmarksNode:
            slicer.util.warningDisplay("Please load landmarks first (Step 3).")
            return

        # Use the user's current sample radius
        sampleRadius = self.normalSampleRadiusSpinBox.value
        imageData = volume.GetImageData()
        spacing = volume.GetSpacing()
        dims = imageData.GetDimensions()

        worldToIJK = vtk.vtkMatrix4x4()
        volume.GetRASToIJKMatrix(worldToIJK)

        all_values = []
        num_points = self.landmarksNode.GetNumberOfControlPoints()

        for i in range(num_points):
            pos = np.zeros(3)
            self.landmarksNode.GetNthControlPointPositionWorld(i, pos)

            # Convert to IJK
            ijk = [0, 0, 0, 1]
            worldToIJK.MultiplyPoint([pos[0], pos[1], pos[2], 1], ijk)
            i0, j0, k0 = int(round(ijk[0])), int(round(ijk[1])), int(round(ijk[2]))

            # Sample a spherical patch
            radiusIJK = max(2, int(sampleRadius / max(spacing)))
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
                        all_values.append(val)

        if len(all_values) < 50:
            slicer.util.warningDisplay("Not enough voxels sampled! Try increasing the sample radius.")
            return

        all_values = np.array(all_values)
        hist, bin_edges = np.histogram(all_values, bins=100)

        # Find the valley between soft tissue and bone (limit to 0–2000 HU)
        valid_indices = np.where((bin_edges[:-1] > 0) & (bin_edges[:-1] < 2000))[0]
        if len(valid_indices) < 2:
            suggested = 300  # fallback
        else:
            valley_idx = valid_indices[np.argmin(hist[valid_indices])]
            suggested = int(bin_edges[valley_idx])

        # Clamp to reasonable values
        suggested = max(100, min(1500, suggested))

        # Display statistics in the console and status bar
        stats_msg = (
            f"Suggested Min HU: {suggested}\n"
            f"Sampled range: {np.min(all_values):.0f} – {np.max(all_values):.0f}\n"
            f"Mean: {np.mean(all_values):.0f} ± {np.std(all_values):.0f}\n"
            f"(Based on {len(all_values)} voxels around {num_points} landmarks)"
        )
        print(stats_msg)

        # Update the spinbox
        self.boneThresholdMinSpinBox.blockSignals(True)
        self.boneThresholdMinSpinBox.setValue(suggested)
        self.boneThresholdMinSpinBox.blockSignals(False)

        self.step2StatusLabel.setText(
            f"✅ Threshold suggested: {suggested} HU. Adjust if needed."
        )
        slicer.util.showStatusMessage(f"Suggested threshold: {suggested} HU", 3000)

    def createStep3_LoadLandmarks(self):
        """Original Step 3 - Load Landmarks"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step: Load Hard Tissue Landmarks")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Load the hard tissue landmarks (in .mrk.json format) that define where the cylinders should be placed. "
            "These should match the standard craniofacial landmark set.\n\n"
            "You can download a template landmark file or load your own."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        buttonLayout = qt.QVBoxLayout()
        buttonLayout.setSpacing(10)
        
        # Download template button
        self.downloadTemplateButton = qt.QPushButton("Download Template Landmarks")
        self.downloadTemplateButton.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.downloadTemplateButton.setToolTip("Download the standard FSTT hard tissue landmark template")
        self.downloadTemplateButton.clicked.connect(self.onDownloadTemplate)
        buttonLayout.addWidget(self.downloadTemplateButton)
        
        # Load local file button
        self.loadLandmarksButton = qt.QPushButton("Load Landmarks from Local File")
        self.loadLandmarksButton.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 8px;")
        self.loadLandmarksButton.setToolTip("Choose a .mrk.json file from your computer.")
        self.loadLandmarksButton.clicked.connect(self.onLoadLandmarks)
        buttonLayout.addWidget(self.loadLandmarksButton)
        
        layout.addLayout(buttonLayout)
        
        self.step3StatusLabel = qt.QLabel("Status: Waiting for user to load landmarks.")
        self.step3StatusLabel.setWordWrap(True)
        layout.addWidget(self.step3StatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep3_5_LandmarkHelpers(self):
        """Step 3.5: Helpers for Type II and III landmark placement."""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 3.5: Landmark Placement Helpers (Optional)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Use these tools to help place Type II and III landmarks accurately.\n"
            "These landmarks are derived from Type I landmarks or anatomical constructions."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Scroll area for all helpers
        scrollArea = qt.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setMinimumHeight(400)
        
        scrollContent = qt.QWidget()
        scrollLayout = qt.QVBoxLayout(scrollContent)
        scrollLayout.setSpacing(15)
        
        # ========== MIDPOINT HELPERS ==========
        midpointGroup = qt.QGroupBox("Midpoint Helpers")
        midpointLayout = qt.QVBoxLayout(midpointGroup)
        
        # mn helper
        mnLayout = qt.QHBoxLayout()
        mnLayout.addWidget(qt.QLabel("<b>mn</b> (midpoint between n and rhi):"))
        self.calculateMnBtn = qt.QPushButton("Calculate and Place")
        self.calculateMnBtn.clicked.connect(lambda: self.calculateMidpoint("mn", "n", "rhi"))
        mnLayout.addWidget(self.calculateMnBtn)
        mnLayout.addStretch()
        midpointLayout.addLayout(mnLayout)
        
        # mp helper
        mpLayout = qt.QHBoxLayout()
        mpLayout.addWidget(qt.QLabel("<b>mp</b> (midpoint between ss and pr):"))
        self.calculateMpBtn = qt.QPushButton("Calculate and Place")
        self.calculateMpBtn.clicked.connect(lambda: self.calculateMidpoint("mp", "ss", "pr"))
        mpLayout.addWidget(self.calculateMpBtn)
        mpLayout.addStretch()
        midpointLayout.addLayout(mpLayout)
        
        # gn helper
        gnLayout = qt.QHBoxLayout()
        gnLayout.addWidget(qt.QLabel("<b>gn</b> (midpoint between pg and me):"))
        self.calculateGnBtn = qt.QPushButton("Calculate and Place")
        self.calculateGnBtn.clicked.connect(lambda: self.calculateMidpoint("gn", "pg", "me"))
        gnLayout.addWidget(self.calculateGnBtn)
        gnLayout.addStretch()
        midpointLayout.addLayout(gnLayout)
        
        scrollLayout.addWidget(midpointGroup)
        
        # ========== LATERAL OFFSET HELPERS ==========
        lateralGroup = qt.QGroupBox("Lateral Offset Helpers")
        lateralLayout = qt.QVBoxLayout(lateralGroup)
        
        lateralDesc = qt.QLabel("Note: alL and alR must be placed first")
        lateralDesc.setStyleSheet("color: #666; font-style: italic;")
        lateralLayout.addWidget(lateralDesc)
        
        # ac helpers
        acLayout = qt.QHBoxLayout()
        acLayout.addWidget(qt.QLabel("<b>acL/acR</b> (5mm lateral to alL/alR):"))
        self.calculateAcBtn = qt.QPushButton("Calculate and Place Both")
        self.calculateAcBtn.clicked.connect(self.calculateAcLandmarks)
        acLayout.addWidget(self.calculateAcBtn)
        acLayout.addStretch()
        lateralLayout.addLayout(acLayout)
        
        scrollLayout.addWidget(lateralGroup)
        
        # ========== GONION HELPERS ==========
        gonionGroup = qt.QGroupBox("Gonion (go) Helpers - Line Intersection Method")
        gonionLayout = qt.QVBoxLayout(gonionGroup)
        
        gonionDesc = qt.QLabel(
            "Draw two lines per side:\n"
            "1. Along the vertical margin of ramus (posterior border)\n"
            "2. Along the horizontal margin of corpus (inferior border)\n"
            "The tool will find their intersection as gonion."
        )
        gonionDesc.setWordWrap(True)
        gonionLayout.addWidget(gonionDesc)
        
        # Right side
        goRLayout = qt.QVBoxLayout()
        goRLayout.addWidget(qt.QLabel("<b>Right Gonion (goR):</b>"))
        goRBtnLayout = qt.QHBoxLayout()
        self.drawRamusRBtn = qt.QPushButton("Draw Ramus Line (R)")
        self.drawRamusRBtn.clicked.connect(lambda: self.startDrawingLine("ramusR"))
        goRBtnLayout.addWidget(self.drawRamusRBtn)
        self.drawCorpusRBtn = qt.QPushButton("Draw Corpus Line (R)")
        self.drawCorpusRBtn.clicked.connect(lambda: self.startDrawingLine("corpusR"))
        goRBtnLayout.addWidget(self.drawCorpusRBtn)
        self.calculateGoRBtn = qt.QPushButton("Calculate goR")
        self.calculateGoRBtn.clicked.connect(lambda: self.calculateGonion("R"))
        goRBtnLayout.addWidget(self.calculateGoRBtn)
        goRLayout.addLayout(goRBtnLayout)
        gonionLayout.addLayout(goRLayout)
        
        # Left side
        goLLayout = qt.QVBoxLayout()
        goLLayout.addWidget(qt.QLabel("<b>Left Gonion (goL):</b>"))
        goLBtnLayout = qt.QHBoxLayout()
        self.drawRamusLBtn = qt.QPushButton("Draw Ramus Line (L)")
        self.drawRamusLBtn.clicked.connect(lambda: self.startDrawingLine("ramusL"))
        goLBtnLayout.addWidget(self.drawRamusLBtn)
        self.drawCorpusLBtn = qt.QPushButton("Draw Corpus Line (L)")
        self.drawCorpusLBtn.clicked.connect(lambda: self.startDrawingLine("corpusL"))
        goLBtnLayout.addWidget(self.drawCorpusLBtn)
        self.calculateGoLBtn = qt.QPushButton("Calculate goL")
        self.calculateGoLBtn.clicked.connect(lambda: self.calculateGonion("L"))
        goLBtnLayout.addWidget(self.calculateGoLBtn)
        goLLayout.addLayout(goLBtnLayout)
        gonionLayout.addLayout(goLLayout)
        
        scrollLayout.addWidget(gonionGroup)
        
        # ========== MMB HELPERS ==========
        mmbGroup = qt.QGroupBox("Mid-Mandibular Border (mmb) Helpers")
        mmbLayout = qt.QVBoxLayout(mmbGroup)
        
        mmbDesc = qt.QLabel("Note: pg, goL, and goR must be placed first")
        mmbDesc.setStyleSheet("color: #666; font-style: italic;")
        mmbLayout.addWidget(mmbDesc)
        
        # mmbR
        mmbRLayout = qt.QHBoxLayout()
        mmbRLayout.addWidget(qt.QLabel("<b>mmbR</b> (midpoint between pg and goR):"))
        self.calculateMmbRBtn = qt.QPushButton("Calculate and Place")
        self.calculateMmbRBtn.clicked.connect(lambda: self.calculateMidpoint("mmbR", "pg", "goR"))
        mmbRLayout.addWidget(self.calculateMmbRBtn)
        mmbRLayout.addStretch()
        mmbLayout.addLayout(mmbRLayout)
        
        # mmbL
        mmbLLayout = qt.QHBoxLayout()
        mmbLLayout.addWidget(qt.QLabel("<b>mmbL</b> (midpoint between pg and goL):"))
        self.calculateMmbLBtn = qt.QPushButton("Calculate and Place")
        self.calculateMmbLBtn.clicked.connect(lambda: self.calculateMidpoint("mmbL", "pg", "goL"))
        mmbLLayout.addWidget(self.calculateMmbLBtn)
        mmbLLayout.addStretch()
        mmbLayout.addLayout(mmbLLayout)
        
        scrollLayout.addWidget(mmbGroup)
        
        # ========== ORBITAL HELPERS ==========
        orbitalGroup = qt.QGroupBox("Orbital (mso/mio) Helpers - Advanced")
        orbitalLayout = qt.QVBoxLayout(orbitalGroup)
        
        orbitalDesc = qt.QLabel(
            "Draw closed curves around each orbit. The tool will find the vertical bisecting line "
            "and place mso (superior) and mio (inferior) landmarks."
        )
        orbitalDesc.setWordWrap(True)
        orbitalLayout.addWidget(orbitalDesc)
        
        # Right orbit
        orbitRLayout = qt.QHBoxLayout()
        orbitRLayout.addWidget(qt.QLabel("<b>Right Orbit:</b>"))
        self.drawOrbitRBtn = qt.QPushButton("Draw Orbit Curve (R)")
        self.drawOrbitRBtn.clicked.connect(lambda: self.startDrawingCurve("orbitR"))
        orbitRLayout.addWidget(self.drawOrbitRBtn)
        self.calculateOrbitRBtn = qt.QPushButton("Calculate msoR and mioR")
        self.calculateOrbitRBtn.clicked.connect(lambda: self.calculateOrbitalLandmarks("R"))
        orbitRLayout.addWidget(self.calculateOrbitRBtn)
        orbitRLayout.addStretch()
        orbitalLayout.addLayout(orbitRLayout)
        
        # Left orbit
        orbitLLayout = qt.QHBoxLayout()
        orbitLLayout.addWidget(qt.QLabel("<b>Left Orbit:</b>"))
        self.drawOrbitLBtn = qt.QPushButton("Draw Orbit Curve (L)")
        self.drawOrbitLBtn.clicked.connect(lambda: self.startDrawingCurve("orbitL"))
        orbitLLayout.addWidget(self.drawOrbitLBtn)
        self.calculateOrbitLBtn = qt.QPushButton("Calculate msoL and mioL")
        self.calculateOrbitLBtn.clicked.connect(lambda: self.calculateOrbitalLandmarks("L"))
        orbitLLayout.addWidget(self.calculateOrbitLBtn)
        orbitLLayout.addStretch()
        orbitalLayout.addLayout(orbitLLayout)
        
        scrollLayout.addWidget(orbitalGroup)
        
        scrollLayout.addStretch()
        scrollArea.setWidget(scrollContent)
        layout.addWidget(scrollArea)
        
        # Status
        self.step3_5StatusLabel = qt.QLabel("Status: Use the helpers above to place Type II and III landmarks.")
        self.step3_5StatusLabel.setWordWrap(True)
        layout.addWidget(self.step3_5StatusLabel)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep4_GeneratePegs(self):
        """Original Step 4 - Generate Pegs"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 4: Generate Cylinders")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Click the button below to automatically generate cylindrical pegs at each landmark position. "
            "The pegs will be:\n"
            "• Placed perpendicular to the bone surface\n"
            "• Oriented outward from the bone\n"
            "• Set to mean soft tissue thickness values from research literature"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Reference information
        refGroup = qt.QGroupBox("FSTT Reference Data")
        refLayout = qt.QVBoxLayout(refGroup)
        
        refLabel = qt.QLabel(
            "<b>Reference Study:</b> Hona, T. W. P. T. and C. N. Stephan (2024). "
            "\"Global facial soft tissue thicknesses for craniofacial identification (2023): "
            "a review of 140 years of data since Welcker's first study.\" "
            "<i>International Journal of Legal Medicine</i> 138(2): 519-535."
        )
        refLabel.setTextFormat(qt.Qt.RichText)
        refLabel.setOpenExternalLinks(True)
        refLabel.setWordWrap(True)
        refLabel.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        refLayout.addWidget(refLabel)
        
        # Create scrollable table
        tableScroll = qt.QScrollArea()
        tableScroll.setWidgetResizable(True)
        tableScroll.setMaximumHeight(250)
        
        tableWidget = qt.QTableWidget()
        tableWidget.setColumnCount(4)
        tableWidget.setHorizontalHeaderLabels(["Landmark Pair", "Hard Tissue", "Soft Tissue", "Mean ± SD (mm)"])
        
        # Populate table with data
        tableData = [
            ("op–op'", "op", "op'", "6.0 ± 2.0"),
            ("v–v'", "v", "v'", "5.0 ± 1.5"),
            ("g–g'", "g", "g'", "5.5 ± 1.0"),
            ("n–se'", "n", "se'", "6.0 ± 1.5"),
            ("mn–mn'", "mn", "mn'", "4.5 ± 1.5"),
            ("rhi–rhi'", "rhi", "rhi'", "3.0 ± 1.0"),
            ("ss–sn'", "ss", "sn'", "13.5 ± 3.5"),
            ("mp–mp'", "mp", "mp'", "11.5 ± 2.5"),
            ("pr–ls'", "pr", "ls'", "12.0 ± 3.0"),
            ("id–li'", "id", "li'", "13.5 ± 3.0"),
            ("sm–sm'", "sm", "sm'", "11.0 ± 2.0"),
            ("pg–pg'", "pg", "pg'", "11.0 ± 2.5"),
            ("gn–gn'", "gn", "gn'", "7.5 ± 2.5"),
            ("me–me'", "me", "me'", "7.0 ± 2.5"),
            ("mso–mso'", "msoL/R", "mso'L/R", "7.0 ± 2.0"),
            ("mio–mio'", "mioL/R", "mio'L/R", "6.5 ± 3.0"),
            ("ac–ac'", "acL/R", "ac'L/R", "10.0 ± 3.0"),
            ("go–go'", "goL/R", "go'L/R", "12.5 ± 6.0"),
            ("zy–zy'", "zyL/R", "zy'L/R", "7.5 ± 3.0"),
            ("sC–sC'", "sCL/R", "sC'L/R", "10.5 ± 2.5"),
            ("iC–iC'", "iCL/R", "iC'L/R", "11.0 ± 2.5"),
            ("ecm2–sM2'", "ecm2(s)L/R", "sM2'L/R", "26.0 ± 7.0"),
            ("ecm2–iM2'", "ecm2(i)L/R", "iM2'L/R", "22.0 ± 6.5"),
            ("mr–mr'", "mrL/R", "mr'L/R", "19.5 ± 5.0"),
            ("mmb–mmb'", "mmbL/R", "mmb'L/R", "11.0 ± 4.0"),
        ]
        
        tableWidget.setRowCount(len(tableData))
        for row, (pair, hard, soft, value) in enumerate(tableData):
            tableWidget.setItem(row, 0, qt.QTableWidgetItem(pair))
            tableWidget.setItem(row, 1, qt.QTableWidgetItem(hard))
            tableWidget.setItem(row, 2, qt.QTableWidgetItem(soft))
            tableWidget.setItem(row, 3, qt.QTableWidgetItem(value))
        
        tableWidget.resizeColumnsToContents()
        tableWidget.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        tableScroll.setWidget(tableWidget)
        refLayout.addWidget(tableScroll)
        
        layout.addWidget(refGroup)
        
        # Peg parameters
        formLayout = qt.QFormLayout()
        
        self.pegRadiusSpinBox = qt.QDoubleSpinBox()
        self.pegRadiusSpinBox.setRange(0.5, 10.0)
        self.pegRadiusSpinBox.setValue(1.5)
        self.pegRadiusSpinBox.setSuffix(" mm")
        self.pegRadiusSpinBox.setToolTip("Radius of the cylindrical pegs.")
        formLayout.addRow("Peg Radius:", self.pegRadiusSpinBox)
        
        # NEW: Perpendicularity Weight Slider
        self.perpendicularityWeightSlider = qt.QSlider(qt.Qt.Horizontal)
        self.perpendicularityWeightSlider.setRange(0, 100)
        self.perpendicularityWeightSlider.setValue(80) # Default 80% surface normal, 20% anatomical
        self.perpendicularityWeightSlider.setTickPosition(qt.QSlider.TicksBelow)
        self.perpendicularityWeightSlider.setTickInterval(10)
        self.perpendicularityWeightSlider.setToolTip("0 = Pure Anatomical Direction\n100 = Pure Surface Perpendicularity\nDefault 80 emphasizes perpendicularity while keeping anatomical safety net.")
        
        weightLayout = qt.QHBoxLayout()
        weightLayout.addWidget(qt.QLabel("0 (Anatomical)"))
        weightLayout.addWidget(self.perpendicularityWeightSlider)
        weightLayout.addWidget(qt.QLabel("100 (Perpendicular)"))
        formLayout.addRow("Perpendicularity Weight:", weightLayout)
        
        self.showSDEndpointsCheckbox = qt.QCheckBox("Show ± SD Endpoints")
        self.showSDEndpointsCheckbox.setChecked(False)
        self.showSDEndpointsCheckbox.setToolTip(
            "Create additional endpoint markers for Mean - SD and Mean + SD lengths.\n"
            "This visualizes the statistical range for each landmark."
        )
        formLayout.addRow("", self.showSDEndpointsCheckbox)
        
        layout.addLayout(formLayout)
        
        self.generatePegsButton = qt.QPushButton("Generate Cylinders")
        self.generatePegsButton.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px;")
        self.generatePegsButton.clicked.connect(self.onGeneratePegs)
        layout.addWidget(self.generatePegsButton, 0, qt.Qt.AlignHCenter)
        
        self.step4StatusLabel = qt.QLabel("Status: Ready to generate cylinders.")
        self.step4StatusLabel.setWordWrap(True)
        layout.addWidget(self.step4StatusLabel)
        
        # Visibility controls (initially hidden, shown after peg generation)
        self.visibilityControlsWidget = qt.QGroupBox("Visibility Controls")
        self.visibilityControlsWidget.setVisible(False)
        visibilityLayout = qt.QVBoxLayout(self.visibilityControlsWidget)
        
        # Cylinders visibility
        cylHeaderLayout = qt.QHBoxLayout()
        cylHeader = qt.QLabel("<b>Cylinders (Pegs):</b>")
        cylHeaderLayout.addWidget(cylHeader)
        cylHeaderLayout.addStretch()
        visibilityLayout.addLayout(cylHeaderLayout)
        
        cylButtonLayout = qt.QHBoxLayout()
        self.showAllCylindersBtn = qt.QPushButton("Show All")
        self.showAllCylindersBtn.clicked.connect(lambda: self.setVisibility("cylinders", "all", True))
        cylButtonLayout.addWidget(self.showAllCylindersBtn)
        
        self.hideAllCylindersBtn = qt.QPushButton("Hide All")
        self.hideAllCylindersBtn.clicked.connect(lambda: self.setVisibility("cylinders", "all", False))
        cylButtonLayout.addWidget(self.hideAllCylindersBtn)
        
        self.showMeanCylindersBtn = qt.QPushButton("Mean Only")
        self.showMeanCylindersBtn.clicked.connect(lambda: self.setVisibility("cylinders", "mean", True))
        cylButtonLayout.addWidget(self.showMeanCylindersBtn)
        
        self.showSDCylindersBtn = qt.QPushButton("± SD Only")
        self.showSDCylindersBtn.clicked.connect(lambda: self.setVisibility("cylinders", "sd", True))
        cylButtonLayout.addWidget(self.showSDCylindersBtn)
        
        visibilityLayout.addLayout(cylButtonLayout)
        
        # Lines visibility
        lineHeaderLayout = qt.QHBoxLayout()
        lineHeader = qt.QLabel("<b>Lines:</b>")
        lineHeaderLayout.addWidget(lineHeader)
        lineHeaderLayout.addStretch()
        visibilityLayout.addLayout(lineHeaderLayout)
        
        lineButtonLayout = qt.QHBoxLayout()
        self.showAllLinesBtn = qt.QPushButton("Show All")
        self.showAllLinesBtn.clicked.connect(lambda: self.setVisibility("lines", "all", True))
        lineButtonLayout.addWidget(self.showAllLinesBtn)
        
        self.hideAllLinesBtn = qt.QPushButton("Hide All")
        self.hideAllLinesBtn.clicked.connect(lambda: self.setVisibility("lines", "all", False))
        lineButtonLayout.addWidget(self.hideAllLinesBtn)
        
        self.showMeanLinesBtn = qt.QPushButton("Mean Only")
        self.showMeanLinesBtn.clicked.connect(lambda: self.setVisibility("lines", "mean", True))
        lineButtonLayout.addWidget(self.showMeanLinesBtn)
        
        self.showSDLinesBtn = qt.QPushButton("± SD Only")
        self.showSDLinesBtn.clicked.connect(lambda: self.setVisibility("lines", "sd", True))
        lineButtonLayout.addWidget(self.showSDLinesBtn)
        
        visibilityLayout.addLayout(lineButtonLayout)
        
        # Landmarks visibility
        landmarkHeaderLayout = qt.QHBoxLayout()
        landmarkHeader = qt.QLabel("<b>Soft Tissue Landmarks:</b>")
        landmarkHeaderLayout.addWidget(landmarkHeader)
        landmarkHeaderLayout.addStretch()
        visibilityLayout.addLayout(landmarkHeaderLayout)
        
        landmarkButtonLayout = qt.QHBoxLayout()
        self.showAllLandmarksBtn = qt.QPushButton("Show All")
        self.showAllLandmarksBtn.clicked.connect(lambda: self.setVisibility("landmarks", "all", True))
        landmarkButtonLayout.addWidget(self.showAllLandmarksBtn)
        
        self.hideAllLandmarksBtn = qt.QPushButton("Hide All")
        self.hideAllLandmarksBtn.clicked.connect(lambda: self.setVisibility("landmarks", "all", False))
        landmarkButtonLayout.addWidget(self.hideAllLandmarksBtn)
        
        self.showMeanLandmarksBtn = qt.QPushButton("Mean Only")
        self.showMeanLandmarksBtn.clicked.connect(lambda: self.setVisibility("landmarks", "mean", True))
        landmarkButtonLayout.addWidget(self.showMeanLandmarksBtn)
        
        self.showSDLandmarksBtn = qt.QPushButton("± SD Only")
        self.showSDLandmarksBtn.clicked.connect(lambda: self.setVisibility("landmarks", "sd", True))
        landmarkButtonLayout.addWidget(self.showSDLandmarksBtn)
        
        visibilityLayout.addLayout(landmarkButtonLayout)
        
        layout.addWidget(self.visibilityControlsWidget)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    def createStep5_AdjustPegs(self):
        """Step 5: Adjust all peg lengths with individual sliders."""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 5: Adjust FSTT Cylinder Lengths")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Adjust the facial soft tissue thickness (FSTT) for each landmark individually.\n"
            "Each slider shows the statistical range (Mean ± SD) based on research literature.\n"
            "All values are initially set to the mean. Adjust as needed and click 'Update' to apply changes."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create scroll area for all the sliders
        scrollArea = qt.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setMinimumHeight(400)
        
        scrollContent = qt.QWidget()
        scrollLayout = qt.QVBoxLayout(scrollContent)
        scrollLayout.setSpacing(10)
        scrollLayout.setContentsMargins(5, 5, 5, 5)
        
        # Storage for all the slider widgets
        self.pegSliders = {}
        self.pegSpinBoxes = {}
        self.pegLabels = {}
        
        # Group landmarks by type for better organization
        midlineLandmarks = []
        bilateralLandmarks = []
        
        for label in sorted(self.defaultFSTT.keys()):
            if label.endswith('L') or label.endswith('R'):
                bilateralLandmarks.append(label)
            else:
                midlineLandmarks.append(label)
        
        # Create midline section
        midlineHeader = qt.QLabel("<b>Midline Landmarks</b>")
        midlineHeader.setStyleSheet("font-size: 14px; color: #007BFF; margin-top: 10px;")
        scrollLayout.addWidget(midlineHeader)
        
        for label in midlineLandmarks:
            self.createLandmarkSlider(label, scrollLayout)
        
        # Create bilateral section
        bilateralHeader = qt.QLabel("<b>Bilateral Landmarks</b>")
        bilateralHeader.setStyleSheet("font-size: 14px; color: #007BFF; margin-top: 10px;")
        scrollLayout.addWidget(bilateralHeader)
        
        for label in bilateralLandmarks:
            self.createLandmarkSlider(label, scrollLayout)
        
        scrollLayout.addStretch()
        scrollArea.setWidget(scrollContent)
        layout.addWidget(scrollArea)
        
        # Quick adjustment buttons
        buttonLayout = qt.QHBoxLayout()
        
        self.resetAllToMeanButton = qt.QPushButton("Reset All to Mean")
        self.resetAllToMeanButton.setToolTip("Reset all FSTT values to their mean values")
        self.resetAllToMeanButton.clicked.connect(self.onResetAllToMean)
        buttonLayout.addWidget(self.resetAllToMeanButton)
        
        self.setAllToMinButton = qt.QPushButton("Set All to Mean - SD")
        self.setAllToMinButton.setToolTip("Set all FSTT values to minimum (Mean - SD)")
        self.setAllToMinButton.clicked.connect(self.onSetAllToMin)
        buttonLayout.addWidget(self.setAllToMinButton)
        
        self.setAllToMaxButton = qt.QPushButton("Set All to Mean + SD")
        self.setAllToMaxButton.setToolTip("Set all FSTT values to maximum (Mean + SD)")
        self.setAllToMaxButton.clicked.connect(self.onSetAllToMax)
        buttonLayout.addWidget(self.setAllToMaxButton)
        
        layout.addLayout(buttonLayout)
        
        # Update button
        self.updatePegsButton = qt.QPushButton("Update FSTT Adjustments")
        self.updatePegsButton.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; padding: 10px; font-size: 14px;"
        )
        self.updatePegsButton.setToolTip("Apply all FSTT adjustments and update the cylinder models")
        self.updatePegsButton.clicked.connect(self.onUpdateAllPegs)
        layout.addWidget(self.updatePegsButton, 0, qt.Qt.AlignHCenter)
        
        self.step5StatusLabel = qt.QLabel("Status: Adjust FSTT values as needed, then click 'Update'.")
        self.step5StatusLabel.setWordWrap(True)
        layout.addWidget(self.step5StatusLabel)
        
        self.stepStack.addWidget(widget)

    def createStep6_Export(self):
        """Original Step 6 - Export"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 6: Export Models")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "Export the surface model and pegs to common 3D file formats "
            "for use in ZBrush, FreeForm, or other 3D modeling software."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Export format selection
        self.exportFormatComboBox = qt.QComboBox()
        self.exportFormatComboBox.addItems(["OBJ (.obj)", "STL (.stl)", "PLY (.ply)", "VTK (.vtk)"])
        layout.addWidget(qt.QLabel("Export Format:"))
        layout.addWidget(self.exportFormatComboBox)
        
        # Export options
        self.exportSurfaceCheckbox = qt.QCheckBox("Export Surface Model")
        self.exportSurfaceCheckbox.setChecked(True)
        layout.addWidget(self.exportSurfaceCheckbox)
        
        self.exportPegsCheckbox = qt.QCheckBox("Export Cylinders")
        self.exportPegsCheckbox.setChecked(True)
        layout.addWidget(self.exportPegsCheckbox)
        
        self.exportCombinedCheckbox = qt.QCheckBox("Export as Combined Model")
        self.exportCombinedCheckbox.setChecked(False)
        self.exportCombinedCheckbox.setToolTip("Combine surface and cylinders into a single file.")
        layout.addWidget(self.exportCombinedCheckbox)
        
        # Export buttons
        buttonLayout = qt.QHBoxLayout()
        
        self.exportButton = qt.QPushButton("Export Models")
        self.exportButton.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px;")
        self.exportButton.clicked.connect(self.onExport)
        buttonLayout.addWidget(self.exportButton)
        
        self.saveLengthsButton = qt.QPushButton("Save FSTT Cylinder Lengths (JSON)")
        self.saveLengthsButton.setStyleSheet("background-color: #6c757d; color: white; padding: 10px;")
        self.saveLengthsButton.setToolTip("Save the cylinder length data to a JSON file for future use.")
        self.saveLengthsButton.clicked.connect(self.onSaveLengths)
        buttonLayout.addWidget(self.saveLengthsButton)
        
        layout.addLayout(buttonLayout)
        
        self.step6StatusLabel = qt.QLabel("Status: Ready to export.")
        self.step6StatusLabel.setWordWrap(True)
        layout.addWidget(self.step6StatusLabel)
        
        # Finish button
        self.finishButton = qt.QPushButton("Finish")
        self.finishButton.clicked.connect(self.onFinish)
        layout.addWidget(self.finishButton)
        
        layout.addStretch(1)
        self.stepStack.addWidget(widget)

    # ==================== CALLBACK METHODS ====================

    def onFHPVolumeSelected(self, node):
        """Handle volume selection in FHP step"""
        if node:
            self.volumeNode = node
            print(f"✅ FHP volume selected: {node.GetName()}")
            self.stepFHPStatusLabel.setText(f"Status: Volume '{node.GetName()}' selected. Load landmarks and click Apply.")
        else:
            self.volumeNode = None
            self.stepFHPStatusLabel.setText("Status: Please select a volume.")
    
    def onFHPLandmarksSelected(self, node):
        """Check if FHP landmarks are valid - IMPROVED label detection"""
        if not node or not self.volumeNode:
            self.applyFHPButton.setEnabled(False)
            return
        
        # Check for required landmarks with flexible matching
        labels = [node.GetNthControlPointLabel(i) for i in range(node.GetNumberOfControlPoints())]
        
        # Debug: print all labels
        print(f"DEBUG: FHP landmark labels found: {labels}")
        
        # Flexible matching for common variations
        has_poL = any(
            label.lower() in ['pol', 'po-l', 'porionl', 'porion-l', 'porion left'] 
            for label in labels
        )
        has_poR = any(
            label.lower() in ['por', 'po-r', 'porionr', 'porion-r', 'porion right'] 
            for label in labels
        )
        has_zyoL = any(
            label.lower() in ['zyol', 'zyo-l', 'orbl', 'orb-l', 'orbitalel', 'orbitale-l', 'orbitale left'] 
            for label in labels
        )
        
        # Also try case-insensitive substring matching
        if not has_poL:
            has_poL = any('pol' in label.lower() or 'porion' in label.lower() and 'l' in label.lower() for label in labels)
        if not has_poR:
            has_poR = any('por' in label.lower() or 'porion' in label.lower() and 'r' in label.lower() for label in labels)
        if not has_zyoL:
            has_zyoL = any(('zyo' in label.lower() or 'orb' in label.lower() or 'orbitale' in label.lower()) and 'l' in label.lower() for label in labels)
        
        if has_poL and has_poR and has_zyoL:
            self.applyFHPButton.setEnabled(True)
            self.stepFHPStatusLabel.setText("Status: ✅ All FHP landmarks found! Ready to apply realignment.")
        else:
            self.applyFHPButton.setEnabled(False)
            missing = []
            if not has_poL: missing.append("poL (left porion)")
            if not has_poR: missing.append("poR (right porion)")
            if not has_zyoL: missing.append("zyoL/orbL (left orbitale)")
            self.stepFHPStatusLabel.setText(f"Status: Missing landmarks: {', '.join(missing)}")
            print(f"DEBUG: Missing FHP landmarks: {missing}")

    def onApplyFHP(self):
        """Apply FHP realignment - FINAL CORRECTED VERSION"""
        print("=" * 80)
        print("🔍 DEBUG: onApplyFHP() called!")
        print("=" * 80)
        
        # ✅ KEY FIX: Get volume directly from selector
        inputVolume = self.fhpVolumeSelector.currentNode()
        
        if not inputVolume:
            print("⚠️ fhpVolumeSelector returned None, trying self.volumeNode...")
            inputVolume = self.volumeNode
        
        if not inputVolume:
            print("⚠️ self.volumeNode is None, trying croppedVolume...")
            inputVolume = self.croppedVolume
        
        if not inputVolume:
            print("❌ ERROR: No volume found!")
            slicer.util.errorDisplay("Please select a CT volume in the dropdown above!")
            return
        
        # Store for later use
        self.volumeNode = inputVolume
        print(f"✅ Using volume: {inputVolume.GetName()}")
        
        fhpNode = self.fhpLandmarksSelector.currentNode()
        if not fhpNode:
            print("❌ ERROR: No FHP landmarks selected!")
            slicer.util.errorDisplay("Please load or select FHP landmarks!")
            return
        
        print(f"✅ FHP landmarks: {fhpNode.GetName()} ({fhpNode.GetNumberOfControlPoints()} points)")
        
        self.stepFHPStatusLabel.setText("Status: Applying FHP realignment...")
        slicer.app.processEvents()
        
        try:
            # Find landmarks
            poL_pos, poR_pos, zyoL_pos = None, None, None
            
            for i in range(fhpNode.GetNumberOfControlPoints()):
                label = fhpNode.GetNthControlPointLabel(i).lower()
                pos = np.zeros(3)
                fhpNode.GetNthControlPointPositionWorld(i, pos)
                
                if 'pol' in label and 'r' not in label:
                    poL_pos = np.array(pos)
                elif 'por' in label and 'l' not in label:
                    poR_pos = np.array(pos)
                elif 'zyo' in label or 'orb' in label:
                    zyoL_pos = np.array(pos)
            
            if poL_pos is None or poR_pos is None or zyoL_pos is None:
                raise ValueError("Could not find all FHP landmarks (poL, poR, zyoL)")
            
            print(f"✅ Found all landmarks: poL={poL_pos}, poR={poR_pos}, zyoL={zyoL_pos}")
            
            # Calculate FHP transform
            po_vec = poR_pos - poL_pos
            
            vTransform1 = vtk.vtkTransform()
            vTransform1.RotateZ(-np.arctan2(po_vec[1], po_vec[0]) * 180 / np.pi)
            
            zyoL_p1 = np.array(vTransform1.GetMatrix().MultiplyPoint(np.append(zyoL_pos, 1.0)))[:3]
            poR_p1 = np.array(vTransform1.GetMatrix().MultiplyPoint(np.append(poR_pos, 1.0)))[:3]
            poL_p1 = np.array(vTransform1.GetMatrix().MultiplyPoint(np.append(poL_pos, 1.0)))[:3]
            
            po_vec_p1 = poR_p1 - poL_p1
            vTransform2 = vtk.vtkTransform()
            vTransform2.RotateY(np.arctan2(po_vec_p1[2], po_vec_p1[0]) * 180 / np.pi)
            
            zyoL_p2 = np.array(vTransform2.GetMatrix().MultiplyPoint(np.append(zyoL_p1, 1.0)))[:3]
            poR_p2 = np.array(vTransform2.GetMatrix().MultiplyPoint(np.append(poR_p1, 1.0)))[:3]
            poL_p2 = np.array(vTransform2.GetMatrix().MultiplyPoint(np.append(poL_p1, 1.0)))[:3]
            
            mid_porion_p2 = (poR_p2 + poL_p2) / 2.0
            po_zyo_vec = zyoL_p2 - mid_porion_p2
            vTransform3 = vtk.vtkTransform()
            vTransform3.RotateX(-np.arctan2(po_zyo_vec[2], po_zyo_vec[1]) * 180 / np.pi)
            
            final_transform = vtk.vtkTransform()
            final_transform.Concatenate(vTransform1)
            final_transform.Concatenate(vTransform2)
            final_transform.Concatenate(vTransform3)
            
            # Create transform node
            self.fhpTransformNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLinearTransformNode', 'FHP_Transform')
            self.fhpTransformNode.SetMatrixTransformToParent(final_transform.GetMatrix())
            
            # Apply to volume
            inputVolume.SetAndObserveTransformNodeID(self.fhpTransformNode.GetID())
            print(f"✅ Transform applied to {inputVolume.GetName()}")
            
            # Apply to landmarks if they exist
            if self.landmarksNode:
                self.landmarksNode.SetAndObserveTransformNodeID(self.fhpTransformNode.GetID())
                print(f"✅ Transform applied to landmarks")
            
            # Harden transform
            inputVolume.HardenTransform()
            if self.landmarksNode:
                self.landmarksNode.HardenTransform()
            print("✅ Transform hardened")
            
            self.undoFHPButton.setEnabled(True)
            self.stepFHPStatusLabel.setText("Status: ✅ FHP realignment applied successfully!")
            slicer.util.showStatusMessage("FHP realignment complete!", 3000)
            print("✅ FHP REALIGNMENT COMPLETED!")
            
        except Exception as e:
            self.stepFHPStatusLabel.setText(f"Status: ❌ Error: {str(e)}")
            slicer.util.errorDisplay(f"FHP realignment failed:\n\n{str(e)}")
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

    def onUndoFHP(self):
        """Undo FHP realignment"""
        if not self.volumeNode:
            return
        
        if self.fhpTransformNode:
            self.volumeNode.SetAndObserveTransformNodeID(None)
            slicer.mrmlScene.RemoveNode(self.fhpTransformNode)
            self.fhpTransformNode = None
        
        self.undoFHPButton.setEnabled(False)
        self.stepFHPStatusLabel.setText("Status: Realignment undone.")
        slicer.util.showStatusMessage("FHP realignment undone!", 3000)

    def autoLoadFHPLandmarks(self):
        """Download and load FHP landmark template"""
        self.stepFHPStatusLabel.setText("Status: Downloading FHP landmarks...")
        slicer.app.processEvents()
        
        url = "https://github.com/user-attachments/files/22434441/FHP_landmarks.json"
        try:
            import urllib.request
            tempPath = os.path.join(slicer.app.temporaryPath, "FHP_landmarks.json")
            urllib.request.urlretrieve(url, tempPath)
            loadedNode = slicer.util.loadMarkups(tempPath)
            if loadedNode:
                loadedNode.SetName("FHP_Landmarks")
                self.fhpLandmarksSelector.setCurrentNode(loadedNode)
                
                # Debug: show what was loaded
                numPoints = loadedNode.GetNumberOfControlPoints()
                print(f"✅ Loaded FHP template with {numPoints} points:")
                for i in range(numPoints):
                    label = loadedNode.GetNthControlPointLabel(i)
                    print(f"   {i}: {label}")
                
                self.stepFHPStatusLabel.setText(
                    f"Status: FHP landmarks loaded ({numPoints} points). "
                    "Place them on your scan, then click 'Apply'."
                )
                slicer.util.showStatusMessage("FHP landmarks loaded!", 3000)
            else:
                raise Exception("Failed to load landmarks")
        except Exception as e:
            self.stepFHPStatusLabel.setText(f"Status: Error downloading: {e}")
            slicer.util.errorDisplay(f"Could not download landmarks: {e}")

    def onCropVolume(self):
        """Crop volume with ROI"""
        roiNode = self.roiSelector.currentNode()
        if not self.volumeNode:
            slicer.util.warningDisplay("No volume selected!")
            return
        if not roiNode:
            slicer.util.warningDisplay("Please select an ROI!")
            return
        
        self.stepCropStatusLabel.setText("Status: Cropping...")
        slicer.app.processEvents()
        
        try:
            # Use Crop Volume module
            cropVolumeLogic = slicer.modules.cropvolume.logic()
            self.croppedVolume = slicer.mrmlScene.AddNewNodeByClass(
                "vtkMRMLScalarVolumeNode", 
                self.volumeNode.GetName() + "_cropped"
            )
            cropVolumeLogic.CropVoxelBased(roiNode, self.volumeNode, self.croppedVolume)
            
            # Hide original, show cropped
            self.volumeNode.GetDisplayNode().SetVisibility(False)
            slicer.util.setSliceViewerLayers(background=self.croppedVolume)
            
            # Update reference
            self.volumeNode = self.croppedVolume
            
            self.stepCropStatusLabel.setText("Status: ✅ Volume cropped successfully!")
            slicer.util.showStatusMessage("Volume cropped!", 3000)
            
        except Exception as e:
            self.stepCropStatusLabel.setText(f"Status: ❌ Error: {e}")
            slicer.util.errorDisplay(f"Cropping failed: {e}")

    def onCreateBoneModel(self):
        """Automatic bone segmentation (simplified from landmarking GUI)"""
        sourceVolume = self.croppedVolume if self.croppedVolume else self.volumeNode
        if not sourceVolume:
            slicer.util.errorDisplay("No volume found!")
            return
        
        self.stepSegStatusLabel.setText("Status: Creating bone model...")
        slicer.app.processEvents()
        
        try:
            # Get CT value range
            imageData = sourceVolume.GetImageData()
            minValue, maxValue = imageData.GetScalarRange()
            
            # Create segmentation
            segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "Bone_Segmentation")
            segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(sourceVolume)
            
            # Add bone segment
            segmentID = segmentationNode.GetSegmentation().AddEmptySegment("Bone", "Bone")
            
            # Set up segment editor
            segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
            segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
            segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
            segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
            segmentEditorWidget.setSegmentationNode(segmentationNode)
            segmentEditorWidget.setSourceVolumeNode(sourceVolume)
            
            # Apply threshold
            minThreshold = 500  # Bone threshold
            self.stepSegStatusLabel.setText(f"Status: Applying threshold ({minThreshold} HU)...")
            slicer.app.processEvents()
            
            segmentEditorWidget.setActiveEffectByName("Threshold")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("MinimumThreshold", str(minThreshold))
            effect.setParameter("MaximumThreshold", str(maxValue))
            effect.self().onApply()
            
            # Create 3D surface
            self.stepSegStatusLabel.setText("Status: Creating 3D surface...")
            slicer.app.processEvents()
            segmentationNode.CreateClosedSurfaceRepresentation()
            
            # Export to model
            modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Bone")
            segmentationLogic = slicer.modules.segmentations.logic()
            success = segmentationLogic.ExportSegmentToRepresentationNode(
                segmentationNode.GetSegmentation().GetSegment(segmentID),
                modelNode
            )
            
            if success:
                # Set color
                displayNode = modelNode.GetDisplayNode()
                if not displayNode:
                    modelNode.CreateDefaultDisplayNodes()
                    displayNode = modelNode.GetDisplayNode()
                if displayNode:
                    displayNode.SetColor(0.9, 0.9, 0.8)  # Bone white
                    displayNode.SetOpacity(1.0)
                
                self.surfaceModel = modelNode
                self.boneModelSelectorAuto.setCurrentNode(modelNode)
                self.boneSegmentationNode = segmentationNode
                
                # Hide segmentation node
                if segmentationNode.GetDisplayNode():
                    segmentationNode.GetDisplayNode().SetVisibility(False)
                
                self.stepSegStatusLabel.setText("Status: ✅ Bone model created successfully!")
                slicer.util.showStatusMessage("Bone model created!", 3000)
            else:
                raise Exception("Export failed")
            
            # Cleanup
            slicer.mrmlScene.RemoveNode(segmentEditorNode)
            
        except Exception as e:
            self.stepSegStatusLabel.setText(f"Status: ❌ Error: {e}")
            slicer.util.errorDisplay(f"Segmentation failed: {e}")
            import traceback
            traceback.print_exc()

    def onBoneModelSelected(self, node):
        """Handle bone model selection"""
        if node:
            self.surfaceModel = node
            self.stepSegStatusLabel.setText(f"Status: Selected '{node.GetName()}' as bone model.")

    def onInputModeChanged(self):
        """Toggle between model and volume mode."""
        if self.modelModeRadio.isChecked():
            self.modelSelectorWidget.setVisible(True)
            self.volumeSelectorWidget.setVisible(False)
            self.useVolumeMode = False
            self.step2StatusLabel.setText("Status: Select a segmented model.")
        else:
            self.modelSelectorWidget.setVisible(False)
            self.volumeSelectorWidget.setVisible(True)
            self.useVolumeMode = True
            self.step2StatusLabel.setText("Status: Select a CT volume.")

    def onSurfaceModelSelected(self, node):
        """Handle model selection."""
        if node:
            self.surfaceModel = node
            self.step2StatusLabel.setText(f"Status: Selected '{self.surfaceModel.GetName()}' as surface model. Ready to proceed.")
        else:
            self.surfaceModel = None
            self.step2StatusLabel.setText("Status: Waiting for user to select a surface model.")

    def onVolumeSelected(self, node):
        """Handle volume selection."""
        if node:
            self.volumeNode = node
            nodeName = self.volumeNode.GetName()
            self.step2StatusLabel.setText(f"Status: Selected '{nodeName}' as CT volume. Ready to proceed.")
        else:
            self.volumeNode = None
            self.step2StatusLabel.setText("Status: Waiting for user to select a CT volume.")

    def onLoadLandmarks(self):
        """Load landmarks from local file"""
        fileName, _ = qt.QFileDialog.getOpenFileName(self, "Load Landmarks", "", "Markup JSON Files (*.mrk.json)")
        if fileName:
            loadedNode = slicer.util.loadMarkups(fileName)
            if loadedNode:
                self.landmarksNode = loadedNode
                self.step3StatusLabel.setText(f"Status: Successfully loaded '{self.landmarksNode.GetName()}' with {self.landmarksNode.GetNumberOfControlPoints()} landmarks.")
                slicer.util.showStatusMessage(f"'{self.landmarksNode.GetName()}' loaded!", 3000)
            else:
                slicer.util.errorDisplay(f"Failed to load landmarks from {fileName}.")

    def onDownloadTemplate(self):
        """Download the template landmark file from GitHub."""
        try:
            import urllib.request
            import tempfile
            
            self.step3StatusLabel.setText("Status: Downloading template...")
            slicer.app.processEvents()
            
            url = "https://github.com/user-attachments/files/25114784/FSTT.Hard.tissue.mrk.json"
            
            # Create temp file
            tempDir = tempfile.gettempdir()
            localPath = os.path.join(tempDir, "FSTT_Hard_tissue_template.mrk.json")
            
            # Download file
            urllib.request.urlretrieve(url, localPath)
            
            # Load the file
            loadedNode = slicer.util.loadMarkups(localPath)
            if loadedNode:
                self.landmarksNode = loadedNode
                self.landmarksNode.SetName("FSTT Hard tissue")
                self.step3StatusLabel.setText(
                    f"Status: Downloaded and loaded template with {self.landmarksNode.GetNumberOfControlPoints()} landmarks. "
                    "You can now place/adjust them."
                )
                slicer.util.showStatusMessage("Template landmarks loaded!", 3000)
            else:
                slicer.util.errorDisplay("Failed to load downloaded template.")
                
        except Exception as e:
            self.step3StatusLabel.setText(f"Status: Failed to download template. Error: {e}")
            slicer.util.errorDisplay(f"Download failed: {e}\nYou can manually download from the GitHub link and load it.")

    # ==================== LANDMARK HELPER METHODS ====================

    def calculateMidpoint(self, targetLabel, landmark1Label, landmark2Label):
        """Calculate midpoint between two landmarks and place/update target landmark."""
        if not self.landmarksNode:
            slicer.util.warningDisplay("Please load landmarks first.")
            return
        
        try:
            # Find the two source landmarks
            pos1 = None
            pos2 = None
            
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                label = self.landmarksNode.GetNthControlPointLabel(i)
                if label == landmark1Label:
                    pos1 = np.zeros(3)
                    self.landmarksNode.GetNthControlPointPositionWorld(i, pos1)
                elif label == landmark2Label:
                    pos2 = np.zeros(3)
                    self.landmarksNode.GetNthControlPointPositionWorld(i, pos2)
            
            if pos1 is None or pos2 is None:
                slicer.util.warningDisplay(f"Could not find both {landmark1Label} and {landmark2Label}. Please place them first.")
                return
            
            # Calculate midpoint
            midpoint = (pos1 + pos2) / 2
            
            # Check if target already exists
            targetIdx = -1
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                if self.landmarksNode.GetNthControlPointLabel(i) == targetLabel:
                    targetIdx = i
                    break
            
            # Update or create
            if targetIdx >= 0:
                self.landmarksNode.SetNthControlPointPositionWorld(targetIdx, midpoint)
                slicer.util.showStatusMessage(f"Updated {targetLabel} position", 2000)
            else:
                self.landmarksNode.AddControlPoint(midpoint, targetLabel)
                slicer.util.showStatusMessage(f"Placed {targetLabel} at midpoint", 2000)
            
            # Snap to surface
            if self.surfaceModel:
                self.snapLandmarkToSurface(targetLabel)
            
            self.step3_5StatusLabel.setText(f"Status: {targetLabel} calculated and snapped to surface. You can adjust it manually.")
            
        except Exception as e:
            slicer.util.errorDisplay(f"Error calculating midpoint: {e}")

    def calculateAcLandmarks(self):
        """Calculate acL and acR as 5mm lateral to alL and alR - FINAL CORRECTED."""
        if not self.landmarksNode:
            slicer.util.warningDisplay("Please load landmarks first.")
            return
        
        try:
            # Find alL and alR
            alL_pos = None
            alR_pos = None
            
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                label = self.landmarksNode.GetNthControlPointLabel(i)
                if label == "alL":
                    alL_pos = np.zeros(3)
                    self.landmarksNode.GetNthControlPointPositionWorld(i, alL_pos)
                elif label == "alR":
                    alR_pos = np.zeros(3)
                    self.landmarksNode.GetNthControlPointPositionWorld(i, alR_pos)
            
            if alL_pos is None or alR_pos is None:
                slicer.util.warningDisplay("Could not find alL and alR. Please place them first.")
                return
            
            # RAS coordinate system:
            # +X = Right (anatomical), -X = Left (anatomical)
            # To move laterally (away from midline):
            # - Left landmark: move MORE negative X (more left)
            # - Right landmark: move MORE positive X (more right)
            
            offset = 5.0
            
            # Left side: move 5mm more left (more negative X)
            acL_pos = alL_pos + np.array([-offset, 0, 0])
            
            # Right side: move 5mm more right (more positive X)
            acR_pos = alR_pos + np.array([offset, 0, 0])
            
            # Debug output
            print(f"DEBUG: alL X-coord: {alL_pos[0]:.2f}, acL X-coord: {acL_pos[0]:.2f} (should be MORE negative)")
            print(f"DEBUG: alR X-coord: {alR_pos[0]:.2f}, acR X-coord: {acR_pos[0]:.2f} (should be MORE positive)")
            
            # Place or update landmarks
            acL_idx = -1
            acR_idx = -1
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                label = self.landmarksNode.GetNthControlPointLabel(i)
                if label == "acL":
                    acL_idx = i
                elif label == "acR":
                    acR_idx = i
            
            if acL_idx >= 0:
                self.landmarksNode.SetNthControlPointPositionWorld(acL_idx, acL_pos)
            else:
                self.landmarksNode.AddControlPoint(acL_pos, "acL")
            
            if acR_idx >= 0:
                self.landmarksNode.SetNthControlPointPositionWorld(acR_idx, acR_pos)
            else:
                self.landmarksNode.AddControlPoint(acR_pos, "acR")
            
            # Snap to surface if model available
            if self.surfaceModel:
                self.snapLandmarkToSurface("acL")
                self.snapLandmarkToSurface("acR")
            
            slicer.util.showStatusMessage("Placed acL and acR laterally", 2000)
            self.step3_5StatusLabel.setText("Status: acL and acR placed 5mm lateral (away from midline). Adjust manually if needed.")
            
        except Exception as e:
            slicer.util.errorDisplay(f"Error calculating ac landmarks: {e}")
            import traceback
            traceback.print_exc()

    def snapLandmarkToSurface(self, landmarkLabel):
        """Snap a landmark to the nearest point on the surface model."""
        if not self.surfaceModel or not self.landmarksNode:
            return
        
        try:
            # Find the landmark
            landmarkIdx = -1
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                if self.landmarksNode.GetNthControlPointLabel(i) == landmarkLabel:
                    landmarkIdx = i
                    break
            
            if landmarkIdx < 0:
                return
            
            # Get current position
            currentPos = np.zeros(3)
            self.landmarksNode.GetNthControlPointPositionWorld(landmarkIdx, currentPos)
            
            # Find closest point on surface
            polyData = self.surfaceModel.GetPolyData()
            locator = vtk.vtkPointLocator()
            locator.SetDataSet(polyData)
            locator.BuildLocator()
            
            closestPointId = locator.FindClosestPoint(currentPos)
            closestPos = np.array(polyData.GetPoint(closestPointId))
            
            distance = np.linalg.norm(currentPos - closestPos)
            
            # Only snap if reasonably close (within 10mm)
            if distance < 10.0:
                self.landmarksNode.SetNthControlPointPositionWorld(landmarkIdx, closestPos)
                print(f"Snapped {landmarkLabel} to surface (distance: {distance:.2f} mm)")
            else:
                print(f"WARNING: {landmarkLabel} too far from surface ({distance:.2f} mm), not snapping")
            
        except Exception as e:
            print(f"Error snapping {landmarkLabel} to surface: {e}")

    def startDrawingLine(self, lineType):
        """Start interactive line drawing for gonion calculation."""
        try:
            lineName = f"construction_line_{lineType}"
            
            # Create or get existing line
            if lineType in self.constructionLines:
                lineNode = self.constructionLines[lineType]
            else:
                lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", lineName)
                lineNode.GetDisplayNode().SetSelectedColor(1, 1, 0)  # Yellow
                lineNode.GetDisplayNode().SetLineThickness(0.5)  # Thinner
                self.constructionLines[lineType] = lineNode
            
            # Clear existing points
            lineNode.RemoveAllControlPoints()
            
            # Set to place mode
            slicer.modules.markups.logic().SetActiveListID(lineNode)
            interactionNode = slicer.app.applicationLogic().GetInteractionNode()
            interactionNode.SetCurrentInteractionMode(interactionNode.Place)
            
            slicer.util.showStatusMessage(f"Draw the {lineType} line (2 points)", 3000)
            
        except Exception as e:
            slicer.util.errorDisplay(f"Error starting line drawing: {e}")

    def calculateGonion(self, side):
        """Calculate gonion as intersection of ramus and corpus lines - with distance checking."""
        try:
            ramusKey = f"ramus{side}"
            corpusKey = f"corpus{side}"
            
            if ramusKey not in self.constructionLines or corpusKey not in self.constructionLines:
                slicer.util.warningDisplay(f"Please draw both ramus and corpus lines for side {side} first.")
                return
            
            ramusLine = self.constructionLines[ramusKey]
            corpusLine = self.constructionLines[corpusKey]
            
            if ramusLine.GetNumberOfControlPoints() < 2 or corpusLine.GetNumberOfControlPoints() < 2:
                slicer.util.warningDisplay("Each line must have 2 points.")
                return
            
            # Get line points
            ramus_p1 = np.zeros(3)
            ramus_p2 = np.zeros(3)
            ramusLine.GetNthControlPointPositionWorld(0, ramus_p1)
            ramusLine.GetNthControlPointPositionWorld(1, ramus_p2)
            
            corpus_p1 = np.zeros(3)
            corpus_p2 = np.zeros(3)
            corpusLine.GetNthControlPointPositionWorld(0, corpus_p1)
            corpusLine.GetNthControlPointPositionWorld(1, corpus_p2)
            
            # Calculate line intersection with distance info
            result = self.findLineIntersection3D(ramus_p1, ramus_p2, corpus_p1, corpus_p2)
            
            if result is None:
                slicer.util.warningDisplay("Lines are parallel or invalid.")
                return
            
            intersection, distance = result
            
            # Warn if lines are far apart
            if distance > 10.0:
                response = slicer.util.confirmYesNoDisplay(
                    f"Warning: The lines are {distance:.1f}mm apart (skew lines).\n"
                    f"This may indicate the lines are not drawn accurately.\n\n"
                    f"Do you want to place gonion at the calculated position anyway?",
                    windowTitle="Lines Don't Meet"
                )
                if not response:
                    return
            elif distance > 3.0:
                print(f"INFO: Lines are {distance:.1f}mm apart (slightly skew)")
            else:
                print(f"INFO: Lines intersect closely (distance: {distance:.1f}mm)")
            
            # Place gonion
            goLabel = f"go{side}"
            go_idx = -1
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                if self.landmarksNode.GetNthControlPointLabel(i) == goLabel:
                    go_idx = i
                    break
            
            if go_idx >= 0:
                self.landmarksNode.SetNthControlPointPositionWorld(go_idx, intersection)
            else:
                self.landmarksNode.AddControlPoint(intersection, goLabel)
            
            # Snap to surface
            if self.surfaceModel:
                self.snapLandmarkToSurface(goLabel)
            
            slicer.util.showStatusMessage(f"Placed {goLabel} at intersection", 2000)
            self.step3_5StatusLabel.setText(
                f"Status: {goLabel} calculated (line distance: {distance:.1f}mm) and snapped to surface. "
                "Adjust manually if needed."
            )
            
        except Exception as e:
            slicer.util.errorDisplay(f"Error calculating gonion: {e}")
            import traceback
            traceback.print_exc()

    def findLineIntersection3D(self, p1, p2, p3, p4):
        """
        Find closest point between two 3D lines (handles skew lines).
        
        Returns: (intersection_point, distance_between_lines)
        Returns None if lines are parallel.
        """
        try:
            # Direction vectors
            d1 = p2 - p1
            d2 = p4 - p3
            
            # Normalize
            d1_mag = np.linalg.norm(d1)
            d2_mag = np.linalg.norm(d2)
            
            if d1_mag < 1e-6 or d2_mag < 1e-6:
                print("Error: One of the lines has zero length")
                return None
            
            d1 = d1 / d1_mag
            d2 = d2 / d2_mag
            
            # Vector between line starting points
            w = p1 - p3
            
            a = np.dot(d1, d1)
            b = np.dot(d1, d2)
            c = np.dot(d2, d2)
            d = np.dot(d1, w)
            e = np.dot(d2, w)
            
            denom = a * c - b * b
            
            if abs(denom) < 1e-6:
                print("Warning: Lines are parallel")
                return None
            
            # Parameters for closest points
            t1 = (b * e - c * d) / denom
            t2 = (a * e - b * d) / denom
            
            # Closest points on each line
            closest1 = p1 + t1 * d1
            closest2 = p3 + t2 * d2
            
            # Calculate distance between the lines
            distance = np.linalg.norm(closest1 - closest2)
            
            # Return midpoint as intersection approximation + distance
            intersection = (closest1 + closest2) / 2
            
            return (intersection, distance)
            
        except Exception as e:
            print(f"Error in line intersection: {e}")
            return None

    def startDrawingCurve(self, curveType):
        """Start interactive closed curve drawing for orbit."""
        try:
            curveName = f"orbit_curve_{curveType}"
            
            # Create or get existing curve
            if curveType in self.orbitCurves:
                curveNode = self.orbitCurves[curveType]
            else:
                curveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", curveName)
                curveNode.GetDisplayNode().SetSelectedColor(0, 1, 1)  # Cyan
                curveNode.GetDisplayNode().SetLineThickness(0.5)  # Thinner
                self.orbitCurves[curveType] = curveNode
            
            # Clear existing points
            curveNode.RemoveAllControlPoints()
            
            # Set to place mode
            slicer.modules.markups.logic().SetActiveListID(curveNode)
            interactionNode = slicer.app.applicationLogic().GetInteractionNode()
            interactionNode.SetCurrentInteractionMode(interactionNode.Place)
            
            slicer.util.showStatusMessage(f"Draw closed curve around {curveType} orbit", 3000)
            
        except Exception as e:
            slicer.util.errorDisplay(f"Error starting curve drawing: {e}")

    def calculateOrbitalLandmarks(self, side):
        """Calculate mso and mio using vertical bisecting line of orbit."""
        try:
            curveKey = f"orbit{side}"
            
            if curveKey not in self.orbitCurves:
                slicer.util.warningDisplay(f"Please draw orbit curve for side {side} first.")
                return
            
            curveNode = self.orbitCurves[curveKey]
            
            if curveNode.GetNumberOfControlPoints() < 3:
                slicer.util.warningDisplay("Orbit curve must have at least 3 points.")
                return
            
            # Get all curve points
            numPoints = curveNode.GetNumberOfControlPoints()
            points = []
            for i in range(numPoints):
                p = np.zeros(3)
                curveNode.GetNthControlPointPositionWorld(i, p)
                points.append(p)
            points = np.array(points)
            
            # Find centroid
            centroid = np.mean(points, axis=0)
            
            # Find leftmost and rightmost points (X direction in RAS)
            leftmost = points[np.argmax(points[:, 0])]
            rightmost = points[np.argmin(points[:, 0])]
            
            # Vertical bisecting line is at midpoint X coordinate
            midX = (leftmost[0] + rightmost[0]) / 2
            
            # Find superior-most and inferior-most points near this X coordinate
            tolerance = 5.0
            nearMidline = points[np.abs(points[:, 0] - midX) < tolerance]
            
            if len(nearMidline) < 2:
                nearMidline = points
            
            # Superior = highest Z
            mso_pos = nearMidline[np.argmax(nearMidline[:, 2])]
            
            # Inferior = lowest Z
            mio_pos = nearMidline[np.argmin(nearMidline[:, 2])]
            
            # Place landmarks
            msoLabel = f"mso{side}"
            mioLabel = f"mio{side}"
            
            # mso
            mso_idx = -1
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                if self.landmarksNode.GetNthControlPointLabel(i) == msoLabel:
                    mso_idx = i
                    break
            if mso_idx >= 0:
                self.landmarksNode.SetNthControlPointPositionWorld(mso_idx, mso_pos)
            else:
                self.landmarksNode.AddControlPoint(mso_pos, msoLabel)
            
            # mio
            mio_idx = -1
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                if self.landmarksNode.GetNthControlPointLabel(i) == mioLabel:
                    mio_idx = i
                    break
            if mio_idx >= 0:
                self.landmarksNode.SetNthControlPointPositionWorld(mio_idx, mio_pos)
            else:
                self.landmarksNode.AddControlPoint(mio_pos, mioLabel)
            
            # Snap to surface
            if self.surfaceModel:
                self.snapLandmarkToSurface(msoLabel)
                self.snapLandmarkToSurface(mioLabel)
            
            slicer.util.showStatusMessage(f"Placed {msoLabel} and {mioLabel}", 2000)
            self.step3_5StatusLabel.setText(f"Status: {msoLabel} and {mioLabel} calculated and snapped to surface. You can adjust them manually.")
            
        except Exception as e:
            slicer.util.errorDisplay(f"Error calculating orbital landmarks: {e}")
            import traceback
            traceback.print_exc()

    # ==================== PEG GENERATION METHODS ====================

    # ------------------------------------------------------------------
    # NEW PATCH-BASED SURFACE NORMAL METHODS (ported from Threefold ANS)
    # ------------------------------------------------------------------
    def computeSurfaceNormalFromVolumePatch(self, landmarkPos, searchRadius=3.0, boneThreshold=200, volumeCentroid=None):
        """
        Compute a robust surface normal using a patch of bone voxels around the landmark.
        Returns (normal, basePoint) or (None, None) if insufficient points.
        """
        if self.volumeNode is None:
            return None, None

        imageData = self.volumeNode.GetImageData()
        spacing = self.volumeNode.GetSpacing()
        dims = imageData.GetDimensions()

        worldToIJK = vtk.vtkMatrix4x4()
        self.volumeNode.GetRASToIJKMatrix(worldToIJK)
        ijkToWorld = vtk.vtkMatrix4x4()
        self.volumeNode.GetIJKToRASMatrix(ijkToWorld)

        # Convert landmark to IJK
        landmarkIJK = [0, 0, 0, 1]
        worldToIJK.MultiplyPoint([landmarkPos[0], landmarkPos[1], landmarkPos[2], 1], landmarkIJK)
        i0, j0, k0 = int(round(landmarkIJK[0])), int(round(landmarkIJK[1])), int(round(landmarkIJK[2]))

        val_at_mp = imageData.GetScalarComponentAsDouble(i0, j0, k0, 0)

        # If landmark is not in bone, search outward for nearest bone voxel
        if val_at_mp < boneThreshold:
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
                                break
                        if found_bone:
                            break
                    if found_bone:
                        break
                if found_bone:
                    break

        radiusIJK = max(2, int(searchRadius / max(spacing)))
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
                    if val >= boneThreshold:
                        rasPos = [0, 0, 0, 1]
                        ijkToWorld.MultiplyPoint([i, j, k, 1], rasPos)
                        surfacePoints.append(np.array(rasPos[:3]))

        if len(surfacePoints) < 4:
            # Fallback: lower threshold
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

        if len(surfacePoints) < 4:
            return None, None

        points = np.array(surfacePoints)
        baseCenter = np.mean(points, axis=0)

        # PCA to get normal (minimum eigenvector)
        centered = points - baseCenter
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        pca_normal = eigenvectors[:, np.argmin(eigenvalues)]

        # --- FIX: Remove hardcoded anterior bias, orient outward using centroid ---
        if volumeCentroid is not None:
            radial_dir = landmarkPos - volumeCentroid
            if np.linalg.norm(radial_dir) > 1e-6:
                radial_dir = radial_dir / np.linalg.norm(radial_dir)
                if np.dot(pca_normal, radial_dir) < 0:
                    pca_normal = -pca_normal
        else:
            # Fallback orientation if no centroid: use anterior
            anterior = np.array([0.0, 1.0, 0.0])
            if np.dot(pca_normal, anterior) < 0:
                pca_normal = -pca_normal

        return pca_normal, baseCenter

    def computeGradientNormal(self, landmarkPos, sampleRadius=3.0, volumeCentroid=None):
        """
        Fallback method: compute normal from image gradient.
        """
        if self.volumeNode is None:
            return None

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
            # Clamp to volume bounds
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
        normal = -grad / mag   # gradient points from low to high; we want outward

        # --- FIX: Remove anterior blending, orient outward using centroid ---
        if volumeCentroid is not None:
            radial_dir = landmarkPos - volumeCentroid
            if np.linalg.norm(radial_dir) > 1e-6:
                radial_dir = radial_dir / np.linalg.norm(radial_dir)
                if np.dot(normal, radial_dir) < 0:
                    normal = -normal
        else:
            # Fallback orientation if no centroid: use anterior
            anterior = np.array([0.0, 1.0, 0.0])
            if np.dot(normal, anterior) < 0:
                normal = -normal

        return normal

    # ------------------------------------------------------------------
    # Override the original findSurfaceNormalFromCT
    # ------------------------------------------------------------------
    def findSurfaceNormalFromCT(self, landmarkPos, boneThresholdMin, boneThresholdMax, sampleRadius, volumeCentroid):
        """
        Wrapper: first try patch-based method, then gradient, then radial fallback.
        """
        # Patch method
        normal, basePoint = self.computeSurfaceNormalFromVolumePatch(
            landmarkPos, searchRadius=sampleRadius, boneThreshold=boneThresholdMin, volumeCentroid=volumeCentroid
        )
        if normal is not None:
            return normal

        # Gradient fallback
        normal = self.computeGradientNormal(landmarkPos, sampleRadius=sampleRadius, volumeCentroid=volumeCentroid)
        if normal is not None:
            return normal

        # Ultimate fallback: radial from centroid
        radial = landmarkPos - volumeCentroid
        if np.linalg.norm(radial) < 0.001:
            return np.array([0.0, 1.0, 0.0])  # anterior
        return radial / np.linalg.norm(radial)

    # ------------------------------------------------------------------
    # The rest remains unchanged (generatePegsFromVolume, generatePegsFromModel, etc.)
    # ------------------------------------------------------------------

    def onGeneratePegs(self):
        """Generate pegs - routes to model or volume method based on mode."""
        if not self.landmarksNode:
            slicer.util.warningDisplay("Please load landmarks first (Step 3).")
            return
        
        # WORKAROUND for selectors
        if not self.useVolumeMode and not self.surfaceModel:
            currentModel = self.surfaceModelSelector.currentNode()
            if currentModel:
                self.surfaceModel = currentModel
                self.step2StatusLabel.setText(f"Status: Using '{self.surfaceModel.GetName()}' as surface model.")
        
        if self.useVolumeMode and not self.volumeNode:
            currentVolume = self.volumeSelector.currentNode()
            if currentVolume:
                self.volumeNode = currentVolume
                self.step2StatusLabel.setText(f"Status: Using '{self.volumeNode.GetName()}' as CT volume.")
        
        if self.useVolumeMode:
            if not self.volumeNode:
                slicer.util.warningDisplay("Please select a CT volume first (Step 2).")
                return
            self.generatePegsFromVolume()
        else:
            if not self.surfaceModel:
                slicer.util.warningDisplay("Please select a surface model first (Step 2).")
                return
            self.generatePegsFromModel()

    def getAnatomicalPegDirection(self, label, landmarkPos, surfaceNormal, centroid, base_weight=0.8):
        """
        Get anatomically correct peg direction based on landmark type.
        
        Parameters:
        - base_weight: 0.0 to 1.0. 1.0 = purely surface normal, 0.0 = purely anatomical.
                       Defaults to 0.8 (80% perpendicular, 20% anatomical).
        """
        
        # Calculate basic directional components
        radialDir = landmarkPos - centroid
        radialDir = radialDir / np.linalg.norm(radialDir)
        
        # Anatomical axes (RAS coordinate system)
        anteriorDir = np.array([0, 1, 0])
        posteriorDir = np.array([0, -1, 0])
        superiorDir = np.array([0, 0, 1])
        inferiorDir = np.array([0, 0, -1])
        rightDir = np.array([1, 0, 0])   # +X is patient's Right
        leftDir = np.array([-1, 0, 0])   # -X is patient's Left
        
        # Helper function to blend anatomical direction with surface normal
        def blend(anatomical, normal, weight):
            direction = (weight * normal) + ((1.0 - weight) * anatomical)
            norm = np.linalg.norm(direction)
            if norm < 1e-6:
                return anatomical / np.linalg.norm(anatomical)
            return direction / norm

        # ========== MIDLINE LANDMARKS ==========
        
        if label == 'v':
            # Vertex: Anatomically superior (up). Surface normal is highly reliable here.
            # Use a minimum weight of 0.9 to ensure it always points straight up.
            return blend(superiorDir, surfaceNormal, max(base_weight, 0.9))
        
        if label == 'op':
            # Opisthocranion: Anatomically posterior (back).
            return blend(posteriorDir, surfaceNormal, base_weight)
        
        if label == 'g':
            return blend(0.7 * anteriorDir + 0.3 * superiorDir, surfaceNormal, base_weight)
        
        if label == 'n':
            return blend(anteriorDir, surfaceNormal, max(base_weight, 0.7))
        
        if label == 'mn':
            return blend(anteriorDir, surfaceNormal, max(base_weight, 0.7))
        
        if label == 'rhi':
            return blend(0.8 * anteriorDir + 0.2 * inferiorDir, surfaceNormal, base_weight)
        
        if label == 'ss':
            return blend(0.7 * anteriorDir + 0.3 * inferiorDir, surfaceNormal, base_weight)
        
        if label == 'mp':
            # mp is on the upper lip, surface normal is highly reliable here
            return blend(anteriorDir, surfaceNormal, max(base_weight, 0.8)) 
            
        if label == 'pr':
            return blend(anteriorDir, surfaceNormal, base_weight)
        
        if label == 'id':
            return blend(0.7 * anteriorDir + 0.3 * inferiorDir, surfaceNormal, base_weight)
        
        if label == 'sm':
            return blend(anteriorDir, surfaceNormal, base_weight)
        
        if label == 'pg':
            return blend(anteriorDir, surfaceNormal, base_weight)
        
        if label == 'gn':
            return blend(0.6 * anteriorDir + 0.4 * inferiorDir, surfaceNormal, base_weight)
        
        if label == 'me':
            return blend(0.3 * anteriorDir + 0.7 * inferiorDir, surfaceNormal, base_weight)
        
        # ========== BILATERAL LANDMARKS ==========
        
        isLeft = label.endswith('L')
        isRight = label.endswith('R')
        lateralDir = leftDir if isLeft else rightDir
        
        if 'mso' in label.lower():
            return blend(0.7 * superiorDir + 0.3 * lateralDir, surfaceNormal, base_weight)
        
        if 'mio' in label.lower():
            return blend(0.6 * anteriorDir + 0.4 * lateralDir, surfaceNormal, base_weight)
        
        if label.startswith('ac'):
            return blend(0.6 * lateralDir + 0.4 * anteriorDir, surfaceNormal, base_weight)
        
        if label.startswith('zy'):
            return blend(0.8 * lateralDir + 0.2 * posteriorDir, surfaceNormal, base_weight)
        
        if label.startswith('sC'):
            return blend(0.5 * anteriorDir + 0.5 * lateralDir, surfaceNormal, base_weight)
        
        if label.startswith('iC'):
            return blend(0.5 * anteriorDir + 0.3 * lateralDir + 0.2 * inferiorDir, surfaceNormal, base_weight)
        
        if 'ecm2' in label.lower():
            return blend(0.7 * lateralDir + 0.3 * posteriorDir, surfaceNormal, base_weight)
        
        if label.startswith('go'):
            return blend(0.5 * lateralDir + 0.3 * inferiorDir + 0.2 * posteriorDir, surfaceNormal, base_weight)
            
        if label.startswith('mmb'):
            direction = 0.5 * lateralDir + 0.2 * inferiorDir + 0.3 * anteriorDir
            return blend(direction, surfaceNormal, max(base_weight, 0.8)) # heavily rely on surface normal
            
        if label.startswith('mr'):
            return blend(0.6 * lateralDir + 0.4 * posteriorDir, surfaceNormal, base_weight)
        
        # ========== FALLBACK ==========
        # If an unknown landmark is encountered, use a combination of radial and surface normal
        return blend(radialDir, surfaceNormal, base_weight)

    def generatePegsFromModel(self):
        """Generate pegs with anatomical orientation from model."""
        self.step4StatusLabel.setText("Status: Generating pegs from model...")
        slicer.app.processEvents()
        
        try:
            self.clearPegs()
            
            polyData = self.surfaceModel.GetPolyData()
            locator = vtk.vtkPointLocator()
            locator.setDataSet(polyData)
            locator.BuildLocator()
            
            normalsFilter = vtk.vtkPolyDataNormals()
            normalsFilter.SetInputData(polyData)
            normalsFilter.ComputePointNormalsOn()
            normalsFilter.Update()
            polyDataWithNormals = normalsFilter.GetOutput()
            
            numLandmarks = self.landmarksNode.GetNumberOfControlPoints()
            pegRadius = self.pegRadiusSpinBox.value
            showSDEndpoints = self.showSDEndpointsCheckbox.checked
            
            # Get weight from GUI slider
            weight = self.perpendicularityWeightSlider.value / 100.0
            
            pegsCreated = 0
            
            # Create organized folder structure
            self.meanSoftTissueLandmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Mean_SoftTissue_Landmarks")
            self.meanSoftTissueLandmarks.GetDisplayNode().SetSelectedColor(1.0, 0.6, 0.2)
            self.meanSoftTissueLandmarks.GetDisplayNode().SetGlyphScale(2.5)
            
            if showSDEndpoints:
                self.minSDSoftTissueLandmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "MinSD_SoftTissue_Landmarks")
                self.minSDSoftTissueLandmarks.GetDisplayNode().SetSelectedColor(0.3, 0.6, 1.0)
                self.minSDSoftTissueLandmarks.GetDisplayNode().SetGlyphScale(2.0)
                
                self.maxSDSoftTissueLandmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "MaxSD_SoftTissue_Landmarks")
                self.maxSDSoftTissueLandmarks.GetDisplayNode().SetSelectedColor(1.0, 0.3, 0.3)
                self.maxSDSoftTissueLandmarks.GetDisplayNode().SetGlyphScale(2.0)
            
            # Get model centroid
            centerOfMassFilter = vtk.vtkCenterOfMass()
            centerOfMassFilter.SetInputData(polyData)
            centerOfMassFilter.Update()
            centroid = np.array(centerOfMassFilter.GetCenter())
            
            for i in range(numLandmarks):
                landmarkPos = np.zeros(3)
                self.landmarksNode.GetNthControlPointPositionWorld(i, landmarkPos)
                label = self.landmarksNode.GetNthControlPointLabel(i)
                
                if label not in self.defaultFSTT:
                    print(f"Warning: No FSTT data for landmark '{label}', skipping...")
                    continue
                
                mean = self.defaultFSTT[label]["mean"]
                sd = self.defaultFSTT[label]["sd"]
                
                # Find surface normal
                closestPointId = locator.FindClosestPoint(landmarkPos)
                surfaceNormal = np.array(polyDataWithNormals.GetPointData().GetNormals().GetTuple(closestPointId))
                
                normalMagnitude = np.linalg.norm(surfaceNormal)
                if normalMagnitude < 0.0001:
                    print(f"Warning: Zero normal at landmark '{label}', skipping...")
                    continue
                    
                surfaceNormal = surfaceNormal / normalMagnitude
                
                # Get anatomically correct peg direction with dynamic weight
                pegDirection = self.getAnatomicalPegDirection(label, landmarkPos, surfaceNormal, centroid, base_weight=weight)
                
                # Ensure direction points outward (not into bone)
                dotProduct = np.dot(pegDirection, surfaceNormal)
                if dotProduct < -0.2:
                    pegDirection = -pegDirection
                    dotProduct = np.dot(pegDirection, surfaceNormal)
                    print(f"Flipped peg direction for {label}")
                
                if dotProduct < 0:
                    print(f"Warning: Using surface normal fallback for {label}")
                    pegDirection = surfaceNormal
                
                startPoint = landmarkPos
                
                # Generate pegs
                pegLengths = {'Mean': mean}
                if showSDEndpoints:
                    pegLengths['-SD'] = mean - sd
                    pegLengths['+SD'] = mean + sd
                
                for suffix, pegLength in pegLengths.items():
                    endPoint = landmarkPos + pegDirection * pegLength
                    
                    if suffix == 'Mean':
                        color = (1.0, 0.6, 0.2)
                        opacity = 0.85
                        pegName = f"peg_{label}_Mean"
                        landmarkList = self.meanSoftTissueLandmarks
                    elif suffix == '-SD':
                        color = (0.3, 0.6, 1.0)
                        opacity = 0.5
                        pegName = f"peg_{label}_MinSD"
                        landmarkList = self.minSDSoftTissueLandmarks
                    elif suffix == '+SD':
                        color = (1.0, 0.3, 0.3)
                        opacity = 0.5
                        pegName = f"peg_{label}_MaxSD"
                        landmarkList = self.maxSDSoftTissueLandmarks
                    
                    pegModel = self.createCylinder(startPoint, endPoint, pegRadius, pegName, color, opacity)
                    
                    if pegModel:
                        softTissueLabel = f"{label}'"
                        landmarkList.AddControlPoint(endPoint, softTissueLabel)
                        
                        if suffix == 'Mean':
                            self.pegModels[label] = pegModel
                            
                            pegLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"peg_line_{label}")
                            pegLine.AddControlPoint(startPoint, label)
                            pegLine.AddControlPoint(endPoint, f"{label}'_{suffix}")
                            pegLine.GetDisplayNode().SetSelectedColor(0, 1, 0)
                            pegLine.GetDisplayNode().SetLineThickness(0.5)
                            pegLine.GetDisplayNode().SetVisibility(False)
                            self.pegLines[label] = pegLine
                            
                            self.pegLengthData[label] = pegLength
                            pegsCreated += 1
                        else:
                            sdLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"peg_line_{label}_{suffix}")
                            sdLine.AddControlPoint(startPoint, label)
                            sdLine.AddControlPoint(endPoint, f"{label}'_{suffix}")
                            sdLine.GetDisplayNode().SetSelectedColor(*color)
                            sdLine.GetDisplayNode().SetLineThickness(0.3)
                            sdLine.GetDisplayNode().SetVisibility(False)
            
            # Organize into folders
            self.organizePegsIntoFolders(showSDEndpoints)
            
            self.visibilityControlsWidget.setVisible(True)
            self.step4StatusLabel.setText(f"Status: Successfully generated {pegsCreated} pegs!")
            slicer.util.showStatusMessage("Pegs generated!", 3000)
            
        except Exception as e:
            self.step4StatusLabel.setText(f"Status: Error generating pegs! {e}")
            slicer.util.errorDisplay(f"Failed to generate pegs: {e}")
            import traceback
            traceback.print_exc()

    def generatePegsFromVolume(self):
        """Generate pegs from CT volume with anatomical orientation."""
        self.step4StatusLabel.setText("Status: Generating pegs from CT volume...")
        slicer.app.processEvents()
        
        try:
            self.clearPegs()
            
            numLandmarks = self.landmarksNode.GetNumberOfControlPoints()
            pegRadius = self.pegRadiusSpinBox.value
            boneThresholdMin = self.boneThresholdMinSpinBox.value
            boneThresholdMax = self.boneThresholdMaxSpinBox.value
            normalSampleRadius = self.normalSampleRadiusSpinBox.value
            showSDEndpoints = self.showSDEndpointsCheckbox.checked
            
            # Get weight from GUI slider
            weight = self.perpendicularityWeightSlider.value / 100.0
            
            pegsCreated = 0
            
            # Create organized folder structure
            self.meanSoftTissueLandmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Mean_SoftTissue_Landmarks")
            self.meanSoftTissueLandmarks.GetDisplayNode().SetSelectedColor(1.0, 0.6, 0.2)
            self.meanSoftTissueLandmarks.GetDisplayNode().SetGlyphScale(2.5)
            
            if showSDEndpoints:
                self.minSDSoftTissueLandmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "MinSD_SoftTissue_Landmarks")
                self.minSDSoftTissueLandmarks.GetDisplayNode().SetSelectedColor(0.3, 0.6, 1.0)
                self.minSDSoftTissueLandmarks.GetDisplayNode().SetGlyphScale(2.0)
                
                self.maxSDSoftTissueLandmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "MaxSD_SoftTissue_Landmarks")
                self.maxSDSoftTissueLandmarks.GetDisplayNode().SetSelectedColor(1.0, 0.3, 0.3)
                self.maxSDSoftTissueLandmarks.GetDisplayNode().SetGlyphScale(2.0)
            
            # Get volume center
            imageData = self.volumeNode.GetImageData()
            dims = imageData.GetDimensions()
            IJKToWorld = vtk.vtkMatrix4x4()
            self.volumeNode.GetIJKToRASMatrix(IJKToWorld)
            centerIJK = [dims[0]/2, dims[1]/2, dims[2]/2, 1]
            centerWorld = [0, 0, 0, 1]
            IJKToWorld.MultiplyPoint(centerIJK, centerWorld)
            volumeCentroid = np.array([centerWorld[0], centerWorld[1], centerWorld[2]])
            
            for i in range(numLandmarks):
                landmarkPos = np.zeros(3)
                self.landmarksNode.GetNthControlPointPositionWorld(i, landmarkPos)
                label = self.landmarksNode.GetNthControlPointLabel(i)
                
                if label not in self.defaultFSTT:
                    print(f"Warning: No FSTT data for landmark '{label}', skipping...")
                    continue
                
                mean = self.defaultFSTT[label]["mean"]
                sd = self.defaultFSTT[label]["sd"]
                
                # Find surface normal from CT using new robust method
                surfaceNormal = self.findSurfaceNormalFromCT(
                    landmarkPos, boneThresholdMin, boneThresholdMax, normalSampleRadius, volumeCentroid
                )
                
                if surfaceNormal is None:
                    print(f"Warning: Could not find surface normal for landmark '{label}', skipping...")
                    continue
                
                # Get anatomically correct peg direction with dynamic weight
                pegDirection = self.getAnatomicalPegDirection(label, landmarkPos, surfaceNormal, volumeCentroid, base_weight=weight)
                
                # Ensure direction points outward
                dotProduct = np.dot(pegDirection, surfaceNormal)
                if dotProduct < -0.2:
                    pegDirection = -pegDirection
                    dotProduct = np.dot(pegDirection, surfaceNormal)
                    print(f"Flipped peg direction for {label}")
                
                if dotProduct < 0:
                    print(f"Warning: Using surface normal fallback for {label}")
                    pegDirection = surfaceNormal
                
                # Generate pegs
                pegLengths = {'Mean': mean}
                if showSDEndpoints:
                    pegLengths['-SD'] = mean - sd
                    pegLengths['+SD'] = mean + sd
                
                for suffix, pegLength in pegLengths.items():
                    startPoint = landmarkPos
                    endPoint = landmarkPos + pegDirection * pegLength
                    
                    if suffix == 'Mean':
                        color = (1.0, 0.6, 0.2)
                        opacity = 0.85
                        pegName = f"peg_{label}_Mean"
                        landmarkList = self.meanSoftTissueLandmarks
                    elif suffix == '-SD':
                        color = (0.3, 0.6, 1.0)
                        opacity = 0.5
                        pegName = f"peg_{label}_MinSD"
                        landmarkList = self.minSDSoftTissueLandmarks
                    elif suffix == '+SD':
                        color = (1.0, 0.3, 0.3)
                        opacity = 0.5
                        pegName = f"peg_{label}_MaxSD"
                        landmarkList = self.maxSDSoftTissueLandmarks
                    
                    pegModel = self.createCylinder(startPoint, endPoint, pegRadius, pegName, color, opacity)
                    
                    if pegModel:
                        softTissueLabel = f"{label}'"
                        landmarkList.AddControlPoint(endPoint, softTissueLabel)
                        
                        if suffix == 'Mean':
                            self.pegModels[label] = pegModel
                            
                            pegLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"peg_line_{label}")
                            pegLine.AddControlPoint(startPoint, label)
                            pegLine.AddControlPoint(endPoint, f"{label}'_{suffix}")
                            pegLine.GetDisplayNode().SetSelectedColor(0, 1, 0)
                            pegLine.GetDisplayNode().SetLineThickness(0.5)
                            pegLine.GetDisplayNode().SetVisibility(False)
                            self.pegLines[label] = pegLine
                            
                            self.pegLengthData[label] = pegLength
                            pegsCreated += 1
                        else:
                            sdLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"peg_line_{label}_{suffix}")
                            sdLine.AddControlPoint(startPoint, label)
                            sdLine.AddControlPoint(endPoint, f"{label}'_{suffix}")
                            sdLine.GetDisplayNode().SetSelectedColor(*color)
                            sdLine.GetDisplayNode().SetLineThickness(0.3)
                            sdLine.GetDisplayNode().SetVisibility(False)
            
            # Organize into folders
            self.organizePegsIntoFolders(showSDEndpoints)
            
            self.visibilityControlsWidget.setVisible(True)
            self.step4StatusLabel.setText(f"Status: Successfully generated {pegsCreated} pegs from CT!")
            slicer.util.showStatusMessage("Pegs generated from CT!", 3000)
            
        except Exception as e:
            self.step4StatusLabel.setText(f"Status: Error generating pegs! {e}")
            slicer.util.errorDisplay(f"Failed to generate pegs: {e}")
            import traceback
            traceback.print_exc()

    def organizePegsIntoFolders(self, showSDEndpoints):
        """Organize pegs into folder hierarchy"""
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        mainFolderID = shNode.CreateFolderItem(shNode.GetSceneItemID(), "FSTT_Pegs_And_Landmarks")
        
        cylindersFolderID = shNode.CreateFolderItem(mainFolderID, "Cylinders")
        linesFolderID = shNode.CreateFolderItem(mainFolderID, "FSTT_Lines")
        landmarksFolderID = shNode.CreateFolderItem(mainFolderID, "Soft_Tissue_Landmarks")
        
        # Organize cylinders
        meanCylFolderID = shNode.CreateFolderItem(cylindersFolderID, "Mean_Cylinders")
        for label, pegModel in self.pegModels.items():
            itemID = shNode.GetItemByDataNode(pegModel)
            shNode.SetItemParent(itemID, meanCylFolderID)
        
        if showSDEndpoints:
            minSDCylFolderID = shNode.CreateFolderItem(cylindersFolderID, "MinSD_Cylinders")
            maxSDCylFolderID = shNode.CreateFolderItem(cylindersFolderID, "MaxSD_Cylinders")
            
            allNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
            for i in range(allNodes.GetNumberOfItems()):
                node = allNodes.GetItemAsObject(i)
                nodeName = node.GetName()
                if "MinSD" in nodeName:
                    itemID = shNode.GetItemByDataNode(node)
                    shNode.SetItemParent(itemID, minSDCylFolderID)
                elif "MaxSD" in nodeName:
                    itemID = shNode.GetItemByDataNode(node)
                    shNode.SetItemParent(itemID, maxSDCylFolderID)
        
        # Organize lines
        meanLinesFolderID = shNode.CreateFolderItem(linesFolderID, "Mean_Lines")
        for label, pegLine in self.pegLines.items():
            itemID = shNode.GetItemByDataNode(pegLine)
            shNode.SetItemParent(itemID, meanLinesFolderID)
            pegLine.GetDisplayNode().SetVisibility(False)
        
        if showSDEndpoints:
            minSDLinesFolderID = shNode.CreateFolderItem(linesFolderID, "MinSD_Lines")
            maxSDLinesFolderID = shNode.CreateFolderItem(linesFolderID, "MaxSD_Lines")
            
            allNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
            for i in range(allNodes.GetNumberOfItems()):
                node = allNodes.GetItemAsObject(i)
                nodeName = node.GetName()
                if "peg_line_" in nodeName:
                    if "-SD" in nodeName:
                        itemID = shNode.GetItemByDataNode(node)
                        shNode.SetItemParent(itemID, minSDLinesFolderID)
                        node.GetDisplayNode().SetVisibility(False)
                    elif "+SD" in nodeName:
                        itemID = shNode.GetItemByDataNode(node)
                        shNode.SetItemParent(itemID, maxSDLinesFolderID)
                        node.GetDisplayNode().SetVisibility(False)
        
        # Organize soft tissue landmarks
        meanLandmarksItemID = shNode.GetItemByDataNode(self.meanSoftTissueLandmarks)
        shNode.SetItemParent(meanLandmarksItemID, landmarksFolderID)
        self.meanSoftTissueLandmarks.GetDisplayNode().SetVisibility(True)
        
        if showSDEndpoints:
            minSDLandmarksItemID = shNode.GetItemByDataNode(self.minSDSoftTissueLandmarks)
            shNode.SetItemParent(minSDLandmarksItemID, landmarksFolderID)
            self.minSDSoftTissueLandmarks.GetDisplayNode().SetVisibility(False)
            
            maxSDLandmarksItemID = shNode.GetItemByDataNode(self.maxSDSoftTissueLandmarks)
            shNode.SetItemParent(maxSDLandmarksItemID, landmarksFolderID)
            self.maxSDSoftTissueLandmarks.GetDisplayNode().SetVisibility(False)

    def createCylinder(self, startPoint, endPoint, radius, label, color=(1.0, 0.6, 0.2), opacity=0.85):
        """Create a cylinder model with custom color and opacity."""
        direction = endPoint - startPoint
        length = np.linalg.norm(direction)
        
        if length < 0.0001:
            print(f"Warning: Zero-length peg for '{label}'")
            return None
            
        direction = direction / length
        
        cylinderSource = vtk.vtkCylinderSource()
        cylinderSource.SetRadius(radius)
        cylinderSource.SetHeight(length)
        cylinderSource.SetResolution(20)
        cylinderSource.CappingOn()
        cylinderSource.Update()
        
        cylinderAxis = np.array([0, 1, 0])
        rotationAxis = np.cross(cylinderAxis, direction)
        rotationAxisMagnitude = np.linalg.norm(rotationAxis)
        
        transform = vtk.vtkTransform()
        transform.Translate(startPoint)
        
        if rotationAxisMagnitude > 0.0001:
            rotationAxis = rotationAxis / rotationAxisMagnitude
            rotationAngle = np.arccos(np.clip(np.dot(cylinderAxis, direction), -1.0, 1.0))
            transform.RotateWXYZ(np.degrees(rotationAngle), rotationAxis[0], rotationAxis[1], rotationAxis[2])
        elif np.dot(cylinderAxis, direction) < 0:
            transform.RotateWXYZ(180, 1, 0, 0)
        
        transform.Translate(0, length / 2, 0)
        
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(cylinderSource.GetOutputPort())
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        
        modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", label)
        modelNode.SetAndObservePolyData(transformFilter.GetOutput())
        
        if not modelNode.GetDisplayNode():
            modelNode.CreateDefaultDisplayNodes()
        displayNode = modelNode.GetDisplayNode()
        displayNode.SetColor(*color)
        displayNode.SetOpacity(opacity)
        displayNode.SetVisibility(True)
        
        return modelNode

    def clearPegs(self):
        """Remove all existing peg models, lines, and landmark lists."""
        for model in self.pegModels.values():
            if model:
                slicer.mrmlScene.RemoveNode(model)
        for line in self.pegLines.values():
            if line:
                slicer.mrmlScene.RemoveNode(line)
        
        if hasattr(self, 'meanSoftTissueLandmarks') and self.meanSoftTissueLandmarks:
            slicer.mrmlScene.RemoveNode(self.meanSoftTissueLandmarks)
        if hasattr(self, 'minSDSoftTissueLandmarks') and self.minSDSoftTissueLandmarks:
            slicer.mrmlScene.RemoveNode(self.minSDSoftTissueLandmarks)
        if hasattr(self, 'maxSDSoftTissueLandmarks') and self.maxSDSoftTissueLandmarks:
            slicer.mrmlScene.RemoveNode(self.maxSDSoftTissueLandmarks)
        
        allNodes = slicer.mrmlScene.GetNodes()
        nodesToRemove = []
        for i in range(allNodes.GetNumberOfItems()):
            node = allNodes.GetItemAsObject(i)
            nodeName = node.GetName() if node else ""
            if "peg_" in nodeName and ("MinSD" in nodeName or "MaxSD" in nodeName):
                nodesToRemove.append(node)
            elif "peg_line_" in nodeName and ("-SD" in nodeName or "+SD" in nodeName):
                nodesToRemove.append(node)
        
        for node in nodesToRemove:
            slicer.mrmlScene.RemoveNode(node)
        
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        mainFolderID = shNode.GetItemByName("FSTT_Pegs_And_Landmarks")
        if mainFolderID:
            shNode.RemoveItem(mainFolderID)
        
        self.pegModels = {}
        self.pegLines = {}
        self.pegLengthData = {}

    # ==================== ADJUST PEGS METHODS ====================

    def createLandmarkSlider(self, label, parentLayout):
        """Create a slider row for a single landmark."""
        if label not in self.defaultFSTT:
            return
        
        mean = self.defaultFSTT[label]["mean"]
        sd = self.defaultFSTT[label]["sd"]
        minVal = mean - sd
        maxVal = mean + sd
        
        landmarkWidget = qt.QWidget()
        landmarkLayout = qt.QHBoxLayout(landmarkWidget)
        landmarkLayout.setContentsMargins(0, 5, 0, 5)
        landmarkLayout.setSpacing(10)
        
        nameLabel = qt.QLabel(f"<b>{label}</b>")
        nameLabel.setFixedWidth(100)
        nameLabel.setAlignment(qt.Qt.AlignLeft | qt.Qt.AlignVCenter)
        landmarkLayout.addWidget(nameLabel)
        
        minLabel = qt.QLabel(f"{minVal:.1f}")
        minLabel.setFixedWidth(40)
        minLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        minLabel.setStyleSheet("color: #666; font-size: 10px;")
        landmarkLayout.addWidget(minLabel)
        
        slider = qt.QSlider(qt.Qt.Horizontal)
        slider.setRange(int(minVal * 10), int(maxVal * 10))
        slider.setValue(int(mean * 10))
        slider.setMinimumWidth(200)
        slider.valueChanged.connect(lambda v, lbl=label: self.onSliderChanged(lbl, v))
        
        self.pegSliders[label] = slider
        landmarkLayout.addWidget(slider)
        
        maxLabel = qt.QLabel(f"{maxVal:.1f}")
        maxLabel.setFixedWidth(40)
        maxLabel.setAlignment(qt.Qt.AlignLeft | qt.Qt.AlignVCenter)
        maxLabel.setStyleSheet("color: #666; font-size: 10px;")
        landmarkLayout.addWidget(maxLabel)
        
        spinBox = qt.QDoubleSpinBox()
        spinBox.setRange(minVal, maxVal)
        spinBox.setValue(mean)
        spinBox.setSuffix(" mm")
        spinBox.setDecimals(1)
        spinBox.setSingleStep(0.1)
        spinBox.setFixedWidth(80)
        spinBox.valueChanged.connect(lambda v, lbl=label: self.onSpinBoxChanged(lbl, v))
        
        self.pegSpinBoxes[label] = spinBox
        landmarkLayout.addWidget(spinBox)
        
        rangeLabel = qt.QLabel(f"[{minVal:.1f} - {maxVal:.1f}]")
        rangeLabel.setStyleSheet("color: #888; font-size: 10px;")
        rangeLabel.setFixedWidth(80)
        landmarkLayout.addWidget(rangeLabel)
        
        self.pegLabels[label] = {
            'minLabel': minLabel,
            'maxLabel': maxLabel,
            'rangeLabel': rangeLabel
        }
        
        parentLayout.addWidget(landmarkWidget)

    def onSliderChanged(self, label, value):
        """Update spinbox when slider changes."""
        length = value / 10.0
        if label in self.pegSpinBoxes:
            self.pegSpinBoxes[label].blockSignals(True)
            self.pegSpinBoxes[label].setValue(length)
            self.pegSpinBoxes[label].blockSignals(False)

    def onSpinBoxChanged(self, label, value):
        """Update slider when spinbox changes."""
        if label in self.pegSliders:
            self.pegSliders[label].blockSignals(True)
            self.pegSliders[label].setValue(int(value * 10))
            self.pegSliders[label].blockSignals(False)

    def onResetAllToMean(self):
        """Reset all sliders to mean values."""
        for label in self.pegSliders.keys():
            if label in self.defaultFSTT:
                mean = self.defaultFSTT[label]["mean"]
                self.pegSliders[label].setValue(int(mean * 10))
                self.pegSpinBoxes[label].setValue(mean)
        
        self.step5StatusLabel.setText("Status: All values reset to mean. Click 'Update' to apply.")

    def onSetAllToMin(self):
        """Set all sliders to minimum (mean - SD)."""
        for label in self.pegSliders.keys():
            if label in self.defaultFSTT:
                mean = self.defaultFSTT[label]["mean"]
                sd = self.defaultFSTT[label]["sd"]
                minVal = mean - sd
                self.pegSliders[label].setValue(int(minVal * 10))
                self.pegSpinBoxes[label].setValue(minVal)
        
        self.step5StatusLabel.setText("Status: All values set to Mean - SD. Click 'Update' to apply.")

    def onSetAllToMax(self):
        """Set all sliders to maximum (mean + SD)."""
        for label in self.pegSliders.keys():
            if label in self.defaultFSTT:
                mean = self.defaultFSTT[label]["mean"]
                sd = self.defaultFSTT[label]["sd"]
                maxVal = mean + sd
                self.pegSliders[label].setValue(int(maxVal * 10))
                self.pegSpinBoxes[label].setValue(maxVal)
        
        self.step5StatusLabel.setText("Status: All values set to Mean + SD. Click 'Update' to apply.")

    def onUpdateAllPegs(self):
        """Update all pegs with the current slider values."""
        if not self.pegModels:
            slicer.util.warningDisplay("Please generate pegs first (Step 4).")
            return
        
        self.step5StatusLabel.setText("Status: Updating all pegs...")
        slicer.app.processEvents()
        
        try:
            updatedCount = 0
            
            for label in self.pegSpinBoxes.keys():
                if label not in self.pegModels or label not in self.pegLines:
                    continue
                
                newLength = self.pegSpinBoxes[label].value
                
                pegLine = self.pegLines[label]
                startPoint = np.zeros(3)
                pegLine.GetNthControlPointPositionWorld(0, startPoint)
                
                originalEndPoint = np.zeros(3)
                pegLine.GetNthControlPointPositionWorld(1, originalEndPoint)
                
                direction = originalEndPoint - startPoint
                originalLength = np.linalg.norm(direction)
                
                if originalLength < 0.0001:
                    continue
                
                direction = direction / originalLength
                endPoint = startPoint + direction * newLength
                
                if self.pegModels[label]:
                    slicer.mrmlScene.RemoveNode(self.pegModels[label])
                
                pegRadius = self.pegRadiusSpinBox.value
                color = (1.0, 0.6, 0.2)
                opacity = 0.85
                pegName = f"peg_{label}_Mean"
                
                newPeg = self.createCylinder(startPoint, endPoint, pegRadius, pegName, color, opacity)
                
                if newPeg:
                    self.pegModels[label] = newPeg
                    pegLine.SetNthControlPointPositionWorld(1, endPoint)
                    pegLine.SetNthControlPointLabel(1, f"{label}'_Mean")
                    self.pegLengthData[label] = newLength
                    updatedCount += 1
            
            self.step5StatusLabel.setText(f"Status: Successfully updated {updatedCount} pegs!")
            slicer.util.showStatusMessage(f"Updated {updatedCount} pegs!", 3000)
            
        except Exception as e:
            self.step5StatusLabel.setText(f"Status: Error updating pegs! {e}")
            slicer.util.errorDisplay(f"Failed to update pegs: {e}")
            import traceback
            traceback.print_exc()

    # ==================== VISIBILITY CONTROL ====================

    def setVisibility(self, objectType, category, visible):
        """Control visibility of different object types."""
        try:
            if objectType == "cylinders":
                allNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
                for i in range(allNodes.GetNumberOfItems()):
                    node = allNodes.GetItemAsObject(i)
                    nodeName = node.GetName()
                    
                    if "peg_" not in nodeName:
                        continue
                    
                    shouldChange = False
                    if category == "all":
                        shouldChange = True
                    elif category == "mean":
                        shouldChange = "Mean" in nodeName
                        if visible and ("MinSD" in nodeName or "MaxSD" in nodeName):
                            node.GetDisplayNode().SetVisibility(False)
                            continue
                    elif category == "sd":
                        shouldChange = "MinSD" in nodeName or "MaxSD" in nodeName
                        if visible and "Mean" in nodeName and "MinSD" not in nodeName and "MaxSD" not in nodeName:
                            node.GetDisplayNode().SetVisibility(False)
                            continue
                    elif category == "+sd":
                        shouldChange = "MaxSD" in nodeName
                    elif category == "-sd":
                        shouldChange = "MinSD" in nodeName
                    
                    if shouldChange and node.GetDisplayNode():
                        node.GetDisplayNode().SetVisibility(visible)
            
            elif objectType == "lines":
                allNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
                for i in range(allNodes.GetNumberOfItems()):
                    node = allNodes.GetItemAsObject(i)
                    nodeName = node.GetName()
                    
                    if "peg_line_" not in nodeName:
                        continue
                    
                    shouldChange = False
                    if category == "all":
                        shouldChange = True
                    elif category == "mean":
                        shouldChange = "-SD" not in nodeName and "+SD" not in nodeName
                        if visible and ("-SD" in nodeName or "+SD" in nodeName):
                            node.GetDisplayNode().SetVisibility(False)
                            continue
                    elif category == "sd":
                        shouldChange = "-SD" in nodeName or "+SD" in nodeName
                        if visible and "-SD" not in nodeName and "+SD" not in nodeName:
                            node.GetDisplayNode().SetVisibility(False)
                            continue
                    elif category == "+sd":
                        shouldChange = "+SD" in nodeName
                    elif category == "-sd":
                        shouldChange = "-SD" in nodeName
                    
                    if shouldChange and node.GetDisplayNode():
                        node.GetDisplayNode().SetVisibility(visible)
            
            elif objectType == "landmarks":
                if hasattr(self, 'meanSoftTissueLandmarks') and self.meanSoftTissueLandmarks:
                    if category in ["all", "mean"]:
                        self.meanSoftTissueLandmarks.GetDisplayNode().SetVisibility(visible)
                    elif category == "sd" and visible:
                        self.meanSoftTissueLandmarks.GetDisplayNode().SetVisibility(False)
                
                if hasattr(self, 'minSDSoftTissueLandmarks') and self.minSDSoftTissueLandmarks:
                    if category in ["all", "sd", "-sd"]:
                        self.minSDSoftTissueLandmarks.GetDisplayNode().SetVisibility(visible)
                    elif category == "mean" and visible:
                        self.minSDSoftTissueLandmarks.GetDisplayNode().SetVisibility(False)
                
                if hasattr(self, 'maxSDSoftTissueLandmarks') and self.maxSDSoftTissueLandmarks:
                    if category in ["all", "sd", "+sd"]:
                        self.maxSDSoftTissueLandmarks.GetDisplayNode().SetVisibility(visible)
                    elif category == "mean" and visible:
                        self.maxSDSoftTissueLandmarks.GetDisplayNode().SetVisibility(False)
            
            statusMsg = f"{'Showing' if visible else 'Hiding'} {category} {objectType}"
            slicer.util.showStatusMessage(statusMsg, 2000)
            
        except Exception as e:
            print(f"Error setting visibility: {e}")
            import traceback
            traceback.print_exc()

    # ==================== EXPORT METHODS ====================

    def onExport(self):
        """Export surface and/or pegs to file."""
        outputDir = qt.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not outputDir:
            return
        
        formatIndex = self.exportFormatComboBox.currentIndex
        extensions = [".obj", ".stl", ".ply", ".vtk"]
        extension = extensions[formatIndex]
        
        try:
            if self.exportCombinedCheckbox.checked:
                appendFilter = vtk.vtkAppendPolyData()
                
                if self.exportSurfaceCheckbox.checked and self.surfaceModel:
                    appendFilter.AddInputData(self.surfaceModel.GetPolyData())
                
                if self.exportPegsCheckbox.checked:
                    for pegModel in self.pegModels.values():
                        if pegModel:
                            appendFilter.AddInputData(pegModel.GetPolyData())
                
                appendFilter.Update()
                combinedPolyData = appendFilter.GetOutput()
                
                outputPath = os.path.join(outputDir, f"combined_model{extension}")
                self.savePolyData(combinedPolyData, outputPath, extension)
                slicer.util.showStatusMessage(f"Exported combined model to {outputPath}", 5000)
                
            else:
                if self.exportSurfaceCheckbox.checked and self.surfaceModel:
                    outputPath = os.path.join(outputDir, f"surface_model{extension}")
                    self.savePolyData(self.surfaceModel.GetPolyData(), outputPath, extension)
                
                if self.exportPegsCheckbox.checked:
                    for label, pegModel in self.pegModels.items():
                        if pegModel:
                            outputPath = os.path.join(outputDir, f"peg_{label}{extension}")
                            self.savePolyData(pegModel.GetPolyData(), outputPath, extension)
                
                slicer.util.showStatusMessage(f"Exported models to {outputDir}", 5000)
            
            self.step6StatusLabel.setText(f"Status: Export complete! Files saved to {outputDir}")
            
        except Exception as e:
            slicer.util.errorDisplay(f"Export failed: {e}")

    def savePolyData(self, polyData, filePath, extension):
        """Save polydata to file based on extension."""
        if extension == ".obj":
            writer = vtk.vtkOBJWriter()
        elif extension == ".stl":
            writer = vtk.vtkSTLWriter()
        elif extension == ".ply":
            writer = vtk.vtkPLYWriter()
        elif extension == ".vtk":
            writer = vtk.vtkPolyDataWriter()
        else:
            raise ValueError(f"Unsupported format: {extension}")
        
        writer.SetFileName(filePath)
        writer.SetInputData(polyData)
        writer.Write()

    def onSaveLengths(self):
        """Save peg lengths to JSON file."""
        fileName, _ = qt.QFileDialog.getSaveFileName(self, "Save Peg Lengths", "", "JSON Files (*.json)")
        if fileName:
            try:
                exportData = {}
                for label, length in self.pegLengthData.items():
                    exportData[label] = {
                        "current_length": length,
                        "mean": self.defaultFSTT[label]["mean"],
                        "sd": self.defaultFSTT[label]["sd"]
                    }
                
                with open(fileName, 'w') as f:
                    json.dump(exportData, f, indent=2)
                slicer.util.showStatusMessage(f"Saved peg lengths to {fileName}", 3000)
                self.step6StatusLabel.setText(f"Status: Saved peg lengths to '{os.path.basename(fileName)}'.")
            except Exception as e:
                slicer.util.errorDisplay(f"Failed to save peg lengths: {e}")

    # ==================== NAVIGATION METHODS ====================

    def updateStepUI(self):
        """Update step UI"""
        self.stepStack.setCurrentIndex(self.currentStep)
        
        # Total steps in the stack
        totalSteps = self.stepStack.count  # FIXED: it's a property, not a method
        
        # Update label
        self.stepLabel.setText(f"Step {self.currentStep + 1}/{totalSteps}")
        
        # Enable/disable navigation buttons
        self.prevButton.setEnabled(self.currentStep > 0)
        self.nextButton.setEnabled(self.currentStep < totalSteps - 1)

    def onPrevButtonClicked(self):
        """Navigate to previous step"""
        if self.currentStep > 0:
            self.currentStep -= 1
            self.updateStepUI()

    def onNextButtonClicked(self):
        """Navigate to next step"""
        totalSteps = self.stepStack.count  # FIXED: property, not method
        if self.currentStep < totalSteps - 1:
            self.currentStep += 1
            self.updateStepUI()

    def syncWithScene(self):
        """Sync with existing nodes in the scene"""
        if not self.surfaceModel:
            self.surfaceModel = slicer.util.getFirstNodeByName("Bone")
        
        if not self.croppedVolume:
            allVolumes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
            for vol in allVolumes:
                if "_cropped" in vol.GetName():
                    self.croppedVolume = vol
                    break
        
        if self.croppedVolume and not self.volumeNode:
            self.volumeNode = self.croppedVolume
            if hasattr(self, 'volumeSelectorWelcome'):
                self.volumeSelectorWelcome.setCurrentNode(self.croppedVolume)
        
        possibleNames = ["FSTT Hard tissue", "FSTT_Hard_Tissue", "HardTissueLandmarks"]
        for name in possibleNames:
            existingLandmarks = slicer.util.getFirstNodeByName(name)
            if existingLandmarks:
                self.landmarksNode = existingLandmarks
                break

    def onFinish(self):
        """Close the GUI safely"""
        try:
            self.hide()
            qt.QTimer.singleShot(100, self.deleteLater)
            print("✅ FSTT Pegs GUI closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing window: {e}")

# ==================== ENTRY POINT ====================

# Clean up any existing instances
try:
    existingGUI = slicer.util.findChild(slicer.util.mainWindow(), "SoftTissueThicknessPegsGUI")
    if existingGUI:
        existingGUI.deleteLater()
except:
    pass

# Create and show the GUI
gui = SoftTissueThicknessPegsGUI()
gui.show()

print("✅ FSTT Pegs GUI loaded successfully!")
print("📌 The window will stay on top of other windows")
print("🔧 All original functionality preserved:")
print("   - FHP realignment (optional)")
print("   - ROI cropping (optional)")
print("   - Bone segmentation (optional)")
print("   - Landmark helpers (midpoint, lateral, gonion, orbital)")
print("   - Peg generation (model and volume modes)")
print("   - Peg adjustment with sliders")
print("   - Export to multiple formats")
                
```


</details>



Landmark definitions are established based on the works of Caple and Stephan (2016)[^2], with additional cephalo- and capulometric pairs from Simpson and Stephan (2008)[^4]. Measurement values are from the 2023 published t-tables by Hona and Stephan (2024)[^3]. 

## Hard tissue (Capulometric) Landmarks

| Label | Full Name | Description | Side |
|-------|-----------|-------------|------|
| op | Opisthocranion | Most posterior median point of the occipital bone, instrumentally determined as the greatest chord length from g. Usually above the external occipital protuberance | Midline |
| v | Vertex | Most superior point of the skull | Midline |
| g | Glabella | Most projecting anterior median point on lower edge of the frontal bone, on the brow ridge, in between the superciliary arches and above the nasal root. In adults, glabella usually represents the most anterior point of the frontal bone | Midline |
| n | Nasion | Intersection of the nasofrontal sutures in the median plane | Midline |
| mn | Midnasale | Point on internasal suture midway between nasion and rhinion | Midline |
| rhi | Rhinion | Most rostral (end) point on the internasal suture | Midline |
| ss | Subspinale | The deepest point seen in the profile view below the anterior nasal spine (orthodontic point A) | Midline |
| mp | Midphiltrum | Median point midway between ss and pr | Midline |
| pr | Prosthion | Median point between the central incisors on the anterior most margin of the maxillary alveolar rim | Midline |
| id | Infradentale | Median point at the superior tip of the septum between the mandibular central incisors | Midline |
| sm | Supramentale | Deepest median point in the groove superior to the mental eminence (orthodontic point B) | Midline |
| pg | Pogonion | Most anterior median point on the mental eminence of the mandible | Midline |
| me | Menton | Most inferior median point of the mental symphysis (may not be the inferior point on the mandible as the chin is often clefted on the inferior margin) | Midline |
| gn | Gnathion | Median point halfway between pg and me | Midline |
| msoL | Mid-supraorbital | Point on the anterior aspect of the superior orbital rim, at a line that vertically bisects the left orbit (left) | Left |
| msoR | Mid-supraorbital | Point on the anterior aspect of the superior orbital rim, at a line that vertically bisects the right orbit (right) | Right |
| mioL | Mid-infraorbital | Point on the anterior aspect of the inferior orbital rim, at a line that vertically bisects the orbit (Left) | Left |
| mioR | Mid-infraorbital | Point on the anterior aspect of the inferior orbital rim, at a line that vertically bisects the orbit (Right) | Right |
| acL | Alar curvature point | Hard tissue approximation of soft tissue ac, approximately 5 mm lateral to al (Left) | Left |
| acR | Alar curvature point | Hard tissue approximation of soft tissue ac, approximately 5 mm lateral to al (Right) | Right |
| goL | Gonion | Point on the rounded margin of the angle of the mandible, bisecting two lines one following vertical margin of ramus and one following horizontal margin of corpus of mandible (Left) | Left |
| goR | Gonion | Point on the rounded margin of the angle of the mandible, bisecting two lines one following vertical margin of ramus and one following horizontal margin of corpus of mandible (Right) | Right |
| zyL | Zygion | Instrumentally determined as the most lateral point on the left zygomatic arch zygomatic arch (Left) | Left |
| zyR | Zygion | Instrumentally determined as the most lateral point on the right zygomatic arch | Right |
| sCL | SupraCanine | Point on superior alveolar ridge superior to the crown of the Left maxillary canine | Left |
| sCR | SupraCanine | Point on superior alveolar ridge superior to the crown of the right maxillary canine | Right |
| iCL | InfraCanine | Point on inferior alveolar ridge inferior to the crown of the left mandibular canine | Left |
| iCR | InfraCanine | Point on inferior alveolar ridge inferior to the crown of the right mandibular canine | Right |
| ecm2(s)L | Ectomolare | Most lateral point on the buccal alveolar margin on the maxilla, at the center of the left second molar position. | Left |
| ecm2(s)R | Ectomolare | Most lateral point on the buccal alveolar margin on the maxilla, at the center of the right second molar position. | Right |
| ecm2(i)L | Ectomolare | Most lateral point on the buccal alveolar margin on the mandible, at the center of the left second molar position. | Left |
| ecm2(i)R | Ectomolare | Most lateral point on the buccal alveolar margin on the mandible, at the center of the right second molar position. | Right |
| mrL | Mid-ramus | Midpoint along the shortest antero-posterior depth of the left  ramus, in the masseteric fossa, and usually close to the level of the level of the occlusal plane | Left |
| mrR | Mid-ramus | Midpoint along the shortest antero-posterior depth of the right ramus, in the masseteric fossa, and usually close to the level of the level of the occlusal plane | Right |
| mmbL | MidMandibular Border | Point on the inferior border of the corpus of the left mandible midway between pg and go | Left |
| mmbR | MidMandibular Border | Point on the inferior border of the corpus of the right mandible midway between pg and go | Right |
| alL | Alare | The most lateral point on the nasal ala on the left | Left |
| alR | Alare | The most lateral point on the nasal ala on the right | Right |

This file contains all of the aforementioned landmarks with their definitions. You can download it manually, but the code below allows for not doing that and loading them directly in the Slicer environment.

[FSTT Hard tissue.mrk.json](https://github.com/user-attachments/files/25114784/FSTT.Hard.tissue.mrk.json)

## FSTT Values used in the GUI
| Landmark Pair | Hard tissue landmark | Soft tissue landmark | Total weighted mean (mm) | SD (mm) |
|---------------|---------------------|---------------------|-------------------------|---------|
| op–op' | op | op' | 6 | 2 |
| v–v' | v | v' | 5 | 1.5 |
| g–g' | g | g' | 5.5 | 1 |
| n–se' | n | se' | 6 | 1.5 |
| mn–mn' | mn | mn' | 4.5 | 1.5 |
| rhi–rhi' | rhi | rhi' | 3 | 1 |
| ss–sn' | ss | sn' | 13.5 | 3.5 |
| mp–mp' | mp | mp' | 11.5 | 2.5 |
| pr–ls' | pr | ls' | 12 | 3 |
| id–li' | id | li' | 13.5 | 3 |
| sm–sm' | sm | sm' | 11 | 2 |
| pg–pg' | pg | pg' | 11 | 2.5 |
| gn–gn' | gn | gn' | 7.5 | 2.5 |
| me–me' | me | me' | 7 | 2.5 |
| mso–mso' | msoL | mso'L | 7 | 2 |
|  | msoR | mso'R | 7 | 2 |
| mio–mio' | mioL | mio'L | 6.5 | 3 |
|  | mioR | mio'R | 6.5 | 3 |
| ac–ac' | acL | ac'L | 10 | 3 |
|  | acR | ac'R | 10 | 3 |
| go–go' | goL | go'L | 12.5 | 6 |
|  | goR | go'R | 12.5 | 6 |
| zy–zy' | zyL | zy'L | 7.5 | 3 |
|  | zyR | zy'R | 7.5 | 3 |
| sC–sC' | sCL | sC'L | 10.5 | 2.5 |
|  | sCR | sC'R | 10.5 | 2.5 |
| iC–iC' | iCL | iC'L | 11 | 2.5 |
|  | iCR | iC'R | 11 | 2.5 |
| ecm2–sM2' | ecm2(s)L | sM2'L | 26 | 7 |
|  | ecm2(s)R | sM2'R | 26 | 7 |
| ecm2–iM2' | ecm2(i)L | iM2'L | 22 | 6.5 |
|  | ecm2(i)R | iM2'R | 22 | 6.5 |
| mr–mr' | mrL | mr'L | 19.5 | 5 |
|  | mrR | mr'R | 19.5 | 5 |
| mmb–mmb' | mmbL | mmb'L | 11 | 4 |
|  | mmbR | mmb'R | 11 | 4 |


## What does the code do?

- FHP realignment of CT scan (optional)
  
As most landmarks are described with the cranium in the Frankfurt Horizontal Plane, this function re-positions the scan bassed on the left and right porions and the left zygion (probably a misnomer; the inferiormost point on the left orbital rim)

- ROI cropping (optional)
  
If the scan includes more structures or unwanted items, this opens Slicer's own module to deal with them

- Bone segmentation (optional)
  
In case you wish to create a model segmentation based on Hounsfield Units, this function created one between the thresholding of 300 and the scan's maximum value

- Landmark placement helpers (midpoint, lateral, gonion, orbital)
  
For landmarks that are defined as depending on other landmarks or lines, this tool creates guidance to place them mathematically - these would STILL need to be manually adjusted onto bone surfaces.

- Peg generation (model and volume modes)
  
The code generates cylinders of the mean reported value of the FSTT at each landmark site, projecting from the bone surface "outwards" based on the landmarks surface environment. Although perpendicularity in in the code, the orientation of these pegs are based on their location (if on the left, points left and is perpendicualr to surface)


- Peg adjustment with sliders
  
The option to toggle these values between the maximum and minimum standard deviations reported in the literature


- Export to multiple formats
  
For practitioners who would like to continue the work in a more familiar environment 







# Bibliography

[^1]: 3D Slicer webpage https://www.slicer.org/
[^2]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." International Journal of Legal Medicine 130(3): 863-879.
[^3]: Hona, T. W. P. T. and C. N. Stephan (2024). "Global facial soft tissue thicknesses for craniofacial identification (2023): a review of 140 years of data since Welcker’s first study." International Journal of Legal Medicine 138(2): 519–535.
[^4]:Stephan, C. N. and E. K. Simpson (2008). "Facial soft tissue depths in craniofacial identification (part I): An analytical review of the published adult data." J Forensic Sci 53(6): 1257–1272.


