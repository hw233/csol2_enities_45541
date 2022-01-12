# -*- coding: gb18030 -*-

"""
排兵布阵-冲锋技能客户端类
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

class Spell_Charge( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# 受术者位移数据
		self.targetMoveSpeed = 0.0	#击退速度
		self.targetMoveDistance = 0.0		#击退距离
		#施法者位移数据
		self.casterMoveDistance = 0.0	#冲刺距离
		self.casterMoveSpeed    = 0.0	#冲刺速度
		self.casterMoveFace     = False  #冲刺方向和释放者朝向是否一致

		self.chargeDirection    = None	#冲刺方向


	def init( self, data ):
		Spell.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 2:
			self.targetMoveSpeed = float( param2[0] )
			self.targetMoveDistance = float( param2[1] )

		param3 = data["param3"].split(";")
		if len( param3 ) >= 3:
			self.casterMoveSpeed = float( param3[0] )
			self.casterMoveDistance = float( param3[1] )
			self.casterMoveFace = bool( int( param3[2] ) )
		if data["param4"] != "":
			self.chargeDirection = eval(data["param4"])

	def cast( self, caster, targetObject ):
		"""
		"""
		Spell.cast( self, caster, targetObject )
		if  self.casterMoveDistance and self.casterMoveSpeed:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					rds.skillEffect.interrupt( caster )#光效中断
					caster.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
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
		Spell._skillAE( self, player, target, caster, damageType, damage )
		#如果当前目标处于霸体状态，将不会差生位移
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if self.targetMoveDistance and self.targetMoveSpeed:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = target.position + direction * self.targetMoveDistance
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )

			if target.id == BigWorld.player().id:
				def __onMoveOver( success ):
					target.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#光效中断
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


