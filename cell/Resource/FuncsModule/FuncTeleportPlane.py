# -*- coding: gb18030 -*-
#
# add by gjx 7/1/14

"""
"""
from Function import Function
from bwdebug import *
import csdefine


class FuncTeleportPlane( Function ):
	"""
	����
	"""
	def __init__( self, section ):
		"""
		param1: _planeType

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._planeType = section.readString( "param1" )

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

		# ����з�������buff
		if player.spaceType == self._planeType:
			WARNING_MSG("Player %i teleport to plane %s which is the same as current." % (player.id, self._planeType))
			return

		player.enterPlane(self._planeType)

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
		if player.spaceType == self._planeType:
			return False

		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# �������Ѿ���������ô��������
			return False

		return True



