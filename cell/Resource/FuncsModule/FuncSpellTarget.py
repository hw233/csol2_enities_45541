# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
import csconst
from bwdebug import *
import Const
import BigWorld


class FuncSpellTarget( Function ):
	"""
	�����ʩ�ż���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		# param1�� ����ID������������9770022001
		Function.__init__( self, section )
		self.skillID = section["param1"].asInt
		self.teleportInfos = section.readString("param2")
		assert self.skillID != 0, "Invalid skill ID!"
		
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
			ERROR_MSG( "player( %s ) talk entity is None." % playerEntity.getName() )
			return
		playerEntity.setTemp( "requestTeleport", self.teleportInfos )
		playerEntity.spellTarget( self.skillID, playerEntity.id )

		