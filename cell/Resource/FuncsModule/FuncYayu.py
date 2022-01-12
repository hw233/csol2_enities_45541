# -*- coding: gb18030 -*-
#


"""
"""
from FuncTeleport import FuncTeleport
import csdefine
import csconst
import BigWorld
import time
import csstatus
from Function import Function

ENTERN_YAYU_MENBER_DISTANCE = 30.0
class FuncEnterYayu( FuncTeleport ):
	"""
	����m؅����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
		self.recordKey = "yayu_record"

	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_EASY )
	
	def do( self, player, talkEntity = None ):
		"""
		����m؅������
		����
			�������������Ѷ�Ա����������
				������鵱ǰû�и�����
				Ҫ��������Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
				�����Աû�н���������ġ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		#if not BigWorld.globalData.has_key('AS_yayuStart') or not BigWorld.globalData["AS_yayuStart"]:
		#	#�m؅�û�п���
		#	player.statusMessage( csstatus.YAYU_IS_NOT_OPEN )
		#	return	
		if self.repLevel > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.YAYU_LEVEL_NOT_ARRIVE, self.repLevel )
			return
			
		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.YAYU_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'Yayu_%i'%player.getTeamMailbox().id ):
			#��ҵĶ���ӵ��һ���m؅����
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_ZHENG_JIU_YA_YU )  and player.query( "lastYayuTeamID", 0 ) != player.getTeamMailbox().id:
				player.client.onStatusMessage( csstatus.YAYU_IN_ALREADY, "" )
				return
			player.gotoSpace( self.spaceName, self.position, self.direction )
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			pList = player.getAllMemberInRange( ENTERN_YAYU_MENBER_DISTANCE )
			
			if not self.checkTeamMembers( player ) :
				return
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_ZHENG_JIU_YA_YU ) :
					enteredMembersStr += ( i.getName() + "," )
			# ���������˼��𲻹�
			if lowLevelMembersStr != "":
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_YAYU_LEVEL, lowLevelMembersStr, self.repLevel )
				return
			# �����������Ѿ��μӹ��m؅�
			if enteredMembersStr != "":
				player.statusMessage( csstatus.YAYU_HAS_ENTERED_TODAY, enteredMembersStr )
				return

			for i in pList:
				i.set( "lastYayuTeamID", player.getTeamMailbox().id )
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterYayuEasy( FuncEnterYayu ):
	# ����m؅������ģʽ
	def __init__( self, section ):
		FuncEnterYayu.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() != csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_EASY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_EASY )

class FuncEnterYayuDefficulty( FuncEnterYayu ):
	# ����m؅��������ģʽ
	def __init__( self, section ):
		FuncEnterYayu.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )

class FuncEnterYayuNightmare( FuncEnterYayu ):
	# ����m؅����ج��ģʽ
	def __init__( self, section ):
		FuncEnterYayu.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )


class FuncHelpYayu( Function ):
	"""
	�����m؅������ս��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		talkEntity.onActived()

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity == None:
			return False
		return talkEntity.queryTemp( "yayuCanTalk", False )


class FuncYayuThanks( Function ):
	"""
	�����m؅������ս��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		talkEntity.onThankOver()

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity == None:
			return False
		return talkEntity.queryTemp( "yayuFinishTalk", False )
