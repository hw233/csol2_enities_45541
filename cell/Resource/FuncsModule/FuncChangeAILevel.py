# -*- coding: gb18030 -*-
# create by TangHui


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus


class FuncChangeAILevel( Function ):
	"""
	�Ի��ı�AI�ȼ�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.AIlevel = section.readInt( "param1" )										#AI �ȼ�


	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		talkEntity.setDefaultAILevel( self.AIlevel )
		talkEntity.setNextRunAILevel( self.AIlevel )
		talkEntity.setTemp( "talkPlayerID",player.id )

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
