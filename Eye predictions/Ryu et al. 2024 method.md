# The Ryu et al. (2024)[^2] method 

The following guide is constructed by the available original study by Ryu et al. (2024)[^2].

The original method was carried out on post-mortem CTs on a population of 171 Korean adults. It devised multple linear regressions to place the most anterior point of the eyeball in 3 dimensions in relation to the bony orbit, with slightly different definitions for orbital breadth and height. 

## Table of Contents

> [!WARNING]
> The sample CT (CBCT PreDentalSurgery) used in the screenshots of this guide does not have all the features (bregma) that are to be landmarked. Please refer to the illustrations in the guide for correct placement. In addition, due to the CT being taken pre-surgery for an underbite, the error rate shown in the guide is probably not representative if implemented on a population without pathologies.



## Landmarks in this guide: 

| Position in code | Position in file | Name in file | Landmark | Definition | defined by | tissue type |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | 1 | n | Nasion | The junction of the internasal suture with the nasofrontal suture | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 1 | 2 | pr | Prosthion | The lowermost point of the intermaxillary suture between the central incisors of the maxilla. | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 2 | 3 | auL | Auriculare (left) | On the LEFT zygomatic root, vertically above the center of the external auditory meatus | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 3 | 4 | auR | Auriculare (right) | On the RIGHT zygomatic root, vertically above the center of the external auditory meatus | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 4 | 5 | mid_au | Auriculare Midpoint | The midpoint in the 3D coordinates of both AU | Ryu et al. 2024 [^2] | hard |
| 5 | 6 | orL | Orbitale (left) | The lowest point on the LEFT orbital rim | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 6 | 7 | orR | Orbitale (right) | The lowest point on the RIGHT orbital rim | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 7 | 8 | b | Bregma | Where the sagittal and coronal sutures meet | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 8 | 9 | g | Glabella | Most projecting anterior median point on lower edge of the frontal bone, on the brow ridge, in between the superciliary arches and above the nasal root. | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 9 | 10 | lat_orL | Lateral Orbitale (left) | Most lateral point on the left orbital rim | Ryu et al. 2024 [^2] | hard |
| 10 | 11 | lat_orR | Lateral Orbitale (right) | Most lateral point on the RIGHT orbital rim | Ryu et al. 2024 [^2] | hard |
| 11 | 12 | dL | Median Orbitale (left) | The point where the LEFT anterior lacrimal ridge meets frontonasal suture(=dacryion) | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 12 | 13 | dR | Median Orbitale (right) | The point where the RIGHT anterior lacrimal ridge meets frontonasal suture | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 13 | 14 | skL | Supra Orbitale (left) | The most upper point on the LEFT orbital rim | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 14 | 15 | skR | Supra Orbitale (right) | The most upper point on the RIGHT orbital rim | Martin, 1928 [^3]; Knussmann, 1988 [^4] | hard |
| 15 | 16 | ocpR | Optic Canal Point (right) | Uppermost point of the RIGHT optic nerve canal | Ryu et al. 2024 [^2] | hard |
| 16 | 17 | ocpL | Optic Canal Point (left) | Uppermost point of the LEFT optic nerve canal | Ryu et al. 2024 [^2] | hard |
| 17 | 18 | 🟦lcL | Lens Centre (left) | The center of gravity of the left lens (sic!)- geometric mean | Ryu et al. 2024 [^2] | soft |
| 18 | 19 | 🟦lcR | Lens Centre (right) | The center of gravity of the right lens (sic!)- geometric mean | Ryu et al. 2024 [^2] | soft |
| 19 | 20 | 🟦laL | Lens Anterior (left) | The most anterior point of the LEFT lens | Ryu et al. 2024 [^2] | soft |
| 20 | 21 | 🟦laR | Lens Anterior (right) | The most anterior point of the RIGHT lens | Ryu et al. 2024 [^2] | soft |
| 21 | 22 | 🟦lpL | Lens Posterior (left) | The most posterior point of the LEFT lens | Ryu et al. 2024 [^2] | soft |
| 22 | 23 | 🟦lpR | Lens Posterior (right) | The most posterior point of the RIGHT lens | Ryu et al. 2024 [^2] | soft |
| 23 | 24 | 🟦osL | Globe Superior (left) | The uppermost point of the LEFT eyeball | Guyomarc'h, 2012 [^5] | soft |
| 24 | 25 | 🟦osR | Globe Superior (right) | The uppermost point of the RIGHTeyeball | Guyomarc'h, 2012 [^5] | soft |
| 25 | 26 | 🟦oiL | Globe Inferior (left) | The lowest point of the LEFT eyeball | Guyomarc'h, 2012 [^5] | soft |
| 26 | 27 | 🟦oiR | Globe Inferior (right) | The lowest point of the RIGHT eyeball | Guyomarc'h, 2012 [^5] | soft |
| 27 | 28 | 🟦opL | Globe Lateral (left) | The most lateral point of the LEFT eyeball | Guyomarc'h, 2012 [^5] | soft |
| 28 | 29 | 🟦opR | Globe Lateral (right) | The most lateral point of the RIGHT eyeball | Guyomarc'h, 2012 [^5] | soft |
| 29 | 30 | 🟦omL | Globe Medial (left) | The most medial mole (sic!) of the LEFT eyeball. | Ryu et al. 2024 [^2] | soft |
| 30 | 31 | 🟦omR | Globe Medial (right) | The most medial mole (sic!) of the RIGHT eyeball. | Ryu et al. 2024 [^2] | soft |
| 31 | 32 | 🟦oaL | Cornea (left) | The most anterior point of the LEFT eyeball | originally undefined! | soft |
| 32 | 33 | 🟦oaR | Cornea (right) | The most anterior point of the RIGHT eyeball | originally undefined! | soft |
| 33 | 34 | 🟦pL | if available, left pupulare | IF DISTINGUISHABLE, Centre of the LEFT pupil | ADDITIONAL | soft |
| 34 | 35 | 🟦pR | if available, right pupulare | IF DISTINGUISHABLE, Centre of the RIGHT pupil | ADDITIONAL | soft |
| 35 | 36 | 🟦gcL | left globe centre | calculated programmatically | originally undefined! | soft |
| 36 | 37 | 🟦gcR | right globe centre | calculated programmatically | originally undefined! | soft |

[Ryu_soft_tissue.mrk.json](https://github.com/user-attachments/files/28473452/Ryu_soft_tissue.mrk.json)
[Ryu_hard_tissue.mrk.json](https://github.com/user-attachments/files/28473451/Ryu_hard_tissue.mrk.json)



> [!IMPORTANT]
> The landmarks with the 🟦 symbol are for reproducing the entire method for validation and not essential to place for applying the eyeball placement for facial approximation.

Illustration of the method: 


> [!WARNING]
> Before you proceed, please make sure you completed the following steps: 

- [ ] The scan has to be re-aligned in the FHP
- [ ] Hard tissue landmarks from the ; except for the mid-auriculare have to be allocated

<img width="906" height="1026" alt="image" src="https://github.com/user-attachments/assets/19d34a4f-641b-4b5e-a051-ea154bc24ac0" />

#### Aiding code to place mid-auriculare
<details>
<summary>mid-au calculation</summary>

	
```python
import slicer
import numpy as np

def update_mid_auriculare_midpoint():
    """
    Calculates the midpoint between 'auL' and 'auR' from a loaded fiducial node
    and updates the position of the 'mid_au' landmark within that same node.
    """
    
    # --- 1. Configuration ---
    # The name of your fiducial list node in the Slicer scene.
    # This should match the name of the file you loaded.
    fiducials_node_name = "Ryu_hard_tissue" 
    
    # --- 2. Get the Landmark Node ---
    try:
        landmarks_node = slicer.util.getNode(fiducials_node_name)
    except slicer.util.MRMLNodeNotFoundException:
        slicer.util.errorDisplay(
            f"Landmark node '{fiducials_node_name}' not found. "
            "Please load your 'Ryu_hard_tissue.mrk.json' file first."
        )
        return

    # --- 3. Get Auriculare Positions ---
    auL_pos, auR_pos = None, None
    for i in range(landmarks_node.GetNumberOfControlPoints()):
        label = landmarks_node.GetNthControlPointLabel(i)
        pos = np.zeros(3)
        landmarks_node.GetNthControlPointPosition(i, pos)
        if label == "auL":
            auL_pos = pos
        elif label == "auR":
            auR_pos = pos

    # Check if both landmarks were found
    if auL_pos is None or auR_pos is None:
        slicer.util.errorDisplay("Could not find 'auL' and/or 'auR' in the landmark node.")
        return

    # --- 4. Calculate the Correct Midpoint ---
    correct_mid_au_pos = (auL_pos + auR_pos) / 2.0
    
    # --- 5. Find and Update the 'mid_au' Landmark ---
    mid_au_index = -1
    for i in range(landmarks_node.GetNumberOfControlPoints()):
        if landmarks_node.GetNthControlPointLabel(i) == "mid_au":
            mid_au_index = i
            break
            
    if mid_au_index != -1:
        # Update the position of the existing 'mid_au' point
        landmarks_node.SetNthControlPointPosition(mid_au_index, correct_mid_au_pos)
        slicer.util.infoDisplay(
            f"Successfully updated 'mid_au' landmark to its correct position: {correct_mid_au_pos}"
        )
    else:
        # If 'mid_au' doesn't exist for some reason, add it
        landmarks_node.AddControlPoint(correct_mid_au_pos, "mid_au")
        slicer.util.warningDisplay("The 'mid_au' landmark was not found, so a new one has been added at the correct position.")
        
# --- Run the function ---
update_mid_auriculare_midpoint()
```

</details>



Example of scene when hard tissue landmarks are allocated


### Main Planes

Ryu et al. (2024)[^2] defined 3 anatomical planes as reference for the further steps in their method: The Frankfort Horizontal plane, the sagittal and frontal planes.  The following code will execute the creation of the 3 planes; just copy and paste it in the Python console, then press enter. 

| Plane |  Definition |
| :--- | :--- |
| Median sagittal plane | Plane passing through 3 landmarks, Nasion, prosthion, auriculare midpoint |
| Orbitale transverse plane | Plane passing through 2 landmarks, orbitale left and auriculare midpoint and orthogonal to the medial sagittal plane |
| Coronal plane | Plane passing through 1 landmark, bregma and orthogonal to the median sagittal and orbitale transverse planes |

<img width="923" height="908" alt="image" src="https://github.com/user-attachments/assets/4607a058-99dc-4cb7-9b19-5240ebfc54b0" />

Example screenshot of the scene after creating the three main reference planes (note that the plane "sizes" were adjusted for visual purposes, they are technically infinite)


<details>
<summary>Main planes code</summary>

	
```python
import slicer
import numpy as np

print("="*60)
print("Running Step 1: Create Main Anatomical Planes (Corrected)")
print("="*60)

def unit(v):
    n = np.linalg.norm(v)
    if n < 1e-9: raise ValueError("Cannot normalize zero-length vector")
    return v / n

def get_landmark(node, label):
    for i in range(node.GetNumberOfControlPoints()):
        if node.GetNthControlPointLabel(i) == label:
            p = np.zeros(3); node.GetNthControlPointPositionWorld(i, p)
            return p
    raise ValueError(f"Landmark '{label}' not found.")

def get_or_create(cls, name):
    n = slicer.mrmlScene.GetFirstNodeByName(name)
    if not n: n = slicer.mrmlScene.AddNewNodeByClass(cls, name)
    return n

def style_plane(plane, color, opacity=0.8):
    d = plane.GetDisplayNode() or plane.CreateDefaultDisplayNodes()
    d.SetColor(color); d.SetSelectedColor(color); d.SetOpacity(opacity); d.SetVisibility(True)

try:
    hard_node = slicer.util.getNode("Ryu_hard_tissue")

    # --- THIS IS THE KEY FIX: Define vectors robustly from landmarks first ---
    auR, auL, n = get_landmark(hard_node, 'auR'), get_landmark(hard_node, 'auL'), get_landmark(hard_node, 'n')
    vec_right = unit(auR - auL)
    vec_anterior_initial = unit(n - (auR + auL) / 2.0)
    vec_anterior = unit(vec_anterior_initial - np.dot(vec_anterior_initial, vec_right) * vec_right) # Orthogonalize
    vec_superior = unit(np.cross(vec_right, vec_anterior)) # Guarantees a right-handed system

    print(f"Corrected vec_superior: {np.round(vec_superior, 2)}")
    print(f"Corrected vec_right:    {np.round(vec_right, 2)}")
    print(f"Corrected vec_anterior: {np.round(vec_anterior, 2)}")

    # Create planes from these corrected vectors
    midsag_plane = get_or_create("vtkMRMLMarkupsPlaneNode", "Median Sagittal Plane")
    midsag_plane.SetOrigin(get_landmark(hard_node, 'n')); midsag_plane.SetNormal(vec_right)
    style_plane(midsag_plane, [0.2, 0.8, 0.2])

    orbital_plane = get_or_create("vtkMRMLMarkupsPlaneNode", "Orbitale Transverse Plane")
    orbital_plane.SetOrigin(get_landmark(hard_node, 'orL')); orbital_plane.SetNormal(vec_superior)
    style_plane(orbital_plane, [0.8, 0.2, 0.2])

    coronal_plane = get_or_create("vtkMRMLMarkupsPlaneNode", "Coronal Plane")
    coronal_plane.SetOrigin(get_landmark(hard_node, 'b')); coronal_plane.SetNormal(vec_anterior)
    style_plane(coronal_plane, [0.2, 0.2, 0.8])

    print("\nStep 1 complete. Main anatomical planes created with correct orientation.")

except Exception as e:
    slicer.util.errorDisplay(f"An error occurred in Step 1: {e}")


```

</details>


### Marginal lines and planes

Now that the "blueprint" planes are present, the guiding lines and marginal planes bisecting the most extreme landmarks can be programmatically created. These are both techinically infinite, but  the guiding lines will be uniformly 75 mm to visualise them - please note that these are NOT measurements. 
Below are the definitions of all the lines/planes created via the code below:

| Line | Landmark to Bisect | Definition | Plane for Reference | Direction | Defined by |
|------|--------------------|------------|---------------------|-----------|-------------|
| guiding_SOM_L/R | skL/R | superior orbital margin on the left/right | parallel to Orbitale transverse plane | laterally | Stephan, 2008[^5] |
| guiding_MOM_L/R | dL/R | medial orbital margin on the left/right | parallel to Median sagittal plane | superoinferiorly | Stephan, 2008[^5] |
| guiding_LOM_L | lat_orL | lateral-most point on the lateral orbital margin on the left | parallel to Median sagittal plane | superoinferiorly | Stephan, 2008[^5] |
| guiding_LOM_R | lat_orR | lateral-most point on the lateral orbital margin on the right | parallel to Median sagittal plane | superoinferiorly | Ryu et al 2024[^2] |
| guiding_IOM_L/R | orL/R | inferior-most point on the infraorbital margin (orbitale) on the left/right | parallel to Orbitale transverse plane | laterally | Stephan, 2008[^5] |

| Plane | Landmark to Bisect | Definition | Plane for Reference | Direction | Defined by |
|-------|--------------------|------------|---------------------|-----------|-------------|
| marginal_SOM_L/R | skL/R | superior orbital marginal plane on the left/right | parallel to Orbitale transverse plane | superoinferiorly | Stephan, 2008[^5] |
| marginal_MOM_L/R | dL/R | medial orbital marginal plane on the left/right | parallel to Median sagittal plane | laterally | Stephan, 2008[^5] |
| marginal_LOM_L | lat_orL | lateral-most point on the lateral orbital marginal plane on the left | parallel to Median sagittal plane | laterally | Stephan, 2008[^5] |
| marginal_LOM_R | lat_orR | lateral-most point on the lateral orbital marginal plane on the right | parallel to Median sagittal plane | laterally | Ryu et al 2024[^2] |
| marginal_IOM_L/R | orL/R | inferior-most point on the infraorbital marginal plane (orbitale) on the left/right | parallel to Orbitale transverse plane | superoinferiorly | Stephan, 2008[^5] |

* note that the directionalities are opposite for planes and lines!

<img width="947" height="791" alt="image" src="https://github.com/user-attachments/assets/f806980f-b5ea-4bab-93af-7817b06f0ef8" />


Screenshot after the code below was run, all other lines/planes/landmarks were hidden from visibility.


<details>	
<summary> Marginal planes and guiding lines code </summary>

```python
import slicer
import numpy as np

print("="*60)
print("Running Step 2: Create Marginal Planes and Guiding Lines")
print("="*60)

def unit(v):
    n = np.linalg.norm(v); return v / n if n > 1e-9 else v

def get_landmark(node, label):
    for i in range(node.GetNumberOfControlPoints()):
        if node.GetNthControlPointLabel(i) == label:
            p = np.zeros(3); node.GetNthControlPointPositionWorld(i, p)
            return p
    raise ValueError(f"Landmark '{label}' not found.")

def get_or_create(cls, name):
    n = slicer.mrmlScene.GetFirstNodeByName(name)
    if not n: n = slicer.mrmlScene.AddNewNodeByClass(cls, name)
    if "Line" in cls: n.RemoveAllControlPoints()
    return n

def style_line(line, color):
    d = line.GetDisplayNode() or line.CreateDefaultDisplayNodes()
    d.SetColor(color); d.SetSelectedColor(color); d.SetVisibility(True)

def style_plane(plane, color, opacity=0.8):
    d = plane.GetDisplayNode() or plane.CreateDefaultDisplayNodes()
    d.SetColor(color); d.SetSelectedColor(color); d.SetOpacity(opacity); d.SetVisibility(True)

def make_line(name, p0, p1, color):
    ln = get_or_create("vtkMRMLMarkupsLineNode", name)
    ln.AddControlPoint(p0); ln.AddControlPoint(p1)
    ln.GetMeasurement("length").SetEnabled(True)
    style_line(ln, color)

try:
    hard_node = slicer.util.getNode("Ryu_hard_tissue")
    
    # Get vectors from the correctly oriented main planes
    vec_superior = np.array(slicer.util.getNode("Orbitale Transverse Plane").GetNormal())
    vec_right = np.array(slicer.util.getNode("Median Sagittal Plane").GetNormal())

    # Create marginal geometry
    defs = [
        ("SOM", "sk", vec_superior, vec_right), ("IOM", "or", vec_superior, vec_right),
        ("MOM", "d", vec_right, vec_superior), ("LOM", "lat_or", vec_right, vec_superior)
    ]
    for base, lm_prefix, plane_n, line_dir in defs:
        for s in ["L", "R"]:
            p = get_landmark(hard_node, f"{lm_prefix}{s}")
            c = [1,0.7,0.2] if s=="L" else [0.2,0.7,1] # Orange for Left, Purple for Right
            pl = get_or_create("vtkMRMLMarkupsPlaneNode", f"marginal_{base}_{s}")
            pl.SetOrigin(p); pl.SetNormal(plane_n); style_plane(pl, c)
            make_line(f"guiding_{base}_{s}", p - line_dir*37.5, p + line_dir*37.5, c)

    print("\nStep 2 complete. Marginal planes and guiding lines created.")

except Exception as e:
    slicer.util.errorDisplay(f"An error occurred in Step 2: {e}")

```

</details>


### Hard tissue measurements for prediction ONLY
Ryu et al. (2024)[^2]  devised regressions specific for biological sex to predict the position of the oa (oculare anterior/cornea by their terminology) and the lens centre, that depend on a few chosen measurement **L/R1, 8, 15, 20**. Regressions from the bony measurements predict soft tissue dimensions **L/R21,22,23,27 and 33**; which determine the approximated position of the eyeball in 3 dimensions. 
After personal communication with the corresponding author, Lee Won-Joon, the following was implemented for the code below: 
**L/R27 approximation is excluded altogether
L/R15 was used to predict L/R33**
L/R20 and L/R27 are instead added to extra hard tissue measurements and the validation steps.

The following code creates the hard tissue measurement necessary to undertake the prediction, summarised in the table below. 

| Line name | Description |
|----------------|-------------|
| L1 | shortest perpendicular guiding_MOM_L line to guiding_LOM_L line distance |
| R1 | shortest perpendicular guiding_MOM_R line to guiding_LOM_R line distance |
| L8 | shortest perpendicular guiding_SOM_L line to guiding_IOM_L line distance |
| R8 | shortest perpendicular guiding_SOM_R line to guiding_IOM_R line distance |
| L15 | shortest perpendicular Coronal plane-guiding_LOM_L line distance |
| R15 | shortest perpendicular Coronal plane-guiding_LOM_R line distance |


<details>	
<summary> Core hard tissue measurment code </summary>
	
```python
import slicer
import numpy as np

print("="*60)
print("Running Step 3: Create Hard Tissue Measurements")
print("="*60)

def unit(v):
    n = np.linalg.norm(v); return v / n if n > 1e-9 else v

def get_landmark(node, label):
    for i in range(node.GetNumberOfControlPoints()):
        if node.GetNthControlPointLabel(i) == label:
            p = np.zeros(3); node.GetNthControlPointPositionWorld(i, p)
            return p
    raise ValueError(f"Landmark '{label}' not found.")

def get_or_create(cls, name):
    n = slicer.mrmlScene.GetFirstNodeByName(name)
    if not n: n = slicer.mrmlScene.AddNewNodeByClass(cls, name)
    if "Line" in cls: n.RemoveAllControlPoints()
    return n

def style_line(line, color):
    d = line.GetDisplayNode() or line.CreateDefaultDisplayNodes()
    d.SetColor(color); d.SetSelectedColor(color); d.SetVisibility(True)

def make_line(name, p0, p1, color, value=None):
    ln = get_or_create("vtkMRMLMarkupsLineNode", name)
    ln.AddControlPoint(p0); ln.AddControlPoint(p1)
    ln.GetMeasurement("length").SetEnabled(True)
    if value is not None: ln.GetMeasurement("length").SetValue(value)
    style_line(ln, color)
    return ln

try:
    hard_node = slicer.util.getNode("Ryu_hard_tissue")
    vec_superior = np.array(slicer.util.getNode("Orbitale Transverse Plane").GetNormal())
    vec_right = np.array(slicer.util.getNode("Median Sagittal Plane").GetNormal())
    vec_anterior = np.array(slicer.util.getNode("Coronal Plane").GetNormal())
    coronal_origin = np.array(slicer.util.getNode("Coronal Plane").GetOrigin())
    
    cyan = [0, 1, 1]
    
    for s in ["L", "R"]:
        # L1/R1: Distance from dL/dR to lat_orL/R along Right direction
        lom_p = get_landmark(hard_node, f"lat_or{s}")
        mom_p = get_landmark(hard_node, f"d{s}")
        dist = abs(np.dot(lom_p - mom_p, vec_right))
        make_line(f"{s}1", mom_p, mom_p + vec_right * np.dot(lom_p - mom_p, vec_right), cyan, dist)
        
        # L8/R8: Distance from skL/R to orL/R along Superior direction
        som_p = get_landmark(hard_node, f"sk{s}")
        iom_p = get_landmark(hard_node, f"or{s}")
        dist = abs(np.dot(som_p - iom_p, vec_superior))
        make_line(f"{s}8", iom_p, iom_p + vec_superior * np.dot(som_p - iom_p, vec_superior), cyan, dist)
        
        # L15/R15: Distance from lat_orL/R to Coronal Plane along Anterior direction
        lom_p = get_landmark(hard_node, f"lat_or{s}")
        dist = abs(np.dot(lom_p - coronal_origin, vec_anterior))
        make_line(f"{s}15", lom_p, lom_p - vec_anterior * np.dot(lom_p - coronal_origin, vec_anterior), cyan, dist)

    print("\nStep 3 complete. Hard tissue measurement lines created.")
    print(f"  ✓ Created L1, R1 (medial-lateral orbital breadth)")
    print(f"  ✓ Created L8, R8 (superior-inferior orbital height)")
    print(f"  ✓ Created L15, R15 (lateral orbitale to coronal plane)")
    print("\nThese three measurements (L/R1, L/R8, L/R15) feed into the regression equations.")
    print("Setup is finished. You can now use the placement tool.")

except Exception as e:
    slicer.util.errorDisplay(f"An error occurred in Step 3: {e}")
```

</details>

<img width="956" height="765" alt="image" src="https://github.com/user-attachments/assets/78d8dc79-522e-4673-a23d-21eae74c81ce" />

### Eye model placement

Next, the **L/R21,22,23 and 33** will be calculated using the hard tissue measurements from the previous step; as published by Ryu et al. (2024)[^2]. These are not visualised before the eyeball placement, but after. When running the code, expect a pop-up window of a graphic user interface (GUI) which asks you to download an artificial eye model for a male or female. The current study did not differentiate between the biological sexes, but some do, hence the option. All eye models were adjusted to the average size of a human eyeball, 24mm in diameter. You'll have to choose the left and right eyes individually - so clicking the "Download and Place Eyeball" twice, but choosing the other side from the dropdown menu. 

| Predictor  | Male equation | Female equation | Predicted soft tissue measurement | Definition of soft tissue measurement |
|----------------------|---------------|-----------------|----------------------------------|----------------------------------------|
| L1 | L23 = 0.844 × L1 - 11.224 | L23 = 0.619 × L1 - 2.175 | L23 |oaL perpendicular distance "inward/laterally" from the MOM_L |
| L8 | L21 = 0.560 × L8 - 3.648 | L21 = 0.349 × L8 + 4.320 | L21 | oaL perpendicular distance "downward" from the SOM_L |
| L8 | L22 = 0.439 × L8 + 3.662 | L22 = 0.652 × L8 - 4.353 | L22 | oaL perpendicular distance "upward" from the IOM_L |
| L15 | L33 = 0.950 × L15 + 19.126 | L33 = 1.005 × L15 + 14.700 | L33 | oaL perpendicular distance "forward/anterior" from the Coronal plane |
| R1 | R23 = 0.734 × R1 - 6.687 | R23 = 0.449 × R1 + 4.505 | R23 | oaR perpendicular distance "inward/laterally" from the MOM_R |
| R8 | R21 = 0.562 × R8 - 3.923 | R21 = 0.407 × R8 + 2.082 | R21 | oaR perpendicular distance "downward" from the SOM_R |
| R8 | R22 = 0.438 × R8 + 3.939 | R22 = 0.593 × R8 - 2.064 | R22 | oaR perpendicular distance "upward" from the IOM_R |
| R15 | R33 = 0.954 × R15 + 18.983 | R33 = 0.973 × R15 + 16.707 | R33 | oaR perpendicular distance "forward/anterior" from the Coronal plane |

When running the code, expect a pop-up window of a graphic user interface (GUI) which asks you to download an artificial eye model for a male or female. The current study did differentiate between the biological sexes hence the option. 
All eye models were adjusted to the average size of a human eyeball, 24mm in diameter. You'll have to choose the left and right eyes individually - so clicking the "Download and Place Eyeball" twice, but choosing the other side from the dropdown menu. 

> [!IMPORTANT]
> After the left eyeball is placed, the scene may "jump". No action needed, it should be restored either after the right eye is placed, or simply clicking the "Anterior" direction in the scene view


<img width="500" height="371" alt="image" src="https://github.com/user-attachments/assets/15457804-b8b0-49ba-bf06-1a59701ca3b1" />

Expect this additional window on the right. 



<img src="https://github.com/user-attachments/assets/2bb83f47-0b74-4f42-9518-b0ba570249c9" width="500">  <img src="https://github.com/user-attachments/assets/af98b5fd-e2b3-4df3-88aa-204420ddae5e" width="500">





<details>	
<summary> Eye model placement code </summary>
	
```python
import slicer
import qt
import numpy as np
import os
import vtk

try:
    import gdown
except ImportError:
    slicer.util.showStatusMessage("Installing 'gdown' package...", 2000)
    slicer.util.pip_install('gdown')
    import gdown

class RyuEyeballPlacementWidget(qt.QWidget):
    def __init__(self, parent=None):
        super(RyuEyeballPlacementWidget, self).__init__(parent)
        self.loaded_nodes = []  # Track loaded nodes for potential cleanup
        self.setup()

    def setup(self):
        self.setLayout(qt.QVBoxLayout())
        
        infoLabel = qt.QLabel("Ryu et al. (2024) - Eyeball Placement\n\nThis tool places an eyeball model based on hard tissue measurements (L/R1, L/R8, L/R15) and sex-specific regression equations.")
        infoLabel.setWordWrap(True)
        self.layout().addWidget(infoLabel)
        
        formLayout = qt.QFormLayout()
        self.sex_combo = qt.QComboBox()
        self.sex_combo.addItems(["Female", "Male"])
        formLayout.addRow("Biological Sex:", self.sex_combo)
        
        self.side_combo = qt.QComboBox()
        self.side_combo.addItems(["Left", "Right"])
        formLayout.addRow("Side:", self.side_combo)
        self.layout().addLayout(formLayout)

        self.place_button = qt.QPushButton("Place Eyeball")
        self.place_button.toolTip = "Calculate predictions from L/R1, L/R8, L/R15 and place eyeball model"
        self.place_button.setStyleSheet("background-color: #A9DFBF; font-weight: bold; padding: 8px;")
        self.layout().addWidget(self.place_button)
        
        self.status_label = qt.QLabel("Ready.")
        self.status_label.setWordWrap(True)
        self.layout().addWidget(self.status_label)
        
        self.layout().addStretch(1)

        # Connections
        self.place_button.clicked.connect(self.run_placement)

    def run_placement(self):
        self.status_label.setText("Starting placement...")
        slicer.app.processEvents()
        
        try:
            SEX = self.sex_combo.currentText
            SIDE = self.side_combo.currentText
            side_char = SIDE[0]
            
            def get_node(name, cls):
                node = slicer.mrmlScene.GetFirstNodeByName(name)
                if not node or not node.IsA(cls):
                    raise ValueError(f"Required node '{name}' of type {cls} not found.")
                return node
            
            def get_line_length(name):
                return get_node(name, "vtkMRMLMarkupsLineNode").GetMeasurement("length").GetValue()

            # Read core measurements
            self.status_label.setText(f"1. Reading measurements for {SIDE} side...")
            slicer.app.processEvents()
            
            L1 = get_line_length(f"{side_char}1")
            L8 = get_line_length(f"{side_char}8")
            L15 = get_line_length(f"{side_char}15")

            # --- Apply sex-specific regression equations ---
            if SEX == "Female":
                pred_L21 = 0.349 * L8 + 4.320
                pred_L22 = 0.652 * L8 - 4.353
                pred_L23 = 0.619 * L1 - 2.175
                pred_L33 = 1.005 * L15 + 14.700
            else:  # Male
                pred_L21 = 0.560 * L8 - 3.648
                pred_L22 = 0.439 * L8 + 3.662
                pred_L23 = 0.844 * L1 - 11.224
                pred_L33 = 0.950 * L15 + 19.126

            self.status_label.setText(f"2. Predictions calculated:\n{side_char}21={pred_L21:.2f}, {side_char}22={pred_L22:.2f}, {side_char}23={pred_L23:.2f}, {side_char}33={pred_L33:.2f}")
            slicer.app.processEvents()

            # Get anatomical reference vectors and planes
            vS = np.array(get_node("Orbitale Transverse Plane", "vtkMRMLMarkupsPlaneNode").GetNormal())
            vR = np.array(get_node("Median Sagittal Plane", "vtkMRMLMarkupsPlaneNode").GetNormal())
            vA = np.array(get_node("Coronal Plane", "vtkMRMLMarkupsPlaneNode").GetNormal())

            # Calculate target eyeball position from predictions
            p_si_1 = np.array(get_node(f"marginal_SOM_{side_char}", "vtkMRMLMarkupsPlaneNode").GetOrigin()) - vS * pred_L21
            p_si_2 = np.array(get_node(f"marginal_IOM_{side_char}", "vtkMRMLMarkupsPlaneNode").GetOrigin()) + vS * pred_L22
            d_si = 0.5 * (np.dot(vS, p_si_1) + np.dot(vS, p_si_2))

            lat_dir = -vR if side_char == "L" else vR
            p_ml = np.array(get_node(f"marginal_MOM_{side_char}", "vtkMRMLMarkupsPlaneNode").GetOrigin()) + lat_dir * pred_L23
            d_ml = np.dot(vR, p_ml)

            p_ap = np.array(get_node("Coronal Plane", "vtkMRMLMarkupsPlaneNode").GetOrigin()) + vA * pred_L33
            d_ap = np.dot(vA, p_ap)

            target_pos = np.linalg.solve(np.array([vS, vR, vA]), np.array([d_si, d_ml, d_ap]))

            # Save 3D view and layout state
            def get_camera_state():
                view = slicer.app.layoutManager().threeDWidget(0).threeDView()
                renderer = view.renderWindow().GetRenderers().GetFirstRenderer()
                cam = renderer.GetActiveCamera()
                return (cam.GetPosition(), cam.GetFocalPoint(), cam.GetViewUp())
            
            def get_layout_state():
                """Save visibility state of all nodes before loading"""
                visibility_state = {}
                for node in slicer.util.getNodesByClass("vtkMRMLNode"):
                    if hasattr(node, 'GetDisplayNode'):
                        display_node = node.GetDisplayNode()
                        if display_node:
                            visibility_state[node.GetID()] = display_node.GetVisibility()
                return visibility_state
            
            camera_state = get_camera_state()
            layout_state = get_layout_state()

            # Download and place eyeball model
            self.status_label.setText("3. Downloading eyeball model...")
            slicer.app.processEvents()
            
            IDS = {
                "Female Left": "1p8rCfH7g35sAKXl0HeVf8PHzPt_xmSes",
                "Female Right": "1SK4alr7IumBGPm9OFUbNTCRAvJCPCpDR",
                "Male Left": "1X7JllfMrZM-AZpSrNh1CZwMGUTnHcqfG",
                "Male Right": "1rKmPbzuC1EjNoxLwoKNLIqLpZcVSxNYh"
            }
            key = f"{SEX} {SIDE}"
            mrb_path = os.path.join(slicer.app.temporaryPath, f"ryu_{key.replace(' ','_')}.mrb")
            gdown.download(id=IDS[key], output=mrb_path, quiet=False)
            
            # Track nodes before loading
            nodes_before = set(slicer.util.getNodesByClass("vtkMRMLNode"))
            
            # Load scene WITHOUT clearing
            slicer.util.loadScene(mrb_path, {"clear": False, "loadCamera": False})
            
            # Get newly loaded nodes
            nodes_after = set(slicer.util.getNodesByClass("vtkMRMLNode"))
            new_nodes = list(nodes_after - nodes_before)
            self.loaded_nodes.extend([n.GetID() for n in new_nodes])

            xform_node, oa0_pos = None, None
            for node in new_nodes:
                if node.IsA("vtkMRMLLinearTransformNode"):
                    xform_node = node
                if node.IsA("vtkMRMLMarkupsFiducialNode"):
                    if node.GetControlPointIndexByLabel(f"oa{side_char}") >= 0:
                        p = np.zeros(3)
                        node.GetNthControlPointPositionWorld(node.GetControlPointIndexByLabel(f"oa{side_char}"), p)
                        oa0_pos = p

            if xform_node is None or oa0_pos is None:
                raise ValueError("Could not find model transform or 'oa' landmark.")

            translation = target_pos - oa0_pos
            matrix = vtk.vtkMatrix4x4()
            xform_node.GetMatrixTransformToParent(matrix)
            for i in range(3):
                matrix.SetElement(i, 3, matrix.GetElement(i, 3) + translation[i])
            xform_node.SetMatrixTransformToParent(matrix)

            # Create prediction measurement lines
            def make_pred_line(name, p0, p1, value, color=(1, 0, 0)):
                ln = slicer.mrmlScene.GetFirstNodeByName(name)
                if not ln:
                    ln = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
                ln.RemoveAllControlPoints()
                ln.AddControlPoint(p0)
                ln.AddControlPoint(p1)
                ln.GetMeasurement("length").SetEnabled(True)
                ln.GetMeasurement("length").SetValue(value)
                d = ln.GetDisplayNode() or ln.CreateDefaultDisplayNodes()
                d.SetColor(color[0], color[1], color[2])
                d.SetSelectedColor(1, 1, 0)
                d.SetVisibility(True)

            coronal_origin = np.array(get_node("Coronal Plane", "vtkMRMLMarkupsPlaneNode").GetOrigin())
            p_on_som = target_pos - vS * np.dot(target_pos - np.array(get_node(f"marginal_SOM_{side_char}", "vtkMRMLMarkupsPlaneNode").GetOrigin()), vS)
            p_on_iom = target_pos - vS * np.dot(target_pos - np.array(get_node(f"marginal_IOM_{side_char}", "vtkMRMLMarkupsPlaneNode").GetOrigin()), vS)
            p_on_mom = target_pos - vR * np.dot(target_pos - np.array(get_node(f"marginal_MOM_{side_char}", "vtkMRMLMarkupsPlaneNode").GetOrigin()), vR)
            p_on_coronal = target_pos - vA * np.dot(target_pos - coronal_origin, vA)

            make_pred_line(f"pred_{side_char}21", target_pos, p_on_som, pred_L21, color=(1, 0, 0))
            make_pred_line(f"pred_{side_char}22", target_pos, p_on_iom, pred_L22, color=(1, 0, 0))
            make_pred_line(f"pred_{side_char}23", target_pos, p_on_mom, pred_L23, color=(1, 0, 0))
            make_pred_line(f"pred_{side_char}33", target_pos, p_on_coronal, pred_L33, color=(1, 0, 0))

            # Restore camera state and layout
            view = slicer.app.layoutManager().threeDWidget(0).threeDView()
            renderer = view.renderWindow().GetRenderers().GetFirstRenderer()
            cam = renderer.GetActiveCamera()
            pos, fp, up = camera_state
            cam.SetPosition(pos)
            cam.SetFocalPoint(fp)
            cam.SetViewUp(up)
            view.renderWindow().Render()
            
            # Restore visibility state of previous nodes
            for node_id, visibility in layout_state.items():
                node = slicer.mrmlScene.GetNodeByID(node_id)
                if node and hasattr(node, 'GetDisplayNode'):
                    display_node = node.GetDisplayNode()
                    if display_node:
                        display_node.SetVisibility(visibility)

            final_message = (f"✓ Prediction complete!\n\n"
                             f"{SEX} {SIDE} eyeball\n\n"
                             f"Predicted soft tissue distances:\n"
                             f"{side_char}21 = {pred_L21:.2f} mm\n"
                             f"{side_char}22 = {pred_L22:.2f} mm\n"
                             f"{side_char}23 = {pred_L23:.2f} mm\n"
                             f"{side_char}33 = {pred_L33:.2f} mm")
            self.status_label.setText(final_message)
            slicer.util.infoDisplay(final_message)

        except Exception as e:
            self.status_label.setText(f"ERROR: {e}")
            slicer.util.errorDisplay(f"An error occurred: {e}")
            raise e

# Cleanup and instantiation
try:
    if 'ryu_placement_widget' in globals() and ryu_placement_widget:
        ryu_placement_widget.parent().close()
except NameError:
    pass

ryu_placement_widget = RyuEyeballPlacementWidget()
dock_widget = qt.QDockWidget("Ryu Eyeball Placement")
dock_widget.setWidget(ryu_placement_widget)
slicer.util.mainWindow().addDockWidget(qt.Qt.RightDockWidgetArea, dock_widget)
dock_widget.show()
```

</details>

<img width="868" height="954" alt="image" src="https://github.com/user-attachments/assets/bd3b313c-576a-44f0-a307-7b4f433a331a" />


View after placing both eyeballs


### Validating the original study
If you wanted to use this this tool for an approximation, you're done!

Additionally, we can compare the predicted and the actual eyeball positions via landmarks, by placing the soft tissue landmarks denoted with a blue square in the previous section "Landmarks in this study". 
You can download them [here](https://github.com/user-attachments/files/27196663/Ryu_soft_tissue.mrk.json).

Once you placed the "ground truth" landmarks (called Ryu_soft_tissue.lmrk.json) onto the scan (you'll likely have to use the red/green/yellow windows for a more precise placement), you can run the codes below. 
It is an iterative process, with an extra step for placing the central landmarks. The lens centre (lcL/R) and globe centre (gcL/R) are found by the code called "true centres placement", by calculating the midpoint between the lens anterior and lens posterior for the lens centre on both sides; and by using a triaxial ellipsoid's geometry to calculate the globe's centre based on the oa-op, oi-os, om-ol distances. Please place all the soft tissue landmarks **with the exception of lcL, lcR, gcL, gcR**, then run the code below. 

<details>	
<summary> Find true soft tissue centres </summary>
	
```python
import slicer
import numpy as np

def place_true_center_landmarks():
    """
    Calculates and places the lens center (lc) and globe center (gc) landmarks
    for both left and right sides within the 'Ryu_soft_tissue' fiducial list.
    """
    print("--- Starting programmatic placement of 'true_lc' and 'true_gc' landmarks ---")

    try:
        landmarks_node = slicer.util.getNode("Ryu_soft_tissue")
        print("Found 'Ryu_soft_tissue' landmark node.")
    except slicer.util.MRMLNodeNotFoundException:
        slicer.util.errorDisplay("ERROR: 'Ryu_soft_tissue' landmark node not found in the scene. Please load it first.")
        return

    # --- Helper function to get landmark positions ---
    def get_landmark_pos(label):
        for i in range(landmarks_node.GetNumberOfControlPoints()):
            if landmarks_node.GetNthControlPointLabel(i) == label:
                pos = np.zeros(3)
                landmarks_node.GetNthControlPointPositionWorld(i, pos)
                return pos
        print(f"Warning: Landmark '{label}' not found.")
        return None

    # --- Helper function to add or update a landmark ---
    def set_or_add_landmark(label, position):
        # Check if the point already exists
        for i in range(landmarks_node.GetNumberOfControlPoints()):
            if landmarks_node.GetNthControlPointLabel(i) == label:
                landmarks_node.SetNthControlPointPositionWorld(i, position)
                print(f"Updated existing landmark: '{label}'")
                return
        # If it doesn't exist, add it
        landmarks_node.AddControlPoint(position, label)
        print(f"Added new landmark: '{label}'")

    # --- Process both Left and Right sides ---
    for side in ["L", "R"]:
        print(f"\nProcessing side: {side}")

        # 1. Calculate and place Lens Center (lc)
        # lc is the midpoint between la (anterior lens) and lp (posterior lens)
        la_pos = get_landmark_pos(f"true_la{side}")
        lp_pos = get_landmark_pos(f"true_lp{side}")

        if la_pos is not None and lp_pos is not None:
            lc_pos = (la_pos + lp_pos) / 2.0
            set_or_add_landmark(f"true_lc{side}", lc_pos)
        else:
            print(f"Could not calculate 'true_lc{side}' due to missing landmarks.")

        # 2. Calculate and place Globe Center (gc)
        # gc is the geometric center of the 6 extreme eyeball points
        oa_pos = get_landmark_pos(f"true_oa{side}") # anterior
        op_pos = get_landmark_pos(f"true_op{side}") # posterior
        os_pos = get_landmark_pos(f"true_os{side}") # superior
        oi_pos = get_landmark_pos(f"true_oi{side}") # inferior
        om_pos = get_landmark_pos(f"true_om{side}") # medial
        ol_pos = get_landmark_pos(f"true_ol{side}") # lateral

        extreme_points = [oa_pos, op_pos, os_pos, oi_pos, om_pos, ol_pos]
        if all(p is not None for p in extreme_points):
            # The center is the average of all 6 extreme points
            gc_pos = np.mean(np.array(extreme_points), axis=0)
            set_or_add_landmark(f"true_gc{side}", gc_pos)
        else:
            print(f"Could not calculate 'true_gc{side}' due to missing extreme landmarks.")

    print("\n--- Landmark placement complete. ---")

# --- Run the function ---
place_true_center_landmarks()

```

</details>

> [!IMPORTANT]
>You do not need to repeat this step for the "artificial" eye models, as these have been exacuted the same way at time of the creation of the model. 

After this, we can add the extra hard tissue measurements (which were not a prerequisite for the approximation, but are present in the study); then the predicted soft tissue measurements based on the true hard tissue lengths, and finally, using the true soft tissue landmarks to measure the "true" soft tissue lengths. 

> [!NOTE]
> There is a measurement that needs manual allocation for both the predicted and true lens diameter length. This is not possible by connecting any already placed landmark (lens posterior and anterior measure the thickness of the lens, not its diameter). See additional instructions below.



<details>	
<summary> Linear lens diameter measurements </summary>

You'll need to open the **Markups** module and click on the _Create Markups_ > _Line_ option. This will add an empty distance measurement called "L_1/2..." by default. Now, if you place two points on either the 3D scene view or the red/yellow/green boxes, a measurement line in mm will show up. It is important that you rename these lines accordingly, as the codes will only recognise them under specific names. These will have to be
1) "true_L30" and "true_R30" for the true lens diamaters on the scans
2) "pred_L30" and "pred_R30" for the diamater of the lens on the "artificial" eye model

It is easier to employ the **lcL/R** points for this manual placement as the line had to connect two opposing sides of the lens in anterior/posterior view and cross the lens centre point. 

It is quite easy to see on the artificial eye model, especially with being able to manipulate the individual parts: go to the **Models** module and hide the layers of the cornea, isris and pupil to see the lens without any other structures obscuring it. 

<img width="1190" height="487" alt="{90ACE94A-49D1-4701-A86E-820667BE6675}" src="https://github.com/user-attachments/assets/efc3698f-49fd-491a-b847-cbd69b209ce5" />

The left eye has the view we need - please note that all other eyeball landmarks were hidden in the **Markups** module (just click onto either the _Left Eyeball lmrks_  or the _Right Eyeball lmrks_, then open the "Control Points" submenu and hide all other landmarks). 

Now, we can go back to the markups module to place the lines: 

<img width="665" height="419" alt="{B1219E9A-CB47-4F17-A408-7BB27A4E17F4}" src="https://github.com/user-attachments/assets/b004d74d-c9c4-4146-9654-4f16a481eede" />

And rename them "pred_L30" and "pred_R30" for the diamater of the lens on the "artificial" eye model. 


This is quite challenging to see on slices for the true soft tissue lens diameter - if you want to "re-slice" the scan adhering to the reference planes, use this snippet: 


```python
import slicer
import numpy as np

print("="*60)
print("Re-orienting Slice Views to Custom Anatomical Planes")
print("="*60)

def get_node(name, cls="vtkMRMLMarkupsPlaneNode"):
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if not node:
        raise ValueError(f"Required plane '{name}' not found. Please create the anatomical planes first.")
    if not node.IsA(cls):
        raise ValueError(f"Node '{name}' is not of type {cls}.")
    return node

try:
    # 1. Get the normal vectors that will become our new anatomical axes
    midsagittal_plane = get_node("Median Sagittal Plane")
    axis_x = np.array(midsagittal_plane.GetNormal())  # Right-Left axis
    
    coronal_plane = get_node("Coronal Plane")
    axis_y = np.array(coronal_plane.GetNormal())      # Anterior-Posterior axis
    
    orbital_plane = get_node("Orbitale Transverse Plane")
    axis_z = np.array(orbital_plane.GetNormal())      # Superior-Inferior axis

    # 2. Normalize and ensure perfect orthogonality (create a right-handed basis)
    axis_x /= np.linalg.norm(axis_x)
    axis_y /= np.linalg.norm(axis_y)
    # Recompute Z to be perfectly orthogonal to X and Y
    axis_z = np.cross(axis_x, axis_y)
    axis_z /= np.linalg.norm(axis_z)
    # Recompute Y to be perfectly orthogonal to the new Z and X
    axis_y = np.cross(axis_z, axis_x)
    axis_y /= np.linalg.norm(axis_y)

    # 3. Get the slice nodes
    red_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
    yellow_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
    green_slice_node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')

    # 4. Create and apply a unique orientation matrix for EACH slice view
    
    # Red Slice (Axial View): XY plane, normal is Z
    axial_matrix = np.identity(4)
    axial_matrix[0, 0:3] = axis_x  # Red view's X-axis is the anatomical Right-Left
    axial_matrix[1, 0:3] = axis_y  # Red view's Y-axis is the anatomical Anterior-Posterior
    axial_matrix[2, 0:3] = axis_z
    vtk_axial_matrix = slicer.util.vtkMatrixFromArray(axial_matrix.T)
    red_slice_node.GetSliceToRAS().DeepCopy(vtk_axial_matrix)
    red_slice_node.UpdateMatrices()
    
    # Yellow Slice (Sagittal View): YZ plane, normal is X
    sagittal_matrix = np.identity(4)
    sagittal_matrix[0, 0:3] = axis_y  # Yellow view's X-axis is the anatomical Anterior-Posterior
    sagittal_matrix[1, 0:3] = axis_z  # Yellow view's Y-axis is the anatomical Superior-Inferior
    sagittal_matrix[2, 0:3] = axis_x
    vtk_sagittal_matrix = slicer.util.vtkMatrixFromArray(sagittal_matrix.T)
    yellow_slice_node.GetSliceToRAS().DeepCopy(vtk_sagittal_matrix)
    yellow_slice_node.UpdateMatrices()

    # Green Slice (Coronal View): ZX plane, normal is Y
    # THIS IS THE KEY CORRECTION
    coronal_matrix = np.identity(4)
    coronal_matrix[0, 0:3] = axis_x  # Green view's X-axis is the anatomical Right-Left
    coronal_matrix[1, 0:3] = axis_z  # Green view's Y-axis is the anatomical Superior-Inferior
    coronal_matrix[2, 0:3] = axis_y
    vtk_coronal_matrix = slicer.util.vtkMatrixFromArray(coronal_matrix.T)
    green_slice_node.GetSliceToRAS().DeepCopy(vtk_coronal_matrix)
    green_slice_node.UpdateMatrices()
    
    # 5. Center the views on the nasion landmark
    try:
        hard_tissue_node = slicer.util.getNode("Ryu_hard_tissue")
        nasion_pos = np.zeros(3)
        nasion_found = False
        for i in range(hard_tissue_node.GetNumberOfControlPoints()):
            if hard_tissue_node.GetNthControlPointLabel(i) == 'n':
                hard_tissue_node.GetNthControlPointPositionWorld(i, nasion_pos)
                nasion_found = True
                break
        
        if nasion_found:
            # Jump all slices to the nasion's position
            for node in [red_slice_node, yellow_slice_node, green_slice_node]:
                node.JumpSlice(nasion_pos[0], nasion_pos[1], nasion_pos[2])

            # Reset the field of view to nicely frame the volume
            slicer.app.layoutManager().sliceWidget('Red').sliceLogic().FitSliceToAll()
            slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic().FitSliceToAll()
            slicer.app.layoutManager().sliceWidget('Green').sliceLogic().FitSliceToAll()
            
    except Exception as e:
        print(f"Could not automatically center views, but re-orientation was successful. Error: {e}")

    print("\nSUCCESS: Slice viewers have been re-oriented to your custom planes.")
    print(" - Red View (Axial) is now aligned with the Orbitale Transverse Plane.")
    print(" - Yellow View (Sagittal) is now aligned with the Median Sagittal Plane.")
    print(" - Green View (Coronal) is now aligned with the Coronal Plane.")

except Exception as e:
    slicer.util.errorDisplay(f"An error occurred during re-orientation: {e}")

```


And scroll until you can see the lens on the scan, to end up with something like this: 

<img width="1510" height="1005" alt="image" src="https://github.com/user-attachments/assets/fac915b0-feac-486c-98b2-3b2f9734cdb1" />

Make sure you rename these lines **true_L30 and "true_R30"**. 

</details>


#### Extra hard tissue measurements

These measurements are also based on only hard tissue, but were not chosen as predictive distances (such as L/R1,8,15,20). For a full reproduction of the method, these would be essential. They are created by the code below. 

| original abbreviation | Slicer abbrv | Original definition | Slicer definition |
|----------------------|--------------|---------------------|-------------------|
| C1 | C1 | Lateral orbit left (landmark)—Lateral orbit right (sagittal plane) | shortest perpendicular distance between the marginal_LOM_R and marginal_LOM_L planes |
| C2 | C2 | Nasion (landmark)—Coronal plane | shortest perpendicular distance between the n and Coronal Plane |
| 2 | L2 | left Supraorbitale (landmark)—leftMedial orbit (sagittal plane) | shortest perpendicular distance between the skL and the marginal_MOM_L plane |
| 2 | R2 | right Supraorbitale (landmark)—Medial orbit (sagittal plane) | shortest perpendicular distance between the skR and the marginal_MOM_R plane |
| 3 | L3 | left Supraorbitale (landmark)— left Lateral orbit (sagittal plane) | shortest perpendicular distance between the skL and marginal_LOM_L plane |
| 3 | R3 | right Supraorbitale (landmark)— right Lateral orbit (sagittal plane) | shortest perpendicular distance between the skR and the marginal_LOM_R plane |
| 4 | L4 | left Orbitale (landmark)—left Medial orbit (sagittal plane) | shortest perpendicular distance between the orL and marginal_MOM_L plane |
| 4 | R4 | right Orbitale (landmark)—right Medial orbit (sagittal plane) | shortest perpendicular distance between the orR and marginal_MOM_R plane |
| 5 | L5 | left Orbitale (landmark)—left Lateral orbit (sagittal plane) | shortest perpendicular distance between the orL and marginal_LOM_L plane |
| 5 | R5 | right Orbitale (landmark)—right Lateral orbit (sagittal plane) | shortest perpendicular distance between the orR and marginal_LOM_R plane |
| 6 | L6 | left Medial Orbit (landmark)—left Supraorbitale (transverse plane) | shortest perpendicular distance between the dL and marginal_SOM_L |
| 6 | R6 | right Medial Orbit (landmark)—right Supraorbitale (transverse plane) | shortest perpendicular distance between the dR and marginal_SOM_R |
| 7 | L7 | left Medial orbit (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the dL and orbitale transverse plane |
| 7 | R7 | right Medial orbit (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the dR and orbitale transverse plane |
| 9 | L9 | left Lateral orbit (landmark)— left Supraorbitale (transverse plane) | shortest perpendicular distance between the lat_orL and marginal_SOM_L |
| 9 | R9 | right Lateral orbit (landmark)— right Supraorbitale (transverse plane) | shortest perpendicular distance between the lat_orR and marginal_SOM_R |
| 10 | L10 | left Lateral orbit (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the lat_orL and orbitale transverse plane |
| 10 | R10 | right Lateral orbit (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the lat_orR and orbitale transverse plane |
| 11 | L11 | left Supraorbitale (landmark)—left Lateral orbit (coronal plane) | shortest perpendicular distance between the skL and guiding_LOM_L line |
| 11 | R11 | right Supraorbitale (landmark)—right Lateral orbit (coronal plane) | shortest perpendicular distance between the skR and guiding_LOM_R line |
| 12 | L12 | Nasion (landmark)— left Lateral orbit (coronal plane) | shortest perpendicular distance between the n and guiding_LOM_L line |
| 12 | R12 | Nasion (landmark)— right Lateral orbit (coronal plane) | shortest perpendicular distance between the n and guiding_LOM_R line |
| 13 | L13 | left Medial orbit (landmark)—left Lateral orbit (coronal plane) | shortest perpendicular distance between the dL and guiding_LOM_L line |
| 13 | R13 | right Medial orbit (landmark)—right Lateral orbit (coronal plane) | shortest perpendicular distance between the dR and guiding_LOM_R line |
| 14 | L14 | left Orbitale (landmark)— left Lateral orbit (coronal plane) | shortest perpendicular distance between the orL and guiding_LOM_L line |
| 14 | R14 | rightOrbitale (landmark)— right Lateral orbit (coronal plane) | shortest perpendicular distance between the orR and guiding_LOM_R line |
| 16 | L16 | left Supraorbitale (landmark)—Coronal plane | shortest perpendicular distance between the skL and the coronal plane |
| 16 | R16 | right Supraorbitale (landmark)—Coronal plane | shortest perpendicular distance between the skR and the coronal plane |
| 17 | L17 | left Optic canal point (landmark)—Coronal plane | shortest perpendicular distance between the ocpL and the coronal plane |
| 17 | R17 | right Optic canal point (landmark)—Coronal plane | shortest perpendicular distance between the ocpR and the coronal plane |
| 18 | L18 | left Optic canal point (landmark)— left Lateral orbit (coronal plane) | shortest perpendicular distance between the ocpL and guiding_LOM_L line |
| 18 | R18 | right Optic canal point (landmark)— right Lateral orbit (coronal plane) | shortest perpendicular distance between the ocpR and guiding_LOM_R line |
| 19 | L19 | left Medial orbit (landmark)—Coronal plane | shortest perpendicular distance between the dL and the coronal plane |
| 19 | R19 | right Medial orbit (landmark)—Coronal plane | shortest perpendicular distance between the dR and the coronal plane |
| 20 | R20 | right Orbitale (landmark)— Coronal plane | shortest perpendicular Coronal plane- IOM_R line distance|
| 20 | L20 | light Orbitale (landmark)— Coronal plane | shortest perpendicular Coronal plane- IOM_L line distance|


<details>	
<summary> Additional hard tissue measurements </summary>
	
```python
import slicer
import numpy as np

print("="*60)
print("Creating DESCRIPTIVE (Rest of) Hard Tissue Measurements")
print("="*60)

# --- Helper Functions (condensed) ---
def get_node(name, cls="vtkMRMLNode"):
    node = slicer.mrmlScene.GetFirstNodeByName(name);
    if not node or not node.IsA(cls): raise ValueError(f"Node '{name}' ({cls}) not found.")
    return node
def get_landmark_pos(node, label):
    for i in range(node.GetNumberOfControlPoints()):
        if node.GetNthControlPointLabel(i) == label:
            p = np.zeros(3); node.GetNthControlPointPositionWorld(i, p); return p
    raise ValueError(f"Landmark '{label}' not found in '{node.GetName()}'.")
def style_line(line_node, color=[1,0.5,0]): # Orange for descriptive measurements
    d = line_node.GetDisplayNode() or line_node.CreateDefaultDisplayNodes();
    d.SetColor(color); d.SetSelectedColor([1,1,0]); d.SetVisibility(True)
    line_node.GetMeasurement("length").SetEnabled(True)
def measure_point_to_plane(point, plane_node):
    o, n = np.zeros(3), np.zeros(3); plane_node.GetOrigin(o); plane_node.GetNormal(n)
    dist = np.dot(point - o, n); return abs(dist), point - dist * n
def measure_point_to_line(point, line_node):
    p1, p2 = np.zeros(3), np.zeros(3); line_node.GetNthControlPointPositionWorld(0, p1); line_node.GetNthControlPointPositionWorld(1, p2)
    if np.linalg.norm(p2-p1) < 1e-6: return 0, p1
    d = (p2-p1)/np.linalg.norm(p2-p1); v = point-p1; t = np.dot(v,d); cp = p1 + t * d
    return np.linalg.norm(point-cp), cp

def create_and_measure(name, p1, p2, value=None):
    if slicer.mrmlScene.GetFirstNodeByName(name):
        print(f"Skipping existing node: {name}")
        return
    line_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
    line_node.AddControlPoint(p1); line_node.AddControlPoint(p2); style_line(line_node)
    if value is not None:
        line_node.GetMeasurement("length").SetValue(value)

try:
    hard_node = get_node("Ryu_hard_tissue", "vtkMRMLMarkupsFiducialNode")
    coronal_plane = get_node("Coronal Plane", "vtkMRMLMarkupsPlaneNode")
    orbital_plane = get_node("Orbitale Transverse Plane", "vtkMRMLMarkupsPlaneNode")

    # --- Bilateral Descriptive Measurements ---
    for side in ["L", "R"]:
        marginal_SOM = get_node(f"marginal_SOM_{side}", "vtkMRMLMarkupsPlaneNode")
        marginal_MOM = get_node(f"marginal_MOM_{side}", "vtkMRMLMarkupsPlaneNode")
        marginal_LOM = get_node(f"marginal_LOM_{side}", "vtkMRMLMarkupsPlaneNode")
        guiding_LOM = get_node(f"guiding_LOM_{side}", "vtkMRMLMarkupsLineNode")

        sk_pos = get_landmark_pos(hard_node, f"sk{side}")
        or_pos = get_landmark_pos(hard_node, f"or{side}")
        d_pos = get_landmark_pos(hard_node, f"d{side}")
        lat_or_pos = get_landmark_pos(hard_node, f"lat_or{side}")
        n_pos = get_landmark_pos(hard_node, "n")

        dist, proj = measure_point_to_plane(sk_pos, marginal_MOM); create_and_measure(f"{side}2", sk_pos, proj)
        dist, proj = measure_point_to_plane(sk_pos, marginal_LOM); create_and_measure(f"{side}3", sk_pos, proj)
        dist, proj = measure_point_to_plane(or_pos, marginal_MOM); create_and_measure(f"{side}4", or_pos, proj)
        dist, proj = measure_point_to_plane(or_pos, marginal_LOM); create_and_measure(f"{side}5", or_pos, proj)
        dist, proj = measure_point_to_plane(d_pos, marginal_SOM); create_and_measure(f"{side}6", d_pos, proj)
        dist, proj = measure_point_to_plane(d_pos, orbital_plane); create_and_measure(f"{side}7", d_pos, proj)
        dist, proj = measure_point_to_plane(lat_or_pos, marginal_SOM); create_and_measure(f"{side}9", lat_or_pos, proj)
        dist, proj = measure_point_to_plane(lat_or_pos, orbital_plane); create_and_measure(f"{side}10", lat_or_pos, proj)
        dist, proj = measure_point_to_line(sk_pos, guiding_LOM); create_and_measure(f"{side}11", sk_pos, proj)
        dist, proj = measure_point_to_line(n_pos, guiding_LOM); create_and_measure(f"{side}12", n_pos, proj)
        dist, proj = measure_point_to_line(d_pos, guiding_LOM); create_and_measure(f"{side}13", d_pos, proj)
        dist, proj = measure_point_to_line(or_pos, guiding_LOM); create_and_measure(f"{side}14", or_pos, proj)
        dist, proj = measure_point_to_plane(sk_pos, coronal_plane); create_and_measure(f"{side}16", sk_pos, proj)
        dist, proj = measure_point_to_plane(d_pos, coronal_plane); create_and_measure(f"{side}19", d_pos, proj)
    
    # --- Midline Descriptive Measurements ---
    if not slicer.mrmlScene.GetFirstNodeByName("C1"):
        lom_l_plane = get_node("marginal_LOM_L", "vtkMRMLMarkupsPlaneNode")
        lom_r_plane = get_node("marginal_LOM_R", "vtkMRMLMarkupsPlaneNode")
        lom_l_origin, lom_r_origin = np.zeros(3), np.zeros(3)
        lom_l_plane.GetOrigin(lom_l_origin); lom_r_plane.GetOrigin(lom_r_origin)
        plane_normal = np.zeros(3); lom_l_plane.GetNormal(plane_normal)
        dist_c1 = abs(np.dot(lom_r_origin - lom_l_origin, plane_normal))
        create_and_measure("C1", lom_l_origin, lom_r_origin, dist_c1)
        
    n_pos = get_landmark_pos(hard_node, "n")
    dist, proj = measure_point_to_plane(n_pos, coronal_plane); create_and_measure("C2", n_pos, proj)

    print("\nSUCCESS: All descriptive hard tissue measurement lines (orange) created.")

except Exception as e:
    slicer.util.errorDisplay(f"An error occurred in descriptive measurement creation: {e}")
```

</details>


#### More predicted soft tissue distances

There have been some soft tissue measurements (L/R21, 22, 23, 33) that were predicted in the step where the artificial eyes were placed. The rest of the predicted soft tissue distances are created by the code below. 

##### More Guide lines
There will be added lines (similar to the guiding_lines previously) to ensure the parallell measurement theme in the original study. 

| Source | guide_line | bisects | is parallel to |
|--------|------------|---------|----------------|
| Predicted (Eyeball lmrks) | pred_lcL line | lcL | Coronal |
| | pred_lcR line | lcR | Coronal |
| | pred_laR line | laR | Coronal |
| | pred_laL line | laL | Coronal |
| | pred_oaR line | oaR | Coronal |
| | pred_oaL line | oaL | Coronal |
| | pred_lpR line | lpR | Coronal |
| | pred_lpL line | lpL | Coronal |
| | pred_oiR line | oiR | orbital transverse |
| | pred_oiL line | oiL | orbital transverse |
| | pred_osR line | osR | orbital transverse |
| | pred_osL line | osL | orbital transverse |
| | pred_omR line | omR | Coronal |
| | pred_omL line | omL | Coronal |
| | pred_olR line | olR | Coronal |
| | pred_olL line | olL | Coronal |
| True (Ryu_soft_tissue) | true_lcL line | true_lcL | Coronal |
| | true_lcR line | true_lcR | Coronal |
| | true_laR line | true_laR | Coronal |
| | true_laL line | true_laL | Coronal |
| | true_oaR line | true_oaR | Coronal |
| | true_oaL line | true_oaL | Coronal |
| | true_lpR line | true_lpR | Coronal |
| | true_lpL line | true_lpL | Coronal |
| | true_oiR line | true_oiR | orbital transverse |
| | true_oiL line | true_oiL | orbital transverse |
| | true_osR line | true_osR | orbital transverse |
| | true_osL line | true_osL | orbital transverse |
| | true_omR line | true_omR | Coronal |
| | true_omL line | true_omL | Coronal |
| | true_olR line | true_olR | Coronal |
| | true_olL line | true_olL | Coronal |




##### Predicted Soft tissue measurements

(2) Additional Predicted measurements
| original | Slicer abbrv | Original definition | Slicer definition |
|----------|--------------|---------------------|-------------------|
| 21 | pred_L21 | left Lens centre (landmark)—left Supraorbitale (transverse plane) | shortest perpendicular distance between the lcL and marginal_SOM_L |
| 21 | pred_R21 | right Lens centre (landmark)—right Supraorbitale (transverse plane) | shortest perpendicular distance between the lcR and marginal_SOM_R |
| 22 | pred_L22 | left Lens centre (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the lcL and orbitale transverse plane |
| 22 | pred_R22 | right Lens centre (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the lcR and orbitale transverse plane |
| 23 | pred_L23 | left Lens centre (landmark)—left Medial orbit (sagittal plane) | shortest perpendicular distance between the lcL and marginal_MOM_L plane |
| 23 | pred_R23 | right Lens centre (landmark)—right Medial orbit (sagittal plane) | shortest perpendicular distance between the lcR and marginal_MOM_R plane |
| 24 | pred_L24 | left Lens centre (landmark)— left Lateral orbit (sagittal plane) | shortest perpendicular distance between the lcL and marginal_LOM_L plane |
| 24 | pred_R24 | right Lens centre (landmark)—right Lateral orbit (sagittal plane) | shortest perpendicular distance between the lcR and marginal_LOM_R plane |
| 25 | pred_L25 | left Lens centre (landmark)—left Lateral orbit (coronal plane) | shortest perpendicular distance between the lcL and guiding_LOM_L line |
| 25 | pred_R25 | right Lens centre (landmark)—right Lateral orbit (coronal plane) | shortest perpendicular distance between the lcR and guiding_LOM_R line |
| 26 | pred_L26 | left Lens centre (landmark)—left Optic canal point | shortest perpendicular distance between the pred_lcL line to pred_ocpL line |
| 26 | pred_R26 | right Lens centre (landmark)—right Optic canal point | shortest perpendicular distance between the pred_lcR line and pred_ocpR line |
| 27 | pred_L27 | left Lens centre (landmark)— Coronal plane | shortest perpendicular distance between the pred_lcL line and Coronal plane |
| 27 | pred_R27 | right Lens centre (landmark)— Coronal plane | shortest perpendicular distance between the pred_lcR line and Coronal plane |
| 28 | pred_L28 | left Lens anterior (landmark)—left Lens posterior | shortest perpendicular distance between pred_laL line and pred_lpL line |
| 28 | pred_R28 | right Lens anterior (landmark)—right Lens posterior | shortest perpendicular distance between pred_laR line and pred_lpR line |
| 29 | pred_L29 | left Cornea (landmark)—left Lens centre (coronal plane) | shortest perpendicular distance between pred_oaL line to pred_lcL line |
| 29 | pred_R29 | right Cornea (landmark)—right Lens centre (coronal plane) | shortest perpendicular distance between pred_oaR line to pred_lcR line |
| 30 | pred_L30 | left Lens diameter | manual |
| 30 | pred_R30 | right Lens diameter | manual |
| 31 | pred_L31 | left Cornea (landmark)— left Lateral orbit (coronal plane) (25 + 29) | L25 + L29 (shortest perpendicular distance between the pred_oaL line and marginal_LOM_L plane) |
| 31 | pred_R31 | right Cornea (landmark)— right Lateral orbit (coronal plane) (25 + 29) | R25 + R29 (shortest perpendicular distance between the pred_oaL line and marginal_LOM_L plane) |
| 32 | pred_L32 | left Cornea (landmark)—left Optic canal point (26 + 29) | L26 + L29 (shortest perpendicular distance between the pred_oaL line and pred_ocpL line) |
| 32 | pred_R32 | right Cornea (landmark)—right Optic canal point (26 + 29) | R26 + R29 (shortest perpendicular distance between the pred_oaR line and pred_ocpR line) |
| 33 | pred_L33 | left Cornea (landmark)—Coronal plane (27 + 29) | L27 + L29 (shortest perpendicular distance between the pred_oaL line and Coronal plane) |
| 33 | pred_R33 | right Cornea (landmark)—Coronal plane (27 + 29) | R27 + R29 (shortest perpendicular distance between the pred_oaR line and Coronal plane) |
| E1_L | pred_E1_L | left Lens centre—left Globe superior (transverse plane) | shortest perpendicular distance between the pred_lcL line and pred_osL line |
| E1_R | pred_E1_R | right Lens centre—right Globe superior (transverse plane) | shortest perpendicular distance between the pred_lcR line and pred_osR line |
| E2_L | pred_E2_L | left Lens centre—left Globe Medial (sagittal plane) | shortest perpendicular distance between the pred_lcL line and pred_omL line |
| E2_R | pred_E2_R | right Lens centre—right Globe Medial (sagittal plane) | shortest perpendicular distance between the pred_lcR line and pred_omR line |
| E3_L | pred_E3_L | left Globe centre—left Globe superior | shortest perpendicular distance between the gcL and pred_osL line |
| E3_R | pred_E3_R | right Globe centre—right Globe superior | shortest perpendicular distance between the gcR and pred_osR line |
| E4_L | pred_E4_L | left Globe centre—left Globe medial | shortest perpendicular distance between the gcL and pred_omL line |
| E4_R | pred_E4_R | rightGlobe centre—right Globe medial | shortest perpendicular distance between the gcR and pred_omR line |
| E5_L | pred_E5_L | left Globe superior—left Globe inferior | osL to oiL |
| E5_R | pred_E5_R | right Globe superior—right Globe inferior | osR to oiR |
| E6_L | pred_E6_L | left Globe lateral—left Globe medial | olL to omL |
| E6_R | pred_E6_R | right Globe lateral—right Globe medial | olR to omR |


To create all of these, copy-paste the following code in the Python console. Once there is a pop-up about the success of the first batch, just click OK for the second batch to run. This could take a few minutes. 


<details>	
<summary> Additional predicted and true soft tissue measurements </summary>
	
```python
import slicer
import numpy as np
import vtk

def create_final_measurements(prefix):
    """
    Creates the final, colored measurement lines. This script relies on the
    'guide lines' and anatomical planes already being present in the scene.
    :param prefix: A string, either "pred_" or "true_".
    """
    print("="*80)
    print(f"Creating FINAL MEASUREMENT LINES from guides with prefix: '{prefix}'")
    print("="*80)

    if prefix not in ["pred_", "true_"]:
        slicer.util.errorDisplay("Prefix must be either 'pred_' or 'true_'.")
        return

    # --- Helper Functions (condensed for brevity) ---
    def get_node(name, cls="vtkMRMLNode"):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if not node: raise ValueError(f"Node '{name}' ({cls}) not found.")
        return node
        
    def get_landmark_pos(node, label):
        p_label = f"true_{label}" if prefix == "true_" else label
        if prefix == "pred_" and node.GetControlPointIndexByLabel(p_label) == -1:
            if node.GetControlPointIndexByLabel(f"{label[:-1]}_{label[-1]}") != -1: p_label = f"{label[:-1]}_{label[-1]}"
        idx = node.GetControlPointIndexByLabel(p_label)
        if idx == -1: raise ValueError(f"Landmark '{p_label}' not found in '{node.GetName()}'.")
        pos = np.zeros(3); node.GetNthControlPointPositionWorld(idx, pos)
        return pos

    def get_landmark_pos_hard_tissue(node, label):
        """Special handler for hard tissue landmarks like ocp that don't have true_ prefix."""
        # ocp landmarks are in hard tissue node but without true_ prefix
        idx = node.GetControlPointIndexByLabel(label)
        if idx == -1: raise ValueError(f"Landmark '{label}' not found in '{node.GetName()}'.")
        pos = np.zeros(3); node.GetNthControlPointPositionWorld(idx, pos)
        return pos

    def create_line(name, p1, p2, color, visible=True):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if not node: node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
        node.RemoveAllControlPoints(); node.AddControlPoint(p1); node.AddControlPoint(p2)
        d = node.GetDisplayNode() or node.CreateDefaultDisplayNodes();
        d.SetColor(color); d.SetSelectedColor([1,1,0]); d.SetVisibility(visible)
        node.GetMeasurement("length").SetEnabled(True)
        return node

    def project_point_to_plane_node(point, plane_node):
        origin, normal = np.zeros(3), np.zeros(3)
        plane_node.GetOrigin(origin); plane_node.GetNormal(normal)
        return point - np.dot(point - origin, normal) * normal

    def project_point_to_line_node(point, line_node):
        p1, p2 = np.zeros(3), np.zeros(3)
        line_node.GetNthControlPointPositionWorld(0, p1); line_node.GetNthControlPointPositionWorld(1, p2)
        t_out = vtk.mutable(0); closest_point = np.zeros(3)
        vtk.vtkLine.DistanceToLine(point, p1, p2, t_out, closest_point)
        return closest_point

    try:
        # --- STAGE 0: Clean up old measurements ---
        print("0. Cleaning up old measurement lines...")
        measurement_prefixes = [f"{prefix}L", f"{prefix}R", f"{prefix}E"]
        nodes_to_remove = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if any(n.GetName().startswith(p) for p in measurement_prefixes)]
        for node in nodes_to_remove: slicer.mrmlScene.RemoveNode(node)
        print(f"   ✓ Removed {len(nodes_to_remove)} old '{prefix}' measurement lines.")

        # --- STAGE 1: Get all required nodes ---
        print("\n1. Finding all required nodes...")
        coronal_plane = get_node("Coronal Plane", "vtkMRMLMarkupsPlaneNode")
        orbital_plane = get_node("Orbitale Transverse Plane", "vtkMRMLMarkupsPlaneNode")
        hard_tissue_node = get_node("Ryu_hard_tissue")  # For ocp landmark

        # --- STAGE 2: Create Final Measurements for each side ---
        print("\n2. Creating final measurement lines...")
        created_count = 0
        final_color = (1,0,0) if prefix == "pred_" else (0,1,0)

        for side in ["L", "R"]:
            print(f"   - Processing Side: {side}")
            side_full = "Left" if side == "L" else "Right"
            eyeball_lm_node = get_node(f"{side_full} Eyeball lmrks" if prefix == "pred_" else "Ryu_soft_tissue")
            
            marginal_SOM, marginal_MOM, marginal_LOM = get_node(f"marginal_SOM_{side}"), get_node(f"marginal_MOM_{side}"), get_node(f"marginal_LOM_{side}")
            guiding_LOM = get_node(f"guiding_LOM_{side}")

            # Get landmark positions from eyeball landmarks node
            lc_pos = get_landmark_pos(eyeball_lm_node, f"lc{side}")
            la_pos = get_landmark_pos(eyeball_lm_node, f"la{side}")
            lp_pos = get_landmark_pos(eyeball_lm_node, f"lp{side}")
            oa_pos = get_landmark_pos(eyeball_lm_node, f"oa{side}")
            os_pos = get_landmark_pos(eyeball_lm_node, f"os{side}")
            oi_pos = get_landmark_pos(eyeball_lm_node, f"oi{side}")
            ol_pos = get_landmark_pos(eyeball_lm_node, f"ol{side}")
            om_pos = get_landmark_pos(eyeball_lm_node, f"om{side}")
            gc_pos = get_landmark_pos(eyeball_lm_node, f"gc{side}")
            
            # --- FIX: Get ocp from hard tissue landmarks (no true_ prefix) ---
            ocp_pos = get_landmark_pos_hard_tissue(hard_tissue_node, f"ocp{side}")
            
            # --- Create Measurement Lines (point to plane/line) ---
            create_line(f"{prefix}{side}17", ocp_pos, project_point_to_plane_node(ocp_pos, coronal_plane), final_color)
            create_line(f"{prefix}{side}18", ocp_pos, project_point_to_line_node(ocp_pos, guiding_LOM), final_color)
            create_line(f"{prefix}{side}21", lc_pos, project_point_to_plane_node(lc_pos, marginal_SOM), final_color)
            create_line(f"{prefix}{side}22", lc_pos, project_point_to_plane_node(lc_pos, orbital_plane), final_color)
            create_line(f"{prefix}{side}23", lc_pos, project_point_to_plane_node(lc_pos, marginal_MOM), final_color)
            create_line(f"{prefix}{side}24", lc_pos, project_point_to_plane_node(lc_pos, marginal_LOM), final_color)
            create_line(f"{prefix}{side}25", lc_pos, project_point_to_line_node(lc_pos, guiding_LOM), final_color)
            
            # --- Create Measurement Lines (point to point) ---
            create_line(f"{prefix}{side}26", lc_pos, ocp_pos, final_color)
            create_line(f"{prefix}{side}27", lc_pos, project_point_to_plane_node(lc_pos, coronal_plane), final_color)
            create_line(f"{prefix}{side}28", la_pos, lp_pos, final_color)
            create_line(f"{prefix}{side}29", oa_pos, lc_pos, final_color)
            create_line(f"{prefix}{side}30", la_pos, lp_pos, final_color)

            # --- Create Composite Measurement Lines ---
            create_line(f"{prefix}{side}31", oa_pos, project_point_to_line_node(oa_pos, guiding_LOM), final_color)
            create_line(f"{prefix}{side}32", oa_pos, ocp_pos, final_color)
            create_line(f"{prefix}{side}33", oa_pos, project_point_to_plane_node(oa_pos, coronal_plane), final_color)

            # --- Create Eyeball Geometry Lines ---
            create_line(f"{prefix}E1_{side}", lc_pos, os_pos, final_color)
            create_line(f"{prefix}E2_{side}", lc_pos, om_pos, final_color)
            create_line(f"{prefix}E3_{side}", gc_pos, os_pos, final_color)
            create_line(f"{prefix}E4_{side}", gc_pos, om_pos, final_color)
            create_line(f"{prefix}E5_{side}", os_pos, oi_pos, final_color)
            create_line(f"{prefix}E6_{side}", ol_pos, om_pos, final_color)
            created_count += 21

        slicer.util.infoDisplay(f"SUCCESS: Created {created_count} final measurement lines for prefix '{prefix}'.")

    except Exception as e:
        slicer.util.errorDisplay(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

create_final_measurements(prefix="pred_")  # Red lines with predicted eyeball landmarks
```

</details>

#### True soft tissue distances

The code below creates the soft tissue measurements related to the true eyeball landmarks. 
There will be added lines (similar to the guiding_lines previously) to ensure the parallell measurement theme in the original study. 

(2) Additional True measurements
| original | Slicer abbrv | Original definition | Slicer definition |
|----------|--------------|---------------------|-------------------|
| 21 | true_L21 | left Lens centre (landmark)—left Supraorbitale (transverse plane) | shortest perpendicular distance between the true_lcL and marginal_SOM_L |
| 21 | true_R21 | right Lens centre (landmark)—right Supraorbitale (transverse plane) | shortest perpendicular distance between the true_lcR and marginal_SOM_R |
| 22 | true_L22 | left Lens centre (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the true_lcL and orbitale transverse plane |
| 22 | true_R22 | right Lens centre (landmark)—Orbitale (transverse plane) | shortest perpendicular distance between the true_lcR and orbitale transverse plane |
| 23 | true_L23 | left Lens centre (landmark)—left Medial orbit (sagittal plane) | shortest perpendicular distance between the true_lcL and marginal_MOM_L plane |
| 23 | true_R23 | right Lens centre (landmark)—right Medial orbit (sagittal plane) | shortest perpendicular distance between the true_lcR and marginal_MOM_R plane |
| 24 | true_L24 | left Lens centre (landmark)— left Lateral orbit (sagittal plane) | shortest perpendicular distance between the true_lcL and marginal_LOM_L plane |
| 24 | true_R24 | rightLens centre (landmark)—right Lateral orbit (sagittal plane) | shortest perpendicular distance between the true_lcR and marginal_LOM_R plane |
| 25 | true_L25 | left Lens centre (landmark)—left Lateral orbit (coronal plane) | shortest perpendicular distance between the true_lcL and guiding_LOM_L line |
| 25 | true_R25 | right Lens centre (landmark)—right Lateral orbit (coronal plane) | shortest perpendicular distance between the true_lcR and guiding_LOM_R line |
| 26 | true_L26 | left Lens centre (landmark)—left Optic canal point | shortest perpendicular distance between the true_lcL line and true_ocpL line |
| 26 | true_R26 | right Lens centre (landmark)—right Optic canal point | shortest perpendicular distance between the true_lcR line and true_ocpR line |
| 27 | true_L27 | left Lens centre (landmark)— Coronal plane | shortest perpendicular distance between the true_lcL line and Coronal plane |
| 27 | true_R27 | rightLens centre (landmark)— Coronal plane | shortest perpendicular distance between the true_lcR line and Coronal plane |
| 28 | true_L28 | left Lens anterior (landmark)—left Lens posterior | shortest perpendicular distance between true_laL line and true_lpL line |
| 28 | true_R28 | right Lens anterior (landmark)—right Lens posterior | shortest perpendicular distance between true_laR line and true_lpR line |
| 29 | true_L29 | left Cornea (landmark)—left Lens centre (coronal plane) | shortest perpendicular distance between true_oaL line and true_lcL line |
| 29 | true_R29 | right Cornea (landmark)—right Lens centre (coronal plane) | shortest perpendicular distance between true_oaR line and true_lcR line |
| 30 | true_L30 | left Lens diameter | manual |
| 30 | true_R30 | right Lens diameter | manual |
| 31 | true_L31 | left Cornea (landmark)— left Lateral orbit (coronal plane) (25 + 29) | L25 + L29 (shortest perpendicular distance between the true_oaL line and marginal_LOM_L plane) |
| 31 | true_R31 | right Cornea (landmark)— right Lateral orbit (coronal plane) (25 + 29) | R25 + R29 (shortest perpendicular distance between the true_oaR line and marginal_LOM_R plane) |
| 32 | true_L32 | left Cornea (landmark)—left Optic canal point (26 + 29) | L26 + L29 (shortest perpendicular distance between the true_oaL line and true_ocpL line) |
| 32 | true_R32 | right Cornea (landmark)—right Optic canal point (26 + 29) | R26 + R29 (shortest perpendicular distance between the true_oaR line and true_ocpR line) |
| 33 | true_L33 | left Cornea (landmark)—Coronal plane (27 + 29) | L27 + L29 (shortest perpendicular distance between the true_oaL line and Coronal plane) |
| 33 | true_R33 | right Cornea (landmark)—Coronal plane (27 + 29) | R27 + R29 (shortest perpendicular distance between the true_oaR line and Coronal plane) |
| E1_L | true_E1_L | left Lens centre—left Globe superior (transverse plane) | shortest perpendicular distance between the true_lcL line and true_osL line |
| E1_R | true_E1_R | right Lens centre—right Globe superior (transverse plane) | shortest perpendicular distance between the true_lcR line and true_osR line |
| E2_L | true_E2_L | left Lens centre—left Globe Medial (sagittal plane) | shortest perpendicular distance between the true_lcL line and true_omL line |
| E2_R | true_E2_R | right Lens centre—right Globe Medial (sagittal plane) | shortest perpendicular distance between the true_lcR line and true_omR line |
| E3_L | true_E3_L | left Globe centre—left Globe superior | shortest perpendicular distance between the gcL and true_osL line |
| E3_R | true_E3_R | right Globe centre—right Globe superior | shortest perpendicular distance between the gcR and true_osR line |
| E4_L | true_E4_L | left Globe centre—left Globe medial | shortest perpendicular distance between the gcL and true_omL line |
| E4_R | true_E4_R | rightGlobe centre—right Globe medial | shortest perpendicular distance between the gcR and true_omR line |
| E5_L | true_E5_L | left Globe superior—left Globe inferior | true_osL to true_oiL |
| E5_R | true_E5_R | right Globe superior—right Globe inferior | true_osR to true_oiR |
| E6_L | true_E6_L | left Globe lateral—left Globe medial | true_olL to true_omL |
| E6_R | true_E6_R | right Globe lateral—right Globe medial | true_olR to true_omR |

<details>	
<summary> True soft tissue measurement creation </summary>
	
```python
import slicer
import numpy as np
import vtk

def create_final_measurements(prefix):
    """
    Creates the final, colored measurement lines. This script relies on the
    'guide lines' and anatomical planes already being present in the scene.
    :param prefix: A string, either "pred_" or "true_".
    """
    print("="*80)
    print(f"Creating FINAL MEASUREMENT LINES from guides with prefix: '{prefix}'")
    print("="*80)

    if prefix not in ["pred_", "true_"]:
        slicer.util.errorDisplay("Prefix must be either 'pred_' or 'true_'.")
        return

    # --- Helper Functions (condensed for brevity) ---
    def get_node(name, cls="vtkMRMLNode"):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if not node: raise ValueError(f"Node '{name}' ({cls}) not found.")
        return node
        
    def get_landmark_pos(node, label):
        p_label = f"true_{label}" if prefix == "true_" else label
        if prefix == "pred_" and node.GetControlPointIndexByLabel(p_label) == -1:
            if node.GetControlPointIndexByLabel(f"{label[:-1]}_{label[-1]}") != -1: p_label = f"{label[:-1]}_{label[-1]}"
        idx = node.GetControlPointIndexByLabel(p_label)
        if idx == -1: raise ValueError(f"Landmark '{p_label}' not found in '{node.GetName()}'.")
        pos = np.zeros(3); node.GetNthControlPointPositionWorld(idx, pos)
        return pos

    def get_landmark_pos_hard_tissue(node, label):
        """Special handler for hard tissue landmarks like ocp that don't have true_ prefix."""
        # ocp landmarks are in hard tissue node but without true_ prefix
        idx = node.GetControlPointIndexByLabel(label)
        if idx == -1: raise ValueError(f"Landmark '{label}' not found in '{node.GetName()}'.")
        pos = np.zeros(3); node.GetNthControlPointPositionWorld(idx, pos)
        return pos

    def create_line(name, p1, p2, color, visible=True):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if not node: node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
        node.RemoveAllControlPoints(); node.AddControlPoint(p1); node.AddControlPoint(p2)
        d = node.GetDisplayNode() or node.CreateDefaultDisplayNodes();
        d.SetColor(color); d.SetSelectedColor([1,1,0]); d.SetVisibility(visible)
        node.GetMeasurement("length").SetEnabled(True)
        return node

    def project_point_to_plane_node(point, plane_node):
        origin, normal = np.zeros(3), np.zeros(3)
        plane_node.GetOrigin(origin); plane_node.GetNormal(normal)
        return point - np.dot(point - origin, normal) * normal

    def project_point_to_line_node(point, line_node):
        p1, p2 = np.zeros(3), np.zeros(3)
        line_node.GetNthControlPointPositionWorld(0, p1); line_node.GetNthControlPointPositionWorld(1, p2)
        t_out = vtk.mutable(0); closest_point = np.zeros(3)
        vtk.vtkLine.DistanceToLine(point, p1, p2, t_out, closest_point)
        return closest_point

    try:
        # --- STAGE 0: Clean up old measurements ---
        print("0. Cleaning up old measurement lines...")
        measurement_prefixes = [f"{prefix}L", f"{prefix}R", f"{prefix}E"]
        nodes_to_remove = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode") if any(n.GetName().startswith(p) for p in measurement_prefixes)]
        for node in nodes_to_remove: slicer.mrmlScene.RemoveNode(node)
        print(f"   ✓ Removed {len(nodes_to_remove)} old '{prefix}' measurement lines.")

        # --- STAGE 1: Get all required nodes ---
        print("\n1. Finding all required nodes...")
        coronal_plane = get_node("Coronal Plane", "vtkMRMLMarkupsPlaneNode")
        orbital_plane = get_node("Orbitale Transverse Plane", "vtkMRMLMarkupsPlaneNode")
        hard_tissue_node = get_node("Ryu_hard_tissue")  # For ocp landmark

        # --- STAGE 2: Create Final Measurements for each side ---
        print("\n2. Creating final measurement lines...")
        created_count = 0
        final_color = (1,0,0) if prefix == "pred_" else (0,1,0)

        for side in ["L", "R"]:
            print(f"   - Processing Side: {side}")
            side_full = "Left" if side == "L" else "Right"
            eyeball_lm_node = get_node(f"{side_full} Eyeball lmrks" if prefix == "pred_" else "Ryu_soft_tissue")
            
            marginal_SOM, marginal_MOM, marginal_LOM = get_node(f"marginal_SOM_{side}"), get_node(f"marginal_MOM_{side}"), get_node(f"marginal_LOM_{side}")
            guiding_LOM = get_node(f"guiding_LOM_{side}")

            # Get landmark positions from eyeball landmarks node
            lc_pos = get_landmark_pos(eyeball_lm_node, f"lc{side}")
            la_pos = get_landmark_pos(eyeball_lm_node, f"la{side}")
            lp_pos = get_landmark_pos(eyeball_lm_node, f"lp{side}")
            oa_pos = get_landmark_pos(eyeball_lm_node, f"oa{side}")
            os_pos = get_landmark_pos(eyeball_lm_node, f"os{side}")
            oi_pos = get_landmark_pos(eyeball_lm_node, f"oi{side}")
            ol_pos = get_landmark_pos(eyeball_lm_node, f"ol{side}")
            om_pos = get_landmark_pos(eyeball_lm_node, f"om{side}")
            gc_pos = get_landmark_pos(eyeball_lm_node, f"gc{side}")
            
            # --- FIX: Get ocp from hard tissue landmarks (no true_ prefix) ---
            ocp_pos = get_landmark_pos_hard_tissue(hard_tissue_node, f"ocp{side}")
            
            # --- Create Measurement Lines (point to plane/line) ---
            create_line(f"{prefix}{side}17", ocp_pos, project_point_to_plane_node(ocp_pos, coronal_plane), final_color)
            create_line(f"{prefix}{side}18", ocp_pos, project_point_to_line_node(ocp_pos, guiding_LOM), final_color)
            create_line(f"{prefix}{side}21", lc_pos, project_point_to_plane_node(lc_pos, marginal_SOM), final_color)
            create_line(f"{prefix}{side}22", lc_pos, project_point_to_plane_node(lc_pos, orbital_plane), final_color)
            create_line(f"{prefix}{side}23", lc_pos, project_point_to_plane_node(lc_pos, marginal_MOM), final_color)
            create_line(f"{prefix}{side}24", lc_pos, project_point_to_plane_node(lc_pos, marginal_LOM), final_color)
            create_line(f"{prefix}{side}25", lc_pos, project_point_to_line_node(lc_pos, guiding_LOM), final_color)
            
            # --- Create Measurement Lines (point to point) ---
            create_line(f"{prefix}{side}26", lc_pos, ocp_pos, final_color)
            create_line(f"{prefix}{side}27", lc_pos, project_point_to_plane_node(lc_pos, coronal_plane), final_color)
            create_line(f"{prefix}{side}28", la_pos, lp_pos, final_color)
            create_line(f"{prefix}{side}29", oa_pos, lc_pos, final_color)
            create_line(f"{prefix}{side}30", la_pos, lp_pos, final_color)

            # --- Create Composite Measurement Lines ---
            create_line(f"{prefix}{side}31", oa_pos, project_point_to_line_node(oa_pos, guiding_LOM), final_color)
            create_line(f"{prefix}{side}32", oa_pos, ocp_pos, final_color)
            create_line(f"{prefix}{side}33", oa_pos, project_point_to_plane_node(oa_pos, coronal_plane), final_color)

            # --- Create Eyeball Geometry Lines ---
            create_line(f"{prefix}E1_{side}", lc_pos, os_pos, final_color)
            create_line(f"{prefix}E2_{side}", lc_pos, om_pos, final_color)
            create_line(f"{prefix}E3_{side}", gc_pos, os_pos, final_color)
            create_line(f"{prefix}E4_{side}", gc_pos, om_pos, final_color)
            create_line(f"{prefix}E5_{side}", os_pos, oi_pos, final_color)
            create_line(f"{prefix}E6_{side}", ol_pos, om_pos, final_color)
            created_count += 21

        slicer.util.infoDisplay(f"SUCCESS: Created {created_count} final measurement lines for prefix '{prefix}'.")

    except Exception as e:
        slicer.util.errorDisplay(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

create_final_measurements(prefix="true_")  # Green lines with true eyeball landmarks (both use same ocp from hard tissue)
```

</details>



#### Comparison of predicted vs true landmarks and distances 
It will create two comparison tables: (1) for comparing length measurements between the "artificial" eyeball model and the true eyeball that were measured by Ryu et al. (2024)[^2] in the original study to create the regressions; (2) for measuring the distance between the true vs artificial eyeball landmarks. 


<details>	
<summary> Comparison code </summary>
	
```python
import slicer
import qt
import numpy as np

def get_landmark_node(pattern, required=True):
    """Finds a fiducial node by a wildcard pattern."""
    try:
        node = slicer.util.getNode(pattern)
        if node: return node
    except slicer.util.MRMLNodeNotFoundException: pass
    
    nodes = [n for n in slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode") if pattern.replace('*','') in n.GetName()]
    if not nodes:
        if required: raise ValueError(f"Could not find required landmark node: '{pattern}'")
        return None
    return nodes[0]

def get_pos(lmk_node, label):
    """Gets the world position of a landmark by its label."""
    if not lmk_node: return None
    idx = lmk_node.GetControlPointIndexByLabel(label)
    if idx == -1: return None
    pos = np.zeros(3); lmk_node.GetNthControlPointPositionWorld(idx, pos)
    return pos

def get_all_lines_by_prefix(prefix):
    """Gets all line nodes with a given prefix and returns a dict of their lengths."""
    lines_dict = {}
    line_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    for node in line_nodes:
        if node.GetName().startswith(prefix):
            key = node.GetName().replace(prefix, "")
            lines_dict[key] = node.GetMeasurement('length').GetValue()
    return lines_dict

def get_line_length(line_name):
    """Gets the length of a specific line by name."""
    try:
        node = slicer.util.getFirstNodeByName(line_name)
        if node and node.IsA("vtkMRMLMarkupsLineNode"):
            return node.GetMeasurement('length').GetValue()
    except: pass
    return None

def select_eyeball_sex():
    """
    Opens a dialog for the user to select which eyeballs were used (Male or Female).
    Returns the selected sex as a string ('Male' or 'Female'), or None if cancelled.
    """
    dialog = qt.QDialog(slicer.util.mainWindow())
    dialog.setWindowTitle("Eyeball Sex Selection")
    dialog.setModal(True)
    dialog.setMinimumWidth(400)
    
    layout = qt.QVBoxLayout(dialog)
    
    # Info label
    info_label = qt.QLabel(
        "Which eyeballs did you use for placement?\n\n"
        "The regression equations are sex-specific, so please confirm "
        "whether you placed Male or Female eyeball models."
    )
    info_label.setWordWrap(True)
    layout.addWidget(info_label)
    
    # Radio buttons
    layout.addSpacing(10)
    button_group = qt.QButtonGroup(dialog)
    
    female_radio = qt.QRadioButton("Female Eyeballs")
    male_radio = qt.QRadioButton("Male Eyeballs")
    female_radio.setChecked(True)  # Default selection
    
    button_group.addButton(female_radio, 0)
    button_group.addButton(male_radio, 1)
    
    layout.addWidget(female_radio)
    layout.addWidget(male_radio)
    
    # Buttons
    layout.addSpacing(10)
    button_layout = qt.QHBoxLayout()
    
    ok_button = qt.QPushButton("OK")
    cancel_button = qt.QPushButton("Cancel")
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    layout.addLayout(button_layout)
    
    layout.addStretch(1)
    
    # Use a container to store the result
    result_container = {"selected_sex": None}
    
    # Connections
    def on_ok():
        result_container["selected_sex"] = "Female" if female_radio.checked else "Male"
        dialog.accept()
    
    def on_cancel():
        result_container["selected_sex"] = None
        dialog.reject()
    
    ok_button.clicked.connect(on_ok)
    cancel_button.clicked.connect(on_cancel)
    
    # Show dialog
    result = dialog.exec_()
    
    return result_container["selected_sex"]

def calculate_additional_predictions(sex, side_char):
    """
    Calculates additional predicted measurements (L/R27, L/R33 from L/R15).
    These are NOT used for eyeball placement but are calculated for comparison.
    """
    predictions = {}
    
    # Get core measurements
    L1 = get_line_length(f"{side_char}1")
    L8 = get_line_length(f"{side_char}8")
    L15 = get_line_length(f"{side_char}15")
    
    if L1 is None or L8 is None or L15 is None:
        return predictions
    
    # Sex-specific regression equations
    if sex == "Female":
        # L27 from L15 (additional prediction, not used for placement)
        pred_L27_from_L15 = 1.007 * L15 + 9.552
        # L33 from L15 (additional prediction, not used for placement)
        pred_L33_from_L15 = 1.005 * L15 + 14.700
    else:  # Male
        # L27 from L15 (additional prediction, not used for placement)
        pred_L27_from_L15 = 0.989 * L15 + 11.550
        # L33 from L15 (additional prediction, not used for placement)
        pred_L33_from_L15 = 0.950 * L15 + 19.126
    
    predictions[f"{side_char}27_from_L15"] = pred_L27_from_L15
    predictions[f"{side_char}33_from_L15"] = pred_L33_from_L15
    
    return predictions

def run_eye_analysis():
    """Compares predicted vs. true landmarks and measurement lengths for the eye prediction method."""
    print("="*80); print("      Starting Eye Prediction Comparison Analysis"); print("="*80)

    try:
        # --- 0. Get sex from user ---
        sex = select_eyeball_sex()
        if sex is None:
            print("Analysis cancelled by user.")
            return
        
        print(f"\n✓ Selected eyeball sex: {sex}\n")

        # --- 1. Find landmark nodes ---
        print("1. Finding landmark nodes...")
        true_lmks_node = get_landmark_node("Ryu_soft_tissue")
        pred_left_lmks_node = get_landmark_node("Left Eyeball lmrks", required=False)
        pred_right_lmks_node = get_landmark_node("Right Eyeball lmrks", required=False)
        print(f"   ✓ True landmarks: '{true_lmks_node.GetName()}'")
        print(f"   ✓ Predicted Left: '{pred_left_lmks_node.GetName() if pred_left_lmks_node else 'NOT FOUND'}'")
        print(f"   ✓ Predicted Right: '{pred_right_lmks_node.GetName() if pred_right_lmks_node else 'NOT FOUND'}'")

        # --- 2. Landmark-to-Landmark Distance Calculation ---
        print("\n2. Calculating landmark-to-landmark distances (3D Error)...")
        landmark_types = ['ocp', 'lc', 'la', 'lp', 'oa', 'os', 'oi', 'ol', 'om', 'gc']
        landmark_results = []
        for side_char, pred_node in [('L', pred_left_lmks_node), ('R', pred_right_lmks_node)]:
            for lmk_type in landmark_types:
                pred_label = f"{lmk_type}{side_char}"
                if lmk_type == 'ocp' and side_char == 'L' and pred_node:
                    if pred_node.GetControlPointIndexByLabel(f"{lmk_type}_{side_char}") != -1:
                        pred_label = f"{lmk_type}_{side_char}"
                true_label = f"true_{lmk_type}{side_char}"
                true_pos, pred_pos = get_pos(true_lmks_node, true_label), get_pos(pred_node, pred_label)
                if true_pos is not None and pred_pos is not None:
                    dist = np.linalg.norm(true_pos - pred_pos)
                    landmark_results.append((pred_label, f"{dist:.2f} mm"))

        # --- 3. Measurement Length Difference Calculation ---
        print("\n3. Calculating measurement length differences...")
        predicted_lengths = get_all_lines_by_prefix("pred_")
        true_lengths = get_all_lines_by_prefix("true_")
        
        measurement_results = []
        all_measurement_keys = sorted(list(set(predicted_lengths.keys()) | set(true_lengths.keys())))

        for key in all_measurement_keys:
            pred_len = predicted_lengths.get(key)
            true_len = true_lengths.get(key)
            pred_str = f"{pred_len:.2f} mm" if pred_len is not None else "N/A"
            true_str = f"{true_len:.2f} mm" if true_len is not None else "N/A"
            diff_str = f"{abs(pred_len - true_len):.2f} mm" if pred_len is not None and true_len is not None else "N/A"
            measurement_results.append((key, pred_str, true_str, diff_str))

        # --- 4. Additional Predictions (L/R27, L/R33 from L/R15) ---
        print("\n4. Calculating additional predictions (not used for placement)...")
        additional_results = []
        
        for side_char in ['L', 'R']:
            predictions = calculate_additional_predictions(sex, side_char)
            
            for pred_key, pred_value in predictions.items():
                # Extract measurement type (e.g., "27" from "L27_from_L15")
                meas_type = pred_key.split('_')[0]  # e.g., "L27"
                
                # Get true measurement
                true_len = get_line_length(f"true_{meas_type}")
                
                pred_str = f"{pred_value:.2f} mm"
                true_str = f"{true_len:.2f} mm" if true_len is not None else "N/A"
                diff_str = f"{abs(pred_value - true_len):.2f} mm" if true_len is not None else "N/A"
                
                # Note: These are regression predictions, not visualized lines
                additional_results.append((f"{pred_key} (regr.)", pred_str, true_str, diff_str))

        # --- 5. Print Formatted Results ---
        print("\n\n" + "="*80); print("                          FINAL ANALYSIS RESULTS"); print("="*80)
        print(f"\nEyeball Sex Used: {sex}\n")
        
        if landmark_results:
            print("\n### Table 1: Landmark Positional Error (3D Distance)\n")
            print("| Landmark | Error (True vs. Predicted) |")
            print("|---|---|")
            for label, dist_str in sorted(landmark_results): 
                print(f"| `{label}` | {dist_str} |")
        
        if measurement_results:
            print("\n\n### Table 2: Visualized Measurement Length Comparison\n")
            print("| Measurement | Predicted Length | True Length | Absolute Difference |")
            print("|---|---|---|---|")
            for key, pred_str, true_str, diff_str in measurement_results: 
                print(f"| `{key}` | {pred_str} | {true_str} | {diff_str} |")
        
        if additional_results:
            print("\n\n### Table 3: Additional Predicted Measurements (Not Used for Placement)\n")
            print("| Prediction | Predicted Value | True Measurement | Absolute Difference |")
            print("|---|---|---|---|")
            for key, pred_str, true_str, diff_str in additional_results: 
                print(f"| `{key}` | {pred_str} | {true_str} | {diff_str} |")
        
        print("\n" + "="*80); print("✓ Analysis complete."); print("="*80)

    except Exception as e:
        slicer.util.errorDisplay(f"An error occurred during analysis: {e}")
        raise e

# --- Run the Analysis ---
run_eye_analysis()
```

</details>






What to expect? The code will print some information on the console, something like this: 

```python
================================================================================
      Starting Eye Prediction Comparison Analysis
================================================================================

✓ Selected eyeball sex: Female

1. Finding landmark nodes...
   ✓ True landmarks: 'Ryu_soft_tissue'
   ✓ Predicted Left: 'Left Eyeball lmrks'
   ✓ Predicted Right: 'Right Eyeball lmrks'

2. Calculating landmark-to-landmark distances (3D Error)...

3. Calculating measurement length differences...

4. Calculating additional predictions (not used for placement)...


================================================================================
                          FINAL ANALYSIS RESULTS
================================================================================

Eyeball Sex Used: Female


### Table 1: Landmark Positional Error (3D Distance)

| Landmark | Error (True vs. Predicted) |
|---|---|
| `gcL` | 2.67 mm |
| `gcR` | 2.67 mm |
| `laL` | 4.53 mm |
| `laR` | 3.23 mm |
| `lcL` | 3.78 mm |
| `lcR` | 2.60 mm |
| `lpL` | 3.14 mm |
| `lpR` | 2.31 mm |
| `oaL` | 5.62 mm |
| `oaR` | 4.03 mm |
| `oiL` | 6.16 mm |
| `oiR` | 3.53 mm |
| `olL` | 4.58 mm |
| `olR` | 5.22 mm |
| `omL` | 2.42 mm |
| `omR` | 2.07 mm |
| `osL` | 2.65 mm |
| `osR` | 6.32 mm |


### Table 2: Visualized Measurement Length Comparison

| Measurement | Predicted Length | True Length | Absolute Difference |
|---|---|---|---|
| `E1_L` | 13.81 mm | 13.18 mm | 0.63 mm |
| `E1_R` | 13.81 mm | 14.89 mm | 1.08 mm |
| `E2_L` | 15.19 mm | 15.25 mm | 0.06 mm |
| `E2_R` | 15.19 mm | 16.16 mm | 0.98 mm |
| `E3_L` | 11.94 mm | 12.50 mm | 0.56 mm |
| `E3_R` | 11.94 mm | 13.20 mm | 1.26 mm |
| `E4_L` | 12.19 mm | 11.86 mm | 0.33 mm |
| `E4_R` | 12.19 mm | 11.66 mm | 0.53 mm |
| `E5_L` | 23.98 mm | 23.96 mm | 0.01 mm |
| `E5_R` | 23.98 mm | 24.73 mm | 0.75 mm |
| `E6_L` | 24.01 mm | 22.29 mm | 1.72 mm |
| `E6_R` | 24.01 mm | 23.15 mm | 0.86 mm |
| `L17` | 2.56 mm | 2.56 mm | 0.00 mm |
| `L18` | 48.80 mm | 48.80 mm | 0.00 mm |
| `L21` | 15.60 mm | 17.83 mm | 2.23 mm |
| `L22` | 19.18 mm | 16.94 mm | 2.23 mm |
| `L23` | 21.75 mm | 23.58 mm | 1.83 mm |
| `L24` | 16.67 mm | 14.85 mm | 1.83 mm |
| `L25` | 19.58 mm | 16.78 mm | 2.80 mm |
| `L26` | 51.30 mm | 50.52 mm | 0.78 mm |
| `L27` | 43.37 mm | 40.92 mm | 2.45 mm |
| `L28` | 3.73 mm | 4.43 mm | 0.70 mm |
| `L29` | 4.67 mm | 4.51 mm | 0.16 mm |
| `L30` | 3.73 mm | 4.43 mm | 0.70 mm |
| `L31` | 22.44 mm | 18.36 mm | 4.08 mm |
| `L32` | 55.66 mm | 54.86 mm | 0.80 mm |
| `L33` | 47.96 mm | 44.69 mm | 3.27 mm |
| `R17` | 0.47 mm | 0.47 mm | 0.00 mm |
| `R18` | 45.40 mm | 45.40 mm | 0.00 mm |
| `R21` | 15.03 mm | 17.15 mm | 2.12 mm |
| `R22` | 18.80 mm | 16.68 mm | 2.12 mm |
| `R23` | 19.97 mm | 21.47 mm | 1.50 mm |
| `R24` | 15.65 mm | 14.15 mm | 1.50 mm |
| `R25` | 18.71 mm | 17.54 mm | 1.18 mm |
| `R26` | 47.44 mm | 48.83 mm | 1.38 mm |
| `R27` | 40.80 mm | 40.90 mm | 0.10 mm |
| `R28` | 3.73 mm | 4.43 mm | 0.70 mm |
| `R29` | 4.67 mm | 4.70 mm | 0.03 mm |
| `R30` | 3.73 mm | 4.43 mm | 0.70 mm |
| `R31` | 21.65 mm | 20.51 mm | 1.14 mm |
| `R32` | 51.72 mm | 52.86 mm | 1.13 mm |
| `R33` | 45.40 mm | 44.76 mm | 0.63 mm |


### Table 3: Additional Predicted Measurements (Not Used for Placement)

| Prediction | Predicted Value | True Measurement | Absolute Difference |
|---|---|---|---|
| `L27_from_L15 (regr.)` | 42.88 mm | 40.92 mm | 1.96 mm |
| `L33_from_L15 (regr.)` | 47.96 mm | 44.69 mm | 3.27 mm |
| `R27_from_L15 (regr.)` | 40.31 mm | 40.90 mm | 0.59 mm |
| `R33_from_L15 (regr.)` | 45.40 mm | 44.76 mm | 0.63 mm |

================================================================================
✓ Analysis complete.
================================================================================
```



### Output
To copy all the linear measurements to clipboard, use the method described in [this guide](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/004_Copying%20measurements%20to%20Clipboard.md). 

> [!IMPORTANT]
> It is very important that you do not treat the pre-programmed lines with set length as measurements in your statistical analysis, therefore there is an example below. ALSO, the additional prediction lines (Table 3) will NOT show up in this!


| ID | line node name | length in mm | Note |
|--------|-------------|-------|-------|
| (none) | guiding_SOM_L | 75 | ❌ - not a real measurement |
| | guiding_SOM_R | 75 | ❌ - not a real measurement |
| | guiding_IOM_L | 75 | ❌ - not a real measurement |
| | guiding_IOM_R | 75 | ❌ - not a real measurement |
| | guiding_MOM_L | 75 | ❌ - not a real measurement |
| | guiding_MOM_R | 75 | ❌ - not a real measurement |
| | guiding_LOM_L | 75 | ❌ - not a real measurement |
| | guiding_LOM_R | 75 | ❌ - not a real measurement |
| | L1 | 35.86 | |
| | L8 | 28.3 | |
| | L15 | 2.49 | |
| | L20 | 1.97 | |
| | R1 | 34.26 | |
| | R8 | 28.96 | |
| | R15 | 4.35 | |
| | R20 | 0.12 | |
| | L2 | 17.31 | |
| | L3 | 18.55 | |
| | L4 | 24.99 | |
| | L5 | 10.87 | |
| | L6 | 8.85 | |
| | L7 | 19.45 | |
| | L9 | 6.48 | |
| | L10 | 21.81 | |
| | L11 | 23.98 | |
| | L12 | 49.87 | |
| | L13 | 36.73 | |
| | L14 | 11.75 | |
| | L16 | 17.68 | |
| | L19 | 10.43 | |
| | R2 | 19.59 | |
| | R3 | 14.67 | |
| | R4 | 25.53 | |
| | R5 | 8.73 | |
| | R6 | 9.04 | |
| | R7 | 18.67 | |
| | R9 | 5.8 | |
| | R10 | 21.91 | |
| | R11 | 19.36 | |
| | R12 | 48.1 | |
| | R13 | 35.23 | |
| | R14 | 9.81 | |
| | R16 | 16.99 | |
| | R19 | 12.58 | |
| | C1 | 91.35 | |
| | C2 | 21.12 | |
| | guide_pred_lcL | 50 | ❌ - not a real measurement |
| | guide_pred_ocpL | 50 | ❌ - not a real measurement |
| | guide_pred_laL | 50 | ❌ - not a real measurement |
| | guide_pred_oaL | 50 | ❌ - not a real measurement |
| | guide_pred_lpL | 50 | ❌ - not a real measurement |
| | guide_pred_omL | 50 | ❌ - not a real measurement |
| | guide_pred_olL | 50 | ❌ - not a real measurement |
| | guide_pred_oiL | 50 | ❌ - not a real measurement |
| | guide_pred_osL | 50 | ❌ - not a real measurement |
| | guide_pred_lcR | 50 | ❌ - not a real measurement |
| | guide_pred_laR | 50 | ❌ - not a real measurement |
| | guide_pred_oaR | 50 | ❌ - not a real measurement |
| | guide_pred_lpR | 50 | ❌ - not a real measurement |
| | guide_pred_omR | 50 | ❌ - not a real measurement |
| | guide_pred_olR | 50 | ❌ - not a real measurement |
| | guide_pred_oiR | 50 | ❌ - not a real measurement |
| | guide_pred_osR | 50 | ❌ - not a real measurement |
| | guide_true_lcL | 50 | ❌ - not a real measurement |
| | guide_true_laL | 50 | ❌ - not a real measurement |
| | guide_true_oaL | 50 | ❌ - not a real measurement |
| | guide_true_lpL | 50 | ❌ - not a real measurement |
| | guide_true_omL | 50 | ❌ - not a real measurement |
| | guide_true_olL | 50 | ❌ - not a real measurement |
| | guide_true_oiL | 50 | ❌ - not a real measurement |
| | guide_true_osL | 50 | ❌ - not a real measurement |
| | guide_true_lcR | 50 | ❌ - not a real measurement |
| | guide_true_ocpR | 50 | ❌ - not a real measurement |
| | guide_true_laR | 50 | ❌ - not a real measurement |
| | guide_true_oaR | 50 | ❌ - not a real measurement |
| | guide_true_lpR | 50 | ❌ - not a real measurement |
| | guide_true_omR | 50 | ❌ - not a real measurement |
| | guide_true_olR | 50 | ❌ - not a real measurement |
| | guide_true_oiR | 50 | ❌ - not a real measurement |
| | guide_true_osR | 50 | ❌ - not a real measurement |
| | pred_L17 | 5.1 | |
| | pred_L18 | 21.81 | |
| | pred_L21 | 13.08 | |
| | pred_L22 | 15.22 | |
| | pred_L23 | 19.96 | |
| | pred_L24 | 15.9 | |
| | pred_L25 | 18.88 | |
| | pred_L26 | 19.69 | |
| | pred_L27 | 12.67 | |
| | pred_L28 | 3.73 | |
| | pred_L29 | 4.67 | |
| | pred_L30 | 3.73 | |
| | pred_L31 | 21.62 | |
| | pred_L32 | 24.23 | |
| | pred_L33 | 17.2 | |
| | pred_E1_L | 13.81 | |
| | pred_E2_L | 15.19 | |
| | pred_E3_L | 11.94 | |
| | pred_E4_L | 12.19 | |
| | pred_E5_L | 23.98 | |
| | pred_E6_L | 24.01 | |
| | pred_R17 | 3.73 | |
| | pred_R18 | 19.3 | |
| | pred_R21 | 13.31 | |
| | pred_R22 | 14.39 | |
| | pred_R23 | 19.33 | |
| | pred_R24 | 14.93 | |
| | pred_R25 | 18.08 | |
| | pred_R26 | 19.83 | |
| | pred_R27 | 14.55 | |
| | pred_R28 | 3.73 | |
| | pred_R29 | 4.67 | |
| | pred_R30 | 3.73 | |
| | pred_R31 | 21.18 | |
| | pred_R32 | 24.4 | |
| | pred_R33 | 19.07 | |
| | pred_E1_R | 13.81 | |
| | pred_E2_R | 15.19 | |
| | pred_E3_R | 11.94 | |
| | pred_E4_R | 12.19 | |
| | pred_E5_R | 23.98 | |
| | pred_E6_R | 24.01 | |
| | true_L17 | 14.18 | |
| | true_L18 | 23.4 | |
| | true_L21 | 16.19 | |
| | true_L22 | 12.11 | |
| | true_L23 | 18 | |
| | true_L24 | 17.86 | |
| | true_L25 | 18.16 | |
| | true_L26 | 15.44 | |
| | true_L27 | 0.78 | |
| | true_L28 | 5.6 | |
| | true_L29 | 9.49 | |
| | true_L30 | 5.6 | |
| | true_L31 | 17.3 | |
| | true_L32 | 23.61 | |
| | true_L33 | 8.51 | |
| | true_E1_L | 20.94 | |
| | true_E2_L | 10.72 | |
| | true_E3_L | 16.14 | |
| | true_E4_L | 12.03 | |
| | true_E5_L | 30.13 | |
| | true_E6_L | 24.74 | |
| | true_R17 | 12.51 | |
| | true_R18 | 19.5 | |
| | true_R21 | 15.36 | |
| | true_R22 | 12.35 | |
| | true_R23 | 18.6 | |
| | true_R24 | 15.66 | |
| | true_R25 | 15.99 | |
| | true_R26 | 16.78 | |
| | true_R27 | 1.12 | |
| | true_R28 | 6.34 | |
| | true_R29 | 9.02 | |
| | true_R30 | 6.34 | |
| | true_R31 | 16.14 | |
| | true_R32 | 24.44 | |
| | true_R33 | 10.11 | |
| | true_E1_R | 19.68 | |
| | true_E2_R | 18 | |
| | true_E3_R | 17 | |
| | true_E4_R | 16.29 | |
| | true_E5_R | 32.35 | |
| | true_E6_R | 30.52 | |


**IDs will return none or unknown if your data was anonymised appropriately**



## Bibliography

[^1]: [Slicer Script Repository](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html)
[^2]: Ryu, J. Y., et al. (2024). "Developing an eyeball positioning method in the eye orbit for craniofacial identification in Korean population." Scientific Reports 14(1).
[^3]: Martin, R. (1928). Lehrbuch der Anthropologie in systematischer Darstellung: mit besonderer Berücksichtigung der anthropologischen Methoden ; für Studierende, Ärzte und Forschungsreisendechichte, Morphologische Methoden. Jena, Gustav Fisher.
[^4]: Knussmann, R. (1988). Anthropologie: Handbuch der vergleichenden Biologie des Menschen, G. Fischer.
[^5]: Guyomarc'h, P., et al. (2012). "Anatomical placement of the human eyeball in the orbit--validation using CT scans of living adults and prediction for facial approximation." J Forensic Sci 57(5): 1271–1275.

[^5]: Stephan, C. N. and P. L. Davidson (2008). "The placement of the human eyeball and canthi in craniofacial identification." Journal of Forensic Sciences 53(3): 612–619.
[^6]: Guyomarc'h, P., et al. (2012). "Anatomical Placement of the Human Eyeball in the Orbit-Validation Using CT Scans of Living Adults and Prediction for Facial Approximation." Journal of Forensic Sciences 57(5): 1271–1275.
