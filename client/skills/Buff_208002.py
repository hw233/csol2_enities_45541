# -*- coding: gb18030 -*-


from bwdebug import *
import event.EventCenter as ECenter
from SpellBase import *
import Math
import Define

class Buff_208002( Buff ):
	"""
	固定方向移动
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Buff.__init__( self )
		self.speed = 0.0
		self.direction = None
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type  dict:			python 字典
		"""
		Buff.init( self, dict )
		self.speed = float( dict.get("Param1") )
		self.direction = Math.Vector3( eval( dict.get("Param2") ) )
	
		
	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.moveDirection = [ self.direction[0], self.direction[2], self.speed ]
			target.updateVelocity()
				

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id:
			target.moveDirection = []
			target.stopMoving()
			
