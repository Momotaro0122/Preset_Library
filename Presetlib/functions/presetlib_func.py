from pynasty import *
import sys
import os
import stat
import ast
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import shutil
import json
import ICON_dirs.get as ig
import datetime
import re
from aronado import _sg_query_util
import time
import tempfile
from misc_pub import get_owner
from presetlib.utils.preset_logger import PRESETLIBLogger
import shotgun

reload(_sg_query_util)
# Configs and Setup
PTH_LIST = ['G:/Tech_Animation/scripts']
MAYA_VERSION = os.environ.get('MAYA_VERSION', '')
MAYA_DOC_FOLDER_NAME = MAYA_VERSION if int(MAYA_VERSION) >= 2016 else MAYA_VERSION + '-x64'
# LOCAL_PRESET_BASE = ""
LOCAL_PRESET_BASE = os.path.join(os.getenv('HOME'), 'maya', MAYA_DOC_FOLDER_NAME, 'presets', 'attrPresets')
# Y:\DJA\assets\type\Character\Ariel\work\elems
SERVER_PRESET_BASE = os.path.join('Y:/{}/assets/type/Character'.format(os.environ.get('TT_PROJCODE')))
DATA_DUMP_PATH = "Y:/{}/episodes/{}/shots/{}/work/elems/Presetlib".format(os.environ.get('TT_PROJCODE'),
                                                                          os.environ.get("TT_EPNAME"),
                                                                          os.environ.get('TT_ENTNAME'))
sg = shotgun.connect()
CURRENT_SHOT = os.environ.get('TT_ENTNAME')
USER = os.environ.get('TT_USER')
decoder = json.JSONDecoder()
logger = PRESETLIBLogger().get_logger()
# Add paths to sys.path
for pth in PTH_LIST:
    if pth not in sys.path:
        sys.path.append(pth)


def extract_letters(s):
    match = re.match(r'([a-zA-Z_]+)_\d+', s)
    if match:
        return match.group(1)
    else:
        return None


def resolve_folder_errors(path):
    if not os.path.isdir(path):
        os.makedirs(path)


# Selection Functions.
def get_namespace(node_name):
    return node_name.split(':')[0] if ':' in node_name else 'default_namespace'


def get_all_dynamic_nodes(ns, ns_div):
    dynamic_patterns = [
        "{}{}{}".format(ns, ns_div, suffix) for suffix in [
            "*DC_Dyn",
            "*Cloth_Ctrl",
            "*C_Dynamics_Ctrl",
            "*Dynamic_Ctrl",
            "*Dynamics_*Ctrl",
            "*Stiff*_Dyn",
            "*Dynamics_Main_Ctrl",
            "*DynamicSettings_Ctrl"
        ]
    ]

    node_types = [
        'nCloth', 'hairSystem', 'nucleus', 'nRigid',
        'dynamicConstraint', 'follicle', 'blendShape',
        'deltaMush', 'textureDeformer', 'volumeAxisField'
    ]

    nodes = []
    for pattern in dynamic_patterns:
        nodes.extend(cmds.ls(pattern))
        nodes.extend(cmds.ls(pattern, type='transform'))

    for nodetype in node_types:
        nodes.extend(cmds.ls("{}{}".format(ns, ns_div), type=nodetype))

    connected_hair_systems = [
        cmds.listConnections(h + '.startCurveAttract', s=1)[0]
        for h in cmds.ls("{}{}".format(ns, ns_div), type='hairSystem')
        if cmds.listConnections(h + '.startCurveAttract', s=1)
    ]

    nodes.extend(connected_hair_systems)
    nodes.extend(cmds.ls("{}{}".format(ns, ns_div), type='blendShape'))

    return nodes

def select_nodes(*args):
    selections = cmds.ls(sl=1)
    data_dict = {}
    for item in selections:
        if check_shot_asset() == "Shot":
            namespace = get_namespace(item)
            ns_divs = [':*', ':DYN:*', ':Cloth:*', ':Hybrid:*', ':Hair:*']
            all_dyn_nodes = []
            for ns_div in ns_divs:
                all_dyn_nodes.extend(get_all_dynamic_nodes(namespace, ns_div))
        else:
            namespace = ""
            ns_divs = ["*"]
            all_dyn_nodes = []
            for ns_div in ns_divs:
                all_dyn_nodes.extend(get_all_dynamic_nodes(namespace, ns_div))
            namespace = os.environ.get('TT_ENTNAME')
        node_type_dict = {node: cmds.nodeType(node) for node in all_dyn_nodes}
        data_dict[namespace] = node_type_dict
    return data_dict

def select_custom_nodes(*args):
    selections = cmds.ls(sl=1)
    data_dict = {}
    all_dyn_nodes = []
    for item in selections:
        if check_shot_asset() == "Shot":
            namespace = get_namespace(item)
            all_dyn_nodes.append(item)
        else:
            all_dyn_nodes.append(item)
            namespace = os.environ.get('TT_ENTNAME')
        node_type_dict = {node: "Custom" for node in all_dyn_nodes}
        data_dict[namespace] = node_type_dict
    return data_dict


def create_preset_structure(base_path, user_name, preset_name, char_name):
    """
    # Example usage
    base_path = "C:\\Users\\Martin\\Documents\\maya\\2019"  # Your desired base path
    user_name = "Martin Lee"  # User's name
    preset_name = "Ariel_Hair"  # Preset's name

    create_preset_structure(base_path, user_name, preset_name)
    """
    # Create directory structure
    user_path = os.path.join(base_path, "Presetlib", user_name, preset_name)
    if not os.path.exists(user_path):
        os.makedirs(user_path)

    # Record the current time
    now = datetime.datetime.now()
    save_time = now.strftime('%Y-%m-%d %H:%M:%S')
    save_character = char_name

    # Write the time and character name to the json file
    info_path = os.path.join(base_path, "Presetlib", user_name)
    info_json_path = os.path.join(info_path, "info.json")
    if os.path.exists(info_json_path) and os.path.getsize(info_json_path) > 0:
        with open(info_json_path, 'r') as f:
            json_data = json.load(f)
    else:
        json_data = {}
    json_data[preset_name] = {
            "save_time": save_time,
            "owner": os.environ.get('TT_USER'),
            "publish": False
        }
    json_data["character_name"] = save_character
    with open(info_json_path, "w") as f:
        json.dump(json_data, f, indent=4)
    logger.info("Preset structure created at: {}".format(user_path))
    return user_path


# Get Functions. 'Ariel', 'Character', dir_append=['products','PresetLib']
def check_shot_asset():
    """Retrieve the file type from environment variable TT_ENTTYPE."""
    return os.environ.get('TT_ENTTYPE')


def get_asset_path_with_print(asset_name, asset_type, dir_append=[]):
    """Get the asset path and print it."""
    path = ig.get_asset_path(asset_name, asset_type, dir_append=dir_append)
    return path


def save_attrPreset(node, filename):
    """
    Save attribute preset for the given node and filename.

    Parameters:
    - node (str): The node for which the preset needs to be saved.
    - filename (str): The filename to which the preset will be saved.

    Returns:
    - str: Path of the saved attribute preset.
    """
    preset_path = os.path.join(LOCAL_PRESET_BASE, cmds.nodeType(node), filename + '.mel')
    if os.path.isfile(preset_path):
        os.remove(preset_path)

    saveAttrMelCmd = 'saveAttrPreset {} "{}" false;'.format(node, filename)
    return mel.eval(saveAttrMelCmd)


def get_map_dict_from_attr(node_name, attributes):
    """
    Retrieve a dictionary of PerVertex attributes for the specified node and its attributes.

    Parameters:
    - node_name (str): The name of the node.
    - attributes (list): List of attributes to be processed.

    Returns:
    - dict: Dictionary with attribute names as keys and their values as values.
    """
    map_dict = {}
    for attr in attributes:
        if 'PerVertex' in attr:
            if cmds.getAttr(node_name + '.' + attr.replace('PerVertex', 'MapType')) == 1:
                logger.info('Parsing %s' % node_name + '.' + attr)
                map_dict[attr] = cmds.getAttr(node_name + '.' + attr)
    return map_dict


def get_nCloth_map_dict(ncNode):
    """
    Get a dictionary of PerVertex attributes for a specified nCloth node.

    Parameters:
    - ncNode (str): Name of the nCloth node.

    Returns:
    - dict: Dictionary of PerVertex attributes.
    """
    nCloth_node = ncNode
    cloth_attr = cmds.listAttr(nCloth_node)
    return get_map_dict_from_attr(nCloth_node, cloth_attr)


def get_nConstraint_map_dict(nConst):
    """
    Get a dictionary of PerVertex attributes for a specified nConstraint node.

    Parameters:
    - nConst (str): Name of the nConstraint node.

    Returns:
    - dict: Dictionary of PerVertex attributes for connected components.
    """
    nComponents = cmds.listConnections(nConst + '.componentIds')
    logger.info('nComponents %s' % nComponents)

    map_dictionary = {}
    if nComponents:
        for ncomp in nComponents:
            ncomp_map_dict = {}
            ncomp_attr = cmds.listAttr(ncomp)
            ncomp_map_dict.update(get_map_dict_from_attr(ncomp, ncomp_attr))

            if ncomp_map_dict:
                ncomp_map_dict[ncomp + 'MapType'] = 1

            nconst_compo_id = cmds.listConnections(ncomp + '.outComponent', p=1)[0].split('.')[-1]
            if ncomp_map_dict:
                map_dictionary[nconst_compo_id] = ncomp_map_dict
            else:
                logger.warning("Passed {} map save because grab {} - presetlib_func.py - line269".
                               format(nconst_compo_id, ncomp_map_dict))
    return map_dictionary


def get_file_info(filepath):
    # Get the modification time
    save_time = time.strftime("%Y/%m/%d %H:%M", time.localtime(os.path.getmtime(filepath)))

    return {"save_time": save_time}


def apply_blendShape_weights(bs_node, mel_path, invert=False, populate_val=1, check_verts=False):
    '''
    #example weight line:
    blendAttr "inputTarget[0].inputTargetGroup[0].targetWeights[7]" 0;
    blendAttr "inputTarget[0].baseWeights[7]" 0;
    '''
    bs_target = cmds.listConnections(bs_node, type='mesh')[0]
    logger.info('bs_target %s' % bs_target)
    targ_v_count = cmds.polyEvaluate(bs_target, v=1)
    logger.info('targ_v_count %s' % targ_v_count)
    v_list = range(0, targ_v_count)
    weight_type = []
    weight_data_store = {}
    with open(mel_path, 'r') as bs_mel_file:
        for line in bs_mel_file:
            if 'Weights' in line:
                line_split = line.split('"')
                vert_i = line_split[1].split('[')[-1].split(']')[0]
                attr_name = line_split[1].strip()
                weight_data_store[int(vert_i)] = float(line_split[-1].split(';')[0])
                if attr_name not in weight_type and 'targetWeights' in attr_name:
                    weight_type.append('inputTarget[0].inputTargetGroup[0].targetWeights[{}]')
                elif attr_name not in weight_type and 'baseWeights' in attr_name:
                    weight_type.append('inputTarget[0].baseWeights[{}]')

                if vert_i not in v_list:
                    if not check_verts:
                        continue
                    else:
                        assert False, 'vert count is different on target blendshape, breaking'
                v_list.remove(int(vert_i))
    weight_type = list(set(weight_type))
    for v in v_list:
        if v in weight_data_store:
            wtyp = weight_type[0]
            val = weight_data_store[v]
            if invert:
                val = 1 - weight_data_store[v]
            cmds.setAttr(bs_node + '.' + wtyp.format(str(v)), val)
        else:
            cmds.setAttr(bs_node + '.' + wtyp.format(str(v)), populate_val)


def print_tree_items(tree_widget, parent_item=None, indent=0):
    if parent_item is None:
        # Get the count of root items, then start from each root item
        for i in range(tree_widget.topLevelItemCount()):
            root_item = tree_widget.topLevelItem(i)
            print_tree_items(tree_widget, root_item, indent)
    else:
        # Print the text of the current item
        print(' ' * indent, parent_item.text(0))
        # Traverse and print all child items
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            print_tree_items(tree_widget, child_item, indent + 2)


def build_nested_dict(current_path):
    if os.path.isdir(current_path):
        items = os.listdir(current_path)
        nested_structure = {}
        for item in items:
            item_path = os.path.join(current_path, item)
            nested_structure[item] = build_nested_dict(item_path)
        return nested_structure
    else:
        return None


def check_asset_scene_exist():
    all_load_asset = []
    for asset in cmds.ls(type='reference'):
        rig_container = asset.split('RN')[0] + ':Container'
        if cmds.objExists(rig_container):
            all_load_asset.append(rig_container.split(':')[0])
    return all_load_asset


def get_shot_asset():
    """
    all_asset_info = [{'type': 'Asset', 'id': 48730, 'name': 'Cauldron_Small'},
        {'type': 'Asset', 'id': 40323, 'name': 'CrystalCavern_SI'},
        {'type': 'Asset', 'id': 49914, 'name': 'FX_Bubble_Columns'},
        {'type': 'Asset', 'id': 54707, 'name': 'FX_Bubble_Columns_SetInt'},
        {'type': 'Asset', 'id': 50005, 'name': 'Jewels'},
        {'type': 'Asset', 'id': 40289, 'name': 'Lucia'},
        {'type': 'Asset', 'id': 51838, 'name': 'Matte_Underwater_Wrap_Day'},
        {'type': 'Asset', 'id': 48733, 'name': 'Wand_Coral'}]
    """
    all_asset_info = _sg_query_util.get_related_assets_to_shot_with_project(entname=os.environ['tt_entname'])
    """
    all_load_asset = [u'Ariel_01:assetInfo']
    """
    if cmds.ls(type='assetInfo'):
        # print("shot")
        all_load_asset = [extract_letters(asset.split(':')[0]) for asset in cmds.ls(type='assetInfo') if ':' in asset]
        # all_load_asset = [asset for asset in cmds.ls(type='assetInfo') if ':' in asset]
    else:
        # print("abc")
        extracted_set = set()
        all_load_asset = []
        for asset in cmds.ls(type='reference'):
            if ':' in asset:
                extracted = extract_letters(asset.split(':')[0])
                if extracted not in extracted_set:
                    extracted_set.add(extracted)
                    all_load_asset.append(extracted)
    return all_asset_info, all_load_asset


def check_all_shot_asset_path_exist(path):
    # path_template = "Y:\\DJA\\assets\\type\\Character\\{}\\work\\elems\\Presetlib"
    path = path.format(os.environ['TT_ENTNAME'])
    if path == SERVER_PRESET_BASE:
        path = os.path.join(path, '{}', 'work/elems/Presetlib')
    if check_shot_asset() == 'Shot':
        all_asset_info, all_load_asset_no_num = get_shot_asset()
        exist_dict = {}
        for item in all_asset_info:
            name = item['name']
            full_path = path.format(name)
            if os.path.exists(full_path) and name in all_load_asset_no_num:
                logger.info("Path for {} exists!".format(name))
                exist_dict[name] = full_path
            else:
                logger.info("Path for {} does NOT exist!".format(name))
        return exist_dict
    else:
        exist_dict = {}
        path = path.format(os.environ['TT_ENTNAME'])
        if os.path.exists(path):
            exist_dict[os.environ['TT_ENTNAME']] = path.format(os.environ['TT_ENTNAME'])
        return exist_dict


def check_file_nodes_type(file_path):
    if os.path.isfile(file_path):
        parent_directory_path = os.path.dirname(file_path)  # Get the parent directory path of the file
        file_node_type = os.path.basename(parent_directory_path)  # Get the name of the parent directory
        return file_node_type
    else:
        return None  # Return None if the file doesn't exist


def apply_attr_preset(node, mel_path):
    attrApplyCmd = 'applyAttrPreset {} "{}" 1;'.format(node, mel_path)
    logger.info(attrApplyCmd)
    mel.eval(attrApplyCmd)

"""
node = 'Ariel_01:Ponytail_05_Scalp_Geo_dup_blendShape'
mel_path = 'C:/Users/martinle/Desktop/Presetlib//martinle/only_test/blendShape//Ponytail_05_Scalp_Geo_dup_blendShape..mel'
apply_attrPreset(node, mel_path)
"""


def remove_key_animation(node):
    """
    Remove keys and zero out rotation of all the object(s) in obj2CutKey
    """
    optVar_setting = cmds.optionVar(q='animLayerSelectionKey')
    cmds.optionVar(intValue=['animLayerSelectionKey', 1])
    cmds.cutKey(node, cl=1)
    cmds.optionVar(intValue=['animLayerSelectionKey', optVar_setting])


# remove_key_animation('Ariel_01:', obj2CutKey=['Root_Ctrl'])


def disconnect_attr(node_witt_attr):
    try:
        obj = om.MSelectionList().add(node_witt_attr).getDependNode(0)
        dependFn = om.MFnDependencyNode(obj)
        mel.eval('CBdeleteConnection "{}";'.format(node_witt_attr))
        del obj
        del dependFn
    except RuntimeError:
        print("Failed to disconnect: {}".format(node_witt_attr))


def ns_abc_search(name_base, node_name):
    node = ['{}:{}:{}'.format(name_base, ns, node_name) for ns in ['Hybrid', 'Cloth', 'Hair', 'DYN']
            if cmds.objExists('{}:{}:{}'.format(name_base, ns, node_name))]
    if node:
        node = node[0]
        return node
    else:
        return None


def ns_depth_search(name_base, node_name, max_depth=5):
    ns_div = '*:'
    ns_depth = 0
    name_zero = 0
    returner = cmds.ls(name_base * name_zero + ns_div * ns_depth + node_name)
    while cmds.ls(name_base * name_zero + ns_div * ns_depth + node_name) == [] and ns_depth < max_depth:
        returner = cmds.ls(name_base * name_zero + ns_div * ns_depth + node_name)
        ns_depth += 1
        name_zero = 1
    returner = cmds.ls(name_base * name_zero + ns_div * ns_depth + node_name)
    return returner


def apply_map_type(nodeName, map_path, map_type, lyr1_ns=''):
    if map_type == 'nCloth_maps' or map_type == 'nRigid_maps':
        with open(map_path, 'r') as map_file:
            map_diction_string = map_file.read()
        map_diction = ast.literal_eval(map_diction_string)
        logger.info('dictionarized maps: %s' % map_diction)
        for nodeSearch in ns_depth_search(lyr1_ns, nodeName):
            for map_diction_item in map_diction:
                if map_diction[map_diction_item] != None:
                    print('currently applying attr:', map_diction_item)
                    cmds.setAttr(nodeSearch + '.' + map_diction_item, map_diction[map_diction_item], type='doubleArray')

    elif map_type == 'dyn_const_maps':
        logger.info('found available {}'.format(map_type))
        with open(map_path, 'r') as map_file:
            map_diction_string = map_file.read()
        map_diction = ast.literal_eval(map_diction_string)
        logger.info('dictionarized maps: %s' % map_diction)
        for nodeSearch in ns_depth_search(lyr1_ns, nodeName):
            for map_diction_item in map_diction:
                nComponent_get = cmds.listConnections(nodeSearch + '.' + map_diction_item)[0]
                for compo_attr in map_diction[map_diction_item]:
                    print('currently applying attr:', nodeName, nComponent_get, compo_attr)
                    if 'PerVertex' in compo_attr:
                        if cmds.objExists(nComponent_get + '.' + compo_attr):
                            cmds.setAttr(nComponent_get + '.' + compo_attr, map_diction[map_diction_item][compo_attr],
                                         type='doubleArray')
                        else:
                            logger.warning("Cannot find {} ... Will skip".format(nComponent_get + '.' + compo_attr))
                    elif 'MapType' in compo_attr:
                        if cmds.objExists(nComponent_get + '.' + compo_attr):
                            cmds.setAttr(nComponent_get + '.' + compo_attr, map_diction[map_diction_item][compo_attr])
                        else:
                            logger.warning("Cannot find {} ... Will skip".format(nComponent_get + '.' + compo_attr))

"""
nodeName = 'Torso_nRigidShape'
map_path = 'Y:\\DJA\\assets\\type\\Character\\Ariel\\work\\elems\\Presetlib\\martinle\\ariel_hair\\nRigid_maps\\Torso_nRigidShape.json'
map_type = 'nRigid_maps'
apply_map_type(nodeName, map_path, map_type, lyr1_ns='')
"""


def normalize_path(path):
    path = path.replace('\\\\', '/')
    path = path.replace('\\', '/')
    return path


# For Anim-layer.
def backup_and_overwrite(original_file, backup_path):
    # 1. Check if the original file exists
    if os.path.exists(original_file):
        # Get the current date and time
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # Use the date and time to create a backup file name
        backup_file = original_file.rsplit('.', 1)[0] + '_backup_{}.{}'.format(current_time,
                                                                               original_file.rsplit('.', 1)[1])
        shutil.copy(original_file, backup_file)
        logger.info('Backup created: %s', backup_file)
        # Check if 'backup' directory exists; if not, create it
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
        # Move the backup file to the 'backup' directory
        shutil.move(backup_file, os.path.join(backup_path, os.path.basename(backup_file)))
        logger.info('Backup file moved to "%s" directory.', backup_path)


'''
# Usage example
file_name = 'example.txt'
new_content = 'This is the new content for the file.'
backup_and_overwrite(file_name, new_content)
'''


def create_imported_preset_json(preset_name_path, shot_name, preset_name, imported_nodes_dict):
    # Define the path for the JSON file and the backup folder
    path = os.path.join(preset_name_path, 'imported_preset_info.json')
    backup_path = os.path.join(preset_name_path, 'backup')
    # Initialize an empty dictionary to store JSON data
    json_data = {}
    # Check if the file exists and is not empty
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, 'r') as f:
            json_data = json.load(f)
        backup_and_overwrite(path, backup_path)
    # Update the json_data dictionary
    if shot_name not in json_data:
        json_data[shot_name] = {}  # Create an empty dictionary if the shot_name key does not exist
    # Here, we assume imported_nodes_dict is a dictionary mapping node names to paths
    json_data[shot_name][preset_name] = imported_nodes_dict
    # Write the updated dictionary back to the file
    with open(path, "w") as f:
        json.dump(json_data, f, indent=4)
    # Log the creation of the backup
    logger.info('Backup created: %s', preset_name_path)


def reimport_for_preset_lay(preset_name):
    imported_preset_info_path = os.path.join(DATA_DUMP_PATH, 'imported_preset_info.json')
    if os.path.isfile(imported_preset_info_path):
        if check_shot_asset() == 'Shot':
            with open(imported_preset_info_path, "r") as f:
                info_data = json.load(f)
            for node, path in info_data[CURRENT_SHOT][preset_name].items():
                apply_attr_preset(node, path)
            logger.info("Reimport preset for layer done")


def create_anim_lay(selected_objects, char_name, preset_name):
    # 1. Toggle the viewport update to off
    cmds.ogs(p=True)
    if not selected_objects:
        cmds.error("Make sure you have something selected for create anim lay")
    else:
        if not cmds.objExists("PRESETLIB_{}_{}".format(char_name, preset_name)):
            replace_preset_name = preset_name
            if '.' in preset_name:
                replace_preset_name = preset_name.replace('.', '_')
            cmds.select(selected_objects)
            mel.eval(
                """
                animLayer AnimLayer1;
                setAttr AnimLayer1.rotationAccumulationMode 0;
                setAttr AnimLayer1.scaleAccumulationMode 1;
                animLayer -e -addSelectedObjects AnimLayer1;
                rename AnimLayer1 PRESETLIB_{}_{};
                """.format(char_name, replace_preset_name))
            start_frame = int(cmds.playbackOptions(query=True, minTime=True))
            end_frame = int(cmds.playbackOptions(query=True, maxTime=True))
            cmds.currentTime(start_frame, edit=True)
            reimport_for_preset_lay(preset_name)
            cmds.setKeyframe(selected_objects)
            cmds.setAttr("PRESETLIB_{}_{}.weight".format(char_name, replace_preset_name), 0)
            # for frame in range(start_frame, end_frame + 1):
            #     cmds.currentTime(frame, edit=True)
            #     cmds.setKeyframe(selected_objects)
            logger.info("PRESETLIB_{}_{} Created!".format(char_name, replace_preset_name))
    # 3. Toggle the viewport update back to on
    cmds.ogs(p=True)


def get_added_keyframe(list1, list2):
    # Convert lists to sets
    set1 = set(list1)
    set2 = set(list2)
    # Find unique items in each set by subtracting the intersection
    unique_in_set1 = set1 - set2
    unique_in_set2 = set2 - set1
    # Combine the unique items from both sets
    unique_items = unique_in_set1.union(unique_in_set2)
    return unique_items


def read_mel_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
            return content
    except IOError as e:
        print("Error reading file: {}".format(e))
        return []


def parse_mel_attributes(file_path):
    mel_content = read_mel_file(file_path)
    attributes = []
    for line in mel_content:
        if line.startswith("blendAttr"):
            parts = line.split(" ")
            attr_name = parts[1].strip('"')
            attributes.append(attr_name)
    return attributes


def filter_mel_content_by_selected_attributes(file_path, selected_attributes):
    filtered_content = []
    mel_content = read_mel_file(file_path)
    for line in mel_content:
        if line.startswith("blendAttr"):
            parts = line.split(" ")
            attr_name = parts[1].strip('"')
            if attr_name in selected_attributes:
                filtered_content.append(line)
        else:
            filtered_content.append(line)
    return filtered_content


def attr_connected_override(mel_path, node, single_attr=False):
    logger.info("Node: {}".format(node))
    mel_attributes = parse_mel_attributes(mel_path)
    attributes = cmds.listAttr(node)
    if single_attr and cmds.listConnections(node, plugs=True):
        disconnect_attr(node)
        logger.warning("  Break Attribute: {}".format(node))
    if attributes:
        for attr in attributes:
            try:
                full_attr = "{}.{}".format(node, attr)
                connections = cmds.listConnections(full_attr, plugs=True)
                if connections and attr in mel_attributes:
                    disconnect_attr(full_attr)
                    logger.warning("  Break Attribute: {}".format(attr))
            except:
                pass


def modify_and_execute_script(selected_attributes, mel_file_path):
    filtered_mel_content = filter_mel_content_by_selected_attributes(mel_file_path, selected_attributes)
    with open(mel_file_path, "rt") as fin:
        data = fin.read()
    data = data.replace(data, "")
    data += '\n' + '\n'.join(filtered_mel_content)
    return data


def apply_single_attr_preset(node, mel_content):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mel', mode='w')
    temp_file.write(mel_content)
    temp_file.close()
    attrApplyCmd = 'applyAttrPreset {} "{}" 1;'.format(node, temp_file.name.replace('\\', '/'))
    mel.eval(attrApplyCmd)
    os.remove(temp_file.name)


#'martinle',
# def server_user_access():
#     if USER in ['damonl', 'erikg', 'riccardos', 'perryh', 'nguyenm', 'ernestos']:
#         return True
#     else:
#         return False
def find_all_sup_user():
    group = sg.find_one("Group", [["code", "is", "TechAnim_Supes"]], ["id"])
    users = []
    _user = []
    if group:
        group_id = group["id"]
        users = sg.find("HumanUser", [["groups", "is", {"type": "Group", "id": group_id}]],
                        ["id", "name", "email", "login"])
        for user in users:
            _user.append(user.get('email').split('@')[0])
    else:
        logger.error("Group 'TechAnim_Supes' not found.")

    return _user


def server_user_access(access_user_path):
    if os.path.exists(access_user_path) and os.path.getsize(access_user_path) > 0:
        with open(access_user_path, 'r') as f:
            json_data = json.load(f)
        if json_data['access']:
            return True
        else:
            return False
    else:
        return False


def preset_publish_checker(info_json, preset_name):
    if 'publish' in info_json[preset_name].keys():
        if info_json[preset_name]['publish']:
            return 'Published'
        else:
            return None


def collect_folder_info(path, character_name):
    # Get the user name
    user = os.environ.get('TT_USER', 'unknown_user')

    # Initialize the result dictionary
    result = {}

    # Iterate over all items in the given path
    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Check if it is a directory
        if os.path.isdir(item_path):
            # Get the last modified time
            mod_time = os.path.getmtime(item_path)
            save_time = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

            # Add information to the dictionary
            result[item] = {
                'owner': user,
                'save_time': save_time,
                'publish': False
            }

    # Add the character name outside of the for loop
    result["character_name"] = character_name

    return result


def build_info_json_for_old(user_path):
    user_path = user_path.replace('\\', '/')
    # Use os.path.normpath and split method to divide the path into parts
    path_parts = os.path.normpath(user_path).split(os.sep)
    info_json_path = os.path.join(user_path, "info.json")
    # Find the positions of "Character" and "work"
    try:
        character_index = path_parts.index("Character")
        work_index = path_parts.index("work")

        # Check if there is at least one element between "Character" and "work"
        if character_index < work_index - 1:
            name_between = path_parts[character_index + 1]
            print(name_between)
        else:
            print("There is no element between 'Character' and 'work'")
    except ValueError:
        print("'Character' or 'work' not found in the path")

    info = collect_folder_info(user_path, name_between)

    # Print formatted JSON
    #print(json.dumps(info, indent=4))
    with open(info_json_path, "w") as f:
        json.dump(info, f, indent=4)


class Attr_Lib_IO_Tool(object):
    def __init__(self, libPath=None):
        """Initialize the Attr_Lib_IO_Tool class.

        Args:
        - libPath (str, optional): Path to the library. Defaults to a constructed path.
        """
        # Construct or use provided library path
        default_path = libPath
        self.attrLibBase = default_path.replace('\\', '/')
        resolve_folder_errors(self.attrLibBase)
        # Define default attributes
        self.selective_attr_node_dict = {
            'mesh': ['primaryVisibility', 'visibility'],
            'MultiplierNode': ['copiesViewPercent'],
        }
        # Set default properties
        self.ns_in_list = True
        self.check_node_ex = True
        self.override_asset = False
        self.asset_task = False
        self.target_asset = ''

    def save_lib_preset(self, nodeName, user_desc):
        """
        Save the library preset for a given node.
        Args:
        - nodeName (str): The name of the node.
        - user_desc (str): User description for the preset.
        """
        obj_name_base = nodeName
        # Handle node naming based on override setting
        if ':' in nodeName:
            if self.override_asset:
                assert self.target_asset, 'self.target_asset cannot be "" '
                nodeName = obj_name_base = nodeName.split(':')[-1].strip()
            else:
                if ':' in nodeName:
                    namespace = nodeName.split(':')[0]
                    obj_name_base = nodeName.split(':')[-1]
        else:
            obj_name_base = nodeName
        node_type = cmds.nodeType(nodeName)
        # Define base directories and file paths
        mel_base = os.path.join(self.attrLibBase, node_type)

        resolve_folder_errors(mel_base)

        mel_file_path = os.path.join(mel_base, "{}.mel".format(obj_name_base))
        if os.path.exists(mel_file_path):
            os.remove(mel_file_path)
        # Handle attribute saving based on node type
        if node_type == 'mesh':
            attr_of_import = ['primaryVisibility', 'visibility', 'castsShadows', 'receiveShadows']
            export_dict = {attr: cmds.getAttr(nodeName + '.' + attr) for attr in attr_of_import}

            with open(os.path.join(mel_base, "{}.json".format(obj_name_base)), 'w') as json_dump_f:
                json.dump(export_dict, json_dump_f)
        else:
            src_attr_mel = save_attrPreset(nodeName, "{}".format(obj_name_base))
            shutil.move(src_attr_mel, mel_base)
        # Save node maps if the node is a certain type
        map_types = {
            'nCloth': 'nCloth_maps',
            'dynamicConstraint': 'dyn_const_maps',
            'nRigid': 'nRigid_maps'
        }
        if node_type in map_types:
            logger.info('saving maps for %s' % nodeName)
            map_base = os.path.join(self.attrLibBase, map_types[node_type])
            resolve_folder_errors(map_base)
            # Choose function based on node type
            map_func = get_nCloth_map_dict if node_type in ['nCloth', 'nRigid'] else get_nConstraint_map_dict

            maps = map_func(nodeName)
            if maps:
                with open(os.path.join(map_base, "{}.json".format(obj_name_base)), 'w') as map_file:
                    json.dump(maps, map_file)
            else:
                logger.warning("Passed {} map save because grab {} - presetlib_func.py - line742".
                               format(nodeName, maps))


    def getLibByAssetName(self, asset):
        """
        TODO: Logic can be improved way more. Should only need to walk it once.
        """
        full_lib_dict = {}
        lib_desc_dict = {}
        for dirpath, subdirs, files in os.walk(self.attrLibBase + '/' + asset):
            if files == ['node_list.txt']:
                lib_desc_dict = {}
                for lib_desc in subdirs:
                    for dirpath, subdirs, files in os.walk(self.attrLibBase + '/' + asset + '/' + lib_desc):
                        if files == []:
                            nodeDictList = {}
                            for nodeType in subdirs:
                                nodeDictList[nodeType] = os.listdir(dirpath + '/' + nodeType)
                            lib_desc_dict[lib_desc] = nodeDictList
        full_lib_dict[asset] = lib_desc_dict
        return full_lib_dict

    def apply_dyn_lib(self, name, desc, parse_preset_str=False):
        # name is now namespace specific..
        _asset_name = '_'.join(name.split('_')[:-1])
        if os.environ['MAYA_VERSION'] < '2016':
            maya_doc_folder_name = os.environ['MAYA_VERSION'] + '-x64'
        else:
            maya_doc_folder_name = os.environ['MAYA_VERSION']
        docDir = os.getenv("HOME") + '/maya/' + maya_doc_folder_name + '/presets/attrPresets'
        getLibs = self.getLibByAssetName(_asset_name)
        mel_info_dict = {}
        if desc in getLibs[_asset_name].keys():
            libDict = getLibs[_asset_name][desc]
            for nodeType in libDict:
                if nodeType == 'nCloth_maps' or nodeType == 'nRigid_maps':
                    logger.info('found available {}'.format(nodeType))
                    for _map in libDict[nodeType]:
                        cmds.refresh()
                        logger.info('applying maps for', _map)
                        with open(self.attrLibBase + '/' + _asset_name + '/' + desc + '/' + nodeType + '/' + _map,
                                  'r') as map_file:
                            map_diction_string = map_file.read()
                        map_diction = ast.literal_eval(map_diction_string)
                        logger.info('dictionarized maps:'+map_diction)
                        nodeName = _map.split('.')[0]
                        # nodeSearch = cmds.ls(name+'*:'+nodeName)[0]
                        for nodeSearch in ns_depth_search(name, nodeName):
                            for map_diction_item in map_diction:
                                if map_diction[map_diction_item] != None:
                                    logger.info('currently applying attr:', map_diction_item, nodeSearch)
                                    cmds.setAttr(nodeSearch + '.' + map_diction_item, map_diction[map_diction_item],
                                                 type='doubleArray')
                elif nodeType == 'dyn_const_maps':
                    logger.info('found available {}'.format(nodeType))
                    for _map in libDict[nodeType]:
                        cmds.refresh()
                        logger.info('applying maps for', _map)
                        with open(self.attrLibBase + '/' + _asset_name + '/' + desc + '/' + nodeType + '/' + _map,
                                  'r') as map_file:
                            map_diction_string = map_file.read()
                        map_diction = ast.literal_eval(map_diction_string)
                        logger.info('dictionarized maps:'+map_diction)
                        nodeName = _map.split('.')[0]
                        # nodeSearch = cmds.ls(name+'*:'+nodeName)[0]
                        for nodeSearch in ns_depth_search(name, nodeName):
                            for map_diction_item in map_diction:
                                nComponent_get = cmds.listConnections(nodeSearch + '.' + map_diction_item)
                                if nComponent_get:

                                    for compo_attr in map_diction[map_diction_item]:
                                        logger.info('currently applying attr:', nodeName, nComponent_get, compo_attr)
                                        if 'PerVertex' in compo_attr and map_diction[map_diction_item][compo_attr]:
                                            cmds.setAttr(nComponent_get[0] + '.' + compo_attr,
                                                         map_diction[map_diction_item][compo_attr], type='doubleArray')
                                        elif 'MapType' in compo_attr:
                                            cmds.setAttr(nComponent_get[0] + '.' + compo_attr,
                                                         map_diction[map_diction_item][compo_attr])
                elif nodeType == 'mesh':
                    logger.info('reading json from mesh preset')
                    for json_dict in libDict[nodeType]:
                        logger.info('applying mesh json for ', json_dict)
                        with open(self.attrLibBase + '/' + _asset_name + '/' + desc + '/' + nodeType + '/' + json_dict,
                                  'r') as json_decode_f:
                            dict_read = decoder.decode(json_decode_f.read())
                        nodeName = json_dict.split('.')[0]
                        if cmds.ls(name + '*:' + nodeName) != []:
                            nodeSearch = cmds.ls(name + '*:' + nodeName)[0]
                            for atr in dict_read:
                                logger.info(atr, dict_read[atr])
                                try:
                                    cmds.setAttr(nodeSearch + '.' + atr, dict_read[atr])
                                except:
                                    logger.info(nodeSearch + '.' + atr, 'not settable')
                else:
                    for node in libDict[nodeType]:
                        cmds.refresh()
                        resolve_folder_errors(docDir + '/' + nodeType)
                        lib_node_mel_path = self.attrLibBase + '/' + _asset_name + '/' + desc + '/' + nodeType + '/' + node
                        temp_mel_read_dict = {}
                        temp_mel_read_dict['nodeType'] = nodeType
                        if parse_preset_str:
                            with open(lib_node_mel_path, 'r') as node_mel_file:
                                for line in node_mel_file:
                                    line_split = line.split(' ')
                                    if line_split[0] == 'blendAttr':
                                        temp_mel_read_dict[ast.literal_eval(line_split[1])] = ast.literal_eval(
                                            line_split[2][:-1])
                            mel_info_dict[node.split('.')[0]] = temp_mel_read_dict
                        else:
                            shutil.copyfile(lib_node_mel_path, docDir + '/' + nodeType + '/temp_attr_apply_' + node)
                            logger.info('Copied: ', lib_node_mel_path, docDir + '/' + nodeType + '/temp_attr_apply_' + node)
                            nodeName = node.split('.')[0]
                            nodeSearch = ns_depth_search(name, nodeName)
                            if nodeSearch != []:
                                cmds.cutKey(nodeSearch[0], cl=1)
                                if nodeType == 'blendShape':
                                    logger.info('DBG::BLENDSHAPE FLOOD: ', nodeSearch[0])
                                    flood_bs_weight(nodeSearch[0], 1)
                                attrApplyCmd = 'applyAttrPreset ' + nodeSearch[0] + ' "temp_attr_apply_' + node[
                                                                                                           :-4] + '" 1;'
                                logger.info(attrApplyCmd)
                                try:
                                    mel.eval(attrApplyCmd)
                                except:
                                    from functools import partial
                                    warn_inval_callbacks = partial(cmds.warning,
                                                                   'ERROR Running Mel for\n' + attrApplyCmd + '\nIgnore this warning if no issues found with respctive node.')
                                    cmds.evalDeferred(warn_inval_callbacks)
                                os.remove(docDir + '/' + nodeType + '/temp_attr_apply_' + node)
                            else:
                                logger.info(name + '*:' + nodeName,
                                      'is not found in the scene, preset application is skipped')
            if parse_preset_str:
                return mel_info_dict
        else:
            logger.info(name, ' has no available preset named: ', desc)

    def apply_preset_on_sel_nodes(self, name, desc):
        _asset_name = '_'.join(name.split('_')[:-1])
        getLibs = self.getLibByAssetName(_asset_name)
        obj_list = []
        targets = cmds.ls(sl=1)
        for obj in targets:
            objFullName = obj
            if cmds.listRelatives(objFullName, shapes=1) != None:
                if (cmds.nodeType(cmds.listRelatives(objFullName, shapes=1)[0]) == 'hairSystem' or
                        cmds.nodeType(cmds.listRelatives(objFullName, shapes=1)[0]) == 'nRigid' or
                        cmds.nodeType(cmds.listRelatives(objFullName, shapes=1)[0]) == 'follicle' or
                        cmds.nodeType(cmds.listRelatives(objFullName, shapes=1)[0]) == 'nCloth'):
                    obj = cmds.listRelatives(objFullName, shapes=1)[0]
            obj_list.append(obj)
        for node in obj_list:
            if cmds.nodeType(node) in getLibs[_asset_name][desc].keys():
                ''
