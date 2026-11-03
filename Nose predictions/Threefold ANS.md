
# The Threefold ANS Method by Krogman & Iscan, 1986[^2], as interpreted by Rynn et al. (2010)[^7]


The method interpretation for the threefold ANS by Krogman & Iscan, 1986[^2] in this guide is based on Rynn et al. (2010)[^7] and Taylor, 2001[^3]

They describe it as follows:

> “A line is projected, following the direction of the ANS, and the average soft tissue depth at mid-philtrum is vertically transposed up to it. The length of the ANS, from the vomer-maxillary junction (VMJ) to the acanthion (at the tip on the ANS) is tripled and added to the transferred average of soft tissue depth” (Krogman 1968[^2], Taylor, 2001[^3])

Stephan et al. 2003[^5] trialled _“substituting original nasal spine length for that determined by margin of most prominent lateral nasal aperture line to tip of nasal spine on lateral radiographs where the vomer was not detectable_ (referred in Rynn et al. 2010[^7] as PLB)”, but found larger margins of error. Therefore, the VMJ in this guide will be described as the junction of the vomer and maxilla (at the base of the nasal spine) and placed at the purple dot on figure 1 (modified from Grey's 1918[^6]). 

<img width="868" height="674" alt="image" src="https://github.com/user-attachments/assets/2f8ecbd2-8403-4125-8cc2-d04cd1534cca" />



## The Rynn et al. (2010) and Taylor (2001)[^3] interpretation

To repeat this interpretation by Rynn et al. (2010)[^7], we will:

To repeat this interpretation by Rynn et al. (2010)[^7], we will:

- [Establish an INB plane](#inb-plane)
- [Make a profile view](#profile-view-model)
- [Draw an acanthion vector](#establishing-the-acanthion-vector)
- [Create and adjust the mid-philtrum point](#mid-philtrum-and-reference-to-mp)
- [Predict Pronasale](#predict-pronasale)
- [Calculate the error](#error-calculation)


Landmarks in this  guide for the Rynn interpretation: 
[KrogmanIscan_hard_tissue.mrk.json](https://github.com/user-attachments/files/20212533/KrogmanIscan_hard_tissue.mrk.json)

[KrogmanIscan_soft_tissue.mrk.json](https://github.com/user-attachments/files/20234679/KrogmanIscan_soft_tissue.mrk.json)

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide does not have all the features (inion, bregma) that are to be landmarked. Please refer to the illustrations in the guide for correct placement. In addition, due to the CT being taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.

KrogmanIscan_soft_tissue contains:
| Position in code | Position in file | Name in file | Landmark name | Definition                                                                                                                     | Defined by            |
|------------------|------------------|--------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 0                | 1                | pronasale    | pronasale     | The most anteriorly protruded point of the apex nasi. In the case of a bifid nose, the more protruding tip is chosen           | Caple and Stephan 2016[^8]|

KrogmanIscan_hard_tissue contains:

| Position in code | Position in file | Name in file | Landmark name | Definition                                                                                                                     | Defined by            |
|------------------|------------------|--------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 0                | 1                | nasion       | nasion        | Intersection of the nasofrontal sutures in the median plane                                                                    | Rynn et al. 2010[^7]      |         
| 1     | 2                | inion        | inion         | Median point between the apices of the superior nuchal lines and at the base of the external occipital protuberance (not the tip of the protuberance) | Rynn et al. 2010[^7]      |
| 2                | 3                | bregma       | bregma        | Where the sagittal and coronal sutures meet. Impossible to determine in juvenile skulls with anterior fontanelle, or with complete suture obliteration | Rynn et al. 2010[^7]      |
| 3                | 4                | subspinale      | subspinale       | Most rostral (end) point on the internasal suture.                                                                            | Rynn et al. 2010[^7]      |
| 4                | 5                | acanthion    | acanthion     | Most anterior tip of the anterior nasal spine                                                                                 | Rynn et al. 2010[^7]      |
| 5                | 6                |  VMJ  | vomer-maxillary junction      |    the point on the cranium where the maxilla and the vomer meet in the midline, at the posterior end of the anterior nasal spine        | Somjai 2025 (unpublished) |
| 6                | 7                |  prosthion  | prosthion      |   Median point between the central incisors on the anterior most margin of the maxillary alveolar rim        | Caple and Stephan 2016[^8], Martin, 1928[^9], Knussmann 1988[^10] |



Illustration of the method: 

> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan has to be re-aligned in the FHP
- [ ] You should have a Bone and Skin model via segmentation (explained later)

You will establish a profile plane,  INB or MSP, based on which landmarks in the hard tissue landmark file you can place. 



### INB plane

To help with the side profile, we will establish the “INB” plane as defined by Rynn et al. 2010[^7]. 

> a midsagittal plane (INB) which bisected the inion, nasion and bregma

by downloading the hard tissue markups file for this method:

[KrogmanIscan_hard_tissue.mrk.json](https://github.com/user-attachments/files/22452149/KrogmanIscan_hard_tissue.mrk.json)


 allocating the first three landmarks (nasion, inion, bregma) and copying and pasting the following code: 
 
<details>
	
<summary>INB plane</summary>

```python

import numpy as np
import slicer
from slicer.util import getNode
from qt import QMessageBox 

# Get the points from the "KrogmanIscan_hard_tissue" node
hardTissueNode = slicer.util.getNode('KrogmanIscan_hard_tissue')
point1 = np.array(hardTissueNode.GetNthControlPointPosition(0))
point2 = np.array(hardTissueNode.GetNthControlPointPosition(1))
point3 = np.array(hardTissueNode.GetNthControlPointPosition(2))

# Calculate the normal of the plane defined by the three points
v1 = point2 - point1
v2 = point3 - point1
planeNormal = np.cross(v1, v2)
planeNormal = planeNormal / np.linalg.norm(planeNormal)  # Normalize the normal vector

# Create a new plane node
newPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'INB')

# Set the origin of the new plane to the first point
newPlaneNode.SetOrigin(point1)

# Set the normal of the new plane
newPlaneNode.SetNormal(planeNormal)

print("INB plane created through selected landmarks.")

# Show a popup message to confirm and remind next steps
msg = QMessageBox()
msg.setIcon(QMessageBox.Information)
msg.setWindowTitle("INB plane created!")
msg.setText(
    "INB plane created through selected landmarks.\n\n"
    "Next steps:\n"
    "1) Create a side profile model cut using the Dynamic Modeler module and the 'INB' plane.\n"
    "2) Place the VMJ/anterior nasal spine base landmark."
)
msg.addButton("OK", QMessageBox.AcceptRole)
msg.exec_()


```

</details>

<img src="https://github.com/user-attachments/assets/536f67fe-0479-43ce-a871-b70eb6f0abf6" width="500">


View after only the first 3 landmarks are allocated correctly AND INB extended via the toggles (dots)


### MSP (mid-sagittal plane)

<details>
<summary>Code for MSP</summary>
	
```python
import numpy as np
import slicer

#--- Configuration ---
#1. Name of the node containing your landmark points.
SOURCE_NODE_NAME = "KrogmanIscan_hard_tissue"

#2. List of point labels that define the Midsagittal Plane.
MSP_POINT_LABELS = ['nasion', 'acanthion', 'prosthion', 'subspinale']

#3. The name for the new plane that will be created.
NEW_PLANE_NAME = 'MSP'

#--- Main Script ---

print(f"Attempting to create '{NEW_PLANE_NAME}'...")

#1. Get the source landmark node from the scene
try:
    sourceNode = slicer.util.getNode(SOURCE_NODE_NAME)
    if not sourceNode:
        raise ValueError(f"Node '{SOURCE_NODE_NAME}' not found.")
except Exception as e:
    slicer.util.errorDisplay(f"Error: {e}")
    raise

#2. Find the coordinates of the points with the specified labels
points = []
found_labels = []
missing_labels = list(MSP_POINT_LABELS)

for i in range(sourceNode.GetNumberOfControlPoints()):
    label = sourceNode.GetNthControlPointLabel(i)
    if label in MSP_POINT_LABELS:
        pos = np.zeros(3)
        sourceNode.GetNthControlPointPosition(i, pos)
        points.append(pos)
        found_labels.append(label)
        if label in missing_labels:
            missing_labels.remove(label)

#3. Check if we found enough points to define a plane
if len(points) < 3:
    slicer.util.errorDisplay(
        f"Could not find at least 3 of the required points in '{SOURCE_NODE_NAME}'.\n"
        f"Found: {found_labels}\n"
        f"Missing: {missing_labels}\n"
        "Cannot calculate a plane."
    )
    raise ValueError("Not enough points to define a plane.")

#If some points were missing, show a warning but continue
if missing_labels:
    slicer.util.warningDisplay(
        f"Warning: Could not find all specified points.\n"
        f"The plane will be calculated using the {len(found_labels)} points that were found: {found_labels}"
    )

#4. --- Best-Fit Plane Calculation using SVD ---
points_array = np.array(points)

#a) Calculate the centroid (average position), which will be the plane's origin.
centroid = points_array.mean(axis=0)

#b) Center the points by subtracting the centroid.
centered_points = points_array - centroid

#c) Use Singular Value Decomposition (SVD) to find the plane's normal.
#The normal vector is the one corresponding to the smallest singular value.
#In numpy's SVD, this is the last row of the 'vh' matrix.
_, _, vh = np.linalg.svd(centered_points)
plane_normal = vh[-1]

#--- Create the New Plane in Slicer ---

#Remove the old plane if it exists to avoid duplicates
oldPlaneNode = slicer.mrmlScene.GetFirstNodeByName(NEW_PLANE_NAME)
if oldPlaneNode:
    slicer.mrmlScene.RemoveNode(oldPlaneNode)
    print(f"Removed existing '{NEW_PLANE_NAME}' plane.")

#Create the new plane node
newPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', NEW_PLANE_NAME)

#Set the origin and normal for the new plane
newPlaneNode.SetOrigin(centroid)
newPlaneNode.SetNormal(plane_normal)

print(f"\nSuccessfully created Midsagittal Plane '{NEW_PLANE_NAME}'.")
print(f"  - Calculated from points: {found_labels}")
print(f"  - Origin (Centroid): {np.round(centroid, 2)}")
print(f"  - Normal Vector: {np.round(plane_normal, 2)}")### Create Midsagittal Plane (MSP) ###
```

</details>



### Segmentation
[link to step-by-step](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/003_Roi%20vs%20Segmentation.md)

You can hide all of these and keep only the models if you wish.

In case still need the red/green/yellow slice windows for precise landmark placement, keep only the original volume node (CTBrain in the example) and the models visible. 

### Profile view model

For this method, a profile view will be useful. 

To open the appropriate module, click on the magnifying glass icon next to the modules: 

![module](https://github.com/user-attachments/assets/08aeb820-240a-4cfd-a9c7-01d017c09c36)

And start typing “dynamic modeller” in the search bar.
![module2](https://github.com/user-attachments/assets/c9dfd153-3c8b-4e99-82a2-8ed83320aec7)

Click “Switch to Module” to open. 

You’ll see this menu on the left side of the screen: 

![dynamic-modeller](https://github.com/user-attachments/assets/035ea262-8235-4665-8c4d-c3df49945944)

The "INB” or "MSP" is established in the environment. To cut the model along this plane (technically cutting it in 2 and choosing which side to keep), choose the first button (Plane Cut).


![image](https://github.com/user-attachments/assets/9c297c00-d350-4994-9386-1e2aea9e3e25)

Make sure you create your cut model with the settings on the screenshot to cut the Bone model at the INB Plane: 

- [ ] Make sure the source volume is the full model of the Bone
- [ ] Choose INB/MSP as the plane node
- [ ]  Operation type should be **Intersection**
- [ ]  You MUST chose the **Create new model as...** from the drop-down menu and type in the custom name with the side prefix - otherwise you'll override your existing models. This time, the negative output will be the right side of the cut and the positive side is the left side
- [ ] DO NOT FORGET TO CLICK APPLY


- [ ] Check if this was executed by finding your 2 new models under the "Models" module

With these settings, the Model list will be the following: 


![image](https://github.com/user-attachments/assets/ca5973b4-e666-4070-8a1c-e1c12584bf46)



And you should have the following individual views (excluding/hiding the original full models for demonstration purposes):

<img src="(https://github.com/user-attachments/assets/1c18929a-71af-4793-a502-f02438d7ee68)" width="500">


You can now allocate the remainder of the landmarks on either model - they should appear on ALL of them. 


### Establishing the acanthion vector
Re-orient the view of either your left-bone model to see its right side OR your right-bone model to see its left side to look inside the cranium: 

To establish the tangent described as in the general direction of the acanthion, like an arrow, manually draw a vector in the general direction of the acanthion by going to “Markups” >”line” and creating a tangent relatively in the vicinity of the reference plane (INB or MSP). Name this line “aca vector” (by double clicking on the name automatically added to the line - likely "L"- and typing it in)

<img src="https://github.com/user-attachments/assets/57341433-009a-47cf-be85-a6fd329fa4b8" width="500">


Now, execute the **aca vector to INB/MSP** code  that projects the lines to the INB/MSP, ensures that it bisects the acanthion and elongates the line in both directions. 
<details>
<summary>Project 'aca vector' onto sagittal plane (MSP or INB)</summary>

```python
### Project 'aca vector' onto sagittal plane (MSP/INB compatible) ###
import numpy as np
import slicer

# --- Configuration ---
# The line to be projected.
SOURCE_LINE_NAME = 'aca vector'
# The script will look for a plane with the first name in this list,
# then fall back to the next name if the first isn't found.
PLANE_PRIORITY_LIST = ['MSP', 'INB']
# How far to extend the source line for an infinite projection effect.
EXTENSION_LENGTH_MM = 100

# --- Main Script ---

# 1. Find the source line
source_line_node = slicer.util.getNode(SOURCE_LINE_NAME)
if not source_line_node:
    slicer.util.errorDisplay(f"Error: Source line '{SOURCE_LINE_NAME}' not found.")
    raise ValueError(f"'{SOURCE_LINE_NAME}' not found.")

# 2. Find the reference plane (MSP or INB)
reference_plane_node = None
found_plane_name = ""
for name in PLANE_PRIORITY_LIST:
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node:
        reference_plane_node = node
        found_plane_name = name
        print(f"Found reference plane: '{found_plane_name}'")
        break

if not reference_plane_node:
    slicer.util.errorDisplay(f"Error: Could not find a reference plane. Please ensure one of the following exists: {PLANE_PRIORITY_LIST}")
    raise ValueError("Reference plane not found.")

# 3. Get the source line's geometry and extend it
if source_line_node.GetNumberOfControlPoints() < 2:
    slicer.util.errorDisplay(f"Error: Source line '{SOURCE_LINE_NAME}' has fewer than 2 points.")
    raise ValueError("Invalid source line.")

p1, p2 = np.zeros(3), np.zeros(3)
source_line_node.GetNthControlPointPositionWorld(0, p1)
source_line_node.GetNthControlPointPositionWorld(1, p2)

direction = p2 - p1
direction_normalized = direction / np.linalg.norm(direction)

extended_point1 = p1 - EXTENSION_LENGTH_MM * direction_normalized
extended_point2 = p2 + EXTENSION_LENGTH_MM * direction_normalized

# 4. Get the plane's geometry
plane_origin = np.zeros(3)
reference_plane_node.GetOriginWorld(plane_origin)
plane_normal = np.zeros(3)
reference_plane_node.GetNormalWorld(plane_normal)

# 5. Project the extended points onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    vector = point - planeOrigin
    distance = np.dot(vector, planeNormal)
    return point - distance * planeNormal

projected_point1 = project_point_onto_plane(extended_point1, plane_origin, plane_normal)
projected_point2 = project_point_onto_plane(extended_point2, plane_origin, plane_normal)

# 6. Create the new projected line
projected_line_name = f'{SOURCE_LINE_NAME} projected onto {found_plane_name} plane'

# Clean up old node if it exists
old_projected_line = slicer.mrmlScene.GetFirstNodeByName(projected_line_name)
if old_projected_line:
    slicer.mrmlScene.RemoveNode(old_projected_line)

# Create the new node
projected_line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', projected_line_name)
projected_line_node.AddControlPoint(projected_point1)
projected_line_node.AddControlPoint(projected_point2)

print(f"Successfully created '{projected_line_name}'.")

```
<img src="https://github.com/user-attachments/assets/f792e15c-1def-482d-ac0c-8ff577017d9c" width="500">

</details>

### Mid-philtrum and reference to mp
The hard tissue mid-philtrum is defined as the _Median point midway between subspinale and prosthion_ – therefore a line connecting the subspinale and prosthion can be established and the midline found programmatically, which is a visual guide to allocate the **mp** landmark via the script below, that also creates the VMJ-acanthion distance. 

<details>

<summary>Mid-philtrum landmark & VMJ-aca line (Improved Logic)</summary>

```python
import numpy as np
import slicer
from slicer.util import getNode
from qt import QMessageBox 

# Get the Markups node for 'KrogmanIscan_hard_tissue'
hardTissueNode = getNode('KrogmanIscan_hard_tissue')

# Create VMJ-aca line
F = getNode('KrogmanIscan_hard_tissue')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(5)  # VMJ at position 5
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(4)  # acanthion at position 4
L.AddControlPoint(secondPoint)
L.SetName('VMJ-aca')

# Create subspinale-prosthion line
L2 = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint2 = F.GetNthControlPointPositionVector(3)  # subspinale at position 3
L2.AddControlPoint(firstPoint2)
secondPoint2 = F.GetNthControlPointPositionVector(6)  # prosthion at position 6
L2.AddControlPoint(secondPoint2)
L2.SetName('ss-pr')

# Get the coordinates of the endpoints from positions 3 (subspinale) and 6 (prosthion)
point1 = np.zeros(3)
point2 = np.zeros(3)
hardTissueNode.GetNthControlPointPosition(3, point1)
hardTissueNode.GetNthControlPointPosition(6, point2)

# Calculate the midpoint
midpoint = (point1 + point2) / 2.0

# Add the midpoint to the 'KrogmanIscan_hard_tissue' node and set its label to "mp"
midpointIndex = hardTissueNode.AddControlPoint(midpoint)
hardTissueNode.SetNthControlPointLabel(midpointIndex, "mp")

# Show a popup message to remind the user
msg = QMessageBox()
msg.setIcon(QMessageBox.Information)
msg.setWindowTitle("Reminder: Adjust Midpoint")
msg.setText(
    "Please move the new 'mp' point so it sits on the surface of the maxilla.\n\n"
    "You can use the Markups control point editing tool to adjust its position as needed."
)
msg.addButton("Noted!", QMessageBox.AcceptRole)
msg.exec_()
```

</details>

If this "mp" does not meet the model, you may have to manually allocate it onto the surface of the maxilla. The script saves "mp" in the "hard tissue" node, in case you'd have to re-allocate or find it.

<img src="https://github.com/user-attachments/assets/58f738d2-d20f-4610-b039-472f26cf9bf4" width="500">

Example of programmatically placing mp that does not meet the bone surface

<img src="https://github.com/user-attachments/assets/628a6079-f810-4ea8-9fc9-5d8294dc45d3" width="500">

Example of the manually adjusted mp

### Predict Pronasale

The following script uses calculations based on the bone model's surface normals and the RAS (Right-Anterior-Superior) coordinate system. The default FSTT (facial soft tissue thickness) value is 11.5mm based on [Hona and Stephan 2024](https://link.springer.com/article/10.1007/s00414-023-03087-x)'s study[^11], and the multiplier is set to 3.0× ANS (Krogman and Iscan, 1986).

After placing the FFST "peg" perpendicularly to the adjusted mp point with the aforementioned length; a line from the FSTT cylinder's anteriormost endpoint is drawn. This line is parallell to the nasal spine vector line and its length is calculated by the original Krogman-Iscan formula (3xANS=3xVMJ-aca). 

There is another method included in the [GUI](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/cf1ead1c8511af060ad219252b803955ba30c53a/Nose%20predictions/Threefold%20ANS%20GUI.md), specifically cerated on an elderly population. 
Matsuda et al. (2023)[^12] revised the original equation to 1.9xANS for their population - however, this comes with their caveat of the midphiltrum FSTT being extremely variable in the elderly. Therefore, the GUI allows for manual adjustment of the average value. 


<details>

<summary>Predict Pronasale - Copy-Pasteable Snippet</summary>

```python
import numpy as np
import vtk
import slicer
from slicer.util import getNode

# --- Configuration ---
PERPENDICULAR_DISTANCE_MM = 11.5  # Default FSTT from Hona and Stephan 2024
MULTIPLIER = 3.0  # 3.0 × ANS (Krogman and Iscan, 1986) or 1.9 × ANS (Matsuda et al., 2023)
SHOW_CYLINDER = True  # Set to False to hide cylinder visualization

# --- Get Required Nodes ---
landmarksNode = getNode('KrogmanIscan_hard_tissue')
boneModel = slicer.util.getFirstNodeByClass('vtkMRMLModelNode')  # Gets first bone model
vmjAcaLine = getNode('VMJ-aca')

# Verify all required nodes exist
if not all([boneModel, landmarksNode, vmjAcaLine]):
    raise ValueError("A required node from a previous step is missing.")

# Find the mp point index
mp_index = -1
for i in range(landmarksNode.GetNumberOfControlPoints()):
    if 'mp' in landmarksNode.GetNthControlPointLabel(i).lower():
        mp_index = i
        break

if mp_index == -1:
    raise ValueError("Could not find 'mp' point in landmarks")

# Get mp position
mp_pos = np.zeros(3)
landmarksNode.GetNthControlPointPositionWorld(mp_index, mp_pos)

# --- Calculate Surface Normal at mp ---
# Use RAS coordinate system: Y-axis is anterior
anterior_dir = np.array([0, 1, 0])

# Get surface normal from bone model
point_locator = vtk.vtkPointLocator()
point_locator.SetDataSet(boneModel.GetPolyData())
point_locator.BuildLocator()

normals_filter = vtk.vtkPolyDataNormals()
normals_filter.SetInputData(boneModel.GetPolyData())
normals_filter.ComputePointNormalsOn()
normals_filter.Update()

avg_normal = np.array(normals_filter.GetOutput().GetPointData().GetNormals().GetTuple(
    point_locator.FindClosestPoint(mp_pos)))

# Ensure the normal points ANTERIORLY (in the same general direction as anterior_dir)
if np.dot(avg_normal, anterior_dir) < 0:
    avg_normal = -avg_normal

# --- Calculate FSTT endpoint ---
end_point_perp = mp_pos + avg_normal * PERPENDICULAR_DISTANCE_MM

# Create FSTT line (perpendicular from mp)
fstt_line = slicer.util.getFirstNodeByName("FSTT mp")
if not fstt_line:
    fstt_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "FSTT mp")
fstt_line.RemoveAllControlPoints()
fstt_line.AddControlPoint(mp_pos)
fstt_line.AddControlPoint(end_point_perp)
fstt_line.GetDisplayNode().SetSelectedColor(0, 1, 0)  # Green
fstt_line.GetDisplayNode().SetLineThickness(0.3)

# --- Create Cylinder Visualization (Optional) ---
cylinder_model = slicer.util.getFirstNodeByName("FSTT mp cylinder")
if SHOW_CYLINDER:
    if not cylinder_model:
        cylinder_model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "FSTT mp cylinder")
    
    # Ensure display node exists and is visible
    if not cylinder_model.GetDisplayNode():
        cylinder_model.CreateDefaultDisplayNodes()
    display_node = cylinder_model.GetDisplayNode()
    display_node.SetVisibility(True)
    
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetRadius(2.0)
    cylinder.SetHeight(PERPENDICULAR_DISTANCE_MM)
    cylinder.SetResolution(30)
    
    direction = end_point_perp - mp_pos
    vtk.vtkMath.Normalize(direction)
    center = mp_pos + 0.5 * PERPENDICULAR_DISTANCE_MM * direction
    
    transform = vtk.vtkTransform()
    initial_axis = [0, 1, 0]  # Cylinder initially along Y-axis
    rotation_axis = np.cross(initial_axis, direction)
    angle_rad = np.arccos(np.dot(initial_axis, direction))
    transform.Translate(center)
    transform.RotateWXYZ(np.rad2deg(angle_rad), rotation_axis)
    
    transform_polydata = vtk.vtkTransformPolyDataFilter()
    transform_polydata.SetTransform(transform)
    transform_polydata.SetInputConnection(cylinder.GetOutputPort())
    transform_polydata.Update()
    
    cylinder_model.SetAndObservePolyData(transform_polydata.GetOutput())
    
    # Set color
    if display_node:
        display_node.SetColor(1, 1, 0)  # Yellow
elif cylinder_model:
    # Hide cylinder if SHOW_CYLINDER is False
    display_node = cylinder_model.GetDisplayNode()
    if display_node:
        display_node.SetVisibility(False)

# --- Calculate Pronasale Position ---
# Calculate pronasale position (anterior projection)
pronasale_pos = end_point_perp + anterior_dir * (vmjAcaLine.GetLineLengthWorld() * MULTIPLIER)

# Create final prediction line
final_line = slicer.util.getFirstNodeByName("pronasale_vector")
if not final_line:
    final_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "pronasale_vector")
final_line.RemoveAllControlPoints()
final_line.AddControlPoint(end_point_perp)
final_line.AddControlPoint(pronasale_pos)
final_line.GetDisplayNode().SetSelectedColor(0, 0, 1)  # Blue
final_line.GetDisplayNode().SetLineThickness(0.3)

# Create predicted pronasale point
predictedPronasaleNode = slicer.util.getFirstNodeByName("predicted pronasale")
if not predictedPronasaleNode:
    predictedPronasaleNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "predicted pronasale")
predictedPronasaleNode.RemoveAllControlPoints()
predictedPronasaleNode.AddControlPoint(pronasale_pos, "pronasale")
predictedPronasaleNode.GetDisplayNode().SetSelectedColor(1, 0, 0)  # Red
predictedPronasaleNode.GetDisplayNode().SetGlyphScale(3.0)

# Output results
print(f"Pronasale prediction complete!")
print(f"VMJ-aca length: {vmjAcaLine.GetLineLengthWorld():.2f} mm")
print(f"FSTT distance: {PERPENDICULAR_DISTANCE_MM:.2f} mm")
print(f"Multiplier: {MULTIPLIER}x")
print(f"Predicted pronasale position: {pronasale_pos}")
```

</details>


### Error Calculation

To validate the prediction against known soft tissue landmarks, make sure you downloaded and allocated  [KrogmanIscan_soft_tissue.mrk.json](https://github.com/user-attachments/files/20234679/KrogmanIscan_soft_tissue.mrk.json) 

Then, copy and paste the following script that creates lines between the predicted and true pronasale and give coordinates of the same. 

<details>

<summary>Calculate Prediction Error</summary>

```python
import numpy as np
import slicer
from slicer.util import getNode

# Get predicted pronasale
predictedPronasaleNode = getNode('predicted pronasale')
if not predictedPronasaleNode:
    raise ValueError("Predicted pronasale not found. Please run prediction first.")

# Get true soft tissue landmarks
trueSoftTissueNode = getNode('KrogmanIscan_soft_tissue')
if not trueSoftTissueNode:
    raise ValueError("True soft tissue landmarks not loaded.")

# Find predicted position
predicted_pos = None
for i in range(predictedPronasaleNode.GetNumberOfControlPoints()):
    if "pronasale" in predictedPronasaleNode.GetNthControlPointLabel(i).lower():
        predicted_pos = np.zeros(3)
        predictedPronasaleNode.GetNthControlPointPositionWorld(i, predicted_pos)
        break

# Find true position
true_pos = None
for i in range(trueSoftTissueNode.GetNumberOfControlPoints()):
    if "pronasale" in trueSoftTissueNode.GetNthControlPointLabel(i).lower():
        true_pos = np.zeros(3)
        trueSoftTissueNode.GetNthControlPointPositionWorld(i, true_pos)
        break

if predicted_pos is None:
    raise ValueError("Could not find 'pronasale' in predicted landmarks")
if true_pos is None:
    raise ValueError("Could not find 'pronasale' in true landmarks")

# Create error visualization line
error_line = slicer.util.getFirstNodeByName("prediction_error")
if not error_line:
    error_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "prediction_error")

if not error_line.GetDisplayNode():
    error_line.CreateDefaultDisplayNodes()

error_line.RemoveAllControlPoints()
error_line.AddControlPoint(predicted_pos)
error_line.AddControlPoint(true_pos)
error_line.GetDisplayNode().SetSelectedColor(1, 0, 0)  # Red

# Calculate and display error
error_distance = np.linalg.norm(predicted_pos - true_pos)
print(f"\n=== Prediction Error ===")
print(f"Predicted position: {predicted_pos}")
print(f"True position: {true_pos}")
print(f"Error distance: {error_distance:.2f} mm")
```

</details>

### Outputs
If you want to copy all linear measurements in the scene for data collection, refer to [this guide](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/7b9aaccce0aaf54cdb91d4888bd12ac06ac452c0/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md)


## Bibliography: 

[^1]: [Slicer Script Repository](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html)
[^2]: Krogman, W. M. and M. Y. Isçan (1986). The human skeleton in forensic medicine. The human skeleton in forensic medicine. Springfield, IL, Charles C Thomas. 15: 202-208.
[^3]: Taylor, K. T. (2001). Forensic art and illustration, CRC press.
[^4]: Gatliff, B. P. (1984). "Facial sculpture on the skull for identification." American Journal of Forensic Medicine and Pathology 5(4): 327-332.
[^5]: Stephan, C. N., et al. (2003). "Predicting nose projection and pronasale position in facial approximation: a test of published methods and proposal of new guidelines." American Journal of Physical Anthropology: The Official Publication of the American Association of Physical Anthropologists 122(3): 240-250.
[^6]: Henry Gray Anatomy of the Human Body. 1918.[Bartleby link] (https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/fig-173)
[^7]: Rynn, C., Wilkinson, C.M. & Peters, H.L. (2010) "Prediction of nasal morphology from the skull." Forensic Sci Med Pathol 6, 20–34. https://doi.org/10.1007/s12024-009-9124-6
[^8]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." Int J Legal Med 130(3): 863-879.
[^9]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^10]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^11]: Hona, T. W. P. T. and C. N. Stephan (2024). "Global facial soft tissue thicknesses for craniofacial identification (2023): a review of 140 years of data since Welcker’s first study." International Journal of Legal Medicine 138(2): 519-535.
[^12]: Matsuda, H., et al. (2023). "Simplified Formula for Estimating Nasal Dimensions for 3-Dimensional Facial Reconstruction among Japanese Adults." Forensic Sciences 3: 381–393.
	


