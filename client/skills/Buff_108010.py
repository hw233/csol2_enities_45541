# -*- coding: gb18030 -*-
"""
Spell技能类。
"""
from SpellBase import *
import BigWorld
import Define

class Buff_108010( Buff ):
	"""
	example:僵直
	"""
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_108010 )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id:
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_108010  )
