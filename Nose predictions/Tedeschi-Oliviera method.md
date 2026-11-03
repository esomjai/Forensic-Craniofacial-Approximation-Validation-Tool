# The Tedeschi-Oliviera (2016) method (as validated by Strapasson (2020))

For reference code snippets and insight for how 3D Slicer works, please refer to the official 3D Slicer webpage [^1]. 


Tedeschi-Oliveira (2016)[^2] proposed their method on lateral cephalograms and and its validation by Strapasson (2020)[^3] on CT scans followed. Their theory stated that the rhinion and prosthion landmarks on the skull usually create a 90 degree angle with the soft nose tip (pronasale). This theory was valid for all their 300 Brazilian male cephalograms and was also supported by Strapasson (2020)[^3]’s validation on 228 CBCTs from Brazilian males and females, with the adjustment to place the predicted pronasale on the midsagittal plane (extra dimension needed for 3D recreation of the lateral cephalograms). 

The main goal for this guide is the easy reproducibility of the Tedeschi-Oliviera method in order to investigate its applicability to other (non-Brazilian) subjects. The predicted pronasale point will be placed onto the midsagittal plane and the actual angle will also be measured as well as the distance between the real and predicted pronasale. 

The same workflow as described below can be performed using a Graphic User Interface (GUI) in the repository. Click [here](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/abb1fa667dae6f5d0e8d64b5a551005023f5dca1/Nose%20predictions/Tedeschi-Oliviera%20GUI.md) to visit the code. 

### This document contains: 

- [Landmarks in this guide](#landmarks-in-this-guide)
- [Illustration of the method](#illustration-of-the-method)
- [Establishing the MSP (midsagittal plane)](#establishing-the-msp-midsagittal-plane)
- [Finding the pronasale prediction point geometrically](#finding-the-pronasale-prediction-point-geometrically)
- [Creating measurements for comparison](#creating-measurements-for-comparison)
- [Full code](#full-code)
- [Output](#output)
- [Bibliography](#bibliography)

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide does not have all the features (inion, bregma) that are to be landmarked. Please refer to the illustrations in the guide for correct placement. In addition, due to the CT being taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.


### Landmarks in this guide 
[Tedeschi_Oliviera_lmrks.mrk.json](https://github.com/user-attachments/files/30263036/Tedeschi_Oliviera_lmrks.mrk.json)


Please note that the pronasale landmark in this table is only applicable if you want to compare the true vs predicted landmark. The code and GUI will run without it present (you can delete it once imported into Slicer without consequences) and will be able to tell the difference between the estimated and true landmark. 

| Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|------------------|------------------|--------------|--------------|------------|------------|
|  0                | 1                |  rhinion       |  rhinion       | limit of the lower nasal bone or the lowest point of the nasal bone on the mid-sagittal plane | Tedeschi-Oliveira (2016)[^2]|
|  1                | 2                | prosthion    | prosthion    | the lowest point of the upper alveolar ridge, located between the upper central incisors on the mid-sagittal plane. | Tedeschi-Oliveira (2016)[^2] |
| 2                | 3                | pronasale     | pronasale    | The most anteriorly protruded point of the apex nasi. In the case of a bifid nose, the more protruding tip is chosen  | Farkas, 1994[^7]; Caple & Stephan 2016[^4]        
| 3            | 4                | inion        | inion        | Median point between the apices of the superior nuchal lines and at the base of the external occipital protuberance (not the tip of the protuberance) | Martin, 1928[^5]; Knussmann, 1988[^6]; Caple & Stephan 2016[^4] |
| 4             | 5                | nasion       | nasion       | Intersection of the nasofrontal sutures in the median plane | Martin, 1928[^5]; Knussmann, 1988[^6]; Caple & Stephan 2016[^4] |
| 5             | 6                | bregma       | bregma       | Where the sagittal and coronal sutures meet. | Martin, 1928[^5]; Knussmann, 1988[^6]; Caple & Stephan 2016[^4]|



### Illustration of the method

> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan has to be re-aligned in the FHP
- [ ] Allocate  landmarks from files

Expected view from the right after placing landmarks



<img src="https://github.com/user-attachments/assets/fdf97e6c-b58c-4ea1-92c8-b6d59f4e049f" width="500">



> [!NOTE]
> The following steps of codes can be run practically as one snippet. The steps are broken down to  explain the reason behind each one. If you are familiar, just jump to the [Full code](#full-code) section

### Establishing the MSP (midsagittal plane)

To establish the most fitting midsagittal plane, the combination on Rynn's (2010)[^8] INB plane with the addition of the rhinion and prosthion will be used. This is because the emphasis on their alignment in the midsagittal plane by Tedeschi-Oliveira (2016)[^2]. The following code creates a plane of best fit along the inion, nasion, bregma, rhinion and  prosthion. 

Expected view after creating the MSP - note that the plane was manually enlarged for illustration, but does not effect measurements/codes, it is purely visual


<img src="https://github.com/user-attachments/assets/0f5803c7-8703-400b-aa41-6a7c2ef60e44" width="500">

> [!IMPORTANT]
> If you use the [GUI](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/abb1fa667dae6f5d0e8d64b5a551005023f5dca1/Nose%20predictions/Tedeschi-Oliviera%20GUI.md) for this method, there is a choice to use different landmarks to create the midsagittal plane based on whether the skullcap is visible. This could be useful if you are replicating the method on a lower resolution CBCT or have otherwise compromised view of the cranial sutures and the occipital shape. 

<details>
<summary> MSP creation </summary>

``` python

###INB+rhinion+prosthion best fit plane####


import slicer
import numpy as np

# Get your landmark node (update the name if needed)
lmrks = slicer.util.getNode('Tedeschi_Oliviera_lmrks')

# Indices you want to use for the best fit plane
indices = [0, 1, 3, 4, 5]

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

### Finding the pronasale prediction point geometrically
The geometrical problem is to find the "apex" or point C of a right triangle, where the A and B points are the rhinion and prosthion (and the angle at C is 90 degrees). In 3D, this would be theoretically an infinite number of solutions, therefore we must restrict the code to only show the solutions that are restricted to the MSP. This is still 2 points, so the code only adds the one more anterior into the original "Tedeschi_Oliviera_lmrks" node at the end, naming it **pronasale pred**. 

Expected view after creating the predicted pronasale


<img src="https://github.com/user-attachments/assets/2eab1fbb-0dd2-49de-a63b-969744c43ce1" width="700">


<details>
<summary> Find predicted pronasale </summary>

``` python
###
import slicer
import numpy as np

# 1. Get the two known points from your landmark node
lmrks = slicer.util.getNode('Tedeschi_Oliviera_lmrks')
A = np.array(lmrks.GetNthControlPointPositionWorld(0))
B = np.array(lmrks.GetNthControlPointPositionWorld(1))

# 2. Get the MSP plane
mspPlaneNode = slicer.util.getNode('MSP')
plane_origin = np.array(mspPlaneNode.GetOriginWorld())
plane_normal = np.array(mspPlaneNode.GetNormalWorld())
plane_normal = plane_normal / np.linalg.norm(plane_normal)

# 3. Compute the vector from A to B
AB = B - A
AB_norm = AB / np.linalg.norm(AB)

# 4. Find a vector perpendicular to AB and on the MSP plane
perp_dir = np.cross(plane_normal, AB_norm)
perp_dir = perp_dir / np.linalg.norm(perp_dir)

# 5. The circle's center is the midpoint of AB
midpoint = (A + B) / 2
radius = np.linalg.norm(AB) / 2

# 6. Two possible apexes
C1 = midpoint + perp_dir * radius
C2 = midpoint - perp_dir * radius

# 7. Choose the more anterior apex (higher Y value)
pronasale_pred = C1 if C1[1] > C2[1] else C2

# 8. Add the apex to the landmark list and name it "pronasale pred"
lmrks.AddControlPointWorld(pronasale_pred)
lmrks.SetNthControlPointLabel(lmrks.GetNumberOfControlPoints()-1, "pronasale pred")

print("Added 'pronasale pred' to your landmark list as the most anterior apex of the right triangle.")
```

</details>


### Creating measurements for comparison

Now that the predicted pronasale point is found, we can generate the measurements for the statistical analysis: the angle between the rhinion, predicted pronasale and prosthion (**AS** - suggested angle, from the original study by Tedeschi-Oliveira (2016)[^2]); the angle between the rhinion, true pronasale and prosthion (**AR** - real angle, from the original study by Tedeschi-Oliveira (2016)[^2]); and the distance between the predicted and true pronasales. 

Expected view after creating the measurements


<img src="https://github.com/user-attachments/assets/517bd867-b08d-4728-8355-5be2cc9bc74d" width="500">


<details>
<summary> Measurements </summary>

``` python

###predicted pronasale angle###
import slicer
import numpy as np

# Get the nodes for the existing points and lines
hardTissueNode = slicer.util.getNode('Tedeschi_Oliviera_lmrks')


# Get the positions of the control points
apexPoint = np.array(hardTissueNode.GetNthControlPointPosition(6))
firstControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(0))
thirdControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(1))

# Create the angle node
angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'AS')
angleNode.AddControlPoint(firstControlPoint)  # First control point
angleNode.AddControlPoint(apexPoint)          # Second control point (apex)
angleNode.AddControlPoint(thirdControlPoint)  # Third control point

print("New angle 'AS' (rhinion-predicted pronasale-prosthion)created successfully.")

###true pronasale angle###
import slicer
import numpy as np

# Get the nodes for the existing points and lines
hardTissueNode = slicer.util.getNode('Tedeschi_Oliviera_lmrks')


# Get the positions of the control points
apexPoint = np.array(hardTissueNode.GetNthControlPointPosition(2))
firstControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(0))
thirdControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(1))

# Create the angle node
angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'AR')
angleNode.AddControlPoint(firstControlPoint)  # First control point
angleNode.AddControlPoint(apexPoint)          # Second control point (apex)
angleNode.AddControlPoint(thirdControlPoint)  # Third control point

print("New angle 'AR' (rhinion-true pronasale-prosthion) created successfully.")

###error of predictiom###

G = slicer.util.getNode('Tedeschi_Oliviera_lmrks')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')

firstPoint = G.GetNthControlPointPositionVector(2)  # true pronasale
L.AddControlPoint(firstPoint)
secondPoint = G.GetNthControlPointPositionVector(6) # predicted pronasale
L.AddControlPoint(secondPoint)
L.SetName('pronasale error')

# Set deep red color when unselected
L.GetDisplayNode().SetColor(0.5, 0, 0)  # deep red
```

</details>

## Full code

There are no additional steps for any adjustments in between the aforementioned codes, therefore you can just copy+paste the full snippet after allocating the landmarks. 


<details>
<summary> Full Code </summary>

``` python
####Tedeschi-Oliviera####


###INB+rhinion+prosthion best fit plane####


import slicer
import numpy as np

# Get your landmark node (update the name if needed)
lmrks = slicer.util.getNode('Tedeschi_Oliviera_lmrks')

# Indices you want to use for the best fit plane
indices = [0, 1, 3, 4, 5]

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


###
import slicer
import numpy as np

# 1. Get the two known points from your landmark node
lmrks = slicer.util.getNode('Tedeschi_Oliviera_lmrks')
A = np.array(lmrks.GetNthControlPointPositionWorld(0))
B = np.array(lmrks.GetNthControlPointPositionWorld(1))

# 2. Get the MSP plane
mspPlaneNode = slicer.util.getNode('MSP')
plane_origin = np.array(mspPlaneNode.GetOriginWorld())
plane_normal = np.array(mspPlaneNode.GetNormalWorld())
plane_normal = plane_normal / np.linalg.norm(plane_normal)

# 3. Compute the vector from A to B
AB = B - A
AB_norm = AB / np.linalg.norm(AB)

# 4. Find a vector perpendicular to AB and on the MSP plane
perp_dir = np.cross(plane_normal, AB_norm)
perp_dir = perp_dir / np.linalg.norm(perp_dir)

# 5. The circle's center is the midpoint of AB
midpoint = (A + B) / 2
radius = np.linalg.norm(AB) / 2

# 6. Two possible apexes
C1 = midpoint + perp_dir * radius
C2 = midpoint - perp_dir * radius

# 7. Choose the more anterior apex (higher Y value)
pronasale_pred = C1 if C1[1] > C2[1] else C2

# 8. Add the apex to the landmark list and name it "pronasale pred"
lmrks.AddControlPointWorld(pronasale_pred)
lmrks.SetNthControlPointLabel(lmrks.GetNumberOfControlPoints()-1, "pronasale pred")

print("Added 'pronasale pred' to your landmark list as the most anterior apex of the right triangle.")

###angles##

###predicted pronasale angle###
import slicer
import numpy as np

# Get the nodes for the existing points and lines
c = slicer.util.getNode('Tedeschi_Oliviera_lmrks')


# Get the positions of the control points
apexPoint = np.array(hardTissueNode.GetNthControlPointPosition(6))
firstControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(0))
thirdControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(1))

# Create the angle node
angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'AS')
angleNode.AddControlPoint(firstControlPoint)  # First control point
angleNode.AddControlPoint(apexPoint)          # Second control point (apex)
angleNode.AddControlPoint(thirdControlPoint)  # Third control point

print("New angle 'AS' (rhinion-predicted pronasale-prosthion)created successfully.")

###true pronasale angle###
import slicer
import numpy as np

# Get the nodes for the existing points and lines
hardTissueNode = slicer.util.getNode('Tedeschi_Oliviera_lmrks')


# Get the positions of the control points
apexPoint = np.array(hardTissueNode.GetNthControlPointPosition(2))
firstControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(0))
thirdControlPoint = np.array(hardTissueNode.GetNthControlPointPosition(1))

# Create the angle node
angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode', 'AR')
angleNode.AddControlPoint(firstControlPoint)  # First control point
angleNode.AddControlPoint(apexPoint)          # Second control point (apex)
angleNode.AddControlPoint(thirdControlPoint)  # Third control point

print("New angle 'AR' (rhinion-true pronasale-prosthion) created successfully.")

###error of predictiom###

G = slicer.util.getNode('Tedeschi_Oliviera_lmrks')
L = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode')

firstPoint = G.GetNthControlPointPositionVector(2)  # true pronasale
L.AddControlPoint(firstPoint)
secondPoint = G.GetNthControlPointPositionVector(6) # predicted pronasale
L.AddControlPoint(secondPoint)
L.SetName('pronasale error')

# Set deep red color when unselected
L.GetDisplayNode().SetColor(0.5, 0, 0)  # deep red

```

</details>

## Output
What can you expect as the outputs from the previous codes?

[Guide to copy measurements to clipboard](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md#content-summary)


| #    | Key                | Value               | Notes |
|------|--------------------|---------------------|-------|
| 1    | pronasale error    | 5.5450954811200495  |   in mm    |
| 2    | AS                 | 90.0                |  in degrees - this is only to check that the code was applied correctly   |
| 3    | AR                 | 101.41878713313862  |  in degrees       |

> [!TIP]
> This method is to be tested in different populations among various population-affinities, ages and BMI potentially, so make sure you include these additional factors and consider them during statistical analysis.


# Bibliography

[^1]: 3D Slicer webpage https://www.slicer.org/
[^2]: Tedeschi-Oliveira, S. V., et al. (2016). "Forensic facial reconstruction: Nasal projection in Brazilian adults." Forensic Science International 266: 123-129.
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
