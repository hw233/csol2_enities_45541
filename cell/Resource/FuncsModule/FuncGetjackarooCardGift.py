# -*- coding: gb18030 -*-
#
# $Id: FuncGetjackarooCardGift.py,v 1.11 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
from bwdebug import *

class FuncGetjackarooCardGift( Function ):
	"""
	��ȡ���ֿ�������Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )		# ��ȡ����ĵȼ�
		self._param2 = section.readInt( "param2" )		# ��ȡ����ƷID


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
		if not self._param1 or not self._param2:
			ERROR_MSG("FuncGetjackarooCardGift, parameter is wrong param = %s, param = %s " % (self._param1,self._param2) )
			return
		player.base.getjackarooCardGift( self._param1, self._param2 )


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


