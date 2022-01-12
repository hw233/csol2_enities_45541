# -*- coding: gb18030 -*-
#
"""
����������Ƿ�û��ѧϰ
edit by wuxo 2013-1-30
"""

from Function import Function


class FuncCheckLivingSkill( Function ):
	"""
	�ж�������Ƿ�û��ѧϰ
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readInt( "param1" )  

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
		for id in player.livingskill:
			baseID = id / 1000
			if baseID == self.param1:
				return False
		return True


