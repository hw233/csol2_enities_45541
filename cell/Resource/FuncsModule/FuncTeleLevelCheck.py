# -*- coding: gb18030 -*-
#

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncTeleLevelCheck( Function ):
	"""
	�жϴ��͵ȼ�
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.reqLevel = section.readInt( "param1" )  #��������ȼ�

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
		if self.reqLevel > player.level:
				return False
		return True
		


#