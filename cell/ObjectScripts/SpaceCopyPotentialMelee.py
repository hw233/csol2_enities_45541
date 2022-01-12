# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import csstatus
import csdefine
import random
import csconst
import Const
import ECBExtend
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
from Resource.CopyPotentialMeleeLoader import CopyPotentialMeleeLoader
from Resource.CopyPotentialMeleeLoader import BOSS_CLASS_NAME
g_config = CopyPotentialMeleeLoader.instance()

TIMER_SPACE_LIfE		= 40 * 60
TIMER_SPAWN_NEXT		= 30
TIMER_SPAWN_START		= 10

TIMER_ARG_NEXT_CONTENT		= 1
TIMER_ARG_CLOSE_SPACE		= 2


class SpaceCopyPotentialMelee( SpaceCopyTeam ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyTeam.load( self, section )
		point = section[ "Space" ][ "BossPoint" ]
		self.bossPoint = ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.addTimer( TIMER_SPACE_LIfE, 0, TIMER_ARG_CLOSE_SPACE )
		selfEntity.setTemp( "copyStartTime", time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, TIMER_SPACE_LIfE )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""
		if monsterClassName not in BOSS_CLASS_NAME:
			selfEntity.liveMonsterNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.liveMonsterNum )
		else:
			selfEntity.liveBossNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.liveBossNum  )
		
		selfEntity.checkDoPass()
				
	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == TIMER_ARG_CLOSE_SPACE:
			self.onOverMelee( selfEntity, True )
		
		elif userArg == TIMER_ARG_NEXT_CONTENT:
			if selfEntity.isLastBatch():
				return
				
			selfEntity.startNextBatch()
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.isTeamCaptain():
			packDict[ "teamLevel" ] = entity.level
			
		return packDict
						
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if params.has_key( "teamLevel" ):
			BigWorld.globalData['potentialMelee_%i' % selfEntity.params['dbID'] ] = True
			selfEntity.setTemp('globalkey','potentialMelee_%i' % selfEntity.params['dbID'] )
			
			selfEntity.base.spawnFlagEntity( { "level": params[ "teamLevel" ] } ) # ˢ����
			selfEntity.teamLevel = params[ "teamLevel" ]
			selfEntity.addTimer( TIMER_SPAWN_START, 0, TIMER_ARG_NEXT_CONTENT )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, g_config.getBatchTotal() )
			#BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, TIMER_SPAWN_START )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, g_config.getMonsterCount() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, g_config.getBossCount() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_POTENTIAL_FLAG_HP, 100 )
			baseMailbox.client.startCopyTime( TIMER_SPACE_LIfE- int( time.time() - selfEntity.queryTemp( "copyStartTime" ) ) )
			
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		֪ͨ������ ָ������Ϣ
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				p = BigWorld.entities[ e.id ]
				p.statusMessage( msgKey, *args )
			else:
				ERROR_MSG( "player %i not found" % e.id )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		SpaceCopyTeam.onLeaveTeam( self, playerEntity )
		playerEntity.getCurrentSpaceBase().cell.setLeaveTeamPlayerMB( playerEntity.base )
	
	def passBatch( self, selfEntity ):
		"""
		ͨ��
		"""
		if selfEntity.isLastBatch():
			self.onOverMelee( selfEntity, False )
		else:
			ntid = selfEntity.popTemp( "SPAWN_NEXT", 0 )
			if ntid:
				selfEntity.cancel( ntid )
				
		selfEntity.addTimer( 0, 0, TIMER_ARG_NEXT_CONTENT )

	def onFlagDie( self, selfEntity ):
		"""
		ʥ���챻�ݻ�
		"""
		selfEntity.addTimer( 10.0, 0, TIMER_ARG_CLOSE_SPACE )
		
	def onOverMelee( self, selfEntity, isTimeout ):
		"""
		�����
		"""
		if isTimeout:
			for e in selfEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].gotoForetime()
				else:
					e.cell.gotoForetime()
			
			# ��ʼ����ʱ30��رո���
			selfEntity.addTimer( 30, 0, Const.SPACE_TIMER_ARG_CLOSE  )
		else:
			#ˢNPC 10111201	�������� npcm0208_1
			elist = []
			for e in selfEntity._players:
				player = BigWorld.entities.get( e.id )
				if player is not None and player.spaceID == selfEntity.spaceID:
					elist.append( player.databaseID )
			
			DEBUG_MSG( "can get rewardPlayers:%s" % elist )
			dict = { "tempMapping" : { "playerLevel": selfEntity.teamLevel, "rewardPlayers" : elist } }
			selfEntity.createNPCObject( "10111201", self.bossPoint[0], self.bossPoint[1], dict ) 
			self.statusMessageAllPlayer( selfEntity, csstatus.POTENTIAL_MELEE_ALERT_OVER )