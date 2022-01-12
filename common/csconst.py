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
LOGIN_ROLE_UPPER_LIMIT		= 3			# 最多可以创建多少个角色( from L3Define.py；原名: C_ACC_MAX_ROLE )


# --------------------------------------------------------------------
# about game status
# --------------------------------------------------------------------
SERVER_TIME_AMEND 			= 100.0		# 服务器时间转成整型时的修正(取小数点后几位*10)，100表示精确到小数点后2位，必须要小数，否则不正确
										# * 100可以使服务器运行240多天而不溢出，如果 * 1000则只能使用服务器运行24天。
# --------------------------------------------------------------------
# about game float2int
# --------------------------------------------------------------------
#。。。如果"FLOAT_ZIP_PERCENT"的配置有更改，请同步更新DataTool里面的
#。。。entities\plugins\ExportPY\convertFunctions_server.py里宠物加载数据预处理部分。
#。。。PS：convertFunctions_server.py里查找"FLOAT_ZIP_PERCENT"即可定位  add by：qiulinhui
FLOAT_ZIP_PERCENT 			= 10000.0	# 游戏浮点数的放大比率

# --------------------------------------------------------------------
# about role's attributes
# --------------------------------------------------------------------
g_map_gender 				= { "GENDER_MALE" : csdefine.GENDER_MALE, "FAMALE" : csdefine.GENDER_FEMALE }		# ( 原名：g_gender )
g_en_gender 				= { csdefine.GENDER_MALE : "male", csdefine.GENDER_FEMALE : "female" }				# ( 原名：g_genderstr )
g_chs_gender 				= { csdefine.GENDER_MALE : cschannel_msgs.SEX_MAN, csdefine.GENDER_FEMALE : cschannel_msgs.SEX_WOMAN }				# ( 原名：g_genderTally )

g_map_class = {																					# ( 原名：g_metier )
		"CLASS_FIGHTER"			: csdefine.CLASS_FIGHTER,
		"CLASS_WARLOCK"			: csdefine.CLASS_WARLOCK,
		"CLASS_SWORDMAN"		: csdefine.CLASS_SWORDMAN,
		"CLASS_ARCHER"			: csdefine.CLASS_ARCHER,
		"CLASS_MAGE"			: csdefine.CLASS_MAGE,
		"CLASS_PRIEST"			: csdefine.CLASS_PRIEST,
		"CLASS_PALADIN"			: csdefine.CLASS_PALADIN,
		}

g_en_class = {														# ( 原名：g_classstr )
		csdefine.CLASS_FIGHTER	: "fighter",
		csdefine.CLASS_WARLOCK	: "warlock",
		csdefine.CLASS_SWORDMAN	: "swordman",
		csdefine.CLASS_ARCHER	: "archer",
		csdefine.CLASS_MAGE		: "mage",
		csdefine.CLASS_PRIEST	: "priest",
		csdefine.CLASS_PALADIN	: "paladin",
		}

g_chs_class = {																					# ( 原名：g_classTally )
		csdefine.CLASS_FIGHTER	: ST.PROFESSION_FIGHTER,
		csdefine.CLASS_WARLOCK	: ST.PROFESSION_WARLOCK,
		csdefine.CLASS_SWORDMAN	: ST.PROFESSION_SWORD,
		csdefine.CLASS_ARCHER	: ST.PROFESSION_ARCHER,
		csdefine.CLASS_MAGE		: ST.PROFESSION_MAGIC,
		csdefine.CLASS_PRIEST	: ST.PROFESSION_PRIEST,
		csdefine.CLASS_PALADIN	: ST.PROFESSION_FIGHTER,														# 显示上还是使用战士
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
ROLE_AOI_RADIUS				= 50.0				# 玩家 AOI 范围

ROLE_INIT_INTERVAL			= 0.1				# 初始化玩家属性的事件间隔( hyw -- 2008.06.09 )

ROLE_MODEL_WIDTH			= 0.4				# 表示角色模型中心点到面部方向BoundingBox的距离( from common/L3Define.py )
ROLE_MODEL_BOUND			= Math.Vector3( ( 0.6, 2.0, 0.4 ) )		# 主角统一的bounding box值（长、高、宽）

ROLE_MOVE_SPEED_BIAS   		= 0.2				# 由于客户端卡或网络延迟的问题，此值必须要有一定的大小，否则很容易就会产生往回拉的问题
												# 实际range = range + ROLE_MOVE_SPEED_BIAS( from common/L3Define.py )
ROLE_TOP_SPEED_Y			= 200				# Y 轴上的数度限制

ROLE_MONEY_UPPER_LIMIT		= 4000000000		# 拥有金钱的上限( from const/L3Define.py；原名：MONEY_MAX )

ROLE_TEACHCREDIT_UPPER_LIMIT	= 2000000000		# 玩家功勋值上限11:33 2008-8-21，wsf

ROLE_GOLD_UPPER_LIMIT		= 900000000			# 拥有金元宝的上限
ROLE_SILVER_UPPER_LIMIT		= 900000000			# 拥有银元宝的上限

ROLE_LEVEL_UPPER_LIMIT		= 110				# 玩家等级上限
PET_LEVEL_UPPER_LIMIT		= 110				# 宠物最大等级限制

PET_ELEMENT_DERATE_MAX = 8000				# 宠物元素伤害抵抗上限 by 姜毅

ROLE_POTENTIAL_UPPER		= 100000000			# 玩家潜能点上限15:38 2008-7-23，wsf
ROLE_EXP2POT_MULTIPLE		= 5					# 经验换潜能的倍率( 5经验换1潜能 )

# -----------------------------------------------------
# 生命参数	( from cell/AttrDefine.py and base/attrDefine.py；designed by penghuawei )( 原名：ROLE_HP_MAX_BASE )
ROLE_HP_MAX_RADIX = {
		csdefine.CLASS_FIGHTER	: 25,		# 战士
		csdefine.CLASS_SWORDMAN	: 24,		# 剑客
		csdefine.CLASS_ARCHER	: 18,		# 射手
		csdefine.CLASS_MAGE		: 15,		# 法师
		csdefine.CLASS_WARLOCK	: 24,		# 巫师
		csdefine.CLASS_PRIEST	: 29,		# 祭师
		}

# 法力参数 ( from cell/AttrDefine.py and base/attrDefine.py；designed by penghuawei )( 原名：ROLE_MP_MAX_BASE )
ROLE_MP_MAX_RADIX = {
		csdefine.CLASS_FIGHTER	: 20,		# 战士
		csdefine.CLASS_SWORDMAN	: 25,		# 剑客
		csdefine.CLASS_ARCHER	: 25,		# 射手
		csdefine.CLASS_MAGE		: 40,		# 法师
		csdefine.CLASS_WARLOCK	: 28,		# 巫师
		csdefine.CLASS_PRIEST	: 22,		# 祭师
		}

# -----------------------------------------------------
g_default_spawn_site = {												# 默认出生点( 原名：g_default_spawn_position )
		csdefine.CLASS_FIGHTER	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 27.705, 177.35, -178.884 ), ( 0.0,0.0,3.117 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( 48.165,162.697,108.306 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_WARLOCK	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 27.705, 177.35, -178.884 ), ( 0.0,0.0,3.117 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( 48.166267,163.667674,132.199509 ), ( 0.000000,0.000000,0.027 ) ) },
		csdefine.CLASS_SWORDMAN	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 712.390, 510.721, 314.424 ), ( 0.0,0.0,0.0 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( -293.884,469.494,680.128 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_ARCHER	: { csdefine.ENTITY_CAMP_TAOISM : ( ( -56.242, 490.657, 198.985 ), ( 0.0,0.0,0.0 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( -41.139,505.648,126.596 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_MAGE		: { csdefine.ENTITY_CAMP_TAOISM : ( ( -502.165, 527.692, -481.557 ), ( 0.0,0.0,0.0 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( -780.981,459.612,325.481 ), ( 0.0,0.0,0.0 ) ) },
		csdefine.CLASS_PRIEST	: { csdefine.ENTITY_CAMP_TAOISM : ( ( 27.705, 177.35, -178.884 ), ( 0.0,0.0,3.117 ) ), csdefine.ENTITY_CAMP_DEMON : ( ( 48.166267,163.667674,132.199509 ), ( 0.000000,0.000000,0.027 ) ) },
		}

g_default_spawn_city = {												# 默认出生地( 原名：g_default_spawn_city )
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
ATTACK_RANGE_BIAS				= 1.5		# 表示由于客户端和服务器EntityPosition不一致允许的攻击距离计算偏差( from common/L3Define.py )

MONSTER_CORPSE_DURATION			= 8.0		# 怪物死亡后尸体消失时间，单位：秒，float( from common/L3Define.py；原名：CORPSE_DELAY )

RESIST_MIN						= 0.0		# 对异常状态抗性的最低限度 by姜毅
RESIST_LEVEL_MIN				= 8			# 对异常状态抗性的下限等级 低于此级数一律返回1% by姜毅

MOVE_TRAP_DELAY_DESTROY_TIME    = 5.0		# 可移动陷阱延迟销毁时间
# --------------------------------------------------------------------
# about communication between entites
# --------------------------------------------------------------------
COMMUNICATE_DISTANCE			= 6.0		# 与 NPC 交互的最大距离, 单位: 米( from L3Define.py; 原名：NPC_TASK_STATUS_SHOW_DISTANCE )

TRADE_ITEMS_UPPER_LIMIT			= 7			# 玩家之间的交易物品数量不能超过 7 个
TRADE_WAITING_TIME				= 15.0		# 玩家邀请等待时间
TRADE_PRICE_UPPER_LIMIT			= 2000000000	# 交易商品的价格上限(有些地方价格参数类型是INT32，如果设置价格超过2147483647则会使价格变为负数)

COMMISSION_ITEMS_UPPER_LIMIT	= 10		# 玩家寄卖的物品数量上限
COMMISSION_CHARGE_PERCENT		= 0.05		# 玩家寄卖费用占出售价格的比例

# --------------------------------------------------------------------
# about pk system
# --------------------------------------------------------------------
PK_PROTECT_LEVEL				= 30		# 30级以下pk保护
PK_GOODNESS_MAX_VALUE			= 100		# 善恶值最大值
PK_MONEY_DROPRATE_MAX			= 0.45		# pk死亡金钱掉落最大比率
PK_MONEY_DROPRATE_EXC			= 0.005		# 每一点pk值额外掉落金钱比率
PK_MONEY_DROPRATE				= 0.05		# 死亡固定掉落金钱比率

PK_EQUIP_DROPRATE				= 20		# 死亡掉落装备概率

# --------------------------------------------------------------------
# about talisman
# --------------------------------------------------------------------
TALISMAN_UPTO_IMMORTAL_LEVEL		= 50	# 法宝升级到仙品限制等级
TALISMAN_UPTO_DEITY_LEVEL			= 100	# 法宝升级到神品限制等级
TALISMAN_ADD_LIFE_ITEM 				= 50101063		# 法宝充值女娲石
TALISMAN_LEVELUP_MAP				= {
										ItemTypeEnum.TALISMAN_COMMON	: [TALISMAN_UPTO_IMMORTAL_LEVEL, csstatus.TALISMAN_LEVELUP_IMM, csstatus.TALISMAN_SKILL_LEVELUP_IMM],
										ItemTypeEnum.TALISMAN_IMMORTAL	: [TALISMAN_UPTO_DEITY_LEVEL, csstatus.TALISMAN_LEVELUP_DEI, csstatus.TALISMAN_SKILL_LEVELUP_DEI],
										ItemTypeEnum.TALISMAN_DEITY		: [150, csstatus.TALISMAN_TOP_LEVEL, csstatus.TALISMAN_SKILL_TOP_LEVEL],
										}	# 法宝升级和品质的关联 [等级限制，状态信息，] by姜毅


# 荣誉值wsf，16:50 2008-7-17
HONOUR_UPPER_LIMIT				= 1000000	# 荣誉值上限
HONOUR_LOWER_LIMIT				= -1000000	# 荣誉值下限


# --------------------------------------------------------------------
# about inventory( from common/spaceConst.py；designed by huangyongwei )
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
	"strength"   : ( 60401001, 60401002, 60401003, 60401013 ),	# 力量魂魄石
	"intellect"  : ( 60401004, 60401005, 60401006, 60401014 ),	# 智力魂魄石
	"dexterity"  : ( 60401007, 60401008, 60401009, 60401015 ),	# 敏捷魂魄石
	"corporeity" : ( 60401010, 60401011, 60401012, 60401016 ),	# 体质魂魄石
	}															# 宠物强化所需要的魂魄石

PET_SMELT_ITEMS			= [60201020, 60201105]									# 精练符物品 ID
PET_DIRECT_ITEMS		= [60201021, 60201106]									# 强化符物品 ID
PET_ADD_LIFE_ITEMS		= [60201004, 60201104]									# 延寿丹物品 ID

pet_joyancy_items = ( \
	60201007,													# 白色
	60201051,													# 蓝色
	60201052,													# 金色
	60201053,													# 粉色
	60201054,													# 绿色
	) 															# 布娃娃ID

# -------------------------------------------
PET_ROLE_COME_OUT_DISTANCE		= 3.0		# 宠物刚刚召唤出来时与玩家的距离

PET_CATCH_OVER_LEVEL			= 5			# 当宠物大于玩家多少级后就不能捕捉
PET_CONJURE_OVER_LEVEL			= 5			# 当宠物大于玩家多少级就不允许出征

PET_LIFE_UPPER_LIMIT			= 60000		# 宠物寿命上限
PET_PROCREATE_MIN_LIFE			= 5000		# 宠物繁殖所需最低寿命
PET_JOYANCY_UPPER_LIMIT			= 100		# 宠物快乐度上限
PET_PROCREATE_MIN_JOYANCY		= 90		# 宠物繁殖所需最低快乐度
PET_FEED_EXP_GAP				= 5			# 经验喂养等级差
PET_PROCREATE_FIND_TEAMMATE_RANGE	= 20		# 宠物繁殖查找范围内的队员不能多于2人

PET_NAME_MAX_LENGTH				= 14		# 宠物名字的最大长度

PET_PROCREATE_MIN_LEVEL			= 40		# 可繁殖宠物的最小等级
PET_PROCREATE_LIFT_NEED			= 5000		# 参与繁殖的宠物的寿命值需求
PET_PROCREATE_JOY_NEED			= 90		# 参与繁殖的宠物快乐度需求
PET_PROCREATE_GAP_LEVEL			= 5			# 繁殖的两个宠物的等级相差不能超过五级
PET_PROPAGATE_KEEPING_TIME		= 48		# 宠物繁殖完后，在保育员处保留的时间（单位小时）
PET_FORCE_FOLLOW_RANGE			= 32.0		# 宠物离开玩家多远就强迫跟随
PET_PROCREATE_OVERDUE_TIME 		= 48 * 3600	# 宠物繁殖过期时限
PET_PROCREATE_NEED_TIME 		= 1 * 3600	# 宠物繁殖所需时间

# -------------------------------------------
# pet follow and fight
# -------------------------------------------
PET_ROLE_KEEP_DISTANCE				= 3.0			# 宠物与玩家之间保持的距离（单位：米）
PET_FORCE_FOLLOW_RANGE				= 52.0			# 宠物离开玩家多远就强迫跟随
PET_ENMITY_RANGE					= 10.0			# 搜寻怪物范围
PET_FORCE_TELEPORT_RANGE			= ROLE_AOI_RADIUS/1.2	# 宠物强制传送距离


# 获得每一个宠物技能的概率，设计原则是1000个宠物中有一个会获得全天赋技能，即宠物获得所有天赋技能的
# 概率为1/1000，则获得每一个天赋技能的概率是0.001 ** ( 1.0/宠物天赋技能个数 )
PET_HAS_ALL_INBORN_SKILL_RATE	= 0.001		# 宠物能获得全天赋技能的概率

pst_storeCount = {}
pst_storeCount[csdefine.PET_STORE_TYPE_LARGE]	= 10		# 大仓库的最大宠物存储数量
pst_storeCount[csdefine.PET_STORE_TYPE_SMALL]	= 5			# 小仓库的最大宠物存储数量
PST_HOLD_DAYS					= 15 						# 仓库的租用天数


# --------------------------------------------------------------------
# about inventory( from common/spaceConst.py；designed by huangyongwei )
# --------------------------------------------------------------------
IV_MONEY_UPPER_LIMIT			= 0x7FFFFFFF	# 仓库最多能存多少钱
IV_PAGES_COUNT					= 3				# 仓库页数
IV_PAGE_ITEMS_COUNT				= 48			# 每页格子数


# --------------------------------------------------------------------
# about quickbar( from common/L3Define.py；designed by huangyw )
# --------------------------------------------------------------------
QB_ITEMS_COUNT				= 750			# 快捷栏最大空间


QB_PET_ITEM_COUNT			= 5				# 宠物快捷格个数

# --------------------------------------------------------------------
# about space( from common/spaceConst.py；designed by panguankong )
# --------------------------------------------------------------------
SPACE_SPACEDATA_KEY						= 256							# Space define, must big than 255( from L3Define.py；原名：KEY_SPACEDATA_SPACEID )
SPACE_SPACEDATA_SPACE_TYPE_KEY			= 257							# 保存在 spaceData 副本类别key
SPACE_SPACEDATA_NUMBER					= 258							# 保存在base端，通过spaceManager生成的唯一的spaceNumber
SPACE_SPACEDATA_LINE_NUMBER				= 259							# 保存在 spaceData 副本第几线的号码
SPACE_SPACEDATA_MAX_LINE_NUMBER			= 260							# 保存在 spaceData 副本有多少条线
SPACE_SPACEDATA_CANNOTPK				= 261							# 保存在 spaceData 副本能否PK
SPACE_SPACEDATA_CANNOTQIECUO			= 262							# 保存在 spaceData 副本能否切磋
SPACE_SPACEDATA_CANNOTCONJUREEIDOLON	= 263							# 保存在 spaceData 副本能否召唤小精灵

SPACE_SPACEDATA_COPY_TITLE				= 270							# 副本名称
SPACE_SPACEDATA_START_TIME				= 271							# 副本开始时间
SPACE_SPACEDATA_LAST_TIME				= 272							# 副本持续时间
SPACE_SPACEDATA_LEAVE_MONSTER			= 273							# 副本剩余小怪数量
SPACE_SPACEDATA_LEAVE_BOSS				= 274							# 副本剩余大怪数量
SPACE_SPACEDATA_LEVEL					= 275							# 副本批次
SPACE_SPACEDATA_MENGMENG				= 276							# 副本蒙蒙数量
SPACE_SPACEDATA_MOWENHU					= 277							# 魔纹虎数量
SPACE_SPACEDATA_GUIYINGSHI				= 278							# 真鬼影狮数量
SPACE_SPACEDATA_NEXT_LEVEL_TIME			= 279							# 下一波到达时间
SPACE_SPACEDATA_YAYU_HP_PRECENT			= 280							# 猰貐血量百分比
SPACE_SPACEDATA_CITYWAR_RIGHT_TONGDBID	= 281							# 城战防守方帮会DBID
SPACE_SPACEDATA_TONG_TERRITORY_TONGDBID	= 282							# 帮会领地副本 记录的帮会DBID
SPACE_SPACEDATA_CITY_REVENUE			= 283							# 城市税率
SPACE_SPACEDATA_TEACH_MONSTER_LEVEL		= 284							# 师徒副本小怪级别
SPACE_SPACEDATA_TREE_HP_PRECENT			= 285							# 神树血量百分比
SPACE_SPACEDATA_CAN_FLY					= 286							# 空间是否可以飞行
SPACE_SPACEDATA_MIN_BBOX				= 287							# 空间外接体的较小对角坐标
SPACE_SPACEDATA_MAX_BBOX				= 288							# 空间外接体的较大对角坐标
SPACE_SPACEDATA_DEATH_DEPTH				= 289							# 控件死亡深度
SPACE_SPACEDATA_DART_POINT				= 290							# 昌平镖局和兴隆镖局势力运镖积分
SPACE_SPACEDATA_CHALLENGE_GATE			= 291							# 华山阵法当前层数
SPACE_SPACEDATA_POTENTIAL_FLAG_HP		= 292							# 潜能乱斗，圣魂旗的血量
SPACE_SPACEDATA_CAN_VEHICLE 			= 293 							# 空间是否可以召唤坐骑
SPACE_SPACEDATA_BATCH					= 294							# 拯救猰貐当前刷怪阶段
SPACE_SPACEDATA_NEXT_BATCH_TIME			= 295							# 新版猰貐下一波到达时间
SPACE_SPACEDATA_YAYU_NEW_HP				= 296							# 新版猰貐血量显示
SPACE_SPACEDATA_PREPARE_TIME			= 297							# 战斗准备时间
SPACE_SPACEDATA_ZHANNAN_ANGER_PERCENT	= 298							# 斋南怒气值百分比（用血量计算）
SPACE_SPACEDATA_ANGER_ISSHOW			= 299							# 是否显示环形怒气值
SPACE_SPACEDATA_TOTAL_BOSS				= 300							# Boss总数
SPACE_DANCECOPY_COMOBOPOINT				= 301 							# 劲舞时刻斗舞副本中连击数
SPACE_DANCECHALLENGE_TIMELIMIT			= 302							# 挑战斗舞副本中时间限制
SPACE_SPACEDATA_YIJIE_SCORE_TIAN		= 303							# 异界战场天族积分
SPACE_SPACEDATA_YIJIE_PLAYER_TIAN		= 304							# 异界战场天族人数
SPACE_SPACEDATA_YIJIE_SCORE_DI			= 305							# 异界战场地族积分
SPACE_SPACEDATA_YIJIE_PLAYER_DI			= 306							# 异界战场地族人数
SPACE_SPACEDATA_YIJIE_SCORE_REN			= 307							# 异界战场人族积分
SPACE_SPACEDATA_YIJIE_PLAYER_REN		= 308							# 异界战场人族人数
SPACE_SPACEDATA_YIJIE_ANGER_FACTION		= 309							# 异界战场激怒阵营
SPACE_SPACEDATA_YIJIE_ALLIANCE_FACTIONS	= 310							# 异界战场同盟双方
SPACE_SPACEDATA_PROGRESS				= 311							# 副本进度

SPACE_COPY_MMP_YAOQI_PERCENT			= 312							# 炼妖壶副本的妖气百分比
SPACE_SPACEDATA_LEAVE_WAVE				= 313							# 剩余怪物波数
SPACE_SPACEDATA_NPC_HP_PRECENT			= 314							# NPC血量百分比


SPACE_CONFIG_PATH 				= "config/server/gameObject/space"	# 空间配置文件


# --------------------------------------------------------------------
# about chatting( from L3Common )
# --------------------------------------------------------------------
CHAT_MESSAGE_UPPER_LIMIT	= 140		# 发言最大允许字节数( 原名：MAX_CHAT_MESSAGE )。由于客户端用了unicode，为了处理汉字，服务器最大字数为客户端的2倍 --pj
CHAT_ESTOP_REPEAT_COUNT		= 10		# 重复多少次同样发言将会被禁言
CHAT_ESTOP_TIME				= 30		# 禁言时间

CHAT_TRADE_DELAY			= 7			# 交易发言发送时间延迟，单位：秒( 原名：BUSINESS_CHAT_DELAY )
CHAT_RUMOR_DELAY			= 600		# 谣言发言时间间隔，单位：秒( 原名：RUMOR_CHAT_DELAY )
CHAT_YELL_DELAY				= 20.0		# 世界发言时间间隔，单位：秒( 原名：YELL_CHAT_DELAY )
CHAT_GLOBAL_DELAY			= 1.0		# 全局发言速度，秒/次，float type( 原名：GLOBAL_CHAT_DELAY )
CHAT_CMAP_DELAY				= 2.0		# 阵营频度的发言时间间隔，单位：秒

CHAT_RUMOR_PROBABILITY		= 0.8		# 造谣成功率：80%( 原名：RUMOR_CHAT_PROBABILITY )

CHAT_RUMOR_MP_DECREMENT		= 0.3		# 每次谣言MP消耗最大MP的百分比( 原名：RUMOR_MP_REDUCE )

CHAT_TRADE_LEVEL_REQUIRE	= 10		# 交易频道发言等级要求( 原名：BUSINESS_CHAT_LVL_REQ )
CHAT_YELL_LEVEL_REQUIRE		= 20		# 世界频道发言等级要求( 原名：YELL_CHAT_LVL_REQ )
CHAT_YELL_USE_MONEY			= 500		# 世界需要的游戏币

CHAT_WELKIN_ITEM			= 110103014	# 天音符物品号
CHAT_TUNNEL_ITEM			= 110103021	# 地音符物品号
CHAT_TUNNEL_ITEM_BINDED		= 110103027	# 地音符物品号(奖品绑定版)

# --------------------------------------------------------------------
# about team( move from base/Const.py by phw )
# --------------------------------------------------------------------
TEAM_FEEDBACK_WAIT_TIME 			= 60			# 组队多长时间没回应时，便销毁队伍（秒）( 原名：DESTORY_TEAM_TIME )
TEAM_OFFLINE_DETECT_INTERVAL 		= 10 			# 玩家下线后，多长时间作一次离线检测( 原名：OFFLINE_LEAVE_HTIME )
TEAM_OFFLINE_DURATION 				= 300 			# 玩家下线多长时间后，被认为是离线( 原名：OFFLINE_LEAVE_TIME )

TEAM_INVITE_KEEP_TIME 				= 30 			# 邀请持续时间(秒)
TEAM_UPDATA_MAX_TIME 				= 3				# 服务器允许更新玩家数据的时间限制
TEAM_MEMBER_MAX						= 5				# 队伍成员最大人数

TEAM_DATA_UPDATE_TIME				= 5				# 远距离玩家每5秒更新一次
TEAM_DATA_UPDATE_TIME_NEAR			= 0.5			# 近距离玩家没0.5秒更新一次
TEAM_DATA_UPDATE_PET				= 5				# 更新队友宠物5秒一次

TEAM_FOLLOW_DISTANCE				= 30			# 米，队伍跟随有效距离

# --------------------------------------------------------------------
# about mail( zyx )
# --------------------------------------------------------------------
MAIL_CHECK_OUTDATED_REPEAT_TIME 	= 30 			# 查询过期需删除邮件的更新时间（秒）
MAIL_TITLE_LENGTH_MAX 				= 20			# 邮件标题最大长度（字节）  zyx: 这个不能改大。否则有问题
MAIL_CONTENT_LENGTH_MAX				= 400			# 邮件内容最大长度（字节）	zyx: 这个不能改大。否则有问题

MAIL_NPC_OUTTIMED					= 604800		# 未读邮件删除时间，单位：秒； 604800 = 3600*24*7 秒；表示邮件多长时间没有阅读就会被删除
MAIL_READ_OUTTIMED					= 7200			# 阅读过的邮件删除时间为： 7200 = 3600*2 秒
MAIL_RETURN_AFTER_SEND				= 604800		# 未读邮件退信时间，单位：秒；表示多长时间邮件没有读过就会被退信
MAIL_RETURN_CHECK_TIME				= 3600			# 退信检查间隔时间，单位：秒
MAIL_RETURN_PROCESS_TIME			= 1				# 退信处理间隔时间（即多长时间处理一封退信），单位：秒

MAIL_RECEIVE_TIME_QUICK				= 0				# 快递收信时间，单位：秒
MAIL_RECEIVE_TIME_NORMAL			= 7200			# 普通信件收信时间，单位：秒

MAIL_FARE							= 50			# 邮寄收费
MAIL_SEND_MONEY_RATE				= 0.002			# 邮寄金钱的收费比率
MAIL_SEND_ITEM_FARE					= 50			# 邮寄物品附加收费
MAIL_UPPER_LIMIT					= 50			# 收件人可存在的邮件数量

# --------------------------------------------------------------------------------
# about bank
# --------------------------------------------------------------------------------
BANK_MONEY_LIMIT				= 4000000000# 存储在钱庄的金钱的上限
BANKBAG_NORMAL_ORDER_COUNT		= 28		# 钱庄包裹最大格子数
BANK_MAX_COUNT					= 7			# 钱庄包裹数量上限
BANK_HIRE_COST_MONEY			= 100		# 前2组包裹位租用费用，暂定100金钱
BANK_HIRE_COST_GOLD				= 10		# 后2组包裹位租用费用，暂定10元宝


# --------------------------------------------------------------------
# 装备修理
# --------------------------------------------------------------------


# --------------------------------------------------------------------------------
# 商品赎回
# --------------------------------------------------------------------------------
REDEEM_ITEM_MAX_COUNT				= 7			# 可赎回商品列表的最大数量，暂定12


# --------------------------------------------------------------------------------
# 摆摊系统
# --------------------------------------------------------------------------------
VEND_ITEM_MAX_COUNT					= 30			# 摆摊物品列表的最大长度
VEND_SIGNBOARD_MAX_LENGTH			= 20			# 摆摊招牌的最大字节数
VEND_PET_MAX_COUNT					= 6				# 摆摊宠物列表的最大长度


# --------------------------------------------------------------------------------
# 玩家关系，RoleRelation( wsf )
# --------------------------------------------------------------------------------
# 师徒关系
TEACH_MASTER_MIN_LEVEL				= 60			# 能成为师父的玩家的最小级别
TEACH_END_TEACH_LEAST_LEVEL			= 50			# 徒弟出师的最小等级
TEACH_PRENTICE_LOWER_LIMIT			= 10			# 能够成为徒弟的玩家级别下限
TEACH_PRENTICE_UPPER_LIMIT			= 49			# 能够成为徒弟的玩家级别上限

TEACH_PRENTICE_MAX_COUNT			= 3				# 一个玩家最多收3个徒弟
TEACH_COMMUNICATE_DISTANCE			= 10			# 拜师时师父与徒弟的距离不能超过10米
TEACH_END_TEACH_AWARD_LIMIT			= 55			# 能够获得出师奖励、组队奖励的徒弟等级不能超过55

TEACH_TEAM_EXP_ADDITIONAL_PERCENT	= 0.2			# 师徒组队经验加成比例
TEACH_TEAM_KILL_BENEFIT_DISTANCE	= 100			# 师徒组队杀怪，能够获得经验加成的范围
TEACH_UPGRADE_MONEY_AWARD_RATE		= 50			# 徒弟升级，师父获得的金钱奖励计算参数
TEACH_END_MASTER_MONEY_AWARD		= 100			# 成功出师，师父获得的金钱奖励计算参数
TEACH_END_MASTER_EXP_AWARD			= 10000			# 成功出师，师父获得的经验奖励计算参数
TEACH_END_MASTER_CREDIT_AWARD		= 20				# 成功出师，师父获得的功勋点奖励计算参数
TEACH_END_PRENTICE_MONEY_AWARD		= 50			# 成功出师，徒弟获得的金钱奖励计算参数
TEACH_END_PRENTICE_EXP_AWARD		= 8000			# 成功出师，徒弟获得的经验奖励计算参数
TEACH_QUERY_MAX_LENGTH			= 14			# 玩家一次能查询的注册收徒信息条数
TEACH_REGISTER_VALID_TIME			= 345600		# 玩家注册拜师管理器有效时间，单位（秒）


# 恋人关系
SWEETIE_NUM_LIMIT					= 15			# 恋人的最大个数
SWEETIE_LEVEL_LIMIT					= 18			# 18级以上(含18级)的玩家才能结为恋人

# 夫妻关系
COUPLE_LEVEL_LIMIT					= 20			# 20级以上(含20级)的玩家才能结为夫妻
COUPLE_WEDDING_CHARGE				= 300000		# 结婚需要每人花费300000金钱
COUPLE_FORCE_DIVORCE_CHARGE			= 500000		# 强制离婚需要500000rmb,太黑了.
COUPLE_HONGBAO_ITEM_ID				= 60101012		# 物品红包的id
COUPLE_WEDDING_RING_PRICE			= 300000		# 找回结婚戒指的花费
COUPLE_TEAM_EXP_PERCENT				= 0.1			# 夫妻组队经验加成比例
COUPLE_SWARE_DISTANCE				= 10.0			# 结婚双方需要保持的最大距离范围

ADD_SWEETIE_NEED_FRIENDLY_VALUE		= 2000		# 加恋人至少需要的友好度
ADD_COUPLE_NEED_FRIENDLY_VALUE		= 5000		# 结婚至少需要的友好度
FORCE_DIVORCE_COST					= 400000	# 强制离婚费用
RELATION_FOE_NUM_LIMIT				= 500		# 玩家仇人上限

RELATION_ALLY_SWEAR_DISTANCE		= 30		# 玩家结拜时的有效距离
RELATION_ALLY_LEVEL_LACK				= 15		# 玩家能够结拜的最小级别
RELATION_ALLY_COST					= 100000	# 结拜花费
RELATION_ALLY_NEED_FRIENDLY_VALUE	= 2000		# 结拜至少需要的友好度
ALLY_CHANGE_TITLE_COST				= 50000	# 改结拜称号所需的金钱
ALLY_TEAM_EXP_PERCENT				= 0.05		# 结拜关系组队经验加成百分比
RELATION_ALLY_NEW_COST				= 50000	# 结拜加入新成员花费

TEACH_SPACE_MONSTER_COUNT		= 40		# 师徒副本小怪数量
TEACH_SPACE_ENTER_TEAMMATE_DISTANCE = 70	# 进入师徒副本的队友距离

# 结拜需要的物品列表array of ( 物品ID, 物品数量 )
RELATION_ALLY_NEED_ITEMS			= [ ( 50101105, 1 ), ( 50101106, 1 ) ]

# 结拜默认称号名称
TITLE_ALLY_DEFAULT_NAME				= cschannel_msgs.VOICE_COMMON_CONST_1

# --------------------------------------------------------------------
# about TONG( designed by kebiao )
# --------------------------------------------------------------------
# 帮会在某等级下最多可招收家族数量
TONG_FAMILY_COUNT_LIMIT = {}
TONG_FAMILY_COUNT_LIMIT[1]		= 3	#tongLevel, familyMaxCount
TONG_FAMILY_COUNT_LIMIT[2]		= 5
TONG_FAMILY_COUNT_LIMIT[3]		= 7
TONG_FAMILY_COUNT_LIMIT[4]		= 9
TONG_FAMILY_COUNT_LIMIT[5]		= 10

TONG_STORAGE_LOG_COUNT			= 200	# 帮会仓库最多存储的log信息条数
TONG_BAG_ORDER_COUNT			= 80	# 帮会仓库包裹的最大格子数
TONG_JOIN_MIN_LEVEL				= 10	# 加入帮会的最小等级

# 帮会铁匠铺折扣
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

# 帮会俸禄兑换额上限
TONG_SALARY_EXCHANGE_RATE = {	1 : 9000, \
								2 : 11700, \
								3 : 14400, \
								4 : 17100, \
								5 : 19800
							}

TONG_SALARY_EXCHANGE_MIN_RATE = 5000 		# 帮会俸禄兑换额下限

JOIN_TONG_INIT_CONTRIBUTE			= 0		# 加入帮会初始贡献度
JOIN_TONG_CHIEF_INIT_CONTRIBUTE		= 100	# 帮主初始贡献度

#帮会擂台相关
TONG_ABATTOIR_PRESTIGE_LIMIT	= 100			# 申请擂台赛的帮会声望限制
TONG_ABATTOIR_MAX_NUM			= 16				# 参加擂台赛的帮会数上限
TONG_ABATTOIR_MATCH_TIME		= 15			# 一场比赛要进行的时间
TONG_ABATTOIR_REST_TIME			= 5				# 一场比赛进行完后休息的时间
TONG_ABATTOIR_MAX_MEMBER   		= 15			# 每个帮会进入战场的人数上限
TONG_ABATTOIR_SINGUP			= 1				#开始报名
TONG_ABATTOIR_ENTER				= 2				#入场
TONG_ABATTOIR_START				= 3				#1场比赛开始
TONG_ABATTOIR_END				= 4				#1场比赛结束
TONG_ABATTOIR_OVER				= 0				#全部比赛结束（未开启）

# --------------------------------------------------------------------
# about gem( designed by wsf )
# --------------------------------------------------------------------
GEM_COUNT_UPPER					= 5			# 玩家能够领取的宝石上限，包括宠物宝石
GEM_ACTIVATE_COST				= 10000		# 激活宝石所需花费
GEM_ROLE_COMMON_COUNT_UPPER		= 50		# 能领取的玩家经验石数量上限
GEM_PET_COMMON_COUNT_UPPER		= 50		# 能领取的宠物经验石数量上限
GEM_PET_COMMON_VALUE_UPPER		= 1000000000# 能领取的代练时间上限和宝石可存储的经验上限
GEM_PET_COMMON_EXP_PERCENT		= 0.02		# 每个宠物经验石所获经验加成百分比
GEM_WORK_HARD_RATE				= 1.5		# 刻苦代练所获经验加成的倍率
GEM_HIRE_PAY					= 10000		# 领取一个经验石的花费


# --------------------------------------------------------------------
# about SpecialShop( designed by wsf )
# --------------------------------------------------------------------
SPECIAL_SHOP_HOT_ITEM_COUNT		= 15		# 热销榜排名数量


# --------------------------------------------------------------------
# about Prestige( designed by wsf )
# --------------------------------------------------------------------
PRESTIGE_UPLIMIT				= 45000		# 声望的最大值限制
PRESTIGE_LOWERLIMIT				= -39000	# 声望的最小值限制

# --------------------------------------------------------------------
INVBUYPERCENT					= 0.2		# 装备和物品的回购价格

PENDING_BUFF_ID					= 32239700101		# 玩家未决状态buff id
PENDING_SKILL_ID				= 322397001			# 未决状态技能id
PROWL_BUFF_ID					= 20002				# 潜行buff id
FLY_TELEPORT_BUFF_ID			= 32239700101		# 玩家未决状态buff id
FOLLOW_SKILL_ID					= 322403001			# 跟随技能id
FOLLOW_BUFF_ID					= 32240300101			# 跟随buff id

# --------------------------------------------------------------------
WUDAO_MAX_NUM                   = 64                # 武道大会一个级别最多参加数量
WUDAO_TIME_REST 				= 3 				# 中间休息时间
WUDAO_TIME_PREPARE				= 2 				# 进场准备时间
WUDAO_TIME_UNDERWAY 			= 5 				# 比赛时间
WUDAO_TIME_SPACE_LIVING			= WUDAO_TIME_PREPARE + WUDAO_TIME_UNDERWAY # 一场比赛的时间
WUDAO_TIME_ROUND				= WUDAO_TIME_REST + WUDAO_TIME_PREPARE + WUDAO_TIME_UNDERWAY # 武道大会一轮的时间
# --------------------------------------------------------------------
TEAM_CHALLENGE_MAX_NUM          = 32                # 组队擂台一个级别最多参加队伍数
TEAM_CHALLENGE_TIME_REST 		= 3 				# 中间休息时间
TEAM_CHALLENGE_TIME_PREPARE		= 2 				# 进场准备时间
TEAM_CHALLENGE_TIME_UNDERWAY 	= 10 				# 比赛时间
TEAM_CHALLENGE_TIME_ROUND		= TEAM_CHALLENGE_TIME_REST + TEAM_CHALLENGE_TIME_PREPARE + TEAM_CHALLENGE_TIME_UNDERWAY # 一轮的时间
ROLECOMPETITION_MAX_NUM         = 30                # 个人竞技一个级别最多参加人数

TEAM_CHALLENGE_JOIN_LEVEL_MIN 		= 60 		#比赛的最小级别
TEAM_CHALLENGE_JOIN_LEVEL_MAX 		= 150		#比赛的最大级别
TEAM_CHALLENGE_JOIN_LEVEL_INCREASE  = 9 		#比赛的等级段递增数
ROLE_SOMPETITION_JOIN_LEVEL_MIN		= 60		#个人竞技比赛的最小级别

TEAM_CHALLENGE_MEMBER_MUST				= 3				#队伍的最少人数
TEAM_CHALLENGE_RECRUIT_DIALOG_TIME		= 30			#对话框弹出的时间

TEAM_CHALLENGE_REWARD_COMMON		= 1 # 保底奖励
TEAM_CHALLENGE_REWARD_WIN			= 2 # N轮胜利奖励
TEAM_CHALLENGE_REWARD_CHAMPION		= 3 # 冠军奖励

# --------------------------------------------------------------------

LUCKY_BOX_ITEM_ZHAOCAI			= 60101008			# 天降宝盒招财宝盒id
LUCKY_BOX_ITEM_JINBAO			= 60101009			# 天降宝盒进宝宝盒id
LUCKY_BOX_MOSTER_LEVEL			= 20				# 掉宝盒怪物最低级别
LUCKY_BOX_DROP_RATE				= 0.015				# 掉宝盒的概率
LUCKY_BOX_USE_LEVEL_CHECK		= 5		# 	玩家使用天降宝盒时等级不能小于其5级以上


#---------------------------------------------------------------------------
FACTION_XL 						= 37				# 兴隆镖局势力声望
FACTION_CP 						= 38				# 昌平镖局势力声望
DART_ROB_MIN_LEVEL				= 3					# 劫镖等级限制（劫镖者和被劫镖车等级差超过这个值，将计算PK值，并且也无法完成任务）
DART_INITIAL_POINT				= 50				# 镖局初始积分


#活动管理
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
BUFF_ID_REVIVE_IN_TIANGUAN = 22120					# 可以在天关原地复活的buffID
BUFF_ID_EXTRA_EXP_IN_TIANGUAN = 22016				# 天关收益buff的ID

# --------------------------------------------------------------------
# 全民知识问答
# --------------------------------------------------------------------
QUIZ_MIN_LEVEL_LIMIT			= 10		# 知识问答最低级别限制
QUIZ_QUESTION_COUNT				= 30		# 知识问答活动题目数量
QUIZ_LUCKY_STAR_COUNT			= 3			# 幸运星数量
QUIZ_GOLD_CONSUME				= 30		# 元宝答题一次消耗的数量
QUIZ_READING_QUESTION_TIME		= 10.0		# 读题目所需时间
QUIZ_ANSWER_TIME				= 10.0		# 答题时间
QUIZ_QUESTION_TIME				= 22.0		# 考一道题所需时间

#---------------------------------------------------------------------
# 技能状态和物品状态的映射字典，key:技能状态，value:物品状态
#---------------------------------------------------------------------
SKILL_STATE_TO_ITEM_STATE = {
	csstatus.SKILL_NOT_READY			: csstatus.CIB_MSG_TEMP_CANT_USE_ITEM,
	csstatus.SKILL_CAST_ENTITY_LEVE_MIN : csstatus.CIB_MSG_ITEM_CAST_LEVEL_MIN,
	csstatus.SKILL_CAST_ENTITY_LEVE_MAX : csstatus.CIB_MSG_ITEM_CAST_LEVEL_MAX,
	csstatus.SKILL_CAST_OBJECT_NOT_ENEMY: csstatus.SKILL_CANT_CAST_ENTITY,
	csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER:csstatus.CIB_MSG_OBJECT_NOT_MONSTER,
	}

#---------------------------------------------------------------------
# 赛马预备位置
#---------------------------------------------------------------------
Start_Positions = [(6.222151,18.349606,-130.868744),	#普通赛马位置
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

Start_Positions_03 = [(87.356224, 0.020237, 14.283286),		#圣诞节赛马开始位置
						(86.986404, 0.023053, 16.305824),
						(86.407257, 0.034930, 18.760397),
						(85.831665, 0.035362, 20.798906),
						(85.394630, 0.030320, 22.764093),
						(84.757584, 0.024771, 25.057795),
						(84.233978, 0.004829, 27.342119),
						]
#---------------------------------------------------------------------
# 需要显示界面的spaceCopy
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


#----------------活动奖励领取
PCU_TAKEPRESENTWITHOUTID	= 0			#不带订单号的奖品领取类型
PCU_TAKESILVERCOINS			= 1			#银元宝领取类型
PCU_TAKEPRESENT				= 2			#带订单号的奖品领取类型
PCU_TAKECHARGE				= 3			#充值领取类型
PCU_TAKECHARGEUNITE			= 4			#领取奖品(带订单和不带订单)
PCU_TAKEPRESENTUNITE		= 5			#所有奖品的领取(除充值外)
PCU_TAKECHARGEUNITE_SINGLE		= 6		#一次领取一个物品的（带/不带订单）奖励

# --------------------------------------------------------------------
# 装备灵魂锁链属性加成
# --------------------------------------------------------------------
EQUIP_GHOST_BIND_ADD_BASERATE = 0.1


# --------------------------------------------------------------------
# 科举考官位置信息
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

#物品品质对应的广播字体颜色 by姜毅
ITEM_BROAD_COLOR_FOR_QUALITY = {
									ItemTypeEnum.CQT_WHITE	:	"@F{fc=(255,255,255)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_BLUE	:	"@F{fc=(0,255,255)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_GOLD	:	"@F{fc=(255,255,0)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_PINK	:	"@F{fc=(255,0,255)}[%s]@F{fc=(255,255,0)}",
									ItemTypeEnum.CQT_GREEN	:	"@F{fc=(0,255,0)}[%s]@F{fc=(255,255,0)}"
								}

GAMERANKING_SEND_DATANUM = 5 #--------------排行榜一次发送数据的条数

# --------------------------------------------------------------------
# 新单人骑宠
# --------------------------------------------------------------------
VEHICLE_DIS_LEVEL_MAX                   = 6  #骑宠高于玩家等级将不可以进行召唤、激活、传功
VEHICLE_AMOUNT_MAX			= 12
VEHICLE_MODEL_BOUND			= Math.Vector3( ( 1.5, 2.0, 1.5 ) )		#骑宠统一的bounding box值（长、高、宽）
VEHICLE_DEADTIEM_LIMIT			= 18446744073709551615	# 骑宠死亡时间上限 UINT64 by姜毅
VEHICLE_DEADTIEM_MIN			= 0			# 骑宠死亡时间下限 by姜毅
VEHICLE_MOUNT_DISTANCE			= 30.0		# 玩家上坐骑距离限制
VEHICLE_SKILLS_TOTAL			= 4			# 骑宠可学习技能总数

VEHICLE_EQUIP_MAPS = {	ItemTypeEnum.VEHICLE_CWT_HALTER 		: "halterID",		# 笼头
						ItemTypeEnum.VEHICLE_CWT_SADDLE 		: "saddleID",		# 马鞍
						ItemTypeEnum.VEHICLE_CWT_NECKLACE		: "necklaceID",		# 项链
						ItemTypeEnum.VEHICLE_CWT_CLAW 			: "clawID",			# 爪环
						ItemTypeEnum.VEHICLE_CWT_MANTLE 		: "mantleID",		# 披风
						ItemTypeEnum.VEHICLE_CWT_BREASTPLATE 	: "breastplateID"	# 护甲
					}

VEHICLE_FOOD_ITEMID = [ 60508021,60508022, 60508023 ]	#骑宠粮草ID

VEHICLE_STEP_UPGRADE_ITEMID = { 1:[ 60508001,60508002 ],	#升阶阶次对应物品ID
							2:[ 60508001,60508002 ],
							3:[ 60508001,60508002 ],
							4:[ 60508001,60508002 ],
							5:[ 60508003,60508004 ],
							6:[ 60508003,60508004 ],
							7:[ 60508003,60508004 ],
							8:[ 60508003,60508004 ],
							9:[ 60508003,60508004 ],
							}

VEHICLE_SEALED_NEED_ITEM = { 1:60508005,	#封灵阶次对应物品ID
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
MAX_FULL_DEGREE		= 31536000	#骑宠饱腹度上限1年


# 监狱捐献数据   最小级别 最大级别 金钱
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
# 特定物品流通等级限制
# --------------------------------------------------------------------
SPECIFIC_ITEM_GIVE_LEVEL = 30

KITBAG_CANT_UNLOCK_INTERVAL			= 3		# 背包密码锁解锁期限，单位：秒
KITBAG_FORCE_UNLOCK_LIMIT_TIME		= 72 * 3600		# 背包强制解锁所需时间

BANK_CANT_UNLOCK_INTERVAL			= 60		# 仓库密码锁解锁期限，单位：秒
BANK_FORCE_UNLOCK_LIMIT_TIME		= 72 * 3600		# 仓库强制解锁所需时间


SELL_POINT_CARD_YAJIN			= 50000			# 寄售点卡押金
SELL_POINT_CARD_LASTTIME		= 86400			# 每张点卡的寄售有效时间（一天）


TISHOU_SHOP_INFO_QUERY_PAGE_SIZE		= 26	# 替售商铺查询页面大小
TISHOU_ITEM_INFO_QUERY_PAGE_SIZE		= 12	# 替售物品查询页面大小
TISHOU_PET_INFO_QUERY_PAGE_SIZE			= 18	# 替售宠物查询页面大小


TISHOU_SHOP_INFO						= 0     # 替售商店信息
TISHOU_ITEM_LOWERLEVEL					= 1     # 物品等级下限
TISHOU_ITEM_UPPERLEVEL					= 2     # 物品等级上限
TISHOU_ITEM_TYPELIMIT					= 3     # 物品类型
TISHOU_ITEM_QALIMIT						= 4     # 物品品质
TISHOU_ITEM_NAME						= 5     # 物品名字
TISHOU_ITEM_METIER						= 6     # 物品职业
TISHOU_PET_LOWERLEVEL					= 7     # 宠物等级下限
TISHOU_PET_UPPERLEVEL					= 8     # 宠物等级上限
TISHOU_PET_ERALIMIT						= 9     # 第几代宠物
TISHOU_PET_GENDERLIMIT					= 10    # 宠物性别
TISHOU_PET_METIERLIMIT					= 11    # 宠物职业
TISHOU_PET_BREEDLIMIT					= 12    # 宠物繁殖与否
TISHOU_OWNER_NAME						= 13	# 店铺主人名字


# --------------------------------------------------------------------
# 切磋相关
# --------------------------------------------------------------------
QIECUO_REQUEST_MAXDIS					= 10.0	# 切磋双方邀请最大距离
QIECUO_REQUEST_TIME						= 15.0	# 切磋邀请时间限制
QIECUO_HP_NOT_FULL						= 10.0	# 切磋邀请血量不满提示时间限制


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
# 替售界面物品类型
# --------------------------------------------------------------------
TI_SHOU_WEAPON					= 1		#武器
TI_SHOU_ARMOR					= 2		#防具
TI_SHOU_PRODUCE_STUFF			= 3		#制作材料
TI_SHOU_TYPE_NONE				= 4		#无

# --------------------------------------------------------------------
# 替售界面物品职业
# --------------------------------------------------------------------
TI_SHOU_CLASS_FIGHTER							= 'Z'		# 战士
TI_SHOU_CLASS_SWORDMAN							= 'J'		# 剑客
TI_SHOU_CLASS_ARCHER							= 'S'		# 射手
TI_SHOU_CLASS_MAGE								= 'F'		# 法师


#替售NPC className
TISHOU_NPC_CLASSNAME	= "10111314"
 # 小精灵 className
EIDOLON_NPC_CLASSNAME	= "10111574"
AUTO_CREATE_EIDOLON_NPC_LEVEL	= 30	# 自动帮玩家召唤小精灵的级别上限
VIP_EIDOLON_LIVE_TIME			= 300	# vip小精灵的存活时间

#点卡查询页面大小
POINT_CARD_PAGE_SIZE			 = 10


#替售NPC 模型
TI_SHOU_MODEL_1			= "gw1189_2"
TI_SHOU_MODEL_2			= "gw1141_3"
TI_SHOU_MODEL_3			= "gw1141_2"
TI_SHOU_MODEL_4			= "gw1181_1"
TI_SHOU_MODEL_5			= "gw1157_3"
TI_SHOU_MODEL_6			= "gw1179_2"
TI_SHOU_MODEL_7			= "gw1180_1"


#副本复活点
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


# 只能在副本进入NPC复活的地图
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

IMAGE_VERIFY_TIME_MAP = { 1:180, 2:60, 3:60 }		# 反外挂验证轮次对应的回答问题时间


#收集系统
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



TONG_CITYWAR_SIGNUP_MAX  = 8 # 帮会城市战最多允许报名数


#帮会会标相关 by 姜毅
USER_TONG_SIGN_REQ_MONEY = 2000000
USER_TONG_SIGN_REQ_TONG_LEVEL = 3


#竞技类活动开始缓冲和结束时间
END_TIME			  	= 120				# 120秒	距离把所有角色踢出副本
SAVE_MODEL_TIME			= 300				# 300秒

#个人竞技活动时间
ROLE_COMPETITION_TIME	= 1800				# 1800秒（30分钟）的个人竞赛时间

#家族竞技活动时间
FAMILY_COMPETITION_TIME = 3600				# 3600秒（60分钟）的家族竞赛时间


#组队竞技活动时间
TEAM_COMPETITION_TIME = 1800				# 1800秒（30分钟）的家族竞赛时间

#帮会竞技奖励
TONG_COMPETITION_AWARD01 = 10381522			# 帮会竞技经验奖励
TONG_COMPETITION_AWARD02 = 5059136			# 帮会竞技潜能奖励

CHALLENGE_CHAMPION_REWARD_LIVING = 7 * 24 * 60 *60 # 竞技类活动冠军奖励的保存时间( 一个星期 )
TONG_CITY_WAR_CHAMPION_REWARD_LIVING = 7 * 24 * 60 * 60 # 帮会城市战活动冠军奖励保存时间( 一个星期 )

#开关Object模型更改后缀
TOUCH_OBJECT_MODELNUM 	= "_on"

C_PREFIX_GBAE					= "GBAE"	# baseApp enityt注册到全局变量的key前缀，广播全局消息时，cell也会使用此定义。11:06 2010-4-20，wsf


#------------ItemAwards 奖励玩家物品相关
AWARDITEM_ACCOUNT	= 1		# 通过账号获取玩家的物品奖励
AWARDITEM_NAME		= 2		# 通过玩家名字获取玩家的物品奖励
AWARDITEM_ORDER		= 3		# 通过订单号获取玩家的物品奖励
AWARDITEM_ANO			= 4		# 通过订单号 玩家名字 账号 获取奖励

OLD_REWARD_LEVEL_LIM = 60		# 老玩家在线奖励领取等级上限


#----------非诚勿扰------------------
ANONYMITY_LOVE_MSG_PAY	= 50000				#匿名发公告费用
LOVE_MSG_PAY			= 5000				#普通公告费用
FCWR_MSGS_LENGTH			= 22			#一次获取告白条目数
FCWR_LOVE_MSG_MIN_LENGTH	= 10			#告白最少字数
FCWR_LOVE_MSG_MAX_LENGTH	= 200			#告白最多字数

FCWR_VOTE_SPEED				= 1800			#投票间隔时间

FCWR_REWARDS = { csdefine.FCWR_VOTE_ALL 			: [60101151,110103038],		#万众瞩目称号 + 长相厮守
				csdefine.FCWR_VOTE_KAN_HAO			: [60101155,110103038],		#天生一对称号 + 长相厮守
				csdefine.FCWR_VOTE_QING_DI			: [60101152,110103038],		#大众情人称号 + 长相厮守
				csdefine.FCWR_VOTE_SHI_LIAN			: [60101153,110103038],		#梦中情人称号 + 长相厮守
				csdefine.FCWR_MAX_COUNT_VOTER_1		: [60101154,110103041],		#热血好青年 + 500元宝
				csdefine.FCWR_MAX_COUNT_VOTER_2		: [60101154,110103042],		#热血好青年 + 250元宝
				csdefine.FCWR_MAX_COUNT_VOTER_3		: [60101154,110103043],		#热血好青年 + 100元宝
					}

# --------------------------------------------------------------------
# 魅力果树活动
# --------------------------------------------------------------------
FRUIT_PICK_DISTANCE						= 5.0		# 魅力果树采集距离
FRUIT_PLANT_DISTANCE					= 4.0		# 魅力果树种植间距

# --------------------------------------------------------------------
# 装备属性抽取
# --------------------------------------------------------------------
EQUIP_EXTRACT_QUALITYS = [ ItemTypeEnum.CQT_BLUE, ItemTypeEnum.CQT_GOLD, ItemTypeEnum.CQT_PINK, ItemTypeEnum.CQT_GREEN ]	# 装备抽取品质定义
EQUIP_EXTRACT_LEVEL_MIN	= 10												# 装备抽取装备需求等级
EQUIP_EXTRACT_NEEDITEMS = 60101174											# 装备抽取需求封灵石
EQUIP_EXTRACT_ITEM_ODDS = 0.3												# 装备抽取需求封灵石成功概率
EQUIP_EXTRACT_SUNEEDITEMS = 60101175 										# 装备抽取需求超级封灵石
EQUIP_EXTRACT_SUITEMS_ODDs = 0.45											# 装备抽取需求超级封灵石成功概率
EQUIP_EXTRACT_PROITEM = 60101176											# 装备抽取成功生成韵灵琥珀
EQUIP_EXTRACT_EXCITEM = 60101177											# 装备抽取附加成功率物品ID
EQUIP_EXTRACT_EXCITEM_ODDS = 1.0											# 装备抽取附加物品成功率
EQUIP_POURE_ATTR_SAME_COUNT = 2

# --------------------------------------------------------------------
# 装备飞升
# --------------------------------------------------------------------
EQUIP_UP_RATE = 0.9															# 装备成功飞升的几率
EQUIP_UP_EXTRA_SLOT_RATE = 0.03												# 飞升时产生第二个属性空位的几率
EQUIP_UP_BASE_LEVEL = 60													#小于这个级别的装备无法飞升



# --------------------------------------------------------------------
# 装备属性重铸
# --------------------------------------------------------------------
EQUIP_ATTR_REBUILD_LEVEL = 30													# 装备属性重铸的最低级别
EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR = 0.2										# 一条属性价值因子占装备价值因子的百分比
EQUIP_ATTR_REBUILD_STAGES = 10													# 装备属性重铸的阶次

#---------------------------------------------------------------------
#夸父神殿(entity 类型)
#---------------------------------------------------------------------
KUA_FU_ENTITY_TYPE_NPC		= 0				#NPC
KUA_FU_ENTITY_TYPE_MONSTER	= 1				#小怪
KUA_FU_ENTITY_TYPE_BOSS		= 2				#BOSS
KUA_FU_ENTITY_TYPE_STONE	= 3				#石像
KUA_FU_ENTITY_TYPE_TRAP		= 4				#陷阱
KUA_FU_ENTITY_TYPE_ICE		= 5				#冰块
KUA_FU_ENTITY_TYPE_DOOR		= 6				#门
KUA_FU_ENTITY_TYPE_SHITI	= 7				#尸体
KUA_FU_ENTITY_TYPE_TREE		= 8				#神树


KUA_FU_EVENT_JUBI_FLY_TO_SKY		= 1										#据比飞向天空
KUA_FU_EVENT_SPAWN_TO_DEADBODY		= 2										#刷出两个死尸
KUA_FU_EVENT_CENTER_FIRE_FLY_TO_SKY	= 3										#触发中心火球飞向天空
KUA_FU_EVENT_FEILIAN_KUI_DI			= 4										#飞廉跪地
KUA_FU_EVENT_STONE_DESTROY			= 5										#石像被摧毁
KUA_FU_EVENT_ZHAO_CHONGZHI			= 6										#招小虫子
KUA_FU_EVENT_XUANFENG				= 7										#产生旋风
KUA_FU_EVENT_TAOZHI					= 8										#产生桃子
KUA_FU_EVENT_HOU_QING				= 9										#后卿回跑



KUA_FU_ACTIVITY_TIME				= 3600				#夸父神殿活动时间

#---------------------------------------------------------------------
#小兔快跑(entity 类型)
#---------------------------------------------------------------------
#刷新点
RABBIT_RUN_ENTITY_TYPE_NPC							= 0
RABBIT_RUN_ENTITY_TYPE_ROAD_POINT					= 1

RABBIT_RUN_ITEM_RADISH								= 50101160				#大白兔奶糖
RABBIT_RUN_CATCH_RABBIT_SKILL_ID					= 344012001				#抓小兔技能ID
RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID 				= 34401200101			#变身为兔子的BUFF ID
RABBIT_RUN_CATCH_RABBIT_WOLF_BUFF_ID				= 34401200102			#变身为狼的BUFF ID
RABBIT_RUN_WAIT_BUFF_ID								= 34402100101			#等待活动开始BUFF ID
RABBIT_RUN_CANT_MOVE_BUFF_ID						= 34402400101			#定身BUFF ID
RABBIT_RUN_QUESTION_BUFF_ID							= 34402000101			#回答问题BUFF ID

#玩家变身为狼或兔子的时间（距离赛跑开始）
RABBIT_RUN_TIME_TO_CHANGE_BODY						= 30					#单位（秒）
RABBIT_RUN_WAIT_TIME								= 180					# 小兔快跑等待时间
RABBIT_RUN_CANT_ENTER_TIME							= 60					# 小兔快跑不允许进入时间（距离活动开始）

RABBIT_RUN_NEED_PLAYER_AMOUNT						= 10						#活动开启需要最少参加玩家数量
RABBIT_RUN_WOLF_CONTROL_NUM							= 5						#狼的出现控制数字

RABBIT_RUN_ACTIVITY_TIME							= 1800					#活动时间

RABBIT_RUN_NPC_REVIDE_MIN_TIME						= 0						#NPC复活最短时间
RABBIT_RUN_NPC_REVIDE_MAX_TIME						= 120					#NPC复活最长时间

RABBIT_RUN_POINT_TRAP_RANGE							= 30					#路点陷阱大小


# -------------------------------------------------------------
# 定时掉落 时间关系而且量不多 暂此作定义
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
# 增加破绽触发率属性指定的技能ID
# -------------------------------------------------------------
EQUIP_EFFECT_ADD_ODDS_SKILL1 	= 311413			# 冲锋
EQUIP_EFFECT_ADD_ODDS_SKILL2 	= 311101			# 猛击
EQUIP_EFFECT_ADD_ODDS_SKILL3 	= 311104			# 横扫
EQUIP_EFFECT_ADD_ODDS_SKILL4	= 321207			# 泰山压顶
EQUIP_EFFECT_ADD_ODDS_SKILL5 	= 311120			# 劲射
EQUIP_EFFECT_ADD_ODDS_SKILL6 	= 311123			# 乱射
EQUIP_EFFECT_ADD_ODDS_SKILL7 	= 321210			# 落日
EQUIP_EFFECT_ADD_ODDS_SKILL8 	= 311114			# 快剑
EQUIP_EFFECT_ADD_ODDS_SKILL9 	= 311117			# 连绵剑
EQUIP_EFFECT_ADD_ODDS_SKILL10 	= 321208			# 追魂夺命
EQUIP_EFFECT_ADD_ODDS_SKILL11 	= 312109			# 火球术
EQUIP_EFFECT_ADD_ODDS_SKILL12 	= 312111			# 电击术
EQUIP_EFFECT_ADD_ODDS_SKILL13 	= 322445			# 风卷残云

# -------------------------------------------------------------
# 破绽属性数量限制
# -------------------------------------------------------------
EQUIP_EFFECT_FLAW_LIMIT			= 3					# 法宝破绽属性最多拥有数

GOD_WEAPON_NAME_COLOR			= (255.0,0.0,0.0)	# 神器名字颜色 by 姜毅

MAX_FLYING_SPEED_INC_PERCENT	= 200.0				# 飞行骑宠的最大速度增益百分比

# --------------------------------------------------------------------
# 装备耐久缩放值
# --------------------------------------------------------------------
EQUIP_HARDINESS_UPDATE_VALUE = 10000.0


# --------------------------------------------------------------------
# 关于竞技集合坐标
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
# 华山阵法/挑战副本
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
# NPC屏幕中央喊话范围限定
# --------------------------------------------------------------------
CHAT_CHANNEL_SC_HINT_AREA = 50							# NPC屏幕中央喊话范围

# --------------------------------------------------------------------
# 野外副本
# --------------------------------------------------------------------
SPACE_COPY_YE_WAI_EASY 			= 0
SPACE_COPY_YE_WAI_DIFFICULTY	= 1
SPACE_COPY_YE_WAI_NIGHTMARE		= 2

SPACE_COPY_YE_WAI_ENTER_MAP = {
	SPACE_COPY_YE_WAI_EASY			: 1,
	SPACE_COPY_YE_WAI_DIFFICULTY	: 3,
	SPACE_COPY_YE_WAI_NIGHTMARE		: 5,
}

# 仿灵魂战神召唤类副本
ROLE_CALL_PGNAGUAL_LIMIT_EASY			= 12 					# 单人副本玩家可以召唤的盘古守护数量
ROLE_CALL_PGNAGUAL_LIMIT_DIFFICULT		= 8						# 三人副本玩家可以召唤的盘古守护数量
ROLE_CALL_PGNAGUAL_LIMIT_NIGHTMARE		= 5						# 五人副本玩家可以召唤的盘古守护数量

# 盘古守护系统允许招怪数量
ROLE_CALL_PGNAGUAL_LIMIT				= 12 					# 玩家可以召唤盘古守护的数量

# 防沉迷
WALLOW_STATES = set( [
	csdefine.WALLOW_STATE_COMMON,
	csdefine.WALLOW_STATE_HALF_LUCRE,
	csdefine.WALLOW_STATE_NO_LUCRE
	] )										# 所有收益状态

# 在 base 中初始化的角色属性
ROLE_INIT_BASES = [ \
	csdefine.ROLE_INIT_OPRECORDS,
	csdefine.ROLE_INIT_PETS,
	csdefine.ROLE_INIT_QUICK_BAR,
	csdefine.ROLE_INIT_VEHICLES,
	csdefine.ROLE_INIT_OFLMSGS,
	csdefine.ROLE_INIT_DAOFA,
	]

# 在 cell 中初始化的角色属性
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

# 可被鼠标选中的 entities
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

# 种族、职业、性别集合
ALL_GENDERS 							= ( csdefine.GENDER_MALE, csdefine.GENDER_FEMALE )
ALL_PROFESSIONS 						= ( csdefine.CLASS_FIGHTER, csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER, csdefine.CLASS_MAGE )
ALL_RACES 								= ( csdefine.YANHUANG, csdefine.JIULI, csdefine.FENGMING )

# 不同职业的出生点（出生所在地）
RACE_CLASS_MAP = {}
RACE_CLASS_MAP[csdefine.CLASS_FIGHTER]				= csdefine.FENGMING
RACE_CLASS_MAP[csdefine.CLASS_SWORDMAN]				= csdefine.FENGMING
RACE_CLASS_MAP[csdefine.CLASS_ARCHER]				= csdefine.FENGMING
RACE_CLASS_MAP[csdefine.CLASS_MAGE]					= csdefine.FENGMING

OPRECORD_ALL_RECORDS = (
	csdefine.OPRECORD_COURSE_HELP,
	csdefine.OPRECORD_UI_TIPS,
	csdefine.OPRECORD_PIXIE_HELP,
	)														# 全部记录类型

BASE_SKILL_TYPE_SPELL_LIST				= [ csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL, csdefine.BASE_SKILL_TYPE_PHYSICS, csdefine.BASE_SKILL_TYPE_MAGIC, csdefine.BASE_SKILL_TYPE_DISPERSION, csdefine.BASE_SKILL_TYPE_ELEM ]		# 主动技能
BASE_SKILL_INITIA_SPELL_LIST			= [ csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL, csdefine.BASE_SKILL_TYPE_PHYSICS, csdefine.BASE_SKILL_TYPE_MAGIC	]		# 主动技能
BASE_SKILL_TYPE_PASSIVE_SPELL_LIST		= [ csdefine.BASE_SKILL_TYPE_PASSIVE, csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE ]	# 被动技能类型列表

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
	] )													# 程序定义的行为技能( 放到行为技能列表中 )

# 背包搜索顺序及优先级
# 搜索所有普通背包、神机匣、装备栏；装备栏必须在最后，以避免被优先删除的可能性
KB_SEARCH_ALL = range( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ) + [ csdefine.KB_CASKET_ID, csdefine.KB_EQUIP_ID ]
# 搜索所有普通背包、神机匣
KB_SEARCH_COMMON_AND_CASKET = range( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ) + [ csdefine.KB_CASKET_ID, ]
# 搜索所有普通背包
KB_SEARCH_COMMON = range( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT )
# 只搜索装备栏
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
# 频道 ID 到频道名称映射
CHAT_CHID_2_NAME = {
	csdefine.CHAT_CHANNEL_NEAR			: ST.CHAT_CHANNEL_NEAR,				# 附近
	csdefine.CHAT_CHANNEL_LOCAL			: ST.CHAT_CHANNEL_LOCAL,			# 本地
	csdefine.CHAT_CHANNEL_TEAM			: ST.CHAT_CHANNEL_TEAM,				# 队伍
	csdefine.CHAT_CHANNEL_FAMILY			: ST.CHAT_CHANNEL_FAMILY,			# 家族
	csdefine.CHAT_CHANNEL_TONG			: ST.CHAT_CHANNEL_TONG,				# 帮会
	csdefine.CHAT_CHANNEL_WHISPER		: ST.CHAT_CHANNEL_WHISPER,			# 密语
	csdefine.CHAT_CHANNEL_WORLD			: ST.CHAT_CHANNEL_WORLD,			# 世界
	csdefine.CHAT_CHANNEL_RUMOR			: ST.CHAT_CHANNEL_RUMOR,			# 谣言
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: ST.CHAT_CHANNEL_WELKIN_YELL,		# 天音
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: ST.CHAT_CHANNEL_TUNNEL_YELL,		# 地音
	csdefine.CHAT_CHANNEL_PLAYMATE		: ST.CHAT_CHANNEL_PLAYMATE,			# 玩伴
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : ST.CHAT_CHANNEL_TONG_CITY_WAR,	# 帮会战场

	# GM/公告频道
	csdefine.CHAT_CHANNEL_SYSBROADCAST	: ST.CHAT_CHANNEL_SYSBROADCAST,		# 广播

	# NPC 发言频道
	csdefine.CHAT_CHANNEL_NPC_SPEAK		: ST.CHAT_CHANNEL_NPC_SPEAK,		# NPC
	csdefine.CHAT_CHANNEL_NPC_TALK		: ST.CHAT_CHANNEL_NPC_TALK,			# NPC对话

	# 系统提示频道
	csdefine.CHAT_CHANNEL_SYSTEM			: ST.CHAT_CHANNEL_SYSTEM,			# 系统
	csdefine.CHAT_CHANNEL_COMBAT			: ST.CHAT_CHANNEL_COMBAT,			# 战斗
	csdefine.CHAT_CHANNEL_PERSONAL		: ST.CHAT_CHANNEL_PERSONAL,			# 个人
	csdefine.CHAT_CHANNEL_MESSAGE		: ST.CHAT_CHANNEL_MESSAGE,			# 消息
	csdefine.CHAT_CHANNEL_SC_HINT		: ST.CHAT_CHANNEL_SC_HINT,			# 屏幕
	csdefine.CHAT_CHANNEL_MSGBOX			: ST.CHAT_CHANNEL_MSGBOX,			# 提示
	csdefine.CHAT_CHANNEL_MSGBOX			: ST.CHAT_CHANNEL_MSGBOX,			# 提示
	csdefine.CHAT_CHANNEL_CAMP			: ST.CHAT_CHANNEL_CAMP,				# 阵营

	}

# 频道名称到频道 ID 的映射
CHAT_NAME_2_CHID = {}
for chid, name in CHAT_CHID_2_NAME.iteritems() :
	CHAT_NAME_2_CHID[name] = chid

# -------------------------------------------
# 向客户端公开的频道（角色可发言的频道）
CHAT_EXPOSED_CHANNELS = set( [
	csdefine.CHAT_CHANNEL_NEAR,						# 附近( 流程：base->cell->client )
	csdefine.CHAT_CHANNEL_LOCAL,						# 本地( 流程：目前还没实现 )
	csdefine.CHAT_CHANNEL_TEAM,						# 队伍( 流程：base->base 上的队伍系统->各成员 client )
	csdefine.CHAT_CHANNEL_FAMILY,					# 家族( 流程：base->base 上的家族系统->各成员 client )
	csdefine.CHAT_CHANNEL_TONG,						# 帮会( 流程：base->base 上的帮会系统->各成员 client )
	csdefine.CHAT_CHANNEL_WHISPER,					# 密语( 流程：base->client )
	csdefine.CHAT_CHANNEL_WORLD,						# 世界( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_RUMOR,						# 谣言( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_WELKIN_YELL,				# 天音( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TUNNEL_YELL,				# 地音( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_PLAYMATE,					# 玩伴( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_CAMP,						# 阵营( 流程：base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR			# 帮会战场频道
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

#家族招人权限表
FAMILY_GRADE_CONSCRIBE				= [ csdefine.FAMILY_GRADE_SHAIKH_SUBALTERN, csdefine.FAMILY_GRADE_SHAIKH ]
#发布公告权限表
FAMILY_GRADE_RELEASE_AFFICHE		= [ csdefine.FAMILY_GRADE_SHAIKH_SUBALTERN, csdefine.FAMILY_GRADE_SHAIKH ]
#开除成员权限表
FAMILY_GRADE_KICK_MEMBER			= [ csdefine.FAMILY_GRADE_SHAIKH_SUBALTERN, csdefine.FAMILY_GRADE_SHAIKH ]
"""
# 帮会仓库大小
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
NEED_ITEM_COUNT_DICT		= { 0:0,1:1,2:2,3:2,4:3,5:4,6:5}	# 扩充相应的仓库时需要的金丝木的数量，格式{仓库索引:数量,....}

# 单方关系列表
SINGLE_RELATION_LIST = [ csdefine.ROLE_RELATION_BLACKLIST, csdefine.ROLE_RELATION_FOE, csdefine.ROLE_RELATION_MASTER, csdefine.ROLE_RELATION_PRENTICE, csdefine.ROLE_RELATION_MASTER_EVER, csdefine.ROLE_RELATION_PRENTICE_EVER ]
# 双发关系列表
MULTI_RELATION_LIST = [ csdefine.ROLE_RELATION_FRIEND, csdefine.ROLE_RELATION_SWEETIE, csdefine.ROLE_RELATION_COUPLE, csdefine.ROLE_RELATION_ALLY ]

RCG_TONG_ROB_WARS			= {1:csdefine.RCG_TONG_ROB_WAR_1, 2:csdefine.RCG_TONG_ROB_WAR_2, 3:csdefine.RCG_TONG_ROB_WAR_3}	# 掠夺战奖励领取
RCG_TEAM_COMP_EXP			= [csdefine.RCG_TEAM_COMP_EXP_1,csdefine.RCG_TEAM_COMP_EXP_2,csdefine.RCG_TEAM_COMP_EXP_3,\
									csdefine.RCG_TEAM_COMP_EXP_4, csdefine.RCG_TEAM_COMP_EXP_5, csdefine.RCG_TEAM_COMP_EXP_6,\
									csdefine.RCG_TEAM_COMP_EXP_7, csdefine.RCG_TEAM_COMP_EXP_8, csdefine.RCG_TEAM_COMP_EXP_9,\
									csdefine.RCG_TEAM_COMP_EXP_10,]

FETE_COMPLETE_STATUS = [ csdefine.LUNARHALO, csdefine.SUNSHINE, csdefine.STARLIGHT ]
JUMP_TYPE_WATERS				= [ csdefine.JUMP_TYPE_WATER1, csdefine.JUMP_TYPE_WATER2, csdefine.JUMP_TYPE_WATER3 ]

# 英雄类别
CHALLENGE_AVATAR_TYPE = ( "chiyou", "huangdi", "houyi", "nuwo" )

CLASS_TO_COPY_DUTIES = {
	csdefine.CLASS_FIGHTER		: ( csdefine.COPY_DUTY_MT, csdefine.COPY_DUTY_DPS, ),				# 战士对应MT和DPS
	csdefine.CLASS_SWORDMAN		: ( csdefine.COPY_DUTY_DPS, ),							# 剑客对应DPS
	csdefine.CLASS_ARCHER 		: ( csdefine.COPY_DUTY_DPS, ),							# 射手对应DPS
	csdefine.CLASS_MAGE 			: ( csdefine.COPY_DUTY_HEALER, csdefine.COPY_DUTY_DPS, ),			# 法师对应治疗和DPS
}

#-------------------------------------------------------------------------------
#可以被追踪的地图
#--------------------------------------------------------------------------------
AREAS_CAN_BE_TRACE		= ["xin_ban_xin_shou_cun","fengming","xin_fei_lai_shi_001",
						 "zly_ban_quan_xiang","zly_ying_ke_cun","zly_bi_shi_jian",
						 "yun_meng_ze_01","yun_meng_ze_02","peng_lai","kun_lun",
						 "bei_ming"]


#-------------------------------------------------------------------------------
#英雄联盟副本
#--------------------------------------------------------------------------------
YXLM_ROBOT_1 = [ "20124014", "20124015", "20124016", "20124017", "20124018" ]
YXLM_ROBOT_2 = [ "20724025", "20724038", "20724039", "20724040", "20724041" ]

#--------------------------------------------------------------------------------
# 车轮战
#--------------------------------------------------------------------------------
TONG_TURN_MEMBER_NUM 		= 5		# 车轮战队伍人数
TONG_TURN_FIGHT_MEM_NUM		= 2		# 车轮战场内出战人数限制
TONG_TURN_LEVEL_MIN			= 40	# 车轮战等级下限
TONG_TURN_STEP_SIGNUP		= 1		# 报名阶段
TONG_TURN_STEP_END			= 2		# 比赛未开启（或已结束）阶段
TONG_TURN_WIN_POINT			= 1		# 车轮战获胜积分

# 有组队限制的地图
TEAM_INVIETE_FORBID_MAP = [ "fu_ben_zheng_jiu_ya_yu_new" ]

# 延迟传送相关
PLAYER_TO_NPC_DISTANCE  = 20.0      # 玩家与施法NPC距离限制

# 阵营

CAMP_KILL_REWARD_HONOUR_BASE = 100

# 阵营车轮战
CAMP_TURN_MEMBER_NUM 		= 1		# 车轮战队伍人数
CAMP_TURN_FIGHT_MEM_NUM		= 2		# 车轮战场内出战人数限制
CAMP_TURN_LEVEL_MIN			= 40	# 车轮战等级下限
CAMP_TURN_STEP_SIGNUP		= 1		# 报名阶段
CAMP_TURN_STEP_END			= 2		# 比赛未开启（或已结束）阶段
CAMP_TURN_WIN_POINT			= 1		# 车轮战获胜积分

# ------------------------------------------------------------------------------
# 道法相关数据
# ------------------------------------------------------------------------------
# 品质对应的基础经验值
DAOFA_QUALITY_EXP = { 2:10, 3:30, 4:50, 5:70,}

# 道法升级所需经验{ 等级:{ 品质:经验， 品质:经验 } }
DAOFA_UPGRADE_EXP = {
				1: { 2:50, 3:70, 4:100, 5:150, },
				2: { 2:200, 3:500, 4:600, 5:1000, },
				3: { 2:0, 3:1500,4:3000, 5:7200, },
				4: { 2:0, 3:0, 4:6000, 5:14400, },
				5: { 2:0, 3:0,4:0, 5:28800, },
				6: { 2:0, 3:0,4:0, 5:0, },
				}

# 道法出售价格 { 品质: 价格 }
DAOFA_PRICE = { 1:220, 2:280, 3:520, 4:750, 5:2500,}

# 道法最大等级 { 品质: 最大等级 }
DAOFA_MAX_LEVEL = { 2: 3, 3: 4, 4: 5, 5: 6, }

# --------------------------------------------------------------------
# 宠物普通攻击技能相关
# --------------------------------------------------------------------
SKILL_ID_PHYSICS_LIST = [csdefine.SKILL_ID_PHYSICS, csdefine.SKILL_ID_SMART_PET_PHYSICS, csdefine.SKILL_ID_INTELLECT_PET_MAGIC]

PET_SKILL_ID_PHYSICS_MAPS = {	csdefine.PET_TYPE_STRENGTH	:	csdefine.SKILL_ID_PHYSICS,
								csdefine.PET_TYPE_BALANCED	:	csdefine.SKILL_ID_PHYSICS,
								csdefine.PET_TYPE_SMART		:	csdefine.SKILL_ID_SMART_PET_PHYSICS,
								csdefine.PET_TYPE_INTELLECT	:	csdefine.SKILL_ID_INTELLECT_PET_MAGIC,
}

# 天命轮回副本
DESTINY_TRANS_COPY_COMMON	= 1		# 普通模式

DESTINY_TRANS_ROLE_INIT_LIVE_POINT		= 3 # 玩家初始复活点数



#跳舞活动经验公式为：(20.952*Lv^1.5+55.238)
#变身大赛活动连续变身成功次数对应经验奖励公式：(371.323 * (Lv^1.5) + 978.942) * (1.196^N) / 212.815
#知识问答活动1点积分兑换经验公式：(2.049*Lv^1.5+5.401)
#科举乡试活动题号对应经验公式：(419.048*Lv^1.5+1104.762)*题号^0.256/24.572
#科举会试活动题号对应经验公式：(558.730*Lv^1.5+1473.016)*题号^0.256/24.572
#科举殿试活动题号对应经验公式：(698.413*Lv^1.5+1841.270)*题号^0.231/33.155
#赛马活动名次对应经验公式：(401.587*Lv^1.5+1058.730)*名次^-1.000
#夜战凤栖镇经验公式：(1396.825*Lv^1.5+3682.540)*(0.5*名次^-1.000+0.5*积分/(积分+(积分+100)^0.5))
#环任务任务环数对应经验公式：(27.937*Lv^1.5+73.651)*(1+(小环数-1)*0.111+(大环数-1)*0.200)
#押镖任务经验公式：(670.476*Lv^1.5+1767.619)
#贵重镖任务经验公式：(838.095*Lv^1.5+2209.524)
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
# 阵营活动相关
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

CAMP_DAILY_REPEAT_LIMIT = 10						# 每天完成阵营日常任务的个数限制
CAMP_ACTIVITY_PERSIST_TIME = 8 * 60 * 60		# 阵营活动默认持续时间
CAMP_ACTIVITY_CHECK_SPELL_ID = 780047001		# 添加检测buff的技能ID
CAMP_OCCUPED_SPELL_ID = 780048001				# 据点被占领给奖励buff的技能ID

# -----------------------------------------------------------------------
# 捕鱼达人
# -----------------------------------------------------------------------
FISHING_GROUND_LENGTH = 40		# 捕鱼场长
FISHING_GROUND_WIDE = 28		# 捕鱼场宽
FISH_HIT_COOLDOWN = 0.2			# 炮弹发射基础冷却时间
FISH_FORT_RADIUS = 8			# 炮台半径

#---------------------------------------------------------------------
# 仙魔论战
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

TDB_FIRDAMAGE_LEVEL_LIMIT = 40			# 首触最低等级要求
TDB_TOP_DAMAGE_LIMIT = 50000			# 伤害榜要求最低伤害量
TDB_TOP_CURE_LIMIT = 30000				# 治疗榜要求最低治疗量
TDB_TOP_DAMAGE_ORDER_LIMIT = 20			# 伤害榜排名数
TDB_TOP_CURE_ORDER_LIMIT = 3			# 治疗榜排名数
TDB_TOP_DIE_ORDER_LIMIT = 20			# 死亡榜排名数

#悬赏任务道具ID
REWARD_QUEST_LOW_ITEM = 110103056
REWARD_QUEST_HIGH_ITEM = 110103057

#劲舞时刻技能ID
DancingKingBuffID = 22135  #舞王Buff (各种舞王都采用此buff，配置的等级不一样，经验倍率也不一样)
DancingBuffID	= 22136    #舞厅中经验Buff
DancingPunishBuffID = 22137 #挑战失败5分钟之内不能再挑战的buff
DanceingPunishSkillID = 780061  #挑战失败5分钟之内不能再挑战的buff对应的技能
DanceSkill1		= 780051001  	#玩家在挑战斗舞或练习斗舞时的空间技能，播放动作dance1
DanceSkill2		= 780052001	#玩家在挑战斗舞或练习斗舞时的空间技能，播放动作dance2
DanceSkill3		= 780053001	#玩家在挑战斗舞或练习斗舞时的空间技能，播放动作dance3
DanceSkill4		= 780054001	#玩家在挑战斗舞或练习斗舞时的空间技能，播放动作dance4
DanceSkill5		= 780055001	#玩家在挑战斗舞或练习斗舞时的空间技能，播放动作dance5
DanceExpSkill			= 780056001  	#玩家在舞厅中获得的普通经验Buff（8个小时）
DanceExpWaitingSkillID	= 780057001  	#玩家在舞厅中获得的候选经验Buff
DanceExpCOPPERSkillID	= 780058001  	#玩家在舞厅中获得的铜牌经验Buff
DanceExpSILVERSkillID	= 780059001  	#玩家在舞厅中获得的银牌经验Buff
DanceExpGLODSkillID		= 780060001  	#玩家在舞厅中获得的金牌经验Buff
SPACE_WUTING = "fu_ben_wu_tai_001"
SPACE_DANCE_CHALLENGE = "dancechellenge"
SPACE_DANCE_PRACTICE = "dancepractice"
spaceDanceSkills = [780051001,780052001,780053001,780054001,780055001]
DANCEHALLAOI	= 100

# 帮会开启各项活动消耗的资金
TONG_FETE_REQUEST_MONEY					= 10000		# 祭祀
TONG_ROBWAR_REQUEST_MONEY				= 20000		# 掠夺战
TONG_MONSTERRAID_REQUEST_MONEY			= 30000		# 魔物来袭
TONG_RACE_REQUEST_MONEY					= 40000		# 帮会赛马
TONG_OPEN_DART_QUEST_REQUEST_MONEY		= 50000		# 开启帮会运镖任务
TONG_OPEN_NORMAL_QUEST_REQUEST_MONEY	= 60000		# 开启帮会日常任务

# 帮会完成各项活动给的经验值
TONG_EXP_REWARD_FETE				= 10000		# 祭祀
TONG_EXP_REWARD_ROBWAR				= 20000		# 掠夺战
TONG_EXP_REWARD_MONSTERRAED			= 30000		# 魔物来袭
TONG_EXP_REWARD_RACE				= 40000		# 帮会赛马

#---------------------------------------------------------------------
# 绝地反击活动
#---------------------------------------------------------------------
JUE_DI_FAN_JI_WAIT_TIME = 25.0							#绝地反击活动匹配成功后等待时间
JUE_DI_FAN_JI_LEVEL_LIMIT = 50							#绝地反击活动报名等级要求

YA_YU_COPY_SPECAIL_ITEMS = [ 40401024, 40401025, 40401026 ]		# 猰貐副本特殊道具ID

# --------------------------------------------------------------------
# 异界战场副本
# --------------------------------------------------------------------
YI_JIE_ZHAN_CHANG_ENRAGE_SKILL_ID		= 123473001		#异界战场激活激怒buff技能
YI_JIE_ZHAN_CHANG_STONE_SKILL_ID		= 123474001		#异界战场激活灵石之力buff技能
YI_JIE_ZHAN_CHANG_DESERTER_SKILL_ID		= 123477001		#异界战场激活逃兵buff技能
YI_JIE_ZHAN_CHANG_MAX_RAGE_SKILL_ID		= 123478001		#异界战场激活满怒buff技能
YI_JIE_ZHAN_CHANG_UNIQUE_SKILL_ID		= 123479001		#异界战场无双技

YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID		= 62004		#异界战场激怒buff
YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID		= 199026	#异界战场逃兵buff
YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID		= 1001		#异界战场满怒buff

# --------------------------------------------------------------------
# 帮会夺城战决赛
# --------------------------------------------------------------------
g_camp_info = { 1: cschannel_msgs.CAMP_FAIRY,
				2: cschannel_msgs.CAMP_DEVIL, }

CITY_WAR_BATTLE_BASE_ACTIVATE_LIMIT = 50

CITY_WAR_RESOURCE_BASE_SKILL = { csdefine.CITY_WAR_FINAL_FACTION_ATTACK: 1,
								 csdefine.CITY_WAR_FINAL_FACTION_DEFEND: 1,
								 }

# --------------------------------------------------------------------
# 帮会烽火连天以及阵营烽火连天共用
# --------------------------------------------------------------------
g_road_info = { "left": cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_UPPER_ROAD,
				 "mid": cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_CENTER_ROAD,
				 "right": cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_LOWER_ROAD,}


#角色模型缩放表
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
# 纯客户端entity类型
# --------------------------------------------------------------------
CLIENT_ENTITY_TYPE = [ "CustomPatrolGraph", "Creature", "Flock", "EnvironmentObject", "SpecialHideEntity", "SoundEntity", "CameraFly", "CameraModel", ]

#静态副本关系实例
RELATION_TYPE_STATIC_SPACE = [ csdefine.RELATION_STATIC_CAMP_FENG_HUO,
								csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY,
								csdefine.RELATION_STATIC_TONG_CITY_WAR,
								csdefine.RELATION_STATIC_YXLM,
								csdefine.RELATION_STATIC_YI_JIE_ZHAN_CHANG,
								csdefine.RELATION_STATIC_TONG_CITY_WAR_FINAL,
								]

#副本与静态关系实例的对应关系
SPACE_MAPPING_RELATION_TYPE_DICT = { csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN : csdefine.RELATION_STATIC_CAMP_FENG_HUO,
									 csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN : csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY,
									 csdefine.SPACE_TYPE_CITY_WAR : csdefine.RELATION_STATIC_TONG_CITY_WAR,
									 csdefine.SPACE_TYPE_CITY_WAR_FINAL : csdefine.RELATION_STATIC_TONG_CITY_WAR_FINAL,
									 csdefine.SPACE_TYPE_YXLM : csdefine.RELATION_STATIC_YXLM,
									 csdefine.SPACE_TYPE_YXLM_PVP : csdefine.RELATION_STATIC_YXLM,
									 csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG : csdefine.RELATION_STATIC_YI_JIE_ZHAN_CHANG,
									 csdefine.SPACE_TYPE_TONG_TERRITORY : csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY,
									}
