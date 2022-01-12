# -*- coding: gb18030 -*-
#
# $Id: FuncLevel.py,v 1.1 2008-01-31 05:18:39 zhangyuxing Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncLevel( Function ):
	"""
	�жϵȼ���Χ
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param01 = section.readInt( "param1" )  #��С�ȼ�
		self.param02 = section.readInt( "pramm2" )  #���ȼ�

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass

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
		if self.param01 == 0:
			if self.param02 == 0 or player.level <= self.param02:
				return True
		else:
			if self.param01 <= player.level and ( self.param02 == 0 or player.level <= self.param02 ):
				return True
		
		return False
		


#