# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld

class FuncEquipPour( Function ):
	"""
	װ�����Թ�ע
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def valid( self, playerEntity, talkEntity = None ):
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

	def do( self, playerEntity, talkEntity = None ):
		"""
		ִ��һ������

		@param playerEntity: ���
		@type  playerEntity: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % player.getName() )
			return
		playerEntity.client.enterEquipPour( talkEntity.id )