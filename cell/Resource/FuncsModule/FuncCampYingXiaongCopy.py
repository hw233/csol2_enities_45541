# -*- coding: gb18030 -*-

# 阵营英雄联盟用
from Function import Function
from bwdebug import *
import random
import re
import math
import csstatus
import csdefine
import csconst
import random
import BigWorld

class FuncCampYingXiaongReq( Function ):
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
		
		player.yingXiongCampReq()
	
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return not player.yingXiongCampGetRivalTeam()

class FuncCampYingXiaongEnter( Function ):
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
		
		player.yingXiongCampEnterReady()

	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return player.yingXiongCampGetRivalTeam()