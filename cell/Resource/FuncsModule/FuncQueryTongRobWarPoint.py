# -*- coding: gb18030 -*-
#
# $Id: FuncExp2Pot.py,v 1.1 2010-01-14 05:18:39 pengju Exp $

"""
"""
import BigWorld
import csdefine
import csstatus
from Function import Function

class FuncQueryTongRobWarPoint( Function ):
	"""
	�鿴�Ӷ�ս����
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
		BigWorld.globalData["TongManager"].queryTongRobWarPoint( player.base, player.tong_dbID, talkEntity.id )

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