# Prokopec and Ubelaker, 2002[^2] - The Aesthetic Method

The following guide is constructed by the available original study by [Prokopec and Ubelaker, 2002](https://archives.fbi.gov/archives/about-us/lab/forensic-science-communications/fsc/jan2002/prokopec.htm) and its interpretation by Rynn et al, (2010)[^3].
The original method seems to be done in 2 dimensions on the bony and soft tissue profiles, but Rynn et al. (2010)[^3] also applied it in 3D. This approach is also applied in three dimensions with adjustments to accommodate to such, for example using planes instead of lines and supplementary lines for precision. 

## Table of Contents
*   [Landmarks in this guide](#landmarks-in-this-guide)
*   [Illustration of the method](#illustration-of-the-method)
*   [Profile plane](#profile-plane)
    *   [INB Plane](#inb-plane)
    *   [MSP Plane](#msp-plane)
*   [NP plane](#np-plane)
*   [PT plane](#pt-plane)
*   [Maximum aperture width](#maximum-aperture-width)
*   [Choose a number of Planes](#choose-a-number-of-planes)
*   [Reference lines along the INB and 4/5/6 mirror planes](#reference-lines-along-the-inb-and-456-mirror-planes)
*   [Reference lines A and B](#reference-lines-a-and-b)
*   [Intersection points between Line B and the intersection lines](#intersection-points-between-line-b-and-the-intersection-lines)
*   [Line B Intersection Points](#line-b-intersection-points)
*   [Optional: Line A Intersections](#optional-line-a-intersections)
*   [Nasal bone outline landmarks](#nasal-bone-outline-landmarks)
*   [Soft tissue nose outline landmarks](#soft-tissue-nose-outline-landmarks)
*   [Optional: Adjusting soft tissue landmarks to profile plane](#optional-adjusting-soft-tissue-landmarks-to-profile-plane)
*   [Measurement lines](#measurement-lines)
*   [Nasal bone outline connecting lines & their intersections with Line B](#nasal-bone-outline-connecting-lines--their-intersections-with-line-b)
*   [Distances between Line A and nose profile & Line A and nasal aperture](#distances-between-line-a-and-nose-profile--line-a-and-nasal-aperture)
*   [Output](#output)
*   [Extra codes for more ideas](#extra-codes-for-more-ideas)
*   [Bibliography](#bibliography)

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide does not have all the features (inion, bregma) that are to be landmarked. Please refer to the illustrations in the guide for correct placement. In addition, due to the CT being taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.



## Landmarks in this guide: 
| Position in code | Position in file | Name in file | Landmark name | Definition                                                                                                                     | Defined by            |
|------------------|------------------|--------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 0                | 1                | nasion       | nasion        | Intersection of the nasofrontal sutures in the median plane                                                                    | Rynn et al. 2010[^3]      |
| 1                | 2                | inion        | inion         | Median point between the apices of the superior nuchal lines and at the base of the external occipital protuberance (not the tip of the protuberance) | Rynn et al. 2010[^3]      |
| 2                | 3                | bregma       | bregma        | Where the sagittal and coronal sutures meet. Impossible to determine in juvenile skulls with anterior fontanelle, or with complete suture obliteration | Rynn et al. 2010[^3]      |
| 3                | 4                | prosthion     | prosthion       | Median point between the central incisors on the anterior most margin of the maxillary alveolar rim | Rynn et al. 2010[^3]      |
| 4                | 5                | subspinale      | subspinale       | The deepest point seen in the profile view below the anterior nasal spine (orthodontic point A) | Caple and Stephan 2016 [^6]     |
| 5                | 6                | rhinion   | rhinion   | Most rostral (end) point on the internasal suture.          |  Rynn et al. 2010[^3] |
| 6                | 7                | acanthion    | acanthion     | Most anterior tip of the anterior nasal spine                                                                                 | Rynn et al. 2010[^3]     |





Illustration of the method: 

> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan has to be re-aligned in the FHP
- [ ] You should have a Bone and Skin model via segmentation (explained later)
- [ ] Allocate ALL landmarks from the [hard_tissue_PU.mrk.json](https://github.com/user-attachments/files/22872691/hard_tissue_PU.mrk.json)




### Profile plane

Based on landmark availability, the module will offer two options to establish a "middle" profile plane: 

a) INB used by Rynn et al. 2010[^3]


b) MSP (midsagittal plane) based on landmark definitions - any landmark already used by the cited literature that is defined as midline - here, it is nasion, prosthion, subspinale, rhinion and acanthion.


#### INB Plane

To help with the side profile, we will establish the “INB” plane as defined by Rynn et al. 2010[^3]. 

> a midsagittal plane (INB) which bisected the inion, nasion and bregma

by downloading markups file for this method, allocating the landmarks  and copying and pasting the following code: 

```python
#INB plane#

import numpy as np
import slicer

# Get the points from the "hard_tissue_PU" node
hardTissueNode = slicer.util.getNode('hard_tissue_PU')
point1 = np.array(hardTissueNode.GetNthControlPointPosition(0))
point2 = np.array(hardTissueNode.GetNthControlPointPosition(1))
point3 = np.array(hardTissueNode.GetNthControlPointPosition(2))

# Calculate the centroid of the three points (the average position)
centroid = (point1 + point2 + point3) / 3.0

# Calculate the normal of the plane defined by the three points
# This part doesn't need to change
v1 = point2 - point1
v2 = point3 - point1
planeNormal = np.cross(v1, v2)
planeNormal = planeNormal / np.linalg.norm(planeNormal)

# Create a new plane node
newPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'INB')

# Set the origin of the new plane to the calculated centroid
newPlaneNode.SetOrigin(centroid)

# Set the normal of the new plane
newPlaneNode.SetNormal(planeNormal)


```
<img src="https://github.com/user-attachments/assets/e651bf90-5d0b-4502-b26a-a53b19de2b9b" width="500">


View of the generated INB 
<img src="https://github.com/user-attachments/assets/5c525822-9a71-4c2b-9b22-18bbd3ef6936" width="500">


INB extended via the toggles (dots)

#### MSP Plane
```python
import numpy as np
import slicer

# --- Configuration ---

# 1. List of point labels that define the Midsagittal Plane (MSP).
#    The script will search for these labels in the source node.
msp_point_labels = ['nasion', 'prosthion', 'subspinale', 'rhinion', 'acanthion']

# 2. The name of the node containing your landmark points.
source_node_name = 'hard_tissue_PU'

# 3. The name for the new plane that will be created.
new_plane_name = 'MSP'


# --- Main Script ---

# Get the source markup fiducials node from the Slicer scene
try:
    sourceNode = slicer.util.getNode(source_node_name)
    if not sourceNode:
        raise ValueError(f"Node '{source_node_name}' not found.")
except ValueError as e:
    slicer.util.errorDisplay(f"Error: {e}")
    # Stop the script if the node doesn't exist
    raise

# Find the coordinates of the points with the specified labels
points = []
found_labels = []
missing_labels = list(msp_point_labels)

for i in range(sourceNode.GetNumberOfControlPoints()):
    label = sourceNode.GetNthControlPointLabel(i)
    if label in msp_point_labels:
        pos = sourceNode.GetNthControlPointPosition(i)
        points.append(list(pos))
        found_labels.append(label)
        if label in missing_labels:
            missing_labels.remove(label)

# Check if we found enough points
if len(points) < 3:
    slicer.util.errorDisplay(
        f"Could not find at least 3 of the specified points in '{source_node_name}'.\n"
        f"Found: {found_labels}\n"
        f"Missing: {missing_labels}\n"
        "Cannot calculate a plane."
    )
    raise ValueError("Not enough points to define a plane.")

# If some points were missing, show a warning but continue
if missing_labels:
    slicer.util.warningDisplay(
        f"Warning: Could not find all specified points.\n"
        f"The plane will be calculated using the points that were found: {found_labels}\n"
        f"Missing points: {missing_labels}"
    )

# Convert the list of points to a NumPy array for calculation
points = np.array(points)

# --- Best-Fit Plane Calculation ---

# 1. Calculate the centroid of the points (this will be the plane's origin)
centroid = points.mean(axis=0)

# 2. Center the points by subtracting the centroid
centered_points = points - centroid

# 3. Use Singular Value Decomposition (SVD) to find the best-fit plane.
#    The normal of the plane is the eigenvector corresponding to the smallest singular value.
#    In numpy's SVD, this is the last row of the 'vh' matrix.
_, _, vh = np.linalg.svd(centered_points)
plane_normal = vh[-1]

# --- Create the New Plane in Slicer ---

# Remove the old plane if it exists, to allow running the script again
# This uses a safer method that doesn't cause an error if the node doesn't exist.
oldPlaneNode = slicer.mrmlScene.GetFirstNodeByName(new_plane_name)
if oldPlaneNode:
    slicer.mrmlScene.RemoveNode(oldPlaneNode)

# Create a new plane node
newPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', new_plane_name)

# Set the origin and normal for the new plane
newPlaneNode.SetOrigin(centroid)
newPlaneNode.SetNormal(plane_normal)

# NOTE: The lines for setting the plane size have been removed for compatibility.
# You can manually adjust the plane size in the 'Markups' module if needed.

print(f"Successfully created Midsagittal Plane '{new_plane_name}'.")
print(f"  - Calculated from {len(points)} points: {found_labels}")
print(f"  - Origin (Centroid): {np.round(centroid, 2)}")
print(f"  - Normal Vector: {np.round(plane_normal, 2)}")

```

</details>


### NP plane
May be referred to as NPP - nasion-prosthion plane; defined by Rynn as 

> a coronal plane which bisects the nasion and prosthion in lateral view, whilst lying at right angles to INB

To create this plane, use this code: 

<summary> NPP </summary>
<details>
	
```python

import numpy as np
import slicer

# --- Configuration ---

# 1. Reference Plane: The script will look for 'MSP' first, then 'INB'.
reference_plane_priority = ['MSP', 'INB']

# 2. NPP Direction Points: A list of point labels that define the "direction"
#    of the NPP. The script will calculate a "best-fit" line through these points.
#    Using more than two points makes the result more stable.
npp_direction_points = ['nasion', 'prosthion', 'subspinale']

# 3. Origin Point: The label of the point to use as the plane's origin.
#    'Prosthion' is a common choice.
origin_point_label = 'prosthion'

# 4. Node Names
source_points_node_name = 'hard_tissue_PU'
new_plane_name = 'NPP_bestfit'


# --- Main Script ---

# 1. Housekeeping: Remove the old plane if it exists
old_npp_node = slicer.mrmlScene.GetFirstNodeByName(new_plane_name)
if old_npp_node:
    slicer.mrmlScene.RemoveNode(old_npp_node)

# 2. Find the Reference Plane (MSP or INB)
reference_plane_node = None
for name in reference_plane_priority:
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node:
        reference_plane_node = node
        print(f"Using '{name}' as the reference plane.")
        break
if not reference_plane_node:
    slicer.util.errorDisplay("Error: Could not find 'MSP' or 'INB'. A reference plane is required.")
    raise ValueError("Reference plane not found.")

# 3. Find the landmark points node
try:
    hard_tissue_node = slicer.util.getNode(source_points_node_name)
except slicer.util.MRMLNodeNotFoundException:
    slicer.util.errorDisplay(f"Error: The points list '{source_points_node_name}' was not found.")
    raise ValueError("Points node not found.")

# 4. Get coordinates for all required points by searching for labels
all_required_labels = list(set(npp_direction_points + [origin_point_label]))
points_coords = {}
for i in range(hard_tissue_node.GetNumberOfControlPoints()):
    label = hard_tissue_node.GetNthControlPointLabel(i)
    if label in all_required_labels:
        pos = np.zeros(3)
        hard_tissue_node.GetNthControlPointPosition(i, pos)
        points_coords[label] = pos

# Check if all required points were found
missing_labels = [label for label in all_required_labels if label not in points_coords]
if missing_labels:
    slicer.util.errorDisplay(f"Error: Could not find required points: {missing_labels}")
    raise ValueError("Missing required points.")

# 5. --- Best-Fit Direction Calculation (The New Logic) ---
# Assemble the array of points that define the direction
direction_points_array = np.array([points_coords[label] for label in npp_direction_points])

# To find the best-fit line, we use PCA (via SVD).
# The direction of the line is the first principal component, which is the
# first eigenvector of the covariance matrix of the centered points.
# In numpy's SVD, this corresponds to the first row of the 'vh' matrix.
centroid = direction_points_array.mean(axis=0)
centered_points = direction_points_array - centroid
_, _, vh = np.linalg.svd(centered_points)
best_fit_direction_vector = vh[0] # The first row is the principal direction

print(f"Calculated best-fit direction from points: {npp_direction_points}")

# 6. Perform the geometric calculations using the new best-fit vector
ref_normal = np.zeros(3)
reference_plane_node.GetNormal(ref_normal)

# The new plane's normal is perpendicular to both the reference plane's normal
# and the "best-fit direction vector" we just calculated.
new_plane_normal = np.cross(ref_normal, best_fit_direction_vector)
new_plane_normal /= np.linalg.norm(new_plane_normal)

# 7. Create the new 'NPP' plane
new_plane_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', new_plane_name)

# Set the origin and normal of the new plane
origin_pos = points_coords[origin_point_label]
new_plane_node.SetOrigin(origin_pos)
new_plane_node.SetNormal(new_plane_normal)

print(f"\nSuccessfully created '{new_plane_name}'.")
print(f"  - Origin set to '{origin_point_label}' at {np.round(origin_pos, 2)}")
print(f"  - Orientation based on best-fit line through {len(npp_direction_points)} points.")
```

</details>


<img src="https://github.com/user-attachments/assets/a567ed66-7091-4934-87d4-c8b5146509fe" width="500">

Immediate view after the code implemented

You can change the colour of the planes for more contrast (and is good practice when using more planes) by double-clicking on the colour square of the plane in the Markups module and choosing a different one. 
<img src="https://github.com/user-attachments/assets/105f9621-7e04-4dd0-9e9a-74ac920ee7cb" width="500">


This screenshot shows the two different planes (NPP with yellow, INB with purple) after extending the INB
<img src="https://github.com/user-attachments/assets/529fdf50-7a4e-4804-9ac5-501cacae1c9c" width="500">



### PT plane
May be referred to as PTP - Prokopec Transverse plane; defined by Rynn as 

> a transverse plane set at right angles to both the INB plane and the NPP, corresponding with the profile prediction lines used by Prokopec and Ubelaker

To create this plane, use this code: 

```python

import numpy as np
import slicer

# --- Configuration ---

# 1. Reference Planes Priority:
#    The script will search for these planes in order to define the PTP.
#    It needs one sagittal plane and one NPP plane.
sagittal_plane_priority = ['MSP', 'INB']
npp_plane_priority = ['NPP_bestfit', 'NPP'] # Looks for the 'bestfit' version first

# 2. Origin Source:
#    Which plane's origin should be used for the new PTP plane?
#    Commonly the sagittal plane's origin is used.
origin_source_priority = ['MSP', 'INB']

# 3. New Plane Name
new_plane_name = 'PTP'


# --- Main Script ---

# 1. Housekeeping: Remove the old PTP plane if it exists
old_ptp_node = slicer.mrmlScene.GetFirstNodeByName(new_plane_name)
if old_ptp_node:
    slicer.mrmlScene.RemoveNode(old_ptp_node)

# 2. Find the required input planes
def find_node_from_priority_list(priority_list):
    """Searches for a node from a list of names and returns the first one found."""
    for name in priority_list:
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node:
            print(f"Found required plane: '{name}'")
            return node, name
    return None, None

sagittal_plane_node, sagittal_name = find_node_from_priority_list(sagittal_plane_priority)
npp_plane_node, npp_name = find_node_from_priority_list(npp_plane_priority)
origin_source_node, origin_source_name = find_node_from_priority_list(origin_source_priority)

# Check if all required planes were found
if not all([sagittal_plane_node, npp_plane_node, origin_source_node]):
    error_msg = "Error: Could not find all required input planes in the scene. Please ensure planes exist with names from the priority lists."
    slicer.util.errorDisplay(error_msg)
    raise ValueError(error_msg)

# 3. Perform the Geometric Calculation
# Get the normals of the two input planes
sagittal_normal = np.zeros(3)
sagittal_plane_node.GetNormal(sagittal_normal)

npp_normal = np.zeros(3)
npp_plane_node.GetNormal(npp_normal)

# The PTP normal is perpendicular to both input normals (the cross product)
ptp_normal = np.cross(sagittal_normal, npp_normal)
ptp_normal /= np.linalg.norm(ptp_normal) # Normalize to a unit vector

# Get the origin from the specified source plane
origin_pos = np.zeros(3)
origin_source_node.GetOrigin(origin_pos)


# 4. Create the new 'PTP' plane
ptp_plane_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', new_plane_name)

# Set the origin and normal for the new plane
ptp_plane_node.SetOrigin(origin_pos)
ptp_plane_node.SetNormal(ptp_normal)

print(f"\nSuccessfully created '{new_plane_name}' plane.")
print(f"  - Normal calculated from '{sagittal_name}' and '{npp_name}'.")
print(f"  - Origin copied from '{origin_source_name}' at {np.round(origin_pos, 2)}.")
```
<img src="https://github.com/user-attachments/assets/5da113b9-cd62-4fc9-b723-05df297708b9" width="500">

Expected view with all three planes established and extended. Landmarks hidden for representative purposes. 

### Maximum aperture width

Rynn et al. (2012) refined the original description from Prokopec and Ubelaker (2002) "4 to 6 equidistant planes" to be constrained to in-between the level of the maximum aperture width and rhinion.  

You will need to switch to the "Bone" model or use the toggle to reveal the hard tissue on the scan for this step. 

[Download maximum_aperture_width_MAW.mrk.json](https://github.com/user-attachments/files/21412671/maximum_aperture_width_MAW.mrk.json)


, and drag-and-drop it into the "Markups" environment (click OK on this pop-up - see screenshot below).

<img width="753" height="470" alt="Screenshot 2025-07-24 145513" src="https://github.com/user-attachments/assets/9e9a24e2-9ca7-4966-a632-9c8c795bf969" />


This item will appear on your markups list with "empty endpoints" - that's completely fine, find the 

![image](https://github.com/user-attachments/assets/06ce0f82-0574-4901-a0ab-9e1f0638ec58)

icon in the second line of menu to start placing the points.

<img src="https://github.com/user-attachments/assets/890795f6-a08d-4a33-abac-0c512a715b84" width="500">

The goal here is to have a linear measurement from the anterior view at the maximum width of the hard tissue nose. 


Now, your "Control Points">"Coordinates" menu should be populated by the two endpoints and a measurement in mm should also show up in the "Node" table. 

<img src="https://github.com/user-attachments/assets/cce4b529-2c48-484f-b977-914804899e7c" width="500">


## Choose a number of Planes

Depending on your choosing, run the codes for the 4/5/6 mirror planes - or all three for comparison. 

<details>
	
<summary>Code for 4 mirror planes</summary>

```python
#4 mirror planes#
import slicer
import numpy as np

#Get the PTP plane node
ptpPlaneNode = slicer.util.getNode('PTP')

#Get the MAW measurement position (assuming it's stored in a node)
#Replace 'MAW' with the actual node name or method to get the MAW position
mawNode = slicer.util.getNode('maximum_nasal_width_MAW')
mawPosition = np.array(mawNode.GetNthControlPointPositionWorld(0))  # Adjust index if needed

#Get the PTP plane position and normal
ptpPlanePosition = np.array(ptpPlaneNode.GetOrigin())
ptpPlaneNormal = np.array(ptpPlaneNode.GetNormal())

#Create the new plane "A" at the MAW level
planeA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'Plane_A')
planeA.SetOrigin(mawPosition)
planeA.SetNormal(ptpPlaneNormal)

#Get the hard_tissue_PU node position
hardTissueNode = slicer.util.getNode('hard_tissue_PU')
rhinionPosition = np.array(hardTissueNode.GetNthControlPointPositionWorld(5))

#Calculate the distance between Plane_A and the rhinion
distance = np.dot(mawPosition - rhinionPosition, ptpPlaneNormal)

#Calculate the positions for the new planes B, C, D
numPlanes = 3
planePositions = [rhinionPosition + (i + 1) * distance / (numPlanes + 1) * ptpPlaneNormal for i in range(numPlanes)]

#Create new planes with names B, C, D
planeNames = ['B', 'C', 'D']
for i, pos in enumerate(planePositions):
    planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', f'Plane_{planeNames[i]}')
    planeNode.SetOrigin(pos)
    planeNode.SetNormal(ptpPlaneNormal)
```
Image if the code for 4 mirror planes is employed:
![image](https://github.com/user-attachments/assets/c684f261-e427-4d4d-8831-17dc7d7e3bbe)

</details>


<details>

<summary>Code for 5 mirror planes</summary>

```python
#5 mirror planes#
import slicer
import numpy as np

# Get the PTP plane node
ptpPlaneNode = slicer.util.getNode('PTP')

# Get the MAW measurement position (assuming it's stored in a node)
# Replace 'MAW' with the actual node name or method to get the MAW position
mawNode = slicer.util.getNode('maximum_nasal_width_MAW')
mawPosition = np.array(mawNode.GetNthControlPointPositionWorld(0))  # Adjust index if needed

# Get the PTP plane position and normal
ptpPlanePosition = np.array(ptpPlaneNode.GetOrigin())
ptpPlaneNormal = np.array(ptpPlaneNode.GetNormal())

# Create the new plane "A" at the MAW level
planeA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'Plane_A')
planeA.SetOrigin(mawPosition)
planeA.SetNormal(ptpPlaneNormal)

# Get the hard_tissue_PU node position
hardTissueNode = slicer.util.getNode('hard_tissue_PU')
rhinionPosition = np.array(hardTissueNode.GetNthControlPointPositionWorld(5))

# Calculate the distance between Plane_A and the rhinion
distance = np.dot(mawPosition - rhinionPosition, ptpPlaneNormal)# Calculate the positions for the new planes B, C, D, E
numPlanes = 4  # Change this to 4 to create 5 planes in total (A, B, C, D, E)
planePositions = [rhinionPosition + (i + 1) * distance / (numPlanes + 1) * ptpPlaneNormal for i in range(numPlanes)]

# Create new planes with names B, C, D, E
planeNames = ['B', 'C', 'D', 'E']
for i, pos in enumerate(planePositions):
    planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', f'Plane_{planeNames[i]}')
    planeNode.SetOrigin(pos)
    planeNode.SetNormal(ptpPlaneNormal)
```
Image if the code for 5 mirror planes is employed: 

![image](https://github.com/user-attachments/assets/ea7b9888-95b6-436c-892d-ada9f77f2a6b)


</details>


<details>
	
<summary>Code for 6 mirror planes</summary>

```python

import slicer
import numpy as np

# Get the PTP plane node
ptpPlaneNode = slicer.util.getNode('PTP')

# Get the MAW measurement position (assuming it's stored in a node)
mawNode = slicer.util.getNode('maximum_nasal_width_MAW')
mawPosition = np.array(mawNode.GetNthControlPointPositionWorld(0))  # Adjust index if needed

# Get the PTP plane position and normal
ptpPlanePosition = np.array(ptpPlaneNode.GetOrigin())
ptpPlaneNormal = np.array(ptpPlaneNode.GetNormal())

# Create the new plane "A" at the MAW level
planeA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'Plane_A')
planeA.SetOrigin(mawPosition)
planeA.SetNormal(ptpPlaneNormal)

# Get the hard_tissue_PU node position
hardTissueNode = slicer.util.getNode('hard_tissue_PU')
rhinionPosition = np.array(hardTissueNode.GetNthControlPointPositionWorld(5))

# Calculate the distance between Plane_A and the rhinion
distance = np.dot(mawPosition - rhinionPosition, ptpPlaneNormal)

# Calculate the positions for the new planes B, C, D, E, F
numPlanes = 5  # Change this to 5 to create 6 planes in total (A, B, C, D, E, F)
planeNames = ['B', 'C', 'D', 'E', 'F']
planePositions = [rhinionPosition + (i + 1) * distance / (numPlanes + 1) * ptpPlaneNormal for i in range(numPlanes)]

# Create new planes with names B, C, D, E, F
for i, pos in enumerate(planePositions):
    planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', f'Plane_{planeNames[i]}')
    planeNode.SetOrigin(pos)
    planeNode.SetNormal(ptpPlaneNormal)
```

Image if the code for 6 mirror planes is employed:
![image](https://github.com/user-attachments/assets/8f635b63-27e2-4857-ae29-1d87db13f103)
</details>


### Reference lines along the INB and 4/5/6 mirror planes

This step establishes the 4/5/6 intersection lines where the individual mirror planes meet the INB plane. 

<details>
<summary>Code for 4 intersection lines</summary>

This script will automatically detect `MSP` or `INB` and intersect it with `Plane_A` through `Plane_D`.

```python
import numpy as np
import slicer

# --- Configuration ---
# The script will look for 'MSP' first, then 'INB'.
SAGITTAL_PLANE_PRIORITY = ['MSP', 'INB']
# The mirror planes to intersect with.
MIRROR_PLANES = ['Plane_A', 'Plane_B', 'Plane_C', 'Plane_D']

# --- Main Script ---

def create_intersection_line(planeNode1, planeNode2, lineNodeName):
    """Creates a vtkMRMLMarkupsLineNode at the intersection of two planes."""
    # Clean up old line node if it exists
    oldLineNode = slicer.mrmlScene.GetFirstNodeByName(lineNodeName)
    if oldLineNode:
        slicer.mrmlScene.RemoveNode(oldLineNode)

    # Get normals and points from the plane nodes
    normal1 = np.zeros(3)
    planeNode1.GetNormal(normal1)
    point1 = np.zeros(3)
    planeNode1.GetOrigin(point1)

    normal2 = np.zeros(3)
    planeNode2.GetNormal(normal2)
    point2 = np.zeros(3)
    planeNode2.GetOrigin(point2)

    # Calculate direction of the intersection line (cross product of normals)
    direction = np.cross(normal1, normal2)

    # Check if planes are parallel
    if np.linalg.norm(direction) < 1e-6:
        print(f"Planes {planeNode1.GetName()} and {planeNode2.GetName()} are parallel.")
        return

    # Normalize the direction vector
    direction /= np.linalg.norm(direction)

    # Calculate a point on the intersection line
    # (solving a system of linear equations)
    try:
        A = np.array([normal1, normal2, direction])
        b = np.array([np.dot(normal1, point1), np.dot(normal2, point2), 0])
        intersection_point = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        print(f"Could not solve for a point on the intersection line for {lineNodeName}. The calculation may be unstable.")
        return

    # Create and set points for the new line node
    intersectionLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', lineNodeName)
    
    # Extend the line for visualization purposes
    extension_factor = 1000
    start_point = intersection_point - extension_factor * direction
    end_point = intersection_point + extension_factor * direction
    
    intersectionLineNode.AddControlPoint(start_point)
    intersectionLineNode.AddControlPoint(end_point)
    print(f"Intersection line '{lineNodeName}' created successfully.")

# --- Execution ---

# 1. Find the sagittal plane (MSP or INB)
sagittal_plane_node = None
sagittal_plane_name = ""
for name in SAGITTAL_PLANE_PRIORITY:
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node:
        sagittal_plane_node = node
        sagittal_plane_name = name
        print(f"Found sagittal reference plane: '{sagittal_plane_name}'")
        break

if not sagittal_plane_node:
    slicer.util.errorDisplay(f"Error: Could not find a sagittal plane. Please ensure '{' or '.join(SAGITTAL_PLANE_PRIORITY)}' exists.")
    raise ValueError("Sagittal reference plane not found.")

# 2. Iterate over mirror planes and create intersection lines
for mirror_plane_name in MIRROR_PLANES:
    mirror_plane_node = slicer.mrmlScene.GetFirstNodeByName(mirror_plane_name)
    if not mirror_plane_node:
        print(f"Warning: Mirror plane '{mirror_plane_name}' not found. Skipping.")
        continue
    
    line_name = f"{sagittal_plane_name}_{mirror_plane_name.split('_')[-1]}"
    create_intersection_line(sagittal_plane_node, mirror_plane_node, line_name)

```
![image](https://github.com/user-attachments/assets/016c35b3-83e6-46ed-8151-ae9d48c79124)

</details>


<details>
<summary>Code for 5 intersection lines</summary>

This script will automatically detect `MSP` or `INB` and intersect it with `Plane_A` through `Plane_E`.

```python
import numpy as np
import slicer

# --- Configuration ---
# The script will look for 'MSP' first, then 'INB'.
SAGITTAL_PLANE_PRIORITY = ['MSP', 'INB']
# The mirror planes to intersect with.
MIRROR_PLANES = ['Plane_A', 'Plane_B', 'Plane_C', 'Plane_D', 'Plane_E']

# --- Main Script ---

def create_intersection_line(planeNode1, planeNode2, lineNodeName):
    """Creates a vtkMRMLMarkupsLineNode at the intersection of two planes."""
    # Clean up old line node if it exists
    oldLineNode = slicer.mrmlScene.GetFirstNodeByName(lineNodeName)
    if oldLineNode:
        slicer.mrmlScene.RemoveNode(oldLineNode)

    # Get normals and points from the plane nodes
    normal1 = np.zeros(3)
    planeNode1.GetNormal(normal1)
    point1 = np.zeros(3)
    planeNode1.GetOrigin(point1)

    normal2 = np.zeros(3)
    planeNode2.GetNormal(normal2)
    point2 = np.zeros(3)
    planeNode2.GetOrigin(point2)

    # Calculate direction of the intersection line (cross product of normals)
    direction = np.cross(normal1, normal2)

    # Check if planes are parallel
    if np.linalg.norm(direction) < 1e-6:
        print(f"Planes {planeNode1.GetName()} and {planeNode2.GetName()} are parallel.")
        return

    # Normalize the direction vector
    direction /= np.linalg.norm(direction)

    # Calculate a point on the intersection line
    # (solving a system of linear equations)
    try:
        A = np.array([normal1, normal2, direction])
        b = np.array([np.dot(normal1, point1), np.dot(normal2, point2), 0])
        intersection_point = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        print(f"Could not solve for a point on the intersection line for {lineNodeName}. The calculation may be unstable.")
        return

    # Create and set points for the new line node
    intersectionLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', lineNodeName)
    
    # Extend the line for visualization purposes
    extension_factor = 1000
    start_point = intersection_point - extension_factor * direction
    end_point = intersection_point + extension_factor * direction
    
    intersectionLineNode.AddControlPoint(start_point)
    intersectionLineNode.AddControlPoint(end_point)
    print(f"Intersection line '{lineNodeName}' created successfully.")

# --- Execution ---

# 1. Find the sagittal plane (MSP or INB)
sagittal_plane_node = None
sagittal_plane_name = ""
for name in SAGITTAL_PLANE_PRIORITY:
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node:
        sagittal_plane_node = node
        sagittal_plane_name = name
        print(f"Found sagittal reference plane: '{sagittal_plane_name}'")
        break

if not sagittal_plane_node:
    slicer.util.errorDisplay(f"Error: Could not find a sagittal plane. Please ensure '{' or '.join(SAGITTAL_PLANE_PRIORITY)}' exists.")
    raise ValueError("Sagittal reference plane not found.")

# 2. Iterate over mirror planes and create intersection lines
for mirror_plane_name in MIRROR_PLANES:
    mirror_plane_node = slicer.mrmlScene.GetFirstNodeByName(mirror_plane_name)
    if not mirror_plane_node:
        print(f"Warning: Mirror plane '{mirror_plane_name}' not found. Skipping.")
        continue
    
    line_name = f"{sagittal_plane_name}_{mirror_plane_name.split('_')[-1]}"
    create_intersection_line(sagittal_plane_node, mirror_plane_node, line_name)
```
Image after the 5 line code is iterated: 
![image](https://github.com/user-attachments/assets/3bc4b9d2-63a3-47ad-9dbe-43a81f2490c3)

</details>



<details>
<summary>Code for 6 intersection lines</summary>
This script will automatically detect `MSP` or `INB` and intersect it with `Plane_A` through `Plane_F`.

```python
import numpy as np
import slicer

# --- Configuration ---
# The script will look for 'MSP' first, then 'INB'.
SAGITTAL_PLANE_PRIORITY = ['MSP', 'INB']
# The mirror planes to intersect with.
MIRROR_PLANES = ['Plane_A', 'Plane_B', 'Plane_C', 'Plane_D', 'Plane_E', 'Plane_F']

# --- Main Script ---

def create_intersection_line(planeNode1, planeNode2, lineNodeName):
    """Creates a vtkMRMLMarkupsLineNode at the intersection of two planes."""
    # Clean up old line node if it exists
    oldLineNode = slicer.mrmlScene.GetFirstNodeByName(lineNodeName)
    if oldLineNode:
        slicer.mrmlScene.RemoveNode(oldLineNode)

    # Get normals and points from the plane nodes
    normal1 = np.zeros(3)
    planeNode1.GetNormal(normal1)
    point1 = np.zeros(3)
    planeNode1.GetOrigin(point1)

    normal2 = np.zeros(3)
    planeNode2.GetNormal(normal2)
    point2 = np.zeros(3)
    planeNode2.GetOrigin(point2)

    # Calculate direction of the intersection line (cross product of normals)
    direction = np.cross(normal1, normal2)

    # Check if planes are parallel
    if np.linalg.norm(direction) < 1e-6:
        print(f"Planes {planeNode1.GetName()} and {planeNode2.GetName()} are parallel.")
        return

    # Normalize the direction vector
    direction /= np.linalg.norm(direction)

    # Calculate a point on the intersection line
    # (solving a system of linear equations)
    try:
        A = np.array([normal1, normal2, direction])
        b = np.array([np.dot(normal1, point1), np.dot(normal2, point2), 0])
        intersection_point = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        print(f"Could not solve for a point on the intersection line for {lineNodeName}. The calculation may be unstable.")
        return

    # Create and set points for the new line node
    intersectionLineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', lineNodeName)
    
    # Extend the line for visualization purposes
    extension_factor = 1000
    start_point = intersection_point - extension_factor * direction
    end_point = intersection_point + extension_factor * direction
    
    intersectionLineNode.AddControlPoint(start_point)
    intersectionLineNode.AddControlPoint(end_point)
    print(f"Intersection line '{lineNodeName}' created successfully.")

# --- Execution ---

# 1. Find the sagittal plane (MSP or INB)
sagittal_plane_node = None
sagittal_plane_name = ""
for name in SAGITTAL_PLANE_PRIORITY:
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node:
        sagittal_plane_node = node
        sagittal_plane_name = name
        print(f"Found sagittal reference plane: '{sagittal_plane_name}'")
        break

if not sagittal_plane_node:
    slicer.util.errorDisplay(f"Error: Could not find a sagittal plane. Please ensure '{' or '.join(SAGITTAL_PLANE_PRIORITY)}' exists.")
    raise ValueError("Sagittal reference plane not found.")

# 2. Iterate over mirror planes and create intersection lines
for mirror_plane_name in MIRROR_PLANES:
    mirror_plane_node = slicer.mrmlScene.GetFirstNodeByName(mirror_plane_name)
    if not mirror_plane_node:
        print(f"Warning: Mirror plane '{mirror_plane_name}' not found. Skipping.")
        continue
    
    line_name = f"{sagittal_plane_name}_{mirror_plane_name.split('_')[-1]}"
    create_intersection_line(sagittal_plane_node, mirror_plane_node, line_name)
```
Image after the 6 line code is iterated: 
![image](https://github.com/user-attachments/assets/2feed628-718b-4a3c-a888-fa5e4abe988d)

</details>


### Reference lines A and B
After this, we establish the lines of reference which are perpendicular to the mirror planes– one along the nasion-prosthion and one parallel to the nasion-prosthion bisecting the rhinion by copy-pasting code “reference lines A and B”. We are using thie same code for ALL options (4/5/6 mirror planes)!

```python

###reference lines A and B###
import slicer
import vtk

# Get the "hard_tissue_PU" node
F = slicer.util.getNode('hard_tissue_PU')

# Create the first line node
L_A = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Line_A')

# Retrieve and add the first point (position 0)
firstPoint = F.GetNthControlPointPositionVector(0)
L_A.AddControlPoint(firstPoint)

# Retrieve and add the second point (position 3)
secondPoint = F.GetNthControlPointPositionVector(3)
L_A.AddControlPoint(secondPoint)

# Retrieve the point at position 5
thirdPoint = F.GetNthControlPointPositionVector(5)

# Calculate the direction vector of the first line
directionVector = vtk.vtkVector3d()
directionVector.SetX(secondPoint.GetX() - firstPoint.GetX())
directionVector.SetY(secondPoint.GetY() - firstPoint.GetY())
directionVector.SetZ(secondPoint.GetZ() - firstPoint.GetZ())

# Create the second line node
L_B = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Line_B')

# Add the third point (position 5)
L_B.AddControlPoint(thirdPoint)

# Extend the direction vector by a factor (e.g., 2 for doubling the length)
factor = 2
extendedDirectionVector = vtk.vtkVector3d()
extendedDirectionVector.SetX(directionVector.GetX() * factor)
extendedDirectionVector.SetY(directionVector.GetY() * factor)
extendedDirectionVector.SetZ(directionVector.GetZ() * factor)

# Calculate and add the fourth point (extended)
fourthPoint = vtk.vtkVector3d()
fourthPoint.SetX(thirdPoint.GetX() + extendedDirectionVector.GetX())
fourthPoint.SetY(thirdPoint.GetY() + extendedDirectionVector.GetY())
fourthPoint.SetZ(thirdPoint.GetZ() + extendedDirectionVector.GetZ())
L_B.AddControlPoint(fourthPoint)

```
This screenshot shows how these lines should look like after the code, with the "Bone" model or toggled view for hard tissue and every other markup hidden. 
![image](https://github.com/user-attachments/assets/6eb075b7-af7c-4bac-bae0-96a38987eac6)

Now, some manual adjustments are required to proceed: As you can see, Line_B needs to be toggled along itself as it is currently starting at the rhinion and we need it spanning before and after its determining landmarks. To do that, click on the “Line_B” icon in the **Node List** in **Markups** and scroll down to “_Display_ options and click on _Interaction handles_. Enable **Visibility** and **Translation**, then use the red arrow to pull the line upwards without changing its direction:


https://github.com/user-attachments/assets/53d1ad03-793b-43b3-abc6-ef4b172b0f5d



### Intersection points between Line B and the intersection lines

The intersection points (called “mirror points” in the code) of planes A, B, C etc with Line_B will be added by the next code, with hot pink showing them. Choose “B intersection points 4” “B intersection points 5” or “B intersection points 6” according to the number of your planes. Optionally, if you wish to compare the curvature of the bony and soft nasal profile, you can also establish the same intersection points for Line A - scroll down to heading _Intersection points between Line A and intersection lines_ for this extra snippet.

### Line B Intersection Points

This step finds the intersection points between the reference line (`Line_B`) and the sagittal intersection lines (`MSP_A`/`INB_A`, `MSP_B`/`INB_B`, etc.) created in the previous step. The new intersection points are created as uniquely named fiducials.

<details>

<summary>4 plane Line B intersection</summary>

```python
import numpy as np
import slicer

# --- Configuration ---
main_line_name = 'Line_B'
line_prefix_priority = ['MSP', 'INB']
mirror_plane_suffixes = ['A', 'B', 'C', 'D']
fiducial_color = (255/255, 105/255, 180/255) # Hot Pink

# --- Main Script ---

def get_line_points(lineNode):
    """Safely get start and end points of a markups line."""
    if not lineNode or lineNode.GetNumberOfControlPoints() < 2:
        return None, None
    startPoint = np.zeros(3)
    endPoint = np.zeros(3)
    lineNode.GetNthControlPointPosition(0, startPoint)
    lineNode.GetNthControlPointPosition(1, endPoint)
    return startPoint, endPoint

def find_line_intersection(line1Node, line2Node):
    """Finds the 3D intersection point of two lines."""
    p1, p2 = get_line_points(line1Node)
    q1, q2 = get_line_points(line2Node)

    if p1 is None or q1 is None:
        return None

    d1 = p2 - p1
    d2 = q2 - q1

    norm_d1 = np.linalg.norm(d1)
    norm_d2 = np.linalg.norm(d2)

    if norm_d1 == 0 or norm_d2 == 0:
        return None # Line has zero length

    d1 /= norm_d1
    d2 /= norm_d2

    cross_d1_d2 = np.cross(d1, d2)
    norm_cross = np.linalg.norm(cross_d1_d2)

    if norm_cross < 1e-6:
        return None  # Lines are parallel

    # Solve for the intersection point
    try:
        t = np.dot(np.cross((q1 - p1), d2), cross_d1_d2) / norm_cross**2
        intersection_point = p1 + t * d1
        return intersection_point
    except Exception as e:
        print(f"Could not calculate intersection: {e}")
        return None

# --- Execution ---
main_line_node = slicer.mrmlScene.GetFirstNodeByName(main_line_name)
if not main_line_node:
    slicer.util.errorDisplay(f"Error: Main line '{main_line_name}' not found.")
    raise ValueError(f"'{main_line_name}' not found.")

# Determine which prefix to use (MSP or INB)
prefix_to_use = None
for prefix in line_prefix_priority:
    # Check if a line with this prefix exists (e.g., 'MSP_A')
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{mirror_plane_suffixes[0]}"):
        prefix_to_use = prefix
        print(f"Found intersection lines with prefix: '{prefix_to_use}'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Error: Could not find any intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Intersection lines not found.")

# Generate the list of line names to check
lines_to_intersect = [f"{prefix_to_use}_{suffix}" for suffix in mirror_plane_suffixes]

for i, line_name in enumerate(lines_to_intersect):
    line2Node = slicer.mrmlScene.GetFirstNodeByName(line_name)
    if not line2Node:
        print(f"Warning: Line '{line_name}' not found. Skipping.")
        continue

    intersection_point = find_line_intersection(main_line_node, line2Node)

    if intersection_point is not None:
        fiducial_name = f'mirrorB_{chr(65 + i)}'
        # Clean up old fiducial if it exists
        old_fiducial = slicer.mrmlScene.GetFirstNodeByName(fiducial_name)
        if old_fiducial:
            slicer.mrmlScene.RemoveNode(old_fiducial)

        fiducialNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', fiducial_name)
        fiducialNode.AddControlPoint(intersection_point)

        # Set fiducial color
        displayNode = fiducialNode.GetDisplayNode()
        if displayNode:
            displayNode.SetSelectedColor(fiducial_color)
            displayNode.SetColor(fiducial_color)
        print(f"Created intersection point '{fiducial_name}'.")
    else:
        print(f"No intersection found between '{main_line_name}' and '{line_name}'.")

```

![image](https://github.com/user-attachments/assets/2a6b319b-4054-407f-a245-43b55089599c)

</details>


<details>
<summary>5 plane Line B intersection</summary>

```python
import numpy as np
import slicer

# --- Configuration ---
main_line_name = 'Line_B'
line_prefix_priority = ['MSP', 'INB']
mirror_plane_suffixes = ['A', 'B', 'C', 'D', 'E']
fiducial_color = (255/255, 105/255, 180/255) # Hot Pink

# --- Main Script ---

def get_line_points(lineNode):
    """Safely get start and end points of a markups line."""
    if not lineNode or lineNode.GetNumberOfControlPoints() < 2:
        return None, None
    startPoint = np.zeros(3)
    endPoint = np.zeros(3)
    lineNode.GetNthControlPointPosition(0, startPoint)
    lineNode.GetNthControlPointPosition(1, endPoint)
    return startPoint, endPoint

def find_line_intersection(line1Node, line2Node):
    """Finds the 3D intersection point of two lines."""
    p1, p2 = get_line_points(line1Node)
    q1, q2 = get_line_points(line2Node)

    if p1 is None or q1 is None:
        return None

    d1 = p2 - p1
    d2 = q2 - q1

    norm_d1 = np.linalg.norm(d1)
    norm_d2 = np.linalg.norm(d2)

    if norm_d1 == 0 or norm_d2 == 0:
        return None # Line has zero length

    d1 /= norm_d1
    d2 /= norm_d2

    cross_d1_d2 = np.cross(d1, d2)
    norm_cross = np.linalg.norm(cross_d1_d2)

    if norm_cross < 1e-6:
        return None  # Lines are parallel

    # Solve for the intersection point
    try:
        t = np.dot(np.cross((q1 - p1), d2), cross_d1_d2) / norm_cross**2
        intersection_point = p1 + t * d1
        return intersection_point
    except Exception as e:
        print(f"Could not calculate intersection: {e}")
        return None

# --- Execution ---
main_line_node = slicer.mrmlScene.GetFirstNodeByName(main_line_name)
if not main_line_node:
    slicer.util.errorDisplay(f"Error: Main line '{main_line_name}' not found.")
    raise ValueError(f"'{main_line_name}' not found.")

# Determine which prefix to use (MSP or INB)
prefix_to_use = None
for prefix in line_prefix_priority:
    # Check if a line with this prefix exists (e.g., 'MSP_A')
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{mirror_plane_suffixes[0]}"):
        prefix_to_use = prefix
        print(f"Found intersection lines with prefix: '{prefix_to_use}'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Error: Could not find any intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Intersection lines not found.")

# Generate the list of line names to check
lines_to_intersect = [f"{prefix_to_use}_{suffix}" for suffix in mirror_plane_suffixes]

for i, line_name in enumerate(lines_to_intersect):
    line2Node = slicer.mrmlScene.GetFirstNodeByName(line_name)
    if not line2Node:
        print(f"Warning: Line '{line_name}' not found. Skipping.")
        continue

    intersection_point = find_line_intersection(main_line_node, line2Node)

    if intersection_point is not None:
        fiducial_name = f'mirrorB_{chr(65 + i)}'
        # Clean up old fiducial if it exists
        old_fiducial = slicer.mrmlScene.GetFirstNodeByName(fiducial_name)
        if old_fiducial:
            slicer.mrmlScene.RemoveNode(old_fiducial)

        fiducialNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', fiducial_name)
        fiducialNode.AddControlPoint(intersection_point)

        # Set fiducial color
        displayNode = fiducialNode.GetDisplayNode()
        if displayNode:
            displayNode.SetSelectedColor(fiducial_color)
            displayNode.SetColor(fiducial_color)
        print(f"Created intersection point '{fiducial_name}'.")
    else:
        print(f"No intersection found between '{main_line_name}' and '{line_name}'.")
```

![image](https://github.com/user-attachments/assets/b3e7883c-5f12-4f4b-86e3-ce2e35cb5966)

</details>


<details>
<summary>6 plane Line B intersection</summary>

```python
import numpy as np
import slicer

# --- Configuration ---
main_line_name = 'Line_B'
line_prefix_priority = ['MSP', 'INB']
mirror_plane_suffixes = ['A', 'B', 'C', 'D', 'E', 'F']
fiducial_color = (255/255, 105/255, 180/255) # Hot Pink

# --- Main Script ---

def get_line_points(lineNode):
    """Safely get start and end points of a markups line."""
    if not lineNode or lineNode.GetNumberOfControlPoints() < 2:
        return None, None
    startPoint = np.zeros(3)
    endPoint = np.zeros(3)
    lineNode.GetNthControlPointPosition(0, startPoint)
    lineNode.GetNthControlPointPosition(1, endPoint)
    return startPoint, endPoint

def find_line_intersection(line1Node, line2Node):
    """Finds the 3D intersection point of two lines."""
    p1, p2 = get_line_points(line1Node)
    q1, q2 = get_line_points(line2Node)

    if p1 is None or q1 is None:
        return None

    d1 = p2 - p1
    d2 = q2 - q1

    norm_d1 = np.linalg.norm(d1)
    norm_d2 = np.linalg.norm(d2)

    if norm_d1 == 0 or norm_d2 == 0:
        return None # Line has zero length

    d1 /= norm_d1
    d2 /= norm_d2

    cross_d1_d2 = np.cross(d1, d2)
    norm_cross = np.linalg.norm(cross_d1_d2)

    if norm_cross < 1e-6:
        return None  # Lines are parallel

    # Solve for the intersection point
    try:
        t = np.dot(np.cross((q1 - p1), d2), cross_d1_d2) / norm_cross**2
        intersection_point = p1 + t * d1
        return intersection_point
    except Exception as e:
        print(f"Could not calculate intersection: {e}")
        return None

# --- Execution ---
main_line_node = slicer.mrmlScene.GetFirstNodeByName(main_line_name)
if not main_line_node:
    slicer.util.errorDisplay(f"Error: Main line '{main_line_name}' not found.")
    raise ValueError(f"'{main_line_name}' not found.")

# Determine which prefix to use (MSP or INB)
prefix_to_use = None
for prefix in line_prefix_priority:
    # Check if a line with this prefix exists (e.g., 'MSP_A')
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{mirror_plane_suffixes[0]}"):
        prefix_to_use = prefix
        print(f"Found intersection lines with prefix: '{prefix_to_use}'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Error: Could not find any intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Intersection lines not found.")

# Generate the list of line names to check
lines_to_intersect = [f"{prefix_to_use}_{suffix}" for suffix in mirror_plane_suffixes]

for i, line_name in enumerate(lines_to_intersect):
    line2Node = slicer.mrmlScene.GetFirstNodeByName(line_name)
    if not line2Node:
        print(f"Warning: Line '{line_name}' not found. Skipping.")
        continue

    intersection_point = find_line_intersection(main_line_node, line2Node)

    if intersection_point is not None:
        fiducial_name = f'mirrorB_{chr(65 + i)}'
        # Clean up old fiducial if it exists
        old_fiducial = slicer.mrmlScene.GetFirstNodeByName(fiducial_name)
        if old_fiducial:
            slicer.mrmlScene.RemoveNode(old_fiducial)

        fiducialNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', fiducial_name)
        fiducialNode.AddControlPoint(intersection_point)

        # Set fiducial color
        displayNode = fiducialNode.GetDisplayNode()
        if displayNode:
            displayNode.SetSelectedColor(fiducial_color)
            displayNode.SetColor(fiducial_color)
        print(f"Created intersection point '{fiducial_name}'.")
    else:
        print(f"No intersection found between '{main_line_name}' and '{line_name}'.")
```

![image](https://github.com/user-attachments/assets/748c6a20-6caa-4419-aad2-ac1483ad3a8e)

</details>


##### Optional Line A intersections

<details>
<summary>4 plane optional Line A intersection points</summary>

###Code for optional Line A intersection points, 4 planes

This script now automatically detects whether to use `MSP_A`, `MSP_B`, etc., or `INB_A`, `INB_B`, etc., based on what it finds in the scene.

```python
### Line A intersection (4 planes, MSP/INB compatible) ###
import numpy as np
import slicer

# --- Configuration ---
main_line_name = 'Line_A'
line_prefix_priority = ['MSP', 'INB']
mirror_plane_suffixes = ['A', 'B', 'C', 'D']
new_point_prefix = 'mirrorA'
# Color for the new points (turquoise)
new_point_color = (0.25, 0.88, 0.81) # (R, G, B) normalized to 0-1

# --- Main Script ---

# 1. Determine the correct prefix for the intersection lines
found_prefix = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{mirror_plane_suffixes[0]}"):
        found_prefix = prefix
        print(f"Found intersection lines with prefix: '{found_prefix}_'")
        break

if not found_prefix:
    slicer.util.errorDisplay(f"Error: Could not find intersection lines with prefixes like 'MSP_' or 'INB_'.")
    raise ValueError("Required intersection lines not found.")

# 2. Dynamically create the list of line names to check
lines_to_intersect = [f"{found_prefix}_{suffix}" for suffix in mirror_plane_suffixes]

# 3. Get the main line node
lineNode_A = slicer.util.getNode(main_line_name)
if not lineNode_A:
    slicer.util.errorDisplay(f"Error: The primary line '{main_line_name}' was not found.")
    raise ValueError(f"'{main_line_name}' not found.")

# --- Helper Functions ---
def get_line_points(lineNode):
    startPoint = np.zeros(3)
    endPoint = np.zeros(3)
    lineNode.GetNthControlPointPositionWorld(0, startPoint)
    lineNode.GetNthControlPointPositionWorld(1, endPoint)
    return startPoint, endPoint

def find_line_intersection(line1Node, line2Node):
    p1, p2 = get_line_points(line1Node)
    d1 = p2 - p1
    q1, q2 = get_line_points(line2Node)
    d2 = q2 - q1

    if np.linalg.norm(d1) == 0 or np.linalg.norm(d2) == 0: return None
    d1 /= np.linalg.norm(d1)
    d2 /= np.linalg.norm(d2)

    cross_d1_d2 = np.cross(d1, d2)
    if np.linalg.norm(cross_d1_d2) < 1e-6: return None

    t = np.dot(np.cross((q1 - p1), d2), cross_d1_d2) / np.linalg.norm(cross_d1_d2)**2
    return p1 + t * d1

# 4. Find intersections and create fiducial points
print(f"Finding intersections with: {lines_to_intersect}")
for i, line_name in enumerate(lines_to_intersect):
    line2Node = slicer.util.getNode(line_name)
    if not line2Node:
        print(f"Warning: Line '{line_name}' not found, skipping.")
        continue

    intersection_point = find_line_intersection(lineNode_A, line2Node)
    if intersection_point is not None:
        point_name = f'{new_point_prefix}_{chr(65 + i)}'
        old_point = slicer.mrmlScene.GetFirstNodeByName(point_name)
        if old_point: slicer.mrmlScene.RemoveNode(old_point)
        
        fiducialNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', point_name)
        fiducialNode.AddControlPoint(intersection_point)
        
        displayNode = fiducialNode.GetDisplayNode()
        displayNode.SetSelectedColor(new_point_color)
        displayNode.SetTextScale(0)
        print(f"Created intersection point '{point_name}'.")
    else:
        print(f"No intersection found between '{main_line_name}' and '{line_name}'.")
```
Screenshot of both line (A and B) intersection points established on a 4 plane model
![image](https://github.com/user-attachments/assets/050b49d1-eb5d-4684-9949-1fdb6fa73462)

</details>

<details>
<summary>5 plane optional Line A intersection points</summary>
###Code for optional Line A intersections, 5 planes

This version is identical in logic but is configured to look for the five intersection lines (`_A` through `_E`).

```python
### Line A intersection (5 planes, MSP/INB compatible) ###
import numpy as np
import slicer

# --- Configuration ---
main_line_name = 'Line_A'
line_prefix_priority = ['MSP', 'INB']
mirror_plane_suffixes = ['A', 'B', 'C', 'D', 'E'] # Changed for 5 planes
new_point_prefix = 'mirrorA'
# Color for the new points (turquoise)
new_point_color = (0.25, 0.88, 0.81) # (R, G, B) normalized to 0-1

# --- Main Script ---

# 1. Determine the correct prefix for the intersection lines
found_prefix = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{mirror_plane_suffixes[0]}"):
        found_prefix = prefix
        print(f"Found intersection lines with prefix: '{found_prefix}_'")
        break

if not found_prefix:
    slicer.util.errorDisplay(f"Error: Could not find intersection lines with prefixes like 'MSP_' or 'INB_'.")
    raise ValueError("Required intersection lines not found.")

# 2. Dynamically create the list of line names to check
lines_to_intersect = [f"{found_prefix}_{suffix}" for suffix in mirror_plane_suffixes]

# 3. Get the main line node
lineNode_A = slicer.util.getNode(main_line_name)
if not lineNode_A:
    slicer.util.errorDisplay(f"Error: The primary line '{main_line_name}' was not found.")
    raise ValueError(f"'{main_line_name}' not found.")

# --- Helper Functions ---
def get_line_points(lineNode):
    startPoint = np.zeros(3)
    endPoint = np.zeros(3)
    lineNode.GetNthControlPointPositionWorld(0, startPoint)
    lineNode.GetNthControlPointPositionWorld(1, endPoint)
    return startPoint, endPoint

def find_line_intersection(line1Node, line2Node):
    p1, p2 = get_line_points(line1Node)
    d1 = p2 - p1
    q1, q2 = get_line_points(line2Node)
    d2 = q2 - q1

    if np.linalg.norm(d1) == 0 or np.linalg.norm(d2) == 0: return None
    d1 /= np.linalg.norm(d1)
    d2 /= np.linalg.norm(d2)

    cross_d1_d2 = np.cross(d1, d2)
    if np.linalg.norm(cross_d1_d2) < 1e-6: return None

    t = np.dot(np.cross((q1 - p1), d2), cross_d1_d2) / np.linalg.norm(cross_d1_d2)**2
    return p1 + t * d1

# 4. Find intersections and create fiducial points
print(f"Finding intersections with: {lines_to_intersect}")
for i, line_name in enumerate(lines_to_intersect):
    line2Node = slicer.util.getNode(line_name)
    if not line2Node:
        print(f"Warning: Line '{line_name}' not found, skipping.")
        continue

    intersection_point = find_line_intersection(lineNode_A, line2Node)
    if intersection_point is not None:
        point_name = f'{new_point_prefix}_{chr(65 + i)}'
        old_point = slicer.mrmlScene.GetFirstNodeByName(point_name)
        if old_point: slicer.mrmlScene.RemoveNode(old_point)

        fiducialNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', point_name)
        fiducialNode.AddControlPoint(intersection_point)
        
        displayNode = fiducialNode.GetDisplayNode()
        displayNode.SetSelectedColor(new_point_color)
        displayNode.SetTextScale(0)
        print(f"Created intersection point '{point_name}'.")
    else:
        print(f"No intersection found between '{main_line_name}' and '{line_name}'.")
```
Screenshot of both line (A and B) intersection points established on a 5 plane model
![image](https://github.com/user-attachments/assets/dfeef8b2-2d02-49de-a57e-1dec4c570c0d)

</details>

<details>
<summary>6 plane optional Line A intersection points</summary>

####Code for optional Line A intersection, 6 planes

This version is also identical in logic but is configured to look for all six intersection lines (`_A` through `_F`).

```python
### Line A intersection (6 planes, MSP/INB compatible) ###
import numpy as np
import slicer

# --- Configuration ---
main_line_name = 'Line_A'
line_prefix_priority = ['MSP', 'INB']
mirror_plane_suffixes = ['A', 'B', 'C', 'D', 'E', 'F'] # Changed for 6 planes
new_point_prefix = 'mirrorA'
# Color for the new points (turquoise)
new_point_color = (0.25, 0.88, 0.81) # (R, G, B) normalized to 0-1

# --- Main Script ---

# 1. Determine the correct prefix for the intersection lines
found_prefix = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{mirror_plane_suffixes[0]}"):
        found_prefix = prefix
        print(f"Found intersection lines with prefix: '{found_prefix}_'")
        break

if not found_prefix:
    slicer.util.errorDisplay(f"Error: Could not find intersection lines with prefixes like 'MSP_' or 'INB_'.")
    raise ValueError("Required intersection lines not found.")

# 2. Dynamically create the list of line names to check
lines_to_intersect = [f"{found_prefix}_{suffix}" for suffix in mirror_plane_suffixes]

# 3. Get the main line node
lineNode_A = slicer.util.getNode(main_line_name)
if not lineNode_A:
    slicer.util.errorDisplay(f"Error: The primary line '{main_line_name}' was not found.")
    raise ValueError(f"'{main_line_name}' not found.")

# --- Helper Functions ---
def get_line_points(lineNode):
    startPoint = np.zeros(3)
    endPoint = np.zeros(3)
    lineNode.GetNthControlPointPositionWorld(0, startPoint)
    lineNode.GetNthControlPointPositionWorld(1, endPoint)
    return startPoint, endPoint

def find_line_intersection(line1Node, line2Node):
    p1, p2 = get_line_points(line1Node)
    d1 = p2 - p1
    q1, q2 = get_line_points(line2Node)
    d2 = q2 - q1

    if np.linalg.norm(d1) == 0 or np.linalg.norm(d2) == 0: return None
    d1 /= np.linalg.norm(d1)
    d2 /= np.linalg.norm(d2)

    cross_d1_d2 = np.cross(d1, d2)
    if np.linalg.norm(cross_d1_d2) < 1e-6: return None

    t = np.dot(np.cross((q1 - p1), d2), cross_d1_d2) / np.linalg.norm(cross_d1_d2)**2
    return p1 + t * d1

# 4. Find intersections and create fiducial points
print(f"Finding intersections with: {lines_to_intersect}")
for i, line_name in enumerate(lines_to_intersect):
    line2Node = slicer.util.getNode(line_name)
    if not line2Node:
        print(f"Warning: Line '{line_name}' not found, skipping.")
        continue

    intersection_point = find_line_intersection(lineNode_A, line2Node)
    if intersection_point is not None:
        point_name = f'{new_point_prefix}_{chr(65 + i)}'
        old_point = slicer.mrmlScene.GetFirstNodeByName(point_name)
        if old_point: slicer.mrmlScene.RemoveNode(old_point)

        fiducialNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', point_name)
        fiducialNode.AddControlPoint(intersection_point)
        
        displayNode = fiducialNode.GetDisplayNode()
        displayNode.SetSelectedColor(new_point_color)
        displayNode.SetTextScale(0)
        print(f"Created intersection point '{point_name}'.")
    else:
        print(f"No intersection found between '{main_line_name}' and '{line_name}'.")
```
Screenshot of both line (A and B) intersection points established on a 6 plane model
![image](https://github.com/user-attachments/assets/4d17b458-90b3-4e8c-93a1-038d518ad0c1)

</details>

### Nasal Bone outline landmarks
Then hide these intersection points and additional information until you have ONLY the skull and the 4/5/6 lines along the INB and Plane A, B,C, D visible. These will be called INB_A, INB_B, INB_C and INB_D (additionally, INB_E and INB_F, if you have 5/6 planes). 

![image](https://github.com/user-attachments/assets/977acc5c-2ec5-4b89-b9c0-ac468ced8723)
I added the names on the screenshot, but these structures are the only ones relevant for the next steps.

Download the json files based on the number of planes you're working with: 

- [nasal bone outline 4.mrk.json](https://github.com/user-attachments/files/19318005/nasal.bone.outline.4.mrk.json)
- [nasal bone outline 5.mrk.json](https://github.com/user-attachments/files/19318009/nasal.bone.outline.5.mrk.json)
- [nasal bone outline 6.mrk.json](https://github.com/user-attachments/files/19318010/nasal.bone.outline.6.mrk.json)

Drag-and-drop into the markups environment, click OK, then plane the points manually. Make sure you have the model in the correct orientation, with the Rx points on the right and Lx points on the left. 

Example of the content of the json in the case of 4 planes

| Name | Where to place?   | 
|-----------|------------|
| R1 | where the bony nasal outline meets the first line from superior (INB_B) on the right   | 
| R2 | where the bony nasal outline meets the second line from superior (INB_C) on the right   |
| R3 | where the bony nasal outline meets the third line from superior (INB_D) on the right   | 
| R4 | where the bony nasal outline meets the fourth line from superior (INB_A) on the right   |
| L1 | where the bony nasal outline meets the first line from superior (INB_B) on the left   | 
| L2 | where the bony nasal outline meets the second line from superior INB_C) on the left   |
| L3 | where the bony nasal outline meets the third line from superior (INB_D) on the left   | 
| L4 | where the bony nasal outline meets the fourth line from superior (INB_A) on the left  |


![image](https://github.com/user-attachments/assets/8896ea6b-0a56-4991-9b7e-12e6ffc86912)

### Soft tissue nose outline landmarks

Adjust your view or call on your skin model to see the soft nose profile.
Download the applicable Markup file for your number of planes: 


- [nose profile outline 4.mrk.json](https://github.com/user-attachments/files/19327865/nose.profile.outline.4.mrk.json)
- [nose profile outline 5.mrk.json](https://github.com/user-attachments/files/19327866/nose.profile.outline.5.mrk.json)
- [nose profile outline 6.mrk.json](https://github.com/user-attachments/files/19327871/nose.profile.outline.6.mrk.json)

Example of the content of the json in the case of 4 planes

| Name | Where to place?   | 
|-----------|------------|
| 1 | where the soft nose surface meets the first line from superior (INB_B) in the middle   | 
| 2 | where the soft nose surface  meets the second line from superior (INB_C) in the middle   |
| 3 | where the soft nose surface  meets the third line from superior (INB_D) in the middle   | 
| 4 | where the soft nose surface  meets the fourth line from superior (INB_A) in the middle   |


Drag and drop “nose profile outline4/5/6” into the Markups environment and place the dots 1…4/5/6 along the nasal profile and line intersections. Make sure these meet the lines - a slightly turned view is the most helpful for this. 
Example for the position of the model and placement of points for 4 planes: 
![image](https://github.com/user-attachments/assets/5897c99a-cba1-4d0a-9aaf-8ff7c625375a)

<details>

<summary>Are the labels in the way to place these points?</summary>

### Does your scene look a bit like this?
NB: this is a 5-plane workflow screenshot

<img src="https://github.com/user-attachments/assets/8e74b437-4f9d-4827-9d0d-3ee2544d38b5" width="500">

If you go to Markups, choose your line the label of which in the way (INB_A in the example here), then choose **Display**>_Advanced_, scroll down to **Properties Label** and untick it, it should hide the label from view. 

![image](https://github.com/user-attachments/assets/9ee86616-8d93-4eaa-960b-e8526cebb3d4)

</details>

The reason for handling the soft and hard tissue differently in this case is due to their shapes: the nose has a convex, the nasal orifice has a concave geometry that is harder to measure without any metadata adjustments (to avoid “eyeballing” and interpretative errors and improve reproducibility). Instead, we mark the outline of the nasal aperture on both sides, connect them (R1 ro L1 etc.) and check it they meet the “mirror” line B.


### Measurement lines 
This will be a 3-step process regardless of how many planes you choose for your process. Copy, paste and run code below for your number of planes.

#### Nasal bone outline connecting lines
 1.This step creates the lines between the nasal bone outline points R1-L1, etc. and names them “nasal outline1” etc

<details>

<summary>Code for 4-plane nasal outline lines</summary>

``` python
###  4 nasal outline lines
import slicer

# Get the point list node
pointListNode = slicer.util.getNode('nasal bone outline 4')

# Function to get point coordinates by index
def getPointCoordinatesByIndex(pointListNode, index):
    if index < pointListNode.GetNumberOfControlPoints():
        position = [0.0, 0.0, 0.0]
        pointListNode.GetNthControlPointPosition(index, position)
        return position
    return None

# Add linear markups for each pair of points
pointPairs = [(0, 4), (1, 5), (2, 6), (3, 7)]
for index, pair in enumerate(pointPairs):
    point1 = getPointCoordinatesByIndex(pointListNode, pair[0])
    point2 = getPointCoordinatesByIndex(pointListNode, pair[1])
    
    if point1 is not None and point2 is not None:
        # Check if a node with the same name already exists
        line_name = f'nasal outline{index + 1}'
        existingNode = slicer.mrmlScene.GetFirstNodeByName(line_name)
        if existingNode:
            slicer.mrmlScene.RemoveNode(existingNode)

        # Create a new linear markup node
        lineMarkupNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', line_name)
        
        # Add points to the linear markup
        lineMarkupNode.AddControlPoint(point1)
        lineMarkupNode.AddControlPoint(point2)
        
        # Set the color to baby blue (RGB: 137, 207, 240)
        displayNode = lineMarkupNode.GetDisplayNode()
        displayNode.SetSelectedColor(137/255, 207/255, 240/255)
    else:
        print(f'Points for indices {pair[0]} or {pair[1]} not found.')
```

<img src="https://github.com/user-attachments/assets/be8c5f36-b083-4f39-bdf9-8b5f6d1e8127" width="500">

</details>

<details>

<summary>Code for 5-plane nasal outline lines</summary>

``` python
###  5 nasal outline lines
import slicer

# Get the point list node
pointListNode = slicer.util.getNode('nasal bone outline 5')

# Function to get point coordinates by index
def getPointCoordinatesByIndex(pointListNode, index):
    if index < pointListNode.GetNumberOfControlPoints():
        position = [0.0, 0.0, 0.0]
        pointListNode.GetNthControlPointPosition(index, position)
        return position
    return None

# Add linear markups for each pair of points
pointPairs = [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]
for index, pair in enumerate(pointPairs):
    point1 = getPointCoordinatesByIndex(pointListNode, pair[0])
    point2 = getPointCoordinatesByIndex(pointListNode, pair[1])
    
    if point1 is not None and point2 is not None:
        # Check if a node with the same name already exists
        line_name = f'nasal outline{index + 1}'
        existingNode = slicer.mrmlScene.GetFirstNodeByName(line_name)
        if existingNode:
            slicer.mrmlScene.RemoveNode(existingNode)

        # Create a new linear markup node
        lineMarkupNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', line_name)
        
        # Add points to the linear markup
        lineMarkupNode.AddControlPoint(point1)
        lineMarkupNode.AddControlPoint(point2)
        
        # Set the color to baby blue (RGB: 137, 207, 240)
        displayNode = lineMarkupNode.GetDisplayNode()
        displayNode.SetSelectedColor(137/255, 207/255, 240/255)
    else:
        print(f'Points for indices {pair[0]} or {pair[1]} not found.')
```

<img src="https://github.com/user-attachments/assets/5937085a-9e71-4d86-848f-7bde519f8768" width="500">

</details>

<details>

<summary>Code for 6-plane nasal outline lines</summary>

``` python
###  6 nasal outline lines
import slicer

# Get the point list node
pointListNode = slicer.util.getNode('nasal bone outline 6')

def getPointCoordinatesByIndex(pointListNode, index):
    if index < pointListNode.GetNumberOfControlPoints():
        position = [0.0, 0.0, 0.0]
        pointListNode.GetNthControlPointPosition(index, position)
        return position
    return None

# Add linear markups for each pair of points
pointPairs = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
for index, pair in enumerate(pointPairs):
    if pair[0] < pointListNode.GetNumberOfControlPoints() and pair[1] < pointListNode.GetNumberOfControlPoints():
        point1 = getPointCoordinatesByIndex(pointListNode, pair[0])
        point2 = getPointCoordinatesByIndex(pointListNode, pair[1])
        
        if point1 is not None and point2 is not None:
            # Check if a node with the same name already exists
            line_name = f'nasal outline{index + 1}'
            existingNode = slicer.mrmlScene.GetFirstNodeByName(line_name)
            if existingNode:
                slicer.mrmlScene.RemoveNode(existingNode)

            # Create a new linear markup node
            lineMarkupNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', line_name)
            
            # Add points to the linear markup
            lineMarkupNode.AddControlPoint(point1)
            lineMarkupNode.AddControlPoint(point2)
            
            # Set the color to baby blue (RGB: 137, 207, 240)
            displayNode = lineMarkupNode.GetDisplayNode()
            displayNode.SetSelectedColor(137/255, 207/255, 240/255)
        else:
            print(f'Points for indices {pair[0]} or {pair[1]} not found.')
    else:
        print(f'Indices {pair[0]} or {pair[1]} are out of range.')
```

<img src="https://github.com/user-attachments/assets/7cb83356-6e1d-43a2-8b13-ba0973ae15db" width="500">

</details>

#### Nasal bone outline connecting lines & their intersections with sagittal lines
 2. This step finds the intersection points of these R-L nasal aperture lines and the sagittal lines (e.g., MSP_B or INB_B) in magenta, and names them “bone1” etc.

<details>

<summary>Code for 4-plane nasal outline intersections</summary>

``` python
###  4 planes - nasal outline intersections (MSP/INB compatible)
import slicer
import numpy as np

# --- Configuration ---
line_prefix_priority = ['MSP', 'INB']
# This mapping preserves the original logic: 'nasal outline1' intersects with sagittal line B, etc.
intersection_map = [
    ('nasal outline1', 'B'),
    ('nasal outline2', 'C'),
    ('nasal outline3', 'D'),
    ('nasal outline4', 'A'),
]

# --- Helper Functions ---
def get_line_points(line_node):
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return p1, p2

def find_intersection(line1_points, line2_points):
    p1, p2 = line1_points
    p3, p4 = line2_points
    d1, d2 = p2 - p1, p4 - p3
    if np.linalg.norm(d1) == 0 or np.linalg.norm(d2) == 0: return None
    A = np.array([d1, -d2]).T
    b = p3 - p1
    try:
        t, s = np.linalg.lstsq(A, b, rcond=None)[0]
        return p1 + t * d1
    except np.linalg.LinAlgError:
        return None

def create_fiducial(name, position):
    old_node = slicer.mrmlScene.GetFirstNodeByName(name)
    if old_node: slicer.mrmlScene.RemoveNode(old_node)
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', name)
    node.AddControlPoint(position)
    displayNode = node.GetDisplayNode()
    displayNode.SetSelectedColor(1.0, 0.0, 1.0) # Magenta

# --- Execution ---
prefix_to_use = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{intersection_map[0][1]}"):
        prefix_to_use = prefix
        print(f"Found sagittal lines with prefix: '{prefix_to_use}_'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Could not find required sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

for i, (outline_name, suffix) in enumerate(intersection_map):
    outline_node = slicer.util.getNode(outline_name)
    sagittal_line_name = f"{prefix_to_use}_{suffix}"
    sagittal_node = slicer.util.getNode(sagittal_line_name)

    if not outline_node or not sagittal_node:
        print(f"Warning: Missing node '{outline_name}' or '{sagittal_line_name}'. Skipping.")
        continue

    intersection = find_intersection(get_line_points(outline_node), get_line_points(sagittal_node))
    if intersection is not None:
        create_fiducial(f"bone{i+1}", intersection)
    else:
        print(f"No intersection found between {outline_name} and {sagittal_line_name}.")
```

<img src="https://github.com/user-attachments/assets/d9f9f43d-acc8-4c64-9aa1-4595069e1caa" width="500">

</details>

<details>

<summary>Code for 5-plane nasal outline intersections</summary>

``` python
###  5 planes - nasal outline intersections (MSP/INB compatible)
import slicer
import numpy as np

# --- Configuration ---
line_prefix_priority = ['MSP', 'INB']
intersection_map = [
    ('nasal outline1', 'B'),
    ('nasal outline2', 'C'),
    ('nasal outline3', 'D'),
    ('nasal outline4', 'E'),
    ('nasal outline5', 'A'),
]

# --- Helper Functions (same as 4-plane version) ---
def get_line_points(line_node):
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return p1, p2

def find_intersection(line1_points, line2_points):
    p1, p2 = line1_points
    p3, p4 = line2_points
    d1, d2 = p2 - p1, p4 - p3
    if np.linalg.norm(d1) == 0 or np.linalg.norm(d2) == 0: return None
    A = np.array([d1, -d2]).T
    b = p3 - p1
    try:
        t, s = np.linalg.lstsq(A, b, rcond=None)[0]
        return p1 + t * d1
    except np.linalg.LinAlgError:
        return None

def create_fiducial(name, position):
    old_node = slicer.mrmlScene.GetFirstNodeByName(name)
    if old_node: slicer.mrmlScene.RemoveNode(old_node)
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', name)
    node.AddControlPoint(position)
    displayNode = node.GetDisplayNode()
    displayNode.SetSelectedColor(1.0, 0.0, 1.0) # Magenta

# --- Execution ---
prefix_to_use = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{intersection_map[0][1]}"):
        prefix_to_use = prefix
        print(f"Found sagittal lines with prefix: '{prefix_to_use}_'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Could not find required sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

for i, (outline_name, suffix) in enumerate(intersection_map):
    outline_node = slicer.util.getNode(outline_name)
    sagittal_line_name = f"{prefix_to_use}_{suffix}"
    sagittal_node = slicer.util.getNode(sagittal_line_name)

    if not outline_node or not sagittal_node:
        print(f"Warning: Missing node '{outline_name}' or '{sagittal_line_name}'. Skipping.")
        continue

    intersection = find_intersection(get_line_points(outline_node), get_line_points(sagittal_node))
    if intersection is not None:
        create_fiducial(f"bone{i+1}", intersection)
    else:
        print(f"No intersection found between {outline_name} and {sagittal_line_name}.")
```

<img src="https://github.com/user-attachments/assets/1a9695de-af58-4cb0-89c5-1dc7c1b85f2d" width="500">

</details>

<details>

<summary>Code for 6-plane nasal outline intersections</summary>

``` python
###  6 planes - nasal outline intersections (MSP/INB compatible)
import slicer
import numpy as np

# --- Configuration ---
line_prefix_priority = ['MSP', 'INB']
intersection_map = [
    ('nasal outline1', 'B'),
    ('nasal outline2', 'C'),
    ('nasal outline3', 'D'),
    ('nasal outline4', 'E'),
    ('nasal outline5', 'F'),
    ('nasal outline6', 'A'),
]

# --- Helper Functions (same as 4-plane version) ---
def get_line_points(line_node):
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return p1, p2

def find_intersection(line1_points, line2_points):
    p1, p2 = line1_points
    p3, p4 = line2_points
    d1, d2 = p2 - p1, p4 - p3
    if np.linalg.norm(d1) == 0 or np.linalg.norm(d2) == 0: return None
    A = np.array([d1, -d2]).T
    b = p3 - p1
    try:
        t, s = np.linalg.lstsq(A, b, rcond=None)[0]
        return p1 + t * d1
    except np.linalg.LinAlgError:
        return None

def create_fiducial(name, position):
    old_node = slicer.mrmlScene.GetFirstNodeByName(name)
    if old_node: slicer.mrmlScene.RemoveNode(old_node)
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', name)
    node.AddControlPoint(position)
    displayNode = node.GetDisplayNode()
    displayNode.SetSelectedColor(1.0, 0.0, 1.0) # Magenta

# --- Execution ---
prefix_to_use = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{intersection_map[0][1]}"):
        prefix_to_use = prefix
        print(f"Found sagittal lines with prefix: '{prefix_to_use}_'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Could not find required sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

for i, (outline_name, suffix) in enumerate(intersection_map):
    outline_node = slicer.util.getNode(outline_name)
    sagittal_line_name = f"{prefix_to_use}_{suffix}"
    sagittal_node = slicer.util.getNode(sagittal_line_name)

    if not outline_node or not sagittal_node:
        print(f"Warning: Missing node '{outline_name}' or '{sagittal_line_name}'. Skipping.")
        continue

    intersection = find_intersection(get_line_points(outline_node), get_line_points(sagittal_node))
    if intersection is not None:
        create_fiducial(f"bone{i+1}", intersection)
    else:
        print(f"No intersection found between {outline_name} and {sagittal_line_name}.")
```

<img src="https://github.com/user-attachments/assets/b9cdbbe0-c6ed-4704-9460-84574975ca0c" width="500">

</details>

#### Optional adjusting codes
If you want to programmatically ensure the manually placed midline points meet the sagittal intersection lines.

<details>

<summary>Adjust midline points on 4 planes</summary>

``` python
### Adjust midline points (4 planes, MSP/INB compatible) ###
import slicer
import numpy as np

# --- Configuration ---
line_prefix_priority = ['MSP', 'INB']
# This mapping defines which points are adjusted to which lines
adjust_map = [
    ('bone1', 'nose profile outline 4', 0, 'B'),
    ('bone2', 'nose profile outline 4', 1, 'C'),
    ('bone3', 'nose profile outline 4', 2, 'D'),
    ('bone4', 'nose profile outline 4', 3, 'A'),
]

# --- Helper Functions ---
def get_line_points(line_node):
    if not line_node or line_node.GetNumberOfControlPoints() < 2: return None
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return p1, p2

def adjust_point_to_line(line_points, point_pos):
    p1, p2 = line_points
    line_vec = p2 - p1
    point_vec = point_pos - p1
    line_vec_normalized = line_vec / np.linalg.norm(line_vec)
    projection_length = np.dot(point_vec, line_vec_normalized)
    return p1 + projection_length * line_vec_normalized

# --- Execution ---
prefix_to_use = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{adjust_map[0][3]}"):
        prefix_to_use = prefix
        print(f"Found sagittal lines with prefix: '{prefix_to_use}_'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Could not find required sagittal intersection lines.")
    raise ValueError("Sagittal lines not found.")

for bone_name, outline_name, outline_idx, suffix in adjust_map:
    sagittal_line_name = f"{prefix_to_use}_{suffix}"
    sagittal_line_node = slicer.util.getNode(sagittal_line_name)
    bone_node = slicer.util.getNode(bone_name)
    outline_node = slicer.util.getNode(outline_name)

    if not all([sagittal_line_node, bone_node, outline_node]):
        print(f"Warning: Skipping adjustment for {bone_name} due to missing nodes.")
        continue

    sagittal_line_points = get_line_points(sagittal_line_node)
    if sagittal_line_points is None: continue

    # Adjust 'bone' point
    bone_pos = np.zeros(3)
    bone_node.GetNthControlPointPosition(0, bone_pos)
    adjusted_bone_pos = adjust_point_to_line(sagittal_line_points, bone_pos)
    bone_node.SetNthControlPointPosition(0, adjusted_bone_pos)
    print(f"Adjusted '{bone_name}' to line '{sagittal_line_name}'.")

    # Adjust corresponding 'nose profile outline' point
    outline_pos = np.zeros(3)
    outline_node.GetNthControlPointPosition(outline_idx, outline_pos)
    adjusted_outline_pos = adjust_point_to_line(sagittal_line_points, outline_pos)
    outline_node.SetNthControlPointPosition(outline_idx, adjusted_outline_pos)
    print(f"Adjusted point {outline_idx} of '{outline_name}' to line '{sagittal_line_name}'.")
```

</details>

<details>

<summary>Adjust midline points on 5 planes</summary>

``` python
### Adjust midline points (5 planes, MSP/INB compatible) ###
import slicer
import numpy as np

# --- Configuration ---
line_prefix_priority = ['MSP', 'INB']
adjust_map = [
    ('bone1', 'nose profile outline 5', 0, 'B'),
    ('bone2', 'nose profile outline 5', 1, 'C'),
    ('bone3', 'nose profile outline 5', 2, 'D'),
    ('bone4', 'nose profile outline 5', 3, 'E'),
    ('bone5', 'nose profile outline 5', 4, 'A'),
]

# --- Helper Functions (same as 4-plane version) ---
def get_line_points(line_node):
    if not line_node or line_node.GetNumberOfControlPoints() < 2: return None
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return p1, p2

def adjust_point_to_line(line_points, point_pos):
    p1, p2 = line_points
    line_vec = p2 - p1
    point_vec = point_pos - p1
    line_vec_normalized = line_vec / np.linalg.norm(line_vec)
    projection_length = np.dot(point_vec, line_vec_normalized)
    return p1 + projection_length * line_vec_normalized

# --- Execution ---
prefix_to_use = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{adjust_map[0][3]}"):
        prefix_to_use = prefix
        print(f"Found sagittal lines with prefix: '{prefix_to_use}_'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Could not find required sagittal intersection lines.")
    raise ValueError("Sagittal lines not found.")

for bone_name, outline_name, outline_idx, suffix in adjust_map:
    sagittal_line_name = f"{prefix_to_use}_{suffix}"
    sagittal_line_node = slicer.util.getNode(sagittal_line_name)
    bone_node = slicer.util.getNode(bone_name)
    outline_node = slicer.util.getNode(outline_name)

    if not all([sagittal_line_node, bone_node, outline_node]):
        print(f"Warning: Skipping adjustment for {bone_name} due to missing nodes.")
        continue

    sagittal_line_points = get_line_points(sagittal_line_node)
    if sagittal_line_points is None: continue

    # Adjust 'bone' point
    bone_pos = np.zeros(3)
    bone_node.GetNthControlPointPosition(0, bone_pos)
    adjusted_bone_pos = adjust_point_to_line(sagittal_line_points, bone_pos)
    bone_node.SetNthControlPointPosition(0, adjusted_bone_pos)
    print(f"Adjusted '{bone_name}' to line '{sagittal_line_name}'.")

    # Adjust corresponding 'nose profile outline' point
    outline_pos = np.zeros(3)
    outline_node.GetNthControlPointPosition(outline_idx, outline_pos)
    adjusted_outline_pos = adjust_point_to_line(sagittal_line_points, outline_pos)
    outline_node.SetNthControlPointPosition(outline_idx, adjusted_outline_pos)
    print(f"Adjusted point {outline_idx} of '{outline_name}' to line '{sagittal_line_name}'.")
```

</details>

<details>

<summary>Adjust midline points on 6 planes</summary>

``` python
### Adjust midline points (6 planes, MSP/INB compatible) ###
import slicer
import numpy as np

# --- Configuration ---
line_prefix_priority = ['MSP', 'INB']
# This mapping defines which points are adjusted to which lines
adjust_map = [
    ('bone1', 'nose profile outline 6', 0, 'B'),
    ('bone2', 'nose profile outline 6', 1, 'C'),
    ('bone3', 'nose profile outline 6', 2, 'D'),
    ('bone4', 'nose profile outline 6', 3, 'E'),
    ('bone5', 'nose profile outline 6', 4, 'F'),
    ('bone6', 'nose profile outline 6', 5, 'A'),
]

# --- Helper Functions ---
def get_line_points(line_node):
    """Safely gets the two endpoints of a line markup."""
    if not line_node or line_node.GetNumberOfControlPoints() < 2:
        return None
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return p1, p2

def adjust_point_to_line(line_points, point_pos):
    """Projects a point onto a line and returns the new position."""
    p1, p2 = line_points
    line_vec = p2 - p1
    point_vec = point_pos - p1
    # Handle zero-length line case
    line_norm_sq = np.dot(line_vec, line_vec)
    if line_norm_sq < 1e-9:
        return p1 # Return the start point if line is degenerate
    
    t = np.dot(point_vec, line_vec) / line_norm_sq
    return p1 + t * line_vec

# --- Execution ---
# 1. Find which prefix is being used in the scene (MSP or INB)
prefix_to_use = None
for prefix in line_prefix_priority:
    # Check for the existence of one of the required lines
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{adjust_map[0][3]}"):
        prefix_to_use = prefix
        print(f"Found sagittal lines with prefix: '{prefix_to_use}_'")
        break

if not prefix_to_use:
    slicer.util.errorDisplay("Could not find required sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

# 2. Loop through the map and adjust points
for bone_name, outline_name, outline_idx, suffix in adjust_map:
    # Get all nodes for this iteration
    sagittal_line_name = f"{prefix_to_use}_{suffix}"
    sagittal_line_node = slicer.util.getNode(sagittal_line_name)
    bone_node = slicer.util.getNode(bone_name)
    outline_node = slicer.util.getNode(outline_name)

    # Check if all required nodes exist before proceeding
    if not all([sagittal_line_node, bone_node, outline_node]):
        print(f"Warning: Skipping adjustment for {bone_name} due to missing nodes.")
        continue

    sagittal_line_points = get_line_points(sagittal_line_node)
    if sagittal_line_points is None:
        print(f"Warning: Could not get points for line '{sagittal_line_name}'.")
        continue

    # Adjust the 'bone' point to the sagittal line
    bone_pos = np.zeros(3)
    bone_node.GetNthControlPointPosition(0, bone_pos)
    adjusted_bone_pos = adjust_point_to_line(sagittal_line_points, bone_pos)
    bone_node.SetNthControlPointPosition(0, adjusted_bone_pos)
    print(f"Adjusted '{bone_name}' to line '{sagittal_line_name}'.")

    # Adjust the corresponding 'nose profile outline' point to the same sagittal line
    outline_pos = np.zeros(3)
    outline_node.GetNthControlPointPosition(outline_idx, outline_pos)
    adjusted_outline_pos = adjust_point_to_line(sagittal_line_points, outline_pos)
    outline_node.SetNthControlPointPosition(outline_idx, adjusted_outline_pos)
    print(f"Adjusted point {outline_idx} of '{outline_name}' to line '{sagittal_line_name}'.")
```

</details>

#### Distances between mirror points and nose landmarks
 3. This step creates length measurements from the mirror point to the a) nose profile (outside portion) coloured in orange and names them “noseprofiletoB1/2/3/4” etc; and b) to the nasal aperture (inside portion) coloured lilac and names them “nasalbonetoB1/2/3/4”.

<details>

<summary>Code for 4-plane inside-outside mirror point</summary>

``` python
###  4 planes - inside-outside mirror point
import slicer

# --- Configuration ---
orange = (1.0, 0.5, 0.0)
lilac = (0.78, 0.64, 0.78)
measurement_map = [
    # (mirror point suffix, outline node index, bone number)
    ('B', 0, 1),
    ('C', 1, 2),
    ('D', 2, 3),
    ('A', 3, 4),
]
outline_node_name = "nose profile outline 4"

# --- Helper Function ---
def create_linear_measurement(name, start_point, end_point, color):
    old_node = slicer.mrmlScene.GetFirstNodeByName(name)
    if old_node: slicer.mrmlScene.RemoveNode(old_node)
    line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    line_node.AddControlPoint(start_point)
    line_node.AddControlPoint(end_point)
    display_node = line_node.GetDisplayNode()
    display_node.SetSelectedColor(color)
    display_node.SetColor(color)

# --- Execution ---
outline_node = slicer.util.getNode(outline_node_name)
if not outline_node:
    slicer.util.errorDisplay(f"Error: Outline node '{outline_node_name}' not found.")
    raise ValueError("Outline node not found.")

for suffix, outline_idx, bone_num in measurement_map:
    # Get required nodes
    mirror_node = slicer.util.getNode(f'mirrorB_{suffix}')
    bone_node = slicer.util.getNode(f'bone{bone_num}')
    
    if not all([mirror_node, bone_node]):
        print(f"Warning: Skipping measurements for set {suffix} due to missing nodes.")
        continue
    
    # Get positions
    mirror_pos = np.zeros(3)
    mirror_node.GetNthControlPointPosition(0, mirror_pos)
    
    bone_pos = np.zeros(3)
    bone_node.GetNthControlPointPosition(0, bone_pos)
    
    outline_pos = np.zeros(3)
    outline_node.GetNthControlPointPosition(outline_idx, outline_pos)
    
    # Create measurements
    create_linear_measurement(f"noseprofiletoB{bone_num}", mirror_pos, outline_pos, orange)
    create_linear_measurement(f"nasalbonetoB{bone_num}", mirror_pos, bone_pos, lilac)
    print(f"Created measurements for set {bone_num}.")
```

<img src="https://github.com/user-attachments/assets/65e998fb-4b37-42d6-82a2-7d67b4634df5" width="500">

</details>

<details>

<summary>Code for 5-plane inside-outside mirror point</summary>

``` python
###   5 planes - inside-outside mirror point
import slicer
import numpy as np

# --- Configuration ---
orange = (1.0, 0.5, 0.0)
lilac = (0.78, 0.64, 0.78)
measurement_map = [
    # (mirror point suffix, outline node index, bone number)
    ('B', 0, 1),
    ('C', 1, 2),
    ('D', 2, 3),
    ('E', 3, 4),
    ('A', 4, 5),
]
outline_node_name = "nose profile outline 5"

# --- Helper Function ---
def create_linear_measurement(name, start_point, end_point, color):
    old_node = slicer.mrmlScene.GetFirstNodeByName(name)
    if old_node: slicer.mrmlScene.RemoveNode(old_node)
    line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    line_node.AddControlPoint(start_point)
    line_node.AddControlPoint(end_point)
    display_node = line_node.GetDisplayNode()
    display_node.SetSelectedColor(color)
    display_node.SetColor(color)

# --- Execution ---
outline_node = slicer.util.getNode(outline_node_name)
if not outline_node:
    slicer.util.errorDisplay(f"Error: Outline node '{outline_node_name}' not found.")
    raise ValueError("Outline node not found.")

for suffix, outline_idx, bone_num in measurement_map:
    # Get required nodes
    mirror_node = slicer.util.getNode(f'mirrorB_{suffix}')
    bone_node = slicer.util.getNode(f'bone{bone_num}')
    
    if not all([mirror_node, bone_node]):
        print(f"Warning: Skipping measurements for set {suffix} due to missing nodes.")
        continue
    
    # Get positions
    mirror_pos = np.zeros(3)
    mirror_node.GetNthControlPointPosition(0, mirror_pos)
    
    bone_pos = np.zeros(3)
    bone_node.GetNthControlPointPosition(0, bone_pos)
    
    outline_pos = np.zeros(3)
    outline_node.GetNthControlPointPosition(outline_idx, outline_pos)
    
    # Create measurements
    create_linear_measurement(f"noseprofiletoB{bone_num}", mirror_pos, outline_pos, orange)
    create_linear_measurement(f"nasalbonetoB{bone_num}", mirror_pos, bone_pos, lilac)
    print(f"Created measurements for set {bone_num}.")
```

<img src="https://github.com/user-attachments/assets/ae87c073-2b4d-45e5-82cd-149c02cfdf86" width="500">

</details>

<details>

<summary>Code for 6-plane inside-outside mirror point</summary>

``` python
###    6 planes - inside-outside mirror point
import slicer
import numpy as np

# --- Configuration ---
orange = (1.0, 0.5, 0.0)
lilac = (0.78, 0.64, 0.78)
measurement_map = [
    # (mirror point suffix, outline node index, bone number)
    ('B', 0, 1),
    ('C', 1, 2),
    ('D', 2, 3),
    ('E', 3, 4),
    ('F', 4, 5),
    ('A', 5, 6),
]
outline_node_name = "nose profile outline 6"

# --- Helper Function ---
def create_linear_measurement(name, start_point, end_point, color):
    old_node = slicer.mrmlScene.GetFirstNodeByName(name)
    if old_node: slicer.mrmlScene.RemoveNode(old_node)
    line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    line_node.AddControlPoint(start_point)
    line_node.AddControlPoint(end_point)
    display_node = line_node.GetDisplayNode()
    display_node.SetSelectedColor(color)
    display_node.SetColor(color)

# --- Execution ---
outline_node = slicer.util.getNode(outline_node_name)
if not outline_node:
    slicer.util.errorDisplay(f"Error: Outline node '{outline_node_name}' not found.")
    raise ValueError("Outline node not found.")

for suffix, outline_idx, bone_num in measurement_map:
    # Get required nodes
    mirror_node = slicer.util.getNode(f'mirrorB_{suffix}')
    bone_node = slicer.util.getNode(f'bone{bone_num}')
    
    if not all([mirror_node, bone_node]):
        print(f"Warning: Skipping measurements for set {suffix} due to missing nodes.")
        continue
    
    # Get positions
    mirror_pos = np.zeros(3)
    mirror_node.GetNthControlPointPosition(0, mirror_pos)
    
    bone_pos = np.zeros(3)
    bone_node.GetNthControlPointPosition(0, bone_pos)
    
    outline_pos = np.zeros(3)
    outline_node.GetNthControlPointPosition(outline_idx, outline_pos)
    
    # Create measurements
    create_linear_measurement(f"noseprofiletoB{bone_num}", mirror_pos, outline_pos, orange)
    create_linear_measurement(f"nasalbonetoB{bone_num}", mirror_pos, bone_pos, lilac)
    print(f"Created measurements for set {bone_num}.")
```

<img src="https://github.com/user-attachments/assets/d64193b0-5db8-4416-94ae-c8e731a9772f" width="500">

</details>


### Output
To copy all the linear measurements to clipboard, use the method described in [this guide](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/004_Copying%20measurements%20to%20Clipboard.md). 
To make sense of the output, keep in mind that the guideline method allows for testing whether Line A and B are true mirror planes (ascertain whether the inside and outside is significantly different) and test its predictive ability with or without soft tissue measurements (facial soft tissue thickness) of your choice to add on for the “noseprofiletoB1/2/3/4” measurements anteriorly (be careful about pairing landmarks! - the original paper simply states "(a little more than 2 mm) was added").  Optionally, you can see if the 4/5 or 6 plane methods predict nasal shape better. 

<details>

<summary>Output for 4 planes with optional Line A measurements</summary>

| Unknown             | Parameter               | Value                   |
|---------------------|-------------------------|-------------------------|
| (unknown)           | maximum nasal width MAW | 34.065879845058085      |
| (unknown)           | INB_A                   | 2000.0                  |
| (unknown)           | INB_B                   | 2000.0000000000002      |
| (unknown)           | INB_C                   | 2000.0000000000005      |
| (unknown)           | INB_D                   | 2000.0000000000005      |
| (unknown)           | Line_A                  | 62.419688580150364      |
| (unknown)           | Line_B                  | 124.83937716030069      |
| (unknown)           | nasal outline1          | 24.366736158161636      |
| (unknown)           | nasal outline2          | 26.81613067797216       |
| (unknown)           | nasal outline3          | 27.80868537156018       |
| (unknown)           | nasal outline4          | 17.38024525644104       |
| (unknown)           | noseprofiletoB1         | 5.525673779566004       |
| (unknown)           | noseprofiletoB2         | 9.902626067446901       |
| (unknown)           | noseprofiletoB3         | 16.137793993929815      |
| (unknown)           | noseprofiletoB4         | 17.09598625672042       |
| (unknown)           | nasalbonetoB1           | 15.780117253842183      |
| (unknown)           | nasalbonetoB2           | 16.49542889900834       |
| (unknown)           | nasalbonetoB3           | 20.14246273809071       |
| (unknown)           | nasalbonetoB4           | 17.749331272230933      |


</details>

<details>

<summary>Output for 5 planes with optional Line A measurements</summary>

| Unknown   | Parameter               | Value                   |
|-----------|-------------------------|-------------------------|
| (unknown) | maximum nasal width MAW | 34.065879845058085      |
| (unknown) | INB_A                   | 2000.0                  |
| (unknown) | INB_B                   | 2000.0000000000002      |
| (unknown) | INB_C                   | 2000.0000000000005      |
| (unknown) | INB_D                   | 2000.0000000000005      |
| (unknown) | INB_E                   | 2000.0                  |
| (unknown) | Line_A                  | 62.419688580150364      |
| (unknown) | Line_B                  | 124.83937716030074      |
| (unknown) | nasal outline1          | 23.09624385966932       |
| (unknown) | nasal outline2          | 24.00250437441322       |
| (unknown) | nasal outline3          | 26.580511864794236      |
| (unknown) | nasal outline4          | 26.84200917751933       |
| (unknown) | nasal outline5          | 18.885324552925304      |
| (unknown) | noseprofiletoB1         | 4.77413457704267        |
| (unknown) | noseprofiletoB2         | 7.7728775719345204      |
| (unknown) | noseprofiletoB3         | 12.299803347006584      |
| (unknown) | noseprofiletoB4         | 16.577556239891496      |
| (unknown) | noseprofiletoB5         | 16.893884167296918      |
| (unknown) | nasalbonetoB1           | 15.669179694093904      |
| (unknown) | nasalbonetoB2           | 14.209577753877143      |
| (unknown) | nasalbonetoB3           | 17.574859858633058      |
| (unknown) | nasalbonetoB4           | 20.19372441866758       |
| (unknown) | nasalbonetoB5           | 18.50970755626509       |

</details>

<details>

<summary>Output for 6 planes with optional Line A measurements</summary>

| Unknown   | Parameter               | Value                   |
|-----------|-------------------------|-------------------------|
| (unknown) | maximum nasal width MAW | 34.065879845058085      |
| (unknown) | INB_A                   | 2000.0                  |
| (unknown) | INB_B                   | 2000.0000000000002      |
| (unknown) | INB_C                   | 2000.0000000000002      |
| (unknown) | INB_D                   | 2000.0000000000005      |
| (unknown) | INB_E                   | 2000.0000000000002      |
| (unknown) | INB_F                   | 2000.0                  |
| (unknown) | Line_A                  | 62.419688580150364      |
| (unknown) | Line_B                  | 124.83937716030076      |
| (unknown) | nasal outline1          | 22.560548604784675      |
| (unknown) | nasal outline2          | 24.27440147938001       |
| (unknown) | nasal outline3          | 26.689979253823722      |
| (unknown) | nasal outline4          | 24.491972756379866      |
| (unknown) | nasal outline5          | 26.589433476120288      |
| (unknown) | nasal outline6          | 21.438268607642662      |
| (unknown) | noseprofiletoB1         | 4.3806753382390555      |
| (unknown) | noseprofiletoB2         | 6.863999026673066       |
| (unknown) | noseprofiletoB3         | 10.403738313217593      |
| (unknown) | noseprofiletoB4         | 14.525122003267612      |
| (unknown) | noseprofiletoB5         | 17.048739616886586      |
| (unknown) | noseprofiletoB6         | 16.869754556328157      |
| (unknown) | nasalbonetoB1           | 15.844204074180183      |
| (unknown) | nasalbonetoB2           | 14.607928382721507      |
| (unknown) | nasalbonetoB3           | 16.55600629779354       |
| (unknown) | nasalbonetoB4           | 17.59277552761434       |
| (unknown) | nasalbonetoB5           | 20.59955288417588       |
| (unknown) | nasalbonetoB6           | 19.449551948971035      |

</details>

> [!IMPORTANT]
> INB_A, INB_B, INB_C, INB_D, INB_E, INB_F and Line_A, Line_B are NOT true measurements. They provide guide (Line_A and Line_B); or are programmed to be elongated to 20 cm (INB_A, etc) - DO NOT use them as measurements in your data analysis! Exercise caution with the "nasal outline1..." measurements as these are specific to the bony nose outlet and there are no comparable measurements for the soft nose. 

### Extra codes for more ideas

> [!IMPORTANT]
> Run these BEFORE you copy all linear measurements to clipboard if you want to implement them. The "pred soft nose outline" measurements should be identical to the "nasalbonetoB" measurements.

If the mirror plane idea has piqued your interest, there is a way to measure the difference (prediction error) between the actual nasal outline points and the predicted nasal outline points. This method assumes `Line_B` is the mirror plane and the `nasalbonetoB` lines represent the distances from the mirror to the bony outline.

This script creates:
1.  A predicted soft tissue outline (`pred soft nose outline`) in **deep purple**, where each line starts from a mirror point and has the same length as the corresponding `nasalbonetoB` line.
2.  A prediction error line (`pred error`) in **burgundy**, connecting the actual soft tissue point to the predicted soft tissue point.

<details>

<summary>Extra error code for 4-plane</summary>

```python
### EXTRA: Prediction error visualization (4 planes, MSP/INB compatible) ###
import slicer
import numpy as np

# --- Configuration ---
# This script will find lines with either 'MSP_' or 'INB_' prefix.
line_prefix_priority = ['MSP', 'INB']
# This defines the mapping between the different line sets.
# Format: (nasalbonetoB_#, noseprofiletoB_#, mirrorB_suffix, sag_line_suffix)
# Note the non-sequential mapping.
line_mappings = [
    ('nasalbonetoB1', 'noseprofiletoB1', 'B', 'B'),
    ('nasalbonetoB2', 'noseprofiletoB2', 'C', 'C'),
    ('nasalbonetoB3', 'noseprofiletoB3', 'D', 'D'),
    ('nasalbonetoB4', 'noseprofiletoB4', 'A', 'A'),
]
# Define colors
deep_purple = (0.29, 0.0, 0.51)
burgundy = (0.5, 0.0, 0.13)

# --- Helper Functions ---
def get_line_points(line_node):
    if not line_node or line_node.GetNumberOfControlPoints() < 2: return None
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return [p1, p2]

def calculate_length(line_node):
    points = get_line_points(line_node)
    if not points: return 0
    return np.linalg.norm(points[1] - points[0])

def create_line(name, p1, p2, color):
    """Creates or updates a line node."""
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if not node:
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    node.RemoveAllControlPoints()
    node.AddControlPoint(p1)
    node.AddControlPoint(p2)
    display_node = node.GetDisplayNode()
    if display_node:
        display_node.SetSelectedColor(color)
        display_node.SetColor(color)
    return node

# --- Main Script ---

# 1. Determine which prefix is used for sagittal lines ('MSP_' or 'INB_')
found_prefix = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{line_mappings[0][3]}"):
        found_prefix = prefix
        print(f"Found sagittal intersection lines with prefix: '{found_prefix}_'")
        break
if not found_prefix:
    slicer.util.errorDisplay("Error: Could not find any sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

# 2. Process each set of corresponding lines
for i, (nb_name, np_name, mb_suffix, sag_suffix) in enumerate(line_mappings, 1):
    
    # Get all required nodes for this iteration
    nasalbonetoB_node = slicer.util.getNode(nb_name)
    noseprofiletoB_node = slicer.util.getNode(np_name)
    mirrorB_node = slicer.util.getNode(f'mirrorB_{mb_suffix}')
    sag_line_node = slicer.util.getNode(f'{found_prefix}_{sag_suffix}')

    if not all([nasalbonetoB_node, noseprofiletoB_node, mirrorB_node, sag_line_node]):
        print(f"Warning: Skipping set {i}, one or more required nodes are missing.")
        continue

    # A. Create the predicted soft tissue outline (purple line)
    length = calculate_length(nasalbonetoB_node)
    sag_line_points = get_line_points(sag_line_node)
    direction = (sag_line_points[1] - sag_line_points[0]) / np.linalg.norm(sag_line_points[1] - sag_line_points[0])
    
    start_point = np.zeros(3)
    mirrorB_node.GetNthControlPointPosition(0, start_point)
    predicted_end_point = start_point + direction * length
    
    pred_line_name = f"pred soft nose outline{i}"
    predicted_line = create_line(pred_line_name, start_point, predicted_end_point, deep_purple)
    print(f"Created '{pred_line_name}'.")

    # B. Create the prediction error line (burgundy line)
    actual_end_point = get_line_points(noseprofiletoB_node)[1]
    error_line_name = f"pred error{i}"
    create_line(error_line_name, actual_end_point, predicted_end_point, burgundy)
    print(f"Created '{error_line_name}'.")

```

</details>

<details>

<summary>Extra error code for 5-plane</summary>

```python
### EXTRA: Prediction error visualization (5 planes, MSP/INB compatible) ###
import slicer
import numpy as np

# --- Configuration ---
# This script will find lines with either 'MSP_' or 'INB_' prefix.
line_prefix_priority = ['MSP', 'INB']
# This defines the mapping between the different line sets.
line_mappings = [
    ('nasalbonetoB1', 'noseprofiletoB1', 'B', 'B'),
    ('nasalbonetoB2', 'noseprofiletoB2', 'C', 'C'),
    ('nasalbonetoB3', 'noseprofiletoB3', 'D', 'D'),
    ('nasalbonetoB4', 'noseprofiletoB4', 'E', 'E'),
    ('nasalbonetoB5', 'noseprofiletoB5', 'A', 'A'),
]
# Define colors
deep_purple = (0.29, 0.0, 0.51)
burgundy = (0.5, 0.0, 0.13)

# --- Helper Functions ---
def get_line_points(line_node):
    if not line_node or line_node.GetNumberOfControlPoints() < 2: return None
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return [p1, p2]

def calculate_length(line_node):
    points = get_line_points(line_node)
    if not points: return 0
    return np.linalg.norm(points[1] - points[0])

def create_line(name, p1, p2, color):
    """Creates or updates a line node."""
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if not node:
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    node.RemoveAllControlPoints()
    node.AddControlPoint(p1)
    node.AddControlPoint(p2)
    display_node = node.GetDisplayNode()
    if display_node:
        display_node.SetSelectedColor(color)
        display_node.SetColor(color)
    return node

# --- Main Script ---

# 1. Determine which prefix is used for sagittal lines ('MSP_' or 'INB_')
found_prefix = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{line_mappings[0][3]}"):
        found_prefix = prefix
        print(f"Found sagittal intersection lines with prefix: '{found_prefix}_'")
        break
if not found_prefix:
    slicer.util.errorDisplay("Error: Could not find any sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

# 2. Process each set of corresponding lines
for i, (nb_name, np_name, mb_suffix, sag_suffix) in enumerate(line_mappings, 1):
    
    # Get all required nodes for this iteration
    nasalbonetoB_node = slicer.util.getNode(nb_name)
    noseprofiletoB_node = slicer.util.getNode(np_name)
    mirrorB_node = slicer.util.getNode(f'mirrorB_{mb_suffix}')
    sag_line_node = slicer.util.getNode(f'{found_prefix}_{sag_suffix}')

    if not all([nasalbonetoB_node, noseprofiletoB_node, mirrorB_node, sag_line_node]):
        print(f"Warning: Skipping set {i}, one or more required nodes are missing.")
        continue

    # A. Create the predicted soft tissue outline (purple line)
    length = calculate_length(nasalbonetoB_node)
    sag_line_points = get_line_points(sag_line_node)
    direction = (sag_line_points[1] - sag_line_points[0]) / np.linalg.norm(sag_line_points[1] - sag_line_points[0])
    
    start_point = np.zeros(3)
    mirrorB_node.GetNthControlPointPosition(0, start_point)
    predicted_end_point = start_point + direction * length
    
    pred_line_name = f"pred soft nose outline{i}"
    predicted_line = create_line(pred_line_name, start_point, predicted_end_point, deep_purple)
    print(f"Created '{pred_line_name}'.")

    # B. Create the prediction error line (burgundy line)
    actual_end_point = get_line_points(noseprofiletoB_node)[1]
    error_line_name = f"pred error{i}"
    create_line(error_line_name, actual_end_point, predicted_end_point, burgundy)
    print(f"Created '{error_line_name}'.")
```

</details>

<details>

<summary>Extra error code for 6-plane</summary>

```python
### EXTRA: Prediction error visualization (6 planes, MSP/INB compatible) ###
import slicer
import numpy as np

# --- Configuration ---
# This script will find lines with either 'MSP_' or 'INB_' prefix.
line_prefix_priority = ['MSP', 'INB']
# This defines the mapping between the different line sets.
line_mappings = [
    ('nasalbonetoB1', 'noseprofiletoB1', 'B', 'B'),
    ('nasalbonetoB2', 'noseprofiletoB2', 'C', 'C'),
    ('nasalbonetoB3', 'noseprofiletoB3', 'D', 'D'),
    ('nasalbonetoB4', 'noseprofiletoB4', 'E', 'E'),
    ('nasalbonetoB5', 'noseprofiletoB5', 'F', 'F'),
    ('nasalbonetoB6', 'noseprofiletoB6', 'A', 'A'),
]
# Define colors
deep_purple = (0.29, 0.0, 0.51)
burgundy = (0.5, 0.0, 0.13)

# --- Helper Functions ---
def get_line_points(line_node):
    if not line_node or line_node.GetNumberOfControlPoints() < 2: return None
    p1, p2 = np.zeros(3), np.zeros(3)
    line_node.GetNthControlPointPosition(0, p1)
    line_node.GetNthControlPointPosition(1, p2)
    return [p1, p2]

def calculate_length(line_node):
    points = get_line_points(line_node)
    if not points: return 0
    return np.linalg.norm(points[1] - points[0])

def create_line(name, p1, p2, color):
    """Creates or updates a line node."""
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if not node:
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', name)
    node.RemoveAllControlPoints()
    node.AddControlPoint(p1)
    node.AddControlPoint(p2)
    display_node = node.GetDisplayNode()
    if display_node:
        display_node.SetSelectedColor(color)
        display_node.SetColor(color)
    return node

# --- Main Script ---

# 1. Determine which prefix is used for sagittal lines ('MSP_' or 'INB_')
found_prefix = None
for prefix in line_prefix_priority:
    if slicer.mrmlScene.GetFirstNodeByName(f"{prefix}_{line_mappings[0][3]}"):
        found_prefix = prefix
        print(f"Found sagittal intersection lines with prefix: '{found_prefix}_'")
        break
if not found_prefix:
    slicer.util.errorDisplay("Error: Could not find any sagittal intersection lines (e.g., 'MSP_A' or 'INB_A').")
    raise ValueError("Sagittal lines not found.")

# 2. Process each set of corresponding lines
for i, (nb_name, np_name, mb_suffix, sag_suffix) in enumerate(line_mappings, 1):
    
    # Get all required nodes for this iteration
    nasalbonetoB_node = slicer.util.getNode(nb_name)
    noseprofiletoB_node = slicer.util.getNode(np_name)
    mirrorB_node = slicer.util.getNode(f'mirrorB_{mb_suffix}')
    sag_line_node = slicer.util.getNode(f'{found_prefix}_{sag_suffix}')

    if not all([nasalbonetoB_node, noseprofiletoB_node, mirrorB_node, sag_line_node]):
        print(f"Warning: Skipping set {i}, one or more required nodes are missing.")
        continue

    # A. Create the predicted soft tissue outline (purple line)
    length = calculate_length(nasalbonetoB_node)
    sag_line_points = get_line_points(sag_line_node)
    direction = (sag_line_points[1] - sag_line_points[0]) / np.linalg.norm(sag_line_points[1] - sag_line_points[0])
    
    start_point = np.zeros(3)
    mirrorB_node.GetNthControlPointPosition(0, start_point)
    predicted_end_point = start_point + direction * length
    
    pred_line_name = f"pred soft nose outline{i}"
    predicted_line = create_line(pred_line_name, start_point, predicted_end_point, deep_purple)
    print(f"Created '{pred_line_name}'.")

    # B. Create the prediction error line (burgundy line)
    actual_end_point = get_line_points(noseprofiletoB_node)[1]
    error_line_name = f"pred error{i}"
    create_line(error_line_name, actual_end_point, predicted_end_point, burgundy)
    print(f"Created '{error_line_name}'.")
```

</details>


## Bibliography

[^1]: [Slicer Script Repository](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html)
[^2]: (https://archives.fbi.gov/archives/about-us/lab/forensic-science-communications/fsc/jan2002/prokopec.htm)
[^3]: Rynn, C., Wilkinson, C.M. & Peters, H.L. (2010) "Prediction of nasal morphology from the skull." Forensic Sci Med Pathol 6, 20–34. https://doi.org/10.1007/s12024-009-9124-6
[^4]: Rynn, C. and C. M. Wilkinson (2006). "Appraisal of traditional and recently proposed relationships between the hard and soft dimensions of the nose in profile." American Journal of Physical Anthropology: The Official Publication of the American Association of Physical Anthropologists 130(3): 364-373.
[^5]: Rynn, C., et al. (2012). Relationships between the skull and face. Craniofacial identification. C. W. C. Rynn. Cambridge, Cambridge University Press: 193-202.
[^6]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." Int J Legal Med 130(3): 863-879.
