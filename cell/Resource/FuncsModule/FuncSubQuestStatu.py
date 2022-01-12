# -*- coding: gb18030 -*-
#
# $Id: FuncSubQuestStatu.py,v 1.1 2008-08-06 01:12:13 zhangyuxing Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncSubQuestStatu( Function ):
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
		self.param02 = section.readInt( "param2" )  #������ID
		self.param03 = section.readInt( "param3" )  #����״̬

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
		quest = player.getQuest( self.param01 )
		if quest != None:
			if player.questsTable.has_quest( self.param01 ) and player.questsTable[self.param01].query( "subQuestID" ) == self.param02:
				if quest.query( player ) == self.param03:
					return True
		return False
			
		


#