# The Purkait and Singh (2024) method

### This document contains instructions for: 


- [Hard tissue landmarks (for prediction of soft tissues)](#landmarks-in-this-guide-for-prediction-of-soft-tissues)
- [Additional soft tissue landmarks (for replicating the full method)](#additional-soft-tissue-landmarks-in-this-guide-for-replicating-the-full-method-not-necessary-for-only-estimation)
- [Illustration of the method](#illustration-of-the-method)
-  [Creating the midsagittal plane (MSP)](#creating-the-midsagittal-plane-msp)
- [Hard tissue measurements and guides](#hard-tissue-measurements-and-guides)
- [Graphic User Interface predicting the soft tissue landmarks](#predicting-the-soft-tissue-landmarks)
- [Measuring the prediction errors](#measuring-the-prediction-errors)
- [Output](#output)
- [Research idea](#research-idea)
- [Bibliography](#bibliography)

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide was taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.


### Landmarks in this guide (for prediction of soft tissues)
[PS_hard_tissue.mrk.json](https://github.com/user-attachments/files/21217369/PS_hard_tissue.mrk.json)

> [!IMPORTANT]  
The original paper uses a "backward" projected hard sn described as: 
_"(...) measured from the soft ‘sn’ point to the maxillary bone (bony sn) parallel to the FH plane"_
This in not feasible to use if only hard tissue is available to reconstruct - therefore the closest hard tissue landmark **subspinale or ss** defined by  Howells (1937)[^4]; Howells (1974)[^5]; Caple & Stephan (2016)[^5]Caple & Stephan (2016)[^3] was implemented. The prediction of this landmark will be excluded from this guide and only the **pronasale** will be described.



| Position in code | Position in file | Name in file   | Landmark name | Definition                                                                                                     | Defined by     |
|------------------|-----------------|---------------|---------------|----------------------------------------------------------------------------------------------------------------|----------------|
| 0                | 1               | n             | nasion             | midpoint of the frontonasal suture on the midsagittal plane                                                    | Purkait & Singh, 2024[^2]  |
| 1                | 2               | rhi           | rhinion           | the point located on the most inferior end of the internasal suture                                            |  Martin (1928)[^6];  Knussman (1988)[^7]; Caple & Stephan (2016)[^3]  |
| 2                | 3               | ss            | subspinale            | CHANGED! The deepest point seen in the profile view below the anterior nasal spine (orthodontic point A)       |  Howells (1937)[^4]; Howells (1974)[^5]; Caple & Stephan (2016)[^3] |
| 3                | 4               | ANS           | anterior nasal spine or acanthion           | Most anterior tip of the anterior nasal spine                                                                  | Howells (1937)[^4]; Howells (1974)[^5]; Caple & Stephan (2016)[^3]  |
| 4                | 5               | A (PA_R)      | A (PA_R)      | most lateral point on the right of the bony pyriform aperture                                                  | Purkait & Singh, 2024[^2]  |
| 5                | 6             | B (PA_L)      | B (PA_L)      | most lateral point on the left of the bony pyriform aperture                                                   | Purkait & Singh, 2024[^2]  |
| 6                | 7              | C (PAB_R)     | C (PAB_R)     | lowest point on the right base of the bony pyriform aperture                                                   | Purkait & Singh, 2024[^2]  |
| 7                | 8              | D (PAB_L)     | D (PAB_L)     | lowest point on the left base of the bony pyriform aperture                                                    | Purkait & Singh, 2024[^2] |

### Additional soft tissue landmarks in this guide (for replicating the full method; not necessary for ONLY estimation)

[PS_soft_tissue.mrk.json](https://github.com/user-attachments/files/21217705/PS_soft_tissue.mrk.json)

| Position in code | Position in file | Name in file   | Landmark name | Definition                | Defined by    |
|------------------|-----------------|---------------|---------------|--------------------------------------|--------------|
| 0                | 1               | n'            | n'            | Point directly anterior to the nasofrontal suture, in the midline, overlying n            | Kolar,  (1997)[^8]; Caple & Stephan (2016)[^5] |
| 1                | 2               | rhi'          | rhi'          | Point overlying rhi, at the end of the internasal suture where bone ends and cartilage begins | Stephan, 2008[^9]; Caple & Stephan (2016)[^3]|
| 2                | 3               | sn'           | sn'           | Median point at the junction between the lower border of the nasal septum and the philtrum area | Caple & Stephan (2016)[^3]|
| 3                | 4               | nt            | nasal tip            | lowest point on the lower margin of the nasal tip in the midsagittal plane                | Purkait & Singh, 2024[^2]|
| 4                | 5               | X1(alL)       | left nasal ala       | The most lateral point on the left nasal ala                                              | Purkait & Singh, 2024[^2]|
| 5                | 6               | X2(alR)       | right nasal ala      | The most lateral point on the right nasal ala                                             | Purkait & Singh, 2024[^2]|
| 6               | 7               | Y1(nbL)       | left nasal base       | the base of the left attachment of nasal wings on the upper lip                           | Purkait & Singh, 2024[^2] |
| 7                | 8               | Y2(nbR)       | right nasal base       | the base of the right attachment of nasal wings on the upper lip                          | Purkait & Singh, 2024[^2]|
| 8                | 9              | prn           | pronasale           | The most anteriorly protruded point of the apex nasi                                      | Farkas (1994)[^10]; Caple & Stephan (2016)[^3]|


### Illustration of the method


> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] Re-aligned the scene in the FHP
- [ ] Created a 4-point FHP 
- [ ] Allocated all hard tissue landmarks

### Creating the midsagittal plane (MSP)

In this case, the midsagittal plane was defined as a plane best fitting the **nasion, rhinion, subspinale and anterior nasal spine**

<details>
<summary> Code for MSP </summary>

``` python
import numpy as np

# Get your landmark node (update the name if needed)
lmrks = slicer.util.getNode('PS_hard_tissue')

# Indices you want to use for the best fit plane
indices = [0, 1, 2, 3]

# Get the coordinates of those points (in world coordinates)
points = []
for i in indices:
    pos = np.array(lmrks.GetNthControlPointPositionWorld(i))
    points.append(pos)
points = np.array(points)

# Compute the centroid
centroid = np.mean(points, axis=0)

# Subtract centroid from points
pts_centered = points - centroid

# Singular Value Decomposition (SVD) for best-fit plane
U, S, Vt = np.linalg.svd(pts_centered)
normal = Vt[2, :]  # The normal of the best-fit plane is the last singular vector

# Create the MSP plane
mspPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP')
mspPlaneNode.SetOriginWorld(centroid)
mspPlaneNode.SetNormalWorld(normal)

print("Best-fit 'MSP' plane created through selected landmarks.")

```


</details>

Expected view after code implementation, showing both the FHP and MSP: 


<img width="3365" height="1559" alt="Picture1" src="https://github.com/user-attachments/assets/a1c1cb8b-dac7-475b-8643-4f1152096c8b" />



### Hard tissue measurements and guides

In the following code, we recreate all the hard tissue measurements mentioned in the paper regardless of their correlation and participation in the regression equations; and additionally, establish some lines that are not true measurements but provide navigation for following lines of code (these will be annotated with a yellow dot in the table below). 
After pasting the code, a pop-up window will as for a facial soft tissue thickness to provide for predicting the sn' based on this measurement - this is in agreement with the original instructions by Purkait and Singh (2024)[^2] and the default measurement is set to 13.5 mm (as described by Hona et al. (2023)[^11] in [Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC10861615/table/Tab3/v))



<details>
<summary> Hard tissue measurements </summary>


``` python
import numpy as np
import slicer

print("Starting line creation...")

# Get nodes
mspNode = slicer.util.getNode('MSP')
fhpNode = slicer.util.getNode('FHP')
hardTissueNode = slicer.util.getNode('PS_hard_tissue')

# Get plane normals
def get_plane_normal(node):
    if 'Plane' in node.GetClassName():
        origin = [0, 0, 0]
        normal = [0, 0, 0]
        node.GetOrigin(origin)
        node.GetNormal(normal)
        return np.array(origin), np.array(normal)
    else:
        pts = []
        for i in range(3):
            pt = [0, 0, 0]
            node.GetNthControlPointPosition(i, pt)
            pts.append(np.array(pt))
        v1 = pts[1] - pts[0]
        v2 = pts[2] - pts[0]
        normal = np.cross(v1, v2)
        return pts[0], normal / np.linalg.norm(normal)

msp_origin, msp_normal = get_plane_normal(mspNode)
fhp_origin, fhp_normal = get_plane_normal(fhpNode)

# Create FHP guide line
line_direction = np.cross(msp_normal, fhp_normal)
line_direction /= np.linalg.norm(line_direction)
half_vec = 35.0 * line_direction

fhp_start = msp_origin - half_vec
fhp_end = msp_origin + half_vec
fhpGuideNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'FHP guide')
fhpGuideNode.AddControlPoint(fhp_start.tolist())
fhpGuideNode.AddControlPoint(fhp_end.tolist())

# Create parallel guide lines through landmarks
guide_names = ['st n guide', 'st rhi guide', 'st sn guide']
for i, name in enumerate(guide_names):
    pos = [0, 0, 0]
    hardTissueNode.GetNthControlPointPosition(i, pos)
    pos = np.array(pos)
    lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    lineNode.AddControlPoint((pos - half_vec).tolist())
    lineNode.AddControlPoint((pos + half_vec).tolist())

# Create AB, CD, baseline
def create_line(idx1, idx2, name):
    p1 = [0, 0, 0]
    p2 = [0, 0, 0]
    hardTissueNode.GetNthControlPointPosition(idx1, p1)
    hardTissueNode.GetNthControlPointPosition(idx2, p2)
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    node.AddControlPoint(p1)
    node.AddControlPoint(p2)
    return node

create_line(4, 5, 'AB')
create_line(6, 7, 'CD')
create_line(0, 3, 'baseline')
create_line(0, 1, 'n to rhi')

# Create rhi to baseline perpendicular
rhi = [0, 0, 0]
hardTissueNode.GetNthControlPointPosition(1, rhi)
rhi = np.array(rhi)

baseline_start = [0, 0, 0]
baseline_end = [0, 0, 0]
slicer.util.getNode('baseline').GetNthControlPointPosition(0, baseline_start)
slicer.util.getNode('baseline').GetNthControlPointPosition(1, baseline_end)
baseline_start = np.array(baseline_start)
baseline_end = np.array(baseline_end)

line_vec = baseline_end - baseline_start
line_unit = line_vec / np.linalg.norm(line_vec)
proj = baseline_start + np.dot(rhi - baseline_start, line_unit) * line_unit

rhiToBaselineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'rhi to baseline')
rhiToBaselineNode.AddControlPoint(rhi.tolist())
rhiToBaselineNode.AddControlPoint(proj.tolist())

# Customize appearance
lines = ["FHP guide", "st n guide", "st rhi guide", "st sn guide", "AB", "CD", "baseline", "n to rhi", "rhi to baseline"]
colors = [[1,0,0], [0,1,0], [0,0,1], [1,1,0], [1,0,1], [0,1,1], [1,0.5,0], [0.5,0,0.5], [0.7,0.3,0.3]]

for name, color in zip(lines, colors):
    node = slicer.util.getNode(name)
    disp = node.GetDisplayNode()
    disp.SetColor(1, 1, 1)
    disp.SetSelectedColor(*color)
    disp.SetGlyphScale(1.8)
    disp.SetLineThickness(0.25)

print("✅ ALL LINES CREATED!")
```


</details>

Expected view after code implementation: 

<img width="746" height="788" alt="image" src="https://github.com/user-attachments/assets/0f912a6d-6911-4041-9110-ddb4aec07e5a" />




| Line name        | name in paper | Definition                                                                                     | Colour                         |
|------------------|--------------|-----------------------------------------------------------------------------------------------|--------------------------------|
|🟡 FHP guide        |     N/A         | line where the MSP and FHP planes intersect (where FHP is perpendicular to MSP by definition)  | <span style="color:Red">Red</span> |
| 🟡st n guide       |      N/A        | parallell line to the FHP guide bisecting the hard tissue nasion (for FSTT for n')            | <span style="color:Green">Green</span> |
| 🟡st rhi guide     |         N/A      | parallell line to the FHP guide bisecting the hard tissue rhinion (for FSTT for rhi')         | <span style="color:Blue">Blue</span> |
| 🟡st sn guide      |    N/A           | parallell line to the FHP guide bisecting the hard tissue ss (for FSTT for sn)                | <span style="color:Yellow">Yellow</span> |
| sn'_FSTT (landmark!)              |    sn          | The position of   soft tissue ‘sn’ was determined by adding the STT at ‘bony sn'         |  |
| n to sn FSTT             |   bony n to sn          | line between the hard tissue nasion and the predicted sn' (via FSTT)        | <span style="color:Olive">Olive</span> |
| AB               |    same          | line connecting A and B - the most lateral points of the bony piriform aperture               | <span style="color:Magenta">Magenta</span> |
| CD               |        same      | line connecting C and D - the lowest points of the bony piriform aperture                     | <span style="color:Cyan">Cyan</span> |
| baseline         |    bony n-ans          | line connecting the hard tissue nasion  ‘n’ and the tip of ANS (ss)                           | <span style="color:Orange">Orange</span> |
| n to rhi         |   bony n-rhi            | line connecting the hard tissue nasion  ‘n’ and the rhinion                                   | <span style="color:Purple">Purple</span> |
| rhi to baseline  |   bony rhi ⟂ baseline            | The shortest perpendicular distance between the rhinion and the baseline (n-ANS)              | <span style="color:#B22222">Brick Red</span> |



## Predicting the soft tissue landmark(s?)

The theory behind both of the codes offered is the same. They define the soft tissue measurements as a line perpendicular to the bone/skin surface, parallel to the FHP, therefore the code project lines of an arbitrary length (70 mm) from the hard tissue landmark to gauge an approximate position of the soft tissue landmarks along the planes (knowing their positions relative to the FHP and MSP, but not the distance from the hard tissue landmark yet) - hence the role of the lines ending with "guide" in this step. 

We will consider distances defined by the statistically significant equations intersecting these guide lines for predicting the  **pronasale**. 
This is where we run into an issue with the **nt** soft tissue prediction - we could proceed with a predicted soft nasion, based on an FSTT value, but there is no "line" guiding the position of this; therefore only a radius closest to an arbitrary line can be stablished which is not justified by any anatomical or geometric knowledge. Therefore, the prediction of this will be excluded. Same for the sn' (already misdefined) - if we arbitrarily assumed a nasion-soft nasion FSTT value (from this paper, its follow-up; or non-sex specific) and from this projected n' drew a circle with the length calculated for soft n-ss (soft n-sn in reality) via the regression featuring n to rhi; it is TECHNICALLY predictable, but relies on the assumption of the use of the FSTT value, NOT the regression. 

| Predicted Distance | Regression Equation | Biological Sex | NOTE |
|--------------------|---------------------|----------------|-----|
| bony n-ss | 4.385 + 0.988 × (baseline) | male | for fragmented skull ONLY |
| soft n-nt | 31.76 + 1.009 × (n to rhi) | male | MUST assume FSTT for n` AND that the nasal tip is on the FSTT guidelines - excluded |
| prn baseline | 19.544 + 0.299 × (rhi to baseline) | male | 
| alL-alR | 25.256 + 0.55 × (AB) | male | not relevant for prediction from hard tissue |
| nbL-nbR | 33.433 + 0.362 × (CD) | male |  not relevant for prediction from hard tissue |
| bony n-ss | 7.673 + 0.909 × (baseline) | female | | for fragmented skull ONLY |
| soft n-nt | 33.23 + 0.768 × (n to rhi) | female | MUST assume FSTT for n` - excluded |
| prn baseline | 15.056 + 0.622 × (rhi to baseline) | female |  | MUST assume FSTT for n` AND that the nasal tip is on the FSTT guidelines - excluded |

Left with equations for each biological sex and the distances they provide, the next step is : 
- The equations featuring the baseline calculate the perpendicular distance between the **baseline** and the **pronasale**. Because Fig. 1 in Purkait & Singh, 2024[^2] shows a line starting from the ANS, perpendicular to the baseline connecting to the pronasale, we create the ANS perpendicular line. The "origin" from where we can apply the distance estimated by the equation will be where the baseline intersects the ANS perpendicular line, anteriorly. This is how we get the **pred_prn**. 

<details>
<summary> GUI for prn prediction </summary>

``` python
import numpy as np
import slicer
import qt

class NasalPredictionWidget(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()
        self.regression_coefficients = {
            'male': {'prn_baseline': (19.544, 0.299)},
            'female': {'prn_baseline': (15.056, 0.622)}
        }
        
    def setup_ui(self):
        layout = qt.QVBoxLayout(self)
        
        title = qt.QLabel("<h2>Nasal Prediction Tool</h2>")
        title.alignment = qt.Qt.AlignCenter
        layout.addWidget(title)
        
        form = qt.QFormLayout()
        
        self.sex_combo = qt.QComboBox()
        self.sex_combo.addItems(["Male", "Female", "Both"])
        form.addRow("Biological Sex:", self.sex_combo)
        
        self.show_lines_checkbox = qt.QCheckBox()
        self.show_lines_checkbox.checked = True
        form.addRow("Show Visualization:", self.show_lines_checkbox)
        
        layout.addLayout(form)
        
        info = qt.QLabel("<b>Required:</b> PS_hard_tissue, baseline, rhi to baseline, n to rhi, MSP<br>"
                        "<b>Creates:</b> pred_prn selected sex(es)")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        self.run_button = qt.QPushButton("Run Prediction")
        self.run_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(self.run_button)
        
        self.status_label = qt.QLabel("Ready")
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)
        
        self.setWindowTitle("Nasal Prediction Tool")
        self.resize(400, 350)
    
    def connect_signals(self):
        self.run_button.clicked.connect(self.run_prediction)
    
    def run_prediction(self):
        self.status_label.setText("Running...")
        self.status_label.setStyleSheet("color: blue;")
        slicer.app.processEvents()
        
        try:
            sex_text = self.sex_combo.currentText
            show_lines = self.show_lines_checkbox.checked
            
            if sex_text == "Both":
                self.create_nasal_prediction("male", show_lines)
                self.create_nasal_prediction("female", show_lines)
                self.status_label.setText("✅ Both predictions completed!")
            else:
                sex = sex_text.lower()
                self.create_nasal_prediction(sex, show_lines)
                self.status_label.setText(f"✅ {sex_text} prediction completed!")
            
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def create_nasal_prediction(self, sex, show_lines):
        print(f"\nCreating {sex} predictions...")
        
        # Get nodes
        hard = slicer.util.getNode('PS_hard_tissue')
        baseline_node = slicer.util.getNode('baseline')
        rhi_baseline_node = slicer.util.getNode('rhi to baseline')
        n_rhi_node = slicer.util.getNode('n to rhi')
        msp_node = slicer.util.getNode('MSP')
        
        # Get or create prediction node
        pred_node_name = f'pred_soft_tissue_{sex}'
        try:
            pred_node = slicer.util.getNode(pred_node_name)
            while pred_node.GetNumberOfControlPoints() > 0:
                pred_node.RemoveNthControlPoint(0)
        except:
            pred_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', pred_node_name)
        
        # Get MSP normal
        if 'Plane' in msp_node.GetClassName():
            msp_normal = [0, 0, 0]
            msp_node.GetNormal(msp_normal)
            msp_normal = np.array(msp_normal)
        else:
            pts = [self.get_point(msp_node, i) for i in range(3)]
            msp_normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
            msp_normal /= np.linalg.norm(msp_normal)
        
        # Find ANS
        ans_idx = 3
        for i in range(hard.GetNumberOfControlPoints()):
            if "ANS" in hard.GetNthControlPointLabel(i):
                ans_idx = i
                break
        ans = self.get_point(hard, ans_idx)
        
        # Get baseline perpendicular direction
        bl_start = self.get_point(baseline_node, 0)
        bl_end = self.get_point(baseline_node, 1)
        bl_dir = (bl_end - bl_start) / np.linalg.norm(bl_end - bl_start)
        perp_vec = np.cross(bl_dir, msp_normal)
        perp_vec /= np.linalg.norm(perp_vec)
        if perp_vec[1] < 0:
            perp_vec = -perp_vec
        
        # Predict pronasale
        rhi_bl_len = self.get_line_length(rhi_baseline_node)
        prn_intercept, prn_coeff = self.regression_coefficients[sex]['prn_baseline']
        prn_dist = prn_intercept + prn_coeff * rhi_bl_len
        pred_prn = ans + prn_dist * perp_vec
        
        if show_lines:
            self.create_line(ans - 30*perp_vec, ans + 30*perp_vec, f"ANS_perp_{sex}", [0,0.8,0.8], [0,1,1])
            self.create_line(ans, pred_prn, f"ANS_to_prn_{sex}", [0.8,0.8,0], [1,0.7,0])
        
    
        # Add predictions to node
        pred_node.AddControlPoint(pred_prn.tolist(), f"pred_prn_{sex}")
       
        
        # Set colors
        disp = pred_node.GetDisplayNode()
        if sex == "male":
            disp.SetColor(0, 0, 0.8)
            disp.SetSelectedColor(0, 0, 1)
        else:
            disp.SetColor(0, 0.8, 0)
            disp.SetSelectedColor(0, 1, 0)
        disp.SetGlyphScale(1.8)
        disp.SetTextScale(3.0)
        
        print(f"✅ {sex.capitalize()} predictions: prn={pred_prn})
    
    
    
    def get_point(self, node, idx):
        pt = [0, 0, 0]
        node.GetNthControlPointPosition(idx, pt)
        return np.array(pt)
    
    def get_line_length(self, node):
        return np.linalg.norm(self.get_point(node, 1) - self.get_point(node, 0))
    
    def create_line(self, p1, p2, name, color=[1,1,1], sel_color=[1,0.5,0], thickness=0.25):
        existing = slicer.util.getFirstNodeByName(name)
        if existing:
            slicer.mrmlScene.RemoveNode(existing)
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
        node.AddControlPoint(p1.tolist())
        node.AddControlPoint(p2.tolist())
        disp = node.GetDisplayNode()
        disp.SetColor(*color)
        disp.SetSelectedColor(*sel_color)
        disp.SetLineThickness(thickness)
        return node

# Launch widget
widget = NasalPredictionWidget()
widget.show()
```

</details>

### Measuring the prediction error
For the following code to work, please place the [soft tissue landmarks] on the model. These are stored in [PS_soft_tissue.mrk.json](https://github.com/user-attachments/files/21253770/PS_soft_tissue.mrk.json). 
The script below connects all the prediction set landmarks with the true landmark, measuring the distance between them and creates  red lines called"error_{predicted lmrk name}". 




<details>
<summary> Prediction error </summary>

``` python
import slicer
import numpy as np

def get_point(node, label):
    for i in range(node.GetNumberOfControlPoints()):
        if node.GetNthControlPointLabel(i) == label:
            pt = [0, 0, 0]
            node.GetNthControlPointPosition(i, pt)
            return np.array(pt)
    return None

def create_error_line(p1, p2, name):
    existing = slicer.util.getFirstNodeByName(name)
    if existing:
        slicer.mrmlScene.RemoveNode(existing)
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    node.AddControlPoint(p1.tolist())
    node.AddControlPoint(p2.tolist())
    disp = node.GetDisplayNode()
    disp.SetColor(1, 0, 0)
    disp.SetSelectedColor(1, 0, 0)
    disp.SetLineThickness(0.2)
    return np.linalg.norm(p2 - p1)

ps_soft = slicer.util.getNode('PS_soft_tissue')
errors = {}

# Male predictions
try:
    male = slicer.util.getNode('pred_soft_tissue_male')
    prn = get_point(ps_soft, "prn")
    pred_prn = get_point(male, "pred_prn_male")
  
    if pred_prn is not None and prn is not None:
        errors['prn_male'] = create_error_line(pred_prn, prn, "error_prn_male")
    
except:
    pass

# Female predictions
try:
    female = slicer.util.getNode('pred_soft_tissue_female')
    prn = get_point(ps_soft, "prn")
    
    pred_prn = get_point(female, "pred_prn_female")
   
    if pred_prn is not None and prn is not None:
        errors['prn_female'] = create_error_line(pred_prn, prn, "error_prn_female")
   
except:
    pass

# FSTT predictions
sn_true = get_point(ps_soft, "sn'")
n_true = get_point(ps_soft, "n'")

try:
    fstt_sn = slicer.util.getNode('pred_FSTT_sn')
    for i in range(fstt_sn.GetNumberOfControlPoints()):
        label = fstt_sn.GetNthControlPointLabel(i)
        pred = get_point(fstt_sn, label)
        if pred is not None and sn_true is not None:
            errors[f'sn_{label}'] = create_error_line(pred, sn_true, f"error_{label}")
except:
    pass

try:
    fstt_n = slicer.util.getNode('pred_FSTT_n')
    for i in range(fstt_n.GetNumberOfControlPoints()):
        label = fstt_n.GetNthControlPointLabel(i)
        pred = get_point(fstt_n, label)
        if pred is not None and n_true is not None:
            errors[f'n_{label}'] = create_error_line(pred, n_true, f"error_{label}")
except:
    pass

print("\n✅ Error lines created:")
for name, dist in errors.items():
    print(f"  {name}: {dist:.2f} mm")
```

You can expect a view like this: 

<img width="830" height="724" alt="image" src="https://github.com/user-attachments/assets/554aab25-1d06-4c1e-938a-3a9e171e40ef" />



</details>


### Recreating all soft and hard tissue measurements 

If you wish to run data analysis on the whole of the study to see different relationships or find equations that suits your population, the code below creates the rest of (soft tissue dependent) measurements mentioned in the study, regardless of their significance. 


<details>
<summary> Rest of the measurements </summary>

``` python
import numpy as np
import slicer

def get_point(node, label):
    for i in range(node.GetNumberOfControlPoints()):
        if node.GetNthControlPointLabel(i) == label:
            pt = [0, 0, 0]
            node.GetNthControlPointPosition(i, pt)
            return np.array(pt)
    raise ValueError(f"Point '{label}' not found")

def create_line(name, p1, p2):
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
    node.AddControlPoint(p1.tolist())
    node.AddControlPoint(p2.tolist())
    node.GetDisplayNode().SetTextScale(3)
    return np.linalg.norm(p2 - p1)

def create_angle(name, p1, apex, p2):
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", name)
    node.AddControlPoint(p1.tolist())
    node.AddControlPoint(apex.tolist())
    node.AddControlPoint(p2.tolist())
    node.GetDisplayNode().SetTextScale(3)
    return node.GetAngleDegrees()

def shortest_distance_lines(p1, p2, q1, q2):
    v = p2 - p1
    u = q2 - q1
    w0 = p1 - q1
    a = np.dot(v, v)
    b = np.dot(v, u)
    c = np.dot(u, u)
    d = np.dot(v, w0)
    e = np.dot(u, w0)
    denom = a*c - b*b
    if abs(denom) < 1e-6:
        return (p1+p2)/2, (q1+q2)/2, np.linalg.norm(np.cross(w0, u)) / np.linalg.norm(u)
    s = (b*e - c*d) / denom
    t = (a*e - b*d) / denom
    P = p1 + s*v
    Q = q1 + t*u
    return P, Q, np.linalg.norm(P-Q)

# Get nodes
hard = slicer.util.getNode('PS_hard_tissue')
soft = slicer.util.getNode('PS_soft_tissue')
baseline_node = slicer.util.getNode('baseline')

# Get baseline for perpendicular calculations
bl_start = [0, 0, 0]
bl_end = [0, 0, 0]
baseline_node.GetNthControlPointPosition(0, bl_start)
baseline_node.GetNthControlPointPosition(1, bl_end)
bl_start = np.array(bl_start)
bl_end = np.array(bl_end)
bl_dir = (bl_end - bl_start) / np.linalg.norm(bl_end - bl_start)

print("\n=== LINEAR MEASUREMENTS ===")

# Soft tissue measurements
measurements = {}
measurements['n-n\''] = create_line("n-n'", get_point(hard, "n"), get_point(soft, "n'"))
measurements['rhi-rhi\''] = create_line("rhi-rhi'", get_point(hard, "rhi"), get_point(soft, "rhi'"))

alL = get_point(soft, "X1(alL)")
alR = get_point(soft, "X2(alR)")
measurements['al-al'] = create_line("al-al", alL, alR)

nbL = get_point(soft, "Y1(nbL)")
nbR = get_point(soft, "Y2(nbR)")
measurements['nb-nb'] = create_line("nb-nb", nbL, nbR)

P, Q, xy_dist = shortest_distance_lines(alL, alR, nbL, nbR)
measurements['X-Y'] = create_line("X-Y", P, Q)

n_soft = get_point(soft, "n'")
nt = get_point(soft, "nt")
measurements['soft n-nt'] = create_line("soft n-nt", n_soft, nt)

prn = get_point(soft, "prn")
prn_proj = bl_start + np.dot(prn - bl_start, bl_dir) * bl_dir
measurements['prn perp baseline'] = create_line("prn perp baseline", prn, prn_proj)

for name, value in measurements.items():
    print(f"  {name}: {value:.2f} mm")

print("\n=== ANGULAR MEASUREMENTS ===")

angles = {}
rhi_soft = get_point(soft, "rhi'")
sn = get_point(soft, "sn'")
angles['soft rhi\'-prn-sn\''] = create_angle("soft rhi'-prn-sn'", rhi_soft, prn, sn)
angles['prn-sn\'-nt'] = create_angle("prn-sn'-nt", prn, sn, nt)
angles['al-prn-al'] = create_angle("al-prn-al", alL, prn, alR)

for name, value in angles.items():
    print(f"  {name}: {value:.2f}°")

print("\n✅ All measurements created!")
```


</details>

| Measurement | Script Implementation | Landmarks Used |
|-------------|----------------------|----------------|
| n-n' | distance between hard and soft tissue nasions| n (hard), n' (soft) |
| rhi-rhi' | distance between hard and soft tissue rhinions | rhi (hard), rhi' (soft) |
| al-al | distance between most laterally projected points on the nasal wings  | X1(alL), X2(alR) |
| nb-nb | distance between the base of the left and right attachment of nasal wings on the upper lip | Y1(nbL), Y2(nbR) |
| X-Y | "X-Y" | Shortest perpendicular distance between al-al and nb-nb |
| soft n-nt | distance between soft nasion and nasal tip | n', nt |
| prn perp baseline | Shortest perpendicular distance between the baseline and the pronasale | prn, projected point on baseline |
| soft rhi'-prn-sn' | angle of the nose tip | rhi', prn, sn' |
| prn-sn'-nt | angle predicting the dipping of the lower part of the nose below the ‘prn’ landmark | prn, sn', nt |
| al-prn-al |  angle of the nasal wing | X1(alL), prn, X2(alR) |

## Output

**Note:** The output depends on which predictions you ran:
- From the nasal prediction GUI: `pred_prn_male/female` and `pred_nt_male/female` in `pred_soft_tissue_male/female` nodes
- From the FSTT GUI: `sn'_FSTT_male/female/nonsex` in `pred_FSTT_sn` and `n'_FSTT_male/female/nonsex` in `pred_FSTT_n`
- Visualization lines if enabled: `ANS_perp_{sex}`, `ANS_to_prn_{sex}`, `n_to_nt_{sex}`, `prn_to_nt_{sex}`
What can you expect as the outputs from the previous codes? There are still a few pseudo-lines to ignore when copying the measurements as described in [this guide](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md#code-to-copy-linear-measurements). 



We will show an example: 


<details>
<summary> Everything was enabled, both male and female predictions, with FSTT option for Non-sex specific </summary>

| Patient ID | Measurement | Value | Notes/Comments |
|------------|-------------|-------|----------------|
| (none) | FHP guide | 70 | ❌ - not a real measurement |
| (none) | st n guide | 70 | ❌ - not a real measurement |
| (none) | st rhi guide | 70 | ❌ - not a real measurement |
| (none) | st sn guide | 70 | ❌ - not a real measurement |
| (none) | AB | 28.48 | |
| (none) | CD | 14.24 | |
| (none) | baseline | 49.61 | |
| (none) | n to rhi | 19.76 | |
| (none) | rhi to baseline | 9.33 | |
| (none) | ANS_perp_male | 60 | ❌ - not a real measurement |
| (none) | ANS_to_prn_male | 22.33 | |
| (none) | n_to_nt_male | 51.7 | |
| (none) | prn_to_nt_male | 22.33 | |
| (none) | ANS_perp_female | 60 | ❌ - not a real measurement |
| (none) | ANS_to_prn_female | 20.86 | |
| (none) | n_to_nt_female | 48.41 | |
| (none) | prn_to_nt_female | 20.86 | |
| (none) | error_prn_male | 9.2 | |
| (none) | error_nt_male | 22.08 | |
| (none) | error_prn_female | 9.75 | |
| (none) | error_nt_female | 21.23 | |
| (none) | error_sn'_FSTT_male | 27.56 | |
| (none) | error_sn'_FSTT_female | 26.24 | |
| (none) | error_sn'_FSTT_nonsex | 29.44 | |
| (none) | error_n'_FSTT_male | 16.53 | |
| (none) | error_n'_FSTT_female | 15.58 | |
| (none) | error_n'_FSTT_nonsex | 17.43 | |
| (none) | n-n' | 12.11 | |
| (none) | rhi-rhi' | 19.04 | |
| (none) | al-al | 43.76 | |
| (none) | nb-nb | 42.16 | |
| (none) | X-Y | 5.61 | |
| (none) | soft n-nt | 55.83 | |
| (none) | prn perp baseline | 25.19 | |
| (none) | soft rhi'-prn-sn' | 128.36 | |
| (none) | prn-sn'-nt | 21.3 | |
| (none) | al-prn-al | 109.86 | |


*the lines pred_prn to pred_sn_{sex} were left is as this line also appeared on Fig. 1 in Purkait & Singh, 2024[^2]

</details>

#### Research idea

It may be worth implementing the coordinate system mentioned by [Thitiorul et al. 2020](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Thitiorul2020.md#the-thitiorul-2020-method) to this method as the nasion is also a central landmark in this method, and run analysis on the individual coordinates to see it these landmarks have significant correlations and/or predictive power to estimate soft tissue landmarks. The description of nt' by Purkait & Singh, 2024[^2] is similar to nd' in [Thitiorul et al. 2020](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Thitiorul2020.md#landmarks-in-this-guide). 

# Bibliography

[^1]: 3D Slicer webpage https://www.slicer.org/
[^2]: Singh, S. and R. Purkait (2024). "Three-dimensional prediction of the nose for facial reconstruction: A preliminary study on North Indian adults." Journal of Forensic and Legal Medicine 105: 102708.
[^3]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." International Journal of Legal Medicine 130(3): 863-879.
[^4]: Howells, W. W. (1937). "The designation of the principle anthrometric landmarks on the head and skull." American Journal of Physical Anthropology 22(3): 477-494.
[^5]: Howells, W. W. (1974). Cranial variation in man: A study by multivariate analysis of patterns of difference among recent human populations. Cambridge, Harvard University.
[^6]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^7]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^8]: Kolar, J. and E. Salter (1997). Craniofacial anthropometry: practical measurement of the head and face for clinical, surgical, and research use. Springfield, Charles C Thomas.
[^9]: Stephan, C. N. and E. K. Simpson (2008). "Facial soft tissue depths in craniofacial identification (part I): An analytical review of the published adult data." Journal of Forensic Sciences 53(6): 1257-1272.
[^10]: Farkas, L. G. (1994). Anthropometry of the Head and Face, Lippincott Williams & Wilkins.	
[^11]: Hona, T. W. P. T. and C. N. Stephan (2024). "Global facial soft tissue thicknesses for craniofacial identification (2023): a review of 140 years of data since Welcker’s first study." International Journal of Legal Medicine 138(2): 519-535.

