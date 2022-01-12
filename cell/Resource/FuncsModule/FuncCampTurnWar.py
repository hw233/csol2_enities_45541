# -*- coding: gb18030 -*-

import csstatus
import csconst
import BigWorld
from Function import Function

class FuncCampTurnWarSignUp( Function ):
	"""
	������ᳵ��ս
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._param1 = section.readString( "param1" )	# �����ĳ���ս����
		
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
		if BigWorld.globalData["CampTurnWarStep"] == csconst.CAMP_TURN_STEP_SIGNUP :
			return True
		return False
	
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
		if not player.isCaptain():
			player.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_NOT_CAPTAIN )
			return

		if player.level < csconst.CAMP_TURN_LEVEL_MIN:
			player.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_LEVEL_WRONG )
			return
		player.client.campTurnWar_signUpCheck( self._param1, csconst.CAMP_TURN_MEMBER_NUM)