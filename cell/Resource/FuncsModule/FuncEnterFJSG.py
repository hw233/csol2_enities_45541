# -*- coding: gb18030 -*-
#

"""
进入封剑神宫副本
"""
from FuncTeleport import FuncTeleport
from bwdebug import *
import random
import math
import csstatus
import csdefine
import csconst
import BigWorld


ENTERN_FJSG_MENBER_DISTANCE = 30.0

class FuncEnterFJSG( FuncTeleport ):
	"""
	进入封剑神宫副本
	"""
	
	def __init__( self, section ):
		"""
		"""
		FuncTeleport.__init__( self, section )
		self.level = 80		#进入等级
		self.recordKey = "fjsg_record"
	
	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyFJSGType", csconst.SPACE_COPY_YE_WAI_EASY )
	
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
		if self.level > player.level:
			player.statusMessage( csstatus.FJSG_LEVEL_NOT_ARRIVE, self.level )
			return
		
		#玩家没有组队
		if not player.isInTeam():
			player.statusMessage( csstatus.FJSG_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'FJSG_%i'%player.getTeamMailbox().id ):
			#玩家的队伍拥有一个邪龙洞穴副本
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG )  and player.query( "lastFJSGTeamID", 0 ) != player.getTeamMailbox().id:
				player.client.onStatusMessage( csstatus.FJSG_IN_ALREADY, "" )
				return
			player.gotoSpace( self.spaceName, self.position, self.direction )
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			pList = player.getAllMemberInRange( ENTERN_FJSG_MENBER_DISTANCE )
			if not self.checkTeamMembers( player ):
				return
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			
			for i in pList:
				if i.level < self.level:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG ) :
					enteredMembersStr += ( i.getName() + "," )
					
			if lowLevelMembersStr != "":
				# 队伍中有人级别不够
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_FJSG_LEVEL, lowLevelMembersStr, self.level )
				return
			if enteredMembersStr != "":
				# 队伍中有人已经参加过封剑神宫活动
				player.statusMessage( csstatus.FJSG_HAS_ENTERED_TODAY, enteredMembersStr )
				return
			pList.remove( player )
			player.gotoSpace( self.spaceName, self.position, self.direction )
			self.setMemberFlags( player )
			for i in pList:
				self.setMemberFlags( i )
				i.set( "lastFJSGTeamID", player.getTeamMailbox().id )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterFJSGEasy( FuncEnterFJSG ):
	# 进入剑神宫副本简单模式
	def __init__( self, section ):
		FuncEnterFJSG.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() != csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_EASY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyFJSGType", csconst.SPACE_COPY_YE_WAI_EASY )

class FuncEnterFJSGDefficulty( FuncEnterFJSG ):
	# 进入剑神宫副本困难模式
	def __init__( self, section ):
		FuncEnterFJSG.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyFJSGType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )

class FuncEnterFJSGNightmare( FuncEnterFJSG ):
	# 进入剑神宫副本噩梦模式
	def __init__( self, section ):
		FuncEnterFJSG.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyFJSGType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )