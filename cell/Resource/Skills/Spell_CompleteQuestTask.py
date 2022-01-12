# -*- coding: gb18030 -*-

from SpellBase import *
import csdefine

class Spell_CompleteQuestTask( Spell ):
	"""
	完成指定任务目标
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.questID = 0	# 任务ID
		self.taskIdx = 0	# 任务目标索引

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.questID = int( dict["param1"] )
		self.taskIdx = int( dict["param2"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return

		if receiver.hasTaskIndex( self.questID, self.taskIdx ):
			receiver.questTaskIncreaseState( self.questID, self.taskIdx )
