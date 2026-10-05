If the projected view of landmarks drive you insane (as much as they drive me insane by cluttering my multiplanar view), use this code once all landmarks are loaded in the scene. 


```python
import slicer

def applyMarkupDisplaySettings(node):
    if not node:
        return
    # Turn off 2D slice projection
    node.SetSliceProjection(0)
    # Disable the outline behind the slice plane
    node.SetSliceProjectionOutlinedBehindSlicePlane(False)
    if hasattr(node, 'SetSliceProjectionUseFiducialColor'):
        node.SetSliceProjectionUseFiducialColor(False)
    # Disable occluded visibility in 3D
    if hasattr(node, 'SetOccludedVisibility'):
        node.SetOccludedVisibility(False)

# Apply to default node (for new markups)
defaultNode = slicer.mrmlScene.GetDefaultNodeByClass('vtkMRMLMarkupsDisplayNode')
if not defaultNode:
    defaultNode = slicer.vtkMRMLMarkupsDisplayNode()
    slicer.mrmlScene.AddDefaultNode(defaultNode)
applyMarkupDisplaySettings(defaultNode)

# Apply to ALL existing markups display nodes (fiducials, lines, planes)
count = 0
for node in slicer.util.getNodesByClass('vtkMRMLMarkupsDisplayNode'):
    applyMarkupDisplaySettings(node)
    count += 1

print(f"Applied settings to default node + {count} existing markups display node(s).")
```
