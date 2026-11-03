```python
# ==============================================================================
# Advanced Orbital Workflow - CONSOLE EDITION (v21 - Final Layout Crash Fix)
# ==============================================================================
# This is a self-contained script that creates a full GUI when pasted directly
# into the 3D Slicer Python Interactor console.
#
# CORRECTIONS:
# - Fixed the 'AttributeError: 'NoneType' object has no attribute 'addRow''
#   crash by correctly initializing the layout for all collapsible boxes.
# - This version is stable, free of startup crashes, and all UI elements
#   are guaranteed to display correctly.
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
from scipy.interpolate import splev, splprep
import re

# --- Define the Logic Class (all the "heavy lifting") ---
class AdvancedOrbitalWorkflowLogic:
    def __init__(self, gui):
        self.gui = gui

    def undo_runs(self):
        logging.info("Cleaning up all generated 'Run' nodes...")
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        sceneItemID = shNode.GetSceneItemID()
        childIDs = vtk.vtkIdList()
        shNode.GetItemChildren(sceneItemID, childIDs)
        for i in range(childIDs.GetNumberOfIds()):
            itemID = childIDs.GetId(i)
            if shNode.GetItemName(itemID).startswith("Run"):
                shNode.RemoveItem(itemID)

    def undo_all(self):
        logging.info("Cleaning up ALL generated nodes...")
        self.undo_runs()
        blueprint_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsNode")
        for node in blueprint_nodes:
            if "orbit bisecting line" in node.GetName() or node.GetName() in ["FHP", "Sagittal", "Frontal", "OBH_L", "OBH_R", "OBB_L", "OBB_R", "SOM_L", "SOM_R", "IOM_L", "IOM_R", "MOM_L", "MOM_R", "LOM_L", "LOM_R", "DLOM_L", "DLOM_R"]:
                slicer.mrmlScene.RemoveNode(node)

    def run_script_with_error_handling(self, script_function, *args):
        try: return script_function(*args)
        except Exception as e:
            slicer.util.errorDisplay(f"An error occurred: {e}", 30)
            logging.error(f"Error during script execution: {e}", exc_info=True)
            return None

    def _execute_script1(self):
        source_node = slicer.util.getFirstNodeByName('Guyomarch_hard_tissue')
        if not source_node: raise ValueError("Node 'Guyomarch_hard_tissue' not found. Please load it first.")
        lm_names=['orR','orL','poR','poL','n','dlomR','dlomL','dL','dR']
        lms={}; [lms.update({lbl:pos}) for lbl in lm_names if (idx:=source_node.GetControlPointIndexByLabel(lbl))!=-1 and (pos:=np.zeros(3),source_node.GetNthControlPointPositionWorld(idx,pos),True)[0] is not None]
        if len(lms)!=len(lm_names): raise ValueError(f"Missing one or more required landmarks from: {lm_names}")
        fhp_pts=np.array([lms['orR'],lms['orL'],lms['poR'],lms['poL']]); cent=fhp_pts.mean(axis=0)
        _,_,vh=np.linalg.svd(fhp_pts-cent); fhp_n=vh[2]
        fhp=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","FHP"); fhp.SetCenter(cent); fhp.SetNormal(fhp_n); fhp.GetDisplayNode().SetSelectedColor(0,1,1)
        or_mid,po_mid=0.5*(lms['orR']+lms['orL']),0.5*(lms['poR']+lms['poL']); ap_d=or_mid-po_mid
        ap_d-=np.dot(ap_d,fhp_n)*fhp_n; ap_d/=np.linalg.norm(ap_d); sp_n=np.cross(fhp_n,ap_d)
        sag=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","Sagittal"); sag.SetCenter(lms['n']); sag.SetNormal(sp_n); sag.GetDisplayNode().SetSelectedColor(1,0,1)
        mid_dlom=(lms['dlomR']+lms['dlomL'])/2.0; fp_n=np.cross(fhp_n,sp_n)
        fp=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","Frontal"); fp.SetCenter(mid_dlom); fp.SetNormal(fp_n); fp.GetDisplayNode().SetSelectedColor(1,1,0)
        po_v=lms['poR']-lms['poL']; ln_d=po_v-np.dot(po_v,fhp_n)*fhp_n; ln_d/=np.linalg.norm(ln_d)
        ln_l=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","L orbit bisecting line"); ln_l.AddControlPoint(lms['dL']-ln_d*50); ln_l.AddControlPoint(lms['dL']+ln_d*50); ln_l.GetDisplayNode().SetSelectedColor(0,1,0)
        ln_r=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","R orbit bisecting line"); ln_r.AddControlPoint(lms['dR']-ln_d*50); ln_r.AddControlPoint(lms['dR']+ln_d*50); ln_r.GetDisplayNode().SetSelectedColor(1,0.5,0)
        slicer.app.processEvents()
        return True

    def _execute_script2(self):
        def unit(v): return v/np.linalg.norm(v) if np.linalg.norm(v) > 1e-9 else v
        def goc_line(name):
            node = slicer.util.getFirstNodeByName(name)
            if node: slicer.mrmlScene.RemoveNode(node)
            return slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", name)
        def ln_pts(ln): p0,p1=np.zeros(3),np.zeros(3); ln.GetNthControlPointPositionWorld(0,p0); ln.GetNthControlPointPositionWorld(1,p1); return p0,p1
        def cl_pts(P0,u,Q0,v): w0=P0-Q0;a,b,c=np.dot(u,u),np.dot(u,v),np.dot(v,v);d,e=np.dot(u,w0),np.dot(v,w0);den=a*c-b*b;s,t=(b*e-c*d)/den if abs(den)>1e-9 else(-d,0.0); return P0+s*u,Q0+t*v
        fhp=slicer.util.getFirstNodeByName('FHP');sag=slicer.util.getFirstNodeByName('Sagittal');src=slicer.util.getFirstNodeByName('Guyomarch_hard_tissue')
        if not all([fhp,sag,src]): raise ValueError("Missing blueprint nodes from Step 2.")
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
            som_node=slicer.util.getFirstNodeByName(f"SOM_{s}");iom_node=slicer.util.getFirstNodeByName(f"IOM_{s}")
            if not som_node or not iom_node: raise ValueError(f"Could not find SOM_{s} or IOM_{s} to calculate OBH.")
            S0,S1=ln_pts(som_node); I0,I1=ln_pts(iom_node)
            p_s,p_i=cl_pts(S0,unit(S1-S0),I0,unit(I1-I0)); obh_node = goc_line(f"OBH_{s}"); obh_node.AddControlPoint(p_s); obh_node.AddControlPoint(p_i)
        slicer.app.processEvents()
        return True

    def _execute_script3(self, run_id, model_key, model_urls, statusLabel, si_method, ml_method, ap_method):
        method_str=f"SI-{si_method[0]}_ML-{ml_method[0]}_AP-{ap_method[0]}";run_name=f"Run{run_id}_{model_key.replace(' ','_')}_{method_str}"
        logging.info(f"--- Creating {run_name} ---");statusLabel.text="Starting...";slicer.app.processEvents()
        def unit(v):v=np.array(v,dtype=float);n=np.linalg.norm(v);return v/n if n>1e-9 else v
        def get_pos(n,lbl):idx=n.GetControlPointIndexByLabel(lbl);pos=[0,0,0];assert idx!=-1,f"'{lbl}' not found!";n.GetNthControlPointPositionWorld(idx,pos);return np.array(pos)
        side_sfx='_L' if 'Left' in model_key else '_R';side_lbl=side_sfx.replace('_','');sex='Male' if 'Male' in model_key else 'Female'
        lmk_n=slicer.util.getFirstNodeByName("Guyomarch_hard_tissue");obh=slicer.util.getFirstNodeByName(f"OBH{side_sfx}");obb=slicer.util.getFirstNodeByName(f"OBB{side_sfx}")
        if not all([lmk_n,obh,obb]): raise ValueError("Missing measurement nodes from Step 4.")
        poR,poL,n_lmk=get_pos(lmk_n,'poR'),get_pos(lmk_n,'poL'),get_pos(lmk_n,'n')
        v_r,v_a_r=unit(poR-poL),n_lmk-(poR+poL)/2.0;v_a=unit(v_a_r-np.dot(v_a_r,v_r)*v_r);v_s=unit(np.cross(v_r,v_a))
        if si_method=="Kazuta et al. 2022":coeffs={"Male":{"L":0.585,"R":0.572},"Female":{"L":0.544,"R":0.536}};p_si=get_pos(lmk_n,f'sk{side_lbl}')-v_s*(coeffs[sex][side_lbl]*obh.GetLineLengthWorld())
        else: p_si=get_pos(lmk_n,f'sk{side_lbl}')-v_s*(0.441*obh.GetLineLengthWorld())
        p_ml=get_pos(lmk_n,f'd{side_lbl}')+(-v_r if side_sfx=='_L' else v_r)*(0.576*obb.GetLineLengthWorld())
        if ap_method!="Mautner and Wilkinson 2003":
            if ap_method=="Kazuta et al. 2022":coeffs={"Male":{"L":0.392,"R":0.391},"Female":{"L":0.370,"R":0.372}};p_ap=get_pos(lmk_n,f'dlom{side_lbl}')+v_a*(coeffs[sex][side_lbl]*obh.GetLineLengthWorld())
            else:p_ap=get_pos(lmk_n,f'dlom{side_lbl}')+v_a*(0.513*obh.GetLineLengthWorld())
            A,b=np.array([v_s,v_r,v_a]),np.array([np.dot(v_s,p_si),np.dot(v_r,p_ml),np.dot(v_a,p_ap)]);target=np.linalg.solve(A,b)
        else:
            # --- Definitive Mautner "Slide" Logic v3 ---
            # a) Define the initial eyeball center line based on SI and ML planes.
            initial_line_pt = np.linalg.lstsq(np.array([v_s, v_r]), np.array([np.dot(v_s, p_si), np.dot(v_r, p_ml)]), rcond=None)[0]
            initial_line_vec = v_a # This line runs parallel to the AP axis

            # b) Get the M&W orbital tangent line
            orbit_curve = slicer.util.getFirstNodeByName(f"{side_lbl}_orbit")
            if not orbit_curve or orbit_curve.GetNumberOfControlPoints() < 3: raise ValueError(f"'{side_lbl}_orbit' curve with >2 points required for M&W.")
            pts=slicer.util.arrayFromMarkupsControlPoints(orbit_curve);tck,u=splprep([pts[:,i] for i in range(3)],s=0,per=True);x,y,z=splev(np.linspace(u.min(),u.max(),200),tck,der=0)
            interp_pts=np.c_[x,y,z];hi_pt=interp_pts[np.argmax(interp_pts[:,2])];lo_pt=interp_pts[np.argmin(interp_pts[:,2])]
            tangent_pt, tangent_vec = hi_pt, unit(lo_pt - hi_pt)

            # c) Define a plane that is parallel to the tangent and 3.88mm anterior to it
            plane_normal = v_a
            plane_point = tangent_pt + plane_normal * 3.88
            
            # d) Find the intersection of the initial eyeball line with this new plane.
            # This is the final target point. It lies on the SI/ML line and is exactly
            # 3.88mm anterior to the M&W tangent.
            dot_v_n = np.dot(initial_line_vec, plane_normal)
            if abs(dot_v_n) < 1e-6: raise ValueError("Initial position line is parallel to the M&W constraint plane. Cannot solve.")
            w = initial_line_pt - plane_point
            s = -np.dot(w, plane_normal) / dot_v_n
            target = initial_line_pt + s * initial_line_vec
        scene_path=os.path.join(slicer.app.temporaryPath,f"{model_key.replace(' ','_')}.mrb");statusLabel.text="Downloading...";slicer.app.processEvents();urllib.request.urlretrieve(model_urls[model_key],scene_path)
        statusLabel.text="Loading...";slicer.app.processEvents();before=set(slicer.util.getNodes().values())
        if not slicer.util.loadScene(scene_path,{"clear":False}):raise RuntimeError("loadScene failed.")
        newly_loaded_nodes=list(set(slicer.util.getNodes().values())-before);shNode=slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene);runFolder=shNode.CreateFolderItem(shNode.GetSceneItemID(),run_name)
        oa_p,xf_orig=None,None
        for n in newly_loaded_nodes:
            shNode.SetItemParent(shNode.GetItemByDataNode(n),runFolder)
            if n.IsA("vtkMRMLLinearTransformNode") and "EyeTransform" in n.GetName():xf_orig=n
            elif n.IsA("vtkMRMLMarkupsFiducialNode"):
                idx=n.GetControlPointIndexByLabel(f"oa{side_lbl}")
                if idx!=-1:pos=[0,0,0];n.GetNthControlPointPositionWorld(idx,pos);oa_p=np.array(pos)
        if not xf_orig or oa_p is None:raise ValueError("Missing 'EyeTransform' or 'oa' from loaded model.")
        t_v=target-oa_p;x_mat=vtk.vtkMatrix4x4();xf_orig.GetMatrixTransformToParent(x_mat)
        t_mat=vtk.vtkMatrix4x4();[t_mat.SetElement(i,3,t_v[i]) for i in range(3)];vtk.vtkMatrix4x4.Multiply4x4(t_mat,x_mat,x_mat);xf_orig.SetMatrixTransformToParent(x_mat)
        statusLabel.text=f"SUCCESS! Created '{run_name}'.";
        
        # --- Store the settings of this run ---
        self.gui.lastRunSettings = {
            "model": model_key.split(" ")[0], # Just 'Male' or 'Female'
            "si": si_method,
            "ml": ml_method,
            "ap": ap_method
        }
        return True

    def _execute_script4(self,run_id):
        # --- Helper Functions ---
        def get_predicted_pos(node, label_prefix):
            if not node: return None
            idx = node.GetControlPointIndexByLabel(label_prefix)
            if idx == -1: return None
            pos = np.zeros(3); node.GetNthControlPointPositionWorld(idx, pos)
            return pos

        def get_truth_pos(node, label_prefix):
            if not node: return None
            idx = node.GetControlPointIndexByLabel(f"true_{label_prefix}")
            if idx == -1: return None
            pos = np.zeros(3); node.GetNthControlPointPositionWorld(idx, pos)
            return pos
            
        def dist_pt_ln(pt, ln_node):
            if pt is None or ln_node is None: return "N/A"
            p1,p2=np.zeros(3),np.zeros(3)
            ln_node.GetNthControlPointPositionWorld(0,p1); ln_node.GetNthControlPointPositionWorld(1,p2)
            line_vec=p2-p1; point_vec=pt-p1; line_len_sq=np.dot(line_vec,line_vec)
            if line_len_sq < 1e-9: return np.linalg.norm(point_vec)
            t = np.dot(point_vec, line_vec) / line_len_sq
            closest_point = p1 + t * line_vec
            return f"{np.linalg.norm(pt - closest_point):.2f}"

        # --- Main Logic ---
        true_n = slicer.util.getFirstNodeByName("Guyomarch_soft_tissue")
        if not true_n: raise ValueError("Ground truth node 'Guyomarch_soft_tissue' not found.")
        
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        pred_l = slicer.util.getFirstNodeByName("Left Eyeball lmrks")
        pred_r = slicer.util.getFirstNodeByName("Right Eyeball lmrks")
        if not pred_l or not pred_r:
            raise ValueError("Could not find 'Left Eyeball lmrks' and/or 'Right Eyeball lmrks' nodes.")

        left_folder_item = shNode.GetItemParent(shNode.GetItemByDataNode(pred_l))
        if not left_folder_item: raise ValueError("Could not find parent folder for 'Left Eyeball lmrks'.")
        
        folder_name = shNode.GetItemName(left_folder_item)
        
        # --- THIS IS THE FIX: Parse the Model Type (Sex) instead of the methods ---
        model_match = re.search(r"Run\d+_(?P<model>Female|Male)_", folder_name)
        report_column_text = model_match.group('model') if model_match else f"Run {run_id}"

        # Also get the methods for conditional checks
        methods_match = re.search(r"SI-(?P<si>.)_ML-(?P<ml>.)_AP-(?P<ap>.)", folder_name)
        methods = methods_match.groupdict() if methods_match else {}

        results = []
        # 1. Always calculate point-to-point landmark errors
        for side_sfx, pred_node in [('L', pred_l), ('R', pred_r)]:
            for lmk_prefix in ['oa', 'op', 'os', 'oi', 'om', 'ol', 'p']:
                label = f"{lmk_prefix}{side_sfx}"
                t_p = get_truth_pos(true_n, label)
                p_p = get_predicted_pos(pred_node, label)
                dist = f"{np.linalg.norm(t_p - p_p):.2f}" if t_p is not None and p_p is not None else "N/A"
                results.append((f"{label}_error", dist, report_column_text))
        
        # 2. Conditionally calculate point-to-line distances
        if methods: # Only proceed if methods were successfully parsed
            si_method_is_G = methods['si'] == 'G'
            ml_method_is_G = methods['ml'] == 'G'
            ap_method_uses_dlom = methods['ap'] in ['G', 'K']

            for side_sfx in ['L', 'R']:
                true_oa_pos = get_truth_pos(true_n, f"oa{side_sfx}")
                pred_oa_pos = get_predicted_pos(pred_l if side_sfx == 'L' else pred_r, f"oa{side_sfx}")
                
                line_checks = {
                    'DLOM': ap_method_uses_dlom, 'SOM': si_method_is_G, 'IOM': si_method_is_G,
                    'LOM': ml_method_is_G, 'MOM': ml_method_is_G
                }
                
                for line_prefix, should_check in line_checks.items():
                    if should_check:
                        line_node_name = f"{line_prefix}_{side_sfx}"
                        line_node = slicer.util.getFirstNodeByName(line_node_name)
                        if line_node:
                            pred_dist = dist_pt_ln(pred_oa_pos, line_node)
                            results.append((f"pred_{line_prefix}-{side_sfx}-oa{side_sfx}", pred_dist, report_column_text))
                            true_dist = dist_pt_ln(true_oa_pos, line_node)
                            results.append((f"true_{line_prefix}-{side_sfx}-oa{side_sfx}", true_dist, report_column_text))

        return results

# --- Define the GUI Widget Class ---
class AdvancedOrbitalWorkflowGUI(qt.QWidget):
    def __init__(self,parent=None):
        super(AdvancedOrbitalWorkflowGUI,self).__init__(parent)
        self.logic = AdvancedOrbitalWorkflowLogic(self)
        self.runCounter = 1
        self.setup() # This calls _setup_connections
        
        # We only need ONE observer now, for the Mautner instructions.
        # All the complex, failing logic for validation is removed.
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAddedEvent, self.onAPMethodChanged)
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeRemovedEvent, self.onAPMethodChanged)
        
        # Manually set the initial state of the UI
        self.onAPMethodChanged()
        self.onRefreshValidation(silent=True) # Call this SILENTLY at startup

    def setup(self):
        self.setWindowTitle("Advanced Orbital Workflow");self.mainLayout=qt.QVBoxLayout(self)
        self.hard_tissue_url="https://github.com/user-attachments/files/27900137/Guyomarch_hard_tissue.mrk.json";self.soft_tissue_url="https://github.com/user-attachments/files/27900157/Guyomarch_soft_tissue.mrk.json"
        self.model_urls={"Female Left":"https://drive.google.com/uc?export=download&id=1IO2-DIroRDhs84rBsQc1srfuzDFyRy2g","Female Right":"https://drive.google.com/uc?export=download&id=1-QCnBmAdogNQLweVzcdVd_SVd3oImz85","Male Left":"https://drive.google.com/uc?export=download&id=120wrETZx5o0-0CwAzldF07ZnFKNgn-Km","Male Right":"https://drive.google.com/uc?export=download&id=1D2ZakWhd6jefyFT-EN3ECdNqVolpi9Ak"}
        self._setup_sections();self._setup_connections()

    def _setup_sections(self):
        self.loadHardTissueButton=qt.QPushButton("Download/Load Hard Tissue Lmks");box1=self._create_collapsible_box("Setup 1: Load Data");box1.layout().addRow(self.loadHardTissueButton);self.mainLayout.addWidget(box1)
        self.runStep1Button=qt.QPushButton("Create Blueprint Planes");box2=self._create_collapsible_box("Setup 2: Create Blueprint");box2.layout().addRow(self.runStep1Button);self.mainLayout.addWidget(box2)
        box3=self._create_collapsible_box("Setup 3: Place Anatomical Landmarks");box3.layout().addRow(qt.QLabel("<b>USER ACTION:</b>\n- Place 'ekL'/'ekR' in 'Guyomarch_hard_tissue'.\n- If using M&W, also draw 'L_orbit' and 'R_orbit' curves."));self.mainLayout.addWidget(box3)
        self.runStep2Button=qt.QPushButton("Create Orbital Measurements");box4=self._create_collapsible_box("Setup 4: Create Measurements");box4.layout().addRow(self.runStep2Button);self.mainLayout.addWidget(box4)
        self.mainLayout.addWidget(self._create_placement_box())
        self.loadSoftTissueButton=qt.QPushButton("Download/Load Soft Tissue Lmks");box6=self._create_collapsible_box("Step 6 (Optional): Load Ground Truth");box6.layout().addRow(self.loadSoftTissueButton);self.mainLayout.addWidget(box6)
        self.mainLayout.addWidget(self._create_validation_box())
        self.mainLayout.addWidget(self._create_management_box())
        self.mainLayout.addStretch(1)

    def _create_placement_box(self):
        box=self._create_collapsible_box("Step 5: Create Eyeball Placement Run");layout=box.layout()
        self.modelSelector=qt.QComboBox();self.modelSelector.addItems(list(self.model_urls.keys()));layout.addRow("Select Eyeball Model:",self.modelSelector)
        self.siMethodSelector=qt.QComboBox();self.siMethodSelector.addItems(["Guyomarc'h et al. 2012","Kazuta et al. 2022"]);layout.addRow("Superoinferior Method:",self.siMethodSelector)
        self.mlMethodSelector=qt.QComboBox();self.mlMethodSelector.addItems(["Guyomarc'h et al. 2012"]);layout.addRow("Mediolateral Method:",self.mlMethodSelector)
        self.apMethodSelector=qt.QComboBox();self.apMethodSelector.addItems(["Guyomarc'h et al. 2012","Kazuta et al. 2022","Mautner and Wilkinson 2003"]);layout.addRow("Anteroposterior Method:",self.apMethodSelector)
        self.mautnerInstructions=qt.QLabel("<b>Action Required:</b> Create Closed Curves named 'L_orbit' and 'R_orbit'.");self.mautnerInstructions.setStyleSheet("color:#D4A017;font-weight:bold;");self.mautnerInstructions.setWordWrap(True);self.mautnerInstructions.setVisible(False);layout.addRow(self.mautnerInstructions)
        self.runPlacementButton=qt.QPushButton("Run");layout.addRow(self.runPlacementButton)
        self.placementStatusLabel=qt.QLabel("Ready.");layout.addRow("Status:",self.placementStatusLabel)
        return box

    def _create_validation_box(self):
        box=self._create_collapsible_box("Step 7 (Optional): Run Validation");layout=box.layout()
        self.refreshValidationButton = qt.QPushButton("1. Refresh Validation Status"); layout.addRow(self.refreshValidationButton)
        self.runSelector=qt.QComboBox();layout.addRow("2. Select Run to Validate:",self.runSelector)
        self.runValidationButton=qt.QPushButton("3. Run Validation");layout.addRow(self.runValidationButton)
        notice=qt.QLabel("<i>To compare different runs, copy the results to a spreadsheet before running a new validation.</i>");notice.setWordWrap(True);notice.setStyleSheet("font-style:italic;");layout.addRow(notice)
        self.validationResultsTable=qt.QTableWidget();self.validationResultsTable.setColumnCount(3);self.validationResultsTable.setHorizontalHeaderLabels(["Measurement","Value (mm)","Method"]);self.validationResultsTable.setMinimumHeight(200);self.validationResultsTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers);self.validationResultsTable.setSelectionBehavior(qt.QAbstractItemView.SelectRows);layout.addRow(self.validationResultsTable)
        self.copyTableButton=qt.QPushButton("Copy Table to Clipboard");layout.addRow(self.copyTableButton)
        return box
        
    def _create_management_box(self):
        box=self._create_collapsible_box("Management");layout=box.layout()
        self.cleanupRunsButton=qt.QPushButton("Clean Up ONLY Runs");layout.addRow(self.cleanupRunsButton)
        self.cleanupAllButton=qt.QPushButton("Clean Up ALL Generated Nodes");layout.addRow(self.cleanupAllButton)
        return box

    def _setup_connections(self):
        self.loadHardTissueButton.connect('clicked(bool)',lambda:self.onLoadMarkups(self.hard_tissue_url,"Guyomarch_hard_tissue"))
        self.loadSoftTissueButton.connect('clicked(bool)',lambda:self.onLoadMarkups(self.soft_tissue_url,"Guyomarch_soft_tissue"))
        self.runStep1Button.connect('clicked(bool)',lambda:self.logic.run_script_with_error_handling(self.logic._execute_script1))
        self.runStep2Button.connect('clicked(bool)',lambda:self.logic.run_script_with_error_handling(self.logic._execute_script2))
        self.runPlacementButton.connect('clicked(bool)',self.onRunPlacement)
        self.apMethodSelector.connect("currentIndexChanged(int)",self.onAPMethodChanged)
        self.runValidationButton.connect('clicked(bool)',self.onRunValidation)
        self.copyTableButton.connect('clicked(bool)',self.onCopyToClipboard)
        self.cleanupRunsButton.connect('clicked(bool)',self.onCleanupRuns)
        self.cleanupAllButton.connect('clicked(bool)',self.onCleanupAll)
        self.refreshValidationButton.connect('clicked(bool)', self.onRefreshValidation)

    def onAPMethodChanged(self):
        isMautnerSelected=self.apMethodSelector.currentText=="Mautner and Wilkinson 2003"
        self.mautnerInstructions.setVisible(isMautnerSelected)
        l_orbit=slicer.util.getFirstNodeByName("L_orbit");r_orbit=slicer.util.getFirstNodeByName("R_orbit")
        self.runPlacementButton.enabled=not isMautnerSelected or (l_orbit and r_orbit)
        self.runPlacementButton.toolTip="Ready to run." if self.runPlacementButton.enabled else "Please create 'L_orbit' and 'R_orbit' curves first."
    
    def onRefreshValidation(self, silent=False):
        """
        This function is the single source of truth. It manually checks all conditions
        and updates the Run Selector and the Run Validation button state.
        """
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        
        # --- 1. Update the Run Selector dropdown ---
        current_selection = self.runSelector.currentText
        self.runSelector.blockSignals(True)
        self.runSelector.clear()
        
        sceneItemID = shNode.GetSceneItemID()
        childIDs = vtk.vtkIdList()
        shNode.GetItemChildren(sceneItemID, childIDs)
        
        run_numbers = set()
        for i in range(childIDs.GetNumberOfIds()):
            itemID = childIDs.GetId(i)
            itemName = shNode.GetItemName(itemID)
            
            # --- THE CORRECT API CALL ---
            # A folder is an item that has no data node associated with it.
            isFolder = shNode.GetItemDataNode(itemID) is None

            if isFolder and itemName.startswith("Run"):
                match = re.search(r"Run(\d+)", itemName)
                if match:
                    run_numbers.add(match.group(1))

        sorted_runs = sorted(list(run_numbers), key=int)
        if sorted_runs:
            self.runSelector.addItems(sorted_runs)
            if current_selection in sorted_runs:
                self.runSelector.setCurrentText(current_selection)
        
        self.runSelector.blockSignals(False)

        # --- 2. Check all conditions to enable the validation button ---
        run_id = self.runSelector.currentText
        
        # Default to disabled
        self.runValidationButton.enabled = False
        
        truth_node_exists = slicer.util.getFirstNodeByName("Guyomarch_soft_tissue") is not None
        run_id_exists = run_id != ""

        has_left_folder = False
        has_right_folder = False
        if run_id_exists:
            for i in range(childIDs.GetNumberOfIds()):
                itemID = childIDs.GetId(i)
                itemName = shNode.GetItemName(itemID)

                # --- THE CORRECT API CALL ---
                isFolder = shNode.GetItemDataNode(itemID) is None
                
                if isFolder:
                    if itemName.startswith(f"Run{run_id}") and "Left" in itemName:
                        has_left_folder = True
                    if itemName.startswith(f"Run{run_id}") and "Right" in itemName:
                        has_right_folder = True
        
        # Final decision
        all_conditions_met = truth_node_exists and run_id_exists and has_left_folder and has_right_folder
        self.runValidationButton.enabled = all_conditions_met

        # Provide clear feedback
        if not truth_node_exists:
            self.runValidationButton.toolTip = "Validation requires 'Guyomarch_soft_tissue' node (Step 6)."
        elif not run_id_exists:
            self.runValidationButton.toolTip = "No Runs found. Click 'Refresh' after creating a run."
        elif not (has_left_folder and has_right_folder):
            self.runValidationButton.toolTip = f"Run {run_id} is missing a complete Left/Right folder pair."
        else:
            self.runValidationButton.toolTip = "Ready to validate."

        if not silent:
            slicer.util.infoDisplay("Validation status refreshed.")
    
    def _create_collapsible_box(self,title):
        try:
            import ctk
            box = ctk.ctkCollapsibleButton()
        except ImportError:
            box = qt.QGroupBox()
            box.setCheckable(True)
        box.text = title
        # This is the correct way to set a layout on a ctkCollapsibleButton
        layout = qt.QFormLayout(box)
        return box

    def onRunPlacement(self):
        # --- Check if settings have changed to decide whether to increment the run counter ---
        currentSettings = {
            "model": self.modelSelector.currentText.split(" ")[0],
            "si": self.siMethodSelector.currentText,
            "ml": self.mlMethodSelector.currentText,
            "ap": self.apMethodSelector.currentText
        }
        
        # If lastRunSettings doesn't exist or if settings are different, increment counter
        if not hasattr(self, 'lastRunSettings') or self.lastRunSettings != currentSettings:
            if hasattr(self, 'lastRunSettings'): # Don't increment on the very first run
                 self.runCounter += 1
            self.lastRunSettings = currentSettings

        self.logic.run_script_with_error_handling(self.logic._execute_script3,self.runCounter,self.modelSelector.currentText,self.model_urls,self.placementStatusLabel,self.siMethodSelector.currentText,self.mlMethodSelector.currentText,self.apMethodSelector.currentText)
    
    def onLoadMarkups(self,url,node_name):
        if slicer.util.getFirstNodeByName(node_name):slicer.util.infoDisplay(f"Node '{node_name}' already exists.");return
        try:
            temp_path=os.path.join(slicer.app.temporaryPath,os.path.basename(url.split('?')[0]));urllib.request.urlretrieve(url,temp_path)
            node=slicer.util.loadMarkups(temp_path);node.SetName(node_name)
            slicer.util.infoDisplay(f"Successfully loaded '{node_name}'.")
        except Exception as e:slicer.util.errorDisplay(f"Failed to load from URL: {e}");slicer.util.showStatusMessage("")

    def onRunPlacement(self):
        self.logic.run_script_with_error_handling(self.logic._execute_script3,self.runCounter,self.modelSelector.currentText,self.model_urls,self.placementStatusLabel,self.siMethodSelector.currentText,self.mlMethodSelector.currentText,self.apMethodSelector.currentText)

    def onRunValidation(self):
        run_id=self.runSelector.currentText
        if not run_id:slicer.util.warningDisplay("Please select a run to validate.");return
        results=self.logic.run_script_with_error_handling(self.logic._execute_script4,run_id)
        if not results:return
        self.validationResultsTable.setRowCount(0);self.validationResultsTable.setRowCount(len(results))
        for i,row_data in enumerate(results):
            measurement,value,method=row_data;self.validationResultsTable.setItem(i,0,qt.QTableWidgetItem(measurement));self.validationResultsTable.setItem(i,1,qt.QTableWidgetItem(str(value)));self.validationResultsTable.setItem(i,2,qt.QTableWidgetItem(method))
        self.validationResultsTable.resizeColumnsToContents()

    def onCopyToClipboard(self):
        clipboard=qt.QApplication.clipboard();text=""
        headers=[self.validationResultsTable.horizontalHeaderItem(c).text() for c in range(self.validationResultsTable.columnCount)];text+="\t".join(headers)+"\n"
        for r in range(self.validationResultsTable.rowCount):
            row_items=[self.validationResultsTable.item(r,c).text() if self.validationResultsTable.item(r,c) else "" for c in range(self.validationResultsTable.columnCount)]
            text+="\t".join(row_items)+"\n"
        clipboard.setText(text);slicer.util.infoDisplay("Results table copied to clipboard.")

    def onCleanupRuns(self):
        self.logic.undo_runs();self.placementStatusLabel.text="Ready.";slicer.util.infoDisplay("Run cleanup complete.")
        
    def onCleanupAll(self):
        self.logic.undo_all();self.placementStatusLabel.text="Ready.";slicer.util.infoDisplay("Full cleanup complete.")

# --- Main execution block ---
try:
    if 'advancedWorkflowGUI' in globals() and advancedWorkflowGUI.parent():globals()['advancedWorkflowGUI'].parent().close()
    del globals()['advancedWorkflowGUI']
except(NameError,KeyError):pass
advancedWorkflowGUI=AdvancedOrbitalWorkflowGUI()
dockWidget=qt.QDockWidget("Advanced Orbital Workflow");dockWidget.setWidget(advancedWorkflowGUI)
slicer.util.mainWindow().addDockWidget(qt.Qt.RightDockWidgetArea,dockWidget);dockWidget.show()

```
