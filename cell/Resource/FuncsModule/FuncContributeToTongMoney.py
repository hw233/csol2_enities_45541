# -*- coding: gb18030 -*-
#
# $Id: FuncQueryFamilyNPC.py,v 1.2 2008-07-19 03:53:07 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csconst
import csstatus

class FuncContributeToTongMoney( Function ):
	"""
	��ҪΪ�����׽�Ǯ
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
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			player.endGossip( talkEntity )
			return
		player.client.tong_onContributeToMoney()
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
# $Log: not supported by cvs2svn $
#
