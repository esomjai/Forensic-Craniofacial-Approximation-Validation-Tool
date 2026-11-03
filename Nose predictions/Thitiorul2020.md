# The Thitiorul (2020) method 

For reference code snippets and insight for how 3D Slicer works, please refer to the official 3D Slicer webpage [^1]. 

Thitiorul et al. (2020)[^2] proposed a novel technique by creating a relative coordinate system with nasion as the origin point (0,0,0) (inspired by Rynn et al. 2010[^3]) and using hard tissue landmark coordinates to predict soft tissue landmark coordinates with regression equations in a Thai population. They calibrated the equations on 108 individuals' cone beam CT and tested their predictabilty on 24 new individuals. Uniquely, they do not try to recreate the lateral cephalogram view, but treat the 3D data as is. 
Their method gives 2 options for validation on a different populations: 1) using their regression formulae to make predictions based on the hard tissue only, then recording error between the predicted and true landmarks or 2) recreating the study with all landmarks to see if the statistical correlation is the same between landmarks in different populations. the first option is described first, click HERE to jump to the section with the second option. 



### This document contains instructions for: 
- [The Thitiorul (2020) method](#the-thitiorul-2020-method)
- [Special instructions for recreating the new coordinate system](#special-instructions-for-recreating-the-new-coordinate-system)
- [Landmarks in this guide](#landmarks-in-this-guide)
- [Illustration of the method](#illustration-of-the-method)
- [Establishing the MSP (midsagittal plane) and the X-Z plane](#establishing-the-msp-midsagittal-plane-and-the-x-z-plane)
- [(Optional) Visualising the coordinate system](#optional-visualising-the-coordinate-system)
- [Creating the predicted soft tissue measurements](#creating-the-predicted-soft-tissue-measurements)
- [Soft tissue landmark definition and error evaluation](#soft-tissue-landmark-definition-and-error-evaluation)
- [Output](#output)
- [Bibliography](#bibliography)

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide does not have all the features (inion, bregma) that are to be landmarked. Please refer to the illustrations in the guide for correct placement. In addition, due to the CT being taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.

### Special instructions for recreating the new coordinate system

- [ ] You can still re-orient the CT in the FHP to help later with landmarking - the navigation via the widget will be assisting you in the directions

However, after you did this and ran the [first code here](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/002_Realign%20CT%20in%20the%20standard%20FHP.md#re-alignment-of-scans); make sure you remove everything from the scene before proceeding. This is OK as the FHP transformation is hardened via the code, so it will not revert to the "unorganised" previous orientation. 

Drag and drop the "reference_nasion" .json file into the environment and allocate your nasion landmark.

[reference_nasion.mrk.json](https://github.com/user-attachments/files/20638483/reference_nasion.mrk.json)

This only contains the nasion as "n". 


Then, run the **nasion as origin** code below - please note that if you click on anything right after running this code that may influence the scene/view, you will have to re-run it. This code does not have a built-in hardening of the transformation as it caused my Slicer programme to crash each time I initiated it, so we will do this by hand. Click on the _Transforms_ module, check that the "MoveToOrigin" transformation is chosen on the top; then scroll down to _Apply transform_ and drag the **MoveToOrigin** and **reference nasion** from _Transformable_ to _Transformed_ via the arrows. This will re-apply the same transformation so it will look unusual - do not panic, just select all that is in the _Transformed_ column and click **Identity**. The nasion and scan should have returned to how it looked like right after the code implementation. Now, still with the contents selected, click on the **Harden Transform** button. This will make the column contents "jump" back to the _Transformable_ column - that is how you can check that it executed the task. Whenever unsure, just go back to the _Markups_ module and check that the nasion coordinates are still (0,0,0). If not, click _Identity_ or start over before hardening the transform. 
Since this process is manual and tedious, the video guidance below may help: 

https://github.com/user-attachments/assets/47a73d84-0a6b-44b3-a7f2-db5ac2f485ca



<details>
<summary> nasion as origin </summary>

``` python
####place n######
import slicer
import numpy as np

# --- USER SETTINGS ---
landmarks_node_name = "reference_nasion"  # Change to your markups node name if needed
n_label = "n"  # The label of the landmark to move to the origin
transform_name = "MoveToOrigin"

# --- Find the coordinates of landmark 'n' ---
markups = slicer.util.getNode(landmarks_node_name)
n_coord = None
for i in range(markups.GetNumberOfControlPoints()):
    if markups.GetNthControlPointLabel(i) == n_label:
        n_coord = [0.0, 0.0, 0.0]
        markups.GetNthControlPointPosition(i, n_coord)
        break
if n_coord is None:
    raise ValueError(f"Could not find a point labeled '{n_label}' in '{landmarks_node_name}'.")

print(f"n landmark found at: {n_coord}")

# --- Create a transform that moves n to the origin ---
move_transform = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", transform_name)
matrix = np.array([
    [1, 0, 0, -n_coord[0]],
    [0, 1, 0, -n_coord[1]],
    [0, 0, 1, -n_coord[2]],
    [0, 0, 0, 1]
])
move_transform.SetMatrixTransformToParent(slicer.util.vtkMatrixFromArray(matrix))
print(f"Transform '{transform_name}' set to translate by: ({-n_coord[0]}, {-n_coord[1]}, {-n_coord[2]})")

# --- Find the only volume in the scene automatically ---
volume_nodes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
if len(volume_nodes) == 1:
    volume = volume_nodes[0]
    print(f"Automatically found the only volume: {volume.GetName()}")
else:
    volume = None
    print(f"Found {len(volume_nodes)} volumes. No volume will be shifted automatically. If you want to shift a volume, please specify its name.")

# --- Apply the transform to all models and markups in the scene, and the volume if present ---
all_nodes_to_transform = []
for nodeClass in ["vtkMRMLModelNode", "vtkMRMLMarkupsFiducialNode"]:
    nodes = slicer.util.getNodesByClass(nodeClass)
    for node in nodes:
        node.SetAndObserveTransformNodeID(move_transform.GetID())
        all_nodes_to_transform.append(node)
        print(f"Transform applied to {node.GetName()}")

if volume:
    volume.SetAndObserveTransformNodeID(move_transform.GetID())
    all_nodes_to_transform.append(volume)
    print(f"Transform applied to volume: {volume.GetName()}")

print("All objects in the scene (models, markups, and the only volume if present) have been shifted so your chosen landmark is at (0,0,0)")

markups = slicer.util.getNode("reference_nasion")
slicer.vtkSlicerTransformLogic().hardenTransform(markups)

``` 

</details>

Now, I would hide the **reference nasion** markup list from the scene to avoid confusion. With the re-orientation, you can now create Bone and Skin segments if you wish. 

### Landmarks in this guide 

[Thitiorul_hard_tissue.mrk.json](https://github.com/user-attachments/files/23696758/Thitiorul_hard_tissue.mrk.json)


> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan was realigned so that n (0,0,0)

For these landmarks, the original authors provide guidance. I suggest placing them until the last two (**nr** - nasal suture and  **ss** - subspinale), then running the codes for reference guiding lines below. The code creates the visual guide lines to place these more precisely. Also, if your "second" nasion is not perfectly placed at 0,0,0, manually edit the RAS coordinates - this is not cheating as we already established this as the origin, it only prevents additional error to arise. 
The following video shows what I mean: 

https://github.com/user-attachments/assets/6569ebd7-3be4-4b07-897e-e152f538429a

| Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|------------------|------------------|--------------|--------------|------------|------------|
| 0                | 1                | n            | nasion            | The most anterior point on the frontonasal suture in the midline | Thitiorul et al. (2020)[^2] |
| 1                | 2                | a            | acanthion            | The tip of the bony anterior nasal spine in the midline | Thitiorul et al. (2020)[^2] |
| 2                | 3                | rhi          | rhinion          | The midline point at the inferior free end of the internasal suture | Thitiorul et al. (2020)[^2] |
| 3                | 4                | zy_L         | left zygion         | The most lateral point on the outline of the LEFT zygomatic arch | Thitiorul et al. (2020)[^2] |
| 4                | 5                | zy_R         | right zygion         | The most lateral point on the outline of the RIGHT zygomatic arch | Thitiorul et al. (2020)[^2] |
| 5                | 6                | ecm_L        | left ectomolare       | The most lateral point on the outer surface of the LEFT maxillary alveolar margin | Thitiorul et al. (2020)[^2] |
| 6                | 7                | ecm_R        | right ectomolare        | The most lateral point on the outer surface of the RIGHT maxillary alveolar margin | Thitiorul et al. (2020)[^2] |
| 7                | 8                | iof_L        | left infraorbital foramen       | The most superior point on the margin of the LEFT  infraorbital foramen | Thitiorul et al. (2020)[^2] |
| 8                | 9                | iof_R        | right infraorbital foramen        | The most superior point on the margin of the RIGHT  infraorbital foramen | Thitiorul et al. (2020)[^2] |
| 9                | 10               | pr           | prosthion           | The lowermost anterior midline point on the alveolar process of the maxilla. | Thitiorul et al. (2020)[^2] |
| 10               | 11               | nr           | nasal suture           | The farthest point perpendicular from the line between n and rhi | Thitiorul et al. (2020)[^2] |
| 11               | 12               | ss           | subspinale           | The deepest point on the curved bony outline between a and pr | Thitiorul et al. (2020)[^2] |


<details>
<summary> lines for placing nr and ss </summary>

``` python
###lines to aid the placement of ss and nr####

G = slicer.util.getNode('Thitiorul_hard_tissue')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')

firstPoint = G.GetNthControlPointPositionVector(0)  # nasion
L.AddControlPoint(firstPoint)
secondPoint = G.GetNthControlPointPositionVector(2) # rhinion
L.AddControlPoint(secondPoint)
L.SetName('for nr')

L.GetDisplayNode().SetColor(0.0, 1.0, 0.0) # green

L.GetDisplayNode().Modified()


G = slicer.util.getNode('Thitiorul_hard_tissue')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')

firstPoint = G.GetNthControlPointPositionVector(1)  # acanthion
L.AddControlPoint(firstPoint)
secondPoint = G.GetNthControlPointPositionVector(9) # prosthion
L.AddControlPoint(secondPoint)
L.SetName('for ss')


L.GetDisplayNode().SetColor(0.0, 1.0, 0.0) # green

L.GetDisplayNode().Modified()

```


</details>


### Illustration of the method


Expected view from the front after placing ALL landmarks


<img src="https://github.com/user-attachments/assets/7cde6de0-03dc-40a1-8108-253b46dbfa1c" width="500">


### Establishing the MSP (midsagittal plane) and the X-Z plane

To establish the most fitting midsagittal plane, the hard tissue landmarks that were described as **Skull: midline landmarks** by Thitiorul et al. (2020)[^2] are all employed to calculate 

Expected view after the creation of MSP and the X-Z Plane


<img src="https://github.com/user-attachments/assets/6a95d568-d75f-406e-9ce5-41ebe2a07f7e" width="500">


<details>
<summary> MSP and X-Z creation </summary>

``` python


###midline plane###
import slicer
import numpy as np

# Get your landmark node (update the name if needed)
lmrks = slicer.util.getNode('Thitiorul_hard_tissue')

# Indices you want to use for the best fit plane
indices = [0, 1, 2, 9, 10, 11]

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


import numpy as np

# Get the landmark coordinates from "Thitiorul_hard_tissue" at index 0
landmarkNode = slicer.util.getNode('Thitiorul_hard_tissue')
landmarkCoordinates = [0, 0, 0]
landmarkNode.GetNthControlPointPosition(0, landmarkCoordinates)

# Retrieve the "MSP" plane node
mspPlaneNode = slicer.util.getNode('MSP')

# Get the normal of the "MSP" plane
mspNormal = [0, 0, 0]
mspPlaneNode.GetNormal(mspNormal)

# Calculate a vector perpendicular to the MSP normal
# Assuming MSP normal is along Y-axis, we can use the cross product with Z-axis
zAxis = [0, 0, 1]
xzPlaneNormal = np.cross(mspNormal, zAxis)

# Create the "X-Z plane" perpendicular to the "MSP" plane and passing through the landmark
xzPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'X-Z plane')
xzPlaneNode.SetOrigin(landmarkCoordinates)
xzPlaneNode.SetNormal(xzPlaneNormal)

# Set additional properties for the "X-Z plane"
xzPlaneNode.SetSize(100, 100)  # Adjust size as needed
xzPlaneNode.SetDisplayVisibility(True)

# Update the scene to reflect the changes
slicer.mrmlScene.Modified()

print("X-Z plane created and set up successfully.")

```

</details>



### (Optional) Visualising the coordinate system

This is to aid the comparison between the original study to the view in Slicer - completely optional. 
The script below will create the 3 axes with nasion as the origin: 

- x axis in red, pointing inferior (down)
- y axis in green, pointing left (patient's right)
- z axis in blue,  pointing posterior (towards the back of the skull)

Expected view (a) with planes; and (b) without reference planes visible. This view is created by adjusting the opacity of the Bone segmentation - you may not see the blue axis if your opacity is 1 or you are using the Volume Rendering function and unsegmented DICOM.


<img src="https://github.com/user-attachments/assets/66501fe3-6b34-4080-9e8d-2d4614801c4b" width="800">


<details>
<summary> Coordinate system visualisation </summary>

``` python
import slicer
import numpy as np

inputMarkupsName = "Thitiorul_hard_tissue"
mspPlaneName = "MSP"
xzPlaneName = "X-Z plane"
originLandmarkLabel = "n"  # "nasion"

# -- Get nodes --
inputMarkups = slicer.util.getNode(inputMarkupsName)
mspPlane = slicer.util.getNode(mspPlaneName)
xzPlane = slicer.util.getNode(xzPlaneName)

# -- Find "n" coordinate --
def get_point_by_label(markupsNode, label):
    for i in range(markupsNode.GetNumberOfControlPoints()):
        if markupsNode.GetNthControlPointLabel(i) == label:
            pt = [0.0, 0.0, 0.0]
            markupsNode.GetNthControlPointPosition(i, pt)
            return np.array(pt)
    raise ValueError(f"Label {label} not found.")

n_coord = get_point_by_label(inputMarkups, originLandmarkLabel)

# -- Get plane normals --
msp_normal = np.array(mspPlane.GetNormal())        # Y: normal to MSP
xz_normal = np.array(xzPlane.GetNormal())          # "Z": perpendicular to MSP and world Z

# -- Define axes --
# Y-axis: MSP normal (midline, usually superior-inferior, but depends on fitting)
y_axis = msp_normal / np.linalg.norm(msp_normal)

# Z-axis: X-Z plane normal, but make sure it points ANTERIOR (out of face)
z_axis = xz_normal / np.linalg.norm(xz_normal)
# (If necessary, flip sign so it points anterior—eyeball it in Slicer)

# X-axis: right, so cross(Y, Z)
x_axis = np.cross(y_axis, z_axis)
x_axis /= np.linalg.norm(x_axis)
# (If necessary, flip sign so X points to patient’s right)

###Visualize the axes in Slicer###
origin = n_coord
length = 100

def create_axis_line(name, axis_vector, color):
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    node.AddControlPointWorld(origin.tolist())
    endpoint = origin + axis_vector * length
    node.AddControlPointWorld(endpoint.tolist())
    disp = node.GetDisplayNode()
    disp.SetSelectedColor(color)
    disp.SetLineThickness(1.0)
    node.SetLocked(True)

create_axis_line('X_axis', x_axis, [1, 0, 0])  # Red
create_axis_line('Y_axis', y_axis, [0, 1, 0])  # Green
create_axis_line('Z_axis', z_axis, [0, 0, 1])  # Blue
```

</details>


### Creating the predicted soft tissue measurements

The code below will be a GUI (Graphic User Interface) that executes the calculations for the predicted soft tissue landmark coordinates from the hard tissue coordinates. 
All of the options use the regression equations published by Thitiorul et al. (2020)[^2], with or without side specificity. As stated by the author, the midline soft tissue landmarks will be calculated using the **left** side's landmark coordinates in each instance and the x coordinate is fixed to **0**.  
In each instance, all the predicted landmarks will be saved in a new point list, with their suffix referring to option 1, 2 or 3 - based on the users choice of execution. 

As a research question, you can compare the predictive power of each of these implementations. 


Original prediction regressions by Thitiorul et al. (2020)[^2]

**Midline**

<table>
  <tr>
    <th>Landmark</th>
    <th>Axis</th>
    <th>Equation</th>
  </tr>
  <tr>
    <td rowspan="2">se'</td>
    <td>y</td>
    <td>-0.869 + 0.212 ss_y + 0.139 zy_z - 0.073 ecm_y</td>
  </tr>
  <tr>
    <td>z</td>
    <td>-1.198 - 1.159 nr_y + 0.691 nr_z - 0.208 iof_y</td>
  </tr>
  <tr>
    <td rowspan="2">npp'</td>
    <td>y</td>
    <td>3.182 + 0.271 ss_y + 0.423 nr_y - 0.098 ecm_y</td>
  </tr>
  <tr>
    <td>z</td>
    <td>5.345 - 0.607 nr_y + 0.840 nr_z</td>
  </tr>
  <tr>
    <td rowspan="2">npa'</td>
    <td>y</td>
    <td>0.587 + 0.739 ss_y + 0.109 pr_z + 0.242 zy_x</td>
  </tr>
  <tr>
    <td>z</td>
    <td>4.315 - 0.371 ss_y + 0.573 ss_z + 0.285 nr_z</td>
  </tr>
  <tr>
    <td rowspan="2">pn'</td>
    <td>y</td>
    <td>-2.091 + 0.818 ss_y + 0.152 pr_z + 0.251 zy_x</td>
  </tr>
  <tr>
    <td>z</td>
    <td>2.095 - 0.288 ss_y + 0.456 ss_z + 0.250 pr_z</td>
  </tr>
  <tr>
    <td rowspan="2">nd'</td>
    <td>y</td>
    <td>-2.040 + 0.865 ss_y + 0.120 pr_z + 0.241 zy_x</td>
  </tr>
  <tr>
    <td>z</td>
    <td>3.626 - 0.392 ss_y + 0.842 ss_z</td>
  </tr>
  <tr>
    <td rowspan="2">sn'</td>
    <td>y</td>
    <td>-1.902 + 0.676 ss_y + 0.260 pr_y + 0.198 zy_x</td>
  </tr>
  <tr>
    <td>z</td>
    <td>6.455 - 0.269 ss_y + 0.551 ss_z + 0.277 pr_z</td>
  </tr>
</table>



**Bilateral**


<table>
  <tr>
    <th>Side</th>
    <th>Landmark</th>
    <th>Axis</th>
    <th>Equation</th>
  </tr>
  <!-- Left Side -->
  <tr>
    <td rowspan="12" style="vertical-align:middle;text-align:center;">Left</td>
    <td rowspan="3">al'L</td>
    <td>x</td>
    <td>7.101 + 0.107 pr_y + 0.316 iof_x - 0.076 zy_y</td>
  </tr>
  <tr>
    <td>y</td>
    <td>2.427 - 0.320 nr_z + 0.733 ss_y + 0.129 pr_z</td>
  </tr>
  <tr>
    <td>z</td>
    <td>2.897 - 0.218 ss_y + 0.464 ss_z + 0.305 pr_z</td>
  </tr>
  <tr>
    <td rowspan="3">als'L</td>
    <td>x</td>
    <td>3.167 + 0.174 iof_x + 0.097 zy_x</td>
  </tr>
  <tr>
    <td>y</td>
    <td>3.993 + 0.453 ss_y + 0.270 pr_y + 0.072 pr_z</td>
  </tr>
  <tr>
    <td>z</td>
    <td>3.827 - 0.466 ss_y + 0.674 ss_z + 0.257 iof_y</td>
  </tr>
  <tr>
    <td rowspan="3">alp'L</td>
    <td>x</td>
    <td>7.885 + 0.060 pr_z + 0.310 iof_x</td>
  </tr>
  <tr>
    <td>y</td>
    <td>4.199 + 0.398 ss_y + 0.224 pr_y + 0.247 iof_y</td>
  </tr>
  <tr>
    <td>z</td>
    <td>2.054 - 0.419 ss_y + 0.433 ss_z + 0.332 pr_z</td>
  </tr>
  <tr>
    <td rowspan="3">ali'L</td>
    <td>x</td>
    <td>4.611 + 0.239 iof_x - 0.070 zy_y</td>
  </tr>
  <tr>
    <td>y</td>
    <td>-0.890 + 0.476 pr_y + 0.377 ss_y + 0.089 zy_x</td>
  </tr>
  <tr>
    <td>z</td>
    <td>0.404 + 0.499 ss_y + 0.312 pr_z - 0.119 zy_y</td>
  </tr>
  <!-- Right Side -->
  <tr>
    <td rowspan="12" style="vertical-align:middle;text-align:center;">Right</td>
    <td rowspan="3">al'R</td>
    <td>x</td>
    <td>8.967 + 0.125 pr_y + 0.249 iof_x - 0.079 zy_y</td>
  </tr>
  <tr>
    <td>y</td>
    <td>0.338 - 0.264 nr_z + 0.760 ss_y + 0.151 pr_z</td>
  </tr>
  <tr>
    <td>z</td>
    <td>2.778 - 0.223 ss_y + 0.437 ss_z + 0.325 pr_z</td>
  </tr>
  <tr>
    <td rowspan="3">als'R</td>
    <td>x</td>
    <td>3.244 + 0.225 iof_x + 0.079 zy_x</td>
  </tr>
  <tr>
    <td>y</td>
    <td>-1.183 + 0.628 pr_y + 0.151 ecm_z</td>
  </tr>
  <tr>
    <td>z</td>
    <td>3.864 - 0.499 ss_y + 0.685 ss_z + 0.350 iof_y</td>
  </tr>
  <tr>
    <td rowspan="3">alp'R</td>
    <td>x</td>
    <td>12.069 + 0.045 pr_z + 0.207 iof_x</td>
  </tr>
  <tr>
    <td>y</td>
    <td>6.126 + 0.626 ss_y + 0.323 iof_y</td>
  </tr>
  <tr>
    <td>z</td>
    <td>2.578 - 0.404 ss_y + 0.403 ss_z + 0.350 pr_z</td>
  </tr>
  <tr>
    <td rowspan="3">ali'R</td>
    <td>x</td>
    <td>6.729 + 0.100 pr_y + 0.165 iof_x - 0.062 zy_y</td>
  </tr>
  <tr>
    <td>y</td>
    <td>-2.325 + 0.504 pr_y + 0.345 ss_y + 0.112 zy_x</td>
  </tr>
  <tr>
    <td>z</td>
    <td>6.363 - 0.161 ss_y + 0.468 ss_z + 0.350 pr_z</td>
  </tr>
</table>



The pop-up widget will offer you three options: 


#### Option 1 - As original paper, assuming symmetry
Use this option if your sample does not exhibit significant difference between the left and right. All prediction regressions are created based on the LEFT side measurements and they are then mirrored onto the right side.   


#### Option 2 - As original paper, with missing parts
Use this option if your sample does not have the "pair" of all the bilateral landmarks. The script tries to find the missing hard tissue landmarks and substitutes it with their other side equivalent.
Thitiorul et al. (2020)[^2] states:
> the left or the right bone landmarks can be used in our equations, interchangeably, if the bone landmarks on one side do not  exist


<details>
<summary> GUI to create the predicted soft tissue landmarks</summary>

``` python
import slicer
import qt
import numpy as np

def get_point_or_replace(markupsNode, label, opposite_label):
    for i in range(markupsNode.GetNumberOfControlPoints()):
        if markupsNode.GetNthControlPointLabel(i) == label:
            pt = [0.0, 0.0, 0.0]
            markupsNode.GetNthControlPointPosition(i, pt)
            return pt
    for i in range(markupsNode.GetNumberOfControlPoints()):
        if markupsNode.GetNthControlPointLabel(i) == opposite_label:
            pt = [0.0, 0.0, 0.0]
            markupsNode.GetNthControlPointPosition(i, pt)
            return pt
    raise ValueError(f"Neither {label} nor {opposite_label} found.")

def run_soft_tissue_regression(hardTissueNode, outputName, mode):
    def get_point_by_label(markupsNode, label):
        for i in range(markupsNode.GetNumberOfControlPoints()):
            if markupsNode.GetNthControlPointLabel(i) == label:
                pt = [0.0, 0.0, 0.0]
                markupsNode.GetNthControlPointPosition(i, pt)
                return pt
        raise ValueError(f"Label {label} not found")

    if mode == "replace":
        zy_L = get_point_or_replace(hardTissueNode, "zy_L", "zy_R")
        zy_R = get_point_or_replace(hardTissueNode, "zy_R", "zy_L")
        ecm_L = get_point_or_replace(hardTissueNode, "ecm_L", "ecm_R")
        ecm_R = get_point_or_replace(hardTissueNode, "ecm_R", "ecm_L")
        iof_L = get_point_or_replace(hardTissueNode, "iof_L", "iof_R")
        iof_R = get_point_or_replace(hardTissueNode, "iof_R", "iof_L")
    else:
        zy_L = get_point_by_label(hardTissueNode, "zy_L")
        zy_R = get_point_by_label(hardTissueNode, "zy_R")
        ecm_L = get_point_by_label(hardTissueNode, "ecm_L")
        ecm_R = get_point_by_label(hardTissueNode, "ecm_R")
        iof_L = get_point_by_label(hardTissueNode, "iof_L")
        iof_R = get_point_by_label(hardTissueNode, "iof_R")

    ss = get_point_by_label(hardTissueNode, "ss")
    nr = get_point_by_label(hardTissueNode, "nr")
    pr = get_point_by_label(hardTissueNode, "pr")

    if mode == "mirror":
        zy_R = zy_L
        ecm_R = ecm_L
        iof_R = iof_L

    zy_L_x, zy_L_y, zy_L_z = abs(zy_L[0]), zy_L[1], abs(zy_L[2])
    zy_R_x, zy_R_y, zy_R_z = abs(zy_R[0]), zy_R[1], abs(zy_R[2])
    ecm_L_y = ecm_L[1]
    ecm_R_y = ecm_R[1]
    ecm_R_z = abs(ecm_R[2])
    ss_y, ss_z = ss[1], abs(ss[2])
    nr_y, nr_z = nr[1], abs(nr[2])
    iof_L_x, iof_L_y = abs(iof_L[0]), iof_L[1]
    iof_R_x, iof_R_y = abs(iof_R[0]), iof_R[1]
    pr_y, pr_z = pr[1], abs(pr[2])

    FLIP_Y = False
    def y_out(val):
        return -val if FLIP_Y else val

    se_y = y_out(-0.869 + 0.212*ss_y + 0.139*zy_L_z - 0.073*ecm_L_y)
    se_z = -1.198 - 1.159*nr_y + 0.691*nr_z - 0.208*iof_L_y

    npp_y = y_out(3.182 + 0.271*ss_y + 0.423*nr_y - 0.098*ecm_L_y)
    npp_z = 5.345 - 0.607*nr_y + 0.840*nr_z

    npa_y = y_out(0.587 + 0.739*ss_y + 0.109*pr_z + 0.242*zy_L_x)
    npa_z = 4.315 - 0.371*ss_y + 0.573*ss_z + 0.285*nr_z

    pn_y = y_out(-2.091 + 0.818*ss_y + 0.152*pr_z + 0.251*zy_L_x)
    pn_z = 2.095 - 0.288*ss_y + 0.456*ss_z + 0.250*pr_z

    nd_y = y_out(-2.040 + 0.865*ss_y + 0.120*pr_z + 0.241*zy_L_x)
    nd_z = 3.626 - 0.392*ss_y + 0.842*ss_z

    sn_y = y_out(-1.902 + 0.676*ss_y + 0.260*pr_y + 0.198*zy_L_x)
    sn_z = 6.455 - 0.269*ss_y + 0.551*ss_z + 0.277*pr_z

    alL_x = -(7.101 + 0.107*pr_y + 0.316*iof_L_x - 0.076*zy_L_y)
    alL_y = y_out(2.427 - 0.320*nr_z + 0.733*ss_y + 0.129*pr_z)
    alL_z = 2.897 - 0.218*ss_y + 0.464*ss_z + 0.305*pr_z

    alsL_x = -(3.167 + 0.174*iof_L_x + 0.097*zy_L_x)
    alsL_y = y_out(3.993 + 0.453*ss_y + 0.270*pr_y + 0.072*pr_z)
    alsL_z = 3.827 - 0.466*ss_y + 0.674*ss_z + 0.257*iof_L_y

    alpL_x = -(7.885 + 0.060*pr_z + 0.310*iof_L_x)
    alpL_y = y_out(4.199 + 0.398*ss_y + 0.224*pr_y + 0.247*iof_L[1])
    alpL_z = 2.054 - 0.419*ss_y + 0.433*ss_z + 0.332*pr_z

    aliL_x = -(4.611 + 0.239*iof_L_x - 0.070*zy_L_y)
    aliL_y = y_out(-0.890 + 0.476*pr_y + 0.377*ss_y + 0.089*zy_L_x)
    aliL_z = 0.404 + 0.499*ss_y + 0.312*pr_z - 0.119*zy_L_y

    if mode == "mirror":
        alR_x, alR_y, alR_z = -alL_x, alL_y, alL_z
        alsR_x, alsR_y, alsR_z = -alsL_x, alsL_y, alsL_z
        alpR_x, alpR_y, alpR_z = -alpL_x, alpL_y, alpL_z
        aliR_x, aliR_y, aliR_z = -aliL_x, aliL_y, aliL_z
    else:
        alR_x = 8.967 + 0.125*pr_y + 0.249*iof_R_x - 0.079*zy_R_y
        alR_y = y_out(0.338 - 0.264*nr_z + 0.760*ss_y + 0.151*pr_z)
        alR_z = 2.778 - 0.223*ss_y + 0.437*ss_z + 0.325*pr_z

        alsR_x = 3.244 + 0.225*iof_R_x + 0.079*zy_R_x
        alsR_y = y_out(-1.183 + 0.628*pr_y + 0.151*ecm_R_z)
        alsR_z = 3.864 - 0.499*ss_y + 0.685*ss_z + 0.350*iof_R_y

        alpR_x = 12.069 + 0.045*pr_z + 0.207*iof_R_x
        alpR_y = y_out(6.126 + 0.626*ss_y + 0.323*iof_R_y)
        alpR_z = 2.578 - 0.404*ss_y + 0.403*ss_z + 0.350*pr_z

        aliR_x = 6.729 + 0.100*pr_y + 0.165*iof_R_x - 0.062*zy_R_y
        aliR_y = y_out(-2.325 + 0.504*pr_y + 0.345*ss_y + 0.112*zy_R_x)
        aliR_z = 6.363 - 0.161*ss_y + 0.468*ss_z + 0.350*pr_z

    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", outputName)
    node.SetDisplayVisibility(True)
    landmarks = [
        ("se'",  [0, se_y, se_z]),
        ("npp'", [0, npp_y, npp_z]),
        ("npa'", [0, npa_y, npa_z]),
        ("pn'",  [0, pn_y, pn_z]),
        ("nd'",  [0, nd_y, nd_z]),
        ("sn'",  [0, sn_y, sn_z]),
        ("al'L",   [alL_x, alL_y, alL_z]),
        ("als'L",  [alsL_x, alsL_y, alsL_z]),
        ("alp'L",  [alpL_x, alpL_y, alpL_z]),
        ("ali'L",  [aliL_x, aliL_y, aliL_z]),
        ("al'R",   [alR_x, alR_y, alR_z]),
        ("als'R",  [alsR_x, alsR_y, alsR_z]),
        ("alp'R",  [alpR_x, alpR_y, alpR_z]),
        ("ali'R",  [aliR_x, aliR_y, aliR_z]),
    ]
    for i, (label, coords) in enumerate(landmarks):
        flipped_coords = [coords[0], coords[1], -coords[2]]  # flip Z axis
        node.AddControlPoint(*flipped_coords)
        node.SetNthControlPointLabel(i, label)
    print(f"Prediction complete: {outputName}")

# ---- GUI ----
w = qt.QWidget()
w.setWindowTitle('Soft Tissue Regression')
l = qt.QVBoxLayout(w)

l.addWidget(qt.QLabel("Input hard tissue Markups: Thitiorul_hard_tissue"))

try:
    hardTissueNode = slicer.util.getNode("Thitiorul_hard_tissue")
except Exception:
    hardTissueNode = None

l.addWidget(qt.QLabel("Output Markups name:"))
outputNameEdit = qt.QLineEdit()
l.addWidget(outputNameEdit)

modeGroup = qt.QButtonGroup()
sideRadio = qt.QRadioButton("Side-specific regression (use left & right independently)")
mirrorRadio = qt.QRadioButton("As in paper: Use LEFT for both, mirror for right")
replaceRadio = qt.QRadioButton("Auto-replace: If one side missing, use the other")
sideRadio.setChecked(True)
modeGroup.addButton(sideRadio)
modeGroup.addButton(mirrorRadio)
modeGroup.addButton(replaceRadio)
l.addWidget(sideRadio)
l.addWidget(mirrorRadio)
l.addWidget(replaceRadio)

# Update output name when radio changes
def updateOutputName():
    if sideRadio.isChecked():
        method = "side"
    elif mirrorRadio.isChecked():
        method = "mirror"
    elif replaceRadio.isChecked():
        method = "replace"
    else:
        method = "side"
    outputNameEdit.setText(f"Predicted_Thitiorul_soft_tissue_{method}")

sideRadio.toggled.connect(updateOutputName)
mirrorRadio.toggled.connect(updateOutputName)
replaceRadio.toggled.connect(updateOutputName)
updateOutputName()  # Set initial name

runBtn = qt.QPushButton("Run Regression")
l.addWidget(runBtn)

def onRun():
    outputName = outputNameEdit.text
    mode = "side"
    if mirrorRadio.isChecked():
        mode = "mirror"
    elif replaceRadio.isChecked():
        mode = "replace"
    if not hardTissueNode:
        slicer.util.errorDisplay("Could not find node 'Thitiorul_hard_tissue'!")
        return
    run_soft_tissue_regression(hardTissueNode, outputName, mode)
    slicer.util.infoDisplay("Done! Check Markups for results.", windowTitle="Done")

runBtn.clicked.connect(onRun)
w.show()
```
</details>

You may notice the "flipping" options in this code - for a while when developing this code my landmarks were upside down and I found that it may be due to my z coordinate, going all the way back to how the direction of that axis is represented via the lines. It was easier to correct it this way, but feel free to report any potential errors should they arise for you. 

### Soft tissue landmark definition and error evaluation

Click here to download:[true_Thitiorul_soft_tissue.mrk.json](https://github.com/user-attachments/files/23696755/true_Thitiorul_soft_tissue.mrk.json)


The predicted landmarks do not have any "definitions" attached to them in the Markups module - unlike the other .json files you encountered. That is because their definitions are the same as the following markup file which you'd have to allocate on the scan's soft tissue to evaluate how well the prediction did. 

| Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|------------------|------------------|--------------|--------------|------------|------------|
| 0                | 1                | se'          | sellion          | The most posterior point in the midline of the nasal root. | Thitiorul et al. (2020)[^2] |
| 1                | 2                | pn'          | pronasale          | The most anterior point on the midsagittal profile of the nose | Thitiorul et al. (2020)[^2] |
| 2                | 3                | sn'          | subnasale          | The point at which the nasal septum between the nostrils merges with the upper cutaneous tip on the midsagittal plane | Thitiorul et al. (2020)[^2] |
| 3                | 4                | al'L         | left alare         | The most lateral point on the LEFT alar contour | Thitiorul et al. (2020)[^2] |
| 4                | 5                | als'L        | left superior alar groove        | The most superior point on the LEFT alar groove | Thitiorul et al. (2020)[^2] |
| 5                | 6                | alp'L        | left posterior alar groove        | The most posterior point on the LEFT  alar groove | Thitiorul et al. (2020)[^2] |
| 6                | 7                | ali'L        | left inferior alar groove        | The most inferior point on the LEFT alar groove | Thitiorul et al. (2020)[^2] |
| 7                | 8                | al'R         | right alare    R right alare             | The most lateral point on the RIGHT alar contour | Thitiorul et al. (2020)[^2] |
| 8                | 9                | als'R        | right superior alar groove      | The most superior point on the RIGHT alar groove | Thitiorul et al. (2020)[^2] |
| 9                | 10               | alp'R        | right posterior alar groove         | The most posterior point on the RIGHT  alar groove | Thitiorul et al. (2020)[^2] |
| 10               | 11               | ali'R        | right inferior alar groove       | The most inferior point on the RIGHT alar groove | Thitiorul et al. (2020)[^2] |
| 11               | 12               | n'           | soft tissue nasion       | The midpoint of the soft tissue contour of the base of the nasal root at the level of the frontonasal suture | Thitiorul et al. (2020)[^2] |
| 12               | 13               | npp'         | n-prn posterior         | The farthest point perpendicular from the line between n’ and prn, located posteriorly | Thitiorul et al. (2020)[^2] |
| 13               | 14               | npa'         | n-prn anterior         | The farthest point perpendicular from the line between n’ and prn, located anteriorly | Thitiorul et al. (2020)[^2] |
| 14               | 15               | nd'          | nasal drop          | The farthest point perpendicular from the line between prn and sn, located inferiorly | Thitiorul et al. (2020)[^2] |

Again, there will be two guiding lines: one connecting the soft tissue nasion with the pronasale (aiding the placement of **npp'** and **npa'**) and one connecting the pronasale to the subnasale (aiding the placement of **nd'**)

<details>
<summary>code for npp', npa' and nd' guiding lines </summary>

``` python
###lines to aid the placement of npp' npa' and nd' ####

G = slicer.util.getNode('true_Thitiorul_soft_tissue')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')

firstPoint = G.GetNthControlPointPositionVector(11)  # soft tissue nasion
L.AddControlPoint(firstPoint)
secondPoint = G.GetNthControlPointPositionVector(1) # pronasale
L.AddControlPoint(secondPoint)
L.SetName('for npp and npa')

L.GetDisplayNode().SetColor(0.0, 1.0, 0.0) # green

L.GetDisplayNode().Modified()

G = slicer.util.getNode('true_Thitiorul_soft_tissue')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')

firstPoint = G.GetNthControlPointPositionVector(1)  # pronasale
L.AddControlPoint(firstPoint)
secondPoint = G.GetNthControlPointPositionVector(2) # subnasale
L.AddControlPoint(secondPoint)
L.SetName('for nd')


L.GetDisplayNode().SetColor(0.0, 1.0, 0.0) # green

L.GetDisplayNode().Modified()
```

</details>


Expected view with guiding lines visible. This view is created by adjusting the opacity of the Skin segmentation - you may not see the _for nd_ line if your opacity is 1 or you are using the Volume Rendering function and unsegmented DICOM.


<img src="https://github.com/user-attachments/assets/9d04fc9c-6834-4c8e-853c-a0f293306924" width="500">



##### Error GUI



<details>
<summary> GUI for error </summary>

``` python
import slicer
import qt
import numpy as np

def getMatchingMarkupsNodes(pred_prefix, true_prefix):
    """Find all markups nodes with specified prefixes."""
    pred_nodes = []
    true_nodes = []
    for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode"):
        if n.GetName().startswith(pred_prefix):
            pred_nodes.append(n)
        elif n.GetName().startswith(true_prefix):
            true_nodes.append(n)
    return pred_nodes, true_nodes

def getLabelToIndexDict(markupsNode):
    """Return a dictionary mapping label to index (strips whitespace)."""
    return {markupsNode.GetNthControlPointLabel(i).strip(): i for i in range(markupsNode.GetNumberOfControlPoints())}

def connectMatchingLandmarks(predNode, trueNode, methodName, color):
    predLabels = getLabelToIndexDict(predNode)
    trueLabels = getLabelToIndexDict(trueNode)
    commonLabels = sorted(set(predLabels).intersection(trueLabels))

    if not commonLabels:
        slicer.util.errorDisplay("No matching labels found between the two nodes!")
        return

    # Remove previous error lines for this method
    for node in slicer.util.getNodesByClass('vtkMRMLMarkupsLineNode'):
        if f"error_{methodName}" in node.GetName():
            slicer.mrmlScene.RemoveNode(node)

    total_error = 0.0
    errors = []
    
    for label in commonLabels:
        pred_idx = predLabels[label]
        true_idx = trueLabels[label]
        pred_pos = np.array(predNode.GetNthControlPointPositionWorld(pred_idx))
        true_pos = np.array(trueNode.GetNthControlPointPositionWorld(true_idx))
        
        # Calculate Euclidean distance
        error = np.linalg.norm(pred_pos - true_pos)
        errors.append((label, error))
        total_error += error

        # Create error line
        lineNodeName = f"error_{methodName}_{label}"
        linesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", lineNodeName)
        linesNode.AddControlPointWorld(pred_pos.tolist())
        linesNode.AddControlPointWorld(true_pos.tolist())
        
        disp = linesNode.GetDisplayNode()
        if disp:
            disp.SetColor(color)
            disp.SetSelectedColor(color)
            disp.SetActiveColor(color)
            disp.SetOpacity(1.0)
            disp.SetGlyphScale(0)  # Hide spheres at endpoints
            disp.SetLineThickness(0.5)
        linesNode.SetDisplayVisibility(True)

    mean_error = total_error / len(commonLabels) if commonLabels else 0
    
    # Display results
    results_text = f"Method: {methodName}\n"
    results_text += f"Total landmarks: {len(commonLabels)}\n"
    results_text += f"Mean error: {mean_error:.2f} mm\n\n"
    results_text += "Individual errors:\n"
    for label, error in sorted(errors, key=lambda x: x[1], reverse=True):
        results_text += f"  {label}: {error:.2f} mm\n"
    
    print(results_text)
    slicer.util.infoDisplay(f"Connected {len(commonLabels)} landmark pairs.\nMean error: {mean_error:.2f} mm")

# -------- GUI --------
w = qt.QWidget()
w.setWindowTitle('Calculate Prediction Errors')
w.setWindowFlags(qt.Qt.Tool | qt.Qt.WindowStaysOnTopHint)
layout = qt.QVBoxLayout(w)

# Info label
infoLabel = qt.QLabel(
    "<b>Calculate prediction accuracy:</b><br>"
    "Select predicted and true soft tissue landmarks,<br>"
    "then choose which prediction method to evaluate."
)
infoLabel.setWordWrap(True)
layout.addWidget(infoLabel)

# Dropdowns for selecting nodes
predCombo = qt.QComboBox()
trueCombo = qt.QComboBox()
layout.addWidget(qt.QLabel("<b>Predicted landmarks:</b>"))
layout.addWidget(predCombo)
layout.addWidget(qt.QLabel("<b>True landmarks:</b>"))
layout.addWidget(trueCombo)

# Method selection - ONLY Mirror and Auto-replace
methodGroup = qt.QButtonGroup()
mirrorRadio = qt.QRadioButton("Standard method (LEFT landmarks, mirrored RIGHT)")
mirrorRadio.setToolTip("Uses LEFT side landmarks only, mirrors for RIGHT side.\nThis is the original validated method from the paper.")
autoReplaceRadio = qt.QRadioButton("Auto-replace method (for damaged skulls)")
autoReplaceRadio.setToolTip("Uses LEFT when available, mirrors RIGHT when LEFT is missing.\nUse this when left side of skull is damaged.")
mirrorRadio.setChecked(True)
methodGroup.addButton(mirrorRadio, 1)
methodGroup.addButton(autoReplaceRadio, 2)

layout.addWidget(qt.QLabel("<b>Prediction method used:</b>"))
layout.addWidget(mirrorRadio)
layout.addWidget(autoReplaceRadio)

# Method names and colors
methodInfo = {
    1: ("Standard", (1.0, 0.0, 1.0)),      # Magenta for standard/mirror
    2: ("AutoReplace", (0.0, 1.0, 1.0))    # Cyan for auto-replace
}

def populateDropdowns():
    predCombo.clear()
    trueCombo.clear()
    pred_prefix = "Predicted"
    true_prefix = "true"
    pred_nodes, true_nodes = getMatchingMarkupsNodes(pred_prefix, true_prefix)
    global _pred_nodes, _true_nodes
    _pred_nodes, _true_nodes = pred_nodes, true_nodes
    for n in pred_nodes:
        predCombo.addItem(n.GetName())
    for n in true_nodes:
        trueCombo.addItem(n.GetName())

populateDropdowns()

def onCalculate():
    if predCombo.currentIndex < 0 or trueCombo.currentIndex < 0:
        slicer.util.errorDisplay("Please select both predicted and true landmark nodes.")
        return
    
    methodId = methodGroup.checkedId()
    if methodId not in methodInfo:
        slicer.util.errorDisplay("Please select a prediction method.")
        return
    
    methodName, color = methodInfo[methodId]
    predNode = _pred_nodes[predCombo.currentIndex]
    trueNode = _true_nodes[trueCombo.currentIndex]
    connectMatchingLandmarks(predNode, trueNode, methodName, color)

calculateButton = qt.QPushButton("Calculate Errors")
calculateButton.setStyleSheet("background-color: #E91E63; color: white; font-weight: bold; padding: 8px;")
calculateButton.clicked.connect(onCalculate)
layout.addWidget(calculateButton)

# Separator
separator = qt.QFrame()
separator.setFrameShape(qt.QFrame.HLine)
separator.setFrameShadow(qt.QFrame.Sunken)
layout.addWidget(separator)

refreshButton = qt.QPushButton("Refresh Node List")
def onRefresh():
    populateDropdowns()
refreshButton.clicked.connect(onRefresh)
layout.addWidget(refreshButton)

w.setLayout(layout)
w.show()
w.raise_()

```

</details>

## Output

What can you expect as the outputs from the previous codes? The error lines should appear with their names reflecting the prediction method used, and measurement values represent the Euclidean distance between predicted and true landmark positions in millimeters.

[Guide to copy measurements to clipboard](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md#content-summary)

| Measurement Type | Name | Value (mm) | Notes |
|------------------|------|------------|-------|
| Guide Line | for_nr | 19.6 | ❌ Not a real measurement - helper line for landmark placement |
| Guide Line | for_ss | 17.95 | ❌ Not a real measurement - helper line for landmark placement |
| Guide Line | for_npp_and_npa | 47.5 | ❌ Not a real measurement - helper line for landmark placement |
| Guide Line | for_nd | 16.37 | ❌ Not a real measurement - helper line for landmark placement |
| Axis Visualization | X_axis | 100 | ❌ Not a real measurement - coordinate system visualization |
| Axis Visualization | Y_axis | 100 | ❌ Not a real measurement - coordinate system visualization |
| Axis Visualization | Z_axis | 100 | ❌ Not a real measurement - coordinate system visualization |
| **Standard Method** | error_Standard_al'L | 3.22 | Left alare prediction error |
| **Standard Method** | error_Standard_al'R | 5.42 | Right alare prediction error |
| **Standard Method** | error_Standard_ali'L | 24.43 | Left inferior alar groove prediction error |
| **Standard Method** | error_Standard_ali'R | 23.43 | Right inferior alar groove prediction error |
| **Standard Method** | error_Standard_alp'L | 4.52 | Left posterior alar groove prediction error |
| **Standard Method** | error_Standard_alp'R | 4.87 | Right posterior alar groove prediction error |
| **Standard Method** | error_Standard_als'L | 3.34 | Left superior alar groove prediction error |
| **Standard Method** | error_Standard_als'R | 3.53 | Right superior alar groove prediction error |
| **Standard Method** | error_Standard_nd' | 3.82 | Nasal drop prediction error |
| **Standard Method** | error_Standard_npa' | 3.45 | N-prn anterior prediction error |
| **Standard Method** | error_Standard_npp' | 11.45 | N-prn posterior prediction error |
| **Standard Method** | error_Standard_pn' | 3.67 | Pronasale prediction error |
| **Standard Method** | error_Standard_se' | 7.05 | Sellion prediction error |
| **Standard Method** | error_Standard_sn' | 6.62 | Subnasale prediction error |
| **Auto-Replace Method** | error_AutoReplace_al'L | 3.22 | Left alare prediction error |
| **Auto-Replace Method** | error_AutoReplace_al'R | 5.42 | Right alare prediction error |
| **Auto-Replace Method** | error_AutoReplace_ali'L | 24.43 | Left inferior alar groove prediction error |
| **Auto-Replace Method** | error_AutoReplace_ali'R | 23.43 | Right inferior alar groove prediction error |
| **Auto-Replace Method** | error_AutoReplace_alp'L | 4.52 | Left posterior alar groove prediction error |
| **Auto-Replace Method** | error_AutoReplace_alp'R | 4.87 | Right posterior alar groove prediction error |
| **Auto-Replace Method** | error_AutoReplace_als'L | 3.34 | Left superior alar groove prediction error |
| **Auto-Replace Method** | error_AutoReplace_als'R | 3.53 | Right superior alar groove prediction error |
| **Auto-Replace Method** | error_AutoReplace_nd' | 3.82 | Nasal drop prediction error |
| **Auto-Replace Method** | error_AutoReplace_npa' | 3.45 | N-prn anterior prediction error |
| **Auto-Replace Method** | error_AutoReplace_npp' | 11.45 | N-prn posterior prediction error |
| **Auto-Replace Method** | error_AutoReplace_pn' | 3.67 | Pronasale prediction error |
| **Auto-Replace Method** | error_AutoReplace_se' | 7.05 | Sellion prediction error |
| **Auto-Replace Method** | error_AutoReplace_sn' | 6.62 | Subnasale prediction error |


> [!NOTE]
> In this example, both methods produced identical results because all LEFT side landmarks were present. You would see differences between the two methods only when LEFT side landmarks are missing and the Auto-Replace method substitutes them with mirrored RIGHT side landmarks.

> [!TIP]
> This method is to be tested in different populations among various population-affinities, ages and BMI potentially, so make sure you include these additional factors and consider them during statistical analysis. The **Standard Method** uses LEFT side landmarks only (as validated in the paper), while the **Auto-Replace Method** is useful when LEFT side landmarks are unavailable due to skull damage.


# Bibliography

[^1]: 3D Slicer webpage https://www.slicer.org/
[^2]: Thitiorul, S., et al. (2020). "Three-Dimensional Prediction of the Nose for Facial Approximation in a Thai Population." J Forensic Sci 65(3): 707-714.
[^3]: Rynn, C., et al. (2010). "Prediction of nasal morphology from the skull." Forensic Science Medicine and Pathology 6(1): 20-34.


[^3]: Strapasson, R. A. P. and R. F. H. Melani (2020). "Facial reconstruction: Validation of the Tedeschi-Oliveira method for estimating the pronasale point in Brazilians." Braz Oral Res 34: e091.
[^4]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." International Journal of Legal Medicine 130(3): 863-879.
[^5]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^6]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^7]: Farkas, L. G. (1994). Anthropometry of the Head and Face, Lippincott Williams & Wilkins.
[^8]: Rynn, C., et al. (2010). "Prediction of nasal morphology from the skull." Forensic Science Medicine and Pathology 6(1): 20-34.

[^2]: Rynn, C. (2006). Craniofacial Approximation and Reconstruction: Tissue Depth Patterning and the Prediction of the Nose. Anatomy and Forensic Anthropology, School of Life Sciences. Dundee, United Kingdom, University of Dundee. Doctor of Philosophy.
[^3]: Rynn, C., et al. (2010). "Prediction of nasal morphology from the skull." Forensic Science Medicine and Pathology 6(1): 20-34.
[^4]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." International Journal of Legal Medicine 130(3): 863-879.
[^5]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^6]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^7]: Howells, W. W. (1937). "The designation of the principle anthrometric landmarks on the head and skull." American Journal of Physical Anthropology 22(3): 477-494.
[^8]: Howells, W. W. (1974). Cranial variation in man: A study by multivariate analysis of patterns of difference among recent human populations. Cambridge, Harvard University.
[^9]: Kolar, J. and E. Salter (1997). Craniofacial anthropometry: practical measurement of the head and face for clinical, surgical, and research use. Springfield, Charles C Thomas.
[^7]: Farkas, L. G. (1994). Anthropometry of the Head and Face, Lippincott Williams & Wilkins.
