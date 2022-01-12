# -*- coding: gb18030 -*-
#
# $Id: FuncContestFamilyNPC.py,v 1.3 2008-07-31 04:14:37 kebiao Exp $

"""
"""
from Function import Function
from FuncTeleport import FuncTeleport
import BigWorld
import csstatus
import csdefine
import csconst

class FuncGoToTongTerritory( Function ):
	"""
	�޽���Ὠ��
	"""
	def __init__( self, section ):
		"""
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
		player.gotoSpace( "fu_ben_bang_hui_ling_di", ( 0,0,0 ), ( 0,0,0 ) )
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
		return player.tong_dbID > 0