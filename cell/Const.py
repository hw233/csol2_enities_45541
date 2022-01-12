# -*- coding: gb18030 -*-

# $Id: Const.py,v 1.34 2008-09-04 07:44:14 kebiao Exp $


"""
locates cell constants

2005.06.06 : tidied up by huangyongwei
"""


import csdefine
import cschannel_msgs
import ShareTexts as ST
import Function
import csconst
import ItemTypeEnum

# --------------------------------------------------------------------
# about role's attributes( from cell/AttrDefine.py；designed by penghuawei )
# --------------------------------------------------------------------

ROLE_HANDEDS_FREE_RANGE				= int( 2.0 * csconst.FLOAT_ZIP_PERCENT )	# 空手攻击距离( 原名：EMPTY_HANDED_RANGE )
ROLE_DOUBLE_DAMAGE_EFFECT 			= 200										# 致命一击效果，默认全部都是增加1倍伤害，即产生2倍(200%)的伤害( 原名：DOUBLE_DAMAGE_EFFECT )

if csdefine.IS_GREEN_VERSION == 0:
	ROLE_MOVE_SPEED_RADIX				= int( 5.0 * csconst.FLOAT_ZIP_PERCENT )	# 移动速度；必须float( 原名：MOVE_SPEED_RADIX )
else:
	ROLE_MOVE_SPEED_RADIX				= int( 8.0 * csconst.FLOAT_ZIP_PERCENT )	# 移动速度；必须float( 原名：MOVE_SPEED_RADIX )

ROLE_MAX_RESIST_NATURE 				= 95										# 最大自然防御( 原名：MAX_RESIST_ELEMENT )
ROLE_MAX_RESIST_VIRUS 				= 95										# 最大毒素防御( 原名：MAX_RESIST_POISON )
ROLE_MAX_RESIST_SPIRIT 				= 95										# 最大精神防御( 原名：MAX_RESIST_SPIRIT )

ROLE_MP_REVER_INTERVAL				= 3.0										# 有hp/mp恢复的entity，hp/mp恢复时的间隔(秒/次)( from L3Define.py；原名：C_REVERT_TIME )

ROLE_HIT_SPEED_BASE					= int( 1.3 * csconst.FLOAT_ZIP_PERCENT )	# 攻击速度，咋的都固定了咧。。。 by 姜毅
# 生命参数
# ROLE_HP_MAX_RADIX																# 被搬到 common/csconst.py 中定义

# 法力参数
# ROLE_MP_MAX_RADIX																# 被搬到 common/csconst.py 中定义
ROLE_DROP_DAMAGE_HEIGHT				= 15.0										# 掉落伤害高度


# 全逆天同前缀套装属性加成 by姜毅
ALL_GOD_PROP_EFFECT	=	0.1 * csconst.FLOAT_ZIP_PERCENT

# --------------------------------------------------------------------
# about pet( hyw )
# --------------------------------------------------------------------
PET_HEARTBEAT_INTERVAL				= 1.0			# 宠物心跳速度
PET_MP_REVER_INTERVAL				= 3.0			# 有hp/mp恢复的entity，hp/mp恢复时的间隔(秒/次)

PET_KEEP_REINBIBLE_MAX				= 3				# 最多能使用几个驾驭典

PET_LIFE_WASTAGE_INTERVAL			= 300.0			# 每隔多长时间宠物寿命折损一次（不足这个时间，不扣除）
PET_JOYANCY_WASTAGE_INTERVAL		= 300.0			# 每隔多长时间宠物快乐度折损一次（不足这个时间，不扣除）

PET_DIE_WITHDRAW_DELAY				= 1.0			# 宠物死亡后多久回收

PET_EXP_LEVEL_LIMIT_GAP				= 5				# 宠物高于角色多少等级将不能吸收经验

PET_TELEPORT_DETECT_CONTROL			= 5				# 每隔一段时间才进行传送检测

PET_FOLLOW_DETECT_CONTROL			= 3				# 每隔一段时间才进行强行跟随

PET_SMART_RANGE						= int( 15.0 * csconst.FLOAT_ZIP_PERCENT )	# 敏捷型宠物攻击距离
PET_INTELLECT_RANGE					= int( 20.0 * csconst.FLOAT_ZIP_PERCENT )	# 智力型宠物攻击距离

# -------------------------------------------
PET_ROLE_KEEP_DISTANCE				= 3.0			# 宠物与玩家之间保持的距离（单位：米）
PET_FORCE_FOLLOW_RANGE				= 52.0			# 宠物离开玩家多远就强迫跟随
PET_ENMITY_RANGE					= 10.0			# 搜寻怪物范围
PET_FORCE_TELEPORT_RANGE			= csconst.ROLE_AOI_RADIUS/1.2	# 宠物强制传送距离

PET_PROPAGATE_NOTIFY_INTERVAL		= 3 * 3600		# 多长时间通知一次玩家领取宠物

PCG_GET_GEM_LEVEL					= 10			# 玩家多少级后可以在 NPC 处购买经验石
PCG_COMMON_GEM_COUNT				= 5				# 存放普通宝石的数量

#-------------------------------------------
# about call monster
#-------------------------------------------
CALL_MONSTER_INIT_TIME				= 2

# --------------------------------------------------------------------
# about quest( from common/QuestDefine.py；designed by kebiao )
# --------------------------------------------------------------------
QUEST_MAX_ASSIGNMENT				= 20			# 最多同时可接多少个任务( 原名：C_MAX_QUEST )


# --------------------------------------------------------------------
# about buffer
# --------------------------------------------------------------------
DEBUFF_COUNT_UPPER_LIMIT			= 10			# 最多允许有几个debuff的存在（如果超过这个数量，后来的会把前面的挤掉）
													# ( from common/L3Define.py；原名：C_MAX_DEBUFF )

# --------------------------------------------------------------------
# about combat
# --------------------------------------------------------------------
global_combatDict = {		#此值只允许是 int, float, string 否则将会出现意外错误
	#///////////////////攻击属性///////////////////////////////////////////////
	"skill_percent" : 0, # 技能攻击力加成
	"skill_value" : 0, # 技能攻击力加值
	#//////////////////其他标志////////////////////////////////////////////////
}

# --------------------------------------------------------------------
# about Vehicle
# --------------------------------------------------------------------
VEHICLE_ACTIVATE_SKILLID				= 860002001		# 激活骑宠技能ID
VEHICLE_ACTIVATE_BUFFID				        = 1022 # 骑宠加属性buff ID
VEHICLE_CONJURE_BUFFID				        = [6005,8006] # 骑宠加速度buff ID
VEHICLE_TRANS_SKILLID				        = 860001001		#传功技能ID

VEHICLE_CONJURE_SKILLID						= 322385001		# 召唤陆行骑宠技能ID
VEHICLE_FLY_CONJURE_SKILLID					= 322724001		# 召唤飞行骑宠技能ID
VEHICLE_WITH_CONJURE_SKILLID				= 322402001		# 共骑技能ID，此技能会触发无敌效果
VEHICLE_UPDATE_TIME							= 15.0			# 骑宠状态下更新timer
VEHICLE_JOYANCY_TIME						= 1800.0		# 骑宠快乐度更新时间
VEHICLE_EXP_DISLEVEL						= 5				# 骑宠与玩家的等级差，超过这个差值无法获取经验
VEHICLE_EXP_ADD								= 500			# 骑宠每隔15秒获取的经验值

# --------------------------------------------------------------------
# pk
# --------------------------------------------------------------------
PK_STATE_ATTACK_TIME						= 120.0			# 恶意pk状态持续时间（秒）
PK_VALUE_LESS_TIME							= 1200.0		# pk值在线流失时间（秒）
PK_VALUE_PRISON_LESS_TIME					= 600.0			# pk值在监狱流失时间（秒）
PK_GOOSNESS_ADD_TIME						= 600.0			# 善良值在线增加时间（秒）
PK_PEACE_DROP_ODDS							= 0.005			# 白名状态掉落装备概率
PK_REDNAME_DROP_ODDS						= 0.05			# 红名状态掉落装备概率
PK_FIGHT_BACK_TIME							= 9.0			# pk反击持续时间（秒）
PLAYER_CAN_BE_ATTACK_PK_VALUE_MIN			= 17			# 玩家被卫兵攻击的最小PK值


# --------------------------------------------------------------------
# 法宝充值物品
# --------------------------------------------------------------------
TALISMAN_ADD_LIFE_TIME 						= 2592000		# 女娲石充值时间（秒）/（30天）

# --------------------------------------------------------------------
# 天降宝盒掉落类型定义
# --------------------------------------------------------------------
LUCKY_BOX_DROP_NORMAL_ITEM					= 0
LUCKY_BOX_DROP_EQUIP						= 1
LUCKY_BOX_DROP_MONEY						= 2
LUCKY_BOX_DROP_POTENTIAL					= 3
LUCKY_BOX_DROP_EXP							= 4
HONOR_ITEM									= 5				#荣誉度物品

#镖车产生劫匪的ID
DART_MONSTERSID = [20111003,20121002,20131001,20141001,20151001,]


TEAM_GAIN_EXP_RANGE					= 100			# 距离，表示组队杀怪，离怪物死亡点多远的队员可获得经验。

# 影响组队跟随的效果状态列表
TEAM_FOLLOW_EFFECT_LIST = [ csdefine.EFFECT_STATE_SLEEP, csdefine.EFFECT_STATE_VERTIGO, csdefine.EFFECT_STATE_FIX ]
# 组队跟随行为限制字
FOLLOW_STATES_ACT_WORD = csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_PK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_FIGHT | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_CALL_PET

TEAM_FOLLOW_TRANSPORT_DISTANCE = 20				# 米，组队跟随传送的半径


#角色状态
state_dict = {csdefine.ENTITY_STATE_FREE	:cschannel_msgs.ROLE_STATE_FREE,
			csdefine.ENTITY_STATE_DEAD		: cschannel_msgs.ROLE_STATE_DIE,
			csdefine.ENTITY_STATE_REST		: cschannel_msgs.ROLE_STATE_XIUXI,
			csdefine.ENTITY_STATE_FIGHT		: cschannel_msgs.ROLE_STATE_FIGHT,
			csdefine.ENTITY_STATE_PENDING	: cschannel_msgs.ROLE_STATE_WEIJUE,
			csdefine.ENTITY_STATE_HANG		: cschannel_msgs.ROLE_STATE_GUAIQI,
			csdefine.ENTITY_STATE_VEND		: cschannel_msgs.ROLE_STATE_BAITAN,
			csdefine.ENTITY_STATE_RACER		: cschannel_msgs.ROLE_STATE_BISAI,
			csdefine.ENTITY_STATE_CHANGING	: cschannel_msgs.ROLE_STATE_BIANSHEN,
			csdefine.ENTITY_STATE_QUIZ_GAME	: cschannel_msgs.ROLE_STATE_WENDA,
			csdefine.ENTITY_STATE_PICK_ANIMA: cschannel_msgs.ROLE_STATE_PICK_ANIMA,
			csdefine.ENTITY_STATE_MAX		: "MAX"
			}

BENEFIT_SKILL_ID		= 122184001	# 累计在线时间奖励技能id
BENIFIT_PERIOD		=	5 * 3600		# 单位：秒。玩家累计在线时间达到，可获得奖励

LT_SENDNUM			= 4 #锦囊一次发送物品的个数

JING_WU_SHI_KE_ENTER = 780023001					# 劲舞时刻，进入舞厅施放技能
JING_WU_SHI_KE_LEAVE = 780024001					# 劲舞时刻，离开舞台施放技能

JING_WU_SHI_KE_BUFF = 22017							# 劲舞时刻buff，标志他在舞厅中
JING_WU_SHI_KE_SINGLE_DANCE_SKILL = 780026001		# 劲舞时刻，单人舞蹈技能
JING_WU_SHI_KE_DOUBLE_DANCE_SKILL = 780027001		# 劲舞时刻，双人舞蹈技能
JING_WU_SHI_KE_TEAM_DANCE_SKILL = 780031001			# 劲舞时刻，组队舞蹈技能
JING_WU_SHI_KE_SINGLE_DANCE_BUFF  = 99011			# 劲舞时刻，单人舞蹈buff
JING_WU_SHI_KE_DOUBLE_DANCE_BUFF  = 99012			# 劲舞时刻，双人舞蹈buff
JING_WU_SHI_KE_TEAM_DANCE_BUFF  = 99017				# 劲舞时刻，组队舞蹈buff
JING_WU_SHI_KE_DANCE_BUFF = 99014					# 劲舞时刻，跳舞时间buff
JING_WU_SHI_KE_TIAO_WU_YAO_JUE_BUFF = 22121			# 劲舞时刻，跳舞要诀buff
JING_WU_SHI_KE_WU_WANG_MI_JUE_BUFF = 22122			# 劲舞时刻，舞王秘诀buff

JING_WU_SHI_KE_TEAM_RANGE = 10						# 组队跳舞一定范围内
JING_WU_SHI_KE_MAX_POINT_ONE_DAY = 30				# 劲舞时刻，一天最大累积积分
JING_WU_SHI_KE_MAX_POINT		 = 2000				# 劲舞时刻，最大累积积分
JING_WU_SHI_KE_POINT_SKILL		 = 780032001		# 劲舞时刻，积分技能
JING_WU_SHI_KE_POINT_BUFF		 = 22123			# 劲舞时刻，积分buff

FA_SHU_JIN_ZHOU_BUFF	= 299017 					# 法术禁咒buff

SUIT_EQUIP_LIMIT = 7    #套装装备数目
INSTENSIFY_BROADCAST_LEVEL = 7		#装备强化的产生信息等级
SUTD_BROADCAST_LEVEL = 60	#镶嵌水晶的产生信息等级

SPACE_COPY_CLOSE_CBID			= 	12456874				# 副本没有玩家，关闭副本专用的TIMER Arg

DARKOFFICE_XL			= 37	# 兴隆势力
DARKOFFICE_CP			= 38	# 昌平势力

DARKOFFICE_NAME			= {
							37	:	cschannel_msgs.DART_INFO_2,
							38	:	cschannel_msgs.DART_INFO_3
						}


TISHOU_ITEM				= 60101071


# --------------------------------------------------------------------
# 切磋
# --------------------------------------------------------------------
QIECUO_NOTIFY_TIME				= 3			# 切磋总提示时间
QIECUO_NOTIFY_INTERVAL_TIME		= 1			# 切磋间隔提示时间
QIECUO_PROJECT_SKILLID			= 780041001	# 切磋无敌保护BUFF
QIECUO_CHECK_INTERVAL_TIME		= 10.0		# 切磋过程检测时间
QIECUO_CONFIRM_TIME				= 18.0		# 切磋邀请者时间确认

# --------------------------------------------------------------------
# 装备修理耐久下降临界点
# --------------------------------------------------------------------
EQUIP_REPAIL_LIMIT = 0.2

# 角色死亡原地复活后，寻找陷阱的最大范围
REVIVE_ON_ORIGIN_RANGE = 30.0


#---------
#同一天，同一个玩家可以在不同区域进行活动的相关定义
#---------
ACTIVITY_AREA_FLAGS = {"xin_ban_xin_shou_cun"	: 0,
						"feng_ming_cheng"		: 1,
						"fengming"				: 2,
						"zly_ban_quan_xiang"	: 3,
						"zly_ying_ke_cun"		: 4,
						"zly_bi_shi_jian"		: 5,
						"yun_meng_ze_01"		: 6,
						"yun_meng_ze_02"		: 7,
						"peng_lai"				: 8,
						"kun_lun"				: 9,
						"xin_fei_lai_shi_001"	: 10,
						}

#帮会赛马凭证
TONG_RACE_ITEM = 50101062

# 角色可学习生活技能数量上限 by 姜毅
LIVING_SKILL_NUM_MAX	=	5



HONOR_RECOVER_TIME		=   360
HONOR_RECOVER_VALUE		= 	1

#替售NPC模型
tsNpcs = { 1 : csconst.TI_SHOU_MODEL_1,
			2: csconst.TI_SHOU_MODEL_2,
			3: csconst.TI_SHOU_MODEL_3,
			4: csconst.TI_SHOU_MODEL_4,
			5: csconst.TI_SHOU_MODEL_5,
			6: csconst.TI_SHOU_MODEL_6,
			7: csconst.TI_SHOU_MODEL_7,
			}

# --------------------------------------------------------------------
# 赛马速度
# --------------------------------------------------------------------
HORSE_MOVE_SPEED_PERCENT		= 0.5

TEACH_KILL_MONSTER_DROP_ITEM = 60101105		# 师徒副本boss掉落物品

TEACH_MASTER_EVERYDAY_REWARD_SKILLID = 322262002	# 师父每日师徒奖励技能id
TEACH_PRENTICE_EVERYDAY_REWARD_SKILLID = 322262001	# 徒弟每日师徒奖励技能id

# --------------------------------------------------------------------
# 组队采集
# --------------------------------------------------------------------
FRIEND_COLLECT_MEM_NUM = 2		# 队伍人数要求
FRIEND_COLLECT_RANGE = 50.0		# 队员范围要求
FRIEND_COLLECT_LEVEL = 10			# 队员等级要求


TANABATA_QUIZ_LEVEL_LIMIT				= 20		# 七夕情感问答最小级别限制
TANABATA_QUIZ_TEAMMATE_DISTANCE			= 20		# 七夕情感问答队友有效距离
TANABATA_QUIZ_REWARD_ITEM				= 50202078	# 七夕情感问答正确时奖励的物品id
TANABATA_QUIZ_DAY_QUESTIONS_COUNT		= 20		# 七夕情感问答每天的题目数量

# --------------------------------------------------------------------
# 引导技能打断
# --------------------------------------------------------------------
INTERRUPTED_BASE_TYPE = set( [
								csdefine.BASE_SKILL_TYPE_MAGIC,
								csdefine.BASE_SKILL_TYPE_PHYSICS,
							] )

# --------------------------------------------------------------------
# 角色解除潜行Buff后，寻找陷阱的最大范围 by 陈晓鸣 2010-09-28
# --------------------------------------------------------------------
ON_REMOVE_BUFF_PROWL_RANGE= 30.0

# --------------------------------------------------------------------
# 移动类型
# --------------------------------------------------------------------
MOVE_TYPE_STOP			= 0		# 处于没有移动中
MOVE_TYPE_DEFAULE		= 1			# 处于向指定点移动
MOVE_TYPE_CHASE			= 2			# 处于追击目标移动
MOVE_TYPE_PATROL		= 3			# 处于巡逻移动
MOVE_TYPE_BACK			= 4			# 处于击退移动
MOVE_TYPE_ROUND			= 5			# 处于游荡移动


# 玩家帮会城市占领的消费贡献度折扣
TONG_HOLD_CITY_CONTRIBUT_DISCOUNT = 0.8

# --------------------------------------------------------------------
# 剧情副本各职业对应模型编号
# --------------------------------------------------------------------
JUQING_MODELNUM_MAPS = {	csdefine.GENDER_MALE | csdefine.CLASS_FIGHTER		:	"gw1372_1",
							csdefine.GENDER_MALE | csdefine.CLASS_SWORDMAN		:	"gw1372_2",
							csdefine.GENDER_MALE | csdefine.CLASS_ARCHER		:	"gw1372_3",
							csdefine.GENDER_MALE | csdefine.CLASS_MAGE			:	"gw1372_4",

							csdefine.GENDER_FEMALE | csdefine.CLASS_FIGHTER		:	"gw1373_1",
							csdefine.GENDER_FEMALE | csdefine.CLASS_SWORDMAN	:	"gw1373_2",
							csdefine.GENDER_FEMALE | csdefine.CLASS_ARCHER		:	"gw1373_3",
							csdefine.GENDER_FEMALE | csdefine.CLASS_MAGE		:	"gw1373_4",
}


# --------------------------------------------------------------------
# 夜战凤栖副本各职业对应模型编号
# --------------------------------------------------------------------
YEZHAN_MODELNUM_MAPS = {	csdefine.GENDER_MALE | csdefine.CLASS_FIGHTER		:	"gwm2111_1",
							csdefine.GENDER_MALE | csdefine.CLASS_SWORDMAN		:	"gwm2711_1",
							csdefine.GENDER_MALE | csdefine.CLASS_ARCHER		:	"gwm2311_1",
							csdefine.GENDER_MALE | csdefine.CLASS_MAGE			:	"gwm2511_1",

							csdefine.GENDER_FEMALE | csdefine.CLASS_FIGHTER		:	"gwm2211_1",
							csdefine.GENDER_FEMALE | csdefine.CLASS_SWORDMAN	:	"gwm2811_1",
							csdefine.GENDER_FEMALE | csdefine.CLASS_ARCHER		:	"gwm2411_1",
							csdefine.GENDER_FEMALE | csdefine.CLASS_MAGE		:	"gwm2611_1",
}

FIGHT_CHECK_TIMER			= 8				# 战斗检测时间

# --------------------------------------------------------------------
# 盘古守护系统相关
# --------------------------------------------------------------------
ROLE_INIT_ACCUM_POINT 			= 300					# 玩家进入星际地图，获得初始气运值

# 盘古守护模式对应技能
PGNAGUAL_ACTION_FOLLOW_SKILLID 	= 323243001 			# 跟随
PGNAGUAL_ACTION_ATTACK_SKILLID 	= 323244001 			# 攻击
PGNAGUAL_NEAR_GROUP_SKILLID 	= 323245001 			# 近战群体类盘古守护使用技能
PGNAGUAL_NEAR_SINGLE_SKILLID 	= 323246001 			# 近战单体类盘古守护使用技能
PGNAGUAL_FAR_PHYSIC_SKILLID 	= 323247001 			# 远程物理类盘古守护使用技能
PGNAGUAL_FAR_MAGIC_SKILLID 		= 323248001 			# 远程法术类盘古守护使用技能

#允许客户端设置的最大AOI值
MAX_AOI_RANGE = 200.0

# 道行修正参数
DAOHENG_AMEND_RATE				= 1.0


#水域加速值
WATER_SPEED_ACCELERATE = 3.0 * csconst.FLOAT_ZIP_PERCENT

ROUND_SPEED			   = [ 5, 7 ] # 怪物游荡行为速度值
ROUND_MIN_DIS			= 2  # 最小游荡距离（与目标的距离）
ROUND_MAX_DIS			= 10 # 最大游荡距离（与目标的距离）
ROUND_TIME_LIMIT		= 4
ROUND_NEAR_OR_FAR_MAX_ANGLE			= 90.0	# 最大的靠近或者远离角度偏移
BACK_SPEED				= [ 4, 5 ]

SPACE_COPY_GLOBAL_KEY = {
	csdefine.SPACE_TYPE_SHEN_GUI_MI_JING 	: "SGK_SHEN_GUI_MI_JING",
	csdefine.SPACE_TYPE_XIE_LONG_DONG_XUE	: "SGK_XIE_LONG_DONG_XUE",
	csdefine.SPACE_TYPE_WU_YAO_QIAN_SHAO	: "SGK_WU_YAO_QIAN_SHAO",
	csdefine.SPACE_TYPE_WU_YAO_WANG_BAO_ZANG	: "SGK_WU_YAO_WANG_BAO_ZANG",
	csdefine.SPACE_TYPE_YXLM				: "SGK_YXLM",
	csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN		: "SGK_SHE_HUN_MI_ZHEN",
	csdefine.SPACE_TYPE_PIG					: "SGK_DU_DU_ZHU",
}

GET_SPACE_COPY_GLOBAL_KEY = lambda stype, tid, deff : "%s_%i_%s"%( SPACE_COPY_GLOBAL_KEY[ stype ], tid, deff )

# SpawnPoint
SPAWN_ON_SERVER_START = 100001
SPAWN_ON_MONSTER_DIED = 100002

#combo计数多久后清0
COMBO_COUNT_CLEAR_TIME = 2.0
COMBO_COUNT_MAX        = 65535

#玩家升级触发范围伤害技能
ROLE_SKILL_IDS_ON_LEVEL_UP  = {
	csdefine.CLASS_FIGHTER   :  "322550",
	csdefine.CLASS_SWORDMAN	 :  "322551",
	csdefine.CLASS_ARCHER    :  "322552",
	csdefine.CLASS_MAGE		 :  "322553",
}

#建筑物创建时触发技能
ENTITY_CREATE_TRIGGER_SKILL_ID = 780049001

# space copy timer arg
SPACE_TIMER_ARG_CLOSE = 1000 # 关闭副本
SPACE_TIMER_ARG_KICK  = 1001 # 踢离所有副本玩家
SPACE_TIMER_ARG_LIFE  = 1002 # 副本时间

#善良值满时增加御敌点数
GOODNESS_ADD_REDUCE_ROLE_DAMAGE = 325

#帮会等级带来的御敌点数变化
TONG_ADD_REDUCE_ROLE_DAMAGE = { 3:400, 4:500, 5:650 }

# 自动掷筛子的时间
AUTO_THROW_SIEVE_TIME = 5.0

#转向的最小角度
ROTATE_MIN_ANGLE = 0.26

#悬赏任务个数
REWARD_QUEST_NUM = 2

#悬赏任务小类别的任务个数
REWARD_QUEST_SMALL_TYPE_NUM = 1

#进入地图后，触发NPC可接任务的最大距离
ENTER_SPACE_AUTO_ACCEPT_QUEST_DISTANCE = 10.0


#一天24小时
ONE_DAY_HOUR = 24

#暗影之门参加等级
AN_YING_ZHI_MENG_LEVEL = 10			#暗影之门玩家等级要求
AN_YING_ZHI_MENG_DISTANCE = 30.0			#暗影之门搜索队伍成员范围

TELEPORT_PLANE_TOPSPEED_LIMIT		= 1000				# 位面传送时的topSpeed上限
TELEPORT_PLANE_SKILLID				= 860022001		# 位面传送改变topspeed的技能id

#SET_TEMP_KEY( 设置临时变量key )
QUEST_SLOTS_MULTIPLE_KEY = "QUEST_SLOTS_MULTIPLE_KEY_%s"
QUEST_AUTO_OPEN_NEXT_KEY = "QUEST_AUTO_OPEN_NEXT_KEY"

# -----------------------------------------------------
# new space copy CopyTemplate timer arg
# 新副本机制下添加timer可以配置在 xml 文件里，参考 CopyStageActions:CopyStageAction12
# 配置人员可自定义一个任何 （0, 10000） 的整数作为timer的 useArg
# 而这里的 timer 并不想让配置人员知晓，故用负数表示
# 目前只发现一个关闭副本的 timer 需要这样
# 后续如有不想让配置人员知晓的 timer都可以放在这里。

# -----------------------------------------------------
SPACE_TIMER_USER_ARG_MAX		= 10000			# 配置人员在一个副本中可自定义的最大 timer useArg

# 以下是会在程序中直接添加的 timer，并不想让配置人员知晓的。
# 副本共有
SPACE_TIMER_ARG_CLOSE_SPACE		= -1
# 防守副本特有
SPACE_TIMER_ARG_FANG_SHOU_DELAY_SPAWN_MONSTER 	= 	-1001		# 防守副本延迟 1 秒刷怪 timer


# 防守副本
COPY_FANG_SHOU_MONSTER_WAVE_MAX			= 12							# 防守副本最大怪物波次
COPY_FANG_SHOU_FIRST_BOSS_WAVE			= 6								# 防守副本第一个BOSS出现波次
COPY_FANG_SHOU_SECOND_BOSS_WAVE			= 12							# 防守副本第二个BOSS出现波次
COPY_FANG_SHOU_AREA_FIRST				= "fu_ben_fang_shou_area_1"		# 防守副本区域一
COPY_FANG_SHOU_AREA_SECOND				= "fu_ben_fang_shou_area_2"		# 防守副本区域二
COPY_FANG_SHOU_AREA_THRID				= "fu_ben_fang_shou_area_3"		# 防守副本区域三
COPY_FANG_SHOU_AREA_FORTH				= "fu_ben_fang_shou_area_4"		# 防守副本区域四
COPY_FANG_SHOU_CHECK_POSITION_CYCLE		= 0.5							# 防守副本检查玩家位置的时间周期
COPY_FANG_SHOU_AERA_POS_Z_FIRST			= -1							# 防守副本第一、二区域边界 z 坐标
COPY_FANG_SHOU_AERA_POS_Z_SECOND		= -85.5							# 防守副本第二、三区域边界 z 坐标
COPY_FANG_SHOU_AERA_POS_Z_THRID			= -163							# 防守副本第三、四区域边界 z 坐标
COPY_FANG_SHOU_BUFF_SPELLS				= {
											COPY_FANG_SHOU_AREA_FIRST	:	( 123735001, 123726001, 123730001 ),	# 防守副本区域一的buff技能
											COPY_FANG_SHOU_AREA_SECOND	:	( 123734001, 123727001, 123731001 ),	# 防守副本区域二的buff技能
											COPY_FANG_SHOU_AREA_THRID	:	( 123733001, 123728001, 123732001 ),	# 防守副本区域三的buff技能
											COPY_FANG_SHOU_AREA_FORTH	:	( 123729001, ),							# 防守副本区域四的buff技能
										}
COPY_FANG_SHOU_CLEAR_BUFF_SPELLS		= ( 123736001, 123739001, 123742001 )										# 清除防守副本增益 Buff 的技能
COPY_FANG_SHOU_LAST_TIME				= 1800																		# 防守副本持续时间
COPY_FANG_SHOU_MONSTER_TOTALS			= 100																		# 防守副本小怪总数
COPY_FANG_SHOU_BOSS_TOTALS				= 2																			# 防守副本BOSS总数
COPY_FANG_SHOU_EACH_WAVE_TIME			= 60																		# 防守副本每波怪物间隔时间
COPY_FANG_SHOU_SPECAIL_ITEMS			= ( 40401034, 40401035, 40401036, 40401037, 40401038 )						# 防守副本特殊道具id列表

#NPCMonster领域范围以及视野范围警戒值
TERRITORY_LIMIT = 100				#领域范围上限值
VIEWRANGE_LIMIT = 100				#视野范围上限值

ACTIVITY_STOP_MOVE_SKILL = 721037001	#通用活动禁止移动BUFF
