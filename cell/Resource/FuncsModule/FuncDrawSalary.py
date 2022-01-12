# -*- coding: gb18030 -*-
#
"""
��ȡٺ»
"""
from Function import Function
import BigWorld
import csconst

class FuncDrawSalary( Function ):
	"""
	��ȡٺ»
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section  )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		tongMailbox = player.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onRequireSalaryInfo( player.base, player.databaseID )
		player.endGossip( talkEntity )

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
		return player.tong_dbID != 0
