# -*- coding:gb18030 -*-

#

from Spell_313100004 import Spell_313100004

class Spell_313113( Spell_313100004 ):
	"""
	有物品检测的启动火把类场景物件，播放动画，完成任务条件,并向指定的NPC发送AI指令
	"""	
	
	def __init__( self ):
		Spell_313100004.__init__( self )
		self.range = 0.0
		self.className = ""
		self.entityType = ""
		self.commandString = 0


	def receive( self, caster, receiver ):
		"""
		"""
		Spell_313100004.receive( self, caster, receiver )
		# 处理发送AI指令
		self.range = float( receiver.getScript().param2 )
		self.className =receiver.getScript().param3
		self.entityType = receiver.getScript().param4
		self.commandString = int( receiver.getScript().param5 )
		
		
		monsterList = receiver.entitiesInRangeExt( self.range, self.entityType, receiver.position )
		for e in monsterList:
			if self.className == "":								# 如果className为空，则发送AI指令给指定范围类该类型的所有怪物
				e.sendAICommand( e.id, self.commandString )		
			else:													# 如果className不为空，则发送AI指令给指定的怪物
				if e.className == self.className:
					e.sendAICommand( e.id, self.commandString )	# 如果受术者不能够接受ai指令，说明此技能的受术对象配置有误

