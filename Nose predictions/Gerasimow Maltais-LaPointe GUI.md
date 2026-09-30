```python

class GerasimowNosePredictor(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        
        # Debug mode
        self.DEBUG_MODE = False
        
        # Set at beginning to avoid errors
        self.minLogLevel = 1
        self.currentDialog = None
        
        # Disable markups popup notifications
        settings = qt.QSettings()
        settings.setValue("Markups/MarkupsFidNotificationPopupEnabled", 0)
        
        self.mainWidget = qt.QWidget()
        self.mainWidget.setWindowTitle("Gerasimov's Nose Prediction (with Maltais-LaPointe's 3D adjustment)")
        self.mainWidget.setObjectName("GerasimowNosePredictor")
        # Pinned by default
        self.mainWidget.setWindowFlags(
            self.mainWidget.windowFlags() | qt.Qt.WindowStaysOnTopHint
        )
        self.isPinned = True
        
        # ==================== MAIN LAYOUT ====================
        mainLayout = qt.QVBoxLayout(self.mainWidget)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(8)
        
        # ==================== TOP BAR: TITLE + PIN ====================
        topBarLayout = qt.QHBoxLayout()
        titleLabel = qt.QLabel("Gerasimov's Two Tangent Method")
        titleLabel.setStyleSheet("font-weight: bold; font-size: 18px;")
        titleLabel.setAlignment(qt.Qt.AlignCenter)
        topBarLayout.addWidget(titleLabel, 1)
        
        self.pinButton = qt.QPushButton("📌 Pinned")
        self.pinButton.setCheckable(True)
        self.pinButton.setChecked(True)
        self.pinButton.setToolTip("Pin window to stay on top (stops it from disappearing behind 3D view)")
        self.pinButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:checked {
                background-color: #f44336;
            }
        """)
        self.pinButton.toggled.connect(self.onPinToggled)
        topBarLayout.addWidget(self.pinButton)
        
        mainLayout.addLayout(topBarLayout)
        
        # ==================== NAVIGATION AT TOP ====================
        self.setupNavigation()
        mainLayout.addLayout(self.navLayout)
        
        # Separator
        separator = qt.QFrame()
        separator.setFrameShape(qt.QFrame.HLine)
        separator.setFrameShadow(qt.QFrame.Sunken)
        mainLayout.addWidget(separator)
        
        # ==================== SCROLLABLE CONTENT ====================
        self.scrollArea = qt.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumHeight(150)
        self.scrollArea.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        
        scrollContent = qt.QWidget()
        scrollLayout = qt.QVBoxLayout(scrollContent)
        scrollLayout.setContentsMargins(0, 0, 0, 0)
        scrollLayout.setSpacing(10)
        
        # Step stack
        self.stepStack = qt.QStackedWidget()
        scrollLayout.addWidget(self.stepStack)
        
        # Status label
        self.stepStatusLabel = qt.QLabel("Ready")
        self.stepStatusLabel.setWordWrap(True)
        self.stepStatusLabel.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 5px; font-weight: bold;")
        scrollLayout.addWidget(self.stepStatusLabel)
        

        # Optional decision log
        logGroupBox = qt.QGroupBox("Decision Log (click to expand/collapse)")
        logGroupBox.setCheckable(True)
        logGroupBox.setChecked(False)
        logGroupBox.setMaximumHeight(150)
        logLayout = qt.QVBoxLayout(logGroupBox)
        logLayout.setContentsMargins(5, 5, 5, 5)
        self.logWidget = qt.QTextEdit()
        self.logWidget.setReadOnly(True)
        self.logWidget.setMaximumHeight(120)
        logLayout.addWidget(self.logWidget)
        scrollLayout.addWidget(logGroupBox)
        
        self.scrollArea.setWidget(scrollContent)
        mainLayout.addWidget(self.scrollArea)
        
        self.decisions = []
        self.log("Starting Two-Tangent Method")
        
    
        # ==================== NODE STORAGE ====================
        self.landmarksNode = None
        self.planeNode = None
        self.boneModel = None
        self.boneLeftModel = None
        self.boneRightModel = None

        # ==================== TANGENT / POINT STORAGE ====================
        self.tangents = {}
        self.points = {}
        self.tangentNodes = {}
        self.tangent_backups = {}
        self.all_measurements = {}
        self.all_coordinates = {}
        self.intersections = {}
        self.tangent_observer_id = None

        # ==================== FLAGS ====================
        self.isDynamicModelerInstalled = False
        self.updatingTangent = False
        self.currentDialog = None
        self.minLogLevel = 1
        self.DEBUG_MODE = False

        # ==================== CURRENT STEP ====================
        self.currentStep = 0
        self.totalSteps = 7

        # Create all step widgets
        self.createAllStepWidgets()

        # Size
        self.mainWidget.setMinimumSize(520, 300)
        self.mainWidget.resize(560, 680)
        self.mainWidget.setMaximumSize(850, 1200)

        # Dependencies & scene
        self.checkDependencies()
        self.syncWithScene()

        # UI
        self.updateStepUI()

        # Show
        self.mainWidget.show()
    
    def showDialogOnTop(self, message, title="Information", icon="info"):
        """Show a dialog that stays on top of the pinned window"""
        dialog = qt.QMessageBox(self.mainWidget)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setWindowFlags(dialog.windowFlags() | qt.Qt.WindowStaysOnTopHint)
        
        if icon == "warning":
            dialog.setIcon(qt.QMessageBox.Warning)
        elif icon == "error":
            dialog.setIcon(qt.QMessageBox.Critical)
        else:
            dialog.setIcon(qt.QMessageBox.Information)
        
        dialog.exec_()
    
    def showConfirmDialogOnTop(self, message, title="Confirm"):
        """Show a confirmation dialog that stays on top"""
        dialog = qt.QMessageBox(self.mainWidget)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        dialog.setWindowFlags(dialog.windowFlags() | qt.Qt.WindowStaysOnTopHint)
        return dialog.exec_() == qt.QMessageBox.Yes
    
    def onPinToggled(self, checked):
        """Toggle window stay-on-top behavior"""
        if checked:
            # Pin the window - stays on top
            self.mainWidget.setWindowFlags(
                self.mainWidget.windowFlags() | qt.Qt.WindowStaysOnTopHint
            )
            self.pinButton.setText("📌 Pinned")
            self.pinButton.setToolTip("Window stays on top. Click to unpin.")
            self.log("Window pinned (stays on top)")
        else:
            # Unpin - normal behavior
            self.mainWidget.setWindowFlags(
                self.mainWidget.windowFlags() & ~qt.Qt.WindowStaysOnTopHint
            )
            self.pinButton.setText("📍 Unpinned")
            self.pinButton.setToolTip("Window can go behind 3D view. Click to pin.")
            self.log("Window unpinned (can go behind)")
        
        # Need to re-show the window for flags to take effect
        self.mainWidget.show()
    
    def debug_print(self, message):
        """Print debug messages only if DEBUG_MODE is enabled"""
        if self.DEBUG_MODE:
            print(f"DEBUG: {message}")
    
    def log(self, decision, level=1):
        """Add a decision to the log if it meets the minimum log level"""
        if level >= self.minLogLevel:
            self.decisions.append(decision)
            self.updateLog()
    
    def updateLog(self):
        """Update the log window"""
        logText = "<h3>Important Actions</h3><ol>"
        for decision in self.decisions:
            logText += f"<li>{decision}</li>"
        logText += "</ol>"
        self.logWidget.setHtml(logText)
    
    def checkDependencies(self):
        """Check if Dynamic Modeler extension is installed"""
        moduleName = "DynamicModeler"
        if moduleName in slicer.app.moduleManager().factoryManager().registeredModuleNames():
            self.isDynamicModelerInstalled = True
        else:
            self.isDynamicModelerInstalled = False
            self.showDialogOnTop(
                "The <b>Dynamic Modeler</b> extension is required for skull cutting (Steps 3-4), but it was not found.\n\n"
                "Please install it to use all features:\n"
                "1. Go to View -> Extension Manager\n"
                "2. Search for 'Dynamic Modeler'\n"
                "3. Click Install\n"
                "4. Restart 3D Slicer\n\n"
                "You can still use the T1-T2 shortcut without this extension.",
                "Missing Required Extension", "warning"
            )
    
    def setupNavigation(self):
        self.navLayout = qt.QHBoxLayout()
        self.navLayout.setContentsMargins(0, 0, 0, 0)
        
        self.prevButton = qt.QPushButton("◀ Previous")
        self.prevButton.setToolTip("Go to the previous step")
        self.prevButton.clicked.connect(self.onPrevButtonClicked)
        
        self.stepLabel = qt.QLabel("Step 1/9")
        self.stepLabel.setAlignment(qt.Qt.AlignCenter)
        self.stepLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.nextButton = qt.QPushButton("Next ▶")
        self.nextButton.setToolTip("Go to the next step")
        self.nextButton.clicked.connect(self.onNextButtonClicked)
        
        self.navLayout.addWidget(self.prevButton)
    
        self.navLayout.addWidget(self.stepLabel)
    
        self.navLayout.addWidget(self.nextButton)
    
    def createAllStepWidgets(self):
        """Create all step widgets"""
        self.createStep1_Welcome()
        self.createStep2_PlaneSetup()
        self.createStep3_Segmentation()
        self.createStep4_ExecuteVisualization()
        self.createStep5_TangentCreation()
        self.createStep6_SoftTissueComparison()
        self.createStep7_Results()
    
    def createStep1_Welcome(self):
        """Step 1: Welcome and Load Landmarks"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Welcome to Gerasimow's Nose Prediction Method")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        title.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = qt.QLabel(
            "This method predicts the pronasale (nose tip) position using tangent lines.\n\n"
            "Please begin by loading the required landmarks using one of the options below."
        )
        desc.setWordWrap(True)
        desc.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(desc)
        
        buttonLayout = qt.QVBoxLayout()
        buttonLayout.setSpacing(10)
        
        self.downloadButton = qt.QPushButton("📥 Download Landmarks from GitHub")
        self.downloadButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.downloadButton.clicked.connect(self.onDownloadLandmarksClicked)
        buttonLayout.addWidget(self.downloadButton)
        
        self.loadLocalButton = qt.QPushButton("📂 Load Landmarks from Local File")
        self.loadLocalButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        self.loadLocalButton.clicked.connect(self.onLoadLocalLandmarksClicked)
        buttonLayout.addWidget(self.loadLocalButton)
        
        layout.addLayout(buttonLayout)
        
        self.step1StatusLabel = qt.QLabel("Status: Waiting for landmarks to be loaded.")
        self.step1StatusLabel.setWordWrap(True)
        self.step1StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.step1StatusLabel)
        
        
        self.stepStack.addWidget(widget)
    
    def createStep2_PlaneSetup(self):
        """Step 2: Create Reference Plane"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 2: Create a Reference Plane")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        desc_html = """
        <p>Create a reference plane for the tangent lines. You have two options:</p>
        <ul>
            <li><b>INB Plane:</b> Uses Inion, Nasion, and Bregma (simple three-point plane)</li>
            <li><b>MSP Plane:</b> Uses Nasion, Acanthion, Prosthion, and Subspinale (best-fit midsagittal plane)</li>
        </ul>
        <p>The plane will be used to constrain the tangent lines in the following steps.</p>
        """
        desc = qt.QLabel(desc_html)
        desc.setTextFormat(qt.Qt.RichText)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        planeChoiceLayout = qt.QVBoxLayout()
        planeChoiceLayout.setSpacing(10)
        
        self.landmarkBundleCombo = qt.QComboBox()
        self.landmarkBundleCombo.addItems([
            "Select a method...",
            "INB (Inion-Nasion-Bregma)",
            "MSP (Midsagittal Best-Fit)"
        ])
        planeChoiceLayout.addWidget(self.landmarkBundleCombo)
        
        self.createPlaneButton = qt.QPushButton("Create Plane")
        self.createPlaneButton.setStyleSheet("background-color: #FFDF00; font-weight: bold; padding: 10px;")
        self.createPlaneButton.clicked.connect(self.onCreatePlaneClicked)
        planeChoiceLayout.addWidget(self.createPlaneButton)
        
        layout.addLayout(planeChoiceLayout)
        
        self.step2StatusLabel = qt.QLabel("Status: Please choose a plane creation method.")
        self.step2StatusLabel.setWordWrap(True)
        self.step2StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.step2StatusLabel)
        
        self.stepStack.addWidget(widget)
    
    def createStep3_Segmentation(self):
        """Step 3: Choose Visualization Method"""
        widget = qt.QWidget()
        mainLayout = qt.QVBoxLayout(widget)
        mainLayout.setSpacing(20)
        
        title = qt.QLabel("Step 3: Choose Your Visualization Method")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        title.setAlignment(qt.Qt.AlignCenter)
        mainLayout.addWidget(title)
        
        intro = qt.QLabel(
            "You need to visualize the skull to place tangent lines accurately. "
            "Choose one of the two methods below:"
        )
        intro.setWordWrap(True)
        intro.setAlignment(qt.Qt.AlignCenter)
        mainLayout.addWidget(intro)
        
        mainLayout.addSpacing(20)
        
        # Option 1: Manual Volume Rendering
        option1Group = qt.QGroupBox()
        option1Group.setStyleSheet("QGroupBox { background-color: #E8F5E9; border: 2px solid #4CAF50; border-radius: 5px; padding: 15px; }")
        option1Layout = qt.QVBoxLayout(option1Group)
        
        option1Title = qt.QLabel("<b>📌 Option 1: Quick Manual Method (Volume Rendering)</b>")
        option1Title.setTextFormat(qt.Qt.RichText)
        option1Title.setStyleSheet("font-size: 14px;")
        option1Layout.addWidget(option1Title)
        
        option1Desc = qt.QLabel(
            "<b>Pros:</b> Fast, reversible, good for beginners<br>"
            "<b>Cons:</b> Temporary visualization only, not saved<br><br>"
            "<b>Best for:</b> Quick analysis, T1-T2 shortcut method, learning"
        )
        option1Desc.setTextFormat(qt.Qt.RichText)
        option1Desc.setWordWrap(True)
        option1Layout.addWidget(option1Desc)
        
        self.chooseManualButton = qt.QPushButton("✓ Choose Manual Method")
        self.chooseManualButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.chooseManualButton.clicked.connect(self.onChooseManualMethod)
        option1Layout.addWidget(self.chooseManualButton)
        
        mainLayout.addWidget(option1Group)
        
        # OR separator
        orLabel = qt.QLabel("<center><b>— OR —</b></center>")
        orLabel.setTextFormat(qt.Qt.RichText)
        orLabel.setStyleSheet("font-size: 14px; font-weight: bold;")
        mainLayout.addWidget(orLabel)
        
        # Option 2: Automatic Segmentation
        option2Group = qt.QGroupBox()
        option2Group.setStyleSheet("QGroupBox { background-color: #E3F2FD; border: 2px solid #2196F3; border-radius: 5px; padding: 15px; }")
        option2Layout = qt.QVBoxLayout(option2Group)
        
        option2Title = qt.QLabel("<b>🤖 Option 2: Permanent Segmentation Method</b>")
        option2Title.setTextFormat(qt.Qt.RichText)
        option2Title.setStyleSheet("font-size: 14px;")
        option2Layout.addWidget(option2Title)
        
        option2Desc = qt.QLabel(
            "<b>Pros:</b> Creates permanent 3D model, can save and export<br>"
            "<b>Cons:</b> More steps, takes longer, requires more disk space<br><br>"
            "<b>Best for:</b> Publication, detailed analysis, model archiving"
        )
        option2Desc.setTextFormat(qt.Qt.RichText)
        option2Desc.setWordWrap(True)
        option2Layout.addWidget(option2Desc)
        
        self.chooseSegmentationButton = qt.QPushButton("✓ Choose Segmentation Method")
        self.chooseSegmentationButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        self.chooseSegmentationButton.clicked.connect(self.onChooseSegmentationMethod)
        option2Layout.addWidget(self.chooseSegmentationButton)
        
        mainLayout.addWidget(option2Group)
        
        mainLayout.addSpacing(20)
        
        self.step3StatusLabel = qt.QLabel("Status: Please choose a visualization method above.")
        self.step3StatusLabel.setWordWrap(True)
        self.step3StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        mainLayout.addWidget(self.step3StatusLabel)
        

        self.stepStack.addWidget(widget)
        
        # Store the chosen method
        self.chosenVisualizationMethod = None
    
    def createStep4_ExecuteVisualization(self):
        """Step 4: Execute the chosen visualization method"""
        widget = qt.QWidget()
        mainLayout = qt.QVBoxLayout(widget)
        mainLayout.setSpacing(15)
        
        title = qt.QLabel("Step 4: Set Up Visualization")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        mainLayout.addWidget(title)
        
        # This will be populated dynamically based on choice
        self.step4ContentWidget = qt.QWidget()
        self.step4ContentLayout = qt.QVBoxLayout(self.step4ContentWidget)
        mainLayout.addWidget(self.step4ContentWidget)
        
        self.step4StatusLabel = qt.QLabel("Status: Complete Step 3 first to see instructions here.")
        self.step4StatusLabel.setWordWrap(True)
        self.step4StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        mainLayout.addWidget(self.step4StatusLabel)
        
        
        self.stepStack.addWidget(widget)
    
    def populateStep4ForManualMethod(self):
        """Populate Step 4 with manual volume rendering instructions"""
        # Clear existing content
        while self.step4ContentLayout.count():
            child = self.step4ContentLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        methodLabel = qt.QLabel("<b>Method: Volume Rendering (Manual)</b>")
        methodLabel.setTextFormat(qt.Qt.RichText)
        methodLabel.setStyleSheet("font-size: 14px; color: #4CAF50;")
        self.step4ContentLayout.addWidget(methodLabel)
        
        # Detailed instructions
        instructionsLabel = qt.QLabel(
            "<b>Follow these steps to set up volume rendering:</b><br><br>"
            "<b>1.</b> Click the button below to open the Volume Rendering module.<br>"
        )
        instructionsLabel.setTextFormat(qt.Qt.RichText)
        instructionsLabel.setWordWrap(True)
        self.step4ContentLayout.addWidget(instructionsLabel)
        
        openVRButton = qt.QPushButton("📊 Open Volume Rendering Module")
        openVRButton.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        openVRButton.clicked.connect(self.onOpenVolumeRendering)
        self.step4ContentLayout.addWidget(openVRButton)
        
        detailedSteps = qt.QLabel(
            "<br><b>2.</b> In the Volume Rendering module: <br>"
            "• Under '<b>Display</b>' section, find the '<b>Crop</b>' subsection<br>"
            "• Click the <b>eye icon</b> next to 'Display ROI' to make it visible<br>"
            "• Tick the checkbox for '<b>Enable</b>' under Crop<br><br>"
            "<b>3.</b> A <b>3D box (ROI)</b> should appear around your skull: <br>"
            "• If you cannot see the box, adjust the '<b>Shift</b>' slider (located right above 'Crop')<br>"
            "• Drag the box handles to cut the skull in half around the <b>acanthion</b> landmark<br>"
            "• This helps you visualize the <b>anterior nasal spine</b> for tangent T2<br><br>"
            "<b>4.</b> For tangent T2, you need to see the general direction of the anterior nasal spine. <br><br>"
            "<b>5.</b> When you're done placing tangents: <br>"
            "• Untick '<b>Enable</b>' under Crop<br>"
            "• Close the eye icon for 'Display ROI'<br>"
            "• This restores the full skull view"
        )
        detailedSteps.setTextFormat(qt.Qt.RichText)
        detailedSteps.setWordWrap(True)
        self.step4ContentLayout.addWidget(detailedSteps)
        
        continueButton = qt.QPushButton("✓ Continue to Tangent Creation")
        continueButton.setStyleSheet("background-color: #FF9800; color: white; padding: 10px; font-weight: bold;")
        continueButton.clicked.connect(self.onSkipToTangents)
        self.step4ContentLayout.addWidget(continueButton)
        
        self.step4StatusLabel.setText("Status: Follow the volume rendering instructions above.")
    
    def populateStep4ForSegmentation(self):
        """Populate Step 4 with detailed segmentation instructions"""
        # Clear existing content
        while self.step4ContentLayout.count():
            child = self.step4ContentLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        methodLabel = qt.QLabel("<b>Method: Segmentation (Permanent Model)</b>")
        methodLabel.setTextFormat(qt.Qt.RichText)
        methodLabel.setStyleSheet("font-size: 14px; color: #2196F3;")
        self.step4ContentLayout.addWidget(methodLabel)
        
        # Create scroll area for detailed instructions
        self.scrollArea = qt.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setMaximumHeight(400)
        instructions_container = qt.QWidget()
        instructions_layout = qt.QVBoxLayout(instructions_container)
        instructions_layout.setContentsMargins(5, 5, 5, 5)
        scrollArea.setWidget(instructions_container)
        
        instructions = qt.QLabel()
        instructions.setTextFormat(qt.Qt.RichText)
        instructions.setWordWrap(True)
        instructions.setText(
            "<b>Follow these steps carefully to create a 'Bone' model:</b><br><br>"
            "<b>1. Open Segment Editor: </b> Click this button to open the module. <br>"
        )
        instructions_layout.addWidget(instructions)
        
        self.openSegmentEditorButton = qt.QPushButton("Open Segment Editor Module")
        self.openSegmentEditorButton.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px;")
        self.openSegmentEditorButton.clicked.connect(self.onOpenSegmentEditor)
        instructions_layout.addWidget(self.openSegmentEditorButton)
        
        instructions2 = qt.QLabel()
        instructions2.setTextFormat(qt.Qt.RichText)
        instructions2.setWordWrap(True)
        instructions2.setText(
            "<br><b>2. Rename your segmentation: </b> Click the dropdown menu next to <b>Segmentation: </b> and choose 'Rename current Segmentation'.<br><br>"
            "<b>3. Source Volume</b> should be the name of your DICOM file.<br><br>"
            "<b>4. Click the plus sign [+] 'Add'. </b><br><br>"
            "<b>5. Choose the Threshold tool</b> from the panel below (in the right column, first row).<br><br>"
            "<b>6. Edit the Threshold Range:</b> The minimum is usually 500. The maximum can stay as is. "
            "You can adjust these values to see more or less detail.<br><br>"
            "<b>7. Click 'Apply'</b> (in the Local histogram menu), then find the <b>'Show 3D'</b> button on the top, "
            "near to where the 'Add' button was. Click it and wait for the model to appear.<br><br>"
            "<b>8. If you're happy with the details,</b> click on the green right arrow to go to the 'Segmentations' module.<br><br>"
            "<b>9. Double click on the row below 'Name'</b> and in the pop-up, edit the model name into <b>'Bone'</b>.<br><br>"
            "<b>10. Scroll to the dropdown menu 'Export/import models and labelmaps': </b> Make sure the <b>Operation</b> is 'Export' "
            "and the <b>Output type</b> is 'Models'. Then move down to the next dropdown and click on '<b>Export</b>'.<br><br>"
            "<b>11. IMPORTANT: </b> You need to import this model back into the scene by clicking the <b>'Data'</b> button "
            "(very top of the Slicer window, under 'File'), 'Choose file(s) to add... ', and navigate to where Slicer saved your model. "
            "Select it and click 'OK'.<br><br>"
            "<b>12. Select the re-imported model below: </b>"
        )
        instructions_layout.addWidget(instructions2)
        
        self.step4ContentLayout.addWidget(scrollArea)
        
        # Model selector
        confirmFrame = qt.QFrame()
        confirmLayout = qt.QFormLayout(confirmFrame)
        confirmLabel = qt.QLabel("Select re-imported 'Bone' model:")
        
        self.boneModelSelector = slicer.qMRMLNodeComboBox()
        self.boneModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.boneModelSelector.setMRMLScene(slicer.mrmlScene)
        self.boneModelSelector.addEnabled = False
        self.boneModelSelector.removeEnabled = False
        self.boneModelSelector.noneEnabled = True
        self.boneModelSelector.currentNodeChanged.connect(self.onConfirmSegmentation)
        
        confirmLayout.addRow(confirmLabel, self.boneModelSelector)
        self.step4ContentLayout.addWidget(confirmFrame)
        
        self.step4StatusLabel.setText("Status: Follow the segmentation instructions above and select the model when done.")
    
    def onChooseManualMethod(self):
        """Handle manual method selection"""
        self.chosenVisualizationMethod = "manual"
        self.step3StatusLabel.setText("Status: Manual method chosen! Proceed to Step 4.")
        self.log("Chose manual volume rendering method")
        self.populateStep4ForManualMethod()
        # Enable next button
        self.nextButton.setEnabled(True)
    
    def onChooseSegmentationMethod(self):
        """Handle segmentation method selection"""
        self.chosenVisualizationMethod = "segmentation"
        self.step3StatusLabel.setText("Status: Segmentation method chosen! Proceed to Step 4.")
        self.log("Chose segmentation method")
        self.populateStep4ForSegmentation()
        # Enable next button
        self.nextButton.setEnabled(True)
    
    def onSkipToTangents(self):
        """Skip directly to tangent creation (for manual method)"""
        self.step4StatusLabel.setText("Status: Proceeding to tangent creation.")
        self.log("Manual method complete, proceeding to tangent creation")
        # Jump to Step 5 (Tangent Creation)
        self.currentStep = 4  # Step 5 is index 4 (0-indexed)
        self.updateStepUI()
    
    def createStep5_TangentCreation(self):
        """Step 5: Create Tangent Lines"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 5: Create Tangent Lines")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Tangent Description Table
        tableGroup = qt.QGroupBox("Tangent Line Reference")
        tableLayout = qt.QVBoxLayout(tableGroup)
        
        # Create table
        self.tangentTable = qt.QTableWidget()
        self.tangentTable.setColumnCount(4)
        self.tangentTable.setHorizontalHeaderLabels(["Tangent", "Description", "Name in Files", "Color"])
        self.tangentTable.horizontalHeader().setStretchLastSection(True)
        
        # Set table data
        tangent_data = [
            ["Tangent 1", "Follows the last third of the nasal bone", "T1", "Yellow"],
            ["Tangent 2", "Follows the general direction of the anterior nasal spine", "T2", "Green"],
            ["Tangent 3", "Follows the last 1-2 mm of the nasal bone", "T3", "Blue"],
            ["Tangent 4 - Right", "Follows the nasal floor to the RIGHT of the anterior nasal spine", "T4R", "Purple"],
            ["Tangent 4 - Left", "Follows the nasal floor to the LEFT of the anterior nasal spine", "T4L", "Purple"]
        ]
        
        self.tangentTable.setRowCount(len(tangent_data))
        for row, data in enumerate(tangent_data):
            for col, value in enumerate(data):
                item = qt.QTableWidgetItem(value)
                if col == 3:  # Color column
                    # Set background color
                    color_map = {
                        "Yellow": qt.QColor(255, 255, 100),
                        "Green": qt.QColor(100, 255, 100),
                        "Blue": qt.QColor(100, 150, 255),
                        "Purple": qt.QColor(160, 100, 200)
                    }
                    if value in color_map:
                        item.setBackground(color_map[value])
                self.tangentTable.setItem(row, col, item)
        
        self.tangentTable.setMinimumHeight(140)
        tableLayout.addWidget(self.tangentTable)
        layout.addWidget(tableGroup)
        
        # T1-T2 Shortcut Section
        shortcutGroup = qt.QGroupBox("Quick Method: T1-T2 Shortcut")
        shortcutLayout = qt.QVBoxLayout(shortcutGroup)
        
        shortcutDesc = qt.QLabel(
            "For a quick prediction using only T1 and T2 tangents, enable the shortcut below. "
            "This will hide the more complex T3, T4R, and T4L options."
        )
        shortcutDesc.setWordWrap(True)
        shortcutLayout.addWidget(shortcutDesc)
        
        self.t1t2ShortcutCheckbox = qt.QCheckBox("Use T1-T2 Shortcut Mode")
        self.t1t2ShortcutCheckbox.setToolTip("When enabled, only T1 and T2 tangents are used")
        self.t1t2ShortcutCheckbox.setChecked(False)
        self.t1t2ShortcutCheckbox.toggled.connect(self.onT1T2ShortcutToggled)
        shortcutLayout.addWidget(self.t1t2ShortcutCheckbox)
        
        layout.addWidget(shortcutGroup)
        
        # Tangent Generation Section
        tangentGroup = qt.QGroupBox("Tangent Line Generation")
        tangentLayout = qt.QVBoxLayout(tangentGroup)
        
        self.regenTangentsButton = qt.QPushButton("🔄 Generate Default Tangents (T1, T2, T3)")
        self.regenTangentsButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        self.regenTangentsButton.setToolTip("Create T1, T2, T3 using default positions on the current plane")
        self.regenTangentsButton.clicked.connect(self.onRegenerateTangentsClicked)
        tangentLayout.addWidget(self.regenTangentsButton)
        
        self.tangentInstructionLabel = qt.QLabel("Click the button above to create tangent lines.")
        self.tangentInstructionLabel.setStyleSheet("font-style: italic; color: #555555; padding: 5px;")
        self.tangentInstructionLabel.setWordWrap(True)
        self.tangentInstructionLabel.setAlignment(qt.Qt.AlignCenter)
        tangentLayout.addWidget(self.tangentInstructionLabel)
        
        layout.addWidget(tangentGroup)
        
        # Project to Plane button (separate, for all tangents)
        projectButton = qt.QPushButton("📐 Project All Tangents to Plane")
        projectButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        projectButton.clicked.connect(self.projectAllTangentsToPlane)
        layout.addWidget(projectButton)
        
        # T4 Section
        self.t4Group = qt.QGroupBox("T4R and T4L Tangents (Nasal Floor Direction)")
        t4Layout = qt.QVBoxLayout(self.t4Group)
        
        # Instructions for T4 placement
        t4Instructions = qt.QLabel(
            "<b>Instructions for T4 tangents:</b><br>"
            "• <b>T4R</b> follows the nasal floor to the RIGHT of the anterior nasal spine<br>"
            "• <b>T4L</b> follows the nasal floor to the LEFT of the anterior nasal spine<br>"
            "• Click 'Create T4R' or 'Create T4L' to create an empty line node<br>"
            "• Then manually add control points using Slicer's Markups tools<br>"
            "• After placing both T4R and T4L, click 'Calculate T4' to generate the average direction"
        )
        t4Instructions.setTextFormat(qt.Qt.RichText)
        t4Instructions.setWordWrap(True)
        t4Layout.addWidget(t4Instructions)
        
        # Create empty line buttons (no auto-placement)
        self.t4rButton = qt.QPushButton("📏 Create Empty T4R Line (Purple - Right nasal floor)")
        self.t4rButton.setStyleSheet("background-color: #9966CC; color: white; font-weight: bold; padding: 10px;")
        self.t4rButton.clicked.connect(self.onCreateEmptyT4R)
        t4Layout.addWidget(self.t4rButton)
        
        self.t4lButton = qt.QPushButton("📏 Create Empty T4L Line (Purple - Left nasal floor)")
        self.t4lButton.setStyleSheet("background-color: #AA88DD; color: white; font-weight: bold; padding: 10px;")
        self.t4lButton.clicked.connect(self.onCreateEmptyT4L)
        t4Layout.addWidget(self.t4lButton)
        
        # Refresh button to check T4 status
        refreshButton = qt.QPushButton("🔄 Refresh T4 Status")
        refreshButton.setStyleSheet("background-color: #607D8B; color: white; padding: 8px;")
        refreshButton.clicked.connect(self.updateT4StatusFromExistingLines)
        t4Layout.addWidget(refreshButton)
        
        # Separator
        separator = qt.QFrame()
        separator.setFrameShape(qt.QFrame.HLine)
        separator.setFrameShadow(qt.QFrame.Sunken)
        t4Layout.addWidget(separator)
        
        # T4 Calculation Section
        calcLabel = qt.QLabel("<b>Calculate T4 from T4R and T4L:</b>")
        calcLabel.setStyleSheet("font-weight: bold; margin-top: 5px; color: #FF9800;")
        t4Layout.addWidget(calcLabel)
        
        calcDesc = qt.QLabel(
            "After placing both T4R and T4L (with at least 2 control points each), click below to calculate T4.\n"
            "T4 represents the general nasal floor direction in the midplane."
        )
        calcDesc.setWordWrap(True)
        calcDesc.setStyleSheet("color: #555; font-style: italic;")
        t4Layout.addWidget(calcDesc)
        
        self.calculateT4Button = qt.QPushButton("🔧 Calculate T4 from T4R/T4L")
        self.calculateT4Button.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        self.calculateT4Button.clicked.connect(self.onCalculateT4FromTangents)
        t4Layout.addWidget(self.calculateT4Button)
        
        # T4 status label
        self.t4StatusLabel = qt.QLabel("T4 Status: Create T4R and T4L, then add control points (at least 2 each).")
        self.t4StatusLabel.setWordWrap(True)
        self.t4StatusLabel.setStyleSheet("padding: 5px; background-color: #f5f5f5; border-radius: 3px;")
        t4Layout.addWidget(self.t4StatusLabel)
        
        layout.addWidget(self.t4Group)
        
        # Intersection Finding
        intersectionGroup = qt.QGroupBox("Find Intersections")
        intersectionLayout = qt.QVBoxLayout(intersectionGroup)
        
        self.extendTangentsButton = qt.QPushButton("📏 Elongate Tangents if Needed")
        self.extendTangentsButton.setStyleSheet("background-color: #66CCBB; color: white; padding: 8px;")
        self.extendTangentsButton.clicked.connect(self.onExtendTangentsClicked)
        intersectionLayout.addWidget(self.extendTangentsButton)
        
        self.findIntersectionsButton = qt.QPushButton("🎯 Find Intersections")
        self.findIntersectionsButton.setStyleSheet("background-color: #99CC66; color: white; font-weight: bold; padding: 10px;")
        self.findIntersectionsButton.clicked.connect(self.onFindIntersectionsClicked)
        intersectionLayout.addWidget(self.findIntersectionsButton)
        
        layout.addWidget(intersectionGroup)
        
        self.step5StatusLabel = qt.QLabel("Status: Ready to create tangent lines.")
        self.step5StatusLabel.setWordWrap(True)
        self.step5StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.step5StatusLabel)
        
        

        self.stepStack.addWidget(widget)
    
    def onCreateEmptyT4R(self):
        """Create an empty T4R line node (user adds points manually)"""
        self.createEmptyLineNode("T4R", [0.7, 0.4, 0.9])
    
    def onCreateEmptyT4L(self):
        """Create an empty T4L line node (user adds points manually)"""
        self.createEmptyLineNode("T4L", [0.7, 0.4, 0.9])
    
    def createEmptyLineNode(self, name, color):
        """Create an empty line node without activating placement"""
        # Remove existing node if present
        try:
            existing = slicer.util.getNode(name)
            slicer.mrmlScene.RemoveNode(existing)
            self.log(f"Removed existing {name}")
        except:
            pass
        
        # Create new line node
        lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
        
        # Set color and properties
        displayNode = lineNode.GetDisplayNode()
        displayNode.SetColor(color[0], color[1], color[2])
        displayNode.SetSelectedColor(color[0], color[1], color[2])
        displayNode.SetLineThickness(0.5)
        displayNode.SetPointLabelsVisibility(True)
        
        # Store reference
        self.tangentNodes[name] = lineNode
        
        self.log(f"Created empty {name} line node")
        self.stepStatusLabel.setText(f"📍 Created empty {name} line. Use Markups tools to add control points.")
        
        # Show instructions
        self.showDialogOnTop(
            f"{name} created!\n\n"
            "To add control points:\n"
            "1. Double-click the line in the 3D view\n"
            "2. Or use the Markups module to add points\n"
            "3. Add at least 2 points to define the direction\n\n"
            "After adding points, click 'Refresh T4 Status' then 'Calculate T4'"
        )
    
    def updateT4StatusFromExistingLines(self):
        """Check T4R and T4L lines and update status"""
        t4r_ok = False
        t4l_ok = False
        
        if "T4R" in self.tangentNodes:
            node = self.tangentNodes["T4R"]
            if node.GetNumberOfControlPoints() >= 2:
                t4r_ok = True
                # Update stored tangents
                start = [0, 0, 0]
                end = [0, 0, 0]
                node.GetNthControlPointPositionWorld(0, start)
                node.GetNthControlPointPositionWorld(1, end)
                self.tangents["T4R"] = {'start': start, 'end': end}
        
        if "T4L" in self.tangentNodes:
            node = self.tangentNodes["T4L"]
            if node.GetNumberOfControlPoints() >= 2:
                t4l_ok = True
                # Update stored tangents
                start = [0, 0, 0]
                end = [0, 0, 0]
                node.GetNthControlPointPositionWorld(0, start)
                node.GetNthControlPointPositionWorld(1, end)
                self.tangents["T4L"] = {'start': start, 'end': end}
        
        if t4r_ok and t4l_ok:
            self.t4StatusLabel.setText("T4 Status: Both T4R and T4L have control points! Click 'Calculate T4'.")
            self.t4StatusLabel.setStyleSheet("padding: 5px; background-color: #ccffcc; border-radius: 3px;")
            self.calculateT4Button.setEnabled(True)
        elif t4r_ok or t4l_ok:
            self.t4StatusLabel.setText("T4 Status: One tangent has points. Add points to the other, then click Calculate T4.")
            self.t4StatusLabel.setStyleSheet("padding: 5px; background-color: #ffffcc; border-radius: 3px;")
            self.calculateT4Button.setEnabled(False)
        else:
            self.t4StatusLabel.setText("T4 Status: Create T4R and T4L, then add control points (at least 2 each).")
            self.t4StatusLabel.setStyleSheet("padding: 5px; background-color: #f5f5f5; border-radius: 3px;")
            self.calculateT4Button.setEnabled(False)
    
    def onCalculateT4FromTangents(self):
        """
        Calculate T4 as the average vector of T4L and T4R.
        T4 represents the general direction of the nasal floor in the midplane.
        """
        self.log("Calculating T4 from T4L and T4R...")
        
        # First, update from existing lines
        self.updateT4StatusFromExistingLines()
        
        # Check if T4L and T4R exist with enough points
        if "T4L" not in self.tangents or "T4R" not in self.tangents:
            self.showDialogOnTop(
                "Cannot calculate T4!\n\n"
                "Please create both T4L and T4R lines and add at least 2 control points to each.\n\n"
                "T4L = Left nasal floor direction\n"
                "T4R = Right nasal floor direction",
                "Warning", "warning"
            )
            return
        
        # Get T4L and T4R data
        t4l_start = np.array(self.tangents["T4L"]['start'])
        t4l_end = np.array(self.tangents["T4L"]['end'])
        t4r_start = np.array(self.tangents["T4R"]['start'])
        t4r_end = np.array(self.tangents["T4R"]['end'])
        
        # Calculate direction vectors
        t4l_dir = _unit(t4l_end - t4l_start)
        t4r_dir = _unit(t4r_end - t4r_start)
        
        # Average the two direction vectors
        t4_dir = _unit(t4l_dir + t4r_dir)
        
        # Calculate midpoint of the two line centers as the origin point
        t4l_center = (t4l_start + t4l_end) / 2.0
        t4r_center = (t4r_start + t4r_end) / 2.0
        t4_origin = (t4l_center + t4r_center) / 2.0
        
        # Create T4 line (100mm length centered at origin)
        line_length = 100.0
        t4_start = t4_origin - t4_dir * (line_length / 2.0)
        t4_end = t4_origin + t4_dir * (line_length / 2.0)
        
        # Create or update T4 tangent (Pink/Magenta)
        self.createTangentLine("T4", t4_start, t4_end, [0.8, 0.4, 0.6])
        
        # Update status
        self.t4StatusLabel.setText(
            f"T4 Status: Calculated as average vector. Direction: [{t4_dir[0]:.2f}, {t4_dir[1]:.2f}, {t4_dir[2]:.2f}]"
        )
        self.log(f"T4 calculated as average vector of T4L and T4R")
        self.log(f"T4 direction: {t4_dir}")
        
        # Show success message
        self.showDialogOnTop(
            "T4 calculated successfully!\n\n"
            "T4 represents the general direction of the nasal floor in the midplane.\n"
            "Use it for R2 point calculation in Step 6."
        )
        
        self.step5StatusLabel.setText("Status: T4 calculated. Ready to find intersections.")
    
    def projectAllTangentsToPlane(self):
        """Project all existing tangents onto the reference plane (USER CONTROLLED)"""
        if not self.planeNode:
            self.showDialogOnTop("Please create a reference plane first (Step 2).", "Warning", "warning")
            return
        
        planeOrigin = np.zeros(3)
        self.planeNode.GetOriginWorld(planeOrigin)
        planeNormal = np.zeros(3)
        self.planeNode.GetNormalWorld(planeNormal)
        
        # Include all tangents EXCEPT T4 (which is calculated, not placed)
        tangent_names = ["T1", "T2", "T3", "T4R", "T4L"]
        projected_count = 0
        
        for name in tangent_names:
            if name in self.tangentNodes:
                node = self.tangentNodes[name]
                if node.GetNumberOfControlPoints() >= 2:
                    start = [0, 0, 0]
                    end = [0, 0, 0]
                    node.GetNthControlPointPositionWorld(0, start)
                    node.GetNthControlPointPositionWorld(1, end)
                    
                    start_proj = self.projectPointOntoPlane(np.array(start), planeOrigin, planeNormal)
                    end_proj = self.projectPointOntoPlane(np.array(end), planeOrigin, planeNormal)
                    
                    wasModified = node.StartModify()
                    node.SetNthControlPointPositionWorld(0, start_proj)
                    node.SetNthControlPointPositionWorld(1, end_proj)
                    node.EndModify(wasModified)
                    
                    # Update stored tangents
                    self.tangents[name] = {'start': start_proj.tolist(), 'end': end_proj.tolist()}
                    projected_count += 1
                    self.log(f"Projected {name} to plane")
        
        if projected_count > 0:
            self.stepStatusLabel.setText(f"📍 Projected {projected_count} tangents to {self.planeNode.GetName()} plane")
            self.showDialogOnTop(f"{projected_count} tangents projected to {self.planeNode.GetName()} plane")
        else:
            self.stepStatusLabel.setText("📍 No tangents found to project")
    
    def createStep6_SoftTissueComparison(self):
        """Step 6: R2 Point Selection and Confirmation"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 6: R2 Point Confirmation")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        adviceLabel = qt.QLabel(
            "<b>R2 Point Definition:</b><br>"
            "• <b>R2</b> is the point where the T4 tangent crosses the nasal soft tissue (midsagittal plane)<br>"
            "• The R2 point should already be placed in your landmarks node<br>"
            "• Use Slicer's Markups tools to adjust its position if needed, then confirm below"
        )
        adviceLabel.setTextFormat(qt.Qt.RichText)
        adviceLabel.setWordWrap(True)
        layout.addWidget(adviceLabel)
        
        # T4 Elongation button (to help see where T4 intersects soft tissue)
        self.elongateT4Button = qt.QPushButton("📏 Elongate T4 Tangent (for better visualization)")
        self.elongateT4Button.setStyleSheet("background-color: #66CCBB; color: white; font-weight: bold; padding: 10px;")
        self.elongateT4Button.clicked.connect(self.onElongateT4ForR2)
        layout.addWidget(self.elongateT4Button)
        
        # Separator
        separator = qt.QFrame()
        separator.setFrameShape(qt.QFrame.HLine)
        separator.setFrameShadow(qt.QFrame.Sunken)
        layout.addWidget(separator)
        
        # R2 Selection Section
        selectionGroup = qt.QGroupBox("R2 Point Selection")
        selectionLayout = qt.QVBoxLayout(selectionGroup)
        
        # Show current R2 status
        self.r2StatusLabel = qt.QLabel("R2 Status: Detecting...")
        self.r2StatusLabel.setWordWrap(True)
        self.r2StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        selectionLayout.addWidget(self.r2StatusLabel)
        
        # Refresh button to check R2 status
        self.refreshR2Button = qt.QPushButton("🔄 Refresh R2 Status")
        self.refreshR2Button.setStyleSheet("background-color: #607D8B; color: white; padding: 8px;")
        self.refreshR2Button.clicked.connect(self.refreshR2Status)
        selectionLayout.addWidget(self.refreshR2Button)
        
        # Confirmation button
        self.confirmR2Button = qt.QPushButton("✓ Confirm R2 Placement")
        self.confirmR2Button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.confirmR2Button.setEnabled(False)
        self.confirmR2Button.clicked.connect(self.onConfirmR2Placed)
        selectionLayout.addWidget(self.confirmR2Button)
        
        layout.addWidget(selectionGroup)
        
        # Error comparison
        self.calculateErrorsButton = qt.QPushButton("📊 Compare True vs. Predicted Points")
        self.calculateErrorsButton.setStyleSheet("background-color: #f0ad4e; color: white; font-weight: bold; padding: 10px;")
        self.calculateErrorsButton.setEnabled(False)
        self.calculateErrorsButton.clicked.connect(self.onCalculateErrorsClicked)
        layout.addWidget(self.calculateErrorsButton)
        
        
        self.stepStack.addWidget(widget)
    
    def onElongateT4ForR2(self):
        """Elongate T4 tangent to help visualize intersection with soft tissue"""
        if "T4" not in self.tangents:
            self.showDialogOnTop("Please calculate T4 first in Step 5.", "Warning", "warning")
            return
        
        elongation_distance = 100  # mm
        
        tangent = self.tangents["T4"]
        start = np.array(tangent['start'])
        end = np.array(tangent['end'])
        
        direction = end - start
        direction_normalized = direction / np.linalg.norm(direction)
        
        new_start = start - elongation_distance * direction_normalized
        new_end = end + elongation_distance * direction_normalized
        
        self.tangents["T4"]['start'] = new_start.tolist()
        self.tangents["T4"]['end'] = new_end.tolist()
        
        if "T4" in self.tangentNodes:
            node = self.tangentNodes["T4"]
            wasModified = node.StartModify()
            node.SetNthControlPointPositionWorld(0, new_start)
            node.SetNthControlPointPositionWorld(1, new_end)
            node.EndModify(wasModified)
        
        self.log("Elongated T4 tangent for R2 placement")
        self.r2StatusLabel.setText("Status: T4 elongated. Refresh R2 status when ready.")
        self.showDialogOnTop("T4 elongated by 100mm in both directions.\n\nRefresh R2 status when ready.")
    
    def refreshR2Status(self):
        """Refresh the status of R2 point (READ ONLY - never creates)"""
        self.log("Refreshing R2 status")
        
        # Clear stored R2 point
        if "R2" in self.points:
            del self.points["R2"]
        
        r2_found = False
        r2_position = None
        r2_source = None
        
        # ONLY check existing landmarks - NEVER create
        if self.landmarksNode:
            for i in range(self.landmarksNode.GetNumberOfControlPoints()):
                label = self.landmarksNode.GetNthControlPointLabel(i)
                self.log(f"Point {i}: '{label}'")
                
                # Look for R2 (exact match)
                if label == "R2" or label.lower() == "r2":
                    pos = [0.0, 0.0, 0.0]
                    self.landmarksNode.GetNthControlPointPositionWorld(i, pos)
                    r2_found = True
                    r2_position = pos
                    r2_source = f"landmarks node (index {i})"
                    self.log(f"Found R2 at index {i} (LPS): [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
                    
                    # Convert to RAS for display (flip Y and Z signs)
                    ras_pos = [pos[0], -pos[1], -pos[2]]
                    self.log(f"RAS equivalent: [{ras_pos[0]:.3f}, {ras_pos[1]:.3f}, {ras_pos[2]:.3f}]")
                    break
        
        if r2_found and r2_position is not None:
            self.points["R2"] = r2_position
            
            # Calculate RAS for display
            ras_x = r2_position[0]
            ras_y = -r2_position[1]
            ras_z = -r2_position[2]
            
            self.r2StatusLabel.setText(
                f"R2 Status: Found at\n"
                f"  LPS: [{r2_position[0]:.1f}, {r2_position[1]:.1f}, {r2_position[2]:.1f}]\n"
                f"  RAS: [{ras_x:.1f}, {ras_y:.1f}, {ras_z:.1f}]\n"
                f"Adjust in 3D view if needed, then click Confirm."
            )
            self.r2StatusLabel.setStyleSheet("padding: 10px; background-color: #ccffcc; border-radius: 5px;")
            self.confirmR2Button.setEnabled(True)
        else:
            self.r2StatusLabel.setText(
                "R2 Status: NOT FOUND.\n\n"
                "Please add a point labeled 'R2' to your Gerasimow_landmarks node.\n"
                "Use Slicer's Markups tools to add the point where T4 crosses the soft tissue."
            )
            self.r2StatusLabel.setStyleSheet("padding: 10px; background-color: #ffcccc; border-radius: 5px;")
            self.confirmR2Button.setEnabled(False)
            self.calculateErrorsButton.setEnabled(False)
    
    def onConfirmR2Placed(self):
        """Confirm that R2 is correctly placed"""
        if "R2" not in self.points:
            self.showDialogOnTop("R2 point not found. Please add 'R2' point to your landmarks node first.", "Warning", "warning")
            return
        
        self.log("R2 placement confirmed")
        pos = self.points["R2"]
        
        # Calculate RAS for display
        ras_x = pos[0]
        ras_y = -pos[1]
        ras_z = -pos[2]
        
        self.r2StatusLabel.setText(
            f"R2 Status: CONFIRMED\n"
            f"  LPS: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]\n"
            f"  RAS: [{ras_x:.1f}, {ras_y:.1f}, {ras_z:.1f}]"
        )
        self.r2StatusLabel.setStyleSheet("padding: 10px; background-color: #ccffcc; border-radius: 5px; font-weight: bold;")
        self.confirmR2Button.setEnabled(False)
        self.calculateErrorsButton.setEnabled(True)
        self.stepStatusLabel.setText("Status: R2 confirmed. Click 'Compare True vs Predicted' to calculate errors.")
        self.showDialogOnTop(f"R2 confirmed!\n\nLPS: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]\nRAS: [{ras_x:.1f}, {ras_y:.1f}, {ras_z:.1f}]\n\nNow click 'Compare True vs Predicted'.")
    
    def onCalculateErrorsClicked(self):
        """Calculate all 8 prediction errors based on different tangent intersections"""
        self.clearResults()
        self.log("Calculating all prediction errors...")
        
        if not self.landmarksNode:
            self.showDialogOnTop("Landmarks node not found.", "Warning", "warning")
            return
        
        # Find true pronasale (original landmark)
        true_prn_index = -1
        for i in range(self.landmarksNode.GetNumberOfControlPoints()):
            label = self.landmarksNode.GetNthControlPointLabel(i)
            if label.lower() == "pronasale" or label.lower() == "prn":
                true_prn_index = i
                break
        
        if true_prn_index < 0:
            self.showDialogOnTop("Could not find true 'pronasale' landmark for comparison.", "Warning", "warning")
            return
        
        true_prn = np.zeros(3)
        self.landmarksNode.GetNthControlPointPositionWorld(true_prn_index, true_prn)
        
        # Calculate all intersection points from tangents
        intersections = self.calculateAllIntersections()
        
        if not intersections:
            self.showDialogOnTop("Could not calculate tangent intersections. Please ensure tangents are properly placed.", "Warning", "warning")
            return
        
        # Calculate 8 errors:
        # 1-4: prn (true pronasale) vs each predicted point
        # 5-8: R2 vs each predicted point
        
        error_pairs = [
            ("prn T1-T2 pred error", "prn", "T1-T2"),
            ("prn T1-T4 pred error", "prn", "T1-T4"),
            ("prn T3-T2 pred error", "prn", "T3-T2"),
            ("prn T3-T4 pred error", "prn", "T3-T4"),
            ("R2 T1-T2 pred error", "R2", "T1-T2"),
            ("R2 T1-T4 pred error", "R2", "T1-T4"),
            ("R2 T3-T2 pred error", "R2", "T3-T2"),
            ("R2 T3-T4 pred error", "R2", "T3-T4")
        ]
        
        # Get R2 position if available
        r2_pos = None
        if "R2" in self.points:
            r2_pos = np.array(self.points["R2"])
        
        for error_name, reference_type, intersection_name in error_pairs:
            # Get the predicted point from intersections
            predicted_point = intersections.get(intersection_name)
            if predicted_point is None:
                self.log(f"Warning: Could not find intersection {intersection_name}")
                continue
            
            # Get the reference point (either true prn or R2)
            if reference_type == "prn":
                reference_point = true_prn
            else:  # R2
                if r2_pos is None:
                    self.log(f"Warning: R2 point not available for {error_name}")
                    continue
                reference_point = r2_pos
            
            error_distance = np.linalg.norm(predicted_point - reference_point)
            
            self.storeMeasurement(error_name, error_distance, "mm", is_error=True)
            self.storeCoordinate(error_name, predicted_point.tolist(), reference_point.tolist())
            
            # Create error visualization line
            line_name = f"error_{error_name.replace(' ', '_')}"
            try:
                error_line = slicer.util.getNode(line_name)
                error_line.RemoveAllControlPoints()
            except:
                error_line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', line_name)
                error_line.GetDisplayNode().SetSelectedColor(1.0, 0.0, 0.0)
            
            error_line.AddControlPoint(reference_point)
            error_line.AddControlPoint(predicted_point)
            
            self.log(f"{error_name}: {error_distance:.2f} mm")
        
        self.r2StatusLabel.setText("All errors calculated! Check Results tab.")
        self.showDialogOnTop("All 8 prediction errors calculated!\n\nCheck Results tab for details.")
        
        # Auto-navigate to results
        reply = self.showConfirmDialogOnTop("Errors calculated. View results now?")
        if reply:
            self.currentStep = 6  # Step 7
            self.updateStepUI()
    
    def calculateAllIntersections(self):
        """Calculate all tangent intersection points"""
        intersections = {}
        
        # Get all tangents
        t1 = self.tangents.get("T1")
        t2 = self.tangents.get("T2")
        t3 = self.tangents.get("T3")
        t4 = self.tangents.get("T4")
        
        if not all([t1, t2, t3, t4]):
            self.log("Warning: Not all tangents (T1, T2, T3, T4) are available")
            return intersections
        
        # Get start and end points for each tangent
        t1_start = np.array(t1['start'])
        t1_end = np.array(t1['end'])
        t2_start = np.array(t2['start'])
        t2_end = np.array(t2['end'])
        t3_start = np.array(t3['start'])
        t3_end = np.array(t3['end'])
        t4_start = np.array(t4['start'])
        t4_end = np.array(t4['end'])
        
        # Calculate direction vectors
        t1_dir = t1_end - t1_start
        t2_dir = t2_end - t2_start
        t3_dir = t3_end - t3_start
        t4_dir = t4_end - t4_start
        
        # Helper function to find intersection of two lines
        def find_intersection(p1, d1, p2, d2):
            A = np.array([d1, -d2]).T
            b = p2 - p1
            try:
                t = np.linalg.lstsq(A, b, rcond=None)[0]
                return p1 + t[0] * d1
            except:
                return None
        
        # Calculate all 4 intersections
        # T1-T2
        intersections["T1-T2"] = find_intersection(t1_start, t1_dir, t2_start, t2_dir)
        # T1-T4
        intersections["T1-T4"] = find_intersection(t1_start, t1_dir, t4_start, t4_dir)
        # T3-T2
        intersections["T3-T2"] = find_intersection(t3_start, t3_dir, t2_start, t2_dir)
        # T3-T4
        intersections["T3-T4"] = find_intersection(t3_start, t3_dir, t4_start, t4_dir)
        
        # Log results
        for name, point in intersections.items():
            if point is not None:
                self.log(f"Intersection {name}: {point}")
            else:
                self.log(f"Intersection {name}: Failed to calculate")
        
        return intersections
    
    def createStep7_Results(self):
        """Step 7: Results and Export"""
        widget = qt.QWidget()
        layout = qt.QVBoxLayout(widget)
        layout.setSpacing(15)
        
        title = qt.QLabel("Step 7: Results and Export")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Measurements Table
        measurementsLabel = qt.QLabel("<b>📏 Measurements (Distances and Angles)</b>")
        measurementsLabel.setStyleSheet("font-size: 14px;")
        layout.addWidget(measurementsLabel)
        
        instructionsLabel = qt.QLabel(
            "Prediction errors are <span style='background-color: #ffffcc;'>highlighted in yellow</span>."
        )
        instructionsLabel.setWordWrap(True)
        layout.addWidget(instructionsLabel)
        
        self.measurementsTable = qt.QTableWidget()
        self.measurementsTable.setColumnCount(3)
        self.measurementsTable.setHorizontalHeaderLabels(["Measurement", "Value", "Unit"])
        self.measurementsTable.horizontalHeader().setStretchLastSection(False)
        try:
            self.measurementsTable.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
        except:
            self.measurementsTable.horizontalHeader().setResizeMode(0, qt.QHeaderView.Stretch)
        self.measurementsTable.setMinimumHeight(200)
        self.measurementsTable.setAlternatingRowColors(True)
        layout.addWidget(self.measurementsTable)
        
        # Coordinates Table
        coordinatesLabel = qt.QLabel("<b>📍 Coordinates Comparison (Predicted vs True)</b>")
        coordinatesLabel.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(coordinatesLabel)
        
        self.coordinatesTable = qt.QTableWidget()
        self.coordinatesTable.setColumnCount(8)
        self.coordinatesTable.setHorizontalHeaderLabels([
            "Landmark",
            "Predicted X", "Predicted Y", "Predicted Z",
            "True X", "True Y", "True Z",
            "3D Error (mm)"
        ])
        try:
            self.coordinatesTable.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
        except:
            self.coordinatesTable.horizontalHeader().setResizeMode(0, qt.QHeaderView.Stretch)
        self.coordinatesTable.setMinimumHeight(150)
        self.coordinatesTable.setAlternatingRowColors(True)
        layout.addWidget(self.coordinatesTable)
        
        # Copy Buttons
        buttonLayout = qt.QHBoxLayout()
        
        self.copyMeasurementsButton = qt.QPushButton("📋 Copy Measurements")
        self.copyMeasurementsButton.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; font-weight: bold;")
        self.copyMeasurementsButton.clicked.connect(self.onCopyMeasurements)
        buttonLayout.addWidget(self.copyMeasurementsButton)
        
        self.copyCoordinatesButton = qt.QPushButton("📋 Copy Coordinates")
        self.copyCoordinatesButton.setStyleSheet("background-color: #3498db; color: white; padding: 8px; font-weight: bold;")
        self.copyCoordinatesButton.clicked.connect(self.onCopyCoordinates)
        buttonLayout.addWidget(self.copyCoordinatesButton)
        
        layout.addLayout(buttonLayout)
        
        # Finish button
        self.finishButton = qt.QPushButton("✓ Finish and Close")
        self.finishButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 12px;")
        self.finishButton.clicked.connect(self.onFinish)
        layout.addWidget(self.finishButton)
        
        self.step7StatusLabel = qt.QLabel("Status: Review your results above.")
        self.step7StatusLabel.setWordWrap(True)
        self.step7StatusLabel.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.step7StatusLabel)
        
    
        self.stepStack.addWidget(widget)
    
    # ========================================================================
    # NAVIGATION METHODS
    # ========================================================================
    def onPrevButtonClicked(self):
        """Go to previous step"""
        if self.currentStep > 0:
            self.currentStep -= 1
            self.updateStepUI()
    
    def onNextButtonClicked(self):
        """Go to next step"""
        if self.currentStep < self.stepStack.count - 1:
            # Validation before moving forward
            if not self.validateCurrentStep():
                return
            self.currentStep += 1
            self.updateStepUI()
    
    def updateStepUI(self):
        """Update the UI for the current step"""
        self.stepStack.setCurrentIndex(self.currentStep)

        # Update the step label and nav buttons first
        self.stepLabel.setText(f"Step {self.currentStep + 1}/{self.totalSteps}")
        self.prevButton.setEnabled(self.currentStep > 0)

        if self.currentStep == self.totalSteps - 1:
            self.nextButton.setText("Finish")
        else:
            self.nextButton.setText("Next ▶")

        # Update status label based on current step
        step_names = ["Load Landmarks", "Create Plane", "Visualization", "Setup",
                    "Tangents", "R2 Placement", "Results"]
        self.stepStatusLabel.setText(f"📍 Current: {step_names[self.currentStep]} - Follow instructions above")

        # Resize the window to fit the current step's content.
        # We can't rely on QStackedWidget's sizeHint (it returns the max
        # of all pages), so we measure the current page directly.
        current_page = self.stepStack.currentWidget()
        if current_page is not None:
            current_page.adjustSize()
            step_height = current_page.sizeHint.height

            # Budget for: top bar (~40) + nav (~40) + separator (~5)
            # + status label (~45) + log (~35) + margins/padding (~40)
            chrome_height = 200

            total_height = step_height + chrome_height

            # Clamp so the window never opens absurdly small or off-screen
            total_height = max(total_height, 400)
            total_height = min(total_height, 900)

            self.mainWidget.resize(self.mainWidget.width, total_height)
    
    def validateCurrentStep(self):
        """Validate current step before moving to next"""
        if self.currentStep == 0:
            # Step 1: Check if landmarks are loaded
            if not self.landmarksNode:
                self.showDialogOnTop("Please load landmarks before continuing.", "Warning", "warning")
                return False
        elif self.currentStep == 1:
            # Step 2: Check if plane is created
            if not self.planeNode:
                self.showDialogOnTop("Please create a reference plane before continuing.", "Warning", "warning")
                return False
        return True
    
    # ========================================================================
    # STEP 5: TANGENT CREATION METHODS
    # ========================================================================
    def onT1T2ShortcutToggled(self, checked):
        """Toggle T1-T2 shortcut mode"""
        self.t4Group.setVisible(not checked)
        if checked:
            self.log("T1-T2 Shortcut mode enabled")
            self.tangentInstructionLabel.setText(
                "Shortcut mode: Only T1 and T2 tangents will be used."
            )
        else:
            self.log("Full tangent mode enabled")
            self.tangentInstructionLabel.setText(
                "Full mode: All tangents (T1, T2, T3, T4R, T4L) will be used."
            )
    
    def createTangentLine(self, name, start, end, color):
        """Create a tangent line node with specified color"""
        # Remove existing node if present
        try:
            oldNode = slicer.util.getNode(name)
            slicer.mrmlScene.RemoveNode(oldNode)
        except:
            pass
        
        # Create new line
        lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
        lineNode.AddControlPoint(start)
        lineNode.AddControlPoint(end)
        
        # Set color
        displayNode = lineNode.GetDisplayNode()
        displayNode.SetSelectedColor(color[0], color[1], color[2])
        displayNode.SetColor(color[0], color[1], color[2])
        displayNode.SetLineThickness(0.5)
        displayNode.SetPointLabelsVisibility(True)
        
        # Store references
        self.tangentNodes[name] = lineNode
        self.tangents[name] = {'start': start.tolist(), 'end': end.tolist()}
        
        self.log(f"Created {name} tangent line")
        
        # Deactivate placement mode
        slicer.modules.markups.logic().StartPlaceMode(0)
        slicer.modules.markups.logic().SetActiveListID(None)
    
    def onRegenerateTangentsClicked(self):
        """Generate default tangent lines"""
        if not self.planeNode:
            self.showDialogOnTop("Please create a plane first (Step 2).", "Warning", "warning")
            return
        
        try:
            self.step5StatusLabel.setText("Status: Generating tangent lines...")
            slicer.app.processEvents()
            
            # Color mapping
            colors = {
                "T1": [1.0, 0.8, 0.0],   # Yellow
                "T2": [0.0, 1.0, 0.0],   # Green
                "T3": [0.2, 0.4, 1.0]    # Blue
            }
            
            # Get plane information
            planeOrigin = np.zeros(3)
            self.planeNode.GetOriginWorld(planeOrigin)
            planeNormal = np.zeros(3)
            self.planeNode.GetNormalWorld(planeNormal)
            
            # Create tangents with different default positions
            # T1 - Upper nasal bone region
            t1_center = planeOrigin + np.array([0, 30, 40])
            t1_start = t1_center + np.array([-30, 0, 0])
            t1_end = t1_center + np.array([30, 0, 0])
            self.createTangentLine("T1", t1_start, t1_end, colors["T1"])
            
            # T2 - Anterior nasal spine region
            t2_center = planeOrigin + np.array([0, -20, 30])
            t2_start = t2_center + np.array([-30, 0, 0])
            t2_end = t2_center + np.array([30, 0, 0])
            self.createTangentLine("T2", t2_start, t2_end, colors["T2"])
            
            if not self.t1t2ShortcutCheckbox.checked:
                # T3 - Last 1-2mm of nasal bone
                t3_center = planeOrigin + np.array([0, 10, 15])
                t3_start = t3_center + np.array([-20, 0, 0])
                t3_end = t3_center + np.array([20, 0, 0])
                self.createTangentLine("T3", t3_start, t3_end, colors["T3"])
            
            self.step5StatusLabel.setText("Status: Default tangents created! Adjust them in the 3D view as needed.")
            self.log("Generated default tangent lines")
            
            # Show instructions for manual adjustment
            self.showDialogOnTop(
                "Tangents created!\n\n"
                "• You can drag the end points in the 3D view to adjust them\n"
                "• Double-click a point to move it precisely\n"
                "• For T4R/T4L, use the 'Create Empty' buttons\n"
                "• After adding points to T4R/T4L, click 'Refresh T4 Status' then 'Calculate T4'"
            )
            
        except Exception as e:
            self.step5StatusLabel.setText(f"Status: Error generating tangents! {e}")
            self.showDialogOnTop(f"Failed to generate tangents: {e}", "Error", "error")
    
    def onExtendTangentsClicked(self):
        """Extend tangent lines"""
        elongation_distance = 50  # mm
        
        tangents_to_extend = ["T1", "T2"]
        if not self.t1t2ShortcutCheckbox.checked:
            tangents_to_extend.extend(["T3", "T4R", "T4L", "T4"])
        
        for tangent_name in tangents_to_extend:
            if tangent_name in self.tangents:
                tangent = self.tangents[tangent_name]
                start = np.array(tangent['start'])
                end = np.array(tangent['end'])
                
                direction = end - start
                direction_normalized = direction / np.linalg.norm(direction)
                
                new_start = start - elongation_distance * direction_normalized
                new_end = end + elongation_distance * direction_normalized
                
                self.tangents[tangent_name]['start'] = new_start.tolist()
                self.tangents[tangent_name]['end'] = new_end.tolist()
                
                if tangent_name in self.tangentNodes:
                    node = self.tangentNodes[tangent_name]
                    wasModified = node.StartModify()
                    node.SetNthControlPointPositionWorld(0, new_start)
                    node.SetNthControlPointPositionWorld(1, new_end)
                    node.EndModify(wasModified)
        
        self.log("Extended tangent lines")
        self.step5StatusLabel.setText("Status: Tangents elongated.")
    
    def onFindIntersectionsClicked(self):
        """Find intersections between tangent lines"""
        self.log("Finding intersections...")
        
        if self.t1t2ShortcutCheckbox.checked:
            # T1-T2 Shortcut mode
            self.runT1T2Shortcut()
        else:
            # Full mode - find all intersections including T4
            self.findAllIntersections()
    
    def runT1T2Shortcut(self):
        """Run the T1-T2 shortcut workflow (only T1-T2 intersection)"""
        self.clearResults()
        self.log("=== Starting T1-T2 Shortcut Workflow ===")
        
        # Check if T1 and T2 exist
        if "T1" not in self.tangents or "T2" not in self.tangents:
            self.showDialogOnTop("T1 and T2 tangents must exist for shortcut mode.", "Warning", "warning")
            return
        
        # Get T1 and T2 data
        t1_start = np.array(self.tangents["T1"]['start'])
        t1_end = np.array(self.tangents["T1"]['end'])
        t2_start = np.array(self.tangents["T2"]['start'])
        t2_end = np.array(self.tangents["T2"]['end'])
        
        t1_dir = t1_end - t1_start
        t2_dir = t2_end - t2_start
        
        # Find T1-T2 intersection
        A = np.array([t1_dir, -t2_dir]).T
        b = t2_start - t1_start
        try:
            t = np.linalg.lstsq(A, b, rcond=None)[0]
            intersection_point = t1_start + t[0] * t1_dir
        except:
            self.showDialogOnTop("Could not calculate T1-T2 intersection.", "Warning", "warning")
            return
        
        self.log(f"T1-T2 intersection found at: {intersection_point}")
        
        # Create predicted pronasale point (T1-T2 method)
        try:
            pred_prn_node = slicer.util.getNode('T1-T2_predicted_pronasale')
            pred_prn_node.RemoveAllControlPoints()
        except:
            pred_prn_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'T1-T2_predicted_pronasale')
            pred_prn_node.GetDisplayNode().SetSelectedColor(1.0, 0.5, 0.0)
        
        pred_prn_node.AddControlPoint(intersection_point, 'T1-T2 pred')
        
        # Calculate error against true pronasale (if available)
        if self.landmarksNode:
            prn_index = self.findPointByName(self.landmarksNode, "pronasale")
            if prn_index >= 0:
                actual_prn = np.zeros(3)
                self.landmarksNode.GetNthControlPointPositionWorld(prn_index, actual_prn)
                
                error_distance = np.linalg.norm(intersection_point - actual_prn)
                
                self.storeMeasurement("T1-T2 Prediction Error", error_distance, "mm", is_error=True)
                self.storeCoordinate("Pronasale (T1-T2)", intersection_point.tolist(), actual_prn.tolist())
                
                self.log(f"T1-T2 prediction error: {error_distance:.2f} mm")
                
                # Create error line
                try:
                    error_line_node = slicer.util.getNode('T1-T2_prediction_error')
                    error_line_node.RemoveAllControlPoints()
                except:
                    error_line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'T1-T2_prediction_error')
                    error_line_node.GetDisplayNode().SetSelectedColor(1.0, 0.0, 0.0)
                
                error_line_node.AddControlPoint(actual_prn)
                error_line_node.AddControlPoint(intersection_point)
            else:
                self.log("True pronasale not found for error calculation")
        
        self.step5StatusLabel.setText("Status: T1-T2 shortcut complete! Check Results tab.")
        self.showDialogOnTop("T1-T2 Shortcut Complete!\nPrediction point created.\n\nUse Step 6 for full error analysis with R2.", "Information")
    
    def findAllIntersections(self):
        """Full mode – no table entries, only logging."""
        self.log("Full mode: Use 'Compare True vs. Predicted Points' to calculate 8 errors.")
        if "T1" in self.tangents and "T2" in self.tangents:
            self.log("T1 and T2 are available – intersection can be seen in the 3D view if you have drawn the lines.")
        if "T4" in self.tangents:
            self.log("T4 is available for R2 calculation in Step 6.")
        self.step5StatusLabel.setText("Status: Full mode ready. Go to Step 6 and click 'Compare True vs. Predicted Points'.")
    
    # ========================================================================
    # RESULT COPYING METHODS
    # ========================================================================
    def onCopyMeasurements(self):
        """Copy measurements table to clipboard"""
        try:
            clipboard_text = "Measurement\tValue\tUnit\n"
            
            for row in range(self.measurementsTable.rowCount):
                metric = self.measurementsTable.item(row, 0).text() if self.measurementsTable.item(row, 0) else ""
                value = self.measurementsTable.item(row, 1).text() if self.measurementsTable.item(row, 1) else ""
                unit = self.measurementsTable.item(row, 2).text() if self.measurementsTable.item(row, 2) else ""
                clipboard_text += f"{metric}\t{value}\t{unit}\n"
            
            from qt import QApplication
            app_clipboard = QApplication.clipboard()
            app_clipboard.setText(clipboard_text)
            self.showDialogOnTop("Measurements copied to clipboard!")
            
        except Exception as e:
            self.showDialogOnTop(f"Failed to copy measurements: {e}", "Error", "error")
    
    def onCopyCoordinates(self):
        """Copy coordinates table to clipboard"""
        try:
            clipboard_text = "Landmark\tPred X\tPred Y\tPred Z\tTrue X\tTrue Y\tTrue Z\t3D Error\n"
            
            for row in range(self.coordinatesTable.rowCount):
                row_data = []
                for col in range(self.coordinatesTable.columnCount):
                    item = self.coordinatesTable.item(row, col)
                    row_data.append(item.text() if item else "")
                clipboard_text += "\t".join(row_data) + "\n"
            
            from qt import QApplication
            app_clipboard = QApplication.clipboard()
            app_clipboard.setText(clipboard_text)
            self.showDialogOnTop("Coordinates copied to clipboard!")
            
        except Exception as e:
            self.showDialogOnTop(f"Failed to copy coordinates: {e}", "Error", "error")
    
    def onFinish(self):
        """Close the GUI"""
        # Clean up observers
        if hasattr(self, 'tangent_observers'):
            for tangent_name, observer_id in self.tangent_observers.items():
                if tangent_name in self.tangentNodes:
                    try:
                        self.tangentNodes[tangent_name].RemoveObserver(observer_id)
                    except:
                        pass
        
        self.log("Finishing Gerasimow's nose prediction workflow")
        self.mainWidget.close()
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    def syncWithScene(self):
        """Check scene for existing nodes"""
        self.log("Checking scene for existing nodes...")
        
        # Check for landmarks
        landmarksNode = slicer.util.getFirstNodeByName("Gerasimow_landmarks")
        if landmarksNode:
            self.landmarksNode = landmarksNode
            self.step1StatusLabel.setText("Status: Found existing 'Gerasimow_landmarks'.")
        
        # Check for plane
        planeNode = slicer.util.getFirstNodeByName("INB") or slicer.util.getFirstNodeByName("MSP")
        if planeNode:
            self.planeNode = planeNode
            self.step2StatusLabel.setText(f"Status: Found existing '{planeNode.GetName()}' plane.")
        
        # Check for bone model
        boneModel = slicer.util.getFirstNodeByName("Bone")
        if boneModel:
            self.boneModel = boneModel
            if hasattr(self, 'boneModelSelector'):
                self.boneModelSelector.setCurrentNode(boneModel)
        
        # Check for tangent lines
        tangent_names = ["T1", "T2", "T3", "T4R", "T4L", "T4"]
        for name in tangent_names:
            try:
                node = slicer.util.getNode(name)
                if node:
                    self.tangentNodes[name] = node
                    if node.GetNumberOfControlPoints() >= 2:
                        start = [0, 0, 0]
                        end = [0, 0, 0]
                        node.GetNthControlPointPositionWorld(0, start)
                        node.GetNthControlPointPositionWorld(1, end)
                        self.tangents[name] = {'start': start, 'end': end}
            except:
                pass
        
        # Check for T4 status
        self.updateT4StatusFromExistingLines()
        
        # Check for R2 point in landmarks node
        self.refreshR2Status()
    
    def findPointByName(self, node, name):
        """Find point index by name in a markups node"""
        if not node:
            return -1
        for i in range(node.GetNumberOfControlPoints()):
            label = node.GetNthControlPointLabel(i)
            if name.lower() in label.lower():
                return i
        return -1
    
    def getPos(self, name, node=None):
        """Get position of a landmark by name"""
        landmark_node = node if node is not None else self.landmarksNode
        if not landmark_node:
            raise ValueError("Landmarks node not found.")
        
        for i in range(landmark_node.GetNumberOfControlPoints()):
            if name.lower() in landmark_node.GetNthControlPointLabel(i).lower():
                pos = np.zeros(3)
                landmark_node.GetNthControlPointPositionWorld(i, pos)
                return pos
        
        raise ValueError(f"Landmark '{name}' not found!")
    
    def projectPointOntoPlane(self, point, planeOrigin, planeNormal):
        """Project a point onto a plane"""
        v = point - planeOrigin
        dist = np.dot(v, planeNormal)
        projected = point - dist * planeNormal
        return projected
    
    def storeMeasurement(self, name, value, unit="mm", is_error=False):
        """Store a measurement for the results table"""
        self.all_measurements[name] = {
            "value": value,
            "unit": unit,
            "is_error": is_error
        }
        self.updateResultsTables()
    
    def storeCoordinate(self, landmark_name, predicted_coords, true_coords=None):
        """Store coordinates for comparison"""
        self.all_coordinates[landmark_name] = {
            "predicted": predicted_coords,
            "true": true_coords
        }
        self.updateResultsTables()
    
    def clearResults(self):
        """Clear all stored measurements and coordinates before a new calculation."""
        self.all_measurements.clear()
        self.all_coordinates.clear()
        self.updateResultsTables()
        self.log("Cleared previous results tables.")
    
    def updateResultsTables(self):
        """Update both results tables with current data"""
        # Update Measurements Table
        self.measurementsTable.setRowCount(0)
        
        for name, data in self.all_measurements.items():
            row = self.measurementsTable.rowCount
            self.measurementsTable.insertRow(row)
            
            nameItem = qt.QTableWidgetItem(name)
            valueItem = qt.QTableWidgetItem("{:.2f}".format(data["value"]))
            unitItem = qt.QTableWidgetItem(data["unit"])
            
            if data.get("is_error", False):
                yellow = qt.QColor(255, 255, 200)
                nameItem.setBackground(yellow)
                valueItem.setBackground(yellow)
                unitItem.setBackground(yellow)
            
            self.measurementsTable.setItem(row, 0, nameItem)
            self.measurementsTable.setItem(row, 1, valueItem)
            self.measurementsTable.setItem(row, 2, unitItem)
        
        # Update Coordinates Table
        self.coordinatesTable.setRowCount(0)
        
        for landmark, data in self.all_coordinates.items():
            row = self.coordinatesTable.rowCount
            self.coordinatesTable.insertRow(row)
            
            predicted_coords = data["predicted"]
            true_coords = data.get("true")
            
            nameItem = qt.QTableWidgetItem(landmark)
            predXItem = qt.QTableWidgetItem("{:.2f}".format(predicted_coords[0]))
            predYItem = qt.QTableWidgetItem("{:.2f}".format(predicted_coords[1]))
            predZItem = qt.QTableWidgetItem("{:.2f}".format(predicted_coords[2]))
            
            self.coordinatesTable.setItem(row, 0, nameItem)
            self.coordinatesTable.setItem(row, 1, predXItem)
            self.coordinatesTable.setItem(row, 2, predYItem)
            self.coordinatesTable.setItem(row, 3, predZItem)
            
            if true_coords is not None:
                trueXItem = qt.QTableWidgetItem("{:.2f}".format(true_coords[0]))
                trueYItem = qt.QTableWidgetItem("{:.2f}".format(true_coords[1]))
                trueZItem = qt.QTableWidgetItem("{:.2f}".format(true_coords[2]))
                
                error_3d = np.linalg.norm(np.array(predicted_coords) - np.array(true_coords))
                errorItem = qt.QTableWidgetItem("{:.2f}".format(error_3d))
                
                yellow = qt.QColor(255, 255, 200)
                errorItem.setBackground(yellow)
                
                self.coordinatesTable.setItem(row, 4, trueXItem)
                self.coordinatesTable.setItem(row, 5, trueYItem)
                self.coordinatesTable.setItem(row, 6, trueZItem)
                self.coordinatesTable.setItem(row, 7, errorItem)
            else:
                for col in range(4, 8):
                    self.coordinatesTable.setItem(row, col, qt.QTableWidgetItem("-"))
    
    # ========================================================================
    # ADDITIONAL HANDLERS
    # ========================================================================
    def onDownloadLandmarksClicked(self):
        """Download landmarks from GitHub"""
        url = "https://github.com/user-attachments/files/28797197/Gerasimow_landmarks.mrk.json"
        self.step1StatusLabel.setText("Status: Downloading...")
        slicer.app.processEvents()
        
        try:
            with urllib.request.urlopen(url) as response:
                fileData = response.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mrk.json', mode='wb') as tempFile:
                tempFile.write(fileData)
                tempFilePath = tempFile.name
            
            loadedNode = slicer.util.loadMarkups(tempFilePath)
            if loadedNode:
                loadedNode.SetName("Gerasimow_landmarks")
                self.landmarksNode = loadedNode
                self.step1StatusLabel.setText("Status: Successfully downloaded and loaded landmarks!")
                self.log("Downloaded landmarks from GitHub")
            
            if os.path.exists(tempFilePath):
                os.remove(tempFilePath)
        except Exception as e:
            self.step1StatusLabel.setText(f"Status: Error downloading! {e}")
            self.showDialogOnTop(f"Failed to download: {e}", "Error", "error")
    
    def onLoadLocalLandmarksClicked(self):
        """Load landmarks from local file"""
        fileName, _ = qt.QFileDialog.getOpenFileName(self.mainWidget, "Load Landmarks", "", "Markup JSON Files (*.mrk.json)")
        if fileName:
            loadedNode = slicer.util.loadMarkups(fileName)
            if loadedNode:
                loadedNode.SetName("Gerasimow_landmarks")
                self.landmarksNode = loadedNode
                self.step1StatusLabel.setText("Status: Successfully loaded local landmarks!")
                self.log(f"Loaded landmarks from {fileName}")
    
    def onCreatePlaneClicked(self):
        """Create reference plane"""
        if not self.landmarksNode:
            self.syncWithScene()
        if not self.landmarksNode:
            self.step2StatusLabel.setText("Status: Error! Go back and load landmarks first.")
            return
        
        choice_index = self.landmarkBundleCombo.currentIndex
        if choice_index == 0:
            self.step2StatusLabel.setText("Status: Please select a plane method.")
            return
        
        self.step2StatusLabel.setText("Status: Creating plane...")
        slicer.app.processEvents()
        
        try:
            plane_name = ""
            if choice_index == 1:
                # INB plane
                plane_name = "INB"
                p_inion = self.getPos("inion")
                p_nasion = self.getPos("nasion")
                p_bregma = self.getPos("bregma")
                
                v1 = p_nasion - p_inion
                v2 = p_bregma - p_inion
                normal = np.cross(v1, v2)
                origin = p_inion
            elif choice_index == 2:
                # MSP plane
                plane_name = "MSP"
                required = ["nasion", "acanthion", "rhinion"]
                points = np.array([self.getPos(name) for name in required])
                centroid = np.mean(points, axis=0)
                covariance_matrix = np.cov(points - centroid, rowvar=False)
                eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
                normal = eigenvectors[:, np.argmin(eigenvalues)]
                origin = centroid
            
            # Remove old plane if exists
            try:
                oldPlane = slicer.util.getNode(plane_name)
                slicer.mrmlScene.RemoveNode(oldPlane)
            except:
                pass
            
            # Create new plane
            planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', plane_name)
            planeNode.SetOrigin(origin)
            planeNode.SetNormal(normal)
            planeNode.SetSize(300, 300)
            planeNode.GetDisplayNode().SetOpacity(0.5)
            
            self.planeNode = planeNode
            self.step2StatusLabel.setText(f"Status: Successfully created '{plane_name}' plane!")
            self.log(f"Created {plane_name} plane")
            
        except Exception as e:
            self.step2StatusLabel.setText(f"Status: Error creating plane! {e}")
            self.showDialogOnTop(f"Failed to create plane: {e}", "Error", "error")
    
    def onConfirmSegmentation(self, node):
        """Confirm bone model selection"""
        if node:
            self.boneModel = node
            self.step3StatusLabel.setText(f"Status: Confirmed '{node.GetName()}' as bone model!")
            self.log(f"Confirmed bone model: {node.GetName()}")
        else:
            self.boneModel = None
            self.step3StatusLabel.setText("Status: Waiting for bone model selection.")
    
    def onOpenSegmentEditor(self):
        """Open the Segment Editor module"""
        slicer.util.selectModule('SegmentEditor')
        self.log("Opened Segment Editor module")
        self.step3StatusLabel.setText("Status: Segment Editor opened. Follow the instructions above.")
    
    def onOpenVolumeRendering(self):
        """Open the Volume Rendering module"""
        slicer.util.selectModule('VolumeRendering')
        self.log("Opened Volume Rendering module for manual method")
        self.step3StatusLabel.setText("Status: Volume Rendering opened. Use Display ROI to visualize the skull.")


# Helper function for unit vector
def _unit(v):
    """Return unit vector"""
    n = np.linalg.norm(v)
    return (v / n) if n > 1e-8 else np.array([1.0, 0.0, 0.0])


# ========================================================================
# SEQUENTIAL WORKFLOW SUPPORT
# ========================================================================

# Store the original onFinish method
original_onFinish = None
sequential_mode = False
next_callback = None

def enable_sequential_mode(callback=None):
    """Enable sequential workflow mode"""
    global sequential_mode, next_callback, original_onFinish
    sequential_mode = True
    next_callback = callback
    
    # Modify the GUI to add completion button if not already there
    if hasattr(gui, 'finishButton'):
        gui.finishButton.setText("✓ Complete Gerasimow & Continue")
        gui.finishButton.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 12px;")
        
        # Store original onFinish and replace with sequential version
        original_onFinish = gui.onFinish
        
        def sequential_finish():
            print("Gerasimow completed, continuing to next tool...")
            original_onFinish()
            if next_callback:
                next_callback()
        
        gui.onFinish = sequential_finish


# Auto-run if script is executed directly
if __name__ == "__main__":
    gui = GerasimowNosePredictor()

```