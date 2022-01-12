# -*- coding: gb18030 -*-
"""
�Ѷȸ�������Ի��ӿ�
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
		self.spaceType = 0 # ����spaceType
	
	def getTeamCopy( self, player ):
		"""
		�������Ƿ��Ѿ���������
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
		����������
		"""
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.enterType ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		"""
		������entity����д����
		"""
		pass

class FuncEnterDeffCPInterface( FuncEnterDeffInterface ):
	# ���ٻ����ػ���
	def __init__( self, section ):
		FuncEnterDeffInterface.__init__( self, section )
		if section.readString( "param4" ):			 # �����ٻ����ػ�������
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_EASY

	def setMemberFlags( self, member ):
		member.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
