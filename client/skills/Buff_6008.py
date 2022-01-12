# -*- coding: gb18030 -*-
#
# 移动迅捷客户端buff脚本
# edit by wuxo 2012-8-13


from bwdebug import *
from SpellBase import *
import BigWorld

class Buff_6008( Buff ):
	"""
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
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
		if caster.id == BigWorld.player().id:
			caster.addBlurEffect()
			if not caster.isMoving():#没有移动
				buffs = caster.attrBuffs
				for buff in buffs:
					skill = buff["skill"]
					if skill.getBuffID() == self.getBuffID():
						index = buff["index"]
						caster.requestRemoveBuff( index )
						return
		caster.setArmCaps()
		
	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		if caster.id == BigWorld.player().id:
			caster.delBlurEffect()
			caster.wasdFlag  = [ False,False,False,False ]
			if caster.physics.velocity.length >0 : #如果正在移动 physics的速度可能还是加成的
				caster.updateVelocity()
		caster.setArmCaps()	