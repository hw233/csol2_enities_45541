# -*- coding: gb18030 -*-
from FuncTeleport import FuncTeleport
from bwdebug import *
import random
import math
import csstatus
import csdefine
import csconst
from FuncEnterDeffInterface import FuncEnterDeffCPInterface
import time
import BigWorld


RESTRICT_TEAM_NUM = 3  						# 进入队伍人数限制3人
ENTERN_SGMJ_MENBER_DISTANCE = 30.0			# 队伍距离
QUEST_WU_YAO_WANG_BAO_ZANG_ID = 40301003	# 巫妖王宝藏副本任务id

class FuncEnterWuYaoWangBaoZang( FuncEnterDeffCPInterface ):
	"""
	进入巫妖王宝藏副本
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_WU_YAO_WANG_BAO_ZANG
	
	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
		member.setTemp( "WuYaoWangEnterType", self.enterType )
	
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
		
		if player.level < self.repLevel:
			player.statusMessage( csstatus.WU_YAO_WANG_BAO_ZANG_ENTER_LEVEL, self.repLevel )
			return
		
		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			allMemberInRange = player.getAllMemberInRange( ENTERN_SGMJ_MENBER_DISTANCE )	# 得到范围内所有队伍成员
			# 判断是否队伍人数是否满足
			
			if not self.checkTeamMembers( player ) :
				return
			
			# 判断是否队伍成员都在
			teamMemberIDs = player.getAllIDNotInRange( ENTERN_SGMJ_MENBER_DISTANCE )
			if len( teamMemberIDs ) > 0:	# 如果队伍中有同志没在范围内
				for id in teamMemberIDs:
					player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
				return

			
			# 判断队伍成员任务是否未失败（任务时间没有超时，防止任务失败，角色没有在副本中，任务没有打上失败标记）
			isAllMemberNotLoseQuest = True
			for member in allMemberInRange:
				if member.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					teamID = member.questsTable[QUEST_WU_YAO_WANG_BAO_ZANG_ID].query( "teamID" )
					if teamID and not BigWorld.globalData.has_key( 'WuYaoWang_%i'%teamID ):	# 如果任务已经失败
						isAllMemberNotLoseQuest = False
						member.questTaskFailed( QUEST_WU_YAO_WANG_BAO_ZANG_ID, 1 )	# 通知任务失败
						player.statusMessage( csstatus.WU_YAO_WANG_BAO_ZANG_QUEST_LOSE, member.playerName )
						
			for i in allMemberInRange:
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG ) :
					player.statusMessage( csstatus.WU_YAO_WANG_BAO_ZANG_HAS_ENTERED_TODAY, i.playerName )
					return
			
			for i in allMemberInRange:
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )

class FuncEnterWuYaoWangBaoZangEasy( FuncEnterWuYaoWangBaoZang ):
	# 进入神鬼秘境简单模式
	def __init__( self, section ):
		FuncEnterWuYaoWangBaoZang.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() != csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_EASY ] :
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_RESTRICT_TEAM_NUM )
			return False
			
		return True
	

class FuncEnterWuYaoWangBaoZangDefficulty( FuncEnterWuYaoWangBaoZang ):
	# 进入神鬼秘境困难模式
	def __init__( self, section ):
		FuncEnterWuYaoWangBaoZang.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_RESTRICT_TEAM_NUM )
			return False
			
		return True
	

class FuncEnterWuYaoWangBaoZangNightmare( FuncEnterWuYaoWangBaoZang ):
	# 进入神鬼秘境噩梦模式
	def __init__( self, section ):
		FuncEnterWuYaoWangBaoZang.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_RESTRICT_TEAM_NUM )
			return False
			
		return True
	