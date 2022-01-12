# -*- coding: gb18030 -*-

import csdefine
import csstatus
from CombatSpell import CombatSpell
import time

class MiniCombatSpell( CombatSpell ):
	def useableCheck( self, caster, target ):
		"""
		"""
		# 施法者检查
		if caster.getState() == csdefine.ENTITY_STATE_DEAD:
			return csstatus.SKILL_IN_DEAD

		if self.getRangeMax( self ) + caster.getBoundingBox().z / 2 + target.getObject().getBoundingBox().z / 2  \
			< caster.getGroundPosition().distTo( target.getObject().getGroundPosition() ):  # 由于追击的时候使用的是地面坐标进行判断，因此这里也采用地面坐标
			return csstatus.SKILL_TOO_FAR
		return csstatus.SKILL_GO_ON

	def persentDamage( self, caster, receiver, damageType, finiDamage ):
		"""
		virtual method.
		"""
		receiver.receiveSpell( caster.id, self.getID(), damageType, finiDamage, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType, finiDamage )

	def use( self, caster, target ):
		"""
		"""
		if not self.isNotRotate:
			caster.rotateToSpellTarget( target )					# 转向
		self.cast( caster, target )

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		caster.addCastQueue( self, target, 0.1 )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		finiDamage = 20
		
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		
		self.persentDamage( caster, receiver, self._damageType, finiDamage )

