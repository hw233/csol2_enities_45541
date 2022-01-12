# -*- coding: gb18030 -*-
"""
����а����Ѩ����
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
	����а����Ѩ����
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
		ִ��һ������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
			
		if self.repLevel > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.XLDX_LEVEL_NOT_ARRIVE, self.repLevel )
			return
			
		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.XLDX_NEED_TEAM )
			return

		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_XIE_LONG, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			pList = player.getAllMemberInRange( ENTERN_XLDX_MENBER_DISTANCE )
			
			if not self.checkTeamMembers( player ):
				return
				
			# �ж��Ƿ�����Ա����
			teamMemberIDs = player.getAllIDNotInRange( ENTERN_XLDX_MENBER_DISTANCE )
			if len( teamMemberIDs ) > 0:	# �����������ͬ־û�ڷ�Χ��
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
				# ���������˼��𲻹�
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_XLDX_LEVEL, lowLevelMembersStr, self.repLevel )
				return
			if enteredMembersStr != "":
				# �����������Ѿ��μӹ�а����Ѩ�
				player.statusMessage( csstatus.XLDX_HAS_ENTERED_TODAY, enteredMembersStr )
				return
				
			for i in pList:
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.position, self.direction )
			
class FuncEnterXieLongDongXueEasy( FuncEnterXieLongDongXue ):
	# ��������ؾ���ģʽ
	def __init__( self, section ):
		FuncEnterXieLongDongXue.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterXieLongDongXueDefficulty( FuncEnterXieLongDongXue ):
	# ��������ؾ�����ģʽ
	def __init__( self, section ):
		FuncEnterXieLongDongXue.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterXieLongDongXueNightmare( FuncEnterXieLongDongXue ):
	# ��������ؾ�ج��ģʽ
	def __init__( self, section ):
		FuncEnterXieLongDongXue.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE