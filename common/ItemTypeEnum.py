# -*- coding: gb18030 -*-

# $Id: ItemTypeEnum.py,v 1.61 2008-08-30 02:41:24 yangkai Exp $

"""
�������ͺ�װ��λ�ó�������
	- CEL_*��װ��λ�ã�װ��ר�ã�
	- CEM_*����װ��ְҵ����ʾ��������Щְҵ��װ����ְҵ���Ϳ�����ϣ�
	- CKT_*���������ͣ�
	- CFE_*�����ߵ�������־��

"""

import Language
import cschannel_msgs
import ShareTexts as ST
# ��Ʒ����( Item Sub Type )
ITEM_UNKOWN							= 0x000000	# δ֪
ITEM_WEAPON							= 0x010000	# ��������
ITEM_ARMOR							= 0x020000	# ���ߵ���
ITEM_ORNAMENT						= 0x030000	# ���ε���
ITEM_PROPERTY						= 0x040000	# ���Ե���
ITEM_VOUCHER						= 0x050000	# ƾ֤����
ITEM_SYSTEM							= 0x060000	# ϵͳ����
ITEM_WAREHOUSE						= 0x070000	# �ֿ����
ITEM_PRODUCE						= 0x080000	# ��������
ITEM_NPC							= 0x090000	# NPC����
ITEM_NORMAL							= 0x100000	# ��ͨ����
ITEM_MONEY							= 0xff0000	# ��Ǯ

ITEM_WEAPON_AXE1					= 0x010101	# ���ָ�
ITEM_WEAPON_SWORD1					= 0x010102	# ���ֽ�
ITEM_WEAPON_HAMMER1					= 0x010103	# ���ִ�
ITEM_WEAPON_SPEAR1					= 0x010104	# ����ì
ITEM_WEAPON_DAGGER					= 0x010105	# ذ��

ITEM_WEAPON_AXE2					= 0x010201	# ˫�ָ�
ITEM_WEAPON_SWORD2					= 0x010202	# ˫�ֽ�
ITEM_WEAPON_HAMMER2					= 0x010203	# ˫�ִ�
ITEM_WEAPON_SPEAR2					= 0x010204	# ˫��ì
ITEM_WEAPON_TWOSWORD				= 0x010205	# ˫�ֽ�

ITEM_WEAPON_LONGBOW					= 0x010301	# ����
ITEM_WEAPON_SHORTBOW				= 0x010302	# �̹�

ITEM_WEAPON_STAFF					= 0x010401	# ����


ITEM_WEAPON_TRUMP					= 0x010502	# ����

ITEM_ARMOR_HEAD						= 0x020100	# ñ��
ITEM_ARMOR_BODY						= 0x020200	# �·�
ITEM_ARMOR_HAUNCH					= 0x020300	# ����
ITEM_ARMOR_CUFF						= 0x020400	# ����
ITEM_ARMOR_VOLA						= 0x020500	# ����
ITEM_ARMOR_BREECH					= 0x020600	# ����
ITEM_ARMOR_FEET						= 0x020700	# Ь��
ITEM_WEAPON_SHIELD					= 0x020800	# ����

ITEM_ORNAMENT_NECKLACE				= 0x030101	# ����
ITEM_ORNAMENT_RING					= 0x030201	# ��ָ
ITEM_ORNAMENT_ACMENT				= 0x030301	# ��Ʒ

ITEM_PROPERTY_MEDICINE				= 0x040101	# ҩˮ
ITEM_PROPERTY_FOOD					= 0x040102	# ʳ��
ITEM_PROPERTY_DRUG					= 0x040103	# ��ҩ
ITEM_PROPERTY_CHARM					= 0x040201	# ����
ITEM_PROPERTY_COUP					= 0x040202	# ����

ITEM_VOUCHER_ITEM					= 0x050101	# ƾ֤����
ITEM_VOUCHER_QUEST					= 0x050201	# ����ƾ֤

ITEM_SYSTEM_FUNC					= 0x060101	# ϵͳ���ܵ���
ITEM_SYSTEM_KASTONE					= 0x060201	# ����ʯ
ITEM_SYSTEM_TALISMAN				= 0x060301	# ����
ITEM_SYSTEM_VEHICLE					= 0x060501	# ���
ITEM_SYSTEM_VEHICLE_SADDLE			= 0x060502	# ���װ����
ITEM_SYSTEM_VEHICLE_HALTER			= 0x060503	# ���װ����ͷ
ITEM_SYSTEM_VEHICLE_NECKLACE		= 0x060504	# ���װ������
ITEM_SYSTEM_VEHICLE_CLAW			= 0x060505	# ���װ��צ��
ITEM_SYSTEM_VEHICLE_MANTLE			= 0x060506	# ���װ������
ITEM_SYSTEM_VEHICLE_BREASTPLATE		= 0x060507	# ���װ������

### �������װ�� ��ʼ ###
ITEM_SYSTEM_FLYING_VEHICLE_SADDLE	= 0x060508	# �������װ����
ITEM_SYSTEM_FLYING_VEHICLE_HALTER	= 0x060509	# �������װ����ͷ
ITEM_SYSTEM_FLYING_VEHICLE_NECKLACE	= 0x060510	# �������װ������
ITEM_SYSTEM_FLYING_VEHICLE_CLAW		= 0x06051A	# �������װ��צ��
ITEM_SYSTEM_FLYING_VEHICLE_MANTLE	= 0x06051B	# �������װ������
ITEM_SYSTEM_FLYING_VEHICLE_BREASTPLATE	= 0x06051C	# �������װ������
### �������װ�� ���� ###

ITEM_SYSTEM_GODSTONE				= 0x060601	# ���ʯ

ITEM_WAREHOUSE_KITBAG				= 0x070101	# ����
ITEM_WAREHOUSE_EQUIP				= 0x070201	# װ����
ITEM_WAREHOUSE_CASKET				= 0x070301	# �챦

ITEM_PRODUCE_STUFF					= 0x080101	# �������
ITEM_QUEST_STUFF					= 0x080201	# �������
ITEM_PRODUCE_JEWELRY				= 0x080301	# ��ʯ
ITEM_EQUIPMAKE_SCROLL				= 0x080401	# ������
ITEM_STILETTO  						= 0x080501	# ����

ITEM_NORMAL_SUNDRIES				= 0x100101	# ����
ITEM_SUPER_DRUG_HP					= 0x110102	# ��ҳ�����ҩ
ITEM_PET_BOOK						= 0x110103	# ���＼����

ITEM_DRUG_ROLE_HP					= 0x110104	# ��ɫ��ͨ��Ѫҩ 1114372
ITEM_DRUG_ROLE_MP					= 0x110105	# ��ɫ��ͨ����ҩ 1114373
ITEM_DRUG_PET_HP					= 0x110106	# ������ͨ��Ѫҩ 1114374
ITEM_DRUG_PET_MP					= 0x110107	# ������ͨ����ҩ 1114375
ITEM_YAO_DING						= 0x110108	# ��ҩ��		 1114376

ITEM_YIN_PIAO						= 0x110109	# Ԫ��Ʊ		 1114377
ITEM_PET_SUPER_DRUG_HP				= 0x11010a	# ���ﳬ����Ѫҩ		 1114378
ITEM_PET_SUPER_DRUG_MP				= 0x11010b	# ���ﳬ������ҩ		 1114379
ITEM_SUPER_DRUG_MP					= 0x11010c	# ��ҳ�����ҩ		 1114380
ITEM_PET_PROPERTY_CHARM				= 0x11010d  # �������   1114381
ITEM_PET_ITEM						= 0x11010e  # �������   1114382
ITEM_ANIMAL_TRAPS					= 0x11010f	# ������     1114383
ITEM_PET_EGG						= 0x110114	# ���ﵰ     1114388

ITEM_FASHION1						= 0x110110	# ʱװ1
ITEM_FASHION2						= 0x110111	# ʱװ2
ITEM_TREASUREMAP					= 0x110112	# �ر�ͼ
ITEM_POTENTIAL_BOOK				= 0x110113	# Ǳ����

ITEM_EXPERIMENT_PINHOLE				= 0x4c63ebd # ʵ����� 80101053
ITEM_GREENCRYSTAL					= 0x4c63eac # ��ˮ�� 80101036

ITEM_VEHICLE_BOOK					= 0x4c63ead	# ��輼���� 80101037

ITEM_NATURE_JADE					= 0x4c63eae	# �컯���
ITEM_VEHICLE_FD					        = 0x4c63eaf	# ιʳ���� 80101039
ITEM_VEHICLE_TURN					= 0x4c63eb0	#�������Ʒ80101040

# -------------------------------------------------
# ��Ʒװ����λ�ö���
# -------------------------------------------------
# Equit location(UINT8)��װ�����ĸ���λ
CEL_HEAD					= 0		# ͷ
CEL_NECK					= 1		# ��
CEL_BODY					= 2		# ����
CEL_BREECH					= 3		# �Ȳ�
CEL_VOLA					= 4		# ����
CEL_HAUNCH					= 5		# ����
CEL_CUFF					= 6		# ��
CEL_LEFTHAND				= 7		# ����
CEL_RIGHTHAND				= 8		# ����
CEL_FEET					= 9		# ��
CEL_LEFTFINGER				= 10	# ����ָ
CEL_RIGHTFINGER				= 11	# ����ָ
CEL_CIMELIA					= 12	# ����ʯ
CEL_TALISMAN				= 13	# ����
CEL_FASHION1                = 14	# ʱװ1
CEL_POTENTIAL_BOOK                = 15	# Ǳ������

CEL_MAX						= 16	# ��ʾ��CEL_*����ֵ������
# wield Type(UINT8)��װ����װ�����ͣ�����װ������λ��(CEL_*)��ӳ���ϵ
CWT_HEAD					= 0		# ͷ     ���� ͷ��
CWT_NECK					= 1		# ��     ���� ����
CWT_BODY					= 2		# ����   ���� ���
CWT_BREECH					= 3		# �β�   ���� ����
CWT_VOLA					= 4		# ��     ���� ����
CWT_HAUNCH					= 5		# ��     ���� ����
CWT_CUFF					= 6		# ��     ���� ����
CWT_LEFTHAND				= 7		# ����   ���� ����
CWT_RIGHTHAND				= 8		# ����   ���� ����
CWT_FEET					= 9		# ��     ���� Ь��
CWT_LEFTFINGER				= 10	# ����ָ ���� ��ָ
CWT_RIGHTFINGER				= 11	# ����ָ ���� ��ָ
CWT_CIMELIA					= 12	# ����ʯ
CWT_TALISMAN				= 13	# ����
CWT_TWOHAND					= 14	# ��Ҫ˫��һ���յ�����
CWT_HANDS					= 15	# ���ֻ����ֿ�������װ��(ֻѡ��һ)
CWT_TWOFINGER				= 16	# ��Ҫ������ָһ��װ��
CWT_FINGERS					= 17	# ����ָ������ָ��������װ��
CWT_RIGHTORTWO				= 18	# ���ֻ�˫����(����û��Ʒ��ʱ��������,��������Ʒ��ʱ��������)
CWT_FASHION1                = 19	# ʱװ1
CWT_FASHION2                = 20	# ʱװ2

# -----------------------------------------------------
# ��ɫ���岿λ����Ӧװ����ӳ�伯��
m_cwt2cist = {
		CWT_HEAD        : ( ITEM_ARMOR_HEAD, ),
		CWT_NECK        : ( ITEM_ORNAMENT_NECKLACE, ),
		CWT_BODY        : ( ITEM_ARMOR_BODY, ),
		CWT_BREECH     	: ( ITEM_ARMOR_BREECH, ),
		CWT_VOLA        : ( ITEM_ARMOR_VOLA, ),
		CWT_HAUNCH		: ( ITEM_ARMOR_HAUNCH, ),
		CWT_CUFF		: ( ITEM_ARMOR_CUFF, ),
		CWT_LEFTHAND    : ( ITEM_WEAPON_SHIELD, ITEM_WEAPON_TRUMP, ),
		CWT_RIGHTHAND   : ( ITEM_WEAPON_TWOSWORD, ITEM_WEAPON_AXE1, ITEM_WEAPON_SWORD1, ITEM_WEAPON_HAMMER1, ITEM_WEAPON_SPEAR1, ITEM_WEAPON_DAGGER, ),
		CWT_FEET        : ( ITEM_ARMOR_FEET, ),
		CWT_LEFTFINGER  : ( ITEM_ORNAMENT_RING, ),
		CWT_RIGHTFINGER : ( ITEM_ORNAMENT_RING, ),
		CWT_TWOFINGER	: ( ITEM_ORNAMENT_RING, ),
		CWT_FINGERS		: ( ITEM_ORNAMENT_RING, ),
		CWT_TWOHAND     : ( ITEM_WEAPON_AXE2, ITEM_WEAPON_SWORD2, ITEM_WEAPON_HAMMER2, ITEM_WEAPON_SPEAR2, ITEM_WEAPON_LONGBOW, ITEM_WEAPON_SHORTBOW, ITEM_WEAPON_STAFF, ),
		CWT_FINGERS     : ( ITEM_ORNAMENT_RING, ),
		CWT_CIMELIA		: ( ITEM_SYSTEM_KASTONE, ),
		CWT_TALISMAN	: ( ITEM_SYSTEM_TALISMAN, ),
		CWT_FASHION1	: ( ITEM_FASHION1, ),
		CWT_FASHION2	: ( ITEM_FASHION2, ITEM_POTENTIAL_BOOK ),
	}

# -------------------------------------------------
# �������϶���
# -------------------------------------------------
WEAPON_LIST = set( [
		ITEM_WEAPON_AXE1,
		ITEM_WEAPON_SWORD1,
		ITEM_WEAPON_HAMMER1,
		ITEM_WEAPON_SPEAR1,
		ITEM_WEAPON_DAGGER,
		ITEM_WEAPON_AXE2,
		ITEM_WEAPON_SWORD2,
		ITEM_WEAPON_HAMMER2,
		ITEM_WEAPON_SPEAR2,
		ITEM_WEAPON_LONGBOW,
		ITEM_WEAPON_SHORTBOW,
		ITEM_WEAPON_STAFF,
		ITEM_WEAPON_TRUMP,
		ITEM_WEAPON_TWOSWORD
				] )

WEAPONNAME_DIC = {
		ITEM_WEAPON_AXE1	: cschannel_msgs.ITEM_AXE1_DES,
		ITEM_WEAPON_SWORD1	: cschannel_msgs.ITEM_SWORD1_DES,
		ITEM_WEAPON_HAMMER1	: cschannel_msgs.ITEM_HAMMER1_DES,
		ITEM_WEAPON_SPEAR1	: cschannel_msgs.ITEM_SPEAR1_DES,
		ITEM_WEAPON_DAGGER	: cschannel_msgs.ITEM_DAGGER_DES,
		ITEM_WEAPON_AXE2	: cschannel_msgs.ITEM_AXE1_DES,
		ITEM_WEAPON_SWORD2	: cschannel_msgs.ITEM_SWORD1_DES,
		ITEM_WEAPON_HAMMER2	: cschannel_msgs.ITEM_HAMMER1_DES,
		ITEM_WEAPON_SPEAR2	: cschannel_msgs.ITEM_SPEAR1_DES,
		ITEM_WEAPON_LONGBOW	: cschannel_msgs.ITEM_BOW1_DES,
		ITEM_WEAPON_SHORTBOW: cschannel_msgs.ITEM_BOW1_DES,
		ITEM_WEAPON_STAFF	: cschannel_msgs.ITEM_STAFF_DES,
		ITEM_WEAPON_TRUMP	: cschannel_msgs.ITEM_TRUMP_DES,
		ITEM_WEAPON_TWOSWORD: cschannel_msgs.ITEM_SWORD1_DES,
				}

# -------------------------------------------------
# ���߼��϶���
# -------------------------------------------------
ARMOR_LIST = [
		ITEM_ARMOR_HEAD,
		ITEM_ARMOR_BODY,
		ITEM_ARMOR_HAUNCH,
		ITEM_ARMOR_CUFF,
		ITEM_ARMOR_VOLA,
		ITEM_ARMOR_BREECH,
		ITEM_ARMOR_FEET,
		ITEM_WEAPON_SHIELD,
				]

# -------------------------------------------------
# ��װ���߼�����
# -------------------------------------------------
ARMOR_SUIT = [
		ITEM_ARMOR_HEAD,
		ITEM_ARMOR_BODY,
		ITEM_ARMOR_BREECH,
		ITEM_ARMOR_VOLA,
		ITEM_ARMOR_HAUNCH,
		ITEM_ARMOR_CUFF,
		ITEM_ARMOR_FEET,
				]
# -------------------------------------------------
# �������϶���
# -------------------------------------------------
KITBAG_LIST = [
		ITEM_WAREHOUSE_KITBAG,		# ����
		ITEM_WAREHOUSE_CASKET,		# ���ϻ
		]

# -------------------------------------------------
# ���μ��϶���
# -------------------------------------------------
ORNAMENT_LIST = [
		ITEM_ORNAMENT_NECKLACE,		# ����
		ITEM_ORNAMENT_RING,			# ��ָ
		ITEM_ORNAMENT_ACMENT,		# ��Ʒ
		]

# -------------------------------------------------
# ������װ����Ʒ
# -------------------------------------------------
OTHEREQUIPITEM_LIST = [
		ITEM_SYSTEM_KASTONE,				# ����ʯ
		ITEM_SYSTEM_TALISMAN,				# ����
		ITEM_FASHION1,						# ʱװ1
		ITEM_FASHION2,						# ʱװ2
		ITEM_POTENTIAL_BOOK,				# Ǳ����
	]
# -------------------------------------------------
# װ�����϶���
# -------------------------------------------------
EQUIP_TYPE_SET = set( list( WEAPON_LIST ) + ARMOR_LIST + ORNAMENT_LIST + OTHEREQUIPITEM_LIST )

# -------------------------------------------------
# ���װ�����϶���
# -------------------------------------------------
VEHICLE_EQUIP_LIST = [
		ITEM_SYSTEM_VEHICLE_SADDLE	,		# ���װ����
		ITEM_SYSTEM_VEHICLE_HALTER	,		# ���װ����ͷ
		ITEM_SYSTEM_VEHICLE_NECKLACE,		# ���װ������
		ITEM_SYSTEM_VEHICLE_CLAW,			# ���װ��צ��
		ITEM_SYSTEM_VEHICLE_MANTLE,			# ���װ������
		ITEM_SYSTEM_VEHICLE_BREASTPLATE,	# ���װ������
	]

# -------------------------------------------------
# �������װ�����϶���
# -------------------------------------------------
FLYING_VEHICLE_EQUIP_LIST = [
		ITEM_SYSTEM_FLYING_VEHICLE_SADDLE,		# �������װ����
		ITEM_SYSTEM_FLYING_VEHICLE_HALTER,		# �������װ����ͷ
		ITEM_SYSTEM_FLYING_VEHICLE_NECKLACE,	# �������װ������
		ITEM_SYSTEM_FLYING_VEHICLE_CLAW,		# �������װ��צ��
		ITEM_SYSTEM_FLYING_VEHICLE_MANTLE,		# �������װ������
		ITEM_SYSTEM_FLYING_VEHICLE_BREASTPLATE,	# �������װ������
	]

# -------------------------------------------------
# ��һָ�Ʒ���϶���
# -------------------------------------------------
ROLE_DRUG_LIST = [
		ITEM_DRUG_ROLE_HP, 			# �����ͨ��Ѫҩ
		ITEM_DRUG_ROLE_MP,			# �����ͨ����ҩ
		ITEM_SUPER_DRUG_HP, 		# ��ҳ�����Ѫҩ
		ITEM_SUPER_DRUG_MP,			# ��ҳ�������ҩ
		ITEM_PROPERTY_MEDICINE,		# ҩˮ
	]

# -------------------------------------------------
# ��������Ʒ���϶���
# -------------------------------------------------
PET_DRUG_LIST = [
        ITEM_DRUG_PET_HP, 			# ������ͨ��Ѫҩ
        ITEM_DRUG_PET_MP,			# ������ͨ����ҩ
        ITEM_PET_PROPERTY_CHARM, 	# �������
        ITEM_PET_SUPER_DRUG_HP,		# ���ﳬ����Ѫҩ
        ITEM_PET_SUPER_DRUG_MP,     # ���ﳬ������ҩ
	]

# -------------------------------------------------
# ��Ʒ���ʱ�����Ͷ���
# -------------------------------------------------
CLTT_NONE					= 0		# ����ʱ
CLTT_ON_GET					= 1		# ��ȡ���ʱ,ʱ�䵽��ʧ
CLTT_ON_WIELD				= 2		# װ�����ʱ,ʱ�䵽��ʧ
CLTT_ON_OFFLINE				= 3		# ���ߺ��ʱ,ʱ�䵽��ʧ
CLTT_ON_GET_EVER			= 4		# ��ȡ���ʱ,ʱ�䵽����ʧ
CLTT_ON_WIELD_EVER			= 5		# װ�����ʱ,ʱ�䵽����ʧ
CLTT_ON_OFFLINE_EVER		= 6		# ���ߺ��ʱ,ʱ�䵽����ʧ

# -------------------------------------------------
# ��Ʒ��־����
# -------------------------------------------------
# ����������־(UINT16)��ʹ��λ����ʾ��
# ��ĳλΪ1ʱ��ʾ��֮��Ӧ�Ĺ���ΪTrue����֮��False
# CFE == const flag enum
CFE_NONE					= 0		#
CFE_NO_DESTROY				= 1		# ��������
CFE_NO_SELL					= 2		# ���ɳ���( �Ƿ�������NPC )
CFE_NO_REPAIR				= 3		# ��������( װ��ר��,ǿ���ԵĲ������޸� )
CFE_NO_WAREHOUSE			= 4		# ���ɴ洢( ���������ֿ� )
CFE_NO_INTENSIFY			= 5		# ����ǿ��
CFE_NO_REBUILD				= 6		# ���ɸ���
CFE_NO_STILETTO				= 7		# ���ɴ��
CFE_NO_ABRASION				= 8		# ����ĥ��
CFE_NO_PICKUP				= 9		# ����ʰȡ

CFE_NO_WASTAGE				= 11	# ��������(ʹ�ú��Ƿ�����)
CFE_NO_TRADE				= 12	# ���ɽ���
CFE_DIE_DROP				= 13	# ��������
CFE_FLYING_ONLY				= 14	# �����������ʹ��


# -------------------------------------------------
# ��Ʒǰ׺����
# -------------------------------------------------
CPT_NONE					= 0		# ��ǰ׺
CPT_NORMAL					= 1		# ��ͨ��
CPT_APPLIED					= 2		# ʵ�õ�
CPT_INTENSIFY				= 3		# ǿ����
CPT_EXCELLENT				= 4		# ������
CPT_COSTFULL				= 5		# ����
CPT_FABULOUS				= 6		# ��˵��
CPT_MYTHIC					= 7		# �񻰵�
CPT_MYGOD					= 8		# �����

# �����𡢷�װ���ܳ��ֵ�ǰ׺
CPT_NO_GREEN = [ CPT_NORMAL, CPT_INTENSIFY, CPT_COSTFULL ]
# ��װ���ܳ��ֵ�ǰ׺
CPT_GREEN = [ CPT_FABULOUS, CPT_MYTHIC, CPT_MYGOD ]
# ���п��ܳ��ֵ�ǰ׺
CPT_ALL = [ CPT_NORMAL, CPT_INTENSIFY, CPT_COSTFULL, CPT_FABULOUS, CPT_MYTHIC, CPT_MYGOD ]

# -------------------------------------------------
# ��ƷƷ�ʶ���
# -------------------------------------------------
CQT_WHITE					= 1		# ��ɫ
CQT_BLUE					= 2		# ��ɫ
CQT_GOLD					= 3		# ��ɫ
CQT_PINK					= 4		# ��ɫ
CQT_GREEN					= 5		# ��ɫ

# -------------------------------------------------
# ��Ʒ�����Ͷ���
# -------------------------------------------------
CBT_NONE					= 0		# δ��
CBT_PICKUP					= 1		# ʰȡ���
CBT_EQUIP					= 2		# װ�����
CBT_HAND					= 3		# �ֶ���
CBT_QUEST 					= 4		# �����
CBT_COUNT 					= 5		# ����������

# -------------------------------------------------
# ��Ʒ�������Ͷ��� by jiangyi
# -------------------------------------------------
COB_NONE					= 0		# δ����
COB_OBEY					= 1		# ������

# -------------------------------------------------
# ���װ����λ�ö���
# -------------------------------------------------
VEHICLE_CEL_HALTER			= 0		# ��ͷ
VEHICLE_CEL_SADDLE			= 1		# ��
VEHICLE_CEL_NECKLACE		= 2		# ����
VEHICLE_CEL_CLAW			= 3		# צ��
VEHICLE_CEL_MANTLE			= 4		# ����
VEHICLE_CEL_BREASTPLATE		= 5		# ����

# -------------------------------------------------
# ���װ�����Ͷ���
# -------------------------------------------------
VEHICLE_CWT_HALTER			= 0		# ��ͷ
VEHICLE_CWT_SADDLE			= 1		# ��
VEHICLE_CWT_NECKLACE		= 2		# ����
VEHICLE_CWT_CLAW			= 3		# צ��
VEHICLE_CWT_MANTLE			= 4		# ����
VEHICLE_CWT_BREASTPLATE		= 5		# ����

# -------------------------------------------------
# ����Ʒ������
# -------------------------------------------------
TALISMAN_COMMON				= 0		# ��Ʒ
TALISMAN_IMMORTAL			= 1		# ��Ʒ
TALISMAN_DEITY				= 2		# ��Ʒ

# -------------------------------------------------
# ��Ʒ��ȡ��ʽ����
# -------------------------------------------------
ITEM_GET_GM					= 0		# Ĭ��
ITEM_GET_PICK				= 1		# �������
ITEM_GET_CARD				= 2		# ������
ITEM_GET_NPCTRADE			= 3		# NPC����
ITEM_GET_SHOP				= 4		# �̳�
ITEM_GET_PTRADE				= 5		# ���֮�佻��
ITEM_GET_QUEST				= 6		# ������
ITEM_GET_STROE				= 7		# ������
ITEM_GET_NPCGIVE			= 8		# NPC�����
ITEM_GET_EQUIP_INSTENSIFY	= 9		# װ��ǿ����һ���ȼ�
ITEM_GET_STUD				= 10	# ��Ƕһ���ȼ�ˮ��

# -------------------------------------------------
# ����׳���
# -------------------------------------------------
ITEM_CHILD_VEHICLE			= [ 60501047, 60501046, 60501045 ]

#---------------------------------------------------------------------
# ��Ʒʰȡ���� by ����
#---------------------------------------------------------------------
PICK_UP_TYPE_DEFAULT = 10000						# Ĭ��ʰȡ�ࣺ����
PICK_UP_TYPE_QUALITY_AREA = xrange( 20000, 29999 )		# ��Ҫ��ƷƷ�ʵ���������

# -------------------------------------------------
# װ�����������
# -------------------------------------------------
EQUIP_EFFECT_TYPE_ADD		= 1		# ��ֵ
EQUIP_EFFECT_TYPE_PER		= 2		# �ӳ�


# -------------------------------------------------
# װ���������Ͷ���
# -------------------------------------------------
EQUIP_NORMAL_ATTR = 1 #һ������
EQUIP_MIDDLE_ATTR = 2 #��������
EQUIP_TOP_ATTR    = 3 #�߼�����


# -------------------------------------------------
# װ��Ʒ�ʾ���������Ŀ����
# -------------------------------------------------
EQUIP_ATTR_NUM_MAPS = { CQT_WHITE : 0,
			CQT_BLUE  : 2,		
			CQT_GOLD  : 3,		# ��ɫ
			CQT_PINK  : 4,		# ��ɫ
			CQT_GREEN : 5		# ��ɫ
			}

#��Ҫ�Ŵ����õ����Ա���
EQUIP_ATTR_MAGNIFY_RATE = {30014:1000.0,30015:1000.0,30016:1000.0,30017:1000.0,}

# -------------------------------------------------
# ��Һͳ��ﲹѪҩƷ����
# -------------------------------------------------
ROLE_DRUG_HP_LIST = [
        ITEM_SUPER_DRUG_HP, 		# ��ҳ�����Ѫҩ
        ITEM_DRUG_ROLE_HP,			# �����ͨ��Ѫҩ
        ITEM_PROPERTY_MEDICINE, 	# ҩˮ
        ITEM_PROPERTY_FOOD,			# ʳ��
        ITEM_PET_SUPER_DRUG_HP,		# ���ﳬ����Ѫҩ
        ITEM_DRUG_PET_HP,			# ������ͨ��Ѫҩ
	]
