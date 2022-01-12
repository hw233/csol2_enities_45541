# -*- coding: gb18030 -*-

# $Id: Const.py,v 1.25 2008-08-15 03:58:51 kebiao Exp $


"""
locates base constants

2005.06.06 : tidied up by huangyongwei
"""

import _md5
import cschannel_msgs
import ShareTexts as ST
import csdefine

# --------------------------------------------------------------------
# about role's attributes( from cell/AttrDefine.py；designed by penghuawei )
# --------------------------------------------------------------------
g_newBornGratuities = {}									# 默认的初始赠送技能和物品等

g_newBornGratuities[csdefine.CLASS_FIGHTER] = {
		"skills"	: [323175001,350100001,312134001,322361002],
		}

g_newBornGratuities[csdefine.CLASS_SWORDMAN] = {
		"skills"	: [311338001,360100001,311339001,322361002],
		}

g_newBornGratuities[csdefine.CLASS_ARCHER] = {
		"skills"	: [323155001,321210001,323283001,322361002],
		}

g_newBornGratuities[csdefine.CLASS_MAGE] = {
		"skills"	: [323147001,322718001,323189001,322361002],
		}


# --------------------------------------------------------------------
# about space( from base/SpaceNormal.py；designed by panguankong )
# --------------------------------------------------------------------
SPACE_LIFECYCLE_HEARTBEAT			= 60			# space 的生命周期的心跳

# --------------------------------------------------------------------
# about friend( wsf )
# --------------------------------------------------------------------
FRIEND_FRIEND_MAX_COUNT 			= 200 			# 好友最大数量( 原名：FRIEND_MAX_COUNT )
FRIEND_BLACKLIST_MAX_COUNT 			= 100 			# 黑名单数量( 原名：BLACKLIST_MAX_COUNT )
FRIEND_GROUP_MAX_COUNT 				= 7 			# 组的最大数量( 原名：GROUP_MAX_COUNT )
FRIEND_LETTER_TIME_OUT				= 3*24*3600		# 好友留言过时时间，单位为秒。
FRIEND_LETTER_MAX_COUNT				= 100			# 好友留言的最大数量

RELATION_ADMIRE_NOTIFY_INTERVAL 		= 1 			# 通知仰慕者时间间隔
RELATION_ADMIRE_COUNT_NOTIFY			= 10			# 每秒通知仰慕者的个数


# --------------------------------------------------------------------
# about corps( from base/Corps.py；designed by panguankong )
# --------------------------------------------------------------------
CORPS_SUE_FOR_PEACE_DURATION		= 600			# 军团求和信息保留时间( 原名：PEACE_KEEP_TIME )
CORPS_SUE_FOR_PEACE_HEARTBEAT 		= 600 			# 求和计时心跳( 原名：PEACE_MSG_CALCULATE_HEARTBEAT )

CORPS_SKILL_DEVELOP_HEARTBEAT		= 3				# 技能研发心跳( 原名：RESEARCH_SKILL_HEARTBEAT )
CORPS_SKILL_MAX_LEVEL				= 10			# 军团技能的最大等级( 原名：CORPS_LEVEL_MAX －－这样写就让人错误理解成军团的最大等级，而不是军团技能的最大等级 )

CORPS_BATTLE_DETECT_HEARTBEAT 		= 300 			# 宣战计时心跳( 原名：ENEMY_MSG_CALCULATE_HEARTBEAT －－敌人信息计算心跳，计算完全没必要写出，因为心跳已经包含计算的意味 )
CORPS_LEAGUE_DETECT_HEARTBEAT		= 300			# 结盟计时心跳( 原名：ALLY_MSG_CALCULATE_HEARTBEAT )

# 战斗公式基数
class CombatRadix:
	"""
	角色战斗相关参数
	"""
	def __init__( self, **argw ):
		"""
		"""
		self.strength = 0 #力量(int)
		self.dexterity = 0 #敏捷(int)
		self.intellect = 0 #智力(int)
		self.corporeity = 0 #体质(int)
		self.strength_value = 0 #力量每级加值(float)
		self.dexterity_value = 0 #敏捷每级加值(float)
		self.intellect_value = 0.0 #智力每级加值(float)
		self.corporeity_value = 0.0 #体质每级加值(float)
		self.HP_regen_base = 0.0 #HP恢复值(float)
		self.MP_regen_base = 0.0 #MP恢复值(float)
		# init
		self.__dict__.update( argw )

# 各职业战斗公式基数
ROLE_COMBAT_RADIX = {
		# 战士
		csdefine.CLASS_FIGHTER	:	CombatRadix(
											strength = 13, #力量(int)
											dexterity = 7, #敏捷(int)
											intellect = 4, #智力(int)
											corporeity = 16, #体质(int)
											strength_value = 2.0, #力量每级加值(float)
											dexterity_value = 1.0, #敏捷每级加值(float)
											intellect_value = 1.0, #智力每级加值(float)
											corporeity_value = 2.5, #体质每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											),
		# 剑客
		csdefine.CLASS_SWORDMAN	:	CombatRadix(
											strength = 10, #力量(int)
											dexterity = 10, #敏捷(int)
											intellect = 9, #智力(int)
											corporeity = 11, #体质(int)
											strength_value = 1.5, #力量每级加值(int)
											dexterity_value = 1.5, #敏捷每级加值(int)
											intellect_value = 1.5, #智力每级加值(float)
											corporeity_value = 1.5, #体质每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											),
		# 射手
		csdefine.CLASS_ARCHER		:	CombatRadix(
											strength = 10, #力量(int)
											dexterity = 13, #敏捷(int)
											intellect = 6, #智力(int)
											corporeity = 11, #体质(int)
											strength_value = 1.5, #力量每级加值(int)
											dexterity_value = 2.5, #敏捷每级加值(int)
											intellect_value = 1.0, #智力每级加值(float)
											corporeity_value = 1.5, #体质每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											),
		# 法师
		csdefine.CLASS_MAGE		:	CombatRadix(
											strength = 6, #力量(int)
											dexterity = 6, #敏捷(int)
											intellect = 18, #智力(int)
											corporeity = 10, #体质(int)
											strength_value = 0.5, #力量每级加值(int)
											dexterity_value = 1.0, #敏捷每级加值(int)
											intellect_value = 3.5, #智力每级加值(float)
											corporeity_value = 1.0, #体质每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											),
		# 巫师
		csdefine.CLASS_WARLOCK	:	CombatRadix(
											strength = 0, #力量(int)
											dexterity = 0, #敏捷(int)
											intellect = 0, #智力(int)
											corporeity = 0, #体质(int)
											strength_value = 0.0, #力量每级加值(float)
											dexterity_value = 0.0, #敏捷每级加值(float)
											intellect_value = 0.0, #智力每级加值(float)
											corporeity_value = 0.0, #体质每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											),
		# 祭师
		csdefine.CLASS_PRIEST		:	CombatRadix(
											strength = 0, #力量(int)
											dexterity = 0, #敏捷(int)
											intellect = 0, #智力(int)
											corporeity = 0, #体质(int)
											strength_value = 0.0, #力量每级加值(float)
											dexterity_value = 0.0, #敏捷每级加值(float)
											intellect_value = 0.0, #智力每级加值(float)
											corporeity_value = 0.0, #体质每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											),
	}	# end of ROLE_COMBAT_RADIX

def calcIntellect( classes, level ):
	"""
	计算智力
	"""
	v = ROLE_COMBAT_RADIX[classes].intellect
	v_value = ROLE_COMBAT_RADIX[classes].intellect_value
	intellect_base =  v + v_value * ( level - 1 )
	return intellect_base

def calcCorporeity( classes, level ):
	"""
	计算体质
	"""
	v = ROLE_COMBAT_RADIX[classes].corporeity
	v_value = ROLE_COMBAT_RADIX[classes].corporeity_value
	corporeity_base =  v + v_value * ( level - 1 )
	return corporeity_base

#------------------------------------计算 HP MP---------------------------------------------------------------

class FighterFunc:
	def __init__( self ):
		"""
		"""
		pass

	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return calcCorporeity( classes, level )  * 10

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return calcIntellect( classes, level ) * 5

class SwordmanFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return calcCorporeity( classes, level ) * 6

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return calcIntellect( classes, level ) * 6

class ArcherFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return calcCorporeity( classes, level ) * 6

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return calcIntellect( classes, level ) * 6

class MageFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return calcCorporeity( classes, level ) * 5

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return calcIntellect( classes, level ) * 10

# 各职业战斗公式基数
ENTITY_COMBAT_BASE_EXPRESSION = {
		# 战士
		csdefine.CLASS_FIGHTER	:	FighterFunc(),
		# 剑客
		csdefine.CLASS_SWORDMAN	:	SwordmanFunc(),
		# 射手
		csdefine.CLASS_ARCHER		:	ArcherFunc(),
		# 法师
		csdefine.CLASS_MAGE		:	MageFunc(),
		# 巫师
		csdefine.CLASS_WARLOCK	:	FighterFunc(),
		# 祭师
		csdefine.CLASS_PRIEST		:	FighterFunc(),
		# 强防战士
		csdefine.CLASS_PALADIN	:	FighterFunc(),
	}	# end of ROLE_COMBAT_RADIX

def calcHPMax( classes, level ):
	"""
	计算hp的基础值

	@param classes: 种族，如FIGHT等
	"""
	return ENTITY_COMBAT_BASE_EXPRESSION[ classes ].calcRoleHPMaxBase( classes, level )

def calcMPMax( classes, level ):
	"""
	计算hp的基础值

	@param classes: 种族，如FIGHT等
	"""
	return ENTITY_COMBAT_BASE_EXPRESSION[ classes ].calcRoleMPMaxBase( classes, level )

TONG_DUTY_NAME = [
	{ "duty" : csdefine.TONG_DUTY_CHIEF,  				"dutyName" 	:	cschannel_msgs.TONG_ZHIYE_BANG_ZHU },
	{ "duty" : csdefine.TONG_DUTY_DEPUTY_CHIEF, 		"dutyName"	:	cschannel_msgs.TONG_ZHIYE_FU_BANG_ZHU },
	{ "duty" : csdefine.TONG_DUTY_TONG,  				"dutyName"	:	cschannel_msgs.TONG_ZHIYE_TANG_ZHU },
	{ "duty" : csdefine.TONG_DUTY_MEMBER,  				"dutyName"	:	cschannel_msgs.TONG_ZHIYE_LOU_LUO },
]

"""
职位	1级帮会	2级帮会	3级帮会	4级帮会	5级帮会
帮主日工资	20000	30000	40000	50000	60000
副帮主日工资	10000	20000	30000	40000	50000
"""
TONG_CHIEF_WAGE = {
	"chief" : {
				1:20000, 2:30000, 3:40000, 4:50000,	5:60000, 6:70000, 7:80000, 8:90000, 9:100000, 10:110000,
	},
	"adjutantChief" : {
				1:10000, 2:20000, 3:30000, 4:40000,	5:50000, 6:60000, 7:70000, 9:80000, 9:90000, 10:100000,
	}
}


"""
帮会等级	1级	2级	3级	4级	5级
商人最大数量	3个	5个	7个	9个	10个
暂时没有用了，改为限时活动了，因此去掉这个配置
TONG_DEALER_COUNT = {
	1 : 3,
	2 : 5,
	3 : 7,
	4 : 9,
	5 : 10,
}
"""
# 帮会资金下限和上限
TONG_MONEY_LIMIT = {
	1 : ( 100000, 20000000 ),
	2 : ( 1000000, 50000000 ),
	3 : ( 2000000, 100000000 ),
	4 : ( 2500000, 300000000 ),
	5 : ( 3000000, 1000000000 ),
	6 : ( 3500000, 1000000000 ),
	7 : ( 4000000, 1000000000 ),
	8 : ( 4500000, 1000000000 ),
	9 : ( 5000000, 1000000000 ),
	10 : ( 5500000, 1000000000 ),
}

TONG_INITIAL_MOBILITY		= 100		# 帮会初始行动力

# 角色初始化快捷栏数据
ROLE_INIT_QUICKBAR_DATA = {
		# 战士
		csdefine.CLASS_FIGHTER:
			{
				0 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_NU_JI ),
				1 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_TIAN_BENG_ZHAN ),
				12 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
				csdefine.QB_AUTO_SPELL_INDEX : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_NU_JI ),
				91 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_NU_JI ),
				92 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_TIAN_BENG_ZHAN ),
				103 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
			},
		# 剑客
		csdefine.CLASS_SWORDMAN:
			{
				0 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_QU_ZHE_JIAN ),
				1 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_KUAI_JIAN ),
				12 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
				csdefine.QB_AUTO_SPELL_INDEX : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_QU_ZHE_JIAN ),
				117 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_QU_ZHE_JIAN ),
				118 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_KUAI_JIAN ),
				129 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
			},
		# 射手
		csdefine.CLASS_ARCHER:
			{
				0 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_SAN_SHE ),
				1 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_LUO_RI ),
				12 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
				csdefine.QB_AUTO_SPELL_INDEX : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_SAN_SHE ),
				169 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_SAN_SHE ),
				170 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_LUO_RI ),
				181 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
			},
		# 法师
		csdefine.CLASS_MAGE:
			{
				0 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_ZHANG_JI ),
				1 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_BAO_LIE_HUO_QIU ),
				12 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
				csdefine.QB_AUTO_SPELL_INDEX : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_ZHANG_JI ),
				221 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_ZHANG_JI ),
				222 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_BAO_LIE_HUO_QIU ),
				233 : ( csdefine.QB_ITEM_SKILL, 0, cschannel_msgs.SKILL_DES_CHUAN_SONG ),
			},
}

LOGIN_ACCOUNT_LIMIT						= 500		# 游戏所有服务器同时登录的人数上限
LOGIN_CALCULATE_TIME_INTERVAL			= 30.0		# 秒，登录等待计算等待时间的有效期限
LOGIN_REFLESH_WAIT_TIME_INTERVAL	= 3.0		# 刷新等待时间的间隔
BASEAPP_PLAYER_COUNT_LIMIT				= 420		# 一个baseApp允许最大的Role在线数量
LOGIN_ATTEMPER_WAIT_LIMIT				= 1000		# 等待队列长度限制

# 玩家account entity状态
ACCOUNT_INITIAL_STATE					= 0		# 初始状态
ACCOUNT_WAITTING_STATE					= 1		# 等待状态
ACCOUNT_LOGIN_STATE						= 2		# 正在登录中
ACCOUNT_GAMMING_STATE					= 3		# 游戏中

PREFIX_GBAE_LOGIN_NUM					= "BGAELNUM"		# 注册到globalData的当前baseApp的登录队列数量key前缀。
PREFIX_GBAE_WAIT_NUM					= "BGAEWNUM"	# 注册到globalData的当前baseApp的等待队列数量key前缀。
PREFIX_GBAE_PLAYER_NUM					= "BGAEPNUM"		# 注册到globalData的当前baseApp的玩家数量key前缀。

WEALTH_RANKING_NUM						= 50  #财富统计排名的数量

RELATION_UID_SAND_MAX_COUNT			= 100 # 每次给申请玩家关系UID的baseEntity分配的uid个数。

# SPACE 加载spawn回调 结果
SPACE_LOADSPAWN_RET_OVER				= 0
SPACE_LOADSPAWN_RET_OPEN_FILE_ERROR		= 1
SPACE_LOADSPAWN_RET_NOT_FOUND_FILE		= 2

# 台湾版自动战斗持续时间（8小时）
AUTO_FIGHT_PERSISTENT_TIME_TW		= 28800.0

# -------------------------------------------------------------
# 数据库字段MD5检测相关 by 姜毅
# -------------------------------------------------------------
MD5Checker_Switcher = False

# -------------------------------------------------------------
# 反外挂apex是不是启动 True表示启动，False表示不启动 by LuoCD
# -------------------------------------------------------------
START_APEX_FLAG = True


#---------------------------------------------------------------
#短信和电话密保检测
#---------------------------------------------------------------
PHONE_CHECK_TYPE_MESSAGE		=	1
PHONE_CHECK_VALUE_MESSAGE		=	2
PHONE_CHECK_TYPE_TELEPHONE		=	2
PHONE_CHECK_VALUE_TELEPHONE		=	1

ANTI_ROBOT_INTERVAL = 1800	# 反外挂图片验证时效
ANTI_ROBOT_RATE		= 0.05	# 反外挂图片验证触发概率

# -------------------------------------------------------------
# 生活系统相关 by 姜毅
# -------------------------------------------------------------
VIM_RESET_TIME	=	4 * 3600

# -------------------------------------------------------------
# 老手定时奖励相关 by 姜毅
# -------------------------------------------------------------
OLD_REWARD_REFLASH_TIME	=	24
OLD_REWARD_WAIT_LIM_SECONDS	=	600

# -------------------------------------------------------------
# 帮会活跃度相关 by 柯标
# -------------------------------------------------------------
TONG_ACTIVITY_POINT_TOP_COUNT	= 30	# 最多允许排名30位

# -------------------------------------------------------------
# 帮会会标相关 by 姜毅
# -------------------------------------------------------------
SEND_TONG_SIGN_TIME_TICK		= 5		# 5秒发送一次（处理一个请求）

# -------------------------------------------------------------
# 元宝交易相关 by 姜毅
# -------------------------------------------------------------
YB_TRADE_BILL_LIMIT			= 5		# 每个角色同时存在订单上限

# -------------------------------------------------------------
# 好友聊天
# -------------------------------------------------------------
CHAT_FRIEND_OFL_MSG_CAPACITY	= 20	# 离线消息保存数量


# -------------------------------------------------------------
# 一键换装
# -------------------------------------------------------------
OKS_TIME_INTERVAL = 10		# 时间间隔


#骑宠来源
VEHICLE_SOURCE_INCUBATE  = 1 #孵蛋
VEHICLE_SOURCE_UP_STEEP_LOW  = 2 #升阶低级道具
VEHICLE_SOURCE_UP_STEEP_HIGH  = 3 #升阶高级道具

# -------------------------------------------------------------
# 帮会签到
# -------------------------------------------------------------
TONG_SIGN_UP_TIMES_LIMIT		= 1	 		# 每日签到次数
TONG_SIGN_UP_GAIN_EXP			= 50		# 每次签到获得帮会经验

#暗影之门
AN_YING_ZHI_MENG_TAOISM			= 1			# 仙道阵营BOSS对应的索引
AN_YING_ZHI_MENG_DEMON			= 2			# 魔道阵营BOSS对应的索引
