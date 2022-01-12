# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csarithmetic
import Math
import math
import csdefine
from gbref import rds

class Spell_HitPush( Spell ):
	"""
	有伤害的位移技能
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# 施法者位移数据
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		# 受术者位移数据
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0

		self.param2 = 0
		self.param3 = 0

	def init( self, data ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, data )

		param2 = data["param2"].split(";")
		self.param2 = len( param2 )
		if self.param2 >= 2:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
		param3 = data["param3"].split(";")
		self.param3 = len( param3 )
		if self.param3 >= 2:
			self.targetMoveSpeed = float( param3[0] )
			self.targetMoveDistance = float( param3[1] )

	def cast( self, caster, targetObject ):
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		Spell.cast( self, caster, targetObject )

		target = targetObject.getObject()
		# 施法者位移
		if self.casterMoveDistance == 0.0:
			yaw = target.yaw
			dstPos = target.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * target.distanceBB( target )
		else:
			direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )
			direction.normalise()
			if direction == Math.Vector3():    #施法者与受术者刚好在一个位置
				yaw = caster.yaw
				direction = direction - ( Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) )
			dstPos = caster.position + direction * self.casterMoveDistance
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
		if self.casterMoveSpeed and self.param2 >= 2:
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					caster.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#光效中断
				caster.moveToDirectly( endDstPos, __onMoveOver )

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
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return

		if self.targetMoveDistance == 0.0:
			yaw = caster.yaw
			dstPos = caster.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * caster.distanceBB( caster )
		else:
			direction = Math.Vector3( caster.position ) - Math.Vector3( target.position )
			direction.normalise()
			if direction == Math.Vector3():    #施法者与受术者刚好在一个位置
				yaw = target.yaw
				direction = direction - ( Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) )
			dstPos = target.position + direction * self.targetMoveDistance
		endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
		if self.targetMoveSpeed and self.param3 >= 2:
			if target.__class__.__name__ == "PlayerRole":
				target.move_speed = self.targetMoveSpeed
				def __onMoveOver( success ):
					target.stopMove()
					if not success:
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
			target.playActions( actionNames )

