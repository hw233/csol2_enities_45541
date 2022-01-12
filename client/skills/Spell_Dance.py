# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds
import csarithmetic
import Math
import math
from Function import Functor 
from gbref import rds

class Spell_Dance( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.danceAction = None



	def init( self, dict ):
		"""
		"""
		Spell.init( self, dict )
		self.danceAction = dict["param1"]  


	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if hasattr( caster, "state" ):
			if caster.state == csdefine.ENTITY_STATE_DEAD:	# 对施法者是否死亡的判断
				return csstatus.SKILL_IN_DEAD
		"""
		# 检查目标是否符合
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查施法者的消耗是否足够
	
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state
	

		if caster.intonating():
			return csstatus.SKILL_INTONATING
		"""
		# 检查玩家是否处于竞技场死亡隐身或GM观察者状态
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE

		# 检查技能cooldown 根据快捷栏变色的需求调整技能条件的判断顺序 这个只能放最后
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		"""
		if caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		"""
		return csstatus.SKILL_GO_ON

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		pass
		

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		print "Spell_Dance caster is ",caster, "targetObject is ", targetObject
		if caster.__class__.__name__ == "PlayerRole":
			rds.actionMgr.playActions( caster.getModel(), [self.danceAction,], callbacks = [ caster.finishSkillPlayAction ])
		elif caster.__class__.__name__ == "DanceNPC": #施法者是NPC
			rds.actionMgr.playActions( caster.getModel(), [self.danceAction,], callbacks = [ caster.cell.finishPlayAction ])
	




