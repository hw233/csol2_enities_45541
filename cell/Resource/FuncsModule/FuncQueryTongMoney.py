# -*- coding: gb18030 -*-
#
# $Id: FuncQueryFamilyNPC.py,v 1.2 2008-07-19 03:53:07 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csconst

class FuncQueryTongMoney( Function ):
	"""
	��ѯ�������ʽ�
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
		# ��ʱֻ�ܴ�base�ϻ�ý�����ά�޷��ã��������ʽ�ͻ��˿����Լ��ҵ�
		tongMailbox = player.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onRequestBuildingSpendMoney( player.base )
		player.endGossip( talkEntity )
		return
	
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
		
		return player.tong_dbID != 0