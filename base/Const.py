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
# about role's attributes( from cell/AttrDefine.py��designed by penghuawei )
# --------------------------------------------------------------------
g_newBornGratuities = {}									# Ĭ�ϵĳ�ʼ���ͼ��ܺ���Ʒ��

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
# about space( from base/SpaceNormal.py��designed by panguankong )
# --------------------------------------------------------------------
SPACE_LIFECYCLE_HEARTBEAT			= 60			# space ���������ڵ�����

# --------------------------------------------------------------------
# about friend( wsf )
# --------------------------------------------------------------------
FRIEND_FRIEND_MAX_COUNT 			= 200 			# �����������( ԭ����FRIEND_MAX_COUNT )
FRIEND_BLACKLIST_MAX_COUNT 			= 100 			# ����������( ԭ����BLACKLIST_MAX_COUNT )
FRIEND_GROUP_MAX_COUNT 				= 7 			# ����������( ԭ����GROUP_MAX_COUNT )
FRIEND_LETTER_TIME_OUT				= 3*24*3600		# �������Թ�ʱʱ�䣬��λΪ�롣
FRIEND_LETTER_MAX_COUNT				= 100			# �������Ե��������

RELATION_ADMIRE_NOTIFY_INTERVAL 		= 1 			# ֪ͨ��Ľ��ʱ����
RELATION_ADMIRE_COUNT_NOTIFY			= 10			# ÿ��֪ͨ��Ľ�ߵĸ���


# --------------------------------------------------------------------
# about corps( from base/Corps.py��designed by panguankong )
# --------------------------------------------------------------------
CORPS_SUE_FOR_PEACE_DURATION		= 600			# ���������Ϣ����ʱ��( ԭ����PEACE_KEEP_TIME )
CORPS_SUE_FOR_PEACE_HEARTBEAT 		= 600 			# ��ͼ�ʱ����( ԭ����PEACE_MSG_CALCULATE_HEARTBEAT )

CORPS_SKILL_DEVELOP_HEARTBEAT		= 3				# �����з�����( ԭ����RESEARCH_SKILL_HEARTBEAT )
CORPS_SKILL_MAX_LEVEL				= 10			# ���ż��ܵ����ȼ�( ԭ����CORPS_LEVEL_MAX ��������д�����˴������ɾ��ŵ����ȼ��������Ǿ��ż��ܵ����ȼ� )

CORPS_BATTLE_DETECT_HEARTBEAT 		= 300 			# ��ս��ʱ����( ԭ����ENEMY_MSG_CALCULATE_HEARTBEAT ����������Ϣ����������������ȫû��Ҫд������Ϊ�����Ѿ������������ζ )
CORPS_LEAGUE_DETECT_HEARTBEAT		= 300			# ���˼�ʱ����( ԭ����ALLY_MSG_CALCULATE_HEARTBEAT )

# ս����ʽ����
class CombatRadix:
	"""
	��ɫս����ز���
	"""
	def __init__( self, **argw ):
		"""
		"""
		self.strength = 0 #����(int)
		self.dexterity = 0 #����(int)
		self.intellect = 0 #����(int)
		self.corporeity = 0 #����(int)
		self.strength_value = 0 #����ÿ����ֵ(float)
		self.dexterity_value = 0 #����ÿ����ֵ(float)
		self.intellect_value = 0.0 #����ÿ����ֵ(float)
		self.corporeity_value = 0.0 #����ÿ����ֵ(float)
		self.HP_regen_base = 0.0 #HP�ָ�ֵ(float)
		self.MP_regen_base = 0.0 #MP�ָ�ֵ(float)
		# init
		self.__dict__.update( argw )

# ��ְҵս����ʽ����
ROLE_COMBAT_RADIX = {
		# սʿ
		csdefine.CLASS_FIGHTER	:	CombatRadix(
											strength = 13, #����(int)
											dexterity = 7, #����(int)
											intellect = 4, #����(int)
											corporeity = 16, #����(int)
											strength_value = 2.0, #����ÿ����ֵ(float)
											dexterity_value = 1.0, #����ÿ����ֵ(float)
											intellect_value = 1.0, #����ÿ����ֵ(float)
											corporeity_value = 2.5, #����ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											),
		# ����
		csdefine.CLASS_SWORDMAN	:	CombatRadix(
											strength = 10, #����(int)
											dexterity = 10, #����(int)
											intellect = 9, #����(int)
											corporeity = 11, #����(int)
											strength_value = 1.5, #����ÿ����ֵ(int)
											dexterity_value = 1.5, #����ÿ����ֵ(int)
											intellect_value = 1.5, #����ÿ����ֵ(float)
											corporeity_value = 1.5, #����ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											),
		# ����
		csdefine.CLASS_ARCHER		:	CombatRadix(
											strength = 10, #����(int)
											dexterity = 13, #����(int)
											intellect = 6, #����(int)
											corporeity = 11, #����(int)
											strength_value = 1.5, #����ÿ����ֵ(int)
											dexterity_value = 2.5, #����ÿ����ֵ(int)
											intellect_value = 1.0, #����ÿ����ֵ(float)
											corporeity_value = 1.5, #����ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											),
		# ��ʦ
		csdefine.CLASS_MAGE		:	CombatRadix(
											strength = 6, #����(int)
											dexterity = 6, #����(int)
											intellect = 18, #����(int)
											corporeity = 10, #����(int)
											strength_value = 0.5, #����ÿ����ֵ(int)
											dexterity_value = 1.0, #����ÿ����ֵ(int)
											intellect_value = 3.5, #����ÿ����ֵ(float)
											corporeity_value = 1.0, #����ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											),
		# ��ʦ
		csdefine.CLASS_WARLOCK	:	CombatRadix(
											strength = 0, #����(int)
											dexterity = 0, #����(int)
											intellect = 0, #����(int)
											corporeity = 0, #����(int)
											strength_value = 0.0, #����ÿ����ֵ(float)
											dexterity_value = 0.0, #����ÿ����ֵ(float)
											intellect_value = 0.0, #����ÿ����ֵ(float)
											corporeity_value = 0.0, #����ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											),
		# ��ʦ
		csdefine.CLASS_PRIEST		:	CombatRadix(
											strength = 0, #����(int)
											dexterity = 0, #����(int)
											intellect = 0, #����(int)
											corporeity = 0, #����(int)
											strength_value = 0.0, #����ÿ����ֵ(float)
											dexterity_value = 0.0, #����ÿ����ֵ(float)
											intellect_value = 0.0, #����ÿ����ֵ(float)
											corporeity_value = 0.0, #����ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											),
	}	# end of ROLE_COMBAT_RADIX

def calcIntellect( classes, level ):
	"""
	��������
	"""
	v = ROLE_COMBAT_RADIX[classes].intellect
	v_value = ROLE_COMBAT_RADIX[classes].intellect_value
	intellect_base =  v + v_value * ( level - 1 )
	return intellect_base

def calcCorporeity( classes, level ):
	"""
	��������
	"""
	v = ROLE_COMBAT_RADIX[classes].corporeity
	v_value = ROLE_COMBAT_RADIX[classes].corporeity_value
	corporeity_base =  v + v_value * ( level - 1 )
	return corporeity_base

#------------------------------------���� HP MP---------------------------------------------------------------

class FighterFunc:
	def __init__( self ):
		"""
		"""
		pass

	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcCorporeity( classes, level )  * 10

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcIntellect( classes, level ) * 5

class SwordmanFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcCorporeity( classes, level ) * 6

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcIntellect( classes, level ) * 6

class ArcherFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcCorporeity( classes, level ) * 6

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcIntellect( classes, level ) * 6

class MageFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcCorporeity( classes, level ) * 5

	def calcRoleMPMaxBase( self, classes, level ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return calcIntellect( classes, level ) * 10

# ��ְҵս����ʽ����
ENTITY_COMBAT_BASE_EXPRESSION = {
		# սʿ
		csdefine.CLASS_FIGHTER	:	FighterFunc(),
		# ����
		csdefine.CLASS_SWORDMAN	:	SwordmanFunc(),
		# ����
		csdefine.CLASS_ARCHER		:	ArcherFunc(),
		# ��ʦ
		csdefine.CLASS_MAGE		:	MageFunc(),
		# ��ʦ
		csdefine.CLASS_WARLOCK	:	FighterFunc(),
		# ��ʦ
		csdefine.CLASS_PRIEST		:	FighterFunc(),
		# ǿ��սʿ
		csdefine.CLASS_PALADIN	:	FighterFunc(),
	}	# end of ROLE_COMBAT_RADIX

def calcHPMax( classes, level ):
	"""
	����hp�Ļ���ֵ

	@param classes: ���壬��FIGHT��
	"""
	return ENTITY_COMBAT_BASE_EXPRESSION[ classes ].calcRoleHPMaxBase( classes, level )

def calcMPMax( classes, level ):
	"""
	����hp�Ļ���ֵ

	@param classes: ���壬��FIGHT��
	"""
	return ENTITY_COMBAT_BASE_EXPRESSION[ classes ].calcRoleMPMaxBase( classes, level )

TONG_DUTY_NAME = [
	{ "duty" : csdefine.TONG_DUTY_CHIEF,  				"dutyName" 	:	cschannel_msgs.TONG_ZHIYE_BANG_ZHU },
	{ "duty" : csdefine.TONG_DUTY_DEPUTY_CHIEF, 		"dutyName"	:	cschannel_msgs.TONG_ZHIYE_FU_BANG_ZHU },
	{ "duty" : csdefine.TONG_DUTY_TONG,  				"dutyName"	:	cschannel_msgs.TONG_ZHIYE_TANG_ZHU },
	{ "duty" : csdefine.TONG_DUTY_MEMBER,  				"dutyName"	:	cschannel_msgs.TONG_ZHIYE_LOU_LUO },
]

"""
ְλ	1�����	2�����	3�����	4�����	5�����
�����չ���	20000	30000	40000	50000	60000
�������չ���	10000	20000	30000	40000	50000
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
���ȼ�	1��	2��	3��	4��	5��
�����������	3��	5��	7��	9��	10��
��ʱû�����ˣ���Ϊ��ʱ��ˣ����ȥ���������
TONG_DEALER_COUNT = {
	1 : 3,
	2 : 5,
	3 : 7,
	4 : 9,
	5 : 10,
}
"""
# ����ʽ����޺�����
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

TONG_INITIAL_MOBILITY		= 100		# ����ʼ�ж���

# ��ɫ��ʼ�����������
ROLE_INIT_QUICKBAR_DATA = {
		# սʿ
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
		# ����
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
		# ����
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
		# ��ʦ
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

LOGIN_ACCOUNT_LIMIT						= 500		# ��Ϸ���з�����ͬʱ��¼����������
LOGIN_CALCULATE_TIME_INTERVAL			= 30.0		# �룬��¼�ȴ�����ȴ�ʱ�����Ч����
LOGIN_REFLESH_WAIT_TIME_INTERVAL	= 3.0		# ˢ�µȴ�ʱ��ļ��
BASEAPP_PLAYER_COUNT_LIMIT				= 420		# һ��baseApp��������Role��������
LOGIN_ATTEMPER_WAIT_LIMIT				= 1000		# �ȴ����г�������

# ���account entity״̬
ACCOUNT_INITIAL_STATE					= 0		# ��ʼ״̬
ACCOUNT_WAITTING_STATE					= 1		# �ȴ�״̬
ACCOUNT_LOGIN_STATE						= 2		# ���ڵ�¼��
ACCOUNT_GAMMING_STATE					= 3		# ��Ϸ��

PREFIX_GBAE_LOGIN_NUM					= "BGAELNUM"		# ע�ᵽglobalData�ĵ�ǰbaseApp�ĵ�¼��������keyǰ׺��
PREFIX_GBAE_WAIT_NUM					= "BGAEWNUM"	# ע�ᵽglobalData�ĵ�ǰbaseApp�ĵȴ���������keyǰ׺��
PREFIX_GBAE_PLAYER_NUM					= "BGAEPNUM"		# ע�ᵽglobalData�ĵ�ǰbaseApp���������keyǰ׺��

WEALTH_RANKING_NUM						= 50  #�Ƹ�ͳ������������

RELATION_UID_SAND_MAX_COUNT			= 100 # ÿ�θ�������ҹ�ϵUID��baseEntity�����uid������

# SPACE ����spawn�ص� ���
SPACE_LOADSPAWN_RET_OVER				= 0
SPACE_LOADSPAWN_RET_OPEN_FILE_ERROR		= 1
SPACE_LOADSPAWN_RET_NOT_FOUND_FILE		= 2

# ̨����Զ�ս������ʱ�䣨8Сʱ��
AUTO_FIGHT_PERSISTENT_TIME_TW		= 28800.0

# -------------------------------------------------------------
# ���ݿ��ֶ�MD5������ by ����
# -------------------------------------------------------------
MD5Checker_Switcher = False

# -------------------------------------------------------------
# �����apex�ǲ������� True��ʾ������False��ʾ������ by LuoCD
# -------------------------------------------------------------
START_APEX_FLAG = True


#---------------------------------------------------------------
#���ź͵绰�ܱ����
#---------------------------------------------------------------
PHONE_CHECK_TYPE_MESSAGE		=	1
PHONE_CHECK_VALUE_MESSAGE		=	2
PHONE_CHECK_TYPE_TELEPHONE		=	2
PHONE_CHECK_VALUE_TELEPHONE		=	1

ANTI_ROBOT_INTERVAL = 1800	# �����ͼƬ��֤ʱЧ
ANTI_ROBOT_RATE		= 0.05	# �����ͼƬ��֤��������

# -------------------------------------------------------------
# ����ϵͳ��� by ����
# -------------------------------------------------------------
VIM_RESET_TIME	=	4 * 3600

# -------------------------------------------------------------
# ���ֶ�ʱ������� by ����
# -------------------------------------------------------------
OLD_REWARD_REFLASH_TIME	=	24
OLD_REWARD_WAIT_LIM_SECONDS	=	600

# -------------------------------------------------------------
# ����Ծ����� by �±�
# -------------------------------------------------------------
TONG_ACTIVITY_POINT_TOP_COUNT	= 30	# �����������30λ

# -------------------------------------------------------------
# �������� by ����
# -------------------------------------------------------------
SEND_TONG_SIGN_TIME_TICK		= 5		# 5�뷢��һ�Σ�����һ������

# -------------------------------------------------------------
# Ԫ��������� by ����
# -------------------------------------------------------------
YB_TRADE_BILL_LIMIT			= 5		# ÿ����ɫͬʱ���ڶ�������

# -------------------------------------------------------------
# ��������
# -------------------------------------------------------------
CHAT_FRIEND_OFL_MSG_CAPACITY	= 20	# ������Ϣ��������


# -------------------------------------------------------------
# һ����װ
# -------------------------------------------------------------
OKS_TIME_INTERVAL = 10		# ʱ����


#�����Դ
VEHICLE_SOURCE_INCUBATE  = 1 #����
VEHICLE_SOURCE_UP_STEEP_LOW  = 2 #���׵ͼ�����
VEHICLE_SOURCE_UP_STEEP_HIGH  = 3 #���׸߼�����

# -------------------------------------------------------------
# ���ǩ��
# -------------------------------------------------------------
TONG_SIGN_UP_TIMES_LIMIT		= 1	 		# ÿ��ǩ������
TONG_SIGN_UP_GAIN_EXP			= 50		# ÿ��ǩ����ð�ᾭ��

#��Ӱ֮��
AN_YING_ZHI_MENG_TAOISM			= 1			# �ɵ���ӪBOSS��Ӧ������
AN_YING_ZHI_MENG_DEMON			= 2			# ħ����ӪBOSS��Ӧ������
