# -*- coding: gb18030 -*-

# $Id: ItemTypeEnum.py,v 1.61 2008-08-30 02:41:24 yangkai Exp $

"""
道具类型和装备位置常量定义
	- CEL_*：装备位置，装备专用；
	- CEM_*：可装备职业，表示可以在哪些职业上装备，职业类型可以组合；
	- CKT_*：背包类型；
	- CFE_*：道具的其它标志；

"""

import Language
import cschannel_msgs
import ShareTexts as ST
# 物品分类( Item Sub Type )
ITEM_UNKOWN							= 0x000000	# 未知
ITEM_WEAPON							= 0x010000	# 武器道具
ITEM_ARMOR							= 0x020000	# 防具道具
ITEM_ORNAMENT						= 0x030000	# 首饰道具
ITEM_PROPERTY						= 0x040000	# 属性道具
ITEM_VOUCHER						= 0x050000	# 凭证道具
ITEM_SYSTEM							= 0x060000	# 系统道具
ITEM_WAREHOUSE						= 0x070000	# 仓库道具
ITEM_PRODUCE						= 0x080000	# 生产道具
ITEM_NPC							= 0x090000	# NPC道具
ITEM_NORMAL							= 0x100000	# 普通道具
ITEM_MONEY							= 0xff0000	# 金钱

ITEM_WEAPON_AXE1					= 0x010101	# 单手斧
ITEM_WEAPON_SWORD1					= 0x010102	# 单手剑
ITEM_WEAPON_HAMMER1					= 0x010103	# 单手锤
ITEM_WEAPON_SPEAR1					= 0x010104	# 单手矛
ITEM_WEAPON_DAGGER					= 0x010105	# 匕首

ITEM_WEAPON_AXE2					= 0x010201	# 双手斧
ITEM_WEAPON_SWORD2					= 0x010202	# 双手剑
ITEM_WEAPON_HAMMER2					= 0x010203	# 双手锤
ITEM_WEAPON_SPEAR2					= 0x010204	# 双手矛
ITEM_WEAPON_TWOSWORD				= 0x010205	# 双持剑

ITEM_WEAPON_LONGBOW					= 0x010301	# 长弓
ITEM_WEAPON_SHORTBOW				= 0x010302	# 短弓

ITEM_WEAPON_STAFF					= 0x010401	# 法杖


ITEM_WEAPON_TRUMP					= 0x010502	# 法器

ITEM_ARMOR_HEAD						= 0x020100	# 帽子
ITEM_ARMOR_BODY						= 0x020200	# 衣服
ITEM_ARMOR_HAUNCH					= 0x020300	# 腰带
ITEM_ARMOR_CUFF						= 0x020400	# 护腕
ITEM_ARMOR_VOLA						= 0x020500	# 手套
ITEM_ARMOR_BREECH					= 0x020600	# 裤子
ITEM_ARMOR_FEET						= 0x020700	# 鞋子
ITEM_WEAPON_SHIELD					= 0x020800	# 盾牌

ITEM_ORNAMENT_NECKLACE				= 0x030101	# 项链
ITEM_ORNAMENT_RING					= 0x030201	# 戒指
ITEM_ORNAMENT_ACMENT				= 0x030301	# 饰品

ITEM_PROPERTY_MEDICINE				= 0x040101	# 药水
ITEM_PROPERTY_FOOD					= 0x040102	# 食物
ITEM_PROPERTY_DRUG					= 0x040103	# 丹药
ITEM_PROPERTY_CHARM					= 0x040201	# 符咒
ITEM_PROPERTY_COUP					= 0x040202	# 锦囊

ITEM_VOUCHER_ITEM					= 0x050101	# 凭证道具
ITEM_VOUCHER_QUEST					= 0x050201	# 任务凭证

ITEM_SYSTEM_FUNC					= 0x060101	# 系统功能道具
ITEM_SYSTEM_KASTONE					= 0x060201	# 魂魄石
ITEM_SYSTEM_TALISMAN				= 0x060301	# 法宝
ITEM_SYSTEM_VEHICLE					= 0x060501	# 骑宠
ITEM_SYSTEM_VEHICLE_SADDLE			= 0x060502	# 骑宠装备马鞍
ITEM_SYSTEM_VEHICLE_HALTER			= 0x060503	# 骑宠装备笼头
ITEM_SYSTEM_VEHICLE_NECKLACE		= 0x060504	# 骑宠装备项链
ITEM_SYSTEM_VEHICLE_CLAW			= 0x060505	# 骑宠装备爪环
ITEM_SYSTEM_VEHICLE_MANTLE			= 0x060506	# 骑宠装备披风
ITEM_SYSTEM_VEHICLE_BREASTPLATE		= 0x060507	# 骑宠装备护甲

### 飞行骑宠装备 开始 ###
ITEM_SYSTEM_FLYING_VEHICLE_SADDLE	= 0x060508	# 飞行骑宠装备马鞍
ITEM_SYSTEM_FLYING_VEHICLE_HALTER	= 0x060509	# 飞行骑宠装备笼头
ITEM_SYSTEM_FLYING_VEHICLE_NECKLACE	= 0x060510	# 飞行骑宠装备项链
ITEM_SYSTEM_FLYING_VEHICLE_CLAW		= 0x06051A	# 飞行骑宠装备爪环
ITEM_SYSTEM_FLYING_VEHICLE_MANTLE	= 0x06051B	# 飞行骑宠装备披风
ITEM_SYSTEM_FLYING_VEHICLE_BREASTPLATE	= 0x06051C	# 飞行骑宠装备护甲
### 飞行骑宠装备 结束 ###

ITEM_SYSTEM_GODSTONE				= 0x060601	# 天罡石

ITEM_WAREHOUSE_KITBAG				= 0x070101	# 背包
ITEM_WAREHOUSE_EQUIP				= 0x070201	# 装备栏
ITEM_WAREHOUSE_CASKET				= 0x070301	# 异宝

ITEM_PRODUCE_STUFF					= 0x080101	# 制造材料
ITEM_QUEST_STUFF					= 0x080201	# 任务材料
ITEM_PRODUCE_JEWELRY				= 0x080301	# 宝石
ITEM_EQUIPMAKE_SCROLL				= 0x080401	# 制作卷
ITEM_STILETTO  						= 0x080501	# 孔针

ITEM_NORMAL_SUNDRIES				= 0x100101	# 杂物
ITEM_SUPER_DRUG_HP					= 0x110102	# 玩家超级补药
ITEM_PET_BOOK						= 0x110103	# 宠物技能书

ITEM_DRUG_ROLE_HP					= 0x110104	# 角色普通补血药 1114372
ITEM_DRUG_ROLE_MP					= 0x110105	# 角色普通补蓝药 1114373
ITEM_DRUG_PET_HP					= 0x110106	# 宠物普通补血药 1114374
ITEM_DRUG_PET_MP					= 0x110107	# 宠物普通补蓝药 1114375
ITEM_YAO_DING						= 0x110108	# 灵药鼎		 1114376

ITEM_YIN_PIAO						= 0x110109	# 元宝票		 1114377
ITEM_PET_SUPER_DRUG_HP				= 0x11010a	# 宠物超级补血药		 1114378
ITEM_PET_SUPER_DRUG_MP				= 0x11010b	# 宠物超级补蓝药		 1114379
ITEM_SUPER_DRUG_MP					= 0x11010c	# 玩家超级补药		 1114380
ITEM_PET_PROPERTY_CHARM				= 0x11010d  # 宠物符咒   1114381
ITEM_PET_ITEM						= 0x11010e  # 宠物道具   1114382
ITEM_ANIMAL_TRAPS					= 0x11010f	# 捕兽器     1114383
ITEM_PET_EGG						= 0x110114	# 宠物蛋     1114388

ITEM_FASHION1						= 0x110110	# 时装1
ITEM_FASHION2						= 0x110111	# 时装2
ITEM_TREASUREMAP					= 0x110112	# 藏宝图
ITEM_POTENTIAL_BOOK				= 0x110113	# 潜能书

ITEM_EXPERIMENT_PINHOLE				= 0x4c63ebd # 实验针孔 80101053
ITEM_GREENCRYSTAL					= 0x4c63eac # 绿水晶 80101036

ITEM_VEHICLE_BOOK					= 0x4c63ead	# 骑宠技能书 80101037

ITEM_NATURE_JADE					= 0x4c63eae	# 造化玉牒
ITEM_VEHICLE_FD					        = 0x4c63eaf	# 喂食道具 80101039
ITEM_VEHICLE_TURN					= 0x4c63eb0	#骑宠变回物品80101040

# -------------------------------------------------
# 物品装备栏位置定义
# -------------------------------------------------
# Equit location(UINT8)；装备栏的各部位
CEL_HEAD					= 0		# 头
CEL_NECK					= 1		# 颈
CEL_BODY					= 2		# 身体
CEL_BREECH					= 3		# 腿部
CEL_VOLA					= 4		# 手掌
CEL_HAUNCH					= 5		# 腰部
CEL_CUFF					= 6		# 腕部
CEL_LEFTHAND				= 7		# 左手
CEL_RIGHTHAND				= 8		# 右手
CEL_FEET					= 9		# 脚
CEL_LEFTFINGER				= 10	# 左手指
CEL_RIGHTFINGER				= 11	# 右手指
CEL_CIMELIA					= 12	# 魂魄石
CEL_TALISMAN				= 13	# 法宝
CEL_FASHION1                = 14	# 时装1
CEL_POTENTIAL_BOOK                = 15	# 潜能天书

CEL_MAX						= 16	# 表示“CEL_*”的值总数量
# wield Type(UINT8)；装备的装备类型，它与装备栏的位置(CEL_*)有映射关系
CWT_HEAD					= 0		# 头     —— 头盔
CWT_NECK					= 1		# 颈     —— 项链
CWT_BODY					= 2		# 身体   —— 身甲
CWT_BREECH					= 3		# 臀部   —— 裤子
CWT_VOLA					= 4		# 手     —— 手套
CWT_HAUNCH					= 5		# 腰     —— 腰带
CWT_CUFF					= 6		# 腕     —— 护腕
CWT_LEFTHAND				= 7		# 左手   —— 盾牌
CWT_RIGHTHAND				= 8		# 右手   —— 武器
CWT_FEET					= 9		# 脚     —— 鞋子
CWT_LEFTFINGER				= 10	# 左手指 —— 戒指
CWT_RIGHTFINGER				= 11	# 右手指 —— 戒指
CWT_CIMELIA					= 12	# 魂魄石
CWT_TALISMAN				= 13	# 法宝
CWT_TWOHAND					= 14	# 需要双手一起握的武器
CWT_HANDS					= 15	# 左手或右手可以随意装备(只选其一)
CWT_TWOFINGER				= 16	# 需要两个手指一起装备
CWT_FINGERS					= 17	# 左手指或右手指可以随意装备
CWT_RIGHTORTWO				= 18	# 右手或双手握(左手没物品的时候是右手,左手有物品的时候是右手)
CWT_FASHION1                = 19	# 时装1
CWT_FASHION2                = 20	# 时装2

# -----------------------------------------------------
# 角色身体部位与相应装备的映射集合
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
# 武器集合定义
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
# 防具集合定义
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
# 套装防具集定义
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
# 背包集合定义
# -------------------------------------------------
KITBAG_LIST = [
		ITEM_WAREHOUSE_KITBAG,		# 包裹
		ITEM_WAREHOUSE_CASKET,		# 神机匣
		]

# -------------------------------------------------
# 首饰集合定义
# -------------------------------------------------
ORNAMENT_LIST = [
		ITEM_ORNAMENT_NECKLACE,		# 项链
		ITEM_ORNAMENT_RING,			# 戒指
		ITEM_ORNAMENT_ACMENT,		# 饰品
		]

# -------------------------------------------------
# 其他可装备物品
# -------------------------------------------------
OTHEREQUIPITEM_LIST = [
		ITEM_SYSTEM_KASTONE,				# 魂魄石
		ITEM_SYSTEM_TALISMAN,				# 法宝
		ITEM_FASHION1,						# 时装1
		ITEM_FASHION2,						# 时装2
		ITEM_POTENTIAL_BOOK,				# 潜能书
	]
# -------------------------------------------------
# 装备集合定义
# -------------------------------------------------
EQUIP_TYPE_SET = set( list( WEAPON_LIST ) + ARMOR_LIST + ORNAMENT_LIST + OTHEREQUIPITEM_LIST )

# -------------------------------------------------
# 骑宠装备集合定义
# -------------------------------------------------
VEHICLE_EQUIP_LIST = [
		ITEM_SYSTEM_VEHICLE_SADDLE	,		# 骑宠装备马鞍
		ITEM_SYSTEM_VEHICLE_HALTER	,		# 骑宠装备笼头
		ITEM_SYSTEM_VEHICLE_NECKLACE,		# 骑宠装备项链
		ITEM_SYSTEM_VEHICLE_CLAW,			# 骑宠装备爪环
		ITEM_SYSTEM_VEHICLE_MANTLE,			# 骑宠装备披风
		ITEM_SYSTEM_VEHICLE_BREASTPLATE,	# 骑宠装备护甲
	]

# -------------------------------------------------
# 飞行骑宠装备集合定义
# -------------------------------------------------
FLYING_VEHICLE_EQUIP_LIST = [
		ITEM_SYSTEM_FLYING_VEHICLE_SADDLE,		# 飞行骑宠装备马鞍
		ITEM_SYSTEM_FLYING_VEHICLE_HALTER,		# 飞行骑宠装备笼头
		ITEM_SYSTEM_FLYING_VEHICLE_NECKLACE,	# 飞行骑宠装备项链
		ITEM_SYSTEM_FLYING_VEHICLE_CLAW,		# 飞行骑宠装备爪环
		ITEM_SYSTEM_FLYING_VEHICLE_MANTLE,		# 飞行骑宠装备披风
		ITEM_SYSTEM_FLYING_VEHICLE_BREASTPLATE,	# 飞行骑宠装备护甲
	]

# -------------------------------------------------
# 玩家恢复品集合定义
# -------------------------------------------------
ROLE_DRUG_LIST = [
		ITEM_DRUG_ROLE_HP, 			# 玩家普通补血药
		ITEM_DRUG_ROLE_MP,			# 玩家普通补蓝药
		ITEM_SUPER_DRUG_HP, 		# 玩家超级补血药
		ITEM_SUPER_DRUG_MP,			# 玩家超级补蓝药
		ITEM_PROPERTY_MEDICINE,		# 药水
	]

# -------------------------------------------------
# 宠物消耗品集合定义
# -------------------------------------------------
PET_DRUG_LIST = [
        ITEM_DRUG_PET_HP, 			# 宠物普通补血药
        ITEM_DRUG_PET_MP,			# 宠物普通补蓝药
        ITEM_PET_PROPERTY_CHARM, 	# 宠物符咒
        ITEM_PET_SUPER_DRUG_HP,		# 宠物超级补血药
        ITEM_PET_SUPER_DRUG_MP,     # 宠物超级补蓝药
	]

# -------------------------------------------------
# 物品存活时间类型定义
# -------------------------------------------------
CLTT_NONE					= 0		# 不计时
CLTT_ON_GET					= 1		# 获取后计时,时间到消失
CLTT_ON_WIELD				= 2		# 装备后计时,时间到消失
CLTT_ON_OFFLINE				= 3		# 下线后计时,时间到消失
CLTT_ON_GET_EVER			= 4		# 获取后计时,时间到不消失
CLTT_ON_WIELD_EVER			= 5		# 装备后计时,时间到不消失
CLTT_ON_OFFLINE_EVER		= 6		# 下线后计时,时间到不消失

# -------------------------------------------------
# 物品标志定义
# -------------------------------------------------
# 道具其它标志(UINT16)，使用位来表示，
# 当某位为1时表示与之对应的功能为True，反之则False
# CFE == const flag enum
CFE_NONE					= 0		#
CFE_NO_DESTROY				= 1		# 不可销毁
CFE_NO_SELL					= 2		# 不可出售( 是否能卖给NPC )
CFE_NO_REPAIR				= 3		# 不可修理( 装备专用,强制性的不允许修复 )
CFE_NO_WAREHOUSE			= 4		# 不可存储( 不允许放入仓库 )
CFE_NO_INTENSIFY			= 5		# 不可强化
CFE_NO_REBUILD				= 6		# 不可改造
CFE_NO_STILETTO				= 7		# 不可打孔
CFE_NO_ABRASION				= 8		# 不可磨损
CFE_NO_PICKUP				= 9		# 不可拾取

CFE_NO_WASTAGE				= 11	# 不可消耗(使用后是否消耗)
CFE_NO_TRADE				= 12	# 不可交易
CFE_DIE_DROP				= 13	# 死亡掉落
CFE_FLYING_ONLY				= 14	# 仅供飞行骑宠使用


# -------------------------------------------------
# 物品前缀定义
# -------------------------------------------------
CPT_NONE					= 0		# 无前缀
CPT_NORMAL					= 1		# 普通的
CPT_APPLIED					= 2		# 实用的
CPT_INTENSIFY				= 3		# 强化的
CPT_EXCELLENT				= 4		# 精良的
CPT_COSTFULL				= 5		# 珍贵的
CPT_FABULOUS				= 6		# 传说的
CPT_MYTHIC					= 7		# 神话的
CPT_MYGOD					= 8		# 逆天的

# 蓝、金、粉装可能出现的前缀
CPT_NO_GREEN = [ CPT_NORMAL, CPT_INTENSIFY, CPT_COSTFULL ]
# 绿装可能出现的前缀
CPT_GREEN = [ CPT_FABULOUS, CPT_MYTHIC, CPT_MYGOD ]
# 所有可能出现的前缀
CPT_ALL = [ CPT_NORMAL, CPT_INTENSIFY, CPT_COSTFULL, CPT_FABULOUS, CPT_MYTHIC, CPT_MYGOD ]

# -------------------------------------------------
# 物品品质定义
# -------------------------------------------------
CQT_WHITE					= 1		# 白色
CQT_BLUE					= 2		# 蓝色
CQT_GOLD					= 3		# 金色
CQT_PINK					= 4		# 粉色
CQT_GREEN					= 5		# 绿色

# -------------------------------------------------
# 物品绑定类型定义
# -------------------------------------------------
CBT_NONE					= 0		# 未绑定
CBT_PICKUP					= 1		# 拾取后绑定
CBT_EQUIP					= 2		# 装备后绑定
CBT_HAND					= 3		# 手动绑定
CBT_QUEST 					= 4		# 任务绑定
CBT_COUNT 					= 5		# 绑定类型总数

# -------------------------------------------------
# 物品认主类型定义 by jiangyi
# -------------------------------------------------
COB_NONE					= 0		# 未认主
COB_OBEY					= 1		# 已认主

# -------------------------------------------------
# 骑宠装备栏位置定义
# -------------------------------------------------
VEHICLE_CEL_HALTER			= 0		# 笼头
VEHICLE_CEL_SADDLE			= 1		# 马鞍
VEHICLE_CEL_NECKLACE		= 2		# 项链
VEHICLE_CEL_CLAW			= 3		# 爪环
VEHICLE_CEL_MANTLE			= 4		# 披风
VEHICLE_CEL_BREASTPLATE		= 5		# 护甲

# -------------------------------------------------
# 骑宠装备类型定义
# -------------------------------------------------
VEHICLE_CWT_HALTER			= 0		# 笼头
VEHICLE_CWT_SADDLE			= 1		# 马鞍
VEHICLE_CWT_NECKLACE		= 2		# 项链
VEHICLE_CWT_CLAW			= 3		# 爪环
VEHICLE_CWT_MANTLE			= 4		# 披风
VEHICLE_CWT_BREASTPLATE		= 5		# 护甲

# -------------------------------------------------
# 法宝品级定义
# -------------------------------------------------
TALISMAN_COMMON				= 0		# 凡品
TALISMAN_IMMORTAL			= 1		# 仙品
TALISMAN_DEITY				= 2		# 神品

# -------------------------------------------------
# 物品获取方式定义
# -------------------------------------------------
ITEM_GET_GM					= 0		# 默认
ITEM_GET_PICK				= 1		# 怪物掉落
ITEM_GET_CARD				= 2		# 开锦囊
ITEM_GET_NPCTRADE			= 3		# NPC交易
ITEM_GET_SHOP				= 4		# 商城
ITEM_GET_PTRADE				= 5		# 玩家之间交易
ITEM_GET_QUEST				= 6		# 任务奖励
ITEM_GET_STROE				= 7		# 开宝箱
ITEM_GET_NPCGIVE			= 8		# NPC活动给予
ITEM_GET_EQUIP_INSTENSIFY	= 9		# 装备强化到一定等级
ITEM_GET_STUD				= 10	# 镶嵌一定等级水晶

# -------------------------------------------------
# 骑宠幼宠类
# -------------------------------------------------
ITEM_CHILD_VEHICLE			= [ 60501047, 60501046, 60501045 ]

#---------------------------------------------------------------------
# 物品拾取类型 by 姜毅
#---------------------------------------------------------------------
PICK_UP_TYPE_DEFAULT = 10000						# 默认拾取类：其它
PICK_UP_TYPE_QUALITY_AREA = xrange( 20000, 29999 )		# 需要物品品质的类型区间

# -------------------------------------------------
# 装备属性类别定义
# -------------------------------------------------
EQUIP_EFFECT_TYPE_ADD		= 1		# 加值
EQUIP_EFFECT_TYPE_PER		= 2		# 加成


# -------------------------------------------------
# 装备属性类型定义
# -------------------------------------------------
EQUIP_NORMAL_ATTR = 1 #一般属性
EQUIP_MIDDLE_ATTR = 2 #精良属性
EQUIP_TOP_ATTR    = 3 #高级属性


# -------------------------------------------------
# 装备品质决定属性条目数量
# -------------------------------------------------
EQUIP_ATTR_NUM_MAPS = { CQT_WHITE : 0,
			CQT_BLUE  : 2,		
			CQT_GOLD  : 3,		# 金色
			CQT_PINK  : 4,		# 粉色
			CQT_GREEN : 5		# 绿色
			}

#需要放大配置的属性编码
EQUIP_ATTR_MAGNIFY_RATE = {30014:1000.0,30015:1000.0,30016:1000.0,30017:1000.0,}

# -------------------------------------------------
# 玩家和宠物补血药品集合
# -------------------------------------------------
ROLE_DRUG_HP_LIST = [
        ITEM_SUPER_DRUG_HP, 		# 玩家超级补血药
        ITEM_DRUG_ROLE_HP,			# 玩家普通补血药
        ITEM_PROPERTY_MEDICINE, 	# 药水
        ITEM_PROPERTY_FOOD,			# 食物
        ITEM_PET_SUPER_DRUG_HP,		# 宠物超级补血药
        ITEM_DRUG_PET_HP,			# 宠物普通补血药
	]
