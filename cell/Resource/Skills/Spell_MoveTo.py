# -*- coding: gb18030 -*-
#

import Math
import math
import BigWorld
import ECBExtend
import random
from SpellBase import *
import csstatus
import csdefine


class Spell_MoveTo( Spell ):
	"""
	# 移动到目标周围一定范围内
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.param1 = float( dict[ "param1" ] )  # param1,离目标的距离
		if dict[ "param2" ]:
			self.param2 = float( dict[ "param2" ] )	 # param2,移动速度
			
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#处理眩晕、定身、昏睡等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )
	
	def cast( self, caster, target ):
		"""
		"""
			
		count = 10
		pos = None
		if hasattr( self, "param2" ):
			caster.move_speed = self.param2
			caster.updateTopSpeed()
		targetEntity = target.getObject()
		for tryNum in xrange( count ):
			a = self.param1 + ( caster.getBoundingBox().z + targetEntity.getBoundingBox().z ) / 3.0
			# 选取半圆周上的点
			targetPos =  target.getObjectPosition()
			yaw = ( caster.position - targetPos ).yaw
			angle = random.uniform( yaw - math.pi/2, yaw + math.pi / 2 )
			direction = Math.Vector3( math.sin( angle ), 0.0, math.cos( angle ) )
			direction.normalise()					# 将向量单位化
			pos = Math.Vector3( targetPos ) + a * direction

			posList = BigWorld.collide( caster.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
			if not posList:
				continue
			caster.gotoPosition( pos )
			if hasattr( self, "param2" ):
				pos_temp = ( pos - caster.position ).length
				delayTime = pos_temp / caster.move_speed
				caster.addTimer( delayTime, 0, ECBExtend.CHARGE_SPELL_CBID )
			break
		Spell.cast( self, caster, target )
		