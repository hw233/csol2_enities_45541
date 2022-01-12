# -*- coding: gb18030 -*-
#python
import time
#bigworld
import BigWorld
#cell
import Const
#common
from bwdebug import INFO_MSG,ERROR_MSG,print_stack
import csdefine
import csstatus
import csconst

from SpaceCopy import SpaceCopy

# ս������Ӫ���졢�ء���
FACTION_TIAN					= csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN
FACTION_DI						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI
FACTION_REN						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN

#
TIMER_FACTION_ENRAGE			= 1
TIMER_CAN_ALLIANCE				= 2
TIMER_FACTION_FLAG_ADD_INTEGRAL = 3
TIMER_ALLIANCCE_END				= 4
TIMER_SPAWN_YI_JIE_STONE		= 5

FACTION_NAME = { FACTION_TIAN : "��", FACTION_DI : "��", FACTION_REN : "��" }
FACTION_FLAG_ADD_INTEGRAL_TIME_PERIOD = 60
FACTION_FLAG_ADD_INTEGRAL_VALUE		  = 1
ALLIANCE_LENGTH_OF_TIME				  = 600
ACTIVITY_LAST_TIME					  = 3600
SPAWN_YI_JIE_STONE_TIME				  = 300

class SpaceCopyYiJieZhanChang( SpaceCopy ):
	# ���ս��
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.battlegroundMgr.playerMaxRage = self.getScript().maxRage	# ���ŭ�������ֵ������ר��
		self.battlegroundMgr.spaceID = self.spaceID
		self.factionFlagTimerInfos = {}			# ��¼��Ӫ����ռ��ʱ����Ϣ { entityID : (TimerID,faction) }
		self.addTimer( self.getScript().canAllianceTime, 0, TIMER_CAN_ALLIANCE )
		self.addTimer( SPAWN_YI_JIE_STONE_TIME, 0, TIMER_SPAWN_YI_JIE_STONE )
		self.__initSpaceData()

# ----------------------------------------------------------------
# �·���
# ----------------------------------------------------------------

	def __initSpaceData( self ) :
		"""
		��ʼ���ռ�����
		"""
		spaceID = self.spaceID
		startTime = time.time()
		if BigWorld.globalData.has_key( "YiJieZhanChang_StartTime" ) :
			startTime = BigWorld.globalData["YiJieZhanChang_StartTime"]
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_START_TIME, startTime )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, ACTIVITY_LAST_TIME )
		
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_TIAN, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_TIAN, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_DI, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_DI, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_REN, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_REN, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_ANGER_FACTION, 0 )
		BigWorld.setSpaceData( spaceID, csconst.SPACE_SPACEDATA_YIJIE_ALLIANCE_FACTIONS, () )

	def closeActivity( self, reason ):
		"""
		<define method>
		�رջ
		"""
		roleInfos = self.battlegroundMgr.rankOnCloseActivity()
		for offlineMember in self.battlegroundMgr.offlineMembers.itervalues() :
			BigWorld.globalData["YiJieZhanChangMgr"].addNeedShowYiJieScorePlayer( offlineMember.databaseID, roleInfos )
		
		if reason == csdefine.YI_JIE_CLOSE_REASON_TIME_END:
			for e in self._players:
				e.cell.yiJieCloseActivity( roleInfos )
				e.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_TIME_END, "" )
		elif reason == csdefine.YI_JIE_CLOSE_REASON_ONE_FACTION_WIN:
			for e in self._players:
				e.cell.yiJieCloseActivity( roleInfos )
				e.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_ONE_FACTION_WIN, "" )
		
		self.addTimer( self.getScript().closeTime, 0, Const.SPACE_TIMER_ARG_KICK )
		self.addTimer( self.getScript().closeTime + 5, 5, Const.SPACE_TIMER_ARG_CLOSE )
	
	def onRoleBeKill( self, pos, deadDBID, killerDBID, killerType ):
		"""
		define method
		����ұ���ɱ
		"""
		if killerType != csdefine.ENTITY_TYPE_ROLE :
			return
		
		self.battlegroundMgr.onKill( deadDBID, killerDBID )
		self.__updateWeakestFaction()
		if self.battlegroundMgr.canAlliance and self.battlegroundMgr.checkAllianceConditions() :
			self.battlegroundMgr.beginAlliance()
			self.addTimer( ALLIANCE_LENGTH_OF_TIME, 0, TIMER_ALLIANCCE_END )
	
	def __updateWeakestFaction( self ) :
		"""
		"""
		mgr = self.battlegroundMgr
		differenceTian	= mgr.factions[ FACTION_TIAN ].kill - mgr.factions[ FACTION_TIAN ].beKill
		differenceDi	= mgr.factions[ FACTION_DI ].kill - mgr.factions[ FACTION_DI ].beKill
		differenceRen	= mgr.factions[ FACTION_REN ].kill - mgr.factions[ FACTION_REN ].beKill
		differences = [ ( differenceTian, FACTION_TIAN ), ( differenceDi, FACTION_DI ), ( differenceRen, FACTION_REN ) ]
		differences.sort( None,lambda x : x[0] )
		if differences[0][0] < differences[1][0] and differences[0][0] < differences[2][0] :
			faction = differences[0][1]
			if mgr.weakestFaction != faction :
				if 	mgr.weakestFaction and mgr.factions[ mgr.weakestFaction ].enrage :
					mgr.enrage( False )
				mgr.weakestFaction = faction
				if mgr.enrageTimerID != 0 :
					self.cancel( mgr.enrageTimerID )
					mgr.enrageTimerID = 0
				mgr.enrageTimerID = self.addTimer( self.getScript().enrageTime, 0, TIMER_FACTION_ENRAGE )
	
	def playerExit( self, playerDBID ):
		"""
		<define method>
		����˳�
		"""
		self.battlegroundMgr.deleteMember( playerDBID )
		BigWorld.globalData["YiJieZhanChangMgr"].onPlayerLeaveBattleground( playerDBID, self.spaceNumber )
	
	def onRoleRevive( self, playerDBID ) :
		"""
		<define method>
		�����վ���ڸ�������
		"""
		self.battlegroundMgr.checkPlayerRage( playerDBID )
	
	def onPlayerUseUniqueSpell( self, playerDBID ) :
		"""
		<define method>
		�����˫��ʹ�óɹ��ص�
		"""
		self.battlegroundMgr.resetPlayerRage( playerDBID )
	
	def onPlayerRequestUniqueSpell( self, playerDBID ) :
		"""
		<define method>
		��������ͷ���˫��
		"""
		self.battlegroundMgr.onPlayerRequestUniqueSpell( playerDBID )
	
	def onOccupyFactionFlag( self, factionFlagID, newFaction ) :
		"""
		<define method>
		��Ӫ����ռ��ʱ����
		"""
		if self.factionFlagTimerInfos.has_key( factionFlagID ) :
			timerID = self.factionFlagTimerInfos[ factionFlagID ][0]
			self.cancel( timerID )
		timerID = self.addTimer( FACTION_FLAG_ADD_INTEGRAL_TIME_PERIOD, FACTION_FLAG_ADD_INTEGRAL_TIME_PERIOD, TIMER_FACTION_FLAG_ADD_INTEGRAL )
		self.factionFlagTimerInfos[ factionFlagID ] = ( timerID, newFaction )
		self.battlegroundMgr.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_OCCUPY_FACTION_FLAG, FACTION_NAME[ newFaction ] )
	

# ----------------------------------------------------------------
# ���ط���
# ----------------------------------------------------------------
	def onEnterCommon( self, baseMailbox, params ) :
		"""
		�������ķ�ʽ���븱��
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		self.battlegroundMgr.onEnterCopy( baseMailbox,params )
	
	def onLeaveCommon( self, baseMailbox, params ) :
		"""
		�������ķ�ʽ�뿪����
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		self.battlegroundMgr.onLeaveCopy( params["databaseID"] )
	
	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		�˽ӿ�����֪ͨ��ɫ���ص�ͼ��ϣ������ƶ��ˣ�����������������Ϸ���ݽ�����
		@param baseMailbox: Ҫ�����space��entity mailbox
		"""
		SpaceCopy.onTeleportReady( self, baseMailbox )
		baseMailbox.client.yiJieOnTeleportReady()
	

	def onTimer( self, timerID, userArg ) :
		if userArg == TIMER_FACTION_ENRAGE :				# ��Ӫ��ŭ
			self.battlegroundMgr.enrage( True )
		elif userArg == TIMER_CAN_ALLIANCE :				# ���Կ�ʼ����
			self.battlegroundMgr.canAlliance = True
			if self.battlegroundMgr.checkAllianceConditions() :
				self.battlegroundMgr.beginAlliance()
				self.addTimer( ALLIANCE_LENGTH_OF_TIME, 0, TIMER_ALLIANCCE_END )
		elif userArg == TIMER_FACTION_FLAG_ADD_INTEGRAL :	# ��Ӫ��������Ӫ����
			for id,faction in self.factionFlagTimerInfos.itervalues() :
				if id == timerID :
					self.battlegroundMgr.addFactionIntegral( faction, FACTION_FLAG_ADD_INTEGRAL_VALUE )
		elif userArg == TIMER_ALLIANCCE_END :				# ����ͬ��
			self.battlegroundMgr.endAlliance()
		elif userArg == TIMER_SPAWN_YI_JIE_STONE :			# ��ʼˢ�����ʯ
			self.base.spawnYiJieStone()
		elif userArg == Const.SPACE_TIMER_ARG_CLOSE:
			if len( self._players ) > 0 :
				return
			self.base.closeSpace( True )					# �رո���
			self.cancel( timerID )
		elif userArg == Const.SPACE_TIMER_ARG_KICK:
			self.getScript().kickAllPlayer( self )			# �߳��������������

