# -*- coding: gb18030 -*-

import cschannel_msgs
import csstatus
import csconst
import Const
import time
import csdefine
import BigWorld
from SpaceCopyTeam import SpaceCopyTeam

CLOSE_DU_DU_ZHU = 1003
SPACE_LIFE_END_KICK_PLAYER_TIME = 30		# ����ʱ�䵽�����ұ�ǿ�ƴ�����ʱ�䣨�룩
SPACE_SUCCESS_KICK_PLAYER_TIME = 90		# Boss��������ұ�ǿ�ƴ�����ʱ�䣨�룩

class SpaceCopyPig( SpaceCopyTeam ):
	"""
	������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		self.recordKey = "duduzhu_record"
		self._spaceLife = 1
		self.bossIDs = []

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyTeam.load( self, section )
		self._spaceLife = section[ "Space" ][ "spaceLife" ].asInt 			# ����ʱ��(����)
		self.bossIDs = section[ "Space" ][ "bossID" ].asString.split(";")	# ������BossIDs

	def packedDomainData( self, player ):
		"""
		"""
		data = SpaceCopyTeam.packedDomainData( self, player )
		
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = player.level
		data["copyLevel"] = level
		data["difficulty"] = player.popTemp( "EnterSpaceDuDuZhu", 0 )
		data["spaceLabel"] = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		data["position"] = 	player.position

		return data

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		# �������ͳ��
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_DU_DU_ZHU, self.recordKey )
		
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		
		# ��һ�ν��븱��
		if not selfEntity.queryTemp( "tempHaveCome", False ):
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.base.spawnMonsters( { "level": selfEntity.params["copyLevel"] } )
			selfEntity.setTemp( "copyStartTime", time.time() )	# ������ʼʱ��
			selfEntity.setTemp( "SPACE_KICK_PLAYER_TIME", SPACE_LIFE_END_KICK_PLAYER_TIME  )
			selfEntity.addTimer( self._spaceLife * 60 - SPACE_LIFE_END_KICK_PLAYER_TIME, 0, CLOSE_DU_DU_ZHU )

		# ��������ʹ��
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, self._spaceLife * 60 )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, className ):
		"""
		���ݲ�ͬ��className����ͬ��������
		"""
		
		if className in self.bossIDs: 
			bossCount = selfEntity.queryTemp( "bossCount" ) - 1
			selfEntity.setTemp( "bossCount", bossCount )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, bossCount )
			if bossCount <= 0: # Boss����,�����ر�
				selfEntity.setTemp( "SPACE_KICK_PLAYER_TIME", SPACE_SUCCESS_KICK_PLAYER_TIME )
				self.closeSpace( selfEntity )
		else:
			allMonsterCount = selfEntity.queryTemp( "allMonsterCount" ) - 1 
			selfEntity.setTemp( "allMonsterCount", allMonsterCount )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, allMonsterCount )
			if allMonsterCount == 0: # С��ȫ��������ˢBoss
				selfEntity.base.spawnMonsters( { "bossIDs": self.bossIDs, "level": selfEntity.params["copyLevel"] } )
				self.broadcastInCopy( selfEntity, cschannel_msgs.BCT_DUDUZHU_BOSS_NOTIFY )

	def broadcastInCopy( self, selfEntity, msg ):
		"""
		�����й㲥
		"""
		for baseMailBox in selfEntity._players:
			baseMailBox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, [] )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		if userArg == CLOSE_DU_DU_ZHU:
			self.closeSpace( selfEntity )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )

	def closeSpace( self, selfEntity ):
		"""
		�رո���
		"""
		closeTime = selfEntity.queryTemp( "SPACE_KICK_PLAYER_TIME", 10 )
		for e in selfEntity._players:
			e.client.onStatusMessage( csstatus.SPACE_CLOSE, str( ( closeTime, ) ) )
		
		selfEntity.addTimer( closeTime, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( closeTime + 5, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
