# Content Summary
- [ROI – Region of Interest](#roi--region-of-interest)
- [Segmentation](#segmentation)
- [Dynamic Modeller Module](#dynamic-modeller-module)
- [ROI vs Segments - Which one is the best to use?](#roi-vs-segments---which-one-is-the-best-to-use)


This section is for after the re-alignment of the scans in FHP and considers different approaches to use of them in craniofacial identification methods Typically, the comparison of soft and hard tissues are the focus and easily switching between these two is of the essence. However, the practitioner may find that creating reproducible renderings of these can be challenging, especially when more manipulation is needed for placing landmarks with an obscure space (e.g. within the temporo-mandibular joint, inside the cranial vault, etc). 

### ROI – Region of Interest
You have now used the _Shift_ function in the Volume Rendering module to place the FHP markers to re-orientate the original DICOM file. Just beneath this function, you can click _Enable_ in the _Crop_ submenu, then choose _Display ROI_ to see a 3D square appear around the scan. Once you toggle each side of the ROI Cube, you can see structures inside the scan that may have been obscured in the 3D view or you could only see them in the other (red/green/yellow) windows. This function is particularly useful if you need to place multiple landmarks inside the cranium or very close to the cervical spine as this allows for a quick view adjustment temporarily. After manipulating the ROI cube, you can always go back to the full scan view.

https://github.com/user-attachments/assets/f46cc9e5-830b-4e2a-8837-f9004752705d

### Segmentation

To standardise the views and make methods reproducible, it is good practice to use the same 2 models for hard and soft tissue landmark allocation. The _Segmentations_ module helps create these based on the HU (Hounsfield Unit) of the CT scan that expresses the radiodensity of a certain substance (skull and facial soft tissue in this case). This is a good reference table for thresholds: [Radlines](https://radlines.org/Hounsfield_unit)
First, find and open the _Segment Editor_ Module:
![segmentation-module1](https://github.com/user-attachments/assets/9de05983-9fed-45da-9863-0939c4af3849)
This window should be showing on the left hand side of your screen:
![segmentation-module2](https://github.com/user-attachments/assets/bc2cce77-0c6a-4536-8bfe-467683976cd9)
This will give you an empty segmentation first. We will re-name out first segmentation _Bone_ by clicking on the drop-down menu _Segmentation:”> “Segmentation_1._
![segmentation-module3](https://github.com/user-attachments/assets/e229a8c3-df90-4206-9721-04e22bb0e83f)
After choosing _Rename Segmentation_, a small window should pop up where you can type in the name of the segment you are creating.

![segmentation-module4](https://github.com/user-attachments/assets/d2f43bb7-cb43-45de-9ea8-78b316774ffb)
In this example, we are making a segmentation for hard tissue bone. Click “OK”.  You need to choose your original DICOM file as the **Source Volume.**
![segmentation-module5-1](https://github.com/user-attachments/assets/a5cbf10d-d5aa-48b7-b8c8-c65c1225ec2e)
Once you chose this, the slices from your DICOM files should appear in the red/green/yellow windows. Click **Add**, then the whole left panel should become active and a new green Segment called **Segment_1** should appear in the list. Choose the tool in the first row on the right called **Threshold** to set up your cranial model.

![segmentation-module6](https://github.com/user-attachments/assets/fa5b3e00-8cd5-48e4-bede-19605249e774)

In this section, you can manually set thresholds for the cranium, but a built-in method works great for bone. Click on **Automatic threshold** and choose **Maximum entropy** – now the parts that will show up in the segmentation should be “blinking” in the slice windows. Then click **Set** and **Apply** in the **Local Histogram** menu and click **Show 3D**at the top. You can also modify the colour of the output segment by clicking on the palette icon. ![palette  widget](https://github.com/user-attachments/assets/5451df67-7c7c-40f8-a415-0552d2e3eccf)


> [!WARNING]
> The suggested (automatic and non-automated) thresholds are my personal preferences, but your choice will have to depend on multiple CT settings that suit your scan visibility the best!

Then, we can create a second segmentation for our surface soft tissues by choosing **Create new Segmentation as…** and naming it **Skin**. Click **Add**, **Threshold” and set the automatic threshold this time to **Otsu**, then click **Set**, **Apply** and **Show 3D**.

![segmentation-module7](https://github.com/user-attachments/assets/102e726f-e694-4adf-9608-8406df2fb30b)

If all features that you will need in your research are shown in these two segmentations, the next step is to import them. Go to the **Segmentation** module by hitting the green arrow at the top or choosing it from the modules menu.

Scroll down to the **Export/import models and labelmaps**, click on it and choose options **Export** and **Models**. Scroll further to the **Export files** menu and choose your destination folder. Make sure you have the original DICOM as your reference volume and click **Export**. The selected Segment should now have been saved in your folder. To export the other segment (skin or bone), scroll up all the way to see **Active segmentation** and choose the segment you did not import yet. The settings will be saved from the previous action, but make sure you click **Export** UNDER THE **Export to files** MENU, NOT the one above.

![segmentation-module10](https://github.com/user-attachments/assets/b0622c0d-1b05-435c-b964-b9f94bab4483)

Now, click on the most left folder icon that says DATA  ![data](https://github.com/user-attachments/assets/f11c5b84-7d1a-48de-9d2f-cc2b5dc1a09c) to add your new models back in the scene. Click **choose files to add** and select your Skin and Bone models from your own location, then hit **Open**.

![segmentation-module9](https://github.com/user-attachments/assets/ca64ca30-b6e8-49ac-8b4c-2304844795f8)
They should appear in the window like this, then click “OK”

 It is normal for Slicer to take some time executing these steps, so be patient.

Once it loads, you will notice that it is a different colour than the one you set and the names are duplicated. If you wish, you can re-set these by going to the **Models** module. 

![models1](https://github.com/user-attachments/assets/7f2b6ed3-1a27-4af4-9da5-9640e76dce36)
Choose the model you’d like to modify and double click on the name to alter it. (Can be useful for scripting!). The colours can also be re-set by the colour filled square under the palette widget   ![palette-widget](https://github.com/user-attachments/assets/ce740608-621b-4bbb-a4c5-734eeaa48d5c). 
If you now go to the “Data” module by clicking the icon or choosing the module, you will see that there are a lot of extra views open, with your models on the very bottom of the list.
![models3-1](https://github.com/user-attachments/assets/03190df3-9d65-4189-be23-78bd91c8cae0)

You can hide all of these and keep only the models if you wish.

In case still need the red/green/yellow slice windows for precise landmark placement, keep only the original volume node (7:THIN BONE HEAD in the example) and the models visible. This way, after you places your landmark, you can still see its location in detail if you double click it in these windows:
![models4](https://github.com/user-attachments/assets/8ed2e231-ccd5-4812-889e-442f55bc29aa)


### Dynamic Modeller Module

Alternatively, the Dynamic Modeller Module is useful when most landmarks are on the surface of your model and you need maybe one “cut” view throughout the data collection. This module can be used to PERMANENTLY crop one of your models – along a plane, within or outside an ROI and many more! 

To open, click on the magnifying glass icon next to the modules: 

![module](https://github.com/user-attachments/assets/08aeb820-240a-4cfd-a9c7-01d017c09c36)

And start typing “dynamic modeller” in the search bar.
![module2](https://github.com/user-attachments/assets/c9dfd153-3c8b-4e99-82a2-8ed83320aec7)
Click “Switch to Module” to open. 

You’ll see this menu on the left side of the screen: 
![dynamic-modeller](https://github.com/user-attachments/assets/035ea262-8235-4665-8c4d-c3df49945944)
For the purpose of demonstration, a random plane called “P” is established in the environment – if there are planes in the instructions in tutorials, they will have criteria on how to create them. To cut the model along this plane (technically cutting it in 2 and choosing which side to keep), choose the first button (Plane Cut).

![dynamic-modeller-plane](https://github.com/user-attachments/assets/07e65389-426c-4167-83ab-26187e8a6f55)

With these settings, the before and after the cut will be the following: 

![after-cut](https://github.com/user-attachments/assets/18cffcf9-5073-4489-92c2-46b4ec893843)

For the input nodes, choose the name of the skull model (“Bone” in our case), Plane node [1] will be the P plane, and Plane node [2] needs to remain None. In Parameters, the operation type should be “Intersection”, in the Output Nodes menu, click on the drop-down menu of either positive or negative side (in this case, the negative side means the bottom remains in the view, top is cut off, the positive side means that the topside will show and bottom will be cut off), choose “Create new model as…”, name it “positive”, then click “Apply”. Now open the Models module and find your new model to view. 

 ### ROI vs Segments - Which one is the best to use? 
The general rule of thumb for using either ROI or Segmentation to access challenging views of the Scan is the following: 

- How many of the landmarks need to be placed in the obscure view and would you have to be consistent? 
- Are there multiple views that would have to be established to place all the landmarks correctly?
- Do you already have a reference plane/ROI box that helps with the "cutting"?
- Is replicability a concern due to different CT scan settings, etc? 
![roi-vs-segment drawio](https://github.com/user-attachments/assets/1a453097-70b7-4fb2-bde6-e5df495ad7e1)

Nonetheless, always include a brief explanation as to why you are using the certain methods you chose, give a detailed overview and be consistent with it. 

### Combining the ROIs as Markups with Segmentations

You may have to use some not-plane specific cropping to make the loading and manipulation of segments quicker - such as cropping out medical devices, hair, etc from both soft tissue and hard tissue models, simply decreasing the area of interest or if you need endocranial strucutres visible from one or multiple sides for landmarking. We can pre-crop (create ROIs) before the general segmentation (for soft and hard tissues) takes place - taking advantage of the easy to manipulate funtion in **Volume Rendering** but also increasing the repeatablity of methods by adhering to threshold values.
A great example is the [Macho method](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Nose%20predictions/Macho%201968.md), where you need to remove the skullcap and partially the squamous part of the temporal bones so that you see inside the craium from multiple views to allocate the landmarks for the 3D determination of the sellion. We will try to demonstrate step-by-step what we mean by this workflow. 
#### Step 1 - FHP
Re-orient the scan in the FHP as described in the [Realign CT](https://github.com/esomjai/Forensic-Craniofacial-Approximation-Database/blob/basics/Start%20here%20/002_Realign%20CT%20in%20the%20standard%20FHP.md) guide. It is pertinent to do this first, otherwise the models derived  from the original scan will not align with the re-oriented scan. 
#### Step 2 - ROIs
In my example case, I already have my _Volume rendering ROI_ from **Volume Rendering** enabled and visible, but wish to add 3 more - one for the skin, one for bone and one for peaking inside the cranium. 
Go to _Markups_> Choose _ROI_ and click it as many times as you need. 
![image](https://github.com/user-attachments/assets/108f6083-0f51-4ec7-9b64-e00a108a0978)
 You can easily rename them by double clicking on their names and typing in a new one. 
<iframe src="https://dundee.cloud.panopto.eu/Panopto/Pages/Embed.aspx?id=2a948b1f-1b0d-404d-b1e8-b2b101105cfd&autoplay=false&offerviewer=false&showtitle=false&showbrand=false&captions=false&start=0&interactivity=all" height="405" width="720" style="border: 1px solid #464646;" allowfullscreen allow="autoplay" aria-label="Panopto Embedded Video Player" aria-description="Mon Mar 31 2025 17:30:38" ></iframe>




[Segmentation](#segmentation)



Check if you have all the full and all the cropped models adequately - colour code, hide visibilities, hide original scan. When happy, go to Save Data > uncheck the "Medical reality bundle option - a list of ALL the created objects. Uncheck all, except for the new cropped models (will appear as .vtk at the end of the list), set them as .stl and save them to the same folder as you previously did with the full models. Now, you can delete every segmentation and the full models from your scene – but keep the rest (transformations, etc.).

![Segmentation workflow](https://github.com/user-attachments/assets/ca206ec1-a70f-406a-b41f-bca437b1e2d4)
