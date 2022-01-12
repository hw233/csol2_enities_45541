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

class Spell_PullAndBite( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		# 受术者位移数据
		self.targetMoveSpeed = 0.0
		#靠近施法者距离
		self.disToCaster  = 2.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		self.disToCaster     = float( data["param1"] )
		self.targetMoveSpeed = float( data["param2"] )
		
		
	def receiveSpell( self, target, casterID, damageType, damage  ):
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
		#加入多个人打一个目标时的表现判断
		if target.beHomingCasterID != 0 and target.beHomingCasterID != caster.id : return
		
		dis = ( target.position - caster.position ).length
		if target.__class__.__name__ == "PlayerRole" and self.targetMoveSpeed and dis > self.disToCaster:
			yaw = ( caster.position - target.position ).yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = target.position + direction * ( dis - self.disToCaster )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, endDstPos+(0,3,0), endDstPos-(0,3,0) )
			
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
			target.playActions( actionNames )
