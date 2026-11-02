You are now confidently opening DICOMs and toggle the Shift to reveal skulls – now it’s time for re-aligning the scan and creating segmentation-based masks for convenience.
### Re-alignment of Scans
First, familiarise yourself with the preferred standard plane in craniofacial approximation  – the Frankfort Horizontal Plane.

> The Frankfort horizontal plane (FH; also called the auriculo-orbital plane) was established at the World Congress of Anthropology, in Frankfort, Germany in 1882. First introduced by Von Ihering, in 1872, this plane used to pass through the centre of the external auditory meatus to the lowest point of the inferior margin of each orbit. The Frankfort agreement then modified this definition, so that the plane would pass through the upper borders of each ear canal or external auditory meatus (Porion/Po), and through the inferior border of the orbital rim (Orbitale/Or). (Cited from [Pittayapat et al., 2018)](https://doi.org/10.1093/ejo/cjx066)

![FHP](https://github.com/user-attachments/assets/b8bbc8c3-ba9e-4c95-b4e0-035a8b103ce0)
The aim of this section is to create a permanent change in the original orientation of the scan and establish a new “normal”  – the FHP. When achieved, navigation of the scan will also become easier as the new plane orientation is applied to the default directions.
![navigation](https://github.com/user-attachments/assets/3391d21f-c7ca-4a8e-9a69-0ef8a06904f9)
First, some extensions will be needed to execute this part. On the right hand side of the second row of the menu, you will find a blue puzzle icon ![extensions](https://github.com/user-attachments/assets/c9e84ef8-ca33-4e92-b2ff-066e977b4ba6) Extensions manager – to click on. Choose _Install Extensions_ and search & install _MarkupsToModel_ and _SegmentEditorExtraEffects._ 

> [!CAUTION]
> any extension installation requires a restart of Slicer – do not forget to save!

Second, you will open the Volume Rendering module  ![volumerendering](https://github.com/user-attachments/assets/a5395818-542d-4d68-8d5e-1757e5c49ec4)
, choose your CT volume and under the Display  section, toggle the shift bar until you can only see bone. The FHP (Frankfurt Horizontal Plane) will be established based on cranial features, so this view setup will help visualise it better. 

Third,  the landmarks of the FHP will be imported into the scene. This is via a special file type called “json” or “mrk.json” which, when dragged-and-dropped into the scene, appear as a table of landmarks.

https://github.com/user-attachments/assets/9fdd8ef9-f382-41c0-a594-4a1b7c9bba5b

These filetypes will appear throughout the tutorials as they provide a transferrable and defined set of landmarks that play an important role in the programming side of tutorials. As the files are saved in these “tables”, the row number of the tables define each landmark added and can be identified by the python script. This numbering-based definition-identification process ensures transparency of the methods as anyone using/opening the json files will have the same landmarks in the same order.
> [!WARNING]
> if you make any changes to the landmarks, the codes provided may not work. Make sure to add only to the end or do not alter them.

Please download the json file for this part of the process by double-clicking: 

[FHP_landmarks.json](https://github.com/user-attachments/files/22434441/FHP_landmarks.json)


This file contains the following landmarks: 


abbreviation | landmark name | definition | defined by
-- | -- | -- | --
zyoL | left orbitale | inferior border of the left orbital rim | Pittayapat et al. 2018
poR | right porion | upper border of the right external auditory meatus or ear canal | Pittayapat et al. 2018
poL | left porion | upper border of the leftexternal auditory meatus or ear canal | Pittayapat et al. 2018


You will see 3 point appear sporadically in the scene – you will have to place these manually to their correct position via the Markups module – which you can find as three asterisks in the second line of the menu. 
![markups](https://github.com/user-attachments/assets/41b52cfe-97ed-4d94-b7fc-77b4d8090285)
You have two methods to place them: 

1. find the landmark in the 3D scene (they will appear green when recognised), click, hold and drag them to their position and let go when happy with their placement. 
2. find the last column of the table containing the landmarks (after “S”) with a map pin on top. In this column, when clicking on the row of the landmark you wish to place, the function changes with each click – from a tick to a circle to a pencil to a cross. When reaching the pencil and simply moving the mouse to the 3D scene, you are holding the landmark and can place it with a single mouse click. 

https://github.com/user-attachments/assets/1e33dd2f-d30e-45ec-a59c-9eb14bcbf66c


If none of these solutions are quick enough for your workflow, check out the Slicer discourse on how you can [employ a GUI for continuous placement](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#add-a-button-to-module-gui-to-activate-control-point-placement)


Once the markups are correctly placed, the re-alignment code can be implemented. Ensure you  have the Python console open. The default position of this in on the bottom of the window – if you cannot see it, press this icon ![python](https://github.com/user-attachments/assets/27a499fa-b3f5-4450-8f49-13bb4920f634) in the second line of the menu to open. Click into the python environment to see a cursor moving. Copy and paste the following snippet: 

```python

import numpy
scene = slicer.mrmlScene
F = getNodesByClass('vtkMRMLMarkupsFiducialNode')
F = F[0]

# Get the fiducial IDs of porions and zygomatico - orbitale  suture from the fiducial list by name
po1_id = -1; po2_id = -1; zyo_id = -1;

for i in range(0, F.GetNumberOfControlPoints()):
	if F.GetNthControlPointLabel(i) == 'poR' :
		po1_id = i
	if F.GetNthControlPointLabel(i) == 'poL' :
		po2_id = i
	if F.GetNthControlPointLabel(i) == 'zyoL' :
		zyo_id = i


# Get the coordinates of landmarks
po1 = [0, 0, 0]
po2 = [0, 0, 0]
zyo = [0, 0, 0]

F.GetNthControlPointPosition(po1_id,po1)
F.GetNthControlPointPosition(po2_id,po2)
F.GetNthControlPointPosition(zyo_id,zyo)

# The vector between two porions that we will align to LR axis by calculating the yaw angle
po =[po1[0] - po2[0], po1[1] -po2[1], po1[2]-po2[2]]
vTransform = vtk.vtkTransform()
vTransform.RotateZ(-numpy.arctan2(po[1], po[0])*180/numpy.pi)
transform = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLinearTransformNode')
transform.SetMatrixTransformToParent(vTransform.GetMatrix())

# Apply the transform to the fiducials and the volume
transform = slicer.vtkMRMLLinearTransformNode()

scene.AddNode(transform) 
transform.SetMatrixTransformToParent(vTransform.GetMatrix())
V = getNodesByClass('vtkMRMLScalarVolumeNode')
V = V[0]
V.SetAndObserveTransformNodeID(transform.GetID())
F.SetAndObserveTransformNodeID(transform.GetID())

# Get the updated (transformed) coordinates from the list
po1 = [0, 0, 0]
po2 = [0, 0, 0]
zyo = [0, 0, 0]

F.GetNthControlPointPosition(po1_id,po1)
F.GetNthControlPointPosition(po2_id,po2)
F.GetNthControlPointPosition(zyo_id,zyo)

# Apply the transform to the coordinates
po1 = vTransform.GetMatrix().MultiplyPoint([po1[0], po1[1], po1[2], 0])
po2 = vTransform.GetMatrix().MultiplyPoint([po2[0], po2[1], po2[2], 0])
zyo = vTransform.GetMatrix().MultiplyPoint([zyo[0], zyo[1], zyo[2], 0])
po =[po1[0]-po2[0], po1[1]-po2[1], po1[2]-po2[2]]

# Calculate the rotation for the roll 
vTransform2 = vtk.vtkTransform()

vTransform2.RotateY(numpy.arctan2(po[2], po[0])*180/numpy.pi)

# Apply the transform to previous transform hierarchy
transform2 = slicer.vtkMRMLLinearTransformNode()
scene.AddNode(transform2) 
transform2.SetMatrixTransformToParent(vTransform2.GetMatrix())
transform.SetAndObserveTransformNodeID(transform2.GetID())

# Get the coordinates again
po1 = [0, 0, 0]
po2 = [0, 0, 0]
zyo = [0, 0, 0]

F.GetNthControlPointPosition(po1_id,po1)
F.GetNthControlPointPosition(po2_id,po2)
F.GetNthControlPointPosition(zyo_id,zyo)

# Apply transforms to points to get updated coordinates
po1 = vTransform.GetMatrix().MultiplyPoint([po1[0], po1[1], po1[2], 0])
po2 = vTransform.GetMatrix().MultiplyPoint([po2[0], po2[1], po2[2], 0])
zyo = vTransform.GetMatrix().MultiplyPoint([zyo[0], zyo[1], zyo[2], 0])
po1 = vTransform2.GetMatrix().MultiplyPoint([po1[0], po1[1], po1[2], 0])
po2 = vTransform2.GetMatrix().MultiplyPoint([po2[0], po2[1], po2[2], 0])
zyo = vTransform2.GetMatrix().MultiplyPoint([zyo[0], zyo[1], zyo[2], 0])

# The vector for pitch angle
po_zyo = [zyo[0]-(po1[0]+po2[0])/2, zyo[1]-(po1[1]+po2[1])/2, zyo[2]-(po1[2]+po2[2])/2]

# Calculate the transform for aligning pitch
vTransform3 = vtk.vtkTransform()
vTransform3.RotateX(-numpy.arctan2(po_zyo[2], po_zyo[1])*180/numpy.pi)

# Apply the transform to both fiducial list and the volume
transform3 = slicer.vtkMRMLLinearTransformNode()
scene.AddNode(transform3) 
transform3.SetMatrixTransformToParent(vTransform3.GetMatrix())
transform2.SetAndObserveTransformNodeID(transform3.GetID())

slicer.vtkSlicerTransformLogic().hardenTransform(V)

```

Or, for a more precise re-orientation, use 4 points: 
[FHP4.mrk.json](https://github.com/user-attachments/files/26278568/FHP4.mrk.json)


```python
import numpy
import vtk
import slicer

scene = slicer.mrmlScene

# Function to find landmarks by label in ANY fiducial node in the scene
def find_landmarks_in_scene(required_labels):
    """
    Search through all fiducial nodes in the scene for the required landmarks.
    Returns a dict with landmark coordinates, or raises error if not found.
    
    Args:
        required_labels: list of label names to find (e.g., ['poR', 'poL', 'orR', 'orL'])
    
    Returns:
        dict with structure: {'poR': [x,y,z], 'poL': [x,y,z], 'orR': [x,y,z], 'orL': [x,y,z]}
    """
    landmarks = {label: None for label in required_labels}
    fiducial_node = None
    
    # Search through all markup fiducial nodes in the scene
    markup_nodes = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
    
    if not markup_nodes:
        raise ValueError("No fiducial markup nodes found in the scene! Please load your landmarks first.")
    
    for markup in markup_nodes:
        for i in range(markup.GetNumberOfControlPoints()):
            label = markup.GetNthControlPointLabel(i)
            if label in required_labels:
                coords = [0, 0, 0]
                markup.GetNthControlPointPosition(i, coords)
                landmarks[label] = coords
                fiducial_node = markup
    
    # Check if all required landmarks were found
    missing = [label for label in required_labels if landmarks[label] is None]
    if missing:
        raise ValueError(f"Could not find landmarks: {missing}. Available landmarks in scene:\n{[markup.GetNthControlPointLabel(i) for markup in markup_nodes for i in range(markup.GetNumberOfControlPoints())]}")
    
    return landmarks, fiducial_node

# Required landmarks
required_labels = ['poR', 'poL', 'orR', 'orL']

try:
    landmarks, F = find_landmarks_in_scene(required_labels)
    print(f"Found landmarks: {list(landmarks.keys())}")
except ValueError as e:
    print(f"Error: {e}")
    raise

# Get volume to transform
V = getNodesByClass('vtkMRMLScalarVolumeNode')
if not V:
    raise ValueError("No volume found in the scene!")
V = V[0]

# STEP 1: Yaw rotation - align the porions (left-right) to the LR axis
po_R = landmarks['poR']
po_L = landmarks['poL']
or_R = landmarks['orR']
or_L = landmarks['orL']

po_vector = [po_R[0] - po_L[0], po_R[1] - po_L[1], po_R[2] - po_L[2]]
yaw_angle = -numpy.arctan2(po_vector[1], po_vector[0]) * 180 / numpy.pi

vTransform1 = vtk.vtkTransform()
vTransform1.RotateZ(yaw_angle)

transform1 = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLinearTransformNode')
transform1.SetMatrixTransformToParent(vTransform1.GetMatrix())

V.SetAndObserveTransformNodeID(transform1.GetID())
F.SetAndObserveTransformNodeID(transform1.GetID())

# Get updated coordinates after yaw rotation
po_R = vTransform1.GetMatrix().MultiplyPoint([po_R[0], po_R[1], po_R[2], 0])
po_L = vTransform1.GetMatrix().MultiplyPoint([po_L[0], po_L[1], po_L[2], 0])
or_R = vTransform1.GetMatrix().MultiplyPoint([or_R[0], or_R[1], or_R[2], 0])
or_L = vTransform1.GetMatrix().MultiplyPoint([or_L[0], or_L[1], or_L[2], 0])

print(f"Step 1 (Yaw): Rotated {yaw_angle:.2f}°")

# STEP 2: Roll rotation - align porions in the AP (anterior-posterior) direction
po_vector = [po_R[0] - po_L[0], po_R[1] - po_L[1], po_R[2] - po_L[2]]
roll_angle = numpy.arctan2(po_vector[2], po_vector[0]) * 180 / numpy.pi

vTransform2 = vtk.vtkTransform()
vTransform2.RotateY(roll_angle)

transform2 = slicer.vtkMRMLLinearTransformNode()
scene.AddNode(transform2)
transform2.SetMatrixTransformToParent(vTransform2.GetMatrix())
transform1.SetAndObserveTransformNodeID(transform2.GetID())

# Apply transforms to get updated coordinates
po_R = vTransform2.GetMatrix().MultiplyPoint([po_R[0], po_R[1], po_R[2], 0])
po_L = vTransform2.GetMatrix().MultiplyPoint([po_L[0], po_L[1], po_L[2], 0])
or_R = vTransform2.GetMatrix().MultiplyPoint([or_R[0], or_R[1], or_R[2], 0])
or_L = vTransform2.GetMatrix().MultiplyPoint([or_L[0], or_L[1], or_L[2], 0])

print(f"Step 2 (Roll): Rotated {roll_angle:.2f}°")

# STEP 3: Pitch rotation - use BOTH orbitales for balanced alignment
# Calculate midpoint between both orbitales (anterior reference)
or_midpoint = [(or_R[0] + or_L[0]) / 2, 
               (or_R[1] + or_L[1]) / 2, 
               (or_R[2] + or_L[2]) / 2]

# Calculate midpoint between both porions (posterior reference)
po_midpoint = [(po_R[0] + po_L[0]) / 2, 
               (po_R[1] + po_L[1]) / 2, 
               (po_R[2] + po_L[2]) / 2]

# Vector from posterior (porions) to anterior (orbitales)
po_or_vector = [or_midpoint[0] - po_midpoint[0], 
                or_midpoint[1] - po_midpoint[1], 
                or_midpoint[2] - po_midpoint[2]]

pitch_angle = -numpy.arctan2(po_or_vector[2], po_or_vector[1]) * 180 / numpy.pi

vTransform3 = vtk.vtkTransform()
vTransform3.RotateX(pitch_angle)

transform3 = slicer.vtkMRMLLinearTransformNode()
scene.AddNode(transform3)
transform3.SetMatrixTransformToParent(vTransform3.GetMatrix())
transform2.SetAndObserveTransformNodeID(transform3.GetID())

print(f"Step 3 (Pitch): Rotated {pitch_angle:.2f}°")

# Harden the transform to make it permanent
slicer.vtkSlicerTransformLogic().hardenTransform(V)

print("✓ Frankfurt Horizontal Plane (FHP) re-alignment complete!")
print(f"  - Yaw (LR alignment): {yaw_angle:.2f}°")
print(f"  - Roll (AP alignment): {roll_angle:.2f}°")
print(f"  - Pitch (balanced bilateral): {pitch_angle:.2f}°")

```
# FHP options

You can establish the Frankfort Horizontal Plane in 2 ways: using the landmarks you used for the re-orientation of the scan refer back to the top of the document) OR you can create a bit more precise plane with 4 landmarks (adding the right most posterior orbital rim). Whichever you choose and name 'FHP' will be reflected in the prediction equation measurement. Both FHP establishing codes operate with the plane fit command. 
Here is a screenshot of comparing the resulting planes with 3- and 4 control points, respectively. I am partial to the 4-point method, especially if there are measurements from the FHP involved.

![Picture2](https://github.com/user-attachments/assets/6d630133-70ca-45bd-a257-67ccb6d44dd3)

<details>

<summary>3-point FHP</summary>
Landmarks are already allocated by you when re-orienting the scan. Copy and paste the code and elongate the plane in any directions needed. 

``` python
###3-point FHP###

import slicer
import numpy as np
import vtk

# Create a new plane node
planeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FHP")

# Get the landmarks node
landmarksNode = slicer.util.getNode("FHP_landmarks")

# Extract the control points from the landmarks node
points = np.array([landmarksNode.GetNthControlPointPosition(i) for i in range(landmarksNode.GetNumberOfControlPoints())])

# Ensure we have at least three points
if points.shape[0] < 3:
    raise ValueError("At least three points are required to define a plane.")

# Calculate the centroid of the points
centroid = points.mean(axis=0)

# Perform Singular Value Decomposition (SVD) to find the normal of the best-fit plane
_, _, vh = np.linalg.svd(points - centroid)
normal = vh[2]

# Create a vtkPlane and set its parameters
plane = vtk.vtkPlane()
plane.SetOrigin(centroid)
plane.SetNormal(normal)

# Set the plane parameters in the plane node
planeNode.SetOrigin(plane.GetOrigin())
planeNode.SetNormal(plane.GetNormal())

import slicer

# Get the plane node 'FHP'
planeNode = slicer.util.getNode('FHP')

# Set the color of the plane to emerald (RGB: 0.31, 0.78, 0.47) when not selected
displayNode = planeNode.GetDisplayNode()
displayNode.SetColor(0.31, 0.78, 0.47)
displayNode.SetSelectedColor(0.31, 0.78, 0.47)
displayNode.SetVisibility(True)
```
</details>

<details>

<summary>4-point FHP</summary>

[FH4_landmarks.json](https://github.com/user-attachments/files/22434548/FH4_landmarks.json)


- yes, you are re-allocating 3 of the same points.

| position  | no. in table | Name | Description                                                        |
|---|----|-------|--------------------------------------------------------------------|
| 0  | 1  | orb1  | inferior border of the left orbital rim                            |
| 1  | 2  | orb2  | inferior border of the right orbital rim                           |
| 2  | 3  | por1  | upper border of the right external auditory meatus or ear canal    |
| 3  | 4  | por2  | upper border of the left external auditory meatus or ear canal     |

Copy and paste the code and elongate the plane in any directions needed. 

```python 
import slicer
import numpy as np
import vtk

# Create a new plane node
planeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FHP")

# Get the landmarks node
landmarksNode = slicer.util.getNode("FH4_landmarks")

# Extract the control points from the landmarks node
points = np.array([landmarksNode.GetNthControlPointPosition(i) for i in range(landmarksNode.GetNumberOfControlPoints())])

# Ensure we have at least three points
if points.shape[0] < 3:
    raise ValueError("At least three points are required to define a plane.")

# Calculate the ce[FH4_landmarks.json](https://github.com/user-attachments/files/22434454/FH4_landmarks.json)
ntroid of the points
centroid = points.mean(axis=0)

# Perform Singular Value Decomposition (SVD) to find the normal of the best-fit plane
_, _, vh = np.linalg.svd(points - centroid)
normal = vh[2]

# Create a vtkPlane and set its parameters
plane = vtk.vtkPlane()
plane.SetOrigin(centroid)
plane.SetNormal(normal)

# Set the plane parameters in the plane node
planeNode.SetOrigin(plane.GetOrigin())
planeNode.SetNormal(plane.GetNormal())

import slicer

# Get the plane node 'FHP'
planeNode = slicer.util.getNode('FHP')

# Set the color of the plane to emerald (RGB: 0.31, 0.78, 0.47) when not selected
displayNode = planeNode.GetDisplayNode()
displayNode.SetColor(0.31, 0.78, 0.47)
displayNode.SetSelectedColor(0.31, 0.78, 0.47)
displayNode.SetVisibility(True)
```
</details>
