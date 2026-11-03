# The Two Tangent Method by Gerasimow, 1955[^2], its revision by Maltais-Lapointe (2016)[^14] based on Ullrich and Stephan (2011)[^7]
# Table of Contents

1.  [Literature context](#literature-context)
    *   [Summary](#summary)
    *   [Landmarks in this guide (for both methods)](#landmarks-in-this-guide-for-both-methods)
    *   [Illustration of the landmarks](#illustration-of-the-landmarks)
    *   [Profile plane](#profile-plane)
    *   [Segmentation](#segmentation)
    *   [Profile view model](#profile-view-model)
    *   [Establishing the tangents (Gerasimow)](#establishing-the-tangents-gerasimow)
    *   [Elongating the tangents](#elongating-the-tangents)
    *   [Error rates](#error-rates)
2.  [Maltais-Lapointe (2016)'s method](#maltais-lapointe-2016s-method)
    *   [Outputs](#outputs)
        *   [Tangents1 and 2 with error](#tangents1-and-2-with-error)
        *   [Tangents1,2,3,4 with error to pronasale and R2](#tangents1234-with-error-to-pronasale-and-r2)
3.  [Bibliography](#bibliography)

## Literature context

Limitations occur in describing this method in detail as his works are available in English only partially, these are (i) the published translations from German (Gerassimow, 1968[^3]; Gerasimov, 1971[^4]) and the (ii) unpublished Tshernezky translation later used for the development of the Manchester protocol (Wilkinson, 2004[^5]; Stephan and Ullrich, 2011[^6]; Stephan and Ullrich, 2015[^7]). 

The summarised theory is that the tip of the soft nose (pronasale) can be predicted by where two tangents meet: (a) the tangent running between the nasion to rhinion OR the line following the bony nose shape in profile view and (b) the tangent aligning with the anterior 1/3rd of the nasal spine OR following its direction as an arrow.

The method followed here will split into two: the first will be called  **Gerasimow** which is the one described by Gatliff (1984)[^8], as the interpretation by Stephan (2003)[^9] was later scrutinised by Rynn and Wilkinson (2006)[^10] and Rynn et al. (2012)[^11]; meanwhile the second will be called as the **Maltais-Lapointe** incorporating their whole study which includes the original Gerasimow and the later interpretation (Ullrich and Stephan, 2011) in one[^7]. 

### Summary

1. [Establish the profile plane](#profile-plane) which serves as the reference plane for generating a standardized profile view.
2. Prepare the CT scan by either:
   - [Cutting the Bone Segmentation](#profile-view-model) along the INB plane, or
   - Using the [Opacity toggle](#maltais-lapointe-2016s-method) to create a clear view.
3. [Draw or programmatically create two (or four) tangents](#establishing-the-tangents), ensuring they are aligned with the INB plane. Then, [elongate the tangents](#elongating-the-tangents) to find their intersection points.
4. Optionally, connect the predicted nose tip (pronasale) and the actual nose tip to calculate the [error rate](#error-rate). Alternatively, compare the coordinate positions of the two points.


### Landmarks in this guide (for both methods): 

| Position in code | Position in file | Name in file | Landmark name | Definition                                                                                                                     | Defined by            |
|------------------|------------------|--------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 0                | 1                | nasion       | nasion        | Intersection of the nasofrontal sutures in the median plane                                                                    |  Caple and Stephan 2016[^11]      |
| 1                | 2                | inion        | inion         | Median point between the apices of the superior nuchal lines and at the base of the external occipital protuberance (not the tip of the protuberance) |  Caple and Stephan 2016[^11]      |
| 2                | 3                | bregma       | bregma        | Where the sagittal and coronal sutures meet. Impossible to determine in juvenile skulls with anterior fontanelle, or with complete suture obliteration |  Caple and Stephan 2016[^11]      |
| 3                | 4                | rhinion      | rhinion       | Most rostral (end) point on the internasal suture.                                                                            |  Caple and Stephan 2016[^11]     |
| 4                | 5                | acanthion    | acanthion     | Most anterior tip of the anterior nasal spine                                                                                 |  Caple and Stephan 2016[^11]      |
| 5                | 6                | pronasale    | pronasale     | The most anteriorly protruded point of the apex nasi. In the case of a bifid nose, the more protruding tip is chosen           | Caple and Stephan 2016[^11]|
| 6                | 7                | Reference point 2    | R2     |The point where the T4 crosses the surface of the nasal soft tissue on the midsagittal plane      | Maltais Lapointe 2016[^14]|

[Gerasimow_landmarks.mrk.json](https://github.com/user-attachments/files/28797197/Gerasimow_landmarks.mrk.json)


> [!WARNING]
> Please note that the tutorial shown the "PreDentalSurgery" CT for demonstration purposes only - in research, CTs with all visible features and without any facial operation would be included. 

### Illustration of the landmarks 

Credit to Tinotenda Chiyangwa©[^15] 

**Hard tissue**

<img src="https://github.com/user-attachments/assets/4c362d65-6be0-49b9-b268-0ed03cff575e" width="500">


**Soft tissue**

<img src="https://github.com/user-attachments/assets/b2d06592-d461-469c-b206-92e52b8d4850" width="500">



> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan has to be re-aligned in the FHP
- [ ] You should have a Bone and Skin model via segmentation (explained later) 
- [ ] If you are following the Maltais-Lapointe[^14] guidance as well, make sure you replicate their Hounsfield Units:
[Maltais-Lapointe guidance](#maltais-lapointe-guidance)

| Tissue/structure | HU min | HU max | 
|------------------|------------------|--------------|
| soft tissue          | -700     | 225       | 
| skull               | 226         |3071 (or maximum available)       |


If you want to see how the code snippets individually build up these two methods, please read on.
If you rather employ a graphic user interface, copy and paste the contents of this [link:](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/19d56a56ac868fd39836058d551f5d054fe5bf53/Nose%20predictions/GerasimowMaltaisLapointe%20GUI.md)  into the python console. 


### Profile plane

To help with the side profile, we will establish either MSP or INB plane, depending on landmark availability. 

“INB” plane as defined by Rynn et al., 2010[^10].: A midsagittal plane (INB) which bisected the inion, nasion, and bregma.


“MSP” plane  defined by any landmarks described as midline: nasion, acanthion and rhinion

Download the markups file for this method: 
[Gerasimow_landmarks.mrk.json](https://github.com/user-attachments/files/28797197/Gerasimow_landmarks.mrk.json)
 Then choose the plane you can create based on landmarks that can be placed on the skull you work with, allocate the  landmarks and copy and paste the following code:the code snippet of your choosing. 

The codes use a centroid origin, calculated from the landmarks that weights all plane-defining landmarks equally and  normal vector based on the same landmarks. 

<details>
<summary>Code for INB</summary>

```python
#INB plane#

import numpy as np
import slicer

# Get the points from the "Gerasimow_landmarks" node
hardTissueNode = slicer.util. getNode('Gerasimow_landmarks')
nasion = np.array(hardTissueNode.GetNthControlPointPosition(0))    # point1: nasion
inion = np.array(hardTissueNode.GetNthControlPointPosition(1))     # point2: inion
bregma = np.array(hardTissueNode.GetNthControlPointPosition(2))    # point3: bregma

# Calculate the centroid (average of the three points)
centroid = (nasion + inion + bregma) / 3.0

# Calculate the normal of the plane defined by the three points
v1 = inion - nasion
v2 = bregma - nasion
planeNormal = np.cross(v1, v2)
planeNormal = planeNormal / np.linalg.norm(planeNormal)  # Normalize the normal vector

# Create a new plane node
newPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'INB')

# Set the origin of the new plane to the centroid
newPlaneNode.SetOrigin(centroid)

# Set the normal of the new plane
newPlaneNode.SetNormal(planeNormal)
```
</details>


If using the nasion, acanthion and rhinion landmarks, use this snippet: 

<details>
<summary>Code for MSP</summary>

```python
	#MSP plane#

import numpy as np
import slicer

#Get the points from the "Gerasimow_landmarks" node
hardTissueNode = slicer.util.getNode('Gerasimow_landmarks')
nasion = np.array(hardTissueNode.GetNthControlPointPosition(0))
acanthion = np.array(hardTissueNode.GetNthControlPointPosition(4))
rhinion = np.array(hardTissueNode.GetNthControlPointPosition(3))

#Calculate the centroid (average of the three points)
centroid = (nasion + acanthion + rhinion) / 3.0

#Calculate the normal of the plane
v1 = acanthion - nasion
v2 = rhinion - nasion
planeNormal = np.cross(v1, v2)
planeNormal = planeNormal / np.linalg.norm(planeNormal)

#Create plane with origin at centroid
newPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP')
newPlaneNode.SetOrigin(centroid)
newPlaneNode.SetNormal(planeNormal)
```

</details>


<img src="https://github.com/user-attachments/assets/77eaf9ee-b9a5-46ab-94cf-3bdd313f6985" width="500">
View after landmarks are allocated correctly.

<img src="https://github.com/user-attachments/assets/b440186b-cfee-4093-bc24-300a49dc82b4" width="500">
The generated INB plane view.

<img src="https://github.com/user-attachments/assets/35c3dcc1-8133-4bd2-878b-d4ba322fa7d8" width="500">
INB extended via the toggles (dots).


### Segmentation
[link to step-by-step](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/003_Roi%20vs%20Segmentation.md)

You can hide all of these and keep only the models if you wish.

In case still need the red/green/yellow slice windows for precise landmark placement, keep only the original volume node (PreDentalSurgery in the example) and the models visible. 


### Profile view model

For the T2 (tangent following the direction of the anterior nasal spine) both in original Gerasimow and the following Maltais-LaPointe method, a profile view (of the Bone model cut along the profile plane) will be useful. 

<details>
<summary>Profile view model intructions</summary>
To open the appropriate module, click on the magnifying glass icon next to the modules: 

<img src="https://github.com/user-attachments/assets/08aeb820-240a-4cfd-a9c7-01d017c09c36" width="500">

And start typing “dynamic modeller” in the search bar.
<img src="https://github.com/user-attachments/assets/c9dfd153-3c8b-4e99-82a2-8ed83320aec7" width="500">
Click “Switch to Module” to open. 

You’ll see this menu on the left side of the screen: 
<img src="https://github.com/user-attachments/assets/035ea262-8235-4665-8c4d-c3df49945944" width="500">
The "INB” is established in the environment. To cut the model along this plane (technically cutting it in 2 and choosing which side to keep), choose the first button (Plane Cut).

> [!IMPORTANT]
> On the example screenshots, the "full model" is named "Skin-cropped" and "Bone-cropped" - this is because the example Brain CT still had the headrest in the segmentation as an artefact, so I removed that

Make sure you create your cut model with the settings on the screenshot to cut the Bone model at the INB Plane: 

- [ ] Make sure the source volume is the full model of the Bone
- [ ] Choose INB as the plane node
- [ ]  Operation type should be **Intersection**
- [ ]  You MUST chose the **Create new model as...** from the drop-down menu and type in the custom name with the **bone** prefix - otherwise you'll override your existing models
- [ ] DO NOT FORGET TO CLICK APPLY



- [ ] Check if this was executed by finding your 2 new models under the "Models" module
<img src="https://github.com/user-attachments/assets/e4fc0f15-acfe-41d4-854c-354188e4f7b0" width="500">
With these settings, the Model list will be the following: 
<img src="https://github.com/user-attachments/assets/2e2fcaab-2716-49e4-a3e7-c34bc4df30bd" width="500">


And you should have the following individual views (excluding/hiding the original full models for demonstration purposes):
<img src="https://github.com/user-attachments/assets/4de15a97-9b76-4fb7-94b1-294d7eaaab35" width="500">

You can now allocate the remainder of the landmarks on either model - they should appear on ALL of them. 
</details>

### Establishing the tangents (Gerasimow)
If you want to do this by hand, you can follow the steps below. 
Alternatively, you can use the [GUI](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/19d56a56ac868fd39836058d551f5d054fe5bf53/Nose%20predictions/GerasimowMaltaisLapointe%20GUI.md). Just copy-paste the code into the Python Console in Slicer and amke sure you tick the box saying **Use T1-T2 Shortcut**. 

If you want to just re-create Gerasimow's method by hand, follow the steps creating tangent1 and tangent2, with the adjusting codes. 

Re-orient the view of either your left-bone model to see its right side OR your right-bone model to see its left side to look inside the cranium: 

You'll have to establish the two tangents by hand
For the  the first tangent: 
1) Draw a line by hand via “Markups”>”+Line” along the anterior 1/3rd of the nasal bones in side profile view and name it “tangent1” by double clicking on the name.
<img src="https://github.com/user-attachments/assets/3bc8fbe5-4b0c-4ce9-b81f-bcb866b60e63" width="500">

2) Then draw a second line in the general direction of where the acanthion is pointing (like an arrow) and name it “tangent2”. Do not worry if it is slanted drastically to the opposite side – the next code snippet will correct that. 
![image](https://github.com/user-attachments/assets/9ac99a96-4a61-4316-ae92-27b3e44836ee)


Now, use the **tangents to profile** code that projects the lines to the INB and ensures that tangent 2 bisects the acanthion.

<details>
<summary>Code for tangents to profile</summary>

```python
###Tangents to Plane (INB or MSP)###

import slicer
import numpy as np

# Try to retrieve the plane (check for both INB and MSP)
plane = None
plane_name = ""
try:
    plane = slicer.util.getNode('INB')
    plane_name = "INB"
    print("Using INB plane")
except:
    try:
        plane = slicer.util.getNode('MSP')
        plane_name = "MSP"
        print("Using MSP plane")
    except:
        raise RuntimeError("Neither INB nor MSP plane found!  Please create one first.")

# Retrieve the point from hard tissue
hard_tissue = slicer.util.getNode('Gerasimow_landmarks')
point = hard_tissue.GetNthControlPointPosition(4)

# Function to project a point onto a plane
def project_point_onto_plane(point, plane_origin, plane_normal):
    point_vector = np.array(point) - np.array(plane_origin)
    distance = np.dot(point_vector, plane_normal)
    projected_point = np.array(point) - distance * np.array(plane_normal)
    return projected_point

# Retrieve tangent1 and tangent2
tangent1 = slicer.util. getNode('tangent1')
tangent2 = slicer.util.getNode('tangent2')

# Project tangent1 and tangent2 onto the plane
plane_origin = plane. GetOrigin()
plane_normal = plane.GetNormal()

tangent1_start = tangent1.GetNthControlPointPosition(0)
tangent1_end = tangent1.GetNthControlPointPosition(1)
tangent1_start_projected = project_point_onto_plane(tangent1_start, plane_origin, plane_normal)
tangent1_end_projected = project_point_onto_plane(tangent1_end, plane_origin, plane_normal)

tangent2_start = tangent2.GetNthControlPointPosition(0)
tangent2_end = tangent2.GetNthControlPointPosition(1)
tangent2_start_projected = project_point_onto_plane(tangent2_start, plane_origin, plane_normal)
tangent2_end_projected = project_point_onto_plane(tangent2_end, plane_origin, plane_normal)

# Update tangent1 and tangent2 with projected points
tangent1.SetNthControlPointPosition(0, *tangent1_start_projected)
tangent1.SetNthControlPointPosition(1, *tangent1_end_projected)
tangent2.SetNthControlPointPosition(0, *tangent2_start_projected)
tangent2.SetNthControlPointPosition(1, *tangent2_end_projected)

# Adjust tangent2 to bisect the point
midpoint = (np.array(tangent2_start_projected) + np.array(tangent2_end_projected)) / 2
bisect_vector = np.array(point) - midpoint
new_tangent2_end = midpoint + bisect_vector

tangent2.SetNthControlPointPosition(1, *new_tangent2_end)

print(f"Tangents projected onto {plane_name} plane and tangent2 adjusted to bisect point")
```
</details>

### Elongating the tangents
The lines are now both present but may appear very short due to the projection if you used the whole skull to allocate these tangents. Even if they look reasonably long, they probably won't meet yet. 
After this, copy and paste the script “prn pred” that elongates both tangents until they meet, creating a new node list (and node) as pred prn (predicted pronasale). 

<details>
<summary>Code to elongate tangents</summary>

```python
###prn pred###
import slicer
import numpy as np

# Function to calculate the direction vector of a line
def calculate_direction_vector(start, end):
    return np.array(end) - np.array(start)

# Function to find the intersection point of two lines
def find_intersection_point(line1_start, line1_dir, line2_start, line2_dir):
    # Solve for t1 and t2 where line1_start + t1 * line1_dir = line2_start + t2 * line2_dir
    A = np.array([line1_dir, -line2_dir]).T
    b = np.array(line2_start) - np.array(line1_start)
    t = np.linalg.lstsq(A, b, rcond=None)[0]
    intersection_point = line1_start + t[0] * line1_dir
    return intersection_point

# Retrieve tangent1 and tangent2
tangent1 = slicer.util.getNode('tangent1')
tangent2 = slicer.util.getNode('tangent2')

# Get the start and end points of tangent1 and tangent2
tangent1_start = np.array(tangent1.GetNthControlPointPosition(0))
tangent1_end = np.array(tangent1.GetNthControlPointPosition(1))
tangent2_start = np.array(tangent2.GetNthControlPointPosition(0))
tangent2_end = np.array(tangent2.GetNthControlPointPosition(1))

# Calculate the direction vectors
tangent1_dir = calculate_direction_vector(tangent1_start, tangent1_end)
tangent2_dir = calculate_direction_vector(tangent2_start, tangent2_end)

# Find the intersection point
intersection_point = find_intersection_point(tangent1_start, tangent1_dir, tangent2_start, tangent2_dir)

# Create a new markups node called "prn pred"
prn_pred = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'prn pred')
prn_pred.AddControlPoint(intersection_point)

# Extend tangent1 and tangent2 beyond the intersection point
extension_length = 10  # Adjust this value as needed

new_tangent1_end = intersection_point + extension_length * tangent1_dir / np.linalg.norm(tangent1_dir)
new_tangent2_end = intersection_point + extension_length * tangent2_dir / np.linalg.norm(tangent2_dir)

tangent1.SetNthControlPointPosition(1, *new_tangent1_end)
tangent2.SetNthControlPointPosition(1, *new_tangent2_end)

print(f"Intersection point added to 'prn pred': {intersection_point}")
print(f"New tangent1 end point: {new_tangent1_end}")
print(f"New tangent2 end point: {new_tangent2_end}")
```
</details>

### Error rates
As a research question, you can also allocate the original pronasale (included in the _Gerasimow landmarks.lmrk.json_ as the last item) and check the error rate (copy and paste the code "prn error"). 

```python
###prn error####

import slicer
import numpy as np

# Retrieve the points
hard_tissue = slicer.util.getNode('Gerasimow landmarks')
point1 = hard_tissue.GetNthControlPointPosition(5)

prn_pred = slicer.util.getNode('prn pred')
point2 = prn_pred.GetNthControlPointPosition(0)

# Create a new markups line node
line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'pred error')
line_node.AddControlPoint(point1)
line_node.AddControlPoint(point2)

# Set the color to burgundy (RGB: 128, 0, 32)
line_node.GetDisplayNode().SetSelectedColor(128/255, 0/255, 32/255)
line_node.GetDisplayNode().SetColor(128/255, 0/255, 32/255)

print(f"New line created between points: {point1} and {point2} with color burgundy")
```

To copy the error measurement, use the method described in [this guide](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/004_Copying%20measurements%20to%20Clipboard.md). 

The outputs are explained [here](#tangents1-and-2-with-error)

## Maltais-Lapointe (2016)`s method

This method does not require you to cut the model in the INB plane - but you will need the separate Bone and Skin Segmentations ready, as specified [previously](#maltais-lapointe-guidance). I found it useful to toggle the opacity of the Bone model when establishing tangent4 - you can find this in the Models module, under _Display_:

<img src="https://github.com/user-attachments/assets/e9930a26-d832-4da6-8446-ccb3d7400b50" width="500">

They established additional tangents: 
Tangent 3 (T3) follows the last 1–2 mm of the nasal bone and tangent 4 (T4) follows the direction of the nasal floor to the right of the anterior nasal spine, 
The nasal spine line is defined as the same as tangent 2.
They also introduce an additional new reference point for error rate measures; R2 is where the nasal spine line meets the soft tissue nose (R1=pronasale). 

| Tangent name | description   | name in the files  | colour in video |
|-----------|------------|-------------------|---------------|
| tangent 1  | follows the last third of the nasal bone   | tangent1 | yellow |
| tangent 2 | follows the general direction of the anterior nasal spine | tangent2 | green   |
| tangent 3  | follows the last 1–2 mm of the nasal bone   | tangent3 | lilac |
| tangent 4  | follows the direction of the nasal floor to the right of the anterior nasal spine  | tangent4 | purple |

Video showing the allocation, projection and elongation of 4 tangents.

You'll need to draw all these tangents by hand and name them "tangent1", "tangent2", "tangent3" and "tangent4" for the following code to work. You'll also need to place R2. 

https://github.com/user-attachments/assets/9d0c3401-cbd3-4846-9670-b5050c024b84 

To place the second point of reference in addition to the pronasale, make "tangent2" visible in the "Markups" module, then change into the Skin segmentation to place these landmarks found in "Gerasimow_landmarks" on both sides. In the original study, this is looked at in 2D, so is one point, but in 3D Slicer and 3D view we will take the line connecting them and where it "pierces" the INB plane. This new point will be added to the end of the pre-existing node list. Then, the created intersection points will be connected to the soft tissue pronasale and R2 to measure errors; the ones in relation to the pronasale with a deep red, while the R2 ones with a bright coral.

Alternatively, use the [GUI](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/19d56a56ac868fd39836058d551f5d054fe5bf53/Nose%20predictions/GerasimowMaltaisLapointe%20GUI.md) for programmatically established *tangent4* and *R2* based on two nasal floor lines. 

<details>
<summary>Code for tangents</summary>

```python
####Re-creating the R2 point#####
import numpy as np
import slicer

# Retrieve the "Gerasimow_landmarks" node
landmarks_node = slicer.util.getNode('Gerasimow_landmarks')

# Get the points at positions 6 and 7
point6 = np.array(landmarks_node.GetNthControlPointPosition(6))
point7 = np.array(landmarks_node.GetNthControlPointPosition(7))

# Create a new line node called "RR2-LR2"
line_node = slicer. mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'RR2-LR2')

# Set the control points of the new line
line_node.AddControlPoint(vtk.vtkVector3d(*point6))
line_node.AddControlPoint(vtk.vtkVector3d(*point7))

# Try to retrieve the plane node (check for both INB and MSP)
plane_node = None
try:
    plane_node = slicer.util.getNode('INB')
    print("Using INB plane")
except:
    try:
        plane_node = slicer.util.getNode('MSP')
        print("Using MSP plane")
    except:
        raise RuntimeError("Neither INB nor MSP plane found!  Please create one first.")

# Get the origin and normal of the plane
plane_origin = np.array(plane_node.GetOrigin())
plane_normal = np.array(plane_node.GetNormal())

# Function to find the intersection point of a line with a plane
def find_intersection_with_plane(line_start, line_end, plane_origin, plane_normal):
    line_dir = line_end - line_start
    t = np.dot(plane_origin - line_start, plane_normal) / np.dot(line_dir, plane_normal)
    intersection_point = line_start + t * line_dir
    return intersection_point

# Find the intersection point of the "RR2-LR2" line with the plane
intersection_point = find_intersection_with_plane(point6, point7, plane_origin, plane_normal)

# Add the intersection point to the "Gerasimow landmarks" node
landmarks_node.AddControlPoint(intersection_point, 'R2')

# Update the scene
slicer.app.processEvents()

###Tangents to Plane & elongation###

import slicer
import numpy as np

# Try to retrieve the plane (check for both INB and MSP)
plane = None
plane_name = ""
try:
    plane = slicer.util.getNode('INB')
    plane_name = "INB"
    print("Using INB plane for tangent projection")
except:
    try:
        plane = slicer. util.getNode('MSP')
        plane_name = "MSP"
        print("Using MSP plane for tangent projection")
    except:
        raise RuntimeError("Neither INB nor MSP plane found! Please create one first.")

# Function to project a point onto a plane
def project_point_onto_plane(point, plane_origin, plane_normal):
    point_vector = np.array(point) - np.array(plane_origin)
    distance = np.dot(point_vector, plane_normal)
    projected_point = np.array(point) - distance * np.array(plane_normal)
    return projected_point

# Retrieve tangent1, tangent2, tangent3 and tangent4
tangent1 = slicer.util.getNode('tangent1')
tangent2 = slicer.util.getNode('tangent2')
tangent3 = slicer.util.getNode('tangent3')
tangent4 = slicer.util.getNode('tangent4')

# Project tangents onto the plane
plane_origin = plane.GetOrigin()
plane_normal = plane.GetNormal()

tangent1_start = tangent1.GetNthControlPointPosition(0)
tangent1_end = tangent1.GetNthControlPointPosition(1)
tangent1_start_projected = project_point_onto_plane(tangent1_start, plane_origin, plane_normal)
tangent1_end_projected = project_point_onto_plane(tangent1_end, plane_origin, plane_normal)

tangent2_start = tangent2.GetNthControlPointPosition(0)
tangent2_end = tangent2.GetNthControlPointPosition(1)
tangent2_start_projected = project_point_onto_plane(tangent2_start, plane_origin, plane_normal)
tangent2_end_projected = project_point_onto_plane(tangent2_end, plane_origin, plane_normal)

tangent3_start = tangent3.GetNthControlPointPosition(0)
tangent3_end = tangent3.GetNthControlPointPosition(1)
tangent3_start_projected = project_point_onto_plane(tangent3_start, plane_origin, plane_normal)
tangent3_end_projected = project_point_onto_plane(tangent3_end, plane_origin, plane_normal)

tangent4_start = tangent4.GetNthControlPointPosition(0)
tangent4_end = tangent4.GetNthControlPointPosition(1)
tangent4_start_projected = project_point_onto_plane(tangent4_start, plane_origin, plane_normal)
tangent4_end_projected = project_point_onto_plane(tangent4_end, plane_origin, plane_normal)

# Update tangents with projected points
tangent1.SetNthControlPointPosition(0, *tangent1_start_projected)
tangent1.SetNthControlPointPosition(1, *tangent1_end_projected)
tangent2.SetNthControlPointPosition(0, *tangent2_start_projected)
tangent2.SetNthControlPointPosition(1, *tangent2_end_projected)
tangent3.SetNthControlPointPosition(0, *tangent3_start_projected)
tangent3.SetNthControlPointPosition(1, *tangent3_end_projected)
tangent4.SetNthControlPointPosition(0, *tangent4_start_projected)
tangent4.SetNthControlPointPosition(1, *tangent4_end_projected)

print(f"Tangents projected onto {plane_name} plane")

###Elongate tangents###

import numpy as np

# Function to calculate the direction vector of a line
def calculate_direction_vector(start, end):
    return np.array(end) - np.array(start)

# Function to find the intersection point of two lines
def find_intersection_point(line1_start, line1_dir, line2_start, line2_dir):
    # Solve for t1 and t2 where line1_start + t1 * line1_dir = line2_start + t2 * line2_dir
    A = np. array([line1_dir, -line2_dir]).T
    b = np.array(line2_start) - np.array(line1_start)
    t = np.linalg.lstsq(A, b, rcond=None)[0]
    intersection_point = line1_start + t[0] * line1_dir
    return intersection_point

# Function to elongate a line in both directions
def elongate_line(start, end, elongation_distance):
    direction_vector = calculate_direction_vector(start, end)
    direction_vector_normalized = direction_vector / np.linalg.norm(direction_vector)
    new_start = start - elongation_distance * direction_vector_normalized
    new_end = end + elongation_distance * direction_vector_normalized
    return new_start, new_end
	
# Retrieve tangents
tangent1 = slicer.util.getNode('tangent1')
tangent2 = slicer.util.getNode('tangent2')
tangent3 = slicer. util.getNode('tangent3')
tangent4 = slicer.util.getNode('tangent4')

# Get the start and end points of tangents
tangents = [tangent1, tangent2, tangent3, tangent4]
elongation_distance = 100  # Elongation distance in mm

for tangent in tangents:
    start = np.array(tangent.GetNthControlPointPosition(0))
    end = np.array(tangent.GetNthControlPointPosition(1))
    new_start, new_end = elongate_line(start, end, elongation_distance)
    tangent.SetNthControlPointPosition(0, *new_start)
    tangent.SetNthControlPointPosition(1, *new_end)

print("Tangents elongated by 100mm in both directions")

###Find intersection points###

import numpy as np

# Create a new markups node list called "prediction points"
prediction_points = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'prediction points')

# Function to calculate the direction vector of a line
def calculate_direction_vector(start, end):
    return np.array(end) - np.array(start)

# Function to find the intersection point of two lines
def find_intersection_point(line1_start, line1_dir, line2_start, line2_dir):
    # Solve for t1 and t2 where line1_start + t1 * line1_dir = line2_start + t2 * line2_dir
    A = np. array([line1_dir, -line2_dir]).T
    b = np.array(line2_start) - np.array(line1_start)
    t = np.linalg.lstsq(A, b, rcond=None)[0]
    intersection_point = line1_start + t[0] * line1_dir
    return intersection_point

# Retrieve tangents
tangent1 = slicer.util.getNode('tangent1')
tangent2 = slicer.util. getNode('tangent2')
tangent3 = slicer.util.getNode('tangent3')
tangent4 = slicer.util.getNode('tangent4')

# Get start and end points of tangents
tangent1_start = [0.0, 0.0, 0.0]
tangent1_end = [0.0, 0.0, 0.0]
tangent2_start = [0.0, 0.0, 0.0]
tangent2_end = [0.0, 0.0, 0.0]
tangent3_start = [0.0, 0.0, 0.0]
tangent3_end = [0.0, 0.0, 0.0]
tangent4_start = [0.0, 0.0, 0.0]
tangent4_end = [0.0, 0.0, 0.0]

tangent1.GetNthControlPointPosition(0, tangent1_start)
tangent1.GetNthControlPointPosition(1, tangent1_end)
tangent2.GetNthControlPointPosition(0, tangent2_start)
tangent2.GetNthControlPointPosition(1, tangent2_end)
tangent3.GetNthControlPointPosition(0, tangent3_start)
tangent3.GetNthControlPointPosition(1, tangent3_end)
tangent4.GetNthControlPointPosition(0, tangent4_start)
tangent4.GetNthControlPointPosition(1, tangent4_end)

# Calculate direction vectors
tangent1_dir = calculate_direction_vector(tangent1_start, tangent1_end)
tangent2_dir = calculate_direction_vector(tangent2_start, tangent2_end)
tangent3_dir = calculate_direction_vector(tangent3_start, tangent3_end)
tangent4_dir = calculate_direction_vector(tangent4_start, tangent4_end)

# Find the intersection points
T1T2intersection_point = find_intersection_point(tangent1_start, tangent1_dir, tangent2_start, tangent2_dir)
T1T4intersection_point = find_intersection_point(tangent1_start, tangent1_dir, tangent4_start, tangent4_dir)
T3T2intersection_point = find_intersection_point(tangent3_start, tangent3_dir, tangent2_start, tangent2_dir)
T3T4intersection_point = find_intersection_point(tangent3_start, tangent3_dir, tangent4_start, tangent4_dir)

# Add the intersection points to the new node list
prediction_points.AddControlPoint(T1T2intersection_point, 'pred T1-T2')
prediction_points.AddControlPoint(T1T4intersection_point, 'pred T1-T4')
prediction_points.AddControlPoint(T3T2intersection_point, 'pred T3-T2')
prediction_points.AddControlPoint(T3T4intersection_point, 'pred T3-T4')

print("Prediction points created")

###Create error measurement lines###

import slicer
import numpy as np

def create_line_between_points(point1_index, point2_index, line_name, color, node1_name='Gerasimow_landmarks', node2_name='prediction points'):
    # Retrieve the points
    node1 = slicer.util.getNode(node1_name)
    point1 = [0.0, 0.0, 0.0]
    node1.GetNthControlPointPosition(point1_index, point1)

    node2 = slicer.util.getNode(node2_name)
    point2 = [0.0, 0.0, 0.0]
    node2.GetNthControlPointPosition(point2_index, point2)

    # Create a new markups line node
    line_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', line_name)
    line_node.AddControlPoint(point1)
    line_node.AddControlPoint(point2)

    # Set the color
    line_node.GetDisplayNode().SetSelectedColor(*color)
    line_node.GetDisplayNode().SetColor(*color)

# Example usage with custom node names
create_line_between_points(5, 0, 'prn T1-T2 pred error', (128/255, 0/255, 32/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(5, 1, 'prn T1-T4 pred error', (128/255, 0/255, 32/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(5, 2, 'prn T3-T2 pred error', (128/255, 0/255, 32/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(5, 3, 'prn T3-T4 pred error', (128/255, 0/255, 32/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(8, 0, 'R2 T1-T2 pred error', (255/255, 69/255, 0/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(8, 1, 'R2 T1-T4 pred error', (255/255, 69/255, 0/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(8, 2, 'R2 T3-T2 pred error', (255/255, 69/255, 0/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')
create_line_between_points(8, 3, 'R2 T3-T4 pred error', (255/255, 69/255, 0/255), node1_name='Gerasimow_landmarks', node2_name='prediction points')

print("Error measurement lines created")
```


</details>



### Outputs
If you want to copy all linear measurements in the scene for data collection, refer to [this guide](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/7b9aaccce0aaf54cdb91d4888bd12ac06ac452c0/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md)

#### Tangents1 and 2 with error
If you only executed the original Gerasimow two tangent method with the error rates added, your output will look like this: 

| (unknown) | tangent1   | 76.67370706918534 |
|-----------|------------|-------------------|
| (unknown) | tangent2   | 52.81195129766234 |
| (unknown) | pred error | 16.34060755830103 |

> [!IMPORTANT]
> Only "pred error" is a true measurement, do not use the other measurements as such in your data analysis!!!!

#### Tangents1,2,3,4 with error to pronasale and R2
The error measure is featured in the code for the Maltais-Lapointe section, so there's no action here; only an explanation provided for the output.
| Patient ID | measurement                          | Value                |          |
|-----------|--------------------------------|----------------------|----------|
| (unknown) | tangent1                      | 204.07274228601256   |    NOT a true measurement      |
| (unknown) | tangent2                      | 204.6648715684675    |      NOT a true measurement     |
| (unknown) | tangent3                      | 201.97502175201623   |    NOT a true measurement       |
| (unknown) | tangent4                      | 218.30578792587923   |    NOT a true measurement       |
| (unknown) | RR2-LR2                       | 6.354926645752534    |    NOT a true measurement       |
| (unknown) | prn T1-T2 pred error          | 7.873743447059059    |          |
| (unknown) | prn T1-T4 pred error          | 21.010305212757533   |          |
| (unknown) | prn T3-T2 pred error          | 8.417639300129508    |          |
| (unknown) | prn T3-T4 pred error          | 15.166210763216496   |          |
| (unknown) | R2 T1-T2 pred error           | 10.147736924776796   |          |
| (unknown) | R2 T1-T4 pred error           | 20.593051749643863   |          |
| (unknown) | R2 T3-T2 pred error           | 2.526685285660386    |          |
| (unknown) | R2 T3-T4 pred error           | 9.89739621086694     |          |

> [!IMPORTANT]
> Only "XX XX-XX pred error" are true measurements, do not use the other outputs (which are free-hand lines programmatically modified) as such in your data analysis as it is NOT representative of the methodology.

## Bibliography: 

[^1]: [Slicer Script Repository](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html)
[^2]:  Gerasimov, M. (1955). "Vosstanovlenie lica po cerepu." Akademii Nauk SSSR.
[^3]:  Gerassimow, M. (1968). Ich suchte Gesichter. Gutersloh (Germany): C, Bertelsmann Verlag.
[^4]:  Gerasimov, M. (1971). The Face Finder. London, Hutchinson.
[^5]:  Wilkinson, C. (2004). Forensic Facial Reconstruction. Cambridge, UK, Cambridge University Press.
[^6]:  Ullrich, H. and C. N. Stephan (2011). "On Gerasimov’s plastic facial reconstruction technique: new insights to facilitate repeatability." Journal of forensic sciences 56(2): 470-474.
[^7]:  Ullrich, H. and C. Stephan (2016). "Mikhail Mikhaylovich Gerasimov’s Authentic Approach to Plastic Facial Reconstruction." Anthropologie (Czech Republic) 54: 97-107.
[^8]:  Gatliff, B. P. (1984). "Facial sculpture on the skull for identification." American Journal of Forensic Medicine and Pathology 5(4): 327-332.
[^9]:  Stephan, C. N., et al. (2003). "Predicting nose projection and pronasale position in facial approximation: a test of published methods and proposal of new guidelines." American Journal of Physical Anthropology: The Official Publication of the American Association of Physical Anthropologists 122(3): 240-250.
[^10]: Rynn, C., Wilkinson, C.M. & Peters, H.L. (2010) "Prediction of nasal morphology from the skull." Forensic Sci Med Pathol 6, 20–34. https://doi.org/10.1007/s12024-009-9124-6
[^11]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." Int J Legal Med 130(3): 863-879.
[^12]: Rynn, C. and C. M. Wilkinson (2006). "Appraisal of traditional and recently proposed relationships between the hard and soft dimensions of the nose in profile." American Journal of Physical Anthropology: The Official Publication of the American Association of Physical Anthropologists 130(3): 364-373.
[^13]: Rynn, C., et al. (2012). "Relationships between the skull and face." Craniofacial identification. C. W. C. Rynn. Cambridge, Cambridge University Press: 193-202.
[^14]:Lapointe, G. M., et al. (2016). "Validation of the New Interpretation of Gerasimov's Nasal Projection Method for Forensic Facial Approximation Using CT Data." Journal of Forensic Sciences 61: S193-S200.
[^15]: Tinotenda Chiyangwa. [LinkedIn](https://www.linkedin.com/in/tinotenda-chiyangwa-9263121a3/), [Instagram](https://www.instagram.com/tino_tenda_arty/?igsh=YnNoMjM2ODRoNG1q#), [Portfolio](https://tinotendachiyangwa.wixsite.com/tino)
