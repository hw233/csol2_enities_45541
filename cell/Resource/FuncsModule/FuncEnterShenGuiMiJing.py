# -*- coding: gb18030 -*-
"""
��������ؾ�����
"""
import random
import math

import BigWorld

import csstatus
import csdefine
import csconst

from bwdebug import *
from FuncEnterDeffInterface import FuncEnterDeffCPInterface

ENTERN_SGMJ_MENBER_DISTANCE = 30.0		# �������
QUEST_SHEN_GUI_MI_JING_ID = 40301001	# ����ؾ���������id

class FuncEnterShenGuiMiJing( FuncEnterDeffCPInterface ):
	"""
	��������ؾ�����
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_SHEN_GUI_MI_JING
	
	def setMemberFlags( self, member ):
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
	
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
			player.statusMessage( csstatus.SHEN_GUI_MI_JING_ENTER_LEVEL, self.repLevel )
			return
			
		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_SHEN_GUI_MI_JING, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
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
			
			isAllMemberNotLoseQuest = True
			for member in allMemberInRange:
				if member.has_quest( QUEST_SHEN_GUI_MI_JING_ID ):
					teamID = member.questsTable[QUEST_SHEN_GUI_MI_JING_ID].query( "teamID" )
					if teamID and not BigWorld.globalData.has_key( 'ShenGuiMiJing_%i'%teamID ):	# ��������Ѿ�ʧ��
						isAllMemberNotLoseQuest = False
						member.questTaskFailed( QUEST_SHEN_GUI_MI_JING_ID, 1 )	# ֪ͨ����ʧ��
						player.statusMessage( csstatus.SHEN_GUI_MI_JING_QUEST_LOSE, member.playerName )
			
			for i in allMemberInRange:
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHEN_GUI_MI_JING ) :
					player.statusMessage( csstatus.SHEN_GUI_MI_JING_HAS_ENTERED_TODAY, i.playerName )
					return
			
			for i in allMemberInRange:
				self.setMemberFlags( i )
				#i.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )
				
			player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )

class FuncEnterShenGuiMiJingEasy( FuncEnterShenGuiMiJing ):
	# ��������ؾ���ģʽ
	def __init__( self, section ):
		FuncEnterShenGuiMiJing.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterShenGuiMiJingDefficulty( FuncEnterShenGuiMiJing ):
	# ��������ؾ�����ģʽ
	def __init__( self, section ):
		FuncEnterShenGuiMiJing.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterShenGuiMiJingNightmare( FuncEnterShenGuiMiJing ):
	# ��������ؾ�ج��ģʽ
	def __init__( self, section ):
		FuncEnterShenGuiMiJing.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE