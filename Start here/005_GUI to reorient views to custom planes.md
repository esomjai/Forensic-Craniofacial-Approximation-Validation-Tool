# Reorient your Slicer views to custom planes

```python
import slicer
import qt
import numpy as np
import urllib.request
import os
import tempfile

# ==============================================================================
# Main GUI Class with Compact Mode and Resizable Panels
# ==============================================================================
class ReorientViewsGUI:
    def __init__(self):
        """Initialize the GUI widget."""
        self.main_widget = qt.QWidget(slicer.util.mainWindow())
        self.main_widget.setWindowFlags(qt.Qt.Tool)
        self.main_widget.setObjectName("ReorientViewsGUIWidget")
        self.main_widget.setWindowTitle("Re-orient Slice Views")
        self.main_widget.setMinimumWidth(400)
        
        # Main layout
        self.main_layout = qt.QVBoxLayout(self.main_widget)
        
        # --- Header with Title and Compact Toggle ---
        header_layout = qt.QHBoxLayout()
        
        title_label = qt.QLabel("Re-orient Slice Views")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Compact mode toggle button
        self.compact_button = qt.QPushButton("⤡ Compact Mode")
        self.compact_button.setCheckable(True)
        self.compact_button.setToolTip("Toggle compact mode to show/hide detailed information")
        self.compact_button.setFixedWidth(120)
        self.compact_button.clicked.connect(self.toggle_compact_mode)
        header_layout.addWidget(self.compact_button)
        
        self.main_layout.addLayout(header_layout)
        
        # --- Create a scroll area for the main content ---
        self.scroll_area = qt.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(qt.QFrame.NoFrame)
        self.main_layout.addWidget(self.scroll_area)
        
        # Container widget for scrollable content
        self.content_widget = qt.QWidget()
        self.content_layout = qt.QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        
        # --- Create splitter for resizable sections ---
        self.splitter = qt.QSplitter(qt.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.content_layout.addWidget(self.splitter)
        
        # --- Panel 1: Reference Image (Collapsible) ---
        self.image_group = qt.QGroupBox("📐 Coordinate System Reference")
        self.image_group.setCheckable(True)
        self.image_group.setChecked(True)
        self.image_group.setToolTip("Uncheck to hide the reference image")
        self.image_group.setStyleSheet("QGroupBox::indicator { width: 13px; height: 13px; }")
        
        image_layout = qt.QVBoxLayout(self.image_group)
        image_layout.setContentsMargins(10, 10, 10, 10)
        
        self.image_label = qt.QLabel()
        self.image_label.setAlignment(qt.Qt.AlignCenter)
        self.image_label.setMinimumHeight(150)
        self.image_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f8f8f8;")
        image_layout.addWidget(self.image_label)
        
        # Image size slider
        image_size_layout = qt.QHBoxLayout()
        image_size_layout.addWidget(qt.QLabel("Image Size:"))
        self.image_size_slider = qt.QSlider(qt.Qt.Horizontal)
        self.image_size_slider.setMinimum(150)
        self.image_size_slider.setMaximum(400)
        self.image_size_slider.setValue(250)
        self.image_size_slider.setToolTip("Adjust the size of the reference image")
        self.image_size_slider.valueChanged.connect(self.update_image_size)
        image_size_layout.addWidget(self.image_size_slider)
        
        self.image_size_label = qt.QLabel("250px")
        self.image_size_label.setFixedWidth(45)
        image_size_layout.addWidget(self.image_size_label)
        
        image_layout.addLayout(image_size_layout)
        
        self.splitter.addWidget(self.image_group)
        
        # --- Panel 2: Plane Selection ---
        self.selector_group = qt.QGroupBox("1. Select Reference Planes")
        self.selector_group.setCheckable(True)
        self.selector_group.setChecked(True)
        self.selector_group.setStyleSheet("QGroupBox::indicator { width: 13px; height: 13px; }")
        
        selector_layout = qt.QFormLayout(self.selector_group)
        selector_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create selectors with normal display
        self.axial_data = self.create_plane_selector_with_normal(
            "Axial (Red) :",
            "Select a transverse plane (normal along Z)."
        )
        self.sagittal_data = self.create_plane_selector_with_normal(
            "Sagittal (Yellow) :",
            "Select a median sagittal plane (normal along X)."
        )
        self.coronal_data = self.create_plane_selector_with_normal(
            "Coronal (Green) :",
            "Select a coronal plane (normal along Y)."
        )
        
        selector_layout.addRow(self.axial_data['label'], self.axial_data['selector_widget'])
        selector_layout.addRow(self.sagittal_data['label'], self.sagittal_data['selector_widget'])
        selector_layout.addRow(self.coronal_data['label'], self.coronal_data['selector_widget'])
        
        self.splitter.addWidget(self.selector_group)
        
        # --- Panel 3: Controls (Collapsible) ---
        self.controls_group = qt.QGroupBox("2. Controls")
        self.controls_group.setCheckable(True)
        self.controls_group.setChecked(True)
        self.controls_group.setStyleSheet("QGroupBox::indicator { width: 13px; height: 13px; }")
        
        controls_layout = qt.QVBoxLayout(self.controls_group)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        # Button row 1
        button_row1 = qt.QHBoxLayout()
        self.ortho_button = qt.QPushButton("🔍 Check Orthogonality")
        self.ortho_button.clicked.connect(self.check_orthogonality)
        button_row1.addWidget(self.ortho_button)
        
        # Auto-flip checkbox
        self.autoflip_check = qt.QCheckBox("🔄 Auto-flip to +Z, +X, +Y")
        self.autoflip_check.setToolTip(
            "If enabled, axial normal will point Superior (+Z), "
            "sagittal to Right (+X), coronal to Anterior (+Y)."
        )
        button_row1.addWidget(self.autoflip_check)
        controls_layout.addLayout(button_row1)
        
        # Apply button
        self.apply_button = qt.QPushButton("✅ Apply New Orientation")
        self.apply_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
        )
        self.apply_button.setToolTip("Re-orients the Red, Yellow, and Green slice views based on the selected planes.")
        self.apply_button.clicked.connect(self.run_reorientation)
        controls_layout.addWidget(self.apply_button)
        
        self.splitter.addWidget(self.controls_group)
        
        # --- Panel 4: Status (Collapsible) ---
        self.status_group = qt.QGroupBox("Status")
        self.status_group.setCheckable(True)
        self.status_group.setChecked(True)
        self.status_group.setStyleSheet("QGroupBox::indicator { width: 13px; height: 13px; }")
        
        status_layout = qt.QVBoxLayout(self.status_group)
        self.status_label = qt.QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.splitter.addWidget(self.status_group)
        
        # Set initial splitter sizes
        self.splitter.setSizes([200, 250, 150, 80])
        
        # --- Help button ---
        help_row = qt.QHBoxLayout()
        help_row.addStretch()
        help_button = qt.QPushButton("❓ Help")
        help_button.setFixedWidth(80)
        help_button.clicked.connect(self.show_help)
        help_row.addWidget(help_button)
        self.content_layout.addLayout(help_row)
        
        # Initialize image cache
        self._pixmap = None
        
        # --- NOW load the image (after all UI elements are created) ---
        # Use a timer to load the image after the UI is fully displayed
        qt.QTimer.singleShot(100, self.load_image_from_url)
        
        self.main_widget.show()
    
    def load_image_from_url(self, url=None):
        """Load an image from a URL and display it in the label."""
        if url is None:
            url = "https://raw.githubusercontent.com/esomjai/Forensic-Craniofacial-Approximation-Database/basics/images/Designer.png"
        
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.close()
            
            # Download the image
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                image_data = response.read()
            
            # Write to temporary file
            with open(temp_file.name, 'wb') as f:
                f.write(image_data)
            
            # Load into QPixmap
            pixmap = qt.QPixmap(temp_file.name)
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            if not pixmap.isNull():
                # Store the original pixmap
                self._pixmap = pixmap
                # Get the current slider value
                size = self.image_size_slider.value
                # Scale and display
                scaled_pixmap = pixmap.scaled(
                    size, int(size * 0.7),
                    qt.Qt.KeepAspectRatio,
                    qt.Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setToolTip("Reference coordinate system diagram")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("✅ Reference image loaded")
            else:
                self.show_fallback_image()
                
        except Exception as e:
            print(f"Could not load image from URL: {e}")
            self.show_fallback_image()
    
    def update_image_size(self, size):
        """Update the size of the reference image."""
        self.image_size_label.setText(f"{size}px")
        
        # Reload and rescale the image if we have it cached
        if hasattr(self, '_pixmap') and self._pixmap:
            scaled_pixmap = self._pixmap.scaled(
                size, int(size * 0.7),
                qt.Qt.KeepAspectRatio,
                qt.Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
    
    def show_fallback_image(self):
        """Display a text-based fallback diagram if image loading fails."""
        fallback_text = """
        ╔═══════════════════════════════════════════╗
        ║     COORDINATE SYSTEM REFERENCE          ║
        ╠═══════════════════════════════════════════╣
        ║        Superior (+Z)                     ║
        ║            ↑                            ║
        ║            |                            ║
        ║  Axial (Red) ← horizontal plane        ║
        ║            |                            ║
        ║Left ←---+→ Right (+X)                  ║
        ║            |                            ║
        ║        Inferior (-Z)                    ║
        ║                                         ║
        ║ • Sagittal (Yellow): normal X          ║
        ║ • Coronal (Green): normal Y            ║
        ╚═══════════════════════════════════════════╝
        """
        self.image_label.setText(fallback_text)
        self.image_label.setStyleSheet(
            "font-family: monospace; "
            "background-color: #f0f0f0; "
            "padding: 10px; "
            "border: 1px solid #cccccc;"
        )
        self.image_label.setToolTip("Fallback text diagram (image could not be loaded)")
        if hasattr(self, 'status_label'):
            self.status_label.setText("⚠️ Using fallback text diagram")
    
    def toggle_compact_mode(self):
        """Toggle compact mode - collapse all groups and adjust layout."""
        is_compact = self.compact_button.isChecked()
        
        if is_compact:
            self.compact_button.setText("⤢ Expand All")
            # Collapse all groups
            self.image_group.setChecked(False)
            self.selector_group.setChecked(False)
            self.controls_group.setChecked(False)
            self.status_group.setChecked(False)
            # Hide scroll area borders
            self.scroll_area.setFrameShape(qt.QFrame.NoFrame)
            # Reduce minimum height
            self.main_widget.setMinimumHeight(150)
        else:
            self.compact_button.setText("⤡ Compact Mode")
            # Expand all groups
            self.image_group.setChecked(True)
            self.selector_group.setChecked(True)
            self.controls_group.setChecked(True)
            self.status_group.setChecked(True)
            # Restore minimum height
            self.main_widget.setMinimumHeight(400)
    
    def create_plane_selector_with_normal(self, label_text, tooltip):
        """Creates a horizontal layout with plane selector, normal display, and flip button."""
        container = qt.QHBoxLayout()
        container.setSpacing(8)
        
        label = qt.QLabel(label_text)
        label.setFixedWidth(110)
        container.addWidget(label)
        
        selector = slicer.qMRMLNodeComboBox()
        selector.nodeTypes = ["vtkMRMLMarkupsPlaneNode"]
        selector.setMRMLScene(slicer.mrmlScene)
        selector.addEnabled = False
        selector.removeEnabled = False
        selector.noneEnabled = True
        selector.setToolTip(tooltip)
        container.addWidget(selector, 1)
        
        normal_label = qt.QLabel("( -, -, - )")
        normal_label.setFixedWidth(150)
        normal_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        container.addWidget(normal_label)
        
        flip_button = qt.QPushButton("↕")
        flip_button.setFixedWidth(30)
        flip_button.setToolTip("Flip the plane's normal direction")
        container.addWidget(flip_button)
        
        widget = qt.QWidget()
        widget.setLayout(container)
        
        data = {
            'label': label,
            'selector': selector,
            'selector_widget': widget,
            'normal_label': normal_label,
            'flip_button': flip_button,
        }
        
        def on_node_changed(node):
            self.update_normal_display(data)
        selector.connect('currentNodeChanged(vtkMRMLNode*)', on_node_changed)
        
        def on_flip_clicked():
            self.flip_plane_normal(data)
        flip_button.clicked.connect(on_flip_clicked)
        
        if selector.currentNode():
            self.update_normal_display(data)
        
        return data
    
    def update_normal_display(self, data):
        """Update the normal label for the given selector data."""
        node = data['selector'].currentNode()
        if not node:
            data['normal_label'].setText("(none)")
            return
        normal = np.array(node.GetNormal())
        normal_str = "({:.2f}, {:.2f}, {:.2f})".format(*normal)
        data['normal_label'].setText(normal_str)
    
    def flip_plane_normal(self, data):
        """Flip the normal of the selected plane and update the display."""
        node = data['selector'].currentNode()
        if not node:
            slicer.util.errorDisplay("No plane selected to flip.")
            return
        normal = np.array(node.GetNormal())
        node.SetNormal(-normal[0], -normal[1], -normal[2])
        self.update_normal_display(data)
        if hasattr(self, 'status_label'):
            self.status_label.setText("↕ Flipped plane normal")
        slicer.app.processEvents()
    
    def get_selected_plane(self, data, plane_name_for_error):
        """Helper to get the node from the selector data."""
        node = data['selector'].currentNode()
        if not node:
            slicer.util.errorDisplay(f"Please select a plane for the '{plane_name_for_error}' view.")
            return None
        return node
    
    def get_normal(self, data):
        """Return the normal vector of the selected plane as a numpy array."""
        node = data['selector'].currentNode()
        if not node:
            return None
        return np.array(node.GetNormal())
    
    def check_orthogonality(self):
        """Compute angles between the three selected normals and warn if not orthogonal."""
        normals = []
        names = ["Axial", "Sagittal", "Coronal"]
        for data, name in zip([self.axial_data, self.sagittal_data, self.coronal_data], names):
            n = self.get_normal(data)
            if n is None:
                slicer.util.errorDisplay(f"Plane for '{name}' is not selected.")
                return
            normals.append(n)
        
        angles = []
        for i in range(3):
            for j in range(i+1, 3):
                dot = np.dot(normals[i], normals[j])
                dot = np.clip(dot, -1.0, 1.0)
                angle_deg = np.arccos(dot) * 180.0 / np.pi
                angles.append((names[i], names[j], angle_deg))
        
        tolerance = 5.0
        ok = all(abs(angle - 90.0) < tolerance for _, _, angle in angles)
        
        if ok:
            msg = "✅ Planes are mutually orthogonal (within ±{}°).".format(tolerance)
            if hasattr(self, 'status_label'):
                self.status_label.setText(msg)
            slicer.util.infoDisplay(msg)
        else:
            msg = "⚠️ Planes are not perfectly orthogonal:\n"
            for name1, name2, angle in angles:
                msg += f"  {name1} vs {name2}: {angle:.1f}°\n"
            msg += "Re-orientation will force orthogonality."
            if hasattr(self, 'status_label'):
                self.status_label.setText("⚠️ Planes not orthogonal")
            slicer.util.warningDisplay(msg)
    
    def run_reorientation(self):
        """Main reorientation logic with optional auto-flip."""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.setText("⏳ Reorienting views...")
            slicer.app.processEvents()
            
            axial_plane = self.get_selected_plane(self.axial_data, "Axial")
            sagittal_plane = self.get_selected_plane(self.sagittal_data, "Sagittal")
            coronal_plane = self.get_selected_plane(self.coronal_data, "Coronal")
            if not all([axial_plane, sagittal_plane, coronal_plane]):
                return
            
            axis_z = np.array(axial_plane.GetNormal())
            axis_x = np.array(sagittal_plane.GetNormal())
            axis_y = np.array(coronal_plane.GetNormal())
            
            if self.autoflip_check.isChecked():
                if axis_z[2] < 0:
                    axial_plane.SetNormal(-axis_z[0], -axis_z[1], -axis_z[2])
                    axis_z = -axis_z
                    self.update_normal_display(self.axial_data)
                if axis_x[0] < 0:
                    sagittal_plane.SetNormal(-axis_x[0], -axis_x[1], -axis_x[2])
                    axis_x = -axis_x
                    self.update_normal_display(self.sagittal_data)
                if axis_y[1] < 0:
                    coronal_plane.SetNormal(-axis_y[0], -axis_y[1], -axis_y[2])
                    axis_y = -axis_y
                    self.update_normal_display(self.coronal_data)
            
            axis_x /= np.linalg.norm(axis_x)
            axis_y /= np.linalg.norm(axis_y)
            axis_z = np.cross(axis_x, axis_y)
            axis_z /= np.linalg.norm(axis_z)
            axis_y = np.cross(axis_z, axis_x)
            axis_y /= np.linalg.norm(axis_y)
            
            red_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
            yellow_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
            green_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
            
            matrix_axial = np.identity(4)
            matrix_axial[0, 0:3], matrix_axial[1, 0:3], matrix_axial[2, 0:3] = axis_x, axis_y, axis_z
            red_node.GetSliceToRAS().DeepCopy(slicer.util.vtkMatrixFromArray(matrix_axial.T))
            red_node.UpdateMatrices()
            
            matrix_sagittal = np.identity(4)
            matrix_sagittal[0, 0:3], matrix_sagittal[1, 0:3], matrix_sagittal[2, 0:3] = axis_y, axis_z, axis_x
            yellow_node.GetSliceToRAS().DeepCopy(slicer.util.vtkMatrixFromArray(matrix_sagittal.T))
            yellow_node.UpdateMatrices()
            
            matrix_coronal = np.identity(4)
            matrix_coronal[0, 0:3], matrix_coronal[1, 0:3], matrix_coronal[2, 0:3] = axis_x, axis_z, axis_y
            green_node.GetSliceToRAS().DeepCopy(slicer.util.vtkMatrixFromArray(matrix_coronal.T))
            green_node.UpdateMatrices()
            
            nasion_pos = self.find_landmark_position("Ryu_hard_tissue", "n")
            if nasion_pos is not None:
                for node in [red_node, yellow_node, green_node]:
                    node.JumpSlice(nasion_pos[0], nasion_pos[1], nasion_pos[2])
            
            slicer.app.layoutManager().sliceWidget('Red').sliceLogic().FitSliceToAll()
            slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic().FitSliceToAll()
            slicer.app.layoutManager().sliceWidget('Green').sliceLogic().FitSliceToAll()
            
            if hasattr(self, 'status_label'):
                self.status_label.setText("✅ Views re-oriented successfully!")
            slicer.util.infoDisplay("SUCCESS: Slice viewers have been re-oriented.")
            
        except Exception as e:
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"❌ Error: {str(e)[:50]}...")
            slicer.util.errorDisplay(f"An error occurred during re-orientation: {e}")
    
    def find_landmark_position(self, node_name, landmark_label):
        """Finds the world position of a landmark in a given fiducial node."""
        try:
            node = slicer.util.getNode(node_name)
            for i in range(node.GetNumberOfControlPoints()):
                if node.GetNthControlPointLabel(i) == landmark_label:
                    pos = np.zeros(3)
                    node.GetNthControlPointPositionWorld(i, pos)
                    return pos
        except:
            return None
        return None
    
    def show_help(self):
        """Display help information."""
        help_text = """
        <h3>Re-orient Slice Views</h3>
        <p><b>Purpose:</b> Re-orient the Red (Axial), Yellow (Sagittal), and Green (Coronal) slice views
        to custom planes defined in your scene.</p>
        
        <p><b>Instructions:</b></p>
        <ol>
            <li><b>Select Planes:</b> Choose three mutually perpendicular planes.</li>
            <li><b>Check Normals:</b> Verify the normal vectors point in the correct direction.</li>
            <li><b>Flip if Needed:</b> Use the ↕ button to reverse a normal direction.</li>
            <li><b>Auto-flip:</b> Enable to automatically orient normals to +Z, +X, +Y.</li>
            <li><b>Apply:</b> Click "Apply New Orientation" to re-orient the views.</li>
        </ol>
        
        <p><b>Plane Mappings:</b></p>
        <ul>
            <li><b>Red (Axial):</b> Normal should point Superior (+Z)</li>
            <li><b>Yellow (Sagittal):</b> Normal should point Right (+X)</li>
            <li><b>Green (Coronal):</b> Normal should point Anterior (+Y)</li>
        </ul>
        
        <p><b>Tips:</b></p>
        <ul>
            <li>Use "Check Orthogonality" to verify your planes are perpendicular.</li>
            <li>Toggle "Compact Mode" to collapse sections for a minimal interface.</li>
            <li>Adjust the image size slider to resize the reference diagram.</li>
        </ul>
        """
        slicer.util.infoDisplay(help_text, windowTitle="Help: Re-orient Slice Views")

# ==============================================================================
# Cleanup and instantiation
# ==============================================================================
try:
    if 'reorient_gui_instance' in globals():
        if reorient_gui_instance and hasattr(reorient_gui_instance, 'main_widget'):
            reorient_gui_instance.main_widget.close()
    del reorient_gui_instance
except NameError:
    pass

reorient_gui_instance = ReorientViewsGUI()


```


