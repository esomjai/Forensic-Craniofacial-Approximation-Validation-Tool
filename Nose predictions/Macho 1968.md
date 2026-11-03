# The Compound Method by Macho, 1968[^2]

> [!WARNING]
> The method does NOT provide regressions that are applicable in the forensic context as all equations contain age in years. Please only use for data collection a nd further analysis, NOT prediction!

The guide of this method represents Rynn’s (2010)[^8] interpretation of the original method  which was based on Goldhamer’s (1926)[^3] hypothesis by Macho et al. (1986)[^2]. 

The prerequisite to implement this study is to be able to see the sella turcica on the scan you're collecting data on - then allocate the sellion landmarks. Refer to discussion on this specific landmark ([Sellion or Sella points](#sellion-or-sella-points))

> [!NOTE]
> The method is illustrated by the 3D Slicer[^1] Sample Data for Post Dental Surgery CT in screenshots. For representing the general population, individuals without facial surgery would be chosen in research - this is only for demonstration purposes. Also note that some landmarks were not visible - again, you would exclude individuals from a study where landmarks cannot be reliably placed, but we proceeded to show our methodology. 


> [!WARNING]
> This method also follows first two steps mentioned in the “Start here” section – after loading the DICOM file, please re-orient the scan in the Frankfort horizontal plane. Please note that the reference plane in this method (SN plane) will NOT be reoriented to act as the transverse plane as its significance is in the measurements, not landmarking.


Steps in this guide 
- [Background & framework for Sellion](#sellion-or-sella-points)
- [Creating the INB plane](#creating-the-inb-plane)
- [Creating the SN plane and line](#sn-plane-and-line)
- Establishing the framework for measurements
  - [Code for projecting the length for apertura piriformis onto the INB plane](#code-for-projecting-the-length-for-apertura-piriformis-onto-the-inb-plane)
  - [Code for projecting the height of bony nose (no.3) onto the INB plane](#code-for-projecting-the-height-of-bony-nose-no3-onto-the-inb-plane)
  - [Code for line bisecting P & parallel to SN line](#code-for-line-bisecting-p--parallel-to-sn-line)
  - [Code for projecting the P parallel line onto INB](#code-for-projecting-the-p-parallel-line-onto-inb)
  - [Code for creating a line bisecting the rhinion & parallel to SN line](#code-for-creating-a-line-bisecting-the-rhinion--parallel-to-sn-line)
  - [Code for projecting rhi parallel line to INB](#code-for-projecting-rhi-parallel-line-to-inb)
  - [Code to find the intersection point of the 3 INB projection line & rhi parallel projection line](#code-to-find-the-intersection-point-of-the-3-inb-projection-line--rhi-parallel-projection-line)
  - [Code to find the intersection point of the 3 INB projection line & P parallel projection line](#code-to-find-the-intersection-point-of-the-3-inb-projection-line--p-parallel-projection-line)
- Establishing measurements
  - [Code for apertura piriformis (measurement no. 2)](#code-for-apertura-piriformis-measurement-no-2)
  - [Code for the height of bony nose (measurement no.3)](#code-for-the-height-of-bony-nose-measurement-no3)
  - [Code for P max projection (no.5)](#code-for-p-max-projection-no5)
  - [Code for height of rhinion (no. 7)](#code-for-height-of-rhinion-no-7)
  - [Code for prominence of rhinion in relation to the n-aca plane (no.6)](#code-for-prominence-of-rhinion-in-relation-to-the-n-aca-plane-no6)
  - [Code for P max (no.4)](#code-for-p-max-no4)
  - [Code for the angle between the plane spina nasalis anterior - nasion & spina nasalis anterior - rhinion plane (no.9)](#code-for-the-angle-between-the-plane-spina-nasalis-anterior---nasion--spina-nasalis-anterior---rhinion-plane-no9)
- [ALL code in one snippet](#all-code-in-one-snippet)
- [Output](#output)
- [Future directions](#future-directions)
- [Bibliography](#bibliography)

 
Landmarks in this guide: 

| Position in code | Position in file | Name in file | Landmark name | Definition                                                                                                                     | Defined by            |
|------------------|------------------|--------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 0                | 1                | nasion       | nasion        | Intersection of the nasofrontal sutures in the median plane                                                                    | Rynn et al. 2010[^8]     |
| 1                | 2                | inion        | inion         | Median point between the apices of the superior nuchal lines and at the base of the external occipital protuberance (not the tip of the protuberance) | Rynn et al. 2010[^8]      |
| 2                | 3                | bregma       | bregma        | Where the sagittal and coronal sutures meet. Impossible to determine in juvenile skulls with anterior fontanelle, or with complete suture obliteration | Rynn et al. 2010[^8]      |
| 3                | 4                | subspinale      | subspinale       | The deepest point seen in the profile view below the anterior nasal spine (orthodontic point A)         | Caple and Stephan 2016[^7]     |
| 4               | 5              | rhinion     | rhinion      | Most rostral (end) point on the internasal suture. | Caple and Stephan 2016[^7]    |
| 5             | 6               | acanthion    | acanthion     | Most anterior tip of the anterior nasal spine                                                                                 | Rynn et al. 2010[^8]      |
| 6                | 7                |  P  |   prominence  | most prominent point among the ossa nasalia      | Macho, 1986[^2] |



### Illustration of the landmarks 

Credit to Tinotenda Chiyangwa©[^9] 

**Hard tissue**

<img src="https://github.com/user-attachments/assets/fe908c4a-904a-4c6c-a195-9f45fc618e82" width="500">


**Soft tissue**

<img src="https://github.com/user-attachments/assets/fe908c4a-904a-4c6c-a195-9f45fc618e82" width="500">


> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan has to be re-aligned in the FHP
- [ ] You should have a Bone and Skin model via segmentation (explained later)

## Sellion or Sella points

By definition, the sella point is a floating landmark. It is used in lateral cephalograms, mainly in dentistry then got adapted for craniofacial measurements in 2D as well.  With the wider use of CBCTs, the allocation of this significant landmark in 3D was debated as some defined it from the profile view (like the original lateral cephalogram and some called for a revised definition of allocating it in 3D. Pittayapat et al. (2014)[^5] found no consensus is defining the sellion in 3D, so they initiated one in their later research (Pittayapat et al. 2015)[^6]. By their definition, the sellion is located within a "coordinate system" comprising of 4 landmarks and vertical plane defined by the mid-APT and mid-ACP points. They also establish Sella 1 and Sella 2 (so not one sellion point) citing "the choice of using Sella 1 or Sella 2 made no significant difference" in reproducibility which with the nasion landmark will be sufficient orientations to fit the SN plane of orientation (sellion1-sellion 2-nasion). 

For the allocation of all landmarks, please download both: 

[Pittayapat_plane.mrk.json](https://github.com/user-attachments/files/20212666/Pittayapat_plane.mrk.json)


[hard_tissue_Macho.mrk.json](https://github.com/user-attachments/files/20212665/hard_tissue_Macho.mrk.json)




And proceed with the allocation of the Pittayapat_plane landmarks first. 

| Position in code | Position in file | Name in file | Landmark name | Definition                                                                                                                     | Defined by            |
|------------------|------------------|--------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 0                | 1                | ACP-R       | anterior clinoid process on the right       | The tip of the anterior clinoid process on the right side                                                                   | Pittayapat et al. 2014      |
| 1                | 2                | ACP-L       | anterior clinoid process on the left       | The tip of the anterior clinoid process on the left side                                                                   | Pittayapat et al. 2014      |
| 2                | 3                | APT-R       | apex of petrous temporal on right        | The apex of the petrous part of the temporal bone on the right side | Pittayapat et al. 2014    |
| 3                | 4                | APT-L       | apex of petrous temporal on left        | The apex of the petrous part of the temporal bone on the left side | Pittayapat et al. 2014    |


**Sellion allocation landmarks illustration**

Credit to Tinotenda Chiyangwa©[^9] 

<img src="https://github.com/user-attachments/assets/d82ca5be-3166-4d8a-9603-3ca173fd9530" width="500">

<img src="https://github.com/user-attachments/assets/e8faf6dd-13f3-485c-ba3c-fb482496bd37" width="500">



The code in the next section will achive the following: 
1) Calculates the midpoints between ACP-R and ACP-L (mid-ACP); between APT-R and APT-L (mid-APT) and adds these into the "Pittayapat  plane" markup list.
2) Creates the mid-ACP and mid-APT planes and their vertical counterparts; then establishes 3 control points on them for later calculations; then 
3) finds the intersections of the paired planes (mid-ACP plane & vertical mid-ACP plane; mid-APT plane & vertical mid-APT plane) and calls them **ACP axis** and **APT axis**, respectively. 
4) Creates two separate node lists (sellion1_node; sellion2_node) with sellion1 and sellion2 as their only points respectively and places these nodes in the environment onto their respective axis - it may not actually look like they are on the axis, but that is accounted for in the next step! It also adds restrictions on how you can toggle these points (explained in the next step). 

### Code for sellions to appear on their axes in the scene


<details>
<summary> Code for Sellions </summary>


```python
#######SN plane###########

###1 - midpoints###########

# Function to calculate the midpoint between two points
def calculate_midpoint(point1, point2):
    return [(point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2, (point1[2] + point2[2]) / 2]

# Retrieve the Pittayapat_plane node
F = getNode('Pittayapat_plane')

# Calculate midpoints
midACP = calculate_midpoint(F.GetNthControlPointPositionVector(0), F.GetNthControlPointPositionVector(1))
midAPT = calculate_midpoint(F.GetNthControlPointPositionVector(2), F.GetNthControlPointPositionVector(3))

# Add the midpoints to the Pittayapat_plane node
F.AddControlPoint(midACP[0], midACP[1], midACP[2])
F.SetNthControlPointLabel(F.GetNumberOfControlPoints() - 1, 'midACP')

F.AddControlPoint(midAPT[0], midAPT[1], midAPT[2])
F.SetNthControlPointLabel(F.GetNumberOfControlPoints() - 1, 'midAPT')

# Print the midpoint coordinates
print('midACP coordinates:', midACP)
print('midAPT coordinates:', midAPT)

#####2 - mid-ACP & vertical mid-ACP planes; mid-APT & vertical mid-APT planes + defining 3 control points on each#####################


import numpy as np

# Function to calculate the plane equation from three points
def calculate_plane(point1, point2, point3):
    v1 = np.array(point2) - np.array(point1)
    v2 = np.array(point3) - np.array(point1)
    normal_vector = np.cross(v1, v2)
    return normal_vector / np.linalg.norm(normal_vector)  # Normalize the normal vector

# Function to add a plane node in 3D Slicer
def add_plane_node(name, origin, normal):
    planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode')
    planeNode.SetName(name)
    planeNode.SetOrigin(origin[0], origin[1], origin[2])
    planeNode.SetNormal(normal.tolist())
    return planeNode

# Retrieve the Pittayapat_plane node
F = slicer.util.getNode('Pittayapat_plane')

# --- Create "mid-ACP" plane ---
point_midACP_1 = F.GetNthControlPointPositionVector(4)
point_midACP_2 = F.GetNthControlPointPositionVector(2)
point_midACP_3 = F.GetNthControlPointPositionVector(3)

# Calculate the plane normal vector for "mid-ACP"
normal_midACP = calculate_plane(point_midACP_1, point_midACP_2, point_midACP_3)

# Add "mid-ACP" plane node
midACP_plane = add_plane_node('mid-ACP', point_midACP_1, normal_midACP)

# --- Create "vertical mid-ACP" plane ---
vertical_normal_midACP = np.cross(normal_midACP, [0, 0, 1])  # Assuming vertical direction is z-axis
vertical_normal_midACP /= np.linalg.norm(vertical_normal_midACP)

# Add "vertical mid-ACP" plane node
vertical_midACP_plane = add_plane_node('vertical mid-ACP', point_midACP_1, vertical_normal_midACP)

# --- Create "mid-APT" plane ---
point_midAPT_1 = F.GetNthControlPointPositionVector(5)
point_midAPT_2 = F.GetNthControlPointPositionVector(0)
point_midAPT_3 = F.GetNthControlPointPositionVector(1)

# Calculate the plane normal vector for "mid-APT"
normal_midAPT = calculate_plane(point_midAPT_1, point_midAPT_2, point_midAPT_3)

# Add "mid-APT" plane node
midAPT_plane = add_plane_node('mid-APT', point_midAPT_1, normal_midAPT)

# --- Create "vertical mid-APT" plane ---
vertical_normal_midAPT = np.cross(normal_midAPT, [0, 0, 1])  # Assuming vertical direction is z-axis
vertical_normal_midAPT /= np.linalg.norm(vertical_normal_midAPT)

# Add "vertical mid-APT" plane node
vertical_midAPT_plane = add_plane_node('vertical mid-APT', point_midAPT_1, vertical_normal_midAPT)

print("Plane nodes 'mid-ACP,' 'vertical mid-ACP,' 'mid-APT,' and 'vertical mid-APT' have been created.")

# Retrieve three random control points for intersection calculations
def get_random_control_points_from_plane(origin, normal, offset=10.0):
    if np.allclose(normal, [0, 0, 1]):
        perp_vector1 = np.array([1, 0, 0])  # Use x-axis for perpendicular vector
    else:
        perp_vector1 = np.cross(normal, [0, 0, 1])
    perp_vector1 /= np.linalg.norm(perp_vector1)

    perp_vector2 = np.cross(normal, perp_vector1)
    perp_vector2 /= np.linalg.norm(perp_vector2)

    point1 = np.array(origin)
    point2 = point1 + offset * perp_vector1
    point3 = point1 + offset * perp_vector2

    return point1.tolist(), point2.tolist(), point3.tolist()

# Intersection line calculations
def calculate_intersection_line(plane1, plane2):
    normal1, d1 = plane1
    normal2, d2 = plane2

    direction = np.cross(normal1, normal2)
    if np.linalg.norm(direction) == 0:
        raise ValueError("Planes are parallel or coincident, no intersection exists.")

    A = np.array([normal1, normal2, direction])
    b = np.array([-d1, -d2, 0])
    point_on_line = np.linalg.solve(A.T @ A, A.T @ b)

    return point_on_line.tolist(), direction.tolist()

# Planes as tuples for intersection
plane_midACP = (normal_midACP, -np.dot(normal_midACP, point_midACP_1))
plane_vertical_midACP = (vertical_normal_midACP, -np.dot(vertical_normal_midACP, point_midACP_1))
plane_midAPT = (normal_midAPT, -np.dot(normal_midAPT, point_midAPT_1))
plane_vertical_midAPT = (vertical_normal_midAPT, -np.dot(vertical_normal_midAPT, point_midAPT_1))

# Calculate the intersection lines
ACP_axis_point, ACP_axis_direction = calculate_intersection_line(plane_midACP, plane_vertical_midACP)
APT_axis_point, APT_axis_direction = calculate_intersection_line(plane_midAPT, plane_vertical_midAPT)

print("ACP axis point:", ACP_axis_point)
print("ACP axis direction:", ACP_axis_direction)
print("APT axis point:", APT_axis_point)
print("APT axis direction:", APT_axis_direction)

#####3 - Axes length set, intersecion lines calculated- ACP axis and APT axis###########

import numpy as np

# Function to restrict an axis length to 200 mm (100 mm to and from the specified midpoint)
def restrict_axis_length_from_point(midpoint, direction, length=200.0):
    half_length = length / 2.0
    start_point = [midpoint[i] - half_length * direction[i] for i in range(3)]
    end_point = [midpoint[i] + half_length * direction[i] for i in range(3)]
    return start_point, end_point

# Retrieve the Pittayapat_plane node
F = slicer.util.getNode('Pittayapat_plane')

# Get the specific points saved in the Pittayapat_plane node
point_for_ACP_axis = F.GetNthControlPointPositionVector(4)  # Position 4
point_for_APT_axis = F.GetNthControlPointPositionVector(5)  # Position 5

# --- Define planes as tuples (normal vector, D value) ---
# Mid-ACP plane
plane_midACP = (np.array(midACP_plane.GetNormal()), -np.dot(np.array(midACP_plane.GetNormal()), midACP_plane.GetOrigin()))

# Vertical mid-ACP plane
plane_vertical_midACP = (np.array(vertical_midACP_plane.GetNormal()), -np.dot(np.array(vertical_midACP_plane.GetNormal()), vertical_midACP_plane.GetOrigin()))

# Mid-APT plane
plane_midAPT = (np.array(midAPT_plane.GetNormal()), -np.dot(np.array(midAPT_plane.GetNormal()), midAPT_plane.GetOrigin()))

# Vertical mid-APT plane
plane_vertical_midAPT = (np.array(vertical_midAPT_plane.GetNormal()), -np.dot(np.array(vertical_midAPT_plane.GetNormal()), vertical_midAPT_plane.GetOrigin()))

# --- Calculate Intersection Lines ---
# ACP axis (intersection of mid-ACP and vertical mid-ACP)
ACP_axis_point, ACP_axis_direction = calculate_intersection_line(plane_midACP, plane_vertical_midACP)
# Ensure ACP axis is centered at the point at position 4 in Pittayapat_plane
ACP_axis_direction /= np.linalg.norm(ACP_axis_direction)  # Normalize the direction vector
start_point_ACP, end_point_ACP = restrict_axis_length_from_point(point_for_ACP_axis, ACP_axis_direction)

# APT axis (intersection of mid-APT and vertical mid-APT)
APT_axis_point, APT_axis_direction = calculate_intersection_line(plane_midAPT, plane_vertical_midAPT)
# Ensure APT axis is centered at the point at position 5 in Pittayapat_plane
APT_axis_direction /= np.linalg.norm(APT_axis_direction)  # Normalize the direction vector
start_point_APT, end_point_APT = restrict_axis_length_from_point(point_for_APT_axis, APT_axis_direction)

# --- Create Markups Line Nodes for Visualization ---
# ACP axis visualization
ACP_axis_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "ACP Axis")
ACP_axis_line.AddControlPoint(vtk.vtkVector3d(start_point_ACP))
ACP_axis_line.AddControlPoint(vtk.vtkVector3d(end_point_ACP))

# APT axis visualization
APT_axis_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "APT Axis")
APT_axis_line.AddControlPoint(vtk.vtkVector3d(start_point_APT))
APT_axis_line.AddControlPoint(vtk.vtkVector3d(end_point_APT))

print("ACP axis (intersection line) created:")
print("Start point:", start_point_ACP)
print("End point:", end_point_ACP)

print("APT axis (intersection line) created:")
print("Start point:", start_point_APT)
print("End point:", end_point_APT)

#####4 - new nodes lists with sellion1 and sellion2, on their respective axes###########################

import vtk
import numpy as np

# Function to create a separate node list and add a point to it
def create_sellion_node(node_name, point_name, position, axis_point, axis_direction):
    # Create a new node for the sellion
    sellion_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", node_name)

    # Add the point to the node
    sellion_node.AddControlPoint(vtk.vtkVector3d(position))
    sellion_node.SetNthControlPointLabel(0, point_name)
    sellion_node.SetNthControlPointLocked(0, False)  # Allow manipulation

    # Enforce constraints to restrict the point to its axis
    def enforce_constraints(caller, event):
        current_position = np.array(sellion_node.GetNthControlPointPositionVector(0))  # Get current position
        constrained_position = project_point_onto_line(current_position, axis_point, axis_direction)  # Constrain to axis
        sellion_node.SetNthControlPointPosition(0, *constrained_position)  # Update position

    # Add observer to the node to constrain movement along the axis
    sellion_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, enforce_constraints)

    # Configure display node for translation-only interaction
    display_node = sellion_node.GetDisplayNode()
    if display_node:
        display_node.SetHandlesInteractive(True)
        display_node.SetTranslationHandleVisibility(True)  # Allow translation
        display_node.SetRotationHandleVisibility(False)    # Disable rotation
        display_node.SetScaleHandleVisibility(False)       # Disable scaling

    print(f"'{point_name}' added to '{node_name}' with constraints applied.")
    return sellion_node

# Function to project a point onto a line defined by a point and direction vector
def project_point_onto_line(point, line_point, line_direction):
    line_direction = np.array(line_direction) / np.linalg.norm(line_direction)  # Normalize direction
    point_vector = np.array(point) - np.array(line_point)
    projection_length = np.dot(point_vector, line_direction)
    projected_point = np.array(line_point) + projection_length * line_direction
    return projected_point.tolist()

# --- sellion1 node list ---
sellion1_node_name = "sellion1_node"
sellion1_point_name = "sellion1"
sellion1_position = ACP_axis_point  # Midpoint of the ACP axis
sellion1_node = create_sellion_node(sellion1_node_name, sellion1_point_name, sellion1_position, ACP_axis_point, ACP_axis_direction)

# --- sellion2 node list ---
sellion2_node_name = "sellion2_node"
sellion2_point_name = "sellion2"
sellion2_position = APT_axis_point  # Midpoint of the APT axis
sellion2_node = create_sellion_node(sellion2_node_name, sellion2_point_name, sellion2_position, APT_axis_point, APT_axis_direction)

print("sellion1 and sellion2 have been added to separate node lists with axis constraints.")
print(f"sellion1 initial position: {sellion1_position}")
print(f"sellion2 initial position: {sellion2_position}")
```



</details>



![image](https://github.com/user-attachments/assets/7a4a46a8-df78-41f4-9ceb-3d2d5904c4db)
What to expect after running the script immediately

5) To focus on the sellions, please hide all markups, except for thed 2 axes and 2 sellion point. The last bit of the script made the mini-coordinate sytem on both sellion to appear in order to help toggling them along their respective axes. As the sellions are close together, I would suggest hiding the other while moving the latter. Aim to position sellions in the middle of the sella turcica cavity. 

https://github.com/user-attachments/assets/15655643-87eb-436e-9e95-8df097f6a187

6) Once happy with the position of the sellions, please run this snippet to stop Slicer to trace their movement: 

``` python
########5 - Stop tracing sellion positions#######

# Function to remove all observers from a node
def remove_observers(node):
    if node:
        # Remove all observers from the node
        node.RemoveObservers(slicer.vtkMRMLMarkupsNode.PointModifiedEvent)
        print(f"Stopped tracking points in node: {node.GetName()}")

# Retrieve the "sellion1_node" and "sellion2_node"
sellion1_node = slicer.util.getNode('sellion1_node')
sellion2_node = slicer.util.getNode('sellion2_node')

# Remove observers from both nodes to stop tracking
remove_observers(sellion1_node)
remove_observers(sellion2_node)

print("Point tracking has been disabled for 'sellion1' and 'sellion2'.")
```


And you can also hide the interaction handles. 
![image](https://github.com/user-attachments/assets/aa268e72-89d3-454e-bd61-e151ce053efb)

## Allocate all the landmarks in "hard_tissue_Macho.json"

[hard_tissue_Macho.mrk.json](https://github.com/user-attachments/files/20212665/hard_tissue_Macho.mrk.json)

> [!IMPORTANT]
> The following codes can be all copied and pasted in one go, we chose to include explanation. For the whole snippet, go to: [ALL code in one snippet](#all-code-in-one-snippet)


<details>

<summary>Creating the INB plane</summary>

 Establishing a vertical profile plane INB based on the definition by Rynn et al. 2010.

> a midsagittal plane (INB) which bisected the inion, nasion and bregma


```python 
#INB plane#

import numpy as np
import slicer

# Get the points from the "hard_tissue_Macho" node
hardTissueNode = slicer.util.getNode('hard_tissue_Macho')
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

```
Expected view after INB is extended: 
![image](https://github.com/user-attachments/assets/073dc584-93d6-4038-b197-2bb386991e13)

</details>


<details>

<summary>SN plane and line</summary> 

The **SN plane** plane (for visualisation of the nasion-sellion plane in 3D) is created by the nasion and midsellion points (vector) and is set to be perpendicular to INB. The **sellions** is a line connecting the left and right sellions, **midsellion** is an addition to the hard tissue landmarks (at position 10) representing halfway through the sellions line and is used to create the SN line with the nasion landmark.

```python
############Creates SN line connecting the midpoint of sellions and the nasion; then SN plane established with the selion midpoint as the origin and its direction as perpendicular to the SN line's orientation########## 
import slicer
import numpy as np

# Access the necessary nodes
hardTissueNode = slicer.util.getNode('hard_tissue_Macho')
sellion1Node = slicer.util.getNode('sellion1_node')
sellion2Node = slicer.util.getNode('sellion2_node')

# Check for node existence
if not hardTissueNode or not sellion1Node or not sellion2Node:
    raise Exception("One or more nodes ('hard_tissue_Macho', 'sellion1_node', 'sellion2_node') not found.")

# Get positions from the sellion nodes
sellion1_pos = [0.0, 0.0, 0.0]
sellion1Node.GetNthControlPointPosition(0, sellion1_pos)

sellion2_pos = [0.0, 0.0, 0.0]
sellion2Node.GetNthControlPointPosition(0, sellion2_pos)

# Create a line node for 'sellions'
sellionsLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'sellions')
sellionsLineNode.AddControlPoint(sellion1_pos)
sellionsLineNode.AddControlPoint(sellion2_pos)
sellionsLineNode.GetDisplayNode().SetSelectedColor(0, 0, 1)  # Blue color

# Calculate the midpoint of 'sellions'
midpoint = (np.array(sellion1_pos) + np.array(sellion2_pos)) / 2

# Add the midpoint to 'hard_tissue_Macho'
hardTissueNode.AddControlPoint(midpoint.tolist(), 'midsellion')

# Retrieve the newly added 'midsellion' and the first point
point0 = [0.0, 0.0, 0.0]
hardTissueNode.GetNthControlPointPosition(0, point0)

midsellion = [0.0, 0.0, 0.0]
hardTissueNode.GetNthControlPointPosition(hardTissueNode.GetNumberOfControlPoints() - 1, midsellion)

# Create and configure the SN line
snLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'SN line')
snLineNode.AddControlPoint(midsellion)
snLineNode.AddControlPoint(point0)
snLineNode.GetDisplayNode().SetSelectedColor(1, 0.5, 0)  # Orange color

# Extend the SN line by 150 mm in both directions
direction = np.array(point0) - np.array(midsellion)
direction /= np.linalg.norm(direction)  # Normalize
extendedPoint1 = np.array(midsellion) + direction * 150
extendedPoint2 = np.array(midsellion) - direction * 150

snLineNode.SetNthControlPointPosition(0, extendedPoint1.tolist())
snLineNode.SetNthControlPointPosition(1, extendedPoint2.tolist())

# Create and configure the SN plane
snPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'SN')

# Set the plane's origin to the midpoint (ensures it meets the line)
planeOrigin = midpoint.tolist()
snPlaneNode.SetOriginWorld(planeOrigin)

# Set the plane's normal vector perpendicular to the SN line direction
# For simplicity, choose an orthogonal vector by swapping and negating components
planeNormal = np.cross(direction, [1, 0, 0])  # Find a vector orthogonal to the SN line
if np.linalg.norm(planeNormal) == 0:  # Handle edge case where direction aligns with [1, 0, 0]
    planeNormal = np.cross(direction, [0, 1, 0])
planeNormal /= np.linalg.norm(planeNormal)  # Normalize the vector

snPlaneNode.SetNormalWorld(planeNormal.tolist())

# Set the color of the plane to orange
displayNode = snPlaneNode.GetDisplayNode()
if displayNode:
    displayNode.SetColor(1.0, 0.5, 0.0)  # RGB values for orange

print("SN line and SN plane created successfully, with the plane meeting the line and parallel to it.")
```
![image](https://github.com/user-attachments/assets/c749c04c-9bca-4e3d-b14a-bb4b4aa5ccb0)
SN plane and SN line in the environment

</details>



### Establishing the measurements 

2.	Measurements 2, 3 and their projections onto the INB plane, a line bisecting the P which is parallel to SN and a line bisecting the rhinion which is also parallel to SN and their projections onto the INB plane – projections are necessary for the lines to intersect eventually on the “profile” as they would on a lateral cephalometry 
3.	3INB proj - rhi parallel intersection and 3INB proj - P parallel intersection: additional landmarks stored in the “hard tissue” node at positions 11 and 12 respectively to mark where the rhi parallel and P parallel projections are intersected by measurement 3 (nasion-acanthion line). 
4.	5 P max proj; 7 height of rhinion; 6 prominence of rhinion in relation to the n-aca plane; 4 P max; 9 angle between plane n-aca and rhi-aca plane as defined in the literature source







<details>

<summary>Code for apertura piriformis (measurement no. 2)</summary> 

```python
###height of apertura piriformis (measurement no. 2 in Macho, 1968)###
F=getNode('hard_tissue_Macho')  
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(4)     
#rhinion#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(5)
#acanthion#
L.AddControlPoint(secondPoint)
L.SetName('height of apertura piriformis rhi-aca')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(64/252,224/255,208/255)
##turqoise colour###
```
![image](https://github.com/user-attachments/assets/50bc4e8d-f63e-479b-93aa-38454127d9ae)

</details>

<details>
<summary>Code for projecting the length for apertura piriformis onto the INB plane</summary> 

```python
#####length of apertura piriformis projected onto INB plane#####
import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('height of apertura piriformis rhi-aca')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', '2 INB proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to yellow
projectedLineNode.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)  # RGB values for yellow
```
![image](https://github.com/user-attachments/assets/3f21cf03-3b0a-4883-a2fc-3522669136a2)
</details>

<details>
<summary>Code for the height of bony nose (measurement no.3)</summary> 

```python
F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(0)     
#nasion#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(5)
#acanthion#
L.AddControlPoint(secondPoint)
L.SetName('height of the bony nose nas-aca')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(230/255, 230/255, 250/255)

```
![image](https://github.com/user-attachments/assets/94604c90-27e9-4254-b09e-5dc778ba5cd5)
</details>

<details>
<summary>Code for projecting the height of bony nose (no.3) onto the INB plane</summary> 

```python

import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('height of the bony nose nas-aca')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', '3 INB proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to green
projectedLineNode.GetDisplayNode().SetSelectedColor(1.0, 0.0, 1.0)  # RGB values for magenta
```
![image](https://github.com/user-attachments/assets/ccce8870-cc8e-4b3a-8e9a-d93a26c9083c)

</details>

<details>
<summary>Code for line bisecting P & parallel to SN line</summary> 

# Get the 'hard_tissue_Macho' and 'SN line' nodes
hard_tissue_node = getNode('hard_tissue_Macho')
SN_line = getNode('SN line')

# Retrieve the coordinates of 'P' at position 6
P_para_position = hard_tissue_node.GetNthControlPointPositionVector(6)

# Determine the direction vector of 'SN line'
start_point_SN = SN_line.GetNthControlPointPositionVector(0)
end_point_SN = SN_line.GetNthControlPointPositionVector(1)
direction_vector = [end_point_SN[i] - start_point_SN[i] for i in range(3)]

# Normalize the direction vector
magnitude = sum([coord**2 for coord in direction_vector])**0.5
direction_vector = [coord / magnitude for coord in direction_vector]

# Calculate the new line's start and end points (100 mm in each direction)
half_length = 100  # half of 200 mm
start_point_new_line = [P_para_position[i] - half_length * direction_vector[i] for i in range(3)]
end_point_new_line = [P_para_position[i] + half_length * direction_vector[i] for i in range(3)]

# Create and configure the new line node
new_line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
new_line.AddControlPoint(start_point_new_line)
new_line.AddControlPoint(end_point_new_line)
new_line.SetName('P parallel')

# Set the line color to orange
line_display = new_line.GetDisplayNode()
line_display.SetColor(1.0, 0.647, 0.0)
```
![image](https://github.com/user-attachments/assets/418640fe-33b3-4c8c-a50c-687097220c01)

</details>

<details>
<summary>Code for projecting the P parallel line onto INB</summary> 

``` python
import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('P parallel')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'P parallel proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to yellow
projectedLineNode.GetDisplayNode().SetSelectedColor(1, 1, 0)  # RGB values for yellow
```
![image](https://github.com/user-attachments/assets/3be0a9ea-8d4f-4001-ad84-b3f984213edc)

</details>

<details>
<summary>Code for creating a line bisecting the rhinion & parallel to SN line</summary>  

```python 
# Get the 'hard_tissue_Macho' and 'SN line' nodes
hard_tissue_node = getNode('hard_tissue_Macho')
SN_line = getNode('SN line')

# Retrieve the coordinates of 'rhi' at position 4
rhi_para_position = hard_tissue_node.GetNthControlPointPositionVector(4)

# Determine the direction vector of 'SN line'
start_point_SN = SN_line.GetNthControlPointPositionVector(0)
end_point_SN = SN_line.GetNthControlPointPositionVector(1)
direction_vector = [end_point_SN[i] - start_point_SN[i] for i in range(3)]

# Normalize the direction vector
magnitude = sum([coord**2 for coord in direction_vector])**0.5
direction_vector = [coord / magnitude for coord in direction_vector]

# Calculate the new line's start and end points (100 mm in each direction)
half_length = 100  # half of 200 mm
start_point_new_line = [rhi_para_position[i] - half_length * direction_vector[i] for i in range(3)]
end_point_new_line = [rhi_para_position[i] + half_length * direction_vector[i] for i in range(3)]

# Create and configure the new line node
new_line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
new_line.AddControlPoint(start_point_new_line)
new_line.AddControlPoint(end_point_new_line)
new_line.SetName('rhi parallel')

# Set the line color to orange
line_display = new_line.GetDisplayNode()
line_display.SetColor(1.0, 0.6, 0.4)
```
![image](https://github.com/user-attachments/assets/172dce3e-3ecc-4343-afa6-e7cf9ed58a6f)

</details>


<details>
<summary>Code for projecting rhi parallel line to INB</summary>  
```python
import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('rhi parallel')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'rhi parallel proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to green
projectedLineNode.GetDisplayNode().SetSelectedColor(1, 1, 0)  # RGB values for yellow
```
![image](https://github.com/user-attachments/assets/9cea628a-0fa7-4acc-9b5b-5f2a77733d79)

</details>


<details>
<summary>Code to find the intersection point of the 3 INB projection line & rhi parallel projection line</summary>  

```python
import numpy as np

# Get the '3 INB proj' and 'rhi parallel proj' nodes
INB_proj_line = getNode('3 INB proj')
rhi_parallel_proj_line = getNode('rhi parallel proj')

# Retrieve control points of the lines
start_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(0))
end_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(1))

start_rhi_parallel_proj = np.array(rhi_parallel_proj_line.GetNthControlPointPositionVector(0))
end_rhi_parallel_proj = np.array(rhi_parallel_proj_line.GetNthControlPointPositionVector(1))

# Define the lines as vectors
vec_INB_proj_line = end_INB_proj_line - start_INB_proj_line
vec_rhi_parallel_proj = end_rhi_parallel_proj - start_rhi_parallel_proj

# Find the intersection point (if exists)
def find_line_intersection(p1, v1, p2, v2):
    w0 = p1 - p2
    a = np.dot(v1, v1)
    b = np.dot(v1, v2)
    c = np.dot(v2, v2)
    d = np.dot(v1, w0)
    e = np.dot(v2, w0)
    
    denom = a*c - b*b
    if denom == 0:
        raise ValueError("Lines are parallel and do not intersect.")
    
    s = (b*e - c*d) / denom
    t = (a*e - b*d) / denom
    
    intersection_point1 = p1 + s*v1
    intersection_point2 = p2 + t*v2
    
    if np.allclose(intersection_point1, intersection_point2):
        return intersection_point1
    else:
        raise ValueError("Lines do not intersect.")

try:
    intersection_point = find_line_intersection(start_INB_proj_line, vec_INB_proj_line, start_rhi_parallel_proj, vec_rhi_parallel_proj)
    
    # Save the intersection point as a new node in 'hard_tissue_Macho'
    hard_tissue = getNode('hard_tissue_Macho')
    new_control_point_index = hard_tissue.AddControlPoint(intersection_point)
    hard_tissue.SetNthControlPointLabel(new_control_point_index, '3INB proj - rhi parallel intersection')
    
    print("Intersection point successfully added to 'hard_tissue_Macho' node.")
except ValueError as e:
    print(str(e))
```
![image](https://github.com/user-attachments/assets/dfa9a55b-1561-455c-bcf3-b55739a2e6d6)
</details>


<details>
<summary>Code to find the intersection point of the 3 INB projection line & P parallel projection line</summary>  

```python
import numpy as np

# Get the '3 INB proj' and 'P parallel proj' nodes
INB_proj_line = getNode('3 INB proj')
P_parallel_proj_line = getNode('P parallel proj')

# Retrieve control points of the lines
start_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(0))
end_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(1))

start_P_parallel_proj = np.array(P_parallel_proj_line.GetNthControlPointPositionVector(0))
end_P_parallel_proj = np.array(P_parallel_proj_line.GetNthControlPointPositionVector(1))

# Define the lines as vectors
vec_INB_proj_line = end_INB_proj_line - start_INB_proj_line
vec_P_parallel_proj = end_P_parallel_proj - start_P_parallel_proj

# Find the intersection point (if exists)
def find_line_intersection(p1, v1, p2, v2):
    w0 = p1 - p2
    a = np.dot(v1, v1)
    b = np.dot(v1, v2)
    c = np.dot(v2, v2)
    d = np.dot(v1, w0)
    e = np.dot(v2, w0)
    
    denom = a*c - b*b
    if denom == 0:
        raise ValueError("Lines are parallel and do not intersect.")
    
    s = (b*e - c*d) / denom
    t = (a*e - b*d) / denom
    
    intersection_point1 = p1 + s*v1
    intersection_point2 = p2 + t*v2
    
    if np.allclose(intersection_point1, intersection_point2):
        return intersection_point1
    else:
        raise ValueError("Lines do not intersect.")

try:
    intersection_point = find_line_intersection(start_INB_proj_line, vec_INB_proj_line, start_P_parallel_proj, vec_P_parallel_proj)
    
    # Save the intersection point as a new node in 'hard_tissue_Macho'
    hard_tissue = getNode('hard_tissue_Macho')
    new_control_point_index = hard_tissue.AddControlPoint(intersection_point)
    hard_tissue.SetNthControlPointLabel(new_control_point_index, '3INB proj - P parallel intersection')
    
    print("Intersection point successfully added to 'hard_tissue_Macho' node.")
except ValueError as e:
    print(str(e))
``` 
![image](https://github.com/user-attachments/assets/0a5d9ff3-3f99-4bc7-bbc6-ad4d756de0f4)
</details>


<details>
<summary>Code for P max projection (no.5)</summary>  

```python

F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(9)     
#number is the number on list of saved points#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(0)
L.AddControlPoint(secondPoint)
L.SetName('5 P max proj')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)
```
![image](https://github.com/user-attachments/assets/99451541-b7fe-4608-a943-b2c42509d552)
</details>


<details>
<summary>Code for height of rhinion (no. 7)</summary>  

```python
F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(8)     
#3INB proj - rhi parallel intersection point#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(0)
#nasion#
L.AddControlPoint(secondPoint)
L.SetName('7 height of rhinion')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)
```
![image](https://github.com/user-attachments/assets/73c7a25d-e3b9-465c-83d2-750da0bedf95)

</details>


<details>
<summary>Code for prominence of rhinion in relation to the n-aca plane (no.6)</summary>  


```python
F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(8)     
#3INB proj - rhi parallel intersection point#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(4)
#rhinion#
L.AddControlPoint(secondPoint)
L.SetName('6 prominence of rhinion in relation to the n-aca plane')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)
```
![image](https://github.com/user-attachments/assets/5c5c15f5-2380-4d65-a64a-7adf60b6833b)
</details>


<details>
<summary>Code for P max (no.4)</summary>  


```python
F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(9)     
#3INB proj - rhi parallel intersection point#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(6)
#P#
L.AddControlPoint(secondPoint)
L.SetName('4 P max')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)
```
![image](https://github.com/user-attachments/assets/f03ac1a7-120c-472d-8ab1-f195f43f3689)

</details>

<details>
<summary>Code for the angle between the plane spina nasalis anterior - nasion & spina nasalis anterior - rhinion plane  (no.9) </summary>  

```python
import slicer
import numpy as np

# Get the nodes for the existing points and lines
hardTissueNode = slicer.util.getNode('hard_tissue_Macho')

# Get the positions of the control points
apexPoint = np.array(hardTissueNode.GetNthControlPointPosition(5))
firstControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(0))
thirdControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(4))

# Create the angle node
angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', '9 angle between plane n-aca and rhi-aca plane')
angleNode.AddControlPoint(firstControlPoint)  # First control point
angleNode.AddControlPoint(apexPoint)          # Second control point (apex)
angleNode.AddControlPoint(thirdControlPoint)  # Third control point

print("New angle '9 angle between plane n-aca and rhi-aca plane' created successfully.")
```
![image](https://github.com/user-attachments/assets/d94b5bad-ad50-48dc-90f0-edd13ece10a8)
</details>

<details>
<summary>ALL code in one snippet </summary>
Just copy+paste this after you allocated all hard_tissue_Macho landmarks


```python

#INB plane#

import numpy as np
import slicer

# Get the points from the "hard_tissue_Macho" node
hardTissueNode = slicer.util.getNode('hard_tissue_Macho')
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

############Creates SN line connecting the midpoint of sellions and the nasion; then SN plane established with the selion midpoint as the origin and its direction as perpendicular to the SN line's orientation########## 
import slicer
import numpy as np

# Access the necessary nodes
hardTissueNode = slicer.util.getNode('hard_tissue_Macho')
sellion1Node = slicer.util.getNode('sellion1_node')
sellion2Node = slicer.util.getNode('sellion2_node')

# Check for node existence
if not hardTissueNode or not sellion1Node or not sellion2Node:
    raise Exception("One or more nodes ('hard_tissue_Macho', 'sellion1_node', 'sellion2_node') not found.")

# Get positions from the sellion nodes
sellion1_pos = [0.0, 0.0, 0.0]
sellion1Node.GetNthControlPointPosition(0, sellion1_pos)

sellion2_pos = [0.0, 0.0, 0.0]
sellion2Node.GetNthControlPointPosition(0, sellion2_pos)

# Create a line node for 'sellions'
sellionsLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'sellions')
sellionsLineNode.AddControlPoint(sellion1_pos)
sellionsLineNode.AddControlPoint(sellion2_pos)
sellionsLineNode.GetDisplayNode().SetSelectedColor(0, 0, 1)  # Blue color

# Calculate the midpoint of 'sellions'
midpoint = (np.array(sellion1_pos) + np.array(sellion2_pos)) / 2

# Add the midpoint to 'hard_tissue_Macho'
hardTissueNode.AddControlPoint(midpoint.tolist(), 'midsellion')

# Retrieve the newly added 'midsellion' and the first point
point0 = [0.0, 0.0, 0.0]
hardTissueNode.GetNthControlPointPosition(0, point0)

midsellion = [0.0, 0.0, 0.0]
hardTissueNode.GetNthControlPointPosition(hardTissueNode.GetNumberOfControlPoints() - 1, midsellion)

# Create and configure the SN line
snLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'SN line')
snLineNode.AddControlPoint(midsellion)
snLineNode.AddControlPoint(point0)
snLineNode.GetDisplayNode().SetSelectedColor(1, 0.5, 0)  # Orange color

# Extend the SN line by 150 mm in both directions
direction = np.array(point0) - np.array(midsellion)
direction /= np.linalg.norm(direction)  # Normalize
extendedPoint1 = np.array(midsellion) + direction * 150
extendedPoint2 = np.array(midsellion) - direction * 150

snLineNode.SetNthControlPointPosition(0, extendedPoint1.tolist())
snLineNode.SetNthControlPointPosition(1, extendedPoint2.tolist())

# Create and configure the SN plane
snPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'SN')

# Set the plane's origin to the midpoint (ensures it meets the line)
planeOrigin = midpoint.tolist()
snPlaneNode.SetOriginWorld(planeOrigin)

# Set the plane's normal vector perpendicular to the SN line direction
# For simplicity, choose an orthogonal vector by swapping and negating components
planeNormal = np.cross(direction, [1, 0, 0])  # Find a vector orthogonal to the SN line
if np.linalg.norm(planeNormal) == 0:  # Handle edge case where direction aligns with [1, 0, 0]
    planeNormal = np.cross(direction, [0, 1, 0])
planeNormal /= np.linalg.norm(planeNormal)  # Normalize the vector

snPlaneNode.SetNormalWorld(planeNormal.tolist())

# Set the color of the plane to orange
displayNode = snPlaneNode.GetDisplayNode()
if displayNode:
    displayNode.SetColor(1.0, 0.5, 0.0)  # RGB values for orange

print("SN line and SN plane created successfully, with the plane meeting the line and parallel to it.")

###height of apertura piriformis###
F=getNode('hard_tissue_Macho')  
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(4)     
#rhinion#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(5)
#acanthion#
L.AddControlPoint(secondPoint)
L.SetName('height of apertura piriformis rhi-aca')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(64/252,224/255,208/255)
##turqoise colour###


#####length of apertura piriformis projected onto INB plane#####
import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('height of apertura piriformis rhi-aca')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', '2 INB proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to green
projectedLineNode.GetDisplayNode().SetSelectedColor(1.0, 0.0, 1.0)  # RGB values for yellow

F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(0)     
#nasion#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(5)
#acanthion#
L.AddControlPoint(secondPoint)
L.SetName('height of the bony nose nas-aca')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(230/255, 230/255, 250/255)

import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('height of the bony nose nas-aca')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', '3 INB proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to green
projectedLineNode.GetDisplayNode().SetSelectedColor(1.0, 0.0, 1.0)  # RGB values for magenta


# Get the 'hard_tissue_Macho' and 'SN line' nodes
hard_tissue_node = getNode('hard_tissue_Macho')
SN_line = getNode('SN line')

# Retrieve the coordinates of 'P' at position 6
P_para_position = hard_tissue_node.GetNthControlPointPositionVector(6)

# Determine the direction vector of 'SN line'
start_point_SN = SN_line.GetNthControlPointPositionVector(0)
end_point_SN = SN_line.GetNthControlPointPositionVector(1)
direction_vector = [end_point_SN[i] - start_point_SN[i] for i in range(3)]

# Normalize the direction vector
magnitude = sum([coord**2 for coord in direction_vector])**0.5
direction_vector = [coord / magnitude for coord in direction_vector]

# Calculate the new line's start and end points (100 mm in each direction)
half_length = 100  # half of 200 mm
start_point_new_line = [P_para_position[i] - half_length * direction_vector[i] for i in range(3)]
end_point_new_line = [P_para_position[i] + half_length * direction_vector[i] for i in range(3)]

# Create and configure the new line node
new_line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
new_line.AddControlPoint(start_point_new_line)
new_line.AddControlPoint(end_point_new_line)
new_line.SetName('P parallel')

# Set the line color to orange
line_display = new_line.GetDisplayNode()
line_display.SetColor(1.0, 0.647, 0.0)


import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('P parallel')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'P parallel proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to green
projectedLineNode.GetDisplayNode().SetSelectedColor(1, 1, 0)  # RGB values for yellow


# Get the 'hard_tissue_Macho' and 'SN line' nodes
hard_tissue_node = getNode('hard_tissue_Macho')
SN_line = getNode('SN line')

# Retrieve the coordinates of 'rhi' at position 4
rhi_para_position = hard_tissue_node.GetNthControlPointPositionVector(4)

# Determine the direction vector of 'SN line'
start_point_SN = SN_line.GetNthControlPointPositionVector(0)
end_point_SN = SN_line.GetNthControlPointPositionVector(1)
direction_vector = [end_point_SN[i] - start_point_SN[i] for i in range(3)]

# Normalize the direction vector
magnitude = sum([coord**2 for coord in direction_vector])**0.5
direction_vector = [coord / magnitude for coord in direction_vector]

# Calculate the new line's start and end points (100 mm in each direction)
half_length = 100  # half of 200 mm
start_point_new_line = [rhi_para_position[i] - half_length * direction_vector[i] for i in range(3)]
end_point_new_line = [rhi_para_position[i] + half_length * direction_vector[i] for i in range(3)]

# Create and configure the new line node
new_line = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
new_line.AddControlPoint(start_point_new_line)
new_line.AddControlPoint(end_point_new_line)
new_line.SetName('rhi parallel')

# Set the line color to orange
line_display = new_line.GetDisplayNode()
line_display.SetColor(1.0, 0.6, 0.4)

import numpy as np
import slicer

# Get the original line node
originalLineNode = slicer.util.getNode('rhi parallel')

# Get the plane node
planeNode = slicer.util.getNode('INB')
planeOrigin = np.array(planeNode.GetOrigin())
planeNormal = np.array(planeNode.GetNormal())

# Get the start and end points of the original line
startPoint = np.array(originalLineNode.GetNthControlPointPosition(0))
endPoint = np.array(originalLineNode.GetNthControlPointPosition(1))

# Function to project a point onto the plane
def project_point_onto_plane(point, planeOrigin, planeNormal):
    pointToPlaneVector = point - planeOrigin
    distanceToPlane = np.dot(pointToPlaneVector, planeNormal)
    projectedPoint = point - distanceToPlane * planeNormal
    return projectedPoint

# Project the start and end points onto the plane
projectedStartPoint = project_point_onto_plane(startPoint, planeOrigin, planeNormal)
projectedEndPoint = project_point_onto_plane(endPoint, planeOrigin, planeNormal)

# Create a new line node for the projected line
projectedLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'rhi parallel proj')
projectedLineNode.AddControlPoint(projectedStartPoint)
projectedLineNode.AddControlPoint(projectedEndPoint)
# Set the color of the new line to green
projectedLineNode.GetDisplayNode().SetSelectedColor(1, 1, 0)  # RGB values for yellow

import numpy as np

# Get the '3 INB proj' and 'rhi parallel proj' nodes
INB_proj_line = getNode('3 INB proj')
rhi_parallel_proj_line = getNode('rhi parallel proj')

# Retrieve control points of the lines
start_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(0))
end_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(1))

start_rhi_parallel_proj = np.array(rhi_parallel_proj_line.GetNthControlPointPositionVector(0))
end_rhi_parallel_proj = np.array(rhi_parallel_proj_line.GetNthControlPointPositionVector(1))

# Define the lines as vectors
vec_INB_proj_line = end_INB_proj_line - start_INB_proj_line
vec_rhi_parallel_proj = end_rhi_parallel_proj - start_rhi_parallel_proj

# Find the intersection point (if exists)
def find_line_intersection(p1, v1, p2, v2):
    w0 = p1 - p2
    a = np.dot(v1, v1)
    b = np.dot(v1, v2)
    c = np.dot(v2, v2)
    d = np.dot(v1, w0)
    e = np.dot(v2, w0)
    
    denom = a*c - b*b
    if denom == 0:
        raise ValueError("Lines are parallel and do not intersect.")
    
    s = (b*e - c*d) / denom
    t = (a*e - b*d) / denom
    
    intersection_point1 = p1 + s*v1
    intersection_point2 = p2 + t*v2
    
    if np.allclose(intersection_point1, intersection_point2):
        return intersection_point1
    else:
        raise ValueError("Lines do not intersect.")

try:
    intersection_point = find_line_intersection(start_INB_proj_line, vec_INB_proj_line, start_rhi_parallel_proj, vec_rhi_parallel_proj)
    
    # Save the intersection point as a new node in 'hard_tissue_Macho'
    hard_tissue = getNode('hard_tissue_Macho')
    new_control_point_index = hard_tissue.AddControlPoint(intersection_point)
    hard_tissue.SetNthControlPointLabel(new_control_point_index, '3INB proj - rhi parallel intersection')
    
    print("Intersection point successfully added to 'hard_tissue_Macho' node.")
except ValueError as e:
    print(str(e))


import numpy as np

# Get the '3 INB proj' and 'P parallel proj' nodes
INB_proj_line = getNode('3 INB proj')
P_parallel_proj_line = getNode('P parallel proj')

# Retrieve control points of the lines
start_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(0))
end_INB_proj_line = np.array(INB_proj_line.GetNthControlPointPositionVector(1))

start_P_parallel_proj = np.array(P_parallel_proj_line.GetNthControlPointPositionVector(0))
end_P_parallel_proj = np.array(P_parallel_proj_line.GetNthControlPointPositionVector(1))

# Define the lines as vectors
vec_INB_proj_line = end_INB_proj_line - start_INB_proj_line
vec_P_parallel_proj = end_P_parallel_proj - start_P_parallel_proj

# Find the intersection point (if exists)
def find_line_intersection(p1, v1, p2, v2):
    w0 = p1 - p2
    a = np.dot(v1, v1)
    b = np.dot(v1, v2)
    c = np.dot(v2, v2)
    d = np.dot(v1, w0)
    e = np.dot(v2, w0)
    
    denom = a*c - b*b
    if denom == 0:
        raise ValueError("Lines are parallel and do not intersect.")
    
    s = (b*e - c*d) / denom
    t = (a*e - b*d) / denom
    
    intersection_point1 = p1 + s*v1
    intersection_point2 = p2 + t*v2
    
    if np.allclose(intersection_point1, intersection_point2):
        return intersection_point1
    else:
        raise ValueError("Lines do not intersect.")

try:
    intersection_point = find_line_intersection(start_INB_proj_line, vec_INB_proj_line, start_P_parallel_proj, vec_P_parallel_proj)
    
    # Save the intersection point as a new node in 'hard_tissue_Macho'
    hard_tissue = getNode('hard_tissue_Macho')
    new_control_point_index = hard_tissue.AddControlPoint(intersection_point)
    hard_tissue.SetNthControlPointLabel(new_control_point_index, '3INB proj - P parallel intersection')
    
    print("Intersection point successfully added to 'hard_tissue_Macho' node.")
except ValueError as e:
    print(str(e))

#####3INB proj - P parallel intersection lines#####
F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(9)     
#number is the number on list of saved points#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(0)
L.AddControlPoint(secondPoint)
L.SetName('5 P max proj')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)

#####3INB proj - rhi parallel intersection lines#####
F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(8)     
#number is the number on list of saved points#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(0)
L.AddControlPoint(secondPoint)
L.SetName('7 height of rhinion')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)

F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(8)     
#number is the number on list of saved points#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(4)
L.AddControlPoint(secondPoint)
L.SetName('6 prominence of rhinion in relation to the n-aca plane')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)

F=getNode('hard_tissue_Macho')  
#opens up the collection of point you stored in the markup file#
L=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')
firstPoint = F.GetNthControlPointPositionVector(9)     
#number is the number on list of saved points#
L.AddControlPoint(firstPoint)
secondPoint = F.GetNthControlPointPositionVector(6)
L.AddControlPoint(secondPoint)
L.SetName('4 P max')     
#name of your measurements#
line_display = L.GetDisplayNode()
line_display.SetSelectedColor(1.0, 0.0, 1.0)

import slicer
import numpy as np

# Get the nodes for the existing points and lines
hardTissueNode = slicer.util.getNode('hard_tissue_Macho')

# Get the positions of the control points
apexPoint = np.array(hardTissueNode.GetNthControlPointPosition(5))
firstControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(0))
thirdControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(4))

# Create the angle node
angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', '9 angle between plane n-aca and rhi-aca plane')
angleNode.AddControlPoint(firstControlPoint)  # First control point
angleNode.AddControlPoint(apexPoint)          # Second control point (apex)
angleNode.AddControlPoint(thirdControlPoint)  # Third control point

print("New angle '9 angle between plane n-aca and rhi-aca plane' created successfully.")
```
![image](https://github.com/user-attachments/assets/753a4193-dd17-4f5c-bb11-0ebf96b1438b)

</details>

## Copying measurements 
To copy the measurements, use the method described in [this guide](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/004_Copying%20measurements%20to%20Clipboard.md). Please note that you will have to run the second code for copying the angle measurement successfully. 

### Output 
The output will look like this (provided you copy the linear measurements first): 
| ID        | Measurement                                               | Unit        | Note                                                                                                         |
|-----------|------------------------------------------------------------|-------------|--------------------------------------------------------------------------------------------------------------|
| (unknown) | ACP Axis                                                   | 200         | PSEUDO-MEASUREMENT - elongated line formed by the intersection of mid-ACP plane & vertical mid-ACP plane      |
| (unknown) | APT Axis                                                   | 200         | PSEUDO-MEASUREMENT - elongated line formed by the intersection of mid-APT plane & vertical mid-APT plane      |
| (unknown) | sellions                                                   | 0.266520709 | Not needed - line connecting the two sellions (for the midsellion point)                                      |
| (unknown) | SN line                                                    | 300         | PSEUDO-MEASUREMENT - elongated line formed by the nasion and the midsellion points                            |
| (unknown) | height of apertura piriformis rhi-aca                      | 37.17531772 |                                                                                                              |
| (unknown) | 2 INB proj                                                 | 37.16266246 | DUPLICATE same length as the line before (height of apertura piriformis), but projected onto the INB plane    |
| (unknown) | height of the bony nose nas-aca                            | 51.69010002 |                                                                                                              |
| (unknown) | 3 INB proj                                                 | 51.6829953  | DUPLICATE same length as the line before (height of the bony nose nas-aca), but projected onto the INB plane  |
| (unknown) | P parallel                                                 | 200         | PSEUDO-MEASUREMENT line bisecting the P point, parallel to SN line                                            |
| (unknown) | P parallel proj                                            | 199.9928997 | PSEUDO-MEASUREMENT and duplicate of previous line (P parallel), but projected to INB plane                    |
| (unknown) | rhi parallel                                               | 200         | PSEUDO-MEASUREMENT line bisecting the rhinion, parallel to SN line                                            |
| (unknown) | rhi parallel proj                                          | 199.9928997 | PSEUDO-MEASUREMENT and duplicate of previous line (rhi parallel), but projected to INB plane                  |
| (unknown) | 5 P max proj                                               | 14.45814586 |                                                                                                              |
| (unknown) | 7 height of rhinion                                        | 16.99366441 |                                                                                                              |
| (unknown) | 6 prominence of rhinion in relation to the n-aca plane     | 9.256110652 |                                                                                                              |
| (unknown) | 4 P max                                                    | 7.695531067 |                                                                                                              |
| (unknown) | 9 angle between plane n-aca and rhi-aca plane              | 14.27636551 |                                                                                                              |

> [!IMPORTANT]
> Only these are true measurements: 
- height of apertura   piriformis rhi-aca
- height of the bony nose nas-aca
- 5 P max proj
- 7 height of rhinion
- 6 prominence of rhinion in relation to the n-aca plane
- 4 P max
- 9 angle between plane n-aca and rhi-aca plane


DO NOT use the other measurements as such in your data analysis!!!!

### Future directions

These hard tissue only measurements can be a basis of comparing other hard tissue-only measurements of the nose to see if there are significant overlaps with other techniques. In addition, the Macho measurements could be investigated for correlations with soft tissue measurements of the nasal profile in other studies. 


## Bibliography: 

[^1]:  [Slicer Script Repository](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html)
[^2]:  Macho G.A. (1986) An appraisal of the plastic reconstruction of the external nose. J. Forensic Sci. 31 (4), 1391–403.
[^3]:  Goldhamer, K. Röntgenologische Studien über das menschliche Profil. I. Äußere Nase. Z. Anat. Entwickl. Gesch. 81, 115–150 (1926). https://doi.org/10.1007/BF02282306
[^4]:  Rynn, C., et al. (2012). Relationships between the skull and face. Craniofacial identification. C. W. C. Rynn. Cambridge, Cambridge University Press: 193-202.
[^5]:  Pittayapat P, Jacobs R, Odri GA, Vasconcelos KD, Willems G, Olszewski R. Reproducibility of the sella turcica landmark in three dimensions using a sella turcica-specific reference system. Imaging Sci Dent. 2015 Mar;45(1):15-22. https://doi.org/10.5624/isd.2015.45.1.15
[^6]:  Pittayapat P, Limchaichana-Bolstad N, Willems G, Jacobs R. Three-dimensional cephalometric analysis in orthodontics: a systematic review. Orthod Craniofac Res 2014;17:69–91.
[^7]:  Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." Int J Legal Med 130(3): 863-879.
[^8]:  Rynn, C., Wilkinson, C.M. & Peters, H.L. Prediction of nasal morphology from the skull. Forensic Sci Med Pathol 6, 20–34 (2010). https://doi.org/10.1007/s12024-009-9124-6
[^9]: Tinotenda Chiyangwa. [LinkedIn](https://www.linkedin.com/in/tinotenda-chiyangwa-9263121a3/), [Instagram](https://www.instagram.com/tino_tenda_arty/?igsh=YnNoMjM2ODRoNG1q#), [Portfolio](https://tinotendachiyangwa.wixsite.com/tino)
