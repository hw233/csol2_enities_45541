# -*- coding: gb18030 -*-

"""This module implements Entity Callback Extend.
$Id: ECBExtend.py,v 1.64 2008-09-05 03:51:04 zhangyuxing Exp $
"""

########################################################################
#
# ģ��: ECBExtend
# ����: ʵ��BigWorld.Entity��Callback��չ��ECBExtend
#       �������лص�
#         onMove(controllerID, userData)
#         onMoveFailure(controllerID, userData)
#         onNavigate(controllerID, userData)
#         onNavigateFailed(controllerID, userData)
#         onTurn(controllerID, userData)
#         onTimer(controllerID, userData)
#       ��صĺ���
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
UPDATE_CLIENT_ITEMS_CBID					= 0x2001	# �ְ�������Ʒ
UPDATE_CLIENT_QUESTLOG_CBID					= 0x2002	# �ְ����¿ͻ���������־( hyw -- 2008.06.09 )

CHANGE_SPACE_TIMER_CBID						= 0x2011	# Space�л����
CHAPMAIN_RESTOREINVOICE_CBID				= 0x2012	# ����NPC������Ļָ���Ʒ��timer
RESTORETIME_TIMER_CBID						= 0x2013	# For Time Restore
MONENMITY_ADD_TRAP_TIMER_CBID				= 0x2014	# ��ʼ����һ��ʱ���ڷ��ݾ�
MONSTER_CORPSE_DELAY_TIMER_CBID				= 0x2015	# ����������ʬ����ʧʱ�䣬��λ���룬float
FIGHT_TIMER_CBID							= 0x2016	# ��ս��״̬�µ�timer
BUFF_TIMER_CBID								= 0x2017	# Buff���õ�timer
REVERT_HPMP_TIMER_CBID						= 0x2018	# HP��MP�ָ�timer
HEARTBEAT_TIMER_CBID						= 0x2019	# ����
DELAY_DAMAGE_TIMER_CBID						= 0x201A	# ��ʱ��Ѫtimer(ͬ�������˺�)
INTONATE_TIMER_CBID							= 0x201B	# ����ʱ��
DESTROY_SELF_TIMER_CBID						= 0x201C	# ɾ��entity����
THINK_TIMER_CBID							= 0x201D	# npc˼��ʱ��
UNHANG_TIMER_CBID							= 0x201E	# ��Hang״̬���Free״̬
HANG_AND_KILL_TIMER_CBID					= 0x201F	# ����ɱ������
DELAY_SHOW_MSG_TIMER_CBID					= 0x2020	# �ӳ���ͻ��˷���һ��showMsg()��Ϣ��ͨ��������Ҫ�����һ������Ϸ����ʾ��Ϣ�á�
MONSTER_RESUME_CBID							= 0x2021	# ���������ͷ����ָ�
AI_TIMER_CBID								= 0x2023	# ����ai���timer

CALL_MONSTER_FOR_108_CBID					= 0x2024	# 108���ٻ�����
ACTIVITY_MONSTER_DISAPPEAR_CBID				= 0x2025	# �������ʧ

GEM_ROLE_TIME_LIMIT_CBID					= 0x2026	# ��Ҿ���ʯϵͳ��14:57 2008-7-23��wsf
GEM_PET_TIME_LIMIT_CBID						= 0x2027	# ���ﾭ��ʯϵͳ��14:58 2008-7-23��wsf

AUTO_TALK_CBID								= 0x2028	# �����������Ի�
ADD_NEW_QUEST_CBID							= 0x2029	# ��������������

QUEST_DART_ACTIVITY_START_CBID				= 0x202a	# ���˻��ʼ
QUEST_DART_ACTIVITY_END_CBID				= 0x202b	# ���˻����
FLY_TO_MASTER_CB							= 0x202c	# �ڳ���������
MERCHANT_RESTOREINVOICE_CBID				= 0x202d	# ����

#�ھ���Ϣ����
QUERY_DART_MESSAGE_CBID						= 0x202e
QUERY_TONG_PRESTIGE_CBID					= 0x202f	# ��ѯ�����������

DELAY_CALL_TIMER_CBID						= 0x2030	# ��ʱ���ú���			2009-3-24 gjx

PET_HEARTBEAT_CBID							= 0x2031	# ������ҵ����
PET_ATTACK_CBID								= 0x2032	# ���Ƴ���ս��
PET_DIE_WITHDRAW_DELAY_CBID					= 0x2033	# ����������ʱ

QUEST_BOX_REDIVIOUS_TIMER_CBID				= 0x2034	# QuestBox���͵�entity���³��ֵ�ʱ��

TITLE_TIMER_CBID							= 0x2035	# ���ƳƺŻ�õ�ʱ�ޡ�15:56 2008-7-15��wsf


# PKϵͳ
PK_STATE_ATTACK_TIMER_CBID					= 0x2036	# pk״̬����ʱ�������
PK_ADD_GOODNESS_TIMER_CBID					= 0x2037	# ��������������ƶ�ֵ�ı�ʱ�������
PK_VALUE_LESS_TIMER_CBID					= 0x2038	# ����pkֵ����timer

TIANGUAN_MENBER_GOIN						= 0x2039	# ��Ա�������

ADD_SUN_BATH_COUNT							= 0x203a	# �����չ�ԡ�Ϸ�ʱ��

#DEL_QUEST_IMPERIAL_EXAMINATION				= 0x203b	# ɾ���ƾ�����

LEAVE_RACEHORSE_MAP							= 0x203c	# �뿪�����ͼ

TEAM_FOLLOW_TRANSPORT						= 0x203d	# ��Ӹ��洫��

LEAVE_TEAM_TIMER							= 0x203e	# ������ǰ���ڿռ�

REMOVE_ROB_FLAG								= 0x203f	# ɾ�����ڱ�־

PRE_TO_FIGHT_STATE							= 0x2041	# �����Ԥս������ս��״̬
PRE_REMOVE_FLAG								= 0x2044	# �����Ԥս������ս��״̬

# ���
VEHICLE_TELEPORT_TIMER_CBID					= 0x2043	# ��贫�ͼ��Timer


ROLE_REVIVE_TIMER							= 0x2045
MONSTER_CHANGE_AI_TO_ONE_LEVEL_CBID			= 0x2046	# �������AI level

ADD_YAYU_TO_EMEMY_CBID						= 0x2047	# ���Ӫm؅Ϊ����
YAYU_BOSS_KUANGBAO_CBID						= 0x2048	# ���罫�죨�m؅BOSS����ÿ�

TISHOU_OPERATE_SPEED_CBID					= 0x2049	# ������Ϊ����
# �д�
QIECUO_NOTIFY_CBID							= 0x204a	# �д�֪ͨtimer
QIECUO_CHECK_CBID							= 0x204b	# �д���timer
QIECUO_CONFIRM_CBID							= 0x204c	# �д���timer


HONOR_RETURN_CBID							= 0x204d	# �����Ȼָ�

INIT_DART_OWNER_CBID						= 0x204e	# ��ʼ���ڳ�����

MONSTER_BOMB_CBID							= 0x2050	# ���������ըTimer
MONSTER_RECOVER_CBID						= 0x2051	# �������������Timer

ROLE_ABANDON_DART_QUEST_CBID				= 0x2052	# ��ɫ��������ڳ��ص�
AREARESTRICTTRANSDUCER_CHECK_TIMER_CBID		= 0x2053	# ��Χ���������״̬timer

ADD_QUEST_FLAG_TIMER_CBID					= 0x2054	# �����������λ�ص�

# �������Timer
FRUITTREE_GROWTH_CBID						= 0x2055	# �������timer
FRUITTREE_DIE_CBID							= 0x2056    # ��������timer

# �ٻ�entity
CALL_MONSTER_INIT							= 0x2057

#������Ƶbuffer�ӳٲ��ž�ͷ�ص�
DELAY_PLAYCAMERA_TIMER_CBID                                             = 0x2058        #�ӳٲ��ž�ͷ�ص�

# pet ai
PET_TELEPORT_CBID							= 0x2059

#��������
REWARD_QUEST_SYSTEM_REFRESH					= 0x205a	# ��������ϵͳˢ��timer

#���ط����ȷ��timer
JUE_DI_FAN_JI_CONFIRM						= 0x205b	# ���ط���ȷ��timer

#
# Turn Callback ID section from 0x4001-0x5000
# ������
WALLOW_PERIODIC_NOTIFY_CBID					= 0x4001	# ���ڳ���֪ͨ

#
# Move Callback ID section from 0x6001-0x7000
#
GOTO_POSITION_CBID							= 0x6001	# �ƶ���ĳ�ط�ʱ�Ļص�������gotoPosition()����
CHASE_ENTITY_CBID							= 0x6002	# ׷��һ��entityʱ�Ļص�������chaseEntity()����

MOVE_TO_PATROL_POINT_FINISH_CB				= 0x8001	# �ƶ���Ѳ�ߵ����

SHOW_LOTTER_ITEMS							= 0x8002	# �����������������Ʒ���ݵ�TIMER
MOVE_TO_POINT_FINISH_CB						= 0x8003

MOVE_RADI_FOLLOW_CBID								= 0x8014   #����Χ��Ŀ���ܶ�

MOVE_NEAR_RADI_FOLLOW_CBID					= 0x8015   #����Χ��Ŀ��������Ŀ���ܶ�
MOVE_FAR_RADI_FOLLOW_CBID					= 0x8016   #����Χ��Ŀ����Զ��Ŀ���ܶ�

# Navigate Callback ID section from 0x8001-0x9000
CITY_WAR_CAST_NPC_TIMER_CBID				= 0x9001	# ս�����죬ͳ˧����ˢ����timer
CITY_WAR_BUILD_TOWER_CBID					= 0x9002	# ս����¥����timer
CITY_WAR_NPC_FOLLOW_CBID					= 0x9003	# ��ս ���ں�����������˴���timer

# ��������
HOMING_SPELL_TICK_CBID						= 0x9100	# �������ܵ�tick�ص�

# ��������
TRIGGER_SPELL_CBID						= 0x9101	# �������ܵĳ���ʱ��ص�

#��漼�ܶ�����ٶȵĸı�ص�
CHARGE_SPELL_CBID						= 0x9102	# ��漼�ܶ�����ٶȵĸı�ص�

#��Ծ����ֵ�ָ�timer
REVERT_ENERGY_TIMER_CBID					= 0x9103

#����ս���񶷵����Զ�˥��timmer
CombatCount_TIMER_CBID					        = 0x9104

# ��������
TISHOU_QUERY_DATA_CBID						= 0x9200	#��ȡ������Ʒ����

LAST_TIMER_CBID								= 0xffff

NPC_VISIBLE_CHANGE							= 0xa000
STEALTH_TIMER_CBID							= 0xa001

FUNCTION_SPELL_TIMER_CBID                                               = 0xa002       #talkfunc���ͷż���TIMER

# �������ϵͳ
CTM_CONFIRM_RESUMING_HALTED_RAID			= 0xa010		# ȷ�ϼ����·�����Ķ���

# BaoZangCopyInterface
ENTER_BAO_ZANG_PVP							= 0xa011		# ���뱦�ظ�������ʱ
READY_BAO_ZANG_PVP							= 0xa012		# ���ظ���׼������ʱ

#combo����2.0����û�й�����0��timmer
COMBO_COUNT_TIMER_CBID                                         = 0xa013  #combo����2.0����û�й�����0��timmer

WAIT_ROLE_REVIVE_CBID						= 0xa014		# ���Ȫm؅�������������30��δ����timer

#��豥���Ȼص�
VEHICLE_ACTIVATE_FULLDEGREE_TIMMER_CBID                      = 0xa015		# �������豥���Ȼص�timer
VEHICLE_CONJURE_FULLDEGREE_TIMMER_CBID                       = 0xa016		# �ٻ�����豥���Ȼص�timer

CHANGE_YAW									= 0xa017
PK_STATE_FIGHT_BACK_TIMER_CBID				= 0xa018		# pk����״̬����ʱ�������

#moveTrap
DELAY_DESTROY_SELF_TIMER_CBID				= 0xa019	# �ӳ�����timer

# ����
ROLE_ITEM_BAG_SAVE_LATER					= 0xa020	# ���������ӳ�д���ݿ�

#Buff_299004
FLAME_WAY_TIMER_CBID						= 0xa021	# ����·������timer

# �����ֻظ���
AUTO_THROW_SIEVE_TIMER_CBID					= 0xa022	# ϵͳ��ɸ��timer
WAIT_ROLE_REVIVE_PRE_SPACE_CBID				= 0xa023	# ͨ��ʧ�ܴ����̽���timer
ROLE_UESE_LIVE_POINT_REVIE_CBID				= 0xa024	# �ؿ���ʹ�ø�����Զ�����timer

DELAY_LINE_TO_POINT_TIMER_CBID				= 0xa025	# �ӳ��˶�timer
CALL_BLEW_MONSTER_CBID						= 0xa026	# �ٻ��Ա�����timer

# ����ʱ��
UPDATE_CLIENT_DANCING_KING_INFOS_CBID		= 0xa027	# ����������������Ϣ
DANCECHELLENGETIMER							= 0xa028    # ��ս����6����ʱ������
DANCETIMEOUTTIMER 							= 0xa02b	# ��ͨλ�þ����8��Сʱ��
DANCEKINGTIMEOUTTIMER						= 0xa02c	# ����λ�þ����8��Сʱ��

#��ӪӢ������
ENTER_CAMP_YING_XIONG_COPY					= 0xa029	# ��ӪӢ���������뵹��ʱ
READY_CAMP_YING_XIONG_COPY					= 0xa02a	# ��ӪӢ������׼������ʱ

# ���ظ���
COPY_FANG_SHOU_CHECK_ROLE_POSITION_CBID		= 0xa100	# ���ظ�������ɫλ��timer



#
# ȫ��Callback�ֵ䣬������ָ����ID��ѯ�ص�����
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

	# �ƺ�( wsf )
	TITLE_TIMER_CBID						: "onTitleAddTimer",

	CALL_MONSTER_FOR_108_CBID				: "callMonster",
	ACTIVITY_MONSTER_DISAPPEAR_CBID			: "disappear",

	# ����ʯϵͳ( wsf )
	GEM_ROLE_TIME_LIMIT_CBID				: "onRoleGemTimeLimit",
	GEM_PET_TIME_LIMIT_CBID					: "onPetGemTimeLimit",

	AUTO_TALK_CBID							: "onAutoTalk",
	ADD_NEW_QUEST_CBID						: "onAutoAddNewQuest",

	# �ھ���Ϣ����
	QUERY_DART_MESSAGE_CBID					: "onQueryDartMessage",
	QUEST_DART_ACTIVITY_START_CBID			: "onDartActivityStart",
	QUEST_DART_ACTIVITY_END_CBID			: "onDartActivityEnd",
	FLY_TO_MASTER_CB						: "flyToMasterCB",

	#����
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
# BigWorld.Entity��Callback��չ��ECBExtend
#
# ע��: ��Class���ܱ�����ʵ������ֻ����BigWorld.Entityͬʱ��ConcreteEntity��̳в�������
#
class ECBExtend:
	#
	# ����: ��ʼ��
	# ����:
	# ����: ���ܱ�����ʵ����
	#
	def __init__( self ):
		pass

	#
	# ����: ʵ��BigWorld.Entity.onTimer����ĳ��Timer Tick����ʱ������
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       timerID			timer��ID
	#       cbID			Callback ID
	# ����:
	#
	def onTimer( self, timerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
			#cb( timerID, cbID )	# phw���Ƶ�����
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke, self )		# ����һ������������ͣ����ڿ�ݲ��ҵ��ô˺����Ķ���
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		# phw: ����������������Ϊ��������������Ҳ���������KeyError��AttributeError�쳣����
		# ���������������ʱ���ײ���
		cb( timerID, cbID )

	#
	# ����: ʵ��BigWorld.Entity.onTurn����ĳ��addYawRotator�������ʱ����
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       controllerID	addYawRotator���ص�controllerID
	#       cbID			Callback ID
	# ����:
	#
	def onTurn( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		cb( controllerID, cbID )

	#
	# ����: ʵ��BigWorld.Entity.onMove����ĳ��moveToPoint����moveToEntity����Ŀ��λ��ʱ����
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       controllerID	moveToPoint����moveToEntity���ص�controllerID
	#       cbID			Callback ID
	# ����:
	#
	def onMove( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onMoveTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, True )

	#
	# ����: ʵ��BigWorld.Entity.onMoveFailure����ĳ��moveToPoint����moveToEntity�޷�����Ŀ��λ��ʱ����
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       controllerID	moveToPoint����moveToEntity���ص�controllerID
	#       cbID			Callback ID
	# ����:
	#
	def onMoveFailure( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onMoveTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, False )

	#
	# ����: ʵ��BigWorld.Entity.onNavigate����ĳ��navigate����Ŀ��λ��ʱ����
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       controllerID	navigate���ص�controllerID
	#       cbID			Callback ID
	# ����:
	#
	def onNavigate( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
			WARNING_MSG( "ECBCallback hasnt implement for ", ae )
			return
		if BigWorld.time() - self.queryTemp( "onNavigateTime", 0 ) < 0.05:
			WARNING_MSG( "ECBCallback be called continuously! %i"%self.id )
			return
		self.setTemp( "onMoveTime", BigWorld.time() )
		cb( controllerID, cbID, True )

	#
	# ����: ʵ��BigWorld.Entity.onNavigateFailure����ĳ��navigate�޷�����Ŀ��λ��ʱ����
	#       ת���cbID��Ӧ�Ļص�����
	# ����:
	#       controllerID	navigate���ص�controllerID
	#       cbID			Callback ID
	# ����:
	#
	def onNavigateFailed( self, controllerID, cbID ):
		global gcbs
		try:
			cbname = gcbs[cbID]
			cb = getattr( self, cbname )
		except KeyError, ke:
			# gcbs������cbID
			WARNING_MSG( "ECBCallback cant found call back for CBID ", ke )
			return
		except AttributeError, ae:
			# self entityû��ʵ�ֶ�Ӧ�Ļص�����
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
