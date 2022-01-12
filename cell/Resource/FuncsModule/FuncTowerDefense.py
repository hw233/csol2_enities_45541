# -*- coding: gb18030 -*-
"""
���������Ի�
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

ENTERN_SGMJ_MENBER_DISTANCE = 30.0		# �������


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
		ִ��һ������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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

		allMemberInRange = player.getAllMemberInRange( ENTERN_SGMJ_MENBER_DISTANCE )	# �õ���Χ�����ж����Ա
		# �ж��Ƿ���������Ƿ�����
		
		if not self.checkTeamMembers( player ) :
			return
		
		# �ж��Ƿ�����Ա����
		teamMemberIDs = player.getAllIDNotInRange( 10 )
		if len( teamMemberIDs ) > 0:	# �����������ͬ־û�ڷ�Χ��
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
	# ��������������ģʽ
	def __init__( self, section ):
		FuncTowerDefense.__init__( self, section )
		if section.readString( "param4" ):			 # �����ٻ����ػ�������
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
	# ����������������ģʽ
	def __init__( self, section ):
		FuncTowerDefense.__init__( self, section )
		if section.readString( "param4" ):			 # �����ٻ����ػ�������
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
	# ������������ج��ģʽ
	def __init__( self, section ):
		FuncTowerDefense.__init__( self, section )
		if section.readString( "param4" ):			 # �����ٻ����ػ�������
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
