# -*- coding: gb18030 -*-
"""
塔防副本对话
"""
from FuncTeleport import FuncTeleport
from FuncEnterDeffInterface import FuncEnterDeffInterface
from bwdebug import *
import random
import math
import csstatus
import csdefine
import csconst
import BigWorld

ENTERN_SGMJ_MENBER_DISTANCE = 30.0		# 队伍距离


class FuncTowerDefense( FuncEnterDeffInterface ):
	def __init__( self, section ):
		"""
		"""
		FuncTeleport.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		pass
	
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
			player.statusMessage( csstatus.SPACE_COPY_LEVEL_ERROR, self.repLevel )
			return
		
		teamCopy = None
		if player.isInTeam():
			teamCopy = self.getTeamCopy( player )
			
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_TOWER_DEFENSE, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_TOWER_DEFENSE )  and player.query( "lastTowerDefenseID", 0 ) != player.getTeamMailbox().id:
				player.statusMessage( csstatus.SPACE_COPY_HAS_ENTERED, player.playerName )
				return
			player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )
			return

		if not player.isTeamCaptain():
			player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
			return

		allMemberInRange = player.getAllMemberInRange( ENTERN_SGMJ_MENBER_DISTANCE )	# 得到范围内所有队伍成员
		# 判断是否队伍人数是否满足
		
		if not self.checkTeamMembers( player ) :
			return
		
		# 判断是否队伍成员都在
		teamMemberIDs = player.getAllIDNotInRange( 10 )
		if len( teamMemberIDs ) > 0:	# 如果队伍中有同志没在范围内
			for id in teamMemberIDs:
				player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return
	
		for i in allMemberInRange:
			if i.isActivityCanNotJoin( csdefine.ACTIVITY_TOWER_DEFENSE ) :
				player.statusMessage( csstatus.SPACE_COPY_HAS_ENTERED, i.playerName )
				return
		
		for i in allMemberInRange:
			i.set( "lastTowerDefenseID", player.getTeamMailbox().id )
			self.setMemberFlags( i )
			
		player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )

class FuncTowerDefenseEasy( FuncTowerDefense ):
	# 进入塔防副本简单模式
	def __init__( self, section ):
		FuncTowerDefense.__init__( self, section )
		if section.readString( "param4" ):			 # 允许召唤的守护的数量
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_EASY

	def checkTeamMembers( self, player ):
		if player.getTeamCount() != csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_EASY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "TowerDefenseType", csconst.SPACE_COPY_YE_WAI_EASY )
		member.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )

class FuncTowerDefenseDefficulty( FuncTowerDefense ):
	# 进入塔防副本困难模式
	def __init__( self, section ):
		FuncTowerDefense.__init__( self, section )
		if section.readString( "param4" ):			 # 允许召唤的守护的数量
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_DIFFICULT
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "TowerDefenseType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )
		member.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )

class FuncTowerDefenseNightmare( FuncTowerDefense ):
	# 进入塔防副本噩梦模式
	def __init__( self, section ):
		FuncTowerDefense.__init__( self, section )
		if section.readString( "param4" ):			 # 允许召唤的守护的数量
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_NIGHTMARE

	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "TowerDefenseType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )
		member.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
