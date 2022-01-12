# -*- coding: gb18030 -*-

# $Id: Define.py,v 1.18 2008-08-20 09:04:01 yangkai Exp $


"""
locates client definations

2005.06.06 : tidied up by huangyongwei
"""
from ItemTypeEnum import *
import csdefine
# --------------------------------------------------------------------
# about player statues
# --------------------------------------------------------------------
# 顶层状态
GST_NONE						= 0x0000		# 未知状态
GST_GAME_INIT					= 0x0001		# 游戏启动状态
GST_LOGIN						= 0x0002		# 处于登录账号状态
GST_ENTER_ROLESELECT_LOADING	= 0x0004		# 登录后加载角色选择场景状态
GST_ROLE_SELECT					= 0x0008		# 处于角色选择状态
GST_BACKTO_ROLESELECT_LOADING	= 0x0010		# 返回角色选择时，加载角色场景状态
GST_ROLE_CREATE					= 0x0020		# 处于角色创建状态
GST_ENTER_WORLD_LOADING			= 0x0040		# 进入游戏加载状态
GST_IN_WORLD					= 0x0080		# 处于世界状态
GST_SPACE_LOADING				= 0x0100		# 角色跳转时加载场景状态
GST_OFFLINE						= 0x0200		# 断线状态

GST_UNBUSYS						= [GST_LOGIN, GST_ROLE_SELECT, GST_ROLE_CREATE, GST_IN_WORLD, GST_OFFLINE]
GST_UNBUSY						= GST_LOGIN | GST_ROLE_SELECT | GST_ROLE_CREATE | GST_IN_WORLD | GST_OFFLINE


# --------------------------------------------------------------------
# 装备物品（模型编号）
# --------------------------------------------------------------------
PRE_EQUIP_NULL				=	0		# 无物品
PRE_EQUIP_DRUG 				=	1		# 补给品
PRE_EQUIP_NORMAL 			=	2		# 普通物品
PRE_EQUIP_ARMET				=	3		# 头盔
PRE_EQUIP_LORICAE			=	4		# 上身铠甲
PRE_EQUIP_ARMGUARD			=	5		# 护手
PRE_EQUIP_SKIRT				=	6		# 下身裙子及其它
PRE_EQUIP_FOOTGUARD			=	7		# 护足
PRE_EQUIP_SHIELD			=	8		# 盾
PRE_EQUIP_LANCE2			=	9		# 双手矛
PRE_EQUIP_KNIFE				=	10		# 单匕首
PRE_EQUIP_STAFF				=	11		# 单手杖
PRE_EQUIP_STAFF2			=	12		# 双手杖
PRE_EQUIP_BOW				=	13		# 弓
PRE_EQUIP_LANCE				=	14		# 单手矛
PRE_EQUIP_TPOISONPIN			=	15		# 投掷用毒针
PRE_EQUIP_TROCK				=	16		# 投掷用石头
PRE_EQUIP_TDART				=	17		# 投掷用矛
PRE_EQUIP_SWORD				=	18		# 单手剑
PRE_EQUIP_SWORD2			=	19		# 双手剑
PRE_EQUIP_ORNAMENT			=	20		# 饰品
PRE_EQUIP_AXE 				=	21		# 单手斧
PRE_EQUIP_AXE2 				=	22		# 双手斧
PRE_EQUIP_HAMMER			=	23		# 单手锤
PRE_EQUIP_HAMMER2 			=	24		# 双手锤
PRE_EQUIP_RING				=	25		# 戒指
PRE_EQUIP_NECKLACE 			=	26		# 项链
PRE_EQUIP_TWOSWORD			=	27		# 双持剑
PRE_EQUIP_TWOLANCE			=	29		# 枪
PRE_EQUIP_JEWEL  			=	96		# 宝石
PRE_EQUIP_SCROLL 			=	97		# 卷轴
PRE_EQUIP_MONEY				=	98		# 金钱
PRE_EQUIP_OTHER				=	99		# 其它物品

# 装备武器类型
WEAPON_TYPE_NONE			=	0		# 空手
WEAPON_TYPE_WEIGHTBLUNT		=	1		# 重钝武器
WEAPON_TYPE_LIGHTBLUNT		=	2		# 轻钝武器
WEAPON_TYPE_WEIGHTSHARP		=	3		# 重锐利武器
WEAPON_TYPE_LIGHTSHARP		=	4		# 轻锐利武器
WEAPON_TYPE_DOUBLEHAND		=	5		# 双持武器
WEAPON_TYPE_BOW				=	6		# 弓
WEAPON_TYPE_THROW			=	7		# 投掷
WEAPON_TYPE_POSISON			=	8		# 毒
WEAPON_TYPE_BIANSHEN		=	9		# 变身模型武器类型

# 装备防具类型
ARMOR_TYPE_EMPTY			=	0		# 无防具
ARMOR_TYPE_CLOTH			=	1		# 布甲
ARMOR_TYPE_SKIN				=	2		# 皮甲
ARMOR_TYPE_WOOD				=	3		# 木头
ARMOR_TYPE_METAL			=	4		# 金属甲
ARMOR_TYPE_SHIELD			=	5		# 盾牌
ARMOR_TYPE_ROCK				=	6		# 石头

WEAPON_TYPE_MAP = {
		ITEM_UNKOWN			:	WEAPON_TYPE_NONE,
		ITEM_WEAPON_AXE2	:	WEAPON_TYPE_WEIGHTSHARP,
		ITEM_WEAPON_HAMMER2	:	WEAPON_TYPE_WEIGHTBLUNT,
		ITEM_WEAPON_STAFF	:	WEAPON_TYPE_WEIGHTBLUNT,
		ITEM_WEAPON_AXE1	:	WEAPON_TYPE_WEIGHTSHARP,
		ITEM_WEAPON_HAMMER1	:	WEAPON_TYPE_LIGHTBLUNT,
		ITEM_WEAPON_SPEAR2	:	WEAPON_TYPE_WEIGHTSHARP,
		ITEM_WEAPON_SWORD2	:	WEAPON_TYPE_WEIGHTSHARP,
		ITEM_WEAPON_SPEAR1	:	WEAPON_TYPE_LIGHTSHARP,
		ITEM_WEAPON_DAGGER	:	WEAPON_TYPE_LIGHTSHARP,
		ITEM_WEAPON_SWORD1	:	WEAPON_TYPE_LIGHTSHARP,
		ITEM_WEAPON_LONGBOW	:	WEAPON_TYPE_BOW,
		ITEM_WEAPON_TWOSWORD:	WEAPON_TYPE_DOUBLEHAND,
		}
WEAPON_TYPE_MODEL_MAP = {
		PRE_EQUIP_NULL		:	WEAPON_TYPE_NONE,
		PRE_EQUIP_AXE2		:	WEAPON_TYPE_WEIGHTSHARP,
		PRE_EQUIP_HAMMER2	:	WEAPON_TYPE_WEIGHTBLUNT,
		PRE_EQUIP_STAFF2	:	WEAPON_TYPE_WEIGHTBLUNT,
		PRE_EQUIP_AXE		:	WEAPON_TYPE_WEIGHTSHARP,
		PRE_EQUIP_HAMMER	:	WEAPON_TYPE_LIGHTBLUNT,
		PRE_EQUIP_LANCE2	:	WEAPON_TYPE_WEIGHTSHARP,
		PRE_EQUIP_SWORD2	:	WEAPON_TYPE_WEIGHTSHARP,
		PRE_EQUIP_LANCE		:	WEAPON_TYPE_LIGHTSHARP,
		PRE_EQUIP_KNIFE		:	WEAPON_TYPE_LIGHTSHARP,
		PRE_EQUIP_SWORD		:	WEAPON_TYPE_LIGHTSHARP,
		PRE_EQUIP_BOW		:	WEAPON_TYPE_BOW,
		PRE_EQUIP_TWOSWORD	:	WEAPON_TYPE_DOUBLEHAND,
		}

WEAPON_TYPE_CHALLENGE = {
		"chiyou"			:	WEAPON_TYPE_WEIGHTSHARP,
		"huangdi"			:	WEAPON_TYPE_DOUBLEHAND,
		"houyi"				:	WEAPON_TYPE_BOW,
		"nuwo"				:	WEAPON_TYPE_WEIGHTBLUNT,
}
# --------------------------------------------------------------------
# about entity be clicked ( come from: client/Const.py；designed by wanhp  )
# --------------------------------------------------------------------
TARGET_CLICK_FAIL			= 	0		# 点击目标失败
TARGET_CLICK_SUCC			= 	1		# 点击目标成功
TARGET_CLICK_MOVE           = 	2		# 点击移动，一般是点击地面或者的二次点击 NPC

TARGET_PURSUE_FAILURE		=	0		# 追击失败
TARGET_PURSUE_SUCCESS		= 	1		# 追击成功
TARGET_PURSUE_MOVING		= 	2		# 正在追击


# --------------------------------------------------------------------
# about skill type ( come from: client/Define.py；designed by panguankong )
# --------------------------------------------------------------------
SKILL_TYPE_ACTIVE_PROFESSION		= 1			# 主动职业技能( 原名：SKILL_TYPE_INITIATIVE_WORK )
SKILL_TYPE_PASSIVE_PROFESSION 		= 2			# 被动职业技能( 原名：SKILL_TYPE_PASSIVENESS_WORK )
SKILL_TYPE_ACTIVE_CORPS				= 3			# 主动军团技能( 原名：SKILL_TYPE_INITIATIVE_CONFRATERNITY )
SKILL_TYPE_PASSIVE_CORPS			= 4			# 被动军团技能( 原名：SKILL_TYPE_PASSIVENESS_CONFRATERNITY )
SKILL_TYPE_ACTIVE_GEST	 			= 5			# ?( 原名：SKILL_TYPE_INITIATIVE_GEST )
SKILL_TYPE_PASSIVE_GEST		 		= 6			# ?( 原名：SKILL_TYPE_PASSIVENESS_GEST )


# ------------------------------------------------------------------------
# 各职业三连击技能ID
# ------------------------------------------------------------------------
SKILL_ID_FIGHTER_TRIGGER_SKILL			= 323175001     # 战士3连击技能ID
SKILL_ID_SWORDMAN_TRIGGER_SKILL			= 311338001     # 剑客3连击技能ID
SKILL_ID_ARCHER_TRIGGER_SKILL			= 323155001     # 射手3连击技能ID
SKILL_ID_MAGE_TRIGGER_SKILL				= 323147001     # 法师3连击技能ID

SKILL_ID_TRIGGER_SKILLS = { 
	csdefine.CLASS_FIGHTER:		SKILL_ID_FIGHTER_TRIGGER_SKILL,		# 战士
	csdefine.CLASS_SWORDMAN:	SKILL_ID_SWORDMAN_TRIGGER_SKILL,	# 剑客
	csdefine.CLASS_ARCHER:		SKILL_ID_ARCHER_TRIGGER_SKILL,		# 射手
	csdefine.CLASS_MAGE:		SKILL_ID_MAGE_TRIGGER_SKILL			# 法师
	}

TRIGGER_SKILL_IDS = [ 323175, 323165, 323155, 323147 ]   # 三连击技能系列ID列表
# ------------------------------------------------------------------------------------------------
# 光效组件ID定义
# ------------------------------------------------------------------------------------------------
PSA_SOURCE_TYPE_ID			 	= 1
PSA_SINK_TYPE_ID			 	= 2
PSA_BARRIER_TYPE_ID			 	= 3
PSA_FORCE_TYPE_ID			 	= 4
PSA_STREAM_TYPE_ID			 	= 5
PSA_JITTER_TYPE_ID				= 6
PSA_SCALAR_TYPE_ID			 	= 7
PSA_TINT_SHADER_TYPE_ID		 	= 8
PSA_NODE_CLAMP_TYPE_ID		 	= 9
PSA_ORBITOR_TYPE_ID				= 10
PSA_FLARE_TYPE_ID				= 11
PSA_COLLIDE_TYPE_ID				= 12
PSA_MATRIX_SWARM_TYPE_ID		= 13
PSA_MAGNET_TYPE_ID				= 14
PSA_SPLAT_TYPE_ID				= 15

# ------------------------------------------------------------------------------------------------
# 动作CAPS定义
# ------------------------------------------------------------------------------------------------
# 状态Caps(可以和行为Caps/索引Caps并存)
CAPS_DEFAULT					= 0			# 默认Caps
CAPS_IDLE						= 1			# 战斗Caps(处于战斗状态下激活)
CAPS_DEAD						= 2			# 死亡Caps(处于死亡状态下激活)
CAPS_LOGIN						= 3			# 登陆Caps(在角色选择画面激活)
CAPS_RANDOM						= 4			# 随机动作Caps(由动作匹配器控制)
CAPS_SNEAK						= 5			# 潜行状态Caps
CAPS_ENVIRONMENT_OBJECT			= 6			# 场景Caps
CAPS_FLY_WATER					= 7			# 水面行走


# 行为Caps(可以和状态Caps并存/索引Caps并存)
CAPS_RADIFOLLOW					= 9			# 游荡Caps
CAPS_NOWEAPON					= 10		# 无武器Caps(玩家卸下武器后激活)
CAPS_WEAPON						= 11		# 拿武器Caps(玩家装备武器后激活)
CAPS_JUMP                       = 12        # 跳跃过程中
CAPS_FASTMOVING                 = 13        # 移动迅捷过程中
CAPS_SPRINT                     = 14        # 冲刺过程中
CAPS_VERTIGO                    = 15        # 眩晕过程中
CAPS_DAN_WEAPON					= 16		# 单手剑Caps
CAPS_SHUANG_WEAPON				= 17		# 双手剑Caps
CAPS_FU_WEAPON					= 18		# 斧头Caps
CAPS_CHANG_WEAPON				= 19		# 长枪Caps

# Caps索引(用于表现多种自定义状态，可以和状态Caps/行为Caps并存)
# 索引一般不用于去CapsOn/CapsOff匹配
# 比如[ 4, 10,25 ] 表示空手状态下的编号为16的随机动作
# 比如[ 4, 11, 25 ] 表示拿武器状态下的编号为16的随机动作
CAPS_LIE_DOWN					= 20		# 躺下（实际是播放dead的最后一帧）
# 预留空位以便扩展，随机动作从25开始
CAPS_INDEX25					= 25
CAPS_INDEX26					= 26
CAPS_INDEX27					= 27
CAPS_INDEX28					= 28
CAPS_INDEX29					= 29
CAPS_INDEX30					= 30
CAPS_INDEX31					= 31

# ------------------------------------------------------------------------------------------------
# 状态对应Caps
# ------------------------------------------------------------------------------------------------
STATE_CAPS = {			csdefine.ENTITY_STATE_FREE			: CAPS_DEFAULT,	# 自由状态
						csdefine.ENTITY_STATE_DEAD 			: CAPS_DEAD,	# 死亡状态
						csdefine.ENTITY_STATE_REST 			: CAPS_DEFAULT,	# 休息状态
						csdefine.ENTITY_STATE_FIGHT 		: CAPS_IDLE,	# 战斗状态
						csdefine.ENTITY_STATE_PENDING 		: CAPS_DEFAULT,	# 未决状态
						csdefine.ENTITY_STATE_VEND			: CAPS_DEFAULT,	# 摆摊状态
						csdefine.ENTITY_STATE_RACER			: CAPS_DEFAULT,	# 比赛状态（例如：赛马）
						csdefine.ENTITY_STATE_CHANGING		: CAPS_DEFAULT,	# 变身状态（如：钓鱼，变身大赛等）
						csdefine.ENTITY_STATE_QUIZ_GAME		: CAPS_DEFAULT,	# 问答状态
						}

# ------------------------------------------------------------------------------------------------
# 状态对应Caps
# ------------------------------------------------------------------------------------------------
CLASS_WEAPONTYPE = {	csdefine.CLASS_FIGHTER				: [ WEAPON_TYPE_WEIGHTSHARP, WEAPON_TYPE_LIGHTBLUNT ],		# 战士(单手斧、枪)
						csdefine.CLASS_SWORDMAN				: [ WEAPON_TYPE_LIGHTSHARP, WEAPON_TYPE_DOUBLEHAND ],		# 剑客（单、双剑）
						csdefine.CLASS_ARCHER				: [ WEAPON_TYPE_BOW ],				# 射手
						csdefine.CLASS_MAGE					: [ WEAPON_TYPE_WEIGHTBLUNT ],		# 法师
						}

# ------------------------------------------------------------------------------------------------
# 怪物对应Caps
# ------------------------------------------------------------------------------------------------
MONSTER_CAPS = { 	csdefine.ENTITY_STATE_FREE					: CAPS_DEFAULT,				# 自由状态
					csdefine.ENTITY_STATE_DEAD					: CAPS_DEAD,				# 死亡状态
					csdefine.ENTITY_STATE_FIGHT					: CAPS_IDLE,				# 战斗状态
					csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT	: CAPS_ENVIRONMENT_OBJECT,	# 场景物件状态
					}

# ------------------------------------------------------------------------------------------------
# 跳跃过程定义
# ------------------------------------------------------------------------------------------------
JUMP_START			= 0						# 准备起跳
JUMP_UP				= 1						# 起跳过程中
JUMP_DOWN			= 2						# 下落过程中
JUMP_END			= 3						# 跳跃完毕

# ------------------------------------------------------------------------------------------------
# 骑宠坐位方式定义
# ------------------------------------------------------------------------------------------------
VEHICLE_MODEL_HIP = 1						# 跨腿
VEHICLE_MODEL_PAN = 2						# 盘腿
VEHICLE_MODEL_STAND = 3						# 浮空

# ------------------------------------------------------------------------------------------------
# 刀光动作集合
# ------------------------------------------------------------------------------------------------
# 重锐利武器类型刀光
LOFT_WEIGHTSHARP = [ 	"attack1_1h", "attack2_1h","attack3_1h","attack4_1h","attack5_1h","crossleg1_1h",\
						"crossleg_1h","crossleg_1h_skill","ride1_1h","ride_1h","ride_1h_skill",]
# 双持武器类型刀光
LOFT_DOUBLEHAND = [ 	"attack1_2h", "attack2_2h","attack3_2h","attack4_2h","attack5_2h","crossleg1_2h",\
						"crossleg_2h","crossleg_2h_skill","ride1_2h","ride_2h","ride_2h_skill",]

LOFT_MAPS = { 	WEAPON_TYPE_WEIGHTSHARP 	: LOFT_WEIGHTSHARP,
				WEAPON_TYPE_DOUBLEHAND 		: LOFT_DOUBLEHAND,
				}

# ------------------------------------------------------------------------------------------------
# 模型组合宏定义
# ------------------------------------------------------------------------------------------------
# 默认主体模型
MODEL_DEFAULT_MAIN		= 0		# 默认主体模型
# 角色装备部分
MODEL_EQUIP_MAIN		= 1		# 装备主体模型（身体）
MODEL_EQUIP_HEAD		= 2		# 装备附属模型（头发）
MODEL_EQUIP_RHAND		= 3		# 装备附属模型（右手武器）
MODEL_EQUIP_LHAND		= 4		# 装备附属模型（左手武器）
MODEL_EQUIP_TALIS		= 5		# 装备额外模型（法宝）
# 骑宠模型
MODEL_VEHICLE			= 6		# 骑宠主体模型
# 飞行传送部分
MODEL_FLY_MAIN			= 11	# 飞行传送主体模型
# 赛马部分
MODEL_HORSE_MAIN		= 21	# 赛马主体模型


# ------------------------------------------------------------------------------------------------
# 模型显示方式宏定义
# ------------------------------------------------------------------------------------------------
MODEL_VISIBLE_TYPE_FALSE		= 0		# 模型不显示
MODEL_VISIBLE_TYPE_TRUE			= 1		# 模型显示
MODEL_VISIBLE_TYPE_FBUTBILL	 	= 2		# 模型不显示但显示附加物
MODEL_VISIBLE_TYPE_SNEAK	 	= 3		# 模型半透明显示

# ------------------------------------------------------------------------------------------------
# 场景音效播放方式
# ------------------------------------------------------------------------------------------------
SOUND_END_BGMUSIC = 1				# 中断背景音乐

# ------------------------------------------------------------------------------------------------
# 模型加载事件
# ------------------------------------------------------------------------------------------------
MODEL_LOAD_ENTER_WORLD			= 0	# 进入视野加载
MODEL_LOAD_IN_WORLD_CHANGE		= 1	# 已在视野加载

# ------------------------------------------------------------------------------------------------
# 地图区域特殊效果
# ------------------------------------------------------------------------------------------------
MAP_AREA_EFFECT_DEFAULT	= 0	# 默认无效果
MAP_AREA_EFFECT_SHUIPAO	= 1	# 水泡效果
MAP_AREA_EFFECT_UNWATER	= 2	# 水扭曲、水底刻蚀纹理动画效果

MAP_AREA_EFFECTS_MODELCHANGE = [ MAP_AREA_EFFECT_SHUIPAO ]							# entity 模型更换检测效果列表
MAP_AREA_EFFECTS_CHANGEAREA	= [ MAP_AREA_EFFECT_SHUIPAO, MAP_AREA_EFFECT_UNWATER ]	# playerRole更换区域检测效果列表

# ------------------------------------------------------------------------------------------------
# 摄像机晃动效果
# ------------------------------------------------------------------------------------------------
CAMERA_SHAKE_NONE		= 0	# 无晃动效果
CAMERA_SHAKE_ONE_TYPE	= 1	# 目标晃动效果
CAMERA_SHAKE_AREA_TYPE	= 2	# 目标范围晃动效果


# ------------------------------------------------------------------------------------------------
# 物品状态定义
# ------------------------------------------------------------------------------------------------
ITEM_STATUS_NATURAL		= 1		# 正常的
ITEM_STATUS_ABRASION	= 2		# 磨损的（还能用，但耐久已经很低了）
ITEM_STATUS_USELESSNESS	= 3		# 无法使用的（损坏了、不符合条件之类的）
ITEM_STATUS_TO_COLOR = {
	ITEM_STATUS_NATURAL		: ( 255,255,255,255 ),
	ITEM_STATUS_ABRASION	: ( 255,255,0,180 ),
	ITEM_STATUS_USELESSNESS	: ( 255,100,100,200 ),
}


# ------------------------------------------------------------------------------------------------
# 玩家控制宏定义
# ------------------------------------------------------------------------------------------------
CONTROL_FORBID_ROLE_MOVE	= 0x00000001	# 不允许控制玩家移动
CONTROL_FORBID_ROLE_CAMERA	= 0x00000010	# 不允许控制玩家摄像头

CONTROL_FORBID_ROLE_LIST = ( CONTROL_FORBID_ROLE_MOVE, CONTROL_FORBID_ROLE_CAMERA )


CONTROL_FORBID_ROLE_MOVE_PLAY_ACTION 	= 0  #动作限制移动
CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT	= 1  #镜头限制移动
CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE   = 2  #下坐骑限制移动
CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK    = 3  #跳砍限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_108007    = 4  #108007限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_108010    = 5  #108010限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_108012    = 6  #108012限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_208003    = 7  #208003限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_99010     = 8  #99010限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_99027     = 9  #99027限制移动
CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL  = 10  #Buff_onPatrol限制移动
CONTROL_FORBID_ROLE_MOVE_SPRINT         = 11  #冲刺限制移动

CONTROL_FORBID_ROLE_MOVE_LIST = (CONTROL_FORBID_ROLE_MOVE_PLAY_ACTION,
				 CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT,
				 CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE,
				 CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_108007,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_108010,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_108012,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_208003,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_99010,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_99027,
				 CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL,
				 CONTROL_FORBID_ROLE_MOVE_SPRINT
				 )

CONTROL_FORBID_ROLE_CAMERA_EVENT = 0 #播放镜头限制摄像机

CONTROL_FORBID_ROLE_CAMERA_LIST = ( CONTROL_FORBID_ROLE_CAMERA_EVENT,)

# ------------------------------------------------------------------------------------------------
# 竞技活动集合时间
# ------------------------------------------------------------------------------------------------
TIME_GATHER_TEAM_CHALLENGE		= 2 * 60
TIME_GATHER_WU_DAO				= 2 * 60
TIME_GATHER_ROLE_COMPETITION	= 5 * 60
TIME_GATHER_TONG_COMPETITION	= 5 * 60
TIME_GATHER_TEAM_COMPETITION	= 5 * 60
TIME_GATHER_TONG_ABATTOIR		= 5 * 60


# ------------------------------------------------------------------------------------------------
# 粒子显示类型
# ------------------------------------------------------------------------------------------------
TYPE_PARTICLE_PLAYER	=	1
TYPE_PARTICLE_PIOP		=	2
TYPE_PARTICLE_PIN		=	3
TYPE_PARTICLE_OP		=	4
TYPE_PARTICLE_NPC		=	5
TYPE_PARTICLE_SCENE		=	6

#登陆地图类型
LOGIN_TYPE_MAP       = 100
SELECT_CAMP_TYPE_MAP = 101

#CG
LOGIN_CG_PATH = "videos/compose-all.avi"


#技能受击状态
COMMON_NO         = 0  #默认状态
COMMON_BE_HIT     = 1 #普通受击(和连击受击区分)

#entity模型真实碰撞体每次增加高度
ENTITIES_MODEL_COLLIDE_HEIGHT =    0.25