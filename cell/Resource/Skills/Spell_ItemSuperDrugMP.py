# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemSuperDrugMP.py,v 1.2 2008-09-01 09:15:58 huangdong Exp $


from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
import csdefine


class Spell_ItemSuperDrugMP( Spell_ItemCure ):
	"""
	使用：累积恢复一定数量的MP
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemCure.__init__( self )

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
		uid = caster.queryTemp( "item_using" )
		caster.setTemp( "Spell_ItemSuperDrugMP_ItemUID", uid )
		Spell_ItemCure.cast( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		# 计算效果值应该在caster为real时进行并更新item的使用效果；但治疗效果要加给receiver，此时需保证receiver是real
		# 设置一个hadReceived标记，receive第一次执行时，caster为real，此时设置hadReceived为True并更新item的使用效果；
		# 如果是第二次进入receve( 通过receiveOnReal )，hadReceived限制了不再对caster进行处理，
		# 如此就不会扣除玩家物品两次使用效果。19:27 2009-11-4，wsf
		stringKey = str( self.getID() ) + str( caster.id )
		hadReceived = False
		if receiver.isReal():
			hadReceived = receiver.queryTemp( stringKey, False )
		if caster and caster.isReal() and not hadReceived:
			Spell_ItemCure.receive( self, caster, receiver )
			item = caster.getByUid( caster.queryTemp( "Spell_ItemSuperDrugMP_ItemUID" ) )
			receiver.setTemp( "buffcurPoint", min( self._effect_max, item.getCurrPoint() ) )
			self.payItemPoint_MP( caster, receiver)
		if not hadReceived:
			receiver.setTemp( stringKey, True )
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.removeTemp( stringKey )
		curPoint = receiver.popTemp( "buffcurPoint", 0 )
		self.cureMP( caster, receiver, curPoint )

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
		targetEntity = target.getObject()
		if targetEntity.MP == targetEntity.MP_Max:
			return csstatus.SKILL_CURE_NONEED
		if targetEntity.getEntityType() == csdefine.ENTITY_TYPE_PET and targetEntity.level < int( self.getParam5Data() ):
			return csstatus.SKILL_ITEM_NOT_READY
		return Spell_ItemCure.useableCheck( self, caster, target)

	def payItemPoint_MP( self , caster, receiver):
		"""
		计算恢复MP后应该扣除的点数
		"""
		uid = caster.queryTemp( "Spell_ItemSuperDrugMP_ItemUID" )
		item = caster.getByUid( uid )
		lostMp = receiver.MP_Max - receiver.MP
		curMP = max( self._effect_min, lostMp )
		curMP = min( self._effect_max, curMP )
		if item:
			item.setTemp("sd_usePoint",curMP)

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		return 0.0