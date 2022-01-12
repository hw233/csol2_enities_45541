# -*- coding: gb18030 -*-
#
# $Id: FuncDrawPresent.py,v 1.11 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
import csconst

class FuncDrawPresent( Function ):
	"""
	��ȡ�������Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )


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
		if self._param1 != 0:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE, self._param1 )
		else:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE, 0 )


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

class FuncDrawPresentSingle( Function ):
	"""
	һ����ȡһ���������Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )


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
		if self._param1 != 0:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE_SINGLE, self._param1 )
		else:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE_SINGLE, 0 )


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
