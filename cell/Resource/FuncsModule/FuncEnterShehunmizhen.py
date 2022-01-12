# -*- coding: gb18030 -*-

from bwdebug import *
import csstatus
import csdefine
import csconst
from FuncEnterDeffInterface import FuncEnterDeffCPInterface

ENTER_SHMZ_MENBER_DISTANCE = 30.0

class FuncEnterShehunmizhen( FuncEnterDeffCPInterface ):
	"""
	进入摄魂迷阵副本
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN

	def setMemberFlags( self, member ):
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
	
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
		#玩家等级不够
		if self.repLevel > player.level:
			player.statusMessage( csstatus.SHMZ_LEVEL_NOT_ARRIVE, self.repLevel )
			return
		
		#玩家没有组队
		if not player.isInTeam():
			player.statusMessage( csstatus.SHMZ_NEED_TEAM )
			return

		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_SHE_HUN_MI_ZHEN, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			pList = player.getAllMemberInRange( ENTER_SHMZ_MENBER_DISTANCE )
			
			if not self.checkTeamMembers( player ):
				return 
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHE_HUN_MI_ZHEN ) :
					enteredMembersStr += ( i.getName() + "," )
					
			if lowLevelMembersStr != "":
				# 队伍中有人级别不够
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_SHMZ_LEVEL, lowLevelMembersStr, self.repLevel )
				return
			if enteredMembersStr != "":
				# 队伍中有人已经参加过封剑神宫活动
				player.statusMessage( csstatus.SHMZ_HAS_ENTERED_TODAY, enteredMembersStr )
				return
			pList.remove( player )
			player.gotoSpace( self.spaceName, self.position, self.direction )
			for i in pList:
				self.setMemberFlags( i )
				i.set( "lastSHMZTeamID", player.getTeamMailbox().id )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterShehunmizhenEasy( FuncEnterShehunmizhen ):
	# 进入摄魂迷阵简单模式
	def __init__( self, section ):
		FuncEnterShehunmizhen.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterShehunmizhenDefficulty( FuncEnterShehunmizhen ):
	# 进入摄魂迷阵困难模式
	def __init__( self, section ):
		FuncEnterShehunmizhen.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterShehunmizhenNightmare( FuncEnterShehunmizhen ):
	# 进入摄魂迷阵噩梦模式
	def __init__( self, section ):
		FuncEnterShehunmizhen.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE
