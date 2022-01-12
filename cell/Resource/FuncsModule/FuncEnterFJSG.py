# -*- coding: gb18030 -*-
#

"""
����⽣�񹬸���
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
	����⽣�񹬸���
	"""
	
	def __init__( self, section ):
		"""
		"""
		FuncTeleport.__init__( self, section )
		self.level = 80		#����ȼ�
		self.recordKey = "fjsg_record"
	
	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyFJSGType", csconst.SPACE_COPY_YE_WAI_EASY )
	
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
		if self.level > player.level:
			player.statusMessage( csstatus.FJSG_LEVEL_NOT_ARRIVE, self.level )
			return
		
		#���û�����
		if not player.isInTeam():
			player.statusMessage( csstatus.FJSG_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'FJSG_%i'%player.getTeamMailbox().id ):
			#��ҵĶ���ӵ��һ��а����Ѩ����
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG )  and player.query( "lastFJSGTeamID", 0 ) != player.getTeamMailbox().id:
				player.client.onStatusMessage( csstatus.FJSG_IN_ALREADY, "" )
				return
			player.gotoSpace( self.spaceName, self.position, self.direction )
		else:
			#����û�и��������ߴ�������
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
				# ���������˼��𲻹�
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_FJSG_LEVEL, lowLevelMembersStr, self.level )
				return
			if enteredMembersStr != "":
				# �����������Ѿ��μӹ��⽣�񹬻
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
	# ���뽣�񹬸�����ģʽ
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
	# ���뽣�񹬸�������ģʽ
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
	# ���뽣�񹬸���ج��ģʽ
	def __init__( self, section ):
		FuncEnterFJSG.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyFJSGType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )