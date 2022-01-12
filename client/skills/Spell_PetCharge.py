# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from SpellBase import *

class Spell_PetCharge( Spell ):
	"""
	宠物冲锋技能客户端脚本
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.config_movespeed = 0.0		# 冲锋速度，不填默认技能飞行速度

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"]:
			self.config_movespeed = float( dict["param1"] )
		else:
			self.config_movespeed = self.getFlySpeed()

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )

		target = targetObject.getObject()
		if caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			def onChargeOver( caster, target, result ):
				caster.onChargeOver()	# 冲锋结束

			caster.cancelHeartBeat()	# 冲锋开始，停止心跳
			caster.isCharging = True
			caster.navigator.chasePosition( target.position, 1.0, self.config_movespeed, onChargeOver )
