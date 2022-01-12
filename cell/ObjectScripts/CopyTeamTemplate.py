# -*- coding: gb18030 -*-

# ------------------------------------------------
# from common
import csstatus
# ------------------------------------------------
# from cell
import Const
import ECBExtend
# ------------------------------------------------

from CopyTemplate import CopyTemplate

class CopyTeamTemplate( CopyTemplate ):
	def __init__( self ):
		CopyTemplate.__init__( self )
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		CopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		CopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		d = CopyTemplate.packedDomainData( self, entity )
		if entity.teamMailbox:
			# 已加入队伍，取队伍数据
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
		return d
	
	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = CopyTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			packDict[ "teamID" ] = player.teamMailbox.id

		return packDict
	
	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		if entity.teamMailbox:
			return csstatus.SPACE_OK
		else:
			return csstatus.SPACE_MISS_NOTTEAM
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		队伍解散
		"""
		self.kickAllPlayer( selfEntity )
		selfEntity.addUserTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE_SPACE )
	
	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		playerEntity.gotoForetime()