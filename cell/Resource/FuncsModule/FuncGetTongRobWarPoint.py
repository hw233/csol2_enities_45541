# -*- coding: gb18030 -*-
#
# $Id: FuncExp2Pot.py,v 1.1 2010-01-14 05:18:39 pengju Exp $

"""
"""
import BigWorld
import csdefine
import csstatus
from Function import Function

class FuncGetTongRobWarPoint( Function ):
	"""
	��ȡ�Ӷ�ս����
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_ROB_WAR_REWARD_GRADE )
			player.endGossip( talkEntity )
			return
		BigWorld.globalData["TongManager"].getTongRobWarPoint( player.base, player.tong_dbID )
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
		return True



#