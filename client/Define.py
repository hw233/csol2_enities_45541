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
# ����״̬
GST_NONE						= 0x0000		# δ֪״̬
GST_GAME_INIT					= 0x0001		# ��Ϸ����״̬
GST_LOGIN						= 0x0002		# ���ڵ�¼�˺�״̬
GST_ENTER_ROLESELECT_LOADING	= 0x0004		# ��¼����ؽ�ɫѡ�񳡾�״̬
GST_ROLE_SELECT					= 0x0008		# ���ڽ�ɫѡ��״̬
GST_BACKTO_ROLESELECT_LOADING	= 0x0010		# ���ؽ�ɫѡ��ʱ�����ؽ�ɫ����״̬
GST_ROLE_CREATE					= 0x0020		# ���ڽ�ɫ����״̬
GST_ENTER_WORLD_LOADING			= 0x0040		# ������Ϸ����״̬
GST_IN_WORLD					= 0x0080		# ��������״̬
GST_SPACE_LOADING				= 0x0100		# ��ɫ��תʱ���س���״̬
GST_OFFLINE						= 0x0200		# ����״̬

GST_UNBUSYS						= [GST_LOGIN, GST_ROLE_SELECT, GST_ROLE_CREATE, GST_IN_WORLD, GST_OFFLINE]
GST_UNBUSY						= GST_LOGIN | GST_ROLE_SELECT | GST_ROLE_CREATE | GST_IN_WORLD | GST_OFFLINE


# --------------------------------------------------------------------
# װ����Ʒ��ģ�ͱ�ţ�
# --------------------------------------------------------------------
PRE_EQUIP_NULL				=	0		# ����Ʒ
PRE_EQUIP_DRUG 				=	1		# ����Ʒ
PRE_EQUIP_NORMAL 			=	2		# ��ͨ��Ʒ
PRE_EQUIP_ARMET				=	3		# ͷ��
PRE_EQUIP_LORICAE			=	4		# ��������
PRE_EQUIP_ARMGUARD			=	5		# ����
PRE_EQUIP_SKIRT				=	6		# ����ȹ�Ӽ�����
PRE_EQUIP_FOOTGUARD			=	7		# ����
PRE_EQUIP_SHIELD			=	8		# ��
PRE_EQUIP_LANCE2			=	9		# ˫��ì
PRE_EQUIP_KNIFE				=	10		# ��ذ��
PRE_EQUIP_STAFF				=	11		# ������
PRE_EQUIP_STAFF2			=	12		# ˫����
PRE_EQUIP_BOW				=	13		# ��
PRE_EQUIP_LANCE				=	14		# ����ì
PRE_EQUIP_TPOISONPIN			=	15		# Ͷ���ö���
PRE_EQUIP_TROCK				=	16		# Ͷ����ʯͷ
PRE_EQUIP_TDART				=	17		# Ͷ����ì
PRE_EQUIP_SWORD				=	18		# ���ֽ�
PRE_EQUIP_SWORD2			=	19		# ˫�ֽ�
PRE_EQUIP_ORNAMENT			=	20		# ��Ʒ
PRE_EQUIP_AXE 				=	21		# ���ָ�
PRE_EQUIP_AXE2 				=	22		# ˫�ָ�
PRE_EQUIP_HAMMER			=	23		# ���ִ�
PRE_EQUIP_HAMMER2 			=	24		# ˫�ִ�
PRE_EQUIP_RING				=	25		# ��ָ
PRE_EQUIP_NECKLACE 			=	26		# ����
PRE_EQUIP_TWOSWORD			=	27		# ˫�ֽ�
PRE_EQUIP_TWOLANCE			=	29		# ǹ
PRE_EQUIP_JEWEL  			=	96		# ��ʯ
PRE_EQUIP_SCROLL 			=	97		# ����
PRE_EQUIP_MONEY				=	98		# ��Ǯ
PRE_EQUIP_OTHER				=	99		# ������Ʒ

# װ����������
WEAPON_TYPE_NONE			=	0		# ����
WEAPON_TYPE_WEIGHTBLUNT		=	1		# �ض�����
WEAPON_TYPE_LIGHTBLUNT		=	2		# �������
WEAPON_TYPE_WEIGHTSHARP		=	3		# ����������
WEAPON_TYPE_LIGHTSHARP		=	4		# ����������
WEAPON_TYPE_DOUBLEHAND		=	5		# ˫������
WEAPON_TYPE_BOW				=	6		# ��
WEAPON_TYPE_THROW			=	7		# Ͷ��
WEAPON_TYPE_POSISON			=	8		# ��
WEAPON_TYPE_BIANSHEN		=	9		# ����ģ����������

# װ����������
ARMOR_TYPE_EMPTY			=	0		# �޷���
ARMOR_TYPE_CLOTH			=	1		# ����
ARMOR_TYPE_SKIN				=	2		# Ƥ��
ARMOR_TYPE_WOOD				=	3		# ľͷ
ARMOR_TYPE_METAL			=	4		# ������
ARMOR_TYPE_SHIELD			=	5		# ����
ARMOR_TYPE_ROCK				=	6		# ʯͷ

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
# about entity be clicked ( come from: client/Const.py��designed by wanhp  )
# --------------------------------------------------------------------
TARGET_CLICK_FAIL			= 	0		# ���Ŀ��ʧ��
TARGET_CLICK_SUCC			= 	1		# ���Ŀ��ɹ�
TARGET_CLICK_MOVE           = 	2		# ����ƶ���һ���ǵ��������ߵĶ��ε�� NPC

TARGET_PURSUE_FAILURE		=	0		# ׷��ʧ��
TARGET_PURSUE_SUCCESS		= 	1		# ׷���ɹ�
TARGET_PURSUE_MOVING		= 	2		# ����׷��


# --------------------------------------------------------------------
# about skill type ( come from: client/Define.py��designed by panguankong )
# --------------------------------------------------------------------
SKILL_TYPE_ACTIVE_PROFESSION		= 1			# ����ְҵ����( ԭ����SKILL_TYPE_INITIATIVE_WORK )
SKILL_TYPE_PASSIVE_PROFESSION 		= 2			# ����ְҵ����( ԭ����SKILL_TYPE_PASSIVENESS_WORK )
SKILL_TYPE_ACTIVE_CORPS				= 3			# �������ż���( ԭ����SKILL_TYPE_INITIATIVE_CONFRATERNITY )
SKILL_TYPE_PASSIVE_CORPS			= 4			# �������ż���( ԭ����SKILL_TYPE_PASSIVENESS_CONFRATERNITY )
SKILL_TYPE_ACTIVE_GEST	 			= 5			# ?( ԭ����SKILL_TYPE_INITIATIVE_GEST )
SKILL_TYPE_PASSIVE_GEST		 		= 6			# ?( ԭ����SKILL_TYPE_PASSIVENESS_GEST )


# ------------------------------------------------------------------------
# ��ְҵ����������ID
# ------------------------------------------------------------------------
SKILL_ID_FIGHTER_TRIGGER_SKILL			= 323175001     # սʿ3��������ID
SKILL_ID_SWORDMAN_TRIGGER_SKILL			= 311338001     # ����3��������ID
SKILL_ID_ARCHER_TRIGGER_SKILL			= 323155001     # ����3��������ID
SKILL_ID_MAGE_TRIGGER_SKILL				= 323147001     # ��ʦ3��������ID

SKILL_ID_TRIGGER_SKILLS = { 
	csdefine.CLASS_FIGHTER:		SKILL_ID_FIGHTER_TRIGGER_SKILL,		# սʿ
	csdefine.CLASS_SWORDMAN:	SKILL_ID_SWORDMAN_TRIGGER_SKILL,	# ����
	csdefine.CLASS_ARCHER:		SKILL_ID_ARCHER_TRIGGER_SKILL,		# ����
	csdefine.CLASS_MAGE:		SKILL_ID_MAGE_TRIGGER_SKILL			# ��ʦ
	}

TRIGGER_SKILL_IDS = [ 323175, 323165, 323155, 323147 ]   # ����������ϵ��ID�б�
# ------------------------------------------------------------------------------------------------
# ��Ч���ID����
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
# ����CAPS����
# ------------------------------------------------------------------------------------------------
# ״̬Caps(���Ժ���ΪCaps/����Caps����)
CAPS_DEFAULT					= 0			# Ĭ��Caps
CAPS_IDLE						= 1			# ս��Caps(����ս��״̬�¼���)
CAPS_DEAD						= 2			# ����Caps(��������״̬�¼���)
CAPS_LOGIN						= 3			# ��½Caps(�ڽ�ɫѡ���漤��)
CAPS_RANDOM						= 4			# �������Caps(�ɶ���ƥ��������)
CAPS_SNEAK						= 5			# Ǳ��״̬Caps
CAPS_ENVIRONMENT_OBJECT			= 6			# ����Caps
CAPS_FLY_WATER					= 7			# ˮ������


# ��ΪCaps(���Ժ�״̬Caps����/����Caps����)
CAPS_RADIFOLLOW					= 9			# �ε�Caps
CAPS_NOWEAPON					= 10		# ������Caps(���ж�������󼤻�)
CAPS_WEAPON						= 11		# ������Caps(���װ�������󼤻�)
CAPS_JUMP                       = 12        # ��Ծ������
CAPS_FASTMOVING                 = 13        # �ƶ�Ѹ�ݹ�����
CAPS_SPRINT                     = 14        # ��̹�����
CAPS_VERTIGO                    = 15        # ѣ�ι�����
CAPS_DAN_WEAPON					= 16		# ���ֽ�Caps
CAPS_SHUANG_WEAPON				= 17		# ˫�ֽ�Caps
CAPS_FU_WEAPON					= 18		# ��ͷCaps
CAPS_CHANG_WEAPON				= 19		# ��ǹCaps

# Caps����(���ڱ��ֶ����Զ���״̬�����Ժ�״̬Caps/��ΪCaps����)
# ����һ�㲻����ȥCapsOn/CapsOffƥ��
# ����[ 4, 10,25 ] ��ʾ����״̬�µı��Ϊ16���������
# ����[ 4, 11, 25 ] ��ʾ������״̬�µı��Ϊ16���������
CAPS_LIE_DOWN					= 20		# ���£�ʵ���ǲ���dead�����һ֡��
# Ԥ����λ�Ա���չ�����������25��ʼ
CAPS_INDEX25					= 25
CAPS_INDEX26					= 26
CAPS_INDEX27					= 27
CAPS_INDEX28					= 28
CAPS_INDEX29					= 29
CAPS_INDEX30					= 30
CAPS_INDEX31					= 31

# ------------------------------------------------------------------------------------------------
# ״̬��ӦCaps
# ------------------------------------------------------------------------------------------------
STATE_CAPS = {			csdefine.ENTITY_STATE_FREE			: CAPS_DEFAULT,	# ����״̬
						csdefine.ENTITY_STATE_DEAD 			: CAPS_DEAD,	# ����״̬
						csdefine.ENTITY_STATE_REST 			: CAPS_DEFAULT,	# ��Ϣ״̬
						csdefine.ENTITY_STATE_FIGHT 		: CAPS_IDLE,	# ս��״̬
						csdefine.ENTITY_STATE_PENDING 		: CAPS_DEFAULT,	# δ��״̬
						csdefine.ENTITY_STATE_VEND			: CAPS_DEFAULT,	# ��̯״̬
						csdefine.ENTITY_STATE_RACER			: CAPS_DEFAULT,	# ����״̬�����磺����
						csdefine.ENTITY_STATE_CHANGING		: CAPS_DEFAULT,	# ����״̬���磺���㣬��������ȣ�
						csdefine.ENTITY_STATE_QUIZ_GAME		: CAPS_DEFAULT,	# �ʴ�״̬
						}

# ------------------------------------------------------------------------------------------------
# ״̬��ӦCaps
# ------------------------------------------------------------------------------------------------
CLASS_WEAPONTYPE = {	csdefine.CLASS_FIGHTER				: [ WEAPON_TYPE_WEIGHTSHARP, WEAPON_TYPE_LIGHTBLUNT ],		# սʿ(���ָ���ǹ)
						csdefine.CLASS_SWORDMAN				: [ WEAPON_TYPE_LIGHTSHARP, WEAPON_TYPE_DOUBLEHAND ],		# ���ͣ�����˫����
						csdefine.CLASS_ARCHER				: [ WEAPON_TYPE_BOW ],				# ����
						csdefine.CLASS_MAGE					: [ WEAPON_TYPE_WEIGHTBLUNT ],		# ��ʦ
						}

# ------------------------------------------------------------------------------------------------
# �����ӦCaps
# ------------------------------------------------------------------------------------------------
MONSTER_CAPS = { 	csdefine.ENTITY_STATE_FREE					: CAPS_DEFAULT,				# ����״̬
					csdefine.ENTITY_STATE_DEAD					: CAPS_DEAD,				# ����״̬
					csdefine.ENTITY_STATE_FIGHT					: CAPS_IDLE,				# ս��״̬
					csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT	: CAPS_ENVIRONMENT_OBJECT,	# �������״̬
					}

# ------------------------------------------------------------------------------------------------
# ��Ծ���̶���
# ------------------------------------------------------------------------------------------------
JUMP_START			= 0						# ׼������
JUMP_UP				= 1						# ����������
JUMP_DOWN			= 2						# ���������
JUMP_END			= 3						# ��Ծ���

# ------------------------------------------------------------------------------------------------
# �����λ��ʽ����
# ------------------------------------------------------------------------------------------------
VEHICLE_MODEL_HIP = 1						# ����
VEHICLE_MODEL_PAN = 2						# ����
VEHICLE_MODEL_STAND = 3						# ����

# ------------------------------------------------------------------------------------------------
# ���⶯������
# ------------------------------------------------------------------------------------------------
# �������������͵���
LOFT_WEIGHTSHARP = [ 	"attack1_1h", "attack2_1h","attack3_1h","attack4_1h","attack5_1h","crossleg1_1h",\
						"crossleg_1h","crossleg_1h_skill","ride1_1h","ride_1h","ride_1h_skill",]
# ˫���������͵���
LOFT_DOUBLEHAND = [ 	"attack1_2h", "attack2_2h","attack3_2h","attack4_2h","attack5_2h","crossleg1_2h",\
						"crossleg_2h","crossleg_2h_skill","ride1_2h","ride_2h","ride_2h_skill",]

LOFT_MAPS = { 	WEAPON_TYPE_WEIGHTSHARP 	: LOFT_WEIGHTSHARP,
				WEAPON_TYPE_DOUBLEHAND 		: LOFT_DOUBLEHAND,
				}

# ------------------------------------------------------------------------------------------------
# ģ����Ϻ궨��
# ------------------------------------------------------------------------------------------------
# Ĭ������ģ��
MODEL_DEFAULT_MAIN		= 0		# Ĭ������ģ��
# ��ɫװ������
MODEL_EQUIP_MAIN		= 1		# װ������ģ�ͣ����壩
MODEL_EQUIP_HEAD		= 2		# װ������ģ�ͣ�ͷ����
MODEL_EQUIP_RHAND		= 3		# װ������ģ�ͣ�����������
MODEL_EQUIP_LHAND		= 4		# װ������ģ�ͣ�����������
MODEL_EQUIP_TALIS		= 5		# װ������ģ�ͣ�������
# ���ģ��
MODEL_VEHICLE			= 6		# �������ģ��
# ���д��Ͳ���
MODEL_FLY_MAIN			= 11	# ���д�������ģ��
# ������
MODEL_HORSE_MAIN		= 21	# ��������ģ��


# ------------------------------------------------------------------------------------------------
# ģ����ʾ��ʽ�궨��
# ------------------------------------------------------------------------------------------------
MODEL_VISIBLE_TYPE_FALSE		= 0		# ģ�Ͳ���ʾ
MODEL_VISIBLE_TYPE_TRUE			= 1		# ģ����ʾ
MODEL_VISIBLE_TYPE_FBUTBILL	 	= 2		# ģ�Ͳ���ʾ����ʾ������
MODEL_VISIBLE_TYPE_SNEAK	 	= 3		# ģ�Ͱ�͸����ʾ

# ------------------------------------------------------------------------------------------------
# ������Ч���ŷ�ʽ
# ------------------------------------------------------------------------------------------------
SOUND_END_BGMUSIC = 1				# �жϱ�������

# ------------------------------------------------------------------------------------------------
# ģ�ͼ����¼�
# ------------------------------------------------------------------------------------------------
MODEL_LOAD_ENTER_WORLD			= 0	# ������Ұ����
MODEL_LOAD_IN_WORLD_CHANGE		= 1	# ������Ұ����

# ------------------------------------------------------------------------------------------------
# ��ͼ��������Ч��
# ------------------------------------------------------------------------------------------------
MAP_AREA_EFFECT_DEFAULT	= 0	# Ĭ����Ч��
MAP_AREA_EFFECT_SHUIPAO	= 1	# ˮ��Ч��
MAP_AREA_EFFECT_UNWATER	= 2	# ˮŤ����ˮ�׿�ʴ������Ч��

MAP_AREA_EFFECTS_MODELCHANGE = [ MAP_AREA_EFFECT_SHUIPAO ]							# entity ģ�͸������Ч���б�
MAP_AREA_EFFECTS_CHANGEAREA	= [ MAP_AREA_EFFECT_SHUIPAO, MAP_AREA_EFFECT_UNWATER ]	# playerRole����������Ч���б�

# ------------------------------------------------------------------------------------------------
# ������ζ�Ч��
# ------------------------------------------------------------------------------------------------
CAMERA_SHAKE_NONE		= 0	# �޻ζ�Ч��
CAMERA_SHAKE_ONE_TYPE	= 1	# Ŀ��ζ�Ч��
CAMERA_SHAKE_AREA_TYPE	= 2	# Ŀ�귶Χ�ζ�Ч��


# ------------------------------------------------------------------------------------------------
# ��Ʒ״̬����
# ------------------------------------------------------------------------------------------------
ITEM_STATUS_NATURAL		= 1		# ������
ITEM_STATUS_ABRASION	= 2		# ĥ��ģ������ã����;��Ѿ��ܵ��ˣ�
ITEM_STATUS_USELESSNESS	= 3		# �޷�ʹ�õģ����ˡ�����������֮��ģ�
ITEM_STATUS_TO_COLOR = {
	ITEM_STATUS_NATURAL		: ( 255,255,255,255 ),
	ITEM_STATUS_ABRASION	: ( 255,255,0,180 ),
	ITEM_STATUS_USELESSNESS	: ( 255,100,100,200 ),
}


# ------------------------------------------------------------------------------------------------
# ��ҿ��ƺ궨��
# ------------------------------------------------------------------------------------------------
CONTROL_FORBID_ROLE_MOVE	= 0x00000001	# �������������ƶ�
CONTROL_FORBID_ROLE_CAMERA	= 0x00000010	# ����������������ͷ

CONTROL_FORBID_ROLE_LIST = ( CONTROL_FORBID_ROLE_MOVE, CONTROL_FORBID_ROLE_CAMERA )


CONTROL_FORBID_ROLE_MOVE_PLAY_ACTION 	= 0  #���������ƶ�
CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT	= 1  #��ͷ�����ƶ�
CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE   = 2  #�����������ƶ�
CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK    = 3  #���������ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_108007    = 4  #108007�����ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_108010    = 5  #108010�����ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_108012    = 6  #108012�����ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_208003    = 7  #208003�����ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_99010     = 8  #99010�����ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_99027     = 9  #99027�����ƶ�
CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL  = 10  #Buff_onPatrol�����ƶ�
CONTROL_FORBID_ROLE_MOVE_SPRINT         = 11  #��������ƶ�

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

CONTROL_FORBID_ROLE_CAMERA_EVENT = 0 #���ž�ͷ���������

CONTROL_FORBID_ROLE_CAMERA_LIST = ( CONTROL_FORBID_ROLE_CAMERA_EVENT,)

# ------------------------------------------------------------------------------------------------
# ���������ʱ��
# ------------------------------------------------------------------------------------------------
TIME_GATHER_TEAM_CHALLENGE		= 2 * 60
TIME_GATHER_WU_DAO				= 2 * 60
TIME_GATHER_ROLE_COMPETITION	= 5 * 60
TIME_GATHER_TONG_COMPETITION	= 5 * 60
TIME_GATHER_TEAM_COMPETITION	= 5 * 60
TIME_GATHER_TONG_ABATTOIR		= 5 * 60


# ------------------------------------------------------------------------------------------------
# ������ʾ����
# ------------------------------------------------------------------------------------------------
TYPE_PARTICLE_PLAYER	=	1
TYPE_PARTICLE_PIOP		=	2
TYPE_PARTICLE_PIN		=	3
TYPE_PARTICLE_OP		=	4
TYPE_PARTICLE_NPC		=	5
TYPE_PARTICLE_SCENE		=	6

#��½��ͼ����
LOGIN_TYPE_MAP       = 100
SELECT_CAMP_TYPE_MAP = 101

#CG
LOGIN_CG_PATH = "videos/compose-all.avi"


#�����ܻ�״̬
COMMON_NO         = 0  #Ĭ��״̬
COMMON_BE_HIT     = 1 #��ͨ�ܻ�(�������ܻ�����)

#entityģ����ʵ��ײ��ÿ�����Ӹ߶�
ENTITIES_MODEL_COLLIDE_HEIGHT =    0.25