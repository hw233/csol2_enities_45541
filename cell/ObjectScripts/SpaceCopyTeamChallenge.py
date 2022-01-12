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

CLEAR_NO_FIGHT		  = 4	# 清除免战效果
CLOSE_TEAM_CHALLENGE  = 5   # 关闭组队擂台

class SpaceCopyTeamChallenge( SpaceCopyTeam ):
	"""
	组队擂台副本空间
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )

		# 进入者最小级别限制
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt


	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		return { 'roleDBID' : entity.databaseID, "level": entity.level, "teamID": entity.teamMailbox.id, "playerName":entity.playerName}

	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		if entity.level < self.enterLimitLevel:
			return csstatus.TEAM_CHALLENGE_NO_WAR_LEVEL

		return csstatus.SPACE_OK

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		packDict[ "teamID" ] = entity.teamMailbox.id
		packDict[ "level" ] =  entity.level
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		# 打包玩家离开的数
		packDict = SpaceCopyTeam.packedSpaceDataOnLeave( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		packDict[ "teamID" ] = entity.teamMailbox.id
		packDict[ "state" ] =  entity.getState()
		packDict[ "isWatchState" ] =  entity.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		playerDBID = params[ "playerDBID" ]
		teamID = params[ "teamID" ]
		level = params[ "level" ]
		if teamID not in selfEntity.teamChallengeInfos.infos.keys():
			BigWorld.globalData[ "TeamChallengeTempID_%i" % teamID ] = self._getStep( level )

		selfEntity.teamChallengeInfos.add( teamID, playerDBID, baseMailbox )
		self._notifyPlayerNum( selfEntity )

		baseMailbox.cell.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# 进入组队擂台，免战
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )		# 设置为和平模式
		baseMailbox.cell.lockPkMode()										# 锁定pk模式，不能设置

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.hasClearNoFight:		# 如果没有清除过角色的免战效果
			baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )

		if params[ "state" ] == csdefine.ENTITY_STATE_DEAD:
			baseMailbox.cell.reviveActivity() # 空血空蓝复活

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

		if not selfEntity.hasClearNoFight: # 如果是比赛还没开始，则不做下面的判断
			return

		if selfEntity.queryTemp( "challengeIsClose" ): # 如果比赛结束了则不作下面的判断
			return

		self.onChangeChallengeInfos( selfEntity, baseMailbox, teamID, playerDBID )

	def clearNoFight( self, selfEntity ):
		"""
		清除免战
		"""
		for e in  selfEntity._players:
			# 设置PK模式
			e.cell.lockPkMode()
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
			# 清除免战
			e.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
			# 广播玩家开打
			e.client.onStatusMessage( csstatus.WU_DAO_CLEAR_NO_FIGHT, "" )

		selfEntity.hasClearNoFight = True		# 标记已经清除过角色的免战效果

	def onRoleIsFailed( self, selfEntity, baseMailBox, teamID, dbid ):
		"""
		玩家死亡
		"""
		selfEntity.teamChallengeInfos.remove( teamID, dbid )
		self._notifyPlayerNum( selfEntity )
		self.onChangeChallengeInfos( selfEntity, baseMailBox, teamID, dbid )

	def onLeaveTeam( self, playerEntity ):
		# 离开队伍回调
		playerEntity.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def closeSpace( self, selfEntity ):
		"""
		出副本，关闭当前副本
		"""
		selfEntity.setTemp( "challengeIsClose", True )		# 设置已经关闭组队擂台

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

		某role在该副本中死亡
		"""
		if not killer:	# 没找到杀人者，非正常死亡不处理，直接返回
			DEBUG_MSG( "player( %s ) has been killed,can't find killer." % role.getName() )
			return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.getState() == csdefine.ENTITY_STATE_DEAD:		# 如果杀人者已经死亡，则返回
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
		# 把玩家从擂台信息中移除
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

				selfEntity.addTimer( 10, 0, CLOSE_TEAM_CHALLENGE )		# 10秒后调用claseWuDao

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