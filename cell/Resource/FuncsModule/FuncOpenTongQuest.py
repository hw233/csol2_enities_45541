# -*- coding: gb18030 -*-

import csstatus

class FuncOpenTongDartQuest:
	"""
	���������������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
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
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_OPEN_TONG_QUEST_REQUEST_CHIEF )
			return
		tongBase = player.tong_getSelfTongEntity()
		if tongBase:
			tongBase.openTongDartQuest( player.base )
	
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
		return True

class FuncOpenTongNormalQuest:
	"""
	��������ճ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.type = section['param1'].asInt
		
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
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_OPEN_TONG_QUEST_REQUEST_CHIEF )
			return
		tongBase = player.tong_getSelfTongEntity()
		if tongBase:
			tongBase.openTongNormalQuest( player.base, self.type )
	
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
		return True