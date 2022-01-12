# -*- coding: gb18030 -*-

import csstatus
import csconst
import BigWorld
from Function import Function

from FuncTeleport import FuncTeleport

class FuncAoZhanSignUp( Function ):
	"""
	��սȺ�۱���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._minLevel = section.readInt( "param1" )	# �����ĳ���ս����
		
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
		if player.level < self._minLevel:
			player.statusMessage( csstatus.AO_ZHAN_QUN_XIONG_JOIN_MIN_LEVEL, player.level )
			return
		
		
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].getSignUpList( player.base )


class FuncAoZhanEnter( FuncTeleport ):
	"""
	��սȺ�۽���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
	
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		FuncTeleport.do( self, player, talkEntity )