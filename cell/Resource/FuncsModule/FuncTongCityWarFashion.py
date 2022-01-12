# -*- coding: gb18030 -*-
"""
����սʱװ�����Ի� 11:27 2010-12-21 by ����
"""
import BigWorld
import csdefine
import csstatus
from Function import Function

class FuncTongCityWarFashionMember( Function ):
	"""
	����սʱװ���� ��Ա
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
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
		if player.tong_dbID <= 0:
			return False
		if player.tong_holdCity == "":
			return False
		return True
		
class FuncTongCityWarFashionChairman( Function ):
	"""
	����սʱװ���� ����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
		player.endGossip( talkEntity )
		
		player.factionCount -= 1
		player.base.setTongFactionCount( player.factionCount )

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
		if player.tong_dbID <= 0:
			return False
		if not player.isTongChief():
			return False
		if player.tong_holdCity == "":
			return False
		if player.factionCount < 1:
			return False
		return True