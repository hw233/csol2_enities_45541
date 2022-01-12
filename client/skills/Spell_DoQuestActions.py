# -*- coding: gb18030 -*-
#
#
import csstatus
from SpellBase import Spell
from gbref import rds
from Function import Functor
import BigWorld
import Const

class Spell_DoQuestActions( Spell ):
	"""
	用于完成指定任务，并执行相关动作
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

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		target = targetObject.getObject()
		player = BigWorld.player()
		if target.id !=  player.id:
			return
		
		player.changeAttackState( Const.ATTACK_STATE_NONE )
		rds.cameraEventMgr.triggerByClass( self.param1 )
		model = caster.getModel()
		if model:
			model.visible = False
		rds.targetMgr.unbindTarget( None )
		