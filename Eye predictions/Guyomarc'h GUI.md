```python
# ==============================================================================
# Advanced Orbital Workflow - CONSOLE EDITION (v13 - Precision Cleanup)
# ==============================================================================
# This is a self-contained script that creates a full GUI when pasted directly
# into the 3D Slicer Python Interactor console.
#
# CORRECTIONS:
# - Implemented a robust node tracking system for perfect cleanup.
# - The "Clean Up" button now precisely removes all generated items (models,
#   sub-models, lines, planes) without touching user data.
#
# INSTRUCTIONS:
# 1. Open 3D Slicer.
# 2. Open the Python Interactor (View -> Python Interactor or Ctrl+3).
# 3. Copy this ENTIRE script block.
# 4. Paste it into the console and press Enter. The GUI will appear.
# ==============================================================================

import slicer
import qt
import logging
import numpy as np
import os
import urllib.request
import shutil
import vtk

# --- Define the Logic Class (all the "heavy lifting") ---
class AdvancedOrbitalWorkflowLogic:
    # --- 1. MODIFICATION: Logic now gets a reference to the GUI to access the tracking list ---
    def __init__(self, gui):
        self.gui = gui

    # --- 2. MODIFICATION: New helper function to track created nodes by their ID ---
    def trackNode(self, node):
        if node and node.GetID() not in self.gui.createdNodeIDs:
            self.gui.createdNodeIDs.append(node.GetID())

    # --- 3. MODIFICATION: The cleanup function is now precise and safe ---
    def undo_all(self):
        logging.info(f"Cleaning up {len(self.gui.createdNodeIDs)} generated nodes...")
        for nodeID in self.gui.createdNodeIDs:
            node = slicer.mrmlScene.GetNodeByID(nodeID)
            if node:
                slicer.mrmlScene.RemoveNode(node)
        # Clear the tracking list after deleting the nodes
        self.gui.createdNodeIDs.clear()

    def run_script_with_error_handling(self, script_function, *args):
        try: return script_function(*args)
        except Exception as e:
            slicer.util.errorDisplay(f"An error occurred: {e}", 30)
            logging.error(f"Error during script execution: {e}", exc_info=True)
            return None

    def _execute_script1(self):
        logging.info("--- Running Script 1: Create Blueprint ---")
        source_node = slicer.util.getNode('Guyomarch_hard_tissue')
        if not source_node: raise ValueError("Node 'Guyomarch_hard_tissue' not found. Please load it first.")
        
        lm_names=['orR','orL','poR','poL','n','dlomR','dlomL','dL','dR']
        lms={}; [lms.update({lbl:pos}) for lbl in lm_names if (idx:=source_node.GetControlPointIndexByLabel(lbl))!=-1 and (pos:=np.zeros(3),source_node.GetNthControlPointPositionWorld(idx,pos),True)[0] is not None]
        if len(lms)!=len(lm_names): raise ValueError(f"Missing one or more required landmarks from: {lm_names}")

        fhp_pts=np.array([lms['orR'],lms['orL'],lms['poR'],lms['poL']]); cent=fhp_pts.mean(axis=0)
        _,_,vh=np.linalg.svd(fhp_pts-cent); fhp_n=vh[2]
        fhp=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","FHP"); fhp.SetCenter(cent); fhp.SetNormal(fhp_n); fhp.GetDisplayNode().SetSelectedColor(0,1,1); self.trackNode(fhp)

        or_mid,po_mid=0.5*(lms['orR']+lms['orL']),0.5*(lms['poR']+lms['poL']); ap_d=or_mid-po_mid
        ap_d-=np.dot(ap_d,fhp_n)*fhp_n; ap_d/=np.linalg.norm(ap_d); sp_n=np.cross(fhp_n,ap_d)
        sag=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","Sagittal"); sag.SetCenter(lms['n']); sag.SetNormal(sp_n); sag.GetDisplayNode().SetSelectedColor(1,0,1); self.trackNode(sag)
        
        mid_dlom=(lms['dlomR']+lms['dlomL'])/2.0; fp_n=np.cross(fhp_n,sp_n)
        fp=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","Frontal"); fp.SetCenter(mid_dlom); fp.SetNormal(fp_n); fp.GetDisplayNode().SetSelectedColor(1,1,0); self.trackNode(fp)

        po_v=lms['poR']-lms['poL']; ln_d=po_v-np.dot(po_v,fhp_n)*fhp_n; ln_d/=np.linalg.norm(ln_d)
        ln_l=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","L orbit bisecting line"); ln_l.AddControlPoint(lms['dL']-ln_d*50); ln_l.AddControlPoint(lms['dL']+ln_d*50); ln_l.GetDisplayNode().SetSelectedColor(0,1,0); self.trackNode(ln_l)
        ln_r=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","R orbit bisecting line"); ln_r.AddControlPoint(lms['dR']-ln_d*50); ln_r.AddControlPoint(lms['dR']+ln_d*50); ln_r.GetDisplayNode().SetSelectedColor(1,0.5,0); self.trackNode(ln_r)
        slicer.app.processEvents()
        return True

    def _execute_script2(self):
        logging.info("--- Running Script 2: Create Measurements ---")
        def unit(v): return v/np.linalg.norm(v)
        def goc_line(name):
            node = slicer.util.getFirstNodeByName(name);
            if node: slicer.mrmlScene.RemoveNode(node)
            newNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
            self.trackNode(newNode) # Track the new line
            return newNode
        def ln_pts(ln): p0,p1=np.zeros(3),np.zeros(3); ln.GetNthControlPointPositionWorld(0,p0); ln.GetNthControlPointPositionWorld(1,p1); return p0,p1
        def cl_pts(P0,u,Q0,v): w0=P0-Q0;a,b,c=np.dot(u,u),np.dot(u,v),np.dot(v,v);d,e=np.dot(u,w0),np.dot(v,w0);den=a*c-b*b;s,t=(b*e-c*d)/den if abs(den)>1e-9 else(-d,0.0); return P0+s*u,Q0+t*v

        fhp,sag,src=slicer.util.getNode('FHP'),slicer.util.getNode('Sagittal'),slicer.util.getNode('Guyomarch_hard_tissue')
        if not all([fhp,sag,src]): raise ValueError("Missing Step 1 nodes.")
        
        si,lr,ap=unit(fhp.GetNormal()),unit(sag.GetNormal()),unit(np.cross(unit(fhp.GetNormal()),unit(sag.GetNormal())))
        def lm(lbl): idx=src.GetControlPointIndexByLabel(lbl);pos=np.zeros(3);assert idx!=-1,f"'{lbl}' not found.";src.GetNthControlPointPositionWorld(idx,pos);return pos
        
        lines=[('SOM_L','skL',lr,'L'),('IOM_L','orL',lr,'L'),('MOM_L','dL',si,'L'),('LOM_L','ekL',si,'L'),('DLOM_L','dlomL',ap,'L'),
               ('SOM_R','skR',lr,'R'),('IOM_R','orR',lr,'R'),('MOM_R','dR',si,'R'),('LOM_R','ekR',si,'R'),('DLOM_R','dlomR',ap,'R')]
        for n,l,d,s in lines:
            ln,c=goc_line(n),lm(l);ln.AddControlPoint(c-d*37.5);ln.AddControlPoint(c+d*37.5)
            clr=[1,.7,.2] if s=='L' else [.2,.7,1];ln.GetDisplayNode().SetSelectedColor(clr);ln.GetDisplayNode().SetColor(clr)
        slicer.app.processEvents()
        
        obb_l_node = goc_line("OBB_L"); obb_l_node.AddControlPoint(lm("ekL")); obb_l_node.AddControlPoint(lm("dL"))
        obb_r_node = goc_line("OBB_R"); obb_r_node.AddControlPoint(lm("ekR")); obb_r_node.AddControlPoint(lm("dR"))
        
        for s in "LR":
            som_node = slicer.util.getNode(f"SOM_{s}"); iom_node = slicer.util.getNode(f"IOM_{s}")
            if not som_node or not iom_node: raise ValueError(f"Could not find SOM_{s} or IOM_{s} to calculate OBH.")
            S0,S1=ln_pts(som_node); I0,I1=ln_pts(iom_node)
            p_s,p_i=cl_pts(S0,unit(S1-S0),I0,unit(I1-I0)); obh_node = goc_line(f"OBH_{s}"); obh_node.AddControlPoint(p_s); obh_node.AddControlPoint(p_i)
        slicer.app.processEvents()
        return True

    def _execute_script3(self, model_key, model_urls, statusLabel):
        logging.info("--- Running Script 3: Place Eyeball ---")
        statusLabel.text="Starting...";slicer.app.processEvents()
        def unit(v):v=np.array(v,float);n=np.linalg.norm(v);return v/n
        def get_pos(n,lbl):idx=n.GetControlPointIndexByLabel(lbl);pos=[0,0,0];assert idx!=-1,f"'{lbl}' not found!";n.GetNthControlPointPositionWorld(idx,pos);return np.array(pos)
        
        side_sfx='_L' if 'Left' in model_key else '_R';side_lbl=side_sfx.replace('_','')
        lmk_n,obh,obb=slicer.util.getNode("Guyomarch_hard_tissue"),slicer.util.getNode(f"OBH{side_sfx}"),slicer.util.getNode(f"OBB{side_sfx}")
        if not all([lmk_n,obh,obb]): raise ValueError("Missing measurement nodes from Step 3.")
        
        scene_path=os.path.join(slicer.app.temporaryPath,f"{model_key.replace(' ','_')}.mrb");statusLabel.text="Downloading...";slicer.app.processEvents()
        with urllib.request.urlopen(model_urls[model_key]) as resp,open(scene_path,'wb') as out_f:shutil.copyfileobj(resp,out_f)
        statusLabel.text="Loading...";slicer.app.processEvents();before=set(slicer.util.getNodes().values())
        if not slicer.util.loadScene(scene_path,{"clear":False}):raise RuntimeError("loadScene failed.")
        
        # Track all newly loaded nodes
        newly_loaded_nodes = list(set(slicer.util.getNodes().values()) - before)
        for node in newly_loaded_nodes:
            self.trackNode(node)

        oa_p,xf=None,None
        for n in newly_loaded_nodes:
            if n.IsA("vtkMRMLLinearTransformNode") and "EyeTransform" in n.GetName():xf=n
            elif n.IsA("vtkMRMLMarkupsFiducialNode"):
                idx=n.GetControlPointIndexByLabel(f"oa{side_lbl}");
                if idx!=-1:pos=[0,0,0];n.GetNthControlPointPositionWorld(idx,pos);oa_p=np.array(pos)
        if not xf or oa_p is None:raise ValueError("Missing 'EyeTransform' or 'oa' from loaded model.")
        
        poR,poL,n_lmk=get_pos(lmk_n,'poR'),get_pos(lmk_n,'poL'),get_pos(lmk_n,'n')
        v_r,v_a_r=unit(poR-poL),n_lmk-(poR+poL)/2;v_a=unit(v_a_r-np.dot(v_a_r,v_r)*v_r);v_s=unit(np.cross(v_r,v_a))
        p_si,p_ml,p_ap=get_pos(lmk_n,f'sk{side_lbl}')-v_s*(0.441*obh.GetLineLengthWorld()),get_pos(lmk_n,f'd{side_lbl}')+(-v_r if side_sfx=='_L' else v_r)*(0.576*obb.GetLineLengthWorld()),get_pos(lmk_n,f'dlom{side_lbl}')+v_a*(0.513*obh.GetLineLengthWorld())
        A,b=np.array([v_s,v_r,v_a]),np.array([np.dot(v_s,p_si),np.dot(v_r,p_ml),np.dot(v_a,p_ap)]);target=np.linalg.solve(A,b)
        
        t_v=target-oa_p;x_mat=vtk.vtkMatrix4x4();xf.GetMatrixTransformToParent(x_mat)
        t_mat=vtk.vtkMatrix4x4();[t_mat.SetElement(i,3,t_v[i]) for i in range(3)]
        vtk.vtkMatrix4x4.Multiply4x4(t_mat,x_mat,x_mat);xf.SetMatrixTransformToParent(x_mat)
        statusLabel.text=f"SUCCESS! '{model_key}' placed."
        return True

    def _execute_script4(self):
        logging.info("--- Running Script 4: Validation (Simplified Naming) ---")
        def get_node(pat,req=True):n=slicer.util.getNode(pat);assert not(req and not n), f"Node '{pat}' not found.";return n
        def get_pos(n,lbl):
            if not n:return None
            idx=n.GetControlPointIndexByLabel(lbl);pos=np.zeros(3);
            if idx==-1:return None
            n.GetNthControlPointPositionWorld(idx,pos);return pos
        def dist_pt_ln(pt, ln):
            p1,p2=np.zeros(3),np.zeros(3);ln.GetNthControlPointPositionWorld(0,p1);ln.GetNthControlPointPositionWorld(1,p2)
            line_vec=p2-p1; point_vec=pt-p1; line_len_sq=np.dot(line_vec,line_vec)
            if line_len_sq<1e-9: return np.linalg.norm(point_vec)
            t=np.dot(point_vec,line_vec)/line_len_sq; closest_point=p1+t*line_vec
            return np.linalg.norm(pt-closest_point)

        true_n,pred_l,pred_r=get_node("Guyomarch_soft_tissue"),get_node("*Left Eyeball lmrks",False),get_node("*Right Eyeball lmrks",False)
        results = []
        method_name = "Guyomarc'h et al. 2012"

        for side,pred in[('L',pred_l),('R',pred_r)]:
            for lmk in['oa','op','os','oi','om','ol','p']:
                b,t_lbl=f"{lmk}{side}",f"true_{lmk}{side}";t_p,p_p=get_pos(true_n,t_lbl),get_pos(pred,b)
                dist="N/A" if t_p is None or p_p is None else f"{np.linalg.norm(t_p-p_p):.2f}"
                results.append((f"{b}_error", dist, method_name))
        
        for side,pred in[('L',pred_l),('R',pred_r)]:
            t_oa,p_oa=get_pos(true_n,f"true_oa{side}"),get_pos(pred,f"oa{side}")
            for pfx in['DLOM','SOM','IOM','LOM','MOM']:
                ln=slicer.util.getNode(f"{pfx}_{side}")
                if ln and p_oa is not None:
                    dist = f"{dist_pt_ln(p_oa,ln):.2f}"
                    results.append((f"pred_{pfx}-{side}-oa{side}", dist, method_name))
                if ln and t_oa is not None:
                    dist = f"{dist_pt_ln(t_oa,ln):.2f}"
                    results.append((f"true_{pfx}-{side}-oa{side}", dist, method_name))
        
        return results

# --- Define the GUI Widget Class ---
class AdvancedOrbitalWorkflowGUI(qt.QWidget):
    def __init__(self, parent=None):
        super(AdvancedOrbitalWorkflowGUI, self).__init__(parent)
        # --- 4. MODIFICATION: Logic now gets a reference to 'self' (the GUI instance) ---
        self.logic = AdvancedOrbitalWorkflowLogic(self)
        self.createdNodeIDs = []
        self.setup()

    def setup(self):
        self.setWindowTitle("Advanced Orbital Workflow")
        self.mainLayout = qt.QVBoxLayout(self)
        self.hard_tissue_url = "https://github.com/user-attachments/files/27900137/Guyomarch_hard_tissue.mrk.json"
        self.soft_tissue_url = "https://github.com/user-attachments/files/27900157/Guyomarch_soft_tissue.mrk.json"
        
        self.model_urls = {
            "Female Left": "https://drive.google.com/uc?export=download&id=1IO2-DIroRDhs84rBsQc1srfuzDFyRy2g",
            "Female Right": "https://drive.google.com/uc?export=download&id=1-QCnBmAdogNQLweVzcdVd_SVd3oImz85",
            "Male Left": "https://drive.google.com/uc?export=download&id=120wrETZx5o0-0CwAzldF07ZnFKNgn-Km",
            "Male Right": "https://drive.google.com/uc?export=download&id=1D2ZakWhd6jefyFT-EN3ECdNqVolpi9Ak"
        }

        setupBox=self._create_collapsible_box("Setup: Load Initial Data")
        self.loadHardTissueButton=qt.QPushButton("Download and Load Hard Tissue Landmarks"); self._add_to_box_layout(setupBox, [self.loadHardTissueButton])
        
        step1Box=self._create_collapsible_box("Step 1: Create Blueprint Planes")
        self.runStep1Button=qt.QPushButton("Create Blueprint");self._add_to_box_layout(step1Box,[qt.QLabel("Creates FHP, Sagittal, and Frontal planes, plus helper lines."),self.runStep1Button])
        
        step2Box=self._create_collapsible_box("Step 2: Place Ectoconchion Landmarks")
        self._add_to_box_layout(step2Box,[qt.QLabel("<b>USER ACTION REQUIRED:</b>\nManually place 'ekL' and 'ekR' in the 'Guyomarch_hard_tissue' list.")])
        
        step3Box=self._create_collapsible_box("Step 3: Create Orbital Measurements")
        self.runStep3Button=qt.QPushButton("Create Measurements");self._add_to_box_layout(step3Box,[qt.QLabel("Creates all orbital margin lines and calculates OBH/OBB rulers."),self.runStep3Button])
        
        step4Box=self._create_collapsible_box("Step 4: Place Predicted Eyeball")
        self.modelSelector=qt.QComboBox();self.modelSelector.addItems(list(self.model_urls.keys()));self.runStep4Button=qt.QPushButton("Download and Place Eyeball");self.placementStatusLabel=qt.QLabel("Ready.")
        formLayout=qt.QFormLayout();formLayout.addRow("Select Eyeball Model:",self.modelSelector);formLayout.addRow(self.runStep4Button);formLayout.addRow("Status:",self.placementStatusLabel);self._add_to_box_layout(step4Box, [formLayout])
        
        step5Box=self._create_collapsible_box("Step 5 (Optional): Load Ground Truth Data")
        self.loadSoftTissueButton=qt.QPushButton("Download and Load Soft Tissue Landmarks"); self._add_to_box_layout(step5Box, [self.loadSoftTissueButton])

        step6Box=self._create_collapsible_box("Step 6 (Optional): Run Validation")
        self.runStep6Button=qt.QPushButton("Run Validation")
        self.validationResultsTable = qt.QTableWidget()
        self.validationResultsTable.setColumnCount(3)
        self.validationResultsTable.setHorizontalHeaderLabels(["Measurement", "Value (mm)", "Method"])
        self.validationResultsTable.setMinimumHeight(200)
        self.validationResultsTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.validationResultsTable.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.copyTableButton = qt.QPushButton("Copy Table to Clipboard")
        self._add_to_box_layout(step6Box, [qt.QLabel("Compares predicted vs. ground truth landmarks."), self.runStep6Button, self.validationResultsTable, self.copyTableButton])

        manageBox=self._create_collapsible_box("Management")
        self.cleanupButton=qt.QPushButton("Clean Up All Generated Nodes");self._add_to_box_layout(manageBox,[self.cleanupButton])
        self.mainLayout.addStretch(1)

        self.loadHardTissueButton.connect('clicked(bool)', lambda: self.onLoadMarkups(self.hard_tissue_url, "Guyomarch_hard_tissue"))
        self.loadSoftTissueButton.connect('clicked(bool)', lambda: self.onLoadMarkups(self.soft_tissue_url, "Guyomarch_soft_tissue"))
        self.runStep1Button.connect('clicked(bool)',lambda: self.logic.run_script_with_error_handling(self.logic._execute_script1) and slicer.util.infoDisplay("Step 1 Complete."))
        self.runStep3Button.connect('clicked(bool)',lambda: self.logic.run_script_with_error_handling(self.logic._execute_script2) and slicer.util.infoDisplay("Step 3 Complete."))
        self.runStep4Button.connect('clicked(bool)',lambda: self.logic.run_script_with_error_handling(self.logic._execute_script3,self.modelSelector.currentText,self.model_urls,self.placementStatusLabel))
        self.runStep6Button.connect('clicked(bool)',self.onRunValidation)
        self.cleanupButton.connect('clicked(bool)',self.onCleanup)
        self.copyTableButton.connect('clicked(bool)', self.onCopyToClipboard)

    def _create_collapsible_box(self, title):
        # This requires ctk to be available in Slicer's environment.
        try:
            import ctk
            box=ctk.ctkCollapsibleButton();box.text=title;self.mainLayout.addWidget(box);return box
        except ImportError:
            box = qt.QGroupBox(title); box.setCheckable(True); self.mainLayout.addWidget(box); return box
    
    def _add_to_box_layout(self, box, widgets):
        if isinstance(widgets[0], qt.QFormLayout):
            layout = widgets[0]
        else:
            layout = qt.QFormLayout()
            for widget in widgets: layout.addRow(widget)
        box.setLayout(layout)

    def onLoadMarkups(self, url, node_name):
        existing_node = slicer.util.getFirstNodeByName(node_name)
        if existing_node:
            slicer.util.infoDisplay(f"Node '{node_name}' already exists. Using existing node.")
            return
        try:
            temp_path = os.path.join(slicer.app.temporaryPath, os.path.basename(url.split('?')[0]))
            slicer.util.showStatusMessage(f"Downloading '{node_name}'...")
            with urllib.request.urlopen(url) as response, open(temp_path, 'wb') as out_file: shutil.copyfileobj(response, out_file)
            node = slicer.util.loadMarkups(temp_path)
            node.SetName(node_name)
            slicer.util.infoDisplay(f"Successfully downloaded and loaded '{node_name}'.")
        except Exception as e: 
            slicer.util.errorDisplay(f"Failed to load landmarks from URL: {e}")
            slicer.util.showStatusMessage("")

    def onRunValidation(self):
        results = self.logic.run_script_with_error_handling(self.logic._execute_script4)
        if results is None: return
        
        self.validationResultsTable.setRowCount(0)
        self.validationResultsTable.setRowCount(len(results))
        
        for row_index, row_data in enumerate(results):
            measurement, value, method = row_data
            self.validationResultsTable.setItem(row_index, 0, qt.QTableWidgetItem(measurement))
            self.validationResultsTable.setItem(row_index, 1, qt.QTableWidgetItem(str(value)))
            self.validationResultsTable.setItem(row_index, 2, qt.QTableWidgetItem(method))
        
        self.validationResultsTable.resizeColumnsToContents()

    def onCleanup(self):
        self.logic.undo_all()
        self.validationResultsTable.setRowCount(0)
        self.placementStatusLabel.text="Ready."
        slicer.util.infoDisplay("Cleanup complete.")

    def onCopyToClipboard(self):
        clipboard = qt.QApplication.clipboard()
        text = ""
        headers = [self.validationResultsTable.horizontalHeaderItem(c).text() for c in range(self.validationResultsTable.columnCount)]
        text += "\t".join(headers) + "\n"
        for r in range(self.validationResultsTable.rowCount):
            row_items = [self.validationResultsTable.item(r, c).text() if self.validationResultsTable.item(r, c) else "" for c in range(self.validationResultsTable.columnCount)]
            text += "\t".join(row_items) + "\n"
        clipboard.setText(text)
        slicer.util.infoDisplay("Results table copied to clipboard.")

# --- Main execution block for the console ---
try:
    if 'advancedWorkflowGUI' in globals() and advancedWorkflowGUI.parent():
        globals()['advancedWorkflowGUI'].parent().close()
    del globals()['advancedWorkflowGUI']
except (NameError, KeyError): pass

advancedWorkflowGUI = AdvancedOrbitalWorkflowGUI()
dockWidget = qt.QDockWidget("Advanced Orbital Workflow")
dockWidget.setWidget(advancedWorkflowGUI)
slicer.util.mainWindow().addDockWidget(qt.Qt.RightDockWidgetArea, dockWidget)
dockWidget.show()

```
