# -*- coding: gb18030 -*-
#
#
import csstatus
from SpellBase import Spell
from gbref import rds
from Function import Functor
import BigWorld
import Const

class Spell_FlyWater( Spell ):
	"""
	凌波微步客户端技能模块
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] != "":
			self.param1 = [ int(i) for i in dict["param1"].split("|")]
		else:
			self.param1 = []
		
		param2 = dict["param2"]
		if param2 == "":
			self.param2 = False
		else:
			self.param2 = True

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		player = BigWorld.player()
		target = targetObject.getObject()
		if target == player:
			player.changeAttackState( Const.ATTACK_STATE_NONE )
			rds.cameraEventMgr.triggerByClass( self.param1 )
			if self.param2:
				model = caster.getModel()
				model.visible = False
				rds.targetMgr.unbindTarget( None )
				

class Spell_FlyWaterAll( Spell_FlyWater ):
	"""
	凌波微步客户端技能模块(对所有看的到的玩家都有变现)
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )


	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		player = BigWorld.player()
		target = targetObject.getObject()
		player.changeAttackState( Const.ATTACK_STATE_NONE )
		rds.cameraEventMgr.triggerByClass( self.param1 )
		if self.param2:
			model = caster.getModel()
			model.visible = False
			rds.targetMgr.unbindTarget( None )