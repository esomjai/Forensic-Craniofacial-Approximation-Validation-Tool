This is a beginner’s guide to the steps after installing 3D Slicer.

We will discuss how to use the built-in scans, how to open DICOM (CT) files and set up a general scene.
We’d recommend taking a look at the “Good-to-Know” section at the bottom to understand the inner workings of Slicer and for top tips to prevent headaches when using Python for the first time.


### Use Sample Data

For demonstration purposes and protecting personal data, all of the written and video guides feature the publicly available built-in CBCT scan. These can all be found in the main menu in Slicer by clicking _File>Download Sample Data_.
![start1](https://github.com/user-attachments/assets/c18356ae-57b9-4b98-8d58-94d22961c797)

This video shows how you can load it from the starts screen – feel free to explore the sample data, however, it is likely that you will use unique data for research.

https://github.com/user-attachments/assets/5404a8c2-8025-4d82-9438-0cfa828a5199

### Loading DICOM Data

Click on the second icon to the left in the second row of the Menu that says _“DCM”_
![dicom](https://github.com/user-attachments/assets/b5030de6-c3ea-4d53-a029-4cbfc398bb70)
This empty window should open up:
![dicom2](https://github.com/user-attachments/assets/b16c1a76-4046-44b2-8f12-256596b5c320)

Click on the button _“Import DICOM files”_ – that should open up the file finder. You should be able to open it up from a cloud-based folder e.g. from OneDrive if synced, but I would recommend saving it somewhere offline you can find it easily.

Choose the folder you wish to open (if you decide to download a CT from a database, it will likely be compressed and you need to unzip it for Slicer to “see”. It still may still display an empty folder, but marching on, click **IMPORT**):
![dicom3](https://github.com/user-attachments/assets/822316ae-3e42-4007-8284-e9a9d40d755c)

This progress bar should appear loading, then it should say ”_Import completed, added x patients, x instances_”.

Now, the ID of your imported scans should appear in the before-empty DICOM database list.
![dicom3 1](https://github.com/user-attachments/assets/93816ee2-5809-49ab-acbb-2d3bb4102be7)
Note that usually databases will anonymise their CTs, so do not expect anything in the _Patient name_ column at the beginning. You should click on the row with your freshly imported CT, then click _Load_, or simply open it via a double click. 
![dicom4](https://github.com/user-attachments/assets/ef27375a-bdaf-495d-8254-7c58250ec272)

Notice that the left panel has now content – named conventionally after the CT scan data. The right side 3D viewer will still be empty – no worries, it is as it should be! Find the cube icon next to _”NAMED CT”_  on the bottom of the left hand side list, click, hold and drag it into the 3d environment – the blue window:
![dicom5](https://github.com/user-attachments/assets/fb5bae0f-3956-4bd4-9439-cb3bc9a9ad00)
> [!NOTE]
> In the screenshot example, the conventions of the NMDID database are shown, but no images from the database!

The image will look unconventional at first as it will load into the 3D Scene without pre-sets – we will fine-tune this in the next section. You have now loaded a DICOM in Slicer! The icon you dragged is good to remember – if the Red/Green/Yellow windows suddenly stop showing the slices of the CT at any point, clicking on it twice (to disappear and re-appear) will fix it. This can be a lifesaver when placing landmarks that may be obscured from the 3d view but are visible on the slices, of for fine-tuning.

![dicom6](https://github.com/user-attachments/assets/c473f5d2-04fb-4f06-b45b-49a140b27605)


### Volume Rendering

Find the **Modules** in the second menu row and click on the downward arrow to open it for options: 
![vol rend1](https://github.com/user-attachments/assets/105a1ed6-b77d-40a0-aeed-1de9c7c2ad33)

We will now adjust the scan to check the hard tissue and prepare for the alignment step.  for Volume, choose your source volume _“NAME”_. Find **Preset** under the **Display** submenu and play about to find the one that suits your scan the best – I find the _CT Chest Contrast Enhanced_ best for soft tissue/hard tissue comparisons. Then, toggle the bar next to **Shift** to reveal bone.


https://github.com/user-attachments/assets/02755454-225b-4390-9592-f2539a33d90e


These changes are not permanent, but extremely useful in getting an overview of the CT quality, discovering artefacts and later on, allocating orienting landmarks (more on this in the [FHP Realignment](url) section)


>[!TIP]
> Top Tips for starting out with Slicer for craniofacial approximation for the first time and reminders as to how the guidelines are structured. 

### Naming conventions
When the guide suggests naming or renaming something, it is likely necessary given for the code/script to work. If you still want these to be name differently, you MUST change it in the scripts to be executed. Look for something like this in the scripts: 

> L.SetName(‘height of apertura piriformis rhi-aca’)
> #name of your measurements#

### Numbering of landmarks in .json and coding
The numbering convention in landmark lists in 3D Slicer is counter-intuitive in coding:
![gtk2](https://github.com/user-attachments/assets/1af43561-b3f7-4098-bbe9-0b9cd4604513)

The table these individual points appear in start with a 1 (first row), but in scripting, to retrieve “nasion” in the first row, its position is considered 0. To make this consistent and easier to follow, the landmarks for each method are pre-established and saved in their respective folders, with the numbers and their position already assigned. PLEASE RETAIN this or only add landmarks at the end of this list for the codes to work (some guide also creates new nodes to add to this list, but the ones mentioned in the guide are accounted for). The descriptions of landmarks are pre-populated with the description provided by the original study or mentioned if defined by a different one in the guide.

| Landmark | no. in "Markups" | no. in coding |
|-----:|-----------|-----------|
|     nasion| 1 |0 |
|     inion| 2 |1 |
|     bregma| 3 |2 |

### Saving your Work
If you want to get back to the exact setup you left, I would recommend saving your individual annotated scans as Medical Reality Bundles (.mrb) – this funtion packs every file type in the environment in one file and re-opens them exactly as they were when you saved them. These files can be a few GBs. Click on **Save**:
![saving1-300x63](https://github.com/user-attachments/assets/0e9d390c-0714-4629-b3ea-4817e92d81d5)
Then choose the third option (present icon): 

![saving-300x156](https://github.com/user-attachments/assets/9c68a26f-b112-4d26-82cb-9aecb21b8957)

Choose the folder you wish to save this either by double-clicking on the Directory bar’s **…** on top or choosing the _Change directory for selected files_ button on the  bottom. 

### Copy all measurements to Clipboard
There is a script provided for copying all linear/angular measurements in the scene onto the clipboard on the [FHP realignment page](.....). Once copied and pasted, the shortcut **Ctrl+M** for lines and **Ctrl+T** for angles will initiate this, and a message with the number of lines/angles should appear. The output of these will have (unknown) as the first row as most CT scans are anonymous – feel free to include an ID. They mention the name of the line/angle and a number in mm/degrees. You will find that some lines are not true measurements, are used as an intermediate line or are extended by code, so they are not to be used as such.

### Extensions & Modules
The realignment page (next step) mentions two extensions necessary to be installed to work. Extensions are “enablers” for different functions and can save a lot of time – I would suggest browsing through them if you have time. 

To access extensions, click on the ![extensions](https://github.com/user-attachments/assets/802a10a3-9927-4481-85cd-05aeaf36757c) icon in the second row of the menu on the far right. 
Find the search bar and find these extensions: _MarkupsToModel_, _SegmentEditorExtraEffects_, and _ExtraMarkups_and install all. 

![extension2-199x300](https://github.com/user-attachments/assets/d27e9d5e-ed7d-46ab-8de6-767c725a061e) ![extension1-171x300](https://github.com/user-attachments/assets/8bbaf2f1-d886-4ac8-af80-7c40db0f16b9) <img width="222" alt="image" src="https://github.com/user-attachments/assets/de3ea53e-5b3e-4616-b2af-f19b8f3c1947" />


> [!NOTE]
> Slicer will require a restart after installation of ANY new extension or extension update, so make sure you save your progress beforehand. These extensions are NECESSARY for some of the codes to work (MarkupsToModel and SegmentEditorExtraEffects for example for the initial FHP realignment).

### Notepad++

If you wish to modify the original codes, I advise opening the code.txt files the Notepad++ programme, where you can highlight sections, find lines referred to in the guide and use the “Search and replace” functions for consistent change along your new code.

To download the free programme, click [here](https://notepad-plus-plus.org/downloads/v8.7.7/).
