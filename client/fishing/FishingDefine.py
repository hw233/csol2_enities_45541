# -*- coding:gb18030 -*-

import math
import csconst

# fishing ground
FISHING_GROUND_HEIGHT = 14.0																# ��3D�����У��泡ƽ��ĸ߶�
FISHING_GROUND_CENTER_POS = (42.673370, FISHING_GROUND_HEIGHT, 46.970688)					# �泡����λ�ã���λ����

FISHING_GROUND_VIEW_SIZE = (32, 24)															# �泡�������ߴ磬��λ����
FISHING_GROUND_ACTUAL_SIZE = (csconst.FISHING_GROUND_LENGTH, csconst.FISHING_GROUND_WIDE)	# �泡ʵ�ʳߴ磬��λ����

# fishing camera
FISHING_CAMERA_UP_SIGHT_YPR = (math.pi, -math.pi / 2.001, 0)
FISHING_CAMERA_DOWN_SIGHT_YPR = (0, -math.pi / 2.001, 0)
FISHING_CAMERA_HEIGHT = 19.56

# fish

# cannon
CANNON_FIRE_INTERVAL_MIN = 0.25                 # ��С����������λ����
CANNON_DECLARE_DIRECTION_CHANGED_DELTA = 0.02   # ����ÿ�仯������ֵ�ʹ����ı�֪ͨ

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
