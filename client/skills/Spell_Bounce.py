# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
from SpellBase import *
import csdefine
from gbref import rds
import csarithmetic
import Math
import math
from gbref import rds
from Function import Functor


class Spell_Bounce( Spell ):
	"""
	建筑物创建时 需要将玩家弹开
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )


	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理
		
		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		# 动作光效部分
		self._skillAE( BigWorld.player(), target, casterID, damageType, damage  )

	def _skillAE( self, player, target, casterID, damageType, damage ):
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
		if target.id == BigWorld.player().id:
			BigWorld.callback( 0.1, Functor( self.moveOut, casterID ) )
			
	def moveOut( self, casterID ):
		caster = BigWorld.entities.get( casterID )
		target = BigWorld.player()
		if caster:
			caster.isCloseCollide( True )
			s1 = caster.getBoundingBox().z / 2
			s2 = caster.getBoundingBox().x / 2
			radius = math.sqrt( s1*s1 + s2*s2 )
			disP = target.position - caster.position
			dis = radius - disP.length
			if dis < 0: return
			yaw = target.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			dstPos = target.position + direction * dis
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, endDstPos+(0,2,0), endDstPos-(0,2,0) )
			def __onMoveOver( success ):
				target.stopMove()
				caster.isCloseCollide( False )
				caster.openCollide()
				rds.skillEffect.interrupt( target )#光效中断
				if not  success:
					DEBUG_MSG( "player move is failed." )
			target.moveToDirectly( endDstPos, __onMoveOver )
		else:	
			BigWorld.callback( 0.1, Functor( self.moveOut, casterID ) )


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


