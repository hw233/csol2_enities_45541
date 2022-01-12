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

class Spell_Immunity_DIY( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.moveDistance = 0.0	#移动距离
		self.moveSpeed    = 0.0	#移动速度
		self.casterMoveDistance = 0.0 # 施法者移动的距离
		self.casterMoveSpeed = 0.0	# 施法者移动的速度


	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		param1 = data["param1"].split(";")
		if len( param1 ) >= 2:
			self.moveDistance = float( param1[1] )
			self.moveSpeed = float( param1[0] )

		if data["param2"]:
			param2 = [ float(i) for i in  data["param2"].split(";") ]
			if len( param2 ) >= 2:
				self.casterMoveDistance, self.casterMoveSpeed = param2

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

		# 检查玩家是否处于竞技场死亡隐身或GM观察者状态
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE

		# 检查技能cooldown 根据快捷栏变色的需求调整技能条件的判断顺序 这个只能放最后
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		if caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		return csstatus.SKILL_GO_ON

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#这里会出错误的原因是 在服务器上一个entity对另一个entity施法 服务器上是看的到施法者的
				#而客户端可能会因为某原因 如：网络延迟 而在本机没有更新到AOI中的那个施法者entity所以
				#会产生这种错误 written by kebiao.  2008.1.8
				return
		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage  )

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
		if self.casterMoveDistance and self.casterMoveSpeed:
			direction = caster.position - target.position
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					if success:
						caster.stopMove()
					else:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#光效中断
				caster.moveToDirectly( endDstPos, __onMoveOver )
				if self.casterMoveFace:
					BigWorld.dcursor().yaw = yaw

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		技能产生伤害时的动作效果等处理
		@param player:			玩家自己
		@type player:			Entity
		@param target:			Spell施放的目标Entity
		@type target:			Entity
		@param caster:			Buff施放者 可能为None
		@type castaer:			Entity
		@param damageType:		伤害类型
		@type damageType:		Integer
		@param damage:			伤害数值
		@type damage:			Integer
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return
		id = self.getID()
		if caster:
			self.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
		#如果当前目标处于霸体状态，将不会差生位移
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY| csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if self.moveDistance and self.moveSpeed:
			yaw = ( target.position - caster.position).yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.moveDistance
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, endDstPos+(0,-3,0), endDstPos+(0,3,0) )
			if target.__class__.__name__ == "PlayerRole":
				target.move_speed = self.moveSpeed
				def __onMoveOver( success ):
					target.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
				target.moveToDirectly( endDstPos, __onMoveOver )

	def hit( self, skillID, target ):
		"""
		播放受击动作
		@param skillID:			技能ID号
		@type skillID:			INT
		@param target:			Spell施放的目标Entity
		@type target:			Entity
		"""
		if target is None:
			return
		if target.actionStateMgr( ):
			weaponType = target.getWeaponType()
			vehicleType = 0
			if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				vehicleType = target.vehicleType
			actionNames = rds.spellEffect.getHitAction( skillID, weaponType, vehicleType )
			rds.actionMgr.playActions( target.getModel(),actionNames )
