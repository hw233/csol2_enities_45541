# -*- coding: gb18030 -*-

# $Id: csconst.py,v 1.82 2008-09-02 10:30:06 fangpengjun Exp $


"""
locates global constants of base/cell/client

2005.06.06 : tidied up by huangyongwei
"""

import Math
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csstatus
import ItemTypeEnum
import Language



# --------------------------------------------------------------------
# about login
# --------------------------------------------------------------------
LOGIN_ROLE_UPPER_LIMIT		= 3			# �����Դ������ٸ���ɫ( from L3Define.py��ԭ��: C_ACC_MAX_ROLE )


# --------------------------------------------------------------------
# about game status
# --------------------------------------------------------------------
SERVER_TIME_AMEND 			= 100.0		# ������ʱ��ת������ʱ������(ȡС�����λ*10)��100��ʾ��ȷ��С�����2λ������ҪС����������ȷ
										# * 100����ʹ����������240��������������� * 1000��ֻ��ʹ�÷���������24�졣
# --------------------------------------------------------------------
# about game float2int
# --------------------------------------------------------------------
#���������"FLOAT_ZIP_PERCENT"�������и��ģ���ͬ������DataTool�����
#������entities\plugins\ExportPY\convertFunctions_server.py������������Ԥ�����֡�
#������PS��convertFunctions_server.py�����"FLOAT_ZIP_PERCENT"���ɶ�λ  add by��qiulinhui
FLOAT_ZIP_PERCENT 			= 10000.0	# ��Ϸ�������ķŴ����

# --------------------------------------------------------------------
# about role's attributes
# --------------------------------------------------------------------
g_map_gender 				= { "GENDER_MALE" : csdefine.GENDER_MALE, "FAMALE" : csdefine.GENDER_FEMALE }		# ( ԭ����g_gender )
g_en_gender 				= { csdefine.GENDER_MALE : "male", csdefine.GENDER_FEMALE : "female" }				# ( ԭ����g_genderstr )
g_chs_gender 				= { csdefine.GENDER_MALE : cschannel_msgs.SEX_MAN, csdefine.GENDER_FEMALE : cschannel_msgs.SEX_WOMAN }				# ( ԭ����g_genderTally )

g_map_class = {																					# ( ԭ����g_metier )
		"CLASS_FIGHTER"			: csdefine.CLASS_FIGHTER,
		"CLASS_WARLOCK"			: csdefine.CLASS_WARLOCK,
		"CLASS_SWORDMAN"		: csdefine.CLASS_SWORDMAN,
		"CLASS_ARCHER"			: csdefine.CLASS_ARCHER,
		"CLASS_MAGE"			: csdefine.CLASS_MAGE,
		"CLASS_PRIEST"			: csdefine.CLASS_PRIEST,
		"CLASS_PALADIN"			: csdefine.CLASS_PALADIN,
		}

g_en_class = {														# ( ԭ����g_classstr )
		csdefine.CLASS_FIGHTER	: "fighter",
		csdefine.CLASS_WARLOCK	: "warlock",
		csdefine.CLASS_SWORDMAN	: "swordman",
		csdefine.CLASS_ARCHER	: "archer",
		csdefine.CLASS_MAGE		: "mage",
		csdefine.CLASS_PRIEST	: "priest",
		csdefine.CLASS_PALADIN	: "paladin",
		}

g_chs_class = {																					# ( ԭ����g_classTally )
		csdefine.CLASS_FIGHTER	: ST.PROFESSION_FIGHTER,
		csdefine.CLASS_WARLOCK	: ST.PROFESSION_WARLOCK,
		csdefine.CLASS_SWORDMAN	: ST.PROFESSION_SWORD,
		csdefine.CLASS_ARCHER	: ST.PROFESSION_ARCHER,
		csdefine.CLASS_MAGE		: ST.PROFESSION_MAGIC,
		csdefine.CLASS_PRIEST	: ST.PROFESSION_PRIEST,
		csdefine.CLASS_PALADIN	: ST.PROFESSION_FIGHTER,														# ��ʾ�ϻ���ʹ��սʿ
		}


g_maps_info = { "fengming":cschannel_msgs.MAP_FENG_MING, "zly_ban_quan_xiang":cschannel_msgs.MAP_BAN_QUAN, "zly_bi_shi_jian":cschannel_msgs.MAP_BI_SHI_SHAN_GU,"feng_ming_cheng":cschannel_msgs.MAP_FENGMINGCHENG,
 "zly_ying_ke_cun":cschannel_msgs.MAP_FEI_YUN_PO, "yun_meng_ze_01":cschannel_msgs.MAP_QING_FENG_YUAN, "yun_meng_ze_02":cschannel_msgs.MAP_WU_MIAO_ZHAO_ZE, "xin_ban_xin_shou_cun":cschannel_msgs.MAP_YIN_SHA_CHUN,
 "liu_wang_mu_001":cschannel_msgs.MAP_GWM_001, "liu_wang_mu_002":cschannel_msgs.MAP_GWM_002, "liu_wang_mu_003":cschannel_msgs.MAP_GWM_003,
 "liu_wang_mu_004":cschannel_msgs.MAP_GWM_004, "liu_wang_mu_005":cschannel_msgs.MAP_GWM_005, "liu_wang_mu_006":cschannel_msgs.MAP_GWM_006,
 "fu_ben_hun_dun_ru_qin":cschannel_msgs.MAP_ZHENG_ZHAN_GU, "fu_ben_dao_yu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "fu_ben_exp_melee":cschannel_msgs.MAP_ZHU_TIAN_SHENG_DI,
 "fu_ben_lin_di":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "fu_ben_ri_guang_yu":cschannel_msgs.MAP_RI_GUANG_YU, "fu_ben_shan_ding":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,
 "fu_ben_shan_gu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "fu_ben_shen_gui_mi_jing":cschannel_msgs.ACTIVITY_SHEN_GUI_MI_JING, "fu_ben_shi_di":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,
 "fu_ben_tian_guan_02":cschannel_msgs.MAP_TIAN_GUAN, "fu_ben_tian_jiang_qi_shou":cschannel_msgs.MAP_QI_HUAN_SHEN_SHOU, "fu_ben_wu_yao_qian_shao":cschannel_msgs.MAP_SHI_HU_SHAN,
 "fu_ben_wu_yao_wang_bao_zang":cschannel_msgs.MAP_YAO_YI_KONG_JIAN, "fu_ben_xuan_tian_huan_jie":cschannel_msgs.MAP_XUAN_TIAN_HUAN_JIE, "fu_ben_zu_dui_jing_ji_chang":cschannel_msgs.MAP_JING_JI_CHANG,
 "gumigong":cschannel_msgs.MAP_GU_MI_GONG, "shuijing":cschannel_msgs.MAP_SHUI_JING_JIE_JIE, "bao_hu_bang_pai":cschannel_msgs.TONG_INFO_24, "fu_ben_bang_hui_ling_di":cschannel_msgs.TONG_INFO_24, "peng_lai":cschannel_msgs.MAP_PENG_LAI, "xin_fei_lai_shi_001":cschannel_msgs.MAP_FEI_LAI_SHI,
 "fu_ben_long_qi_dong_01":cschannel_msgs.MAP_LONG_DONG_1_CENG, "fu_ben_long_qi_dong_02":cschannel_msgs.MAP_LONG_DONG_2_CENG,"fu_ben_ran_hun_shan_gu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "fu_ben_liu_sha_mi_cheng_001":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "fu_ben_feng_hua_jue_gu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,
 "fu_ben_li_hen_shan_lin_001":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,"fu_ben_wu_tai_001":cschannel_msgs.MAP_WU_TAI, "fu_ben_du_du_zhu":cschannel_msgs.MAP_LE_YUAN, "fu_ben_zheng_jiu_ya_yu":cschannel_msgs.MAP_SHEN_CANG_YU,"fu_ben_xie_long_dong_xue":cschannel_msgs.MAP_XIE_LONG_DONG_XUE,
 "sai_ma_chang_01":cschannel_msgs.MAP_SAI_MA_CHANG, "sai_ma_chang_03":cschannel_msgs.MAP_SAI_MA_CHANG, "fu_ben_jia_zu_jing_ji_chang":cschannel_msgs.MAP_JIA_ZU_JING_JI_CHANG, "wu_dao":cschannel_msgs.ACTIVITY_WU_DAO_DA_HUI,
 "fu_ben_ge_ren_jing_ji_chang":cschannel_msgs.MAP_GE_REN_JING_JI_CHANG, "city_war_a":cschannel_msgs.MAP_BANG_HUI_DUO_CHENG_A_FANG_JIAN, "city_war_b":cschannel_msgs.MAP_BANG_HUI_DUO_CHENG_B_FANG_JIAN, "city_war_c":cschannel_msgs.MAP_BANG_HUI_DUO_CHENG_C_FANG_JIAN,
 "city_war_d":cschannel_msgs.MAP_BANG_HUI_DUO_CHENG_D_FANG_JIAN, "city_war_e":cschannel_msgs.MAP_BANG_HUI_DUO_CHENG_E_FANG_JIAN, "fu_ben_npc_zheng_duo":cschannel_msgs.MAP_JIA_ZU_ZHAN_CHANG, "prison":cschannel_msgs.MAP_JIAN_YU, "fu_ben_tian_xiang_xue_ling":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,
 "fu_ben_feng_jian_shen_gong":cschannel_msgs.MAP_FENG_JIAN_SHEN_GONG, "fu_ben_she_hun_mi_zhen":cschannel_msgs.MAP_SHE_HUN_MI_ZHEN, "fu_ben_shi_tu_fu_ben":cschannel_msgs.MAP_SHI_TU_FU_BEN, "kun_lun":cschannel_msgs.MAP_KUN_LUN, "fu_ben_kuafu_remains":cschannel_msgs.MAP_KUAFU_REMAINS, "bao_hu_bang_pai_mid_autumn":cschannel_msgs.MID_ATUTMIN_COPY,
 "fu_ben_kua_fu_shen_dian_001":cschannel_msgs.MAP_KUAFU_REMAINS, "chu_yao_li_hen_shan_lin":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "chu_yao_lin_di":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "chu_yao_liu_sha_mi_cheng":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "chu_yao_ran_hun_shan_gu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,
 "chu_yao_shan_ding":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "chu_yao_shan_gu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "chu_yao_shi_di":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "chu_yao_tian_xiang_xue_ling":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "jiao_fei_dao_yu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN,
 "jiao_fei_lin_di":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "jiao_fei_shan_ding":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "jiao_fei_shan_gu":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, "jiao_fei_shi_di":cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN, }


# -----------------------------------------------------
ROLE_AOI_RADIUS				= 50.0				# ��� AOI ��Χ

ROLE_INIT_INTERVAL			= 0.1				# ��ʼ��������Ե��¼����( hyw -- 2008.06.09 )

ROLE_MODEL_WIDTH			= 0.4				# ��ʾ��ɫģ�����ĵ㵽�沿����BoundingBox�ľ���( from common/L3Define.py )
ROLE_MODEL_BOUND			= Math.Vector3( ( 0.6, 2.0, 0.4 ) )		# ����ͳһ��bounding boxֵ�������ߡ���

ROLE_MOVE_SPEED_BIAS   		= 0.2				# ���ڿͻ��˿��������ӳٵ����⣬��ֵ����Ҫ��һ���Ĵ�С����������׾ͻ����������������
												# ʵ��range = range + ROLE_MOVE_SPEED_BIAS( from common/L3Define.py )
ROLE_TOP_SPEED_Y			= 200				# Y ���ϵ���������

ROLE_MONEY_UPPER_LIMIT		= 4000000000		# ӵ�н�Ǯ������( from const/L3Define.py��ԭ����MONEY_MAX )

ROLE_TEACHCREDIT_UPPER_LIMIT	= 2000000000		# ��ҹ�ѫֵ����11:33 2008-8-21��wsf

ROLE_GOLD_UPPER_LIMIT		= 900000000			# ӵ�н�Ԫ��������
ROLE_SILVER_UPPER_LIMIT		= 900000000			# ӵ����Ԫ��������

ROLE_LEVEL_UPPER_LIMIT		= 110				# ��ҵȼ�����
PET_LEVEL_UPPER_LIMIT		= 110				# �������ȼ�����

PET_ELEMENT_DERATE_MAX = 8000				# ����Ԫ���˺��ֿ����� by ����

ROLE_POTENTIAL_UPPER		= 100000000			# ���Ǳ�ܵ�����15:38 2008-7-23��wsf
ROLE_EXP2POT_MULTIPLE		= 5					# ���黻Ǳ�ܵı���( 5���黻1Ǳ�� )

# -----------------------------------------------------
# ��������	( from cell/AttrDefine.py and base/attrDefine.py��designed by penghuawei )( ԭ����ROLE_HP_MAX_BASE )
ROLE_HP_MAX_RADIX = {
		csdefine.CLASS_FIGHTER	: 25,		# սʿ
		csdefine.CLASS_SWORDMAN	: 24,		# ����
		csdefine.CLASS_ARCHER	: 18,		# ����
		csdefine.CLASS_MAGE		: 15,		# ��ʦ
		csdefine.CLASS_WARLOCK	: 24,		# ��ʦ
		csdefine.CLASS_PRIEST	: 29,		# ��ʦ
		}

# �������� ( from cell/AttrDefine.py and base/attrDefine.py��designed by penghuawei )( ԭ����ROLE_MP_MAX_BASE )
ROLE_MP_MAX_RADIX = {
		csdefine.CLASS_FIGHTER	: 20,		# սʿ
		csdefine.CLASS_SWORDMAN	: 25,		# ����
		csdefine.CLASS_ARCHER	: 25,		# ����
		csdefine.CLASS_MAGE		: 40,		# ��ʦ
		csdefine.CLASS_WARLOCK	: 28,		# ��ʦ
		csdefine.CLASS_PRIEST	: 22,		# ��ʦ
		}

# -----------------------------------------------------
g_default_spawn_site = {												# Ĭ�ϳ�����( ԭ����g_default_spawn_position )
		csdefine.CLASS_FIGHTER	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 27.705, 177.35, -178.884 ), ( 0.0,0.0,3.117 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( 48.165,162.697,108.306 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_WARLOCK	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 27.705, 177.35, -178.884 ), ( 0.0,0.0,3.117 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( 48.166267,163.667674,132.199509 ), ( 0.000000,0.000000,0.027 ) ) },
		csdefine.CLASS_SWORDMAN	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 712.390, 510.721, 314.424 ), ( 0.0,0.0,0.0 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( -293.884,469.494,680.128 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_ARCHER	: { csdefine.ENTITY_CAMP_TAOISM : ( ( -56.242, 490.657, 198.985 ), ( 0.0,0.0,0.0 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( -41.139,505.648,126.596 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_MAGE		: { csdefine.ENTITY_CAMP_TAOISM : ( ( -502.165, 527.692, -481.557 ), ( 0.0,0.0,0.0 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( -780.981,459.612,325.481 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_PRIEST	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 27.705, 177.35, -178.884 ), ( 0.0,0.0,3.117 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( 48.166267,163.667674,132.199509 ), ( 0.000000,0.000000,0.027 ) ) },
		}

g_default_spawn_city = {												# Ĭ�ϳ�����( ԭ����g_default_spawn_city )
		csdefine.JIULI		: { csdefine.ENTITY_CAMP_TAOISM :{ csdefine.CLASS_FIGHTER: "zy_wa_huang_gong",
																csdefine.CLASS_SWORDMAN: "zy_wa_huang_gong",
																csdefine.CLASS_ARCHER: "zy_wa_huang_gong",
																csdefine.CLASS_MAGE: "zy_wa_huang_gong"
																},
								csdefine.ENTITY_CAMP_DEMON :{csdefine.CLASS_FIGHTER: "zy_xiu_luo_dian" ,
																csdefine.CLASS_SWORDMAN: "zy_xiu_luo_dian",
																csdefine.CLASS_ARCHER: "zy_xiu_luo_dian",
																csdefine.CLASS_MAGE: "zy_xiu_luo_dian"
																},
								},
		csdefine.YANHUANG	: { csdefine.ENTITY_CAMP_TAOISM :	{csdefine.CLASS_FIGHTER: "zy_wa_huang_gong",
																csdefine.CLASS_SWORDMAN: "zy_wa_huang_gong",
																csdefine.CLASS_ARCHER: "zy_wa_huang_gong",
																csdefine.CLASS_MAGE: "zy_wa_huang_gong"
																},
								csdefine.ENTITY_CAMP_DEMON :{csdefine.CLASS_FIGHTER: "zy_xiu_luo_dian",
																csdefine.CLASS_SWORDMAN: "zy_xiu_luo_dian",
																csdefine.CLASS_ARCHER: "zy_xiu_luo_dian",
																csdefine.CLASS_MAGE: "zy_xiu_luo_dian"
																},
								},
		csdefine.FENGMING	:  { csdefine.ENTITY_CAMP_TAOISM :{csdefine.CLASS_FIGHTER: "zy_wa_huang_gong",
																csdefine.CLASS_SWORDMAN: "zy_yu_xu_gong",
																csdefine.CLASS_ARCHER: "zy_bi_you_gong",
																csdefine.CLASS_MAGE: "zy_ba_jing_gong"
																},
								csdefine.ENTITY_CAMP_DEMON :{csdefine.CLASS_FIGHTER: "zy_xiu_luo_dian",
																csdefine.CLASS_SWORDMAN: "zy_lei_yin_si",
																csdefine.CLASS_ARCHER: "zy_wu_ji_dian",
																csdefine.CLASS_MAGE: "zy_huo_yun_gong"
																},
								},
					}
# --------------------------------------------------------------------
# about combat & skill
# --------------------------------------------------------------------
ATTACK_RANGE_BIAS				= 1.5		# ��ʾ���ڿͻ��˺ͷ�����EntityPosition��һ������Ĺ����������ƫ��( from common/L3Define.py )

MONSTER_CORPSE_DURATION			= 8.0		# ����������ʬ����ʧʱ�䣬��λ���룬float( from common/L3Define.py��ԭ����CORPSE_DELAY )

RESIST_MIN						= 0.0		# ���쳣״̬���Ե�����޶� by����
RESIST_LEVEL_MIN				= 8			# ���쳣״̬���Ե����޵ȼ� ���ڴ˼���һ�ɷ���1% by����

MOVE_TRAP_DELAY_DESTROY_TIME    = 5.0		# ���ƶ������ӳ�����ʱ��
# --------------------------------------------------------------------
# about communication between entites
# --------------------------------------------------------------------
COMMUNICATE_DISTANCE			= 6.0		# �� NPC ������������, ��λ: ��( from L3Define.py; ԭ����NPC_TASK_STATUS_SHOW_DISTANCE )

TRADE_ITEMS_UPPER_LIMIT			= 7			# ���֮��Ľ�����Ʒ�������ܳ��� 7 ��
TRADE_WAITING_TIME				= 15.0		# �������ȴ�ʱ��
TRADE_PRICE_UPPER_LIMIT			= 2000000000	# ������Ʒ�ļ۸�����(��Щ�ط��۸����������INT32��������ü۸񳬹�2147483647���ʹ�۸��Ϊ����)

COMMISSION_ITEMS_UPPER_LIMIT	= 10		# ��Ҽ�������Ʒ��������
COMMISSION_CHARGE_PERCENT		= 0.05		# ��Ҽ�������ռ���ۼ۸�ı���

# --------------------------------------------------------------------
# about pk system
# --------------------------------------------------------------------
PK_PROTECT_LEVEL				= 30		# 30������pk����
PK_GOODNESS_MAX_VALUE			= 100		# �ƶ�ֵ���ֵ
PK_MONEY_DROPRATE_MAX			= 0.45		# pk������Ǯ����������
PK_MONEY_DROPRATE_EXC			= 0.005		# ÿһ��pkֵ��������Ǯ����
PK_MONEY_DROPRATE				= 0.05		# �����̶������Ǯ����

PK_EQUIP_DROPRATE				= 20		# ��������װ������

# --------------------------------------------------------------------
# about talisman
# --------------------------------------------------------------------
TALISMAN_UPTO_IMMORTAL_LEVEL		= 50	# ������������Ʒ���Ƶȼ�
TALISMAN_UPTO_DEITY_LEVEL			= 100	# ������������Ʒ���Ƶȼ�
TALISMAN_ADD_LIFE_ITEM 				= 50101063		# ������ֵŮ�ʯ
TALISMAN_LEVELUP_MAP				= {
										ItemTypeEnum.TALISMAN_COMMON	: [TALISMAN_UPTO_IMMORTAL_LEVEL, csstatus.TALISMAN_LEVELUP_IMM, csstatus.TALISMAN_SKILL_LEVELUP_IMM],
										ItemTypeEnum.TALISMAN_IMMORTAL	: [TALISMAN_UPTO_DEITY_LEVEL, csstatus.TALISMAN_LEVELUP_DEI, csstatus.TALISMAN_SKILL_LEVELUP_DEI],
										ItemTypeEnum.TALISMAN_DEITY		: [150, csstatus.TALISMAN_TOP_LEVEL, csstatus.TALISMAN_SKILL_TOP_LEVEL],
										}	# ����������Ʒ�ʵĹ��� [�ȼ����ƣ�״̬��Ϣ��] by����


# ����ֵwsf��16:50 2008-7-17
HONOUR_UPPER_LIMIT				= 1000000	# ����ֵ����
HONOUR_LOWER_LIMIT				= -1000000	# ����ֵ����


# --------------------------------------------------------------------
# about inventory( from common/spaceConst.py��designed by huangyongwei )
# --------------------------------------------------------------------
pet_ch_hierarchies = {}
pet_ch_hierarchies[csdefine.PET_HIERARCHY_GROWNUP]		= cschannel_msgs.PET_CHENG_NIAN
pet_ch_hierarchies[csdefine.PET_HIERARCHY_INFANCY1]		= cschannel_msgs.PET_BAO_BAO
pet_ch_hierarchies[csdefine.PET_HIERARCHY_INFANCY2]		= cschannel_msgs.PET_ER_DAI_BAO_BAO

pet_ch_types = {}
pet_ch_types[csdefine.PET_TYPE_STRENGTH]				= cschannel_msgs.PET_TYPE_LI_LIANG
pet_ch_types[csdefine.PET_TYPE_SMART]					= cschannel_msgs.PET_TYPE_MI_JIE
pet_ch_types[csdefine.PET_TYPE_INTELLECT]				= cschannel_msgs.PET_TYPE_ZHI_LI
pet_ch_types[csdefine.PET_TYPE_BALANCED]				= cschannel_msgs.PET_TYPE_JUN_HENG

pet_ch_species = {}
for hierarchy, hch in pet_ch_hierarchies.iteritems() :
	for ptype, tch in pet_ch_types.iteritems() :
		pet_ch_species[hierarchy | ptype] = hch + "/" + tch

pet_enhance_stones = { \
	"strength"   : ( 60401001, 60401002, 60401003, 60401013 ),	# ��������ʯ
	"intellect"  : ( 60401004, 60401005, 60401006, 60401014 ),	# ��������ʯ
	"dexterity"  : ( 60401007, 60401008, 60401009, 60401015 ),	# ���ݻ���ʯ
	"corporeity" : ( 60401010, 60401011, 60401012, 60401016 ),	# ���ʻ���ʯ
	}															# ����ǿ������Ҫ�Ļ���ʯ

PET_SMELT_ITEMS			= [60201020, 60201105]									# ��������Ʒ ID
PET_DIRECT_ITEMS		= [60201021, 60201106]									# ǿ������Ʒ ID
PET_ADD_LIFE_ITEMS		= [60201004, 60201104]									# ���ٵ���Ʒ ID

pet_joyancy_items = ( \
	60201007,													# ��ɫ
	60201051,													# ��ɫ
	60201052,													# ��ɫ
	60201053,													# ��ɫ
	60201054,													# ��ɫ
	) 															# ������ID

# -------------------------------------------
PET_ROLE_COME_OUT_DISTANCE		= 3.0		# ����ո��ٻ�����ʱ����ҵľ���

PET_CATCH_OVER_LEVEL			= 5			# �����������Ҷ��ټ���Ͳ��ܲ�׽
PET_CONJURE_OVER_LEVEL			= 5			# �����������Ҷ��ټ��Ͳ��������

PET_LIFE_UPPER_LIMIT			= 60000		# ������������
PET_PROCREATE_MIN_LIFE			= 5000		# ���ﷱֳ�����������
PET_JOYANCY_UPPER_LIMIT			= 100		# ������ֶ�����
PET_PROCREATE_MIN_JOYANCY		= 90		# ���ﷱֳ������Ϳ��ֶ�
PET_FEED_EXP_GAP				= 5			# ����ι���ȼ���
PET_PROCREATE_FIND_TEAMMATE_RANGE	= 20		# ���ﷱֳ���ҷ�Χ�ڵĶ�Ա���ܶ���2��

PET_NAME_MAX_LENGTH				= 14		# �������ֵ���󳤶�

PET_PROCREATE_MIN_LEVEL			= 40		# �ɷ�ֳ�������С�ȼ�
PET_PROCREATE_LIFT_NEED			= 5000		# ���뷱ֳ�ĳ��������ֵ����
PET_PROCREATE_JOY_NEED			= 90		# ���뷱ֳ�ĳ�����ֶ�����
PET_PROCREATE_GAP_LEVEL			= 5			# ��ֳ����������ĵȼ����ܳ����弶
PET_PROPAGATE_KEEPING_TIME		= 48		# ���ﷱֳ����ڱ���Ա��������ʱ�䣨��λСʱ��
PET_FORCE_FOLLOW_RANGE			= 32.0		# �����뿪��Ҷ�Զ��ǿ�ȸ���
PET_PROCREATE_OVERDUE_TIME 		= 48 * 3600	# ���ﷱֳ����ʱ��
PET_PROCREATE_NEED_TIME 		= 1 * 3600	# ���ﷱֳ����ʱ��

# -------------------------------------------
# pet follow and fight
# -------------------------------------------
PET_ROLE_KEEP_DISTANCE				= 3.0			# ���������֮�䱣�ֵľ��루��λ���ף�
PET_FORCE_FOLLOW_RANGE				= 52.0			# �����뿪��Ҷ�Զ��ǿ�ȸ���
PET_ENMITY_RANGE					= 10.0			# ��Ѱ���ﷶΧ
PET_FORCE_TELEPORT_RANGE			= ROLE_AOI_RADIUS/1.2	# ����ǿ�ƴ��;���


# ���ÿһ�����＼�ܵĸ��ʣ����ԭ����1000����������һ������ȫ�츳���ܣ��������������츳���ܵ�
# ����Ϊ1/1000������ÿһ���츳���ܵĸ�����0.001 ** ( 1.0/�����츳���ܸ��� )
PET_HAS_ALL_INBORN_SKILL_RATE	= 0.001		# �����ܻ��ȫ�츳���ܵĸ���

pst_storeCount = {}
pst_storeCount[csdefine.PET_STORE_TYPE_LARGE]	= 10		# ��ֿ��������洢����
pst_storeCount[csdefine.PET_STORE_TYPE_SMALL]	= 5			# С�ֿ��������洢����
PST_HOLD_DAYS					= 15 						# �ֿ����������


# --------------------------------------------------------------------
# about inventory( from common/spaceConst.py��designed by huangyongwei )
# --------------------------------------------------------------------
IV_MONEY_UPPER_LIMIT			= 0x7FFFFFFF	# �ֿ�����ܴ����Ǯ
IV_PAGES_COUNT					= 3				# �ֿ�ҳ��
IV_PAGE_ITEMS_COUNT				= 48			# ÿҳ������


# --------------------------------------------------------------------
# about quickbar( from common/L3Define.py��designed by huangyw )
# --------------------------------------------------------------------
QB_ITEMS_COUNT				= 750			# ��������ռ�


QB_PET_ITEM_COUNT			= 5				# �����ݸ����

# --------------------------------------------------------------------
# about space( from common/spaceConst.py��designed by panguankong )
# --------------------------------------------------------------------
SPACE_SPACEDATA_KEY						= 256							# Space define, must big than 255( from L3Define.py��ԭ����KEY_SPACEDATA_SPACEID )
SPACE_SPACEDATA_SPACE_TYPE_KEY			= 257							# ������ spaceData �������key
SPACE_SPACEDATA_NUMBER					= 258							# ������base�ˣ�ͨ��spaceManager���ɵ�Ψһ��spaceNumber
SPACE_SPACEDATA_LINE_NUMBER				= 259							# ������ spaceData �����ڼ��ߵĺ���
SPACE_SPACEDATA_MAX_LINE_NUMBER			= 260							# ������ spaceData �����ж�������
SPACE_SPACEDATA_CANNOTPK				= 261							# ������ spaceData �����ܷ�PK
SPACE_SPACEDATA_CANNOTQIECUO			= 262							# ������ spaceData �����ܷ��д�
SPACE_SPACEDATA_CANNOTCONJUREEIDOLON	= 263							# ������ spaceData �����ܷ��ٻ�С����

SPACE_SPACEDATA_COPY_TITLE				= 270							# ��������
SPACE_SPACEDATA_START_TIME				= 271							# ������ʼʱ��
SPACE_SPACEDATA_LAST_TIME				= 272							# ��������ʱ��
SPACE_SPACEDATA_LEAVE_MONSTER			= 273							# ����ʣ��С������
SPACE_SPACEDATA_LEAVE_BOSS				= 274							# ����ʣ��������
SPACE_SPACEDATA_LEVEL					= 275							# ��������
SPACE_SPACEDATA_MENGMENG				= 276							# ������������
SPACE_SPACEDATA_MOWENHU					= 277							# ħ�ƻ�����
SPACE_SPACEDATA_GUIYINGSHI				= 278							# ���Ӱʨ����
SPACE_SPACEDATA_NEXT_LEVEL_TIME			= 279							# ��һ������ʱ��
SPACE_SPACEDATA_YAYU_HP_PRECENT			= 280							# �m؅Ѫ���ٷֱ�
SPACE_SPACEDATA_CITYWAR_RIGHT_TONGDBID	= 281							# ��ս���ط����DBID
SPACE_SPACEDATA_TONG_TERRITORY_TONGDBID	= 282							# �����ظ��� ��¼�İ��DBID
SPACE_SPACEDATA_CITY_REVENUE			= 283							# ����˰��
SPACE_SPACEDATA_TEACH_MONSTER_LEVEL		= 284							# ʦͽ����С�ּ���
SPACE_SPACEDATA_TREE_HP_PRECENT			= 285							# ����Ѫ���ٷֱ�
SPACE_SPACEDATA_CAN_FLY					= 286							# �ռ��Ƿ���Է���
SPACE_SPACEDATA_MIN_BBOX				= 287							# �ռ������Ľ�С�Խ�����
SPACE_SPACEDATA_MAX_BBOX				= 288							# �ռ������Ľϴ�Խ�����
SPACE_SPACEDATA_DEATH_DEPTH				= 289							# �ؼ��������
SPACE_SPACEDATA_DART_POINT				= 290							# ��ƽ�ھֺ���¡�ھ��������ڻ���
SPACE_SPACEDATA_CHALLENGE_GATE			= 291							# ��ɽ�󷨵�ǰ����
SPACE_SPACEDATA_POTENTIAL_FLAG_HP		= 292							# Ǳ���Ҷ���ʥ�����Ѫ��
SPACE_SPACEDATA_CAN_VEHICLE 			= 293 							# �ռ��Ƿ�����ٻ�����
SPACE_SPACEDATA_BATCH					= 294							# ���Ȫm؅��ǰˢ�ֽ׶�
SPACE_SPACEDATA_NEXT_BATCH_TIME			= 295							# �°�m؅��һ������ʱ��
SPACE_SPACEDATA_YAYU_NEW_HP				= 296							# �°�m؅Ѫ����ʾ
SPACE_SPACEDATA_PREPARE_TIME			= 297							# ս��׼��ʱ��
SPACE_SPACEDATA_ZHANNAN_ANGER_PERCENT	= 298							# ի��ŭ��ֵ�ٷֱȣ���Ѫ�����㣩
SPACE_SPACEDATA_ANGER_ISSHOW			= 299							# �Ƿ���ʾ����ŭ��ֵ
SPACE_SPACEDATA_TOTAL_BOSS				= 300							# Boss����
SPACE_DANCECOPY_COMOBOPOINT				= 301 							# ����ʱ�̶��踱����������
SPACE_DANCECHALLENGE_TIMELIMIT			= 302							# ��ս���踱����ʱ������
SPACE_SPACEDATA_YIJIE_SCORE_TIAN		= 303							# ���ս���������
SPACE_SPACEDATA_YIJIE_PLAYER_TIAN		= 304							# ���ս����������
SPACE_SPACEDATA_YIJIE_SCORE_DI			= 305							# ���ս���������
SPACE_SPACEDATA_YIJIE_PLAYER_DI			= 306							# ���ս����������
SPACE_SPACEDATA_YIJIE_SCORE_REN			= 307							# ���ս���������
SPACE_SPACEDATA_YIJIE_PLAYER_REN		= 308							# ���ս����������
SPACE_SPACEDATA_YIJIE_ANGER_FACTION		= 309							# ���ս����ŭ��Ӫ
SPACE_SPACEDATA_YIJIE_ALLIANCE_FACTIONS	= 310							# ���ս��ͬ��˫��
SPACE_SPACEDATA_PROGRESS				= 311							# ��������

SPACE_COPY_MMP_YAOQI_PERCENT			= 312							# �����������������ٷֱ�
SPACE_SPACEDATA_LEAVE_WAVE				= 313							# ʣ����ﲨ��
SPACE_SPACEDATA_NPC_HP_PRECENT			= 314							# NPCѪ���ٷֱ�


SPACE_CONFIG_PATH 				= "config/server/gameObject/space"	# �ռ������ļ�


# --------------------------------------------------------------------
# about chatting( from L3Common )
# --------------------------------------------------------------------
CHAT_MESSAGE_UPPER_LIMIT	= 140		# ������������ֽ���( ԭ����MAX_CHAT_MESSAGE )�����ڿͻ�������unicode��Ϊ�˴����֣��������������Ϊ�ͻ��˵�2�� --pj
CHAT_ESTOP_REPEAT_COUNT		= 10		# �ظ����ٴ�ͬ�����Խ��ᱻ����
CHAT_ESTOP_TIME				= 30		# ����ʱ��

CHAT_TRADE_DELAY			= 7			# ���׷��Է���ʱ���ӳ٣���λ����( ԭ����BUSINESS_CHAT_DELAY )
CHAT_RUMOR_DELAY			= 600		# ҥ�Է���ʱ��������λ����( ԭ����RUMOR_CHAT_DELAY )
CHAT_YELL_DELAY				= 20.0		# ���緢��ʱ��������λ����( ԭ����YELL_CHAT_DELAY )
CHAT_GLOBAL_DELAY			= 1.0		# ȫ�ַ����ٶȣ���/�Σ�float type( ԭ����GLOBAL_CHAT_DELAY )
CHAT_CMAP_DELAY				= 2.0		# ��ӪƵ�ȵķ���ʱ��������λ����

CHAT_RUMOR_PROBABILITY		= 0.8		# ��ҥ�ɹ��ʣ�80%( ԭ����RUMOR_CHAT_PROBABILITY )

CHAT_RUMOR_MP_DECREMENT		= 0.3		# ÿ��ҥ��MP�������MP�İٷֱ�( ԭ����RUMOR_MP_REDUCE )

CHAT_TRADE_LEVEL_REQUIRE	= 10		# ����Ƶ�����Եȼ�Ҫ��( ԭ����BUSINESS_CHAT_LVL_REQ )
CHAT_YELL_LEVEL_REQUIRE		= 20		# ����Ƶ�����Եȼ�Ҫ��( ԭ����YELL_CHAT_LVL_REQ )
CHAT_YELL_USE_MONEY			= 500		# ������Ҫ����Ϸ��

CHAT_WELKIN_ITEM			= 110103014	# ��������Ʒ��
CHAT_TUNNEL_ITEM			= 110103021	# ��������Ʒ��
CHAT_TUNNEL_ITEM_BINDED		= 110103027	# ��������Ʒ��(��Ʒ�󶨰�)

# --------------------------------------------------------------------
# about team( move from base/Const.py by phw )
# --------------------------------------------------------------------
TEAM_FEEDBACK_WAIT_TIME 			= 60			# ��Ӷ೤ʱ��û��Ӧʱ�������ٶ��飨�룩( ԭ����DESTORY_TEAM_TIME )
TEAM_OFFLINE_DETECT_INTERVAL 		= 10 			# ������ߺ󣬶೤ʱ����һ�����߼��( ԭ����OFFLINE_LEAVE_HTIME )
TEAM_OFFLINE_DURATION 				= 300 			# ������߶೤ʱ��󣬱���Ϊ������( ԭ����OFFLINE_LEAVE_TIME )

TEAM_INVITE_KEEP_TIME 				= 30 			# �������ʱ��(��)
TEAM_UPDATA_MAX_TIME 				= 3				# �������������������ݵ�ʱ������
TEAM_MEMBER_MAX						= 5				# �����Ա�������

TEAM_DATA_UPDATE_TIME				= 5				# Զ�������ÿ5�����һ��
TEAM_DATA_UPDATE_TIME_NEAR			= 0.5			# ���������û0.5�����һ��
TEAM_DATA_UPDATE_PET				= 5				# ���¶��ѳ���5��һ��

TEAM_FOLLOW_DISTANCE				= 30			# �ף����������Ч����

# --------------------------------------------------------------------
# about mail( zyx )
# --------------------------------------------------------------------
MAIL_CHECK_OUTDATED_REPEAT_TIME 	= 30 			# ��ѯ������ɾ���ʼ��ĸ���ʱ�䣨�룩
MAIL_TITLE_LENGTH_MAX 				= 20			# �ʼ�������󳤶ȣ��ֽڣ�  zyx: ������ܸĴ󡣷���������
MAIL_CONTENT_LENGTH_MAX				= 400			# �ʼ�������󳤶ȣ��ֽڣ�	zyx: ������ܸĴ󡣷���������

MAIL_NPC_OUTTIMED					= 604800		# δ���ʼ�ɾ��ʱ�䣬��λ���룻 604800 = 3600*24*7 �룻��ʾ�ʼ��೤ʱ��û���Ķ��ͻᱻɾ��
MAIL_READ_OUTTIMED					= 7200			# �Ķ������ʼ�ɾ��ʱ��Ϊ�� 7200 = 3600*2 ��
MAIL_RETURN_AFTER_SEND				= 604800		# δ���ʼ�����ʱ�䣬��λ���룻��ʾ�೤ʱ���ʼ�û�ж����ͻᱻ����
MAIL_RETURN_CHECK_TIME				= 3600			# ���ż����ʱ�䣬��λ����
MAIL_RETURN_PROCESS_TIME			= 1				# ���Ŵ�����ʱ�䣨���೤ʱ�䴦��һ�����ţ�����λ����

MAIL_RECEIVE_TIME_QUICK				= 0				# �������ʱ�䣬��λ����
MAIL_RECEIVE_TIME_NORMAL			= 7200			# ��ͨ�ż�����ʱ�䣬��λ����

MAIL_FARE							= 50			# �ʼ��շ�
MAIL_SEND_MONEY_RATE				= 0.002			# �ʼĽ�Ǯ���շѱ���
MAIL_SEND_ITEM_FARE					= 50			# �ʼ���Ʒ�����շ�
MAIL_UPPER_LIMIT					= 50			# �ռ��˿ɴ��ڵ��ʼ�����

# --------------------------------------------------------------------------------
# about bank
# --------------------------------------------------------------------------------
BANK_MONEY_LIMIT				= 4000000000# �洢��Ǯׯ�Ľ�Ǯ������
BANKBAG_NORMAL_ORDER_COUNT		= 28		# Ǯׯ������������
BANK_MAX_COUNT					= 7			# Ǯׯ������������
BANK_HIRE_COST_MONEY			= 100		# ǰ2�����λ���÷��ã��ݶ�100��Ǯ
BANK_HIRE_COST_GOLD				= 10		# ��2�����λ���÷��ã��ݶ�10Ԫ��


# --------------------------------------------------------------------
# װ������
# --------------------------------------------------------------------


# --------------------------------------------------------------------------------
# ��Ʒ���
# --------------------------------------------------------------------------------
REDEEM_ITEM_MAX_COUNT				= 7			# �������Ʒ�б������������ݶ�12


# --------------------------------------------------------------------------------
# ��̯ϵͳ
# --------------------------------------------------------------------------------
VEND_ITEM_MAX_COUNT					= 30			# ��̯��Ʒ�б����󳤶�
VEND_SIGNBOARD_MAX_LENGTH			= 20			# ��̯���Ƶ�����ֽ���
VEND_PET_MAX_COUNT					= 6				# ��̯�����б����󳤶�


# --------------------------------------------------------------------------------
# ��ҹ�ϵ��RoleRelation( wsf )
# --------------------------------------------------------------------------------
# ʦͽ��ϵ
TEACH_MASTER_MIN_LEVEL				= 60			# �ܳ�Ϊʦ������ҵ���С����
TEACH_END_TEACH_LEAST_LEVEL			= 50			# ͽ�ܳ�ʦ����С�ȼ�
TEACH_PRENTICE_LOWER_LIMIT			= 10			# �ܹ���Ϊͽ�ܵ���Ҽ�������
TEACH_PRENTICE_UPPER_LIMIT			= 49			# �ܹ���Ϊͽ�ܵ���Ҽ�������

TEACH_PRENTICE_MAX_COUNT			= 3				# һ����������3��ͽ��
TEACH_COMMUNICATE_DISTANCE			= 10			# ��ʦʱʦ����ͽ�ܵľ��벻�ܳ���10��
TEACH_END_TEACH_AWARD_LIMIT			= 55			# �ܹ���ó�ʦ��������ӽ�����ͽ�ܵȼ����ܳ���55

TEACH_TEAM_EXP_ADDITIONAL_PERCENT	= 0.2			# ʦͽ��Ӿ���ӳɱ���
TEACH_TEAM_KILL_BENEFIT_DISTANCE	= 100			# ʦͽ���ɱ�֣��ܹ���þ���ӳɵķ�Χ
TEACH_UPGRADE_MONEY_AWARD_RATE		= 50			# ͽ��������ʦ����õĽ�Ǯ�����������
TEACH_END_MASTER_MONEY_AWARD		= 100			# �ɹ���ʦ��ʦ����õĽ�Ǯ�����������
TEACH_END_MASTER_EXP_AWARD			= 10000			# �ɹ���ʦ��ʦ����õľ��齱���������
TEACH_END_MASTER_CREDIT_AWARD		= 20				# �ɹ���ʦ��ʦ����õĹ�ѫ�㽱���������
TEACH_END_PRENTICE_MONEY_AWARD		= 50			# �ɹ���ʦ��ͽ�ܻ�õĽ�Ǯ�����������
TEACH_END_PRENTICE_EXP_AWARD		= 8000			# �ɹ���ʦ��ͽ�ܻ�õľ��齱���������
TEACH_QUERY_MAX_LENGTH			= 14			# ���һ���ܲ�ѯ��ע����ͽ��Ϣ����
TEACH_REGISTER_VALID_TIME			= 345600		# ���ע���ʦ��������Чʱ�䣬��λ���룩


# ���˹�ϵ
SWEETIE_NUM_LIMIT					= 15			# ���˵�������
SWEETIE_LEVEL_LIMIT					= 18			# 18������(��18��)����Ҳ��ܽ�Ϊ����

# ���޹�ϵ
COUPLE_LEVEL_LIMIT					= 20			# 20������(��20��)����Ҳ��ܽ�Ϊ����
COUPLE_WEDDING_CHARGE				= 300000		# �����Ҫÿ�˻���300000��Ǯ
COUPLE_FORCE_DIVORCE_CHARGE			= 500000		# ǿ�������Ҫ500000rmb,̫����.
COUPLE_HONGBAO_ITEM_ID				= 60101012		# ��Ʒ�����id
COUPLE_WEDDING_RING_PRICE			= 300000		# �һؽ���ָ�Ļ���
COUPLE_TEAM_EXP_PERCENT				= 0.1			# ������Ӿ���ӳɱ���
COUPLE_SWARE_DISTANCE				= 10.0			# ���˫����Ҫ���ֵ������뷶Χ

ADD_SWEETIE_NEED_FRIENDLY_VALUE		= 2000		# ������������Ҫ���Ѻö�
ADD_COUPLE_NEED_FRIENDLY_VALUE		= 5000		# ���������Ҫ���Ѻö�
FORCE_DIVORCE_COST					= 400000	# ǿ��������
RELATION_FOE_NUM_LIMIT				= 500		# ��ҳ�������

RELATION_ALLY_SWEAR_DISTANCE		= 30		# ��ҽ��ʱ����Ч����
RELATION_ALLY_LEVEL_LACK				= 15		# ����ܹ���ݵ���С����
RELATION_ALLY_COST					= 100000	# ��ݻ���
RELATION_ALLY_NEED_FRIENDLY_VALUE	= 2000		# ���������Ҫ���Ѻö�
ALLY_CHANGE_TITLE_COST				= 50000	# �Ľ�ݳƺ�����Ľ�Ǯ
ALLY_TEAM_EXP_PERCENT				= 0.05		# ��ݹ�ϵ��Ӿ���ӳɰٷֱ�
RELATION_ALLY_NEW_COST				= 50000	# ��ݼ����³�Ա����

TEACH_SPACE_MONSTER_COUNT		= 40		# ʦͽ����С������
TEACH_SPACE_ENTER_TEAMMATE_DISTANCE = 70	# ����ʦͽ�����Ķ��Ѿ���

# �����Ҫ����Ʒ�б�array of ( ��ƷID, ��Ʒ���� )
RELATION_ALLY_NEED_ITEMS			= [ ( 50101105, 1 ), ( 50101106, 1 ) ]

# ���Ĭ�ϳƺ�����
TITLE_ALLY_DEFAULT_NAME				= cschannel_msgs.VOICE_COMMON_CONST_1

# --------------------------------------------------------------------
# about TONG( designed by kebiao )
# --------------------------------------------------------------------
# �����ĳ�ȼ����������ռ�������
TONG_FAMILY_COUNT_LIMIT = {}
TONG_FAMILY_COUNT_LIMIT[1]		= 3	#tongLevel, familyMaxCount
TONG_FAMILY_COUNT_LIMIT[2]		= 5
TONG_FAMILY_COUNT_LIMIT[3]		= 7
TONG_FAMILY_COUNT_LIMIT[4]		= 9
TONG_FAMILY_COUNT_LIMIT[5]		= 10

TONG_STORAGE_LOG_COUNT			= 200	# ���ֿ����洢��log��Ϣ����
TONG_BAG_ORDER_COUNT			= 80	# ���ֿ��������������
TONG_JOIN_MIN_LEVEL				= 10	# ���������С�ȼ�

# ����������ۿ�
TONG_TJP_REBATE = {
	1 	: 0.90,
	2 	: 0.85,
	3 	: 0.80,
	4 	: 0.75,
	5 	: 0.70,
	6 	: 0.65,
	7 	: 0.60,
	8 	: 0.55,
	9 	: 0.50,
	10 	: 0.4,
}

TONG_MEMBER_LIMIT_DICT = { 1:30, 2:60, 3:90, 4:120, 5:150, 6:180, 7:210, 8:240, 9:270, 10:300 }

# ���ٺ»�һ�������
TONG_SALARY_EXCHANGE_RATE = {	1 : 9000, \
								2 : 11700, \
								3 : 14400, \
								4 : 17100, \
								5 : 19800
							}

TONG_SALARY_EXCHANGE_MIN_RATE = 5000 		# ���ٺ»�һ�������

JOIN_TONG_INIT_CONTRIBUTE			= 0		# �������ʼ���׶�
JOIN_TONG_CHIEF_INIT_CONTRIBUTE		= 100	# ������ʼ���׶�

#�����̨���
TONG_ABATTOIR_PRESTIGE_LIMIT	= 100			# ������̨���İ����������
TONG_ABATTOIR_MAX_NUM			= 16				# �μ���̨���İ��������
TONG_ABATTOIR_MATCH_TIME		= 15			# һ������Ҫ���е�ʱ��
TONG_ABATTOIR_REST_TIME			= 5				# һ���������������Ϣ��ʱ��
TONG_ABATTOIR_MAX_MEMBER   		= 15			# ÿ��������ս������������
TONG_ABATTOIR_SINGUP			= 1				#��ʼ����
TONG_ABATTOIR_ENTER				= 2				#�볡
TONG_ABATTOIR_START				= 3				#1��������ʼ
TONG_ABATTOIR_END				= 4				#1����������
TONG_ABATTOIR_OVER				= 0				#ȫ������������δ������

# --------------------------------------------------------------------
# about gem( designed by wsf )
# --------------------------------------------------------------------
GEM_COUNT_UPPER					= 5			# ����ܹ���ȡ�ı�ʯ���ޣ��������ﱦʯ
GEM_ACTIVATE_COST				= 10000		# ���ʯ���軨��
GEM_ROLE_COMMON_COUNT_UPPER		= 50		# ����ȡ����Ҿ���ʯ��������
GEM_PET_COMMON_COUNT_UPPER		= 50		# ����ȡ�ĳ��ﾭ��ʯ��������
GEM_PET_COMMON_VALUE_UPPER		= 1000000000# ����ȡ�Ĵ���ʱ�����޺ͱ�ʯ�ɴ洢�ľ�������
GEM_PET_COMMON_EXP_PERCENT		= 0.02		# ÿ�����ﾭ��ʯ������ӳɰٷֱ�
GEM_WORK_HARD_RATE				= 1.5		# �̿����������ӳɵı���
GEM_HIRE_PAY					= 10000		# ��ȡһ������ʯ�Ļ���


# --------------------------------------------------------------------
# about SpecialShop( designed by wsf )
# --------------------------------------------------------------------
SPECIAL_SHOP_HOT_ITEM_COUNT		= 15		# ��������������


# --------------------------------------------------------------------
# about Prestige( designed by wsf )
# --------------------------------------------------------------------
PRESTIGE_UPLIMIT				= 45000		# ���������ֵ����
PRESTIGE_LOWERLIMIT				= -39000	# ��������Сֵ����

# --------------------------------------------------------------------
INVBUYPERCENT					= 0.2		# װ������Ʒ�Ļع��۸�

PENDING_BUFF_ID					= 32239700101		# ���δ��״̬buff id
PENDING_SKILL_ID				= 322397001			# δ��״̬����id
PROWL_BUFF_ID					= 20002				# Ǳ��buff id
FLY_TELEPORT_BUFF_ID			= 32239700101		# ���δ��״̬buff id
FOLLOW_SKILL_ID					= 322403001			# ���漼��id
FOLLOW_BUFF_ID					= 32240300101			# ����buff id

# --------------------------------------------------------------------
WUDAO_MAX_NUM                   = 64                # ������һ���������μ�����
WUDAO_TIME_REST 				= 3 				# �м���Ϣʱ��
WUDAO_TIME_PREPARE				= 2 				# ����׼��ʱ��
WUDAO_TIME_UNDERWAY 			= 5 				# ����ʱ��
WUDAO_TIME_SPACE_LIVING			= WUDAO_TIME_PREPARE + WUDAO_TIME_UNDERWAY # һ��������ʱ��
WUDAO_TIME_ROUND				= WUDAO_TIME_REST + WUDAO_TIME_PREPARE + WUDAO_TIME_UNDERWAY # ������һ�ֵ�ʱ��
# --------------------------------------------------------------------
TEAM_CHALLENGE_MAX_NUM          = 32                # �����̨һ���������μӶ�����
TEAM_CHALLENGE_TIME_REST 		= 3 				# �м���Ϣʱ��
TEAM_CHALLENGE_TIME_PREPARE		= 2 				# ����׼��ʱ��
TEAM_CHALLENGE_TIME_UNDERWAY 	= 10 				# ����ʱ��
TEAM_CHALLENGE_TIME_ROUND		= TEAM_CHALLENGE_TIME_REST + TEAM_CHALLENGE_TIME_PREPARE + TEAM_CHALLENGE_TIME_UNDERWAY # һ�ֵ�ʱ��
ROLECOMPETITION_MAX_NUM         = 30                # ���˾���һ���������μ�����

TEAM_CHALLENGE_JOIN_LEVEL_MIN 		= 60 		#��������С����
TEAM_CHALLENGE_JOIN_LEVEL_MAX 		= 150		#��������󼶱�
TEAM_CHALLENGE_JOIN_LEVEL_INCREASE  = 9 		#�����ĵȼ��ε�����
ROLE_SOMPETITION_JOIN_LEVEL_MIN		= 60		#���˾�����������С����

TEAM_CHALLENGE_MEMBER_MUST				= 3				#�������������
TEAM_CHALLENGE_RECRUIT_DIALOG_TIME		= 30			#�Ի��򵯳���ʱ��

TEAM_CHALLENGE_REWARD_COMMON		= 1 # ���׽���
TEAM_CHALLENGE_REWARD_WIN			= 2 # N��ʤ������
TEAM_CHALLENGE_REWARD_CHAMPION		= 3 # �ھ�����

# --------------------------------------------------------------------

LUCKY_BOX_ITEM_ZHAOCAI			= 60101008			# �콵�����вƱ���id
LUCKY_BOX_ITEM_JINBAO			= 60101009			# �콵���н�������id
LUCKY_BOX_MOSTER_LEVEL			= 20				# �����й�����ͼ���
LUCKY_BOX_DROP_RATE				= 0.015				# �����еĸ���
LUCKY_BOX_USE_LEVEL_CHECK		= 5		# 	���ʹ���콵����ʱ�ȼ�����С����5������


#---------------------------------------------------------------------------
FACTION_XL 						= 37				# ��¡�ھ���������
FACTION_CP 						= 38				# ��ƽ�ھ���������
DART_ROB_MIN_LEVEL				= 3					# ���ڵȼ����ƣ������ߺͱ����ڳ��ȼ�������ֵ��������PKֵ������Ҳ�޷��������
DART_INITIAL_POINT				= 50				# �ھֳ�ʼ����


#�����
DAY_MAP = {0:'Monday',1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}

MONDAY 		= 0
TUESDAY 	= 1
WEDNESDAY 	= 2
THURSDAY	= 3
FRIDAY		= 4
SATURADAY	= 5
SUNDAY		= 6


DOUBLE_EXP_SHOW_MAP = {
	50		: "50%",
	100 	: "100%",
	200 	: "200%",
	300 	: "300%",
	400 	: "400%",
	500 	: "500%",
	600 	: "600%",
	700 	: "700%",
	800 	: "800%",
	900 	: "900%",
	1000	: "1000%",
}
#----------------------------------------------------------
BUFF_ID_REVIVE_IN_TIANGUAN = 22120					# ���������ԭ�ظ����buffID
BUFF_ID_EXTRA_EXP_IN_TIANGUAN = 22016				# �������buff��ID

# --------------------------------------------------------------------
# ȫ��֪ʶ�ʴ�
# --------------------------------------------------------------------
QUIZ_MIN_LEVEL_LIMIT			= 10		# ֪ʶ�ʴ���ͼ�������
QUIZ_QUESTION_COUNT				= 30		# ֪ʶ�ʴ���Ŀ����
QUIZ_LUCKY_STAR_COUNT			= 3			# ����������
QUIZ_GOLD_CONSUME				= 30		# Ԫ������һ�����ĵ�����
QUIZ_READING_QUESTION_TIME		= 10.0		# ����Ŀ����ʱ��
QUIZ_ANSWER_TIME				= 10.0		# ����ʱ��
QUIZ_QUESTION_TIME				= 22.0		# ��һ��������ʱ��

#---------------------------------------------------------------------
# ����״̬����Ʒ״̬��ӳ���ֵ䣬key:����״̬��value:��Ʒ״̬
#---------------------------------------------------------------------
SKILL_STATE_TO_ITEM_STATE = {
	csstatus.SKILL_NOT_READY			: csstatus.CIB_MSG_TEMP_CANT_USE_ITEM,
	csstatus.SKILL_CAST_ENTITY_LEVE_MIN : csstatus.CIB_MSG_ITEM_CAST_LEVEL_MIN,
	csstatus.SKILL_CAST_ENTITY_LEVE_MAX : csstatus.CIB_MSG_ITEM_CAST_LEVEL_MAX,
	csstatus.SKILL_CAST_OBJECT_NOT_ENEMY: csstatus.SKILL_CANT_CAST_ENTITY,
	csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER:csstatus.CIB_MSG_OBJECT_NOT_MONSTER,
	}

#---------------------------------------------------------------------
# ����Ԥ��λ��
#---------------------------------------------------------------------
Start_Positions = [(6.222151,18.349606,-130.868744),	#��ͨ����λ��
				(6.198310,18.347652,-129.942719),
				(6.163738,18.347652,-129.005447),
				(6.099733,18.347652,-128.125687),
				(6.055299,18.349606,-127.217415),
				(6.008567,18.349606,-126.271141),
				(5.983170,18.349606,-125.321480),
				(5.941438,18.349606,-124.363823),
				(5.886509,18.349606,-123.384743),
				(5.858191,18.349606,-122.449036),
				(5.794187,18.349606,-121.569260),
				(5.749752,18.349606,-120.660912),
				(5.703021,18.349606,-119.714638),
				(5.673449,18.349606,-118.750778),
				(5.631716,18.349606,-117.793121),
				(5.576788,18.349606,-116.814041),
				(5.548471,18.349606,-115.878334),
				(5.484465,18.349606,-114.998558),
				(5.440031,18.349606,-114.090210),
				(5.393299,18.349606,-113.143936)]

Start_Positions_03 = [(87.356224, 0.020237, 14.283286),		#ʥ��������ʼλ��
						(86.986404, 0.023053, 16.305824),
						(86.407257, 0.034930, 18.760397),
						(85.831665, 0.035362, 20.798906),
						(85.394630, 0.030320, 22.764093),
						(84.757584, 0.024771, 25.057795),
						(84.233978, 0.004829, 27.342119),
						]
#---------------------------------------------------------------------
# ��Ҫ��ʾ�����spaceCopy
#---------------------------------------------------------------------
HAVE_SPACE_COPY_INTERFACE = [csdefine.SPACE_TYPE_SHUIJING,
					csdefine.SPACE_TYPE_TIAN_GUAN,
					csdefine.SPACE_TYPE_POTENTIAL,
					csdefine.SPACE_TYPE_POTENTIAL_MELEE,
					csdefine.SPACE_TYPE_SHEN_GUI_MI_JING,
					csdefine.SPACE_TYPE_WU_YAO_QIAN_SHAO,
					csdefine.SPACE_TYPE_WU_YAO_WANG_BAO_ZANG,
					csdefine.SPACE_TYPE_EXP_MELEE,
					csdefine.SPACE_TYPE_HUNDUN,
					csdefine.SPACE_TYPE_DRAGON,
					csdefine.SPACE_TYPE_PIG,
					csdefine.SPACE_TYPE_PROTECT_TONG,
					csdefine.SPACE_TYPE_YAYU,
					csdefine.SPACE_TYPE_XIE_LONG_DONG_XUE,
					csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN,
					csdefine.SPACE_TYPE_FJSG,
					csdefine.SPACE_TYPE_TONG_TERRITORY,
					csdefine.SPACE_TYPE_TEACH_KILL_MONSTER,
					csdefine.SPACE_TYPE_KUAFU_REMAINS,
					csdefine.SPACE_TYPE_CHALLENGE,
					csdefine.SPACE_TYPE_TEAM_CHALLENGE,
					csdefine.SPACE_TYPE_YXLM,
					csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI,
					csdefine.SPACE_TYPE_YXLM_PVP,
					csdefine.SPACE_TYPE_DESTINY_TRANS,
					csdefine.SPACE_TYPE_DANCECOPY_PARCTICE,
					csdefine.SPACE_TYPE_DANCECOPY_CHALLENGE,
					csdefine.SPACE_TYPE_TEMPLATE,
					csdefine.SPACE_TYPE_FANG_SHOU,
					csdefine.SPACE_TYPE_MELT_MONSTER_POT,
					]


#----------------�������ȡ
PCU_TAKEPRESENTWITHOUTID	= 0			#���������ŵĽ�Ʒ��ȡ����
PCU_TAKESILVERCOINS			= 1			#��Ԫ����ȡ����
PCU_TAKEPRESENT				= 2			#�������ŵĽ�Ʒ��ȡ����
PCU_TAKECHARGE				= 3			#��ֵ��ȡ����
PCU_TAKECHARGEUNITE			= 4			#��ȡ��Ʒ(�������Ͳ�������)
PCU_TAKEPRESENTUNITE		= 5			#���н�Ʒ����ȡ(����ֵ��)
PCU_TAKECHARGEUNITE_SINGLE		= 6		#һ����ȡһ����Ʒ�ģ���/��������������

# --------------------------------------------------------------------
# װ������������Լӳ�
# --------------------------------------------------------------------
EQUIP_GHOST_BIND_ADD_BASERATE = 0.1


# --------------------------------------------------------------------
# �ƾٿ���λ����Ϣ
# --------------------------------------------------------------------
KAOGUANS = {
	1 : cschannel_msgs.KE_JU_INFO_1,
	2 : cschannel_msgs.KE_JU_INFO_2,
	3 : cschannel_msgs.KE_JU_INFO_3,
	4 : cschannel_msgs.KE_JU_INFO_4,
	5 : cschannel_msgs.KE_JU_INFO_5,
	6 : cschannel_msgs.KE_JU_INFO_6,
	7 : cschannel_msgs.KE_JU_INFO_7,
	8 : cschannel_msgs.KE_JU_INFO_8,
	9 : cschannel_msgs.KE_JU_INFO_9,
	10 : cschannel_msgs.KE_JU_INFO_10,
	11 : cschannel_msgs.KE_JU_INFO_11,
	12 : cschannel_msgs.KE_JU_INFO_12,
	13 : cschannel_msgs.KE_JU_INFO_13,
	14 : cschannel_msgs.KE_JU_INFO_14,
	15 : cschannel_msgs.KE_JU_INFO_15,
	}

#��ƷƷ�ʶ�Ӧ�Ĺ㲥������ɫ by����
ITEM_BROAD_COLOR_FOR_QUALITY = {
									ItemTypeEnum.CQT_WHITE	:	"@F{fc=(255,255,255)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_BLUE	:	"@F{fc=(0,255,255)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_GOLD	:	"@F{fc=(255,255,0)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_PINK	:	"@F{fc=(255,0,255)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_GREEN	:	"@F{fc=(0,255,0)}[%s]@F{fc=(255,255,0)}"
								}

GAMERANKING_SEND_DATANUM = 5 #--------------���а�һ�η������ݵ�����

# --------------------------------------------------------------------
# �µ������
# --------------------------------------------------------------------
VEHICLE_DIS_LEVEL_MAX                   = 6  #��������ҵȼ��������Խ����ٻ����������
VEHICLE_AMOUNT_MAX			= 12
VEHICLE_MODEL_BOUND			= Math.Vector3( ( 1.5, 2.0, 1.5 ) )		#���ͳһ��bounding boxֵ�������ߡ���
VEHICLE_DEADTIEM_LIMIT			= 18446744073709551615	# �������ʱ������ UINT64 by����
VEHICLE_DEADTIEM_MIN			= 0			# �������ʱ������ by����
VEHICLE_MOUNT_DISTANCE			= 30.0		# ����������������
VEHICLE_SKILLS_TOTAL			= 4			# ����ѧϰ��������

VEHICLE_EQUIP_MAPS = {	ItemTypeEnum.VEHICLE_CWT_HALTER 		: "halterID",		# ��ͷ
						ItemTypeEnum.VEHICLE_CWT_SADDLE 		: "saddleID",		# ��
						ItemTypeEnum.VEHICLE_CWT_NECKLACE		: "necklaceID",		# ����
						ItemTypeEnum.VEHICLE_CWT_CLAW 			: "clawID",			# צ��
						ItemTypeEnum.VEHICLE_CWT_MANTLE 		: "mantleID",		# ����
						ItemTypeEnum.VEHICLE_CWT_BREASTPLATE 	: "breastplateID"	# ����
					}

VEHICLE_FOOD_ITEMID = [ 60508021,60508022, 60508023 ]	#�������ID

VEHICLE_STEP_UPGRADE_ITEMID = { 1:[ 60508001,60508002 ],	#���׽״ζ�Ӧ��ƷID
							2:[ 60508001,60508002 ],
							3:[ 60508001,60508002 ],
							4:[ 60508001,60508002 ],
							5:[ 60508003,60508004 ],
							6:[ 60508003,60508004 ],
							7:[ 60508003,60508004 ],
							8:[ 60508003,60508004 ],
							9:[ 60508003,60508004 ],
							}

VEHICLE_SEALED_NEED_ITEM = { 1:60508005,	#����״ζ�Ӧ��ƷID
							2:60508006,
							3:60508007,
							4:60508008,
							5:60508009,
							6:60508010,
							7:60508011,
							8:60508012,
							9:60508013,
							}

VEHICLE_STEP_UPGRADE_SUCCESSRATE = 0.5

VEHICLE_TYPE_TEXT = {	csdefine.VEHICLE_TYPE_LAND: 	ST.VEHICLE_TYPE_LAND,
						csdefine.VEHICLE_TYPE_FLY:		ST.VEHICLE_TYPE_FLY,
					}
MAX_FULL_DEGREE		= 31536000	#��豥��������1��


# ������������   ��С���� ��󼶱� ��Ǯ
PRISON_CONTRIBUTE_DATAS = [
	( 30,	39,		24000 ),
	( 40,	49,		36000 ),
	( 50,	59,		60000 ),
	( 60,	69,		72000 ),
	( 70,	79,		84000 ),
	( 80,	89,		96000 ),
	( 90,	99,		108000 ),
	( 100,	109,	120000 ),
	( 110,	119,	132000 ),
	( 120,	129,	144000 ),
	( 130,	139,	156000 ),
	( 140,	149,	168000 ),
	( 150,	1000,	180000 ),
]

# --------------------------------------------------------------------
# �ض���Ʒ��ͨ�ȼ�����
# --------------------------------------------------------------------
SPECIFIC_ITEM_GIVE_LEVEL = 30

KITBAG_CANT_UNLOCK_INTERVAL			= 3		# �����������������ޣ���λ����
KITBAG_FORCE_UNLOCK_LIMIT_TIME		= 72 * 3600		# ����ǿ�ƽ�������ʱ��

BANK_CANT_UNLOCK_INTERVAL			= 60		# �ֿ��������������ޣ���λ����
BANK_FORCE_UNLOCK_LIMIT_TIME		= 72 * 3600		# �ֿ�ǿ�ƽ�������ʱ��


SELL_POINT_CARD_YAJIN			= 50000			# ���۵㿨Ѻ��
SELL_POINT_CARD_LASTTIME		= 86400			# ÿ�ŵ㿨�ļ�����Чʱ�䣨һ�죩


TISHOU_SHOP_INFO_QUERY_PAGE_SIZE		= 26	# �������̲�ѯҳ���С
TISHOU_ITEM_INFO_QUERY_PAGE_SIZE		= 12	# ������Ʒ��ѯҳ���С
TISHOU_PET_INFO_QUERY_PAGE_SIZE			= 18	# ���۳����ѯҳ���С


TISHOU_SHOP_INFO						= 0     # �����̵���Ϣ
TISHOU_ITEM_LOWERLEVEL					= 1     # ��Ʒ�ȼ�����
TISHOU_ITEM_UPPERLEVEL					= 2     # ��Ʒ�ȼ�����
TISHOU_ITEM_TYPELIMIT					= 3     # ��Ʒ����
TISHOU_ITEM_QALIMIT						= 4     # ��ƷƷ��
TISHOU_ITEM_NAME						= 5     # ��Ʒ����
TISHOU_ITEM_METIER						= 6     # ��Ʒְҵ
TISHOU_PET_LOWERLEVEL					= 7     # ����ȼ�����
TISHOU_PET_UPPERLEVEL					= 8     # ����ȼ�����
TISHOU_PET_ERALIMIT						= 9     # �ڼ�������
TISHOU_PET_GENDERLIMIT					= 10    # �����Ա�
TISHOU_PET_METIERLIMIT					= 11    # ����ְҵ
TISHOU_PET_BREEDLIMIT					= 12    # ���ﷱֳ���
TISHOU_OWNER_NAME						= 13	# ������������


# --------------------------------------------------------------------
# �д����
# --------------------------------------------------------------------
QIECUO_REQUEST_MAXDIS					= 10.0	# �д�˫������������
QIECUO_REQUEST_TIME						= 15.0	# �д�����ʱ������
QIECUO_HP_NOT_FULL						= 10.0	# �д�����Ѫ��������ʾʱ������


QIECUO_REQUEST_SAY_MSGS	= [ cschannel_msgs.POTENTIAL_VOICE27,
							cschannel_msgs.POTENTIAL_VOICE28,
							cschannel_msgs.POTENTIAL_VOICE29,
							]
QIECUO_WIN_SAY_MSGS = [	cschannel_msgs.POTENTIAL_VOICE30,
							cschannel_msgs.POTENTIAL_VOICE31,
							cschannel_msgs.POTENTIAL_VOICE32,
							]
QIECUO_LOSE_SAY_MSGS = [ cschannel_msgs.POTENTIAL_VOICE33,
							cschannel_msgs.POTENTIAL_VOICE34,
							cschannel_msgs.POTENTIAL_VOICE35,
							]

QIECUO_WIN_SAY_MSGS = [
	cschannel_msgs.POTENTIAL_VOICE30,
	cschannel_msgs.POTENTIAL_VOICE31,
	cschannel_msgs.POTENTIAL_VOICE32,
	]

QIECUO_LOSE_SAY_MSGS = [
	cschannel_msgs.POTENTIAL_VOICE33,
	cschannel_msgs.POTENTIAL_VOICE34,
	cschannel_msgs.POTENTIAL_VOICE35,
	]

# --------------------------------------------------------------------
# ���۽�����Ʒ����
# --------------------------------------------------------------------
TI_SHOU_WEAPON					= 1		#����
TI_SHOU_ARMOR					= 2		#����
TI_SHOU_PRODUCE_STUFF			= 3		#��������
TI_SHOU_TYPE_NONE				= 4		#��

# --------------------------------------------------------------------
# ���۽�����Ʒְҵ
# --------------------------------------------------------------------
TI_SHOU_CLASS_FIGHTER							= 'Z'		# սʿ
TI_SHOU_CLASS_SWORDMAN							= 'J'		# ����
TI_SHOU_CLASS_ARCHER							= 'S'		# ����
TI_SHOU_CLASS_MAGE								= 'F'		# ��ʦ


#����NPC className
TISHOU_NPC_CLASSNAME	= "10111314"
 # С���� className
EIDOLON_NPC_CLASSNAME	= "10111574"
AUTO_CREATE_EIDOLON_NPC_LEVEL	= 30	# �Զ�������ٻ�С����ļ�������
VIP_EIDOLON_LIVE_TIME			= 300	# vipС����Ĵ��ʱ��

#�㿨��ѯҳ���С
POINT_CARD_PAGE_SIZE			 = 10


#����NPC ģ��
TI_SHOU_MODEL_1			= "gw1189_2"
TI_SHOU_MODEL_2			= "gw1141_3"
TI_SHOU_MODEL_3			= "gw1141_2"
TI_SHOU_MODEL_4			= "gw1181_1"
TI_SHOU_MODEL_5			= "gw1157_3"
TI_SHOU_MODEL_6			= "gw1179_2"
TI_SHOU_MODEL_7			= "gw1180_1"


#���������
g_spaceCopyReviveDict = {	"fu_ben_zu_dui_jing_ji_chang"	: [( -0.918, 5.112, 104.200 ), ( -2.389, 4.678, -60.276 ), ( 71.558, 4.679, 16.489 ), ( -78.512, 4.667, 16.665 )],
							"shuijing" 						: [( 15.221, 19.823, -21.644 )],
							"fu_ben_wu_yao_wang_bao_zang"	: [( 10.266, -1.189, -89.028 )],
							"fu_ben_shen_gui_mi_jing"		: [( -8.563, 0.376, -53.970 )],
							"fu_ben_exp_melee"				: [( 24.643, 0.832, 46.112 )],
							"fu_ben_zheng_jiu_ya_yu"		: [( 6.36, 0.79, 5.22 )],
							"fu_ben_wu_yao_qian_shao"		: [( 131.505, 1.91, -96.102)],
							"gumigong"						: [( 20.165, 19.608, 55.613  )],
							"fu_ben_xuan_tian_huan_jie"		: [( 25.643, 0.832, 46.112 )],
							"fu_ben_xie_long_dong_xue"		: [( 140.787, 6.81, -72.596 )],
							"fu_ben_dao_yu"					: [( -54.133,2.969,-9.093 )],
							"fu_ben_shan_gu"				: [( 130.274,0.107,46.777 )],
							"fu_ben_shi_di"					: [( 124.629,-6.033,-41.09 )],
							"fu_ben_li_hen_shan_lin_001"	: [( 144.115,10.874,99.046 )],
							"fu_ben_ran_hun_shan_gu"		: [( 9.319,21.195,136.531 )],
							"fu_ben_shan_ding"				: [( -42.903,41.999,52.702 )],
							"fu_ben_feng_hua_jue_gu"		: [( -81.178,-0.47,-89.513 )],
							"fu_ben_lin_di"					: [( -27.765,2.882,101.489 )],
							"fu_ben_liu_sha_mi_cheng_001"	: [( 116.182,8.431,34.0 )],
							"fu_ben_tian_xiang_xue_ling"	: [( -44.838,-1.544,-118.647 )],
							"fu_ben_hun_dun_ru_qin"			: [( 46.457, 15.896, 84.152 )],
							"fu_ben_tian_jiang_qi_shou"		: [( -14.324, 4.279, 30.427 )],
							"fu_ben_du_du_zhu"				: [( -26.895, -2.187, -103.997 )],
							"fu_ben_feng_jian_shen_gong"	: [( 0, 0, 0)],
							"fu_ben_ge_ren_jing_ji_chang"	: [( -34.304474, 9.010988, -14.443275 ), ( -11.973862, 9.010985, -8.718079 ), ( -2.413582, 9.010985, -17.638672 ), ( -3.514259, 4.570011, -42.833721 ), ( -53.601414, 4.752189, -33.626236 ), ( -33.702850, 9.011001, 47.945988 ), ( -12.906525, 9.010993, 41.236683 ), ( -28.065475, 9.010985, 3.996282 ), ( -27.746368, 9.010993, 24.071093 ), ( -1.464996, 9.010985, 51.149097 ), ( -37.899731, 9.010985, 13.585574), ( -2.240967, 9.010993, 30.676607 ), ( -2.264381, 9.010997, 4.548246 ), ( -13.552719, 9.010989, 16.481108 ), ( -3.347694, 4.590103, 76.450493 ), ( -61.682640, 4.610000, 16.451010 ), ( -53.323135, 4.569999, 65.047829 ), ( 26.788765, 9.010986, -14.379707 ), ( 6.705331, 9.010985, -7.365448 ), ( 47.821335, 4.569999, -35.815308 ), ( 27.854292, 9.010985, 47.844902 ), ( 13.128451, 9.010985, 41.063583 ), ( 23.052652, 9.010978, 26.031006 ), ( 23.884405, 9.010985, 5.178188 ), ( 31.260454, 9.010985, 15.645858 ), ( 7.899153, 9.010989, 16.575697 ), ( 56.847187, 4.571655, 17.315851 ), ( 45.869755, 4.632308, 66.260468 )],
							"fu_ben_jia_zu_jing_ji_chang"	: [( -0.918, 5.112, 104.200 ), ( -2.389, 4.678, -60.276 ), ( 71.558, 4.679, 16.489 ), ( -78.512, 4.667, 16.665 )],
							"fu_ben_tian_guan_02"			: [( -286, 40, 9 )],
							"fu_ben_feng_jian_shen_gong"	: [( -146, 1, 5)],
							"fu_ben_she_hun_mi_zhen"		: [( 139, 49, -141 )],
							"fu_ben_shi_tu_fu_ben"		: [( -116.682, 9.978, -48.342 )],
							"fu_ben_kua_fu_shen_dian"		: [( 60.049, 24.756, 150.834 )],
							"fu_ben_qian_shi"				: [( 15.625, -5.093, 0.583 )],
							"fu_ben_plot_lv40"				: [( -61.646,23.969,182.113 )],
							"fu_ben_hua_shan_001"			: [(-246.272, 15.371, -20.439)],
							"fu_ben_hua_shan_002"			: [(-110.712, 18.559, 17.424)],
							"fu_ben_hua_shan_003"			: [(2.630, 10.259, 27.98)],
							"fu_ben_hua_shan_004"			: [(188.766, 0.111, -77.213)],
							"fu_ben_hua_shan_pi_shan"		: [(140.907, 35.768, -26.083)],
							"ying_xiong_lian_meng_01"		: [(-201.734, 15.928, -147.079)],
							"ying_xiong_lian_meng_pvp"		: [(-201.734, 15.928, -147.079), (50.887, 16.076, 105.075)],
							"fu_ben_bang_hui_che_lun_zhan"	: [( 0, 0, 0)],
							"fu_ben_ye_zhan_feng_qi"		: [( 0, 0, 0)],
							"fu_ben_bang_hui_feng_huo_lian_tian" : [( 0, 0, 0)],
						}


# ֻ���ڸ�������NPC����ĵ�ͼ
COPY_REVIVE_PREVIOUS = [
	"xin_ban_xin_shou_cun_10",
	"fu_ben_xin_shou_cun_10",
	"feng_ming_20_dao",
	"feng_ming_20_mo",
	"xin_fei_lai_shi_001_25_dao",
	"xin_fei_lai_shi_001_30_dao",
	"zly_ban_quan_xiang_36_dao",
	"zly_ban_quan_xiang_34_mo",
	"zly_ying_ke_cun_45_dao",
	"zly_ying_ke_cun_45_mo",
	"fu_ben_xin_shou_cun_54_dao",
	"fu_ben_xin_shou_cun_54_mo",
	"zly_ban_quan_xiang_36_mo",
	"xin_ban_xin_shou_cun_7",
	"fu_ben_xin_shou_cun_7",
]

IMAGE_VERIFY_TIME_MAP = { 1:180, 2:60, 3:60 }		# �������֤�ִζ�Ӧ�Ļش�����ʱ��


#�ռ�ϵͳ
COLLECTION_BAG_SIZE		= 20


TONG_CITYWAR_CITY_MAPS = {	"zly_ban_quan_xiang":	cschannel_msgs.MAP_JIU_HE_DU,
							"zly_bi_shi_jian":		cschannel_msgs.MAP_BI_SHI_JIAN,
							"yun_meng_ze_01":		cschannel_msgs.MAP_QING_NIAO_YI,
							"yun_meng_ze_02":		cschannel_msgs.MAP_WU_MIAO_ZHAI,
							"fengming":				cschannel_msgs.MAP_FENGMINGCHENG,
							"xin_fei_lai_shi_001":	cschannel_msgs.MAP_FEI_LAI_SHI,
							"kun_lun":				cschannel_msgs.MAP_TAI_A_CHENG,
							"xin_ban_xin_shou_cun":	cschannel_msgs.MAP_YIN_SHA_CHUN,
							"peng_lai":				cschannel_msgs.MAP_DONG_HUA_ZI_FU,
						}


CAMP_CITYWAR_CITY_MAPS = {	"zly_ban_quan_xiang":	cschannel_msgs.MAP_JIU_HE_DU,
							"zly_bi_shi_jian":		cschannel_msgs.MAP_BI_SHI_JIAN,
							"yun_meng_ze_01":		cschannel_msgs.MAP_QING_NIAO_YI,
							"yun_meng_ze_02":		cschannel_msgs.MAP_WU_MIAO_ZHAI,
							"fengming":				cschannel_msgs.MAP_FENGMINGCHENG,
							"xin_fei_lai_shi_001":	cschannel_msgs.MAP_FEI_LAI_SHI,
							"kun_lun":				cschannel_msgs.MAP_TAI_A_CHENG,
							"xin_ban_xin_shou_cun":	cschannel_msgs.MAP_YIN_SHA_CHUN,
							"peng_lai":				cschannel_msgs.MAP_DONG_HUA_ZI_FU,
						}



TONG_CITYWAR_SIGNUP_MAX  = 8 # ������ս�����������


#�������� by ����
USER_TONG_SIGN_REQ_MONEY = 2000000
USER_TONG_SIGN_REQ_TONG_LEVEL = 3


#��������ʼ����ͽ���ʱ��
END_TIME			  	= 120				# 120��	��������н�ɫ�߳�����
SAVE_MODEL_TIME			= 300				# 300��

#���˾����ʱ��
ROLE_COMPETITION_TIME	= 1800				# 1800�루30���ӣ��ĸ��˾���ʱ��

#���徺���ʱ��
FAMILY_COMPETITION_TIME = 3600				# 3600�루60���ӣ��ļ��徺��ʱ��


#��Ӿ����ʱ��
TEAM_COMPETITION_TIME = 1800				# 1800�루30���ӣ��ļ��徺��ʱ��

#��Ὰ������
TONG_COMPETITION_AWARD01 = 10381522			# ��Ὰ�����齱��
TONG_COMPETITION_AWARD02 = 5059136			# ��Ὰ��Ǳ�ܽ���

CHALLENGE_CHAMPION_REWARD_LIVING = 7 * 24 * 60 *60 # �������ھ������ı���ʱ��( һ������ )
TONG_CITY_WAR_CHAMPION_REWARD_LIVING = 7 * 24 * 60 * 60 # ������ս��ھ���������ʱ��( һ������ )

#����Objectģ�͸��ĺ�׺
TOUCH_OBJECT_MODELNUM 	= "_on"

C_PREFIX_GBAE					= "GBAE"	# baseApp enitytע�ᵽȫ�ֱ�����keyǰ׺���㲥ȫ����Ϣʱ��cellҲ��ʹ�ô˶��塣11:06 2010-4-20��wsf


#------------ItemAwards ���������Ʒ���
AWARDITEM_ACCOUNT	= 1		# ͨ���˺Ż�ȡ��ҵ���Ʒ����
AWARDITEM_NAME		= 2		# ͨ��������ֻ�ȡ��ҵ���Ʒ����
AWARDITEM_ORDER		= 3		# ͨ�������Ż�ȡ��ҵ���Ʒ����
AWARDITEM_ANO			= 4		# ͨ�������� ������� �˺� ��ȡ����

OLD_REWARD_LEVEL_LIM = 60		# ��������߽�����ȡ�ȼ�����


#----------�ǳ�����------------------
ANONYMITY_LOVE_MSG_PAY	= 50000				#�������������
LOVE_MSG_PAY			= 5000				#��ͨ�������
FCWR_MSGS_LENGTH			= 22			#һ�λ�ȡ�����Ŀ��
FCWR_LOVE_MSG_MIN_LENGTH	= 10			#�����������
FCWR_LOVE_MSG_MAX_LENGTH	= 200			#����������

FCWR_VOTE_SPEED				= 1800			#ͶƱ���ʱ��

FCWR_REWARDS = { csdefine.FCWR_VOTE_ALL 			: [60101151,110103038],		#������Ŀ�ƺ� + ��������
				csdefine.FCWR_VOTE_KAN_HAO			: [60101155,110103038],		#����һ�Գƺ� + ��������
				csdefine.FCWR_VOTE_QING_DI			: [60101152,110103038],		#�������˳ƺ� + ��������
				csdefine.FCWR_VOTE_SHI_LIAN			: [60101153,110103038],		#�������˳ƺ� + ��������
				csdefine.FCWR_MAX_COUNT_VOTER_1		: [60101154,110103041],		#��Ѫ������ + 500Ԫ��
				csdefine.FCWR_MAX_COUNT_VOTER_2		: [60101154,110103042],		#��Ѫ������ + 250Ԫ��
				csdefine.FCWR_MAX_COUNT_VOTER_3		: [60101154,110103043],		#��Ѫ������ + 100Ԫ��
					}

# --------------------------------------------------------------------
# ���������
# --------------------------------------------------------------------
FRUIT_PICK_DISTANCE						= 5.0		# ���������ɼ�����
FRUIT_PLANT_DISTANCE					= 4.0		# ����������ֲ���

# --------------------------------------------------------------------
# װ�����Գ�ȡ
# --------------------------------------------------------------------
EQUIP_EXTRACT_QUALITYS = [ ItemTypeEnum.CQT_BLUE, ItemTypeEnum.CQT_GOLD, ItemTypeEnum.CQT_PINK, ItemTypeEnum.CQT_GREEN ]	# װ����ȡƷ�ʶ���
EQUIP_EXTRACT_LEVEL_MIN	= 10												# װ����ȡװ������ȼ�
EQUIP_EXTRACT_NEEDITEMS = 60101174											# װ����ȡ�������ʯ
EQUIP_EXTRACT_ITEM_ODDS = 0.3												# װ����ȡ�������ʯ�ɹ�����
EQUIP_EXTRACT_SUNEEDITEMS = 60101175 										# װ����ȡ���󳬼�����ʯ
EQUIP_EXTRACT_SUITEMS_ODDs = 0.45											# װ����ȡ���󳬼�����ʯ�ɹ�����
EQUIP_EXTRACT_PROITEM = 60101176											# װ����ȡ�ɹ�������������
EQUIP_EXTRACT_EXCITEM = 60101177											# װ����ȡ���ӳɹ�����ƷID
EQUIP_EXTRACT_EXCITEM_ODDS = 1.0											# װ����ȡ������Ʒ�ɹ���
EQUIP_POURE_ATTR_SAME_COUNT = 2

# --------------------------------------------------------------------
# װ������
# --------------------------------------------------------------------
EQUIP_UP_RATE = 0.9															# װ���ɹ������ļ���
EQUIP_UP_EXTRA_SLOT_RATE = 0.03												# ����ʱ�����ڶ������Կ�λ�ļ���
EQUIP_UP_BASE_LEVEL = 60													#С����������װ���޷�����



# --------------------------------------------------------------------
# װ����������
# --------------------------------------------------------------------
EQUIP_ATTR_REBUILD_LEVEL = 30													# װ��������������ͼ���
EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR = 0.2										# һ�����Լ�ֵ����ռװ����ֵ���ӵİٷֱ�
EQUIP_ATTR_REBUILD_STAGES = 10													# װ�����������Ľ״�

#---------------------------------------------------------------------
#�丸���(entity ����)
#---------------------------------------------------------------------
KUA_FU_ENTITY_TYPE_NPC		= 0				#NPC
KUA_FU_ENTITY_TYPE_MONSTER	= 1				#С��
KUA_FU_ENTITY_TYPE_BOSS		= 2				#BOSS
KUA_FU_ENTITY_TYPE_STONE	= 3				#ʯ��
KUA_FU_ENTITY_TYPE_TRAP		= 4				#����
KUA_FU_ENTITY_TYPE_ICE		= 5				#����
KUA_FU_ENTITY_TYPE_DOOR		= 6				#��
KUA_FU_ENTITY_TYPE_SHITI	= 7				#ʬ��
KUA_FU_ENTITY_TYPE_TREE		= 8				#����


KUA_FU_EVENT_JUBI_FLY_TO_SKY		= 1										#�ݱȷ������
KUA_FU_EVENT_SPAWN_TO_DEADBODY		= 2										#ˢ��������ʬ
KUA_FU_EVENT_CENTER_FIRE_FLY_TO_SKY	= 3										#�������Ļ���������
KUA_FU_EVENT_FEILIAN_KUI_DI			= 4										#�������
KUA_FU_EVENT_STONE_DESTROY			= 5										#ʯ�񱻴ݻ�
KUA_FU_EVENT_ZHAO_CHONGZHI			= 6										#��С����
KUA_FU_EVENT_XUANFENG				= 7										#��������
KUA_FU_EVENT_TAOZHI					= 8										#��������
KUA_FU_EVENT_HOU_QING				= 9										#�������



KUA_FU_ACTIVITY_TIME				= 3600				#�丸���ʱ��

#---------------------------------------------------------------------
#С�ÿ���(entity ����)
#---------------------------------------------------------------------
#ˢ�µ�
RABBIT_RUN_ENTITY_TYPE_NPC							= 0
RABBIT_RUN_ENTITY_TYPE_ROAD_POINT					= 1

RABBIT_RUN_ITEM_RADISH								= 50101160				#���������
RABBIT_RUN_CATCH_RABBIT_SKILL_ID					= 344012001				#ץС�ü���ID
RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID 				= 34401200101			#����Ϊ���ӵ�BUFF ID
RABBIT_RUN_CATCH_RABBIT_WOLF_BUFF_ID				= 34401200102			#����Ϊ�ǵ�BUFF ID
RABBIT_RUN_WAIT_BUFF_ID								= 34402100101			#�ȴ����ʼBUFF ID
RABBIT_RUN_CANT_MOVE_BUFF_ID						= 34402400101			#����BUFF ID
RABBIT_RUN_QUESTION_BUFF_ID							= 34402000101			#�ش�����BUFF ID

#��ұ���Ϊ�ǻ����ӵ�ʱ�䣨�������ܿ�ʼ��
RABBIT_RUN_TIME_TO_CHANGE_BODY						= 30					#��λ���룩
RABBIT_RUN_WAIT_TIME								= 180					# С�ÿ��ܵȴ�ʱ��
RABBIT_RUN_CANT_ENTER_TIME							= 60					# С�ÿ��ܲ��������ʱ�䣨������ʼ��

RABBIT_RUN_NEED_PLAYER_AMOUNT						= 10						#�������Ҫ���ٲμ��������
RABBIT_RUN_WOLF_CONTROL_NUM							= 5						#�ǵĳ��ֿ�������

RABBIT_RUN_ACTIVITY_TIME							= 1800					#�ʱ��

RABBIT_RUN_NPC_REVIDE_MIN_TIME						= 0						#NPC�������ʱ��
RABBIT_RUN_NPC_REVIDE_MAX_TIME						= 120					#NPC�����ʱ��

RABBIT_RUN_POINT_TRAP_RANGE							= 30					#·�������С


# -------------------------------------------------------------
# ��ʱ���� ʱ���ϵ���������� �ݴ�������
# -------------------------------------------------------------
DROP_TASKEVENTS = {
		"LuckyBoxActivity_start" : {
						"LuckyBoxActivity_start_notice" : "onStartLuckyBoxNotice",
						"LuckyBoxActivity_start" : "onStartLuckyBox",
						"LuckyBoxActivity_end" : "onEndLuckyBox",
					  },
		"MidAutumnActivity_start" : {
						"MidAutumnActivity_start_notice" : "onStartMidAutNotice",
						"MidAutumnActivity_start" : "onStartMidAut",
						"MidAutumnActivity_end" : "onEndMidAut",
					},
		}

# -------------------------------------------------------------
# ������������������ָ���ļ���ID
# -------------------------------------------------------------
EQUIP_EFFECT_ADD_ODDS_SKILL1 	= 311413			# ���
EQUIP_EFFECT_ADD_ODDS_SKILL2 	= 311101			# �ͻ�
EQUIP_EFFECT_ADD_ODDS_SKILL3 	= 311104			# ��ɨ
EQUIP_EFFECT_ADD_ODDS_SKILL4	= 321207			# ̩ɽѹ��
EQUIP_EFFECT_ADD_ODDS_SKILL5 	= 311120			# ����
EQUIP_EFFECT_ADD_ODDS_SKILL6 	= 311123			# ����
EQUIP_EFFECT_ADD_ODDS_SKILL7 	= 321210			# ����
EQUIP_EFFECT_ADD_ODDS_SKILL8 	= 311114			# �콣
EQUIP_EFFECT_ADD_ODDS_SKILL9 	= 311117			# ���ལ
EQUIP_EFFECT_ADD_ODDS_SKILL10 	= 321208			# ׷�����
EQUIP_EFFECT_ADD_ODDS_SKILL11 	= 312109			# ������
EQUIP_EFFECT_ADD_ODDS_SKILL12 	= 312111			# �����
EQUIP_EFFECT_ADD_ODDS_SKILL13 	= 322445			# ������

# -------------------------------------------------------------
# ����������������
# -------------------------------------------------------------
EQUIP_EFFECT_FLAW_LIMIT			= 3					# ���������������ӵ����

GOD_WEAPON_NAME_COLOR			= (255.0,0.0,0.0)	# ����������ɫ by ����

MAX_FLYING_SPEED_INC_PERCENT	= 200.0				# ������������ٶ�����ٷֱ�

# --------------------------------------------------------------------
# װ���;�����ֵ
# --------------------------------------------------------------------
EQUIP_HARDINESS_UPDATE_VALUE = 10000.0


# --------------------------------------------------------------------
# ���ھ�����������
# --------------------------------------------------------------------
TRANSMIT_TYPE_WUDAO				 = 1
TRANSMIT_TYPE_TEAM_CHALLENGE 	 = 2
TRANSMIT_TYPE_TONG_ABA			 = 3
TRANSMIT_TYPE_TEAM_COMPETITION	 = 4
TRANSMIT_TYPE_TONG_COMPETITION	 = 5
TRANSMIT_TYPE_ROLE_COMPETITION   = 6
TRANSMIT_SPACE_INFOS = {
	TRANSMIT_TYPE_WUDAO				 : ( "fengming", ( 187.675, 10.5, 173 ), (0.000000, 0.000000, -1.5707963 ) ),
	TRANSMIT_TYPE_TEAM_CHALLENGE	 : ( "fengming", ( 187.675, 10.5, 177 ), (0.000000, 0.000000, -1.5707963 ) ),
	TRANSMIT_TYPE_TONG_ABA			 : ( "fengming", ( 218.687, 10.5, 159.349 ), (0.000000, 0.000000, 1.5707963 ) ),
	TRANSMIT_TYPE_TEAM_COMPETITION	 : ( "fengming", ( 187.675, 10.5, 165 ), (0.000000, 0.000000, -1.5707963 ) ),
	TRANSMIT_TYPE_TONG_COMPETITION	 : ( "fengming", ( 212.033, 10.5, 163.713 ), (0, 0, 0 ) ),
	TRANSMIT_TYPE_ROLE_COMPETITION	 : ( "fengming", ( 187.675, 10.5, 169 ), (0.000000, 0.000000, -1.5707963 ) ),
}


# --------------------------------------------------------------------
# ��ɽ��/��ս����
# --------------------------------------------------------------------
HUA_SHAN_PI_SHAN_GATE = 400
SPACE_CHALLENGE_TYPE_SINGLE = 1
SPACE_CHALLENGE_TYPE_MANY	= 2

SPACE_CHALLENGE_SHOW_TYPE_DEFAULT = 1
SPACE_CHALLENGE_SHOW_TYPE_RESERVE = 2

CHALLENGE_AVATAR_LIST = {
	csdefine.CLASS_FIGHTER		: "chiyou",
	csdefine.CLASS_SWORDMAN		: "huangdi",
	csdefine.CLASS_ARCHER		: "houyi",
	csdefine.CLASS_MAGE			: "nuwo",
	}

# --------------------------------------------------------------------
# NPC��Ļ���뺰����Χ�޶�
# --------------------------------------------------------------------
CHAT_CHANNEL_SC_HINT_AREA = 50							# NPC��Ļ���뺰����Χ

# --------------------------------------------------------------------
# Ұ�⸱��
# --------------------------------------------------------------------
SPACE_COPY_YE_WAI_EASY 			= 0
SPACE_COPY_YE_WAI_DIFFICULTY	= 1
SPACE_COPY_YE_WAI_NIGHTMARE		= 2

SPACE_COPY_YE_WAI_ENTER_MAP = {
	SPACE_COPY_YE_WAI_EASY			: 1,
	SPACE_COPY_YE_WAI_DIFFICULTY	: 3,
	SPACE_COPY_YE_WAI_NIGHTMARE		: 5,
}

# �����ս���ٻ��ั��
ROLE_CALL_PGNAGUAL_LIMIT_EASY			= 12 					# ���˸�����ҿ����ٻ����̹��ػ�����
ROLE_CALL_PGNAGUAL_LIMIT_DIFFICULT		= 8						# ���˸�����ҿ����ٻ����̹��ػ�����
ROLE_CALL_PGNAGUAL_LIMIT_NIGHTMARE		= 5						# ���˸�����ҿ����ٻ����̹��ػ�����

# �̹��ػ�ϵͳ�����й�����
ROLE_CALL_PGNAGUAL_LIMIT				= 12 					# ��ҿ����ٻ��̹��ػ�������

# ������
WALLOW_STATES = set( [
	csdefine.WALLOW_STATE_COMMON,
	csdefine.WALLOW_STATE_HALF_LUCRE,
	csdefine.WALLOW_STATE_NO_LUCRE
	] )										# ��������״̬

# �� base �г�ʼ���Ľ�ɫ����
ROLE_INIT_BASES = [ \
	csdefine.ROLE_INIT_OPRECORDS,
	csdefine.ROLE_INIT_PETS,
	csdefine.ROLE_INIT_QUICK_BAR,
	csdefine.ROLE_INIT_VEHICLES,
	csdefine.ROLE_INIT_OFLMSGS,
	csdefine.ROLE_INIT_DAOFA,
	]

# �� cell �г�ʼ���Ľ�ɫ����
ROLE_INIT_CELLS = ( \
	csdefine.ROLE_INIT_KITBAGS,
	csdefine.ROLE_INIT_ITEMS,
	csdefine.ROLE_INIT_COMPLETE_QUESTS,
	csdefine.ROLE_INIT_QUEST_LOGS,
	csdefine.ROLE_INIT_SKILLS,
	csdefine.ROLE_INIT_BUFFS,
	csdefine.ROLE_INIT_COLLDOWN,
	csdefine.ROLE_INIT_PRESTIGE,
	csdefine.ROLE_INIT_REWARD_QUESTS,
	)

ENTITY_TYPE_ALL						= [
		csdefine.ENTITY_TYPE_ROLE,
		csdefine.ENTITY_TYPE_NPC,
		csdefine.ENTITY_TYPE_MONSTER,
		csdefine.ENTITY_TYPE_PET,
		csdefine.ENTITY_TYPE_PREVIEWROLE,
		csdefine.ENTITY_TYPE_DROPPED_ITEM,
		csdefine.ENTITY_TYPE_DROPPED_BOX,
		csdefine.ENTITY_TYPE_SPACE_DOOR,
		csdefine.ENTITY_TYPE_SPACE_TRANSPORT,
		csdefine.ENTITY_TYPE_SPACE_ENTITY,
		csdefine.ENTITY_TYPE_WEATHER_SYSTEM,
		csdefine.ENTITY_TYPE_QUEST_BOX,
		csdefine.ENTITY_TYPE_PROXIMITY_TRANSDUCER,
		csdefine.ENTITY_TYPE_SPACE_GATE,
		csdefine.ENTITY_TYPE_SLAVE_MONSTER,
		csdefine.ENTITY_TYPE_MISC,
		csdefine.ENTITY_TYPE_TREASURE_MONSTER,
		csdefine.ENTITY_TYPE_CONVOY_MONSTER,
		csdefine.ENTITY_TYPE_VEHICLE,
		csdefine.ENTITY_TYPE_VEHICLE_DART,
		csdefine.ENTITY_TYPE_YAYU,
		csdefine.ENTITY_TYPE_SERVER_ENTITY,
		csdefine.ENTITY_TYPE_COLLECT_POINT,
		csdefine.ENTITY_TYPE_FRUITTREE,
		csdefine.ENTITY_TYPE_CHALLENGE_TRANSDUCER,
		csdefine.ENTITY_TYPE_CALL_MONSTER,
		csdefine.ENTITY_TYPE_SPACE_CHALLENGE_DOOR,
		csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER,
		csdefine.ENTITY_TYPE_CITY_MASTER,
		csdefine.ENTITY_TYPE_PANGU_NAGUAL,
		csdefine.ENTITY_TYPE_NPC_FORMATION,
		csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM,
	]

# �ɱ����ѡ�е� entities
ENTITIES_CAN_BE_SELECTED 			= [
	csdefine.ENTITY_TYPE_ROLE,
	csdefine.ENTITY_TYPE_PET,
	csdefine.ENTITY_TYPE_NPC,
	csdefine.ENTITY_TYPE_MONSTER,
	csdefine.ENTITY_TYPE_QUEST_BOX,
	csdefine.ENTITY_TYPE_SPACE_GATE,
	csdefine.ENTITY_TYPE_SLAVE_MONSTER,
	csdefine.ENTITY_TYPE_MISC,
	csdefine.ENTITY_TYPE_TREASURE_MONSTER,
	csdefine.ENTITY_TYPE_VEHICLE,
	csdefine.ENTITY_TYPE_SPACE_DOOR,
	csdefine.ENTITY_TYPE_VEHICLE_DART,
	csdefine.ENTITY_TYPE_YAYU,
	csdefine.ENTITY_TYPE_COLLECT_POINT,
	csdefine.ENTITY_TYPE_FRUITTREE,
	csdefine.ENTITY_TYPE_CALL_MONSTER,
	csdefine.ENTITY_TYPE_SPACE_CHALLENGE_DOOR,
	csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER,
	csdefine.ENTITY_TYPE_PANGU_NAGUAL,
	csdefine.ENTITY_TYPE_NPC_FORMATION,
	csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM,
	]

ACTFBLIST = (
	csdefine.ACTION_FORBID_MOVE, csdefine.ACTION_FORBID_CHAT, csdefine.ACTION_FORBID_USE_ITEM, csdefine.ACTION_FORBID_WIELD, csdefine.ACTION_FORBID_ATTACK, csdefine.ACTION_FORBID_PK,
	csdefine.ACTION_FORBID_SPELL_PHY, csdefine.ACTION_FORBID_SPELL_MAGIC, csdefine.ACTION_FORBID_TRADE, csdefine.ACTION_FORBID_FIGHT, csdefine.ACTION_ALLOW_VEND, csdefine.ACTION_FORBID_JUMP ,
	csdefine.ACTION_FORBID_CALL_PET, csdefine.ACTION_FORBID_TALK, csdefine.ACTION_FORBID_VEHICLE, csdefine.ACTION_ALLOW_DANCE, csdefine.ACTION_FORBID_INTONATING, csdefine.ACTION_FORBID_CHANGE_MODEL
	)

ACTFBMASK =	[ 0,																																												# STATE_FREE
			  csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_JUMP \
			  | csdefine.ACTION_FORBID_TALK | csdefine.ACTION_FORBID_VEHICLE,																																		# ENTITY_STATE_DEAD
			  csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_TRADE,																							# ENTITY_STATE_REST
			  csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_TRADE,																																		# ENTITY_STATE_FIGHT
			  csdefine.ACTION_FORBID_CHAT | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_TRADE \
			  | csdefine.ACTION_FORBID_PK | csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_TALK,																							# ENTITY_STATE_PENDING
			  csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_CHAT | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_JUMP,	# ENTITY_STATE_HANG
			  csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_FIGHT \
			  | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE,																											# ENTITY_STATE_VEND
			  csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK  | csdefine.ACTION_FORBID_TRADE	| csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE,																# ENTITY_STATE_RACER
			  csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK  | csdefine.ACTION_FORBID_TRADE	| csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE,																# ENTITY_STATE_CHANGING
			  csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_CHAT | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_TRADE \
			  | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_PK | csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_TALK,																							# ENTITY_STATE_QUIZ_GAME
			  csdefine.ACTION_FORBID_ATTACK  | csdefine.ACTION_FORBID_TRADE	| csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC \
			  | csdefine.ACTION_FORBID_WIELD,																																							# ENTITY_STATE_DANCE
			  csdefine.ACTION_FORBID_ATTACK  | csdefine.ACTION_FORBID_TRADE	| csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC \
			  | csdefine.ACTION_FORBID_WIELD,																																							# ENTITY_STATE_REQUEST_DANCE
			  csdefine.ACTION_FORBID_ATTACK  | csdefine.ACTION_FORBID_TRADE	| csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC \
			  | csdefine.ACTION_FORBID_WIELD,																																							# ENTITY_STATE_DOUBLE_DANCE
			  0,																																												# ENTITY_STATE_ENVIRONMENT_OBJECT
			  0,
			 ]

# ���塢ְҵ���Ա𼯺�
ALL_GENDERS 							= ( csdefine.GENDER_MALE, csdefine.GENDER_FEMALE )
ALL_PROFESSIONS 						= ( csdefine.CLASS_FIGHTER, csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER, csdefine.CLASS_MAGE )
ALL_RACES 								= ( csdefine.YANHUANG, csdefine.JIULI, csdefine.FENGMING )

# ��ְͬҵ�ĳ����㣨�������ڵأ�
RACE_CLASS_MAP = {}
RACE_CLASS_MAP[csdefine.CLASS_FIGHTER]				= csdefine.FENGMING
RACE_CLASS_MAP[csdefine.CLASS_SWORDMAN]				= csdefine.FENGMING
RACE_CLASS_MAP[csdefine.CLASS_ARCHER]				= csdefine.FENGMING
RACE_CLASS_MAP[csdefine.CLASS_MAGE]					= csdefine.FENGMING

OPRECORD_ALL_RECORDS = (
	csdefine.OPRECORD_COURSE_HELP,
	csdefine.OPRECORD_UI_TIPS,
	csdefine.OPRECORD_PIXIE_HELP,
	)														# ȫ����¼����

BASE_SKILL_TYPE_SPELL_LIST				= [ csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL, csdefine.BASE_SKILL_TYPE_PHYSICS, csdefine.BASE_SKILL_TYPE_MAGIC, csdefine.BASE_SKILL_TYPE_DISPERSION, csdefine.BASE_SKILL_TYPE_ELEM ]		# ��������
BASE_SKILL_INITIA_SPELL_LIST			= [ csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL, csdefine.BASE_SKILL_TYPE_PHYSICS, csdefine.BASE_SKILL_TYPE_MAGIC	]		# ��������
BASE_SKILL_TYPE_PASSIVE_SPELL_LIST		= [ csdefine.BASE_SKILL_TYPE_PASSIVE, csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE ]	# �������������б�

EFFECT_STATE_LIST = [ csdefine.EFFECT_STATE_SLEEP, csdefine.EFFECT_STATE_VERTIGO, csdefine.EFFECT_STATE_FIX, csdefine.EFFECT_STATE_HUSH_PHY, \
						csdefine.EFFECT_STATE_HUSH_MAGIC, csdefine.EFFECT_STATE_INVINCIBILITY, csdefine.EFFECT_STATE_NO_FIGHT, \
						csdefine.EFFECT_STATE_PROWL, csdefine.EFFECT_STATE_FOLLOW, csdefine.EFFECT_STATE_LEADER, csdefine.EFFECT_STATE_ALL_NO_FIGHT,\
						csdefine.EFFECT_STATE_WATCHER, csdefine.EFFECT_STATE_DEAD_WATCHER, csdefine.EFFECT_STATE_HEGEMONY_BODY, csdefine.EFFECT_STATE_BE_HOMING ]

SKILL_ID_ACTIONS = set( [
	#csdefine.SKILL_ID_PHYSICS,
	csdefine.SKILL_ID_SGL_DANCING,
	csdefine.SKILL_ID_DBL_DANCING,
	#csdefine.SKILL_ID_TEAM_DANCING,
	csdefine.SKILL_ID_FACE_DRINK,
	csdefine.SKILL_ID_FACE_BYE,
	csdefine.SKILL_ID_FACE_REFUSE,
	csdefine.SKILL_ID_FACE_DEFY,
	csdefine.SKILL_ID_FACE_KNEE,
	csdefine.SKILL_ID_FACE_TALK,
	csdefine.SKILL_ID_FACE_SMILE,
	csdefine.SKILL_ID_FACE_SIT,
	csdefine.SKILL_ID_FACE_LIE,
	] )													# ���������Ϊ����( �ŵ���Ϊ�����б��� )

# ��������˳�����ȼ�
# ����������ͨ���������ϻ��װ������װ��������������Ա��ⱻ����ɾ���Ŀ�����
KB_SEARCH_ALL = range( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ) + [ csdefine.KB_CASKET_ID, csdefine.KB_EQUIP_ID ]
# ����������ͨ���������ϻ
KB_SEARCH_COMMON_AND_CASKET = range( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ) + [ csdefine.KB_CASKET_ID, ]
# ����������ͨ����
KB_SEARCH_COMMON = range( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT )
# ֻ����װ����
KB_SEARCH_EQUIP = [ csdefine.KB_EQUIP_ID, ]

QUEST_OBJECTIVE_SUBMIT_TYPES = [
	csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY,
	csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT,
	csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT,
	csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL,
	csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED,
	csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO,
	csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP,
	csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY,
	csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY,
]

# -------------------------------------------
# Ƶ�� ID ��Ƶ������ӳ��
CHAT_CHID_2_NAME = {
	csdefine.CHAT_CHANNEL_NEAR			: ST.CHAT_CHANNEL_NEAR,				# ����
	csdefine.CHAT_CHANNEL_LOCAL			: ST.CHAT_CHANNEL_LOCAL,			# ����
	csdefine.CHAT_CHANNEL_TEAM			: ST.CHAT_CHANNEL_TEAM,				# ����
	csdefine.CHAT_CHANNEL_FAMILY			: ST.CHAT_CHANNEL_FAMILY,			# ����
	csdefine.CHAT_CHANNEL_TONG			: ST.CHAT_CHANNEL_TONG,				# ���
	csdefine.CHAT_CHANNEL_WHISPER		: ST.CHAT_CHANNEL_WHISPER,			# ����
	csdefine.CHAT_CHANNEL_WORLD			: ST.CHAT_CHANNEL_WORLD,			# ����
	csdefine.CHAT_CHANNEL_RUMOR			: ST.CHAT_CHANNEL_RUMOR,			# ҥ��
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: ST.CHAT_CHANNEL_WELKIN_YELL,		# ����
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: ST.CHAT_CHANNEL_TUNNEL_YELL,		# ����
	csdefine.CHAT_CHANNEL_PLAYMATE		: ST.CHAT_CHANNEL_PLAYMATE,			# ���
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : ST.CHAT_CHANNEL_TONG_CITY_WAR,	# ���ս��

	# GM/����Ƶ��
	csdefine.CHAT_CHANNEL_SYSBROADCAST	: ST.CHAT_CHANNEL_SYSBROADCAST,		# �㲥

	# NPC ����Ƶ��
	csdefine.CHAT_CHANNEL_NPC_SPEAK		: ST.CHAT_CHANNEL_NPC_SPEAK,		# NPC
	csdefine.CHAT_CHANNEL_NPC_TALK		: ST.CHAT_CHANNEL_NPC_TALK,			# NPC�Ի�

	# ϵͳ��ʾƵ��
	csdefine.CHAT_CHANNEL_SYSTEM			: ST.CHAT_CHANNEL_SYSTEM,			# ϵͳ
	csdefine.CHAT_CHANNEL_COMBAT			: ST.CHAT_CHANNEL_COMBAT,			# ս��
	csdefine.CHAT_CHANNEL_PERSONAL		: ST.CHAT_CHANNEL_PERSONAL,			# ����
	csdefine.CHAT_CHANNEL_MESSAGE		: ST.CHAT_CHANNEL_MESSAGE,			# ��Ϣ
	csdefine.CHAT_CHANNEL_SC_HINT		: ST.CHAT_CHANNEL_SC_HINT,			# ��Ļ
	csdefine.CHAT_CHANNEL_MSGBOX			: ST.CHAT_CHANNEL_MSGBOX,			# ��ʾ
	csdefine.CHAT_CHANNEL_MSGBOX			: ST.CHAT_CHANNEL_MSGBOX,			# ��ʾ
	csdefine.CHAT_CHANNEL_CAMP			: ST.CHAT_CHANNEL_CAMP,				# ��Ӫ

	}

# Ƶ�����Ƶ�Ƶ�� ID ��ӳ��
CHAT_NAME_2_CHID = {}
for chid, name in CHAT_CHID_2_NAME.iteritems() :
	CHAT_NAME_2_CHID[name] = chid

# -------------------------------------------
# ��ͻ��˹�����Ƶ������ɫ�ɷ��Ե�Ƶ����
CHAT_EXPOSED_CHANNELS = set( [
	csdefine.CHAT_CHANNEL_NEAR,						# ����( ���̣�base->cell->client )
	csdefine.CHAT_CHANNEL_LOCAL,						# ����( ���̣�Ŀǰ��ûʵ�� )
	csdefine.CHAT_CHANNEL_TEAM,						# ����( ���̣�base->base �ϵĶ���ϵͳ->����Ա client )
	csdefine.CHAT_CHANNEL_FAMILY,					# ����( ���̣�base->base �ϵļ���ϵͳ->����Ա client )
	csdefine.CHAT_CHANNEL_TONG,						# ���( ���̣�base->base �ϵİ��ϵͳ->����Ա client )
	csdefine.CHAT_CHANNEL_WHISPER,					# ����( ���̣�base->client )
	csdefine.CHAT_CHANNEL_WORLD,						# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_RUMOR,						# ҥ��( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_WELKIN_YELL,				# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TUNNEL_YELL,				# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_PLAYMATE,					# ���( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_CAMP,						# ��Ӫ( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR			# ���ս��Ƶ��
	] )

KITBAG_ADD_ITEM_SUCCESS_RESULTS = [ csdefine.KITBAG_ADD_ITEM_SUCCESS, csdefine.KITBAG_STACK_ITEM_SUCCESS, csdefine.KITBAG_ADD_ITEM_BY_STACK_SUCCESS ]

SPECIALSHOP_GOOS_LIST = [
#								csdefine.SPECIALSHOP_OTHER_GOODS,
								csdefine.SPECIALSHOP_RECOMMEND_GOODS,
								csdefine.SPECIALSHOP_ESPECIAL_GOODS,
								csdefine.SPECIALSHOP_CURE_GOODS,
								csdefine.SPECIALSHOP_REBUILD_GOODS,
								csdefine.SPECIALSHOP_CRYSTAL_GOODS,
								csdefine.SPECIALSHOP_ENHANCE_GOODS,
								csdefine.SPECIALSHOP_TALISMAN_GOODS,
								csdefine.SPECIALSHOP_VEHICLE_GOODS,
								csdefine.SPECIALSHOP_PET_GOODS,
								csdefine.SPECIALSHOP_FASHION_GOODS,
								]

#��������Ȩ�ޱ�
FAMILY_GRADE_CONSCRIBE				= [ csdefine.FAMILY_GRADE_SHAIKH_SUBALTERN, csdefine.FAMILY_GRADE_SHAIKH ]
#��������Ȩ�ޱ�
FAMILY_GRADE_RELEASE_AFFICHE		= [ csdefine.FAMILY_GRADE_SHAIKH_SUBALTERN, csdefine.FAMILY_GRADE_SHAIKH ]
#������ԱȨ�ޱ�
FAMILY_GRADE_KICK_MEMBER			= [ csdefine.FAMILY_GRADE_SHAIKH_SUBALTERN, csdefine.FAMILY_GRADE_SHAIKH ]
"""
# ���ֿ��С
TONG_WAREHOUSE_LIMIT = {
	1 	: 50,
	2 	: 60,
	3 	: 70,
	4 	: 80,
	5 	: 90,
	6 	: 100,
	7 	: 110,
	8	: 120,
	9	: 130,
	10	: 140,
}
"""
NEED_ITEM_COUNT_DICT		= { 0:0,1:1,2:2,3:2,4:3,5:4,6:5}	# ������Ӧ�Ĳֿ�ʱ��Ҫ�Ľ�˿ľ����������ʽ{�ֿ�����:����,....}

# ������ϵ�б�
SINGLE_RELATION_LIST = [ csdefine.ROLE_RELATION_BLACKLIST, csdefine.ROLE_RELATION_FOE, csdefine.ROLE_RELATION_MASTER, csdefine.ROLE_RELATION_PRENTICE, csdefine.ROLE_RELATION_MASTER_EVER, csdefine.ROLE_RELATION_PRENTICE_EVER ]
# ˫����ϵ�б�
MULTI_RELATION_LIST = [ csdefine.ROLE_RELATION_FRIEND, csdefine.ROLE_RELATION_SWEETIE, csdefine.ROLE_RELATION_COUPLE, csdefine.ROLE_RELATION_ALLY ]

RCG_TONG_ROB_WARS			= {1:csdefine.RCG_TONG_ROB_WAR_1, 2:csdefine.RCG_TONG_ROB_WAR_2, 3:csdefine.RCG_TONG_ROB_WAR_3}	# �Ӷ�ս������ȡ
RCG_TEAM_COMP_EXP			= [csdefine.RCG_TEAM_COMP_EXP_1,csdefine.RCG_TEAM_COMP_EXP_2,csdefine.RCG_TEAM_COMP_EXP_3,\
									csdefine.RCG_TEAM_COMP_EXP_4, csdefine.RCG_TEAM_COMP_EXP_5, csdefine.RCG_TEAM_COMP_EXP_6,\
									csdefine.RCG_TEAM_COMP_EXP_7, csdefine.RCG_TEAM_COMP_EXP_8, csdefine.RCG_TEAM_COMP_EXP_9,\
									csdefine.RCG_TEAM_COMP_EXP_10,]

FETE_COMPLETE_STATUS = [ csdefine.LUNARHALO, csdefine.SUNSHINE, csdefine.STARLIGHT ]
JUMP_TYPE_WATERS				= [ csdefine.JUMP_TYPE_WATER1, csdefine.JUMP_TYPE_WATER2, csdefine.JUMP_TYPE_WATER3 ]

# Ӣ�����
CHALLENGE_AVATAR_TYPE = ( "chiyou", "huangdi", "houyi", "nuwo" )

CLASS_TO_COPY_DUTIES = {
	csdefine.CLASS_FIGHTER		: ( csdefine.COPY_DUTY_MT, csdefine.COPY_DUTY_DPS, ),				# սʿ��ӦMT��DPS
	csdefine.CLASS_SWORDMAN		: ( csdefine.COPY_DUTY_DPS, ),							# ���Ͷ�ӦDPS
	csdefine.CLASS_ARCHER 		: ( csdefine.COPY_DUTY_DPS, ),							# ���ֶ�ӦDPS
	csdefine.CLASS_MAGE 			: ( csdefine.COPY_DUTY_HEALER, csdefine.COPY_DUTY_DPS, ),			# ��ʦ��Ӧ���ƺ�DPS
}

#-------------------------------------------------------------------------------
#���Ա�׷�ٵĵ�ͼ
#--------------------------------------------------------------------------------
AREAS_CAN_BE_TRACE		= ["xin_ban_xin_shou_cun","fengming","xin_fei_lai_shi_001",
						 "zly_ban_quan_xiang","zly_ying_ke_cun","zly_bi_shi_jian",
						 "yun_meng_ze_01","yun_meng_ze_02","peng_lai","kun_lun",
						 "bei_ming"]


#-------------------------------------------------------------------------------
#Ӣ�����˸���
#--------------------------------------------------------------------------------
YXLM_ROBOT_1 = [ "20124014", "20124015", "20124016", "20124017", "20124018" ]
YXLM_ROBOT_2 = [ "20724025", "20724038", "20724039", "20724040", "20724041" ]

#--------------------------------------------------------------------------------
# ����ս
#--------------------------------------------------------------------------------
TONG_TURN_MEMBER_NUM 		= 5		# ����ս��������
TONG_TURN_FIGHT_MEM_NUM		= 2		# ����ս���ڳ�ս��������
TONG_TURN_LEVEL_MIN			= 40	# ����ս�ȼ�����
TONG_TURN_STEP_SIGNUP		= 1		# �����׶�
TONG_TURN_STEP_END			= 2		# ����δ���������ѽ������׶�
TONG_TURN_WIN_POINT			= 1		# ����ս��ʤ����

# ��������Ƶĵ�ͼ
TEAM_INVIETE_FORBID_MAP = [ "fu_ben_zheng_jiu_ya_yu_new" ]

# �ӳٴ������
PLAYER_TO_NPC_DISTANCE  = 20.0      # �����ʩ��NPC��������

# ��Ӫ

CAMP_KILL_REWARD_HONOUR_BASE = 100

# ��Ӫ����ս
CAMP_TURN_MEMBER_NUM 		= 1		# ����ս��������
CAMP_TURN_FIGHT_MEM_NUM		= 2		# ����ս���ڳ�ս��������
CAMP_TURN_LEVEL_MIN			= 40	# ����ս�ȼ�����
CAMP_TURN_STEP_SIGNUP		= 1		# �����׶�
CAMP_TURN_STEP_END			= 2		# ����δ���������ѽ������׶�
CAMP_TURN_WIN_POINT			= 1		# ����ս��ʤ����

# ------------------------------------------------------------------------------
# �����������
# ------------------------------------------------------------------------------
# Ʒ�ʶ�Ӧ�Ļ�������ֵ
DAOFA_QUALITY_EXP = { 2:10, 3:30, 4:50, 5:70,}

# �����������辭��{ �ȼ�:{ Ʒ��:���飬 Ʒ��:���� } }
DAOFA_UPGRADE_EXP = {
				1: { 2:50, 3:70, 4:100, 5:150, },
				2: { 2:200, 3:500, 4:600, 5:1000, },
				3: { 2:0, 3:1500,4:3000, 5:7200, },
				4: { 2:0, 3:0, 4:6000, 5:14400, },
				5: { 2:0, 3:0,4:0, 5:28800, },
				6: { 2:0, 3:0,4:0, 5:0, },
				}

# �������ۼ۸� { Ʒ��: �۸� }
DAOFA_PRICE = { 1:220, 2:280, 3:520, 4:750, 5:2500,}

# �������ȼ� { Ʒ��: ���ȼ� }
DAOFA_MAX_LEVEL = { 2: 3, 3: 4, 4: 5, 5: 6, }

# --------------------------------------------------------------------
# ������ͨ�����������
# --------------------------------------------------------------------
SKILL_ID_PHYSICS_LIST = [csdefine.SKILL_ID_PHYSICS, csdefine.SKILL_ID_SMART_PET_PHYSICS, csdefine.SKILL_ID_INTELLECT_PET_MAGIC]

PET_SKILL_ID_PHYSICS_MAPS = {	csdefine.PET_TYPE_STRENGTH	:	csdefine.SKILL_ID_PHYSICS,
								csdefine.PET_TYPE_BALANCED	:	csdefine.SKILL_ID_PHYSICS,
								csdefine.PET_TYPE_SMART		:	csdefine.SKILL_ID_SMART_PET_PHYSICS,
								csdefine.PET_TYPE_INTELLECT	:	csdefine.SKILL_ID_INTELLECT_PET_MAGIC,
}

# �����ֻظ���
DESTINY_TRANS_COPY_COMMON	= 1		# ��ͨģʽ

DESTINY_TRANS_ROLE_INIT_LIVE_POINT		= 3 # ��ҳ�ʼ�������



#�������鹫ʽΪ��(20.952*Lv^1.5+55.238)
#����������������ɹ�������Ӧ���齱����ʽ��(371.323 * (Lv^1.5) + 978.942) * (1.196^N) / 212.815
#֪ʶ�ʴ�1����ֶһ����鹫ʽ��(2.049*Lv^1.5+5.401)
#�ƾ����Ի��Ŷ�Ӧ���鹫ʽ��(419.048*Lv^1.5+1104.762)*���^0.256/24.572
#�ƾٻ��Ի��Ŷ�Ӧ���鹫ʽ��(558.730*Lv^1.5+1473.016)*���^0.256/24.572
#�ƾٵ��Ի��Ŷ�Ӧ���鹫ʽ��(698.413*Lv^1.5+1841.270)*���^0.231/33.155
#�������ζ�Ӧ���鹫ʽ��(401.587*Lv^1.5+1058.730)*����^-1.000
#ҹս�������鹫ʽ��(1396.825*Lv^1.5+3682.540)*(0.5*����^-1.000+0.5*����/(����+(����+100)^0.5))
#��������������Ӧ���鹫ʽ��(27.937*Lv^1.5+73.651)*(1+(С����-1)*0.111+(����-1)*0.200)
#Ѻ�������鹫ʽ��(670.476*Lv^1.5+1767.619)
#�����������鹫ʽ��(838.095*Lv^1.5+2209.524)
ACTIVITY_GET_EXP_FORMULA = {
	csdefine.ACTIVITY_TIAO_WU				: 	"20.952 * pow( %s, 1.5 ) + 55.238",
	csdefine.ACTIVITY_BIAN_SHEN_DA_SAI		:	"( 371.323 * pow( %s, 1.5 ) + 978.942 ) * pow( 1.196, %s ) / 212.815",
	csdefine.ACTIVITY_ZHI_SHI_WEN_DA		:	"2.049 * pow( %s, 1.5 ) + 5.401",
	csdefine.ACTIVITY_EXAMINATION_XIANGSHI	:	"( 419.048 * pow( %s, 1.5 ) + 1104.762 ) * pow( %s, 0.256 ) / 24.572",
	csdefine.ACTIVITY_EXAMINATION_HUISHI	:	"( 558.730 * pow( %s, 1.5 ) + 1473.016 ) * pow( %s, 0.256 ) / 24.572",
	csdefine.ACTIVITY_EXAMINATION_DIANSHI	:	"( 698.413 * pow( %s, 1.5 ) + 1841.270 ) * pow( %s, 0.231 ) / 33.155",
	csdefine.ACTIVITY_SAI_MA				:	"( 401.587 * pow( %s, 1.5 ) + 1058.730 ) * pow( %s, -1.000 )",
	csdefine.ACTIVITY_YE_ZHAN_FENG_QI		:	"( 1396.825 * pow( %s, 1.5 ) + 3682.540 ) * ( 0.5 * pow( %s, -1.000 ) + 0.5 * %s / ( %s + pow( ( score + 100 ), 0.5 ) ))",
	csdefine.ACTIVITY_LOOP_QUEST_30_59		:	"( 27.937 * pow( %s, 1.5 ) + 73.651 ) * ( 1 + ( %s - 1 ) * 0.111 + ( %s - 1 ) * 0.200 )",
	csdefine.ACTIVITY_LOOP_QUEST_60_95		:	"( 27.937 * pow( %s, 1.5 ) + 73.651 ) * ( 1 + ( %s - 1 ) * 0.111 + ( %s - 1 ) * 0.200 )",
	csdefine.ACTIVITY_NORMAL_DART			:	"670.476 * pow( %s, 1.5 ) + 1767.619",
	csdefine.ACTIVITY_EXP_DART				:	"838.095 * pow( %s, 1.5 ) + 2209.524"
}

ACTIVITY_GET_EXP = lambda act, *args : eval( ACTIVITY_GET_EXP_FORMULA[ act ] % args )


#---------------------------------------------------------------------
# ��Ӫ����
#---------------------------------------------------------------------
CAMP_ACTIVITY_TYPES = [ csdefine.CAMP_ACT_DESTROY_BASE, csdefine.CAMP_ACT_OBTAIN_POINT, csdefine.CAMP_ACT_KILL_BOSS,
						csdefine.CAMP_ACT_OCCUPY_BASE, csdefine.CAMP_ACT_INTERCEPT_HELPER, csdefine.CAMP_ACT_LITTLE_WAR,
						csdefine.CAMP_ACT_BIG_WAR ]

CAMP_ACTIVITY_INFO = {		csdefine.CAMP_ACT_DESTROY_BASE		:	cschannel_msgs.CAMP_ACT_DESTROY_BASE,
							csdefine.CAMP_ACT_OBTAIN_POINT		:	cschannel_msgs.CAMP_ACT_OBTAIN_POINT,
							csdefine.CAMP_ACT_KILL_BOSS			:	cschannel_msgs.CAMP_ACT_KILL_BOSS,
							csdefine.CAMP_ACT_OCCUPY_BASE		:	cschannel_msgs.CAMP_ACT_OCCUPY_BASE,
							csdefine.CAMP_ACT_INTERCEPT_HELPER	:	cschannel_msgs.CAMP_ACT_INTERCEPT_HELPER,
							csdefine.CAMP_ACT_LITTLE_WAR		:	cschannel_msgs.CAMP_ACT_LITTLE_WAR,
							csdefine.CAMP_ACT_BIG_WAR			:	cschannel_msgs.CAMP_ACT_BIG_WAR,
						}

CAMP_DAILY_REPEAT_LIMIT = 10						# ÿ�������Ӫ�ճ�����ĸ�������
CAMP_ACTIVITY_PERSIST_TIME = 8 * 60 * 60		# ��Ӫ�Ĭ�ϳ���ʱ��
CAMP_ACTIVITY_CHECK_SPELL_ID = 780047001		# ��Ӽ��buff�ļ���ID
CAMP_OCCUPED_SPELL_ID = 780048001				# �ݵ㱻ռ�������buff�ļ���ID

# -----------------------------------------------------------------------
# �������
# -----------------------------------------------------------------------
FISHING_GROUND_LENGTH = 40		# ���㳡��
FISHING_GROUND_WIDE = 28		# ���㳡��
FISH_HIT_COOLDOWN = 0.2			# �ڵ����������ȴʱ��
FISH_FORT_RADIUS = 8			# ��̨�뾶

#---------------------------------------------------------------------
# ��ħ��ս
#---------------------------------------------------------------------
TDB_BOSS_CLASSNAME_T =  "20717007"
TDB_BOSS_CLASSNAME_D =  "20717001"
TDB_MONSTER_CLASSNAMES_T = [ "20717008","20717009","20717010","20254069","20717012","20717013","20717014","20717015" ]
TDB_MONSTER_CLASSNAMES_D = [ "20717002","20717003","20717004","20717005","20717006" ]
TDB_MONSTERS = [ TDB_BOSS_CLASSNAME_T ] + [ TDB_BOSS_CLASSNAME_D ] + TDB_MONSTER_CLASSNAMES_T + TDB_MONSTER_CLASSNAMES_D

TDB_TRANSPORT_SPACE_T = "zly_ban_quan_xiang"
TDB_TRANSPORT_SPACE_D = "zy_xiu_luo_dian"
TDB_TRANSPORT_POSITION_T = ( 419.939453, 451.459473, 463.497742 )
TDB_TRANSPORT_POSITION_D = ( 51.813, 155.100, -78.074  )

TDB_FIRDAMAGE_LEVEL_LIMIT = 40			# �״���͵ȼ�Ҫ��
TDB_TOP_DAMAGE_LIMIT = 50000			# �˺���Ҫ������˺���
TDB_TOP_CURE_LIMIT = 30000				# ���ư�Ҫ�����������
TDB_TOP_DAMAGE_ORDER_LIMIT = 20			# �˺���������
TDB_TOP_CURE_ORDER_LIMIT = 3			# ���ư�������
TDB_TOP_DIE_ORDER_LIMIT = 20			# ������������

#�����������ID
REWARD_QUEST_LOW_ITEM = 110103056
REWARD_QUEST_HIGH_ITEM = 110103057

#����ʱ�̼���ID
DancingKingBuffID = 22135  #����Buff (�������������ô�buff�����õĵȼ���һ�������鱶��Ҳ��һ��)
DancingBuffID	= 22136    #�����о���Buff
DancingPunishBuffID = 22137 #��սʧ��5����֮�ڲ�������ս��buff
DanceingPunishSkillID = 780061  #��սʧ��5����֮�ڲ�������ս��buff��Ӧ�ļ���
DanceSkill1		= 780051001  	#�������ս�������ϰ����ʱ�Ŀռ似�ܣ����Ŷ���dance1
DanceSkill2		= 780052001	#�������ս�������ϰ����ʱ�Ŀռ似�ܣ����Ŷ���dance2
DanceSkill3		= 780053001	#�������ս�������ϰ����ʱ�Ŀռ似�ܣ����Ŷ���dance3
DanceSkill4		= 780054001	#�������ս�������ϰ����ʱ�Ŀռ似�ܣ����Ŷ���dance4
DanceSkill5		= 780055001	#�������ս�������ϰ����ʱ�Ŀռ似�ܣ����Ŷ���dance5
DanceExpSkill			= 780056001  	#����������л�õ���ͨ����Buff��8��Сʱ��
DanceExpWaitingSkillID	= 780057001  	#����������л�õĺ�ѡ����Buff
DanceExpCOPPERSkillID	= 780058001  	#����������л�õ�ͭ�ƾ���Buff
DanceExpSILVERSkillID	= 780059001  	#����������л�õ����ƾ���Buff
DanceExpGLODSkillID		= 780060001  	#����������л�õĽ��ƾ���Buff
SPACE_WUTING = "fu_ben_wu_tai_001"
SPACE_DANCE_CHALLENGE = "dancechellenge"
SPACE_DANCE_PRACTICE = "dancepractice"
spaceDanceSkills = [780051001,780052001,780053001,780054001,780055001]
DANCEHALLAOI	= 100

# ��Ὺ���������ĵ��ʽ�
TONG_FETE_REQUEST_MONEY					= 10000		# ����
TONG_ROBWAR_REQUEST_MONEY				= 20000		# �Ӷ�ս
TONG_MONSTERRAID_REQUEST_MONEY			= 30000		# ħ����Ϯ
TONG_RACE_REQUEST_MONEY					= 40000		# �������
TONG_OPEN_DART_QUEST_REQUEST_MONEY		= 50000		# ���������������
TONG_OPEN_NORMAL_QUEST_REQUEST_MONEY	= 60000		# ��������ճ�����

# �����ɸ������ľ���ֵ
TONG_EXP_REWARD_FETE				= 10000		# ����
TONG_EXP_REWARD_ROBWAR				= 20000		# �Ӷ�ս
TONG_EXP_REWARD_MONSTERRAED			= 30000		# ħ����Ϯ
TONG_EXP_REWARD_RACE				= 40000		# �������

#---------------------------------------------------------------------
# ���ط����
#---------------------------------------------------------------------
JUE_DI_FAN_JI_WAIT_TIME = 25.0							#���ط����ƥ��ɹ���ȴ�ʱ��
JUE_DI_FAN_JI_LEVEL_LIMIT = 50							#���ط���������ȼ�Ҫ��

YA_YU_COPY_SPECAIL_ITEMS = [ 40401024, 40401025, 40401026 ]		# �m؅�����������ID

# --------------------------------------------------------------------
# ���ս������
# --------------------------------------------------------------------
YI_JIE_ZHAN_CHANG_ENRAGE_SKILL_ID		= 123473001		#���ս�����ŭbuff����
YI_JIE_ZHAN_CHANG_STONE_SKILL_ID		= 123474001		#���ս��������ʯ֮��buff����
YI_JIE_ZHAN_CHANG_DESERTER_SKILL_ID		= 123477001		#���ս�������ӱ�buff����
YI_JIE_ZHAN_CHANG_MAX_RAGE_SKILL_ID		= 123478001		#���ս��������ŭbuff����
YI_JIE_ZHAN_CHANG_UNIQUE_SKILL_ID		= 123479001		#���ս����˫��

YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID		= 62004		#���ս����ŭbuff
YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID		= 199026	#���ս���ӱ�buff
YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID		= 1001		#���ս����ŭbuff

# --------------------------------------------------------------------
# �����ս����
# --------------------------------------------------------------------
g_camp_info = { 1: cschannel_msgs.CAMP_FAIRY,
				2: cschannel_msgs.CAMP_DEVIL, }

CITY_WAR_BATTLE_BASE_ACTIVATE_LIMIT = 50

CITY_WAR_RESOURCE_BASE_SKILL = { csdefine.CITY_WAR_FINAL_FACTION_ATTACK: 1,
								 csdefine.CITY_WAR_FINAL_FACTION_DEFEND: 1,
								 }

# --------------------------------------------------------------------
# ����������Լ���Ӫ������칲��
# --------------------------------------------------------------------
g_road_info = { "left": cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_UPPER_ROAD,
				 "mid": cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_CENTER_ROAD,
				 "right": cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_LOWER_ROAD,}


#��ɫģ�����ű�
MATCHING_DICT = {
	csdefine.GENDER_MALE: {
		csdefine.CLASS_FIGHTER  : 1.1,
		csdefine.CLASS_SWORDMAN : 1.2,
		csdefine.CLASS_ARCHER   : 1.2,
		csdefine.CLASS_MAGE     : 1.1,		},
	csdefine.GENDER_FEMALE: {
		csdefine.CLASS_FIGHTER  : 1.2,
		csdefine.CLASS_SWORDMAN : 1.2,
		csdefine.CLASS_ARCHER   : 1.2,
		csdefine.CLASS_MAGE     : 1.1,		},
}

# --------------------------------------------------------------------
# ���ͻ���entity����
# --------------------------------------------------------------------
CLIENT_ENTITY_TYPE = [ "CustomPatrolGraph", "Creature", "Flock", "EnvironmentObject", "SpecialHideEntity", "SoundEntity", "CameraFly", "CameraModel", ]

#��̬������ϵʵ��
RELATION_TYPE_STATIC_SPACE = [ csdefine.RELATION_STATIC_CAMP_FENG_HUO,
								csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY,
								csdefine.RELATION_STATIC_TONG_CITY_WAR,
								csdefine.RELATION_STATIC_YXLM,
								csdefine.RELATION_STATIC_YI_JIE_ZHAN_CHANG,
								csdefine.RELATION_STATIC_TONG_CITY_WAR_FINAL,
								]

#�����뾲̬��ϵʵ���Ķ�Ӧ��ϵ
SPACE_MAPPING_RELATION_TYPE_DICT = { csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN : csdefine.RELATION_STATIC_CAMP_FENG_HUO,
									 csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN : csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY,
									 csdefine.SPACE_TYPE_CITY_WAR : csdefine.RELATION_STATIC_TONG_CITY_WAR,
									 csdefine.SPACE_TYPE_CITY_WAR_FINAL : csdefine.RELATION_STATIC_TONG_CITY_WAR_FINAL,
									 csdefine.SPACE_TYPE_YXLM : csdefine.RELATION_STATIC_YXLM,
									 csdefine.SPACE_TYPE_YXLM_PVP : csdefine.RELATION_STATIC_YXLM,
									 csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG : csdefine.RELATION_STATIC_YI_JIE_ZHAN_CHANG,
									 csdefine.SPACE_TYPE_TONG_TERRITORY : csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY,
									}
