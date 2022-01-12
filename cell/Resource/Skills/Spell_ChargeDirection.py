# -*- coding:gb18030 -*-
#edit by wuxo 2013-10-16

import Math
import math

import copy
import csstatus
import csdefine
import csarithmetic
import SkillTargetObjImpl
from Spell_PhysSkillImprove import Spell_PhysSkillImprove

class Spell_ChargeDirection( Spell_PhysSkillImprove ):
	"""
	吟唱时决定冲锋方向 仅限怪物使用
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		#施法者位移数据
		self.casterMoveSpeed    = 20.0   #冲刺速度 
		self.casterMoveDistance = 0.0	#冲刺距离

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )
		param1 = data["param2"].split(";")
		if len( param1 ) >= 2:
			self.casterMoveSpeed = float( param1[0] )
			self.casterMoveDistance = float( param1[1] )

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
		dstPos = target.getObjectPosition()
		direction = dstPos - caster.position
		direction.normalise()
		caster.setTemp( "CHARGE_DIRECTION", direction )
		return Spell_PhysSkillImprove.useableCheck( self, caster, target )

	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		# 施法者位移
		if self.casterMoveDistance and self.casterMoveSpeed:
			direction = caster.popTemp( "CHARGE_DIRECTION", None )
			if not direction:
				direction = Math.Vector3( math.sin(caster.yaw), 0.0, math.cos(caster.yaw) )
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			caster.moveToPosFC( endDstPos, self.casterMoveSpeed, True )
		Spell_PhysSkillImprove.cast( self, caster, target )
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		dstPos = caster.position
		target = SkillTargetObjImpl.createTargetObjPosition(dstPos)
		return Spell_PhysSkillImprove.getReceivers( self, caster, target )

class Spell_ChargeToPos( Spell_PhysSkillImprove ):
	"""
	吟唱时决定冲锋位置 仅限怪物使用
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		#施法者位移数据
		self.casterMoveSpeed    = 20.0   #冲刺速度
		self.delayTime  = 0.5 #延迟伤害时间

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )
		self.casterMoveSpeed = float( data["param2"] )

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
		state = Spell_PhysSkillImprove.useableCheck( self, caster, target )
		if state == csstatus.SKILL_GO_ON:
			if not target:
				dstPos = caster.position
			else:
				dstPos = target.getObjectPosition()
			caster.setTemp( "CHARGE_TARGET_POS", copy.deepcopy( dstPos ))
		return state

	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		# 施法者位移
		if self.casterMoveSpeed:
			pos = caster.popTemp( "CHARGE_TARGET_POS", None )
			if not pos:
				pos = target.getObjectPosition()
			self.delayTime = ( pos - caster.position ).length / self.casterMoveSpeed
			caster.moveToPosFC( pos, self.casterMoveSpeed, True )
		Spell_PhysSkillImprove.cast( self, caster, target )
	
	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		return  self.delayTime
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		dstPos = caster.position
		target = SkillTargetObjImpl.createTargetObjPosition( dstPos )
		return Spell_PhysSkillImprove.getReceivers( self, caster, target )