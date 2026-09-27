If the projected view of landmarks drive you insane like the drive me insane, use this code once all landmarks are loaded in the scene. 


```python
import slicer

# --- Helper: apply settings to a single display node ---
def applyMarkupDisplaySettings(node):
    if not node:
        return
    # Turn off 2D slice projection
    # vtkMRMLMarkupsDisplayNode.ProjectionOff == 0
    node.SetSliceProjection(0)
    # Disable the outline behind the slice plane
    node.SetSliceProjectionOutlinedBehindSlicePlane(False)
    # Some Slicer versions also expose an "UseFiducialColor"/"Outlined" combo;
    # make sure the outlined variant is off too if the method exists.
    if hasattr(node, 'SetSliceProjectionUseFiducialColor'):
        node.SetSliceProjectionUseFiducialColor(False)

# --- 1. Apply to the default node (for new markups) ---
defaultNode = slicer.mrmlScene.GetDefaultNodeByClass('vtkMRMLMarkupsDisplayNode')
if not defaultNode:
    defaultNode = slicer.vtkMRMLMarkupsDisplayNode()
    slicer.mrmlScene.AddDefaultNode(defaultNode)
applyMarkupDisplaySettings(defaultNode)

# --- 2. Apply to all existing markups display nodes ---
count = 0
for node in slicer.util.getNodesByClass('vtkMRMLMarkupsDisplayNode'):
    applyMarkupDisplaySettings(node)
    count += 1

print(f"Applied settings to default node + {count} existing markups display node(s).")


```
