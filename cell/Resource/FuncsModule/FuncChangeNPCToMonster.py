# -*- coding: gb18030 -*-

"""
"""
from Function import Function
import csdefine
import csstatus
import Language
import time
import BigWorld


class FuncChangeNPCToMonster( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		#self.AIlevel = section.readInt( "param1" )										#AI �ȼ�
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		talkEntity.changeToMonster( talkEntity.level, player.id )
		player.endGossip( talkEntity )
