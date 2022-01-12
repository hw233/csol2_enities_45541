# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import Const
import ECBExtend
from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps

TIMER_CLOSE_ACT = 1

class SpaceCopyMapsTeam( SpaceCopyMaps ):
	"""
	多地图组队副本脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyMaps.__init__( self )
		self._isPickMembers = 0
		
	def load( self, section ):
		SpaceCopyMaps.load( self, section )
		self._isPickMembers = section[ "Space" ][ "pickMembers" ].asInt
	
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		d = { 'dbID' : entity.databaseID }
		d[ "enterCopyKey" ] = self.className
		d[ "enterCopyNo" ] = self._spaceMapsNo
		d["teamID"] = entity.teamMailbox.id			#去掉是否有队伍的判断，如果没有队伍，就直接在这里报错。GRL
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
	
	def closeMapsCopy( self, playerEntity ):
		"""
		关闭多地图副本入口(玩家调用)
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
			
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.className, "closeCopyItem", ( { "teamID": playerEntity.teamMailbox.id } ) )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		if userArg == Const.SPACE_TIMER_ARG_LIFE:
			selfEntity.domainMB.closeCopyItem( { "teamID": selfEntity.copyKey } )
		else:
			SpaceCopyMaps.onTimer( self, selfEntity, id, userArg )
	
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