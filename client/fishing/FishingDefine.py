# -*- coding:gb18030 -*-

import math
import csconst

# fishing ground
FISHING_GROUND_HEIGHT = 14.0																# 在3D坐标中，渔场平面的高度
FISHING_GROUND_CENTER_POS = (42.673370, FISHING_GROUND_HEIGHT, 46.970688)					# 渔场中心位置，单位：米

FISHING_GROUND_VIEW_SIZE = (32, 24)															# 渔场可视区尺寸，单位：米
FISHING_GROUND_ACTUAL_SIZE = (csconst.FISHING_GROUND_LENGTH, csconst.FISHING_GROUND_WIDE)	# 渔场实际尺寸，单位：米

# fishing camera
FISHING_CAMERA_UP_SIGHT_YPR = (math.pi, -math.pi / 2.001, 0)
FISHING_CAMERA_DOWN_SIGHT_YPR = (0, -math.pi / 2.001, 0)
FISHING_CAMERA_HEIGHT = 19.56

# fish

# cannon
CANNON_FIRE_INTERVAL_MIN = 0.25                 # 最小发射间隔，单位：秒
CANNON_DECLARE_DIRECTION_CHANGED_DELTA = 0.02   # 朝向每变化多少数值就触发改变通知

# cannonball
AUTO_BUY_AMOUNT = 10

# reward
REWARD_TYPE_COIN = 1
REWARD_TYPE_INGOT = 2

# config
FISH_DATA_PATH = "config/client/fishing/FishingFishes_client.xml"
CANNONBALL_DATA_PATH = "config/client/fishing/FishingBullets_client.xml"
MULTIPLE_CARD_DATA_PATH = "config/client/fishing/FishingItems_client.xml"
EFFECT_DATA_PATH = "config/client/fishing/FishingEffect_client.xml"
