# -*- coding: gb18030 -*-
#

"""
��������ǰ�ڸ���
"""
from FuncEnterDeffInterface import FuncEnterDeffCPInterface
from bwdebug import *
import random
import math
import csstatus
import csdefine
import csconst
import time
import BigWorld

RESTRICT_TEAM_NUM = 3  					# ���������������3��
ENTERN_SGMJ_MENBER_DISTANCE = 30.0		# �������
QUEST_WU_YAO_QIAN_SHAO_ID = 40301002	# ����ǰ�ڸ�������id

class FuncEnterWuYaoQianShao( FuncEnterDeffCPInterface ):
	"""
	��������ǰ�ڸ���
	"""
	
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_WU_YAO_QIAN_SHAO
	
	def setMemberFlags( self, member ):
		FuncEnterDeffCPInterface.setMemberFlags( self, member )
		#member.setTemp( "WuYaoQianShaoEnterType", self.enterType )
	
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
			player.statusMessage( csstatus.WU_YAO_QIAN_SHAO_ENTER_LEVEL, self.repLevel )
			return
		
		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_WU_YAO_QIAN_SHAO, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
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
				if member.has_quest( QUEST_WU_YAO_QIAN_SHAO_ID ):
					teamID = member.questsTable[QUEST_WU_YAO_QIAN_SHAO_ID].query( "teamID" )
					if teamID and not BigWorld.globalData.has_key( 'WuYaoQianShao_%i'%teamID ):	# ��������Ѿ�ʧ��
						isAllMemberNotLoseQuest = False
						member.questTaskFailed( QUEST_WU_YAO_QIAN_SHAO_ID, 1 )	# ֪ͨ����ʧ��
						player.statusMessage( csstatus.WU_YAO_QIAN_SHAO_QUEST_LOSE, member.playerName )
			
			for i in allMemberInRange:
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_WU_YAO_QIAN_SHAO ) :
					player.statusMessage( csstatus.WU_YAO_QIAN_SHAO_HAS_ENTERED_TODAY, i.playerName )
					return
			
			for i in allMemberInRange:
				self.setMemberFlags( i )
				#i.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )
			
			player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )
		
class FuncEnterWuYaoQianShaoEasy( FuncEnterWuYaoQianShao ):
	# ��������ؾ���ģʽ
	def __init__( self, section ):
		FuncEnterWuYaoQianShao.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterWuYaoQianShaoDefficulty( FuncEnterWuYaoQianShao ):
	# ��������ؾ�����ģʽ
	def __init__( self, section ):
		FuncEnterWuYaoQianShao.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterWuYaoQianShaoNightmare( FuncEnterWuYaoQianShao ):
	# ��������ؾ�ج��ģʽ
	def __init__( self, section ):
		FuncEnterWuYaoQianShao.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE