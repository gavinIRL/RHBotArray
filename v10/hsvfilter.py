import typing
# custom data structure to hold the state of an HSV filter


class HsvFilter:
    def __init__(self, hMin=None, sMin=None, vMin=None, hMax=None, sMax=None, vMax=None,
                 sAdd=None, sSub=None, vAdd=None, vSub=None):
        self.hMin = hMin
        self.sMin = sMin
        self.vMin = vMin
        self.hMax = hMax
        self.sMax = sMax
        self.vMax = vMax
        self.sAdd = sAdd
        self.sSub = sSub
        self.vAdd = vAdd
        self.vSub = vSub


# Putting this here out of the way as it's a chonk
# For a given item string case it will return the optimal filter and the correct position to look
def grab_object_preset(object_name=None, **kwargs) -> typing.Tuple[HsvFilter, list]:
    if object_name is None:
        #print("Using default filter")
        return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0), [3, 32, 1280, 794]
    if object_name == "dungeon_check":
        return HsvFilter(0, 73, 94, 106, 255, 255, 0, 0, 0, 0), [1083, 295, 1188, 368]
    if object_name == "enemy_map_loc":
        #print("Using enemy location filter")
        if kwargs.get("big_map"):
            return HsvFilter(0, 128, 82, 8, 255, 255, 0, 66, 30, 34), [485, 280, 900, 734]
        return HsvFilter(0, 128, 82, 8, 255, 255, 0, 66, 30, 34), [1100, 50, 1260, 210]
    if object_name == "player_map_loc":
        if kwargs.get("big_map"):
            return HsvFilter(31, 94, 86, 73, 255, 255, 0, 0, 0, 0), [485, 280, 900, 734]
        return HsvFilter(31, 94, 86, 73, 255, 255, 0, 0, 0, 0), [1100, 50, 1260, 210]
    if object_name == "other_player_map_loc":
        if kwargs.get("big_map"):
            return HsvFilter(16, 172, 194, 32, 255, 255, 0, 0, 70, 37), [485, 280, 900, 734]
        return HsvFilter(16, 172, 194, 32, 255, 255, 0, 0, 70, 37), [1100, 50, 1260, 210]
    if object_name == "loot_far":
        return HsvFilter(14, 116, 33, 32, 210, 59, 16, 0, 3, 0), [10, 145, 1084, 684]
    if object_name == "loot_near":
        return HsvFilter(0, 155, 135, 31, 240, 217, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "prompt_press_x_pickup":
        return HsvFilter(78, 110, 110, 97, 189, 255, 0, 0, 0, 0), [1080, 660, 1255, 725]
    if object_name == "message_section_cleared":
        return HsvFilter(0, 0, 214, 179, 65, 255, 0, 0, 0, 17), [464, 600, 855, 680]
    if object_name == "message_go":
        return HsvFilter(32, 114, 89, 58, 255, 255, 0, 12, 0, 0), [600, 222, 700, 275]
    if object_name == "enemy_nametag":
        return HsvFilter(49, 0, 139, 91, 30, 197, 0, 0, 40, 38), [10, 145, 1084, 684]
    if object_name == "message_boss_encounter":
        return HsvFilter(0, 92, 128, 13, 255, 255, 0, 0, 0, 0), [630, 520, 1120, 680]
    if object_name == "display_boss_name_and_healthbar":
        return HsvFilter(0, 92, 123, 29, 255, 255, 0, 0, 0, 20), [415, 533, 888, 700]
    if object_name == "loot_chest_normal":
        # This is a difficult one to separate
        return HsvFilter(0, 34, 38, 28, 152, 124, 0, 0, 5, 12), [10, 145, 1084, 684]
    if object_name == "map_outline":
        if kwargs.get("big_map"):
            return HsvFilter(0, 128, 82, 8, 255, 255, 0, 66, 30, 34), [485, 280, 900, 734]
        return HsvFilter(0, 128, 82, 8, 255, 255, 0, 66, 30, 34), [1100, 50, 1260, 210]
    if object_name == "gate_map_pos":
        # This is a very difficult one to separate
        if kwargs.get("big_map"):
            return HsvFilter(0, 128, 82, 8, 255, 255, 0, 66, 30, 34), [485, 280, 900, 734]
        return HsvFilter(0, 128, 82, 8, 255, 255, 0, 66, 30, 34), [1100, 50, 1260, 210]
    if object_name == "prompt_move_reward_screen":
        return HsvFilter(72, 98, 92, 105, 255, 225, 0, 54, 24, 38)
    if object_name == "prompt_select_card":
        return HsvFilter(79, 149, 140, 255, 255, 255, 0, 0, 0, 0)
    if object_name == "event_chest_special_appear":
        return HsvFilter(0, 124, 62, 88, 217, 246, 0, 0, 0, 0)
    if object_name == "inventory_green_item":
        return HsvFilter(37, 147, 0, 61, 255, 255, 0, 0, 0, 0)
    if object_name == "inventory_blue_item":
        return HsvFilter(79, 169, 0, 109, 246, 188, 0, 0, 0, 0)
    if object_name == "inventory_yellow_item":
        # This is a dangerous one as it can barely
        # distinguish against green items and vice versa
        return HsvFilter(19, 91, 107, 31, 168, 181, 0, 11, 32, 21)
    if object_name == "inventory_purple_item":
        return HsvFilter(126, 153, 0, 255, 255, 255, 0, 0, 0, 0)
    if object_name == "button_repair":
        return None, [208, 600]

    # These are all To be done later
    if object_name == "event_card_trade":
        return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0)
    if object_name == "event_otherworld":
        return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0)
    if object_name == "loot_chest_special":
        if kwargs.get("big_map"):
            return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0), [10, 145, 1084, 684]
        return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "cards":
        return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0), [735, 32, 1085, 100]
    if object_name == "enemy_arrow":
        return HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "healthbars":
        return HsvFilter(10, 86, 190, 28, 184, 255, 0, 0, 0, 50), [10, 145, 1084, 684]
    if object_name == "healthbarsv2":
        return HsvFilter(15, 116, 149, 64, 255, 255, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "tough_enemy_tag":
        return HsvFilter(0, 110, 0, 22, 255, 255, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "tough_enemy_tagv2":
        return HsvFilter(0, 131, 104, 13, 255, 226, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "otherplayertag":
        return HsvFilter(0, 110, 83, 121, 255, 255, 0, 0, 0, 0), [10, 145, 1084, 684]
    if object_name == "enemy_map_locv2":
        return HsvFilter(0, 132, 102, 14, 255, 255, 0, 0, 0, 0), [1100, 50, 1260, 210]
    if object_name == "enemy_map_locv3":
        return HsvFilter(0, 198, 163, 14, 255, 255, 0, 0, 0, 0), [1100, 50, 1260, 210]
    if object_name == "combo_count":
        return HsvFilter(99, 0, 63, 175, 190, 255, 0, 0, 0, 0), [1045, 235, 1190, 315]

    # Buttons for clicking, known positions
    if object_name == "button_explore_again":
        return None, []
    if object_name == "button_choose_map":
        return None, []
    if object_name == "button_open_store":
        return None, []
    if object_name == "button_go_town":
        return None, []
    if object_name == "button_inv_equipment":
        return None, []
    if object_name == "button_inv_consume":
        return None, []
    if object_name == "button_inv_other":
        return None, []
    if object_name == "button_repair_confirm":
        return None, []
    if object_name == "inv_grid_location":
        return None, [533+44*kwargs.get("col"), 277+44*kwargs.get("row")]
