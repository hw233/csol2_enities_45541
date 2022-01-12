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
# about role's attributes( from cell/AttrDefine.py��designed by penghuawei )
# --------------------------------------------------------------------

ROLE_HANDEDS_FREE_RANGE				= int( 2.0 * csconst.FLOAT_ZIP_PERCENT )	# ���ֹ�������( ԭ����EMPTY_HANDED_RANGE )
ROLE_DOUBLE_DAMAGE_EFFECT 			= 200										# ����һ��Ч����Ĭ��ȫ����������1���˺���������2��(200%)���˺�( ԭ����DOUBLE_DAMAGE_EFFECT )

if csdefine.IS_GREEN_VERSION == 0:
	ROLE_MOVE_SPEED_RADIX				= int( 5.0 * csconst.FLOAT_ZIP_PERCENT )	# �ƶ��ٶȣ�����float( ԭ����MOVE_SPEED_RADIX )
else:
	ROLE_MOVE_SPEED_RADIX				= int( 8.0 * csconst.FLOAT_ZIP_PERCENT )	# �ƶ��ٶȣ�����float( ԭ����MOVE_SPEED_RADIX )

ROLE_MAX_RESIST_NATURE 				= 95										# �����Ȼ����( ԭ����MAX_RESIST_ELEMENT )
ROLE_MAX_RESIST_VIRUS 				= 95										# ����ط���( ԭ����MAX_RESIST_POISON )
ROLE_MAX_RESIST_SPIRIT 				= 95										# ��������( ԭ����MAX_RESIST_SPIRIT )

ROLE_MP_REVER_INTERVAL				= 3.0										# ��hp/mp�ָ���entity��hp/mp�ָ�ʱ�ļ��(��/��)( from L3Define.py��ԭ����C_REVERT_TIME )

ROLE_HIT_SPEED_BASE					= int( 1.3 * csconst.FLOAT_ZIP_PERCENT )	# �����ٶȣ�զ�Ķ��̶����֡����� by ����
# ��������
# ROLE_HP_MAX_RADIX																# ���ᵽ common/csconst.py �ж���

# ��������
# ROLE_MP_MAX_RADIX																# ���ᵽ common/csconst.py �ж���
ROLE_DROP_DAMAGE_HEIGHT				= 15.0										# �����˺��߶�


# ȫ����ͬǰ׺��װ���Լӳ� by����
ALL_GOD_PROP_EFFECT	=	0.1 * csconst.FLOAT_ZIP_PERCENT

# --------------------------------------------------------------------
# about pet( hyw )
# --------------------------------------------------------------------
PET_HEARTBEAT_INTERVAL				= 1.0			# ���������ٶ�
PET_MP_REVER_INTERVAL				= 3.0			# ��hp/mp�ָ���entity��hp/mp�ָ�ʱ�ļ��(��/��)

PET_KEEP_REINBIBLE_MAX				= 3				# �����ʹ�ü�����Ԧ��

PET_LIFE_WASTAGE_INTERVAL			= 300.0			# ÿ���೤ʱ�������������һ�Σ��������ʱ�䣬���۳���
PET_JOYANCY_WASTAGE_INTERVAL		= 300.0			# ÿ���೤ʱ�������ֶ�����һ�Σ��������ʱ�䣬���۳���

PET_DIE_WITHDRAW_DELAY				= 1.0			# �����������û���

PET_EXP_LEVEL_LIMIT_GAP				= 5				# ������ڽ�ɫ���ٵȼ����������վ���

PET_TELEPORT_DETECT_CONTROL			= 5				# ÿ��һ��ʱ��Ž��д��ͼ��

PET_FOLLOW_DETECT_CONTROL			= 3				# ÿ��һ��ʱ��Ž���ǿ�и���

PET_SMART_RANGE						= int( 15.0 * csconst.FLOAT_ZIP_PERCENT )	# �����ͳ��﹥������
PET_INTELLECT_RANGE					= int( 20.0 * csconst.FLOAT_ZIP_PERCENT )	# �����ͳ��﹥������

# -------------------------------------------
PET_ROLE_KEEP_DISTANCE				= 3.0			# ���������֮�䱣�ֵľ��루��λ���ף�
PET_FORCE_FOLLOW_RANGE				= 52.0			# �����뿪��Ҷ�Զ��ǿ�ȸ���
PET_ENMITY_RANGE					= 10.0			# ��Ѱ���ﷶΧ
PET_FORCE_TELEPORT_RANGE			= csconst.ROLE_AOI_RADIUS/1.2	# ����ǿ�ƴ��;���

PET_PROPAGATE_NOTIFY_INTERVAL		= 3 * 3600		# �೤ʱ��֪ͨһ�������ȡ����

PCG_GET_GEM_LEVEL					= 10			# ��Ҷ��ټ�������� NPC ��������ʯ
PCG_COMMON_GEM_COUNT				= 5				# �����ͨ��ʯ������

#-------------------------------------------
# about call monster
#-------------------------------------------
CALL_MONSTER_INIT_TIME				= 2

# --------------------------------------------------------------------
# about quest( from common/QuestDefine.py��designed by kebiao )
# --------------------------------------------------------------------
QUEST_MAX_ASSIGNMENT				= 20			# ���ͬʱ�ɽӶ��ٸ�����( ԭ����C_MAX_QUEST )


# --------------------------------------------------------------------
# about buffer
# --------------------------------------------------------------------
DEBUFF_COUNT_UPPER_LIMIT			= 10			# ��������м���debuff�Ĵ��ڣ����������������������Ļ��ǰ��ļ�����
													# ( from common/L3Define.py��ԭ����C_MAX_DEBUFF )

# --------------------------------------------------------------------
# about combat
# --------------------------------------------------------------------
global_combatDict = {		#��ֵֻ������ int, float, string ���򽫻�����������
	#///////////////////��������///////////////////////////////////////////////
	"skill_percent" : 0, # ���ܹ������ӳ�
	"skill_value" : 0, # ���ܹ�������ֵ
	#//////////////////������־////////////////////////////////////////////////
}

# --------------------------------------------------------------------
# about Vehicle
# --------------------------------------------------------------------
VEHICLE_ACTIVATE_SKILLID				= 860002001		# ������輼��ID
VEHICLE_ACTIVATE_BUFFID				        = 1022 # ��������buff ID
VEHICLE_CONJURE_BUFFID				        = [6005,8006] # �����ٶ�buff ID
VEHICLE_TRANS_SKILLID				        = 860001001		#��������ID

VEHICLE_CONJURE_SKILLID						= 322385001		# �ٻ�½����輼��ID
VEHICLE_FLY_CONJURE_SKILLID					= 322724001		# �ٻ�������輼��ID
VEHICLE_WITH_CONJURE_SKILLID				= 322402001		# ���＼��ID���˼��ܻᴥ���޵�Ч��
VEHICLE_UPDATE_TIME							= 15.0			# ���״̬�¸���timer
VEHICLE_JOYANCY_TIME						= 1800.0		# �����ֶȸ���ʱ��
VEHICLE_EXP_DISLEVEL						= 5				# �������ҵĵȼ�����������ֵ�޷���ȡ����
VEHICLE_EXP_ADD								= 500			# ���ÿ��15���ȡ�ľ���ֵ

# --------------------------------------------------------------------
# pk
# --------------------------------------------------------------------
PK_STATE_ATTACK_TIME						= 120.0			# ����pk״̬����ʱ�䣨�룩
PK_VALUE_LESS_TIME							= 1200.0		# pkֵ������ʧʱ�䣨�룩
PK_VALUE_PRISON_LESS_TIME					= 600.0			# pkֵ�ڼ�����ʧʱ�䣨�룩
PK_GOOSNESS_ADD_TIME						= 600.0			# ����ֵ��������ʱ�䣨�룩
PK_PEACE_DROP_ODDS							= 0.005			# ����״̬����װ������
PK_REDNAME_DROP_ODDS						= 0.05			# ����״̬����װ������
PK_FIGHT_BACK_TIME							= 9.0			# pk��������ʱ�䣨�룩
PLAYER_CAN_BE_ATTACK_PK_VALUE_MIN			= 17			# ��ұ�������������СPKֵ


# --------------------------------------------------------------------
# ������ֵ��Ʒ
# --------------------------------------------------------------------
TALISMAN_ADD_LIFE_TIME 						= 2592000		# Ů�ʯ��ֵʱ�䣨�룩/��30�죩

# --------------------------------------------------------------------
# �콵���е������Ͷ���
# --------------------------------------------------------------------
LUCKY_BOX_DROP_NORMAL_ITEM					= 0
LUCKY_BOX_DROP_EQUIP						= 1
LUCKY_BOX_DROP_MONEY						= 2
LUCKY_BOX_DROP_POTENTIAL					= 3
LUCKY_BOX_DROP_EXP							= 4
HONOR_ITEM									= 5				#��������Ʒ

#�ڳ������ٷ˵�ID
DART_MONSTERSID = [20111003,20121002,20131001,20141001,20151001,]


TEAM_GAIN_EXP_RANGE					= 100			# ���룬��ʾ���ɱ�֣�������������Զ�Ķ�Ա�ɻ�þ��顣

# Ӱ����Ӹ����Ч��״̬�б�
TEAM_FOLLOW_EFFECT_LIST = [ csdefine.EFFECT_STATE_SLEEP, csdefine.EFFECT_STATE_VERTIGO, csdefine.EFFECT_STATE_FIX ]
# ��Ӹ�����Ϊ������
FOLLOW_STATES_ACT_WORD = csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_PK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_FIGHT | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_CALL_PET

TEAM_FOLLOW_TRANSPORT_DISTANCE = 20				# �ף���Ӹ��洫�͵İ뾶


#��ɫ״̬
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

BENEFIT_SKILL_ID		= 122184001	# �ۼ�����ʱ�佱������id
BENIFIT_PERIOD		=	5 * 3600		# ��λ���롣����ۼ�����ʱ��ﵽ���ɻ�ý���

LT_SENDNUM			= 4 #����һ�η�����Ʒ�ĸ���

JING_WU_SHI_KE_ENTER = 780023001					# ����ʱ�̣���������ʩ�ż���
JING_WU_SHI_KE_LEAVE = 780024001					# ����ʱ�̣��뿪��̨ʩ�ż���

JING_WU_SHI_KE_BUFF = 22017							# ����ʱ��buff����־����������
JING_WU_SHI_KE_SINGLE_DANCE_SKILL = 780026001		# ����ʱ�̣������赸����
JING_WU_SHI_KE_DOUBLE_DANCE_SKILL = 780027001		# ����ʱ�̣�˫���赸����
JING_WU_SHI_KE_TEAM_DANCE_SKILL = 780031001			# ����ʱ�̣�����赸����
JING_WU_SHI_KE_SINGLE_DANCE_BUFF  = 99011			# ����ʱ�̣������赸buff
JING_WU_SHI_KE_DOUBLE_DANCE_BUFF  = 99012			# ����ʱ�̣�˫���赸buff
JING_WU_SHI_KE_TEAM_DANCE_BUFF  = 99017				# ����ʱ�̣�����赸buff
JING_WU_SHI_KE_DANCE_BUFF = 99014					# ����ʱ�̣�����ʱ��buff
JING_WU_SHI_KE_TIAO_WU_YAO_JUE_BUFF = 22121			# ����ʱ�̣�����Ҫ��buff
JING_WU_SHI_KE_WU_WANG_MI_JUE_BUFF = 22122			# ����ʱ�̣������ؾ�buff

JING_WU_SHI_KE_TEAM_RANGE = 10						# �������һ����Χ��
JING_WU_SHI_KE_MAX_POINT_ONE_DAY = 30				# ����ʱ�̣�һ������ۻ�����
JING_WU_SHI_KE_MAX_POINT		 = 2000				# ����ʱ�̣�����ۻ�����
JING_WU_SHI_KE_POINT_SKILL		 = 780032001		# ����ʱ�̣����ּ���
JING_WU_SHI_KE_POINT_BUFF		 = 22123			# ����ʱ�̣�����buff

FA_SHU_JIN_ZHOU_BUFF	= 299017 					# ��������buff

SUIT_EQUIP_LIMIT = 7    #��װװ����Ŀ
INSTENSIFY_BROADCAST_LEVEL = 7		#װ��ǿ���Ĳ�����Ϣ�ȼ�
SUTD_BROADCAST_LEVEL = 60	#��Ƕˮ���Ĳ�����Ϣ�ȼ�

SPACE_COPY_CLOSE_CBID			= 	12456874				# ����û����ң��رո���ר�õ�TIMER Arg

DARKOFFICE_XL			= 37	# ��¡����
DARKOFFICE_CP			= 38	# ��ƽ����

DARKOFFICE_NAME			= {
							37	:	cschannel_msgs.DART_INFO_2,
							38	:	cschannel_msgs.DART_INFO_3
						}


TISHOU_ITEM				= 60101071


# --------------------------------------------------------------------
# �д�
# --------------------------------------------------------------------
QIECUO_NOTIFY_TIME				= 3			# �д�����ʾʱ��
QIECUO_NOTIFY_INTERVAL_TIME		= 1			# �д�����ʾʱ��
QIECUO_PROJECT_SKILLID			= 780041001	# �д��޵б���BUFF
QIECUO_CHECK_INTERVAL_TIME		= 10.0		# �д���̼��ʱ��
QIECUO_CONFIRM_TIME				= 18.0		# �д�������ʱ��ȷ��

# --------------------------------------------------------------------
# װ�������;��½��ٽ��
# --------------------------------------------------------------------
EQUIP_REPAIL_LIMIT = 0.2

# ��ɫ����ԭ�ظ����Ѱ����������Χ
REVIVE_ON_ORIGIN_RANGE = 30.0


#---------
#ͬһ�죬ͬһ����ҿ����ڲ�ͬ������л����ض���
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

#�������ƾ֤
TONG_RACE_ITEM = 50101062

# ��ɫ��ѧϰ������������� by ����
LIVING_SKILL_NUM_MAX	=	5



HONOR_RECOVER_TIME		=   360
HONOR_RECOVER_VALUE		= 	1

#����NPCģ��
tsNpcs = { 1 : csconst.TI_SHOU_MODEL_1,
			2: csconst.TI_SHOU_MODEL_2,
			3: csconst.TI_SHOU_MODEL_3,
			4: csconst.TI_SHOU_MODEL_4,
			5: csconst.TI_SHOU_MODEL_5,
			6: csconst.TI_SHOU_MODEL_6,
			7: csconst.TI_SHOU_MODEL_7,
			}

# --------------------------------------------------------------------
# �����ٶ�
# --------------------------------------------------------------------
HORSE_MOVE_SPEED_PERCENT		= 0.5

TEACH_KILL_MONSTER_DROP_ITEM = 60101105		# ʦͽ����boss������Ʒ

TEACH_MASTER_EVERYDAY_REWARD_SKILLID = 322262002	# ʦ��ÿ��ʦͽ��������id
TEACH_PRENTICE_EVERYDAY_REWARD_SKILLID = 322262001	# ͽ��ÿ��ʦͽ��������id

# --------------------------------------------------------------------
# ��Ӳɼ�
# --------------------------------------------------------------------
FRIEND_COLLECT_MEM_NUM = 2		# ��������Ҫ��
FRIEND_COLLECT_RANGE = 50.0		# ��Ա��ΧҪ��
FRIEND_COLLECT_LEVEL = 10			# ��Ա�ȼ�Ҫ��


TANABATA_QUIZ_LEVEL_LIMIT				= 20		# ��Ϧ����ʴ���С��������
TANABATA_QUIZ_TEAMMATE_DISTANCE			= 20		# ��Ϧ����ʴ������Ч����
TANABATA_QUIZ_REWARD_ITEM				= 50202078	# ��Ϧ����ʴ���ȷʱ��������Ʒid
TANABATA_QUIZ_DAY_QUESTIONS_COUNT		= 20		# ��Ϧ����ʴ�ÿ�����Ŀ����

# --------------------------------------------------------------------
# �������ܴ��
# --------------------------------------------------------------------
INTERRUPTED_BASE_TYPE = set( [
								csdefine.BASE_SKILL_TYPE_MAGIC,
								csdefine.BASE_SKILL_TYPE_PHYSICS,
							] )

# --------------------------------------------------------------------
# ��ɫ���Ǳ��Buff��Ѱ����������Χ by ������ 2010-09-28
# --------------------------------------------------------------------
ON_REMOVE_BUFF_PROWL_RANGE= 30.0

# --------------------------------------------------------------------
# �ƶ�����
# --------------------------------------------------------------------
MOVE_TYPE_STOP			= 0		# ����û���ƶ���
MOVE_TYPE_DEFAULE		= 1			# ������ָ�����ƶ�
MOVE_TYPE_CHASE			= 2			# ����׷��Ŀ���ƶ�
MOVE_TYPE_PATROL		= 3			# ����Ѳ���ƶ�
MOVE_TYPE_BACK			= 4			# ���ڻ����ƶ�
MOVE_TYPE_ROUND			= 5			# �����ε��ƶ�


# ��Ұ�����ռ������ѹ��׶��ۿ�
TONG_HOLD_CITY_CONTRIBUT_DISCOUNT = 0.8

# --------------------------------------------------------------------
# ���鸱����ְҵ��Ӧģ�ͱ��
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
# ҹս���ܸ�����ְҵ��Ӧģ�ͱ��
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

FIGHT_CHECK_TIMER			= 8				# ս�����ʱ��

# --------------------------------------------------------------------
# �̹��ػ�ϵͳ���
# --------------------------------------------------------------------
ROLE_INIT_ACCUM_POINT 			= 300					# ��ҽ����Ǽʵ�ͼ����ó�ʼ����ֵ

# �̹��ػ�ģʽ��Ӧ����
PGNAGUAL_ACTION_FOLLOW_SKILLID 	= 323243001 			# ����
PGNAGUAL_ACTION_ATTACK_SKILLID 	= 323244001 			# ����
PGNAGUAL_NEAR_GROUP_SKILLID 	= 323245001 			# ��սȺ�����̹��ػ�ʹ�ü���
PGNAGUAL_NEAR_SINGLE_SKILLID 	= 323246001 			# ��ս�������̹��ػ�ʹ�ü���
PGNAGUAL_FAR_PHYSIC_SKILLID 	= 323247001 			# Զ���������̹��ػ�ʹ�ü���
PGNAGUAL_FAR_MAGIC_SKILLID 		= 323248001 			# Զ�̷������̹��ػ�ʹ�ü���

#����ͻ������õ����AOIֵ
MAX_AOI_RANGE = 200.0

# ������������
DAOHENG_AMEND_RATE				= 1.0


#ˮ�����ֵ
WATER_SPEED_ACCELERATE = 3.0 * csconst.FLOAT_ZIP_PERCENT

ROUND_SPEED			   = [ 5, 7 ] # �����ε���Ϊ�ٶ�ֵ
ROUND_MIN_DIS			= 2  # ��С�ε����루��Ŀ��ľ��룩
ROUND_MAX_DIS			= 10 # ����ε����루��Ŀ��ľ��룩
ROUND_TIME_LIMIT		= 4
ROUND_NEAR_OR_FAR_MAX_ANGLE			= 90.0	# ���Ŀ�������Զ��Ƕ�ƫ��
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

#combo������ú���0
COMBO_COUNT_CLEAR_TIME = 2.0
COMBO_COUNT_MAX        = 65535

#�������������Χ�˺�����
ROLE_SKILL_IDS_ON_LEVEL_UP  = {
	csdefine.CLASS_FIGHTER   :  "322550",
	csdefine.CLASS_SWORDMAN	 :  "322551",
	csdefine.CLASS_ARCHER    :  "322552",
	csdefine.CLASS_MAGE		 :  "322553",
}

#�����ﴴ��ʱ��������
ENTITY_CREATE_TRIGGER_SKILL_ID = 780049001

# space copy timer arg
SPACE_TIMER_ARG_CLOSE = 1000 # �رո���
SPACE_TIMER_ARG_KICK  = 1001 # �������и������
SPACE_TIMER_ARG_LIFE  = 1002 # ����ʱ��

#����ֵ��ʱ�������е���
GOODNESS_ADD_REDUCE_ROLE_DAMAGE = 325

#���ȼ����������е����仯
TONG_ADD_REDUCE_ROLE_DAMAGE = { 3:400, 4:500, 5:650 }

# �Զ���ɸ�ӵ�ʱ��
AUTO_THROW_SIEVE_TIME = 5.0

#ת�����С�Ƕ�
ROTATE_MIN_ANGLE = 0.26

#�����������
REWARD_QUEST_NUM = 2

#��������С�����������
REWARD_QUEST_SMALL_TYPE_NUM = 1

#�����ͼ�󣬴���NPC�ɽ������������
ENTER_SPACE_AUTO_ACCEPT_QUEST_DISTANCE = 10.0


#һ��24Сʱ
ONE_DAY_HOUR = 24

#��Ӱ֮�Ųμӵȼ�
AN_YING_ZHI_MENG_LEVEL = 10			#��Ӱ֮����ҵȼ�Ҫ��
AN_YING_ZHI_MENG_DISTANCE = 30.0			#��Ӱ֮�����������Ա��Χ

TELEPORT_PLANE_TOPSPEED_LIMIT		= 1000				# λ�洫��ʱ��topSpeed����
TELEPORT_PLANE_SKILLID				= 860022001		# λ�洫�͸ı�topspeed�ļ���id

#SET_TEMP_KEY( ������ʱ����key )
QUEST_SLOTS_MULTIPLE_KEY = "QUEST_SLOTS_MULTIPLE_KEY_%s"
QUEST_AUTO_OPEN_NEXT_KEY = "QUEST_AUTO_OPEN_NEXT_KEY"

# -----------------------------------------------------
# new space copy CopyTemplate timer arg
# �¸������������timer���������� xml �ļ���ο� CopyStageActions:CopyStageAction12
# ������Ա���Զ���һ���κ� ��0, 10000�� ��������Ϊtimer�� useArg
# ������� timer ��������������Ա֪�������ø�����ʾ
# Ŀǰֻ����һ���رո����� timer ��Ҫ����
# �������в�����������Ա֪���� timer�����Է������

# -----------------------------------------------------
SPACE_TIMER_USER_ARG_MAX		= 10000			# ������Ա��һ�������п��Զ������� timer useArg

# �����ǻ��ڳ�����ֱ����ӵ� timer����������������Ա֪���ġ�
# ��������
SPACE_TIMER_ARG_CLOSE_SPACE		= -1
# ���ظ�������
SPACE_TIMER_ARG_FANG_SHOU_DELAY_SPAWN_MONSTER 	= 	-1001		# ���ظ����ӳ� 1 ��ˢ�� timer


# ���ظ���
COPY_FANG_SHOU_MONSTER_WAVE_MAX			= 12							# ���ظ��������ﲨ��
COPY_FANG_SHOU_FIRST_BOSS_WAVE			= 6								# ���ظ�����һ��BOSS���ֲ���
COPY_FANG_SHOU_SECOND_BOSS_WAVE			= 12							# ���ظ����ڶ���BOSS���ֲ���
COPY_FANG_SHOU_AREA_FIRST				= "fu_ben_fang_shou_area_1"		# ���ظ�������һ
COPY_FANG_SHOU_AREA_SECOND				= "fu_ben_fang_shou_area_2"		# ���ظ��������
COPY_FANG_SHOU_AREA_THRID				= "fu_ben_fang_shou_area_3"		# ���ظ���������
COPY_FANG_SHOU_AREA_FORTH				= "fu_ben_fang_shou_area_4"		# ���ظ���������
COPY_FANG_SHOU_CHECK_POSITION_CYCLE		= 0.5							# ���ظ���������λ�õ�ʱ������
COPY_FANG_SHOU_AERA_POS_Z_FIRST			= -1							# ���ظ�����һ��������߽� z ����
COPY_FANG_SHOU_AERA_POS_Z_SECOND		= -85.5							# ���ظ����ڶ���������߽� z ����
COPY_FANG_SHOU_AERA_POS_Z_THRID			= -163							# ���ظ���������������߽� z ����
COPY_FANG_SHOU_BUFF_SPELLS				= {
											COPY_FANG_SHOU_AREA_FIRST	:	( 123735001, 123726001, 123730001 ),	# ���ظ�������һ��buff����
											COPY_FANG_SHOU_AREA_SECOND	:	( 123734001, 123727001, 123731001 ),	# ���ظ����������buff����
											COPY_FANG_SHOU_AREA_THRID	:	( 123733001, 123728001, 123732001 ),	# ���ظ�����������buff����
											COPY_FANG_SHOU_AREA_FORTH	:	( 123729001, ),							# ���ظ��������ĵ�buff����
										}
COPY_FANG_SHOU_CLEAR_BUFF_SPELLS		= ( 123736001, 123739001, 123742001 )										# ������ظ������� Buff �ļ���
COPY_FANG_SHOU_LAST_TIME				= 1800																		# ���ظ�������ʱ��
COPY_FANG_SHOU_MONSTER_TOTALS			= 100																		# ���ظ���С������
COPY_FANG_SHOU_BOSS_TOTALS				= 2																			# ���ظ���BOSS����
COPY_FANG_SHOU_EACH_WAVE_TIME			= 60																		# ���ظ���ÿ��������ʱ��
COPY_FANG_SHOU_SPECAIL_ITEMS			= ( 40401034, 40401035, 40401036, 40401037, 40401038 )						# ���ظ����������id�б�

#NPCMonster����Χ�Լ���Ұ��Χ����ֵ
TERRITORY_LIMIT = 100				#����Χ����ֵ
VIEWRANGE_LIMIT = 100				#��Ұ��Χ����ֵ

ACTIVITY_STOP_MOVE_SKILL = 721037001	#ͨ�û��ֹ�ƶ�BUFF
