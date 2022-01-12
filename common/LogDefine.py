# -*- coding: gb18030 -*-
import csdefine

LOG_TYPE_QUEST		= 1		# 任务
LOG_TYPE_ACT_COPY 	= 2		# 活动&副本
LOG_TYPE_SKILL	 	= 3		# 技能
LOG_TYPE_ORG		= 4		# 组织（包括帮会，婚姻，结拜等）
LOG_TYPE_FUNC		= 5		# 系统功能
LOG_TYPE_COUNT		= 6 	# 统计
LOG_TYPE_PRO		= 7		# 属性

LOG_TYPE_ITEM		= 8 	# 物品
LOG_TYPE_MONEY		= 9 	# 金钱
LOG_TYPE_SILVER		= 10	# 银元宝
LOG_TYPE_GOLD		= 11	# 金元宝

LOG_TYPE_EXCEPT		= 12	# 异常
LOG_TYPE_GM			= 13	# GM工具操作

# --------------------------
# 任务2级分类
# --------------------------
LT_QUEST_ACCEPT					= 1		#接受任务
LT_QUEST_COMPLETE				= 2		#完成任务
LT_QUEST_ABANDON				= 3		#放弃任务

# --------------------------
# 活动&副本2级分类
# --------------------------
LT_AC_START						= 1		#活动开始
LT_AC_STOP						= 2		#活动结束
LT_AC_KILL_MONSTER				= 3		#击杀活动怪物
LT_AC_JOIN						= 4		#活动参与
LT_AC_RESULT					= 5		#活动结果
LT_AC_ANSWER					= 6		#活动答题
LT_AT_DISTRIBUTION				= 7		#活动分配
LT_AT_COPY_OPEN					= 8		#副本开启

# --------------------------
# 技能2级分类
# --------------------------
LT_SKILL_LEARN					= 1 	#学习技能
LT_SKILL_UPGRADE				= 2		#升级技能
LT_SKILL_REMOVE					= 3		#遗忘技能（当前只有生活技能）

LT_SKILL_PG_LEARN				= 4		#学习盘古技能
LT_SKILL_PG_UPGRADE				= 5		#升级盘古技能

LT_SKILL_TONG_LEARN				= 6		#学习帮会技能
LT_SKILL_TONG_UPGRADE			= 7		#升级帮会技能

LT_SKILL_PET_LEARN				= 8 	#宠物学习技能
LT_SKILL_PET_UPGRADE			= 9		#宠物升级技能

LT_SKILL_VEHICLE_LEARN			= 10	#骑宠学习技能
LT_SKILL_VEHICLE_UPGRADE		= 11	#骑宠升级技能

# --------------------------
# 组织2级分类
# --------------------------
# 关于帮会
LT_ORG_TONG						= 0		# 帮会
LT_ORG_TONG_CREATE 				= 1		#帮会创建
LT_ORG_TONG_DISMISS				= 2		#帮会解散
LT_ORG_TONG_MONEY_CHANGE		= 3		#帮会金钱变化
LT_ORG_TONG_BUILDING_CHANGE 	= 4		#帮会建筑度变量
LT_ORG_TONG_ITEMBAGS_ADD		= 5		#帮会仓库存物品
LT_ORG_TONG_ITEMBAGS_REMOVE		= 6		#帮会仓库取物品
LT_ORG_TONG_UPLEVEL				= 7		#帮会升级
LT_ORG_TONG_DEMOTION			= 8		#帮会降级
LT_ORG_TONG_PRESTIGE_CHANGE		= 9		#帮会声望改变
LT_ORG_TONG_MEMBER_ADD			= 10	#帮会加入成员
LT_ORG_TONG_MEMBER_REMOVE		= 11	#帮会删除成员
LT_ORG_TONG_LEADER_CHANGE		= 12	#帮主改变
LT_ORG_TONG_SET_GRADE			= 13	#帮会成员权限设置
LT_ORG_TONG_WAGE				= 14	#帮会工资
LT_ORG_TONG_CITY_WAR_SET_MASTER	= 15	#设置城主
LT_ORG_TONG_CITY_G_REVENUE		= 16	#城主领取税收
LT_ORG_TONG_CITY_R_REVENUE		= 17	#收取税收
LT_ORG_TONG_EXP_CHANGE			= 18	#帮会经验变化

# 婚姻
LT_ORG_MARRY_SWEETIE			= 100	#婚姻
LT_ORG_MARRY_SWEETIE_BUILD		= 101	#恋人关系建立
LT_ORG_MARRY_SWEETIE_REMOVE		= 102	#恋人关系解除
LT_ORG_MARRY_COUPLE_BUILD		= 103	#夫妻关系建立
LT_ORG_MARRY_COUPLE_REMOVE		= 104	#夫妻关系解除

# 师徒
LT_ORG_TEACH					= 200	#师徒
LT_ORG_TEACH_BUILD				= 201	#建立师徒关系
LT_ORG_TEACH_REMOVE				= 202	#解除师徒关系
LT_ORG_TEACH_COMPLETE			= 203	#出师

# 结拜
LT_ORG_ALLY						= 300	#结拜
LT_ORG_ALLY_CHANGE				= 301	#结拜列表改改

# --------------------------
# 功能2级分类
# --------------------------
# GM操作
LT_FUNC_GM						= 0		#GM操作
LT_FUNC_GM_COMMAND				= 1		#使用GM指令

# 邮件系统
LT_FUNC_MAIL					= 100	#邮件系统
LT_FUNC_MAIL_SEND				= 101	#发送邮件
LT_FUNC_MAIL_READ				= 102	#阅读邮件
LT_FUNC_MAIL_RETURN				= 103	#主动退信
LT_FUNC_MAIL_REMOVE				= 104	#删除邮件
LT_FUNC_MAIL_SYS_RETURN			= 105	#系统退信
LT_FUNC_MAIL_UP_TIME			= 106	#更新邮件时间

# 账号
LT_FUNC_ACCOUNT					= 200	#账号
LT_FUNC_ACCOUNT_REGISTER		= 201	#账号注册
LT_FUNC_ACCOUNT_LOGON			= 202	#账号登陆
LT_FUNC_ACCOUNT_LOGOUT			= 203	#账号下线

# 角色
LT_FUNC_ROLE					= 300	#角色
LT_FUNC_ROLE_LOGON				= 301	#角色上线
LT_FUNC_ROLE_LOGOUT				= 302	#角色返回角色选择
LT_FUNC_ROLE_UPGRADE			= 303	#角色升级
LT_FUNC_ROLE_START_TRAININGS	= 304	#角色经验代练
LT_FUNC_ROLE_BEKILL				= 305	#角色被击杀
LT_FUNC_ROLE_ONLINE				= 306	#角色创建完成
LT_FUNC_ROLE_ADD				= 307	#角色添加
LT_FUNC_ROLE_DELETE				= 308	#角色删除 
LT_FUNC_ROLE_LOGOFF				= 309	#角色返回账号登陆
LT_FUNC_ROLE_SEND_RUMOR			= 310	#角色发谣言


# 摆摊
LT_FUNC_VEND					= 400	#玩家摆摊

# 装备
LT_FUNC_EQUIP					= 500	#装备
LT_FUNC_EQUIP_STILETTO			= 501	#装备打孔
LT_FUNC_EQUIP_INTENSIFY			= 502	#装备强化
LT_FUNC_EQUIP_REBUILD			= 503	#装备改造
LT_FUNC_EQUIP_BIND				= 504	#装备认主
LT_FUNC_EQUIP_SPECIAL_COMPOSE	= 505	#装备特殊合成
LT_FUNC_EQUIP_IMPROVE_QUALITY	= 506	#绿装升品
LT_FUNC_EQUIP_REFINE_GODWEAPON	= 507	#炼制神器
LT_FUNC_EQUIP_STUFF_COMPOSE		= 508	#材料合成
LT_FUNC_EQUIP_SPLIT				= 509	#装备分拆
LT_FUNC_EQUIP_STUDDED			= 510	#装备镶嵌
LT_FUNC_EQUIP_CHANGE_PROPERTY	= 511	#绿装洗前缀
LT_FUNC_EQUIP_MAKE				= 512	#装备制造
LT_FUNC_EQUIP_REPAIR_NORMAL		= 513	#装备普通修理

# 水晶
LT_FUNC_CRYSTAL					= 600	#水晶
LT_FUNC_CRYSTAL_REMOVE			= 601	#水晶摘除

# 法宝
LT_FUNC_TALISMAN				= 700	#法宝
LT_FUNC_TALISMAN_ADD_LIFE		= 701	#法宝充值
LT_FUNC_TALISMAN_SPLIT			= 702	#法宝分解
LT_FUNC_TALISMAN_INTENSIFY		= 703	#法宝强化

#宠物
LT_FUNC_PET						= 800	#宠物
LT_FUNC_PET_ADD					= 801	#获得宠物
LT_FUNC_PET_DEL					= 802	#失去宠物
LT_FUNC_PET_BREED				= 803 	#宠物繁值
LT_FUNC_PET_START_TRAININGS		= 804	#宠物经验代练

#交易
LT_FUNC_TRADE					= 900	#交易
LT_FUNC_TRADE_NPC_BUY			= 901	#从NPC处买东西
LT_FUNC_TRADE_NPC_SELL			= 902	#把东西卖给NPC
LT_FUNC_TRADE_SWAP_MONEY		= 903	#玩家交易金钱
LT_FUNC_TRADE_SWAP_ITEM			= 904	#玩家交易物品
LT_FUNC_TRADE_SWAP_PET			= 905	#玩家交易宠物

#替身寄售
LT_FUNC_TI_SHOU					= 1000	#替身寄售
LT_FUNC_TI_SHOU_BUY_PET			= 1001	#从替身上购买宠物
LT_FUNC_TI_SHOU_BUY_ITEM		= 1002	#从替身上购买物品

#采集
LT_FUNC_COLLECT					= 1100	#采集

#点卡
LT_FUNC_PC						= 1200	#点卡
LT_FUNC_PC_RECHARGE				= 1201	#点卡充值

#反外挂
LT_FUNC_AP						= 1300	#反外挂
LT_FUNC_AP_KICK_ROLE			= 1301	#反外挂踢玩家下线

#宠物仓库
LT_FUNC_PET_STORAGE				= 1400	#宠物仓库
LT_FUNC_PET_STORAGE_ADD			= 1401	#往宠物仓库存宠物
LT_FUNC_PET_STORAGE_TAKE		= 1402	#从宠物仓库取宠物

#道具商城
LT_FUNC_SPECIAL_STOP			= 1500	#道具商城
LT_FUNC_SPECIAL_STOP_BUY		= 1501	#从商城买道具

#仓库
LT_FUNC_BANK					= 1600	#仓库
LT_FUNC_BANK_STORE				= 1601	#存物品
LT_FUNC_BANK_TAKE				= 1602	#取物品
LT_FUNC_BANK_DES				= 1603	#销毁物品
LT_FUNC_BANK_EXTEND				= 1604	#拓充仓库

#订单领取
LT_FUNC_PRESENT					= 1700	#订单
LT_FUNC_PRESENT_PACKAGE			= 1701	#奖品包
LT_FUNC_PRESENT_SILVER			= 1702	#银元宝奖励
LT_FUNC_PRESENT_CHARGE			= 1703	#充值领取

# 统计
LT_COUNT_ROLE_WEALTH			= 1		#角色金钱统计
LT_COUNT_ROLE_LEVEL				= 2		#角色等级&职业统计
LT_COUNT_ROLE_COUNT				= 3		#当前在线角色
LT_COUNT_TONG_INFO				= 4		#帮会信息统计
LT_COUNT_TONG_COUNT				= 5		#帮会个数统计
LT_COUNT_ONLINE_ACCOUNT			= 6		#在线账号数

# --------------------------
# 属性相关2级分类
# --------------------------
LT_PRO_EXP_CHANGE				= 1		#经验改变
LT_PRO_POTENTIAL_CHANGE			= 2		#潜能改变

# 道行
LT_PRO_DAOHENG					= 100	#道行
LT_PRO_DAOHENG_ADD				= 101	#角色道行属性增长
LT_PRO_DAOHENG_SET				= 102	#设置角色道行属性

#积分
LT_PRO_SCORE_HONOR				= 200	#积分
LT_PRO_SCORE_HONOR_ADD			= 201	#个人荣誉增加
LT_PRO_SCORE_HONOR_SUB			= 202	#个人荣誉减少

LT_PRO_SCORE_PERSONAL_ADD		= 203	#增加个人竞技积分
LT_PRO_SCORE_PERSONAL_SUB		= 204	#减少个人竞技积分

LT_PRO_SCORE_TONG_SCORE_ADD		= 205	#增加帮会竞技积分
LT_PRO_SCORE_TONG_SCORE_SUB		= 206	#减少帮会竞技积分

LT_FUNC_TEAM_COMPETITION_ADD	= 207	#添加组队竞技积分
LT_FUNC_TEAM_COMPETITION_SUB	= 208	#减少组队竞技积分

# --------------------------
# 物品2级分类
# --------------------------
LT_ITEM_ADD						= 1		#添加物品
LT_ITEM_DEL						= 2		#删除物品
LT_ITEM_SET_AMOUNT				= 3		#设置物品数量

# --------------------------
# 金钱2级分类
# --------------------------
LT_MONEY_CHANGE					= 1		#角色金钱改变

# --------------------------
# 银元宝2级分类
# --------------------------
LT_SILVER_CHANGE				= 1		#银元宝改变

# --------------------------
# 金元宝2级分类
# --------------------------
LT_GOLD_CHANGE					= 1		#金元宝改变

# --------------------------
# 异常分类
# --------------------------
LT_EXCEPT_LOG					= 1		#日志异常
LT_EXCEPT_LOTTERY				= 2		#锦囊错误
LT_EXCEPT_ITEM_DROP				= 3		#物品掉落配置错误
LT_EXCEPT_CHARGE_PRESENT		= 4		#收取奖励错误

#---------------------------
# GM工具操作
#---------------------------
LOG_GM_RESET_BANK_PW		= 1		#重设仓库密码
LOG_GM_CHANGE_POS			= 2		#更改角色坐标
LOG_GM_RESUME_ROLE			= 3		#角色恢复
LOG_GM_ACCOUNT_HOSTING		= 4		#帐号托管
LOG_GM_MODIFY_BULLETIN		= 5		#修改公告
LOG_GM_BATCH_LOCK_ACC		= 6		#批量封号
LOG_GM_BLOCK_ACC			= 7		#封存账号
LOG_GM_FREE_ACC				= 8		#封锁账号
LOG_GM_MODIFY_MONEY			= 9		#修改角色创世币
LOG_GM_MODIFY_PK_VALUE		= 10	#修改PK值
LOG_GM_MODIFY_PET_STRORAGE	= 11	#宠物修改
LOG_GM_MODIFY_GOLD_SILVER	= 12	#修改帐号元宝
LOG_GM_MODIFY_RELATION		= 13	#修改角色关系
LOG_GM_ADD_BULLETIN			= 14	#添加公告
LOG_GM_MODIFY_WEB_PRESENTID	= 15	#更新web礼物ID
LOG_GM_CONFIG_ITEMAWARDS	= 16	#奖励配置
LOG_GM_DELETE_ITEM			= 17	#删除玩家物品
LOG_GM_DELETE_MAIL			= 18	#删除玩家邮件
LOG_GM_DELETE_BUFF			= 19	#删除玩家buff
LOG_GM_DELETE_PET_ITEM		= 20	#删除宠物buff

# WebServer操作
LOG_GM_UPDATE_PASSWORD		= 21	#修改账号密码
LOG_GM_WEB_SUSPEND_ACC		= 22	#WebServer封存账号
LOG_GM_WEB_RESUME_ACC		= 23	#WebServer解封账号
LOG_GM_SET_ADULT			= 24	#标记用户为成年人
LOG_GM_GIVE_PRESENTS		= 25	#为指定账号送出奖励
LOG_GM_CHECK_PRESENTS_RE	= 26	#检查订单号的发奖品(重发)
LOG_GM_CHECK_PRESENTS		= 27	#检查订单号的发奖品
LOG_GM_USE_JACKAROO_CARD	= 28	#设置使用新手卡用户
LOG_GM_GIFT_SILVER_COINS_RE	= 29	#赠送银元宝（重发）
LOG_GM_GIFT_SILVER_COINS	= 30	#赠送银元宝
LOG_GM_CHARGE_RE			= 31	#兑换元宝（重发）
LOG_GM_CHARGE				= 32	#兑换元宝



#副本类型活动
COPYSPACE_ACTIVITYS = {
	csdefine.SPACE_TYPE_CITY_WAR				:	csdefine.ACTIVITY_TONG_DUO_CHENG,
	csdefine.SPACE_TYPE_TONG_ABA				:	csdefine.ACTIVITY_BANG_HUI_LEI_TAI,
	csdefine.SPACE_TYPE_TIAN_GUAN				:	csdefine.ACTIVITY_CHUANG_TIAN_GUAN,
	csdefine.SPACE_TYPE_RACE_HORSE				:	csdefine.ACTIVITY_SAI_MA,
	csdefine.SPACE_TYPE_POTENTIAL				:	csdefine.ACTIVITY_POTENTIAL,
	csdefine.SPACE_TYPE_WU_DAO					:	csdefine.ACTIVITY_WU_DAO_DA_HUI,
	csdefine.SPACE_TYPE_SHEN_GUI_MI_JING		:	csdefine.ACTIVITY_SHEN_GUI_MI_JING,
	csdefine.SPACE_TYPE_WU_YAO_QIAN_SHAO		:	csdefine.ACTIVITY_WU_YAO_QIAN_SHAO,
	csdefine.SPACE_TYPE_WU_YAO_WANG_BAO_ZANG	:	csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG,
	csdefine.SPACE_TYPE_SHUIJING				:	csdefine.ACTIVITY_SHUI_JING,
	csdefine.SPACE_TYPE_HUNDUN					:	csdefine.ACTIVITY_HUN_DUN_RU_QIN,
	csdefine.SPACE_TYPE_TEAM_COMPETITION		:	csdefine.ACTIVITY_TEAM_COMPETITION,
	csdefine.SPACE_TYPE_DRAGON					:	csdefine.ACTIVITY_DRAGON,
	csdefine.SPACE_TYPE_PROTECT_TONG			:	csdefine.ACTIVITY_TONG_PROTECT,
	csdefine.SPACE_TYPE_POTENTIAL_MELEE			:	csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU,
	csdefine.SPACE_TYPE_EXP_MELEE				:	csdefine.ACTIVITY_JING_YAN_LUAN_DOU,
	csdefine.SPACE_TYPE_PIG						:	csdefine.ACTIVITY_DU_DU_ZHU,
	csdefine.SPACE_TYPE_YAYU					:	csdefine.ACTIVITY_ZHENG_JIU_YA_YU,
	csdefine.SPACE_TYPE_XIE_LONG_DONG_XUE		:	csdefine.ACTIVITY_XIE_LONG,
	csdefine.SPACE_TYPE_FJSG					:	csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG,
	csdefine.SPACE_TYPE_TONG_COMPETITION		:	csdefine.ACTIVITY_BANG_HUI_JING_JI,
	csdefine.SPACE_TYPE_ROLE_COMPETITION		:	csdefine.ACTIVITY_GE_REN_JING_JI,
	csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN			:	csdefine.ACTIVITY_SHE_HUN_MI_ZHEN,
	csdefine.SPACE_TYPE_TEACH_KILL_MONSTER		:	csdefine.ACTIVITY_SHI_TU,
	csdefine.SPACE_TYPE_KUAFU_REMAINS			:	csdefine.ACTIVITY_KUA_FU,
	csdefine.SPACE_TYPE_RABBIT_RUN				:	csdefine.ACTIVITY_RUN_RABBIT,
	csdefine.SPACE_TYPE_BEFORE_NIRVANA			:	csdefine.ACTIVITY_BEFORE_NIRVANA,
	csdefine.SPACE_TYPE_CHALLENGE				:	csdefine.ACTIVITY_CHALLENGE_FUBEN,
	csdefine.SPACE_TYPE_TEAM_CHALLENGE			:	csdefine.ACTIVITY_TEAM_CHALLENGE,
	csdefine.SPACE_TYPE_PLOT_LV40				:	csdefine.ACTIVITY_PLOT_LV40,
	csdefine.SPACE_TYPE_PLOT_LV60				:	csdefine.ACTIVITY_PLOT_LV60,
	csdefine.SPACE_TYPE_TOWER_DEFENSE			:	csdefine.ACTIVITY_TOWER_DEFENSE,
	csdefine.SPACE_TYPE_YXLM					:	csdefine.ACTIVITY_YING_XIONG_LIAN_MENG,
	csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI			:	csdefine.ACTIVITY_YE_ZHAN_FENG_QI,
	csdefine.SPACE_TYPE_TONG_TURN_WAR			:	csdefine.ACTIVITY_TONG_TURN_WAR,
	csdefine.SPACE_TYPE_YXLM_PVP				:	csdefine.ACTIVITY_YING_XIONG_LIAN_MENG_PVP,
	csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN		:	csdefine.ACTIVITY_TONG_FENG_HUO_LIAN_TIAN,
	csdefine.SPACE_TYPE_TIAO_WU					:	csdefine.ACTIVITY_TIAO_WU,
	}



MONSTER_DIED_ABOUT_ACTIVITYS =	{
	csdefine.ACTIVITY_CHUANG_TIAN_GUAN			:	[ 20611156,20621156,20631156,20641156,20651156 ],	#闯天关
	csdefine.ACTIVITY_BIN_LIN_CHENG_XIA			:	[ 20614002,20624003,20634002,20644001,20654002,20614004,20624005,20624008 ],	#兵临城下
	csdefine.ACTIVITY_DU_DU_ZHU					:	[ 20354002 ],
	csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG		:	[ 20742031 ],	#封剑神宫
	csdefine.ACTIVITY_HUN_DUN_RU_QIN			:	[ 20124001,20134001,20144001 ],		#混沌入侵
	csdefine.ACTIVITY_NIU_MO_WANG				:	[ 20714003 ],						#牛魔王
	csdefine.ACTIVITY_QIAN_NIAN_DU_WA			:	[ 20334003 ],						#千年毒蛙
	csdefine.ACTIVITY_JING_YAN_LUAN_DOU			:	[ 20654003 ],						#经验乱斗
	csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU		:	[ 20754009 ],						#潜能乱斗
	csdefine.ACTIVITY_SHE_HUN_MI_ZHEN			:	[ 20714004 ],						#摄魂迷阵
	csdefine.ACTIVITY_SHUI_JING					:	[ 20724002 ],						#水晶副本
	csdefine.ACTIVITY_TIAN_JIANG_QI_SHOU		:	[ 20314006 ],						#天降奇兽
	csdefine.ACTIVITY_ZHENG_JIU_YA_YU			:	[ 20754011 ],						#拯救猰貐
	csdefine.ACTIVITY_DUO_LUO_LIE_REN			:	[ 20134003 ],						#堕落猎人55
	csdefine.ACTIVITY_BAI_SHE_YAO				:	[ 20724004 ],						#白蛇妖56
	csdefine.ACTIVITY_JU_LING_MO				:	[ 20714002 ],						#巨灵魔57
	csdefine.ACTIVITY_XIAO_TIAN_DA_JIANG		:	[ 20724005 ],						#啸天大将58
	csdefine.ACTIVITY_FENG_KUANG_JI_SHI			:	[ 20144003 ],						#疯狂祭师59
	csdefine.ACTIVITY_HAN_DI_DA_JIANG			:	[ 20754012 ],						#憾地大将60
	csdefine.ACTIVITY_SHENG_LIN_ZHI_WANG		:	[],									#森林之主
	csdefine.ACTIVITY_NU_MU_LUO_SHA				:	[],									#怒目罗刹
	csdefine.ACTIVITY_YE_WAI_BOSS				:	[ 20324001,20354001,20314001,20324002,20344001,20344002,20314002,20324003,20334001,20314003,20344003,20654001,20254001,20624001,20444001,20344004,20714001,20614001,20314004,20334002,20624002,20744001,20754001,20754002,20344005,20634001,20744002,20744003,20324004,20614003,20434001,20454001,20324005,20724001,20624004,20214001,20624007,20644003,20334004,20624006,20644004,20654004 ],
	csdefine.ACTIVITY_TONG_PROTECT				:	[20114002,20124002,20134002,20144002],
}

