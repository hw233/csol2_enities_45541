# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyTeam.py,v 1.2 2008-08-01 03:31:46 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import Const
import ECBExtend
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyTeam( SpaceCopy ):
	"""
	用于匹配SpaceDomainCopyTeam的基础类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )
		
	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		if entity.teamMailbox:
			return csstatus.SPACE_OK
		else:
			return csstatus.SPACE_MISS_NOTTEAM
		
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		d = SpaceCopy.packedDomainData( self, entity )
		if entity.teamMailbox:
			# 已加入队伍，取队伍数据
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["spaceKey"] = entity.teamMailbox.id
		return d
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		队伍解散
		"""
		selfEntity.addTimer( 1.0, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
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