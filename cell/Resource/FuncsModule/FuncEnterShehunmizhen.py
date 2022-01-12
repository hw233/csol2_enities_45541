# -*- coding: gb18030 -*-

from bwdebug import *
import csstatus
import csdefine
import csconst
from FuncEnterDeffInterface import FuncEnterDeffCPInterface

ENTER_SHMZ_MENBER_DISTANCE = 30.0

class FuncEnterShehunmizhen( FuncEnterDeffCPInterface ):
	"""
	����������󸱱�
	"""
	def __init__( self, section ):
		"""
		"""
		FuncEnterDeffCPInterface.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY
		self.spaceType = csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN

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
		#��ҵȼ�����
		if self.repLevel > player.level:
			player.statusMessage( csstatus.SHMZ_LEVEL_NOT_ARRIVE, self.repLevel )
			return
		
		#���û�����
		if not player.isInTeam():
			player.statusMessage( csstatus.SHMZ_NEED_TEAM )
			return

		teamCopy = self.getTeamCopy( player )
		if teamCopy:
			self.setMemberFlags( player )
			teamCopy.onPlayerReqEnter( csdefine.ACTIVITY_SHE_HUN_MI_ZHEN, player.base, player.databaseID, self.calcPosition( self.position ), self.direction )
		else:
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			pList = player.getAllMemberInRange( ENTER_SHMZ_MENBER_DISTANCE )
			
			if not self.checkTeamMembers( player ):
				return 
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHE_HUN_MI_ZHEN ) :
					enteredMembersStr += ( i.getName() + "," )
					
			if lowLevelMembersStr != "":
				# ���������˼��𲻹�
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_SHMZ_LEVEL, lowLevelMembersStr, self.repLevel )
				return
			if enteredMembersStr != "":
				# �����������Ѿ��μӹ��⽣�񹬻
				player.statusMessage( csstatus.SHMZ_HAS_ENTERED_TODAY, enteredMembersStr )
				return
			pList.remove( player )
			player.gotoSpace( self.spaceName, self.position, self.direction )
			for i in pList:
				self.setMemberFlags( i )
				i.set( "lastSHMZTeamID", player.getTeamMailbox().id )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterShehunmizhenEasy( FuncEnterShehunmizhen ):
	# ������������ģʽ
	def __init__( self, section ):
		FuncEnterShehunmizhen.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_EASY

class FuncEnterShehunmizhenDefficulty( FuncEnterShehunmizhen ):
	# ���������������ģʽ
	def __init__( self, section ):
		FuncEnterShehunmizhen.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_DIFFICULTY

class FuncEnterShehunmizhenNightmare( FuncEnterShehunmizhen ):
	# �����������ج��ģʽ
	def __init__( self, section ):
		FuncEnterShehunmizhen.__init__( self, section )
		self.enterType = csconst.SPACE_COPY_YE_WAI_NIGHTMARE
