# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from Spell_Cursor import Spell_Cursor
from gbref import rds
import csdefine
import Math
from Function import Functor
from SpellBase.Spell import Spell
import csarithmetic

class Spell_323079( Spell_Cursor ):
	def __init__( self ):
		"""
		"""
		Spell_Cursor.__init__( self )
		self.param2 = 6.0
		self.param3 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_Cursor.init( self, dict )
		param2 = dict["param2"]
		if param2 != "":
			self.param2 = float( param2 )

		param3 = dict["param3"]
		if param3 != "":
			self.param3 = int( param3 )

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_Cursor.cast( self, caster, targetObject )
		targetPos = targetObject.getObjectPosition()
		dir = Math.Vector3( targetPos  - caster.position )
		caster.lastJumpAttackDir = dir
		caster.lastJumpAttackDir.normalise()

		if caster == BigWorld.player():
			distance = caster.position.flatDistTo( targetPos )
			targetPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, targetPos )
			speed = self.param2
			jumpTime = ( distance/speed )/2.0
			if jumpTime < 0.5:
				jumpTime = 0.5
				speed = distance/jumpTime
				if speed > self.param2:
					speed = self.param2
			caster.move_speed = speed
			caster.jumpToPoint( targetPos, jumpTime, csdefine.JUMP_TYPE_ATTACK )


class Spell_jumpAttck( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.param2 = 6.0
		self.param3 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		param2 = dict["param2"]
		if param2 != "":
			self.param2 = float( param2 )

		param3 = dict["param3"]
		if param3 != "":
			self.param3 = int( param3 )

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		targetPos = targetObject.getObjectPosition()
		dir = Math.Vector3( targetPos  - caster.position )
		caster.lastJumpAttackDir = dir
		caster.lastJumpAttackDir.normalise()

		if caster == BigWorld.player():
			distance = caster.position.flatDistTo( targetPos )
			targetPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, targetPos )
			speed = self.param2
			jumpTime = ( distance/speed )/2.0
			if jumpTime < 0.5:
				jumpTime = 0.5
				speed = distance/jumpTime
				if speed > self.param2:
					speed = self.param2
			caster.move_speed = speed
			caster.jumpToPoint( targetPos, jumpTime, csdefine.JUMP_TYPE_ATTACK )