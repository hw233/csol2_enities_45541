# -*- coding: gb18030 -*-

import csstatus
import csdefine
import csconst
from bwdebug import *
from FuncEnterDeffInterface import FuncEnterDeffCPInterface

class FuncDuDuzhu( FuncEnterDeffCPInterface ):
	"""
	进入嘟嘟猪
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_PIG
		self.memberDis = section["param4"].asFloat				# 队伍成员距离

	def setMemberFlags( self, member ):
		"""
		往进入entity身上写数据
		"""
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
		member.setTemp( "EnterSpaceDuDuZhu", self.enterType )

	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )

		if self.repLevel > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.DUDUZHU_FORBID_LEVEL, self.repLevel )
			return
			
		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.TALK_FORBID_TEAM )
			return
		
		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_DU_DU_ZHU, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			
			if not self.checkTeamMembers( player ):
				return
				
			# 判断是否队伍成员都在
			teamMemberIDs = player.getAllIDNotInRange( self.memberDis )
			if len( teamMemberIDs ) > 0:	# 如果队伍中有同志没在范围内
				for id in teamMemberIDs:
					player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
				return
		
			pList = player.getAllMemberInRange( self.memberDis )
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_DU_DU_ZHU ) :
					enteredMembersStr += ( i.getName() + "," )
					
			if lowLevelMembersStr != "":
				# 队伍中有人级别不够
				player.statusMessage( csstatus.DUDUZHU_FORBID_MEMBER_LEVEL_LESS, lowLevelMembersStr, self.repLevel )
				return
				
			if enteredMembersStr != "":
				# 队伍中有人已经参加嘟嘟猪活动
				player.statusMessage( csstatus.SPACE_COPY_HAS_ENTERED, enteredMembersStr )
				return
				
			for i in pList:
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncDuDuzhuEasy( FuncDuDuzhu ):
	# 进入嘟嘟猪简单模式
	def __init__( self, section ):
		FuncDuDuzhu.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncDuDuzhuDifficulty( FuncDuDuzhu ):
	# 进入神嘟嘟猪困难模式
	def __init__( self, section ):
		FuncDuDuzhu.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncDuDuzhuNightmare( FuncDuDuzhu ):
	# 进入嘟嘟猪噩梦模式
	def __init__( self, section ):
		FuncDuDuzhu.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE