# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function

import csdefine

class FuncStartPickAnima( Function ):
	"""
	��ʼʰȡ����淨
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		player.changeState( csdefine.ENTITY_STATE_PICK_ANIMA )
		player.endGossip( talkEntity )


class FuncStopPickAnima( Function ):
	"""
	����ʰȡ����淨
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		spaceCell = player.getCurrentSpaceCell()
		if spaceCell:
			spaceCell.onGameOver()

		player.changeState( csdefine.ENTITY_STATE_FREE )
		player.endGossip( talkEntity )