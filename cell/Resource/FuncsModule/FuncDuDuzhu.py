# -*- coding: gb18030 -*-

import csstatus
import csdefine
import csconst
from bwdebug import *
from FuncEnterDeffInterface import FuncEnterDeffCPInterface

class FuncDuDuzhu( FuncEnterDeffCPInterface ):
	"""
	��������
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_PIG
		self.memberDis = section["param4"].asFloat				# �����Ա����

	def setMemberFlags( self, member ):
		"""
		������entity����д����
		"""
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
		member.setTemp( "EnterSpaceDuDuZhu", self.enterType )

	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )

		if self.repLevel > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.DUDUZHU_FORBID_LEVEL, self.repLevel )
			return
			
		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.TALK_FORBID_TEAM )
			return
		
		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_DU_DU_ZHU, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			
			if not self.checkTeamMembers( player ):
				return
				
			# �ж��Ƿ�����Ա����
			teamMemberIDs = player.getAllIDNotInRange( self.memberDis )
			if len( teamMemberIDs ) > 0:	# �����������ͬ־û�ڷ�Χ��
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
				# ���������˼��𲻹�
				player.statusMessage( csstatus.DUDUZHU_FORBID_MEMBER_LEVEL_LESS, lowLevelMembersStr, self.repLevel )
				return
				
			if enteredMembersStr != "":
				# �����������Ѿ��μ�����
				player.statusMessage( csstatus.SPACE_COPY_HAS_ENTERED, enteredMembersStr )
				return
				
			for i in pList:
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncDuDuzhuEasy( FuncDuDuzhu ):
	# ���������ģʽ
	def __init__( self, section ):
		FuncDuDuzhu.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncDuDuzhuDifficulty( FuncDuDuzhu ):
	# ��������������ģʽ
	def __init__( self, section ):
		FuncDuDuzhu.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncDuDuzhuNightmare( FuncDuDuzhu ):
	# ��������ج��ģʽ
	def __init__( self, section ):
		FuncDuDuzhu.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE