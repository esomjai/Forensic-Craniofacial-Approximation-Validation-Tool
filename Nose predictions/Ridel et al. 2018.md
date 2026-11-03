# The Ridel et al. 2018 [^2] method (inspired by Lee et al. 2014)[^3]

For reference code snippets and insight for how 3D Slicer works, please refer to the official 3D Slicer webpage [^1]. 

The aim of the Ridel et al. (2018)[^2] paper was to test the reproducibility of the plane-to-plane and point-to-plane technique proposed by Lee et al. (2014)[^3] on a South African sample. The major difference between these two methods is the "starting" transverse plane to which all measurements are referenced:

-  Lee et al. (2014)[^3] utilised the natural head position with a radio-opaque  reference ear plug (REP) and head posture aligner (HPA), based on the works of Hwang et al. (2013)[^4] where the 
-  Ridel et al. (2018)[^2] standardised the scans after acquiring them via the Frankfort Horizontal Plane

Lee et al. (2014)[^3] report higher precision with measurements using the natural head position, however, this technique requires "intervention" at the point of acquiring the cone beam CT scans - and is not applicable for scans already obtained clinically without the reference devices (REF and HPA). Due to the reduced applicability of the natural head position, this tutorial focuses on the Ridel et al. (2018)[^2] version of the method.

### This document contains instructions for: 

 - [Landmarks in this guide (for prediction of soft tissues)](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#landmarks-in-this-guide-for-prediction-of-soft-tissues)
 - [Creating reference planes for replicating the hard tissue planes in the study](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#reference-planes-for-replicating-the-hard-tissue-planes-in-the-study)
 - [Creating the 7 hard tissue planes](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#create-the-hard-tissue-planes)
 - [Taking hard tissue measurements](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#hard-tissue-measurements)
 - [Using the prediction regressions estimating the Sn, Pn and Al](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#prediction-regressions-estimating-the-sn-pn-and-al)
 - [Creating the predicted soft tissue points](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#create-the-predicted-soft-tissue-points)
 - [Measuring the prediction errors](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#measuring-the-prediction-errors)
 - [What to expect for an output](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#output)
 - [An additional research idea](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md#research-idea)


> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guidewas taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.


### Landmarks in this guide (for prediction of soft tissues)

[Ridel_hard_tissue.mrk.json](https://github.com/user-attachments/files/20970624/Ridel_hard_tissue.mrk.json)


| Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|------------------|------------------|--------------|---------------|------------|------------|
| 0               | 1                | n            | Nasion        | The most anterior point on the frontonasal suture in the midline | Martin (1928)[^6];   Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 1                | 2                | ns           | Nasospinale   | The tip of the bony anterior nasal spine in the midline | Martin (1928)[^6];  Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 2                | 3                | rhi          | Rhinion       | The midline point at the inferior free end of the internasal suture | Martin (1928)[^6];   Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 3                | 4                | alR          | Alare Right   | Instrumentally determined as the most lateral point on the nasal aperture in a transverse plane on the right | Buikstra (1994)[^12]; Caple & Stephan (2016)[^5]  |
| 4                | 5                | alL          | Alare Left    | Instrumentally determined as the most lateral point on the nasal aperture in a transverse plane on the left | Buikstra (1994)[^12]; Caple & Stephan (2016)[^5]  |


### Illustration of the method


> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] Re-aligned the scene in the FHP
- [ ] Created a 4-point FHP 
- [ ] Allocated all hard tissue landmarks


### Reference planes for replicating the hard tissue planes in the study
The following table provides a summary of the hard tissue planes used to predict soft tissue dimensions
| Abbreviation of Hard Tissue Plane | Hard Tissue Plane Name          | Definition of Hard Tissue Plane                                                                                  |
|-----------------------------------|---------------------------------|-----------------------------------------------------------------------------------------------------------------|
| FHP                              | Frankfort Horizontal Plane      | The blueprint plane for the transverse planes (Tr); created by allovating left and right porions and left and right orbitale |
| MSP                              | MidSagittal Plane               | The blueprint plane for the sagittal planes (Sa); defined as a plane perpendicular to the FHP and best fitting the nasion, rhinion and nasospinale (ANS) landmarks |
| FRP                              | Frontal Plane                   | The blueprint plane for the coronal planes (Cor); defined as the plane perpendicular to both FHP and MSP         |
| nTr                              | nasion transverse plane         | Bisects the nasion, is parallel to FHP                                                                           |
| rhiTr                            | rhinion transverse plane        | Bisects the rhinion, is parallel to FHP                                                                          |
| nsTr                             | nasospinale transverse plane    | Bisects the ANS (nasospinale), is parallel to FHP                                                                |
| alLSa                            | left alare sagittal plane       | Bisects the left alare, is parallel to MSP                                                                       |
| alRSa                            | right alare sagittal plane      | Bisects the right alare, is parallel to MSP                                                                      |
| nCor                             | nasion coronal plane            | Bisects the nasion, is parallel to FRP                                                                           |
| rhiCor                           | rhinion coronal plane           | Bisects the rhinion, is parallel to FRP                                                                          |


<details>
<summary> Create the blueprint planes (FHP, MSP and FRP) </summary>

``` python
import numpy as np
import slicer

def create_orthogonal_planes():
    # Get existing nodes
    fhp_plane = slicer.util.getNode('FHP')
    if not fhp_plane:
        raise ValueError("FHP plane not found in the scene")
    
    points_node = slicer.util.getNode('Ridel_hard_tissue')
    if not points_node:
        raise ValueError("Ridel_hard_tissue markup not found in the scene")
    
    # Get the three points for MSP
    point0 = np.zeros(3)
    point1 = np.zeros(3)
    point2 = np.zeros(3)
    points_node.GetNthControlPointPosition(0, point0)
    points_node.GetNthControlPointPosition(1, point1)
    points_node.GetNthControlPointPosition(2, point2)
    
    # Calculate FHP normal
    fhp_normal = np.zeros(3)
    fhp_plane.GetNormal(fhp_normal)
    
    # Create MSP plane (same as before)
    vec1 = point1 - point0
    vec2 = point2 - point0
    msp_normal = np.cross(vec1, vec2)
    msp_normal = msp_normal / np.linalg.norm(msp_normal)
    
    # Ensure MSP is perpendicular to FHP
    dot_product = np.dot(msp_normal, fhp_normal)
    if not np.isclose(dot_product, 0, atol=1e-5):
        msp_normal = msp_normal - dot_product * fhp_normal
        msp_normal = msp_normal / np.linalg.norm(msp_normal)
    
    center = (point0 + point1 + point2) / 3.0
    
    msp_plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'MSP')
    msp_plane.SetNormalWorld(msp_normal)
    msp_plane.SetOriginWorld(center)
    msp_plane.SetSize(100, 100)
    
    # Now create FRP plane (perpendicular to both FHP and MSP)
    frp_normal = np.cross(fhp_normal, msp_normal)
    frp_normal = frp_normal / np.linalg.norm(frp_normal)
    
    # Use the same center point for consistency
    frp_plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'FRP')
    frp_plane.SetNormalWorld(frp_normal)
    frp_plane.SetOriginWorld(center)
    frp_plane.SetSize(100, 100)
    
    print("All three orthogonal planes created successfully")
    return msp_plane, frp_plane

# Run the function
create_orthogonal_planes()
```
![1](https://github.com/user-attachments/assets/3dc16e0c-2fdc-41d1-bd0f-e714a98bb729)


</details>



### Create the hard tissue planes

The following code creates the nTr, rhiTr, nsTr, alLSa, alRSa, nCor, rhiCor planes with reference colouring to their respective blueprint plane (blue if they are parallel to the FHP, green if they are parallel to the FRP and yellow if they are parallell to the MSP)

<details>
<summary> Create the 7 hard tissue planes </summary>

``` python
import numpy as np
import slicer
from slicer.util import getNode

def create_anatomical_planes():
    # Get existing reference planes
    fhp = getNode('FHP')
    msp = getNode('MSP')
    frp = getNode('FRP')
    
    # Get the landmark points
    points_node = getNode('Ridel_hard_tissue')
    
    # Extract all points
    points = []
    for i in range(points_node.GetNumberOfControlPoints()):
        pt = np.zeros(3)
        points_node.GetNthControlPointPosition(i, pt)
        points.append(pt)
    
    # Define indices
    nasion = 0
    nasospinale = 1
    rhinion = 2
    right_alare = 3
    left_alare = 4

    # Get reference plane normals
    fhp_normal = np.zeros(3)
    msp_normal = np.zeros(3)
    frp_normal = np.zeros(3)
    fhp.GetNormal(fhp_normal)
    msp.GetNormal(msp_normal)
    frp.GetNormal(frp_normal)

    # Create transverse planes (parallel to FHP)
    def create_transverse_plane(name, point, color=[0, 0, 1]):  # Blue
        plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', name)
        plane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneTypePointNormal)
        plane.SetNormalWorld(fhp_normal)
        plane.SetOriginWorld(point)
        plane.SetSize(180, 180)  # Larger size as requested
        
        # Set color and display properties
        display_node = plane.GetDisplayNode()
        if not display_node:
            display_node = plane.CreateDefaultDisplayNodes()
        display_node.SetSelectedColor(color)
        display_node.SetColor(color)
        display_node.SetTextScale(4)  # Make labels visible
        return plane

    # Create sagittal planes (parallel to MSP)
    def create_sagittal_plane(name, point, color=[1, 1, 0]):  # Yellow
        plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', name)
        plane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneTypePointNormal)
        plane.SetNormalWorld(msp_normal)
        plane.SetOriginWorld(point)
        plane.SetSize(180, 180)
        
        display_node = plane.GetDisplayNode()
        if not display_node:
            display_node = plane.CreateDefaultDisplayNodes()
        display_node.SetSelectedColor(color)
        display_node.SetColor(color)
        display_node.SetTextScale(4)
        return plane

    # Create coronal planes (parallel to FRP)
    def create_coronal_plane(name, point, color=[0, 1, 0]):  # Green
        plane = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', name)
        plane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneTypePointNormal)
        plane.SetNormalWorld(frp_normal)
        plane.SetOriginWorld(point)
        plane.SetSize(180, 180)
        
        display_node = plane.GetDisplayNode()
        if not display_node:
            display_node = plane.CreateDefaultDisplayNodes()
        display_node.SetSelectedColor(color)
        display_node.SetColor(color)
        display_node.SetTextScale(4)
        return plane

    # Create all planes
    # Transverse planes (blue)
    nTr = create_transverse_plane("nTr", points[nasion])
    rhiTr = create_transverse_plane("rhiTr", points[rhinion])
    nsTr = create_transverse_plane("nsTr", points[nasospinale])
    
    # Sagittal planes (yellow)
    alLSa = create_sagittal_plane("alLSa", points[left_alare])
    alRSa = create_sagittal_plane("alRSa", points[right_alare])
    
    # Coronal planes (green)
    nCor = create_coronal_plane("nCor", points[nasion])
    rhiCor = create_coronal_plane("rhiCor", points[rhinion])
    
    print("All anatomical planes created with:")
    print("- 180mm size")
    print("- Visible labels")
    print("- Correct color coding")
    return [nTr, rhiTr, nsTr, alLSa, alRSa, nCor, rhiCor]

# Run the function
create_anatomical_planes()
```
![Picture2](https://github.com/user-attachments/assets/698b1605-b7f7-4f04-8027-dcf1e4cec651)


</details>

### Hard tissue measurements

To apply the original regression equations by Ridel et al (2018), only 4 hard tissue measurements are required - Nasal width, Nasal height, Nasal bone length and Nasal bone projection - which will be marked with 🔵 in the following table. We will include the third nasal bone angle measurement as well in the code in case you wish to recalibrate the regression equation in the future - you can choose to ignore this datapoint. There will also be two extra lines _Nasal Bone Vector_ and _nTr AP Vector_ created to measure the angle - these are not true measurements, and will not be treated as such. 


| Measurement name  | Plane 1  | Plane 2 |
|---|---|---|
| 🔵 Nasal width           | alLSa  | alRSa   |
| 🔵 Nasal height          | nTr    | nsTr    |
| 🔵 Nasal bone length     | nTr    | rhiTr   |
| 🔵 Nasal bone projection | nCor   | rhiCor  |
| Nasal bone angle (°) |   apex -n; rhi-n elongated, nTr |   |  |

![4](https://github.com/user-attachments/assets/2c718449-8413-456e-9c0a-d23de7291c86)


<details>
<summary> Create the hard tissue measurements </summary>

``` python
import slicer
import numpy as np

def create_measurements():
    # Get existing plane nodes
    planes = {
        "nTr": slicer.util.getNode("nTr"),
        "rhiTr": slicer.util.getNode("rhiTr"),
        "nsTr": slicer.util.getNode("nsTr"),
        "alLSa": slicer.util.getNode("alLSa"),
        "alRSa": slicer.util.getNode("alRSa"),
        "nCor": slicer.util.getNode("nCor"),
        "rhiCor": slicer.util.getNode("rhiCor")
    }
    
    # Validate planes exist
    missing_planes = [name for name, node in planes.items() if not node]
    if missing_planes:
        raise ValueError(f"Missing planes: {', '.join(missing_planes)}")

    # Get fiducial points
    hard_tissue = slicer.util.getNode("Ridel_hard_tissue")
    if not hard_tissue:
        raise ValueError("Ridel_hard_tissue fiducial node not found")

    # Get nasion and rhinion points
    nasion = np.zeros(3)
    rhinion = np.zeros(3)
    hard_tissue.GetNthControlPointPosition(0, nasion)
    hard_tissue.GetNthControlPointPosition(2, rhinion)

    def create_plane_distance_measurement(name, plane1, plane2):
        """Creates measurement of shortest distance between two parallel planes"""
        # Get plane properties
        origin1 = np.array(plane1.GetOriginWorld())
        normal1 = np.array(plane1.GetNormalWorld())
        origin2 = np.array(plane2.GetOriginWorld())
        normal2 = np.array(plane2.GetNormalWorld())
        
        # Normalize normals
        normal1 = normal1 / np.linalg.norm(normal1)
        normal2 = normal2 / np.linalg.norm(normal2)
        
        # Verify planes are parallel
        if not np.allclose(np.cross(normal1, normal2), [0,0,0], atol=1e-3):
            raise ValueError(f"Planes for {name} are not parallel")
        
        # Calculate perpendicular distance
        distance = abs(np.dot(normal1, origin2 - origin1))
        
        # Create points that will be clearly visible between the planes
        # Use a point midway between the plane origins
        mid_point = (origin1 + origin2) / 2
        line_start = mid_point - normal1 * distance/2
        line_end = mid_point + normal1 * distance/2
        
        # Create measurement
        line_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
        line_node.AddControlPointWorld(line_start)
        line_node.AddControlPointWorld(line_end)
        line_node.GetMeasurement('length').SetEnabled(True)
        line_node.GetDisplayNode().SetSelectedColor(0.2, 0.8, 0.2)  # Green
        line_node.GetDisplayNode().SetTextScale(4)
        
        return distance

    # =============================================
    # 1. FRONTAL VIEW MEASUREMENTS (1-3)
    # =============================================
    
    try:
        # 1. Nasal width - between alare sagittal planes
        nasal_width = create_plane_distance_measurement("Nasal width", planes["alLSa"], planes["alRSa"])
        
        # 2. Nasal height - between nTr and nsTr
        nasal_height = create_plane_distance_measurement("Nasal height", planes["nTr"], planes["nsTr"])
        
        # 3. Nasal bone length - between nTr and rhiTr
        nasal_bone_length = create_plane_distance_measurement("Nasal bone length", planes["nTr"], planes["rhiTr"])
        
    except ValueError as e:
        slicer.util.errorDisplay(str(e))
        return

    # =============================================
    # 2. LATERAL VIEW MEASUREMENTS (4-5)
    # =============================================
    
    try:
        # 4. Nasal bone projection - special handling to ensure visibility between nCor and rhiCor
        nCor_normal = np.array(planes["nCor"].GetNormalWorld())
        nCor_normal = nCor_normal / np.linalg.norm(nCor_normal)
        rhiCor_normal = np.array(planes["rhiCor"].GetNormalWorld())
        rhiCor_normal = rhiCor_normal / np.linalg.norm(rhiCor_normal)
        
        if not np.allclose(np.cross(nCor_normal, rhiCor_normal), [0,0,0], atol=1e-3):
            raise ValueError("nCor and rhiCor planes are not parallel")
        
        nCor_origin = np.array(planes["nCor"].GetOriginWorld())
        rhiCor_origin = np.array(planes["rhiCor"].GetOriginWorld())
        nasal_projection = abs(np.dot(nCor_normal, rhiCor_origin - nCor_origin))
        
        # Create a point that is clearly between both planes
        # Use the midpoint between the nasion and rhinion projected onto the normal
        nasal_midpoint = (nasion + rhinion) / 2
        line_start = nasal_midpoint - nCor_normal * nasal_projection/2
        line_end = nasal_midpoint + nCor_normal * nasal_projection/2
        
        projection_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "Nasal bone projection")
        projection_line.AddControlPointWorld(line_start)
        projection_line.AddControlPointWorld(line_end)
        projection_line.GetMeasurement('length').SetEnabled(True)
        projection_line.GetDisplayNode().SetSelectedColor(0.2, 0.8, 0.2)  # Green
        projection_line.GetDisplayNode().SetTextScale(4)
        
    except ValueError as e:
        slicer.util.errorDisplay(str(e))
        return

    # =============================================
    # 5. Nasal bone angle - CORRECT DEFINITION
    # =============================================
    
    # Create superiorly elongated n-rhi line (hidden)
    nasal_bone_vec = rhinion - nasion
    elongation_factor = 1.5
    superior_point = nasion - nasal_bone_vec * elongation_factor
    
    elongated_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "Nasal Bone Vector")
    elongated_line.AddControlPointWorld(superior_point)
    elongated_line.AddControlPointWorld(rhinion)
    elongated_line.GetDisplayNode().SetVisibility(False)

    # Create nTr bisecting line (hidden)
    nTr_normal = np.array(planes["nTr"].GetNormalWorld())
    nTr_origin = np.array(planes["nTr"].GetOriginWorld())
    
    # Project nasion onto nTr plane
    v = nasion - nTr_origin
    dist = np.dot(v, nTr_normal)
    projected_nasion = nasion - dist * nTr_normal
    
    # Anterior-posterior direction in plane
    ant_post_dir = np.array([0, 1, 0])  # RAS +Y = anterior
    plane_dir = ant_post_dir - np.dot(ant_post_dir, nTr_normal) * nTr_normal
    plane_dir = plane_dir/np.linalg.norm(plane_dir)
    
    line_length = 50
    anterior_point = projected_nasion + plane_dir * line_length/2
    posterior_point = projected_nasion - plane_dir * line_length/2
    
    bisecting_line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "nTr AP Vector")
    bisecting_line.AddControlPointWorld(anterior_point)
    bisecting_line.AddControlPointWorld(posterior_point)
    bisecting_line.GetDisplayNode().SetVisibility(False)

    # Create visible angle measurement
    angle_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "Nasal bone angle")
    angle_node.AddControlPointWorld(posterior_point)  # Posterior point on bisecting line
    angle_node.AddControlPointWorld(nasion)           # Apex (nasion)
    angle_node.AddControlPointWorld(superior_point)   # Superior extended point
    angle_node.GetMeasurement('angle').SetEnabled(True)
    angle_node.GetDisplayNode().SetSelectedColor(0.8, 0.2, 0.2)  # Red
    angle_node.GetDisplayNode().SetTextScale(4)

    print("All measurements created successfully")

# Run the function
create_measurements()

# Script to create nCor_line and nTr_line in 3D Slicer

import slicer
from slicer.util import getNode
import numpy as np

# Function to create a line at the intersection of two planes, passing through a point
def createIntersectionLine(planeNode1, planeNode2, pointNode, pointIndex, lineName, lineLength=200):
    # Get the planes
    plane1 = getNode(planeNode1)
    plane2 = getNode(planeNode2)
    
    if not plane1 or not plane2:
        print(f"Error: Could not find planes {planeNode1} or {planeNode2}")
        return None
    
    # Get the nasion point
    points = getNode(pointNode)
    if not points:
        print(f"Error: Could not find points node {pointNode}")
        return None
        
    # Get the coordinates of the nasion (at the specified index)
    pointsArray = slicer.util.arrayFromMarkupsControlPoints(points)
    if pointIndex >= len(pointsArray):
        print(f"Error: Point index {pointIndex} is out of range")
        return None
        
    nasion = pointsArray[pointIndex]
    
    # Get the normal vectors of the planes
    normal1 = np.array(plane1.GetNormal())
    normal2 = np.array(plane2.GetNormal())
    
    # Calculate the direction of the intersection line (cross product of the normals)
    lineDirection = np.cross(normal1, normal2)
    lineDirection = lineDirection / np.linalg.norm(lineDirection)  # Normalize
    
    # Create a line node
    lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", lineName)
    
    # Define two points along the line
    point1 = nasion + lineDirection * (lineLength/2)
    point2 = nasion - lineDirection * (lineLength/2)
    
    # Add the points to the line
    lineNode.AddControlPoint(point1)
    lineNode.AddControlPoint(point2)
    
    print(f"Created {lineName} successfully")
    return lineNode

# Create the two required lines
nasionIndex = 0  # The index of nasion in "Ridel_hard_tissue"

# Create nCor_line
nCor_line = createIntersectionLine("MSP", "nCor", "Ridel_hard_tissue", nasionIndex, "nCor_line")

# Create nTr_line
nTr_line = createIntersectionLine("MSP", "nTr", "Ridel_hard_tissue", nasionIndex, "nTr_line")
#
```

Nasal bone length
<img src="https://github.com/user-attachments/assets/e57cf57e-4392-44d5-b577-834343ade37c" width="500">

Nasal bone projection
<img src="https://github.com/user-attachments/assets/a0618722-524e-4f47-8cef-9697091fbb2e" width="500">

Nasal height
<img src="https://github.com/user-attachments/assets/7cfac638-8a5d-4009-9656-4f40a5b6fbb5" width="500">

Nasal width
<img src="https://github.com/user-attachments/assets/c8167f46-a390-4c7b-8aeb-8e866738fd1a" width="500">

</details>

### Prediction regressions estimating the Sn, Pn and Al

First, I want to draw attention to the reporting disparity between Ridel et al. 2018 and Lee et al 2014 - the planes are named differently in Ridel et al. 2018, but are reported with the names equivalent in Lee et al (NaCor instead of nCor, etc). Thes have been taken into consideration when implementing the regressions. 
A [follow-up study](https://www.sciencedirect.com/science/article/pii/S1344622320301577#f0005) comparing the peformance of both Ridel et al. 2018 and Lee et al. 2014 on a Korean sample by Kim et al. (2021)[^13] demonstrated that the regressions perform differently. As the transverse plane implemented by Lee et al. 2014 (natural head position) performed worse on the FHP-oriented sample as expected, these regressions are not used in the code. 

The code works on the presumption that all the predicted measurements for a plane are to be implemented on the other plane ( e.g. Sn-nTr distance measured onto the nCor_line, etc.) and start at the intersection of the two lines, the nasion. 
As Ridel et al. 2018 warns about the incompleteness of their prediction with the left and right alare, the estimated dimension can be visualised, but the predicted points are NOT to be compared to the true soft tissue landmarks for error!
Two windows will pop up when running the script: 1)  **Facial landmark prediction** where you can choose which population-specific landmark estimation regression to use and 2) **Prediction Set manager** where all the predicted landmark sets are documented.

When you are happy with every soft tissue landmark you wish to predict, their population-specific and type of regression, click the button **Create New Prediction Set** and see how this appears in the environment as well as the manager window. 
To reduce clutter, the **Remove helper lines** button deleted all the reference lines used in the predictions. 


What to expect when running the GUI:

https://github.com/user-attachments/assets/dcb003b2-4986-47e3-80d1-a8bc08637034



<details>
<summary> Create the predicted soft tissue points </summary>

``` python
import slicer
import numpy as np
import qt
import vtk
import datetime
import re

print("\n=== FACIAL LANDMARK PREDICTION TOOL (MULTIPLE SETS) ===")
print("This script creates a new set of landmarks each time you run predictions")
print("The main GUI now stays open so you can create multiple sets!")

# Global variable to track our prediction manager window
predictionManagerWindow = None

# --- Helper: Remove helper measurement lines ---
def removeHelperMeasurementLines():
    """
    Remove all temporary helper lines (e.g., nTr_measurement, nCor_measurement) from the scene.
    """
    removed_count = 0
    for lineNode in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
        name = lineNode.GetName()
        if "nTr_measurement" in name or "nCor_measurement" in name:
            slicer.mrmlScene.RemoveNode(lineNode)
            removed_count += 1
    slicer.util.delayDisplay(f"Removed {removed_count} helper measurement lines.")

# --- Function to find lines in your scene with improved debugging ---
def findAllLines():
    print("\n--- LINES IN YOUR SCENE ---")
    nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    for node in nodes:
        name = node.GetName()
        p1 = np.zeros(3)
        p2 = np.zeros(3)
        node.GetNthControlPointPosition(0, p1)
        node.GetNthControlPointPosition(1, p2)
        length = np.linalg.norm(p2 - p1)
        print(f"Found: '{name}' (length: {length:.2f} mm)")
    print("-------------------------")

def getMeasurementFromLine(lineName):
    nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    exactMatch = None
    for node in nodes:
        if node.GetName().lower() == lineName.lower():
            exactMatch = node
            break
    if exactMatch:
        p1 = np.zeros(3)
        p2 = np.zeros(3)
        exactMatch.GetNthControlPointPosition(0, p1)
        exactMatch.GetNthControlPointPosition(1, p2)
        distance = np.linalg.norm(p2 - p1)
        print(f"✓ Found EXACT match for '{lineName}': '{exactMatch.GetName()}' = {distance:.2f} mm")
        return distance
    bestNode = None
    matchScore = 0
    for node in nodes:
        nodeName = node.GetName().lower()
        searchName = lineName.lower()
        score = 0
        for word in searchName.split():
            if word in nodeName:
                score += 1
        if score > matchScore:
            matchScore = score
            bestNode = node
    if bestNode and matchScore > 0:
        p1 = np.zeros(3)
        p2 = np.zeros(3)
        bestNode.GetNthControlPointPosition(0, p1)
        bestNode.GetNthControlPointPosition(1, p2)
        distance = np.linalg.norm(p2 - p1)
        print(f"✓ Found PARTIAL match for '{lineName}': '{bestNode.GetName()}' = {distance:.2f} mm")
        return distance
    print(f"✗ Could not find any match for: '{lineName}'")
    return None

def getNasionPoint():
    try:
        hardTissueNode = slicer.util.getNode("Ridel_hard_tissue")
        nasionPoint = np.zeros(3)
        hardTissueNode.GetNthControlPointPosition(0, nasionPoint)
        print("✓ Found Nasion point")
        return nasionPoint
    except:
        print("✗ Could not find Nasion point (looked for 'Ridel_hard_tissue')")
        return None

def createPredictionNode(nodeName):
    predNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", nodeName)
    print(f"✓ Created new prediction node '{nodeName}'")
    displayNode = predNode.GetDisplayNode()
    if displayNode:
        displayNode.SetTextScale(2.0)
        displayNode.SetGlyphScale(1.5)
    return predNode

# UPDATED FUNCTION: Fixed directions - removed negative signs to make points go in correct directions
def placeLandmark(predNode, landmarkName, nTrDistance, nCorDistance=None, equationCode=""):
    # Add equation code to landmark name if provided
    if equationCode:
        trackedName = f"{landmarkName}_{equationCode}"
    else:
        trackedName = f"{landmarkName}"
        
    print(f"Creating landmark: {trackedName}")
    
    # Get reference lines
    try:
        nTrLine = slicer.util.getNode("nTr_line")
        if nCorDistance is not None:
            nCorLine = slicer.util.getNode("nCor_line")
        else:
            nCorLine = None
    except Exception as e:
        print(f"✗ Could not find reference line(s): {str(e)}")
        return None
        
    # Get Nasion point (intersection of the two planes)
    nasionPoint = getNasionPoint()
    if nasionPoint is None:
        return None
    
    # Calculate vectors along each line
    p1 = np.zeros(3)
    p2 = np.zeros(3)
    nTrLine.GetNthControlPointPosition(0, p1)
    nTrLine.GetNthControlPointPosition(1, p2)
    nTrVector = p2 - p1
    nTrUnitVector = nTrVector / np.linalg.norm(nTrVector)
    # FIXED: Remove negative sign to get correct direction (forward)
    nTrUnitVector = nTrUnitVector  # Forwards direction
    
    # Create a point by moving DIRECTLY along nTr line by nCor distance
    predSetName = predNode.GetName().split("_")[-1]  # Get the timestamp part
    
    if nCorDistance is not None:
        print(f"➡️ Moving {nCorDistance:.2f} mm along nTr line from Nasion")
        nTrPoint = nasionPoint + nCorDistance * nTrUnitVector
        
        # Create measurement line showing nCor on nTr line
        try:
            measurementName = f"{predSetName}_{landmarkName}_nTr_measurement"
            slicer.mrmlScene.RemoveNode(slicer.util.getNode(measurementName))
        except:
            pass
            
        nTrMeasurementLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", measurementName)
        nTrMeasurementLine.AddControlPoint(nasionPoint)
        nTrMeasurementLine.AddControlPoint(nTrPoint)
        
        # Set color 
        displayNode = nTrMeasurementLine.GetDisplayNode()
        if displayNode:
            displayNode.SetColor(1, 0.5, 0)  # Orange
    else:
        # For Al which doesn't have nCor, just use nTr directly
        print(f"➡️ Using nTr value directly for {landmarkName} (no nCor value)")
        nTrPoint = nasionPoint
    
    # Final point starts at nTr point for true bi-planar placement
    finalPoint = nTrPoint
    
    # If we have nCor line, create point by moving DIRECTLY along nCor line by nTr distance
    if nTrDistance is not None and nCorLine is not None:
        nCorP1 = np.zeros(3)
        nCorP2 = np.zeros(3)
        nCorLine.GetNthControlPointPosition(0, nCorP1)
        nCorLine.GetNthControlPointPosition(1, nCorP2)
        
        nCorVector = nCorP2 - nCorP1
        nCorUnitVector = nCorVector / np.linalg.norm(nCorVector)
        # FIXED: Remove negative sign to get correct direction (downwards)
        nCorUnitVector = nCorUnitVector  # Downwards direction
        
        # Calculate the final point by moving from nTr point along nCor 
        print(f"➡️ Moving {nTrDistance:.2f} mm along nCor line from the nTr point")
        finalPoint = nTrPoint + nTrDistance * nCorUnitVector
        
        # Create measurement line along nCor
        try:
            nCorName = f"{predSetName}_{landmarkName}_nCor_measurement"
            slicer.mrmlScene.RemoveNode(slicer.util.getNode(nCorName))
        except:
            pass
            
        nCorMeasurementLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", nCorName)
        nCorMeasurementLine.AddControlPoint(nTrPoint)  # Start from nTr point
        nCorMeasurementLine.AddControlPoint(finalPoint)
        
        # Set color
        displayNode = nCorMeasurementLine.GetDisplayNode()
        if displayNode:
            displayNode.SetColor(0.5, 0, 1)  # Purple
            
    # Add landmark to prediction node
    idx = predNode.AddControlPoint(finalPoint)
    predNode.SetNthControlPointLabel(idx, trackedName)
    print(f"✓ Added landmark '{trackedName}' to prediction set")
        
    return finalPoint

def findMeasurements():
    results = {
        "Nasal height": None,
        "Nasal width": None,
        "Nasal bone length": None,
        "Nasal bone projection": None
    }
    print("\n--- LOOKING FOR MEASUREMENT LINES ---")
    findAllLines()
    for name in results:
        results[name] = getMeasurementFromLine(name)
    usedLines = {}
    nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    for name, value in results.items():
        if value is not None:
            for node in nodes:
                nodeName = node.GetName()
                p1 = np.zeros(3)
                p2 = np.zeros(3)
                node.GetNthControlPointPosition(0, p1)
                node.GetNthControlPointPosition(1, p2)
                distance = np.linalg.norm(p2 - p1)
                if abs(distance - value) < 0.01:
                    if nodeName in usedLines:
                        print(f"⚠️ WARNING: Line '{nodeName}' used for multiple measurements!")
                        print(f"   - Used for: {usedLines[nodeName]} AND {name}")
                    else:
                        usedLines[nodeName] = name
    return results

def getExistingPredictionSets():
    predSets = []
    nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")
    for node in nodes:
        name = node.GetName()
        if name.startswith("Pred_"):
            predSets.append(name)
    return predSets

def updatePredictionManagerTable():
    global predictionManagerWindow
    if predictionManagerWindow:
        predictionManagerWindow.refresh()

class PredictionManagerDialog(qt.QWidget):
    def __init__(self, predSets=None, parent=None):
        super(PredictionManagerDialog, self).__init__(parent)
        self.setWindowTitle("Prediction Set Manager")
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)
        global predictionManagerWindow
        predictionManagerWindow = self
        self.setWindowFlags(qt.Qt.WindowStaysOnTopHint)
        self.predSets = predSets if predSets else []
        layout = qt.QVBoxLayout(self)
        title = qt.QLabel("PREDICTION SET MANAGER")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: green")
        layout.addWidget(title)
        info = qt.QLabel("Manage your prediction sets while you work")
        layout.addWidget(info)
        self.table = qt.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Show", "Hide", "Delete"])
        self.table.setSelectionBehavior(qt.QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # --- Cleanup button ---
        cleanupBtn = qt.QPushButton("Remove Helper Lines")
        cleanupBtn.setStyleSheet("background-color: #FFF8DC; font-weight: bold;")
        cleanupBtn.clicked.connect(removeHelperMeasurementLines)
        layout.addWidget(cleanupBtn)

        refreshBtn = qt.QPushButton("Refresh List")
        refreshBtn.setStyleSheet("background-color: #CCFFFF")
        refreshBtn.clicked.connect(self.refresh)
        layout.addWidget(refreshBtn)
        closeBtn = qt.QPushButton("Close Manager")
        closeBtn.setStyleSheet("background-color: #FFCCCC; font-weight: bold; font-size: 14px; padding: 8px;")
        closeBtn.clicked.connect(lambda: self.hide())
        layout.addWidget(closeBtn)
        self.populateTable()
    def refresh(self):
        self.predSets = getExistingPredictionSets()
        self.populateTable()
    def populateTable(self):
        self.table.setRowCount(0)
        for i, predSet in enumerate(self.predSets):
            self.table.insertRow(i)
            nameItem = qt.QTableWidgetItem(predSet)
            self.table.setItem(i, 0, nameItem)
            showBtn = qt.QPushButton("Show")
            showBtn.setStyleSheet("background-color: #CCFFCC")
            showBtn.setProperty("predSet", predSet)
            showBtn.clicked.connect(self.onShowButtonClicked)
            self.table.setCellWidget(i, 1, showBtn)
            hideBtn = qt.QPushButton("Hide")
            hideBtn.setStyleSheet("background-color: #FFCCCC")
            hideBtn.setProperty("predSet", predSet)
            hideBtn.clicked.connect(self.onHideButtonClicked)
            self.table.setCellWidget(i, 2, hideBtn)
            delBtn = qt.QPushButton("Delete")
            delBtn.setStyleSheet("background-color: #FFAAAA")
            delBtn.setProperty("predSet", predSet)
            delBtn.setProperty("row", i)
            delBtn.clicked.connect(self.onDeleteButtonClicked)
            self.table.setCellWidget(i, 3, delBtn)
        self.table.resizeColumnsToContents()
    def onShowButtonClicked(self):
        sender = self.sender()
        predSet = sender.property("predSet")
        self.showPredSet(predSet)
    def onHideButtonClicked(self):
        sender = self.sender()
        predSet = sender.property("predSet")
        self.hidePredSet(predSet)
    def onDeleteButtonClicked(self):
        sender = self.sender()
        predSet = sender.property("predSet")
        row = sender.property("row")
        self.deletePredSet(predSet, row)
    def showPredSet(self, name):
        try:
            node = slicer.util.getNode(name)
            node.SetDisplayVisibility(True)
            for lineNode in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
                if lineNode.GetName().startswith(name.split("_")[-1]):
                    lineNode.SetDisplayVisibility(True)
            print(f"✓ Showing prediction set: {name}")
        except:
            print(f"✗ Could not find prediction set: {name}")
    def hidePredSet(self, name):
        try:
            node = slicer.util.getNode(name)
            node.SetDisplayVisibility(False)
            for lineNode in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
                if lineNode.GetName().startswith(name.split("_")[-1]):
                    lineNode.SetDisplayVisibility(False)
            print(f"✓ Hiding prediction set: {name}")
        except:
            print(f"✗ Could not find prediction set: {name}")
    def deletePredSet(self, name, row):
        msgBox = qt.QMessageBox()
        msgBox.setText(f"Delete prediction set '{name}'?")
        msgBox.setInformativeText("This cannot be undone.")
        msgBox.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        msgBox.setDefaultButton(qt.QMessageBox.No)
        ret = msgBox.exec_()
        if ret == qt.QMessageBox.Yes:
            try:
                node = slicer.util.getNode(name)
                slicer.mrmlScene.RemoveNode(node)
                timestamp = name.split("_")[-1]
                for lineNode in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
                    if lineNode.GetName().startswith(timestamp):
                        slicer.mrmlScene.RemoveNode(lineNode)
                self.table.removeRow(row)
                self.predSets.remove(name)
                print(f"✓ Deleted prediction set: {name}")
            except:
                print(f"✗ Could not delete prediction set: {name}")

class EquationSelectionDialog(qt.QWidget):
    def __init__(self, measurements, existingPredSets, parent=None):
        super(EquationSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Predict Facial Landmarks")
        self.setMinimumWidth(550)
        self.measurements = measurements
        self.existingPredSets = existingPredSets
        self.predictionManager = None
        self.createPredictionManager()
        layout = qt.QVBoxLayout(self)
        title = qt.QLabel("FACIAL LANDMARK PREDICTION")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: blue")
        layout.addWidget(title)
        info = qt.QLabel("This tool will create a NEW SET of landmarks each time you click 'Create'.\nThe dialog stays open so you can create multiple sets!")
        layout.addWidget(info)
        infoManager = qt.QLabel("The Prediction Manager window is also open so you can work with both at once!")
        infoManager.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(infoManager)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.nameLayout = qt.QHBoxLayout()
        self.nameLayout.addWidget(qt.QLabel("Prediction Set Name:"))
        self.nameEdit = qt.QLineEdit(f"Comparison_{timestamp}")
        self.nameLayout.addWidget(self.nameEdit)
        layout.addLayout(self.nameLayout)
        popLayout = qt.QHBoxLayout()
        popLayout.addWidget(qt.QLabel("Population:"))
        self.popCombo = qt.QComboBox()
        self.popCombo.addItems(["Black South African", "White South African"])
        popLayout.addWidget(self.popCombo)
        layout.addLayout(popLayout)
        self.popCombo.currentIndexChanged.connect(self.updateEquations)
        measGroup = qt.QGroupBox("Available Measurements")
        measLayout = qt.QFormLayout(measGroup)
        allAvailable = True
        for name, value in self.measurements.items():
            if value is not None:
                measLayout.addRow(f"{name}:", qt.QLabel(f"{value:.2f} mm"))
            else:
                label = qt.QLabel("NOT FOUND")
                label.setStyleSheet("color: red")
                measLayout.addRow(f"{name}:", label)
                allAvailable = False
        layout.addWidget(measGroup)
        self.createPronasaleGroup(layout)
        self.createSubnasaleGroup(layout)
        self.createAlareGroup(layout)
        if not allAvailable:
            warning = qt.QLabel("Some measurements are missing!\nNot all equations will work.")
            warning.setStyleSheet("color: red; font-weight: bold")
            layout.addWidget(warning)
        buttonsLayout = qt.QHBoxLayout()
        createBtn = qt.QPushButton("Create New Prediction Set")
        createBtn.setStyleSheet("background-color: #CCFFCC; font-weight: bold; padding: 12px;")
        createBtn.clicked.connect(self.createPredictionSet)
        buttonsLayout.addWidget(createBtn)
        managerBtn = qt.QPushButton("Show Manager")
        managerBtn.setStyleSheet("background-color: #CCCCFF; padding: 12px;")
        managerBtn.clicked.connect(lambda: self.showPredictionManager())
        buttonsLayout.addWidget(managerBtn)
        closeBtn = qt.QPushButton("Close")
        closeBtn.setStyleSheet("padding: 12px;")
        closeBtn.clicked.connect(lambda: self.close())
        buttonsLayout.addWidget(closeBtn)
        layout.addLayout(buttonsLayout)

        # --- Cleanup button ---
        cleanupBtn2 = qt.QPushButton("Remove Helper Lines")
        cleanupBtn2.setStyleSheet("background-color: #FFF8DC; font-weight: bold;")
        cleanupBtn2.clicked.connect(removeHelperMeasurementLines)
        layout.addWidget(cleanupBtn2)

        self.updateEquations()
    def createPredictionManager(self):
        self.predictionManager = PredictionManagerDialog(self.existingPredSets)
        self.predictionManager.move(50, 50)
        self.predictionManager.show()
    def showPredictionManager(self):
        if self.predictionManager:
            self.predictionManager.refresh()
            self.predictionManager.show()
            self.predictionManager.raise_()
    def createPredictionSet(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        baseName = self.nameEdit.text.split("_")[0]
        self.nameEdit.setText(f"{baseName}_{timestamp}")
        population = self.popCombo.currentText
        predSetName = self.nameEdit.text
        popCode = "BSA" if population == "Black South African" else "WSA"
        nodeName = f"Pred_{popCode}_{predSetName}"
        print(f"\n--- CREATING NEW PREDICTION SET: {nodeName} ---")
        print(f"Population: {population}")
        predNode = createPredictionNode(nodeName)
        displayNode = predNode.GetDisplayNode()
        if displayNode:
            if population == "Black South African":
                displayNode.SetSelectedColor(0.9, 0.5, 0.5)
            else:
                displayNode.SetSelectedColor(0.5, 0.5, 0.9)
        if self.pnGroupBox.isChecked():
            print("\n[PREDICTING PRONASALE (Pn)]")
            pnNTrEquation = self.pnNTrCombo.currentText
            pnNTrCode = self.pnNTrCombo.currentData
            pnNCorEquation = self.pnNCorCombo.currentText
            pnNCorCode = self.pnNCorCombo.currentData
            pnNTrValue = calculateFromEquation(pnNTrEquation, self.measurements)
            pnNCorValue = calculateFromEquation(pnNCorEquation, self.measurements)
            equationCode = f"{pnNTrCode}_{pnNCorCode}"
            if pnNTrValue is not None and pnNCorValue is not None:
                print(f"Placing Pn using equations:")
                print(f"  nTr: {pnNTrEquation} = {pnNTrValue:.2f} mm")
                print(f"  nCor: {pnNCorEquation} = {pnNCorValue:.2f} mm")
                placeLandmark(predNode, "Pn", pnNTrValue, pnNCorValue, equationCode)
            else:
                print("✗ Cannot place Pn - missing required measurements")
        if self.snGroupBox.isChecked():
            print("\n[PREDICTING SUBNASALE (Sn)]")
            snNTrEquation = self.snNTrCombo.currentText
            snNTrCode = self.snNTrCombo.currentData
            snNCorEquation = self.snNCorCombo.currentText
            snNCorCode = self.snNCorCombo.currentData
            snNTrValue = calculateFromEquation(snNTrEquation, self.measurements)
            snNCorValue = calculateFromEquation(snNCorEquation, self.measurements)
            equationCode = f"{snNTrCode}_{snNCorCode}"
            if snNTrValue is not None and snNCorValue is not None:
                print(f"Placing Sn using equations:")
                print(f"  nTr: {snNTrEquation} = {snNTrValue:.2f} mm")
                print(f"  nCor: {snNCorEquation} = {snNCorValue:.2f} mm")
                placeLandmark(predNode, "Sn", snNTrValue, snNCorValue, equationCode)
            else:
                print("✗ Cannot place Sn - missing required measurements")
        if self.alGroupBox.isChecked():
            print("\n[PREDICTING ALARE (Al)]")
            alNTrEquation = self.alNTrCombo.currentText
            alNTrCode = self.alNTrCombo.currentData
            alNTrValue = calculateFromEquation(alNTrEquation, self.measurements)
            if alNTrValue is not None:
                print(f"Placing Al using equations:")
                print(f"  nTr: {alNTrEquation} = {alNTrValue:.2f} mm")
                print("  nCor: None (no equation available)")
                equationCode = alNTrCode
                placeLandmark(predNode, "Al", alNTrValue, None, equationCode)
            else:
                print("✗ Cannot place Al - missing required measurements")
        print(f"\n--- PREDICTION SET CREATED: {nodeName} ---")
        print(f"You can create more sets without closing this dialog!")
        slicer.util.messageBox(f"Created new prediction set: {nodeName}\n\nYou can create more sets without closing this dialog!")
        updatePredictionManagerTable()
    def createPronasaleGroup(self, parentLayout):
        self.pnGroupBox = qt.QGroupBox("Pronasale (Pn)")
        self.pnGroupBox.setCheckable(True)
        self.pnGroupBox.setChecked(True)
        pnLayout = qt.QVBoxLayout(self.pnGroupBox)
        pnNTrLabel = qt.QLabel("Select equation for Pn to nTr:")
        pnLayout.addWidget(pnNTrLabel)
        self.pnNTrCombo = qt.QComboBox()
        pnLayout.addWidget(self.pnNTrCombo)
        pnNCorLabel = qt.QLabel("Select equation for Pn to nCor:")
        pnLayout.addWidget(pnNCorLabel)
        self.pnNCorCombo = qt.QComboBox()
        pnLayout.addWidget(self.pnNCorCombo)
        parentLayout.addWidget(self.pnGroupBox)
    def createSubnasaleGroup(self, parentLayout):
        self.snGroupBox = qt.QGroupBox("Subnasale (Sn)")
        self.snGroupBox.setCheckable(True)
        self.snGroupBox.setChecked(True)
        snLayout = qt.QVBoxLayout(self.snGroupBox)
        snNTrLabel = qt.QLabel("Select equation for Sn to nTr:")
        snLayout.addWidget(snNTrLabel)
        self.snNTrCombo = qt.QComboBox()
        snLayout.addWidget(self.snNTrCombo)
        snNCorLabel = qt.QLabel("Select equation for Sn to nCor:")
        snLayout.addWidget(snNCorLabel)
        self.snNCorCombo = qt.QComboBox()
        snLayout.addWidget(self.snNCorCombo)
        parentLayout.addWidget(self.snGroupBox)
    def createAlareGroup(self, parentLayout):
        self.alGroupBox = qt.QGroupBox("Alare (Al)")
        self.alGroupBox.setCheckable(True)
        self.alGroupBox.setChecked(True)
        alLayout = qt.QVBoxLayout(self.alGroupBox)
        self.alNTrCombo = qt.QComboBox()
        alLayout.addWidget(qt.QLabel("Select equation for Al to nTr:"))
        alLayout.addWidget(self.alNTrCombo)
        alNote = qt.QLabel("Note: Alare only uses nTr as there are no regression equations for nCor.")
        alNote.setStyleSheet("color: blue")
        alLayout.addWidget(alNote)
        parentLayout.addWidget(self.alGroupBox)
    def updateEquations(self):
        self.pnNTrCombo.clear()
        self.pnNCorCombo.clear()
        self.snNTrCombo.clear()
        self.snNCorCombo.clear()
        self.alNTrCombo.clear()
        if self.popCombo.currentText == "Black South African":
            self.pnNTrCombo.addItem("−17.805 + 1.170 × Nasal height", "BSA_nh")
            self.pnNCorCombo.addItem("30.403 - 0.290 × Nasal bone length", "BSA_nbl")
            self.snNTrCombo.addItem("−5.208 + 1.140 × Nasal height", "BSA_nh")
            self.snNTrCombo.addItem("29.723 + 1.092 × Nasal bone length", "BSA_nbl")
            self.snNTrCombo.addItem("1.270 + 0.795 × Nasal height + 0.531 × Nasal bone length", "BSA_nh+nbl")
            self.snNCorCombo.addItem("3.063 + 1.060 × Nasal bone projection", "BSA_nbp")
            self.alNTrCombo.addItem("−7.148 + 1.036 × Nasal height", "BSA_nh")
            self.alNTrCombo.addItem("25.608 + 0.943 × Nasal bone length", "BSA_nbl")
            self.alNTrCombo.addItem("2.369 + 0.782 × Nasal height + 0.391 × Nasal bone length", "BSA_nh+nbl")
        else:
            self.pnNTrCombo.addItem("−7.969 + 0.963 × Nasal height", "WSA_nh")
            self.pnNTrCombo.addItem("22.859 + 1.004 × Nasal bone length", "WSA_nbl")
            self.pnNTrCombo.addItem("−1.341 + 0.633 × Nasal height + 0.554 × Nasal bone length", "WSA_nh+nbl")
            self.pnNCorCombo.addItem("19.616 + 1.085 × Nasal bone projection", "WSA_nbp")
            self.snNTrCombo.addItem("2.950 + 0.991 × Nasal height", "WSA_nh")
            self.snNTrCombo.addItem("37.287 + 0.891 × Nasal bone length", "WSA_nbl")
            self.snNTrCombo.addItem("6.850 + 0.797 × Nasal height + 0.326 × Nasal bone length", "WSA_nh+nbl")
            self.snNCorCombo.addItem("5.055 + 1.050 × Nasal bone projection", "WSA_nbp")
            self.alNTrCombo.addItem("1.974 + 0.876 × Nasal height", "WSA_nh")
            self.alNTrCombo.addItem("32.924 + 0.757 × Nasal bone length", "WSA_nbl")
            self.alNTrCombo.addItem("4.779 + 0.737 × Nasal height + 0.234 × Nasal bone length", "WSA_nh+nbl")

def calculateFromEquation(equationText, measurements):
    nasalHeight = measurements.get("Nasal height")
    nasalWidth = measurements.get("Nasal width")
    nasalBoneLength = measurements.get("Nasal bone length")
    nasalBoneProjection = measurements.get("Nasal bone projection")
    if "Nasal height" in equationText and nasalHeight is None:
        print(f"Cannot calculate equation - missing Nasal height")
        return None
    if "Nasal width" in equationText and nasalWidth is None:
        print(f"Cannot calculate equation - missing Nasal width")
        return None
    if "Nasal bone length" in equationText and nasalBoneLength is None:
        print(f"Cannot calculate equation - missing Nasal bone length")
        return None
    if "Nasal bone projection" in equationText and nasalBoneProjection is None:
        print(f"Cannot calculate equation - missing Nasal bone projection")
        return None
    if "−17.805 + 1.170 × Nasal height" in equationText:
        return -17.805 + 1.170 * nasalHeight
    elif "30.403 - 0.290 × Nasal bone length" in equationText:
        return 30.403 - 0.290 * nasalBoneLength
    elif "−5.208 + 1.140 × Nasal height" in equationText:
        return -5.208 + 1.140 * nasalHeight
    elif "29.723 + 1.092 × Nasal bone length" in equationText:
        return 29.723 + 1.092 * nasalBoneLength
    elif "1.270 + 0.795 × Nasal height + 0.531 × Nasal bone length" in equationText:
        return 1.270 + 0.795 * nasalHeight + 0.531 * nasalBoneLength
    elif "3.063 + 1.060 × Nasal bone projection" in equationText:
        return 3.063 + 1.060 * nasalBoneProjection
    elif "−7.148 + 1.036 × Nasal height" in equationText:
        return -7.148 + 1.036 * nasalHeight
    elif "25.608 + 0.943 × Nasal bone length" in equationText:
        return 25.608 + 0.943 * nasalBoneLength
    elif "2.369 + 0.782 × Nasal height + 0.391 × Nasal bone length" in equationText:
        return 2.369 + 0.782 * nasalHeight + 0.391 * nasalBoneLength
    elif "−7.969 + 0.963 × Nasal height" in equationText:
        return -7.969 + 0.963 * nasalHeight
    elif "22.859 + 1.004 × Nasal bone length" in equationText:
        return 22.859 + 1.004 * nasalBoneLength
    elif "−1.341 + 0.633 × Nasal height + 0.554 × Nasal bone length" in equationText:
        return -1.341 + 0.633 * nasalHeight + 0.554 * nasalBoneLength
    elif "19.616 + 1.085 × Nasal bone projection" in equationText:
        return 19.616 + 1.085 * nasalBoneProjection
    elif "2.950 + 0.991 × Nasal height" in equationText:
        return 2.950 + 0.991 * nasalHeight
    elif "37.287 + 0.891 × Nasal bone length" in equationText:
        return 37.287 + 0.891 * nasalBoneLength
    elif "6.850 + 0.797 × Nasal height + 0.326 × Nasal bone length" in equationText:
        return 6.850 + 0.797 * nasalHeight + 0.326 * nasalBoneLength
    elif "5.055 + 1.050 × Nasal bone projection" in equationText:
        return 5.055 + 1.050 * nasalBoneProjection
    elif "1.974 + 0.876 × Nasal height" in equationText:
        return 1.974 + 0.876 * nasalHeight
    elif "32.924 + 0.757 × Nasal bone length" in equationText:
        return 32.924 + 0.757 * nasalBoneLength
    elif "4.779 + 0.737 × Nasal height + 0.234 × Nasal bone length" in equationText:
        return 4.779 + 0.737 * nasalHeight + 0.234 * nasalBoneLength
    print(f"Equation not recognized: {equationText}")
    return None

def runPredictionTool():
    print("\n--- FINDING MEASUREMENTS PRECISELY ---")
    measurements = findMeasurements()
    existingPredSets = getExistingPredictionSets()
    print(f"Found {len(existingPredSets)} existing prediction sets")
    dialog = EquationSelectionDialog(measurements, existingPredSets)
    dialog.show()
    return dialog

# Run the tool
predictionDialog = runPredictionTool()
```


</details>

To explain the naming convention of the predicted soft tissue points, take 
**Pn_WSA_nh_WSA_nbp** 

as the example: 

 - Pn {pronasale}

 - WSA {equation for the White South African population}

 - nh {equation featuring _nasal height_  **only** was used for calculating distance to nTr  & applied to nCor}

 - nbp {equation featuring _nasal bone projection_ **only** was used for calculating distance to nCor was used & applied to nTr}

### Measuring the prediction errors
For the following code to work, please place the soft tissue landmarks on the model. These are stored in [Ridel_soft_tissue.mrk.json](https://github.com/user-attachments/files/20970625/Ridel_soft_tissue.mrk.json)

 The script below connects all the prediction set landmarks with the true landmark, measuring the distance between them and creates these green lines calling the "error_{predicted lmrk name}". 

|Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|---|-----|--------|--------------|---------------------------------------------------------------------------------------------------------|------------|
| 1 | 2   | pn'    | pronasale          | The most anteriorly protruded point of the apex nasi. In the case of a bifid nose, the more protruding tip is chosen. |   Buikstra (1994)[^12]; Farkas (1994) [^11]; Caple & Stephan (2016)[^5]         |
| 2 | 3  | sn'    | subnasale          | Median point at the junction between the lower border of the nasal septum and the philtrum area.         |   Buikstra (1994)[^12]; Kolar (1997)[^10]; Caple & Stephan (2016)[^5]   |
| 3 | 4  | al'L   | left alare         | The most lateral point on the left nasal ala.                                                            |   Buikstra (1994)[^12]; Kolar (1997)[^10]; Caple & Stephan (2016)[^5]         |
| 4 | 5  | al'R   | right alare        | The most lateral point on the right nasal ala.                                                           |    Buikstra (1994)[^12]; Kolar (1997)[^10]; Caple & Stephan (2016)[^5]        |

![error](https://github.com/user-attachments/assets/67fe1868-4a2c-4d91-8491-0a07bb325d82)


<details>
<summary> Create the error between predicted and true soft tissue points </summary>

``` python
import slicer
import re

# --- CONFIGURATION ---
original_node_name = "Ridel_soft_tissue"
prediction_prefix = "Pred_"

def get_core_label(label):
    return re.sub(r"[^a-zA-Z0-9]", "", label).lower()

def pred_label_prefix(core_label):
    if core_label.startswith('all'):
        return 'AlL_'
    elif core_label.startswith('alr'):
        return 'AlR_'
    else:
        return core_label.capitalize() + "_"

try:
    origNode = slicer.util.getNode(original_node_name)
except Exception as e:
    slicer.util.errorDisplay(f"Could not find node '{original_node_name}' in the scene!")
    raise e

predNodes = [
    node for node in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")
    if node.GetName().startswith(prediction_prefix)
]

if not predNodes:
    slicer.util.errorDisplay("No prediction nodes found (no nodes named 'Pred_*').")
    raise Exception("No prediction nodes.")

origLabels = [origNode.GetNthControlPointLabel(i) for i in range(origNode.GetNumberOfControlPoints())]
origCores = [get_core_label(lbl) for lbl in origLabels]
predPrefixes = [pred_label_prefix(core) for core in origCores]

paired_landmarks = {}

for orig_index, orig_label in enumerate(origLabels):
    pred_prefix = predPrefixes[orig_index]
    print(f"\nOriginal landmark: '{orig_label}' (looking for predicted names starting with: '{pred_prefix}')")
    paired_landmarks[orig_label] = []
    for predNode in predNodes:
        predNodeName = predNode.GetName()
        for pred_index in range(predNode.GetNumberOfControlPoints()):
            pred_label = predNode.GetNthControlPointLabel(pred_index)
            if pred_label.startswith(pred_prefix):
                paired_landmarks[orig_label].append(
                    (predNodeName, pred_label, pred_index)
                )
                print(f"  ↳ Found in {predNodeName}: '{pred_label}' (index {pred_index})")

for orig_label, pred_list in paired_landmarks.items():
    orig_idx = next(i for i in range(origNode.GetNumberOfControlPoints())
                    if origNode.GetNthControlPointLabel(i) == orig_label)
    orig_point = [0,0,0]
    origNode.GetNthControlPointPosition(orig_idx, orig_point)
    for predNodeName, pred_label, pred_idx in pred_list:
        predNode = slicer.util.getNode(predNodeName)
        pred_point = [0,0,0]
        predNode.GetNthControlPointPosition(pred_idx, pred_point)
        lineName = f"error_{pred_label}"
        try:
            slicer.mrmlScene.RemoveNode(slicer.util.getNode(lineName))
        except:
            pass
        lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", lineName)
        lineNode.AddControlPoint(orig_point)
        lineNode.AddControlPoint(pred_point)
        displayNode = lineNode.GetDisplayNode()
        if displayNode:
            displayNode.SetLineThickness(0.2)   # As thin as possible
            displayNode.SetColor(0, 1, 0)       # Green for unselected
            displayNode.SetSelectedColor(0, 1, 0) # Green for selected

print("\nAll green, thin error lines are created and named as error_{predicted_point_name}!")
```


</details>



## Output
What can you expect as the outputs from the previous codes? We deleted a few extra lines with the **Remove helper lines** button, but there are still a few pseudo-lines to ignore when copying the measurements as decribed in [this guide](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md#code-to-copy-linear-measurements). We will show an example: 

<details>
<summary> Output example </summary>

| #  | Key                                 | Value                      | Notes |
|----|-------------------------------------|----------------------------|-------|
| 1  | Nasal width                        | 29.327888823096725         |       |
| 2  | Nasal height                       | 48.46643957081512          |       |
| 3  | Nasal bone length                  | 15.730008146012219         |       |
| 4  | Nasal bone projection              | 11.684143206638295         |       |
| 5  | Nasal Bone Vector                  | 48.989462815781316         |   ❌ - not a real measurement    |
| 6  | nTr AP Vector                      | 49.99999999999999          | ❌ - not a real measurement      |
| 7  | nCor_line                          | 200.0                      |   ❌ - not a real measurement    |
| 8  | nTr_line                           | 200.00000000000003         |  ❌ - not a real measurement     |
| 9  | error_Pn_BSA_nh_BSA_nbl            | 4.158088586052671          |       |
| 10 | error_Pn_WSA_nh_WSA_nbp            | 3.816614659968691          |       |
| 11 | error_Pn_WSA_nh+nbl_WSA_nbp        | 3.4756712343544436         |       |
| 12 | error_Sn_BSA_nh_BSA_nbp            | 6.425194233693379          |       |
| 13 | error_Sn_WSA_nh_WSA_nbp            | 4.38652782571401           |       |
| 14 | error_Sn_WSA_nh+nbl_WSA_nbp        | 4.529989191659301          |       |
| 15 | Nasal bone angle        | 53.44257035855746          |       |

</details>




#### Research idea

It may be worth implementing the coordinate system mentioned by Thitiorul et al. 2020[^14] to this method as the nasion is the central landmark in this method, and run analysis on the individual coordinates to see it these landmarks have significant correlations and/or predictive power to estimate soft tissue landmarks. You can check out the tutorial for the original method [here](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Thitiorul2020.md)

# Bibliography

[^1]: 3D Slicer webpage https://www.slicer.org/
[^2]: Ridel et al. (2018). "Skeletal dimensions as predictors for the shape of the nose in a South African sample: A cone-beam computed tomography (CBCT) study." Forensic Science International 289: 18-26.
[^3]: Lee, K.-M., et al. (2014). "Three-dimensional prediction of the nose for facial reconstruction using cone-beam computed tomography." Forensic Science International 236: 194.e191-194.e195.
[^4]: Hwang, H.-S., et al. (2013). "Use of Reference Ear Plug to improve accuracy of lateral cephalograms generated from cone-beam computed tomography scans." Korean Journal of Orthodontics 43(2): 54-61.
[^5]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." International Journal of Legal Medicine 130(3): 863-879.
[^6]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^7]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^8]: Howells, W. W. (1937). "The designation of the principle anthrometric landmarks on the head and skull." American Journal of Physical Anthropology 22(3): 477-494.
[^9]: Howells, W. W. (1974). Cranial variation in man: A study by multivariate analysis of patterns of difference among recent human populations. Cambridge, Harvard University.
[^10]: Kolar, J. and E. Salter (1997). Craniofacial anthropometry: practical measurement of the head and face for clinical, surgical, and research use. Springfield, Charles C Thomas.
[^11]: Farkas, L. G. (1994). Anthropometry of the Head and Face, Lippincott Williams & Wilkins.	
[^12]: Buikstra, J. E. and D. H. Ubelaker (1994). Standards for data collection from human skeletal remains. Fayetteville: Arkansas.
[^13]: Kim, D.-H., et al. (2021). "Application of nasal profile estimation methods for Korean population." Legal Medicine 48: 101823.
[^14]: Thitiorul, S., et al. (2020). "Three-Dimensional Prediction of the Nose for Facial Approximation in a Thai Population." J Forensic Sci 65(3): 707-714.








