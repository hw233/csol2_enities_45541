# -*- coding: gb18030 -*-

# $Id: Const.py,v 1.23 2008-08-11 08:38:12 huangdong Exp $


"""
locates client constants

2005.06.06 : tidied up by huangyongwei
"""
import csdefine
import ShareTexts
from config.client.msgboxtexts import Datas as mbmsgs
from CamerasMgr import WorldCamHandler
from CamerasMgr import FixWorldCamHandler
import cschannel_msgs

# --------------------------------------------------------------------
# about account
# --------------------------------------------------------------------
ACC_GUARD_WRONG_TIMES		= 3					# 允许密保卡输入错误多少次

# --------------------------------------------------------------------
# about role and team
# --------------------------------------------------------------------
ROLE_HEADERS = {}
ROLE_HEADERS[csdefine.CLASS_FIGHTER]			= { csdefine.GENDER_MALE : "maps/role_headers/nan_zhan_shi.dds", csdefine.GENDER_FEMALE : "maps/role_headers/nv_zhan_shi.dds" }
ROLE_HEADERS[csdefine.CLASS_SWORDMAN]			= { csdefine.GENDER_MALE : "maps/role_headers/nan_jian_ke.dds", csdefine.GENDER_FEMALE : "maps/role_headers/nv_jian_ke.dds" }
ROLE_HEADERS[csdefine.CLASS_ARCHER]				= { csdefine.GENDER_MALE : "maps/role_headers/nan_she_shou.dds", csdefine.GENDER_FEMALE : "maps/role_headers/nv_she_shou.dds" }
ROLE_HEADERS[csdefine.CLASS_MAGE]				= { csdefine.GENDER_MALE : "maps/role_headers/nan_fa_shi.dds", csdefine.GENDER_FEMALE : "maps/role_headers/nv_fa_shi.dds" }


# --------------------------------------------------------------------
# about loading ground
# --------------------------------------------------------------------
LOADING_BACK_GROUND = {}
LOADING_BACK_GROUND[csdefine.CLASS_FIGHTER]		= { csdefine.GENDER_MALE : "maps/loading_grounds/jlnanz.dds", csdefine.GENDER_FEMALE : "maps/loading_grounds/jlnvz.dds" }
LOADING_BACK_GROUND[csdefine.CLASS_SWORDMAN]	= { csdefine.GENDER_MALE : "maps/loading_grounds/yhnanj.dds", csdefine.GENDER_FEMALE : "maps/loading_grounds/yhnvj.dds" }
LOADING_BACK_GROUND[csdefine.CLASS_ARCHER]		= { csdefine.GENDER_MALE : "maps/loading_grounds/yhnang.dds", csdefine.GENDER_FEMALE : "maps/loading_grounds/yhnvg.dds" }
LOADING_BACK_GROUND[csdefine.CLASS_MAGE]		= { csdefine.GENDER_MALE : "maps/loading_grounds/fmnanf.dds", csdefine.GENDER_FEMALE : "maps/loading_grounds/fmnvf.dds" }


# --------------------------------------------------------------------
# about pet
# --------------------------------------------------------------------
pet_ch_characters = {}
pet_ch_characters[csdefine.PET_CHARACTER_SUREFOOTED]	= ShareTexts.PET_CHARACTER_SUREFOOTED
pet_ch_characters[csdefine.PET_CHARACTER_CLOVER]		= ShareTexts.PET_CHARACTER_CLOVER
pet_ch_characters[csdefine.PET_CHARACTER_CANNILY]		= ShareTexts.PET_CHARACTER_CANNILY
pet_ch_characters[csdefine.PET_CHARACTER_BRAVE]			= ShareTexts.PET_CHARACTER_BRAVE
pet_ch_characters[csdefine.PET_CHARACTER_LIVELY]		= ShareTexts.PET_CHARACTER_LIVELY

pet_ch_action_modes = {}
pet_ch_action_modes[csdefine.PET_ACTION_MODE_FOLLOW]	= ShareTexts.PET_ACTION_MODE_FOLLOW
pet_ch_action_modes[csdefine.PET_ACTION_MODE_KEEPING]	= ShareTexts.PET_ACTION_MODE_KEEPING

pet_ch_tussle_modes = {}
pet_ch_tussle_modes[csdefine.PET_TUSSLE_MODE_ACTIVE]	= ShareTexts.PET_TUSSLE_MODE_ACTIVE
pet_ch_tussle_modes[csdefine.PET_TUSSLE_MODE_PASSIVE]	= ShareTexts.PET_TUSSLE_MODE_PASSIVE
pet_ch_tussle_modes[csdefine.PET_TUSSLE_MODE_GUARD]		= ShareTexts.PET_TUSSLE_MODE_GUARD

# --------------------------------------------------------------------
# about tong
# --------------------------------------------------------------------
TONG_GRADE_MAPPING = {}
TONG_GRADE_MAPPING[csdefine.TONG_DUTY_CHIEF]				= ShareTexts.TONG_GRADE_CHIEF
TONG_GRADE_MAPPING[csdefine.TONG_DUTY_DEPUTY_CHIEF]			= ShareTexts.TONG_GRADE_CHIEF_SUBALTERN
TONG_GRADE_MAPPING[csdefine.TONG_DUTY_TONG]					= ShareTexts.TONG_GRADE_TONG
TONG_GRADE_MAPPING[csdefine.TONG_DUTY_MEMBER]				= ShareTexts.TONG_GRADE_MEMBER
TONG_GRADE_MAPPING[0]										= ShareTexts.TONG_GRADE_MEMBER

ATTACK_STATE_NONE					= 0			# 无攻击状态
ATTACK_STATE_AUTO_FIGHT				= 1			# 自动战斗攻击状态
ATTACK_STATE_ONCE					= 2			# 使用技能攻击一次状态
ATTACK_STATE_NORMAL					= 3			# 使用普通物理技能攻击状态
ATTACK_STATE_AUTO_SPELL				= 4			# 使用指定技能后并与普通物理攻击循环使用状态
ATTACK_STATE_AUTO_CONFIRM_SPELL		= 5			# 使用指定技能后一直使用普通物理攻击状态
ATTACK_STATE_HOMING_SPELL			= 6			# 使用引导连续攻击状态
ATTACK_STATE_AUTO_SPELL_HOMING		= 7			# 使用指定技能后并与引导连续攻击循环使用状态
ATTACK_STATE_SPELL_AND_HOMING		= 8			# 使用指定技能后一直使用引导连续攻击状态
ATTACK_STATE_AUTO_SPELL_CURSOR		= 9			# 使用指定技能后使用鼠标为位置攻击状态

AUTO_FIGHT_ENERGY_NEED				= 60		# 自动战斗开始所需的最小精力值
AUTO_RESTORE_DETECT_INTERVAL		= 2			# 秒，自动恢复的timer间隔

AUTO_FIGHT_DETECT					= 0.8		# 秒，自动战斗每次检测的间隔
AUTO_ATTACK_DELAY_AMEND				= 0.3		# 秒，每次攻击的间隔修正
AUTO_PICK_UP_DISTANCE				= 30.0		# 自动拾取范围
AUTO_PICK_UP_DELAY					= 1.5		# 秒，自动拾取两个物品间隔时间
AUTO_PICK_UP_START_DELAY			= 0.5		# 从脱离战斗到自动捡取开始延时
AUTO_ATTACK_RANGE					= 30.0		# 自动战斗搜寻攻击目标的半径

AUTO_FIGHT_PERSISTENT_TIME			= 1800.0	# 每一次开始自动战斗持续时间
AUTO_FIGHT_PERSISTENT_TIME_TW		= 28800.0	# 台湾版自动战斗持续时间（8小时）
AUTO_FIGHT_REPAIR_ITEM_ID				= 110103045		# 自动修理用物品ID
AUTO_FIGHT_REBOIN_ITEM_ID				= 110103001	# 自动复活用物品ID

DANGER_MP							= 0.10      # 危险魔法量百分比
DANGER_HP							= 0.10      # 危险血量百分比
# --------------------------------------------------------------------
# 能够最终的任务类型
# --------------------------------------------------------------------
TRACE_QUEST_TYPE = [
	csdefine.QUEST_OBJECTIVE_KILL, \
	csdefine.QUEST_OBJECTIVE_DELIVER, \
	csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER, \
	csdefine.QUEST_OBJECTIVE_KILL_WITH_PET, \
	csdefine.QUEST_OBJECTIVE_EVOLUTION,\
	csdefine.QUEST_OBJECTIVE_TALK,\
	csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE,\
	csdefine.QUEST_OBJECTIVE_DELIVER_PET,
	csdefine.QUEST_OBJECTIVE_ENTER_SPCACE,
	]											# 追踪的任务类型


# --------------------------------------------------------------------
# 显示 NPC 头顶名字的范围
# --------------------------------------------------------------------
SHOW_NPCNAME_RANGE					= 100.0

TEAM_FOLLOW_REQUEST_VALIDITY		= 20	# 秒，跟随邀请的有效期
TEAM_FOLLOW_START_DISTANCE			= 0.8	# 米，跟随邀请开始时移动到离队长身边的距离
TEAM_FOLLOW_DETECT_INTERVAL			= 0.2	# 秒，跟随侦测时间间隔
TEAM_FOLLOW_BEHIND_DISTANCE			= 3.0	# 米，跟随邀请开始时移动到离队长身边的距离
TEAM_FOLLOW_WAIT_TIEM				= 8		# 秒，2秒内找不到队长则推出跟随

ROLE_FOLLOW_MAX_DISTANCE = 20.0		 #玩家发起跟随的最大距离
ROLE_FOLLOW_NEAR_DISTANCE = 1.5            #玩家移动到离跟随目标身边的距离
# --------------------------------------------------------------------
# NPC用武器自发光强化等级默认为7
# --------------------------------------------------------------------
NPC_SHINE_INTENSIFY					= 7

"""
职位	1级帮会	2级帮会	3级帮会	4级帮会	5级帮会
帮主日工资	20000	30000	40000	50000	60000
副帮主日工资	10000	20000	30000	40000	50000
"""
TONG_CHIEF_WAGE = {
	"right" :
	{ 1 : 20000,	2 : 30000,	3 : 40000,	4 : 50000,	5 : 60000, },
	"left" :
	{ 1 : 10000,	2 : 20000,	3 : 30000,	4 : 40000,	5 : 50000, },
	}

# 帮会资金下限和上限
TONG_MONEY_LIMIT = {
	1 : ( 100000, 5000000 ),
	2 : ( 1000000, 10000000 ),
	3 : ( 2000000, 20000000 ),
	4 : ( 2500000, 25000000 ),
	5 : ( 3000000, 9999999999 ),
}
# 帮会权限、帮会职务
TONG_DUTY_NAME = {
	 csdefine.TONG_DUTY_CHIEF 					:	cschannel_msgs.TONG_ZHIYE_BANG_ZHU ,
	 csdefine.TONG_DUTY_DEPUTY_CHIEF			:	cschannel_msgs.TONG_ZHIYE_FU_BANG_ZHU ,
	 csdefine.TONG_DUTY_TONG 					:	cschannel_msgs.TONG_ZHIYE_TANG_ZHU ,
	 csdefine.TONG_DUTY_MEMBER  				:	cschannel_msgs.TONG_ZHIYE_LOU_LUO ,
}

PET_PASSTIVE_SKILL_FLY_TIME		= 0.5	# 宠物被动技能提示时间间隔


# 申请入帮时间间隔限制
JOIN_TONG_REQUEST_LIMIT_INTERVAL = 1200

# --------------------------------------------------------------------
# 法师脚底光圈粒子路径
# --------------------------------------------------------------------
CLASS_MAGE_USE_PARTICLE = "particles/huan_new1.xml"

# --------------------------------------------------------------------
# 创建角色时候角色模型数据
# --------------------------------------------------------------------
ROLE_CREATE_EQUIP_MAP = {
	csdefine.CLASS_FIGHTER		: [ 3040080, 3050080, 3060080, 3070080, 5290039, 0 ],		# 战士
	csdefine.CLASS_SWORDMAN		: [ 1040040, 1050040, 1060040, 1070040, 5271000, 0 ],			# 剑客
	csdefine.CLASS_ARCHER		: [ 2040080, 2050080, 2060080, 2070080, 0, 5130045 ],			# 射手
	csdefine.CLASS_MAGE		: [ 4040080, 4050080, 4060080, 4070080, 5120245, 0 ],			# 法师
	}

# --------------------------------------------------------------------
# 默认装备编号合集
# --------------------------------------------------------------------
# 默认脸型编号
ROLE_EQUIP_FACE_MAP = {
	csdefine.CLASS_SWORDMAN | csdefine.GENDER_MALE 		:	1000000,
	csdefine.CLASS_SWORDMAN | csdefine.GENDER_FEMALE	:	1000004,
	csdefine.CLASS_ARCHER | csdefine.GENDER_MALE 	 	:	2000000,
	csdefine.CLASS_ARCHER | csdefine.GENDER_FEMALE	 	:	2000004,
	csdefine.CLASS_FIGHTER | csdefine.GENDER_MALE 	 	:	3000000,
	csdefine.CLASS_FIGHTER | csdefine.GENDER_FEMALE	 	:	3000004,
	csdefine.CLASS_MAGE | csdefine.GENDER_MALE 		 	:	4000000,
	csdefine.CLASS_MAGE | csdefine.GENDER_FEMALE	 	:	4000004,
	}

# 默认发型编号
ROLE_EQUIP_HAIR_MAP = {
	csdefine.CLASS_SWORDMAN | csdefine.GENDER_MALE 		:	1010000,
	csdefine.CLASS_SWORDMAN | csdefine.GENDER_FEMALE	:	1010004,
	csdefine.CLASS_ARCHER | csdefine.GENDER_MALE 	 	:	2010000,
	csdefine.CLASS_ARCHER | csdefine.GENDER_FEMALE	 	:	2010004,
	csdefine.CLASS_FIGHTER | csdefine.GENDER_MALE 	 	:	3010000,
	csdefine.CLASS_FIGHTER | csdefine.GENDER_FEMALE	 	:	3010004,
	csdefine.CLASS_MAGE | csdefine.GENDER_MALE 		 	:	4010000,
	csdefine.CLASS_MAGE | csdefine.GENDER_FEMALE	 	:	4010004,
	}

# 默认身体编号
ROLE_EQUIP_VOLA_MAP = {
	csdefine.CLASS_SWORDMAN :	1050000,
	csdefine.CLASS_ARCHER 	:	2050000,
	csdefine.CLASS_FIGHTER 	:	3050000,
	csdefine.CLASS_MAGE 	:	4050000,
	}

# 默认下身编号
ROLE_EQUIP_BODY_MAP = {
	csdefine.CLASS_SWORDMAN :	1040000,
	csdefine.CLASS_ARCHER 	:	2040000,
	csdefine.CLASS_FIGHTER 	:	3040000,
	csdefine.CLASS_MAGE 	:	4040000,
	}

# 默认手套编号
ROLE_EQUIP_BREE_MAP = {
	csdefine.CLASS_SWORDMAN :	1060000,
	csdefine.CLASS_ARCHER 	:	2060000,
	csdefine.CLASS_FIGHTER 	:	3060000,
	csdefine.CLASS_MAGE 	:	4060000,
	}

# 默认鞋子编号
ROLE_EQUIP_TINT_MAP = {
	csdefine.CLASS_SWORDMAN :	5,
	csdefine.CLASS_ARCHER 	:	3,
	csdefine.CLASS_FIGHTER 	:	4,
	csdefine.CLASS_MAGE 	:	2,
	}

# --------------------------------------------------------------------
# 装备发光等级定义
# --------------------------------------------------------------------
EQUIP_WEAPON_FLOW_LEVEL		= 5			# 武器流光出现强化等级
EQUIP_ARMOR_FLOW_LEVEL		= 4			# 防具流光出现强化等级
EQUIP_WEAPON_GLOW_LEVEL		= 5			# 武器自发光出现强化等级

# --------------------------------------------------------------------
# 法宝目标点
# --------------------------------------------------------------------
TALISMAN_TARGET_HP			= "HP_right_shoulder"
TALISMAN_ADD_LIFE_TIME 		= 2592000		# 女娲石充值时间（秒）/（30天）

# --------------------------------------------------------------------
# 装备强化数值显示颜色
# --------------------------------------------------------------------
EQUIP_INTENSIFY_COLOR = ( 255, 192, 0 )

# --------------------------------------------------------------------
# 刀光
# --------------------------------------------------------------------
LOFT_FIGHTER_HP			= "HP_sfx2"
LOFT_FIGHTER			= "particles/loft/loft2.xml"
LOFT_SWORDMAN_HP		= "HP_sfx1"
LOFT_SWORDMAN			= "particles/loft/loft4.xml"

# --------------------------------------------------------------------
# 创建角色画面光效表现
# --------------------------------------------------------------------
ROLE_CREATE_MAGE_HP			= ["HP_sfx1"]
ROLE_CREATE_MAGE_PATH		= ["particles/fazhang.xml"]
ROLE_EQUIP_FEET_MAP = {
	csdefine.CLASS_SWORDMAN :	1070000,
	csdefine.CLASS_ARCHER 	:	2070000,
	csdefine.CLASS_FIGHTER 	:	3070000,
	csdefine.CLASS_MAGE 	:	4070000,
	}

#创建角色场景摄像机最大拉伸值
ROLE_CREATE_MAX_DISTACE = 7.68

# --------------------------------------------------------------------
# 职业对应dye
# --------------------------------------------------------------------
ROLE_CREATE_EFFECT_MAGE 	= [
	( 1.45, 0.15, "HP_magic_l", "particles/fashishou.xml" ),
	( 1.9, 1.5, "HP_root", "particles/fashishen.xml" ),
	( 3, 1.6, "HP_root", "particles/fashishen2.xml" ),
	( 0.8, 0.15, "HP_magic_l", "particles/fashiqiu.xml" ),
	( 2, 1.6, "HP_root", "particles/fashidi.xml" ),
	]

ROLE_CREATE_SWORDMAN_HP		= ["HP_sfx2"]
ROLE_CREATE_SWORDMAN_PATH	= ["particles/zhujue_jianeffect.xml"]
ROLE_CREATE_EFFECT_SWORDMAN = [
	( 0, 0.6, "HP_hitPoint", "particles/jianke_sf_1.xml" ),
	( 0, 0.6, "HP_magic_l", "particles/jianke_sf_2.xml" ),
	( 0, 0.8, "HP_magic_r", "particles/jianke_sf_2.xml" ),
	( 0.5, 2, "HP_root", "particles/jianke_sf_3.xml" ),
	( 0.7, 2, "HP_body", "particles/jianke_sf_4.xml" ),
	( 1.75, 2, "HP_root", "particles/jianke_sf_5.xml" ),
	]

ROLE_CREATE_ARCHER_HP		= ["HP_sfx1", "HP_sfx2"]
ROLE_CREATE_ARCHER_PATH		= ["particles/gongjianyan.xml", "particles/gongjianyan.xml"]
ROLE_CREATE_EFFECT_ARCHER 	= [
	( 2.2, 1.60, "HP_root", "particles/gongjianshen.xml" ),
	( 3.1, 0.15, "HP_magic_l", "particles/gongjianquan.xml" ),
	( 0.6, 1, "HP_body", "particles/gongjian1.xml" ),
	( 0.2, 0.5, "HP_magic_l", "particles/gongjianshou2.xml" ),
	( 1.6, 1.6, "HP_body", "particles/gongjiandian.xml" ),
	( 1.5, 0.6, "HP_magic_l", "particles/gongshou2.xml" ),
	( 1.0, 1.6, "HP_root", "particles/gongjiantiao.xml" ),
	( 2.2, 1, "HP_body", "particles/gongjianshe.xml" ),
	]

ROLE_CREATE_FIGHTER_HP		= ["HP_sfx1"]
ROLE_CREATE_FIGHTER_PATH	= ["particles/weapon_1_9.xml"]
ROLE_CREATE_EFFECT_FIGHTER 	= [
	( 0.7, 2, "HP_root", "particles/zs_k_1.xml" ),
	( 1.25, 2, "HP_hitPoint", "particles/zs_k_2.xml" ),
	( 1.7, 2, "HP_root", "particles/zs_k_3.xml" ),
	]

ROLE_CREATE_EFFECT_CLASS_MAP = {
	csdefine.CLASS_FIGHTER		: ROLE_CREATE_EFFECT_FIGHTER,
	csdefine.CLASS_SWORDMAN		: ROLE_CREATE_EFFECT_SWORDMAN,
	csdefine.CLASS_ARCHER		: ROLE_CREATE_EFFECT_ARCHER,
	csdefine.CLASS_MAGE			: ROLE_CREATE_EFFECT_MAGE,
	}

CC_FUBENNAME_DONOT_CONVERT_LIST = ["fu_ben_bang_hui_ling_di","fu_ben_xin_shou_cun"]

#死亡模型
ROLE_DEAD_HP					= "HP_hitPoint"
# --------------------------------------------------------------------
# 飞翔传送
# --------------------------------------------------------------------
TELEPORT_HP						= "HP_hip_01"
TELEPORT_HIP					= "hip_01"
TELEPORT_MODELNUM				= "gw4006_1"
# 降落光效
TELEPORT_VEHICLE_HP 			= "HP_root"
TELEPORT_VEHICLE_PARTICLE 		= "particles/flydown.xml"

#摄像机相对于不同角色类型的绑定点的偏移量
CAMERA_PROVITE_OFFSET_TO_ROLE = {
	csdefine.CLASS_FIGHTER		: ( 0.0, 1.8, 0.0 ),
	csdefine.CLASS_SWORDMAN		: ( 0.0, 1.8, 0.0 ),
	csdefine.CLASS_ARCHER		: ( 0.0, 1.8, 0.0 ),
	csdefine.CLASS_MAGE			: ( 0.0, 2.3, 0.0 )
}

CAMERA_PROVITE_OFFSET_TO_SLAVEDART		= ( 0.0, 2.3, 0.0 )
CAMERA_MIN_DISTANCE_TO_SLAVEDART		= 3.0
CAMERA_MIN_DISTANCE_TO_VEHICLE			= 3.0
CAMERA_MIN_DISTANCE_TO_STAND_VEHICLE	= 5.0

BENIFIT_PERIOD		=	5 * 3600		# 单位：秒。玩家累计在线时间达到，可获得奖励

# 摄像机控制模式
CAMERA_CONTROL_MOD_1 = 1
CAMERA_CONTROL_MOD_2 = 2
CAMERA_CONTROL_SHAKE_ACCEPT_X = 0.1
CAMERA_CONTROL_SHAKE_ACCEPT_Y = 0.1

# --------------------------------------------------------------------
# 头发动画
# --------------------------------------------------------------------
HAIR_ACTION_1 		= "hair_bone_1"
HAIR_ACTION_2 		= "hair_bone_2"


# --------------------------------------------------------------------
# 骑宠动作对应玩家动作表
# --------------------------------------------------------------------
VEHICLE_ACTION_MAPS = {	"walk" 			: [("ride_walk", "crossleg_walk","float_walk"), ("ride_walk_weapon", "crossleg_walk_weapon","float_walk_weapon"), ("ride_walk_weapon_dan", "crossleg_walk_weapon_dan","float_walk_weapon_dan"),\
										("ride_walk_weapon_shuang", "crossleg_walk_weapon_shuang","float_walk_weapon_shuang"), ("ride_walk_weapon_fu", "crossleg_walk_weapon_fu","float_walk_weapon_fu"),\
										("ride_walk_weapon_chang", "crossleg_walk_weapon_chang","float_walk_weapon_chang")],
						"run" 			: [("ride_run", "crossleg_run","float_run"), ("ride_run_weapon", "crossleg_run_weapon","float_run_weapon"), ("ride_run_weapon_dan", "crossleg_run_weapon_dan","float_run_weapon_dan"),\
										("ride_run_weapon_shuang", "crossleg_run_weapon_shuang","float_run_weapon_shuang"), ("ride_run_weapon_fu", "crossleg_run_weapon_fu","float_run_weapon_fu"),\
										("ride_run_weapon_chang", "crossleg_run_weapon_chang","float_run_weapon_chang")],
						"stand" 		: [("ride_stand", "crossleg_stand","float_stand"), ("ride_stand_weapon", "crossleg_stand_weapon","float_stand_weapon"), ("ride_stand_weapon_dan", "crossleg_stand_weapon_dan","float_stand_weapon_dan"),\
										("ride_stand_weapon_shuang", "crossleg_stand_weapon_shuang","float_stand_weapon_shuang"), ("ride_stand_weapon_fu", "crossleg_stand_weapon_fu","float_stand_weapon_fu"),\
										("ride_stand_weapon_chang", "crossleg_stand_weapon_chang","float_stand_weapon_chang")],
						"jump_begin" 	: [("ride_jump_begin", "crossleg_jump_begin","float_stand"), ("ride_jump_begin_weapon", "crossleg_jump_begin_weapon","float_stand_weapon"),\
										("ride_jump_begin_weapon_dan", "crossleg_jump_begin_weapon_dan","float_stand_weapon_dan"), ("ride_jump_begin_weapon_shuang", "crossleg_jump_begin_weapon_shuang","float_stand_weapon_shuang"),\
										("ride_jump_begin_weapon_fu", "crossleg_jump_begin_weapon_fu","float_stand_weapon_fu"), ("ride_jump_begin_weapon_chang", "crossleg_jump_begin_weapon_chang","float_stand_weapon_chang")],
						"jump_process" 	: [("ride_jump_process", "crossleg_jump_process","float_stand"), ("ride_jump_process_weapon", "crossleg_jump_process_weapon","float_stand_weapon"),\
										("ride_jump_process_weapon_dan", "crossleg_jump_process_weapon_dan","float_stand_weapon_dan"), ("ride_jump_process_weapon_shuang", "crossleg_jump_process_weapon_shuang","float_stand_weapon_shuang"),\
										("ride_jump_process_weapon_fu", "crossleg_jump_process_weapon_fu","float_stand_weapon_fu"), ("ride_jump_process_weapon", "crossleg_jump_process_weapon","float_stand_weapon")],
						"jump_end" 		: [("ride_jump_end", "crossleg_jump_end","float_stand"), ("ride_jump_end_weapon", "crossleg_jump_end_weapon","float_stand_weapon"),\
										("ride_jump_end_weapon_dan", "crossleg_jump_end_weapon_dan","float_stand_weapon_dan"), ("ride_jump_end_weapon_shuang", "crossleg_jump_end_weapon_shuang","float_stand_weapon_shuang"),\
										("ride_jump_end_weapon_fu", "crossleg_jump_end_weapon_fu","float_stand_weapon_fu"), ("ride_jump_end_weapon_chang", "crossleg_jump_end_weapon_chang","float_stand_weapon_chang")],
						"float_up" 		: [("float_up", "float_up","float_up"), ("float_up", "float_up","float_up"), ("float_up_dan", "float_up_dan","float_up_dan"), ("float_up_shuang", "float_up_shuang","float_up_shuang"),\
										("float_up_fu", "float_up_fu","float_up_fu"), ("float_up_chang", "float_up_chang","float_up_chang")],
						}

VEHICLE_RANDOM_ACTION_MAPS = {
						"run" 			: [([], [],["float_run_random1","float_run_random2"]), ([], [],["float_run_random1","float_run_random2"]), ([], [],["float_run_random1_dan","float_run_random2_dan"]),\
										([], [],["float_run_random1_shuang","float_run_random2_shuang"]), ([], [],["float_run_random1_fu","float_run_random2_fu"]), ([], [],["float_run_random1_chang","float_run_random2_chang"])],
						"stand" 		: [(["ride_random1"], ["crossleg_random1"],["float_stand_random"]), (["ride_random1_weapon"], ["crossleg_random1_weapon"],["float_stand_random"]),\
										(["ride_random1_weapon_dan"], ["crossleg_random1_weapon_dan"],["float_stand_random_dan"]), (["ride_random1_weapon_shuang"], ["crossleg_random1_weapon_shuang"],["float_stand_random_shuang"]),\
										(["ride_random1_weapon_fu"], ["crossleg_random1_weapon_fu"],["float_stand_random_fu"]), (["ride_random1_weapon_chang"], ["crossleg_random1_weapon_chang"],["float_stand_random_chang"])],
						}


VEHICLE_CONJURE_PARTICLE 	= "particles/bianshen_sf.xml"
VEHICLE_CONJURE_HP			= "HP_root"

#-------------排名系统
LEVELRANKING			=	1		# 玩家等级排行
MONEYRANKING			=	2		# 玩家金钱排行
TONGRANKING				=	3		# 帮会排行
FAMILYRANKING			=	4		# 家族排行
PFRANKING				=	5		# PK排行榜

# --------------------------------------------------------------------
# 新单人坐骑
# --------------------------------------------------------------------
# 坐骑绑定点
VEHICLE_HIP				= "hip_01"		# 跨腿
VEHICLE_HIP_HP			= "HP_hip_01"	# 跨腿
VEHICLE_PAN				= "pan_01"		# 盘腿
VEHICLE_PAN_HP			= "HP_pan_01"	# 盘腿
VEHICLE_STAND			= "stand_01"	# 浮空
VEHICLE_STAND_HP		= "HP_stand_01"	# 浮空

# --------------------------------------------------------------------
# 装备固定点
# --------------------------------------------------------------------
MODEL_HAIR_HP			= "HP_head"			# 头发
MODEL_RIGHT_HAND_HP		= "HP_right_hand"	# 右手
MODEL_LEFT_HAND_HP		= "HP_left_hand"	# 左手1
MODEL_LEFT_SHIELD_HP	= "HP_left_shield"	# 左手2

# --------------------------------------------------------------------
# 头发动作
# --------------------------------------------------------------------
HAIR_MODEL_ACTION1 		= "hair_bone_1"		# 头发动作1（轻微）
HAIR_MODEL_ACTION2 		= "hair_bone_2"		# 头发动作1（剧烈）

# --------------------------------------------------------------------
# 挖宝锄头
# --------------------------------------------------------------------
CHUTOU_MODEL_PATH		= "weapon/zb_chu_gao_001/zb_chu_gao_001.model"

# --------------------------------------------------------------------
# 伤害统计
# --------------------------------------------------------------------
STA_BROADCAST_INTERVAL	= 1.0	# 伤害统计每条信息输出间隔时间，聊天频道做了1秒的时间限制

# --------------------------------------------------------------------
# 物品使用二次确认及其相应提示信息 by姜毅
# --------------------------------------------------------------------
INFO_PET_REBOIN	=	mbmsgs[0x00c1]		# 你确定要将正在出战的宠物进行还童操作么？
INFO_PET_FORGET	=	mbmsgs[0x00c2]		# 使用忘忧丹会让你的宠物遗忘所有技能，真的要这样做么？
INFO_POTENTIAL_BOOK	=	mbmsgs[0x00c3]
INFO_PET_SUPER_REBOIN	= mbmsgs[0x00c4] 	#使用超级还童丹提示
INFO_PET_SUPER_WASH = mbmsgs[0x00cb] #使用超级洗髓丹提示
INFO_FORGET_SKILL_ITEM = mbmsgs[0x00c5] # 北冥炉
INFO_REPAIR_ITEM = mbmsgs[0x00c6] # 天工槌
INFO_AF_TIME_PLUS1 = mbmsgs[0x00c8] # 司辰沙漏
INFO_AF_TIME_PLUS2 = mbmsgs[0x00c9] # 司辰沙漏 再充值
INFO_AF_TIME_PLUS = [INFO_AF_TIME_PLUS1, INFO_AF_TIME_PLUS2]
# INFO_AF_TIME_PLUS[BigWorld.player().af_time_extra > 0]

SECOND_QUEST_ITEM_AND_INFO 	=	{
									60201002 : INFO_PET_REBOIN,
									60201008 : INFO_PET_REBOIN,
									60201003 : INFO_PET_REBOIN,
									60201055 : INFO_PET_SUPER_REBOIN,
									60201005 : INFO_PET_FORGET,
									60201056 : INFO_PET_SUPER_WASH,
									60101111 : INFO_POTENTIAL_BOOK,
									60101112 : INFO_POTENTIAL_BOOK,
									60101113 : INFO_POTENTIAL_BOOK,
									110103044 : INFO_FORGET_SKILL_ITEM,
									110103045 : INFO_REPAIR_ITEM,
									110103046 : INFO_AF_TIME_PLUS1,
									}

# --------------------------------------------------------------------
# 禁止使用收费药品地图副本 by姜毅
# --------------------------------------------------------------------
SPACE_FORBIT_AUTO_DRUG	=	[csdefine.SPACE_TYPE_TONG_ABA]


# --------------------------------------------------------------------
# 默认物品图标编号
# --------------------------------------------------------------------
ITEM_DEFAULT_ICON 	= "tb_yw_sj_005"

# --------------------------------------------------------------------
# pk
# --------------------------------------------------------------------
PK_MODEL_MSG_MAPS = {	csdefine.PK_CONTROL_PROTECT_PEACE		: ShareTexts.PK_CONTROL_PROTECT_PEACE,
						csdefine.PK_CONTROL_PROTECT_TEAMMATE	: ShareTexts.PK_CONTROL_PROTECT_TEAMMATE,
						csdefine.PK_CONTROL_PROTECT_KIN			: ShareTexts.PK_CONTROL_PROTECT_KIN,
						csdefine.PK_CONTROL_PROTECT_TONG		: ShareTexts.PK_CONTROL_PROTECT_TONG,
						csdefine.PK_CONTROL_PROTECT_NONE		: ShareTexts.PK_CONTROL_PROTECT_NONE,
						csdefine.PK_CONTROL_PROTECT_RIGHTFUL	: ShareTexts.PK_CONTROL_PROTECT_RIGHTFUL,
						csdefine.PK_CONTROL_PROTECT_JUSTICE		: ShareTexts.PK_CONTROL_PROTECT_JUSTICE,
						}

# --------------------------------------------------------------------
# 切磋旗子模型路径
# --------------------------------------------------------------------
QIECUO_QIZI_MODEL_PATH	= "space/chang_jing_wu_jian/wu_jian/ty_jue_dou_qi_zi.model"

# --------------------------------------------------------------------
# 赛马模型路径
# --------------------------------------------------------------------
HORSERACE_MODEL_PATH	= "mount/gw0700/gw0700.model"
HORSERACE_CHRISTMAS_MODEL_NUMBER	= "gw1280_1"
import Language
if Language.LANG == Language.LANG_BIG5:
	HORSERACE_CHRISTMAS_MODEL_NUMBER	= "gw1280_2"
HORSERACE_MODEL_HP		= "HP_hip_01"
HORSERACE_MODEL_HIP		= "hip_01"
# --------------------------------------------------------------------
# 摆摊模型编号
# --------------------------------------------------------------------
VEND_MODELNUM = {}
VEND_MODELNUM[ csdefine.GENDER_MALE ] 	= "gw0108_1"
VEND_MODELNUM[ csdefine.GENDER_FEMALE ] = "gw0109_1"

# --------------------------------------------------------------------
# 钓鱼模型路径
# --------------------------------------------------------------------
FISHING_MODEL_PATH	= "weapon/zb_yu_gan_001/zb_yu_gan_001.model"
FISHING_MODEL_HP	= "HP_right_hand"

# --------------------------------------------------------------------
# 空模型
# --------------------------------------------------------------------
EMPTY_MODEL_PATH = "particles/gxcone.model"
EMPTY_MODEL_PATH_1 = "particles/gxcone1.model"

# --------------------------------------------------------------------
# 烟花
# --------------------------------------------------------------------
YANHUA_START_HP		= "HP_right_hand"
YANHUA_END_HP		= "HP_root"
YANHUA_SHE_PATH		= "particles/jieri_009.xml"

# -------------------------------------------------------------
# 二代宠物模型编号固定附加
# -------------------------------------------------------------
PET_ATTACH_MODELNUM				= "f"

# -------------------------------------------------------------
# 升级相关
# -------------------------------------------------------------
UPDATE_LEVEL_HP			= "HP_root"
UPDATE_LEVEL_PATH		= "particles/levelup/levelup.xml"
UPDATE_LEVEL_EFFECT		= "322730_shifang"
UPDATE_SKILL_EFFECT		= "322731_shifang"

# -------------------------------------------------------------
# 直接触发相关
# -------------------------------------------------------------
DIRECT_TALK = [csdefine.ENTITY_TYPE_COLLECT_POINT]

# -------------------------------------------------------------
# 地图区域效果水泡
# -------------------------------------------------------------
MAP_AREA_SHUIPAO_HP 	= "HP_head"
MAP_AREA_SHUIPAO_PATH 	= "particles/qipao.xml"

# -------------------------------------------------------------
# 静态模型后缀
# -------------------------------------------------------------
MODEL_STATIC_MODELNUM 	= "_static"

# -------------------------------------------------------------
# 封剑神宫门动画名称
# -------------------------------------------------------------
DOOR_FENG_JIAN_SHEN_GONG_STAR	= "opendoor"
DOOR_FENG_JIAN_SHEN_GONG_END	= "opendoorover"
DOOR_FENG_JIAN_SHEN_GONG_OVER	= "closedoor"
DOOR_FENG_JIAN_SHEN_GONG_DEF	= "closedoorover"

# -------------------------------------------------------------
# 静态怪物动画名称
# -------------------------------------------------------------
COLLISION_MONSTER_START	= "open"
COLLISION_MONSTER_END	= "openover"
COLLISION_MONSTER_OVER	= "close"
COLLISION_MONSTER_DEF	= "closeover"


# -------------------------------------------------------------
# 静态模型空碰撞盒子模型编号
# -------------------------------------------------------------
STATIC_MODEL_MODELNUM		= "gw7602"
COllISION_MODEL_MODELNUM	= "gw5121"

# -------------------------------------------------------------
# 模型缩放中缩放时间间隔
# -------------------------------------------------------------
MODEL_SCALE_TICK	= 0.04

# -------------------------------------------------------------
# 摄像头范围震动生效半径
# -------------------------------------------------------------
CAMERA_AREA_EFFECT_RADAIS	= 15

NPC_MODEL_SCALE_TIME_LEN = 2.0	# npc模型增大时长

VERTICAL_PITCH = -1.55	# 角色垂直pitch旋转角度
# -------------------------------------------------------------
# 不同状态活动的显示颜色
# -------------------------------------------------------------
_ACT_STATECOLOR = {
	0 : ( 232, 100, 27, 255 ),			# 未开始
	1 : ( 54, 210, 4, 255 ),			# 正在进行
	2 : ( 128, 128, 128, 255 ),			# 结束
	}

# -------------------------------------------------------------
# 一键换装
# -------------------------------------------------------------
ONE_KEY_SUIT_CD_ID		= 9999
ONE_KEY_SUIT_CD_TIME	= 10.0
ONE_KEY_SUIT_PART_MAP = {
	0	: "cel_head",		# 头     —— 头盔
	1	: "cel_neck",		# 颈     —— 项链
	2	: "cel_body",		# 身体   —— 身甲
	3	: "cel_breech",		# 臀部   —— 裤子
	4	: "cel_vola",		# 手     —— 手套
	5	: "cel_haunch",		# 腰     —— 腰带
	6	: "cel_cuff",		# 腕     —— 护腕
	7	: "cel_lefthand",		# 左手   —— 盾牌
	8	: "cel_tighthand",		# 右手   —— 武器
	9	: "cel_feet",		# 脚     —— 鞋子
	10	: "cel_leftfinger",	# 左手指 —— 戒指
	11	: "cel_rightfinger",	# 右手指 —— 戒指
	12	: "cel_cimelia",		# 魂魄石
	13	: "cel_talisman",	# 法宝
	}


COLLITION_DETECTION_LEN = 1	# 碰撞检测的射线长度
START_FALLING_SPEED = -0.6	# 当玩家在垂直方向上的速度小于这个值的时候，玩家才会下落，否则，引擎会忽略此值 by mushuang

# -------------------------------------------------------------
# 新的跳跃（2/3段跳）状态常量定义（physics.jumpState）
# -------------------------------------------------------------
STATE_JUMP_DEFAULT	= -1
STATE_JUMP_START	= 0
STATE_JUMP_UP		= 1
STATE_JUMP_START2	= 2
STATE_JUMP_UP2		= 3
STATE_JUMP_START3	= 4
STATE_JUMP_UP3		= 5
STATE_JUMP_DOWN		= 6
# 注意：
# 	STATE_JUMP_START/2/3、JUMPSTATE_JUMP_FINISH为瞬时事件，脚本中不在特定时间点检测不到，但是实际上并
# 没有太多需求去检测它们。 by mushuang

# -------------------------------------------------------------
# bounding box
# -------------------------------------------------------------
SPACE_INFINITE_DEPTH = -100000.0				# 无限深度模拟值


# -------------------------------------------------------------
# 常用动作名
# -------------------------------------------------------------
MODEL_ACTION_DIE						=	"die"
MODEL_ACTION_DIE_DAN					=	"die_dan"
MODEL_ACTION_DIE_SHUANG					=	"die_shuang"
MODEL_ACTION_DIE_FU						=	"die_fu"
MODEL_ACTION_DIE_CHANG					=	"die_chang"
MODEL_ACTION_DEAD						=	"dead"
MODEL_ACTION_JUMP_BEGIN					=	"jump_begin"
MODEL_ACTION_JUMP_PROCESS				= 	"jump_process"
MODEL_ACTION_JUMP_END					= 	"jump_end"
MODEL_ACTION_JUMP_BEGIN_STAND			=	"jump_stand_begin"
MODEL_ACTION_JUMP_BEGIN_STAND_DAN		=	"jump_stand_begin_dan"
MODEL_ACTION_JUMP_BEGIN_STAND_SHUANG	=	"jump_stand_begin_shuang"
MODEL_ACTION_JUMP_BEGIN_STAND_FU		=	"jump_stand_begin_fu"
MODEL_ACTION_JUMP_BEGIN_STAND_CHANG		=	"jump_stand_begin_chang"
MODEL_ACTION_JUMP_BEGIN_MOVE			=	"jump_move_begin"
MODEL_ACTION_JUMP_BEGIN_MOVE_DAN		=   "jump_move_begin_dan"
MODEL_ACTION_JUMP_BEGIN_MOVE_SHUANG		=	"jump_move_begin_shuang"
MODEL_ACTION_JUMP_BEGIN_MOVE_FU			=	"jump_move_begin_fu"
MODEL_ACTION_JUMP_BEGIN_MOVE_CHANG		=	"jump_move_begin_chang"
MODEL_ACTION_JUMP_STEP2                 =   "jump_step2"
MODEL_ACTION_JUMP_STEP2_DAN				=	"jump_step2_dan"
MODEL_ACTION_JUMP_STEP2_SHUANG			=	"jump_step2_shuang"
MODEL_ACTION_JUMP_STEP2_FU				=	"jump_step2_fu"
MODEL_ACTION_JUMP_STEP2_CHANG			=	"jump_step2_chang"
MODEL_ACTION_JUMP_STEP3                 =   "jump_step3"
MODEL_ACTION_JUMP_STEP3_DAN				=	"jump_step3_dan"
MODEL_ACTION_JUMP_STEP3_SHUANG			=	"jump_step3_shuang"
MODEL_ACTION_JUMP_STEP3_FU				=	"jump_step3_fu"
MODEL_ACTION_JUMP_STEP3_CHANG			=	"jump_step3_chang"
MODEL_ACTION_JUMP_AIR					=	"jump_air"
MODEL_ACTION_JUMP_AIR_DAN				=	"jump_air_dan"
MODEL_ACTION_JUMP_AIR_SHUANG			=	"jump_air_shuang"
MODEL_ACTION_JUMP_AIR_FU				=	"jump_air_fu"
MODEL_ACTION_JUMP_AIR_CHANG				=	"jump_air_chang"
MODEL_ACTION_JUMP_PREPARE               =   "jump_prepare"
MODEL_ACTION_JUMP_PREPARE_DAN			=	"jump_prepare_dan"
MODEL_ACTION_JUMP_PREPARE_SHUANG		=	"jump_prepare_shuang"
MODEL_ACTION_JUMP_PREPARE_FU			=	"jump_prepare_fu"
MODEL_ACTION_JUMP_PREPARE_CHANG			=	"jump_prepare_chang"
MODEL_ACTION_JUMP_PREPARE_END           =   "jump_prepare_end"
MODEL_ACTION_JUMP_PREPARE_END_DAN		=	"jump_prepare_end_dan"
MODEL_ACTION_JUMP_PREPARE_END_SHUANG	=	"jump_prepare_end_shuang"
MODEL_ACTION_JUMP_PREPARE_END_FU		=	"jump_prepare_end_fu"
MODEL_ACTION_JUMP_PREPARE_END_CHANG		=	"jump_prepare_end_chang"
MODEL_ACTION_JUMP_END_STAND				=	"jump_stand_end"
MODEL_ACTION_JUMP_END_STAND_DAN			=	"jump_stand_end_dan"
MODEL_ACTION_JUMP_END_STAND_SHUANG		=	"jump_stand_end_shuang"
MODEL_ACTION_JUMP_END_STAND_FU			=	"jump_stand_end_fu"
MODEL_ACTION_JUMP_END_STAND_CHANG		=	"jump_stand_end_chang"
MODEL_ACTION_JUMP_END_MOVE              =	"jump_move_end"
MODEL_ACTION_JUMP_END_MOVE_DAN			=	"jump_move_end_dan"
MODEL_ACTION_JUMP_END_MOVE_SHUANG		=	"jump_move_end_shuang"
MODEL_ACTION_JUMP_END_MOVE_FU			=	"jump_move_end_fu"
MODEL_ACTION_JUMP_END_MOVE_CHANG		=	"jump_move_end_chang"
MODEL_ACTION_MOVE						=	"Move"
MODEL_ACTION_RIDE_STAND					=	"ride_stand"
MODEL_ACTION_RIDE_RUN					=	"ride_run"
MODEL_ACTION_CROSSLEG_STAND				=	"crossleg_stand"
MODEL_ACTION_FLOAT_STAND				=	"float_stand"
MODEL_ACTION_FLOAT_UP					=	"float_up"
MODEL_ACTION_PLAY						=	"play"
MODEL_ACTION_WALK						=	"walk"
MODEL_ACTION_DANCE						=	"dance"
MODEL_ACTION_DANCE6						=	"dance6"
MODEL_ACTION_STAND						=	"stand"
MODEL_ACTION_FISHING					=	"fishing"
MODEL_ACTION_RESIST						=	"resist"
MODEL_ACTION_RESIST_DAN					=	"resist_dan"
MODEL_ACTION_RESIST_SHUANG				=	"resist_shuang"
MODEL_ACTION_RESIST_FU					=	"resist_fu"
MODEL_ACTION_RESIST_CHANG				=	"resist_chang"
MODEL_ACTION_DODGE						=	"dodge"
MODEL_ACTION_DODGE_DAN					=	"dodge_dan"
MODEL_ACTION_DODGE_SHUANG				=	"dodge_shuang"
MODEL_ACTION_DODGE_FU					=	"dodge_fu"
MODEL_ACTION_DODGE_CHANG				=	"dodge_chang"
MODEL_ACTION_DEFY						= 	"defy"
MODEL_ACTION_WJ_STAND					=	"WJ_stand"
MODEL_ACTION_HAIR_BONE_1				=	"hair_bone_1"
MODEL_ACTION_NEWLYBUILT					=	"newlybuilt"
MODEL_ACTION_NEWLYBUILT_DAN				=	"swordman_lianji01_dan"
MODEL_ACTION_NEWLYBUILT_SHUANG			=	"newlybuilt_shuang"
MODEL_ACTION_NEWLYBUILT_FU				=	"newlybuilt_fu"
MODEL_ACTION_NEWLYBUILT_CHANG			=	"newlybuilt_chang"
MODEL_ACTION_RIDE_UP					=	"jump_ride_up"
MODEL_ACTION_RIDE_UP_OVER				=	"jump_ride_up_over"
MODEL_ACTION_RIDE_DOWN					=	"jump_step2_high"
MODEL_ACTION_RIDE_DOWN_OVER				=	"jump_ride_down_2"

MODEL_ACTION_WATER_JUMP_BEGIN1			=	"water_jump1_begin"
MODEL_ACTION_WATER_JUMP_BEGIN2			=	"water_jump2_begin"
MODEL_ACTION_WATER_JUMP_BEGIN3			=	"water_jump3_begin"

MODEL_ACTION_WATER_JUMP_PROCESS1		=	"water_jump1_process"
MODEL_ACTION_WATER_JUMP_PROCESS2		=	"water_jump2_process"
MODEL_ACTION_WATER_JUMP_PROCESS3		=	"water_jump3_process"

MODEL_ACTION_WATER_JUMP_END1			=	"water_jump1_end"
MODEL_ACTION_WATER_JUMP_END1_DAN		=	"water_jump1_end_dan"
MODEL_ACTION_WATER_JUMP_END1_SHUANG		=	"water_jump1_end_shuang"
MODEL_ACTION_WATER_JUMP_END1_FU			=	"water_jump1_end_fu"
MODEL_ACTION_WATER_JUMP_END1_CHANG		=	"water_jump1_end_chang"
MODEL_ACTION_WATER_JUMP_END2			=	"water_jump2_end"
MODEL_ACTION_WATER_JUMP_END2_DAN		=	"water_jump2_end_dan"
MODEL_ACTION_WATER_JUMP_END2_SHUANG		=	"water_jump2_end_shuang"
MODEL_ACTION_WATER_JUMP_END2_FU			=	"water_jump2_end_fu"
MODEL_ACTION_WATER_JUMP_END2_CHANG		=	"water_jump2_end_chang"
MODEL_ACTION_WATER_JUMP_END3			=	"water_jump3_end"
MODEL_ACTION_WATER_JUMP_END3_DAN		=	"water_jump3_end_dan"
MODEL_ACTION_WATER_JUMP_END3_SHUANG		=	"water_jump3_end_shuang"
MODEL_ACTION_WATER_JUMP_END3_FU			=	"water_jump3_end_fu"
MODEL_ACTION_WATER_JUMP_END3_CHANG		=	"water_jump3_end_chang"

MODEL_ACTION_JUMP_ATTACK1				= 	"jump_attack4_1h_fu_1"
MODEL_ACTION_JUMP_ATTACK2				= 	"jump_attack4_1h_fu_2"
MODEL_ACTION_JUMP_ATTACK3				= 	"jump_attack4_1h_fu_3"

MODEL_ACTION_WATER_RUN					=	"water_run"
MODEL_ACTION_WATER_RUN_DAN				=	"water_run_dan"
MODEL_ACTION_WATER_RUN_SHUANG			=	"water_run_shuang"
MODEL_ACTION_WATER_RUN_FU				=	"water_run_fu"
MODEL_ACTION_WATER_RUN_CHANG			=	"water_run_chang"

MODEL_ACTION_MAGIC_CAST					= 	"magic_cast1"
MODEL_ACTION_RUN_BACK					= 	"run_back"
MODEL_ACTION_RANDOM						= 	"random1"
MODEL_ACTION_IDLE						= 	"idle"
MODEL_ACTION_STAND_1					=	"stand_1"
MODEL_ACTION_QX_STAND					=	"qx_stand"


g_worldCamHandlers = {
						csdefine.NORMAL_WORLD_CAM_HANDLER: WorldCamHandler(),
						csdefine.FIX_WORLD_CAM_HANDLER: FixWorldCamHandler(),
						}

MODEL_ACTION_NEWLYBUILT_LIST = [MODEL_ACTION_NEWLYBUILT,MODEL_ACTION_NEWLYBUILT,MODEL_ACTION_NEWLYBUILT_DAN,MODEL_ACTION_NEWLYBUILT_SHUANG,MODEL_ACTION_NEWLYBUILT_FU,MODEL_ACTION_NEWLYBUILT_CHANG]

# -------------------------------------------------------------
# 跳跃
# -------------------------------------------------------------
JUMP_PREPARE_TIME                        = 0.01  #蓄力时间
JUMP_GENEGRAVITY				= 2.0			# 陆地跳跃重力因子
JUMP_WATER_GENEGRAVITY			= 1.0			# 水面跳跃重力因子
JUMP_LAND_HEIGHT				= 3.0			# 陆地跳跃高度
JUMP_LAND_HEIGHT2                               = 3.0 #陆地二段跳高度
JUMP_LAND_HEIGHT3                               = 4.0 #陆地三段跳高度
JUMP_WATER_HEIGHT				= 6.0			# 水面跳跃高度
JUMP_WATER_EFFECTID				= "fly_water"	# 水面移动效果ID
JUMP_WATER_EFFECT_TIME			= 0.3			# 水面效果播放间隔
JUMP_FAST_BUFF_TRIGGER_TIME			= 0.5            #释放迅捷移动buff的两次按键间隔时间
JUMP_FAST_BUFF_TRIGGER_SKILLS = [ 322539001, 322539002, 322539003 ]                #迅捷移动技能ID(分三级)
JUMP_FAST_BUFF_ID = "006008"
JUMP_EFFECT_ID = "322537_shifang"
JUMP_SPELL_SKILLS	=	[ 322538 ]				# 跳跃中可释放的技能ID


# 骑宠跳跃动作
JUMP_VEHICLE_ACTION_MAPS = {
	csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_UP1		:	[MODEL_ACTION_JUMP_BEGIN,MODEL_ACTION_JUMP_PROCESS],
	csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_DOWN		:	[MODEL_ACTION_JUMP_PROCESS],
	csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_END		:	[MODEL_ACTION_JUMP_END],
}

# 跳跃动作
JUMP_ACTIONS_MAPS = {
csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_UP1		:	{0: ([MODEL_ACTION_JUMP_BEGIN_STAND,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_BEGIN_MOVE,MODEL_ACTION_JUMP_AIR]), 1: ([MODEL_ACTION_JUMP_BEGIN_STAND_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_BEGIN_MOVE_DAN,MODEL_ACTION_JUMP_AIR_DAN]),\
															2: ([MODEL_ACTION_JUMP_BEGIN_STAND_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_BEGIN_MOVE_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG]), 3: ([MODEL_ACTION_JUMP_BEGIN_STAND_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_BEGIN_MOVE_FU,MODEL_ACTION_JUMP_AIR_FU]),\
															4: ([MODEL_ACTION_JUMP_BEGIN_STAND_CHANG,MODEL_ACTION_JUMP_AIR_CHANG],[MODEL_ACTION_JUMP_BEGIN_MOVE_CHANG,MODEL_ACTION_JUMP_AIR_CHANG])},
csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_UP2		:	([MODEL_ACTION_JUMP_STEP2,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_STEP2_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_STEP2_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_STEP2_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_STEP2_CHANG,MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_UP3		:	([MODEL_ACTION_JUMP_STEP3,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_STEP3_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_STEP3_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_STEP3_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_STEP3_CHANG,MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_UPPREPARE  :   ([MODEL_ACTION_JUMP_PREPARE,MODEL_ACTION_JUMP_PREPARE_END],[MODEL_ACTION_JUMP_PREPARE_DAN,MODEL_ACTION_JUMP_PREPARE_END_DAN],[MODEL_ACTION_JUMP_PREPARE_SHUANG,MODEL_ACTION_JUMP_PREPARE_END_SHUANG],[MODEL_ACTION_JUMP_PREPARE_FU,MODEL_ACTION_JUMP_PREPARE_END_FU],[MODEL_ACTION_JUMP_PREPARE_CHANG,MODEL_ACTION_JUMP_PREPARE_END_CHANG]),
csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_DOWN		:	([MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_END		:	{0: ([MODEL_ACTION_JUMP_END_STAND],[MODEL_ACTION_JUMP_END_MOVE]), 1: ([MODEL_ACTION_JUMP_END_STAND_DAN],[MODEL_ACTION_JUMP_END_MOVE_DAN]), 2: ([MODEL_ACTION_JUMP_END_STAND_SHUANG],[MODEL_ACTION_JUMP_END_MOVE_SHUANG]),\
															3: ([MODEL_ACTION_JUMP_END_STAND_FU],[MODEL_ACTION_JUMP_END_MOVE_FU]), 4: ([MODEL_ACTION_JUMP_END_STAND_CHANG],[MODEL_ACTION_JUMP_END_MOVE_CHANG])},

csdefine.JUMP_TYPE_WATER1 | csdefine.JUMP_TIME_UP1		:	([MODEL_ACTION_JUMP_STEP2,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_STEP2_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_STEP2_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_STEP2_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_STEP2_CHANG,MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_WATER1 | csdefine.JUMP_TIME_DOWN		:	([MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_WATER1 | csdefine.JUMP_TIME_END		:	([MODEL_ACTION_WATER_JUMP_END1],[MODEL_ACTION_WATER_JUMP_END1_DAN],[MODEL_ACTION_WATER_JUMP_END1_SHUANG],[MODEL_ACTION_WATER_JUMP_END1_FU],[MODEL_ACTION_WATER_JUMP_END1_CHANG]),

csdefine.JUMP_TYPE_WATER2 | csdefine.JUMP_TIME_UP1		:	([MODEL_ACTION_JUMP_STEP2,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_STEP2_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_STEP2_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_STEP2_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_STEP2_CHANG,MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_WATER2 | csdefine.JUMP_TIME_DOWN		:	([MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_WATER2 | csdefine.JUMP_TIME_END		:	([MODEL_ACTION_WATER_JUMP_END2],[MODEL_ACTION_WATER_JUMP_END2_DAN],[MODEL_ACTION_WATER_JUMP_END2_SHUANG],[MODEL_ACTION_WATER_JUMP_END2_FU],[MODEL_ACTION_WATER_JUMP_END2_CHANG]),

csdefine.JUMP_TYPE_WATER3 | csdefine.JUMP_TIME_UP1		:	([MODEL_ACTION_JUMP_STEP2,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_STEP2_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_STEP2_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_STEP2_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_STEP2_CHANG,MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_WATER3 | csdefine.JUMP_TIME_DOWN		:	([MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_WATER3 | csdefine.JUMP_TIME_END		:	([MODEL_ACTION_WATER_JUMP_END3],[MODEL_ACTION_WATER_JUMP_END3_DAN],[MODEL_ACTION_WATER_JUMP_END3_SHUANG],[MODEL_ACTION_WATER_JUMP_END3_FU],[MODEL_ACTION_WATER_JUMP_END3_CHANG]),

csdefine.JUMP_TYPE_ATTACK | csdefine.JUMP_TIME_UP1		:	([MODEL_ACTION_JUMP_ATTACK1,MODEL_ACTION_JUMP_ATTACK2],[MODEL_ACTION_JUMP_ATTACK1,MODEL_ACTION_JUMP_ATTACK2],[MODEL_ACTION_JUMP_ATTACK1,MODEL_ACTION_JUMP_ATTACK2],[MODEL_ACTION_JUMP_ATTACK1,MODEL_ACTION_JUMP_ATTACK2],[MODEL_ACTION_JUMP_ATTACK1,MODEL_ACTION_JUMP_ATTACK2]),
csdefine.JUMP_TYPE_ATTACK | csdefine.JUMP_TIME_DOWN		:	([MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_ATTACK | csdefine.JUMP_TIME_END		:	([MODEL_ACTION_JUMP_ATTACK3],[MODEL_ACTION_JUMP_ATTACK3],[MODEL_ACTION_JUMP_ATTACK3],[MODEL_ACTION_JUMP_ATTACK3],[MODEL_ACTION_JUMP_ATTACK3]),

csdefine.JUMP_TYPE_SIMULATE | csdefine.JUMP_TIME_UP1		:	([MODEL_ACTION_JUMP_STEP2,MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_STEP2_DAN,MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_STEP2_SHUANG,MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_STEP2_FU,MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_STEP2_CHANG,MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_SIMULATE | csdefine.JUMP_TIME_DOWN		:	([MODEL_ACTION_JUMP_AIR],[MODEL_ACTION_JUMP_AIR_DAN],[MODEL_ACTION_JUMP_AIR_SHUANG],[MODEL_ACTION_JUMP_AIR_FU],[MODEL_ACTION_JUMP_AIR_CHANG]),
csdefine.JUMP_TYPE_SIMULATE | csdefine.JUMP_TIME_END		:	([MODEL_ACTION_WATER_JUMP_END1],[MODEL_ACTION_WATER_JUMP_END1_DAN],[MODEL_ACTION_WATER_JUMP_END1_SHUANG],[MODEL_ACTION_WATER_JUMP_END1_FU],[MODEL_ACTION_WATER_JUMP_END1_CHANG]),
}

# -------------------------------------------------------------
# 随机动作触发事件常量
# -------------------------------------------------------------
RANDOM_TRIGGER_TIME_MIN			=	4.0			# 最小触发时间
RANDOM_TRIGGER_TIME_MAX			=	8.0			# 最大触发时间

# -------------------------------------------------------------
# 跳砍
# -------------------------------------------------------------
JUMP_ATTACK_EFFECTID = "tiaokan"
JUMP_ATTACK_CAMERA_EFFECTID = 3
JUMP_ATTACK_DELAY = 0.0

# -------------------------------------------------------------
# 横版副本参数
# -------------------------------------------------------------
ENTITY_FACE_TO_TIME = 0.5
ENTITY_FACE_LEFT_YAW = 1.57
ENTITY_FACE_RIGHT_YAW = -1.57

# -------------------------------------------------------------
# 在静态模型下展示动态模型的通用后缀名
# -------------------------------------------------------------
DYNAMIC_MODEL_NAME = "_dynamic"

# -------------------------------------------------------------
# 资源类型定义
# -------------------------------------------------------------
REES_TYPE_UNDEFINE		= 0
RES_TYPE_MAPPING 		= 1
RES_TYPE_SOUND			= 2

# -------------------------------------------------------------
# 默认模型编号
# -------------------------------------------------------------
PET_DEFAULT_MODEL = "gw1307_3"
LAND_VEHICLE_DEFAULT_MODEL_NUM = 9110013
SKY_VEHICLE_DEFAULT_MODEL_NUM = 9110122

# ------------------------------------------------------------------------------------------------
# 飞扬文字字体类型
# ------------------------------------------------------------------------------------------------
TYPEMAPS = { "default":["system_small.font", 1.0],
			"roleCombat":["dmgtext_n2r.font", 0.8 ],
			"petCombat":["dmgtext_n2r.font", 0.8 ],
			"targetCombat":{"font": "dmgtext_r2n.font","role":1.2,"pet": 1.0},
			}

# 可以攻击怪物列表(自动战斗，tab)
ATTACK_MOSNTER_LIST = [ csdefine.ENTITY_TYPE_MONSTER,\
							 csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER,\
							 csdefine.ENTITY_TYPE_TREASURE_MONSTER,\
							 csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ]

#飞行光效类型集合
HOMER_EFFECT_LIST = ["HomerModelEffect", "HomerParticleEffect", "HomerParabolaParticleEffect", "HomerParabolaModelEffect"]

#水面跳跃相关
WATER_JUMP_TIME = 8.0  # 间隔
WATER_JUMP_PRO = 0.8   # 概率


# entity模型更换时优先访问Node数据点
MODEL_ACCESS_NODES = [		"HP_root",
								"HP_hitPoint",
								"HP_body",
								"HP_title",
								"HP_head",
								"HP_magic_l",
								"HP_magic_r",
								"HP_left_hand",
								"HP_right_hand",
								"HP_left_foot",
								"HP_right_foot",
								"HP_left_shoulder",
								"HP_right_shoulder",
								"HP_left_waise",
								"HP_right_waise",
								"HP_back_shield",
								"HP_back_weapon",
								"HP_sfx1",
								"HP_hip_01",
								"HP_stand_01",
								"HP_pan_01",
								"HP_SFX09" ]

#灵魂币掉落光效
ACCUMPOINT_EFFECT_ID = "jinbidiaoluo"

CASKET_WINDOW_EQUIP_BULID = 0 #装备打造
CASKET_WINDOW_ATTR_EXTRACT = 1 #装备抽取
CASKET_WINDOW_ATTR_POUR = 2 #属性灌注
CASKET_WINDOW_EQUIP_INTENSIFY = 3 #装备强化
CASKET_WINDOW_SPECIAL_STUFF_COM = 4 #特殊合成

CASKET_WINDOW_EQUIP = 0	#装备格
CASKET_WINDOW_STONE = 1	#石头格
CASKET_WINDOW_STUFF = 2	# 材料格
CASKET_WINDOW_SHEN = 3	# 神征令格

#自动战斗功能相关
SHOW_AUTOBAR_LEVEL_LIMITED = 20		# 限制等级
SHOW_AUTOBAR_QUEST_LIST = [ 20101173, 20101314 ]	# 任务触发开放自动战斗

#在这些地图中点击绿色字体时屏蔽“引路蜂/自动寻路”框的显示，直接寻路
SPACE_NOT_SHOW_NAVIGATE_SELECT = [ "zy_wa_huang_gong_47_mo" ]

#眩晕buffID 为了自动匹配眩晕动作
VERTIGO_BUFF_ID1 = "108001"
VERTIGO_BUFF_ID2 = "108007"

#战旗被占领光效
FHLT_BATTLEFLAG_OWN_EFFECT_ID = "112160_sf_magic_red"   # 本方占领-红色光效
FHLT_BATTLEFLAG_OTHER_EFFECT_ID = "112160_sf_magic_green" #对方占领-绿色光效

#镜头动作Y轴跟随
CAMERA_FOLLOW_Y_DIS_1 = 0.7
CAMERA_FOLLOW_Y_DIS_2 = 0.0

#城主NPC
MASTER_NPC_CLASSNAME = "10121122"

TOWER_DEFENCE_SKILLNUM = 3	#塔防副本技能数

#任务语音状态
GOSSIP_QUEST_STATES = { csdefine.QUEST_STATE_NOT_HAVE: "before_accept",
							csdefine.QUEST_STATE_FINISH: "after_complete",
						}

#战斗背景音乐路径
FIGHT_MUSIC_PATH = "bgm/scene_fighting03"

#脚步声绑定点
FOOT_TRIGGER_LEFT_NODE  = "HP_left_foot"
FOOT_TRIGGER_RIGHT_NODE = "HP_right_foot"
FOOT_TRIGGER_SOUND_PATH = "players/footsteps"

#凌波微步音效
WATER_FLY_SOUND = "players/footsteps/walkstepwater"

#需要摇老虎机决定任务倍数的奖励类型
QUEST_REWARD_SLOTS_TYPE = [
	csdefine.QUEST_REWARD_SOLTS_MONEY,
	csdefine.QUEST_REWARD_SOLTS_EXP,
	csdefine.QUEST_REWARD_SOLTS_POTENTIAL,
	csdefine.QUEST_REWARD_SOLTS_DAOHENG,
]

#能够在连击状态下使用的技能列表
HOMING_SPELL_CAN_USE_SKILL_LIST = [ 312680, 312681, 312682, 312683, ]		#目前只有闪躲技能能够在连击技能状态下使用

#主线任务自动交接时间
QUEST_MAIN_QUEST_AUTO_TIME = 15.0

#鼠标消息处理类型
MOUSE_HAADLED_BY_NOT_UI = 0
MOUSE_HAADLED_BY_UI = 1

# 寻路指引模型
AUTO_RUN_GUIDE_MODEL_PATH 	= "particles/model/jianl.model"
FUBEN_GUIDE_MODEL_PATH		= "particles/model/jianl.model"
FUBEN_GUIDE_MODEL_ACTION	= "stand"
FUBEN_GUIDE_HARD_POINT 		= "HP_title"
AUTO_RUN_DISTANCE 			= 3.0
AUTO_RUN_TIME_TICK 			= 0.15

PRE_ECOMPLETE_EFFECT		= "quest_npc"

#闪躲技能ID
AVOIDANCE_SKILL_ID_LIST = [ 312680, 312681, 312682, 312683 ]
