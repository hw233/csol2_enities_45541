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


RESTRICT_TEAM_NUM = 3  						# ���������������3��
ENTERN_SGMJ_MENBER_DISTANCE = 30.0			# �������
QUEST_WU_YAO_WANG_BAO_ZANG_ID = 40301003	# ���������ظ�������id

class FuncEnterWuYaoWangBaoZang( FuncEnterDeffCPInterface ):
	"""
	�������������ظ���
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
		ִ��һ������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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

			allMemberInRange = player.getAllMemberInRange( ENTERN_SGMJ_MENBER_DISTANCE )	# �õ���Χ�����ж����Ա
			# �ж��Ƿ���������Ƿ�����
			
			if not self.checkTeamMembers( player ) :
				return
			
			# �ж��Ƿ�����Ա����
			teamMemberIDs = player.getAllIDNotInRange( ENTERN_SGMJ_MENBER_DISTANCE )
			if len( teamMemberIDs ) > 0:	# �����������ͬ־û�ڷ�Χ��
				for id in teamMemberIDs:
					player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
				return

			
			# �ж϶����Ա�����Ƿ�δʧ�ܣ�����ʱ��û�г�ʱ����ֹ����ʧ�ܣ���ɫû���ڸ����У�����û�д���ʧ�ܱ�ǣ�
			isAllMemberNotLoseQuest = True
			for member in allMemberInRange:
				if member.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					teamID = member.questsTable[QUEST_WU_YAO_WANG_BAO_ZANG_ID].query( "teamID" )
					if teamID and not BigWorld.globalData.has_key( 'WuYaoWang_%i'%teamID ):	# ��������Ѿ�ʧ��
						isAllMemberNotLoseQuest = False
						member.questTaskFailed( QUEST_WU_YAO_WANG_BAO_ZANG_ID, 1 )	# ֪ͨ����ʧ��
						player.statusMessage( csstatus.WU_YAO_WANG_BAO_ZANG_QUEST_LOSE, member.playerName )
						
			for i in allMemberInRange:
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG ) :
					player.statusMessage( csstatus.WU_YAO_WANG_BAO_ZANG_HAS_ENTERED_TODAY, i.playerName )
					return
			
			for i in allMemberInRange:
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )

class FuncEnterWuYaoWangBaoZangEasy( FuncEnterWuYaoWangBaoZang ):
	# ��������ؾ���ģʽ
	def __init__( self, section ):
		FuncEnterWuYaoWangBaoZang.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() != csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_EASY ] :
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_RESTRICT_TEAM_NUM )
			return False
			
		return True
	

class FuncEnterWuYaoWangBaoZangDefficulty( FuncEnterWuYaoWangBaoZang ):
	# ��������ؾ�����ģʽ
	def __init__( self, section ):
		FuncEnterWuYaoWangBaoZang.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_RESTRICT_TEAM_NUM )
			return False
			
		return True
	

class FuncEnterWuYaoWangBaoZangNightmare( FuncEnterWuYaoWangBaoZang ):
	# ��������ؾ�ج��ģʽ
	def __init__( self, section ):
		FuncEnterWuYaoWangBaoZang.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_RESTRICT_TEAM_NUM )
			return False
			
		return True
	