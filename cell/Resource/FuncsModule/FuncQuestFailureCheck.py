# -*- coding: gb18030 -*-
#
# ��������ʧ�������0��ʧ�ܣ�1��δʧ��
# by ganjinxing 2012-01-10

from Function import Function


class FuncQuestFailureCheck( Function ):
	"""
	�ж�����״̬��Χ
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param01 = section.readInt( "param1" )  #����ID
		self.param02 = section.readInt( "param2" )  #����״̬

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
		if not player.has_quest( self.param01 ) :
			return False
		if self.param02 == 0 :
			return player.questIsFailed( self.param01 )
		elif self.param02 == 1 :
			return not player.questIsFailed( self.param01 )
		return False

#