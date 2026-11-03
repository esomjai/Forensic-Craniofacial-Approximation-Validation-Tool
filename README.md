# Forensic Craniofacial Approximation Guidelines Validation Tool
Often comparisons of the theoretical and anatomical basis, data collection methods, reliability and success rates, as well as details of the sample population used to establish these guides cannot be readily made due to their heterogeneity, leaving them to interpret these recommendations and assess their limitations.
To improve repeatibility of forensic craniofacial approximation methods, this project aims to “translate” well-known techniques into the world of medical imaging and Python with the help of the open-source programme, 3D Slicer. Please visit their official website for  more information and free download.

<img width="557" height="245" alt="Picture1" src="https://github.com/user-attachments/assets/76380451-d877-44f0-927d-29eeb0469054" />


All methodology was developed on [NMDID](https://nmdid.unm.edu/welcome)[^1] post-mortem CTs (Edgar, HJH; Daneshvari Berry, S; Moes, E; Adolphi, NL; Bridges, P; Nolte, KB (2020). New Mexico Decedent Image Database. Office of the Medical Investigator, University of New Mexico. doi.org/10.25827/5s8c-n515.)  but are shown in the guides using the Sample Data by 3D Slicer which is openly accessible.

If this is your first time working with Slicer, please start in the "Start here" folder and First Steps.md file.

When noticing any errors, please contact me!

This is a work in progress repository, so take everything with a pinch of salt :)

> [!IMPORTANT]
> Please note that these guidelines are the researcher’s interpretation of the cited literature. If you notice any errors or have any questions, please do not hesitate to get in touch at [e.m.somjai@dundee.ac.uk](mailto:e.m.somjai@dundee.ac.uk). 

### Setup (Preparation of the raw DICOM files)
For most protocols, the first step is the re-orientation of the scan in the Frankfort Horizontal Plane (FHP), visualising the FHP and translating the scan so that nasion is at coordinates 0,0,0.  
  - For a step-by-step tutorial,  please visit [this page](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/002_Realign%20CT%20in%20the%20standard%20FHP.md)
  - For the .json file and code only, go to [this release](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/002_Realignment%20GUI.md))
If you choose to do a segmentation, follow the tutorial at [ROI vs Segmentation](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/003_Roi%20vs%20Segmentation.md)

Do not forget to re-visit the [tutorial](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/blob/basics/004_Copying%20measurements%20to%20Clipboard.md) or [code](https://github.com/esomjai/ForensicCraniofacialApproximationDatabase/releases/tag/CopyMeasurementsToClipboard) for copying measurements to the clipboard

For a fully transparent format, I recommend having 3 tables: 
1) measurement.csv - output tables for each method, as it appears in the GUI populated by scene information
2) RStudio.csv - to run comparison between any or all prediction methods; added to the end of each GUI
3) population.csv - to have population data with meta-rich information separately

**An RStudio script to run landmark error data for nose predictions is currently underway**

#### Currently available methodologies for nose approximation and their original papers are: 

Method name | Method reference | Step-by-step explanation | Graphic User Interface
-- | -- | -- | --
Two Tangent | Gerasimow, 1955 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/0b9f33b72407d2e59e15148d74327f73cfa04910/Nose%20predictions/Gerasimow-MaltaisLapointe%20Two%20tangent%20method.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/0b9f33b72407d2e59e15148d74327f73cfa04910/Nose%20predictions/Gerasimow%20Maltais-LaPointe%20GUI.md)
Threefold ANS | Krogman & Iscan, 1986 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Threefold%20ANS.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/0b9f33b72407d2e59e15148d74327f73cfa04910/Nose%20predictions/Threefold%20ANS%20GUI.md)
Aesthetic Method | Prokopec & Ubelaker, 2002 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Prokopec%26Ubelaker%20Aesthetic%20Method.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/0b9f33b72407d2e59e15148d74327f73cfa04910/Nose%20predictions/Prokopec-Ubelaker%20module.md)
Stephan's Method | Stephan, 2003 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Stephan%202003.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Stephan%20et%20al%20GUI.md)
The Rynn method | Rynn et al. 2010 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Rynn's%20(2010)%20method.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Rynn%20GUI.md)
The Tedeschi-Oliviera method | Tedeschi-Oliviera (2016) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Tedeschi-Oliviera%20method.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Tedeschi-Oliviera%20GUI.md)
The Ridel et al. method | Ridel et al. 2018 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20et%20al.%202018.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ridel%20GUI.md)
The Ryu method | Ryu et al. 2020 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ryu%20et%20al.%202020.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Ryu%20GUI.md)
The Thitiorul method | Thitiorul et al. 2020 | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Thitiorul2020.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Thitiorul%20(2020)%20GUI.md)
The Purkait and Singh method | Purkait & Singh (2024) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Purkait%20and%20Singh%202024.md) | [link](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Purkait%20and%20Singh%202024%20GUI.md)








[^1]: Edgar, HJH; Daneshvari Berry, S; Moes, E; Adolphi, NL; Bridges, P; Nolte, KB (2020). New Mexico Decedent Image Database. Office of the Medical Investigator, University of New Mexico. doi.org/10.25827/5s8c-n515.
