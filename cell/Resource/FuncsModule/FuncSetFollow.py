# -*- coding: gb18030 -*-
from Function import Function
from bwdebug import *
import random
import math
import Math
import utils
import csstatus
import csdefine
import csconst
import BigWorld


class FuncSetFollow( Function ):
	"""
	���ø�����
	"""
	
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		talkEntity.setTemp( "talkFollowID", player.id )

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
		return player.has_quest( self.param1 )