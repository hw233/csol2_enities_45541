# -*- coding: gb18030 -*-
#


from Function import Function
from FuncSunBath import FuncEnterSunBath
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncEndQuestTaskThenTeleport( FuncEnterSunBath ):
	"""
	�ж��Ƿ����ĳ������Ŀ�ꡣ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		FuncEnterSunBath.__init__( self, section )
		questAndTask = section.readString( "param5" ).split( ":" )	# ����ID������Ŀ������
		self.questID = int( questAndTask[0] )
		self.taskIndex = int( questAndTask[1] )

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
		if not player.taskIsCompleted( self.questID, self.taskIndex ):
			player.statusMessage( csstatus.ROLE_QUEST_TASK_IS_NOT_COMPLETED )
			return
		if player.level < self.repLevel:
			player.statusMessage( csstatus.SUN_BATHING_ENTER_LEVEL, self.repLevel )
			return
		player.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
		player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )


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


