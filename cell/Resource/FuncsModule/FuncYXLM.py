# -*- coding: gb18030 -*-
from Function import Function
from FuncEnterDeffInterface import FuncEnterDeffInterface
from bwdebug import *
import random
import re
import math
import csstatus
import csdefine
import csconst
import random
import BigWorld
import FuncEnterFJSG

class FuncEnterCopyYXYM( FuncEnterDeffInterface ):
	"""
	英雄联盟副本
	"""
	
	def __init__( self, section ):
		FuncEnterDeffInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_YXLM
	
	def setMemberFlags( self, member ):
		FuncEnterDeffInterface.setMemberFlags( self, member )
		member.setTemp( "YXLMEnterType", self.enterType )
	
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
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_LEVEL, self.repLevel )
			return
		
		#玩家没有组队
		if not player.isInTeam():
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return

		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_FLAGS_YING_XIONG_LIAN_MENG, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
				return

			pList = player.getAllMemberInRange( 30.0 )
			if not self.checkTeamMembers( player ):
				return
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_YING_XIONG_LIAN_MENG ) :
					enteredMembersStr += ( i.getName() + "," )
					
			if lowLevelMembersStr != "":
				# 队伍中有人级别不够
				player.statusMessage( csstatus.SPACE_COOY_YE_WAI_NEED_LEVEL, lowLevelMembersStr, self.repLevel )
				return
				
			if enteredMembersStr != "":
				# 队伍有人进入次数满
				player.statusMessage( csstatus.SPACE_COOY_YE_WAI_JOIN_FULL, enteredMembersStr )
				return
				
			for i in pList:
				self.setMemberFlags( i )
			rbtCls = []
			while len( rbtCls ) < 5:							#随机取5个不同的机器人
				rcls = random.choice( csconst.YXLM_ROBOT_2 )
				if rcls in rbtCls:continue
				rbtCls.append( rcls )
			robotsInfos = player.getBaoZangReqRobotInfos()
			player.baoZangReqPVE( robotsInfos, rbtCls )

class FuncEnterCopyYXYMEasy( FuncEnterCopyYXYM ):
	# 进入神鬼秘境简单模式
	def __init__( self, section ):
		FuncEnterCopyYXYM.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterCopyYXYMDefficulty( FuncEnterCopyYXYM ):
	# 进入神鬼秘境困难模式
	def __init__( self, section ):
		FuncEnterCopyYXYM.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterCopyYXYMNightmare( FuncEnterCopyYXYM ):
	# 进入神鬼秘境噩梦模式
	def __init__( self, section ):
		FuncEnterCopyYXYM.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE

class FuncBaoZangReqPVP( Function ):
	# 申请英雄联盟PVP模式
	def __init__( self, section ):
		Function.__init__( self, section )
		self.reqLevel = section.readInt( "param1" )
		self.diffLevel = section.readInt( "param2" )
		self.minJoin = section.readInt( "param3" )
	
	def do( self, player, talkEntity = None ):
		player.endGossip( talkEntity )
		
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
		
		if self.minJoin > player.getTeamCount():
			player.statusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_MIN_JOIN, self.minJoin )
			return
		
		# 判断是否队伍成员都在
		teamMemberIDs = player.getAllIDNotInRange( 30 )
		if len( teamMemberIDs ) > 0:	# 如果队伍中有同志没在范围内
			for id in teamMemberIDs:
				player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return
			
		minLevel = player.level
		maxLevel = player.level
		pList = player.getAllMemberInRange( 30.0 )
		for p in pList:
			if p.level > maxLevel:
				maxLevel = p.level
			
			if p.level < minLevel:
				minLevel = p.level 
				
		if maxLevel - minLevel > self.diffLevel:
			player.statusMessage(  csstatus.YING_XIONG_LIAN_MENG_PVP_DIFF_LEVEL, self.diffLevel  )
			return
		
		player.baoZangReqPVP()
	
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return not player.baoZangGetRivalTeam()

class FuncBaoZangEnterPVP( Function ):
	# 请求进入
	def __init__( self, section ):
		Function.__init__( self, section )
		self.spaceName = section.readString( "param1" )
		try:
			posAndDir = eval( re.sub( "\s*;\s*|\s+", ",", section.readString( "param2" ) ) )
		except Exception, err:
			posAndDir = ( 0,0,0,0,0,0 )
			ERROR_MSG( "space name =", self.spaceName, "pos and dir =", section.readString( "param2" ), err )
		position_1,direction_1 = posAndDir[:3],posAndDir[3:]
		
		try:
			posAndDir = eval( re.sub( "\s*;\s*|\s+", ",", section.readString( "param3" ) ) )
		except Exception, err:
			posAndDir = ( 0,0,0,0,0,0 )
			ERROR_MSG( "space name =", self.spaceName, "pos and dir =", section.readString( "param3" ), err )
		
		position_2,direction_2 = posAndDir[:3],posAndDir[3:]
		
		self.position = ( position_1, position_2 )
		self.direction = ( direction_1, direction_2 )
		
		self.minJoin = section.readInt( "param4" )
		self.diffLevel = section.readInt( "param5" )
		
	def do( self, player, talkEntity = None ):
		player.endGossip( talkEntity )
		
	 	if not player.isTeamCaptain():
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
		
		if self.minJoin > player.getTeamCount():
			player.statusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_MIN_JOIN, self.minJoin )
			return
		
		# 判断是否队伍成员都在
		teamMemberIDs = player.getAllIDNotInRange( 30 )
		if len( teamMemberIDs ) > 0:	# 如果队伍中有同志没在范围内
			for id in teamMemberIDs:
				player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return
			
		minLevel = player.level
		maxLevel = player.level
		pList = player.getAllMemberInRange( 30.0 )
		for p in pList:
			if p.level > maxLevel:
				maxLevel = p.level
			
			if p.level < minLevel:
				minLevel = p.level 
				
		if maxLevel - minLevel > self.diffLevel:
			p.statusMessage(  csstatus.YING_XIONG_LIAN_MENG_PVP_DIFF_LEVEL, self.diffLevel  )
			return
		
		player.baoZangEnterReady()

	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return player.baoZangGetRivalTeam()
	 
class FuncYXYMCloseSpace( Function ):
	def __init__( self, section ):
		Function.__init__( self, section )
	
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
			
		spaceMB = player.getCurrentSpaceBase()
		if BigWorld.entities.get( spaceMB.id ):
			BigWorld.entities[ spaceMB.id ].closeYXLMSpace()
		else:
			spaceMB.cell.closeYXLMSpace()