# -*- coding: gb18030 -*-

"""This module implements Entity Callback Extend.
$Id: ECBExtend.py,v 1.64 2008-09-05 03:51:04 zhangyuxing Exp $
"""

########################################################################
#
# 模块: ECBExtend
# 功能: 实现BigWorld.Entity的Callback扩展类ECBExtend
#       包括下列回调
#         onMove(controllerID, userData)
#         onMoveFailure(controllerID, userData)
#         onNavigate(controllerID, userData)
#         onNavigateFailed(controllerID, userData)
#         onTurn(controllerID, userData)
#         onTimer(controllerID, userData)
#       相关的函数
#         moveToEntity
#         moveToPoint
#         navigate
#         navigateFollow
#         navigateStep
#         addYawRotator
#         addTimer
#
########################################################################
import BigWorld
from bwdebug import *

#
# Timer Callback ID section from 0x2001-0x3000
#
UPDATE_CLIENT_ITEMS_CBID					= 0x2001	# 分包发送物品
UPDATE_CLIENT_QUESTLOG_CBID					= 0x2002	# 分包更新客户端任务日志( hyw -- 2008.06.09 )

CHANGE_SPACE_TIMER_CBID						= 0x2011	# Space切换检查
CHAPMAIN_RESTOREINVOICE_CBID				= 0x2012	# 商人NPC基础类的恢复商品的timer
RESTORETIME_TIMER_CBID						= 0x2013	# For Time Restore
MONENMITY_ADD_TRAP_TIMER_CBID				= 0x2014	# 初始化后一段时间内放陷井
MONSTER_CORPSE_DELAY_TIMER_CBID				= 0x2015	# 怪物死亡后尸体消失时间，单位：秒，float
FIGHT_TIMER_CBID							= 0x2016	# 在战斗状态下的timer
BUFF_TIMER_CBID								= 0x2017	# Buff作用的timer
REVERT_HPMP_TIMER_CBID						= 0x2018	# HP、MP恢复timer
HEARTBEAT_TIMER_CBID						= 0x2019	# 心跳
DELAY_DAMAGE_TIMER_CBID						= 0x201A	# 延时费血timer(同步技能伤害)
INTONATE_TIMER_CBID							= 0x201B	# 吟唱时间
DESTROY_SELF_TIMER_CBID						= 0x201C	# 删除entity自身
THINK_TIMER_CBID							= 0x201D	# npc思考时间
UNHANG_TIMER_CBID							= 0x201E	# 从Hang状态变成Free状态
HANG_AND_KILL_TIMER_CBID					= 0x201F	# 挂起并杀死怪物
DELAY_SHOW_MSG_TIMER_CBID					= 0x2020	# 延迟向客户端发送一个showMsg()信息，通常用于需要在玩家一进入游戏后显示消息用。
MONSTER_RESUME_CBID							= 0x2021	# 怪物生命和法力恢复
AI_TIMER_CBID								= 0x2023	# 进入ai检测timer

CALL_MONSTER_FOR_108_CBID					= 0x2024	# 108星召唤怪物
ACTIVITY_MONSTER_DISAPPEAR_CBID				= 0x2025	# 活动怪物消失

GEM_ROLE_TIME_LIMIT_CBID					= 0x2026	# 玩家经验石系统，14:57 2008-7-23，wsf
GEM_PET_TIME_LIMIT_CBID						= 0x2027	# 宠物经验石系统，14:58 2008-7-23，wsf

AUTO_TALK_CBID								= 0x2028	# 服务器出发对话
ADD_NEW_QUEST_CBID							= 0x2029	# 服务器发送任务

QUEST_DART_ACTIVITY_START_CBID				= 0x202a	# 国运活动开始
QUEST_DART_ACTIVITY_END_CBID				= 0x202b	# 国运活动结束
FLY_TO_MASTER_CB							= 0x202c	# 镖车过传送门
MERCHANT_RESTOREINVOICE_CBID				= 0x202d	# 跑商

#镖局信息管理
QUERY_DART_MESSAGE_CBID						= 0x202e
QUERY_TONG_PRESTIGE_CBID					= 0x202f	# 查询帮会声望排名

DELAY_CALL_TIMER_CBID						= 0x2030	# 延时调用函数			2009-3-24 gjx

PET_HEARTBEAT_CBID							= 0x2031	# 跟随玩家的侦测
PET_ATTACK_CBID								= 0x2032	# 控制宠物战斗
PET_DIE_WITHDRAW_DELAY_CBID					= 0x2033	# 死亡回收延时

QUEST_BOX_REDIVIOUS_TIMER_CBID				= 0x2034	# QuestBox类型的entity重新出现的时间

TITLE_TIMER_CBID							= 0x2035	# 控制称号获得的时限。15:56 2008-7-15，wsf


# PK系统
PK_STATE_ATTACK_TIMER_CBID					= 0x2036	# pk状态持续时间控制器
PK_ADD_GOODNESS_TIMER_CBID					= 0x2037	# 红名或蓝名玩家善恶值改变时间控制器
PK_VALUE_LESS_TIMER_CBID					= 0x2038	# 在线pk值减少timer

TIANGUAN_MENBER_GOIN						= 0x2039	# 成员进入天关

ADD_SUN_BATH_COUNT							= 0x203a	# 增加日光浴合法时间

#DEL_QUEST_IMPERIAL_EXAMINATION				= 0x203b	# 删除科举任务

LEAVE_RACEHORSE_MAP							= 0x203c	# 离开赛马地图

TEAM_FOLLOW_TRANSPORT						= 0x203d	# 组队跟随传送

LEAVE_TEAM_TIMER							= 0x203e	# 传出当前所在空间

REMOVE_ROB_FLAG								= 0x203f	# 删除劫镖标志

PRE_TO_FIGHT_STATE							= 0x2041	# 怪物从预战斗进入战斗状态
PRE_REMOVE_FLAG								= 0x2044	# 怪物从预战斗进入战斗状态

# 骑宠
VEHICLE_TELEPORT_TIMER_CBID					= 0x2043	# 骑宠传送检测Timer


ROLE_REVIVE_TIMER							= 0x2045
MONSTER_CHANGE_AI_TO_ONE_LEVEL_CBID			= 0x2046	# 怪物更还AI level

ADD_YAYU_TO_EMEMY_CBID						= 0x2047	# 增加猰貐为敌人
YAYU_BOSS_KUANGBAO_CBID						= 0x2048	# 混沌将领（猰貐BOSS）变得狂暴

TISHOU_OPERATE_SPEED_CBID					= 0x2049	# 替售行为控制
# 切磋
QIECUO_NOTIFY_CBID							= 0x204a	# 切磋通知timer
QIECUO_CHECK_CBID							= 0x204b	# 切磋检测timer
QIECUO_CONFIRM_CBID							= 0x204c	# 切磋检测timer


HONOR_RETURN_CBID							= 0x204d	# 荣誉度恢复

INIT_DART_OWNER_CBID						= 0x204e	# 初始化镖车主人

MONSTER_BOMB_CBID							= 0x2050	# 怪物出生后爆炸Timer
MONSTER_RECOVER_CBID						= 0x2051	# 怪物出生后治疗Timer

ROLE_ABANDON_DART_QUEST_CBID				= 0x2052	# 角色请求放弃镖车回调
AREARESTRICTTRANSDUCER_CHECK_TIMER_CBID		= 0x2053	# 范围触发器检测状态timer

ADD_QUEST_FLAG_TIMER_CBID					= 0x2054	# 增加任务表现位回调

# 果树存活Timer
FRUITTREE_GROWTH_CBID						= 0x2055	# 果树存活timer
FRUITTREE_DIE_CBID							= 0x2056    # 果树死亡timer

# 召唤entity
CALL_MONSTER_INIT							= 0x2057

#播放视频buffer延迟播放镜头回调
DELAY_PLAYCAMERA_TIMER_CBID                                             = 0x2058        #延迟播放镜头回调

# pet ai
PET_TELEPORT_CBID							= 0x2059

#悬赏任务
REWARD_QUEST_SYSTEM_REFRESH					= 0x205a	# 悬赏任务系统刷新timer

#绝地反击活动确认timer
JUE_DI_FAN_JI_CONFIRM						= 0x205b	# 绝地反击确认timer

#
# Turn Callback ID section from 0x4001-0x5000
# 防沉迷
WALLOW_PERIODIC_NOTIFY_CBID					= 0x4001	# 定期沉迷通知

#
# Move Callback ID section from 0x6001-0x7000
#
GOTO_POSITION_CBID							= 0x6001	# 移动到某地方时的回调，用于gotoPosition()方法
CHASE_ENTITY_CBID							= 0x6002	# 追赶一个entity时的回调，用于chaseEntity()方法

MOVE_TO_PATROL_POINT_FINISH_CB				= 0x8001	# 移动到巡逻点结束

SHOW_LOTTER_ITEMS							= 0x8002	# 锦囊向服务器发送物品数据的TIMER
MOVE_TO_POINT_FINISH_CB						= 0x8003

MOVE_RADI_FOLLOW_CBID								= 0x8014   #怪物围绕目标跑动

MOVE_NEAR_RADI_FOLLOW_CBID					= 0x8015   #怪物围绕目标做靠近目标跑动
MOVE_FAR_RADI_FOLLOW_CBID					= 0x8016   #怪物围绕目标做远离目标跑动

# Navigate Callback ID section from 0x8001-0x9000
CITY_WAR_CAST_NPC_TIMER_CBID				= 0x9001	# 战场将领，统帅周期刷守卫timer
CITY_WAR_BUILD_TOWER_CBID					= 0x9002	# 战场塔楼建造timer
CITY_WAR_NPC_FOLLOW_CBID					= 0x9003	# 城战 龙炮和玄坚跟随主人处理timer

# 辅助技能
HOMING_SPELL_TICK_CBID						= 0x9100	# 辅助技能的tick回调

# 触发技能
TRIGGER_SPELL_CBID						= 0x9101	# 触发技能的持续时间回调

#冲锋技能对玩家速度的改变回调
CHARGE_SPELL_CBID						= 0x9102	# 冲锋技能对玩家速度的改变回调

#跳跃能量值恢复timer
REVERT_ENERGY_TIMER_CBID					= 0x9103

#脱离战斗格斗点数自动衰减timmer
CombatCount_TIMER_CBID					        = 0x9104

# 替售数据
TISHOU_QUERY_DATA_CBID						= 0x9200	#获取替售物品数据

LAST_TIMER_CBID								= 0xffff

NPC_VISIBLE_CHANGE							= 0xa000
STEALTH_TIMER_CBID							= 0xa001

FUNCTION_SPELL_TIMER_CBID                                               = 0xa002       #talkfunc的释放技能TIMER

# 副本组队系统
CTM_CONFIRM_RESUMING_HALTED_RAID			= 0xa010		# 确认加入半路副本的队伍

# BaoZangCopyInterface
ENTER_BAO_ZANG_PVP							= 0xa011		# 进入宝藏副本倒计时
READY_BAO_ZANG_PVP							= 0xa012		# 宝藏副本准备倒计时

#combo计数2.0秒内没有攻击清0的timmer
COMBO_COUNT_TIMER_CBID                                         = 0xa013  #combo计数2.0秒内没有攻击清0的timmer

WAIT_ROLE_REVIVE_CBID						= 0xa014		# 拯救猰貐副本内玩家死亡30秒未复活timer

#骑宠饱腹度回调
VEHICLE_ACTIVATE_FULLDEGREE_TIMMER_CBID                      = 0xa015		# 激活的骑宠饱腹度回调timer
VEHICLE_CONJURE_FULLDEGREE_TIMMER_CBID                       = 0xa016		# 召唤的骑宠饱腹度回调timer

CHANGE_YAW									= 0xa017
PK_STATE_FIGHT_BACK_TIMER_CBID				= 0xa018		# pk反击状态持续时间控制器

#moveTrap
DELAY_DESTROY_SELF_TIMER_CBID				= 0xa019	# 延迟销毁timer

# 背包
ROLE_ITEM_BAG_SAVE_LATER					= 0xa020	# 背包操作延迟写数据库

#Buff_299004
FLAME_WAY_TIMER_CBID						= 0xa021	# 火焰路径生成timer

# 天命轮回副本
AUTO_THROW_SIEVE_TIMER_CBID					= 0xa022	# 系统掷筛子timer
WAIT_ROLE_REVIVE_PRE_SPACE_CBID				= 0xa023	# 通关失败打开棋盘界面timer
ROLE_UESE_LIVE_POINT_REVIE_CBID				= 0xa024	# 关卡内使用复活点自动复活timer

DELAY_LINE_TO_POINT_TIMER_CBID				= 0xa025	# 延迟运动timer
CALL_BLEW_MONSTER_CBID						= 0xa026	# 召唤自爆怪物timer

# 劲舞时刻
UPDATE_CLIENT_DANCING_KING_INFOS_CBID		= 0xa027	# 分批发送舞王的信息
DANCECHELLENGETIMER							= 0xa028    # 挑战斗舞6分钟时间限制
DANCETIMEOUTTIMER 							= 0xa02b	# 普通位置经验的8个小时了
DANCEKINGTIMEOUTTIMER						= 0xa02c	# 舞王位置经验的8个小时了

#阵营英雄王座
ENTER_CAMP_YING_XIONG_COPY					= 0xa029	# 阵营英雄王座进入倒计时
READY_CAMP_YING_XIONG_COPY					= 0xa02a	# 阵营英雄王座准备倒计时

# 防守副本
COPY_FANG_SHOU_CHECK_ROLE_POSITION_CBID		= 0xa100	# 防守副本检查角色位置timer



#
# 全局Callback字典，用来从指定的ID查询回调函数
#
gcbs = {
	UPDATE_CLIENT_ITEMS_CBID				: "onTimer_updateClientItems",
	UPDATE_CLIENT_QUESTLOG_CBID				: "onTimer_updateClientQuestLogs",

	RESTORETIME_TIMER_CBID					: "onRestoreTime",
	BUFF_TIMER_CBID							: "onBuffTick",
	HEARTBEAT_TIMER_CBID					: "onHeartbeat",
	DELAY_DAMAGE_TIMER_CBID					: "onReceiveDelayOver",

	LAST_TIMER_CBID							: "onLastTimer",	# !!!Should never hit me!!!
	REVERT_HPMP_TIMER_CBID					: "onRevertTimer",
	CHAPMAIN_RESTOREINVOICE_CBID			: "onRestoreInvoices",
	MONENMITY_ADD_TRAP_TIMER_CBID			: "onPlaceTrap",
	MONSTER_CORPSE_DELAY_TIMER_CBID			: "onCorpseDelayTimer",
	FIGHT_TIMER_CBID						: "onFightTimer",
	INTONATE_TIMER_CBID						: "onIntonateOver",
	DESTROY_SELF_TIMER_CBID					: "onDestroySelfTimer",
	THINK_TIMER_CBID						: "onThinkTimer",

	UNHANG_TIMER_CBID						: "onUnhang",
	HANG_AND_KILL_TIMER_CBID				: "onHangAndKill",
	MONSTER_RESUME_CBID						: "onResumeTimer",

	# Navigate Callback
	GOTO_POSITION_CBID						: "onMovedFinish",
	CHASE_ENTITY_CBID						: "onChaseFinish",

	# about pet( hyw )
	PET_HEARTBEAT_CBID						: "onPetHeartbeatTimer",
	PET_ATTACK_CBID							: "onPetAttackTimer",
	PET_DIE_WITHDRAW_DELAY_CBID				: "onPetDieWithdrawTimer",
	PET_TELEPORT_CBID						: "onTeleportTimer",

	#pk system Callback
	PK_STATE_ATTACK_TIMER_CBID				: "onPkAttackChangeTimer",
	PK_ADD_GOODNESS_TIMER_CBID				: "onAddGoodnessTimer",
	PK_VALUE_LESS_TIMER_CBID				: "onLessPkValueTimer",
	PK_STATE_FIGHT_BACK_TIMER_CBID			: "onPkFightBackChangeTimer",

	VEHICLE_TELEPORT_TIMER_CBID				: "onVehicleTeleportTimer",

	# patrol ( kebiao )
	MOVE_TO_PATROL_POINT_FINISH_CB			: "onPatrolToPointFinish",
	MOVE_TO_POINT_FINISH_CB					: "onLineToPointFinish",
	MOVE_RADI_FOLLOW_CBID					: "onMoveRaidFollowCB",
	MOVE_NEAR_RADI_FOLLOW_CBID				: "onMoveNearRaidFollowCB",
	MOVE_FAR_RADI_FOLLOW_CBID				: "onMoveFarRaidFollowCB",

	#ai ( kb )
	AI_TIMER_CBID							: "onAITimer",
	# tong( kb )
	QUERY_TONG_PRESTIGE_CBID				: "onOrderTongByPrestige",

	# 称号( wsf )
	TITLE_TIMER_CBID						: "onTitleAddTimer",

	CALL_MONSTER_FOR_108_CBID				: "callMonster",
	ACTIVITY_MONSTER_DISAPPEAR_CBID			: "disappear",

	# 经验石系统( wsf )
	GEM_ROLE_TIME_LIMIT_CBID				: "onRoleGemTimeLimit",
	GEM_PET_TIME_LIMIT_CBID					: "onPetGemTimeLimit",

	AUTO_TALK_CBID							: "onAutoTalk",
	ADD_NEW_QUEST_CBID						: "onAutoAddNewQuest",

	# 镖局信息管理
	QUERY_DART_MESSAGE_CBID					: "onQueryDartMessage",
	QUEST_DART_ACTIVITY_START_CBID			: "onDartActivityStart",
	QUEST_DART_ACTIVITY_END_CBID			: "onDartActivityEnd",
	FLY_TO_MASTER_CB						: "flyToMasterCB",

	#跑商
	MERCHANT_RESTOREINVOICE_CBID			: "onRestoreMerchandise",

	QUEST_BOX_REDIVIOUS_TIMER_CBID			: "onRedivious",

	TIANGUAN_MENBER_GOIN					: "enterTianguan",

	SHOW_LOTTER_ITEMS						: "showLotterItems",
	ADD_SUN_BATH_COUNT						: "addSunBathCount",

	LEAVE_RACEHORSE_MAP						: "onLeaveRacehorseMap",

	CITY_WAR_CAST_NPC_TIMER_CBID			: "onCityWarCastNPCTimer",
	CITY_WAR_BUILD_TOWER_CBID				: "onCityWarTowerBuildComplete",
	CITY_WAR_NPC_FOLLOW_CBID				: "onCityWarNPCFollowProcess",

	TEAM_FOLLOW_TRANSPORT					: "team_followTransportCB",

	DELAY_CALL_TIMER_CBID					: "onDelayCallTimer",

	LEAVE_TEAM_TIMER						: "onLeaveTeamTimer",
	REMOVE_ROB_FLAG							: "onRemoveRobFlag",
	PRE_TO_FIGHT_STATE						: "preToFightState",
	PRE_REMOVE_FLAG							: "preRemoveFlag",
	ROLE_REVIVE_TIMER						: "onReviveTimer",
	MONSTER_CHANGE_AI_TO_ONE_LEVEL_CBID		: "onSetAILevelToOne",
	ADD_YAYU_TO_EMEMY_CBID					: "onAddYayuToEnemy",
	YAYU_BOSS_KUANGBAO_CBID					: "onKuangbao",
	TISHOU_OPERATE_SPEED_CBID				: "onAllowOperate",
	QIECUO_NOTIFY_CBID						: "onQieCuoTimerNotify",
	QIECUO_CHECK_CBID						: "onQieCuoTimerCheck",
	QIECUO_CONFIRM_CBID						: "onQieCuoConfirm",
	HONOR_RETURN_CBID						: "onHonorRecover",
	INIT_DART_OWNER_CBID					: "onInitOwner",
	MONSTER_BOMB_CBID						: "onBombTimer",
	MONSTER_RECOVER_CBID					: "onRecoverTimer",
	HOMING_SPELL_TICK_CBID					: "onHomingSpellTick",
	TRIGGER_SPELL_CBID					: "onTriggerSpell",
	CHARGE_SPELL_CBID					: "onChargeOver",
	ROLE_ABANDON_DART_QUEST_CBID			: "onAbandonDartQuestCBID",
	AREARESTRICTTRANSDUCER_CHECK_TIMER_CBID : "onAreaRestrictTransducerCheckTimer",
	ADD_QUEST_FLAG_TIMER_CBID				: "onQuestFlagCBID",

	WALLOW_PERIODIC_NOTIFY_CBID				: "onWallowNotify",

	FRUITTREE_GROWTH_CBID					: "onFruitTreeGrowth",
	FRUITTREE_DIE_CBID						: "onFruitTreeDie",

	CALL_MONSTER_INIT						: "onTimer_initCallMonster",

        NPC_VISIBLE_CHANGE						: "onTimerNPCVisibleChange",
        TISHOU_QUERY_DATA_CBID					: "onQueryTiShouData",
        DELAY_PLAYCAMERA_TIMER_CBID                             :   "onDelayPlayCamera" ,
        STEALTH_TIMER_CBID						: "onStealth",
        REVERT_ENERGY_TIMER_CBID                                : "onAutoEnergyTimer",
        CombatCount_TIMER_CBID                                  : "onAutoCombatCountTimer",
        FUNCTION_SPELL_TIMER_CBID                                : "onFuncSpell",

	CTM_CONFIRM_RESUMING_HALTED_RAID		: "onTimer_joinHaltedRaid",
	ENTER_BAO_ZANG_PVP						: "baoZangEnterCopy",
	READY_BAO_ZANG_PVP						: "baoZangEnterReadyEnd",
	
	
	COMBO_COUNT_TIMER_CBID                                  : "clearComboCount",

	WAIT_ROLE_REVIVE_CBID					: "onTime_RoleRevive",
	VEHICLE_ACTIVATE_FULLDEGREE_TIMMER_CBID                 : "onActivateVehicleFD",
	VEHICLE_CONJURE_FULLDEGREE_TIMMER_CBID                  : "onConjureVehicleFD",
	CHANGE_YAW								: "changeYaw",
	DELAY_DESTROY_SELF_TIMER_CBID			: "onDelayDestroySelfTimer",
	ROLE_ITEM_BAG_SAVE_LATER				: "kitbags_onSaveLaterTimer",
	FLAME_WAY_TIMER_CBID					: "onFlameWayTimer",
	AUTO_THROW_SIEVE_TIMER_CBID				: "onAutoThrowSieve",
	WAIT_ROLE_REVIVE_PRE_SPACE_CBID			: "onTime_RoleRevivePreSpace",
	ROLE_UESE_LIVE_POINT_REVIE_CBID			: "reviveCostLivePoint",
	DELAY_LINE_TO_POINT_TIMER_CBID			: "onDelayLineToPointTimer",
	CALL_BLEW_MONSTER_CBID					: "onCallBlewMonsterTimer",
	REWARD_QUEST_SYSTEM_REFRESH				: "onTimer_rewardQuestRefresh",
	UPDATE_CLIENT_DANCING_KING_INFOS_CBID	: "onTimer_updateClientDancingKingInfos",
	DANCECHELLENGETIMER						: "onTimerDanceChellengeTimeOver",
	JUE_DI_FAN_JI_CONFIRM					: "onTimer_jueDiFanJiConfirm",
	ENTER_CAMP_YING_XIONG_COPY				: "yingXiongCampEnterCopy",
	READY_CAMP_YING_XIONG_COPY				: "yingXiongCampEnterReadyEnd",
	DANCETIMEOUTTIMER						: "danceTimeOut",
	DANCEKINGTIMEOUTTIMER					: "danceKingTimeOut",
	COPY_FANG_SHOU_CHECK_ROLE_POSITION_CBID	: "onTimer_FangShouCheckRolePos",
}

#
# BigWorld.Entity的Callback扩展类ECBExtend
#
# 注意: 本Class不能被单独实例化，只能与BigWorld.Entity同时被ConcreteEntity类继承才有意义
#
class ECBExtend:
	#
	# 功能: 初始化
	# 参数:
	# 返回: 不能被单独实例化
	#
	def __init__( self ):
		pass

	#
	# 功能: 实现BigWorld.Entity.onTimer，当某个Timer Tick到达时被调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       timerID			timer的ID
	#       cbID			Callback ID
	# 返回:
	#
	def onTimer( self, timerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
			#cb( timerID, cbID )	# phw：移到下面
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke, self )		# 增加一个输出错误类型，便于快捷查找调用此函数的对象
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		# phw: 从上面移下来，因为在这个函数里可能也会有上面的KeyError和AttributeError异常产生
		# 移下来后产生错误时容易测试
		cb( timerID, cbID )

	#
	# 功能: 实现BigWorld.Entity.onTurn，当某个addYawRotator动作完成时调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       controllerID	addYawRotator返回的controllerID
	#       cbID			Callback ID
	# 返回:
	#
	def onTurn( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		cb( controllerID, cbID )

	#
	# 功能: 实现BigWorld.Entity.onMove，当某个moveToPoint或者moveToEntity到达目标位置时调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       controllerID	moveToPoint或者moveToEntity返回的controllerID
	#       cbID			Callback ID
	# 返回:
	#
	def onMove( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onMoveTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, True )

	#
	# 功能: 实现BigWorld.Entity.onMoveFailure，当某个moveToPoint或者moveToEntity无法到达目标位置时调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       controllerID	moveToPoint或者moveToEntity返回的controllerID
	#       cbID			Callback ID
	# 返回:
	#
	def onMoveFailure( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onMoveTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, False )

	#
	# 功能: 实现BigWorld.Entity.onNavigate，当某个navigate到达目标位置时调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       controllerID	navigate返回的controllerID
	#       cbID			Callback ID
	# 返回:
	#
	def onNavigate( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onNavigateTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, True )

	#
	# 功能: 实现BigWorld.Entity.onNavigateFailure，当某个navigate无法到达目标位置时调用
	#       转向该cbID对应的回调函数
	# 参数:
	#       controllerID	navigate返回的controllerID
	#       cbID			Callback ID
	# 返回:
	#
	def onNavigateFailed( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs不包含cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entity没有实现对应的回调函数
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onNavigateTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, False )

#########################
# End of ECBExtend.py   #
#########################
