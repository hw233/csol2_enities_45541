# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import BigWorld
import csdefine


class FuncTakeSilver( Function ):
	"""
	��ȡԪ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass


	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		player.base.takeSilver()
		


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

