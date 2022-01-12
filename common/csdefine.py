# -*- coding: gb18030 -*-

# $Id: csdefine.py,v 1.182 2008-09-05 02:23:15 songpeifang Exp $


"""
locates global definations of base/cell/client

2005.06.06 : tidied up by huangyongwei
"""

import cPickle
import Language
import cschannel_msgs
import ShareTexts as ST

# --------------------------------------------------------------------
# �汾���ƣ��������е�����ɫ�滹����ͨ��
# ���������ǾͿ��Ը���ʵ�����������ĳЩϵͳ����
# ��ĳЩ��Ҫ���ֵĵط�����Դ�ֵ���ж�
# 0 == ��ͨ�汾��1 == ��ɫ�汾
# --------------------------------------------------------------------
IS_GREEN_VERSION = 1

# --------------------------------------------------------------------
# about server state( from L3Define.py��defined by penghuawei )
# --------------------------------------------------------------------
SERVERST_STATUS_COMMON				= 1 	# ״̬һ��
SERVERST_STATUS_WELL				= 2		# ״̬����
SERVERST_STATUS_BUSY				= 3		# ��������æ
SERVERST_STATUS_HALTED				= 4		# ��������ͣ

# --------------------------------------------------------------------
# ������
# --------------------------------------------------------------------
# ״̬����
WALLOW_STATE_COMMON					= 0		# ����״̬
WALLOW_STATE_HALF_LUCRE				= 1		# �������
WALLOW_STATE_NO_LUCRE				= 2		# ����Ϊ 0



# --------------------------------------------------------------------
# about initialize type of the role( 2008.06.05: by penghuawei )
# --------------------------------------------------------------------
ROLE_INIT_OPRECORDS					= 0		# ������¼�ĳ�ʼ��
ROLE_INIT_KITBAGS					= 1		# �����ĳ�ʼ��
ROLE_INIT_ITEMS						= 2		# ��Ʒ�͵��ߵĳ�ʼ��
ROLE_INIT_SKILLS					= 3		# �����б�ĳ�ʼ��
ROLE_INIT_BUFFS						= 4		# buff �ĳ�ʼ��
ROLE_INIT_COMPLETE_QUESTS			= 5		# �������ĳ�ʼ���б�
ROLE_INIT_QUEST_LOGS				= 6		# ������־��ʼ��
ROLE_INIT_PETS						= 7		# �����ʼ��
ROLE_INIT_COLLDOWN					= 8		# ��ȴ
ROLE_INIT_QUICK_BAR					= 9		# �������ʼ��
ROLE_INIT_PRESTIGE					= 10	# ��ʼ������
ROLE_INIT_VEHICLES					= 11	# ��ʼ�����
ROLE_INIT_MONEY						= 12	# ��ʼ����Ǯ
ROLE_INIT_OFLMSGS					= 13	# ��ʼ��������Ϣ
ROLE_INIT_DAOFA						= 14	# ��ʼ������
ROLE_INIT_REWARD_QUESTS				= 15	# ��ʼ����������




# --------------------------------------------------------------------
# about entity ( from common/utype.py��designed by all team members )
# --------------------------------------------------------------------
ENTITY_TYPE_ROLE					= 1		# ��ɫ
ENTITY_TYPE_NPC						= 2		# NPC
ENTITY_TYPE_MONSTER					= 3		# ����
ENTITY_TYPE_PET						= 4		# ����
ENTITY_TYPE_PREVIEWROLE				= 5		# ��ɫѡ��entity
ENTITY_TYPE_DROPPED_ITEM			= 6		# ������Ʒ
ENTITY_TYPE_SPAWN_POINT				= 7		# ������
ENTITY_TYPE_SPACE_DOOR				= 8		# ������
ENTITY_TYPE_SPACE_TRANSPORT			= 9		# ���͵�
ENTITY_TYPE_SPACE_ENTITY			= 10	# ����ʦ
ENTITY_TYPE_WEATHER_SYSTEM			= 11	# ����ϵͳ
ENTITY_TYPE_QUEST_BOX				= 12	# ��������
ENTITY_TYPE_PROXIMITY_TRANSDUCER	= 13	# ��
ENTITY_TYPE_SPACE_GATE				= 14	# �ؿ�����
ENTITY_TYPE_SLAVE_MONSTER			= 15	# �����˵Ĺ��Ʃ�绤��NPC��
ENTITY_TYPE_MISC					= 16	# �������û��������Ҫ�жϵ����Ͷ���Ϊ���ࣩ
ENTITY_TYPE_TREASURE_MONSTER		= 17	# ������������Ȩ�����Լ�����Ļ���б�����ͨMonster��
ENTITY_TYPE_DROPPED_BOX				= 18	# ������Ʒ
ENTITY_TYPE_CONVOY_MONSTER			= 19	# �������
ENTITY_TYPE_VEHICLE					= 20	# ���
ENTITY_TYPE_TONG_CITYWAR_MONSTER	= 21	# �����ս����
ENTITY_TYPE_VEHICLE_DART			= 22	# �ڳ�
ENTITY_TYPE_YAYU					= 23	# �m؅����ʱû�жԿ��Ա������Ĺ������һ�����ͣ����պ�������˵��
ENTITY_TYPE_SERVER_ENTITY			= 24	# ������ENTITY�� �ͻ��˲��ɼ��� ֧��AI
ENTITY_TYPE_COLLECT_POINT			= 25	# �ɼ��� by ����
ENTITY_TYPE_TONG_NAGUAL				= 26	# �������
ENTITY_TYPE_MONSTER_ATTACK_BOX		= 27	# ���﹥�ǻ�е���ġ����֮�䡱������
ENTITY_TYPE_FRUITTREE				= 28	# ��Ϧ�����������
ENTITY_TYPE_EIDOLON_NPC				= 29	# С����NPC
ENTITY_TYPE_CHALLENGE_TRANSDUCER	= 30	# ��ս������������
ENTITY_TYPE_CALL_MONSTER			= 31	# �ٻ������
ENTITY_TYPE_SPACE_CHALLENGE_DOOR	= 32	# ��ɽ�󷨴�����
ENTITY_TYPE_CITY_MASTER				= 33	# ��������
ENTITY_TYPE_PANGU_NAGUAL			= 34	# �̹��ػ�
ENTITY_TYPE_NPC_FORMATION			= 35	# ����NPC
ENTITY_TYPE_SKILL_TRAP				= 36    # ��������
ENTITY_TYPE_NPC_OBJECT				= 37	# �������
ENTITY_TYPE_MONSTER_BELONG_TEAM		= 38	# ���ݶ����ж�ս����ϵ����
ENTITY_TYPE_SPACE_SHUIJING_DOOR		= 39	# ˮ������������
ENTITY_TYPE_XIAN_FENG				= 40	# �����ս������������죩�ȷ��
ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER = 41	# �����ս������������죩������
ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR = 42	# �����ս������������죩��̳
ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER = 43	# �����ս������������죩���ط�����
ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BATTLE_FLAG = 44	# �����ս������������죩ս��
ENTITY_TYPE_DANCE_KING					=45		# ��������(ʵ�����Ƴ�������)
ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER		= 46	# ���ս������
ENTITY_TYPE_DANCESEAT					= 47	# ������λ
ENTITY_TYPE_NPCDanceModel					= 48	# ��������ʾ�Ľ�ɫģ��
ENTITY_TYPE_CITY_WAR_FINAL_BASE			= 49	# �����ս�����ݵ�
ENTITY_TYPE_CAMP_XIAN_FENG				= 50	# ��Ӫ��������ȷ��
ENTITY_TYPE_CAMP_FENG_HUO_TOWER			= 51	# ��Ӫ������������
ENTITY_TYPE_CAMP_FENG_HUO_ALTAR			= 52	# ��Ӫ��������̳
ENTITY_TYPE_CAMP_FENG_HUO_BASE_TOWER	= 53	# ��Ӫ���������ط�����
ENTITY_TYPE_CAMP_FENG_HUO_BATTLE_FLAG	= 54	# ��Ӫ�������ս��



# ���ڱ�ʶ�����ĳ��Entity(��Ҫ��NPC)��ӵ����Щ����
ENTITY_FLAG_SKILL_TRAINER				= 1				# ����ѵ��ʦ
ENTITY_FLAG_CHAPMAN						= 2				# ����
ENTITY_FLAG_REPAIRER					= 3				# ����
ENTITY_FLAG_BANK_CLERK					= 4				# ���а���Ա
ENTITY_FLAG_POSTMAN						= 5				# �ʲ�
ENTITY_FLAG_AUCTIONEER					= 6				# ����ʦ
ENTITY_FLAG_TRANSPORT					= 7				# ������
ENTITY_FLAG_QUEST_ISSUER				= 8				# ���񷢷���
ENTITY_FLAG_SPEAKER						= 9				# ˵���ߣ�ע�����п��ԶԻ���NPC�����ﶼӦ�����ô�ѡ�ֻ�����˴�ֵ���ͻ��˲�Ӧ����Ӧ�Ի�������������жϣ��˱�־����δ��AI��ʱ�ر�NPC�ĶԻ����ܣ���δʵ�֣�
ENTITY_FLAG_QUEST_BOX					= 10			# ��������
ENTITY_FLAG_EQUIP_MAKER					= 11			# װ������ʦ
ENTITY_FLAG_PET_CARE					= 12			# ���ﱣ��Ա
ENTITY_FLAG_MONSTER_INITIATIVE			= 13
ENTITY_FLAG_CAN_CATCH					= 14			# �ɲ�׽����
ENTITY_FLAG_COLLECT_POINT				= 15			# �ɼ��� by ����
ENTITY_FLAG_COPY_STARTING				= 16			# �������ڽ�����
ENTITY_FLAG_QUEST_STARTING				= 17			# �������ڽ�����
ENTITY_FLAG_QUEST_WORKING				= 18			# NPCOBJECT�������������
ENTITY_FLAG_CHANG_COLOR_RED				= 19			# npcģ�ͱ�Ϊ��ɫ
ENTITY_FLAG_CAN_NOT_SELECTED			= 20			# ���ܱ���ɫ���ѡ��
ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER		= 21			# ���Ա����﹥����־
ENTITY_FLAG_UNVISIBLE					= 22			# �ö��󲻿ɼ�
ENTITY_FLAG_CHRISTMAS_HORSE				= 23			# ʥ���������־
ENTITY_FLAG_MONSTER_FLY					= 24			# �ͻ��˿��Ա���monster�ڿ�������(������monster��filter)
ENTITY_FLAG_CANT_BE_HIT_BY_ROLE			= 25			# �����Ա���ҹ�����־(˫��)
ENTITY_FLAG_GUARD						= 26			# ����
ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE	= 27			# ����ս��״̬��ת���־
ENTITY_FLAG_ONLY_FACE_LEFT_OR_RIGHT		= 28			# �����Ϸ���ﳯ���־
ENTITY_FLAG_MONSTER_THINK				= 29			# ���ﲻ�����AOI��Χ��Ҳ����think�ı�־
ENTITY_FLAG_NOT_CHECK_AND_MOVE			= 30			# ���ﲻ���Լ�����ѡ��վλ�ı�־
ENTITY_FLAG_NOT_FULL					= 31			# ����Ѫ�������
ENTITY_FLAG_ALAWAY_SHOW_NAME			= 32			# ��������Ӱ�죬����һֱ��ʾ���ֱ�ʶ
ENTITY_VOLATILE_ALWAYS_OPEN             = 33            # ���곯��ͬ��һֱ��
ENTITY_FLAG_FRIEND_ROLE             	= 34            # ��ҶԹ����Ѻ�
ENTITY_FLAG_NPC_NAME					= 35			# ͷ������ǿ����ʾΪNPC�ĸ�ʽ
ENTITY_FLAG_RAD_FOLLOW					= 36			# �ε���־
ENTITY_VOLATILE_ALWAYS_CLOSE			= 37			# ���곯��ͬ��һֱ�رգ����ڷ����������ͣ�
ENTITY_FLAG_CANT_BE_HIT_BY_MONSTER		= 38			# �����Ա����﹥����־������
ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2		= 39			# �����Ա���ҹ�����־������
ENTITY_FLAG_HEAD_ALWAYS_SHOW			= 40			# ͷ�����ƺ�Ѫ��һֱ��ʾ
ENTITY_FLAG_RAD_FOLLOW_ACTION			= 41			# ƥ���ε�������־
ENTITY_FLAG_ALAWAY_HIDE_NAME			= 42			# ���ι�������
ENTITY_FLAG_ALAWAY_HIDE_LEVEL			= 43			# ���ι���ȼ�
ENTITY_FLAG_ALAWAY_HIDE_HPBAR			= 44			# ���ι���Ѫ��
ENTITY_FLAG_CLOSE_FADE_MODEL			= 45			# �رչ���ģ�͵��뵭��
ENTITY_FLAG_ALAWAY_LIE_DOWN				= 46			# monster����״̬��������������
ENTITY_FLAG_ALAWAY_HIDE_CMAP			= 47			# ���ι�����Ӫ��ʾ
ENTITY_FLAG_MODEL_COLLIDE				= 48			# �ͻ���ģ��������ʵ��ײ
ENTITY_FLAG_SPECIAL_BOSS				= 49			# ����boss�������ֱ�־λ���ڹ������ʱ����ʾ��ͷ�����ͷ��������ʾboss��ǰ����Ŀ�ꡣ
ENTITY_FLAG_ALAWAY_HIDE_QUEST			= 50			# ���ι���������
ENTITY_FLAG_SHOW_DAMAGE_VALUE			= 51			# ��ʾNPC�˺���ֵ
ENTITY_FLAG_CANT_HIT_AND_BE_HIT_MONSTER	= 52			# �����Ա����﹥����־��˫��

# ----------------------------------------------------
# ��ҵ�ǰ����ӵ�еı��
ROLE_FLAG_CAPTAIN						= 1				# �ӳ�
ROLE_FLAG_MERCHANT						= 2				# ����״̬
ROLE_FLAG_XL_ROBBING					= 3				# ��¡��������
ROLE_FLAG_BLOODY_ITEM					= 4				# Я����Ѫ��Ʒ
ROLE_FLAG_ICHOR							= 5 			# ��ҩ����״̬
ROLE_FLAG_DRIVERING_DART				= 6 			# �ڼ�ʻ�ڳ�״̬
ROLE_FLAG_SPREADER						= 7 			# �ƹ�Ա
ROLE_FLAG_XL_DARTING					= 8				# ��¡������
ROLE_FLAG_CP_DARTING					= 9				# ��ƽ������
ROLE_FLAG_CP_ROBBING					= 10			# ��ƽ��������
ROLE_FLAG_TEAMMING						= 11 			# �����
ROLE_FLAG_SPEC_COMPETETE				= 12 			# ����ĳ���⾺����
ROLE_FLAG_FLY_TELEPORT					= 13 			# ���贫��
ROLE_FLAG_TISHOU						= 14 			# �������״̬
ROLE_FLAG_TONG_BAG						= 15			# �򿪰��ֿ�״̬ by����
ROLE_FLAG_REGISTER_MASTER				= 16			# ע����ͽ���
ROLE_FLAG_COUPLE_AGREE					= 17			# ���ͬ����������
ROLE_FLAG_AUTO_FIGHT					= 18			# ��ҽ����Զ�ս�����
ROLE_FLAG_CITY_WAR_FUNGUS				= 19			# ��ս�ɵ�Ģ���ߵı��
ROLE_FLAG_SAFE_AREA						= 20			# ��ȫ����
ROLE_FLAG_HIDE_INFO						= 21			# ������ݱ�־
ROLE_FLAG_AREA_SKILL_ONLY				= 22			# �ռ似�ܱ�־,��˼��ָ��ǰֻ��ʹ������ռ����õļ��ܡ�
ROLE_FLAG_FLY							= 23			# ������

ROLE_FLAG_ROLE_RECORD_INIT_OVER			= 30	#��ɫ��ʼ�����roleRecord�ı�־
ROLE_FLAG_ACCOUNT_RECORD_INIT_OVER		= 31	#��ɫ��ʼ�����accountRecord�ı�־
ROLE_FLAG_FORBID_TOPSPEED		= 32	#��ֹ�޸��ٶ�����ֵ���

# --------------------------------------------------------------------
# ��ɫ״̬
# --------------------------------------------------------------------
ENTITY_STATE_FREE						= 0				# ����״̬
ENTITY_STATE_DEAD						= 1				# ����״̬
ENTITY_STATE_REST						= 2				# ��Ϣ״̬
ENTITY_STATE_FIGHT						= 3				# ս��״̬
ENTITY_STATE_PENDING					= 4				# δ��״̬
ENTITY_STATE_HANG						= 5				# ����״̬(�жϽ���������ģ��)
ENTITY_STATE_VEND						= 6				# ��̯״̬
ENTITY_STATE_RACER						= 7				# ����״̬�����磺����
ENTITY_STATE_CHANGING					= 8				# ����״̬���磺���㣬��������ȣ�
ENTITY_STATE_QUIZ_GAME					= 9				# �ʴ�״̬
ENTITY_STATE_DANCE						= 10			# ����״̬
ENTITY_STATE_REQUEST_DANCE				= 11			# ��������״̬
ENTITY_STATE_DOUBLE_DANCE				= 12			# ˫������״̬(����ENTITY_STATE_DANCE��Ϊ�˿ͻ��˲��Ŷ���)
ENTITY_STATE_ENVIRONMENT_OBJECT			= 13			# �������״̬
ENTITY_STATE_PICK_ANIMA					= 14			# ʰȡ����
ENTITY_STATE_MAX						= 15			# MAX



ACTION_FORBID_MOVE						= 0x00000001	# �������ƶ���־( ԭ����ACTION_MOVE )
ACTION_FORBID_CHAT						= 0x00000002	# �����������־( ԭ����ACTION_CHAT )
ACTION_FORBID_USE_ITEM					= 0x00000004	# ������ʹ����Ʒ��־( ԭ����ACTION_USE_ITEM )
ACTION_FORBID_WIELD						= 0x00000008	# ������װ����Ʒ��־( ԭ����ACTION_WIELD )
ACTION_FORBID_ATTACK					= 0x00000010	# ����������־(��ͨ������)( ԭ����ACTION_ATTACK )
ACTION_FORBID_SPELL_PHY					= 0x00000020	# ������ʹ�������ܱ�־
ACTION_FORBID_SPELL_MAGIC				= 0x00000040	# ������ʹ�÷������ܱ�־
ACTION_FORBID_TRADE						= 0x00000080	# �������ױ�־( ԭ����ACTION_TRADE )
ACTION_FORBID_FIGHT						= 0x00000100	# ���������ս����־( ԭ����ACTION_FIGHT )
ACTION_ALLOW_VEND						= 0x00000200	# �����̯״̬
ACTION_FORBID_JUMP						= 0x00000400	# ��������Ծ״̬
ACTION_FORBID_PK						= 0x00000800	# ������PK
ACTION_FORBID_CALL_PET					= 0x00001000	# �������г���
ACTION_FORBID_TALK						= 0x00002000	# ��������NPC�Ի�
ACTION_FORBID_BODY_CHANGE				= 0x00004000	# ���������
ACTION_FORBID_VEHICLE					= 0x00008000	# ���������
ACTION_ALLOW_DANCE						= 0x00010000	# ��������״̬
ACTION_FORBID_INTONATING				= 0x00020000	# ����������
ACTION_FORBID_CHANGE_MODEL				= 0x00040000	# ������װ�������ģ��

#��ϱ�־
ACTION_FORBID_SPELL = ACTION_FORBID_SPELL_PHY | ACTION_FORBID_SPELL_MAGIC






# ������״̬
M_SUB_STATE_NONE						= 0 		# ��
M_SUB_STATE_FLEE						= 1 		# ����
M_SUB_STATE_CHASE						= 2 		# ׷��
M_SUB_STATE_WALK						= 3 		# ���ת��
M_SUB_STATE_GOBACK						= 4 		# ս����������
M_SUB_STATE_CONTINUECHASE				= 5   		# ����߶�,�����޸�navigateFollow�׳����쳣

# entity ��̬
ENTITY_POSTURE_NONE						= 0			# ����̬
ENTITY_POSTURE_DEFENCE					= 1			# ����
ENTITY_POSTURE_VIOLENT					= 2			# ��
ENTITY_POSTURE_DEVIL_SWORD				= 3			# ħ��
ENTITY_POSTURE_SAGE_SWORD				= 4			# ʥ��
ENTITY_POSTURE_SHOT						= 5			# ����
ENTITY_POSTURE_PALADIN					= 6			# ����
ENTITY_POSTURE_MAGIC					= 7			# ����
ENTITY_POSTURE_CURE						= 8			# ҽ��


# --------------------------------------------------------------------
# about role( from L3Common )
# --------------------------------------------------------------------
# �Ա�
GENDER_MALE								= 0x0		# ����
GENDER_FEMALE							= 0x1		# Ů��

# ְҵ
CLASS_UNKNOWN							= 0x00		# δ֪
CLASS_FIGHTER							= 0x10		# սʿ
CLASS_SWORDMAN							= 0x20		# ����
CLASS_ARCHER							= 0x30		# ����
CLASS_MAGE								= 0x40		# ��ʦ
CLASS_PALADIN							= 0x50		# ǿ����սʿ��NPCר�ã�
CLASS_WARLOCK							= 0x60		# ��ʦ( ��ȥ�� )
CLASS_PRIEST							= 0x70		# ��ʦ( ��ȥ�� )

# entity ��Ӫ
ENTITY_CAMP_NONE						= 0 # û����Ӫ��
ENTITY_CAMP_TAOISM						= 1 # �����Ӫ
ENTITY_CAMP_DEMON						= 2 # ħ����Ӫ

# ����
# phw: �����й��ң���Ϊ���������壺���͡����ֵ���ħ��
YANHUANG								= 0x0000	# �׻ƹ�
JIULI									= 0x0100	# �����
FENGMING								= 0x0200	# ������

# ��������
RCMASK_GENDER							= 0x0000000f	# �Ա�����
RCMASK_CLASS							= 0x000000f0	# ְҵ����
RCMASK_RACE								= 0x00000f00	# ��������
RCMASK_FACTION							= 0x000ff000	# ��������
RCMASK_CAMP								= 0x00f00000	# ������Ӫ
RCMASK_ALL								= 0x00ffffff	# RCMASK_GENDER | RCMASK_CLASS | RCMASK_RACE | RCMASK_FACTION | RCMASK_CAMP






# ����ڸ��ֹ�ϵ�е���ݱ��( wsf )
TEACH_PRENTICE_FLAG							= 0x001			# ʦͽ��ϵ�е�ͽ�����
TEACH_MASTER_FLAG							= 0x002			# ʦͽ��ϵ�е�ʦ�����

SWEETIE_IDENTITY							= 0x004			# ���˹�ϵ���

COUPLE_AGREEMENT							= 0x008			# ͬ���Ϊ���޹�ϵ�ı��
COUPLE_IDENTITY								= 0x010			# ���޹�ϵ���

TEACH_REGISTER_MASTER_FLAG					= 0x020			# �Ƿ�ע����ͽ�ı��


# --------------------------------------------------------------------
# �ͻ��˲�����¼����
# --------------------------------------------------------------------
OPRECORD_COURSE_HELP						= 1				# ���̰�����¼����
OPRECORD_UI_TIPS							= 2				# UI ��ʾ��¼
OPRECORD_PIXIE_HELP							= 3				# �����������¼



# --------------------------------------------------------------------
# about npc
# --------------------------------------------------------------------
# NPC����Ϊ( from L3Define.py )
NPC_BEHAVE_STATE_NONE					= 0				# ��
NPC_BEHAVE_STATE_WALK					= 1				# ��
NPC_BEHAVE_STATE_RUN					= 2				# ��


# --------------------------------------------------------------------
# about pet( hyw )
# --------------------------------------------------------------------
# �����ӡ��
PET_STAMP_SYSTEM						= 1				# ϵͳӡ��
PET_STAMP_MANUSCRIPT					= 2				# ��дӡ��

# ���ﱲ��
PET_HIERARCHY_GROWNUP					= 0x01			# �������
PET_HIERARCHY_INFANCY1					= 0x02			# һ������
PET_HIERARCHY_INFANCY2					= 0x03			# ��������
# �������
PET_TYPE_STRENGTH						= CLASS_FIGHTER		# ������( ��Ӧսʿ )
PET_TYPE_BALANCED						= CLASS_SWORDMAN	# ������( ��Ӧ���� )
PET_TYPE_SMART							= CLASS_ARCHER		# ������( ��Ӧ���� )
PET_TYPE_INTELLECT						= CLASS_MAGE		# ������( ��Ӧ��ʦ )
# ����
PET_HIERARCHY_MASK						= 0x0f			# ���ﱲ������
PET_TYPE_MASK							= 0xf0			# �����������

# �����Ը�
PET_CHARACTER_SUREFOOTED				= 1				# ���ص�
PET_CHARACTER_CLOVER					= 2				# �ϻ۵�
PET_CHARACTER_CANNILY					= 3				# ������
PET_CHARACTER_BRAVE						= 4				# �¸ҵ�
PET_CHARACTER_LIVELY					= 5				# ���õ�

# -------------------------------------------
# �����÷�ʽ
PET_GET_CATHOLICON						= 1				# ��ͯ��
PET_GET_RARE_CATHOLICON					= 2				# ϴ�赤
PET_GET_SUPER_CATHOLICON					= 3			# ������ͯ��
PET_GET_SUPER_RARE_CATHOLICON				= 4			# ����ϴ�赤
PET_GET_SUPER_CATCH							= 5			# ���ܲ�׽
PET_GET_CATCH							= 6				# ��׽
PET_GET_PROPAGATE						= 7				# ��ֳ
PET_GET_EGG1							= 8				# ������ﵰ
PET_GET_EGG2							= 9				# 1�����ﵰ
PET_GET_EGG3							= 10			# 2�����ﵰ

# -------------------------------------------
# ����״̬
PET_STATUS_WITHDRAWED					= 1				# ����״̬
PET_STATUS_WITHDRAWING					= 2				# ���ڻ���״̬
PET_STATUS_CONJURING					= 3				# �����ٻ�״̬
PET_STATUS_CONJURED						= 4				# ����״̬
# ������շ�ʽ
PET_WITHDRAW_COMMON						= 1				# ��������
PET_WITHDRAW_HP_DEATH					= 2				# ��Ѫ��Ϊ����������
PET_WITHDRAW_LIFE_DEATH					= 3				# ������Ϊ����������
PET_WITHDRAW_CONJURE					= 4				# ��������
PET_WITHDRAW_FREE						= 5				# ��������
PET_WITHDRAW_OWNER_DEATH				= 6				# ���������������
PET_WITHDRAW_OFFLINE					= 7				# ���߻���
PET_WITHDRAW_FLYTELEPORT				= 8				# ���贫�ͻ���
PET_WITHDRAW_GMWATCHER					= 9				# ����GM�۲��߻���
PET_WITHDRAW_BUFF						= 10			# buffҪ�����

# -----------------------------------------------------
# ������ƶ���Ϊ״̬
PET_ACTION_MODE_FOLLOW					= 0				# ����
PET_ACTION_MODE_KEEPING					= 1				# ͣ��
# �����ս����Ϊ״̬
PET_TUSSLE_MODE_ACTIVE					= 0				# ����
PET_TUSSLE_MODE_PASSIVE					= 1				# ����
PET_TUSSLE_MODE_GUARD					= 2				# ����


# -----------------------------------------------------
# ǿ������
PET_ENHANCE_COMMON						= 1				# ��ͨǿ��
PET_ENHANCE_FREE						= 2				# ����ǿ��
# ����ʯ����
PET_ANIMA_GEM_TYPE_CRACKED				= 1				# �����
PET_ANIMA_GEM_TYPE_COMMON				= 2				# ��ͨ��
PET_ANIMA_GEM_TYPE_PERFECT				= 3				# ������


# -----------------------------------------------------
# ��ʯ����
PET_GEM_TYPE_NONE						= 0				# δ֪��ʯ����
PET_GEM_TYPE_COMMON						= 1				# ��ͨ��ʯ
PET_GEM_TYPE_TRAIN						= 2				# ������ʯ
# ����Ĵ�����ʽ
PET_TRAIN_TYPE_NONE	  					= 0				# û�д���
PET_TRAIN_TYPE_COMMON					= 1				# ��ͨ������ʽ
PET_TRAIN_TYPE_HARD	  					= 2				# �̿������ʽ

# -----------------------------------------------------
# �ֿ�����
PET_STORE_TYPE_LARGE					= 1				# ��ֿ�
PET_STORE_TYPE_SMALL					= 2				# С�ֿ�

PET_STORE_STATUS_NONE					= 0				# δ����״̬
PET_STORE_STATUS_HIRING					= 1				# ����ʹ��״̬
PET_STORE_STATUS_OVERDUE				= 2				# ����״̬

# -----------------------------------------------------
# ���ﷱֳ״̬
PET_PROCREATE_STATUS_NONE				= 0				# û�з�ֳ
PET_PROCREATE_STATUS_PROCREATING		= 1				# ���ڷ�ֳ
PET_PROCREATE_STATUS_PROCREATED			= 2				# �ѷ�ֳ

# -----------------------------------------------------
# ���ﷱֳ����״̬
PET_PROCREATION_DEFAULT					= 0				# Ĭ��״̬�����û���г��ﷱֳ����
PET_PROCREATION_WAITING					= 1				# �ȴ�״̬����Ҵ���npc�Ի��Ƚ���ȴ�״̬
PET_PROCREATION_SELECTING 				= 2				# ѡ��ֳ����״̬
PET_PROCREATION_LOCK 					= 3				# ��������״̬
PET_PROCREATION_SURE					= 4				# ȷ���ύ��ֳ����״̬
PET_PROCREATION_COMMIT					= 5				# �ύ��ֳ����״̬


# --------------------------------------------------------------------
# about skill( from common/QuestDefine.py��designed by penghuawei )
# --------------------------------------------------------------------
# SKILL��Ч�����ͣ������п������Ե�Ч����������ֶ�ȡ�������Եĺ�δ�����Ч��������ȡ��
SKILL_EFFECT_STATE_BENIGN				= 1				# ����Ч��
SKILL_RAYRING_EFFECT_STATE_BENIGN		= 2				# �⻷����Ч��
SKILL_EFFECT_STATE_NONE					= 0				# δ�������ͣ���ӹ(��״̬)
SKILL_EFFECT_STATE_MALIGNANT			= -1			# ����
SKILL_RAYRING_EFFECT_STATE_MALIGNANT	= -2			# �⻷����
# ʩչ��ʽ
SKILL_CAST_OBJECT_TYPE_NONE				= 0				# ����ҪĿ���λ��;
SKILL_CAST_OBJECT_TYPE_POSITION			= 1				# ��λ��ʩչ;
SKILL_CAST_OBJECT_TYPE_ENTITY			= 2				# ��Ŀ��Entityʩչ;
SKILL_CAST_OBJECT_TYPE_ITEM				= 3				# ��Ŀ����Ʒʩչ
SKILL_CAST_OBJECT_TYPE_ENTITYS			= 4				# �Զ��Ŀ��Entityʩչ;
# �������÷�Χ
SKILL_SPELL_AREA_SINGLE					= 0				# ����
SKILL_SPELL_AREA_CIRCLE					= 1				# Բ������
SKILL_SPELL_AREA_RADIAL					= 2				# ֱ��
SKILL_SPELL_AREA_SECTOR					= 3				# ����
#����ʩ��
SKILL_SPELL_INTONATE = 0       #����ʩ��
SKILL_SPELL_RECEIVE_DALAY_TIME = 1 #��������ʩ��

# buff�����
BUFF_TYPE_NONE							= 0				# δ��������
BUFF_TYPE_ATTRIBUTE						= 1				# ��������
BUFF_TYPE_PHYSICS_ATTACK				= 2				# �������Ա�������
BUFF_TYPE_MAGIC_ATTACK					= 3				# ����������������
BUFF_TYPE_NOT_ATTACK					= 4				# �ǹ����Ա�������
BUFF_TYPE_RESIST						= 5				# ����
BUFF_TYPE_MOVE_SPEED					= 6				# �ƶ����ٶ�
BUFF_TYPE_SLOW_OPER						= 7				# ��������Ч��
BUFF_TYPE_AFFECT_ACTION					= 8				# Ӱ����ΪЧ��
BUFF_TYPE_AFFECT_CURE					= 9				# ����Ч���仯
BUFF_TYPE_BRING_DAMAGE					= 10			# ����Ч��
BUFF_TYPE_SPECILIZE_ACCORD				= 11			# ���������
BUFF_TYPE_IMMUNE						= 12			# ����Ч��
BUFF_TYPE_DERATE						= 13			# ����
BUFF_TYPE_DISCHARGE_SKILL				= 14			# ʩ��
BUFF_TYPE_IMBIBE						= 15			# ����
BUFF_TYPE_REFLECT						= 16			# ����Ч��
BUFF_TYPE_WEAPON						= 17			# ����Ч��
BUFF_TYPE_VAMPIRE						= 18			# ����ѪЧ��
BUFF_TYPE_RELATION_AWARD				= 19			# ��ϵ����Ч��
BUFF_TYPE_HIDE							= 20			# ����Ч��
BUFF_TYPE_DIFFUSE						= 21			# ��ɢЧ��
BUFF_TYPE_SYSTEM						= 22			# ϵͳBUFF
BUFF_TYPE_SHIELD1						= 23			# ת������I
BUFF_TYPE_SHIELD2						= 24			# ת������II
BUFF_TYPE_ATTACK_RANGE					= 25			# ��̱仯
BUFF_TYPE_ELEM_ATTACK_BUFF				= 26			# Ԫ�ع���
BUFF_TYPE_ELEM_DERATE_RATIO_BUFF		= 27			# Ԫ�ؿ���
BUFF_TYPE_COMPLEX_BASE_PROPERTY1		= 60			# �������Ը���I
BUFF_TYPE_COMPLEX_SPEED1				= 61			# �ٶȸ���I
BUFF_TYPE_COMPLEX_ATTACK				= 62			# ��������
BUFF_TYPE_COMPLEX_SHIELD				= 63			# �����ิ��
BUFF_TYPE_COMPLEX_SPEED2				= 64			# �ٶȸ���II
BUFF_TYPE_COMPLEX_BIDIRECTIONAL1		= 65			# ˫�򸴺�I
BUFF_TYPE_COMPLEX_BASE_PROPERTY2		= 66			# �������Ը���II
BUFF_TYPE_FLAW							= 70			# ����Ч��
BUFF_TYPE_COMPLEX_PUBLIC				= 99			# ����Ч��
BUFF_TYPE_ELEM_ATTACK_DEBUFF			= 126			# Ԫ�ع���
BUFF_TYPE_ELEM_DERATE_RATIO_DEBUFF		= 127			# Ԫ�ؿ���

#BUFF��Դ
BUFF_ORIGIN_NONE						= 0				# ����Դ����δ֪��Դ
BUFF_ORIGIN_EQUIP						= 1				# װ��
BUFF_ORIGIN_DRUG						= 2				# ҩˮ
BUFF_ORIGIN_SCROLL						= 3				# ����
BUFF_ORIGIN_EVENT						= 4				# �¼�
BUFF_ORIGIN_STATE1						= 5				# ״̬1
BUFF_ORIGIN_STATE2						= 6				# ״̬2
BUFF_ORIGIN_STATE3						= 7				# ״̬3
BUFF_ORIGIN_PUBLIC						= 8				# ����
BUFF_ORIGIN_FINISH						= 9				# �ռ�
BUFF_ORIGIN_SYSTEM						= 10			# ϵͳ���ͻ��˲���ʾ������ʾ��
BUFF_ORIGIN_YXLM						= 11			# Ӣ�����˰��ʧ�䱦�ظ�����NPC���۵�װ����buff
BUFF_ORIGIN_YXLM_COEXISTENT				= 12			# Ӣ�����˰��ʧ�䱦�ظ�����NPC���۵�װ����buff����ͬID��Buff�ɹ��棩

# ���ܻ�������
BASE_SKILL_TYPE_NONE					= 0				# �Ǽ��ܣ������ڼ��������ѵ�����ܡ���ͨ����������Ϊ����spell���ֵ�spell�ȶ�����һ�ࣩ
BASE_SKILL_TYPE_PASSIVE					= 1				# ��������
BASE_SKILL_TYPE_BUFF					= 2				# BUFF���� (��ΪBUFFʵ��Ҳ�Ǽ���ϵͳ�е�һԱ���������Ƕ���һ��ϵ�е�Type����)
BASE_SKILL_TYPE_PHYSICS_NORMAL			= 3				# ��ͨ������
BASE_SKILL_TYPE_PHYSICS					= 4				# ����ϵ����
BASE_SKILL_TYPE_MAGIC					= 5				# ����ϵ����
BASE_SKILL_TYPE_ITEM					= 6				# ����ϵ����
BASE_SKILL_TYPE_ACTION					= 7				# ��Ϊ����
BASE_SKILL_TYPE_DISPERSION				= 8				# ��ɢϵ����
BASE_SKILL_TYPE_ELEM					= 9				# Ԫ�ؼ���
BASE_SKILL_TYPE_POSTURE_PASSIVE			= 10			# ��̬�������ܣ�����ĳ����̬����Ч���ı������ܣ�



#BUFFϵͳ�ж϶���
BUFF_INTERRUPT_NONE						= 0				# ������ �޶���Ĵ��
BUFF_INTERRUPT_GET_HIT					= 1				# �ܴ��ʱ���
BUFF_INTERRUPT_REQUEST_CANCEL			= 2				# ����ֶ�����ȡ��BUFFʱ���
BUFF_INTERRUPT_ON_DIE					= 3				# ����ʱ���µĴ��
BUFF_INTERRUPT_ON_CHANGED_SPACE			= 4				# �л�����ʱ���´��
BUFF_INTERRUPT_CHANGE_TITLE				= 5				# �����ƺ�ʱ���µĴ�ϣ�16:14 2008-7-16��wsf
BUFF_INTERRUPT_RETRACT_VEHICLE			= 6				# ��������ж�(���ר��)
BUFF_INTERRUPT_RETRACT_PROWL			= 7				# �����ж���
BUFF_INTERRUPT_HORSE					= 8				# �����ж���
BUFF_INTERRUPT_INVINCIBLE_EFFECT		= 9				# ���и���Ч����buff��Ҫ��������ж��룬 �ṩ���������ж�
BUFF_INTERRUPT_POSTURE_CHANGE			= 10			# ��̬�л��ж�
BUFF_INTERRUPT_VEHICLE_OFF				= 11			# ������Ƴ����buff
BUFF_INTERRUPT_COMPLETE_VIDEO			= 12			#��Ƶ��������Ƴ�buff
BUFF_INTERRUPT_LAND_VEHICLE				= 13			#���½�����buff
BUFF_INTERRUPT_TELEPORT_FLY				= 14			#��Ϸ��贫��buff

# entity���ϵ�BUFF״̬����
#BUFF_STATE_NORMAL						= 0x00000000	# ����״̬
BUFF_STATE_HAND							= 0x00000001	# ʧЧ������״̬ ��ʱֹͣ
BUFF_STATE_DISABLED						= 0x00000002	# ʧЧ״̬ ��Ȼ��ʱ

#���ܶ���
SHIELD_TYPE_VOID						= 0				# �����ͻ��� �������κ������˺�
SHIELD_TYPE_PHYSICS						= 1				# ������ ���������˺�
SHIELD_TYPE_MAGIC						= 2				# �������� ���շ����˺�

# �˺����ͣ���Ҫ���ڱ�ʶ���ܵ��������͵��˺�
DAMAGE_TYPE_VOID 						= 0x00			# �������˺�(��ֵһ��ֻ�����˺��������ͺͻ�����������)
DAMAGE_TYPE_PHYSICS_NORMAL				= 0x01			# ��ͨ�������˺�
DAMAGE_TYPE_PHYSICS						= 0x02			# �������˺�
DAMAGE_TYPE_MAGIC						= 0x04			# �������������˺�
DAMAGE_TYPE_FLAG_DOUBLE					= 0x08			# ����������һ��
DAMAGE_TYPE_FLAG_BUFF					= 0x10			# �˺�����buff����
DAMAGE_TYPE_REBOUND						= 0x20			# �����˺�
DAMAGE_TYPE_DODGE						= 0x40			# �˺�Ϊ0 ������ ����Ȼ���ڴ˴��˺������е�һ������
DAMAGE_TYPE_RESIST_HIT					= 0x100			# �м� ����Ȼ���ڴ˴��˺������е�һ������
DAMAGE_TYPE_ELEM_HUO					= 0x200			# ��Ԫ���˺�
DAMAGE_TYPE_ELEM_XUAN					= 0x400			# ��Ԫ���˺�
DAMAGE_TYPE_ELEM_LEI					= 0x600			# ��Ԫ���˺�
DAMAGE_TYPE_ELEM_BING					= 0x800			# ��Ԫ���˺�
DAMAGE_TYPE_ELEM						= 0x1000		# Ԫ���˺�����
DAMAGE_TYPE_DROP						= 0x900		# �����˺�

# ��������������Щ�˻���������������w
RECEIVER_CONDITION_ENTITY_NONE			= 0x00		# ������
RECEIVER_CONDITION_ENTITY_SELF			= 0x01		# �Լ�
RECEIVER_CONDITION_ENTITY_TEAMMEMBER	= 0x02		# ��Ա
RECEIVER_CONDITION_ENTITY_MONSTER		= 0x03		# ����
RECEIVER_CONDITION_ENTITY_ROLE			= 0x04		# ���
RECEIVER_CONDITION_ENTITY_ENEMY			= 0x05		# ����
RECEIVER_CONDITION_ENTITY_NOTATTACK		= 0x06		# ���ɹ�����
RECEIVER_CONDITION_KIGBAG_ITEM			= 0x07		# ��Ʒ
RECEIVER_CONDITION_ENTITY_RANDOMENEMY	= 0x08		# ���� ����������ڹ�������N������
RECEIVER_CONDITION_ENTITY_SELF_PET		= 0x09		# ������ս���� (�൱������ ����ѡ��һ��Ŀ��)
RECEIVER_CONDITION_ENTITY_PET			= 0x10		# ��ս���� ����Ҫ���ѡ��һ�����
RECEIVER_CONDITION_ENTITY_NPC			= 0x11		# NPC
RECEIVER_CONDITION_ENTITY_SELF_SLAVE_MONSTER = 0x12 #��������
RECEIVER_CONDITION_ENTITY_OTHER_ROLE	= 0x13		# �������
RECEIVER_CONDITION_ENTITY_NPC_OR_MONSTER= 0x14		# �����NPC
RECEIVER_CONDITION_ENTITY_NPCOBJECT		= 0x15		# ����NPC
RECEIVER_CONDITION_ENTITY_NOT_ENEMY_ROLE= 0x16		# �ǵж����
RECEIVER_CONDITION_ENTITY_VEHICLE_DART	= 0x17		# �ڳ�
RECEIVER_CONDITION_ENTITY_ROLE_ONLY		= 0x18		# ���������Ч����ʷԭ��ԭ������������Ϊ��ҵļ�����ض�Ҳ���
RECEIVER_CONDITION_ENTITY_ROLE_ENEMY_ONLY = 0x19	# ���Եж������Ч
RECEIVER_CONDITION_ROLE_WITH_COMPLETED_QUESTS = 0x1a	# ��Ҫ������ָ������
RECEIVER_CONDITION_ROLE_HAS_UNCOMPLETED_QUESTS = 0x1b	# ��Ҫӵ������һ��δ�������

#���ܶ���entity����
SKILL_TARGET_OBJECT_NONE 			= 0x00
SKILL_TARGET_OBJECT_ENTITY 			= 0x01
SKILL_TARGET_OBJECT_POSITION		= 0x02
SKILL_TARGET_OBJECT_ITEM 			= 0x03
SKILL_TARGET_OBJECT_ENTITYS			= 0x04
SKILL_TARGET_OBJECT_ENTITYPACKET	= 0x05
# ʩ������������Щ�˿���ʩչĳ��������
# ���в�����Ϻ��ǡ��롱��ϵ����ˣ�ĳЩ״̬��Ϻ󽫻�������⣬
# ��CASTER_CONDITION_FIGHT_STATE��CASTER_CONDITION_FIGHT_NOT_STATE��Ͻ����·�������ʩ��
CASTER_CONDITION_ATTACK_ALLOW			= 0x00000001		# ����ʹ����ͨ������
CASTER_CONDITION_SPELL_ALLOW			= 0x00000002		# ����ʩ��(���²�����ʩ����ԭ��ܶ࣬�类��Ĭ�����Ե�)
CASTER_CONDITION_BUFF_NO_HAVE			= 0x00000004		# ���ϲ�����ָ�����͵�buff
CASTER_CONDITION_BUFF_HAVE				= 0x00000008		# ���ϱ������ָ�����͵�buff
CASTER_CONDITION_FIGHT_STATE			= 0x00000010		# ���봦��ս��״̬
CASTER_CONDITION_FIGHT_NOT_STATE		= 0x00000020		# ���봦�ڷ�ս��״̬
CASTER_CONDITION_STATE_DEAD				= 0x00000040		# �������ߣ����ͨ������ͨ��ʮ�ּܸ����Լ��ļ��ܣ�
CASTER_CONDITION_STATE_LIVE				= 0x00000080		# ���ŵ�
CASTER_CONDITION_EMPTY_HAND				= 0x00000100		# �������(��ֻ�ֶ�����)
CASTER_CONDITION_EMPTY_PRIMARY_HAND		= 0x00000200		# ��(��������)�ֱ���Ϊ��
CASTER_CONDITION_WEAPON_CONFINE			= 0x00000400		# ����װ��������(����ʲô����)
CASTER_CONDITION_POSSESS_ITEM			= 0x00000800		# ����ӵ��ĳ��Ʒ
CASTER_CONDITION_WEAPON_EQUIP			= 0x00001000		# ����װ����ĳ���͵�����
CASTER_CONDITION_MOVE_NOT_STATE			= 0x00002000		# ����û�д����ƶ�״̬
CASTER_CONDITION_SHIELD_EQUIP			= 0x00004000		# ����װ���˶���
CASTER_CONDITION_STATE_NO_PK			= 0x00008000		# ��PK״̬
CASTER_CONDITION_IN_APPOINT_SPACE		= 0x00010000		# ��Ҫָ����ͼ
CASTER_CONDITION_WEAPON_TALISMAN		= 0x00020000		# ��Ҫװ������
CASTER_CONDITION_IN_APPOINT_SPACE_NOT_USE = 0x00040000		# ָ����ͼ����ʹ��
CASTER_CONDITION_NOT_ENEMY_STATE		= 0x00080000		# �Ƿ�Ϊ�ж�״̬
CASTER_CONDITION_POSTURE				= 0x00100000		# ����ĳ����̬
CASTER_CONDITION_SPACE_SUPPORT_FLY		= 0x00200000		# �ռ�֧�ַ���
CASTER_CONDITION_IS_FLYING_STATUS		= 0x00400000		# ���ڷ���״̬
CASTER_CONDITION_IS_GROUND_STATUS		= 0x00800000		# ���ڵ���״̬


# ʩչ���������������������
SKILL_REQUIRE_TYPE_NONE					= 0x01				# ������
SKILL_REQUIRE_TYPE_MANA					= 0x02				# ��Ҫħ��
SKILL_REQUIRE_TYPE_ITEM					= 0x03				# ��Ҫ��Ʒ
SKILL_REQUIRE_TYPE_MONEY				= 0x04				# ��Ҫ��Ǯ
SKILL_REQUIRE_TYPE_VITALITY				= 0x05				# ��Ҫ����ֵ
SKILL_REQUIRE_TYPE_HP   				= 0x06				# ��Ҫ����ֵ

# Ч��״̬
EFFECT_STATE_SLEEP						= 0x0001			# ��˯Ч��
EFFECT_STATE_VERTIGO					= 0x0002			# ѣ��Ч��
EFFECT_STATE_FIX						= 0x0004			# ����Ч��
EFFECT_STATE_HUSH_PHY					= 0x0008			# �����ĬЧ��
EFFECT_STATE_HUSH_MAGIC					= 0x0010			# ������ĬЧ��
EFFECT_STATE_INVINCIBILITY				= 0x0020			# �޵�Ч��
EFFECT_STATE_NO_FIGHT					= 0x0040			# ��սЧ��
EFFECT_STATE_PROWL						= 0x0080			# Ǳ��Ч��
EFFECT_STATE_FOLLOW						= 0x0100			# ���棨��Ҵ�����Ӹ����У�
EFFECT_STATE_LEADER						= 0x0200			# ��������Ҵ�����������У�
EFFECT_STATE_ALL_NO_FIGHT				= 0x0400			# ȫ����սЧ��(�����κ�entity)
EFFECT_STATE_WATCHER					= 0x0800			# GM�۲���Ч�����޷��������޷����������޷����鿴��
EFFECT_STATE_DEAD_WATCHER				= 0x1000			# �����������������޷��������޷����������޷����鿴��
EFFECT_STATE_HEGEMONY_BODY				= 0x2000			# ����Ч����������������ܻ�
EFFECT_STATE_BE_HOMING				= 0x4000			# ����Ч��,���������ƶ�

# --------------------------------------------------------------------
# custom id of skill define( designed by kebiao )
# --------------------------------------------------------------------
# �����Զ��弼��ID
SKILL_ID_PHYSICS						= 1				# ��ͨ����������ID
SKILL_ID_SMART_PET_PHYSICS				= 2				# �����ͳ�����ͨ����������ID
SKILL_ID_INTELLECT_PET_MAGIC			= 3				# �����ͳ�����ͨħ����������ID
SKILL_ID_PLAYER_TELEPORT				= 322361002		# ��ҵ�Ĭ�ϴ��ͼ���
SKILL_ID_CATCH_PRISON					= 780040001		# ץ���������ļ���ID
SKILL_ID_CONJURE_PET 					= 101 			# �ٻ�����
SKILL_ID_SGL_DANCING					= 201			# ������
SKILL_ID_DBL_DANCING					= 202			# ˫����
#SKILL_ID_TEAM_DANCING					= 203			# ���鹲��
SKILL_ID_FACE_DRINK						= 11			# ��ˮ
SKILL_ID_FACE_BYE						= 12			# ����
SKILL_ID_FACE_REFUSE					= 13			# �ܾ�
SKILL_ID_FACE_DEFY						= 14			# ����
SKILL_ID_FACE_KNEE						= 15			# ��
SKILL_ID_FACE_TALK						= 16			# ��̸
SKILL_ID_FACE_SMILE						= 17			# Ц
SKILL_ID_FACE_SIT						= 18			# ��
SKILL_ID_FACE_LIE						= 19			# ��



SKILL_ID_LIMIT							= 1000			# �������ü���ID�߽磬С��1000Ϊ��������
# --------------------------------------------------------------------
# ai  define( designed by kebiao )
# --------------------------------------------------------------------
AI_TYPE_GENERIC_FREE					=	1			# ͨ��AI���� free״̬��
AI_TYPE_GENERIC_ATTACK					=	2			# ͨ��AI���� ս��״̬��
AI_TYPE_SCHEME							=	3			# ����AI���� ս��״̬��
AI_TYPE_SPECIAL							=	4			# ����AI���� ս��״̬��
AI_TYPE_EVENT							=	5			# �¼�AI���� �κ�״̬��
AI_TYPE_COMBO							=	6			# ����AI���� ս��״̬��
AI_TYPE_COMBO_ACTIVERATE				= 	7			# ����AIִ�и��� ս��״̬��

# ai �¼�
AI_EVENT_NONE							=	0			# ζ֪�������¼�
AI_EVENT_ENEMY_LIST_CHANGED				=	1			# ս���б��ı�
AI_EVENT_DAMAGE_LIST_CHANGED			=	2			# �˺��б��ı�
AI_EVENT_CURE_LIST_CHANGED				=	3			# �����б��ı�
AI_EVENT_FRIEND_LIST_CHANGED			=	30			# �ѷ��б��ı�
AI_EVENT_ATTACKER_ON_REMOVE				=	32			# ��ǰ���������Ƴ������б�ʱ(����,������Ұ,�Ҳ�����)
AI_EVENT_STATE_CHANGED					=	8			# ״̬�ı�
AI_EVENT_SUBSTATE_CHANGED				=	29			# sub״̬�ı�
AI_EVENT_SKILL_HIT						=	9			# ����������ʱ
AI_EVENT_SKILL_DOUBLEHIT				=	12			# ����������һ��ʱ
AI_EVENT_SKILL_MISS						=	15			# ������δ����
AI_EVENT_SKILL_RESISTHIT				= 	27			# Ŀ���м�������
AI_EVENT_SKILL_RECEIVE_HIT				=	17			# ��������
AI_EVENT_SKILL_RECEIVE_DOUBLEHIT		=	19			# �����ܵ�����һ��
AI_EVENT_HP_CHANGED						=	21			# ����HP�ı�ʱ
AI_EVENT_MP_CHANGED						=	22			# ����MP�ı�ʱ
AI_EVENT_ADD_REMOVE_BUFF				=	23			# ����BUFF״̬�иı�
AI_EVENT_SPELL							=	25			# ����ʩ��ʱ
AI_EVENT_TARGET_DEAD					=	26			# ��ǰĿ������ʱ
AI_EVENT_COMMAND						=	28			# �յ�AI����
AI_EVENT_SPELL_ENTERTRAP				=	33			# ��entity��������뿪���������¼�
AI_EVENT_ENTITY_ON_DESTROY				=	31			# entity������ʱ (����������)
AI_EVENT_ENTITY_ON_DEAD					=   34			# entity���� ����
AI_EVENT_SPELL_OVER						=	35			# ����ʩ�����
AI_EVENT_SPELL_INTERRUPTED				=	36			# ���ܱ�����¼�
AI_EVENT_TALK							=	37			# �Ի�����AI�¼�
AI_EVENT_BOOTY_OWNER_CHANGED			=	38			# ս��Ʒӵ���߸ı���
AI_EVENT_CHANGE_BATTLECAMP				=	39			# �ı������Ӫ�¼�
AI_EVENT_ENTER_GUARD_TRAP				=	40			# ��entity�������������¼�

# --------------------------------------------------------------------
# about kitbag( from common/L3Define.py��designed by penghuawei )
# --------------------------------------------------------------------
KB_COUNT							= 7		# ��󱳰�������������װ������( ԭ����C_KITBAGMAX )
KB_EQUIP_ID							= 0x00	# װ������λ�ã����ֵ��������self.KB_COMMON_ID �� KB_COMMON_ID + KB_COUNT֮���ֵ(ԭ����C_EQUIP_ORDER )
KB_COMMON_ID						= 0x01	# �������Ͽ�ʼλ��(ԭ����C_KITBAG_ORDER )
KB_EXCONE_ID						= 0x02	# �������1
KB_EXCTWO_ID						= 0x03	# �������2
KB_EXCTHREE_ID						= 0x04	# �������3
KB_EXCFOUR_ID						= 0x05	# �������4
KB_EXCFIVE_ID						= 0x06	# �������5
KB_EXCSIX_ID						= 0x07	# �������6
KB_CASKET_ID						= 0x08	# ���ϻ����λ
KB_RACE_ID							= 0x09	# ������λ
KB_MAX_SPACE						= 0xff	# �����������ռ�λ
KB_MAX_COLUMN						= 0x06	# �������������
KB_CASKET_SPACE						= 0xfd	# ���ϻˮ��ժ����ʼ����
KB_ZD_MAX_SPACE						= 20	# ֤��ϵͳ�����������ռ�
KB_ZD_MAX_EQUIP_SPACE				= 8		# ֤��ϵͳ��ɫ�������ռ�
KB_ZHENG_DAO_ID						= 0x10	# ֤���������
KB_COM_DAO_XIN_ID					= 0x11	# ���Ľ�����ͨ����
KB_EQUIP_DAO_XIN_ID					= 0x12	# ��ɫ���Ľ������



# --------------------------------------------------------------------
# about bankBags( from common/L3Define.py��designed by wangshufeng )
# --------------------------------------------------------------------
BANK_COUNT							= 7		# Ǯׯ����������
BANK_COMMON_ID						= 0x00	# ǮׯĬ�ϵĿ�ʼ����λ��
BANK_SORT_BY_ID						= 0		# ��Ʒ�������ͣ����ͣ�id��
BANK_SORT_BY_QUALITY				= 1		# ��Ʒ�������ͣ�Ʒ��
BANK_SORT_BY_PRICE					= 2		# ��Ʒ�������ͣ��۸�
BANK_SORT_BY_LEVEL					= 3		# ��Ʒ�������ͣ��ȼ�


# --------------------------------------------------------------------
# about quickbar( from common/L3Define.py��designed by huangyongwei )
# --------------------------------------------------------------------
QB_ITEM_NONE						= 0		# �տ����
QB_ITEM_SKILL						= 1		# ���ܿ����
QB_ITEM_TACT						= 2		# ��ɫ���������
QB_ITEM_KITBAG						= 3		# �����е���Ʒ���߿����
QB_ITEM_EQUIP						= 4		# װ���еĵ���
QB_ITEM_PET_SKILL					= 5		# ���＼�ܿ����
QB_ITEM_VEHICLE						= 6		# �����Ʒ�����

# --------------------------------------------------------------------
QB_IDX_POSTURE_NONE					= 0		# ���·��������һҳ��ͨ״̬�µ�����
QB_IDX_PAGE2						= 1		# ���·�������ڶ�ҳ������
QB_IDX_PAGE3						= 2		# ���·����������ҳ������
QB_IDX_HIDE_BAR						= 3		# �ұߵ����ؿ����������
QB_IDX_POSTURE_DEFENCE				= 5		# ������̬��Ӧ�Ŀ��������				����������������������������������������
QB_IDX_POSTURE_VIOLENT				= 7		# ����̬��Ӧ�Ŀ��������				���������Ϊ2�ǽ�һ�п�������ӵ����� ��
QB_IDX_POSTURE_DEVIL_SWORD			= 9		# ħ����̬��Ӧ�Ŀ��������				����չ��20����������10�����������Ժ�  ��
QB_IDX_POSTURE_SAGEL_SWORD			= 11	# ʥ����̬��Ӧ�Ŀ��������				��Ҫ����ʱ�Ͳ���Ҫ��̫��Ķ�          ��
QB_IDX_POSTURE_SHOT					= 13	# ������̬��Ӧ�Ŀ��������				����������������������������������������
QB_IDX_POSTURE_PALADIN				= 15	# ������̬��Ӧ�Ŀ��������
QB_IDX_POSTURE_MAGIC				= 17	# ������̬��Ӧ�Ŀ��������
QB_IDX_POSTURE_CURE					= 19	# ҽ����̬��Ӧ�Ŀ��������
QB_AUTO_SPELL_INDEX					= 267	# �Զ��������ܿ�������������������������Զ�ս���������


# --------------------------------------------------------------------
# about quest( from common/QuestDefine.py��designed by penghuawei/kebiao )
# --------------------------------------------------------------------
# quest type
QUEST_TYPE_NONE						= 0		# δ����
QUEST_TYPE_TREASURE					= 1		# ��������
QUEST_TYPE_POTENTIAL				= 2		# Ǳ������
QUEST_TYPE_PLACARD					= 3		# ����ͨ������
QUEST_TYPE_CTG						= 4		# ���������
QUEST_TYPE_DART						= 5		# ��������
QUEST_TYPE_ROB						= 6		# ��������
QUEST_TYPE_MEMBER_DART				= 7 	# ��Ա��������
QUEST_TYPE_IMPERIAL_EXAMINATION 	= 8		# �ƾٿ���
QUEST_TYPE_MERCHANT					= 9		# �̻�����
QUEST_TYPE_RUN_MERCHANT				= 10	# ��������
QUEST_TYPE_TONG_FETE				= 11	# ������
QUEST_TYPE_TONG_BUILD				= 12	# ��Ὠ��
QUEST_TYPE_TONG_NORMAL				= 13	# ����ճ�
QUEST_TYPE_CAMP_ACTIVITY			= 14	# ��Ӫ�����
QUEST_TYPE_CAMP_DAILY				= 15	# ��Ӫ�ճ�����

#reward quest bigType
REWARD_QUEST_TYPE_NONE				= 0		#δ��������
REWARD_QUEST_TYPE_TONG				= 1		#�������
REWARD_QUEST_TYPE_CAMP				= 2		#��Ӫ����
REWARD_QUEST_TYPE_DAILY				= 3		#ÿ������

#reward quest smallType
REWARD_QUEST_TYPE_NONE						= 0		# δ����
REWARD_QUEST_TYPE_TREASURE					= 1		# ��������
REWARD_QUEST_TYPE_POTENTIAL					= 2		# Ǳ������
REWARD_QUEST_TYPE_PLACARD					= 3		# ����ͨ������
REWARD_QUEST_TYPE_CTG						= 4		# ���������
REWARD_QUEST_TYPE_DART						= 5		# ��������
REWARD_QUEST_TYPE_ROB						= 6		# ��������
REWARD_QUEST_TYPE_MEMBER_DART				= 7 	# ��Ա��������
REWARD_QUEST_TYPE_IMPERIAL_EXAMINATION 		= 8		# �ƾٿ���
REWARD_QUEST_TYPE_MERCHANT					= 9		# �̻�����
REWARD_QUEST_TYPE_RUN_MERCHANT				= 10	# ��������
REWARD_QUEST_TYPE_TONG_FETE					= 11	# ������
REWARD_QUEST_TYPE_TONG_BUILD				= 12	# ��Ὠ��
REWARD_QUEST_TYPE_TONG_NORMAL				= 13	# ����ճ�
REWARD_QUEST_TYPE_CAMP_ACTIVITY				= 14	# ��Ӫ�����
REWARD_QUEST_TYPE_CAMP_DAILY				= 15	# ��Ӫ�ճ�����
REWARD_QUEST_TYPE_CRUSADE					= 16	# ÿ���ַ�����
REWARD_QUEST_TYPE_MATERIAL					= 17	# ÿ�ղ�������
REWARD_QUEST_TYPE_SPACE_COPY				= 18	# ÿ�ո�������


# task objective
QUEST_OBJECTIVE_NONE				= 0		# �����ڵ�Ҫ��( ԭ����TASK_OBJECTIVE_NONE )
QUEST_OBJECTIVE_KILL				= 1		# ɱ��( ԭ����TASK_OBJECTIVE_KILL )
QUEST_OBJECTIVE_DELIVER				= 2		# ������Ʒ( ԭ����TASK_OBJECTIVE_DELIVER )
QUEST_OBJECTIVE_TIME				= 3		# ʱ������(���ܳ�����ʱ��)( ԭ����TASK_OBJECTIVE_TIME )
QUEST_OBJECTIVE_EVENT_USE_ITEM		= 4		# ʹ����Ʒ( ԭ����TASK_OBJECTIVE_ACTIVE_ITEM )
QUEST_OBJECTIVE_OWN_PET				= 5		# ����ӵ������
QUEST_OBJECTIVE_SUBMIT				= 6		# �ύ��Ʒ
QUEST_OBJECTIVE_EVENT_TRIGGER		= 7		# �¼�����
QUEST_OBJECTIVE_TEAM				= 8		# �������Ŀ��
QUEST_OBJECTIVE_LEVEL				= 9		# �ȼ�����Ŀ��
QUEST_OBJECTIVE_QUEST				= 10	# ���һ��������������Ŀ��(ר����Ի�����)
QUEST_OBJECTIVE_SUBMIT_PICTURE		= 11 	# �ύ����
QUEST_OBJECTIVE_DELIVER_PET			= 12	# �ռ�����
QUEST_OBJECTIVE_SUBMIT_QUALITY		= 13	# �ύ��Ʒ�����ԣ�Ʒ�ʣ�
QUEST_OBJECTIVE_SUBMIT_SLOT			= 14	# �ύ��Ʒ�����ԣ�������
QUEST_OBJECTIVE_SUBMIT_EFFECT		= 15	# �ύ��Ʒ�����ԣ���Ƕ��
QUEST_OBJECTIVE_SUBMIT_LEVEL		= 16	# �ύ��Ʒ�����ԣ�ǿ����
QUEST_OBJECTIVE_SUBMIT_BINDED		= 17	# �ύ��Ʒ�����ԣ��󶨣�
QUEST_OBJECTIVE_PET_EVENT			= 18 	# ����ָ�����񴥷�����
QUEST_OBJECTIVE_DART_KILL			= 19	# ��������֮ɱ�ڳ�
QUEST_OBJECTIVE_EVOLUTION			= 20	# �������
QUEST_OBJECTIVE_SUBMIT_YINPIAO		= 21	# �ύ��Ʒ (��Ʊ)
QUEST_OBJECTIVE_IMPERIAL_EXAMINATION= 22	# �ƾٿ���
QUEST_OBJECTIVE_KILL_WITH_PET		= 23	# �ͳ���һ��ս��
QUEST_OBJECTIVE_KILL_ROLE_TYPE_MONSTER= 24	# ɱ���ͽ�ɫͬ��ְҵ�Ĺ���
QUEST_OBJECTIVE_SHOW_KAOGUAN		= 25	# ��ʾ�ƾٿ��Եĵ�ǰ����
QUEST_OBJECTIVE_QUEST_NORMAL		= 26	# ���һ��������������Ŀ��(ר�������ͨ����)
QUEST_OBJECTIVE_QUESTION			= 27	# �ʴ���ʽ������
QUEST_OBJECTIVE_SKILL_LEARNED		= 28	# ѧ����һ�����ܵ�����
QUEST_OBJECTIVE_PET_ACT				= 29	# ��ս��һ������
QUEST_OBJECTIVE_TALK				= 30	# ��������Ŀ��
QUEST_OBJECTIVE_HASBUFF				= 31	# ӵ��buffĿ��
QUEST_OBJECTIVE_DELIVER_QUALITY		= 32	# ������Ʒ����ɫ��
QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY 	= 33	# �ύ����
QUEST_OBJECTIVE_SUBMIT_DANCE	 	= 34	# �ύ����
QUEST_OBJECTIVE_POTENTIAL_FINISH	= 35 	# ���һ��Ǳ������
QUEST_OBJECTIVE_SUBMIT_LQEQUIP		= 36	# �ύһ��Ʒ�ʵȼ���װ��
QUEST_OBJECTIVE_EVENT_USE_SKILL		= 37	# ʹ�ü���
QUEST_OBJECTIVE_EVENT_REVIVE_POS	= 38	# ���ð󶨵�
QUEST_OBJECTIVE_KILLS = 39	# ɱ���ֹ�
QUEST_OBJECTIVE_ENTER_SPCACE 		= 40	# ����ĳһ���ռ�
QUEST_OBJECTIVE_LIVING_SKILL_LEARNED= 41	# ѧϰ����ܵ�Ŀ��
QUEST_OBJECTIVE_POTENTIAL			= 42    # Ǳ������ר��
QUEST_OBJECTIVE_SUBMIT_EMPTY		= 43	# �ύ��Ʒ�����ԣ���λ��
QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY	= 44    # ӵ����Ʒ�������ύ�����ԣ���λ��
QUEST_OBJECTIVE_ADD_CAMP_MORALE		= 45	# �����Ӫ����
QUEST_OBJECTIVE_CAMP_KILL			= 46	# ��Ӫ���ɱ��������
QUEST_OBJECTIVE_VEHICLE_ACTIVED			= 47	# ����һ�����
QUEST_OBJECTIVE_CAMPACT_DELIVER		= 48	# ��Ӫ�������Ʒ����Ŀ��
QUEST_OBJECTIVE_CAMPACT_TALK		= 49	# ��Ӫ��Ի�����
QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM	= 50	# ��Ӫ�ʹ����Ʒ����




# quest dialog object for the start or the end.
QUEST_DIALOG_ITEM					= 0		# ��Ʒ
QUEST_DIALOG_GAMEOBJECT				= 1		# ��Ϸ�����NPC

# quest reward type
QUEST_REWARD_NONE					= 0		# ����ʹ����
QUEST_REWARD_EXP					= 1		# ��������
QUEST_REWARD_ITEMS					= 2		# ��������Ʒ
QUEST_REWARD_CHOOSE_ITEMS			= 3		# ������ѡһ��Ʒ
QUEST_REWARD_RANDOM_ITEMS			= 4		# ���������Ʒ
QUEST_REWARD_MONEY					= 5		# ������Ǯ
QUEST_REWARD_TITLE					= 6		# �����ƺ�
QUEST_REWARD_SKILL					= 7		# ��������
QUEST_REWARD_POTENTIAL				= 8		# ����Ǳ�ܵ�
QUEST_REWARD_FIXED_RANDOM_ITEMS		= 9		# �̶������������Ȼ�������Ʒ�е�һ����û�У�
QUEST_REWARD_RELATION_MONEY			= 10	# ������Ǯ����
QUEST_REWARD_RELATION_EXP			= 11	# �������齱��
QUEST_REWARD_PRESTIGE				= 12	# ��������
QUEST_REWARD_MERCHANT_MONEY			= 13	# ���̽���
QUEST_REWARD_TONG_CONTRIBUTE		= 14	# �ﹱ����
QUEST_REWARD_TONG_BUILDVAL			= 15	# ��Ὠ���
QUEST_REWARD_TONG_MONEY				= 16	# ����ʽ�
QUEST_REWARD_EXP_FROM_ROLE_LEVEL	= 17	# ������ҵȼ������ľ���ֵ
QUEST_REWARD_TITLE					= 18	# �ƺŽ���
QUEST_REWARD_EXP_SECOND_PERCENT		= 19	# �����뾭��ӳ�
QUEST_REWARD_TONG_CONTRIBUTE_NORMAL = 20	# �����ﹱ��Ĭ�Ϸ�ʽ��
QUEST_REWARD_ROLE_LEVEL_MONEY		= 21	# ������ҵȼ������Ľ�Ǯ
QUEST_REWARD_PET_EXP				= 22    # ���ﾭ�齱��
QUEST_REWARD_IE_TITLE				= 23	# �ƾٳƺŽ���
QUEST_REWARD_RANDOM_ITEM_FROM_TABLE	= 24	# ��ȡ���ñ����Ʒ����
QUEST_REWARD_RELATION_PET_EXP		= 25    # ���ﻷ�����齱��
QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL= 26	# ������ҵȼ�����������ľ���ֵ
QUEST_REWARD_PET_EXP_SECOND_PERCENT	= 27	# �����뾭��ӳɣ����
QUEST_REWARD_DEPOSIT				= 28	# ����Ѻ��
QUEST_REWARD_MULTI_EXP				= 29	# �౶���ﾭ�齱�������� 8000 x 3
QUEST_REWARD_MULTI_PET_EXP			= 30	# �౶���ﾭ�齱�������� 3000 x 2
QUEST_REWARD_MULTI_MONEY			= 31	# �౶��Ǯ���������� 5��10�� x 2
QUEST_REWARD_ITEMS_QUALITY			= 32	# ��������Ʒ��Ʒ��
QUEST_REWARD_SPECIAL_TONG_BUILDVAL	= 33	# ����ر���Ƚ���
QUEST_REWARD_FUBI_ITEMS				= 34	# ���ҽ���
QUEST_REWARD_CHOOSE_ITEMS_AND_BIND	= 35	# ��ѡһ��������Ʒ��
QUEST_REWARD_TONG_FETE				= 36	# ������װ���һ�����
QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL	= 37	# ��Ʒ������������Ʒ�ȼ��ͽ�����ʱ��ҵȼ�һ����
QUEST_REWARD_MONEY_TONG_DART		= 38	# ����������ý�Ǯ
QUEST_REWARD_EXP_TONG_DART 			= 39	# ���ھ��齱��
QUEST_REWARD_TONG_ACTIONVAL			= 40	# ����ж���
QUEST_REWARD_CAMP_MORALE			= 41 	# ��Ӫʿ��
QUEST_REWARD_CAMP_HONOUR			= 42	# ��Ӫ����
QUEST_REWARD_DAOHENG				= 43	# ���н���
QUEST_REWARD_RATE_MONEY_FROM_ROLE_LEVEL	= 44	# ������ҵȼ���һ�����ʻ�Ľ�Ǯ����
QUEST_REWARD_RATE_EXP_FROM_ROLE_LEVEL	= 45	# ������ҵȼ���һ�����ʻ�ľ��齱��
QUEST_REWARD_RATE_QUEST_PART_COMPLETED	= 46	# ���һ��������Ŀ��Ҫ���Ľ���
QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY = 47	# ������������Ʒ�ʻ�ò�ͬ�Ľ�Ǯ����
QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY = 48	# ������������Ʒ�ʻ�ò�ͬ�ľ��齱��
QUEST_REWARD_TONG_NOMAL_MONEY		= 49	# ����Ǯ����
QUEST_REWARD_TONG_EXP				= 50	# ��ᾭ�齱��
QUEST_REWARD_ITEMS_FROM_CLASS		= 51	# �������ְҵ���費ͬ����Ʒ����
QUEST_REWARD_SKILL_FROM_CLASS		= 52	# �������ְҵ��������ͬ�ļ���
QUEST_REWARD_SOLTS_MONEY			= 53	# �����ϻ�����������������Ǯ
QUEST_REWARD_SOLTS_EXP				= 54	# �����ϻ�������������������
QUEST_REWARD_SOLTS_POTENTIAL		= 55	# �����ϻ���������������Ǳ��ֵ
QUEST_REWARD_SOLTS_DAOHENG			= 56	# �����ϻ�������������������ֵ


QUEST_STATE_NOT_ALLOW				= 0		# ��������������
QUEST_STATE_NOT_HAVE				= 1		# ��û�нӸ�����(�Ѿ����Խ�)(���ۼ���������)
QUEST_STATE_NOT_FINISH				= 2		# ��û�����Ŀ��
QUEST_STATE_FINISH					= 3		# �����Ŀ��(���Խ�����)
QUEST_STATE_COMPLETE				= 4		# �������Ѿ�������
QUEST_STATE_DIRECT_FINISH			= 5		# ���������ֱ��ȥ���
QUEST_STATE_NOT_HAVE_LEVEL_SUIT		= 6		# ��û�нӸ�����(�Ѿ����Խ�)(�������)��NPC��������״̬��λ��ǣ�������Ϊ����������жϡ�

QUEST_COMPLETE_RULE_DEFAULT			= 0		# ȫ��Ŀ����ɲ������
QUEST_COMPLETE_RULE_PART_TASK_COM	= 1		# ֻҪһ��Ŀ����ɾ����������
#####################################################################################
# ���������������Ŀǰû�����ڱ���������ͣ����������������ͼ��!!!   			#
# ���GossipType���и���λ�øĶ���Ҳ��Ҫ�Դ������Ķ�								#
#####################################################################################
QUEST_STATE_NOT_HAVE_BLUE			= 25	# ��ɫ̾�š�����û�нӸ�����(�Ѿ����Խ�)����ӦGossipType����24


QUEST_STYLE_NORMAL					= 0		# ��ͨ��������
QUEST_STYLE_RANDOM_GROUP			= 1		# ���ѭ������������
QUEST_STYLE_RANDOM					= 2		# ���ѭ������������
QUEST_STYLE_DIRECT_FINISH			= 3		# ֱ���ύ��������
QUEST_STYLE_FIXED_LOOP				= 4		# �̶���������
QUEST_STYLE_LOOP_GROUP				= 5		# ����������
QUEST_STYLE_POTENTIAL				= 6		# Ǳ��������ʽ
QUEST_STYLE_108_STAR				= 7		# 108��������ʽ
QUEST_STYLE_TONG_SPACE_COPY			= 8		# ��ḱ��������
QUEST_STYLE_TONG_FUBEN				= 9     # ��ḱ��������
QUEST_STYLE_NORMAL1					= 10	# ��ͨ��������1������ͨ����������Ҫ���𣺵ȼ����10������Ȼ����ʾ��ɫ��̾�ŵĽ�ȡ������ʾ����
QUEST_STYLE_ABANDOND_ATNPC			= 11	# ֻ��ͨ��NPC��������������
QUEST_STYLE_AUTO					= 12	#�Զ���������

QUEST_REMOVE_FLAG_PLAYER_CHOOSE     = 1		# ���������������
QUEST_REMOVE_FLAG_NPC_CHOOSE		= 2		# ��ָ��NPC������

GOSSIP_TYPE_QUEST_STATE_NOT_ALLOW				= 0		# ��������������Ի�����
GOSSIP_TYPE_QUEST_STATE_NOT_HAVE				= 1		# ��û�нӸ�����(�Ѿ����Խ�)�Ի�����
GOSSIP_TYPE_QUEST_STATE_NOT_FINISH				= 2		# ��û�����Ŀ��Ի�����
GOSSIP_TYPE_QUEST_STATE_FINISH					= 3		# �����Ŀ��(���Խ�����)�Ի�����
GOSSIP_TYPE_QUEST_STATE_COMPLETE				= 4		# �������Ѿ������˶Ի�����
GOSSIP_TYPE_QUEST_STATE_DIRECT_FINISH			= 5		# ���������ֱ��ȥ��ɶԻ�����
GOSSIP_TYPE_TRADE								= 6		# ���׶Ի�����
GOSSIP_TYPE_NORMAL_TALKING						= 7		# ��ͨ�Ի�����
GOSSIP_TYPE_SKILL_LEARN							= 8		# ����ѧϰ�Ի�����


# --------------------------------------------------------------------
# about chat
# all are modified :
#	�� reclassfied all channels
#	�� one channel for one thing
#	by hyw--2009.08.13
# --------------------------------------------------------------------
# ��ɫ����Ƶ����ע�⣺Ƶ��ǰ׺һ���ǡ�CHAT_CHANNEL_����
CHAT_CHANNEL_NEAR					= 1				# ����Ƶ��
CHAT_CHANNEL_LOCAL					= 2				# ����Ƶ��
CHAT_CHANNEL_TEAM					= 3				# ����Ƶ��
CHAT_CHANNEL_FAMILY					= 4				# ����Ƶ��
CHAT_CHANNEL_TONG					= 5				# ���Ƶ��
CHAT_CHANNEL_WHISPER				= 6				# ˽��Ƶ��
CHAT_CHANNEL_WORLD					= 7				# ����Ƶ��(��Ҫ��Ϸ��)
CHAT_CHANNEL_RUMOR					= 8				# ҥ��Ƶ��
CHAT_CHANNEL_WELKIN_YELL			= 9				# ��������ͨ���ֹ㲥����Ҫ��ң�
CHAT_CHANNEL_TUNNEL_YELL			= 10			# �������ɴ�����㲥����Ҫ��Ԫ��
CHAT_CHANNEL_TONG_CITY_WAR			= 22			# ���ս��Ƶ��

# GM/����Ƶ��
CHAT_CHANNEL_SYSBROADCAST			= 11			# �㲥(������ҷ���)

# NPC ����Ƶ��
CHAT_CHANNEL_NPC_SPEAK				= 12			# NPC��������NPC ����������ǰ׺Ϊ��N������NPC �������ǰ׺Ϊ��M������NPC ���磨����ǰ׺Ϊ��W������
CHAT_CHANNEL_NPC_TALK				= 13			# NPC �Ի�Ƶ��

# ϵͳ��ʾƵ��
CHAT_CHANNEL_SYSTEM					= 14			# ϵͳƵ������ʾ�ɷ����������ĸ��ֻ�������Ʒ/ǿ��/��Ƕ�Ȳ�����
CHAT_CHANNEL_COMBAT					= 15			# ս��Ƶ������ʾս����Ϣ��
CHAT_CHANNEL_PERSONAL				= 16			# ����Ƶ��������Ƶ����ʾ����ڻ�þ��顢Ǳ�ܡ���Ǯ����Ʒ��Ԫ������Ϣ��
CHAT_CHANNEL_MESSAGE				= 17			# ��ϢƵ������ʾ��ɫ�Ĳ��������Ĵ�����Ϣ����ʾ��Ϣ��
CHAT_CHANNEL_SC_HINT				= 18			# ����Ļ�м���ʾ��Ƶ��
CHAT_CHANNEL_MSGBOX					= 19			# �� MessageBox ��ʾ��Ƶ��

# ������������
CHAT_CHANNEL_PLAYMATE				= 20			# �������

# ������������
CHAT_CHANNEL_CAMP					= 21			# ��ӪƵ��

# -------------------------------------------
# ����ԭ��
CHAT_FORBID_BY_GM					= 1		# �� GM ����
CHAT_FORBID_REPEAT					= 2		# ���ظ����Ե�һ��������������
CHAT_FORBID_JAIL					= 3		# ��������������
CHAT_FORBID_GUANZHAN				= 4		# �����й�սBUFF

# --------------------------------------------------------------------
# about friend( from common/FriendType.py��designed by panguankong )
# --------------------------------------------------------------------
FRIEND_KINDLY_GROUPID				= 1		# ������(ԭ����FRIEND_GROUPID )
FRIEND_BLACKLIST_GROUPID			= 0		# ��������( ԭ����BLACKLIST_GROUPID )


# --------------------------------------------------------------------
# about relation( from L3Define.py )
# --------------------------------------------------------------------
RELATION_NONE						= 0 	# ���κι�ϵ��һ������Ĭ��ֵ
RELATION_FRIEND						= 1 	# ���ѹ�ϵ( ԭ����C_RELATION_FRIEND )
RELATION_NEUTRALLY					= 2 	# ������ϵ( ԭ����C_RELATION_NEUTRALLY )
RELATION_ANTAGONIZE 				= 3 	# �жԹ�ϵ( ԭ����C_RELATION_ANTAGONIZE )
RELATION_NOFIGHT					= 4		# ��ս��ϵ

# --------------------------------------------------------------------
# about trade( from L3Define.py )
# --------------------------------------------------------------------
# ����״̬, ��ʶ��ǰ�������ֽ���״̬
TRADE_NONE							= 0		# �޽���
TRADE_CHAPMAN						= 1		# ������NPC����(����/����)
TRADE_SWAP							= 2		# ���֮���Ǯ/��Ʒ����
TRADE_INVENTORY						= 4		# �ֿ����
TRADE_CASKET						= 8		# ���ϻ����
TRADE_PRODUCE						= 16	# װ������
TRADE_TISHOU						= 32	# ������Ʒ
TRADE_MAX							= 3		# ����Щ���ײ����������ǳ��� TRADE_NONE ��TRADE_*������

# ����ҽ�����״̬
TRADE_SWAP_DEFAULT					= 0		# ����Ĭ��״̬
TRADE_SWAP_INVITE					= 1		# ��������״̬
TRADE_SWAP_WAITING					= 2		# ���׵ȴ�״̬(״̬����15������û��Ӧ����ȡ��)
TRADE_SWAP_BEING					= 3		# ��Ʒ���׿�ʼ״̬
TRADE_SWAP_LOCK						= 4		# ��Ʒ����״̬
TRADE_SWAP_PET_INVITE				= 5		# ���ｻ������״̬
TRADE_SWAP_PET_WAITING				= 6		# ���ｻ�׵ȴ�״̬
TRADE_SWAP_PET_BEING				= 7		# ���ｻ�׿�ʼ״̬
TRADE_SWAP_PET_LOCK					= 8		# ���ｻ������״̬
TRADE_SWAP_SURE						= 9		# ����ȷ��״̬
TRADE_SWAP_LOCKAGAIN				= 10	# ˫���ٴ�����״̬

TRADE_MAX_GOODS_NUM					= 100	# ��������˽��������������Ʒ��������

TRADE_REQUIRE_AMOUNT_TIME			= 30	# ������Ʒ�������ʱ��

# --------------------------------------------------------------------
# about pk
# --------------------------------------------------------------------
PK_STATE_PROTECT					= 0x01	# ����״̬
PK_STATE_PEACE						= 0x02	# ����״̬
PK_STATE_ATTACK						= 0x04	# ����(����)״̬(120����û���ٴδ�����Ϊ�ǹ���״̬)
PK_STATE_REDNAME					= 0x08	# ����״̬
PK_STATE_BLUENAME					= 0x10	# ����״̬
PK_STATE_ORANGENAME					= 0x20	# ����״̬��Ҳ����С����״̬��


#pk����͵ȼ�
PK_ALLOW_LEVEL_MIN					= 31	# 31���ſ���pk

#pkģʽ
PK_CONTROL_PROTECT_PEACE				= 1		# ��ƽģʽ
PK_CONTROL_PROTECT_TEAMMATE				= 2		# ���ģʽ
PK_CONTROL_PROTECT_KIN					= 3		# ����ģʽ
PK_CONTROL_PROTECT_TONG					= 4		# ���ģʽ
PK_CONTROL_PROTECT_RIGHTFUL				= 5		# ����ģʽ
PK_CONTROL_PROTECT_JUSTICE				= 6		# ����ģʽ
PK_CONTROL_PROTECT_NONE					= 7		# ȫ��ģʽ
PK_CONTROL_PROTECT_TEMPORARY_FACTION	= 8		# ��ʱ��Ӫģʽ ( Ŀǰֻ�����ս���д��ڣ�����ͬһ��ʱ��Ӫ����Ҳ����໥���� )
PK_CONTROL_PROTECT_LEAGUE				= 9		# ����ģʽ�������ս������������Ϊ��λ��
PK_CONTROL_PROTECT_CAMP					= 10	# ��Ӫģʽ

PK_CONTROL_PROTECT_ACT_1				= 20	#�ģʽ1
PK_CONTROL_PROTECT_ACT_2				= 21	#�ģʽ2
PK_CONTROL_PROTECT_ACT_3				= 22	#�ģʽ2

#���ڻ�жϵ�PKģʽ
SYS_PK_CONTOL_ACT = [
	PK_CONTROL_PROTECT_ACT_1,
	PK_CONTROL_PROTECT_ACT_2,
	PK_CONTROL_PROTECT_ACT_3,
]

#pk����͵ȼ�
PK_CATCH_VALUE						= 60	# pkֵ���������������ץ������

# --------------------------------------------------------------------
# about equip
# --------------------------------------------------------------------
EQUIP_ABRASION_NORMALATTACK			= 1		# ���������ͨ��������
EQUIP_ABRASION_SPELLATTACK			= 2		# ������ļ��ܹ�������


EQUIP_REPAIR_NORMAL					= 1		# ��ͨ����
EQUIP_REPAIR_SPECIAL				= 2		# ��������
EQUIP_REPAIR_ITEM				= 3		# ͨ����Ʒ����


#��Ʒ���뱳������״̬
KITBAG_CAN_HOLD						= 0		# �����������ɽ�������Ʒ
KITBAG_NO_MORE_SPACE				= 1		# �����ռ䲻��
KITBAG_ITEM_COUNT_LIMIT				= 2		# ���ӵ��������Ʒ����ӵ������
KITBAG_ADD_ITEM_BY_STACK_SUCCESS	= 3		# ͨ��������Ʒ�������Ʒ
KITBAG_ADD_ITEM_SUCCESS				= 4		# �����Ʒ�ɹ�
KITBAG_ADD_ITEM_FAILURE				= 5		# �����Ʒʧ��
KITBAG_STACK_ITEM_SUCCESS			= 6		# ���ӳɹ�
KITBAG_STACK_ITEM_NO_SAME_ITEM		= 7		# ������Ʒʱû����ͬ����Ʒ
KITBAG_STACK_ITEM_NO_MORE			= 8		# ������Ʒ˿ʱ������Ʒ�����Ե���
KITBAG_STACK_DSTITEM_NO_MORE		= 9		# ������Ʒ����ʱĿ����Ʒ�����Ե���
KITBAG_STACK_ITEM_ID_DIFF			= 10	# ������Ʒ����ʱ����Ʒͬ��
KITBAG_STACK_ITEM_SUCC_1			= 11	# ������Ʒ���ӳɹ���Դ��Ʒ��ʣ��
KITBAG_STACK_ITEM_SUCC_2			= 12	# ������Ʒ���ӳɹ���û��ʣ��


# ---------------------------------------------------------------------
# Ĭ�Ͻ�Ǯ��������Ŷ���
# --------------------------------------------------------------------
ITEMID_MONEY			= 60101001	# ��Ǯ		money
ITEMID_KITBAG_EQUIP		= 70101006	# װ����    kitbag_equip
ITEMID_KITBAG_NORMAL	= 70101007	# Ĭ�ϱ���  kitbag_normal
ITEMID_KITBAG_CASKET	= 70101008	# ���ϻ    kitbag_casket


# ---------------------------------------------------------------------
# �����̳ǣ���Ʒ���ͱ�־λ����( wsf )
# ---------------------------------------------------------------------
SPECIALSHOP_OTHER_GOODS				= 0x000		# ������Ʒ
SPECIALSHOP_HOT_GOODS				= 0x001		# ��������Ʒ���
SPECIALSHOP_RECOMMEND_GOODS		= 0x002		# �Ƽ���Ʒ���(���ڵ�������Ʒ)
SPECIALSHOP_ESPECIAL_GOODS			= 0x004		# ��ĵر�����Ʒ���
SPECIALSHOP_CURE_GOODS				= 0x008		# �ָ�����Ʒ���
SPECIALSHOP_REBUILD_GOODS			= 0x010		# ��������Ʒ���
SPECIALSHOP_VEHICLE_GOODS			= 0x020		# ��������Ʒ���
SPECIALSHOP_PET_GOODS				= 0x040		# ��������Ʒ���
SPECIALSHOP_FASHION_GOODS			= 0x080		# ʱװ����Ʒ���
SPECIALSHOP_ENHANCE_GOODS			= 0x100		# ǿ����������Ʒ���
SPECIALSHOP_CRYSTAL_GOODS			= 0x200		# ˮ������Ʒ���
SPECIALSHOP_TALISMAN_GOODS			= 0x400		# ��������Ʒ���

SPECIALSHOP_SUBTYPE_MOS_CRYSTAL	= 0			# ��Ƕˮ������
SPECIALSHOP_SUBTYPE_VAL_GOODS		= 1			# �����챦����
SPECIALSHOP_SUBTYPE_EXP_GOODS		= 2			# �����鵤����
SPECIALSHOP_SUBTYPE_REST_GOODS	= 3			# �ָ�ҩƷ����
SPECIALSHOP_SUBTYPE_LAND_VEHICLE	= 4			# ½����������
SPECIALSHOP_SUBTYPE_SKY_VEHICLE		= 5			# ������������
SPECIALSHOP_SUBTYPE_PET_BOOK		= 6			# �����鼮����
SPECIALSHOP_SUBTYPE_PET_PROPS		= 7			# �����������
SPECIALSHOP_SUBTYPE_PET_EGG			= 8			# ���ﵰ����
SPECIALSHOP_SUBTYPE_MALE_FASHION	= 9			# ����ʱװ����
SPECIALSHOP_SUBTYPE_FEMALE_FASHION = 10			# Ů��ʱװ����
SPECIALSHOP_SUBTYPE_VEHICLE_PROPS	= 11		# �����������

SPECIALSHOP_GOODS_TYPES = SPECIALSHOP_HOT_GOODS | SPECIALSHOP_RECOMMEND_GOODS | SPECIALSHOP_ESPECIAL_GOODS | SPECIALSHOP_CURE_GOODS | SPECIALSHOP_VEHICLE_GOODS | SPECIALSHOP_PET_GOODS | SPECIALSHOP_FASHION_GOODS


SPECIALSHOP_MONEY_TYPE_GOLD			= 0			# �����̳ǵ��ߵĻ������ͣ���Ԫ��
SPECIALSHOP_MONEY_TYPE_SILVER		= 1			# �����̳ǵ��ߵĻ������ͣ���Ԫ��

# ������Ʒʱ���̳�״̬��hyw--2009.03.27��
SPECIALSHOP_REQ_SUCCESS				= 1			# ����ɹ�
SPECIALSHOP_REQ_FAIL_CLOSED			= 2			# �̳�û��
SPECIALSHOP_REQ_FAIL_NOT_EXIST		= 3			# ��Ʒ������
SPECIALSHOP_REQ_FAIL_LOCKED			= 4			# ��Ʒ���ɹ���

CURRENCY_TYPE_MONEY		= 1			# ��Ϸ�һ�������
CURRENCY_TYPE_SILVER		= 2			# ��Ԫ����������
CURRENCY_TYPE_GOLD		= 3			# ��Ԫ����������

# --------------------------------------------------------------------
# ���ϻ
# --------------------------------------------------------------------
# ���ϻ����
CASKET_FUC_STUFFCOMPOSE				= 1		# ���Ϻϳ�
CASKET_FUC_EQUIPSTILETTO			= 2		# װ�����
CASKET_FUC_EQUIPSPLIT				= 3		# װ�����
CASKET_FUC_EQUIPSTUDDED				= 4		# װ����Ƕ
CASKET_FUC_EQUIPINTENSIFY			= 5		# װ��ǿ��
CASKET_FUC_EQUIPREBUILD				= 6		# װ������
CASKET_FUC_EQUIPBIND				= 7		# װ����
CASKET_FUC_EQUIPPERSONALITY			= 8 	# װ�����Ի�
CASKET_FUC_EQUIPWASHATTR			= 9		# װ��ϴ����
CASKET_FUC_SPECIALCOMPOSE			= 10	# ����ϳ�
CASKET_FUC_TALISMANFIX				= 11	# �����޸�
CASKET_FUC_TALISMAN_SPLIT			= 12	# �����ֽ�
CASKET_FUC_TALISMAN_INS				= 13	# ����ǿ��
CASKET_FUC_REMOVECRYSTAL			= 14	# ˮ��ժ��
CASKET_FUC_CHANGEPROPERTY			= 15	# ϴǰ׺
CASKET_FUC_IMPROVEQUALITY			= 16	#��װ��Ʒ

# װ��ǿ�����
EQUIP_INTENSIFY_MAX_LEVEL			= 9		# ǿ������ߵȼ�

# --------------------------------------------------------------------
# ���ʽ
# --------------------------------------------------------------------
REVIVE_ON_CITY						= 1		# �سǸ���
REVIVE_ON_ORIGIN					= 2		# ԭ�ظ���
REVIVE_ON_TOMB						= 3		# Ĺ�ظ���
REVIVE_BY_ITEM						= 4		# ͨ��ĳ����Ʒ����
REVIVE_BY_BUFF						= 5		# ͨ��ĳ��BUFF����
REVIVE_ON_SPACECOPY					= 6		# �ڸ�����ڸ���
REVIVE_PRE_SPACE					= 7		# �����һ����ͼ
REVIVE_BY_REVIVEPOINT				= 8		# ͨ���������ԭ�ظ���

# --------------------------------------------------------------------
# about mail
# --------------------------------------------------------------------
# �ż�����������
MAIL_SENDER_TYPE_PLAYER				= 1		# ��Ҽ���
MAIL_SENDER_TYPE_NPC				= 2		# npc����
MAIL_SENDER_TYPE_GM					= 3		# GM����
MAIL_SENDER_TYPE_RETURN				= 4		# ����

# �ż�����
MAIL_TYPE_QUICK						= 1		# ���
MAIL_TYPE_NORMAL					= 2		# ��ͨ�ʼ�

# --------------------------------------------------------------------
# about team pickup state
# --------------------------------------------------------------------
TEAM_PICKUP_STATE_FREE				= 0		# ����ʰȡ
TEAM_PICKUP_STATE_ORDER				= 1		# ����ʰȡ
TEAM_PICKUP_STATE_SPECIFY			= 2		# �ӳ�ָ��


# --------------------------------------------------------------------
# about spaceType( kebiao )
# --------------------------------------------------------------------
SPACE_TYPE_NORMAL					= 0		# ��ͨ��ͼ
SPACE_TYPE_CITY_WAR					= 2		# ��������ս��
SPACE_TYPE_TONG_ABA					= 3		# �����̨��ս��
SPACE_TYPE_TONG_TERRITORY			= 4		# ������
SPACE_TYPE_SUN_BATHING				= 5		# �չ�ԡ��̲ -spf
SPACE_TYPE_TIAN_GUAN				= 6		# ��ظ���
SPACE_TYPE_RACE_HORSE				= 7		# ������
SPACE_TYPE_POTENTIAL				= 8		# Ǳ�ܸ���
SPACE_TYPE_WU_DAO					= 9     # ������
SPACE_TYPE_SHEN_GUI_MI_JING			= 10    # ����ؾ�
SPACE_TYPE_WU_YAO_QIAN_SHAO			= 11	# ����ǰ��
SPACE_TYPE_WU_YAO_WANG_BAO_ZANG		= 12	# ����������
SPACE_TYPE_SHUIJING					= 13	# ˮ������
SPACE_TYPE_HUNDUN					= 14	# ��������
SPACE_TYPE_TEAM_COMPETITION			= 15	# ��Ӿ���
SPACE_TYPE_DRAGON					= 16	# ��ͷ�����
SPACE_TYPE_PROTECT_TONG				= 17	# ��������
SPACE_TYPE_POTENTIAL_MELEE			= 18	# Ǳ���Ҷ�����
SPACE_TYPE_EXP_MELEE				= 19	# �����Ҷ�����
SPACE_TYPE_PIG						= 20	# ������
SPACE_TYPE_PRISON					= 21	# ����
SPACE_TYPE_YAYU						= 22	# ���Ȫm؅
SPACE_TYPE_XIE_LONG_DONG_XUE		= 23	# а����Ѩ
SPACE_TYPE_FJSG						= 24	# �⽣��
SPACE_TYPE_TONG_COMPETITION			= 25	# ��Ὰ��
SPACE_TYPE_ROLE_COMPETITION			= 26	# ���˾���
SPACE_TYPE_SHE_HUN_MI_ZHEN			= 27	# �������
SPACE_TYPE_TEACH_KILL_MONSTER		= 28	# ʦͽ����
SPACE_TYPE_KUAFU_REMAINS 			= 29	# �丸���
SPACE_TYPE_RABBIT_RUN				= 30	# С�ÿ���
SPACE_TYPE_BEFORE_NIRVANA			= 31	# 10������
SPACE_TYPE_CHALLENGE				= 32	# ��ս����
SPACE_TYPE_TEAM_CHALLENGE			= 33	# �����̨
SPACE_TYPE_PLOT_LV40				= 34	# 40�����鸱��
SPACE_TYPE_PLOT_LV60				= 35	# 60�����鸱��
SPACE_TYPE_TOWER_DEFENSE			= 36	# �������
SPACE_TYPE_YXLM						= 37	# Ӣ�����˸���
SPACE_TYPE_YE_ZHAN_FENG_QI			= 38 	# ҹս������
SPACE_TYPE_TONG_TURN_WAR			= 39	# ��ᳵ��ս
SPACE_TYPE_YXLM_PVP 				= 40	# Ӣ�����˸���PVP
SPACE_TYPE_FENG_HUO_LIAN_TIAN 		= 41	# �����ս������������죩
SPACE_TYPE_TIAO_WU					= 42	# �����ͼ
SPACE_TYPE_DESTINY_TRANS			= 43	# �����ֻظ���
SPACE_TYPE_MERCURY_CORE_MAP			= 44	# ˮ֮���ĸ���
SPACE_TYPE_YI_JIE_ZHAN_CHANG		= 45	# ���ս������
SPACE_TYPE_AO_ZHAN_QUN_XIONG		= 46	# ��սȺ��
SPACE_TYPE_DANCEHALL				= 47    # ����
SPACE_TYPE_DANCECOPY_CHALLENGE		= 48	# ������ս����
SPACE_TYPE_JUE_DI_FAN_JI			= 49	# ���ط��������
SPACE_TYPE_CAMP_TURN_WAR			= 50	# ��Ӫ����ս
SPACE_TYPE_DANCECOPY_PARCTICE		= 51	# ������ϰ����
SPACE_TYPE_CITY_WAR_FINAL			= 52	# �����ս����
SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN	= 53	# ��Ӫ�������
SPACE_TYPE_TEMPLATE					= 54	# ����ģ��
SPACE_TYPE_WM						= 55	# λ���ͼ
SPACE_TYPE_MELT_MONSTER_POT			= 56	# ����������
SPACE_TYPE_FANG_SHOU				= 57	# ���ظ���

# --------------------------------------------------------------------
# about family( kebiao )
# --------------------------------------------------------------------
FAMILY_AFFICHE_LENGTH_MAX			= 200	# ���幫���������
FAMILY_MEMBER_COUNT_MAX				= 15	# ������������
FAMILY_MEMBER_LEVEL_LOW				= 10	# �������ĳ�Ա��ͼ���
FAMILY_CREATE_MONEY					= 100000# ������������ķ���
FAMILY_CREATE_LEVEL					= 30	# ������������ȼ�

#����Ȩ��
FAMILY_GRADE_MEMBER					= 1		# �����Ա
FAMILY_GRADE_SHAIKH					= 101	# �����峤
FAMILY_GRADE_SHAIKH_SUBALTERN		= 100	# ���帱�峤



# --------------------------------------------------------------------
# about tong( kebiao )
# --------------------------------------------------------------------
TONG_AFFICHE_LENGTH_MAX				= 200	# ��ṫ���������
TONG_MEMBER_SCHOLIUM_LENGTH_MAX		= 7		# ����Ա��ע�������
TONG_CREATE_MONEY					= 300000# �����������ķ���
TONG_CREATE_LEVEL					= 30	# �����������ȼ�
TONG_LEAGUE_MAX_COUNT				= 2		# ���ͬ�˵�������
TONG_AMOUNT_MAX						= 1000	# �������ܴ����İ������
TONG_AD_LENGTH_MAX 					= 40    # ��������������

# ���ְλ
TONG_DUTY_MEMBER				= 1 # ����
TONG_DUTY_TONG					= 2 # ����
TONG_DUTY_DEPUTY_CHIEF			= 3 # ������
TONG_DUTY_CHIEF					= 4 # ����

TONG_DUTY_CHIEF_SUBALTERN_COUNT	= 2		# ��󸱰�������
TONG_DUTY_TONG_COUNT			= 4		# �����������

TONG_DUTYS =[ TONG_DUTY_MEMBER, TONG_DUTY_TONG, TONG_DUTY_DEPUTY_CHIEF, TONG_DUTY_CHIEF ]
TONG_CITY_WAR_SPEAK = [TONG_DUTY_TONG, TONG_DUTY_DEPUTY_CHIEF, TONG_DUTY_CHIEF]		#���ս������Ƶ������ְ��

# ���Ȩ��
TONG_RIGHT_MEMBER_MANAGE		= 1 # ��Ա����(���ա��������)
TONG_RIGHT_AFFICHE				= 2 # ��ṫ��
TONG_RIGHT_PET_SELECT			= 3 # ����ѡ��
TONG_RIGHT_CHANGE_DUTY			= 4 # ְλ���
TONG_RIGHT_STORAGE_MANAGE		= 5 # �ֿ�Ȩ������
TONG_RIGHT_LEAGUE_MAMAGE		= 6 # ͬ�˹���
TONG_RIGHT_ACTIVITY				= 7 # ���( ħ����Ϯ�������롢����Ӷ�ս )
TONG_RIGHT_SALARY_RATE			= 8 # ���ٺ»�һ���
TONG_RIGHT_DISMISS_TONG			= 9 # ��ɢ���
TONG_RIGHT_CALL_ALL_MEMBER		= 10 # ������
TONG_RIGHT_GRADE_CHAT			= 11 # ��ȡ�������
TONG_RIGHET_STORAGE_ITEM_ACCESS	= 12 # �����Ʒ��ȡ
TONG_RIGHT_MEMBER_SCHOLIUM		= 13 # ���ó�Ա��ע
TONG_RIGHT_ACTIVITY_ABA			= 14 # �����̨
TONG_RIGHT_ACTIVITY_COMPETITION	= 15 # ��Ὰ��
TONG_RIGHT_SET_AD				= 16 # �����
TONG_RIGHT_CHANGE_NAME			= 17 # ������
TONG_RIGHT_SIGN					= 18 # �����
TONG_RIGHT_ASSIGN_ITEM		= 19 #������Ʒ

# ְλ��Ӧ���ܱ�
TONG_DUTY_RIGHTS_MAPPING ={
	TONG_DUTY_MEMBER			:	[ TONG_RIGHET_STORAGE_ITEM_ACCESS],
	TONG_DUTY_TONG				:	[ TONG_RIGHT_MEMBER_MANAGE,TONG_RIGHET_STORAGE_ITEM_ACCESS ],
	TONG_DUTY_DEPUTY_CHIEF		:	[ TONG_RIGHT_MEMBER_MANAGE, TONG_RIGHT_AFFICHE, TONG_RIGHT_PET_SELECT,TONG_RIGHET_STORAGE_ITEM_ACCESS, \
										TONG_RIGHT_ACTIVITY_ABA,TONG_RIGHT_ACTIVITY_COMPETITION ],
	TONG_DUTY_CHIEF				:	[ TONG_RIGHT_MEMBER_MANAGE, TONG_RIGHT_AFFICHE, TONG_RIGHT_PET_SELECT, TONG_RIGHT_CHANGE_DUTY, \
										TONG_RIGHT_STORAGE_MANAGE,TONG_RIGHT_LEAGUE_MAMAGE, TONG_RIGHT_ACTIVITY, TONG_RIGHT_SALARY_RATE, \
										TONG_RIGHT_DISMISS_TONG, TONG_RIGHT_CALL_ALL_MEMBER, TONG_RIGHT_GRADE_CHAT,TONG_RIGHET_STORAGE_ITEM_ACCESS, \
										TONG_RIGHT_MEMBER_SCHOLIUM, TONG_RIGHT_ACTIVITY_ABA, TONG_RIGHT_ACTIVITY_COMPETITION, TONG_RIGHT_SET_AD, \
										TONG_RIGHT_CHANGE_NAME, TONG_RIGHT_SIGN, TONG_RIGHT_ASSIGN_ITEM ] ,
}

TONG_DUTY_CLIENT_RIGHTS_MAPPING = {
	TONG_DUTY_MEMBER			:	[ ],
	TONG_DUTY_TONG				:	[ TONG_RIGHT_MEMBER_MANAGE ],
	TONG_DUTY_DEPUTY_CHIEF		:	[ TONG_RIGHT_MEMBER_MANAGE, TONG_RIGHT_AFFICHE, TONG_RIGHT_PET_SELECT ],
	TONG_DUTY_CHIEF				:	[ TONG_RIGHT_MEMBER_MANAGE, TONG_RIGHT_AFFICHE, TONG_RIGHT_PET_SELECT, TONG_RIGHT_CHANGE_DUTY, TONG_RIGHT_STORAGE_MANAGE ],
}

# ��Ὠ�����
TONG_BUILDING_TYPE_YSDT	= 0x00000001	# ���´���
TONG_BUILDING_TYPE_JK	= 0x00000002	# ���
TONG_BUILDING_TYPE_SSD	= 0x00000004	# ���޵�
TONG_BUILDING_TYPE_CK	= 0x00000008	# �ֿ�
TONG_BUILDING_TYPE_TJP	= 0x00000010	# ������
TONG_BUILDING_TYPE_SD	= 0x00000020	# �̵�
TONG_BUILDING_TYPE_YJY	= 0x00000040	# �о�Ժ

# ����������
TONG_SHENSHOU_TYPE_1	= 1				# ��������
TONG_SHENSHOU_TYPE_2	= 2				# ��ë����
TONG_SHENSHOU_TYPE_3	= 3				# ����ʥ��
TONG_SHENSHOU_TYPE_4	= 4				# ������ȸ


# ���ֿ��������
TONG_STORAGE_OPERATION_ADD		= 1			# ������Ʒ
TONG_STORAGE_OPERATION_MINUS	= 0			# ȡ����Ʒ

# ������ս��
TONG_CW_FLAG_MONSTER			= 1			# ��ͨС��
TONG_CW_FLAG_LP					= 2			# ����
TONG_CW_FLAG_TOWER				= 3			# ��¥
TONG_CW_FLAG_XJ					= 4			# �ط�BOSS


TONG_SKILL_ALL			= 0			# ���а�Ἴ��
TONG_SKILL_ROLE		= 1			# ����ɫ��������
TONG_SKILL_PET			= 2			# �����＼������


# --------------------------------------------------------------------
# about prestige( wangshufeng )
# --------------------------------------------------------------------
PRESTIGE_ENEMY				=			1	# ���
PRESTIGE_STRANGE			=			2	# �䵭
PRESTIGE_NEUTRAL			=			3	# ����
PRESTIGE_FRIENDLY			=			4	# ����
PRESTIGE_RESPECT			=			5	# ����
PRESTIGE_ADMIRE				=			6	# �羴
PRESTIGE_ADORE				=			7	# ���


# --------------------------------------------------------------------
# about title( wangshufeng )
# --------------------------------------------------------------------
TITLE_CONFIRM_TYPE			= 1			# һ�����ͱ��
TITLE_COUPLE_TYPE			= 2			# �������ͱ��
TITLE_TONG_TYPE				= 3			# ������ͱ��
TITLE_MERCHANT_TYPE			= 4			# �������ͱ��
TITLE_IE_TYPE				= 5			# �ƾ����ͱ��
TITLE_TEACH_PRENTICE_TYPE	= 6			# ͽ�����ͱ��
TITLE_TEACH_MASTER_TYPE		= 7			# ʦ���ƺ����ͱ��

TITLE_COUPLE_MALE_ID		= 4			# �ƺš�%s���Ϲ�����id
TITLE_COUPLE_FEMALE_ID		= 5			# �ƺš�%s�����š���id
TITLE_TEACH_PRENTICE_ID		= 3			# �ƺš�%s��ͽ�ܡ���id
TITLE_ALLY_ID					= 91		# ��ݳƺ�id

TITLE_NONE						= 0			#�޳ƺ�
TITLE_NOVICIATE_LANLUHU_X		= 8		#��¡�ھ���·��
TITLE_NOVICIATE_CHANGZISHOU_X	= 9		#��¡�ھ�������
TITLE_NOVICIATE_NEW_DART_X		= 10	#��¡�ھ�������ʦ
TITLE_NOVICIATE_WUSHI_X			= 11	#��¡�ھ���ʦ
TITLE_NOVICIATE_DART_HEAD_X		= 12	#��¡�ھ���ͷ
TITLE_NOVICIATE_DART_FU_X		= 13	#��¡�ھָ�����ͷ
TITLE_NOVICIATE_DART_KING_X		= 14	#��¡�ھ�����
TITLE_NOVICIATE_CHANGZISHOU_C	= 15	#��ƽ�ھ�������
TITLE_NOVICIATE_NEW_DART_C		= 16	#��ƽ�ھ�������ʦ
TITLE_NOVICIATE_WUSHI_C			= 17	#��ƽ�ھ���ʦ
TITLE_NOVICIATE_DART_HEAD_C		= 18	#��ƽ�ھ���ͷ
TITLE_NOVICIATE_DART_FU_C		= 19	#��ƽ�ھָ�����ͷ
TITLE_NOVICIATE_DART_KING_C		= 20	#��ƽ�ھ�����
TITLE_NOVICIATE_LANLUHU_C		= 21	#��ƽ�ھ���·��

FACTION_XINGLONG				= 37	# ��¡�ھ�����id
FACTION_CHANGPING				= 38	# ��ƽ�ھ�����id

# --------------------------------------------------------------------
# about RoleGem( wangshufeng )
# --------------------------------------------------------------------
GEM_ROLE_ACTIVE_FLAG		= 0x01		# ��ɫ����ʯ�����־λ
GEM_PET_ACTIVE_FLAG			= 0x02		# ���ﾭ��ʯ�����־λ
GEM_ROLE_COMMON_INDEX		= 0			# ��Ҿ���ʯ�ĳ�ʼindex
GEM_PET_COMMON_INDEX		= 50		# ��ҳ��ﾭ��ʯ�ĳ�ʼindex
GEM_WORK_NORMAL				= 1			# ��ͨ��������
GEM_WORK_HARD				= 2			# �̿��������

# ---------------------------------------------------------------------
# �����̨����ض���
# ---------------------------------------------------------------------
ABATTOIR_GAME_NONE			= 0	# �ޱ���
ABATTOIR_EIGHTHFINAL		= 1	# �˷�֮һ����
ABATTOIR_QUARTERFINAL		= 2	# �ķ�֮һ����
ABATTOIR_SEMIFINAL			= 3	# �����
ABATTOIR_FINAL				= 4	# ����

# ---------------------------------------------------------------------
# �����ս�����壬���������ǵ�����ϵ�����ԱȽϴ�С
# ---------------------------------------------------------------------
CITY_WAR_LEVEL_NONE	= 0				# �ޱ���
CITY_WAR_LEVEL_QUARTERFINAL = 1		# 4��֮һ����
CITY_WAR_LEVEL_SEMIFINAL = 2		# �����
CITY_WAR_LEVEL_FINAL = 3			# ����

# ---------------------------------------------------------------------
# ���ֿ����λ����( wsf )
# ---------------------------------------------------------------------
TONG_STORAGE_ONE			= 0	# ����1
TONG_STORAGE_TWO			= 1	# ����2
TONG_STORAGE_THREE			= 2	# ����3
TONG_STORAGE_FOUR			= 3	# ����4
TONG_STORAGE_FIVE			= 4	# ����5
TONG_STORAGE_SIX			= 5	# ����6

TONG_STORAGE_COUNT			= 6	# �ֿ�����������


# ---------------------------------------------------------------------
# ����ֿ�ʱ��һЩ����
# ---------------------------------------------------------------------

ID_OF_ITEM_OPEN_BAG			= 110103020

# ---------------------------------------------------------------------
# �ı��Ǯ�ķ�ʽ( zds,15:19 2009-2-7 )
# ---------------------------------------------------------------------
CHANGE_MONEY_INITIAL				= 0			# �ͻ��˳�ʼ����Ǯ
CHANGE_MONEY_NORMAL					= 1			# ��ͨ�ĸı��Ǯ
CHANGE_MONEY_STORE					= 2			# �����Ǯ
CHANGE_MONEY_FETCH					= 3			# ȡ����Ǯ
CHANGE_MONEY_TEACH_REWARD			= 4			# ͽ��������ʦ����ý���
CHANGE_MONEY_GEM_HIRE				= 5			# ���þ��鱦ʯ�����Ľ�Ǯ
CHANGE_MONEY_BUR_FROM_NPC			= 6			# ��NPC��������Ʒ
CHANGE_MONEY_FAMILYWAR_BUR_FROM_NPC	= 7			# ����ս����NPC��������Ʒ
CHANGE_MONEY_REDEEMITEM				= 8			# �����Ʒ
CHANGE_MONEY_BUY_FROM_DARKTRADER	= 9			# �Ӻ������˴�������Ʒ
CHANGE_MONEY_TONGABABUYFROMNPC	    = 10		# ��������̨��Ʒ
CHANGE_MONEY_ROLE_TRADING			= 11		# ��ҽ���
CHANGE_MONEY_CREATE_FAMILY			= 12		# ��������
CHANGE_MONEY_FAMILY_ONCONTESTNPC	= 13		# ����NPC����
CHANGE_MONEY_FAMILY_CHALLENGE		= 14		# ���롰������ս���ķ���
CHANGE_MONEY_DLGBUYTRAINGEM			= 15		# NPC������ﾭ��ʯ
CHANGE_MONEY_HIRECOMMONGEM			= 16		# ���ó��ﾭ��ʯ
CHANGE_MONEY_REPLYFORMARRIAGE		= 17		# ���
CHANGE_MONEY_FORCEDIVORCE			= 18		# ���
CHANGE_MONEY_FINDWEDDINGRING		= 19		# �һؽ���ָ
CHANGE_MONEY_SALEGOODS				= 20		# ������Ʒ
CHANGE_MONEY_RECEIVESALEITEM		= 21		# ��������ҷ�����Ʒ
CHANGE_MONEY_CHAT_YELL				= 22		# �ź�
CHANGE_MONEY_PROCREATE				= 23		# ���ﷱֳ
CHANGE_MONEY_BUYITEMFROMDARKMERCHANT= 24		# �Ӱ��������˴�������Ʒ
CHANGE_MONEY_CREATETONG				= 25		# �������
CHANGE_MONEY_REPAIRONEEQUIPBASE		= 26		# ����װ������
CHANGE_MONEY_REPAIRALLEQUIPBASE		= 27		# ������������װ��
CHANGE_MONEY_PAYQUESTDEPOSIT		= 28		# ֧���������Ѻ��
CHANGE_MONEY_MONEYTOYINPIAO			= 29		# �һ���Ʊ
CHANGE_MONEY_MONEYDROPONDIED		= 30		# ��������
CHANGE_MONEY_STUFFCOMPOSE			= 31		# ���Ϻϳ�
CHANGE_MONEY_EQUIPSTILETTO			= 32		# װ�����
CHANGE_MONEY_EQUIPSPLIT				= 33		# װ�����
CHANGE_MONEY_EQUIPINTENSIFY			= 34		# װ��ǿ��
CHANGE_MONEY_EQUIPREBUILD			= 35		# װ������
CHANGE_MONEY_EQUIPBIND				= 36		# װ����
CHANGE_MONEY_SPECIALCOMPOSE			= 37		# ����ϳ�
CHANGE_MONEY_EQUIPMAKE				= 38		# װ������
CHANGE_MONEY_SAVEDOUBLEEXPBUFF		= 39		# ����˫������BUFF
CHANGE_MONEY_MAIL_SEND				= 40		# �����ʼ�
CHANGE_MONEY_VEND_SELL				= 41		# ��̯����
CHANGE_MONEY_VEND_SELLPET			= 42		# �����̯����
CHANGE_MONEY_LEARN_SKILL			= 43		# ѧϰ����
CHANGE_MONEY_AUGURY					= 44		# ռ��
CHANGE_MONEY_HUISHIBUKAO			= 45		# �ƾٻ��Բ���
CHANGE_MONEY_SUANGUAZHANBU			= 46		# ����ռ��
CHANGE_MONEY_TREASUREMAP			= 47		# ����ģ����ֽ��
CHANGE_MONEY_TELEPORT				= 48		# ����
CHANGE_MONEY_REACCEPTLOOPQUEST		= 49		# �ؽӻ�����
CHANGE_MONEY_BUKAO					= 50		# �ƾٲ���
CHANGE_MONEY_DEPOSIT				= 51		# ����Ѻ��
CHANGE_MONEY_SELLTONPC				= 52		# ������Ʒ��NPC
CHANGE_MONEY_PICKUPMONEY			= 53		# ʰȡ���
CHANGE_MONEY_MASTERENDTEACH			= 54		# ʦ�����ʦͽ��ϵ
CHANGE_MONEY_PRENTICEENDTEACH		= 55		# ͽ�ܽ��ʦͽ��ϵ
CHANGE_MONEY_CMS_RECEIVEMONEY		= 56		# �����۳���Ʒ
CHANGE_MONEY_SELLITEMTODARKMERCHANT	= 57		# ������Ʒ����������
CHANGE_MONEY_RETURNDEPOSIT			= 58		# ��������Ѻ��
CHANGE_MONEY_REQUESTADDITEM			= 59		# �����ȡ���
CHANGE_MONEY_MAIL_RECEIVEMONEY		= 60		# �ʼ���ȡ���
CHANGE_MONEY_REWARD_RACEHORSE		= 61		# ������
CHANGE_MONEY_DARTREWARD				= 62		# ����������ȡ����һ�ܽ���
CHANGE_MONEY_ABANDONED				= 63		# ��������ķ��� ���ز���Ѻ��
CHANGE_MONEY_QUESTPLACARDGIGHGRADE	= 64		# ��Ӣ��������
CHANGE_MONEY_QTTASKKILLDART			= 65		# ɱ�������ȡ
CHANGE_MONEY_WIZCOMMAND_SET_MONEY	= 66		# GM�������ý�Ǯ
CHANGE_MONEY_LOTTERYITEM			= 67		# ���ҳ�ȡ
CHANGE_MONEY_WUDAOAWARD				= 68		# ������
CHANGE_MONEY_GROUPQUESTREACCEPT		= 69		# ������ʧ�ܣ����������½��ܣ���Ҫ��Ʒ���Ǯ�Ĵ���
CHANGE_MONEY_REWARDVALTOMONEY		= 70		# �ͽ�㻻��Ǯ
CHANGE_MONEY_REDPACKAGE				= 71		# �����ȡ
CHANGE_MONEY_LUCKYBOXJINBAO			= 72		# ��������
CHANGE_MONEY_LUCKYBOXZHAOCAI		= 73		# �вƱ���
CHANGE_MONEY_QUESTPLACARDGENERAL	= 74		# ��ͨ�����������
CHANGE_MONEY_QTREWARDMONEY			= 75		# ������
CHANGE_MONEY_QTREWARDROBDARTMONEY	= 76		# ������
CHANGE_MONEY_QTREWARDMERCHANTMONEY	= 77		# �������������
CHANGE_MONEY_QTREWARDROLELEVELMONEY	= 78		# ������
CHANGE_MONEY_QTREWARDMONEYFROMTABLE	= 79		# ������
CHANGE_MONEY_DEPOSIT_RETURN			= 80		# ����Ѻ�𷵻�
CHANGE_MONEY_PRISON_CONTRIBUTE		= 81		# ��������
CHANGE_MONEY_OPEN_TREASURE_BOX		= 82		# ��������
CHANGE_MONEY_DETACHFAMILY			= 83		# �뿪�����ǲɢ��(�����˳����)
CHANGE_MONEY_MEMBER_LEVEL			= 84		# �뿪�����ǲɢ��(��Ա�˳����)
CHANGE_MONEY_GETCONTESTNPCMONEY		= 85		# ��Ա��ȡNPC�����
CHANGE_MONEY_CITYTONGMONEY			= 86		# ��ȡ����ռ����Ĺ����
CHANGE_MONEY_RECEIVETSPET			= 87		# ��ü��۵ĳ���
CHANGE_MONEY_CITYWAR_OVER			= 88		# ��ս�������뽱��
CHANGE_MONEY_RECEIVETSITEM			= 89		# ��ü��۵���Ʒ
CHANGE_MONEY_BUYCOLLECTIONITEM		= 90		# ֧���չ���ƷѺ���򷽣�
CHANGE_MONEY_SELLCOLLECTIONITEM		= 91		# �����չ���Ʒ��ã�������
CHANGE_MONEY_CANCELCOLLECTIONITEM	= 92		# ȡ���չ���ƷѺ���򷽣�
CHANGE_MONEY_CMS_SOCKS				= 93		# ʥ������
CHANGE_MONEY_TONG_CITYWAR_SIGNUP	= 94		# ��ս���ķ���
CHANGE_MONEY_YYD_BOX				= 95		# ����������
CHANGE_MONEY_UPDATE_COLLECTION_ITEM_INFO	= 96	#�����չ���Ʒ��Ϣ����Ľ�Ǯ�仯
CHANGE_MONEY_TALISMAN_SPLIT			= 97		# �����ֽ������Ǯ�仯 by ����
CHANGE_MONEY_BUY_YUANBAO			= 98		# ����Ԫ�� by ����
CHANGE_MONEY_CANCLE_YBT_BILL		= 99		# �������� by ����
CHANGE_MONEY_DRAW_MONEY				= 100		# �����˺�ȡ����Ǯ by ����
CHANGE_MONEY_RECEIVETS_MONEY		= 101		# ��ü��۵Ľ�Ǯ
CHANGE_MONEY_EQUIP_EXTRACT			= 102		# װ�����Գ�ȡ����Ľ�Ǯ�仯
CHANGE_MONEY_EQUIP_POUR				= 103		# װ�����Թ�ע����Ľ�Ǯ�仯
CHANGE_MONEY_EQUIP_UP				= 104		# װ������
CHANGE_MONEY_RABBIT_RUN				= 105		# С�ÿ���
CHANGE_MONEY_ALLY					= 106		# ���
CHANGE_MONEY_TONG_CONTRIBUTE		= 107		# ������
CHANGE_MONEY_POINT_CARD_YAJIN		= 108		# ���۵㿨Ѻ��
CHANGE_MONEY_FCWR_FOR_MSG			= 109		# �ǳ����ŷ��Է�
CHANGE_MONEY_LIVING_LEVEL_UP_SKILL	= 110		# ����������շ�
CHANGE_MONEY_NPC_TALK				= 111		# ��NPC�Ի��շ�
CHANGE_MONEY_FISHING_JOY				= 112		# ��Ҳ���
CHANGE_MONEY_JUE_DI_FAN_JI			= 113		# ���ط����������Ǯ
CHANGE_MONEY_AO_ZHAN_QUN_XIONG		= 114		# ��սȺ�ۻ������Ǯ
CHANGE_MONEY_CAMP_FENG_HUO			= 115		# ��Ӫ�������������Ǯ

# ---------------------------------------------------------------------
# �ı�Ǳ�ܵķ�ʽ	by����
# ---------------------------------------------------------------------
CHANGE_POTENTIAL_INITIAL			= 0			# Ĭ�Ϸ�ʽ
CHANGE_POTENTIAL_FABAO				= 1			# ������ȡǱ�� by����
CHANGE_POTENTIAL_ZHAOCAI			= 2			# �вƱ���
CHANGE_POTENTIAL_JINBAO				= 3			# ��������
CHANGE_POTENTIAL_CITYWAR_OVER		= 4			# ��ս�������뽱��
CHANGE_POTENTIAL_ROBOT_VERIFY		= 5			# �������֤���⽱��
CHANGE_POTENTIAL_CMS_SOCKS			= 6			# ʥ������
CHANGE_POTENTIAL_OLD_PLAYER_REWARD	= 7			# �������߶�ʱ����
CHANGE_POTENTIAL_YYD_BOX			= 8			# ����������
CHANGE_POTENTIAL_USE_ITEM			= 9			# ʹ��Ǳ�ܵ�
CHANGE_POTENTIAL_USE_ITEM_2			= 10		# ʹ��Ǳ����Ʒ
CHANGE_POTENTIAL_TRANS				= 11		# ������ȡǱ��
CHANGE_POTENTIAL_PICK_ANIMA			= 12		# ʰȡ��������ȡ

# ---------------------------------------------------------------------
# �ı�Ԫ���ķ�ʽ
# ---------------------------------------------------------------------
CHANGE_GOLD_INITIAL					= 0
CHANGE_GOLD_NORMAL					= 1
CHANGE_SILVER_INITIAL				= 0
CHANGE_SILVER_NORMAL				= 1

# ---------------------------------------------------------------------
# ��ɫ��Ϊ
# ---------------------------------------------------------------------
ROLE_TALK_BEHAVIOR 					= 0						# �Ի���
ROLE_SPELL_BEHAVIOR 				= 1						# ������
ROLE_PICK_DROPBOX_BEHAVIOR			= 2						# ʰȡ��ͨ������Ϊ
ROLE_PICK_QUESTBOX_BEHAVIOR			= 3						# ʰȡ����������Ϊ


# ---------------------------------------------------------------------
# �ı书ѫֵ�ķ�ʽ
# ---------------------------------------------------------------------
CHANGE_TEACH_CREDIT_NORMAL		= 0			# ��ͨ�ĸı书ѫֵ
CHANGE_TEACH_CREDIT_REWARD		= 1			# ͽ��������ʦ����ý���



#----------------------------------------------------------------------
#��Ϸ��������
#----------------------------------------------------------------------
REWARD_NONE						= 0							#������
REWARD_TEAMCOMPETITION_EXP		= 1 						#��Ӿ������齱��
REWARD_TEAMCOMPETITION_ITEMS	= 2 						#��Ӿ�����Ʒ����
REWARD_RACE_HORSE				= 3							#������
REWARD_RACE_HORSE_ITEMS			= 4							#������Ʒ����
REWARD_RABBIT_RUN				= 5							#С�ÿ���
REWARD_TONG_ABA					= 6							#�����̨���ھ���Ʒ����
REWARD_TEAMCOMPETITION_POT		= 7							#��Ӿ���Ǳ�ܽ���
REWARD_TEAMCOMPETITION_BOX_EXP	= 8							#��Ӿ������Ӿ��齱��
REWARD_ROLECOMPETITION_EXP		= 9							#���˾������齱��
REWARD_ROLECOMPETITION_BOX_EXP	= 10						#���˾������Ӿ��齱��
REWARD_TONG_ABA_EXP				= 11						#�����̨����ʤ���齱��
REWARD_TONG_WUDAO				= 12						#����ڻά��
REWARD_TONG_TEAM_CHALLENGE		= 13						#�����̨����
REWARD_TONG_TONG_CITY_WAR		= 14						#������ս����

#----------------------------------------------------------------------
# ���ӵ��䷽ʽ
#----------------------------------------------------------------------
DROPPEDBOX_TYPE_NONE			= 0							# Ĭ�ϵ��䷽ʽ
DROPPEDBOX_TYPE_MONSTER			= 1 						# �������
DROPPEDBOX_TYPE_STROE			= 2 						# ���������
DROPPEDBOX_TYPE_OTHER			= 3							# ��������

# ---------------------------------------------------------------------
# addProxyData - onProxyDataDownloadComplete�����api�ĵ���
# ͨ�Ż�����Ϣid���壬20:43 2009-7-7��wsf
# ---------------------------------------------------------------------
PROXYDATA_CSOL_VERSION		= 1						# ������ǰ�汾����

#----------------------------------------------------------------------
#����Ǯ�ı��ԭ��
#----------------------------------------------------------------------
TONG_CHANGE_MONEY_NORMAL				=	0	# Ĭ��
TONG_CHANGE_MONEY_DETACHFAMILY			=	1	# �������룬ǲɢ��
TONG_CHANGE_MONEY_PAYFIRSTCHIEF			=	2	# �������ʷ���
TONG_CHANGE_MONEY_PAYSECONDCHIEF		=	3	# ���������ʷ���
TONG_CHANGE_MONEY_SUBMITCONTESTMONEY	=	4	# �����������ս
TONG_CHANGE_MONEY_CITYWARBUYMACHINE		=	5	# ���ս�����е
TONG_CHANGE_MONEY_BUILDCITYWARTOWER		=	6	# �����ս��¥
TONG_CHANGE_MONEY_ROBWARFAILED			=	7	# ������Ӷ�ս��ʧ��
TONG_CHANGE_MONEY_RESEARCHSKILL			=	8	# �з�һ����Ἴ��
TONG_CHANGE_MONEY_CHANGEMAKEITEMS		=	9	# �ı��������з�����Ʒ
TONG_CHANGE_MONEY_PAYSPENDMONEY			=	10	# ���ά����
TONG_CHANGE_MONEY_BUILDTONGBUILDING		=	11	# �����޽���Ὠ��
TONG_CHANGE_MONEY_SELECTSHOUSHOU		=	12	# ѡ��������
TONG_CHANGE_MONEY_ROBWARSUCCESSFULLY	=	13	# ������Ӷ�ս��ʤ��
TONG_CHANGE_MONEY_BACKOUTTONGBUILDING	=	14	# ��Ὠ���з���,������޽��Ľ������������ʽ�
TONG_CHANGE_MONEY_GMCOMMAND				=	15	# GM�������Ӱ���Ǯ
TONG_CHANGE_MONEY_QTREWARDMERCHANTMONEY	=	16	# �������
TONG_CHANGE_MONEY_QTREWARDTONGMONEY		=	17	# ��ṱ������
TONG_CHANGE_MONEY_CITY_REVENUE			=	18	# �����ȡ����˰��
TONG_CHANGE_MONEY_SUBMIT_TONG_SIGN		=	19	# ����ϴ����
TONG_CHANGE_MONEY_CHANGE_TONG_SIGN		=	20	# ���������
TONG_CHANGE_MONEY_CONTRIBUTE_TO			=	21	# �����׽�Ǯ
TONG_CHANGE_MONEY_ITEM						= 22	# ����ʽ�ı����
TONG_CHANGE_MONEY_ABATTOIR				= 	23	# �����̨��������
TONG_CHANGE_MONEY_SALARY				=	24	# ������ȡ���ٺ»
TONG_CHANGE_MONEY_CITY_WAR_INTEGAL		= 	25	# ������ս�������ֶһ�
TONG_CHANGE_MONEY_QTREWARD				= 	26	# ������
TONG_CHANGE_MONEY_REQUEST_FETE			=	27	# ����������
TONG_CHANGE_MONEY_REQUEST_ROB_WAR		=	28	# ��������Ӷ�ս�
TONG_CHANGE_MONEY_REQUEST_MONSTER_RAID	=	29	# ����ħ����Ϯ�
TONG_CHANGE_MONEY_REQUEST_RACE			=	30	# �����������
TONG_CHANGE_MONEY_OPEN_DART_QUEST		=	31	# ���������������
TONG_CHANGE_MONEY_OPEN_NORMAL_QUEST		= 	32	# ��������ճ�����
TONG_CHANGE_MONEY_BUY_SPECIAL_ITEM		= 	33	# ��Ṻ��������Ʒ

#---------------------------------------------------------------------
#��ᾭ��ı�ԭ��
#---------------------------------------------------------------------
TONG_CHANGE_EXP_QTREWARD				= 1		# ������
TONG_CHANGE_EXP_MONSTER_RAID			= 2		# ħ����Ϯ
TONG_CHANGE_EXP_FETE					= 3		# ����
TONG_CHANGE_EXP_RACE					= 4		# �������
TONG_CHANGE_EXP_ROB_WAR					= 5		# �Ӷ�ս
TONG_CHANGE_EXP_SIGN_IN					= 6		# ���ǩ��

#---------------------------------------------------------------------
#ɾ����Ʒ��ԭ��
#---------------------------------------------------------------------
DELETE_ITEM_NORMAL						=	0	# Ĭ��
DELETE_ITEM_STACK						=	1	# ������Ʒ����Ʒ�ϲ���
DELETE_ITEM_STOREITEM					=	2	# �洢��Ʒ
DELETE_ITEM_EQUIPSTILETTO				=	3	# װ�����
DELETE_ITEM_CLEARWARITEMS				=	4	# �������ս��������ϵ�ս����Ʒ
DELETE_ITEM_WARITEMSDROPONDIED			=	5	# ����ս����������ս����Ʒ
DELETE_ITEM_CLEARABAITEMS				=	6	# ���������ս��������ϵ�ս����Ʒ
DELETE_ITEM_ABAITEMSDROPONDIED			=	7	# ������ս����������ս����Ʒ
DELETE_ITEM_COMMAND_CLEANBAGS			=	8	# GM������հ���
DELETE_ITEM_COMMAND_SWEAR				=	9	# ��Ϊ����ɾ��ͬ�Ľ�
DELETE_ITEM_WELKINYELL					=	10	# �������㲥ɾ��������
DELETE_ITEM_TUNNELYELL					=	11	# �������㲥ɾ��������
DELETE_ITEM_REMOVE_BC_CARDS				=	12	# (����)ɾ�����������Ƭ
DELETE_ITEM_PET_ADDLIFE					=	13	# ������������ֵɾ�����ٵ�
DELETE_ITEM_PET_ADDJOYANCY				=	14	# �������ӿ��ֶ�ɾ��һ�������������
DELETE_ITEM_PET_ENHANCE					=	15	# ����ǿ��ɾ��(���ʹ�ó���ǿ������ʱ��ɾ���ù�������Ҫ����Ʒ)
DELETE_ITEM_SUPERKLJDACTIVITY			=	16	# ��δ��ɵĹ��ܣ������ҵ�����ɾ�������󽱵���Ʒ
DELETE_ITEM_KLJDEXPREWARD				=	17	# ��δ��ɵĹ��ܣ����ֽ𵰣���ȡ���齱��,ɾ�����ֽ𵰾��齱����Ʒ
DELETE_ITEM_KLJDZUOQIREWARD				=	18	# ��δ��ɵĹ��ܣ����ֽ𵰣���ȡ���ｱ��,ɾ�����ֽ����ｱ����Ʒ
DELETE_ITEM_CLEARCITYWARFUNGUS			=	19	# ������뿪ս��ʱҪ������ϵ�Ģ����Ʒ
DELETE_ITEM_TONG_STOREITEM				=	20	# �洢�����ֿ�
DELETE_ITEM_TONG_ANGELEXCHANGE			=	21	# (����)���黻��
DELETE_ITEM_DROPONDIED					=	22	# �����������
DELETE_ITEM_STUFFCOMPOSE				=	23	# ���Ϻϳ�
DELETE_ITEM_EQUIPSPLIT					=	24	# װ�����
DELETE_ITEM_EQUIPSTUDDED				=	25	# װ����Ƕ
DELETE_ITEM_EQUIPINTENSIFY				=	26	# װ��ǿ��
DELETE_ITEM_EQUIPREBUILD				=	27	# װ������
DELETE_ITEM_EQUIPBIND					=	28	# װ����
DELETE_ITEM_SPECIALCOMPOSE				=	29	# ����ϳ�
DELETE_ITEM_EQUIPMAKE					=	30	# װ������
DELETE_ITEM_USEFLY						=	31	# ʹ����·��
DELETE_ITEM_USEITEMREVIVE				=	32	# �ø�����Ʒ����
DELETE_ITEM_USE							=	33	# ʹ����Ʒ�������ʹ�õ���Ʒ����Ϊ��ҵ�ʹ����Ϊ��ɾ�������磺ʹ��ҩˮƿ��
DELETE_ITEM_DIGTREASURE					=	34	# �ھ�ر�ͼ����Ϊ�ڱ��ص���Ϊ��ɾ������Ʒ�����磺��ͷ��
DELETE_ITEM_FISHINGINCHARGE				=	35	# �泡��������ȡ����ʱ��
DELETE_ITEM_CIFU						=	36	# ������͸�
DELETE_ITEM_XIANLING					=	37	# ������������
DELETE_ITEM_JIANZHENG					=	38	# ������֤��Ե
DELETE_ITEM_PEARLPRIME					=	39	# ��ȡ���龫��
DELETE_ITEM_CREATETONGRACEHORSE			=	40	# �����������
DELETE_ITEM_SHITUREWARD					=	41	# ʦͽ�ػ���ȡ����
DELETE_ITEM_SHITUCHOUJIANG				=	42	# ʦͽ�ػ��齱
DELETE_ITEM_RECORDRANQUEST				=	43	# ��¼�������
DELETE_ITEM_ABANDONEDQUESTRANDOM		=	44	# ��������
DELETE_ITEM_ABANDONEDQUESTLOOP			=	45	# �������������
DELETE_ITEM_COMPLETEQTTASKSUBMIT		=	46	# ��ͨ�ύ����ɾ���ύ��Ʒ
DELETE_ITEM_COMPLETESUBMITPICTURE		=	47	# �ύ����,ɾ����Ʒ(��������)
DELETE_ITEM_COMPLETESUBMIT_YINPIAO		=	48	# �ύ��Ʊ,ɾ����Ʒ(��������)
DELETE_ITEM_BCREWARD					=	49	# ��ȡ��ɫ��������,�Ƴ���������ϵ�ֽ��
DELETE_ITEM_SELLTONPC					=	50	# ���۸�NPC
DELETE_ITEM_ROLETRADING					=	51	# ��ҽ���
DELETE_ITEM_DESTROYITEM					=	52	# ������Ʒ
DELETE_ITEM_SALEGOODS					=	53	# ����һ����Ʒ
DELETE_ITEM_PAYYINPIAO					=	54	# ������Ʒ ֧����Ʊ
DELETE_ITEM_ACTIVATEBAG					=	55	# �������
DELETE_ITEM_USEVEHICLEITEM				=	56	# ʹ�������Ʒ
DELETE_ITEM_USEVEHICLEEQUIP				=	57	# ʹ�����װ��
DELETE_ITEM_ITEMLIFEOVER				=	58	# ��������Ʒ�������ڵ���й���ʱ�����Ʒ����ʱ�Զ�ɾ����
DELETE_ITEM_MAIL_SEND					=	59	# ����ʼ���Ʒ
DELETE_ITEM_VEND_SELL					=	60	# ��̯����
DELETE_ITEM_SPELLTOITEM					=	61	# ͬ��DELETE_ITEM_USE������ʹ��Ŀ������һ����Ʒ��
DELETE_ITEM_BUYFROMDARKTRADER			=	62	# ������Ʒ,��������̻����
DELETE_ITEM_BUYFROMITEMCHAPMAN			=	63	# �������Ʒ����Ʒ����NPC���˴�����һ��������ĳ����Ʒ�������˵�������Ʒ��
DELETE_ITEM_SYS_RECLAIM_ITEM			=	64	# ϵͳ���������Ʒ(��ҵ�ĳЩ��Ϊ����ϵͳɾ��ĳЩ�ض�����Ʒ����������뿪ĳ������򴥷���ĳ���������)
DELETE_ITEM_PAY							=	65	# ʹ�ü���������Ʒ
DELETE_ITEM_COMMITCITYWAR				=	66	# �ύ����ս������
DELETE_ITEM_QTSREMOVEITEM				=	67	# ����ɾ����Ʒ
DELETE_ITEM_QTSCHECKITEM				=	68	# ����ɾ����Ʒ
DELETE_ITEM_QTSAFTERDELETEITEM			=	69	# ���������ɾ����Ӧ��������Ʒ
DELETE_ITEM_QTTASKDELIVER				=	70	# �ռ�������������ɾ��
DELETE_ITEM_STACKABLEITEM				=	79	# ��Ʒ������һ��������������ֵ��ӵ���һ����Ʒ��
DELETE_ITEM_AUTOINSTUFFS				=	80	# װ�������У��Զ��ϲ����������Ĳ���
DELETE_ITEM_STACKABLEINBAG				=	81	# �����ڵ�����Ʒ
DELETE_ITEM_DOMESTICATEVEHICLE			=	82	# �������ֶ�״̬
DELETE_ITEM_FEEDVEHICLE					=	83	# ���ιʳ
DELETE_ITEM_UPDATETALISMANGRADE			=	84	# ��������Ʒ��
DELETE_ITEM_ACTIVATETALISMANATTR		=	85	# ���������
DELETE_ITEM_REBUILDTALISMANATTR			=	87	# ���취������
DELETE_ITEM_ADDTALISMANLIFE				=	88	# ������ֵ��������ʹ�����޵ķ��������ӷ�����ʹ������ʱ���õ��ĳ�ֵ���ߵ�ɾ����
DELETE_ITEM_USEYAODING					=	89	# ʹ����ҩ��
DELETE_ITEM_ITEMTELEPORT				=	90	# ʹ�ô��;��ᣬ ������� ����
DELETE_ITEM_SPLITITEM					=	91	# �����Ʒ
DELETE_ITEM_COMBINEITEM					=	92	# ��Ʒ�ϲ�
DELETE_ITEM_COLLECTION					=	93	# �չ���Ʒ
DELETE_ITEM_TALISMAN_SPLIT				=	94	# �����ֽ�
DELETE_ITEM_TALISMAN_INTENSIFY			=	95	# ����ǿ��
DELETE_ITEM_COLLECT_POINT				=	96	# �ɼ�
DELETE_ITEM_GOD_WEAPON_MAKE				=	97	# ����
DELETE_ITEM_ALLY						=	98	# ���
DELETE_ITEM_LUCKY_BOX					=	99	# �콵����
DELETE_ITEM_POTENTIAL_BOOK				= 	100	# ʹ��Ǳ����
DELETE_ITEM_MONSTER_ATTACK				=	101	# ���﹥��
DELETE_ITEM_MEGRA_FRUIT					=	102	# ��Ϧ�������ʵ�ϳ��Ƴ�
DELETE_ITEM_EQUIP_EXTRACT				=	103	# װ����ȡ
DELETE_ITEM_EQUIP_POUR					=	104	# װ����ע
DELETE_ITEM_EQUIP_UP					=	105 # װ������
DELETE_ITEM_EQUIP_ATTR_REBUILD			=	106 # װ����������
DELETE_ITEM_RABBIT_RUN					= 	107	# С�ÿ���
DELETE_ITEM_REMOVECRYSTAL				=	108	# ˮ��ժ��
DELETE_ITEM_CHANGEPROPERTY				=	109 # ϴǰ׺
DELETE_ITEM_IMPROVEQUALITY				=	110 # ��װ��Ʒ
DELETE_ITEM_USENATRUEJADEITEM			=	111 # ʹ���컯���
DELETE_ITEM_UP_STEP			       		=	112 # �������
DELETE_ITEM_VEHICLE_TO_ITEM				=	113 # �������Ʒ
DELETE_ITEM_TO_KITBAG					=	114	# �ѵ���ת�ɱ���
DELETE_ITEM_KITBAG_TO_ITEM				=	115	# �ѱ���ת�ɵ���
DELETE_ITEM_SWAP_KITBAG					=	116	# ��������������λ��
DELETE_ITEM_GMCOMMAND					=	117	# GM����ɾ��
DELETE_ITEM_REWARD_QUEST				=	118	# ʹ�õ���ˢ����������
#-------------------------------------------------------------------------------
#�����Ʒ��ԭ��
#-------------------------------------------------------------------------------
ITEM_NORMAL								=	0	# Ĭ��
ADD_ITEM_BUYFROMNPC						=	1	# ��NPC������
ADD_ITEM_BUYFROMITEMCHAPMAN				=	2	# ����������NPC�ǣ��������Ʒ����Ʒ
ADD_ITEM_ROLE_TRADING					=	3	# ��ҽ���
ADD_ITEM_RECEIVESPECIALGOODS			=	4	# �̳ǹ�����Ʒ
ADD_ITEM_ADDLOTTERYITEM					=	5	# ���ӽ��ҽ�����Ʒ
ADD_ITEM_EQUIPSTUDDED					=	6	# װ����Ƕ�������Ѹ�Ϊ85��˭�ɵģ���
ADD_ITEM_EQUIPINTENSIFY					=	7	# װ��ǿ���������Ѹ�Ϊ86��˭�ɵģ���
ADD_ITEM_REQUESTADDITEM					=	8	# ʰȡ��Ʒ
ADD_ITEM_ONLINEBENEFI					=	9	# �����ۼ�ʱ�佱��
ADD_ITEM_QUESTDART						=	10	# ����������
ADD_ITEM_QTREWARDITEMS					=	11	# ��ͨ������Ʒ������һ��������
ADD_ITEM_QTREWARDCHOOSEITEMS			=	12	# ��ѡһ��Ʒ����
ADD_ITEM_QTREWARDRNDITEMS				=	13	# �����Ʒ����������õ�һ��������
ADD_ITEM_QTREWARDFIXEDRNDITEMS			=	14	# �����Ʒ��������Ȼ�õ�����е�ĳһ����
ADD_ITEM_QTREWARDRANDOMITEMFROMTABLE	=	15	# ���������������Ʒ��Դ��һ�����
ADD_ITEM_QUESTTONGNORMALLOOPGROUP		=	16	# ��ỷ������
ADD_ITEM_QUESTTONGFETEGROUP				=	17	# ��������Ʒ����
ADD_ITEM_QUESTTONGBUILDGROUP			=	18	# ��Ὠ����Ʒ����
ADD_ITEM_QTSGIVEITEMS					=	19	# ���������Ʒ�����������Ҫ�õ�
ADD_ITEM_QTSGIVEYINPIAO					=	20	# ���������Ʊ������������
ADD_ITEM_QUEST							=	21	# ͨ������õ�һЩ��ͨ��Ʒ
ADD_ITEM_QUESTPOTENTIAL					=	22	# Ǳ��������
ADD_ITEM_GMCOMMAND						=	23	# GM��������
ADD_ITEM_MASTERENDTEACH					=	24	# ���ʦͽ��ϵ
ADD_ITEM_REPLYFORMARRIAGE				=	25	# ��ҽ��,��ȡ����ָ(Ů)
ADD_ITEM_MARRYSUCCESS					=	26	# ��ҽ��,��ȡ����ָ(��)
ADD_ITEM_FINDWEDDINGRING				=	27	# ��������һؽ���ָ
ADD_ITEM_RECEIVESALEITEM				=	28	# ���������Ʒ
ADD_ITEM_RECEIVECANCELITEM				=	29	# ���ȡ��������Ʒ
ADD_ITEM_TONG_ANGELEXCHANGE				=	30	# �����ϣ����黻��
ADD_ITEM_ADDWUDAOAWARD					=	31	# �����ά��
ADD_ITEM_TAKEPRESENT					=	32	# ��Ӫ���������ǰ���������ڡ�custom_ChargePresentUnite���͡�custom_ItemAwards����Ľ�����
ADD_ITEM_EQUIPMAKE						=	33	# װ������
ADD_ITEM_VEND_SELL						=	34	# ��̯������Ʒ
ADD_ITEM_LUCKYBOXJINBAO					=	35	# �������е���
ADD_ITEM_CHINAJOY_VIP					=	36	# ��CHINAJOY��VIP�����ã������Ա�ְҵ���һ������
ADD_ITEM_TREASUREMAP					=	37	# �ر�ͼ����
ADD_ITEM_LUCKYBOXZHAOCAI				=	38	# �вƱ��е���
ADD_ITEM_CHINAJOY						=	39	# ��CHINAJOY�����ã�ֻ����һ����Ʒ
ADD_ITEM_FISHING						=	40	# ������
ADD_ITEM_PRESENTKIT						=	41	# ����Ʒ����ã�һ���Ƚ�ͨ�õ�ͨ��ʹ��һ����Ʒ���һ����Ʒ�Ľ�����ʽ
ADD_ITEM_TEAMCOMPETITION				=	42	# ��Ӿ�����Ʒ����
ADD_ITEM_DARTREWARD						=	43	# ������ȡ����һ�ܽ���
ADD_ITEM_TESTACTIVITYGIFT				=	44	# ���ȼ�����������������NPC����ȡ��10-50���ȼ�������
ADD_ITEM_SPREADERGIFT					=	45	# �ƹ�Ա�����������ר�ã�
ADD_ITEM_SHITUCHOUJIANG					=	46	# ʦͽ�ػ��齱
ADD_ITEM_CHUSHIREWARD					=	47	# ʦͽ�ػ�30��45����ʦ����
ADD_ITEM_FAMILYWARBUYFROMNPC			=	48	# �������ս����Ʒ
ADD_ITEM_REDEEMITEM						=	49	# �����Ʒ
ADD_ITEM_BUYFROMDARKTRADER				=	50	# �������Ʒ
ADD_ITEM_BUYFROMTONGNPC					=	51	# �����ϣ����NPC��������Ʒ
ADD_ITEM_TONGABABUYFROMNPC				=	52	# ��������̨��Ʒ
ADD_ITEM_PICKUPITEM						=	53	# ʰȡһ����ƷEntity
ADD_ITEM_DOKLJDREWARD					=	54	# ��δ��ɵĹ��ܣ��ҵ�����
ADD_ITEM_DOSUPERKLJDACTIVITY			=	55	# ��δ��ɵĹ��ܣ������ҵ�����
ADD_ITEM_DOKLJDZUOQIREWARD				=	56	# ��δ��ɵĹ��ܣ����ֽ𵰣���ȡ���ｱ��
ADD_ITEM_BUYITEMFROMMERCHANT			=	57	#  ��Ҵ��ز����˴��������Ʒ
ADD_ITEM_BUYITEMFROMDARKMERCHANT		=	58	#  ��ҴӺ������˴��������Ʒ
ADD_ITEM_CHANGEGOLDTOITEM				=	59	# ��Ʊ�滻Ϊ��Ԫ��Ʊ��Ʒ
ADD_ITEM_GETCITYTONGITEM				=	60	# ��ȡ����ռ����ľ����ʵ
ADD_ITEM_ADDQUESTITEM					=	61	# �ӳ�������ϻ�õ���Ʒ�������ӡ�ʬ��ȣ�
ADD_ITEM_RECEIVEITEM					=	62	# ��ȡ�ʼ�������Ʒ
ADD_ITEM_ONREWARDITEM					=	63	# �����ϣ��ͽ��������װ��
ADD_ITEM_ITEMTELEPORT					=	64	# ʹ�ô�����Ʒ��ã��������һ�����Ʒʹ�ú����ɣ�
ADD_ITEM_ITEM_PICTURE					=	65	# ʹ�û�������
ADD_ITEM_CIFU							=	66	# ����͸���ȡ���չ�ԡ������֮һ������NPC�Ի��ķ�ʽ����Ʒ����Ʒ����
ADD_ITEM_XIANLING						=	67	# ���������ȡ���չ�ԡ������֮һ������NPC�Ի��ķ�ʽ����Ʒ����Ʒ����
ADD_ITEM_JIANZHENG						=	68	# ������֤��Ե��ȡ���չ�ԡ������֮һ������NPC�Ի��ķ�ʽ����Ʒ����Ʒ����
ADD_ITEM_POTENTIALMELEE					=	69	# Ǳ���Ҷ�����
ADD_ITEM_TAKELINGYAO					=	70	# ��ȡ��ҩ
ADD_ITEM_LOGINBCGAME					=	71	# �μӱ��������ȡ
ADD_ITEM_BCREWARD						=	72	# ���������ȡ����
ADD_ITEM_STOREITEM						=	73	# ������ȡ��(�洢��Ʒʱ���ŵ�������Ʒ�ĸ����ϣ�������Ʒ����)
ADD_ITEM_ADDITEM2ORDER					=	74	# ������ȡ������һ����Ʒ�ŵ�ָ��������ָ�������У�
ADD_ITEM_FETCHITEM2KITBAGS				=	75	# ������ȡ������һ����Ʒ�ŵ�ָ�������У�
ADD_ITEM_TONG_STOREITEM					=	76	# ���������ȡ��(�洢��Ʒʱ���ŵ�������Ʒ�ĸ����ϣ�������Ʒ����)
ADD_ITEM_TONG_FETCHITEM					=	77	# ���������ȡ��(��һ����Ʒ�ŵ�ָ��������)
ADD_ITEM_TONG_ADDITEM2ORDER				=	78	# ���������ȡ������һ����Ʒ�ŵ�ָ��������ָ�������У�
ADD_ITEM_STACKABLEITEM					=	79	# ��Ʒ������,���ӵ�������Ʒ��
ADD_ITEM_STACKABLEINBAG					=	81	# �����ڵ�����Ʒ
ADD_ITEM_COMBINEITEM					=	82	# ��Ʒ�ϲ����������ӣ�
ADD_ITEM_EQUIPSTILETTO					=	83	# װ�����
ADD_ITEM_STUFFCOMPOSE					=	84	# ���Ϻϳ�
ADD_ITEM_EQUIPSTUDDED					=	85	# װ����Ƕ
ADD_ITEM_EQUIPINTENSIFY					=	86	# װ��ǿ��
ADD_ITEM_EQUIPREBUILD					=	87	# װ������
ADD_ITEM_EQUIPBIND						=	88	# װ����
ADD_ITEM_SPECIALCOMPOSE					=	89	# ����ϳ�
ADD_ITEM_REQUESTIEEXP					=	90	# �ƾٿ��Խ���
ADD_ITEM_REQUESTIETITLE					=	91	# ��ȡ�ƺŽ���
ADD_ITEM_RACEHORSE						=	92	# ������Ʒ����
ADD_ITEM_TAKEJKCARDPRESENT				=	93	# ��ȡ���ֿ������������ר�ã�
ADD_ITEM_FIXITMEREWARD					=	94	# �½�ɫ��ʱ����
ADD_ITEM_TREASURE_BOX					=	95	# ��������
ADD_ITEM_STACK							=	96	# �϶�һ���ɵ�������ӵ���Ʒ��
ADD_ITEM_GIVEFIXTIMEREWARD				=	97	# ͨ��ֱ�Ӹ�������ʼ���ʽ�������ʵʱ���ֽ���
ADD_ITEM_SPLITITEM						=	98	# �����Ʒ��ȡ��ֳ�����Ʒ
ADD_ITEM_AUTOINSTUFFS					=	99	# װ�������Զ���ֺ��ȡ��ֳ�����Ʒ
ADD_ITEM_CMS_SOCKS						= 	100	# ʥ�����ӣ����вơ�����������ͬ���ܵ���Ʒ��
ADD_ITEM_OLD_PLAYER_REWARD				=	101	# �������߽��� by ����
ADD_ITEM_FOR_HONOR_GIFT					= 	102	# �����ȱ��У�����NPC�Ի��ķ�ʽ��ʹ������ֵ��ȡ�ı��У�
ADD_ITEM_YYD_BOX						= 	103	# ����������
ADD_ITEM_EQUIPSPLIT						=	104	# װ�����
ADD_ITEM_ROB_WAR_ITEM					=	105	# �Ӷ�ս��ȡ����
ADD_ITEM_SALEGOODS						=	106 # ������NPC�������Ʒ�����������ȡ��
ADD_ITEM_COLLECTION						=	107	# �չ���Ʒ�����ҵ�����NPC�ϻ�ȡ�ɹ��չ�����Ʒ��
ADD_ITEM_TALISMAN_SPLIT					=	108	# �����ֽ�
ADD_ITEM_TALISMAN_INTENSIFY				=	109	# ����ǿ��
ADD_ITEM_COLLECT_POINT					=	110	# �ɼ�����
ADD_ITEM_TEACH_SUCCESS					=	111	# ��ʦ�ɹ�
ADD_ITEM_GOD_WEAPON_MAKE				=	112	# ��������
ADD_ITEM_SPRING_FESTIVAL				=	113	# ���ڻ
ADD_ITEM_USE							=	114	# ʹ����Ʒ�õ���һ����Ʒ
ADD_ITEM_DANCE							=	115	# ����
ADD_ITEM_CHANGE_BODY					=	116	# ����
ADD_ITEM_TANABATA_QUIZ					=	117	# ��Ϧ�ʴ���Ʒ����
ADD_ITEM_SKILL_CLEAR					=	118	# ϴ������Ʒ���
ADD_ITEM_FRUIT_TREE						=	119	# ��Ϧ����������ɼ����
ADD_ITEM_MEGRA_FRUIT					=	120	# ��Ϧ�������ʵ�ϳɻ��
ADD_ITEM_GET_FRUIT						=	121	# ��Ϧ�������ʵ��ȡ����
ADD_ITEM_EQUIP_EXTRACT					= 	122	# װ����ȡ
ADD_ITEM_RABBIT_RUN						= 	123	# С�ÿ��ܻ�����Ʒ
ADD_ITEM_REMOVECRYSTAL					=	124	# ˮ��ժ��
ADD_ITEM_CHANGEPROPERTY					=	125	# ϴǰ׺
ADD_ITEM_IMPROVEQUALITY					=	126	# ��װ��Ʒ
ADD_ITEM_VEHICLE_TO_ITEM				=	127	# �������Ʒ
ADD_ITEM_TO_KITBAG						=	128	# �ѵ���ת�ɱ���
ADD_ITEM_KITBAG_TO_ITEM					=	128	# �ѱ���ת�ɵ���
ADD_ITEM_SWAP_KITBAG					=	129	# ��������������λ��
ADD_ITEM_BY_TALK						=	130	# �Ի�������Ʒ

#-------------------------------------------------------------------------------
#��ӵ��е�ԭ��
#-------------------------------------------------------------------------------
ADD_DAOHENG_REASON_QUEST				= 1
ADD_DAOHENG_REASON_KILL_MONSTER			= 2

#-------------------------------------------------------------------------------
#�����ȸı��ԭ��
#-------------------------------------------------------------------------------
HONOR_CHANGE_REASON_RECOVER				= 1		#����ֵ�ָ�
HONOR_CHANGE_REASON_ZHENG_DUO			= 2		#NPC����ս

# ---------------------------------------------------------------------
# entity�������������Ͷ���( kebiao, 2009-7-15 )
# ---------------------------------------------------------------------
ENTITY_CACHE_TASK_TYPE_NPCOBJECT0						= 0x00000000			# ��ȡnpcobjectģ����ص�����
ENTITY_CACHE_TASK_TYPE_NPCOBJECT1						= 0x00000011			# ��ȡ����NPCģ����ص�����
ENTITY_CACHE_TASK_TYPE_MONSTER0							= 0x00000010			# ��ȡmonsterģ����ص�����
ENTITY_CACHE_TASK_TYPE_COMBATUNIT0						= 0x00000020			# ��ȡcombatunitģ����ص�����
ENTITY_CACHE_TASK_TYPE_PET0								= 0x00000030			# ��ȡpetģ����ص�����=======





# ---------------------------------------------------------------------
# ��Ѽ�¼��־��Ҳ���ǲ��ɲμӱ�ǣ�
# ---------------------------------------------------------------------
ACTIVITY_FLAGS_TIANGUAN					= 0		#���
ACTIVITY_FLAGS_SHUIJING					= 1		#ˮ��
ACTIVITY_FLAGS_RACEHORSE				= 2		#����
ACTIVITY_FLAGS_YAYU						= 3		#�m؅
ACTIVITY_FLAGS_XLDX						= 4		#а����Ѩ
ACTIVITY_FLAGS_CMS_SOCKS				= 5		#ʥ��������
ACTIVITY_FLAGS_MEMBER_DART				= 6		#��Ա����
ACTIVITY_FLAGS_SPRING_RIDDLE			= 7		# ���ڵ���
ACTIVITY_FLAGS_FJSG						= 8		#�⽣��
ACTIVITY_FLAGS_SHMZ						= 9		#�������
ACTIVITY_FLAGS_TEACH_REWARD				= 10	#ʦͽÿ�ս���
ACTIVITY_FLAGS_FCWR						= 11	#�ǳ����ŷ������¼
ACTIVITY_FLAGS_TANABATA_QUIZ			= 12	# �����Ϧ�ʴ�
ACTIVITY_FLAGS_RABBITRUN				= 13	# С�ÿ���
ACTIVITY_FLAGS_KUAFUREMAIN				= 14	# �丸���
ACTIVITY_FLAGS_TONG_FUBEN				= 15	#��ḱ������
ACTIVITY_FLAGS_CHALLENGE_FUBEN			= 16	#��ս����
ACTIVITY_FLAGS_CHALLENGE_FUBEN_MANY		= 17 	#��ս����������
ACTIVITY_FLAGS_SHENGUIMIJING			= 18	# ����ؾ�
ACTIVITY_FLAGS_WUYAOQIANSHAO			= 19	# ����ǰ��
ACTIVITY_FLAGS_WUYAOWANGBAOZANG			= 20	# ʧ�䱦��(����������)
ACTIVITY_FLAGS_JYLD						= 21	# �����Ҷ�
ACTIVITY_FLAGS_QNLD						= 22	# Ǳ���Ҷ�
ACTIVITY_FLAGS_YING_XIONG_LIAN_MENG		= 23	#Ӣ������
ACTIVITY_FLAGS_YE_ZHAN_FENG_QI			= 24	#ҹս����ս��
ACTIVITY_FLAGS_YAYU_NEW					= 25	#�°����Ȫm؅
ACTIVITY_FLAGS_DESTINY_TRANS			= 26	# �����ֻظ���
ACTIVITY_FLAGS_TOWER_DEFENSE			= 27	# ��������
ACTIVITY_FLAGS_DUDUZHU					= 28	# ����


# ---------------------------------------------------------------------
# ��Ҫ�洢�ı�־Ϊ
# ---------------------------------------------------------------------
ENTITY_FLAG_KUA_FU_QUEST				= 0		# ӵ�п丸�������

#-----------------------------------------------------------------------
#���Ӿ����ԭ��
#-----------------------------------------------------------------------
CHANGE_EXP_INITIAL							= 0		# �ͻ��˳�ʼ������
CHANGE_EXP_ABA								= 1		# �����̨�����齱��
CHANGE_EXP_COMMAND							= 2		# GM�������Ӿ���
CHANGE_EXP_MASTERENDTEACH					= 3		# ���ʦͽ��ϵ
CHANGE_EXP_PRENTICEENDTEACH					= 4		# ��ҳ�ʦ
CHANGE_EXP_TEACH_REWARD						= 5		# ͽ��������ʦ����ý���
CHANGE_EXP_FABAO							= 6		# ������ȡ���� by����
CHANGE_EXP_QUIZ_GAMEOVER					= 7		# ��Ҵ�����ܽ���
CHANGE_EXP_TRAINEXPGEM						= 8 	# ������մ�����ʯ����
CHANGE_EXP_BCNPC							= 9		# NPC���������ȡ����
CHANGE_EXP_KLJDEXPREWARD					= 10	# ���ֽ𵰾��齱��
CHANGE_EXP_KEJUREWARD						= 11	# �ƾٿ��Խ�������
CHANGE_EXP_WUDAOAWARD						= 12	# �����ά������
CHANGE_EXP_KILLMONSTER						= 13	# ɱ�ֻ�ȡ����
CHANGE_EXP_REWARDVALTOEXP					= 14	# �ͽ�㻻ȡ����
CHANGE_EXP_DANCE							= 15	# �����þ���
CHANGE_EXP_LUCKYBOXJINBAO					= 16	# �������л�ȡ����
CHANGE_EXP_DOUBLEDANCE						= 17	# ˫�����þ���
CHANGE_EXP_TROOPDANCE						= 18	# ��������þ���
CHANGE_EXP_SUN_BATH							= 19	# �չ�ԡ��ȡ����
CHANGE_EXP_LUCKYBOXZHAOCAI					= 20	# �вƱ��л�ȡ����
CHANGE_EXP_TEAMCOMPETITION					= 21	# ��Ӿ������齱��
CHANGE_EXP_RACEHORSE						= 22	# ������
CHANGE_EXP_DARTREWARD						= 23	# ����������ȡ����һ�ܽ���
CHANGE_EXP_PEARLPRIME						= 24	# ��ȡ���龫��
CHANGE_EXP_CHUSHIREWARD						= 25	# ʦͽ�ػ�30��45����ʦ����(������ͽ������ȡ)
CHANGE_EXP_PLACARDGIGHGRADE					= 26	# ��Ӣ��������
CHANGE_EXP_PLACARDGENERAL					= 27	# ��ͨ��������
CHANGE_EXP_QTREWARD							= 28	# �������þ���
CHANGE_EXP_QTREWARDPERCENTAGEEXP			= 29	# �������þ���
CHANGE_EXP_QTREWARDRELATIONEXP				= 30	# �������þ���
CHANGE_EXP_QTREWARDEXPFROMROLELEVEL			= 31	# �������þ���
CHANGE_EXP_QTREWARDSECONDPERCENTEXP			= 32	# �������þ���
CHANGE_EXP_QTREWARDEXPFROMTABLE				= 33	# �������þ���
CHANGE_EXP_AIACTION							= 34	# ��ȡ����NPC���;���
CHANGE_EXP_FAMILYTEAM						= 35	# ������ӻ�ȡ���⾭��
CHANGE_EXP_NORMAL							= 36	# ��ͨ�ĸı侭��,��ɱ�ֵ�
CHANGE_EXP_CITYWAR_OVER						= 37	# ��ս�������뽱��
CHANGE_EXP_ROBOT_VERIFY_RIGHT				= 38	# �������֤���⽱��
CHANGE_EXP_CMS_SOCKS						= 39	# ʥ������
CHANGE_EXP_OLD_PLAYER_REWARD				= 40	# ����Ҽ�ʱ��ȡ����
CHANGE_EXP_YYD_BOX							= 41	# ����������
CHANGE_EXP_AND_POTENTIAL					= 42	# ���黻Ǳ��
CHANGE_EXP_TONG_ROB							= 43	# �Ӷ�ս���Ľ���
CHANGE_EXP_FISHING							= 44	# ����Ľ���
CHANGE_EXP_TEACH_BUFF						= 45	# ʦͽ����buff�Ľ���
CHANGE_EXP_RABBITRUN						= 46	# С�ÿ���
CHANGE_EXP_TONG_DART_ROB					= 47	# �ڳ�ˢ�ٷ�ʱ��������Ҿ��齱��
CHANGE_EXP_TEAM_CHALLENGE					= 48	# �����̨�����ľ���
CHANGE_EXP_USE_ROLE_COMPETITION_ITEM		= 49	#ʹ�ø��˾������鵤
CHANGE_EXP_CITYWAR_MASTER					= 50	# �������轱��
CHANGE_EXP_TONGCOMPETITION					= 51	# ��Ὰ�����齱��
CHANGE_EXP_TONGCOMPETITION_BOX				= 52	# ��Ὰ�����Ӿ��齱��
CHANGE_EXP_DANCE							= 53	# ����exp
CHANGE_EXP_DANCEKING						= 54	# ����exp
CHANGE_EXP_JUE_DI_FAN_JI					= 55	# ���ط�������齱��
CHANGE_EXP_AO_ZHAN_QUN_XIONG				= 56	# ��սȺ�ۻ
CHANGE_EXP_CAMP_FENG_HUO					= 57	# ��Ӫ����������齱��

#----------------------------------------------------------------------
#�㿨����(��ֵ����)
#-----------------------------------------------------------------------
RECHANGE_OVERTIME_FAILED					= -1		# ��ʱ����
RECHANGE_SUCCESS							= 0			# �㿨���۳ɹ�
RECHANGE_NO_OR_PWD_FAILED				    = 1			# ���Ż��������
RECHANGE_USED_FAILED					    = 2			# ��ʹ�õĿ�
RECHANGE_ACCOUNT_NOT_ACTIVITIED_FAILED	    = 3			# �ʺ�δ�ڸ�������
RECHANGE_ACCOUNT_NOT_HAVE_FAILED		    = 4			# �ʺŲ�����
RECHANGE_FAILED							    = 5			# ��ֵʧ��
RECHANGE_MD5_FAILED						    = 6			# MD5У��ʧ��
RECHANGE_PARAMS_FAILED					    = 7			# ����������
RECHANGE_SERVER_NAME_FAILED				    = 8			# �����ڵķ�������
RECHANGE_OVER_DUPLICATE_FAILED			    = 9			# �������ظ�
RECHANGE_TEN_YUAN						    = 10		# 10Ԫ��ֵ�Ŀ�
RECHANGE_IP_FAILED						    = 11		# IP���󣬷������������ͷ�������IP��Ӧ����
RECHANGE_ACCOUNT_MSG_FALIED				    = 12		# ��ȡ�ʺ���Ϣʧ��
RECHANGE_CARD_LOCKED_CARD				    = 13		# �ѷ�ŵĿ�
RECHANGE_LOGGED_FALID					    = 14		# д���ֵ��־ʧ��
RECHANGE_CARD_NOT_EXIST_CARD			    = 15		# �������� �� ��δ����
RECHANGE_SEND_YUANBAO_FAILED			    = 16		# �����ɹ������Ƿ���Ԫ��ʧ��
RECHANGE_THIRTY							    = 30		# 30Ԫ��ֵ�Ŀ�
RECHANGE_CARD_VALUE_FAILED				    = 17		# ��ֵ����


#----------------------------------------------------------------------
#�㿨����(��ʱ����)
#----------------------------------------------------------------------
OVERTIME_OVERTIME_FAILED					= -1		# ��ʱ����
OVERTIME_RECHANGE_SUCCESS					= 0	    	# ��ʱ����ֵ�ɹ�
OVERTIME_RECHANGE_FAILED					= 1	    	# ��ʱ����ֵ����
OVERTIME_NO_ORDER_FAILED					= 2 		# ��ʱû���������


ROLE_RELATION_BLACKLIST						= 0x0001		# ��Һ�������ϵ
ROLE_RELATION_FOE								= 0x0002		# ��ҳ��˹�ϵ
ROLE_RELATION_MASTER						= 0x0004		# ���ʦ����ϵ
ROLE_RELATION_PRENTICE						= 0x0008		# ���ͽ�ܹ�ϵ
ROLE_RELATION_FRIEND							= 0x0010		# ��Һ��ѹ�ϵ
ROLE_RELATION_SWEETIE						= 0x0020		# ������˹�ϵ
ROLE_RELATION_COUPLE							= 0x0040		# ��ҷ��޹�ϵ
ROLE_RELATION_ALLY							= 0x0080		# ��ҽ�ݹ�ϵ
ROLE_RELATION_MASTER_EVER					= 0x0100		# ��ҹ�ȥ��ʦ��
ROLE_RELATION_PRENTICE_EVER				= 0x0200		# ��ҹ�ȥ��ͽ��


#-----------------------------------------------------------------------
# ���/��ɫ������ǣ���Ч�ã� by����
#-----------------------------------------------------------------------
VEHICLE_ACTION_TYPE_CONJURE		= 1		# �ٻ�
VEHICLE_ACTION_TYPE_JUMP		= 2		# ��Ծ
VEHICLE_ACTION_TYPE_RANDOM		= 3		# �������
VEHICLE_ACTION_TYPE_WALK		= 4		# ����

#-----------------------------------------------------------------------
# �д�״̬
#-----------------------------------------------------------------------
QIECUO_NONE						= 0		# �д�Ĭ��״̬
QIECUO_INVITE					= 1		# �д�����״̬
QIECUO_BEINVITE					= 2		# �д豻����״̬
QIECUO_READY					= 3		# �д�׼��״̬
QIECUO_FIRE						= 4		# �д����״̬



#------------------------------------------------------------------------
#���ӳ����ԭ��
#------------------------------------------------------------------------
ADDPET_INIT						= 1		# ��ʼ��
ADDPET_PETTRADING				= 2		# ���ｻ��
ADDPET_TAKEPETFROMBANK			= 3		# �ֿ���ȡ������
ADDPET_CATCHPET					= 4		# ��׽����
ADDPET_FOSTER					= 5		# ���ﷱֳ
ADDPET_RECEIVETSPET				= 6		# ��ȡ���۵ĳ���
ADDPET_BUYFROMVEND				= 7		# �Ӱ�̯�й���


#------------------------------------------------------------------------
#ɾ�������ԭ��
#------------------------------------------------------------------------
DELETEPET_PETTRADING			= 1		# ���ｻ��
DELETEPET_PETSTORE				= 2		# �ֿ��д洢����
DELETEPET_FREEPET				= 3		# ��������
DELETEPET_COMBINEPETS			= 4		# ����ϳ�
DELETEPET_PROCREATEPET			= 5		# ���ﷱֳ
DELETEPET_TSPET					= 6		# ���ۼ��۳���
DELETEPET_VEND_SELLPET			= 7		# ��̯����


#-------------------------------------------------------------------------
#��Ԫ���ı��ԭ��
#-------------------------------------------------------------------------
CHANGE_SILVER_WEEKONLINETIMEGIFT	=	1	# ��ȡ�ܽ���
CHANGE_SILVER_TESTWEEKGIFT			=	2	# ��ȡ�ܽ���(�Ͻӿ�)
CHANGE_SILVER_SILVERPRESENT			=	3	# ��ȡ��Ԫ������
CHANGE_SILVER_CHARGE				=	4	# ��ֵ�һ���Ԫ��
CHANGE_SILVER_GMCOMMAND				=	5	# GM����
CHANGE_SILVER_BUYITEM				=	6	# �����̳���Ʒ
AUTOUSEYELL							=	7	# �Զ�������Ʒ
CHANGE_SILVER_ITEMTOSILVER			=	8	# Ԫ��Ʊ�����Ԫ��
CHANGE_SILVER_MESSY_TAKE			=	9	# ÿ����ȡ��һ�����
CHANGE_SILVER_FISHING_JOY			=	10	# �������

#-------------------------------------------------------------------------
#��Ԫ���ı��ԭ��
#-------------------------------------------------------------------------
CHANGE_GOLD_BANK_ITEM2GOLD			=	1	# Ԫ��Ʊ�һ��ɽ�Ԫ��
CHANGE_GOLD_GEM_CHARGE				=	2	# ��ֵ������ʯ
CHANGE_GOLD_PTN_TRAINCHARGE			=	3	# ��ֵ���������ʯ
CHANGE_GOLD_QUIZ_USEGOLD			=	4	# ʹ��Ԫ������
CHANGE_GOLD_BUYITEM					=	5	# �����̳���Ʒ
CHANGE_GOLD_PST_HIRE				=	6	# ���ó���ֿ�
AUTOUSEYELL							=	7	# �Զ�������Ʒ
CHANGE_GOLD_BANK_CHANGEGOLDTOITEM	=	8	# Ԫ��Ʊ�һ�
CHANGE_GOLD_CHARGE					=	9	# ��ֵ�һ�
CHANGE_GOLD_GMCOMMAND				=	10	# GM����
CHANGE_GOLD_YBT_CANCLE_BILL				=	11	# Ԫ�����׳������� by����
CHANGE_GOLD_YBT_SELL						=	12	# Ԫ��������Ԫ�� by����
CHANGE_GOLD_YBT_SELL_BILL					=	13	# Ԫ�����׽������۶��� by ����
CHANGE_GOLD_YBT_DRAW_YB					=	14	# ȡ���˺�Ԫ�� by ����
CHANGE_GOLD_ZD_ACTIVE_GRID			=	15	# ������ĸ���
CHANGE_GOLD_ZD_ACTIVE_GUIDE			=	16	# Ԫ���ٻ���ʦ


# ��npc������Ʒ�۸�����
INVOICE_NEED_MONEY = 0x01				# Ǯ�ｻ��
INVOICE_NEED_ITEM = 0x02					# ���ｻ��
INVOICE_NEED_DANCE_POINT = 0x04		# ������ֻ���Ʒ
INVOICE_NEED_TONG_CONTRIBUTE	= 0x08	# ��ṱ��
INVOICE_NEED_CHEQUE = 0x10				# ��Ʊ����
INVOICE_NEED_ROLE_PERSONAL_SCORE = 0x20				# ���˾�������
INVOICE_NEDD_TEAM_COMPETITION_POINT		= 0x40	#��Ӿ�������
INVOICE_NEED_TONG_SCORE   = 0x80		# ��Ὰ�����ֻ���Ʒ
INVOICE_NEED_ROLE_ACCUM_POINT = 0x100	# ����ֵ����Ʒ
INVOICE_NEED_SOUL_COIN = 0x200	# ���һ���Ʒ
INVOICE_NEED_CAMP_HONOUR = 0x400	# ���һ���Ʒ

# npc��Ʒ����
INVOICE_CLASS_TYPE_NORMAL	= 1			# ��ͨ��Ʒ
INVOICE_CLASS_TYPE_BIND		= 2			# ���ۺ��



#-------------------------------------------------------------------------
# ����ϵͳ by ����
#-------------------------------------------------------------------------
LIVING_SKILL_MAX	=	1	# ��ɫ����ѧϰ�������������

#-------------------------------------------------------------------------
# �������� by ����
# �ر�ǰ׺:RCG_	(reward config)
#-------------------------------------------------------------------------

RCG_OLD_PLAYER_FIXTIME		=	10001			# ��������߽���
RCG_TONG_FETE					= 10111		# �����뽱��

RCG_VIP_PACK					= 10021	# VIP���
RCG_LV_20_PACK				= 10022	# 20�����
RCG_LV_30_PACK				= 10023	# 30�����
RCG_LV_40_PACK				= 10024	# 40�����
RCG_LV_50_PACK				= 10025	# 50�����
RCG_NEWCARD_LV_15_PACK	= 10026	# 15�����ֿ����
RCG_NEWCARD_LV_35_PACK	= 10027	# 35�����ֿ����
RCG_CHINA_JOY_PACK		= 10028	# CHINA JOY���
RCG_TUIGUANG_PACK		= 10029	# �ƹ�Ա���
RCG_BENQ_PACK			= 10030	# �������
RCG_NORMAL_CASSTO_PACK	= 10031	# ��ͨ����ʯ���
RCG_INST_STUF_PACK		= 10032	# װ��ǿ���������
RCG_EQUMAKE_STUF_PACK	= 10033	# װ������������
RCG_PERF_CASSTO_PACK	= 10034	# ��������ʯ�����
RCG_LV10_PACK			= 10035	# 10�����
RCG_NEWCARD_LV_5_PACK	= 10036	# 5�����ֿ����
RCG_NEWCARD_LV_25_PACK	= 10037	# 25�����ֿ����
RCG_NEWCARD_LV_45_PACK	= 10038	# 45�����ֿ����

RCG_FISH						= 10301	# ����
RCG_KJ							= 10302	# �ƾٽ���
RCG_HAPPY_GODEN_EGG		= 10303	# ���ֽ�
RCG_SUPER_HAPPY_GODEN_EGG	= 10304	# �������ֽ�
RCG_HAPPY_GODEN_EGG_V	= 10305	# ���ֽ���轱��
RCG_WD_FORE_LEVEL			= 10306	# ������4lv����
RCG_WD_THREE_LEVEL			= 10307	# ������3lv����
RCG_SPRING_LIGHT			= 10308	# ���ڵ���
RCG_TONG_CITY_EXP			= 10309	# ����ռ����ľ����ʵ
RCG_TONG_ROB_WAR_1		= 10400	# �Ӷ�ս������ȡ 1
RCG_TONG_ROB_WAR_2		= 10401	# �Ӷ�ս������ȡ 2
RCG_TONG_ROB_WAR_3		= 10402	# �Ӷ�ս������ȡ 3
RCG_D_TEACH					= 10403	# ��ʦ��������Ʒ�б�
RCG_MARRY_RING				= 10404	# ����ָ��Ʒ
RCG_TEACH_END_SUC			= 10405	# ͽ�ܳ�ʦ�ɹ�����õĳ�ʦ״
RCG_TEACH_END_SUC_THK	= 10406	# ͽ�ܳ�ʦ�ɹ�ʦ������õĸж�״
RCG_TEACH_LEVEL_UP			= 10407	# ͽ��������õ�����״
RCG_TEACH_SUC				= 10408	# ��ʦ�ɹ�
RCG_TEACH_EVERY_DAY		= 10409	# ͽ��ÿ��ʦͽ����С�;��鵤
RCG_TANABATA_FRUIT		= 10411	# ��Ϧ�������ʵ����
RCG_MID_AUT_YGBH			= 10412	# �����¹ⱦ��
RCG_QUIZ_GAME_FESTIVAL		= 10413	# ֪ʶ�ʴ��ض����ս���

RCG_RACE_HORSE				= 10500	# ������Ʒ����

RCG_TEAM_COMP_EXP_1		= 10501	# ��Ӿ������齱��1
RCG_TEAM_COMP_EXP_2		= 10502	# ��Ӿ������齱��2
RCG_TEAM_COMP_EXP_3		= 10503	# ��Ӿ������齱��3
RCG_TEAM_COMP_EXP_4		= 10504	# ��Ӿ������齱��4
RCG_TEAM_COMP_EXP_5		= 10505	# ��Ӿ������齱��5
RCG_TEAM_COMP_EXP_6		= 10506	# ��Ӿ������齱��6
RCG_TEAM_COMP_EXP_7		= 10507	# ��Ӿ������齱��7
RCG_TEAM_COMP_EXP_8		= 10508	# ��Ӿ������齱��8
RCG_TEAM_COMP_EXP_9		= 10509	# ��Ӿ������齱��9
RCG_TEAM_COMP_EXP_10		= 10510	# ��Ӿ������齱��10

RCG_LUCKY_BOX		= 10511	# �콵����
RCG_MID_AUTUMN	= 10512	# �������

RCG_RACE_HORSE_CHRIS			= 10513	# ʥ��������Ʒ����
RCG_TONG_ABA					= 10514	# �����̨���ھ���Ʒ����,id��δȷ��

#-------------------------------------------------------------------------
#�������
#-------------------------------------------------------------------------
ACTIVITY_PARENT_TYPE_QUEST				= 1				#������
ACTIVITY_PARENT_TYPE_SPACECOPY			= 2				#������
ACTIVITY_PARENT_TYPE_ITEM				= 3				#��Ʒ
ACTIVITY_PARENT_TYPE_MONEY				= 4				#��Ǯ
ACTIVITY_PARENT_TYPE_SKILL				= 5				#����
ACTIVITY_PARENT_TYPE_SKILL				= 5				#��֯��������ᣬ����ȣ�

ACTIVITY_PARENT_TYPE_OTHER				= 2				#������
ACTIVITY_PARENT_TYPE_MONSTER_DIED		= 3				#��������
ACTIVITY_PARENT_TYPE_CHANGE_MONSTER		= 4				#��ɹ���


#-------------------------------------------------------------------------
#�����
#-------------------------------------------------------------------------
ACTIVITY_ROLE_UP					=	-1	#��ɫ����
ACTIVITY_LOOP_QUEST_30_59			=	0	#30-59��������
ACTIVITY_LOOP_QUEST_60_95			=	1	#60-95��������
ACTIVITY_TONG_LUE_DUO				=	2	#����Ӷ�ս
ACTIVITY_TONG_DUO_CHENG				=	3	#�����ս
ACTIVITY_NPC_LUE_DUO				=	4	#NPC�Ӷ�ս
ACTIVITY_NPC_GUA_JING_YAN			=	5	#NPC�Ҿ���
ACTIVITY_JIA_ZU_LEI_TAI				=	6	#������̨��
ACTIVITY_JIA_ZU_TIAO_ZHAN			=	7	#������ս��
ACTIVITY_XING_XIU					=	8	#������ս
ACTIVITY_TAO_FA						=	9	#�ַ�����
ACTIVITY_NORMAL_DART				=	10	#��ͨ������
ACTIVITY_EXP_DART					=	11	#����������
ACTIVITY_FAMILY_DART				=	12	#����������
ACTIVITY_CAI_LIAO_QUEST				=	13	#��������
ACTIVITY_KE_JU_QUEST				=	14	#�ƾٴ���
ACTIVITY_JIAO_FEI_QUEST				=	15	#�˷�����
ACTIVITY_CHU_YAO_QUEST				=	16	#��������
ACTIVITY_SHANG_HUI_QUEST			=	17	#�̻�����
ACTIVITY_SHENG_WANG					=	18	#��������
ACTIVITY_FAMILY_RICHANG_QUEST		=	19	#�����ճ�����
ACTIVITY_TONG_JISHI_QUEST			=	20	#������
ACTIVITY_TONG_JIANSHE_QUEST			=	21	#��Ὠ������
ACTIVITY_TONG_RICHANG_QUEST			=	22	#����ճ�����
ACTIVITY_TONG_MERCHANT				=	23	#�����������
ACTIVITY_CHUANG_TIAN_GUAN			=	24	#�����
ACTIVITY_CANG_BAO_TU				=	25	#�ر�ͼ
ACTIVITY_LING_GONG_ZI				=	26	#�칤��
ACTIVITY_TONG_PROTECT				=	27	#��������
ACTIVITY_BIN_LIN_CHENG_XIA			=	28	#���ٳ���
ACTIVITY_SAI_MA						=	29	#����
ACTIVITY_DU_DU_ZHU					=	30	#����
ACTIVITY_FENG_JIAN_SHEN_GONG		=	31	#�⽣��
ACTIVITY_GE_REN_JING_JI				=	32	#���˾���
ACTIVITY_TOU_JI_SHANG_REN			=	33	#Ͷ������
ACTIVITY_HUN_DUN_RU_QIN				=	34	#��������
ACTIVITY_NIU_MO_WANG				=	35	#ţħ��
ACTIVITY_QIAN_NIAN_DU_WA			=	36	#ǧ�궾��
ACTIVITY_BANG_HUI_JING_JI			=	37	#��Ὰ��
ACTIVITY_TIAO_WU					=	38	#����
ACTIVITY_BIAN_SHEN_DA_SAI			=	39	#�������
ACTIVITY_DIAO_YU					=	40	#����
ACTIVITY_CAI_JI_ZHEN_ZHU			=	41	#�ɼ�����
ACTIVITY_JING_YAN_LUAN_DOU			=	42	#�����Ҷ�
ACTIVITY_QIAN_NENG_LUAN_DOU			=	43	#Ǳ���Ҷ�
ACTIVITY_SHE_HUN_MI_ZHEN			=	44	#�������
ACTIVITY_SHEN_GUI_MI_JING			=	45	#����ؾ�
ACTIVITY_SHI_LUO_BAO_ZHANG			=	46	#ʧ�䱦��
ACTIVITY_WU_YAO_QIAN_SHAO			=	47	#����ǰ��
ACTIVITY_SHUI_JING					=	48	#ˮ������
ACTIVITY_TIAN_CI_QI_FU				=	49	#�����
ACTIVITY_TIAN_JIANG_QI_SHOU			=	50	#�콵����
ACTIVITY_ZHI_SHI_WEN_DA				=	51	#֪ʶ�ʴ�
ACTIVITY_WU_DAO_DA_HUI				=	52	#������
ACTIVITY_ZHENG_JIU_YA_YU			=	53	#���Ȫm؅
ACTIVITY_ZU_DUI_LUAN_DOU			=	54	#����Ҷ�
ACTIVITY_DUO_LUO_LIE_REN			=	55	#��������
ACTIVITY_BAI_SHE_YAO				=	56	#������
ACTIVITY_JU_LING_MO					=	57	#����ħ
ACTIVITY_XIAO_TIAN_DA_JIANG			=	58	#Х���
ACTIVITY_FENG_KUANG_JI_SHI			=	59	#����ʦ
ACTIVITY_HAN_DI_DA_JIANG			=	60	#���ش�
ACTIVITY_SHENG_LIN_ZHI_WANG			=	61	#ɭ��֮��
ACTIVITY_NU_MU_LUO_SHA				=	62	#ŭĿ��ɲ
ACTIVITY_YE_WAI_BOSS				=	63	#Ұ��BOSS
ACTIVITY_NPC_ZHENG_DUO				=	64	#NPC����ս
ACTIVITY_BAO_XIANG					=	65	#�콵���У����䣩
ACTIVITY_FAMILY_NPC					=	66	#ӵ��NPC�ļ�������
ACTIVITY_FAMILY_COUNT				=   67  #��������
ACTIVITY_TONG_COUNT					=   68  #�������
ACTIVITY_QUEST_SHOUJI				=   69  #�ռ�����
ACTIVITY_QUEST_LAN_LV				=   70  #��װ����װ
ACTIVITY_SHI_TU						=	71  #ʦͽ�
ACTIVITY_NPC_BUY					=	72  #NPC���������Ʒ
ACTIVITY_TONG_GONGZI				=	73  #��ᷢ���ʻ
ACTIVITY_NPC_SELL					=	74  #��ҹ���NPC��Ʒ
ACTIVITY_XIU_LI						=	75  #�������װ��
ACTIVITY_SHEN_JI_XIA				=	76  #���ϻ�
ACTIVITY_QUEST_JU_QING				=	77  #��������
ACTIVITY_RUN_RABBIT					=   78  #С�ÿ���
ACTIVITY_BANG_HUI_LEI_TAI			=	79	#�����̨��
ACTIVITY_XIE_LONG					= 	80  #а����Ѩ
ACTIVITY_POTENTIAL					= 	81  #Ǳ�ܸ������˷ˣ������ȣ�
ACTIVITY_ROLE_VEND					=	82	#��̯
ACTIVITY_ROLE_TI_SHOU				=	83	#����
ACTIVITY_ROLE_EXP_GEM				=	84	#��ɫ����
ACTIVITY_PET_EXP_GEM				=	85	#�������
ACTIVITY_TALISMAN					= 	86  #����
ACTIVITY_EQUIP						= 	87  #װ�����
ACTIVITY_CMS_SOCKS					= 	88	#ʥ������
ACTIVITY_MEMBER_DART				=	89	#��Ա����
ACTIVITY_SPRING_RIDDER				=	90	#��������
ACTIVITY_FEI_CHENG_WU_YAO			= 	91	#�ǳ�����
ACTIVITY_TANABATA_QUIZ				=	92	#��Ϧ�ʴ�
ACTIVITY_KUA_FU						=	93	#�丸���
ACTIVITY_TONG_FUBEN					= 	94	#��ḱ��
ACTIVITY_CHALLENGE_FUBEN			= 	95	#������ս����
ACTIVITY_CHALLENGE_FUBEN_MANY		=	96	#������ս����
ACTIVITY_YING_XIONG_LIAN_MENG		=	97	#Ӣ�����˸���
ACTIVITY_YE_ZHAN_FENG_QI			=	98	#ҹս����ս��
ACTIVITY_ZHENG_JIU_YA_YU_NEW		=	99	#�°����Ȫm؅
ACTIVITY_TONG_FENG_HUO_LIAN_TIAN	=	100	#�����ս������������죩
ACTIVITY_TOWER_DEFENSE				=	101 #��������
ACTIVITY_TEAM_COMPETITION			=	102 #��Ӿ���
ACTIVITY_DRAGON						= 	103	#��ͷ�����
ACTIVITY_BEFORE_NIRVANA				=	104 #10�����鸱��
ACTIVITY_PLOT_LV40					=	105 #40�����鸱��
ACTIVITY_PLOT_LV60					=	106 #60�����鸱��
ACTIVITY_TEAM_CHALLENGE				=	107 #�����̨
ACTIVITY_TONG_TURN_WAR				=	108 #��ᳵ��ս
ACTIVITY_YING_XIONG_LIAN_MENG_PVP	=	109 #Ӣ�����˸���PVP
ACTIVITY_EXAMINATION_XIANGSHI		=	110 #�ƾ٣�����
ACTIVITY_EXAMINATION_HUISHI			=	111 #�ƾ٣�����
ACTIVITY_EXAMINATION_DIANSHI		=	112 #�ƾ٣�����
ACTIVITY_DENTITY_TRANS_COM			=	113	#�����ֻظ�������ͨģʽ��
ACTIVITY_TONG_CAMPAIGN				=	114	#���ħ����Ϯ
ACTIVITY_YI_JIE_ZHAN_CHANG			=	115 #���ս������
ACTIVITY_AO_ZHAN_QUN_XIONG			=	116 #��սȺ��

DIRECT_WRITE_LOG_MGR				= 	0	#�ͳ��ֱ��д��־��ʽ
WRITE_BUFFER_LOG_MGR				= 	1	#�ͳ�ƻ���д��־��ʽ




#������Ϊ
ACTIVITY_QUEST_ACTION_ACCEPT		=	0	#��������
ACTIVITY_QUEST_ACTION_COMPLETE		=	1	#�������
ACTIVITY_QUEST_ACTION_ABANDON		=	2	#��������

#����뷽ʽ
ACTIVITY_JOIN_ROLE		= 	1	#���˲���
ACTIVITY_JOIN_TEAM		= 	2	#�������
ACTIVITY_JOIN_TONG		=	3	#������

#��������Ϊ
ACTIVITY_COMPETITION_START			= 	0	#����
ACTIVITY_COMPETITION_TEAM_POINT		=	1	#����
ACTIVITY_COMPETITION_ADD_HONOR		=	2	#��������
ACTIVITY_COMPETITION_SUB_HONOR		=	3	#��������
ACTIVITY_COMPETITION_CHANGE_BOX		=	4	#�һ�����
ACTIVITY_COMPETITION_SIGN_UP		=	5	#����/����
ACTIVITY_COMPETITION_ROLE_KILL		=	6	#ɱ�����
ACTIVITY_COMPETITION_TIME			=	7	#����ʱ��
ACTIVITY_COMPETITION_ADD_PERSONAL_SCORE	=	8	#���Ӹ��˾�������
ACTIVITY_COMPETITION_SUB_PERSONAL_SCORE	=	9	#���ٸ��˾�������

#��action
ACTIVITY_ACTION_ROLE_UP			= 	0	#��ɫ����
ACTIVITY_ACTION_ROLE_ADD_EXP	= 	1	#��ɫ��þ���
ACTIVITY_ACTION_ROLE_TRIGGER	= 	2	#�������������﹥������
ACTIVITY_ACTION_MONSTER_DIED	= 	3	#��������
ACTIVITY_ACTION_COPY_START		= 	4	#��������
ACTIVITY_ACTION_USE_ITEM		= 	5	#ʹ����Ʒ
ACTIVITY_ACTION_LING_GONG_ZI	= 	6	#��ȡ����
ACTIVITY_ACTION_TRADE			= 	7	#����
ACTIVITY_ACTION_DANCE			= 	8	#����
ACTIVITY_ACTION_BODY_CHANGE		= 	9	#����
ACTIVITY_ACTION_PASSED			= 	10	#ͨ��
ACTIVITY_ACTION_DIAO_YU			= 	11	#����
ACTIVITY_ACTION_CAIJI			=	12	#�ɼ�
ACTIVITY_ACTION_QI_FU			=	13	#��
ACTIVITY_ACTION_JI_SI			=	14	#����
ACTIVITY_ACTION_REWARD_MONEY	= 	15	#������Ǯ
ACTIVITY_ACTION_TONG_CITY_RECORD	= 	16	#��ս��¼
ACTIVITY_ACTION_REWARD_MONEY_CONTRIBUTE = 17	# ������ṱ��
ACTIVITY_ACTION_CITY_MASTER_SET	= 18	# ��������
ACTIVITY_ACTION_CITY_WAR_SIGN_UP_COUNT	= 19	# ��ս��������
ACTIVITY_ACTION_COPY_SPACE_LEVEL	= 20 #�����ȼ���
ACTIVITY_ACTION_CURRENT_PLAYER_COUNT = 21 #��ǰ�����
ACTIVITY_ACTION_ROLE_START_BEHAVIOR		 = 22 #����һ����Ϊ�����ۣ���̯����ɫ��������������ȣ�
ACTIVITY_ACTION_TALISMAN_REBUILD	= 23 #����ϴ����
ACTIVITY_MAKE_EQUIP					= 24 #װ�����죨װ�����죩
ACTIVITY_ACTION_BUY_ITEM			= 25 #����Ʒ
ACTIVITY_ACTION_BUY_PET				= 26 #�����
ACTIVITY_ACTION_REWARD_TONG_ACITONVAL = 27	# ��������ж���
ACTIVITY_ACTION_REWARD_DAOHENG		= 28 # ��������

# ----------------------------------------------------
# Ԫ���������
# ----------------------------------------------------
YB_TRADE_TYPE_BUY		= 1		# ������Ϊ ����Ԫ��
YB_TRADE_TYPE_SELL		= 2		# ������Ϊ ����Ԫ��
YB_BILL_TYPE_BUY			= 1		# �������� ��Ԫ��
YB_BILL_TYPE_SELL			= 2		# �������� ����Ԫ��
YB_BILL_STATE_FREE			= 0		# ����״̬ ����
YB_BILL_STATE_TRADE_LOCK = 1		# ����״̬ ��������
YB_BILL_STATE_OVER_DUE	= 2		# ����״̬ ����
YB_BILL_STATE_SELL_OUT	= 3		# ����״̬ �ۿ�
YB_BILL_STATE_ON_TRADE	= 4		# ����״̬ ������
YB_RECORD_BUY_BILL		= 1		# ��ϸ���� �������۶���
YB_RECORD_SELL_BILL		= 2		# ��ϸ���� �����󹺶���
YB_RECORD_BUY			= 3		# ��ϸ���� ��Ԫ��
YB_RECORD_SELL			= 4		# ��ϸ���� ��Ԫ��


# ----------------------------------------------------
# ���﹥��
# ----------------------------------------------------
SPECIAL_BOX_01	= 1							#��ã֮��
SPECIAL_BOX_02	= 2							#�־�֮��
SPECIAL_BOX_03  = 3							#�ڰ�֮��


# ----------------------------------------------------
# ���ҵ����������Ҫ��һЩ��¼�������ĳЩ�������Ϣ��
# ----------------------------------------------------
MESSY_JOB_TAKE_SILVER	= 1					#��ȡԪ��


#------------------------------------------------------
#�ǳ�����
#------------------------------------------------------
FCWR_VOTE_ALL			= 0					#��ͶƱ
FCWR_VOTE_KAN_HAO		= 1					#����
FCWR_VOTE_QING_DI		= 2					#���
FCWR_VOTE_SHI_LIAN		= 3					#ʧ��
FCWR_VOTE_KAN_QI		= 4					#����Ϸ
FCWR_VOTE_FAN_DUI		= 5					#����
FCWR_VOTE_LU_GUO		= 6					#·��

FCWR_MAX_COUNT_VOTER_1		= 7					#ͶƱ��Ŀ��һ��
FCWR_MAX_COUNT_VOTER_2		= 8					#ͶƱ��Ŀ�ڶ���
FCWR_MAX_COUNT_VOTER_3		= 9					#ͶƱ��Ŀ������

#------------------------------------------------------
# �����������췽ʽ
#------------------------------------------------------
FRUIT_TREE_RIPE_NORMAL	 = 1		# ������Ȼ����
FRUIT_TREE_RIPE_FAST	 = 2		# ����ʩ�ʳ���

# ----------------------------------------------------------------------------
# �������ɻ����
# ----------------------------------------------------------------------------
PROTECT_TONG_NORMAL			= 0		# ����������ͨ�
PROTECT_TONG_MID_AUTUMN		= 1		# ������������

# ----------------------------------------------------------------------------
# ���ħ����Ϯ added by mushuang
# ----------------------------------------------------------------------------
MONSTER_RAID_TIME_OUT_CBID = 100 # �ʱ�䵽��callback id
PRIZE_DURATION = 15 * 60 # ������ڵ�ʱ��

#-----------------------------------------------------------------------------
#���������֮������Ի�õ�״̬ �μ� CSOL-9750 by mushuang
#-----------------------------------------------------------------------------
NONE_STATUS = 0
LUNARHALO = 1	# ���θ�¶
SUNSHINE = 2	# �չ��¶
STARLIGHT = 3	# �ǻԸ�¶



TONG_FETE_ACT_VAL = 30 # ������������ж���

FLYING_BUFF_ID = 8006  # �������buff��ID
VEHICLE_BUFF_ID = 6005 # ½�����buff��ID

#-----------------------------------------------------------------------------
#����������Ʒ����Ҫ���� ���־��
#-----------------------------------------------------------------------------
TISHOU_BUY_FROM_TISHOUMGR	= 0				#ͨ������������
TISHOU_BUY_FROM_TISHOUNPC	= 1				#ͨ��NPC����
TISHOU_BUY_SUCCESS			= 2				#����ɹ�

ROLE_DIE_DROP_PROTECT_LEVEL = 30			# ����������䱣������С�ڴ˼��𲻵���װ������Ʒ

#-----------------------------------------------------------------------------
#���vip������
#-----------------------------------------------------------------------------
ROLE_VIP_LEVEL_NONE			= 0
ROLE_VIP_LEVEL_GOLD			= 1
ROLE_VIP_LEVEL_PLATINUM		= 2
ROLE_VIP_LEVEL_DIAMOND		= 3

#������������Ʒ�ʽ
NORMAL_WORLD_CAM_HANDLER		= 1	#������������Ʒ�ʽ
FIX_WORLD_CAM_HANDLER			= 2	#�̶��ӽ���������Ʒ�ʽ

#-----------------------------------------------------------------------------
# ��Ծ����
#-----------------------------------------------------------------------------
JUMP_TIME_UP1					= 0x1				# ��Ծ�����׶�1
JUMP_TIME_UP2					= 0x2				# ��Ծ�����׶�2
JUMP_TIME_UP3					= 0x3				# ��Ծ�����׶�3
JUMP_TIME_DOWN					= 0x4				# ��Ծ����׶�
JUMP_TIME_END					= 0x5				# ��Ծ�����׶�
JUMP_TIME_UPPREPARE				= 0x6				# ���������׶�

JUMP_TYPE_LAND					= 0x10				# ½����Ծ
JUMP_TYPE_WATER1				= 0x20				# ˮ����Ծ1
JUMP_TYPE_WATER2				= 0x30				# ˮ����Ծ2
JUMP_TYPE_WATER3				= 0x40				# ˮ����Ծ3
JUMP_TYPE_ATTACK				= 0x80				# ����
JUMP_TYPE_SIMULATE                              = 0x50                          #ģ����Ծ

JUMP_TIME_MASK					= 0x0000000f		# ��Ծ�׶�����
JUMP_TYPE_MASK					= 0x000000f0		# ��Ծ��������



JUMP_UP2_SKILLID                                = 322537001 #2��������ID
JUMP_UP3_SKILLID                                = 322537002 #3��������ID

JUMP_UP2_ENERGY                                = 5   #2������������ֵ
JUMP_UP3_ENERGY                                = 10  #3������������ֵ
JUMP_ENERGY_MAX                                = 100 #��Ծ�������ֵ

ROLE_ENERGY_REVER_INTERVAL                      = 1.0  #��Ծ����ֵ���Զ��ָ�timer
ROLE_ENERGY_REVER_VALUE                         = 5.0  #��Ծ����ֵ���Զ��ָ�ֵ

#�񶷵���
ROLE_CombatCount_MAX  = 5                             #���񶷵���
ROLE_CombatCount_TIMMER                      = 1.0  #����ս���񶷵����Զ�˥��timmer
ROLE_CombatCount_TIMMER_VALUE                = 1  #����ս���񶷵����Զ�˥��ֵ

#-----------------------------------------------------------------------------
# ��������������
#-----------------------------------------------------------------------------
ROLE_INITIALIZE					= 0					# ��ɫ��ʼ������


#-----------------------------------------------------------------------------
# ��ս����
#-----------------------------------------------------------------------------
CHALLENGE_RANK_EASY = 0
CHALLENGE_RANK_HARD = 1


MATCH_LEVEL_NONE = 0			#
MATCH_LEVEL_FINAL = 1			# ����
MATCH_LEVEL_SEMIFINALS = 2		# �����
MATCH_LEVEL_QUARTERFINAL = 3	# �ķ�֮һ����
MATCH_LEVEL_QUARTERFINAL = 4	# �˷�֮һ����
MATCH_LEVEL_SIXTEENTH = 5		# ʮ����֮һ����
MATCH_LEVEL_SIXTEENTH = 6		# ��ʮ����֮һ����

MATCH_TYPE_PERSON_ABA = 1			# ������
MATCH_TYPE_TEAM_ABA = 2				# �����̨
MATCH_TYPE_TONG_ABA = 3				# �����̨
MATCH_TYPE_TEAM_COMPETITION = 4		# ���龺��
MATCH_TYPE_TONG_COMPETITION = 5		# ��Ὰ��
MATCH_TYPE_PERSON_COMPETITION = 6	# ���˾���

#-----------------------------------------------------------------------------
# ����ͳ��(����)
#-----------------------------------------------------------------------------
CPU_COST_SKILL				= 1		#��������
CPU_COST_AI					= 2		#AI����
CPU_COST_AI_SC				= 3		#AIʹ��Ƶ��

#-----------------------------------------------------------------------------
# ����ͳ��(����)
#-----------------------------------------------------------------------------
CPU_COST_SKILL_CHECK		= 1	#��⼼��
CPU_COST_SKILL_USE			= 2	#ʹ�ü���
CPU_COST_SKILL_ARRIVE		= 3 #���ܵ���


CPU_COST_AI_FREE		= 1 #ai ����
CPU_COST_AI_FIGHT		= 2 #ai ս��

AI_ACTION				= 1 	# AI����
AI_CONDITION			= 2 	# AI����

#-----------------------------------------------------------------------------
# �����״̬
#-----------------------------------------------------------------------------
ACTIVITY_CAN_JOIN					= 1	#���Բ���
ACTIVITY_CAN_NOT_JOIN				= 2 #���ܲ���


#-----------------------------------------------------------------------------
# �������ϵͳ
#-----------------------------------------------------------------------------
COPY_DUTY_MT			= 1					# ��������ְ��̹��
COPY_DUTY_HEALER		= 2					# ��������ְ������
COPY_DUTY_DPS			= 3					# ��������ְ���˺����



TIME_LIMIT_OF_DUTIES_SELECTION 	= 120.0		# ְ��ѡ��ʱ�����ƣ���λ����
TIME_LIMIT_OF_MATCHED_CONFIRM 	= 120.0		# ƥ��ȷ��ʱ�����ƣ���λ����
TIME_RESET_MATCH_STATUS			= 3.0       # ���˵���뿪���������¼��븱�������һ��3���ʱ��
TIME_LIMIT_OF_CONFIRM_RESUMING 	= 120.0		# ȷ�ϼ����·���������ʱ�����ƣ���λ����
TIME_LIMIT_OF_MATCHED_INTERVAL	= 900.0		# ƥ�����ٴ�ʹ�õ���ȴʱ�䣬 ��λ����
TIME_LIMIT_OF_KICKING_INTERVAL	= 300.0		# �����޳�����ͶƱ��ʱ��������λ����
# ����ְ��ƥ��״̬����
COPY_TEAM_DUTIES_CONFLICT 				= 1			# ְ���ͻ
COPY_TEAM_DUTIES_MATCH_PARTIALLY 		= 2			# ְ�𲿷�ƥ�䣬���黹ȱ����ְ��
COPY_TEAM_DUTIES_MATCH_PLENARILY 		= 3			# ְ����ȫƥ�䣬����ƥ��ɹ�
COPY_TEAM_BLACKLIST_CONFLICT			= 4			# ��������ͻ
COPY_TEAM_RECRUITER_CONFLICT			= 5			# ��ļ�߳�ͻ
# ����ƥ��״̬
MATCH_STATUS_PERSONAL_NORMAL			= 0			# ����ƥ��״̬����ͨ״̬
MATCH_STATUS_PERSONAL_SELECTING_DUTY	= 1			# ����ƥ��״̬��ְ��ѡ��״̬(�����ҲŻ�������״̬)
MATCH_STATUS_PERSONAL_MATCHING			= 2			# ����ƥ��״̬������ƥ��״̬
MATCH_STATUS_PERSONAL_CONFIRMING		= 3			# ����ƥ��״̬������ְ��ȷ��
MATCH_STATUS_PERSONAL_MATCHED			= 4			# ����ƥ��״̬��ְ��ȷ�ϳɹ�
# ƥ��ɹ�״̬
MATCH_STATUS_PERSONAL_INSIDECOPY		= 0			# ����ƥ��״̬��ƥ��ɹ����ڸ�����
MATCH_STATUS_PERSONAL_OUTSIDECOPY		= 1			# ����ƥ��״̬��ƥ��ɹ����ڸ�����
# ����ƥ��״̬
MATCH_STATUS_TEAM_NORMAL				= 0			# ����ƥ��״̬����ͨ����
MATCH_STATUS_TEAM_SELECTING_DUTY		= 1			# ����ƥ��״̬��ְ��ѡ��״̬(�����ҲŻ�������״̬)
MATCH_STATUS_TEAM_MATCHING				= 2			# ����ƥ��״̬�������Ŷ���
MATCH_STATUS_TEAM_MATCHED				= 3			# ����ƥ��״̬��ƥ��ɹ�
# ƥ��ɹ�״̬
MATCH_STATUS_TEAM_MATCH_PLENARY			= 0			# ����ƥ��״̬��ƥ�����Ա����
MATCH_STATUS_TEAM_MATCH_VACANT			= 1			# ����ƥ��״̬��ƥ��Ĳ�ȱ����
# ְ��ȷ��״̬
MATCHED_CONFIRM_STATUS_ACCEPT			= 1			# ְ��ȷ��״̬������
MATCHED_CONFIRM_STATUS_ABANDON			= 2			# ְ��ȷ��״̬������
MATCHED_CONFIRM_STATUS_PENDING			= 3			# ְ��ȷ��״̬��δѡ��
# ������ԭ����
LEAVE_TEAM_ACTIVE						= 1			# ����Լ��������
LEAVE_TEAM_VOTE_KICKED					= 2			# ��ͶƱ�߳�����
LEAVE_TEAM_ABANDON_MATCH				= 3			# ������·�����Ӷ��뿪����

#������Ͷ���
VEHICLE_TYPE_LAND = 1 #½�����
VEHICLE_TYPE_FLY  = 2 #�������
VEHICLE_UPDATE_REASON_LEVEL_UP = 1 #�ȼ��ı���������Ըı�
VEHICLE_UPDATE_REASON_STEP_UP  = 2 #������������Ըı�

# Ұ�⸱�� monster type ����
MONSTER_TYPE_COMMON_MONSTER 	= 0 	# С��
MONSTER_TYPE_COMMON_BOSS		= 1		# boss
MONSTER_TYPE_NON_METERING		= 2 	# ���������

# ����
RESIST_NONE			 = 0
RESIST_YUANLI		 = 1
RESIST_LINGLI		 = 2
RESIST_TIPO			 = 3


#-----------------------------------------------------------------------------
# �̹��ػ�ϵͳ
#-----------------------------------------------------------------------------

# �̹��ػ���Ϊ
PGNAGUAL_ACTION_MODE_FOLLOW 			= 0					# ����
PGNAGUAL_ACTION_MODE_ATTACK 			= 1					# ����
PGNAGUAL_ACTION_MODE_NEAR_GROUP 		= 2					# ��սȺ�����̹��ػ�ʹ�ü���
PGNAGUAL_ACTION_MODE_NEAR_SINGLE 		= 3					# ��ս�������̹��ػ�ʹ�ü���
PGNAGUAL_ACTION_MODE_FAR_PHYSIC 		= 4					# Զ���������̹��ػ�ʹ�ü���
PGNAGUAL_ACTION_MODE_FAR_MAGIC 			= 5					# Զ�̷������̹��ػ�ʹ�ü���

# �̹��ػ��������Ͷ���
PGNAGUAL_TYPE_NEAR_GROUP 				= 1					# ��սȺ��
PGNAGUAL_TYPE_NEAR_SINGLE 				= 2					# ��ս����
PGNAGUAL_TYPE_FAR_PHYSIC 				= 3					# Զ������
PGNAGUAL_TYPE_FAR_MAGIC 				= 4					# Զ�̷���

# �̹��ػ����컯��뺵ľ���
PGNAGUAL_REALM_DIXIAN 					= 1 				# ����
PGNAGUAL_REALM_TIANXIAN 				= 2 				# ����
PGNAGUAL_REALM_TAIYISANXIAN 			= 3 				# ̫��ɢ��
PGNAGUAL_REALM_DALUOJINXIAN 			= 4 				# ���޽���
PGNAGUAL_REALM_ZHUNSHENG 				= 5 				# ׼ʥ

# ����
PG_FORMATION_TYPE_CIRCLE		= 1 	# ��Բ��
PG_FORMATION_TYPE_SNAKE			= 2 	# ������
PG_FORMATION_TYPE_FISH			= 3 	# ������
PG_FORMATION_TYPE_ARROW			= 4 	# ��ʸ��
PG_FORMATION_TYPE_GOOSE			= 5 	# ������
PG_FORMATION_TYPE_CRANE			= 6 	# ������
PG_FORMATION_TYPE_MOON			= 7 	# ������
PG_FORMATION_TYPE_EIGHT			= 8 	# ������
PG_FORMATION_TYPE_TAIL			= 9 	# β����
PG_FORMATION_TYPE_SCATTERED		= 10 	# ��ɢ��

#-----------------------------------------------------------------------------
# Ӣ�����˰�ʧ�䱦��
#-----------------------------------------------------------------------------
YXLM_MAX_EQUIP_AMOUNT			= 6		# �������6��װ��


#-----------------------------------------------------------------------------
# �����ز����ĸ���ԭ��
#-----------------------------------------------------------------------------
# �������ԭ��
TONG_CREATE_REASON_NOMAL		= 1		# �������̴���
TONG_CREATE_REASON_GM			= 2		# GMָ���

# ɾ�����ԭ��

TONG_DELETE_REASON_GM				= 1		# GMָ��ɾ��
TONG_DELETE_REASON_MONEY_LESS		= 2		# ����ά���Ѳ���
TONG_DELETE_REASON_ACTIVITY_LOW		= 3		# ��Ծ��̫��
TONG_DELETE_REASON_NOMAL			= 4		# ������ɢ

# �������ԭ��
TONG_CHIEF_CHANGE_REASON			= 1		# ������λ

# ��������ı�ԭ��
TONG_PRESTIGE_CHANGE_REST			= 0		# ����ԭ��
TONG_PRESTIGE_CHANGE_GM				= 1		# GMָ��
TONG_PRESTIGE_CHANGE_USE_ITEM		= 2		# ʹ����Ʒ�ı�������
TONG_PRESTIGE_CHANGE_ABA			= 3		# �����̨
TONG_PRESTIGE_CHANGE_ROB_WAR		= 4		# �����

# ���ȼ��ı�ԭ��
TONG_LEVEL_CHANGE_REASON_GM				= 0		# GMָ��
TONG_LEVEL_CHANGE_REASON_TERRITORY		= 1		# ��Ὠ������
TONG_LEVEL_CHANGE_REASON_ADD_EXP		= 2		# ��ᾭ������


#�ƺŸı�ԭ��
ALLY_TITILE_CHANGE_REASON_INIT			= 0		# ��ʼ����ݳƺ�
ALLY_TITILE_CHANGE_REASON_ADD			= 1		# ���ӽ�ݳƺ�
ALLY_TITILE_CHANGE_REASON_ADD_MEMBER		= 2		# ���ӽ�ݳƺ�
ALLY_TITILE_CHANGE_REASON_MEMBER_CHANGE			= 3		# ���Ľ�ݳƺ�


#-----------------------------------------------------------------------------
# ҹս������ս��
#-----------------------------------------------------------------------------
# �����ر�ԭ��
FENG_QI_CLOSE_REASON_MIN_PLAYER 	= 1 # �õ�ͼ����̫��
FENG_QI_CLOSE_REASON_MIN_LEVEL 		= 2 # �õȼ�����̫��
FENG_QI_CLOSE_REASON_TIME_OUT		= 3 # ��ʱ������

# �����ֻظ��������¼�����
CHESS_BOARD_EVE_NONE				= 0 # ��
CHESS_BOARD_EVE_MOVE				= 1 # �����ƶ�
CHESS_BOARD_EVE_BUFF				= 2 # ���Buff
CHESS_BOARD_EVE_BOSS				= 3 # ��սBoss
CHESS_BOARD_EVE_DROP				= 4 # �౶����

DESTINY_ENTER_GATE_SINGLE			= 1 # ���˽���
DESTINY_ENTER_GATE_TEAM				= 2 # �������

# ��ʾ��Ϣ
DESTINY_TRANS_FAILED_GATE			= 1	# ͨ��ʧ��
DESTINY_TRANS_FINISH_GATE			= 2	# ���
DESTINY_TRANS_FIRST_NAME			= 3	# ��һ��

#----------------------------------------------------------------------------
# ��Ӫ�����
#----------------------------------------------------------------------------
CAMP_ACT_DESTROY_BASE		= 1		# �ƻ��ݵ�
CAMP_ACT_OBTAIN_POINT		= 2		# ��û���
CAMP_ACT_KILL_BOSS			= 3		# ��ɱBoss
CAMP_ACT_OCCUPY_BASE		= 4		# ��ռ�ݵ�
CAMP_ACT_INTERCEPT_HELPER	= 5		# ����֧Ԯ����
CAMP_ACT_LITTLE_WAR			= 6		# С����
CAMP_ACT_BIG_WAR			= 7		# ȫ��ս��

# -----------------------------------------------------------------------
# �ͻ��˶Ի������������ȼ�
# -----------------------------------------------------------------------
GOSSIP_PLAY_VOICE_PRIORITY_DEFAULT	= 0				#Ĭ������
GOSSIP_PLAY_VOICE_PRIORITY_OPTION	= 1				#�Ի�����
GOSSIP_PLAY_VOICE_PRIORITY_QUEST		= 2				#��������

#��������ˢ������
REWARD_QUEST_SYSTEM_REFRESH			= 0				#ϵͳˢ��
REWARD_QUEST_LOW_ITEM_REFRESH		= 1				#�͵ȵ���ˢ��
REWARD_QUEST_HIGH_ITEM_REFRESH		= 2				#�ߵȵ���ˢ��

#��������Ʒ������
REWARD_QUEST_QUALITY_WHITE			= 1				#��ɫƷ��
REWARD_QUEST_QUALITY_BLUE			= 2				#��ɫƷ��
REWARD_QUEST_QUALITY_PURPLE			= 3				#��ɫƷ��
REWARD_QUEST_QUALITY_GREEN			= 4				#��ɫƷ��

#��������ÿ���ܹ���ȡ���ܴ���
REWARD_QUEST_CAN_ACCEPT_NUM			= 20			#��������ÿ���ܽ���20��

#�������������ʾ״̬
REWARD_QUEST_CAN_ACCEPT				= 0				#�ɽ�ȡ��������
REWARD_QUEST_ACCEPT					= 1				#�ѽ�ȡ��������
REWARD_QUEST_COMPLETED				= 2				#�������������

#------------------------------------------------------------------------
# ��ħ��ս��������
#------------------------------------------------------------------------
TDB_JOIN_REWARD					= 1				# ���뽱
TDB_DAMAGE_REWARD				= 2				# �˺���
TDB_FIRST_DAMAGE_REWARD			= 3				# �״���
TDB_DEATH_REWARD				= 4				# ��������
TDB_CURE_REWARD					= 5				# ���ƽ���

#------------------------------------------------------------------------
# ��սȺ��
#------------------------------------------------------------------------
#��������
AO_ZHAN_ROOM_TYPE_NO_FAILURE	= 1		#û��ʧ����
AO_ZHAN_ROOM_TYPE_HAS_FAILURE	= 2		#��ʧ����

#------------------------------------------------------------------------
# ���ս��
#------------------------------------------------------------------------
# վ����������Ӫ
YI_JIE_ZHAN_CHANG_FACTION_TIAN		= 1		#�췽��Ӫ
YI_JIE_ZHAN_CHANG_FACTION_DI		= 2		#�ط���Ӫ
YI_JIE_ZHAN_CHANG_FACTION_REN		= 3		#�˷���Ӫ

# �����ر�ԭ��
YI_JIE_CLOSE_REASON_TIME_END		= 1 	# �������ʱ��
YI_JIE_CLOSE_REASON_ONE_FACTION_WIN = 2		# һ����Ӫ��ǰȡ��ʤ��

#------------------------------------------------------------------------
# ���ط����
#------------------------------------------------------------------------
JUE_DI_FAN_JI_NOT_SIGN_UP				= 0				# δ�����׶�
JUE_DI_FAN_JI_HAS_SIGN_UP				= 1				# �Ѿ������ȴ��׶�
JUE_DI_FAN_JI_HAS_MATCHED				= 2				# �Ѿ�ƥ��ɹ��׶�
JUE_DI_FAN_JI_HAS_CONFIRM_ENTER			= 3				# �Ѿ�ȷ������׶�
JUE_DI_FAN_JI_HAS_ENTERED				= 4				# �Ѿ����븱���׶�
JUE_DI_FAN_JI_SHOW_RANK_LIST			= 5				# �����鿴�񵥽׶�
JUE_DI_FAN_JI_VICTORY_STATUS			= 2				# ���ط���ʤ��״̬
JUE_DI_FAN_JI_DRAW_STATUS				= 1				# ���ط���ƽ��״̬
JUE_DI_FAN_JI_FAILED_STATUS				= 0				# ���ط���ʧ��״̬

#�������
DANCE_CAN_CHALLENGE					= 1		#��ʾ������ս
DANCE_IN_PROTECT_TIME				= 2		#��ʾ���ڱ���ʱ��
DANCE_IS_CHALLENGED					= 3		#��ʾ��������ս
DANCE_CHALLENGE_MYSELF				= 4		#��ʾ��ս�Լ�
DANCE_CHALLENGE_LOWER_LEVEL_DANCER	= 5		#��ʾ��ս�͵ȼ��������Լ�Ҳ������
DANCE_POSITION_IS_EMPTY				= 6		#��ʾ��ǰλ��û���������Լ�����ֱ�ӳ�Ϊ����
DANCE_EXP_NOT_GET				= 7		#��ʾ��ǰ��δ��ȡ�ľ���
DANCEK_NOT_GET_POSITION				= 8		#��ʾδ��ȡλ��
DANCER_GOLDEN	= 1		#��������
DANCER_SILVER	= 2		#��������
DANCER_COPPER	= 3		#ͭ������
DANCER_CANDIDATE	= 4		#��ѡ����
DANCER_NONE		= 0		#δ�ϰ�
DANCER_GOLDEN_RATITO 	= 10  	#�����������鱶��10
DANCER_SILVER_RATITO	= 5  	#�����������鱶��5
DANCER_COPPER_RATITO	= 3		#ͭ���������鱶��3
DANCER_CANDIDATE_RATITO	= 2		#��ѡ�������鱶��2
DANCER_NONE_RATITO		= 1		#δ�ϰ��鱶��
DANCETIMEOUTTIMER			= 4104
DANCEKINGTIMEOUTTIMER		= 4105
DANCEHALLPERSONLIMIT		= 20
DANCETIMELIMIT 				= 8*60*60
DANCECOPYTIMELIMIT			= 360  # ��ս���踱������ʱ��
DANCEKINGRANGE				= 50  # �����п��Կ���npc�����ַ�Χ

#------------------------------------------------------------------------
# �����ս����
#------------------------------------------------------------------------
# �ݵ����Ͷ���
CITY_WAR_FINAL_BASE_NONE				= 0
CITY_WAR_FINAL_BASE_RESOURCE			= 1				# ��Դ�ݵ�
CITY_WAR_FINAL_BASE_BATTLE				= 2				# ս���ݵ�
CITY_WAR_FINAL_BASE_FLAG				= 3				# �����
CITY_WAR_FINAL_BASE_HEROMONU			= 4				# Ӣ�鱮
CITY_WAR_FINAL_BASE_FLAG_GUARD			= 5				# ���콫
CITY_WAR_FINAL_LIGHT_WALL				= 6				# ��ǽ

# �ݵ����
CITY_WAR_FINAL_FACTION_NONE				= 0				# �޹���
CITY_WAR_FINAL_FACTION_ATTACK			= 1				# ���Ƿ�
CITY_WAR_FINAL_FACTION_DEFEND			= 2				# �سǷ�

# --------------------------------------------------------------------
# copyEvent  define( designed by wangzhen )
# --------------------------------------------------------------------
# �����¼�
COPY_EVENT_ON_BEGIN_STAGE				= 1				# �����ؿ���ʼ
COPY_EVENT_ON_MONSTER_DIE				= 2				# ��������
COPY_EVENT_ON_ROLE_DIE					= 3				# ��ɫ����
COPY_EVENT_ON_ENTER_COPY				= 4				# ��ҽ��븱��
COPY_EVENT_ON_LEAVE_COPY				= 5				# ����뿪����
COPY_EVENT_ON_TELEPORT_READY			= 6				# ��ͼ������ɣ���ҿ����ƶ�
COPY_EVENT_ON_FIRST_ENTER_COPY			= 7				# ��һ����ҽ����¼�
COPY_EVENT_ON_TIMER						= 8				# ����onTimer�¼�
# �����������¼�
COPY_EVENT_MMP_ON_SPAWN_GOBLIN			= 100			# ˢС���¼�
COPY_EVENT_MMP_ON_EVIL_WIND				= 101			# �������¼�
COPY_EVENT_MMP_ON_FLOOR_TRAP			= 102			# ���������¼�
COPY_EVENT_MMP_ON_BEFORE_SPAWN_GOBLIN	= 103			# ����ˢ���¼�
# ���ظ����¼�
COPY_EVENT_FANG_SHOU_ON_GEAR_STARTING	= 200			# ���ؿ����¼�
COPY_EVENT_FANG_SHOU_ON_NPC_HP_CHANGED	= 201			# ����NPCѪ���ı��¼�
COPY_EVENT_FANG_SHOU_ON_TOWER_CREATE	= 202			# ���ظ��������������¼�



#��̬��ϵģʽ���Ͷ���
RELATION_STATIC_CAMP							= 1				#��ͨ��Ӫ��ϵģʽ
RELATION_STATIC_CAMP_FENG_HUO					= 2				#��Ӫ������츱��ģʽ
RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY		= 3				#��������츱���Լ�������ģʽ
RELATION_STATIC_TONG_CITY_WAR					= 4				#����ս����ģʽ
RELATION_STATIC_YXLM							= 5				#Ӣ�����˸���ģʽ
RELATION_STATIC_YI_JIE_ZHAN_CHANG				= 6				#���ս������ģʽ
RELATION_STATIC_TONG_CITY_WAR_FINAL				= 7				#����ս��������ģʽ



#��̬����ʱ����ϵģʽ���Ͷ���
RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID			= 1				#��̬�����ж�ID��ϵ
RELATION_DYNAMIC_PRESONAL_FRIEND_ID				= 2				#��̬�����Ѻ�ID��ϵ
RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_DBID		= 3				#��̬�����ж�DBID��ϵ
RELATION_DYNAMIC_PRESONAL_FRIEND_DBID			= 4				#��̬�����Ѻ�DBID��ϵ
RELATION_DYNAMIC_TEAM_ANTAGONIZE				= 5				#��̬�жԶ����ϵ
RELATION_DYNAMIC_TEAM_FRIEND					= 6				#��̬�Ѻö����ϵ
RELATION_DYNAMIC_TONG_ANTAGONIZE				= 7				#��̬�ж԰���ϵ
RELATION_DYNAMIC_TONG_FRIEND					= 8				#��̬�Ѻð���ϵ
RELATION_DYNAMIC_COMBAT_CAMP_ANTAGONIZE			= 9				#��̬�ж�ս����Ӫ��ϵ
RELATION_DYNAMIC_COMBAT_CAMP_FRIEND				= 10			#��̬�Ѻ�ս����Ӫ��ϵ

#ģ����ʾ����
VISIBLE_RULE_BY_PLANEID			= 1 #λ��ID
VISIBLE_RULE_BY_FLAG			= 2	#��ʶλ
VISIBLE_RULE_BY_FLASH			= 3 #����
VISIBLE_RULE_BY_TEL_AND_TEST	= 4	#����״̬�Ͳ���״̬
VISIBLE_RULE_BY_SHOW_SELF		= 5 #��ʾ�Լ����Լ��
VISIBLE_RULE_BY_SETTING_1		= 6 #Role�û�����
VISIBLE_RULE_BY_SETTING_2		= 7 #pet�û�����
VISIBLE_RULE_BY_WATCH			= 8 #�۲���ģ��
VISIBLE_RULE_BY_PROWL_1			= 9 #PlayerRole,ownPetǱ��ģʽ
VISIBLE_RULE_BY_PROWL_2			= 10 #RoleǱ��ģʽ
VISIBLE_RULE_BY_PROWL_3			= 11 #petǱ��ģʽ

#�ռ���ҹ���
FIND_SPACE_ITEM_FOR_COMMON_COPYS		= 1		
FIND_SPACE_ITEM_FOR_BIG_MAP				= 2	
FIND_SPACE_ITEM_FOR_COPY_TEMP			= 3
FIND_SPACE_ITEM_FOR_DANCE_HALL			= 4
FIND_SPACE_ITEM_FOR_MULTILINE			= 5
FIND_SPACE_ITEM_FOR_PLANES				= 6

