# -*- coding: gb18030 -*-
"""
难度副本进入对话接口
"""
import random
import math

import BigWorld

import csstatus
import csconst
import Const

from FuncTeleport import FuncTeleport

class FuncEnterDeffInterface( FuncTeleport ):
	def __init__( self, section ):
		FuncTeleport.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = 0 # 副本spaceType
	
	def getTeamCopy( self, player ):
		"""
		检查队伍是否已经开启副本
		"""
		if player.isInTeam():
			globalKey = Const.GET_SPACE_COPY_GLOBAL_KEY( self.spaceType ,player.getTeamMailbox().id, self.enterType )
			if BigWorld.cellAppData.has_key( globalKey ):
				spaceMB = BigWorld.cellAppData[ globalKey ]
				if BigWorld.entities.has_key( spaceMB.id ):
					return BigWorld.entities[ spaceMB.id ]
				else:
					return spaceMB.cell
		
		return None
	
	def checkTeamMembers( self, player ):
		"""
		检查队伍人数
		"""
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.enterType ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		"""
		往进入entity身上写数据
		"""
		pass

class FuncEnterDeffCPInterface( FuncEnterDeffInterface ):
	# 有召唤的守护的
	def __init__( self, section ):
		FuncEnterDeffInterface.__init__( self, section )
		if section.readString( "param4" ):			 # 允许召唤的守护的数量
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_EASY

	def setMemberFlags( self, member ):
		member.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
