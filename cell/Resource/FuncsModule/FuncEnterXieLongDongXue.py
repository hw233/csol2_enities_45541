# -*- coding: gb18030 -*-
"""
进入邪龙洞穴副本
"""
from bwdebug import *
import random
import math
import csstatus
import csdefine
import csconst
import BigWorld

import Const
from FuncEnterDeffInterface import FuncEnterDeffCPInterface

ENTERN_XLDX_MENBER_DISTANCE = 30.0

class FuncEnterXieLongDongXue( FuncEnterDeffCPInterface ):
	"""
	进入邪龙洞穴副本
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_XIE_LONG_DONG_XUE
	
	def setMemberFlags( self, member ):
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
		member.setTemp( "EnterSpaceXieLongType", self.enterType )
	
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
			
		if self.repLevel > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.XLDX_LEVEL_NOT_ARRIVE, self.repLevel )
			return
			
		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.XLDX_NEED_TEAM )
			return

		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_XIE_LONG, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			pList = player.getAllMemberInRange( ENTERN_XLDX_MENBER_DISTANCE )
			
			if not self.checkTeamMembers( player ):
				return
				
			# 判断是否队伍成员都在
			teamMemberIDs = player.getAllIDNotInRange( ENTERN_XLDX_MENBER_DISTANCE )
			if len( teamMemberIDs ) > 0:	# 如果队伍中有同志没在范围内
				for id in teamMemberIDs:
					player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
				return
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_XIE_LONG ) :
					enteredMembersStr += ( i.getName() + "," )
					
			if lowLevelMembersStr != "":
				# 队伍中有人级别不够
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_XLDX_LEVEL, lowLevelMembersStr, self.repLevel )
				return
			if enteredMembersStr != "":
				# 队伍中有人已经参加过邪龙洞穴活动
				player.statusMessage( csstatus.XLDX_HAS_ENTERED_TODAY, enteredMembersStr )
				return
				
			for i in pList:
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.position, self.direction )
			
class FuncEnterXieLongDongXueEasy( FuncEnterXieLongDongXue ):
	# 进入神鬼秘境简单模式
	def __init__( self, section ):
		FuncEnterXieLongDongXue.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterXieLongDongXueDefficulty( FuncEnterXieLongDongXue ):
	# 进入神鬼秘境困难模式
	def __init__( self, section ):
		FuncEnterXieLongDongXue.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterXieLongDongXueNightmare( FuncEnterXieLongDongXue ):
	# 进入神鬼秘境噩梦模式
	def __init__( self, section ):
		FuncEnterXieLongDongXue.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE