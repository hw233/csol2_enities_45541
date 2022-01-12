# -*- coding: gb18030 -*-
#

from FuncTeleport import FuncTeleport
from Function import Function
import csdefine
import csconst
import BigWorld
import time
import csstatus

ENTERN_YAYU_MENBER_DISTANCE = 30.0
ENTER_YAYU_POSITION	= (4, 2, 4)				#����m����λ��

class FuncEnterYayuNew( FuncTeleport ):
	"""
	����m؅����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
		self.recordKey = "yayu_record_new"

	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )
	
	def do( self, player, talkEntity = None ):
		"""
		����m؅������
		����
			�������������Ѷ�Ա����������
				������鵱ǰû�и�����
				Ҫ��������Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				�����������ܴ��ڸ���ģʽ��Ӧ����
				�����Աû�н���������ġ�
		ֻ���Լ�һ���˲��ܽ��븱��
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		if self.repLevel > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.YAYU_LEVEL_NOT_ARRIVE, self.repLevel )
			return
			
		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.YAYU_NEW_NEED_TEAM )
			return
		
		if BigWorld.globalData.has_key( 'Yayu_%i'%player.getTeamMailbox().id ):
			#��ҵĶ���ӵ��һ���m؅�����������ٽ���
			player.client.onStatusMessage( csstatus.YAYU_NEW_HAS_ENTERED_TODAY, "" )
			return
		
		#����û�и��������ߴ�������
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
			return
			
		# �ж��Ƿ�����Ա����
		teamMemberIDs = player.getAllIDNotInRange( ENTERN_YAYU_MENBER_DISTANCE )
		if len( teamMemberIDs ) > 0:
			for id in teamMemberIDs:
				player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return
		
		if not self.checkTeamMembers( player ) :
			return
		
		# ��Ա�����ж�	
		pList = player.getAllMemberInRange( ENTERN_YAYU_MENBER_DISTANCE )
		lowLevelMembersStr = ""
		enteredMembersStr = ""
		for i in pList:
			if i.level < self.repLevel:
				lowLevelMembersStr += ( i.getName() + "," )
			if i.isActivityCanNotJoin( csdefine.ACTIVITY_ZHENG_JIU_YA_YU_NEW ) :
				enteredMembersStr += ( i.getName() + "," )
		
		if lowLevelMembersStr != "":
			# ���������˼��𲻹�
			player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_YAYU_LEVEL, lowLevelMembersStr, self.repLevel )
			return
		
		"""
		Ϊ�˷�����ԣ���ʱ���������ж�
		if enteredMembersStr != "":
			# �����������Ѿ��μӹ��m؅�
			player.statusMessage( csstatus.YAYU_NEW_HAS_FINISHED_TODAY, enteredMembersStr )
			return
		"""
		
		# ���븱��
		pList.remove( player )
		self.setMemberFlags( player )
		player.gotoSpace( self.spaceName, self.position, self.direction )
		
		for i in pList:
			self.setMemberFlags( i )
			i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterYayuNewDifficulty( FuncEnterYayuNew ):
	# ����m؅��������ģʽ
	def __init__( self, section ):
		FuncEnterYayuNew.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )

class FuncEnterYayuNewNightmare( FuncEnterYayuNew ):
	# ����m؅����ج��ģʽ
	def __init__( self, section ):
		FuncEnterYayuNew.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )