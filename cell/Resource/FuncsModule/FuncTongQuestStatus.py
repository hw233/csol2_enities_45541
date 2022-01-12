# -*- coding: gb18030 -*-
#
# $Id: FuncTongQuestStatus.py

"""
"""
from Function import Function
import BigWorld
import csdefine

class FuncTongQuestStatus( Function ):
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
		self.param03 = section.readInt( "param3" ) #����ȼ�,��԰����������
		self.param04 = section.readInt( "param4" )  #�������ְ�����ǰ��������

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
		scrEntity = talkEntity.getScript()
		if self.param03 > 0:							#Ϊ��������
			count = 0
			for level in range( self.param03 ):
				questID = int( "%d00%d"%( self.param01, level + 1 ) )
				quest = scrEntity.getQuest( questID )
				questState = quest.query( player )
				if questState == self.param02:
					count += 1
			if count >= self.param03:						#ÿ���ȼ������ɽ�
				return True
		else:
			quest = scrEntity.getQuest( self.param01 )
			questState = quest.query( player )
			questType = quest.getType()
			if questState == self.param02:
				return True
			elif questState == csdefine.QUEST_STATE_NOT_HAVE:
				if questType == csdefine.QUEST_TYPE_TONG_FETE and not talkEntity.feteOpen:
					return True
		return False
