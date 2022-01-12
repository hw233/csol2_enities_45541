# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from FuncTeleport import FuncTeleport
from bwdebug import *
import BigWorld
import csstatus
import csdefine
import csconst

class FuncEnterSunBath( FuncTeleport ):
	"""
	�������Ǹ���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
		if section.readString( "param4" ):			 # �����ٻ����ػ�������
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_EASY
		
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
		if player.level < self.repLevel:
			player.statusMessage( csstatus.SUN_BATHING_ENTER_LEVEL, self.repLevel )
			return
		player.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
		player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )
		