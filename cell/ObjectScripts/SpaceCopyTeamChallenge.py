# -*- coding: gb18030 -*-
#
#$Id:$

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
import Const
from SpaceCopyTeam import SpaceCopyTeam

CLEAR_NO_FIGHT		  = 4	# �����սЧ��
CLOSE_TEAM_CHALLENGE  = 5   # �ر������̨

class SpaceCopyTeamChallenge( SpaceCopyTeam ):
	"""
	�����̨�����ռ�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )

		# ��������С��������
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt


	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		return { 'roleDBID' : entity.databaseID, "level": entity.level, "teamID": entity.teamMailbox.id, "playerName":entity.playerName}

	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		if entity.level < self.enterLimitLevel:
			return csstatus.TEAM_CHALLENGE_NO_WAR_LEVEL

		return csstatus.SPACE_OK

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		packDict[ "teamID" ] = entity.teamMailbox.id
		packDict[ "level" ] =  entity.level
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		# �������뿪����
		packDict = SpaceCopyTeam.packedSpaceDataOnLeave( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		packDict[ "teamID" ] = entity.teamMailbox.id
		packDict[ "state" ] =  entity.getState()
		packDict[ "isWatchState" ] =  entity.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
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
		playerDBID = params[ "playerDBID" ]
		teamID = params[ "teamID" ]
		level = params[ "level" ]
		if teamID not in selfEntity.teamChallengeInfos.infos.keys():
			BigWorld.globalData[ "TeamChallengeTempID_%i" % teamID ] = self._getStep( level )

		selfEntity.teamChallengeInfos.add( teamID, playerDBID, baseMailbox )
		self._notifyPlayerNum( selfEntity )

		baseMailbox.cell.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# ���������̨����ս
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )		# ����Ϊ��ƽģʽ
		baseMailbox.cell.lockPkMode()										# ����pkģʽ����������

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.hasClearNoFight:		# ���û���������ɫ����սЧ��
			baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )

		if params[ "state" ] == csdefine.ENTITY_STATE_DEAD:
			baseMailbox.cell.reviveActivity() # ��Ѫ��������

		if params[ "isWatchState" ] :
			baseMailbox.cell.onLeaveWatchMode()

		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.setSysPKMode( 0 )
		playerDBID = params[ "playerDBID" ]
		teamID = params[ "teamID" ]
		if not teamID:
			teamID = selfEntity.teamChallengeInfos.findTeamID( playerDBID )

		selfEntity.teamChallengeInfos.remove( teamID, playerDBID )
		self._notifyPlayerNum( selfEntity )

		if not selfEntity.hasClearNoFight: # ����Ǳ�����û��ʼ������������ж�
			return

		if selfEntity.queryTemp( "challengeIsClose" ): # �����������������������ж�
			return

		self.onChangeChallengeInfos( selfEntity, baseMailbox, teamID, playerDBID )

	def clearNoFight( self, selfEntity ):
		"""
		�����ս
		"""
		for e in  selfEntity._players:
			# ����PKģʽ
			e.cell.lockPkMode()
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
			# �����ս
			e.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
			# �㲥��ҿ���
			e.client.onStatusMessage( csstatus.WU_DAO_CLEAR_NO_FIGHT, "" )

		selfEntity.hasClearNoFight = True		# ����Ѿ��������ɫ����սЧ��

	def onRoleIsFailed( self, selfEntity, baseMailBox, teamID, dbid ):
		"""
		�������
		"""
		selfEntity.teamChallengeInfos.remove( teamID, dbid )
		self._notifyPlayerNum( selfEntity )
		self.onChangeChallengeInfos( selfEntity, baseMailBox, teamID, dbid )

	def onLeaveTeam( self, playerEntity ):
		# �뿪����ص�
		playerEntity.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def closeSpace( self, selfEntity ):
		"""
		���������رյ�ǰ����
		"""
		selfEntity.setTemp( "challengeIsClose", True )		# �����Ѿ��ر������̨

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )
			else:
				e.cell.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_TEAM_CHALLENGE:
			self.closeSpace( selfEntity )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		if not killer:	# û�ҵ�ɱ���ߣ�����������������ֱ�ӷ���
			DEBUG_MSG( "player( %s ) has been killed,can't find killer." % role.getName() )
			return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.getState() == csdefine.ENTITY_STATE_DEAD:		# ���ɱ�����Ѿ��������򷵻�
			return

		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			spaceBase = role.getCurrentSpaceBase()
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				self.onRoleIsFailed( spaceEntity, role.base, role.teamMailbox.id, role.databaseID )
			else:
				spaceBase.cell.remoteScriptCall( "onRoleIsFailed", ( role.base, role.teamMailbox.id, role.databaseID ) )

		#role.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def _getStep( self, level ):
		if level >= csconst.TEAM_CHALLENGE_JOIN_LEVEL_MIN and level <= csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX:
			if level == csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX:
				return level / 10 - 1
			else:
				return level / 10
		else:
			return 0

	def onChangeChallengeInfos( self, selfEntity, baseMailBox, teamID, dbid ):
		# define method
		# ����Ҵ���̨��Ϣ���Ƴ�
		if len( selfEntity.teamChallengeInfos[ teamID ] ) == 0:
			teamIDs = selfEntity.teamChallengeInfos.infos.keys()
			teamIDs.remove( teamID )
			if len( teamIDs ) == 1:
				winTID = teamIDs[0]
				if len( selfEntity.teamChallengeInfos[ winTID ] ) == 0:
					return

				BigWorld.globalData[ "TeamChallengeMgr" ].teamWin( winTID )

				for e in selfEntity._players:
					e.client.onStatusMessage( csstatus.TEAM_CHALLENGE_COMPLETE, "" )

				selfEntity.addTimer( 10, 0, CLOSE_TEAM_CHALLENGE )		# 10������claseWuDao

	def _notifyPlayerNum( self, selfEntity ):
		teamIDs = selfEntity.teamChallengeInfos.infos.keys()
		teamID = teamIDs[0]
		lNum = len( selfEntity.teamChallengeInfos[ teamID ] )
		rNum = 0

		if len( teamIDs ) == 2:
			teamIDs.remove( teamID )
			rTeamID = teamIDs[0]
			rNum = len( selfEntity.teamChallengeInfos[ rTeamID ] )
			for dbid in selfEntity.teamChallengeInfos[ rTeamID ]:
				selfEntity.teamChallengeInfos.dbidToMailBox[ dbid ].client.teamChallengeMember( rNum, lNum )

			rTeamWatchList = selfEntity.queryTemp( rTeamID, [] )
			for mb in rTeamWatchList:
				mb.client.teamChallengeMember( rNum, lNum )

		for dbid in selfEntity.teamChallengeInfos[ teamID ]:
			selfEntity.teamChallengeInfos.dbidToMailBox[ dbid ].client.teamChallengeMember( lNum, rNum )

			lTeamWatchList = selfEntity.queryTemp( teamID, [] )
			for mb in lTeamWatchList:
				mb.client.teamChallengeMember( lNum, rNum )