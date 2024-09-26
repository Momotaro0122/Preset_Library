# Preset Library
A tool containing import, export, and blending preset functions.

_Last updated by Martin Lee: 2024-09-10_

---

### INTRODUCTION

This tool is based on the old preset lib tool, but adds some new features (like blending presets, and importing a single attribute of a node), renewing the whole UI, and also organizing the data files with new structures.

### How to set up

```python
import presetlib.presetlib_ui as pp
reload(pp)
win = pp.MainPresetLibUI()
win.show()
```
---
## How to import

1. Make sure you are on the **Import Tab**.
2. Select the path you want to import from, the default is Y drive from the server.
3. Hit the **Load** button.
4. After hitting the load button, you will see the character name appear in the character combo box. Select the character you want to import in the dropdown list.
5. After selecting the character name in the list, you will see the preset name appear in the **Preset Name** combo box.
6. You can choose whether you want to import the whole node(s) or a single attribute from the two radio buttons before selecting the preset name from the dropdown menu.
7. Select the preset you want to import, and you will see all the sorted nodes and data from that preset.
8. After that, you can either **Select All** or manually select the nodes for import. When it’s done, hit **Import Preset**.

### Import single attribute

1. Finish the steps from 1-5 in "How to import".
2. Select **Single Attribute** button.
3. Select the preset you want to import.
4. Select the node you want to import.
5. Select the attribute you want to import and hit **OK**.

## How to export

1. Select the path you want to export.
2. The server path for exporting will only be open for Sups, Leads, or certain artists.
3. Select any part of the character(s) that you want to export and hit **Refresh Selection**.
4. Select the node(s) that you want to export, or hit **Select All** for all the nodes.
5. Hit **Export**.
6. Choose or type in the preset name.

### Export custom nodes

1. Turn on the **Export Node Mode**.
2. Hit **Refresh Selection** to only export the custom nodes, or hit **Add Custom Node To List** to export the nodes with the other default nodes.
3. Select the node(s) that you want to export.
4. Hit **Export**.

- **Only export the custom nodes demo**.
- **Export the nodes with the other default nodes demo**: Do this after finishing steps 1-5 from "How to export".

---

## How to blend preset

1. This function only opens in shot and abc scenes. Please make sure to import the preset that you need before blending.
2. If the scene already has preset layers, start from step 3.
3. You can hit the **Refresh Imported Preset** button to see what presets were imported in this shot and are ready for blending.
4. Hit the **Create Preset Layers** button, and select what preset you want to create an animation layer for. You can see the preset layer you just created here.
5. After creating all the preset layers, hit the **Fill Edit Layers List** button.
6. Now, you can use two or more layers by keying their weights to approach blending.

## Import Tab UI Introduction

- **Import Tab**:
  - Radio buttons: Local, Server
  - Server path: `Y:/{Show}/assets/type/Character/{Character}/work/elems/Presetlib/`
  - Local path: `C:/Users/{User Name}/Documents/maya/{Version}/presets/attrPresets`

- **Browse** button for choosing the directory you want.
- **Load** button for loading character names.
- **Character combo box** for choosing character import.
- **Choose Whole nodes** or **Single Attribute**.

  *Make sure to select which mode (Whole nodes or Single Attribute) you want before selecting the preset name from the dropdown list. You can check if the nodes can be imported.*

- Section for deciding the preset you want to import.
- A tree list for each node’s detail in the preset.

---

## Export Tab UI Introduction

- **Export Tab**:
  - Path-changing section.
  - **Refresh Selection** button for loading the tree list with assets and their nodes in the scene.
  - Export tree list part, for choosing which node(s) you want to export.

---

## Edit Tab UI Introduction

- **Edit Tab**:
  - Imported Preset tree list: This list will show which preset has been imported in this shot.
    - *This list can collapse.*

- **Create Preset Layers** button: After clicking, a dialog will pop up for the user to decide which imported preset they want to create a preset layer for.
- After hitting the **Fill Edit Layers List** button, the preset will show up as a part of the list.

---

### Preset Layer Editor

- Name of the preset layer (always starts with `PRESETLIB_`).
- Slider for adjusting the value of the preset layer’s weight.
- Set key on the current frame for the preset layer’s weight.
- Remove all keys that have been set on this preset layer’s weight.
- Select the current preset layer’s node.

---

## Preset Manager

This tool is for users to manage the existing presets.

### How to open?

1. Hit the **Load** button.
2. Select **Character** in the dropdown list.
3. Right-click on the **Preset Name** combo box.
4. Left-click on **Preset Manager**.

### Rename

1. Double-click on the creator of the preset.
2. Select the preset you want to manage.
3. Hit the **Rename** button, type in the new name, and hit **OK**.

### Delete

1. Double-click on the creator of the preset.
2. Select the preset you want to manage.
3. Hit the **Delete** button, and confirm with **Yes**.

### Publish & Unpublish

The publish system is for users who have access to the preset server to indicate which preset is ready for other artists to use in the show.

1. Double-click on the creator of the preset.
2. Select the preset you want to **Publish** or **Unpublish**.
3. Hit the **Publish** or **Unpublish** button.
4. After confirming in the dialog, if “---(Published)” shows up after your preset name, it means you published it successfully.

Now you can see the preset in the **Preset Lib**. If you have access to the server, your preset dropdown list will show all presets, including those that haven't been published. If you don’t have access to the server, your preset dropdown list will only show the presets that have been published.
