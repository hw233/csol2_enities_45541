 # -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpellBase import * 
from gbref import rds
import csdefine
import Math
import csstatus
from Function import Functor

#����
class Spell_311307( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.param2 = 6.0
		self.param3 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
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
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		targetPos = targetObject.getObjectPosition()
		dir = Math.Vector3( targetPos  - caster.position )
		caster.lastJumpAttackDir = dir
		caster.lastJumpAttackDir.normalise()

		if caster == BigWorld.player():
			distance = caster.distanceBB( targetObject.getObject() ) + caster.distanceBB( caster )
			targetPos = targetObject.getObjectPosition()
			targetPos = caster.position + dir * distance
			speed = self.param2
			jumpTime = ( distance/speed )/2.0
			if jumpTime < 0.5:
				jumpTime = 0.5
				speed = distance/jumpTime
				if speed > self.param2:
					speed = self.param2
			caster.move_speed = speed
			caster.jumpToPoint( targetPos, jumpTime, csdefine.JUMP_TYPE_ATTACK )
