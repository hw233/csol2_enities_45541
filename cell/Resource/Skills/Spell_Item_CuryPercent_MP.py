# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemSuperDrugMP.py,v 1.2 2008-09-01 09:15:58 huangdong Exp $


from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
import csdefine


class Spell_Item_CuryPercent_MP( Spell_ItemCure ):
	"""
	使用：累积恢复一定数量的MP,每次按百分比恢复
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemCure.__init__( self )

	def init( self, dictDat ):
		"""
		读取技能配置
		@param dictDat:	配置数据
		@type dictDat:	python dictDat
		"""
		Spell_ItemCure.init( self, dictDat )
		self._effect_max = dictDat[ "EffectMax" ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		uid = caster.queryTemp( "item_using" )
		hasReceived = False

		if caster.isReal() and not caster.queryTemp( uid, False ):
			Spell_ItemCure.receive( self, caster, receiver )
			uid = caster.queryTemp( "item_using" )
			item = caster.getByUid( uid )
			receiver.setTemp( "buffcurPoint", min( int( receiver.MP_Max / 100.0 * self._effect_max ) + self._effect_min , item.getCurrPoint() ) )
			self.payItemPoint_MP( caster, receiver, item )

		if not receiver.isReal():
			caster.setTemp( uid, True)						# 之所以将判断重复的数据记录在cast身上，是因为这里cast肯定为real 这样receiveOnReal的时候 该值一定被修改了。
			receiver.receiveOnReal( caster.id, self )
			return

		caster.setTemp( uid, False )						# setTemp可以远程修改
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

	def payItemPoint_MP( self , caster, receiver, item):
		"""
		计算恢复MP后应该扣除的点数
		"""
		lostMp = receiver.MP_Max - receiver.MP
		effect = int( receiver.MP_Max / 100.0 * self._effect_max ) + self._effect_min
		curMP = max( self._effect_min, lostMp )
		curMP = min( effect, curMP )
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