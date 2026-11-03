# The Ryu et al. 2020 method 

For reference code snippets and insight for how 3D Slicer works, please refer to the official 3D Slicer webpage [^1]. 

The Ryu et al. 2020[^2] method investigated multiple correlations between hard and soft tissue landmarks and measurement on 100 deceased Korean subjects. As  previous methods described by Ridel et al. (2018)[^3] and Lee et al. (2014)[^4], this method also features standardised planes which create the framework for 76 measurements. They describe 26 statistically significant regression equations predicting a soft tissue measurement from a single hard tissue measurement. As the definitions from hard tissue landmarks and measurements in relation to their planes provide a framework, unknown soft tissue measurements and consequently, soft tissue landmarks can be predicted based on their methods via placing the predicted soft tissue point at the coordinates where they simultaneously  fulfil the calculated distances from their assigned planes.

As with other tutorials, this one will focus on 
1) Reproducing the method in a situation where only hard tissue is available (predicted measurements); 
2) then investigating the predictive power via establishing the true measurements


### This document contains instructions for: 

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide was taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.


### Landmarks in this guide (for prediction of soft tissues)

[Ryu_hard_tissue.mrk.json](https://github.com/user-attachments/files/24859018/Ryu_hard_tissue.mrk.json)



| Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|------------------|------------------|--------------|---------------|------------|------------|
| 0 | 1 | N | nasion | Intersection of the nasofrontal sutures in the median plane | Ryu et al. (2020)[^2]  |
| 1 | 2 | lambda | lambda | Point at which the two legs of the lambdoid suture and sagittal suture meet  | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5]  |
| 2 | 3 | prosthion | prosthion | Median point between the central incisors on the anterior most margin of the maxillary alveolar rim | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5]  |
| 3 | 4 | bregma | bregma | Where the sagittal and coronal sutures meet | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 4 | 5 | O_L | left orbitale | Most inferior point on the left inferior orbital rim. Usually falls along the lateral half of the orbital margin | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 5 | 6 | O_R | right orbitale | Most inferior point on the right inferior orbital rim. Usually falls along the lateral half of the orbital margin | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 6 | 7 | por_L | left porion | Upper border of the right external auditory meatus or ear canal | Pittayapat et al. (2017)[^8]|
| 7 | 8 | por_R | right porion | Upper border of the left external auditory meatus or ear canal | Pittayapat et al. (2017)[^8] |
| 8 | 9 | au_L | left auriculare | On the left zygomatic root, vertically above the center of the left external auditory meatus | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 9 | 10 | au_R | right auriculare | On the right zygomatic root, vertically above the center of the right external auditory meatus | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 10 | 11 | R | rhinion | Most rostral (end) point on the internasal suture. Cannot be determined accurately if nasal bones are broken distally | Martin (1928)[^6]; Knussman (1988)[^7]; Caple & Stephan (2016)[^5] |
| 11 | 12 | AC | acanthion | Most anterior tip of the anterior nasal spine | Howells (1937)[^9]; Howells (1974)[^10]; Caple & Stephan (2016)[^5] |
| 12 | 13 | IC_L | left inferior concha | Point where the left inferior nasal concha is submerged into the medial wall of the nasal aperture | Ryu et al. (2020)[^2]  |
| 13 | 14 | IC_R | right inferior concha | Point where the right inferior nasal concha is submerged into the medial wall of the nasal aperture | Ryu et al. (2020)[^2] |
| 14 | 15 | A_L | left alare | Instrumentally determined as the most lateral point on the left of the nasal aperture in a transverse plane | Buikstra (1994)[^13]; Caple & Stephan (2016)[^5]  |
| 15 | 16 | A_R | right alare | Instrumentally determined as the most lateral point on the right of the nasal aperture in a transverse plane | Buikstra (1994)[^13]; Caple & Stephan (2016)[^5]  |
| 16 | 17 | NAG_L | left nasal aperture groove | Most posterior point on the left lateral curvature of the nasal aperture from profile view | Ryu et al. (2020)[^2] |
| 17 | 18 | NAG_R | right nasal aperture groove | Most posterior point on the right lateral curvature of the nasal aperture from profile view | Ryu et al. (2020)[^2]  |
| 18 | 19 | NAI_L | left nasal aperture inferior | Most inferior point on the left of the nasal aperture from the frontal view | Ryu et al. (2020)[^2]  |
| 19 | 20 | NAI_R | right nasal aperture inferior | Most inferior point on the right of the nasal aperture from the frontal view | Ryu et al. (2020)[^2] |

Soft tissue landmarks (ALLOCATION NOT NECESSARY for the prediction code to work)
[Ryu_soft_tissue.mrk.json](https://github.com/user-attachments/files/29245314/Ryu_soft_tissue.mrk.json)



| Position in code | Position in file | Name in file | Landmark name | Definition | Defined by |
|------------------|-----------------|--------------|---------------|------------|------------|
| 0 | 1 | S | selion | Deepest midline point of the nasofrontal angle | Kolar, 1997[^11]; Caple & Stephan (2016)[^5]  |
| 1 | 2 | PN | pronasale | Most anteriorly projected point on a nose | Ryu et al. 2020[^2]  |
| 2 | 3 | SN | SN | Median point at the junction between the lower border of the nasal septum and the philtrum area | Kolar, 1997[^11]; Caple & Stephan (2016)[^5] |
| 3 | 4 | ACS_L | ACS_L | Highest point on the left ala nasi (rounded wing shape of a nose) |  Ryu et al. 2020[^2] |
| 4 | 5 | ACS_R | ACS_R | Highest point on the right ala nasi (rounded wing shape of a nose) |  Ryu et al. 2020[^2] |
| 5 | 6 | ACP_L | ACP_L | Most posterolateral point of the left curvature of the base of the nasal alae |  Ryu et al. 2020[^2] |
|6 | 7 | ACP_R | ACP_R | Most posterolateral point of the right curvature of the base of the nasal alae |  Ryu et al. 2020[^2] |
| 7 | 8 | NA_L | NA_L | The most lateral point on the left nasal ala |  Ryu et al. 2020[^2] |
| 8 | 9 | NA_R | NA_R | The most lateral point on the right nasal ala |  Ryu et al. 2020[^2] |
| 9 | 10 | ACI_L | ACI_L | Most posterolateral point of the curvature of the base line of the left nasal ala |  Ryu et al. 2020[^2] |
| 10 | 11 | ACI_R | ACI_R | Most posterolateral point of the curvature of the base line of the right nasal ala |  Ryu et al. 2020[^2]|




### Illustration of the method


> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] Re-aligned the scene in the FHP
- [ ] Allocated all hard tissue landmarks

### Reference planes & linear measurements from hard tissue landmarks in the study

The following code snippet creates both the reference planes and all linear hard tissue measurements based on the placed landmarks. These are summarised by the two tables below: 

<table>
  <thead>
    <tr>
      <th>Plane in scene</th>
      <th>Definition by Ryu et al. (2020)</th>
      <th>Coded using…</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Midsagittal</td>
      <td>Plane passing through the three landmarks, nasion, prosthion and lambda</td>
      <td></td>
    </tr>
    <tr>
      <td>Orbital</td>
      <td>Plane that passes through the two landmarks auriculare midpoint and orbitale and is orthogonal to the midsagittal plane</td>
      <td>midpoint betreen the auriculare (au_L, au_R) and L/R orbitale</td>
    </tr>
    <tr>
      <td>Coronal</td>
      <td>Plane that passes through one landmark, bregma and is orthogonal to the midsagittal plane and orbital plane</td>
      <td></td>
    </tr>
    <tr>
      <td>Rhinion</td>
      <td>Plane that passes through one landmark, rhinion and is parallel to the orbital plane</td>
      <td></td>
    </tr>
    <tr>
      <td>Left Alare Sagittal</td>
      <td>Plane that passes through one landmark, left alare and is parallel to the midsagittal plane</td>
      <td>sides separately</td>
    </tr>
    <tr>
      <td>Right Alare Sagittal</td>
      <td>Plane that passes through one landmark, right alare and is parallel to the midsagittal plane</td>
      <td></td>
    </tr>
  </tbody>
</table>

#### Measurements

| Measurement Code | Landmark name | Landmark code | Tissue type | Landmark plane name |
|-----------------|---------------|--------------|------------|-------------------|
| N1 | Acanthion | AC | hard | Midsagittal |
| N2 | Acanthion | AC | hard | Left Alare Sagittal |
| N3 | Acanthion | AC | hard | Right Alare Sagittal |
| N4 | Nasion | N | hard | Orbital |
| N5 | Acanthion | AC | hard | Orbital |
| N6 | Nasion | N | hard | Coronal |
| N7 | Acanthion | AC | hard | Coronal |
| N8 | Sellion | S | soft | Midsagittal |
| N9 | Sellion | S | soft | Left Alare Sagittal |
| N10 | Sellion | S | soft | Right Alare Sagittal |
| N11 | Pronasale | PN | soft | Midsagittal |
| N12 | Pronasale | PN | soft | Left Alare Sagittal |
| N13 | Pronasale | PN | soft | Right Alare Sagittal |
| N14 | Subnasale | SN | soft | Midsagittal |
| N15 | Subnasale | SN | soft | Left Alare Sagittal |
| N16 | Subnasale | SN | soft | Right Alare Sagittal |
| N17 | Sellion | S | soft | Orbital |
| N18 | Pronasale | PN | soft | Orbital |
| N19 | Subnasale | SN | soft | Orbital |
| N20 | Sellion | S | soft | Coronal |
| N21 | Pronasale | PN | soft | Coronal |
| N22 | Subnasale | SN | soft | Coronal |
| N23 | Orbitale (L) | O_L | hard | Rhinion |
| N24 | Orbitale (R) | O_R | hard | Rhinion |
| N25 | Sellion | S | soft | Rhinion |
| N26 | Acanthion | AC | hard | Rhinion |
| N27 | Subnasale | SN | soft | Rhinion |
| N28 | Rhinion | R | hard | Coronal |
| N29 | Left Inferior Concha | IC_L | hard | Midsagittal |
| N30 | Left Alare | A_L | hard | Midsagittal |
| N31 | Left Nasal Greater wing | NAG_L | hard | Midsagittal |
| N32 | Left Nasal Inferior | NAI_L | hard | Midsagittal |
| N33 | Left Inferior Concha | IC_L | hard | Orbital |
| N34 | Left Alare | A_L | hard | Orbital |
| N35 | Left Nasal Greater wing | NAG_L | hard | Orbital |
| N36 | Left Nasal Inferior | NAI_L | hard | Orbital |
| N37 | Left Inferior Concha | IC_L | hard | Coronal |
| N38 | Left Alare | A_L | hard | Coronal |
| N39 | Left Nasal Greater wing | NAG_L | hard | Coronal |
| N40 | Left Nasal Inferior | NAI_L | hard | Coronal |
| N41 | Left Alar crease Superior | ACS_L | soft | Midsagittal |
| N42 | Left Alar crease Posterior | ACP_L | soft | Midsagittal |
| N43 | Left Nose | NA_L | soft | Midsagittal |
| N44 | Left Alar crease Inferior | ACI_L | soft | Midsagittal |
| N45 | Left Alar crease Superior | ACS_L | soft | Orbital |
| N46 | Left Alar crease Posterior | ACP_L | soft | Orbital |
| N47 | Left Nose | NA_L | soft | Orbital |
| N48 | Left Alar crease Inferior | ACI_L | soft | Orbital |
| N49 | Left Alar crease Superior | ACS_L | soft | Coronal |
| N50 | Left Alar crease Posterior | ACP_L | soft | Coronal |
| N51 | Left Nose | NA_L | soft | Coronal |
| N52 | Left Alar crease Inferior | ACI_L | soft | Coronal |
| N53 | Right Inferior Concha | IC_R | hard | Midsagittal |
| N54 | Right Nose | NA_R | soft | Midsagittal |
| N55 | Right Nasal Greater wing | NAG_R | hard | Midsagittal |
| N56 | Right Nasal Inferior | NAI_R | hard | Midsagittal |
| N57 | Right Inferior Concha | IC_R | hard | Orbital |
| N58 | Right Nose | NA_R | soft | Orbital |
| N59 | Right Nasal Greater wing | NAG_R | hard | Orbital |
| N60 | Right Nasal Inferior | NAI_R | hard | Orbital |
| N61 | Right Inferior Concha | IC_R | hard | Coronal |
| N62 | Right Nose | NA_R | soft | Coronal |
| N63 | Right Nasal Greater wing | NAG_R | hard | Coronal |
| N64 | Right Nasal Inferior | NAI_R | hard | Coronal |
| N65 | Right Alar crease Superior | ACS_R | soft | Midsagittal |
| N66 | Right Alar crease Posterior | ACP_R | soft | Midsagittal |
| N67 | Right Nose | NA_R | soft | Midsagittal |
| N68 | Right Alar crease Inferior | ACI_R | soft | Midsagittal |
| N69 | Right Alar crease Superior | ACS_R | soft | Orbital |
| N70 | Right Alar crease Posterior | ACP_R | soft | Orbital |
| N71 | Right Nose | NA_R | soft | Orbital |
| N72 | Right Alar crease Inferior | ACI_R | soft | Orbital |
| N73 | Right Alar crease Superior | ACS_R | soft | Coronal |
| N74 | Right Alar crease Posterior | ACP_R | soft | Coronal |
| N75 | Right Nose | NA_R | soft | Coronal |
| N76 | Right Alar crease Inferior | ACI_R | soft | Coronal |

<details>
<summary> Code for hard tissue planes and measurements </summary>

``` python
import slicer
import numpy as np
import vtk
import os

# Helper to force colors to stick
def _ensure_display_node(node):
    dn = node.GetDisplayNode()
    if not dn:
        dn = node.CreateDefaultDisplayNodes()
    return dn

def get_hard_tissue_node():
    node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
    if node is not None and node.IsA("vtkMRMLMarkupsFiducialNode"):
        return node
    default_path = os.path.join(os.path.expanduser("~"), "Ryu_hard_tissue.mrk.json")
    if os.path.exists(default_path):
        node = slicer.util.loadMarkups(default_path)
        if node is not None:
            node.SetName("Ryu_hard_tissue")
            return node
    slicer.util.errorDisplay("Load 'Ryu_hard_tissue.mrk.json' manually.")
    return None

def create_anatomical_planes(landmarksNode):
    # Midsagittal
    midsag_pts = np.array([landmarksNode.GetNthControlPointPosition(i) 
                           for i in range(landmarksNode.GetNumberOfControlPoints()) 
                           if landmarksNode.GetNthControlPointLabel(i) in ["N", "lambda", "prosthion"]])
    centroid = midsag_pts.mean(axis=0)
    _, _, vh = np.linalg.svd(midsag_pts - centroid)
    normal = vh[2]
    if normal[0] < 0: normal *= -1
    midsagPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Midsagittal")
    midsagPlane.SetOrigin(centroid); midsagPlane.SetNormal(normal)
    dn = _ensure_display_node(midsagPlane)
    dn.SetColor(0.31, 0.78, 0.47); dn.SetSelectedColor(0.31, 0.78, 0.47) # Emerald

    # Orbital
    au_L = au_R = O_L = O_R = None
    for i in range(landmarksNode.GetNumberOfControlPoints()):
        p = np.array(landmarksNode.GetNthControlPointPosition(i))
        lbl = landmarksNode.GetNthControlPointLabel(i)
        if lbl == "au_L": au_L = p
        elif lbl == "au_R": au_R = p
        elif lbl == "O_L": O_L = p
        elif lbl == "O_R": O_R = p
    au_mid = (au_L + au_R) / 2.0
    pts = np.array([O_R, O_L, au_mid])
    centroid = pts.mean(axis=0)
    _, _, vh = np.linalg.svd(pts - centroid)
    initial_n = vh[2]
    midsag_n = np.array(midsagPlane.GetNormal())
    orbital_n = initial_n - np.dot(initial_n, midsag_n) * midsag_n
    orbital_n /= np.linalg.norm(orbital_n)
    if orbital_n[2] > 0: orbital_n *= -1
    orbPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Orbital")
    orbPlane.SetOrigin(centroid); orbPlane.SetNormal(orbital_n)
    dn = _ensure_display_node(orbPlane)
    dn.SetColor(0.78, 0.31, 0.47); dn.SetSelectedColor(0.78, 0.31, 0.47) # Purple

    # Coronal
    bregma = None
    for i in range(landmarksNode.GetNumberOfControlPoints()):
        if landmarksNode.GetNthControlPointLabel(i) == "bregma":
            bregma = np.array(landmarksNode.GetNthControlPointPosition(i)); break
    coronal_n = np.cross(midsag_n, orbital_n)
    coronal_n /= np.linalg.norm(coronal_n)
    if coronal_n[1] < 0: coronal_n *= -1
    corPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Coronal")
    corPlane.SetOrigin(bregma); corPlane.SetNormal(coronal_n)
    dn = _ensure_display_node(corPlane)
    dn.SetColor(0.31, 0.47, 0.78); dn.SetSelectedColor(0.31, 0.47, 0.78) # Blue

    # Rhinion
    rhinion = None
    for i in range(landmarksNode.GetNumberOfControlPoints()):
        if landmarksNode.GetNthControlPointLabel(i) == "R":
            rhinion = np.array(landmarksNode.GetNthControlPointPosition(i)); break
    rhPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Rhinion")
    rhPlane.SetOrigin(rhinion); rhPlane.SetNormal(orbital_n)
    dn = _ensure_display_node(rhPlane)
    dn.SetColor(0.9, 0.7, 0.1); dn.SetSelectedColor(0.9, 0.7, 0.1) # Gold

    # Alare Sagittal Planes
    for lm, pn in [("A_L", "Left Alare Sagittal"), ("A_R", "Right Alare Sagittal")]:
        p = None
        for i in range(landmarksNode.GetNumberOfControlPoints()):
            if landmarksNode.GetNthControlPointLabel(i) == lm:
                p = np.array(landmarksNode.GetNthControlPointPosition(i)); break
        plane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", pn)
        plane.SetOrigin(p); plane.SetNormal(midsag_n)
        dn = _ensure_display_node(plane)
        if "Left" in pn:
            dn.SetColor(0.2, 0.8, 0.2); dn.SetSelectedColor(0.2, 0.8, 0.2)  # Green
        else:
            dn.SetColor(0.8, 0.2, 0.2); dn.SetSelectedColor(0.8, 0.2, 0.2)  # Red

    print("Anatomical planes created.")

def create_hard_tissue_measurements(landmarksNode):
    measurements = [
        ("N1", "AC", "Midsagittal"), ("N2", "AC", "Left Alare Sagittal"), ("N3", "AC", "Right Alare Sagittal"),
        ("N4", "N", "Orbital"), ("N5", "AC", "Orbital"), ("N6", "N", "Coronal"), ("N7", "AC", "Coronal"),
        ("N28", "R", "Coronal"), ("N29", "IC_L", "Midsagittal"), ("N30", "A_L", "Midsagittal"),
        ("N31", "NAG_L", "Midsagittal"), ("N32", "NAI_L", "Midsagittal"), ("N33", "IC_L", "Orbital"),
        ("N34", "A_L", "Orbital"), ("N35", "NAG_L", "Orbital"), ("N36", "NAI_L", "Orbital"),
        ("N37", "IC_L", "Coronal"), ("N38", "A_L", "Coronal"), ("N39", "NAG_L", "Coronal"), ("N40", "NAI_L", "Coronal"),
        ("N53", "IC_R", "Midsagittal"), ("N54", "A_R", "Midsagittal"), ("N55", "NAG_R", "Midsagittal"), ("N56", "NAI_R", "Midsagittal"),
        ("N57", "IC_R", "Orbital"), ("N59", "NAG_R", "Orbital"), ("N60", "NAI_R", "Orbital"),
        ("N61", "IC_R", "Coronal"), ("N63", "NAG_R", "Coronal"), ("N64", "NAI_R", "Coronal")
    ]
    for lname, lm, pn in measurements:
        point = None
        for i in range(landmarksNode.GetNumberOfControlPoints()):
            if landmarksNode.GetNthControlPointLabel(i) == lm:
                point = np.array(landmarksNode.GetNthControlPointPosition(i)); break
        if point is None: continue
        plane = slicer.mrmlScene.GetFirstNodeByName(pn)
        if plane is None: continue
        n = np.array(plane.GetNormal()); o = np.array(plane.GetOrigin())
        proj = point - np.dot(point - o, n) * n
        
        line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", lname)
        line.AddControlPoint(point); line.AddControlPoint(proj)
        line.GetMeasurement('length').SetEnabled(True)
        dn = _ensure_display_node(line)
        dn.SetColor(0, 1, 1); dn.SetSelectedColor(0, 1, 1) # Cyan
    print("Hard tissue measurement lines created (Cyan).")

try:
    hard_node = get_hard_tissue_node()
    if hard_node is not None:
        create_anatomical_planes(hard_node)
        create_hard_tissue_measurements(hard_node)
        slicer.util.delayDisplay("Setup Complete", 3000)
except Exception as e:
    slicer.util.errorDisplay(f"Error: {str(e)}")

```
</details>

You can expect the following view after the code: 


<img src="https://github.com/user-attachments/assets/7769ae85-8827-4595-82b1-277023747572" width="500">



Feel free to adjust the size of the visible planes (in theory, they are infinite, so this is just for visuals).


### Prediction regressions

The original study distinguished their regression equations based on biological sex, therefore an graphic user interface will offer you to choose the biological sex of the skull. Then the following equations are applied to first estimate the soft tissue linear measurements, then landmarks. 

| Sides   | Predicted Length | Regression for Males                | Regression for Females                | Common Plane |
|---------|------------------|-------------------------------------|---------------------------------------|--------------|
| midline | **N17**          | 0.92×**N4**−3.58                    | 0.85×**N4**−1.10                      | Orbital      |
| midline | **N18**          | 0.91×**N5**−6.84                    | 1.01×**N5**−9.04                      | Orbital      |
| midline | **N19**          | 0.91×**N5**+5.81                    | 1.00×**N5**+3.23                      | Orbital      |
| midline | **N20**          | 0.93×**N6**+11.28                   | 0.96×**N6**+8.36                      | Coronal      |
| midline | **N21**          | 0.96×**N7**+24.70                   | 1.00×**N7**+19.50                     | Coronal      |
| midline | **N22**          | 0.96 × **N7** + 11.20               | 1.02×**N7**+5.18                      | Orbital      |
| left    | **N45**          | 0.66×**N35**−3.97                   | 0.67×**N35**−3.71                     | Orbital      |
| right   | **N69**          | 0.62×**N59**−2.63                   | 0.66×**N59**−3.60                     | Orbital      |
| left    | **N46**          | 0.75×**N35**+3.07                   | 0.80×**N35**+3.27                     | Orbital      |
| right   | **N70**          | 0.75×**N59**+3.70                   | 0.77×**N59**+3.85                     | Orbital      |
| left    | **N47**          | 0.66×**N35**+6.72                   | 0.65×**N35**+6.73                     | Orbital      |
| right   | **N71**          | 0.66×**N59**+6.77                   | 0.78×**N59**+3.82                     | Orbital      |
| left    | **N48**          | 0.66×**N35**+14.01                  | 0.65×**N35**+13.58                    | Orbital      |
| right   | **N72**          | 0.69×**N59**+13.52                  | 0.65×**N59**+13.15                    | Coronal      |
| left    | **N49**          | 0.91×**N39**+19.98                  | 0.97×**N39**+14.07                    | Coronal      |
| right   | **N73**          | 0.92×**N63**+18.62                  | 0.90×**N63**+18.81                    | Coronal      |
| left    | **N50**          | 0.95×**N39**+10.59                  | 0.95×**N39**+10.26                    | Coronal      |
| right   | **N74**          | 0.99×**N63**+8.11                   | 1.00×**N63**+6.55                     | Coronal      |
| left    | **N51**          | 0.98×**N39**+12.26                  | 0.95×**N39**+12.71                    | Coronal      |
| right   | **N75**          | 1.02×**N63**+9.19                   | 1.03×**N63**+7.54                     | Coronal      |
| left    | **N52**          | 0.96×**N39**+15.18                  | 0.99×**N39**+11.45                    | Coronal      |
| right   | **N76**          | 0.99×**N63**+13.23                  | 1.02×**N63**+9.06                     | Coronal      |


  The code's logic is the following - approximated distances (from the regresion equations) of the soft tissue landmarks from the planes in the "framework" are simultaneously applied to predict the position of the soft tissue landmark. 



<details>
<summary> GUI code for prediction of soft tissue landmarks</summary>
  
``` python
import qt
import slicer
import numpy as np
import datetime

def _ensure_display_node(node):
    dn = node.GetDisplayNode()
    if not dn:
        dn = node.CreateDefaultDisplayNodes()
    return dn

class LengthPredictionDialog(qt.QDialog):
    def __init__(self, main_gui, parent=None):
        super(LengthPredictionDialog, self).__init__(parent)
        self.main_gui = main_gui
        self.setWindowTitle("Predict Soft Tissue Lengths")
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(qt.QLabel("<b>Select Biological Sex:</b>"))
        self.sex_combo = qt.QComboBox()
        self.sex_combo.addItems(["Male", "Female"])
        self.layout().addWidget(self.sex_combo)
        self.predict_btn = qt.QPushButton("Predict Lengths and Create Lines")
        self.predict_btn.setStyleSheet("background-color: #CCFFCC; font-weight: bold; padding: 8px;")
        self.predict_btn.clicked.connect(self.run_length_prediction)
        self.layout().addWidget(self.predict_btn)

    def get_regressions(self, sex, m):
        # Helper to safely get a measurement value or 0.0 if it doesn't exist
        def val(k): 
            return m.get(k, 0.0)

        # Helper to prioritize the best R^2 equation
        def pick_best(options):
            # options: list of tuples (R^2, independent_measurement, equation_lambda)
            # We loop through them in order (highest R^2 first)
            for _, measure_key, eq in options:
                if val(measure_key) > 0.1: # Check if measurement exists and is valid
                    return eq(val(measure_key))
            return 0.0 # Fallback if all are missing

        pred = {}

        if sex == "Male":
            # --- Midline (No conflicts, single R^2 per plane) ---
            pred["N17"] = 0.92 * val("N4") - 3.58
            pred["N18"] = 0.91 * val("N5") - 6.84
            pred["N19"] = 0.91 * val("N5") + 5.81
            pred["N20"] = 0.93 * val("N6") + 11.28
            pred["N21"] = 0.96 * val("N7") + 24.70
            pred["N22"] = 0.96 * val("N7") + 11.20

            # --- Alare Orbital (No conflicts, single R^2 per plane) ---
            pred["N45"] = 0.66 * val("N35") - 3.97
            pred["N69"] = 0.62 * val("N59") - 2.63
            pred["N46"] = 0.75 * val("N35") + 3.07
            pred["N70"] = 0.75 * val("N59") + 3.70
            pred["N47"] = 0.66 * val("N35") + 6.72
            pred["N71"] = 0.66 * val("N59") + 6.77
            pred["N48"] = 0.66 * val("N35") + 14.01
            pred["N72"] = 0.69 * val("N59") + 13.52

            # --- Alare Coronal (Prioritized by R^2: N39/N63 > N7 > N28) ---
            # N49 (Left ACS)
            pred["N49"] = pick_best([
                (85, "N39", lambda x: 0.91 * x + 19.98), # Primary (Highest R²)
                (80, "N7",  lambda x: 0.84 * x + 16.41), # Secondary
                (71, "N28", lambda x: 0.85 * x + 11.47)  # Tertiary
            ])
            # N50 (Left ACP)
            pred["N50"] = pick_best([
                (90, "N39", lambda x: 0.95 * x + 10.59),
                (82, "N7",  lambda x: 0.87 * x + 8.61),
                (66, "N28", lambda x: 0.83 * x + 7.11)
            ])
            # N51 (Left NA)
            pred["N51"] = pick_best([
                (87, "N39", lambda x: 0.98 * x + 12.26),
                (82, "N7",  lambda x: 0.92 * x + 8.38),
                (70, "N28", lambda x: 0.90 * x + 4.58)
            ])
            # N52 (Left ACI)
            pred["N52"] = pick_best([
                (88, "N39", lambda x: 0.96 * x + 15.18),
                (83, "N7",  lambda x: 0.90 * x + 11.41),
                (63, "N28", lambda x: 0.83 * x + 12.30)
            ])
            # N73 (Right ACS)
            pred["N73"] = pick_best([
                (84, "N63", lambda x: 0.92 * x + 18.62),
                (75, "N7",  lambda x: 0.83 * x + 17.20),
                (69, "N28", lambda x: 0.85 * x + 10.92)
            ])
            # N74 (Right ACP)
            pred["N74"] = pick_best([
                (90, "N63", lambda x: 0.99 * x + 8.11),
                (81, "N7",  lambda x: 0.90 * x + 6.34),
                (66, "N28", lambda x: 0.87 * x + 4.21)
            ])
            # N75 (Right NA)
            pred["N75"] = pick_best([
                (88, "N63", lambda x: 1.02 * x + 9.19),
                (81, "N7",  lambda x: 0.94 * x + 6.12),
                (70, "N28", lambda x: 0.94 * x + 1.61)
            ])
            # N76 (Right ACI)
            pred["N76"] = pick_best([
                (88, "N63", lambda x: 0.99 * x + 13.23),
                (83, "N7",  lambda x: 0.92 * x + 9.52),
                (62, "N28", lambda x: 0.85 * x + 10.92)
            ])

            # --- Alare Sagittal (Lateral) ---
            pred["N41"] = 0.56 * val("N30") + 7.61
            pred["N42"] = 0.68 * val("N30") + 12.51
            pred["N43"] = 0.58 * val("N30") + 13.39
            pred["N44"] = 0.65 * val("N30") + 6.57
            pred["N65"] = 0.0 # p>=0.05
            pred["N66"] = 0.79 * val("N54") + 11.13
            pred["N67"] = 0.68 * val("N54") + 12.12
            pred["N68"] = 0.48 * val("N54") + 8.83

        else: # Female
            # --- Midline ---
            pred["N17"] = 0.85 * val("N4") - 1.10
            pred["N18"] = 1.01 * val("N5") - 9.04
            pred["N19"] = 1.00 * val("N5") + 3.23
            pred["N20"] = 0.96 * val("N6") + 8.36
            pred["N21"] = 1.00 * val("N7") + 19.50
            pred["N22"] = 1.02 * val("N7") + 5.18

            # --- Alare Orbital ---
            pred["N45"] = 0.67 * val("N35") - 3.71
            pred["N69"] = 0.66 * val("N59") - 3.60
            pred["N46"] = 0.80 * val("N35") + 3.27
            pred["N70"] = 0.77 * val("N59") + 3.85
            pred["N47"] = 0.65 * val("N35") + 6.73
            pred["N71"] = 0.78 * val("N59") + 3.82
            pred["N48"] = 0.65 * val("N35") + 13.58
            pred["N72"] = 0.65 * val("N59") + 13.15

            # --- Alare Coronal (Prioritized by R^2: N39/N63 > N28 > N7 for Females) ---
            # N49 (Left ACS)
            pred["N49"] = pick_best([
                (93, "N39", lambda x: 0.97 * x + 14.07), # Primary
                (87, "N28", lambda x: 0.96 * x + 1.71),  # Secondary (N28 > N7 for Female)
                (86, "N7",  lambda x: 0.95 * x + 7.65)   # Tertiary
            ])
            # N50 (Left ACP)
            pred["N50"] = pick_best([
                (97, "N39", lambda x: 0.95 * x + 10.26),
                (87, "N28", lambda x: 0.92 * x - 0.61),
                (90, "N7",  lambda x: 0.93 * x + 3.83)
            ])
            # N51 (Left NA)
            pred["N51"] = pick_best([
                (95, "N39", lambda x: 0.95 * x + 12.71),
                (93, "N28", lambda x: 0.96 * x - 0.93),
                (93, "N7",  lambda x: 0.95 * x + 4.62)
            ])
            # N52 (Left ACI)
            pred["N52"] = pick_best([
                (99, "N39", lambda x: 0.99 * x + 11.45),
                (86, "N28", lambda x: 0.96 * x + 0.16),
                (89, "N7",  lambda x: 0.97 * x + 4.68)
            ])
            # N73 (Right ACS)
            pred["N73"] = pick_best([
                (95, "N63", lambda x: 0.90 * x + 18.81),
                (89, "N28", lambda x: 0.92 * x + 4.71),
                (91, "N7",  lambda x: 0.93 * x + 9.62)
            ])
            # N74 (Right ACP)
            pred["N74"] = pick_best([
                (96, "N63", lambda x: 1.00 * x + 6.55),
                (89, "N28", lambda x: 1.02 * x - 8.55),
                (91, "N7",  lambda x: 1.03 * x - 3.54)
            ])
            # N75 (Right NA)
            pred["N75"] = pick_best([
                (94, "N63", lambda x: 1.03 * x + 7.54),
                (88, "N28", lambda x: 1.05 * x - 8.27),
                (92, "N7",  lambda x: 1.07 * x - 3.82)
            ])
            # N76 (Right ACI)
            pred["N76"] = pick_best([
                (95, "N63", lambda x: 1.02 * x + 9.06),
                (87, "N28", lambda x: 1.03 * x - 5.60),
                (91, "N7",  lambda x: 1.05 * x - 1.35)
            ])

            # --- Alare Sagittal (Lateral) p>=0.05, set to 0 ---
            pred["N41"] = 0.0
            pred["N42"] = 0.0
            pred["N43"] = 0.0
            pred["N44"] = 0.0
            pred["N65"] = 0.0
            pred["N66"] = 0.0
            pred["N67"] = 0.0
            pred["N68"] = 0.0

        return pred

    def run_length_prediction(self):
        # (The rest of this method remains EXACTLY the same as before)
        sex = self.sex_combo.currentText
        self.main_gui.last_prediction_sex = sex
        
        measurements = {}
        all_line_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
        for n in all_line_nodes:
            name = n.GetName()
            if name.startswith("N") and not name.startswith("Predicted_") and not name.startswith("True_"):
                suffix = name[1:]
                if suffix.isdigit():
                    meas = n.GetMeasurement('length')
                    if meas is not None: measurements[name] = meas.GetValue()
        
        pred_lengths = self.get_regressions(sex, measurements)

        for node in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
            if node.GetName().startswith("Predicted_"): slicer.mrmlScene.RemoveNode(node)

        hard_map = {
            "N17": "N4", "N18": "N5", "N19": "N5", "N20": "N6", "N21": "N7", "N22": "N7",
            "N45": "N34", "N46": "N34", "N47": "N34", "N48": "N34",
            "N49": "N7", "N50": "N7", "N51": "N7", "N52": "N7",
            "N69": "N34", "N70": "N34", "N71": "N34", "N72": "N34",
            "N73": "N7", "N74": "N7", "N75": "N7", "N76": "N7",
            "N41": "N30", "N42": "N30", "N43": "N30", "N44": "N30",
            "N65": "N54", "N66": "N54", "N67": "N54", "N68": "N54"
        }
        plane_map = {
            "N17":"Orbital", "N18":"Orbital", "N19":"Orbital", "N20":"Coronal", "N21":"Coronal", "N22":"Coronal",
            "N45":"Orbital","N46":"Orbital","N47":"Orbital","N48":"Orbital", "N49":"Coronal","N50":"Coronal","N51":"Coronal","N52":"Coronal",
            "N69":"Orbital","N70":"Orbital","N71":"Orbital","N72":"Orbital", "N73":"Coronal","N74":"Coronal","N75":"Coronal","N76":"Coronal",
            "N41":"Left Alare Sagittal", "N42":"Left Alare Sagittal", "N43":"Left Alare Sagittal", "N44":"Left Alare Sagittal",
            "N65":"Right Alare Sagittal", "N66":"Right Alare Sagittal", "N67":"Right Alare Sagittal", "N68":"Right Alare Sagittal"
        }
        
        hard_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
        if not hard_node:
            slicer.util.errorDisplay("Hard tissue node 'Ryu_hard_tissue' not found.")
            return

        for pred_name, length in pred_lengths.items():
            plane_node = slicer.mrmlScene.GetFirstNodeByName(plane_map[pred_name])
            if not plane_node: continue
            n = np.array(plane_node.GetNormal())
            o = np.array(plane_node.GetOrigin())
            
            num = int(pred_name[1:])
            start_lm = "N" if num <= 22 else "A_L" if num <= 52 else "A_R"
            
            start_pos = None
            for i in range(hard_node.GetNumberOfControlPoints()):
                if hard_node.GetNthControlPointLabel(i) == start_lm:
                    start_pos = np.array(hard_node.GetNthControlPointPosition(i)); break
            if start_pos is None: continue
            
            hard_line = slicer.mrmlScene.GetFirstNodeByName(hard_map[pred_name])
            if not hard_line or hard_line.GetNumberOfControlPoints() < 2: continue
            
            lm_pos = np.array(hard_line.GetNthControlPointPosition(0))
            proj_pos = np.array(hard_line.GetNthControlPointPosition(1))
            dir_vec = lm_pos - proj_pos
            norm_val = np.linalg.norm(dir_vec)
            if norm_val < 1e-6: continue
            dir_vec /= norm_val
            
            proj_pt = start_pos - np.dot(start_pos - o, n) * n
            end_pos = proj_pt + dir_vec * length
            
            line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"Predicted_{pred_name}")
            line.AddControlPoint(proj_pt); line.AddControlPoint(end_pos)
            line.GetMeasurement('length').SetEnabled(True)
            dn = _ensure_display_node(line)
            dn.SetColor(0, 0, 1)      # Blue
            dn.SetSelectedColor(0, 0, 1)
            
        self.main_gui.steps_completed['predicted_lengths'] = True
        slicer.util.infoDisplay("Blue predicted lines created.")
        self.close()

class RyuGUI:
    def __init__(self):
        self.main_widget = qt.QWidget(slicer.util.mainWindow())
        self.main_widget.setWindowFlags(qt.Qt.Tool)
        self.main_widget.setWindowTitle("Ryu et al. Prediction")
        self.main_widget.setMinimumSize(400, 200)
        self.vbox = qt.QVBoxLayout(self.main_widget)
        self.vbox.addWidget(qt.QLabel("<b>Ryu et al. (2020) Prediction</b>"))
        self.last_prediction_sex = None
        self.steps_completed = {"predicted_lengths": False}
        self.length_prediction_dialog = None
        
        self.btn_pred_len = qt.QPushButton("Step 1: Predict Blue Lines (Regression)")
        self.btn_pred_len.clicked.connect(self.launch_length_prediction)
        self.vbox.addWidget(self.btn_pred_len)
        
        self.btn_pred_lm = qt.QPushButton("Step 2: Create Pink Landmarks (Simultaneous)")
        self.btn_pred_lm.clicked.connect(self.create_predicted_landmarks)
        self.vbox.addWidget(self.btn_pred_lm)
        
        self.main_widget.show()

    def launch_length_prediction(self):
        if not self.length_prediction_dialog:
            self.length_prediction_dialog = LengthPredictionDialog(self, parent=self.main_widget)
        self.length_prediction_dialog.show()

    def get_landmark_pos(self, node, name):
        if not node: return None
        for i in range(node.GetNumberOfControlPoints()):
            if node.GetNthControlPointLabel(i) == name:
                return np.array(node.GetNthControlPointPosition(i))
        return None

    def create_predicted_landmarks(self):
        if self.last_prediction_sex is None:
            slicer.util.errorDisplay("Run Step 1 first.")
            return

        hard_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
        if not hard_node: return

        planes = {}
        for p_name in ["Midsagittal", "Orbital", "Coronal"]:
            p_node = slicer.mrmlScene.GetFirstNodeByName(p_name)
            if not p_node:
                slicer.util.errorDisplay(f"Plane {p_name} not found!")
                return
            planes[p_name] = p_node
            
        origins = {n: np.array(p.GetOrigin()) for n, p in planes.items()}
        normals = {n: np.array(p.GetNormal()) for n, p in planes.items()}
        
        # Critical Override: Force Midsagittal normal to point Right (+X)
        if normals["Midsagittal"][0] < 0:
            normals["Midsagittal"] *= -1

        midsag_origin = origins.get("Midsagittal")
        midsag_normal = normals.get("Midsagittal")
        
        node_name = f"Predicted_Soft_Tissue_{self.last_prediction_sex}"
        pred_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", node_name)
        pred_node.RemoveAllControlPoints()
        dn = _ensure_display_node(pred_node)
        dn.SetColor(1, 0.4, 0.7); dn.SetSelectedColor(1, 0.4, 0.7) # Pink

        landmark_defs = {
            "S": ("N", ["N8", "N17", "N20"]), "PN": ("N", ["N11", "N18", "N21"]), "SN": ("N", ["N14", "N19", "N22"]),
            "ACS_L": ("A_L", ["N41", "N45", "N49"]), "ACP_L": ("A_L", ["N42", "N46", "N50"]),
            "NA_L": ("A_L", ["N43", "N47", "N51"]), "ACI_L": ("A_L", ["N44", "N48", "N52"]),
            "ACS_R": ("A_R", ["N65", "N69", "N73"]), "ACP_R": ("A_R", ["N66", "N70", "N74"]),
            "NA_R": ("A_R", ["N67", "N71", "N75"]), "ACI_R": ("A_R", ["N68", "N72", "N76"])
        }
        plane_map = {
            "N8":"Midsagittal","N17":"Orbital","N20":"Coronal", "N11":"Midsagittal","N18":"Orbital","N21":"Coronal",
            "N14":"Midsagittal","N19":"Orbital","N22":"Coronal", "N41":"Midsagittal","N45":"Orbital","N49":"Coronal",
            "N42":"Midsagittal","N46":"Orbital","N50":"Coronal", "N43":"Midsagittal","N47":"Orbital","N51":"Coronal",
            "N44":"Midsagittal","N48":"Orbital","N52":"Coronal", "N65":"Midsagittal","N69":"Orbital","N73":"Coronal",
            "N66":"Midsagittal","N70":"Orbital","N74":"Coronal", "N67":"Midsagittal","N71":"Orbital","N75":"Coronal",
            "N68":"Midsagittal","N72":"Orbital","N76":"Coronal"
        }

        def get_pred_dist(code):
            line = slicer.mrmlScene.GetFirstNodeByName(f"Predicted_{code}")
            if not line or line.GetNumberOfControlPoints() < 2: return None
            return line.GetMeasurement('length').GetValue()

        for lm, (start_lm, codes) in landmark_defs.items():
            start_pos = self.get_landmark_pos(hard_node, start_lm)
            if start_pos is None: continue

            side_sign = 1
            if start_lm == "A_L": side_sign = -1
            elif start_lm == "A_R": side_sign = 1

            dist_dict = {p: 0.0 for p in ["Midsagittal", "Orbital", "Coronal"]}
            valid = 0
            
            for code in codes:
                plane = plane_map.get(code)
                if plane:
                    d = get_pred_dist(code)
                    if d is not None and d > 0.1:
                        dist_dict[plane] = d * side_sign if plane == "Midsagittal" else d
                        valid += 1
            
            # Fallback for lateral offset (applies side_sign)
            if abs(dist_dict["Midsagittal"]) < 0.1:
                lateral_offset = np.dot(start_pos - midsag_origin, midsag_normal)
                dist_dict["Midsagittal"] = side_sign * lateral_offset
            
            # Midline landmarks have 0 lateral offset
            if lm in ["S", "PN", "SN"]: dist_dict["Midsagittal"] = 0.0
            
            # --- CRITICAL EXCEPTION FOR SELION ---
            # Orbital plane points DOWN (-Z). Adding pushes down, Subtracting pushes UP (Superior).
            if lm == "S" and dist_dict["Orbital"] != 0.0:
                dist_dict["Orbital"] = -1.0 * dist_dict["Orbital"]
            # -------------------------------------
            
            if valid >= 2:
                final_pos = np.zeros(3)
                for p_name, dist_val in dist_dict.items():
                    o = origins[p_name]
                    n_vec = normals[p_name]
                    if o is not None and n_vec is not None:
                        scalar = np.dot(o, n_vec) + dist_val
                        final_pos += scalar * n_vec
                pred_node.AddControlPoint(final_pos, lm)
            else:
                print(f"Skipping {lm} (insufficient predicted distances)")
        slicer.util.infoDisplay("Pink landmarks created.")


# ==========================================
# CLEANUP & RUN - 100% SAFE
# ==========================================
if 'ryu_gui_instance' in globals() and ryu_gui_instance is not None:
    try:
        if hasattr(ryu_gui_instance, 'main_widget') and ryu_gui_instance.main_widget:
            try: ryu_gui_instance.main_widget.close()
            except: pass
        if hasattr(ryu_gui_instance, 'length_prediction_dialog') and ryu_gui_instance.length_prediction_dialog:
            try: ryu_gui_instance.length_prediction_dialog.close()
            except: pass
    except Exception:
        pass
    del ryu_gui_instance

ryu_gui_instance = RyuGUI()

```

</details>

You can expect a window to pop up asking you to choose a biological sex for predictions - this is due to the original paper providing sexually dimorphic equations.

<img width="616" height="355" alt="image" src="https://github.com/user-attachments/assets/cf7ba9ef-c180-482c-883e-628870a98f92" />

Once you chose and clicked the "Predict Lengths and Create Lines" button, the following should show up: 

<img src="https://github.com/user-attachments/assets/5a0e0d27-cf0e-45fc-8a4e-aa54a9ed565f" width="500">

Then, click the "Step 2" button to show the predicted soft tissue landmarks


<img src="https://github.com/user-attachments/assets/40f2ba16-6286-4b46-81f0-0524a5f47a8e" width="500">

The code will produce predicted linear measurement and a new point list called **Predicted_Soft_Landmarks** containing the predicted landmarks.

If you want to see how the prediction is created, copy and paste the following code: 

<details>
<summary> Code to visualise bilateral soft tissue landmark (ACP_L) prediction </summary>

``` python
# ---------------------------
# Bilateral ACP_L Visualization (CORRECTED)
# ---------------------------
def visualize_acpl_simultaneous():
    for n in slicer.util.getNodesByClass('vtkMRMLMarkupsNode'):
        if n.GetName().startswith('Step_ACP_L_') or n.GetName().startswith('Path_ACP_L_'): slicer.mrmlScene.RemoveNode(n)
    
    line_lat = slicer.mrmlScene.GetFirstNodeByName("Predicted_N42")
    line_orb = slicer.mrmlScene.GetFirstNodeByName("Predicted_N46")
    line_cor = slicer.mrmlScene.GetFirstNodeByName("Predicted_N50")
    if not (line_lat and line_orb and line_cor):
        return print("Predicted lines not found.")

    d_lat = line_lat.GetMeasurement('length').GetValue()
    d_orb = line_orb.GetMeasurement('length').GetValue()
    d_cor = line_cor.GetMeasurement('length').GetValue()

    planes = {n: slicer.mrmlScene.GetFirstNodeByName(n) for n in ["Midsagittal", "Orbital", "Coronal"]}
    if None in planes.values(): return print("Planes missing!")
    origins = {n: np.array(p.GetOrigin()) for n, p in planes.items()}
    normals = {n: np.array(p.GetNormal()) for n, p in planes.items()}
    dist = {"Midsagittal": -1.0 * d_lat, "Orbital": d_orb, "Coronal": d_cor}
    
    final_pos = np.zeros(3)
    for p, d in dist.items(): final_pos += (np.dot(origins[p], normals[p]) + d) * normals[p]
    
    # --- CORRECTED SAFE LOOKUP FOR A_L ---
    hard_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
    a_l = None
    if hard_node:
        for i in range(hard_node.GetNumberOfControlPoints()):
            if hard_node.GetNthControlPointLabel(i) == "A_L":
                a_l = np.array(hard_node.GetNthControlPointPosition(i))
                break
    if a_l is None:
        a_l = np.zeros(3)
    # -------------------------------------

    for p, d in dist.items():
        o, n = origins[p], normals[p]
        proj = o + (a_l - o) - np.dot(a_l - o, n) * n
        offset = proj + n * d
        line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"Step_ACP_L_Line_{p}")
        line.AddControlPoint(proj); line.AddControlPoint(offset)
        dn = _ensure_display_node(line)
        dn.SetColor(1, 0.5, 0); dn.SetSelectedColor(1, 0.5, 0)  # Orange
    
    final = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Step_ACP_L_Final")
    final.AddControlPoint(final_pos)
    dn = _ensure_display_node(final)
    dn.SetColor(1, 0, 0); dn.SetSelectedColor(1, 0, 0)  # Red
    print(f"Final ACP_L (Simultaneous): {final_pos}")

visualize_acpl_simultaneous()
```

</details>

<img width="2757" height="2393" alt="help2" src="https://github.com/user-attachments/assets/d61e86f1-177d-440b-868b-88d2484607d7" />


Please note that the equation for calculating N42 is not in the main body of text in the original article, but to be found in Supplementary material C. 


<details>
<summary> Code to visualise midline soft tissue landmark (pronasale) prediction </summary>
  
``` python
import slicer
import numpy as np

def _ensure_display_node(node):
    dn = node.GetDisplayNode()
    if not dn:
        dn = node.CreateDefaultDisplayNodes()
    return dn

# ---------------------------
# Midline PN Visualization
# ---------------------------
def visualize_pn_simultaneous():
    for n in slicer.util.getNodesByClass('vtkMRMLMarkupsNode'):
        if n.GetName().startswith('Step_PN_') or n.GetName().startswith('Path_PN_'): slicer.mrmlScene.RemoveNode(n)
    
    line_orb = slicer.mrmlScene.GetFirstNodeByName("Predicted_N18")
    line_cor = slicer.mrmlScene.GetFirstNodeByName("Predicted_N21")
    if not line_orb or not line_cor:
        return print("Predicted_N18/N21 not found. Run Step 1.")

    d_orb = line_orb.GetMeasurement('length').GetValue()
    d_cor = line_cor.GetMeasurement('length').GetValue()

    planes = {n: slicer.mrmlScene.GetFirstNodeByName(n) for n in ["Midsagittal", "Orbital", "Coronal"]}
    if None in planes.values():
        return print("Planes missing!")
    origins = {n: np.array(p.GetOrigin()) for n, p in planes.items()}
    normals = {n: np.array(p.GetNormal()) for n, p in planes.items()}
    dist = {"Midsagittal": 0.0, "Orbital": d_orb, "Coronal": d_cor}
    
    final_pos = np.zeros(3)
    for p, d in dist.items(): final_pos += (np.dot(origins[p], normals[p]) + d) * normals[p]
    
    hard_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_hard_tissue")
    nasion = np.array(hard_node.GetNthControlPointPosition(0)) if hard_node else np.zeros(3)

    for p, d in dist.items():
        o, n = origins[p], normals[p]
        proj = o + (nasion - o) - np.dot(nasion - o, n) * n
        offset = proj + n * d
        line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"Step_PN_Line_{p}")
        line.AddControlPoint(proj); line.AddControlPoint(offset)
        dn = _ensure_display_node(line)
        dn.SetColor(1, 0.5, 0); dn.SetSelectedColor(1, 0.5, 0)  # Orange
    
    final = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Step_PN_Final")
    final.AddControlPoint(final_pos)
    dn = _ensure_display_node(final)
    dn.SetColor(1, 0, 0); dn.SetSelectedColor(1, 0, 0)  # Red
    print(f"Final PN (Simultaneous): {final_pos}")

visualize_pn_simultaneous()

```

</details>


<img width="3746" height="2365" alt="help1" src="https://github.com/user-attachments/assets/06857534-226a-4f83-a5af-f05cbdb2cb3a" />




### Measuring the prediction errors

To establish the difference between the predicted and true measurments as well as the placement of the predicted soft tissue landmarks to the true soft tissue landmarks, allocate the contents of the _Ryu_soft_tissue.mrk.json_. 


The following code will create the true soft tissue measurements based on the true soft tissue landmarks (N8-N22, N25, N27, N41-52, N54, N58, N62, N65-76) and draws a line between the predicted soft tissue landmark stored in "Predicted_Soft_Landmarks" and the true landmarks in "Ryu_soft_tissue". 

| Measurement Code | Landmark                  | Name in "Ryu_soft_tissue" | Landmark Tissue Type | Plane Name in Scene      |
|------------------|--------------------------|---------------------------|---------------------|-------------------------|
| N8               | Selion                   | S                         | soft                | Midsagittal             |
| N9               | Selion                   | S                         | soft                | Left Alare Sagittal     |
| N10              | Selion                   | S                         | soft                | Right Alare Sagittal    |
| N11              | Pronasale                | PN                        | soft                | Midsagittal             |
| N12              | Pronasale                | PN                        | soft                | Left Alare Sagittal     |
| N13              | Pronasale                | PN                        | soft                | Right Alare Sagittal    |
| N14              | Subnasale                | SN                        | soft                | Midsagittal             |
| N15              | Subnasale                | SN                        | soft                | Left Alare Sagittal     |
| N16              | Subnasale                | SN                        | soft                | Right Alare Sagittal    |
| N17              | Selion                   | S                         | soft                | Orbital                 |
| N18              | Pronasale                | PN                        | soft                | Orbital                 |
| N19              | Subnasale                | SN                        | soft                | Orbital                 |
| N20              | Selion                   | S                         | soft                | Coronal                 |
| N21              | Pronasale                | PN                        | soft                | Coronal                 |
| N22              | Subnasale                | SN                        | soft                | Coronal                 |
| N25              | Selion                   | S                         | soft                | Rhinion                 |
| N27              | Subnasale                | SN                        | soft                | Rhinion                 |
| N41              | Left Alar curvature superior   | ACS_L                | soft                | Midsagittal             |
| N42              | Left Alar curvature posterior  | ACP_L                | soft                | Midsagittal             |
| N43              | Left Nose Alare               | NA_L                 | soft                | Midsagittal             |
| N44              | Left Alar curvature inferior   | ACI_L                | soft                | Midsagittal             |
| N45              | Left Alar curvature superior   | ACS_L                | soft                | Orbital                 |
| N46              | Left Alar curvature posterior  | ACP_L                | soft                | Orbital                 |
| N47              | Left Nose Alare               | NA_L                 | soft                | Orbital                 |
| N48              | Left Alar curvature inferior   | ACI_L                | soft                | Orbital                 |
| N49              | Left Alar curvature superior   | ACS_L                | soft                | Coronal                 |
| N50              | Left Alar curvature posterior  | ACP_L                | soft                | Coronal                 |
| N51              | Left Nose Alare               | NA_L                 | soft                | Coronal                 |
| N52              | Left Alar curvature inferior   | ACI_L                | soft                | Coronal                 |
| N54              | Right Nose Alare              | NA_R                 | soft                | Midsagittal             |
| N58              | Right Nose Alare              | NA_R                 | soft                | Orbital                 |
| N62              | Right Nose Alare              | NA_R                 | soft                | Coronal                 |
| N65              | Right Alar curvature superior  | ACS_R                | soft                | Midsagittal             |
| N66              | Right Alar curvature posterior | ACP_R                | soft                | Midsagittal             |
| N67              | Right Nose Alare              | NA_R                 | soft                | Midsagittal             |
| N68              | Right Alar curvature inferior  | ACI_R                | soft                | Midsagittal             |
| N69              | Right Alar curvature superior  | ACS_R                | soft                | Orbital                 |
| N70              | Right Alar curvature posterior | ACP_R                | soft                | Orbital                 |
| N71              | Right Nose Alare              | NA_R                 | soft                | Orbital                 |
| N72              | Right Alar curvature inferior  | ACI_R                | soft                | Orbital                 |
| N73              | Right Alar curvature superior  | ACS_R                | soft                | Coronal                 |
| N74              | Right Alar curvature posterior | ACP_R                | soft                | Coronal                 |
| N75              | Right Nose Alare              | NA_R                 | soft                | Coronal                 |
| N76              | Right Alar curvature inferior  | ACI_R                | soft                | Coronal                 |

<details>
<summary>Code for creating the true soft tissue measurements</summary>

```python
import slicer
import numpy as np

def _ensure_display_node(node):
    dn = node.GetDisplayNode()
    if not dn:
        dn = node.CreateDefaultDisplayNodes()
    return dn

def create_true_soft_tissue_measurements():
    # Get nodes
    soft_tissue_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_soft_tissue")
    if not soft_tissue_node:
        return print("Error: 'Ryu_soft_tissue' not found. Please load the soft tissue landmarks.")

    # Define soft tissue measurements based on your provided list
    soft_tissue_measurements = [
        ("N8", "S", "Midsagittal"), ("N9", "S", "Left Alare Sagittal"), ("N10", "S", "Right Alare Sagittal"),
        ("N11", "PN", "Midsagittal"), ("N12", "PN", "Left Alare Sagittal"), ("N13", "PN", "Right Alare Sagittal"),
        ("N14", "SN", "Midsagittal"), ("N15", "SN", "Left Alare Sagittal"), ("N16", "SN", "Right Alare Sagittal"),
        ("N17", "S", "Orbital"), ("N18", "PN", "Orbital"), ("N19", "SN", "Orbital"),
        ("N20", "S", "Coronal"), ("N21", "PN", "Coronal"), ("N22", "SN", "Coronal"),
        ("N25", "S", "Rhinion"), ("N27", "SN", "Rhinion"),
        ("N41", "ACS_L", "Midsagittal"), ("N42", "ACP_L", "Midsagittal"), ("N43", "NA_L", "Midsagittal"), ("N44", "ACI_L", "Midsagittal"),
        ("N45", "ACS_L", "Orbital"), ("N46", "ACP_L", "Orbital"), ("N47", "NA_L", "Orbital"), ("N48", "ACI_L", "Orbital"),
        ("N49", "ACS_L", "Coronal"), ("N50", "ACP_L", "Coronal"), ("N51", "NA_L", "Coronal"), ("N52", "ACI_L", "Coronal"),
        ("N54", "NA_R", "Midsagittal"), ("N58", "NA_R", "Orbital"), ("N62", "NA_R", "Coronal"),
        ("N65", "ACS_R", "Midsagittal"), ("N66", "ACP_R", "Midsagittal"), ("N67", "NA_R", "Midsagittal"), ("N68", "ACI_R", "Midsagittal"),
        ("N69", "ACS_R", "Orbital"), ("N70", "ACP_R", "Orbital"), ("N71", "NA_R", "Orbital"), ("N72", "ACI_R", "Orbital"),
        ("N73", "ACS_R", "Coronal"), ("N74", "ACP_R", "Coronal"), ("N75", "NA_R", "Coronal"), ("N76", "ACI_R", "Coronal")
    ]

    missing_landmarks = set()
    missing_planes = set()
    created_count = 0

    for line_name, landmark_name, plane_name in soft_tissue_measurements:
        point = None
        for i in range(soft_tissue_node.GetNumberOfControlPoints()):
            if soft_tissue_node.GetNthControlPointLabel(i) == landmark_name:
                point = np.array(soft_tissue_node.GetNthControlPointPosition(i))
                break

        if point is None:
            missing_landmarks.add(landmark_name)
            continue

        plane_node = slicer.mrmlScene.GetFirstNodeByName(plane_name)
        if plane_node is None:
            missing_planes.add(plane_name)
            continue

        # Create the line
        line_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", line_name)
        
        # Calculate projected point
        plane_normal = np.array(plane_node.GetNormal())
        plane_origin = np.array(plane_node.GetOrigin())
        v = point - plane_origin
        distance = np.dot(v, plane_normal)
        projected_point = point - distance * plane_normal
        
        # Add points
        line_node.AddControlPoint(point)
        line_node.AddControlPoint(projected_point)
        
        # Configure line
        line_node.GetMeasurement('length').SetEnabled(True)
        
        # Force Color to Green (0, 1, 0)
        dn = _ensure_display_node(line_node)
        dn.SetColor(0, 1, 0)
        dn.SetSelectedColor(0, 1, 0)
        
        created_count += 1

    print(f"\n--- Results ---")
    print(f"Created {created_count} true soft tissue measurement lines (Green).")
    if missing_landmarks:
        print(f"Missing {len(missing_landmarks)} landmarks in Ryu_soft_tissue:")
        for name in sorted(missing_landmarks): print(f" - {name}")
    if missing_planes:
        print(f"Missing {len(missing_planes)} planes: {sorted(missing_planes)}")

# Execute
create_true_soft_tissue_measurements()

```

</details>

<img width="670" height="640" alt="image" src="https://github.com/user-attachments/assets/99965c92-be36-42fa-bdf6-5326f97cc738" />


<details>
<summary>Code for comparing the true vs predicted soft tissue landmarks </summary>

```python
import slicer
import numpy as np

def _ensure_display_node(node):
    dn = node.GetDisplayNode()
    if not dn:
        dn = node.CreateDefaultDisplayNodes()
    return dn

def measure_prediction_errors():
    true_node = slicer.mrmlScene.GetFirstNodeByName("Ryu_soft_tissue")
    pred_nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if "Predicted_Soft_Tissue" in n.GetName()]
    
    if not true_node:
        return print("Error: Please allocate the soft tissue landmarks (Ryu_soft_tissue) first.")
    if not pred_nodes:
        return print("Error: Please run Step 2 in the GUI to generate the predicted pink landmarks first.")
    
    pred_node = pred_nodes[-1]
    
    # Clear any previous error lines
    for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode"):
        if n.GetName().startswith("error_"): slicer.mrmlScene.RemoveNode(n)

    def get_pos(node, label):
        for i in range(node.GetNumberOfControlPoints()):
            if node.GetNthControlPointLabel(i) == label:
                return np.array(node.GetNthControlPointPosition(i))
        return None

    print("\n--- Calculating Prediction Errors ---")
    for i in range(true_node.GetNumberOfControlPoints()):
        label = true_node.GetNthControlPointLabel(i)
        true_pos = get_pos(true_node, label)
        pred_pos = get_pos(pred_node, label)
        
        if true_pos is not None and pred_pos is not None:
            dist = np.linalg.norm(pred_pos - true_pos)
            
            line = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", f"error_{label}")
            line.AddControlPoint(true_pos)
            line.AddControlPoint(pred_pos)
            line.GetMeasurement('length').SetEnabled(True)
            
            dn = _ensure_display_node(line)
            dn.SetColor(0.5, 0, 0.125); dn.SetSelectedColor(0.7, 0, 0.175)  # Burgundy
            
            print(f"Error for {label}: {dist:.2f} mm")
        else:
            print(f"Warning: Could not find predicted landmark for {label}")

measure_prediction_errors()

```

</details>



The picture below shows the distances between true and predicted soft tissue measurements:


<img width="915" height="1099" alt="image" src="https://github.com/user-attachments/assets/d28abc6e-e5f3-41cc-aa99-ec1487dba814" />



## Output
Below is a table of measurements to be expected once the linear measurements of the scene are copied onto the clipboard [Guide to copy measurements to clipboard](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/004_Copy%20measurements%20to%20clipboard.md#content-summary)


<details>
<summary>Example output </summary>

| ID         | measurement     | in mm        |
|------------|----------------|--------------|
| (none)     | N1             | 0.51         |
| (none)     | N2             | 12.17        |
| (none)     | N3             | 14.12        |
| (none)     | N4             | 27.98        |
| (none)     | N5             | 22.44        |
| (none)     | N6             | 110.30       |
| (none)     | N7             | 109.53       |
| (none)     | N28            | 120.52       |
| (none)     | N29            | 11.16        |
| (none)     | N30            | 12.69        |
| (none)     | N31            | 14.10        |
| (none)     | N32            | 6.37         |
| (none)     | N33            | 4.08         |
| (none)     | N34            | 11.82        |
| (none)     | N35            | 15.22        |
| (none)     | N36            | 20.20        |
| (none)     | N37            | 103.93       |
| (none)     | N38            | 101.38       |
| (none)     | N39            | 98.85        |
| (none)     | N40            | 104.05       |
| (none)     | N53            | 12.27        |
| (none)     | N54            | 13.61        |
| (none)     | N55            | 14.06        |
| (none)     | N56            | 5.32         |
| (none)     | N57            | 6.07         |
| (none)     | N59            | 15.35        |
| (none)     | N60            | 20.43        |
| (none)     | N61            | 104.24       |
| (none)     | N63            | 99.74        |
| (none)     | N64            | 103.79       |
| (none)     | Predicted_N17  | 22.17        |
| (none)     | Predicted_N18  | 13.58        |
| (none)     | Predicted_N19  | 26.23        |
| (none)     | Predicted_N20  | 113.86       |
| (none)     | Predicted_N21  | 129.85       |
| (none)     | Predicted_N22  | 116.35       |
| (none)     | Predicted_N45  | 6.08         |
| (none)     | Predicted_N69  | 6.89         |
| (none)     | Predicted_N46  | 14.49        |
| (none)     | Predicted_N70  | 15.21        |
| (none)     | Predicted_N47  | 16.77        |
| (none)     | Predicted_N71  | 16.90        |
| (none)     | Predicted_N48  | 24.06        |
| (none)     | Predicted_N72  | 24.11        |
| (none)     | Predicted_N49  | 108.41       |
| (none)     | Predicted_N73  | 108.11       |
| (none)     | Predicted_N50  | 103.90       |
| (none)     | Predicted_N74  | 104.91       |
| (none)     | Predicted_N51  | 109.15       |
| (none)     | Predicted_N75  | 109.08       |
| (none)     | Predicted_N52  | 109.98       |
| (none)     | Predicted_N76  | 110.29       |
| (none)     | Predicted_N41  | 14.71        |
| (none)     | Predicted_N42  | 21.14        |
| (none)     | Predicted_N43  | 20.75        |
| (none)     | Predicted_N44  | 14.82        |
| (none)     | Predicted_N65  | 0.00         |
| (none)     | Predicted_N66  | 21.88        |
| (none)     | Predicted_N67  | 21.38        |
| (none)     | Predicted_N68  | 15.36        |
| (none)     | N8             | 1.26         |
| (none)     | N9             | 11.43        |
| (none)     | N10            | 14.87        |
| (none)     | N11            | 0.91         |
| (none)     | N12            | 11.78        |
| (none)     | N13            | 14.52        |
| (none)     | N14            | 0.58         |
| (none)     | N15            | 12.11        |
| (none)     | N16            | 14.19        |
| (none)     | N17            | 24.48        |
| (none)     | N18            | 16.54        |
| (none)     | N19            | 26.40        |
| (none)     | N20            | 116.95       |
| (none)     | N21            | 138.50       |
| (none)     | N22            | 120.94       |
| (none)     | N25            | 13.13        |
| (none)     | N27            | 37.75        |
| (none)     | N41            | 18.54        |
| (none)     | N42            | 19.77        |
| (none)     | N43            | 17.91        |
| (none)     | N44            | 12.61        |
| (none)     | N45            | 14.79        |
| (none)     | N46            | 19.17        |
| (none)     | N47            | 19.16        |
| (none)     | N48            | 24.60        |
| (none)     | N49            | 115.36       |
| (none)     | N50            | 113.58       |
| (none)     | N51            | 118.68       |
| (none)     | N52            | 114.30       |
| (none)     | N54            | 16.31        |
| (none)     | N58            | 18.56        |
| (none)     | N62            | 120.50       |
| (none)     | N65            | 15.00        |
| (none)     | N66            | 18.27        |
| (none)     | N67            | 16.31        |
| (none)     | N68            | 11.33        |
| (none)     | N69            | 12.63        |
| (none)     | N70            | 18.62        |
| (none)     | N71            | 18.56        |
| (none)     | N72            | 24.60        |
| (none)     | N73            | 116.04       |
| (none)     | N74            | 117.69       |
| (none)     | N75            | 120.50       |
| (none)     | N76            | 115.82       |
| (none)     | error_S        | 4.06         |
| (none)     | error_PN       | 9.19         |
| (none)     | error_SN       | 4.63         |
| (none)     | error_ACS_L    | 11.78        |
| (none)     | error_ACS_R    | 9.89         |
| (none)     | error_ACP_L    | 10.84        |
| (none)     | error_ACP_R    | 13.71        |
| (none)     | error_NA_L     | 10.23        |
| (none)     | error_NA_R     | 12.61        |
| (none)     | error_ACI_L    | 4.88         |
| (none)     | error_ACI_R    | 6.86         |
</details>


#### Research ideas


As noticed during the implementation of the method, the predicted lengths on soft tissue measurements are close to the true measurement, but misplaced - the only reference for their placements are the hard tissue landmark and plane, but not any other position of the line within the plane - this could be investigated by using the [Thitiorul (2020) method](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Thitiorul2020.md) that takes the 3d coordinates of the landmarks to create prediction equations. 


As the original  Ryu et al. 2020[^2] method featured participants of Korean ancestry, other populations may have slightly different relationships between the same measurements/landmarks - therefore investigating whether a "recalibration" (see [Rynn's method](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Rynn's%20(2010)%20method.md)) for other populations is necessary. 


# Bibliography

[^1]: 3D Slicer webpage https://www.slicer.org/
[^2]: Ryu, J. Y., et al. (2020). "Craniofacial anthropometric investigation of relationships between the nose and nasal aperture using 3D computed tomography of Korean subjects." Scientific Reports 10(1): 16077.
[^3]: Ridel et al. (2018). "Skeletal dimensions as predictors for the shape of the nose in a South African sample: A cone-beam computed tomography (CBCT) study." Forensic Science International 289: 18-26.
[^4]: Lee, K.-M., et al. (2014). "Three-dimensional prediction of the nose for facial reconstruction using cone-beam computed tomoraphy." Forensic Science International 236: 194.e191-194.e195.
[^5]: Caple, J. and C. N. Stephan (2016). "A standardized nomenclature for craniofacial and facial anthropometry." International Journal of Legal Medicine 130(3): 863-879.
[^6]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^7]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^8]: Pittayapat, P., et al. (2017). "Three-dimensional Frankfort horizontal plane for 3D cephalometry: a comparative assessment of conventional versus novel landmarks and horizontal planes." European Journal of Orthodontics 40(3): 239-248.
[^9]: Howells, W. W. (1937). "The designation of the principle anthrometric landmarks on the head and skull." American Journal of Physical Anthropology 22(3): 477-494.
[^10]: Howells, W. W. (1974). Cranial variation in man: A study by multivariate analysis of patterns of difference among recent human populations. Cambridge, Harvard University.
[^11]: Kolar, J. and E. Salter (1997). Craniofacial anthropometry: practical measurement of the head and face for clinical, surgical, and research use. Springfield, Charles C Thomas.
[^12]: Farkas, L. G. (1994). Anthropometry of the Head and Face, Lippincott Williams & Wilkins.	
[^13]: Buikstra, J. E. and D. H. Ubelaker (1994). Standards for data collection from human skeletal remains. Fayetteville: Arkansas.
Howells (1937)[^9]; Howells (1974)[^10]; Caple & Stephan (2016)[^5]

